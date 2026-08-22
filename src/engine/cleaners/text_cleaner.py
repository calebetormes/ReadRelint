import re
from typing import Tuple, List, Dict, Any


def clean_relint_text(text: str) -> str:
    """
    Remove blocos administrativos, cabeçalhos institucionais, avisos legais de sigilo,
    numeração de páginas e assinaturas inúteis do texto do RELINT.

    :param text: Texto bruto extraído do PDF ou histórico.
    :return: Texto limpo pronto para envio à LLM ou salvamento.
    """
    if not text:
        return ""

    # 1. Remove todos os blocos de aviso legal de documento preparatório/acesso restrito (com ou sem 'Página X de Y')
    disclaimer_pattern = re.compile(
        r'(?:P[aá]g(?:ina)?\s*\d+(?:\s*de\s*\d+)?\s*[\r\n]*)?'
        r'DOCUMENTO\s+PREPARAT[OÓ]RIO\s*[\–\-\—]\s*ACESSO\s+RESTRITO.*?'
        r'n[ãa]o\s+autorizados\.?',
        re.IGNORECASE | re.DOTALL
    )
    cleaned_text = re.sub(disclaimer_pattern, "", text)

    # 1b. Fallback para aviso legal isolado da Lei 12.527/2011
    legal_notice_pattern = re.compile(
        r'Nos\s+termos\s+do\s+Art\.\s*7.*?n[ãa]o\s+autorizados\.?',
        re.IGNORECASE | re.DOTALL
    )
    cleaned_text = re.sub(legal_notice_pattern, "", cleaned_text)

    # 2. Remove cabeçalhos repetitivos da Brigada Militar / Segurança Pública
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

    # 5. Padrão regex cobrindo termos de corte de rodapé (Distribuição:, Assinatura:, Instruções:)
    pattern = re.compile(
        r'(?:^|\n)\s*(?:distribui[çc][ãa]o|assinatura|instru[çc][õo]es)\s*:.*',
        re.IGNORECASE | re.DOTALL
    )

    cleaned_text = re.sub(pattern, "", cleaned_text)
    return normalize_whitespace_and_paragraphs(cleaned_text)


def normalize_whitespace_and_paragraphs(text: str) -> str:
    """
    Remove quebras de linha artificiais no meio de parágrafos (oriundas do layout do PDF),
    preservando quebras de linha duplas (\n\n) para parágrafos reais, itens de lista (- ou *),
    e campos de cabeçalho (ex: DATA:, ASSUNTO:, RG:, NOME:).
    Também elimina múltiplos espaços consecutivos em branco e pontuações isoladas.
    """
    if not text:
        return ""

    # 1. Normaliza finais de linha \r\n para \n e limpa espaços ao redor das quebras
    text = re.sub(r'[ \t]*\r?\n[ \t]*', '\n', text)

    # 1b. Trata casos onde o cabeçalho 'ANEXOS: XXX' está grudado na mesma linha com o texto narrativo ou com divisórias '____'
    pattern_inline = re.compile(
        r'(?i)\b(ANEXOS?\s*:\s*(?:XXX|NENHUMA?|NADA|\-|\d+|[A-Z0-9_\-\.]{1,20}))(?:\s*_{3,})?\s+(?=[A-Z\d\"][a-z\u00C0-\u00FF]|\bEm\b|\bNo\b|\bNa\b|\bConforme\b|\bSegundo\b|\bAo\b|\bUm\b|\bUma\b)'
    )
    text = re.sub(pattern_inline, r'\1\n\n', text)

    # 2. Preserva parágrafos reais (\n\n ou mais) usando um marcador temporário
    MARKER = "___PARAGRAPH_BREAK___"
    text = re.sub(r'\n{2,}', MARKER, text)

    # 3. Processa cada bloco preservado
    blocks = text.split(MARKER)
    cleaned_blocks = []

    for block in blocks:
        lines = [l.strip() for l in block.split('\n') if l.strip()]
        if not lines:
            continue

        merged_lines = []
        for line in lines:
            if not merged_lines:
                merged_lines.append(line)
            else:
                last_line = merged_lines[-1]

                # Critérios para MANTER uma quebra de linha individual:
                # - A linha atual é um campo formal (ex: ASSUNTO:, DATA:, ORIGEM:, RG:, NOME:, SUSPEITO 01:)
                # - A linha atual começa com um marcador de lista (- ou * ou 1. ou 2.)
                # - A linha anterior termina com dois pontos (:) ou é a linha de ANEXOS:
                is_field_header = bool(re.match(r'^(?:[A-Z0-9_\-\.\s]{2,30}:|SUSPEITO|ANTECEDENTES|FOTO|REGISTRO|IMAGEM|ANEXOS|\-|\*|\d+[\.\)])', line, re.IGNORECASE))
                last_ended_with_colon = last_line.endswith(':')
                last_is_anexos = bool(re.match(r'^ANEXOS?\s*:', last_line, re.IGNORECASE))

                if is_field_header or last_ended_with_colon or last_is_anexos:
                    merged_lines.append(line)
                else:
                    # Junta com a linha anterior usando um espaço
                    merged_lines[-1] = last_line + " " + line

        cleaned_blocks.append("\n".join(merged_lines))

    # 4. Reconstitui os parágrafos com quebra dupla (\n\n)
    result = "\n\n".join(cleaned_blocks)

    # 5. Garante que após a linha de ANEXOS: haja uma linha em branco (\n\n) separando o cabeçalho do corpo do texto
    result = re.sub(
        r'((?:ANEXOS?\s*:[^\n]*))(\n+)(?=[^\s\n])',
        r'\1\n\n',
        result,
        flags=re.IGNORECASE
    )

    # 6. Normaliza múltiplos espaços horizontais consecutivos no meio da linha
    result = re.sub(r'[ \t]{2,}', ' ', result)

    # 7. Corrige pontuação com espaço antes (ex: "anos , ATUAL" -> "anos, ATUAL")
    result = re.sub(r'\s+([,\.\;:\?\!])', r'\1', result)

    return result.strip()

def extract_history_from_annex(text: str) -> str:
    """
    Extrai o histórico integral caso encontre a palavra 'ANEXOS:'.
    Aplica a limpeza de cabeçalhos, numeração de páginas e avisos de sigilo.
    """
    if not text:
        return ""
    
    match = re.search(r'(?i)ANEXOS?\s*:\s*(.*)', text, re.DOTALL)
    if match:
        extracted = match.group(1).strip()
        return clean_relint_text(extracted)
    return ""


def extract_date_of_fact(text: str) -> str:
    """
    Extrai heuristicamente a data de ocorrência do fato a partir do texto/primeira frase do RELINT.
    Suporta formatos: 'DD de mês de AAAA', 'DD/MM/AAAA', 'DD.MM.AAAA', etc.
    """
    if not text:
        return ""

    # Limita a busca aos primeiros 1500 caracteres para focar na introdução/primeiro parágrafo do histórico
    snippet = text[:1500]

    # 1. Padrão: "01 de janeiro de 2025" ou "12 de Maio de 2026"
    match = re.search(r'\b(\d{1,2}\s+de\s+[a-zA-Z\u00C0-\u00FF]+\s+de\s+\d{4})\b', snippet, re.IGNORECASE)
    if match:
        return match.group(1).strip()

    # 2. Padrão: "15/08/2026" ou "15.08.2026" ou "15-08-2026"
    match = re.search(r'\b(\d{1,2}[\/\.-]\d{1,2}[\/\.-]\d{2,4})\b', snippet)
    if match:
        return match.group(1).strip()

    # 3. Padrão: "12 de maio 2026"
    match = re.search(r'\b(\d{1,2}\s+de\s+[a-zA-Z\u00C0-\u00FF]+\s+\d{4})\b', snippet, re.IGNORECASE)
    if match:
        return match.group(1).strip()

    return ""

def extract_time_of_fact(text: str) -> str:
    """
    Extrai heuristicamente a hora de ocorrência do fato no primeiro parágrafo do RELINT.
    Formatos aceitos: '01h30min', '14:30', '18h', 'por volta das 14h', etc.
    """
    if not text:
        return ""

    snippet = text[:1500]
    match = re.search(
        r'\b(?:às|por volta d[as]|aproximadamente\s+às)?\s*(\d{1,2}\s*[hH]\s*(?:\d{2}\s*min?)?|\d{1,2}:\d{2}(?:\s*h)?)\b',
        snippet
    )
    if match:
        return match.group(1).strip()

    return ""

def extract_map_url(text: str) -> str:
    """
    Captura URLs do Google Maps presentes no texto do RELINT.
    """
    if not text:
        return ""

    match = re.search(r'https?://(?:maps\.app\.goo\.gl|google\.com/maps|goo\.gl/maps)/[^\s,;><\)\']+', text)
    if match:
        return match.group(0).strip()

    return ""

def resolve_coordinates_and_map_info(text: str, map_url: str = "") -> Tuple[str, str]:
    """
    Identifica o link do mapa e tenta extrair as coordenadas geográficas (Latitude, Longitude).
    Suporta coordenadas decimais (-28.26123, -53.49123) e DMS (28°15'40"S 53°29'28"W).
    Retorna uma tupla: (map_url, coordinates)
    """
    if not text and not map_url:
        return "", ""

    found_url = map_url if map_url else extract_map_url(text)
    coords = ""

    # 1. Tentar encontrar coordenadas decimais (ex: -28.26123, -53.49123 ou 28.26123 S, 53.49123 W)
    match_coords = re.search(r'(-?\d{1,2}\.\d{4,8})\s*[\s,;/\\]+\s*(-?\d{1,2}\.\d{4,8})', text)
    if match_coords:
        coords = f"{match_coords.group(1)}, {match_coords.group(2)}"

    # 2. Se não encontrou decimais simples, buscar formato DMS (Graus, Minutos e Segundos)
    if not coords:
        match_dms = re.search(r'(\d{1,2}°\s*\d{1,2}[\'′]\s*[\d\.]+"?\s*[Ss])\s*[\s,;]+\s*(\d{1,2}°\s*\d{1,2}[\'′]\s*[\d\.]+"?\s*[WwOo])', text)
        if match_dms:
            coords = f"{match_dms.group(1)} {match_dms.group(2)}"

    # 3. Se houver link do Google Maps e ainda não encontramos coordenadas no texto, tenta resolver o link encurtado
    if found_url and not coords and "maps.app.goo.gl" in found_url:
        try:
            import urllib.request
            req = urllib.request.Request(found_url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=3) as resp:
                final_url = resp.geturl()
                m_latlng = re.search(r'(-?\d{1,2}\.\d{4,8})\s*,\s*(-?\d{1,2}\.\d{4,8})', final_url)
                if m_latlng:
                    coords = f"{m_latlng.group(1)}, {m_latlng.group(2)}"
        except Exception:
            pass

    return found_url, coords


def extract_subject_fallback(text: str, filename: str = "") -> str:
    """
    Extrai deterministicamente o assunto do RELINT a partir da linha ASSUNTO: no cabeçalho
    ou, caso falhe, a partir do nome do arquivo PDF.
    """
    if text:
        match = re.search(r'(?i)ASSUNTO\s*:\s*([^\r\n]+)', text)
        if match:
            sub = match.group(1).strip()
            if len(sub) > 3:
                return sub

    if filename:
        clean_fn = re.sub(r'(?i)\.pdf$', '', filename)
        parts = [p.strip() for p in clean_fn.split(' - ') if p.strip()]
        if len(parts) >= 3:
            return " - ".join(parts[2:])
        elif len(parts) == 2:
            return parts[1]
        elif len(parts) == 1:
            return parts[0]

    return ""


def extract_fallback_summary(text: str, subject: str = "") -> str:
    """
    Gera um resumo narrativo determinístico e limpo via Regex descartando
    cabeçalhos administrativos (RELATÓRIO DE INTELIGÊNCIA..., DATA:, ORIGEM:, etc.)
    e capturando o primeiro parágrafo relevante da ocorrência.
    """
    if not text:
        return ""

    # 1. Tenta extrair a parte narrativa a partir de ANEXOS: ou descarta linhas de metadados
    match_body = re.search(r'(?i)ANEXOS?\s*:\s*(?:XXX|\w+)?\s*[\r\n]+(.*)', text, re.DOTALL)
    body = match_body.group(1).strip() if match_body else text

    # 2. Remove legendas de fotos comuns
    body = re.sub(r'(?i)(?:FOTO|IMAGEM|REGISTRO|CÂMERA)\s+D[OE]\s+[^\r\n]+', '', body)

    # 3. Divide em parágrafos e busca o primeiro parágrafo narrativo significativo
    paragraphs = [p.strip() for p in body.split('\n') if len(p.strip()) > 30]

    narrative = ""
    for p in paragraphs:
        upper_p = p.upper()
        if any(kw in upper_p for kw in ["RELATÓRIO DE INTELIGÊNCIA", "ORIGEM:", "DIFUSÃO:", "REFERÊNCIA:", "DATA:"]):
            continue
        narrative = p
        break

    if not narrative and len(body) > 0:
        narrative = body[:400]

    # Limita tamanho a 450 caracteres sem cortar palavra
    if len(narrative) > 450:
        narrative = narrative[:450].rsplit(' ', 1)[0] + "..."

    if subject and not narrative.lower().startswith(subject.lower()[:15]):
        return f"{subject}. {narrative}"
    return narrative


def clean_person_name(name: str) -> str:
    """
    Remove ruídos narrativos, prefixos relacionais e policiais, documentos grudados
    e normaliza a capitalização e pontuação dos nomes de participantes.
    """
    if not name:
        return ""

    # 1. Normaliza quebras de linha internas e espaços múltiplos
    clean = re.sub(r'[\r\n\t]+', ' ', name)
    clean = re.sub(r'[ \t]{2,}', ' ', clean).strip()

    # 2. Se contiver uma sequência pura em MAIÚSCULAS no meio ou final, extrai a parte em maiúsculas
    upper_seq = re.findall(r'\b[A-ZÀ-Ú]{2,}(?:\s+(?:DA|DE|DO|DOS|DAS|E|[A-ZÀ-Ú]{2,}))+\b', clean)
    if upper_seq:
        longest = max(upper_seq, key=len)
        if len(longest.split()) >= 2:
            clean = longest

    # 3. Remove sufixos de documentos e registros colados (RG, CPF, CNH, MATRÍCULA, etc.)
    clean = re.sub(r'(?i)\s*(?:[-–—\s]*\s*(?:RG|CPF|ID\s*FUNC|MATR[ÍI]CULA|CNH|PROCESSO|BO|DP)[:\s\.\d\-/]+.*)$', '', clean)
    clean = re.sub(r'(?i)\s+Rg$', '', clean)

    # 4. Lista refinada de prefixos policiais, judiciais e relacionais a remover
    prefix_patterns = [
        r'.*?\bidentificad[oa]\s+(?:como\s+sendo|como|de\s+nome|por)?\s*',
        r'.*?\bpres[oa]\s+(?:um\s+homem|uma\s+mulher|um\s+indiv[íi]duo|de\s+nome)?\s*',
        r'.*?\b(?:padrasto|madrasta|irm[ãa][o]|filh[oa]|pai|m[ãa]e|espos[ao]|companheir[oa]|marido|mulher|patr[ãa]o|funcion[áa]ri[oa]|gerente|vizinh[oa]|caroneiro|condutor|motorista|propriet[áa]rio)\s+',
        r'.*?\b(?:pm\s+|pme\s+|sd\s+|sgt\s+|cb\s+|ten\s+|cap\s+|maj\s+|cel\s+|policial(?:\s+militar|\s+civil|\s+penal)?\s+)',
        r'.*?\b(?:momento\s+em\s+que\s+foi\s+feito\s+contato\s+com|feito\s+contato\s+com|em\s+contato\s+com|contato\s+com)\s*',
        r'.*?\b(?:o\s+|a\s+)?(?:senhor[a]?|indiv[íi]duo|menor(?:\s+de\s+idade)?|crian[çc]a|v[íi]tima|suspeit[oa]|acusad[oa]|testemunha|comunicante|envolvid[oa]|autor[a]?)\s+',
        r'^(?:estavam?|estava|havia|foram|foi|encontrava-se)\s+',
        r'^(?:de\s+|da\s+|do\s+|dos\s+|das\s+|em\s+|no\s+|na\s+|a\s+|o\s+|e\s+|com\s+|pelo\s+|pela\s+)'
    ]

    for pat in prefix_patterns:
        clean = re.sub(r'(?i)^' + pat, '', clean)

    # 5. Limpa pontuações residuais nas pontas
    clean = clean.strip(' ,.-–—:;"\'()[]{}*')

    # 6. Formata capitalização limpa (Title Case)
    clean = clean.title() if clean.isupper() or clean.islower() else clean

    # 7. Formata preposições da língua portuguesa em minúsculas (de, da, do, dos, das, e)
    tokens = clean.split()
    if len(tokens) >= 2:
        formatted_tokens = [tokens[0]]
        for t in tokens[1:-1]:
            if t.lower() in ["da", "de", "do", "dos", "das", "e"]:
                formatted_tokens.append(t.lower())
            else:
                formatted_tokens.append(t)
        formatted_tokens.append(tokens[-1])
        clean = " ".join(formatted_tokens)

    return clean


def extract_fallback_participants(text: str) -> List[Dict[str, Any]]:
    """
    Extrai deterministicamente participantes citados no texto do RELINT delegando ao ParticipantExtractor.
    """
    if not text:
        return []
    try:
        from src.engine.extractors.deterministic.participants.participant_extractor import ParticipantExtractor
        extractor = ParticipantExtractor()
        participants, _ = extractor.extract_participants(text)
        return participants
    except Exception:
        return []





