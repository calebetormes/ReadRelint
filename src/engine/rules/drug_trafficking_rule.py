from typing import List
from src.engine.rules.base_rule import IncidentRule

class DrugTraffickingRule(IncidentRule):
    @property
    def name(self) -> str:
        return "Prisão por Tráfico"

    @property
    def db_name(self) -> str:
        return "drug_trafficking.json"
        
    def get_schema_model(self) -> type:
        from src.dashboard.backend.core.entities import DrugTraffickingReport
        return DrugTraffickingReport

    def get_bm_group(self, filename: str = "", subject: str = "") -> str:
        from src.dashboard.backend.core.entities import BmGroup
        return BmGroup.PRISAO_TRAFICO.value

    @property
    def keywords(self) -> List[str]:
        return ["tráfico", "trafico", "drogas", "entorpecentes", "maconha", "cocaína", "cocaina", "crack", "apreensão"]

    def matches_filter(self, text: str) -> bool:
        if not text: return False
        text_lower = text.lower()
        return any(k in text_lower for k in self.keywords)

    @property
    def questions(self) -> dict:
        return {
            "natureza": "Qual o crime ou fato principal ocorrido?",
            "drogas": "Foram apreendidas drogas ou entorpecentes?",
        }

    def validate_qa_results(self, qa_results: dict) -> bool:
        natureza = qa_results.get("natureza", "").lower()
        drogas = qa_results.get("drogas", "").lower()
        
        valid_terms = ["tráfico", "trafico", "entorpecente", "droga", "maconha", "cocaína", "cocaina", "crack"]
        return any(term in natureza or term in drogas for term in valid_terms)
