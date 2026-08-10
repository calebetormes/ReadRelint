import re
from typing import Tuple


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
    return cleaned_text.strip()

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



