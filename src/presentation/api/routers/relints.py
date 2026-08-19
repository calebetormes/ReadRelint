"""
FastAPI Router for RELINT reports management.

Exposes endpoints for:
  - GET  /relints          — paginated list with filtering
  - GET  /relints/{id}     — full detail of a single report
"""
from typing import List, Optional, Any, Dict
from fastapi import APIRouter, Depends, HTTPException, Query
from src.adapters.sqlite_repo import SqliteRepo
from src.presentation.api.dependencies import get_db_repo, get_person_repo
from src.presentation.api.schemas.relints import (
    RelintSummaryResponse,
    RelintDetailResponse,
    ParticipantDTO,
    RelintUpdateRequest,
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
    Looks up a report by doc_id directly.
    Returns None if not found.
    """
    return repo.get_by_id(report_id)


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

    for report in repo.get_all():
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
            id=str(report.id or ""),
            source_file=report.source_file or "",
            subject=report.subject or "",
            date_of_fact=report.date_of_fact or "",
            time_of_fact=report.time_of_fact or "",
            bm_group=b_group,
            relint_type=r_type,
            municipality=muni,
            neighborhood=getattr(report, "neighborhood", "") or "",
            police_unit=getattr(report, "police_unit", "") or "",
            summary=report.summary or "",
            extraction_method=getattr(report, "extraction_method", None) or "Regex (Sem IA)",
            participants=_build_participants_dto(report.participants or []),
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

    report_dict = report.model_dump(exclude={"participants", "images", "bm_group", "relint_type"})
    report_dict.update({
        "bm_group": _enum_to_str(report.bm_group),
        "relint_type": _enum_to_str(report.relint_type),
        "municipality": report.municipality or addr_info["municipality"],
        "neighborhood": report.neighborhood or addr_info["neighborhood"],
        "address": addr_info["formatted_address"],
        "police_unit": getattr(report, "police_unit", "") or "",
        "coordinates": coords,
        "map_url": map_url,
        "precision_level": precision_level,
        "precision_label": precision_label,
        "images": _build_image_list(report.images or []),
        "participants": _build_participants_dto(report.participants or []),
    })

    from src.domain.entities import HomicideReport, DrugTraffickingReport, EstablishmentRobberyReport, ResidenceRobberyReport, VehicleRobberyReport, PedestrianRobberyReport, VehicleTheftReport

    if isinstance(report, HomicideReport):
        report_dict["homicide_details"] = {
            "fact_type": report.fact_type,
            "motivation": report.motivation,
            "registry_number": getattr(report, "registry_number", ""),
            "registry_agency": getattr(report, "registry_agency", ""),
            "registry_year": getattr(report, "registry_year", "")
        }
    elif isinstance(report, DrugTraffickingReport):
        report_dict["drug_trafficking_details"] = {
            "drug_quantity": report.drug_quantity,
            "drug_types": report.drug_types
        }
    elif isinstance(report, EstablishmentRobberyReport):
        report_dict["establishment_robbery_details"] = {
            "establishment_type": report.establishment_type,
            "location_type": report.location_type,
            "injured_victims": report.injured_victims,
            "hostage_victim": report.hostage_victim
        }
    elif isinstance(report, ResidenceRobberyReport):
        report_dict["residence_robbery_details"] = {
            "location_type": report.location_type,
            "injured_victims": report.injured_victims,
            "hostage_victim": report.hostage_victim
        }
    elif isinstance(report, VehicleRobberyReport):
        report_dict["vehicle_robbery_details"] = {
            "vehicle_model": report.vehicle_model,
            "license_plate": report.license_plate,
            "recovered": report.recovered,
            "recovery_location": report.recovery_location
        }
    elif isinstance(report, PedestrianRobberyReport):
        report_dict["pedestrian_robbery_details"] = {
            "injured_victims": report.injured_victims,
            "weapon_used": report.weapon_used,
            "stolen_object": report.stolen_object
        }
    elif isinstance(report, VehicleTheftReport):
        report_dict["vehicle_theft_details"] = {
            "vehicle_model": report.vehicle_model,
            "license_plate": report.license_plate,
            "recovered": report.recovered,
            "recovery_location": report.recovery_location
        }

    report_dict["id"] = report_id
    return RelintDetailResponse(**report_dict)


@router.put("/{report_id}", response_model=RelintDetailResponse)
def update_relint(
    report_id: str,
    payload: RelintUpdateRequest,
    repo: SqliteRepo = Depends(get_db_repo),
) -> RelintDetailResponse:
    """Updates an existing RELINT report and its specialty details."""
    from src.domain.entities import IncidentReport, HomicideReport, Participant

    report = _find_report_by_id(report_id, repo)
    if not report:
        raise HTTPException(status_code=404, detail=f"RELINT '{report_id}' not found.")

    curr_bm_group = payload.bm_group if payload.bm_group is not None else _enum_to_str(report.bm_group)
    is_homicide = (
        curr_bm_group.lower() in ("homicídio", "homicidio")
        or payload.homicide_details is not None
        or isinstance(report, HomicideReport)
    )

    updated_dict = report.model_dump()

    fields_to_check = [
        "subject", "main_fact", "date_of_fact", "time_of_fact", "bm_group",
        "relint_type", "municipality", "neighborhood", "address", "police_unit",
        "coordinates", "map_url", "summary", "content",
        "registry_number", "registry_agency", "registry_year"
    ]
    for field in fields_to_check:
        val = getattr(payload, field, None)
        if val is not None:
            updated_dict[field] = val

    updated_dict["user_edited"] = True

    if payload.participants is not None:
        existing_part_map = {}
        for ep in (report.participants or []):
            name_key = (ep.name or "").strip().lower()
            if name_key:
                existing_part_map[name_key] = ep

        new_participants = []
        for p_dto in payload.participants:
            name_key = (p_dto.name or "").strip().lower()
            existing_p = existing_part_map.get(name_key)

            p_bg = p_dto.background if p_dto.background is not None and p_dto.background != "" else (existing_p.background if existing_p else "")
            p_photo = p_dto.photo_path if p_dto.photo_path is not None and p_dto.photo_path != "" else (existing_p.photo_path if existing_p else "")

            new_participants.append(Participant(
                name=p_dto.name,
                nickname=p_dto.nickname or "",
                document=p_dto.document or "",
                background=p_bg or "",
                participation_type=p_dto.participation_type or "Acusado",
                photo_path=p_photo or ""
            ))
        updated_dict["participants"] = new_participants

    if is_homicide:
        if payload.homicide_details:
            h_det = payload.homicide_details
            if getattr(h_det, "registry_number", None) is not None: updated_dict["registry_number"] = h_det.registry_number
            if getattr(h_det, "registry_agency", None) is not None: updated_dict["registry_agency"] = h_det.registry_agency
            if getattr(h_det, "registry_year", None) is not None: updated_dict["registry_year"] = h_det.registry_year
            if getattr(h_det, "fact_type", None) is not None: updated_dict["fact_type"] = h_det.fact_type
            if getattr(h_det, "motivation", None) is not None: updated_dict["motivation"] = h_det.motivation
        updated_report = __import__("src.domain.entities", fromlist=["HomicideReport"]).HomicideReport(**updated_dict)
    elif curr_bm_group == "Prisão por Tráfico" or payload.drug_trafficking_details is not None:
        if payload.drug_trafficking_details:
            d_det = payload.drug_trafficking_details
            if getattr(d_det, "drug_quantity", None) is not None: updated_dict["drug_quantity"] = d_det.drug_quantity
            if getattr(d_det, "drug_types", None) is not None: updated_dict["drug_types"] = d_det.drug_types
        updated_report = __import__("src.domain.entities", fromlist=["DrugTraffickingReport"]).DrugTraffickingReport(**updated_dict)
    elif curr_bm_group == "Roubo a Estabelecimento" or payload.establishment_robbery_details is not None:
        if payload.establishment_robbery_details:
            e_det = payload.establishment_robbery_details
            if getattr(e_det, "establishment_type", None) is not None: updated_dict["establishment_type"] = e_det.establishment_type
            if getattr(e_det, "location_type", None) is not None: updated_dict["location_type"] = e_det.location_type
            if getattr(e_det, "injured_victims", None) is not None: updated_dict["injured_victims"] = e_det.injured_victims
            if getattr(e_det, "hostage_victim", None) is not None: updated_dict["hostage_victim"] = e_det.hostage_victim
        updated_report = __import__("src.domain.entities", fromlist=["EstablishmentRobberyReport"]).EstablishmentRobberyReport(**updated_dict)
    elif curr_bm_group == "Roubo a Residência" or payload.residence_robbery_details is not None:
        if payload.residence_robbery_details:
            r_det = payload.residence_robbery_details
            if getattr(r_det, "location_type", None) is not None: updated_dict["location_type"] = r_det.location_type
            if getattr(r_det, "injured_victims", None) is not None: updated_dict["injured_victims"] = r_det.injured_victims
            if getattr(r_det, "hostage_victim", None) is not None: updated_dict["hostage_victim"] = r_det.hostage_victim
        updated_report = __import__("src.domain.entities", fromlist=["ResidenceRobberyReport"]).ResidenceRobberyReport(**updated_dict)
    elif curr_bm_group == "Roubo de Veículo" or payload.vehicle_robbery_details is not None:
        if payload.vehicle_robbery_details:
            v_det = payload.vehicle_robbery_details
            if getattr(v_det, "vehicle_model", None) is not None: updated_dict["vehicle_model"] = v_det.vehicle_model
            if getattr(v_det, "license_plate", None) is not None: updated_dict["license_plate"] = v_det.license_plate
            if getattr(v_det, "recovered", None) is not None: updated_dict["recovered"] = v_det.recovered
            if getattr(v_det, "recovery_location", None) is not None: updated_dict["recovery_location"] = v_det.recovery_location
        updated_report = __import__("src.domain.entities", fromlist=["VehicleRobberyReport"]).VehicleRobberyReport(**updated_dict)
    elif curr_bm_group == "Roubo a Pedestre" or payload.pedestrian_robbery_details is not None:
        if payload.pedestrian_robbery_details:
            p_det = payload.pedestrian_robbery_details
            if getattr(p_det, "injured_victims", None) is not None: updated_dict["injured_victims"] = p_det.injured_victims
            if getattr(p_det, "weapon_used", None) is not None: updated_dict["weapon_used"] = p_det.weapon_used
            if getattr(p_det, "stolen_object", None) is not None: updated_dict["stolen_object"] = p_det.stolen_object
        updated_report = __import__("src.domain.entities", fromlist=["PedestrianRobberyReport"]).PedestrianRobberyReport(**updated_dict)
    elif curr_bm_group == "Furto de Veículo" or payload.vehicle_theft_details is not None:
        if payload.vehicle_theft_details:
            f_det = payload.vehicle_theft_details
            if getattr(f_det, "vehicle_model", None) is not None: updated_dict["vehicle_model"] = f_det.vehicle_model
            if getattr(f_det, "license_plate", None) is not None: updated_dict["license_plate"] = f_det.license_plate
            if getattr(f_det, "recovered", None) is not None: updated_dict["recovered"] = f_det.recovered
            if getattr(f_det, "recovery_location", None) is not None: updated_dict["recovery_location"] = f_det.recovery_location
        updated_report = __import__("src.domain.entities", fromlist=["VehicleTheftReport"]).VehicleTheftReport(**updated_dict)
    else:
        updated_report = IncidentReport(**updated_dict)

    repo.save(updated_report)

    # Transmite o evento SSE de atualização para todos os clientes ativos
    try:
        from src.presentation.api.routers.events import broadcaster
        bm_str = updated_report.bm_group.value if hasattr(updated_report.bm_group, "value") else str(updated_report.bm_group or "Outros")
        broadcaster.broadcast("relint_updated", {
            "id": str(updated_report.id or report_id),
            "source_file": updated_report.source_file or "",
            "subject": updated_report.subject or "",
            "bm_group": bm_str,
            "municipality": updated_report.municipality or ""
        })
    except Exception:
        pass

    return get_relint_by_id(report_id, repo)


# ─────────────────────────────────────────────────────────────────────────────
# Endpoint de Participantes e Dossiês (Garantia de rota em /api/v1/participants)
# ─────────────────────────────────────────────────────────────────────────────
from src.presentation.api.routers.participants import list_participants as _list_p, get_participant_dossier as _get_p_dossier, PersonDossierDTO

@router.get("/participants", response_model=List[PersonDossierDTO], tags=["participants"])
def get_participants_list_fallback(
    search: Optional[str] = Query(None),
    recurrent_only: bool = Query(False),
    person_repo = Depends(get_person_repo)
):
    return _list_p(search=search, recurrent_only=recurrent_only, person_repo=person_repo)


@router.get("/participants/{person_id}", response_model=PersonDossierDTO, tags=["participants"])
def get_participant_dossier_fallback(
    person_id: str,
    person_repo = Depends(get_person_repo)
):
    return _get_p_dossier(person_id=person_id, person_repo=person_repo)

