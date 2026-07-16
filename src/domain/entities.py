from typing import Optional, List, Any
from pydantic import BaseModel, Field

class IncidentReport(BaseModel):
    """
    Representa a entidade de domínio de um relatório de boletim de ocorrência.
    Suporta campos novos (content) e campos legados de forma opcional para retrocompatibilidade.
    """
    source_file: str = Field(description="Nome do arquivo PDF de origem")
    content: Optional[str] = Field(default=None, description="Conteúdo ou resumo estruturado do fato extraído pela IA")

    # Campos legados (opcionais) para manter compatibilidade com dados já cadastrados
    relint_number: Optional[str] = Field(default=None)
    subject: Optional[str] = Field(default=None)
    diffusion: Optional[str] = Field(default=None)
    attachment: Optional[str] = Field(default=None)
    incident_nature: Optional[str] = Field(default=None)
    incident_group: Optional[str] = Field(default=None)
    incident_type: Optional[str] = Field(default=None)
    incident_time: Optional[str] = Field(default=None)
    address: Optional[Any] = Field(default=None)
    participants: Optional[List[Any]] = Field(default=None)
    vehicles: Optional[List[Any]] = Field(default=None)
    attending_officer: Optional[str] = Field(default=None)
    history_summary: Optional[str] = Field(default=None)
