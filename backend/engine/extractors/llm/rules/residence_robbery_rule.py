from typing import List
from backend.engine.extractors.llm.rules.base_rule import IncidentRule

class ResidenceRobberyRule(IncidentRule):
    @property
    def name(self) -> str:
        return "Roubo a Residência"

    @property
    def db_name(self) -> str:
        return "residence_robbery.json"
        
    def get_schema_model(self) -> type:
        from backend.dashboard.backend.core.entities import ResidenceRobberyReport
        return ResidenceRobberyReport

    def get_bm_group(self, filename: str = "", subject: str = "") -> str:
        from backend.dashboard.backend.core.entities import BmGroup
        return BmGroup.ROUBO_RESIDENCIA.value

    @property
    def keywords(self) -> List[str]:
        return ["roubo", "assalto", "residência", "residencia", "casa", "apartamento"]

    def matches_filter(self, text: str) -> bool:
        if not text: return False
        text_lower = text.lower()
        return "roubo" in text_lower and any(k in text_lower for k in ["residência", "residencia", "casa", "apartamento"])

    @property
    def questions(self) -> dict:
        return {
            "natureza": "Qual o crime ou fato principal ocorrido?",
            "local": "Onde ocorreu o roubo?",
        }

    def validate_qa_results(self, qa_results: dict) -> bool:
        natureza = qa_results.get("natureza", "").lower()
        local = qa_results.get("local", "").lower()
        
        is_robbery = "roubo" in natureza or "assalto" in natureza
        is_residence = any(term in local or term in natureza for term in ["residência", "residencia", "casa", "apartamento", "sítio", "sitio", "chácara"])
        return is_robbery and is_residence
