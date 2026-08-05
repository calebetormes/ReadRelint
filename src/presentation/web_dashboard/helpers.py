from pathlib import Path
from typing import List, Dict, Any, Tuple
from src.adapters.tinydb_repo import TinyDbRepo

def get_participant_field(p: Any, field_name: str, default: str = "") -> str:
    """Extrai campo de participante de forma segura, seja ele dicionário ou objeto Pydantic."""
    if isinstance(p, dict):
        return p.get(field_name) or default
    return getattr(p, field_name, default) or default

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
