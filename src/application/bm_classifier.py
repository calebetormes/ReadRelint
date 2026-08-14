"""
Classificador determinístico de BmGroup para RELINTs.

Funciona como camada de segurança *pós-LLM*: analisa o nome do arquivo,
o assunto e o conteúdo usando padrões regex para corrigir classificações
incorretas ou ausentes do modelo de linguagem.

Hierarquia de prioridade (maior especificidade vence):
  1. Homicídio / Feminicídio / Latrocínio
  2. Prisão por Tráfico
  3. Roubo a Estabelecimento
  4. Roubo a Residência
  5. Roubo de Veículo
  6. Roubo a Pedestre
  7. Furto de Veículo
  8. Furto Qualificado
  9. Outros (fallback)
"""

import re
from typing import Optional


# ---------------------------------------------------------------------------
# Padrões de classificação ordenados por especificidade decrescente
# Cada entrada é (BmGroup_value, [patterns])
# ---------------------------------------------------------------------------

_CLASSIFICATION_RULES: list[tuple[str, list[str]]] = [

    # 1. Homicídio (mais específico — evita ambiguidade com roubo + morte)
    (
        "Homicídio",
        [
            r"homic[ií]dio",
            r"feminic[ií]dio",
            r"latroc[ií]nio",
            r"\bóbito\b", r"\bobito\b",
            r"\bcadáver\b", r"\bcadaver\b",
            r"\bassassinato\b",
            r"\bexecutado\b", r"\bexecutada\b",
            r"\balvejado\b", r"\balvejada\b",
            r"encontro\s+de\s+c[oó]rpo",
            r"c[oó]rpo\s+sem\s+vida",
            r"v[ií]tima\s+fatal",
        ],
    ),

    # 2. Tráfico de drogas
    (
        "Prisão por Tráfico",
        [
            r"tr[aá]fico",
            r"entorpecente",
            r"\bdroga[s]?\b",
            r"\bcocaína\b", r"\bcocaina\b",
            r"\bcrak\b", r"\bcrack\b",
            r"\bmaconha\b", r"\bcannabis\b",
            r"\bprisão\s+por\s+tráfico\b",
            r"\bpreso\s+.*tráfico\b",
            r"\bposse\s+de\s+droga\b",
        ],
    ),

    # 3. Roubo a Estabelecimento
    (
        "Roubo a Estabelecimento",
        [
            r"roubo\s+a\s+estabelecimento",
            r"roubo\s+ao?\s+(?:comércio|comercio|supermercado|loja|banco|farmácia|farmacia|posto\s+de\s+combust)",
            r"assalto\s+a\s+(?:banco|loja|supermercado|farmácia|farmacia|posto\s+de\s+combust)",
            r"roubo\s+(?:em|de)\s+(?:banco|caixa\s+eletrônico|caixa\s+eletronico)",
        ],
    ),

    # 4. Roubo a Residência
    (
        "Roubo a Residência",
        [
            r"roubo\s+a\s+resid[eê]ncia",
            r"roubo\s+(?:de|em|\u00e0)\s+(?:casa|resid[eê]ncia|domic[ií]lio|im[oó]vel)",
            r"assalto\s+(?:a|\u00e0)\s+(?:casa|resid[eê]ncia|domic[ií]lio)",
            r"invas[aã]o\s+de\s+(?:casa|domic[ií]lio)",
            r"roubo\s+(?:na|em)\s+(?:resid[eê]ncia|casa)",
        ],
    ),

    # 5. Roubo de Veículo
    (
        "Roubo de Veículo",
        [
            r"roubo\s+de\s+ve[íi]culo",
            r"roubo\s+do\s+ve[íi]culo",
            r"ve[íi]culo\s+roubado",
            r"subtra[çc][ãa]o\s+de\s+ve[íi]culo",
            r"assalto\s+ao?\s+ve[íi]culo",
            r"roubo\s+de\s+(?:carro|moto|caminhão|caminhao|ônibus|onibus)",
            r"roubo\s+de\s+motocicleta",
        ],
    ),

    # 6. Roubo a Pedestre (mais genérico que os outros roubos)
    (
        "Roubo a Pedestre",
        [
            r"roubo\s+a\s+pedestre",
            r"roubo\s+(?:de\s+)?(?:transeunte|passante|pedestre)",
            r"assalto\s+a\s+(?:pedestre|pessoa\s+na\s+rua|transeunte)",
            r"roubo\s+(?:de\s+)?(?:celular|carteira|bolsa|relógio|relogio)\b(?!.*resid[eê]ncia)",
            r"\broubo\b(?!.*(?:ve[íi]culo|carro|moto|estabelecimento|resid[eê]ncia|casa))",
        ],
    ),

    # 7. Furto de Veículo
    (
        "Furto de Veículo",
        [
            r"furto\s+de\s+ve[íi]culo",
            r"furto\s+do\s+ve[íi]culo",
            r"ve[íi]culo\s+furtado",
            r"furto\s+de\s+(?:carro|moto|caminhão|caminhao|motocicleta)",
        ],
    ),

    # 8. Furto Qualificado
    (
        "Furto Qualificado",
        [
            r"furto\s+qualificado",
            r"furto\s+mediante\s+(?:escalada|arrombamento|destruição|destruicao|chave\s+falsa)",
            r"\bfurto\b",
        ],
    ),
]


def classify_bm_group(
    filename: str = "",
    subject: str = "",
    content: str = "",
    llm_bm_group: Optional[str] = None,
) -> str:
    """
    Classifica deterministicamente o BmGroup de uma ocorrência analisando
    o nome do arquivo, o assunto e o conteúdo com padrões regex ordenados.

    Retorna:
      - O valor string do BmGroup classificado (ex: "Homicídio").
      - Se a LLM já retornou um valor válido (não "Outros"), ele é preservado
        desde que não seja contraditado por um padrão de maior prioridade.

    Args:
        filename: Nome do arquivo PDF de origem.
        subject: Campo ASSUNTO extraído do RELINT.
        content: Texto do histórico/conteúdo.
        llm_bm_group: Classificação sugerida pelo LLM (pode ser None ou "Outros").
    """
    # Corpus de busca: filename + subject têm maior peso; content completa.
    # Concatenamos em ordem de confiança.
    primary = f"{filename} {subject}".lower()
    secondary = (content or "").lower()
    full_corpus = f"{primary} {secondary}"

    for bm_value, patterns in _CLASSIFICATION_RULES:
        for pattern in patterns:
            if re.search(pattern, full_corpus, re.IGNORECASE):
                return bm_value

    # Nenhum padrão bateu: se a LLM sugeriu algo diferente de "Outros", preservar
    if llm_bm_group and llm_bm_group not in ("Outros", "outros", None):
        return llm_bm_group

    return "Outros"
