import json
import sqlite3
from pathlib import Path
from typing import List, Optional
from src.domain.entities import Person
from src.ports.person_repo import IPersonRepo


class SqlitePersonRepo(IPersonRepo):
    """
    Implementação concreta (Adapter) para o repositório de Pessoas (Dossiê consolidado)
    utilizando SQLite.
    """

    def __init__(self, db_path: Path):
        """
        Inicializa o repositório de pessoas apontando para o arquivo de banco SQLite fornecido.

        :param db_path: Caminho completo para o arquivo .db do SQLite.
        """
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("PRAGMA journal_mode=WAL;")
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS persons (
                    person_id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    data TEXT NOT NULL
                );
            """)
            conn.commit()

    def save(self, person: Person) -> str:
        """
        Salva uma nova pessoa no SQLite.
        """
        person_dict = person.model_dump()
        json_data = json.dumps(person_dict, ensure_ascii=False)

        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO persons (person_id, name, data)
                VALUES (?, ?, ?)
                ON CONFLICT(person_id) DO UPDATE SET name=excluded.name, data=excluded.data;
            """, (person.person_id, person.name, json_data))
            conn.commit()
            return person.person_id

    def update(self, person: Person) -> None:
        """
        Atualiza uma pessoa existente no SQLite.
        """
        self.save(person)

    def get_by_id(self, person_id: str) -> Optional[Person]:
        """
        Busca uma pessoa no SQLite pelo seu ID único.
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT data FROM persons WHERE person_id = ? LIMIT 1;", (person_id,))
            row = cursor.fetchone()
            if not row:
                return None
            data_dict = json.loads(row["data"])
            return Person(**data_dict)

    def get_by_document(self, document: str) -> Optional[Person]:
        """
        Busca uma pessoa pelo número de documento (RG/CPF).
        """
        if not document:
            return None
        clean_doc = document.strip().replace(".", "").replace("-", "")

        for p in self.get_all():
            for doc in p.documents:
                if doc and doc.strip().replace(".", "").replace("-", "") == clean_doc:
                    return p
        return None

    def get_all(self) -> List[Person]:
        """
        Retorna todas as pessoas cadastradas no banco SQLite.
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT data FROM persons ORDER BY name ASC;")
            rows = cursor.fetchall()
            persons = []
            for row in rows:
                try:
                    data_dict = json.loads(row["data"])
                    persons.append(Person(**data_dict))
                except Exception:
                    pass
            return persons

    def clear_all(self) -> None:
        """
        Remove todas as pessoas cadastradas no banco SQLite.
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM persons;")
            conn.commit()

