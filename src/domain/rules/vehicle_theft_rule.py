from typing import List
from src.domain.rules.base_rule import IncidentRule

class VehicleTheftRule(IncidentRule):
    @property
    def name(self) -> str:
        return "Furto de Veículo"

    @property
    def db_name(self) -> str:
        return "vehicle_theft.json"
        
    def get_schema_model(self) -> type:
        from src.domain.entities import VehicleTheftReport
        return VehicleTheftReport

    def get_bm_group(self, filename: str = "", subject: str = "") -> str:
        from src.domain.entities import BmGroup
        return BmGroup.FURTO_VEICULO.value

    @property
    def keywords(self) -> List[str]:
        return ["furto", "veículo", "veiculo", "carro", "moto", "caminhonete"]

    def matches_filter(self, text: str) -> bool:
        if not text: return False
        text_lower = text.lower()
        return "furto" in text_lower and any(k in text_lower for k in ["veículo", "veiculo", "carro", "moto", "caminhonete", "motocicleta"])

    @property
    def questions(self) -> dict:
        return {
            "natureza": "Qual o crime ou fato principal ocorrido?",
            "objeto": "O que foi furtado?",
        }

    def validate_qa_results(self, qa_results: dict) -> bool:
        natureza = qa_results.get("natureza", "").lower()
        objeto = qa_results.get("objeto", "").lower()
        
        is_theft = "furto" in natureza
        is_vehicle = any(term in objeto or term in natureza for term in ["veículo", "veiculo", "carro", "moto", "caminhonete", "motocicleta"])
        return is_theft and is_vehicle
