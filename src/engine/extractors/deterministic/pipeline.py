# -*- coding: utf-8 -*-
"""
Pipeline orquestrador de extração determinística (sem IA).
Executa as etapas de extração de participantes, síntese, assunto, classificação BM e geolocalização,
consolidando os resultados e emitindo alertas de execução.
"""

from typing import Any, Dict
from src.engine.cleaners.bm_classifier import classify_bm_group
from src.engine.cleaners.text_cleaner import (
    clean_relint_text,
    extract_fallback_summary,
    extract_subject_fallback,
    resolve_coordinates_and_map_info,
)
from src.engine.extractors.base import ExtractionAlert, ExtractionResult, IExtractor
from src.engine.extractors.deterministic.participants.participant_extractor import ParticipantExtractor


class DeterministicPipeline(IExtractor):
    """Pipeline mestre de extração determinística sem uso de LLM."""

    def __init__(self) -> None:
        self.participant_extractor = ParticipantExtractor()

    def extract(self, text: str, filename: str = "", **kwargs: Any) -> ExtractionResult:
        """
        Executa a extração determinística completa de um documento RELINT.
        """
        result = ExtractionResult(
            data={},
            extraction_method="Regex (Sem IA)",
            alerts=[],
            success=True
        )

        if not text or not text.strip():
            result.add_alert(
                level="error",
                stage="input_validation",
                message="Texto do documento está vazio ou não pôde ser lido."
            )
            result.success = False
            return result

        cleaned_text = clean_relint_text(text)

        # 1. Extração de Assunto
        try:
            subject = extract_subject_fallback(cleaned_text, filename)
            result.data["subject"] = subject
        except Exception as e:
            result.add_alert(level="warning", stage="subject_extractor", message=f"Erro ao extrair assunto: {e}")
            result.data["subject"] = "Não informado"

        # 2. Extração de Síntese / Resumo
        try:
            summary = extract_fallback_summary(cleaned_text, subject=result.data.get("subject", ""))
            result.data["summary"] = summary
            result.data["main_fact"] = summary
        except Exception as e:
            result.add_alert(level="warning", stage="summary_extractor", message=f"Erro ao extrair síntese: {e}")
            result.data["summary"] = ""
            result.data["main_fact"] = ""

        # 3. Extração Especialista de Participantes
        try:
            participants, part_alerts = self.participant_extractor.extract_participants(cleaned_text)
            result.data["participants"] = participants
            result.alerts.extend(part_alerts)
        except Exception as e:
            result.add_alert(level="error", stage="participants_extractor", message=f"Erro na extração de participantes: {e}")
            result.data["participants"] = []

        # 4. Classificação de Grupo BM
        try:
            bm_group = classify_bm_group(filename, result.data.get("subject", ""), cleaned_text)
            result.data["bm_group"] = bm_group
        except Exception as e:
            result.add_alert(level="warning", stage="bm_classifier", message=f"Erro na classificação BM: {e}")
            result.data["bm_group"] = "Outros"

        # 5. Resolução de Coordenadas e Mapa
        try:
            map_url, coords = resolve_coordinates_and_map_info(cleaned_text)
            result.data["map_url"] = map_url
            result.data["coordinates"] = coords
        except Exception as e:
            result.add_alert(level="warning", stage="geo_resolver", message=f"Erro na resolução de coordenadas: {e}")
            result.data["map_url"] = None
            result.data["coordinates"] = None

        return result
