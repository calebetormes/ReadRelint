# -*- coding: utf-8 -*-
"""
Validador, sanitizador e resolvedor de mapas e endereços para saídas da LLM.
"""

import re
import urllib.parse
from typing import Dict, Any, Tuple


def sanitize_summary(summary: Any, subject: str = "") -> str:
    """
    Sanitiza o texto da síntese removendo chavões residuais de preâmbulo policial.
    Se a síntese for muito curta ou idêntica ao assunto (preguiça da LLM), retorna vazio
    para forçar o fallback do Regex.
    """
    if not summary or isinstance(summary, bool):
        return ""

    text = str(summary).strip()

    # Remove preâmbulos comuns
    patterns_to_remove = [
        r'(?i)^chegando\s+ao\s+local,?\s*(?:a\s+guarni[çc][ãa]o\s+)?(?:constatou|relatou)\s+que\s*,?\s*',
        r'(?i)^conforme\s+(?:boletim|relat[oó]rio|informa[çc][õo]es|registro)[^,:]*[,:]\s*',
        r'(?i)^em\s+data\s+de\s+\d{2}/\d{2}/\d{4},?\s*',
        r'(?i)^na\s+data\s+supracitada,?\s*'
    ]

    for pat in patterns_to_remove:
        text = re.sub(pat, '', text).strip()

    # Garante primeira letra maiúscula
    if text:
        text = text[0].upper() + text[1:]

    # Trava inteligente B1: Rejeitar se for idêntica ao subject ou muito curta
    if subject and text:
        # Se o texto da síntese começar quase exatamente igual ao subject, é plágio da LLM
        if text.lower().startswith(subject.lower()[:30]) or len(text) < 50:
            return ""

    return text


def format_address_and_maps(raw_data: Dict[str, Any]) -> Tuple[str, str, str]:
    """
    Formata o endereço no padrão 'Rua, nº - Município' e gera os links e coordenadas
    oficiais no padrão do Google Maps.

    Retorna: (formatted_address: str, map_url: str, coordinates: str)
    """
    def _safe_str(val: Any) -> str:
        if isinstance(val, bool) or val is None:
            return ""
        return str(val).strip()

    street = _safe_str(raw_data.get("street") or raw_data.get("address"))
    number = _safe_str(raw_data.get("number"))
    municipality = _safe_str(raw_data.get("municipality") or raw_data.get("municipio"))
    raw_coords = _safe_str(raw_data.get("coordinates"))
    raw_map_url = _safe_str(raw_data.get("map_url"))

    # 1. Montagem do endereço simplificado: Rua, nº - Município
    address_parts = []
    if street:
        if number and number.lower() not in ["none", "null", ""]:
            # Se a rua já tiver o número embutido, evita duplicar
            if re.search(r'\b(?:n[oº°]?\s*)?\d+\b', street):
                address_parts.append(street)
            else:
                num_str = f"nº {number}" if number.upper() != "S/N" else "S/N"
                address_parts.append(f"{street}, {num_str}")
        else:
            address_parts.append(street)

    formatted_address = ", ".join(address_parts)
    if formatted_address and municipality and municipality.lower() not in formatted_address.lower():
        formatted_address = f"{formatted_address} - {municipality}"
    elif not formatted_address and municipality:
        formatted_address = municipality

    # 2. Normalização de Coordenadas Google Maps (-29.xxxx, -51.xxxx)
    clean_coords = ""
    if raw_coords and raw_coords.lower() not in ["none", "null", ""]:
        # Tenta extrair par decimal de latitude e longitude
        coord_match = re.search(r'(-?\d{1,2}\.\d+)[,\s]+(-?\d{1,3}\.\d+)', raw_coords)
        if coord_match:
            clean_coords = f"{coord_match.group(1)}, {coord_match.group(2)}"
        else:
            clean_coords = raw_coords

    # 3. Geração do Link do Google Maps
    final_map_url = ""
    if raw_map_url and "google.com/maps" in raw_map_url or "maps.app.goo.gl" in raw_map_url:
        final_map_url = raw_map_url
    elif clean_coords:
        coords_for_url = clean_coords.replace(" ", "")
        final_map_url = f"https://www.google.com/maps?q={coords_for_url}"
    elif formatted_address:
        query = urllib.parse.quote_plus(formatted_address)
        final_map_url = f"https://www.google.com/maps/search/?api=1&query={query}"

    return formatted_address, final_map_url, clean_coords


def validate_and_normalize_llm_response(raw_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Valida e normaliza o dicionário extraído pela LLM antes de salvar.
    """
    if not isinstance(raw_data, dict):
        return {}

    normalized = dict(raw_data)

    # 1. Sanitiza a síntese
    summary = normalized.get("summary") or normalized.get("resumo") or ""
    subject = normalized.get("subject") or normalized.get("assunto") or ""
    normalized["summary"] = sanitize_summary(summary, subject=subject)

    # 2. Formata endereço simplificado e resolve Google Maps
    address, map_url, coords = format_address_and_maps(normalized)
    normalized["address"] = address
    normalized["map_url"] = map_url
    normalized["coordinates"] = coords

    return normalized
