# -*- coding: utf-8 -*-
"""
Pipeline orquestrador de extração 100% Cognitivo via LLM (Ollama).
Processa o documento exclusivamente com Inteligência Artificial, sem interferência
ou fallbacks determinísticos/regex.
"""

from typing import Any, Dict, Optional
from backend.core.entities import IncidentReport
from backend.engine.cleaners.text_cleaner import clean_relint_text
from backend.engine.extractors.base import ExtractionAlert, ExtractionResult, IExtractor
from backend.engine.extractors.llm.llm_processor import ILlmProcessor
from backend.engine.extractors.llm.ollama_client import OllamaClient


from backend.engine.extractors.llm.extractors.summary_extractor import SummaryExtractor
from backend.engine.extractors.llm.extractors.location_extractor import LocationExtractor


class LlmPipeline(IExtractor):
    """
    Pipeline especialista de extração puramente cognitiva via LLM.
    """

    def __init__(self, processor: Optional[ILlmProcessor] = None) -> None:
        self.processor = processor or OllamaClient()
        self.summary_extractor = SummaryExtractor(self.processor)
        self.location_extractor = LocationExtractor(self.processor)

    def extract(
        self,
        text: str,
        filename: str = "",
        rule: Any = None,
        pre_extracted_entities: list = None,
        **kwargs: Any
    ) -> ExtractionResult:
        """
        Executa a extração 100% orientada por LLM com JSON Schema estruturado.
        """
        result = ExtractionResult(
            data={},
            extraction_method="Ollama (IA)",
            alerts=[],
            success=True
        )

        if not text or not text.strip():
            result.add_alert(
                level="error",
                stage="llm_input_validation",
                message="Texto do documento está vazio ou inválido para envio à LLM."
            )
            result.success = False
            return result

        cleaned_text = clean_relint_text(text)

        # Determina o Schema e perguntas de suporte da regra
        questions = getattr(rule, "questions", {}) if rule else {}
        schema_model = rule.get_schema_model() if rule and hasattr(rule, "get_schema_model") else IncidentReport

        try:
            raw_response = self.processor.process_text(
                cleaned_text,
                questions=questions,
                schema_model=schema_model,
                pre_extracted_entities=pre_extracted_entities
            )


            if isinstance(raw_response, dict):
                from backend.engine.extractors.llm.validators.llm_response_validator import validate_and_normalize_llm_response
                result.data = validate_and_normalize_llm_response(raw_response)
            else:
                result.data = {}
                result.add_alert(
                    level="warning",
                    stage="llm_json_parser",
                    message="Resposta da LLM não pôde ser interpretada como um dicionário JSON."
                )

            # Pass 1: Extração Dedicada de Síntese e Assunto (Alta Fidelidade)
            summary_data = self.summary_extractor.extract(cleaned_text, filename=filename)
            if summary_data.get("summary"):
                result.data["summary"] = summary_data["summary"]
            if summary_data.get("subject") and (not result.data.get("subject") or len(str(result.data.get("subject"))) < 5):
                result.data["subject"] = summary_data["subject"]

            # Pass 2: Extração Dedicada de Localização e Georreferenciamento
            location_data = self.location_extractor.extract(cleaned_text, filename=filename)
            for loc_key in ["address", "municipality", "neighborhood", "police_unit", "coordinates", "map_url", "geo_precision"]:
                if location_data.get(loc_key):
                    result.data[loc_key] = location_data[loc_key]


        except Exception as err:
            result.success = False
            result.add_alert(
                level="error",
                stage="llm_execution",
                message=f"Falha na execução do modelo Ollama: {err}"
            )

        return result
