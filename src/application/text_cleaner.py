import re

def clean_relint_text(text: str) -> str:
    """
    Remove blocos administrativos e assinaturas inúteis do final do texto do RELINT.
    Corta todo o conteúdo a partir da primeira ocorrência de termos como
    'Distribuição:', 'Assinatura:' ou 'Instruções:'.

    :param text: Texto bruto extraído do PDF.
    :return: Texto limpo pronto para envio à LLM.
    """
    if not text:
        return ""

    # 1. Remove todos os blocos de aviso legal de documento preparatório/acesso restrito
    disclaimer_pattern = re.compile(
        r'DOCUMENTO\s+PREPARAT[OÓ]RIO\s+[\–\-]\s+ACESSO\s+RESTRITO.*?'
        r'n[ãa]o\s+autorizados\.?',
        re.IGNORECASE | re.DOTALL
    )
    cleaned_text = re.sub(disclaimer_pattern, "", text)

    # 2. Remove cabeçalhos repetitivos da Brigada Militar
    header_pattern = re.compile(
        r'ESTADO\s+DO\s+RIO\s+GRANDE\s+DO\s+SUL\s*'
        r'SECRETARIA\s+DA\s+SEGURAN[ÇC]A\s+P[ÚU]BLICA\s*'
        r'BRIGADA\s+MILITAR\s*'
        r'SISTEMA\s+DE\s+INTELIG[ÊE]NCIA',
        re.IGNORECASE
    )
    cleaned_text = re.sub(header_pattern, "", cleaned_text)

    # 3. Remover numeração de páginas (ex: "Página 1 de 5", "Pág. 2", "Pg 3", "Page 1 of 2")
    page_pattern = re.compile(
        r'(?i)\b(?:p[aá]g(?:ina)?|pg|page)\.?[ \t]*\d+(?:[ \t]+(?:de|of)[ \t]+\d+)?\b'
    )
    cleaned_text = re.sub(page_pattern, "", cleaned_text)

    # 4. Remover números de páginas isolados em uma única linha
    isolated_number_pattern = re.compile(
        r'(?m)^\s*\d+\s*$'
    )
    cleaned_text = re.sub(isolated_number_pattern, "", cleaned_text)

    # 5. Padrão regex cobrindo termos de corte comuns (case-insensitive e tolerante a acentuação)
    pattern = re.compile(
        r'(?:^|\n)\s*(?:distribui[çc][ãa]o|assinatura|instru[çc][õo]es)\s*:.*',
        re.IGNORECASE | re.DOTALL
    )

    # Substitui todo o trecho casado a partir da palavra-chave por nada
    cleaned_text = re.sub(pattern, "", cleaned_text)
    return cleaned_text.strip()
