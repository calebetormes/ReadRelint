"""
FastAPI Router for RELINT reports management.

Exposes endpoints for:
  - GET  /relints          — paginated list with filtering
  - GET  /relints/{id}     — full detail of a single report
  - PUT  /relints/{id}     — update user-editable fields
"""
from typing import List, Optional, Any, Dict
from fastapi import APIRouter, Depends, HTTPException, Query
from src.adapters.sqlite_repo import SqliteRepo
from src.presentation.api.dependencies import get_db_repo
from src.presentation.api.schemas.relints import (
    RelintSummaryResponse,
    RelintDetailResponse,
    RelintUpdateRequest,
    ParticipantDTO,
)

router = APIRouter(prefix="/relints", tags=["relints"])


# ─────────────────────────────────────────────────────────────────────────────
# Private helpers
# ─────────────────────────────────────────────────────────────────────────────

def _enum_to_str(val: Any, fallback: str = "Outros") -> str:
    """Converts enum values or plain values to a string, with a safe fallback."""
    if val is None:
        return fallback
    if hasattr(val, "value"):
        return str(val.value)
    return str(val) or fallback


def _normalize_image_path(raw_path: str) -> str:
    """
    Converts a filesystem path stored in the database (e.g. data/media/folder/img.jpeg)
    into a publicly accessible web URL path (/media/folder/img.jpeg).
    """
    clean = str(raw_path).replace("\\", "/")
    if "data/media/" in clean:
        return "/media/" + clean.split("data/media/", 1)[1]
    if not clean.startswith("/") and not clean.startswith("http"):
        return "/" + clean
    return clean


def _build_image_list(raw_images: list) -> List[Dict[str, Any]]:
    """Normalizes raw image records into a consistent list of dicts."""
    result = []
    for img in raw_images:
        if isinstance(img, dict):
            path = img.get("path") or img.get("file_path") or ""
            caption = img.get("caption") or ""
            page = img.get("page") or 1
        elif isinstance(img, str):
            path, caption, page = img, "", 1
        else:
            continue
        result.append({
            "path": _normalize_image_path(path),
            "caption": caption,
            "page": page,
        })
    return result


def _build_participants_dto(participants: list) -> List[ParticipantDTO]:
    """Maps domain Participant objects to ParticipantDTO for API responses."""
    return [
        ParticipantDTO(
            name=p.name,
            nickname=p.nickname or "",
            document=p.document or "",
            background=p.background or "",
            participation_type=_enum_to_str(p.participation_type, fallback="Acusado"),
            photo_path=p.photo_path or "",
        )
        for p in (participants or [])
    ]


def _find_report_by_id(report_id: str, repo: SqliteRepo):
    """
    Looks up a report by UUID first, then falls back to positional integer index.
    Returns None if not found.
    """
    report = repo.get_by_id(report_id)
    if report:
        return report
    try:
        idx = int(report_id) - 1
        all_reports = repo.get_all()
        if 0 <= idx < len(all_reports):
            return all_reports[idx]
    except ValueError:
        pass
    return None


# ─────────────────────────────────────────────────────────────────────────────
# Endpoints
# ─────────────────────────────────────────────────────────────────────────────

@router.get("", response_model=List[RelintSummaryResponse])
def list_relints(
    search: Optional[str] = Query(None, description="Full-text search in subject/summary/content/participants"),
    bm_group: Optional[str] = Query(None, description="Filter by BM Group (case-insensitive)"),
    relint_type: Optional[str] = Query(None, description="Filter by RELINT type"),
    municipality: Optional[str] = Query(None, description="Filter by municipality (partial match)"),
    repo: SqliteRepo = Depends(get_db_repo),
) -> List[RelintSummaryResponse]:
    """Returns all RELINT reports, with optional text search and category filters."""
    results = []

    for idx, report in enumerate(repo.get_all(), start=1):
        b_group = _enum_to_str(report.bm_group)
        r_type = _enum_to_str(report.relint_type)
        muni = report.municipality or ""

        if bm_group and bm_group.lower() not in ("todos", b_group.lower()):
            continue
        if relint_type and relint_type.lower() not in ("todos", r_type.lower()):
            continue
        if municipality and municipality.lower() != "todos" and municipality.lower() not in muni.lower():
            continue

        if search:
            query = search.lower()
            participants_text = " ".join(
                f"{p.name or ''} {p.nickname or ''} {p.document or ''}"
                for p in (report.participants or [])
            )
            matches = (
                query in (report.subject or "").lower()
                or query in (report.summary or "").lower()
                or query in (report.content or "").lower()
                or query in muni.lower()
                or query in participants_text.lower()
            )
            if not matches:
                continue

        results.append(RelintSummaryResponse(
            id=str(idx),
            source_file=report.source_file or "",
            subject=report.subject or "",
            date_of_fact=report.date_of_fact or "",
            time_of_fact=report.time_of_fact or "",
            bm_group=b_group,
            relint_type=r_type,
            municipality=muni,
            summary=report.summary or "",
            participants_count=len(report.participants or []),
            images_count=len(report.images or []),
            user_edited=getattr(report, "user_edited", False) or False,
        ))

    return results


@router.get("/{report_id}", response_model=RelintDetailResponse)
def get_relint_by_id(
    report_id: str,
    repo: SqliteRepo = Depends(get_db_repo),
) -> RelintDetailResponse:
    """Returns the full detail view of a single RELINT report."""
    from src.application.geo_service import extract_structured_address, resolve_report_map_info

    report = _find_report_by_id(report_id, repo)
    if not report:
        raise HTTPException(status_code=404, detail=f"RELINT '{report_id}' not found.")

    addr_info = extract_structured_address(report)
    map_url, coords, precision_level, precision_label = resolve_report_map_info(report)

    return RelintDetailResponse(
        id=report_id,
        source_file=report.source_file or "",
        subject=report.subject or "",
        main_fact=report.main_fact or "",
        date_of_fact=report.date_of_fact or "",
        time_of_fact=report.time_of_fact or "",
        bm_group=_enum_to_str(report.bm_group),
        relint_type=_enum_to_str(report.relint_type),
        municipality=report.municipality or addr_info["municipality"],
        neighborhood=report.neighborhood or addr_info["neighborhood"],
        street=report.street or addr_info["street"],
        number=report.number or addr_info["number"],
        address=addr_info["formatted_address"],
        coordinates=coords,
        map_url=map_url,
        precision_level=precision_level,
        precision_label=precision_label,
        summary=report.summary or "",
        content=report.content or "",
        user_edited=getattr(report, "user_edited", False) or False,
        images=_build_image_list(report.images or []),
        participants=_build_participants_dto(report.participants or []),
    )


@router.put("/{report_id}", response_model=RelintDetailResponse)
def update_relint(
    report_id: str,
    payload: RelintUpdateRequest,
    repo: SqliteRepo = Depends(get_db_repo),
) -> RelintDetailResponse:
    """Updates user-editable metadata fields of a RELINT and sets user_edited=True."""
    report = _find_report_by_id(report_id, repo)
    if not report:
        raise HTTPException(status_code=404, detail=f"RELINT '{report_id}' not found.")

    for field, value in payload.model_dump(exclude_unset=True).items():
        if value is not None:
            setattr(report, field, value)

    report.user_edited = True
    repo.save(report)

    return get_relint_by_id(report_id, repo=repo)
