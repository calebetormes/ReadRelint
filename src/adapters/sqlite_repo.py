import json
import sqlite3
from pathlib import Path
from typing import List, Optional
from src.domain.entities import IncidentReport
from src.ports.database_repo import IDatabaseRepo


class SqliteRepo(IDatabaseRepo):
    """
    Implementação concreta (Adapter) para persistência de relatórios de incidentes
    utilizando banco de dados relacional SQLite com a tabela 'relints' e colunas explícitas.
    """

    def __init__(self, db_path: Path):
        """
        Inicializa o repositório SQLite apontando para o arquivo de banco fornecido.

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
            
            # Tabela relints com colunas estruturadas para consultas SQL diretas
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS relints (
                    doc_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    source_file TEXT UNIQUE NOT NULL,
                    subject TEXT,
                    date_of_fact TEXT,
                    time_of_fact TEXT,
                    bm_group TEXT,
                    relint_type TEXT,
                    municipality TEXT,
                    summary TEXT,
                    data TEXT NOT NULL
                );
            """)
            
            # Migração/Suporte transparente caso exista tabela 'reports' legada
            cursor.execute("""
                CREATE VIEW IF NOT EXISTS reports AS SELECT * FROM relints;
            """)
            conn.commit()

    def save(self, report: IncidentReport) -> str:
        """
        Salva ou atualiza um relatório de incidente na tabela relints do SQLite.

        :param report: Entidade IncidentReport a ser persistida.
        :return: ID único atribuído ao relatório persistido.
        """
        report_dict = report.model_dump()
        json_data = json.dumps(report_dict, ensure_ascii=False)
        
        source_file = report.source_file or ""
        subject = report.subject or ""
        date_of_fact = report.date_of_fact or ""
        time_of_fact = report.time_of_fact or ""
        
        bm_val = getattr(report.bm_group, "value", report.bm_group) if report.bm_group else "Outros"
        type_val = getattr(report.relint_type, "value", report.relint_type) if report.relint_type else "Outros"
        
        bm_group = str(bm_val)
        relint_type = str(type_val)
        municipality = report.municipality or ""
        summary = report.summary or ""

        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO relints (
                    source_file, subject, date_of_fact, time_of_fact,
                    bm_group, relint_type, municipality, summary, data
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(source_file) DO UPDATE SET
                    subject=excluded.subject,
                    date_of_fact=excluded.date_of_fact,
                    time_of_fact=excluded.time_of_fact,
                    bm_group=excluded.bm_group,
                    relint_type=excluded.relint_type,
                    municipality=excluded.municipality,
                    summary=excluded.summary,
                    data=excluded.data;
            """, (
                source_file, subject, date_of_fact, time_of_fact,
                bm_group, relint_type, municipality, summary, json_data
            ))
            
            cursor.execute("SELECT doc_id FROM relints WHERE source_file = ?;", (source_file,))
            row = cursor.fetchone()
            conn.commit()
            return str(row["doc_id"]) if row else ""

    def get_by_id(self, report_id: str) -> Optional[IncidentReport]:
        """
        Busca um relatório no SQLite pelo seu ID único.
        """
        try:
            doc_id_int = int(report_id)
        except ValueError:
            return None

        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT data FROM relints WHERE doc_id = ?;", (doc_id_int,))
            row = cursor.fetchone()
            if not row:
                return None
            data_dict = json.loads(row["data"])
            return IncidentReport(**data_dict)

    def get_all(self) -> List[IncidentReport]:
        """
        Retorna todos os relatórios cadastrados no SQLite.
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT data FROM relints ORDER BY doc_id ASC;")
            rows = cursor.fetchall()
            reports = []
            for row in rows:
                try:
                    data_dict = json.loads(row["data"])
                    reports.append(IncidentReport(**data_dict))
                except Exception:
                    pass
            return reports

    def exists_by_source_file(self, filename: str) -> bool:
        """
        Verifica se um relatório originado do arquivo fornecido já existe.
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT 1 FROM relints WHERE source_file = ? LIMIT 1;", (filename,))
            return cursor.fetchone() is not None

    def delete_by_source_file(self, filename: str) -> bool:
        """
        Remove um relatório do SQLite com base no nome do arquivo original.
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM relints WHERE source_file = ?;", (filename,))
            conn.commit()
            return cursor.rowcount > 0

    def get_by_source_file(self, filename: str) -> Optional[IncidentReport]:
        """
        Busca um relatório pelo nome do arquivo original.
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT data FROM relints WHERE source_file = ? LIMIT 1;", (filename,))
            row = cursor.fetchone()
            if not row:
                return None
            data_dict = json.loads(row["data"])
            return IncidentReport(**data_dict)

    def clear_all(self) -> None:
        """
        Remove todos os registros da tabela de relatórios.
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM relints;")
            conn.commit()
