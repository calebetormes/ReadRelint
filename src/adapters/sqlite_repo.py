import sqlite3
from pathlib import Path
from typing import List, Optional, Dict, Any
from src.domain.entities import IncidentReport, HomicideReport, Participant, BmGroup, RelintType
from src.ports.database_repo import IDatabaseRepo


class SqliteRepo(IDatabaseRepo):
    """
    Implementação concreta (Adapter) para persistência de relatórios de incidentes
    utilizando um banco de dados SQLite 100% relacional e normalizado (sem JSON blob).
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
        conn.execute("PRAGMA foreign_keys = ON;")
        return conn

    def _init_db(self) -> None:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("PRAGMA journal_mode=WAL;")

            # 1. Tabela Principal de Ocorrências / RELINTs
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
                    extraction_method TEXT DEFAULT 'Ollama (IA)',
                    user_edited INTEGER DEFAULT 0
                );
            """)

            # Migração automática para bancos já existentes
            cursor.execute("PRAGMA table_info(relints);")
            cols = [row["name"] for row in cursor.fetchall()]
            if "extraction_method" not in cols:
                cursor.execute("ALTER TABLE relints ADD COLUMN extraction_method TEXT DEFAULT 'Ollama (IA)';")

            # 2. Especialização de Homicídios (1 para 1 com relints)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS homicide_details (
                    relint_id INTEGER PRIMARY KEY,
                    registry_number TEXT,
                    registry_agency TEXT,
                    registry_year TEXT,
                    fact_type TEXT,
                    motivation TEXT,
                    FOREIGN KEY (relint_id) REFERENCES relints(id) ON DELETE CASCADE
                );
            """)

            # 3. Cadastro Central de Pessoas
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

            # 4. Tabela de Junção de Participantes (N para N)
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

            # 5. Imagens e Mídias Anexas (1 para N)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS relint_images (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    relint_id INTEGER NOT NULL,
                    file_path TEXT NOT NULL,
                    caption TEXT,
                    FOREIGN KEY (relint_id) REFERENCES relints(id) ON DELETE CASCADE
                );
            """)

            # Suporte para consultas legadas que utilizavam a chave doc_id ou a visão 'reports'
            cursor.execute("""
                CREATE VIEW IF NOT EXISTS reports AS SELECT id AS doc_id, * FROM relints;
            """)

            conn.commit()

    def _enum_to_str(self, val: Any) -> str:
        if not val:
            return ""
        if hasattr(val, "value"):
            return str(val.value)
        return str(val)

    def save(self, report: IncidentReport) -> str:
        """
        Salva ou atualiza um relatório de incidente de forma 100% relacional no SQLite.

        :param report: Entidade IncidentReport ou HomicideReport a ser persistida.
        :return: ID único atribuído ao relatório persistido.
        """
        source_file = report.source_file or ""
        subject = report.subject or ""
        main_fact = getattr(report, "main_fact", "") or ""
        date_of_fact = report.date_of_fact or ""
        time_of_fact = report.time_of_fact or ""
        bm_group = self._enum_to_str(report.bm_group) or "Outros"
        relint_type = self._enum_to_str(report.relint_type) or "Outros"
        municipality = report.municipality or ""
        neighborhood = getattr(report, "neighborhood", "") or ""
        address = getattr(report, "address", "") or ""
        police_unit = getattr(report, "police_unit", "") or ""
        coordinates = getattr(report, "coordinates", "") or ""
        map_url = getattr(report, "map_url", "") or ""
        summary = report.summary or ""
        content = report.content or ""
        extraction_method = getattr(report, "extraction_method", None) or "Regex (Sem IA)"
        user_edited = 1 if getattr(report, "user_edited", False) else 0

        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # 1. Salva ou atualiza na tabela principal 'relints'
            cursor.execute("""
                INSERT INTO relints (
                    source_file, subject, main_fact, date_of_fact, time_of_fact,
                    bm_group, relint_type, municipality, neighborhood, address,
                    police_unit, coordinates, map_url, summary, content, extraction_method, user_edited
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(source_file) DO UPDATE SET
                    subject=excluded.subject,
                    main_fact=excluded.main_fact,
                    date_of_fact=excluded.date_of_fact,
                    time_of_fact=excluded.time_of_fact,
                    bm_group=excluded.bm_group,
                    relint_type=excluded.relint_type,
                    municipality=excluded.municipality,
                    neighborhood=excluded.neighborhood,
                    address=excluded.address,
                    police_unit=excluded.police_unit,
                    coordinates=excluded.coordinates,
                    map_url=excluded.map_url,
                    summary=excluded.summary,
                    content=excluded.content,
                    extraction_method=excluded.extraction_method,
                    user_edited=excluded.user_edited;
            """, (
                source_file, subject, main_fact, date_of_fact, time_of_fact,
                bm_group, relint_type, municipality, neighborhood, address,
                police_unit, coordinates, map_url, summary, content, extraction_method, user_edited
            ))

            cursor.execute("SELECT id FROM relints WHERE source_file = ?;", (source_file,))
            row = cursor.fetchone()
            if not row:
                conn.commit()
                return ""
            relint_id = row["id"]

            # 2. Atualiza detalhes de Homicídio se aplicável
            is_homicide = (bm_group == "Homicídio" or isinstance(report, HomicideReport))
            if is_homicide:
                reg_num = getattr(report, "registry_number", None) or ""
                reg_agency = getattr(report, "registry_agency", None) or ""
                reg_year = getattr(report, "registry_year", None) or ""
                fact_type = getattr(report, "fact_type", None) or ""
                motivation = self._enum_to_str(getattr(report, "motivation", "Desconhecido")) or "Desconhecido"

                cursor.execute("""
                    INSERT INTO homicide_details (
                        relint_id, registry_number, registry_agency, registry_year, fact_type, motivation
                    )
                    VALUES (?, ?, ?, ?, ?, ?)
                    ON CONFLICT(relint_id) DO UPDATE SET
                        registry_number=excluded.registry_number,
                        registry_agency=excluded.registry_agency,
                        registry_year=excluded.registry_year,
                        fact_type=excluded.fact_type,
                        motivation=excluded.motivation;
                """, (relint_id, reg_num, reg_agency, reg_year, fact_type, motivation))
            else:
                cursor.execute("DELETE FROM homicide_details WHERE relint_id = ?;", (relint_id,))

            # 3. Atualiza Imagens anexas
            cursor.execute("DELETE FROM relint_images WHERE relint_id = ?;", (relint_id,))
            for img in (report.images or []):
                file_path = ""
                caption = ""
                if isinstance(img, dict):
                    file_path = img.get("file_path") or img.get("path") or ""
                    caption = img.get("caption") or ""
                elif isinstance(img, str):
                    file_path = img
                if file_path:
                    cursor.execute("""
                        INSERT INTO relint_images (relint_id, file_path, caption)
                        VALUES (?, ?, ?);
                    """, (relint_id, file_path, caption))

            # 4. Atualiza Pessoas e Participantes
            cursor.execute("DELETE FROM relint_participants WHERE relint_id = ?;", (relint_id,))
            for part in (report.participants or []):
                if isinstance(part, dict):
                    p_name = (part.get("name") or "").strip()
                    p_doc = (part.get("document") or "").strip()
                    p_nick = (part.get("nickname") or "").strip()
                    p_back = (part.get("background") or "").strip()
                    raw_type = part.get("participation_type", "Acusado")
                    photo_path = part.get("photo_path") or ""
                else:
                    p_name = (getattr(part, "name", "") or "").strip()
                    p_doc = (getattr(part, "document", "") or "").strip()
                    p_nick = (getattr(part, "nickname", "") or "").strip()
                    p_back = (getattr(part, "background", "") or "").strip()
                    raw_type = getattr(part, "participation_type", "Acusado")
                    photo_path = getattr(part, "photo_path", "") or ""

                if not p_name:
                    continue

                clean_doc = p_doc.replace(".", "").replace("-", "") if p_doc else ""
                p_key = clean_doc if clean_doc else p_name.lower()

                cursor.execute("""
                    INSERT INTO persons (person_key, name, nickname, document, background)
                    VALUES (?, ?, ?, ?, ?)
                    ON CONFLICT(person_key) DO UPDATE SET
                        name=excluded.name,
                        nickname=CASE WHEN excluded.nickname != '' THEN excluded.nickname ELSE persons.nickname END,
                        document=CASE WHEN excluded.document != '' THEN excluded.document ELSE persons.document END,
                        background=CASE WHEN excluded.background != '' THEN excluded.background ELSE persons.background END;
                """, (p_key, p_name, p_nick, p_doc, p_back))

                cursor.execute("SELECT id FROM persons WHERE person_key = ?;", (p_key,))
                p_row = cursor.fetchone()
                if p_row:
                    person_id = p_row["id"]
                    part_type = self._enum_to_str(raw_type) or "Acusado"
                    cursor.execute("""
                        INSERT INTO relint_participants (relint_id, person_id, participation_type, photo_path)
                        VALUES (?, ?, ?, ?);
                    """, (relint_id, person_id, part_type, photo_path))

            conn.commit()
            return str(relint_id)

    def _build_report_from_row(self, conn: sqlite3.Connection, relint_row: sqlite3.Row) -> IncidentReport:
        relint_id = relint_row["id"]
        cursor = conn.cursor()

        # 1. Carrega Imagens
        cursor.execute("SELECT file_path, caption FROM relint_images WHERE relint_id = ? ORDER BY id ASC;", (relint_id,))
        img_rows = cursor.fetchall()
        images = [{"file_path": r["file_path"], "caption": r["caption"]} for r in img_rows]

        # 2. Carrega Participantes (JOIN entre relint_participants e persons)
        cursor.execute("""
            SELECT p.name, p.nickname, p.document, p.background, rp.participation_type, rp.photo_path
            FROM relint_participants rp
            JOIN persons p ON rp.person_id = p.id
            WHERE rp.relint_id = ?
            ORDER BY rp.id ASC;
        """, (relint_id,))
        part_rows = cursor.fetchall()
        participants = []
        for pr in part_rows:
            participants.append(Participant(
                name=pr["name"],
                nickname=pr["nickname"] or "",
                document=pr["document"] or "",
                background=pr["background"] or "",
                participation_type=pr["participation_type"] or "Acusado",
                photo_path=pr["photo_path"] or ""
            ))

        # 3. Verifica se possui detalhes de Homicídio
        cursor.execute("SELECT * FROM homicide_details WHERE relint_id = ?;", (relint_id,))
        hom_row = cursor.fetchone()

        report_data = {
            "id": str(relint_id),
            "source_file": relint_row["source_file"],
            "subject": relint_row["subject"] or "",
            "main_fact": relint_row["main_fact"] or "",
            "date_of_fact": relint_row["date_of_fact"] or "",
            "time_of_fact": relint_row["time_of_fact"] or "",
            "bm_group": relint_row["bm_group"] or "Outros",
            "relint_type": relint_row["relint_type"] or "Outros",
            "municipality": relint_row["municipality"] or "",
            "neighborhood": relint_row["neighborhood"] or "",
            "address": relint_row["address"] or "",
            "police_unit": relint_row["police_unit"] or "",
            "coordinates": relint_row["coordinates"] or "",
            "map_url": relint_row["map_url"] or "",
            "summary": relint_row["summary"] or "",
            "content": relint_row["content"] or "",
            "extraction_method": relint_row["extraction_method"] if ("extraction_method" in relint_row.keys() and relint_row["extraction_method"]) else "Regex (Sem IA)",
            "user_edited": bool(relint_row["user_edited"]),
            "images": images,
            "participants": participants
        }

        if hom_row or relint_row["bm_group"] == "Homicídio":
            if hom_row:
                report_data.update({
                    "registry_number": hom_row["registry_number"] or "",
                    "registry_agency": hom_row["registry_agency"] or "",
                    "registry_year": hom_row["registry_year"] or "",
                    "fact_type": hom_row["fact_type"] or "",
                    "motivation": hom_row["motivation"] or "Desconhecido",
                })
            return HomicideReport(**report_data)

        return IncidentReport(**report_data)

    def get_by_id(self, report_id: str) -> Optional[IncidentReport]:
        """
        Busca um relatório no SQLite pelo seu ID único.
        """
        try:
            relint_id = int(report_id)
        except ValueError:
            return None

        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM relints WHERE id = ?;", (relint_id,))
            row = cursor.fetchone()
            if not row:
                return None
            return self._build_report_from_row(conn, row)

    def get_all(self) -> List[IncidentReport]:
        """
        Retorna todos os relatórios cadastrados no SQLite ordenados do mais recente para o mais antigo.
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM relints ORDER BY id DESC;")
            rows = cursor.fetchall()
            reports = []
            for row in rows:
                try:
                    reports.append(self._build_report_from_row(conn, row))
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
            cursor.execute("SELECT * FROM relints WHERE source_file = ? LIMIT 1;", (filename,))
            row = cursor.fetchone()
            if not row:
                return None
            return self._build_report_from_row(conn, row)

    def clear_all(self) -> None:
        """
        Remove todos os registros das tabelas de relatórios.
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM relints;")
            cursor.execute("DELETE FROM persons;")
            conn.commit()

    def get_all_source_filenames(self) -> set:
        """
        Retorna um conjunto em memória contendo os nomes de todos os arquivos já cadastrados (busca O(1)).
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT source_file FROM relints WHERE source_file IS NOT NULL AND source_file != '';")
            rows = cursor.fetchall()
            return {row["source_file"] for row in rows}

    def get_report_counts(self) -> dict:
        """
        Retorna a contagem estatística agregada em 1 única query SQL ultrarrápida (0.1ms).
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) AS total FROM relints;")
            total_row = cursor.fetchone()
            total = total_row["total"] if total_row else 0

            cursor.execute("""
                SELECT 
                    SUM(CASE WHEN extraction_method LIKE '%Ollama%' OR extraction_method LIKE '%LLM%' THEN 1 ELSE 0 END) AS llm_count,
                    SUM(CASE WHEN (extraction_method LIKE '%Regex%' OR extraction_method LIKE '%Sem IA%') AND extraction_method NOT LIKE '%Ollama%' THEN 1 ELSE 0 END) AS regex_count
                FROM relints;
            """)
            row = cursor.fetchone()
            llm_cnt = row["llm_count"] if (row and row["llm_count"]) else 0
            regex_cnt = row["regex_count"] if (row and row["regex_count"]) else 0

            return {
                "total": total,
                "llm": llm_cnt,
                "regex": regex_cnt
            }
