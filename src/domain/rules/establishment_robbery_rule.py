from typing import List
from src.domain.rules.base_rule import IncidentRule

class EstablishmentRobberyRule(IncidentRule):
    @property
    def name(self) -> str:
        return "Roubo a Estabelecimento"

    @property
    def db_name(self) -> str:
        return "establishment_robbery.json"
        
    def get_schema_model(self) -> type:
        from src.domain.entities import EstablishmentRobberyReport
        return EstablishmentRobberyReport

    def get_bm_group(self, filename: str = "", subject: str = "") -> str:
        from src.domain.entities import BmGroup
        return BmGroup.ROUBO_ESTABELECIMENTO.value

    @property
    def keywords(self) -> List[str]:
        return ["roubo", "assalto", "estabelecimento", "comércio", "comercio", "lotérica", "loterica", "banco", "posto"]

    def matches_filter(self, text: str) -> bool:
        if not text: return False
        text_lower = text.lower()
        return "roubo" in text_lower and any(k in text_lower for k in ["estabelecimento", "comércio", "comercio", "lotérica", "banco", "posto", "farmácia", "mercado"])

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
        is_establishment = any(term in local or term in natureza for term in ["estabelecimento", "comércio", "comercio", "lotérica", "banco", "posto", "farmácia", "mercado", "loja"])
        return is_robbery and is_establishment
