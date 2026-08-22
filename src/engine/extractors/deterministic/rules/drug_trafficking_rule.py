# -*- coding: utf-8 -*-
"""
Regra determinística de extração especializada de Tráfico de Drogas (sem IA).
Extrai tipo de substâncias e quantidades apreendidas via regex.
"""

import re
from typing import Any, Dict, List, Tuple
from src.engine.extractors.base import ExtractionAlert
from src.engine.extractors.deterministic.rules.base_rule import IDeterministicRule


class DrugTraffickingDeterministicRule(IDeterministicRule):
    """Regra determinística para ocorrências de tráfico de entorpecentes."""

    @property
    def name(self) -> str:
        return "Tráfico de Drogas (Determinístico)"

    def extract_specialty_data(self, text: str) -> Tuple[Dict[str, Any], List[ExtractionAlert]]:
        """
        Extrai tipo_drogas e quantidade_drogas a partir do texto do RELINT.
        """
        alerts: List[ExtractionAlert] = []
        data: Dict[str, Any] = {
            "drug_types": [],
            "drug_quantities": ""
        }

        if not text:
            return data, alerts

        text_upper = text.upper()

        # Identifica tipos de entorpecentes
        drug_types = []
        if re.search(r'\b(?:COCA[ÍI]NA|PINO[S]?\s+DE\s+COCA[ÍI]NA)\b', text_upper):
            drug_types.append("Cocaína")
        if re.search(r'\b(?:MACONHA|BUCHA[S]?\s+DE\s+MACONHA|TIJOLO[S]?\s+DE\s+MACONHA)\b', text_upper):
            drug_types.append("Maconha")
        if re.search(r'\b(?:CRACK|PEDRA[S]?\s+DE\s+CRACK)\b', text_upper):
            drug_types.append("Crack")
        if re.search(r'\b(?:ECSTASY|EXTASY|MDMA|LSD)\b', text_upper):
            drug_types.append("Sintéticos")

        data["drug_types"] = drug_types

        # Identifica pesos ou quantidades (ex: 500g, 1,5kg, 32 pedras, 15 porções)
        quantities = re.findall(
            r'(?i)\b\d+(?:[,\.]\d+)?\s*(?:g|kg|gramas|quilos|pedras|buchas|pinos|por[çc][õo]es|tijolos)\b',
            text
        )
        if quantities:
            data["drug_quantities"] = ", ".join(quantities[:5])

        return data, alerts
