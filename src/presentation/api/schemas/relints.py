"""
Pydantic schemas for RELINTs REST API endpoints.
"""
from typing import List, Optional, Any, Dict
from pydantic import BaseModel, Field

class RelintSummaryResponse(BaseModel):
    """Summary representation of a RELINT report for list/table view."""
    id: str
    source_file: str
    subject: Optional[str] = ""
    date_of_fact: Optional[str] = ""
    time_of_fact: Optional[str] = ""
    bm_group: Optional[str] = "Outros"
    relint_type: Optional[str] = "Outros"
    municipality: Optional[str] = ""
    police_unit: Optional[str] = ""
    summary: Optional[str] = ""
    extraction_method: Optional[str] = "Ollama (IA)"
    participants_count: int = 0
    images_count: int = 0
    user_edited: bool = False

class ParticipantDTO(BaseModel):
    """Participant information inside a RELINT."""
    name: str
    nickname: Optional[str] = ""
    document: Optional[str] = ""
    background: Optional[str] = ""
    participation_type: Optional[str] = "Acusado"
    photo_path: Optional[str] = ""

class RelintDetailResponse(BaseModel):
    """Complete detail representation of an IncidentReport."""
    model_config = {"extra": "allow"}
    
    id: str
    source_file: str
    subject: Optional[str] = ""
    main_fact: Optional[str] = ""
    date_of_fact: Optional[str] = ""
    time_of_fact: Optional[str] = ""
    bm_group: Optional[str] = "Outros"
    relint_type: Optional[str] = "Outros"
    municipality: Optional[str] = ""
    neighborhood: Optional[str] = ""
    address: Optional[str] = ""
    police_unit: Optional[str] = ""
    coordinates: Optional[str] = ""
    map_url: Optional[str] = ""
    precision_level: Optional[str] = "unknown"
    precision_label: Optional[str] = "Sem Dados de Localização"
    summary: Optional[str] = ""
    content: Optional[str] = ""
    extraction_method: Optional[str] = "Ollama (IA)"
    user_edited: bool = False
    images: List[Dict[str, Any]] = Field(default_factory=list)
    participants: List[ParticipantDTO] = Field(default_factory=list)

class RelintUpdateRequest(BaseModel):
    """Payload for updating user-editable RELINT metadata and content."""
    subject: Optional[str] = None
    main_fact: Optional[str] = None
    summary: Optional[str] = None
    content: Optional[str] = None
    date_of_fact: Optional[str] = None
    time_of_fact: Optional[str] = None
    bm_group: Optional[str] = None
    relint_type: Optional[str] = None
    municipality: Optional[str] = None
    neighborhood: Optional[str] = None
    address: Optional[str] = None
    police_unit: Optional[str] = None
    coordinates: Optional[str] = None
    map_url: Optional[str] = None
    participants: Optional[List[ParticipantDTO]] = None
    
    # Homicide specific optional fields
    registry_number: Optional[str] = None
    registry_agency: Optional[str] = None
    registry_year: Optional[str] = None
    fact_type: Optional[str] = None
    motivation: Optional[str] = None
