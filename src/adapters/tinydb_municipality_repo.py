from pathlib import Path
from typing import List, Optional
from tinydb import TinyDB, Query
from src.domain.entities import Municipality
from src.ports.municipality_repo import IMunicipalityRepo

class TinyDbMunicipalityRepo(IMunicipalityRepo):
    """
    Implementação concreta (Adapter) para persistência de Municípios (Mancha Criminal) no TinyDB.
    """

    def __init__(self, db_path: Path):
        db_path_obj = Path(db_path)
        db_path_obj.parent.mkdir(parents=True, exist_ok=True)
        self.db = TinyDB(db_path_obj, encoding="utf-8", ensure_ascii=False)

    def save(self, municipality: Municipality) -> str:
        doc_id = self.db.insert(municipality.model_dump())
        return str(doc_id)

    def update(self, municipality: Municipality) -> None:
        mun_query = Query()
        self.db.update(municipality.model_dump(), mun_query.name == municipality.name)

    def get_by_name(self, name: str) -> Optional[Municipality]:
        if not name:
            return None
        mun_query = Query()
        doc = self.db.get(mun_query.name.matches(name, flags=2)) # flags=2 (re.IGNORECASE)
        if doc is None:
            return None
        return Municipality(**dict(doc))

    def get_all(self) -> List[Municipality]:
        return [Municipality(**dict(doc)) for doc in self.db.all()]
