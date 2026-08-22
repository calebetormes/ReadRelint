from typing import List
from backend.engine.extractors.llm.rules.base_rule import IncidentRule

class PedestrianRobberyRule(IncidentRule):
    @property
    def name(self) -> str:
        return "Roubo a Pedestre"

    @property
    def db_name(self) -> str:
        return "pedestrian_robbery.json"
        
    def get_schema_model(self) -> type:
        from backend.dashboard.backend.core.entities import PedestrianRobberyReport
        return PedestrianRobberyReport

    def get_bm_group(self, filename: str = "", subject: str = "") -> str:
        from backend.dashboard.backend.core.entities import BmGroup
        return BmGroup.ROUBO_PEDESTRE.value

    @property
    def keywords(self) -> List[str]:
        return ["roubo", "assalto", "pedestre", "transeunte", "via pública", "via publica"]

    def matches_filter(self, text: str) -> bool:
        if not text: return False
        text_lower = text.lower()
        return "roubo" in text_lower and any(k in text_lower for k in ["pedestre", "transeunte", "via pública", "via publica", "rua"])

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
        is_pedestrian = any(term in local or term in natureza for term in ["pedestre", "transeunte", "via pública", "via publica", "rua"])
        return is_robbery and is_pedestrian
