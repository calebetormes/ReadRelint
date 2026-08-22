# -*- coding: utf-8 -*-
"""
Interface base para regras de extração determinística (sem IA).
Cada regra especializada implementa métodos de extração baseados em padrões regex e heurísticas.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from src.engine.extractors.base import ExtractionAlert


class IDeterministicRule(ABC):
    """Contrato base para regras especializadas de extração determinística."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Nome identificador da regra especializada."""
        pass

    @abstractmethod
    def extract_specialty_data(self, text: str) -> tuple[Dict[str, Any], List[ExtractionAlert]]:
        """
        Executa a extração especializada de atributos específicos do tipo de crime a partir do texto.
        Retorna uma tupla contendo o dicionário de campos extraídos e a lista de alertas.
        """
        pass
