import sqlite3
from pathlib import Path
from typing import List, Optional
from datetime import datetime
from src.domain.entities import Person
from src.ports.person_repo import IPersonRepo


class SqlitePersonRepo(IPersonRepo):
    """
    Implementação concreta (Adapter) para o repositório de Pessoas (Dossiê consolidado)
    utilizando a tabela relacional normalizada 'persons' e junções com 'relint_participants'.
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
        conn.execute("PRAGMA foreign_keys = ON;")
        return conn

    def _init_db(self) -> None:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("PRAGMA journal_mode=WAL;")
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS relints (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    source_file TEXT UNIQUE NOT NULL,
                    subject TEXT,
                    main_fact TEXT,
                    date_of_fact TEXT,
                    time_of_fact TEXT,
                    bm_group TEXT,
                    relint_type TEXT,
                    municipality TEXT,
                    neighborhood TEXT,
                    address TEXT,
                    police_unit TEXT,
                    coordinates TEXT,
                    map_url TEXT,
                    summary TEXT,
                    content TEXT,
                    user_edited INTEGER DEFAULT 0
                );
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS persons (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    person_key TEXT UNIQUE NOT NULL,
                    name TEXT NOT NULL,
                    nickname TEXT,
                    document TEXT,
                    background TEXT
                );
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS relint_participants (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    relint_id INTEGER NOT NULL,
                    person_id INTEGER NOT NULL,
                    participation_type TEXT,
                    photo_path TEXT,
                    FOREIGN KEY (relint_id) REFERENCES relints(id) ON DELETE CASCADE,
                    FOREIGN KEY (person_id) REFERENCES persons(id) ON DELETE CASCADE
                );
            """)
            conn.commit()

    def save(self, person: Person) -> str:
        """
        Salva ou atualiza uma pessoa no SQLite.
        """
        p_name = person.name.strip()
        p_doc = (person.documents[0] if person.documents else "") or ""
        clean_doc = p_doc.replace(".", "").replace("-", "") if p_doc else ""
        p_key = person.person_id or (clean_doc if clean_doc else p_name.lower())
        p_nick = ", ".join(set(person.aliases)) if person.aliases else ""
        p_back = ""

        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO persons (person_key, name, nickname, document, background)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(person_key) DO UPDATE SET
                    name=excluded.name,
                    nickname=CASE WHEN excluded.nickname != '' THEN excluded.nickname ELSE persons.nickname END,
                    document=CASE WHEN excluded.document != '' THEN excluded.document ELSE persons.document END;
            """, (p_key, p_name, p_nick, p_doc, p_back))
            conn.commit()
            return p_key

    def update(self, person: Person) -> None:
        """
        Atualiza uma pessoa existente no SQLite.
        """
        self.save(person)

    def _build_person_from_row(self, conn: sqlite3.Connection, row: sqlite3.Row) -> Person:
        person_db_id = row["id"]
        person_key = row["person_key"]
        name = row["name"]
        nickname = row["nickname"] or ""
        document = row["document"] or ""

        cursor = conn.cursor()
        # Busca RELINTs vinculados via tabela de junção relint_participants
        cursor.execute("""
            SELECT r.source_file, rp.photo_path
            FROM relint_participants rp
            JOIN relints r ON rp.relint_id = r.id
            WHERE rp.person_id = ?;
        """, (person_db_id,))
        p_rows = cursor.fetchall()

        linked_relints = list(set(r["source_file"] for r in p_rows if r["source_file"]))
        photos = list(set(r["photo_path"] for r in p_rows if r["photo_path"]))
        aliases = [a.strip() for a in nickname.split(",") if a.strip()]
        documents = [document] if document else []

        return Person(
            person_id=person_key,
            name=name,
            aliases=aliases,
            documents=documents,
            photos=photos,
            linked_relints=linked_relints,
            last_updated=datetime.now().isoformat()
        )

    def get_by_id(self, person_id: str) -> Optional[Person]:
        """
        Busca uma pessoa no SQLite pelo seu person_key.
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM persons WHERE person_key = ? LIMIT 1;", (person_id,))
            row = cursor.fetchone()
            if not row:
                return None
            return self._build_person_from_row(conn, row)

    def get_by_document(self, document: str) -> Optional[Person]:
        """
        Busca uma pessoa pelo número de documento (RG/CPF).
        """
        if not document:
            return None
        clean_doc = document.strip().replace(".", "").replace("-", "")

        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM persons WHERE REPLACE(REPLACE(document, '.', ''), '-', '') = ? LIMIT 1;", (clean_doc,))
            row = cursor.fetchone()
            if not row:
                return None
            return self._build_person_from_row(conn, row)

    def get_all(self) -> List[Person]:
        """
        Retorna todas as pessoas cadastradas no banco SQLite.
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM persons ORDER BY name ASC;")
            rows = cursor.fetchall()
            persons = []
            for row in rows:
                try:
                    persons.append(self._build_person_from_row(conn, row))
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
