from pathlib import Path
from typing import List, Optional
from tinydb import TinyDB, Query
from src.domain.entities import Person
from src.ports.person_repo import IPersonRepo

class TinyDbPersonRepo(IPersonRepo):
    """
    Implementação concreta (Adapter) para persistência de Pessoas (Participantes) no TinyDB.
    """

    def __init__(self, db_path: Path):
        db_path_obj = Path(db_path)
        db_path_obj.parent.mkdir(parents=True, exist_ok=True)
        self.db = TinyDB(db_path_obj, encoding="utf-8", ensure_ascii=False)

    def save(self, person: Person) -> str:
        doc_id = self.db.insert(person.model_dump())
        return str(doc_id)

    def update(self, person: Person) -> None:
        person_query = Query()
        self.db.update(person.model_dump(), person_query.person_id == person.person_id)

    def get_by_id(self, person_id: str) -> Optional[Person]:
        person_query = Query()
        doc = self.db.get(person_query.person_id == person_id)
        if doc is None:
            return None
        return Person(**dict(doc))

    def get_by_document(self, document: str) -> Optional[Person]:
        if not document:
            return None
        person_query = Query()
        # Procura se o documento informado existe na lista de documents do Person
        doc = self.db.get(person_query.documents.any(document))
        if doc is None:
            return None
        return Person(**dict(doc))

    def get_all(self) -> List[Person]:
        return [Person(**dict(doc)) for doc in self.db.all()]
