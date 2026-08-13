"""
Geolocation and Address Resolution Service.
Provides deterministic extraction, fallback parsing, Google Maps URL generation,
and 3-level precision categorization for RELINT reports.
"""
import re
import urllib.parse
from typing import Dict, Any, Tuple
from src.application.text_cleaner import resolve_coordinates_and_map_info

# Common Rio Grande do Sul and Espírito Santo municipalities for regex fallback
KNOWN_MUNICIPALITIES = [
    "IBIRUBÁ", "PANAMBI", "PALMEIRA DAS MISSÕES", "RODEIO BONITO",
    "SANTA BÁRBARA DO SUL", "ERVAL SECO", "CRUZ ALTA", "PASSO FUNDO",
    "IJUÍ", "CARAZINHO", "SANTA ROSA", "ERVAL SECO", "CHAPADA",
    "VITÓRIA", "VILA VELHA", "SERRA", "CARIACICA", "VIANA", "GUARAPARI",
    "CACHOEIRO DE ITAPEMIRIM", "LINHARES", "SÃO MATEUS", "COLATINA"
]

def extract_structured_address(report: Any) -> Dict[str, str]:
    """
    Extracts structured address fields (municipality, street, number, neighborhood)
    from report attributes with deterministic regex fallback on the report text.
    """
    muni = getattr(report, "municipality", None) or ""
    street = getattr(report, "street", None) or ""
    num = getattr(report, "number", None) or ""
    neigh = getattr(report, "neighborhood", None) or ""
    addr_raw = getattr(report, "address", None) or ""
    content = getattr(report, "content", None) or ""
    
    text_source = f"{addr_raw} {content}".strip()

    # 1. Municipality Fallback
    if not muni or muni in ["Não Informado", "None", ""]:
        for c in KNOWN_MUNICIPALITIES:
            if re.search(r'\b' + re.escape(c) + r'\b', text_source, re.IGNORECASE):
                muni = c.title()
                break
        if not muni or muni in ["None", ""]:
            muni = "Não Informado"

    # 2. Neighborhood Fallback
    if not neigh or neigh in ["Não Informado", "None", ""]:
        m_bairro = re.search(r'(?i)bairro\s+([a-zA-Z\u00C0-\u00FF\s\-]+?)(?:,|\sen\b|\sem\b|\s-|\.|$)', text_source)
        if m_bairro:
            neigh = m_bairro.group(1).strip()
        else:
            neigh = "Não Informado"

    # 3. Street Fallback
    if not street or street in ["Não Informado", "None", ""]:
        m_rua = re.search(
            r'(?i)\b(rua|av\.|avenida|travessa|rodovia|alameda)\s+([a-zA-Z\u00C0-\u00FF\s0-9\-]+?)(?:,|\snº|\sn°|\sno\b|\sn\b|\.|$)',
            text_source
        )
        if m_rua:
            street = f"{m_rua.group(1).capitalize()} {m_rua.group(2).strip()}"
        else:
            street = "Não Informado"

    # 4. Number Fallback
    if not num or num in ["Não Informado", "None", ""]:
        m_num = re.search(r'(?i)\b(?:nº|n°|nº\.|n°\.|nº\s*|n°\s*|número\s*)\s*(\d+|s/n)\b', text_source)
        if m_num:
            num = m_num.group(1).strip()
        else:
            num = "S/N"

    # Assemble formatted address string
    components = []
    if street != "Não Informado":
        components.append(street)
    if num not in ["S/N", "Não Informado", "None"]:
        components.append(f"nº {num}")
    elif street != "Não Informado":
        components.append("S/N")
    if neigh != "Não Informado":
        components.append(f"Bairro {neigh}")
    if muni != "Não Informado":
        components.append(f"{muni} - RS")

    formatted_address = ", ".join(components) if components else (addr_raw if addr_raw not in ["Não Informado", "None"] else "Endereço não informado")

    return {
        "municipality": muni,
        "street": street,
        "number": num,
        "neighborhood": neigh,
        "formatted_address": formatted_address
    }

def resolve_report_map_info(report: Any) -> Tuple[str, str, str, str]:
    """
    Resolves geolocation information, returning:
    (map_url, coordinates, precision_level, precision_label)

    precision_level:
      - 'exact_coords': Alta Precisão (Verde) - Lat/Lng exatas no RELINT.
      - 'direct_link':  Média Precisão (Azul) - Link do Google Maps no RELINT.
      - 'address_inferred': Precisão Estimada (Laranja) - Gerado via busca do endereço.
      - 'unknown': Sem Localização (Cinza) - Nenhuma informação.
    """
    map_url = getattr(report, "map_url", None) or ""
    coords = getattr(report, "coordinates", None) or ""
    content = getattr(report, "content", None) or ""

    res_url, res_coords = resolve_coordinates_and_map_info(content, map_url=map_url if map_url not in ["Não Informado", "None"] else "")
    
    final_coords = coords if (coords and coords not in ["Não Informado", "None"]) else res_coords
    final_url = map_url if (map_url and map_url not in ["Não Informado", "None"]) else res_url

    # 1. Exact Coordinates (Alta Precisão)
    if final_coords:
        if not final_url:
            query_coords = urllib.parse.quote(final_coords)
            final_url = f"https://www.google.com/maps/search/?api=1&query={query_coords}"
        return final_url, final_coords, "exact_coords", "Alta Precisão (Coordenadas Exatas)"

    # 2. Direct Link in RELINT (Média Precisão)
    if final_url:
        return final_url, "", "direct_link", "Precisão Média (Link Citado no RELINT)"

    # 3. Inferred Address Search (Precisão Estimada)
    addr_info = extract_structured_address(report)
    query_parts = []
    if addr_info["street"] != "Não Informado":
        query_parts.append(addr_info["street"])
    if addr_info["number"] not in ["S/N", "Não Informado", "None"]:
        query_parts.append(addr_info["number"])
    if addr_info["neighborhood"] != "Não Informado":
        query_parts.append(f"Bairro {addr_info['neighborhood']}")
    if addr_info["municipality"] != "Não Informado":
        query_parts.append(f"{addr_info['municipality']} - RS")

    if query_parts:
        query_str = urllib.parse.quote(", ".join(query_parts))
        generated_url = f"https://www.google.com/maps/search/?api=1&query={query_str}"
        return generated_url, "", "address_inferred", "Precisão Estimada (Busca por Endereço)"

    return "", "", "unknown", "Sem Dados de Localização"
