from typing import List
from src.engine.extractors.llm.rules.base_rule import IncidentRule

class VehicleRobberyRule(IncidentRule):
    @property
    def name(self) -> str:
        return "Roubo de Veículo"

    @property
    def db_name(self) -> str:
        return "vehicle_robbery.json"
        
    def get_schema_model(self) -> type:
        from src.dashboard.backend.core.entities import VehicleRobberyReport
        return VehicleRobberyReport

    def get_bm_group(self, filename: str = "", subject: str = "") -> str:
        from src.dashboard.backend.core.entities import BmGroup
        return BmGroup.ROUBO_VEICULO.value

    @property
    def keywords(self) -> List[str]:
        return ["roubo", "assalto", "veículo", "veiculo", "carro", "moto", "caminhonete"]

    def matches_filter(self, text: str) -> bool:
        if not text: return False
        text_lower = text.lower()
        return "roubo" in text_lower and any(k in text_lower for k in ["veículo", "veiculo", "carro", "moto", "caminhonete", "motocicleta"])

    @property
    def questions(self) -> dict:
        return {
            "natureza": "Qual o crime ou fato principal ocorrido?",
            "objeto": "O que foi roubado?",
        }

    def validate_qa_results(self, qa_results: dict) -> bool:
        natureza = qa_results.get("natureza", "").lower()
        objeto = qa_results.get("objeto", "").lower()
        
        is_robbery = "roubo" in natureza or "assalto" in natureza
        is_vehicle = any(term in objeto or term in natureza for term in ["veículo", "veiculo", "carro", "moto", "caminhonete", "motocicleta"])
        return is_robbery and is_vehicle
