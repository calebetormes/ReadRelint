from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, model_validator

class Participant(BaseModel):
    """
    Representa um participante citado no RELINT.
    """
    name: Optional[str] = Field(default=None, description="Nome completo da pessoa")
    nickname: Optional[str] = Field(default=None, description="Alcunha, apelido ou vulgo")
    document: Optional[str] = Field(default=None, description="Documento de identificação (CPF ou RG)")


class IncidentReport(BaseModel):
    """
    Representa a entidade de domínio de um relatório de inteligência (RELINT) processado.
    """
    source_file: str = Field(description="Nome do arquivo PDF de origem")
    subject: Optional[str] = Field(default=None, description="Assunto principal do relatório")
    date_of_fact: Optional[str] = Field(default=None, description="Data em que o fato ocorreu")
    participants: Optional[List[Participant]] = Field(default=[], description="Lista de participantes do caso")
    content: Optional[str] = Field(default=None, description="Histórico completo e literal do RELINT")
    summary: Optional[str] = Field(default=None, description="Resumo de um parágrafo elaborado do RELINT")
    bm_group: Optional[str] = Field(default=None, description="Enquadramento do fato no grupo BM (Roubos, Furtos, Homicídios, Outros)")
    user_edited: bool = Field(default=False, description="Indica se o relatório foi editado manualmente pelo usuário")

    # Fallback/Retrocompatibilidade para métodos ou acessos antigos se necessário
    @model_validator(mode="before")
    @classmethod
    def handle_legacy_fields(cls, data: Any) -> Any:
        if isinstance(data, dict):
            # Se vier do banco antigo, tenta mapear para manter retrocompatibilidade parcial
            if "main_fact" in data and not data.get("subject"):
                data["subject"] = data["main_fact"]
            if "occurred_fact" in data and not data.get("subject"):
                data["subject"] = data["occurred_fact"]
            if "clean_content" in data and not data.get("content"):
                data["content"] = data["clean_content"]
            if "history_summary" in data and not data.get("summary"):
                data["summary"] = data["history_summary"]
            if "incident_group" in data and not data.get("bm_group"):
                data["bm_group"] = data["incident_group"]
        return data

    @property
    def main_fact(self) -> Optional[str]:
        return self.subject

    @main_fact.setter
    def main_fact(self, value: Optional[str]):
        self.subject = value

    @property
    def clean_content(self) -> Optional[str]:
        return self.content

    @clean_content.setter
    def clean_content(self, value: Optional[str]):
        self.content = value
