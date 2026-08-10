from pathlib import Path
import re
from typing import List, Dict, Any, Tuple
from src.adapters.tinydb_repo import TinyDbRepo
from src.application.text_cleaner import (
    extract_date_of_fact,
    extract_time_of_fact,
    extract_map_url,
    resolve_coordinates_and_map_info
)

def clean_html(html_str: str) -> str:
    """Remove todo recuo de linha do HTML para evitar que o Markdown do Streamlit o converta em bloco de código."""
    if not html_str:
        return ""
    return "\n".join(line.strip() for line in html_str.splitlines() if line.strip())

def get_participant_field(p: Any, field_name: str, default: str = "") -> str:
    """Extrai campo de participante de forma segura, seja ele dicionário ou objeto Pydantic."""
    if isinstance(p, dict):
        return p.get(field_name) or default
    return getattr(p, field_name, default) or default


def get_report_date_of_fact(r: Any) -> str:
    """Extrai a data do fato do objeto de relatório ou executa o fallback heurístico no texto."""
    date_val = getattr(r, "date_of_fact", None) or getattr(r, "modification_date_history", None)
    if date_val and str(date_val).strip() and str(date_val).strip() not in ["Não Informado", "None"]:
        return str(date_val).strip()
    
    content = getattr(r, "content", "") or ""
    extracted = extract_date_of_fact(content)
    return extracted if extracted else "Não Informado"

def get_report_time_of_fact(r: Any) -> str:
    """Extrai a hora do fato do objeto de relatório ou executa o fallback heurístico no texto."""
    time_val = getattr(r, "time_of_fact", None)
    if time_val and str(time_val).strip() and str(time_val).strip() not in ["Não Informado", "None"]:
        return str(time_val).strip()
    
    content = getattr(r, "content", "") or ""
    extracted = extract_time_of_fact(content)
    return extracted if extracted else "Não Informado"

def get_report_map_info(r: Any) -> Tuple[str, str, str, str]:
    """
    Retorna a tupla (map_url, coordinates, precision_level, precision_label).
    Garante que SEMPRE teremos um link do Google Maps e uma classificação de precisão.

    precision_level:
      - 'exact_coords': Alta Precisão (Verde #059669) - Coordenadas Lat/Lng exatas no RELINT.
      - 'direct_link':  Média Precisão (Azul #0284c7) - Link do Google Maps citado no RELINT.
      - 'address_inferred': Precisão Estimada (Laranja #d97706) - Gerado por busca do endereço.
      - 'unknown': Sem Localização (Cinza #475569) - Nenhuma informação de local.
    """
    import urllib.parse

    map_url = getattr(r, "map_url", None) or ""
    coords = getattr(r, "coordinates", None) or ""
    
    content = getattr(r, "content", "") or ""
    res_url, res_coords = resolve_coordinates_and_map_info(content, map_url=map_url if map_url not in ["Não Informado", "None"] else "")
    
    final_coords = coords if (coords and coords not in ["Não Informado", "None"]) else res_coords
    final_url = map_url if (map_url and map_url not in ["Não Informado", "None"]) else res_url
    
    # 1. Prioridade 1: Coordenadas Exatas (ALTA PRECISÃO - VERDE)
    if final_coords:
        if not final_url:
            query_coords = urllib.parse.quote(final_coords)
            final_url = f"https://www.google.com/maps/search/?api=1&query={query_coords}"
        return final_url, final_coords, "exact_coords", "Alta Precisão (Coordenadas Exatas)"
        
    # 2. Prioridade 2: Link Direto citado no RELINT (MÉDIA PRECISÃO - AZUL)
    if final_url:
        return final_url, "", "direct_link", "Precisão Média (Link Citado no RELINT)"

    # 3. Prioridade 3: Gerar link via busca do endereço estruturado (PRECISÃO ESTIMADA - LARANJA)
    addr_info = get_report_structured_address(r)
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




def get_report_structured_address(r: Any) -> Dict[str, str]:
    """Retorna os campos de endereço estruturados (municipality, street, number, neighborhood)."""
    muni = getattr(r, "municipality", None) or ""
    street = getattr(r, "street", None) or ""
    num = getattr(r, "number", None) or ""
    neigh = getattr(r, "neighborhood", None) or ""

    addr_raw = getattr(r, "address", "") or ""
    content = getattr(r, "content", "") or ""
    text_source = (addr_raw + " " + content)

    if not muni or muni in ["Não Informado", "None"]:
        cidades = [
            "VITÓRIA", "VILA VELHA", "SERRA", "CARIACICA", "VIANA", "GUARAPARI",
            "CACHOEIRO DE ITAPEMIRIM", "LINHARES", "SÃO MATEUS", "COLATINA",
            "PANAMBI", "IBIRUBÁ", "PALMEIRA DAS MISSÕES", "RODEIO BONITO",
            "SANTA BÁRBARA DO SUL", "ERVAL SECO", "CRUZ ALTA"
        ]
        for c in cidades:
            if c in text_source.upper():
                muni = c.title()
                break
        if not muni: muni = "Não Informado"

    if not neigh or neigh in ["Não Informado", "None"]:
        m_bairro = re.search(r'(?i)bairro\s+([a-zA-Z\u00C0-\u00FF\s\-]+?)(?:,|\sen\b|\sem\b|\s-|\.|$)', text_source)
        neigh = m_bairro.group(1).strip() if m_bairro else "Não Informado"

    if not street or street in ["Não Informado", "None"]:
        m_rua = re.search(r'(?i)\b(rua|av\.|avenida|travessa|rodovia|alameda)\s+([a-zA-Z\u00C0-\u00FF\s0-9\-]+?)(?:,|\snº|\sno\b|\sn\b|\.|$)', text_source)
        street = f"{m_rua.group(1).capitalize()} {m_rua.group(2).strip()}" if m_rua else "Não Informado"

    if not num or num in ["Não Informado", "None"]:
        m_num = re.search(r'(?i)\b(?:nº|n°|nº\.|n°\.|nº\s*|n°\s*|número\s*)\s*(\d+|s/n)\b', text_source)
        num = m_num.group(1).strip() if m_num else "S/N"

    return {
        "municipality": muni,
        "street": street,
        "number": num,
        "neighborhood": neigh
    }



def load_data() -> Tuple[List[Any], Path]:
    """Carrega dados do relatório de inteligência usando TinyDbRepo."""
    db_path = Path("data/relints.json")
    if not db_path.exists():
        db_path = Path("data/homicides.json")
        if not db_path.exists():
            return [], Path("data/relints.json")
    repo = TinyDbRepo(db_path)
    return repo.get_all(), db_path

def find_vinculos(current_file: str, name: str, doc: str, all_reports: List[Any]) -> List[str]:
    """Procura por outros relatórios que citem o mesmo participante (por nome ou documento)."""
    vinculos = []
    clean_name = (name or "").strip().lower()
    clean_doc = (doc or "").strip().replace(".", "").replace("-", "")
    
    if not clean_name and not clean_doc:
        return vinculos
        
    for r in all_reports:
        if r.source_file == current_file:
            continue
        parts = r.participants or []
        for p in parts:
            p_name = get_participant_field(p, "name")
            p_doc = get_participant_field(p, "document")
            
            p_clean_name = p_name.strip().lower()
            p_clean_doc = p_doc.strip().replace(".", "").replace("-", "")
            
            if clean_doc and p_clean_doc and clean_doc == p_clean_doc:
                vinculos.append(r.source_file)
                break
            elif clean_name and p_clean_name and clean_name == p_clean_name and len(clean_name) > 4:
                vinculos.append(r.source_file)
                break
    return sorted(list(set(vinculos)))

def filter_reports(reports: List[Any], search_query: str, selected_groups: List[str]) -> List[Any]:
    """Filtra a lista de relatórios com base na consulta de pesquisa e grupos BM selecionados."""
    filtered_reports = []
    for r in reports:
        subject = getattr(r, "subject", "Sem Assunto") or "Sem Assunto"
        bm_group = getattr(r, "bm_group", "Outros") or "Outros"
        date_of_fact = getattr(r, "date_of_fact", "Não Informado") or "Não Informado"
        summary = getattr(r, "summary", "") or ""
        content = getattr(r, "content", "") or ""
        
        if bm_group not in selected_groups:
            continue
            
        match_search = True
        if search_query:
            query = search_query.lower()
            participants_text = ""
            for p in (r.participants or []):
                p_name = get_participant_field(p, "name")
                p_nick = get_participant_field(p, "nickname")
                p_doc = get_participant_field(p, "document")
                participants_text += f" {p_name} {p_nick} {p_doc}"
                
            match_search = (
                query in r.source_file.lower() or
                query in subject.lower() or
                query in summary.lower() or
                query in content.lower() or
                query in bm_group.lower() or
                query in date_of_fact.lower() or
                query in participants_text.lower()
            )
            
        if match_search:
            filtered_reports.append(r)
    return filtered_reports

def get_persons_data(reports: List[Any]) -> List[Dict[str, Any]]:
    """
    Carrega ou agrega pessoas consolidadas (dossiê) a partir dos relatórios ou do repo de pessoas.
    Garante resiliência mesmo se o banco participants.json ainda não tiver sido populado pelo ETL.
    """
    persons_map: Dict[str, Dict[str, Any]] = {}
    
    # 1. Tentar ler do banco dedicado se existir
    part_db_path = Path("data/participants.json")
    if part_db_path.exists():
        try:
            from src.adapters.tinydb_person_repo import TinyDbPersonRepo
            repo = TinyDbPersonRepo(part_db_path)
            for p in repo.get_all():
                key = p.person_id
                persons_map[key] = {
                    "person_id": p.person_id,
                    "name": p.name,
                    "aliases": p.aliases,
                    "documents": p.documents,
                    "linked_relints": p.linked_relints,
                    "participation_types": [],
                    "backgrounds": []
                }
        except Exception:
            pass

    # 2. Se a leitura do banco não trouxe registros ou se queremos enriquecer com os relatórios atuais:
    for r in reports:
        source_file = r.source_file
        for p in (r.participants or []):
            name = get_participant_field(p, "name")
            nick = get_participant_field(p, "nickname")
            doc = get_participant_field(p, "document")
            bg = get_participant_field(p, "background")
            ptype = get_participant_field(p, "participation_type")

            if not name and not nick and not doc:
                continue

            # Chave única baseada em documento ou nome limpo
            key = doc.strip().replace(".", "").replace("-", "") if doc and doc.strip() else name.strip().lower()
            if not key:
                key = nick.strip().lower()

            if key not in persons_map:
                persons_map[key] = {
                    "person_id": key,
                    "name": name if name else (nick if nick else "Desconhecido"),
                    "aliases": [nick] if nick else [],
                    "documents": [doc] if doc else [],
                    "linked_relints": [source_file],
                    "participation_types": [ptype] if ptype else [],
                    "backgrounds": [bg] if bg else []
                }
            else:
                entry = persons_map[key]
                if name and entry["name"] in ["Desconhecido", ""] and name != entry["name"]:
                    entry["name"] = name
                if nick and nick not in entry["aliases"]:
                    entry["aliases"].append(nick)
                if doc and doc not in entry["documents"]:
                    entry["documents"].append(doc)
                if source_file not in entry["linked_relints"]:
                    entry["linked_relints"].append(source_file)
                if ptype and ptype not in entry["participation_types"]:
                    entry["participation_types"].append(ptype)
                if bg and bg not in entry["backgrounds"]:
                    entry["backgrounds"].append(bg)

    return list(persons_map.values())

def get_municipalities_data(reports: List[Any]) -> List[Dict[str, Any]]:
    """
    Carrega ou agrega dados de municípios (Mancha Criminal Territorial).
    """
    muni_map: Dict[str, Dict[str, Any]] = {}

    # 1. Tentar ler do banco dedicado se existir
    muni_db_path = Path("data/municipalities.json")
    if muni_db_path.exists():
        try:
            from src.adapters.tinydb_municipality_repo import TinyDbMunicipalityRepo
            repo = TinyDbMunicipalityRepo(muni_db_path)
            for m in repo.get_all():
                muni_map[m.name.upper()] = {
                    "name": m.name,
                    "state": m.state,
                    "linked_relints": m.linked_relints,
                    "stats_by_group": m.stats_by_group
                }
        except Exception:
            pass

    # 2. Agregar dos relatórios
    cidades_conhecidas = [
        "VITÓRIA", "VILA VELHA", "SERRA", "CARIACICA", "VIANA", "GUARAPARI",
        "CACHOEIRO DE ITAPEMIRIM", "LINHARES", "SÃO MATEUS", "COLATINA",
        "ARACRUZ", "BARRA DE SÃO FRANCISCO", "MARATAÍZES", "ANCHIETA"
    ]

    for r in reports:
        address = getattr(r, "address", "") or ""
        content = getattr(r, "content", "") or ""
        bm_group = getattr(r, "bm_group", "Outros")
        if hasattr(bm_group, "value"):
            bm_group = bm_group.value
        elif not bm_group:
            bm_group = "Outros"

        # Tentar extrair cidade do endereço ou texto
        found_city = None
        combined_text = (address + " " + content).upper()
        for c in cidades_conhecidas:
            if c in combined_text:
                found_city = c.capitalize()
                break

        if not found_city:
            found_city = "Não Identificado"

        if found_city not in muni_map:
            muni_map[found_city] = {
                "name": found_city,
                "state": "ES",
                "linked_relints": [r.source_file],
                "stats_by_group": {bm_group: 1}
            }
        else:
            entry = muni_map[found_city]
            if r.source_file not in entry["linked_relints"]:
                entry["linked_relints"].append(r.source_file)
            stats = entry["stats_by_group"]
            stats[bm_group] = stats.get(bm_group, 0) + 1

    return list(muni_map.values())

def get_crime_stats(reports: List[Any]) -> Dict[str, Any]:
    """
    Calcula agregados estatísticos por Grupo BM para o painel analítico de crimes.
    """
    stats: Dict[str, int] = {}
    reports_by_group: Dict[str, List[Any]] = {}

    for r in reports:
        bm_group = getattr(r, "bm_group", "Outros")
        if hasattr(bm_group, "value"):
            bm_group = bm_group.value
        elif not bm_group:
            bm_group = "Outros"

        stats[bm_group] = stats.get(bm_group, 0) + 1
        if bm_group not in reports_by_group:
            reports_by_group[bm_group] = []
        reports_by_group[bm_group].append(r)

    return {
        "group_counts": stats,
        "reports_by_group": reports_by_group,
        "total_reports": len(reports)
    }

