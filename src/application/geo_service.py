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
    Extracts structured address fields (municipality, neighborhood, address)
    from report attributes with deterministic regex fallback on the report text.
    """
    muni = getattr(report, "municipality", None) or ""
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

    # Assemble formatted address string
    formatted_address = addr_raw if addr_raw not in ["Não Informado", "None", ""] else ""
    if not formatted_address:
        components = []
        if neigh != "Não Informado":
            components.append(f"Bairro {neigh}")
        if muni != "Não Informado":
            components.append(f"{muni} - RS")
        formatted_address = ", ".join(components) if components else "Endereço não informado"

    return {
        "municipality": muni,
        "neighborhood": neigh,
        "formatted_address": formatted_address
    }

MUNICIPALITY_CENTROIDS: Dict[str, Tuple[str, str]] = {
    "PANAMBI": ("-28.2926", "-53.5019"),
    "IBIRUBÁ": ("-28.6275", "-53.0905"),
    "PALMEIRA DAS MISSÕES": ("-27.8986", "-53.3136"),
    "RODEIO BONITO": ("-27.4725", "-53.0450"),
    "SANTA BÁRBARA DO SUL": ("-28.3653", "-53.2483"),
    "ERVAL SECO": ("-27.5333", "-53.5019"),
    "CRUZ ALTA": ("-28.6386", "-53.6064"),
    "PASSO FUNDO": ("-28.2612", "-52.4083"),
    "IJUÍ": ("-28.3875", "-53.9147"),
    "CARAZINHO": ("-28.2839", "-52.7864"),
    "SANTA ROSA": ("-27.8719", "-54.4806"),
    "CHAPADA": ("-28.0558", "-53.0678"),
    "BOA VISTA DO INCRA": ("-28.5639", "-53.2425"),
    "VITÓRIA": ("-20.3155", "-40.3128"),
    "VILA VELHA": ("-20.3297", "-40.2925"),
    "SERRA": ("-20.1286", "-40.3078"),
    "CARIACICA": ("-20.2639", "-40.4200"),
    "VIANA": ("-20.3906", "-40.4678"),
    "GUARAPARI": ("-20.6728", "-40.4981"),
    "CACHOEIRO DE ITAPEMIRIM": ("-20.8489", "-41.1128"),
    "LINHARES": ("-19.3911", "-40.0722"),
    "SÃO MATEUS": ("-18.7161", "-39.8589"),
    "COLATINA": ("-19.5389", "-40.6300"),
}
DEFAULT_RS_CENTROID = ("-28.3000", "-53.3000")

def resolve_report_map_info(report: Any) -> Tuple[str, str, str, str]:
    """
    Resolves geolocation information, ALWAYS returning a valid:
    (map_url, coordinates, precision_level, precision_label)

    precision_level:
      - 'exact_coords': Alta Precisão (Verde) - Coordenadas GPS exatas no RELINT.
      - 'direct_link':  Precisão Média (Azul) - Link direto citado no RELINT.
      - 'address_inferred': Precisão Estimada (Laranja) - Busca por endereço com coordenadas aproximadas.
      - 'low_precision': Precisão Geral / Baixa (Amarelo) - Coordenadas estimadas por Município/Região.
    """
    map_url = getattr(report, "map_url", None) or ""
    coords = getattr(report, "coordinates", None) or ""
    content = getattr(report, "content", None) or ""

    res_url, res_coords = resolve_coordinates_and_map_info(content, map_url=map_url if map_url not in ["Não Informado", "None"] else "")
    
    final_coords = coords if (coords and coords not in ["Não Informado", "None"]) else res_coords
    final_url = map_url if (map_url and map_url not in ["Não Informado", "None"]) else res_url

    # 1. Exact Coordinates present (Alta Precisão)
    if final_coords:
        if not final_url:
            query_coords = urllib.parse.quote(final_coords)
            final_url = f"https://www.google.com/maps/search/?api=1&query={query_coords}"
        return final_url, final_coords, "exact_coords", "Alta Precisão (Coordenadas Exatas)"

    # Resolve estimated centroid coordinates for municipality fallback
    addr_info = extract_structured_address(report)
    muni_name = (addr_info.get("municipality") or "").strip().upper()
    est_lat, est_lng = MUNICIPALITY_CENTROIDS.get(muni_name, DEFAULT_RS_CENTROID)
    inferred_coords = f"{est_lat}, {est_lng} (Aproximado)"

    # 2. Direct Link present in RELINT (Precisão Média)
    if final_url:
        return final_url, inferred_coords, "direct_link", "Precisão Média (Link Citado no RELINT)"

    # 3. Inferred Address Search (Precisão Estimada)
    query_parts = []
    if addr_info["formatted_address"] and addr_info["formatted_address"] != "Endereço não informado":
        query_parts.append(addr_info["formatted_address"])
    elif addr_info["municipality"] != "Não Informado":
        query_parts.append(f"{addr_info['municipality']} - RS")

    if query_parts:
        query_str = urllib.parse.quote(", ".join(query_parts))
        generated_url = f"https://www.google.com/maps/search/?api=1&query={query_str}"
        return generated_url, inferred_coords, "address_inferred", "Precisão Estimada (Busca por Endereço)"

    # 4. Low Precision Fallback (Sempre cria URL e Coordenadas por Município ou Estado)
    muni_query = addr_info["municipality"] if addr_info["municipality"] != "Não Informado" else "Rio Grande do Sul"
    query_str = urllib.parse.quote(f"{muni_query} - RS")
    generated_url = f"https://www.google.com/maps/search/?api=1&query={query_str}"
    
    return generated_url, inferred_coords, "low_precision", "Precisão Geral (Município / Região)"
