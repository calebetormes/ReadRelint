# -*- coding: utf-8 -*-
"""
Extrator especializado de Síntese e Assunto via LLM (Passo 1 do Pipeline Multi-Pass).
"""

import logging
from typing import Any, Dict, Optional

from backend.engine.cleaners.text_cleaner import (
    extract_fallback_summary,
    extract_subject_fallback,
)
from backend.engine.extractors.llm.llm_processor import ILlmProcessor
from backend.engine.extractors.llm.schemas.summary_schema import SummaryExtraction
from backend.engine.extractors.llm.validators.llm_response_validator import sanitize_summary

logger = logging.getLogger(__name__)


class SummaryExtractor:
    """
    Extrator cognitivo dedicado para redação de síntese narrativa e extração de assunto.
    """

    def __init__(self, processor: ILlmProcessor) -> None:
        self.processor = processor

    def extract(self, text: str, filename: str = "") -> Dict[str, str]:
        """
        Executa a leitura focada exclusivamente na geração da síntese factual.
        Retorna um dicionário com 'subject' e 'summary'.
        """
        if not text or not text.strip():
            fallback_sub = extract_subject_fallback("", filename=filename)
            return {
                "subject": fallback_sub,
                "summary": fallback_sub
            }

        fallback_subject = extract_subject_fallback(text, filename=filename)
        fallback_summary = extract_fallback_summary(text, subject=fallback_subject)

        try:
            logger.info("Executando Pass 1 (Síntese) via LLM...")
            raw_response = self.processor.process_text(
                text=text,
                schema_model=SummaryExtraction
            )

            if not isinstance(raw_response, dict):
                logger.warning("Resposta da LLM no Pass 1 não é um dicionário. Usando fallback.")
                return {
                    "subject": fallback_subject,
                    "summary": fallback_summary
                }

            extracted_subject = (raw_response.get("subject") or "").strip()
            if not extracted_subject or len(extracted_subject) < 5:
                extracted_subject = fallback_subject

            raw_summary = raw_response.get("summary") or ""
            clean_summary = sanitize_summary(raw_summary, subject=extracted_subject)

            # Se a síntese for rejeitada ou vazia, recorre ao fallback seguro
            if not clean_summary or len(clean_summary) < 40:
                logger.info("Síntese da LLM rejeitada ou vazia. Aplicando fallback determinístico.")
                clean_summary = fallback_summary

            return {
                "subject": extracted_subject,
                "summary": clean_summary
            }

        except Exception as err:
            logger.error(f"Erro na execução do SummaryExtractor: {err}. Recorrendo ao fallback.")
            return {
                "subject": fallback_subject,
                "summary": fallback_summary
            }
