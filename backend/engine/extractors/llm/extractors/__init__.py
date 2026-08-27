# -*- coding: utf-8 -*-
"""
Pacote de extratores especializados para o pipeline multi-pass cognitivo.
"""

from backend.engine.extractors.llm.extractors.summary_extractor import SummaryExtractor
from backend.engine.extractors.llm.extractors.location_extractor import LocationExtractor

__all__ = ["SummaryExtractor", "LocationExtractor"]
