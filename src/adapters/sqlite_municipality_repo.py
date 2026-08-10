import json
import sqlite3
from pathlib import Path
from typing import List, Optional
from src.domain.entities import Municipality
from src.ports.municipality_repo import IMunicipalityRepo


class SqliteMunicipalityRepo(IMunicipalityRepo):
    """
    Implementação concreta (Adapter) para o repositório de Municípios (Mancha Criminal)
    utilizando SQLite.
    """

    def __init__(self, db_path: Path):
        """
        Inicializa o repositório de municípios apontando para o arquivo de banco SQLite fornecido.

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
                CREATE TABLE IF NOT EXISTS municipalities (
                    name TEXT PRIMARY KEY,
                    data TEXT NOT NULL
                );
            """)
            conn.commit()

    def save(self, municipality: Municipality) -> str:
        """
        Salva ou atualiza um município no SQLite.
        """
        mun_dict = municipality.model_dump()
        json_data = json.dumps(mun_dict, ensure_ascii=False)

        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO municipalities (name, data)
                VALUES (?, ?)
                ON CONFLICT(name) DO UPDATE SET data=excluded.data;
            """, (municipality.name, json_data))
            conn.commit()
            return municipality.name

    def update(self, municipality: Municipality) -> None:
        """
        Atualiza um município existente no SQLite.
        """
        self.save(municipality)

    def get_by_name(self, name: str) -> Optional[Municipality]:
        """
        Busca um município pelo nome exato (case-insensitive).
        """
        if not name:
            return None
        clean_name = name.strip().lower()

        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT data FROM municipalities WHERE LOWER(name) = ? LIMIT 1;", (clean_name,))
            row = cursor.fetchone()
            if not row:
                return None
            data_dict = json.loads(row["data"])
            return Municipality(**data_dict)

    def get_all(self) -> List[Municipality]:
        """
        Retorna todos os municípios cadastrados no banco SQLite.
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT data FROM municipalities ORDER BY name ASC;")
            rows = cursor.fetchall()
            muns = []
            for row in rows:
                try:
                    data_dict = json.loads(row["data"])
                    muns.append(Municipality(**data_dict))
                except Exception:
                    pass
            return muns

    def clear_all(self) -> None:
        """
        Remove todos os municípios cadastrados no banco SQLite.
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM municipalities;")
            conn.commit()

