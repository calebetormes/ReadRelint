"""
FastAPI Router para Gerenciamento de Participantes e Dossiês Consolidados de Envolvidos.
"""
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field, computed_field

from backend.api.dependencies import get_person_repo
from backend.dashboard.backend.database.person_repo import IPersonRepo

router = APIRouter(prefix="/participants", tags=["participants"])


class LinkedRelintSummary(BaseModel):
    relint_id: int
    source_file: str
    subject: str
    date_of_fact: str
    participation_type: str
    municipality: str


class PersonDossierDTO(BaseModel):
    person_id: str
    name: str
    nickname: str
    document: str
    background: str
    photo_path: str
    photos: List[str]
    linked_relints_count: int
    linked_relints: List[LinkedRelintSummary]

    @computed_field
    @property
    def nome(self) -> str:
        return self.name

    @computed_field
    @property
    def alcunha(self) -> str:
        return self.nickname

    @computed_field
    @property
    def documento(self) -> str:
        return self.document

    @computed_field
    @property
    def antecedentes(self) -> str:
        return self.background

    @computed_field
    @property
    def caminho_foto(self) -> str:
        return self.photo_path

    @computed_field
    @property
    def galeria_fotos(self) -> List[str]:
        return self.photos

    @computed_field
    @property
    def quantidade_relints(self) -> int:
        return self.linked_relints_count


@router.get("", response_model=List[PersonDossierDTO])
def list_participants(
    search: Optional[str] = Query(None, description="Busca por nome, alcunha ou RG/CPF"),
    recurrent_only: bool = Query(False, description="Filtrar apenas reincidentes (> 1 RELINT)"),
    person_repo: IPersonRepo = Depends(get_person_repo)
) -> List[PersonDossierDTO]:
    """
    Retorna a lista consolidada de todos os participantes com contagem de ocorrências,
    foto principal e galeria de fotos vinculadas.
    """
    with person_repo._get_connection() as conn:
        cursor = conn.cursor()
        
        query = """
            SELECT 
                p.id,
                p.chave_pessoa,
                p.nome,
                p.alcunha,
                p.documento,
                p.antecedentes,
                COUNT(DISTINCT rp.relint_id) AS relint_count
            FROM pessoas p
            LEFT JOIN relint_participantes rp ON p.id = rp.pessoa_id
            GROUP BY p.id
        """
        cursor.execute(query)
        p_rows = cursor.fetchall()

        results = []
        search_lower = search.lower().strip() if search else ""

        for p in p_rows:
            p_id = p["id"]
            p_key = p["chave_pessoa"]
            name = p["nome"] or ""
            nick = p["alcunha"] or ""
            doc = p["documento"] or ""
            bg = p["antecedentes"] or ""
            relint_cnt = p["relint_count"] or 0

            if recurrent_only and relint_cnt <= 1:
                continue

            if search_lower:
                match_name = search_lower in name.lower()
                match_nick = search_lower in nick.lower()
                clean_doc = doc.lower().replace(".", "").replace("-", "")
                clean_search = search_lower.replace(".", "").replace("-", "")
                match_doc = clean_search in clean_doc if clean_doc else False
                if not (match_name or match_nick or match_doc):
                    continue

            cursor.execute("""
                SELECT 
                    r.id AS relint_id,
                    r.arquivo_origem,
                    r.assunto,
                    r.data_fato,
                    r.municipio,
                    rp.tipo_participacao,
                    rp.caminho_foto
                FROM relint_participantes rp
                JOIN relints r ON rp.relint_id = r.id
                WHERE rp.pessoa_id = ?
                ORDER BY r.id DESC;
            """, (p_id,))
            rel_rows = cursor.fetchall()

            linked_relints = []
            photos = []
            main_photo = ""

            for r in rel_rows:
                f_path = r["caminho_foto"] or ""
                if f_path and f_path not in photos:
                    photos.append(f_path)
                    if not main_photo:
                        main_photo = f_path

                linked_relints.append(LinkedRelintSummary(
                    relint_id=r["relint_id"],
                    source_file=r["arquivo_origem"] or "",
                    subject=r["assunto"] or "Sem assunto",
                    date_of_fact=r["data_fato"] or "",
                    participation_type=r["tipo_participacao"] or "Acusado",
                    municipality=r["municipio"] or ""
                ))

            results.append(PersonDossierDTO(
                person_id=p_key,
                name=name,
                nickname=nick,
                document=doc,
                background=bg,
                photo_path=main_photo,
                photos=photos,
                linked_relints_count=len(linked_relints),
                linked_relints=linked_relints
            ))

        results.sort(key=lambda x: x.linked_relints_count, reverse=True)
        return results


@router.get("/{person_id}", response_model=PersonDossierDTO)
def get_participant_dossier(
    person_id: str,
    person_repo: IPersonRepo = Depends(get_person_repo)
) -> PersonDossierDTO:
    """
    Retorna o dossiê detalhado de um participante específico.
    """
    with person_repo._get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM pessoas WHERE chave_pessoa = ? OR id = ? LIMIT 1;", (person_id, person_id))
        p = cursor.fetchone()
        if not p:
            raise HTTPException(status_code=404, detail="Participante não encontrado.")

        p_id = p["id"]
        p_key = p["chave_pessoa"]
        name = p["nome"] or ""
        nick = p["alcunha"] or ""
        doc = p["documento"] or ""
        bg = p["antecedentes"] or ""

        cursor.execute("""
            SELECT 
                r.id AS relint_id,
                r.arquivo_origem,
                r.assunto,
                r.data_fato,
                r.municipio,
                rp.tipo_participacao,
                rp.caminho_foto
            FROM relint_participantes rp
            JOIN relints r ON rp.relint_id = r.id
            WHERE rp.pessoa_id = ?
            ORDER BY r.id DESC;
        """, (p_id,))
        rel_rows = cursor.fetchall()

        linked_relints = []
        photos = []
        main_photo = ""

        for r in rel_rows:
            f_path = r["caminho_foto"] or ""
            if f_path and f_path not in photos:
                photos.append(f_path)
                if not main_photo:
                    main_photo = f_path

            linked_relints.append(LinkedRelintSummary(
                relint_id=r["relint_id"],
                source_file=r["arquivo_origem"] or "",
                subject=r["assunto"] or "Sem assunto",
                date_of_fact=r["data_fato"] or "",
                participation_type=r["tipo_participacao"] or "Acusado",
                municipality=r["municipio"] or ""
            ))

        return PersonDossierDTO(
            person_id=p_key,
            name=name,
            nickname=nick,
            document=doc,
            background=bg,
            photo_path=main_photo,
            photos=photos,
            linked_relints_count=len(linked_relints),
            linked_relints=linked_relints
        )
