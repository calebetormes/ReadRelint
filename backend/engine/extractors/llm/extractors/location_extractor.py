# -*- coding: utf-8 -*-
"""
Extrator especializado de Localização, Endereço e Georreferenciamento via LLM (Passo 2 do Pipeline Multi-Pass).
"""

import logging
import re
import urllib.parse
import urllib.request
from typing import Any, Dict, Optional, Tuple

from backend.engine.extractors.llm.llm_processor import ILlmProcessor
from backend.engine.extractors.llm.schemas.location_schema import LocationExtraction

logger = logging.getLogger(__name__)


def sanitize_address_field(text: str) -> str:
    """
    Higieniza campos de endereço removendo ruídos narrativos, links, coordenadas e termos institucionais.
    """
    if not text:
        return ""

    s = str(text).strip()

    # 1. Trunca antes de links HTTP
    s = re.split(r'https?://', s)[0].strip()

    # 2. Trunca antes de termos de coordenadas/GPS
    s = re.split(r'(?i)\b(?:coordenadas\s*geogr[áa]ficas|coordenadas|coord\.|lat\/long|\(-?\d{1,2}\.\d+)', s)[0].strip()

    # 3. Trunca antes de verbos ou expressões narrativas institucionais
    s = re.split(
        r'(?i)\b(?:foi\s+informado|foi\s+acionad[oa]|atrav[ée]s\s+da\s+sala|via\s+telefone|chegou\s+ao\s+conhecimento|uma\s+guarni[çc][ãa]o|a\s+equipe|ap[óo]s\s+liga[çc][ãa]o|em\s+cumprimento|comunica[çc][ãa]o\s+de\s+venda|diante\s+dessas)\b',
        s
    )[0].strip()

    # 4. Remove parênteses de referências comerciais ou pontos de referência (ex: "( FARMÁCIA SÃO JOÃO )")
    s = re.sub(r'\([^\)]*\)', '', s).strip()

    # 5. Remove pontuações periféricas e ruídos isolados
    s = re.sub(r'^[,\.–—\-:;()]+|[,\.–—\-:;()]+$', '', s).strip()

    return s


def check_raw_text_geo_sources(text: str) -> Tuple[bool, bool, str, str]:
    """
    Analisa o texto bruto do documento para determinar com precisão a origem das informações geográficas:
    - has_raw_coords: True se há coordenadas explicitamente digitadas no documento.
    - has_raw_map_url: True se há link do Google Maps explicitamente presente no documento.
    Retorna: (has_raw_coords: bool, has_raw_map_url: bool, raw_coords: str, raw_map_url: str)
    """
    if not text:
        return False, False, "", ""

    # 1. Busca coordenadas explícitas no texto (decimal ou DMS)
    raw_coords = ""
    match_dec = re.search(r'(-?\d{1,2}\.\d{4,8})\s*[\s,;/]+\s*(-?\d{1,2}\.\d{4,8})', text)
    if match_dec:
        raw_coords = f"{match_dec.group(1)}, {match_dec.group(2)}"
    else:
        match_dms = re.search(r'(\d{1,2}°\s*\d{1,2}[\'′]\s*[\d\.]+\"?\s*[Ss])\s*[\s,;]+\s*(\d{1,2}°\s*\d{1,2}[\'′]\s*[\d\.]+\"?\s*[WwOo])', text)
        if match_dms:
            raw_coords = f"{match_dms.group(1)} {match_dms.group(2)}"

    # 2. Busca link explícito do Google Maps no texto
    raw_map_url = ""
    match_url = re.search(r'https?://(?:maps\.app\.goo\.gl|google\.com/maps|goo\.gl/maps)/[^\s,;><\)\']+', text)
    if match_url:
        raw_map_url = match_url.group(0).strip()

    has_coords = bool(raw_coords)
    has_map_url = bool(raw_map_url)

    return has_coords, has_map_url, raw_coords, raw_map_url


def extract_street_and_number_fallback(text: str) -> Tuple[str, str, str]:
    """
    Extrai deterministicamente rua, número e bairro do texto quando a LLM falha ou omite a rua.
    Preserva nomes compostos e abreviaturas de ruas (ex: 'Rua Elias C. Lash, 255').
    Retorna: (street, number, neighborhood)
    """
    if not text:
        return "", "", ""

    # Padrão flexível para logradouros comuns em RELINTs (sem cortar em pontos de abreviatura)
    pat = re.search(
        r'(?i)\b(?:na|no|em|localizad[oa]\s+na|localizad[oa]\s+no)\s+((?:Rua|Avenida|Av\.|Av|Travessa|Beco|Estrada|Linha|Rodovia|BR|RS)\b[^,\n\(\)]+?)(?:,\s*(?:n[oº°\.]*\s*|km\s*)?([0-9A-Za-z\/\-]+|S\/N))?(?:,\s*(?:bairro\s*)?([^,\n\(\)\-]+?))?(?:,\s*\(|\s*\(|,\s*(?:em|no|na)\s+[A-Za-zÀ-ÿ\s]+?-\s*RS|\n|-|\Z)',
        text
    )
    if pat:
        street = sanitize_address_field(pat.group(1))
        num = sanitize_address_field(pat.group(2) or "")
        neigh = sanitize_address_field(pat.group(3) or "")

        street = re.sub(r'(?i)^(?:na|no|em|localizad[oa]\s+na|localizad[oa]\s+no)\s+', '', street).strip()
        if neigh.lower().startswith("bairro"):
            neigh = re.sub(r'(?i)^bairro\s*', '', neigh).strip()
        # Se o bairro capturou 'centro de [cidade]', extrai apenas 'Centro'
        if "centro de" in neigh.lower():
            neigh = "Centro"
        return street, num, neigh

    return "", "", ""


def extract_municipality_from_context(text: str, filename: str = "") -> str:
    """
    Extrai deterministicamente o município a partir do Assunto ou do nome do arquivo.
    """
    if text:
        # Padrão: ASSUNTO: ... EM [CIDADE] - RS
        m_assunto = re.search(r'(?i)ASSUNTO\s*:\s*.*?\bem\s+([A-Za-zÀ-ÿ\s]+?)\s*-\s*RS', text)
        if m_assunto:
            muni = m_assunto.group(1).strip()
            if len(muni) > 2:
                return muni.title() if muni.isupper() else muni

    if filename:
        # Padrão no nome do arquivo: ... em [CIDADE] - RS.pdf
        m_fn = re.search(r'(?i)\bem\s+([A-Za-zÀ-ÿ\s]+?)\s*-\s*RS', filename)
        if m_fn:
            muni = m_fn.group(1).strip()
            if len(muni) > 2:
                return muni.title() if muni.isupper() else muni

    return ""


def resolve_short_maps_url(url: str, timeout: float = 3.0) -> Tuple[str, str]:
    """
    Resolve links encurtados do Google Maps (maps.app.goo.gl) seguindo o redirect
    para extrair as coordenadas latitude e longitude em formato decimal.
    Retorna tupla: (expanded_url: str, coordinates: str)
    """
    if not url or "maps.app.goo.gl" not in url:
        return url, ""

    try:
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        )
        with urllib.request.urlopen(req, timeout=timeout) as response:
            final_url = response.geturl()
            match = re.search(r'(-?\d{1,2}\.\d{4,8})\s*,\s*(-?\d{1,2}\.\d{4,8})', final_url)
            if match:
                coords = f"{match.group(1)}, {match.group(2)}"
                return final_url, coords
            return final_url, ""
    except Exception as err:
        logger.debug(f"Não foi possível resolver link encurtado {url}: {err}")
        return url, ""


def format_google_standard_address(
    street: str = "",
    number: str = "",
    neighborhood: str = "",
    municipality: str = ""
) -> str:
    """
    Monta o endereço no padrão oficial: Logradouro, nº [ou S/N] - Bairro, Município - RS
    Descarta automaticamente placeholders como 'Sem informação', 'Não informado', etc.
    """
    INVALID_PLACEHOLDERS = {
        "sem informação", "sem informacao", "não informado", "nao informado",
        "não consta", "nao consta", "não possui", "nao possui", "n/i", "n/a",
        "none", "null", "desconhecido", "xxx", "-"
    }

    clean_street = sanitize_address_field(street or "")
    clean_number = sanitize_address_field(number or "")
    clean_neigh = sanitize_address_field(neighborhood or "")
    clean_muni = sanitize_address_field(municipality or "")

    if clean_street.lower() in INVALID_PLACEHOLDERS:
        clean_street = ""
    if clean_number.lower() in INVALID_PLACEHOLDERS:
        clean_number = ""
    if clean_neigh.lower() in INVALID_PLACEHOLDERS:
        clean_neigh = ""
    if clean_muni.lower() in INVALID_PLACEHOLDERS:
        clean_muni = ""

    # Normalização de zona rural para o bairro
    is_rural = any(term in clean_street.lower() for term in ["linha", "estrada", "assentamento", "interior", "fazenda", "br-", "rs-", "rodovia"])
    if is_rural and not clean_neigh:
        clean_neigh = "Interior"

    parts = []
    if clean_street:
        if clean_number:
            # Se o número for indicação de Km (ex: 'Km 47'), anexa com vírgula se a rua já não contiver
            if "km" in clean_number.lower():
                if "km" not in clean_street.lower():
                    parts.append(f"{clean_street}, {clean_number}")
                else:
                    parts.append(clean_street)
            # Se a rua já contiver explicitamente 'nº 123' ou ', 123'
            elif re.search(r'\b(?:n[oº°]?\s*)\d+\b', clean_street, re.IGNORECASE) or re.search(r',\s*\d+\b', clean_street):
                parts.append(clean_street)
            else:
                num_str = f"nº {clean_number}" if clean_number.upper() != "S/N" else "S/N"
                parts.append(f"{clean_street}, {num_str}")
        else:
            parts.append(clean_street)

    formatted = ", ".join(parts)

    if clean_neigh and clean_neigh.lower() not in formatted.lower():
        if formatted:
            formatted = f"{formatted} - {clean_neigh}"
        else:
            formatted = clean_neigh

    if clean_muni:
        if clean_muni.lower() not in formatted.lower():
            if formatted:
                formatted = f"{formatted}, {clean_muni} - RS"
            else:
                formatted = f"{clean_muni} - RS"
        elif not formatted.endswith("- RS") and not formatted.endswith("RS"):
            formatted = f"{formatted} - RS"

    return formatted.strip(" ,-") or "-"


class LocationExtractor:
    """
    Extrator cognitivo dedicado para geolocalização, endereçamento e coordenadas.
    """

    def __init__(self, processor: ILlmProcessor) -> None:
        self.processor = processor

    def extract(self, text: str, filename: str = "") -> Dict[str, Any]:
        """
        Executa o Pass 2 focado exclusivamente na extração da localização.
        Classifica estritamente a precisão em 3 níveis:
        - Alta: Coordenadas encontradas explicitamente no texto do documento.
        - Média: Link do Google Maps encontrado no documento (coordenadas geradas via link).
        - Baixa: Somente endereço no documento (coordenadas/links gerados por busca com município).
        """
        has_raw_coords, has_raw_map_url, raw_coords, raw_map_url = check_raw_text_geo_sources(text)

        # Determina com rigor a precisão com base na fonte textual bruta
        if has_raw_coords:
            precision_level = "alta"
        elif has_raw_map_url:
            precision_level = "media"
        else:
            precision_level = "baixa"

        # Extrai município determinístico do Assunto ou do nome do arquivo
        fb_muni = extract_municipality_from_context(text, filename=filename)

        # Extrai batalhão policial (ex: '37º BPM', '39º BPM')
        fb_unit = ""
        unit_match = re.search(r'\b(\d{1,2}[º°]?\s*BPM(?:\/[A-Z\-]+)?)\b', text, re.IGNORECASE)
        if unit_match:
            fb_unit = unit_match.group(1).strip()

        data: Dict[str, Any] = {
            "street": "",
            "number": "",
            "neighborhood": "",
            "municipality": fb_muni,
            "police_unit": fb_unit,
            "address": "",
            "coordinates": raw_coords,
            "map_url": raw_map_url,
            "geo_precision": precision_level
        }

        if not text or not text.strip():
            return data

        try:
            logger.info("Executando Pass 2 (Localização) via LLM...")
            raw_response = self.processor.process_text(
                text=text,
                schema_model=LocationExtraction
            )

            if isinstance(raw_response, dict):
                data["street"] = sanitize_address_field(str(raw_response.get("street") or "").strip())
                data["number"] = sanitize_address_field(str(raw_response.get("number") or "").strip())
                data["neighborhood"] = sanitize_address_field(str(raw_response.get("neighborhood") or "").strip())
                
                extracted_muni = sanitize_address_field(str(raw_response.get("municipality") or "").strip())
                if extracted_muni and len(extracted_muni) > 2:
                    # Se o município extraído da LLM não bater com o Assunto formal, prefere o do Assunto
                    if fb_muni and fb_muni.lower() not in extracted_muni.lower() and extracted_muni.lower() not in text.lower():
                        data["municipality"] = fb_muni
                    else:
                        data["municipality"] = extracted_muni
                elif fb_muni:
                    data["municipality"] = fb_muni

                extracted_unit = str(raw_response.get("police_unit") or "").strip()
                if extracted_unit and len(extracted_unit) > 2:
                    data["police_unit"] = extracted_unit

                # Validação anti-alucinação de coordenadas:
                # Só aceita coordenadas da LLM se os dígitos existirem literalmente no texto
                extracted_coords = str(raw_response.get("coordinates") or "").strip()
                if extracted_coords and extracted_coords.lower() not in ["none", "null", ""]:
                    # Extrai o primeiro número decimal da coordenada da LLM
                    m_d = re.search(r'-?\d{2}\.\d{3,}', extracted_coords)
                    if m_d and (m_d.group(0) in text or (raw_map_url and m_d.group(0) in raw_map_url)):
                        data["coordinates"] = extracted_coords
                    elif not data["coordinates"]:
                        logger.warning(f"Descartando coordenadas alucinadas pela LLM ({extracted_coords}) pois não existem no texto.")

                # Se a LLM capturou link do maps que existe no documento
                extracted_map = str(raw_response.get("map_url") or "").strip()
                if extracted_map and extracted_map.lower() not in ["none", "null", ""] and not data["map_url"]:
                    if "maps.app.goo.gl" in extracted_map or "google.com/maps" in extracted_map:
                        data["map_url"] = extracted_map

        except Exception as err:
            logger.error(f"Erro na execução do LocationExtractor: {err}. Mantendo fallback.")

        # 1.1. Fallback determinístico de logradouro se a LLM omitiu ou colocou apenas o bairro na rua
        if data["street"].lower().startswith("bairro"):
            data["neighborhood"] = re.sub(r'(?i)^bairro\s*', '', data["street"]).strip()
            data["street"] = ""

        if not data["street"] or len(data["street"]) < 3:
            fb_street, fb_num, fb_neigh = extract_street_and_number_fallback(text)
            if fb_street:
                data["street"] = fb_street
            if fb_num and not data["number"]:
                data["number"] = fb_num
            if fb_neigh and not data["neighborhood"]:
                data["neighborhood"] = fb_neigh

        # 2. Regra de Bairro para Zona Rural:
        # Se for linha rural / rodovia / estrada e o bairro não for informado, marca 'Interior'
        is_rural = any(term in data["street"].lower() for term in ["linha", "estrada", "assentamento", "interior", "fazenda", "br-", "rs-", "rodovia"])
        if is_rural and (not data["neighborhood"] or data["neighborhood"].lower() in ["none", "null", ""]):
            data["neighborhood"] = "Interior"

        # 3. Resolução de Coordenadas do Link Encurtado (se tiver link e não tiver coords digitadas)
        if data["map_url"] and not data["coordinates"] and "maps.app.goo.gl" in data["map_url"]:
            _, resolved_coords = resolve_short_maps_url(data["map_url"])
            if resolved_coords:
                data["coordinates"] = resolved_coords

        # Normaliza formato das coordenadas
        if data["coordinates"]:
            coord_match = re.search(r'(-?\d{1,2}\.\d{4,8})\s*[\s,;/]+\s*(-?\d{1,2}\.\d{4,8})', data["coordinates"])
            if coord_match:
                data["coordinates"] = f"{coord_match.group(1)}, {coord_match.group(2)}"

        # 4. Formatação do Endereço Padrão Google (Garante Município e RS)
        formatted_addr = format_google_standard_address(
            street=data["street"],
            number=data["number"],
            neighborhood=data["neighborhood"],
            municipality=data["municipality"]
        )
        data["address"] = formatted_addr

        # 5. Geração do Link do Google Maps se não houver link no documento
        if not data["map_url"]:
            if data["coordinates"]:
                coords_clean = data["coordinates"].replace(" ", "")
                data["map_url"] = f"https://www.google.com/maps?q={coords_clean}"
            elif formatted_addr and formatted_addr != "-":
                query = urllib.parse.quote_plus(formatted_addr)
                data["map_url"] = f"https://www.google.com/maps/search/?api=1&query={query}"

        # 6. Fixa o nível de precisão estrito
        data["geo_precision"] = precision_level

        return data
