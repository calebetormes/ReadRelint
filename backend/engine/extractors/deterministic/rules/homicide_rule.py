# -*- coding: utf-8 -*-
"""
Regra determinística de extração especializada de dados de Homicídios (sem IA).
Extrai tipo de fato (tentado/consumado), motivação provável e delegacia/órgão policial via regex.
"""

import re
from typing import Any, Dict, List, Tuple
from backend.engine.extractors.base import ExtractionAlert
from backend.engine.extractors.deterministic.rules.base_rule import IDeterministicRule


class HomicideDeterministicRule(IDeterministicRule):
    """Regra determinística para ocorrências de homicídio."""

    @property
    def name(self) -> str:
        return "Homicídios (Determinístico)"

    def extract_specialty_data(self, text: str) -> Tuple[Dict[str, Any], List[ExtractionAlert]]:
        """
        Extrai tipo_fato e motivacao a partir do texto do RELINT via regex determinístico.
        """
        alerts: List[ExtractionAlert] = []
        data: Dict[str, Any] = {
            "fact_type": "Consumado",
            "motivation": "Desconhecida"
        }

        if not text:
            return data, alerts

        text_upper = text.upper()

        # 1. Detecção do Tipo de Fato (Tentado vs Consumado)
        if re.search(r'\b(?:HOMIC[ÍI]DIO\s+TENTADO|TENTATIVA\s+DE\s+HOMIC[ÍI]DIO|TENTADO)\b', text_upper):
            data["fact_type"] = "Tentado"
        elif re.search(r'\b(?:HOMIC[ÍI]DIO\s+CONSUMADO|CONSUMADO|[ÓO]BITO|MORREU|CAD[ÁA]VER)\b', text_upper):
            data["fact_type"] = "Consumado"

        # 2. Detecção de Motivação
        motivation_map = [
            (r'\b(?:TR[ÁA]FICO|FAC[ÇC][ÃA]O|DISPUTA\s+DE\s+TERRIT[ÓO]RIO|PONTO\s+DE\s+DROGA)\b', "Tráfico de Drogas"),
            (r'\b(?:FEMINIC[ÍI]DIO|VIOL[ÊE]NCIA\s+DOM[ÉE]STICA|EX-COMPANHEIR[OA]|EX-MARIDO)\b', "Feminicídio"),
            (r'\b(?:LATROC[ÍI]NIO|ROUBO\s+SEGUIDO\s+DE\s+MORTE)\b', "Latrocínio"),
            (r'\b(?:CONFRONTO|OPOSI[ÇC][ÃA]O\s+[ÀA]\s+A[ÇC][ÃA]O\s+POLICIAL|INTERVEN[ÇC][ÃA]O\s+POLICIAL)\b', "Oposição à Ação Policial"),
            (r'\b(?:DESAVEN[ÇC]A|DISCUSS[ÃA]O|BRIGA|MOTIVO\s+F[ÚU]TIL)\b', "Desavença / Briga"),
        ]

        for pattern, mot in motivation_map:
            if re.search(pattern, text_upper):
                data["motivation"] = mot
                break

        return data, alerts
