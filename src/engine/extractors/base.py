# -*- coding: utf-8 -*-
"""
Contratos e estruturas base para os motores de extração (LLM e Determinístico).
Define o padrão de alertas e resultados de processamento.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List
from abc import ABC, abstractmethod


@dataclass
class ExtractionAlert:
    """Representa um alerta ou aviso gerado durante qualquer etapa do pipeline de extração."""
    level: str  # 'info', 'warning', 'error'
    stage: str  # ex: 'spacy_ner', 'ibge_validator', 'structured_parser'
    message: str
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict[str, str]:
        return {
            "level": self.level,
            "stage": self.stage,
            "message": self.message,
            "timestamp": self.timestamp
        }


@dataclass
class ExtractionResult:
    """Resultado consolidado da extração contendo os dados estruturados e alertas emitidos."""
    data: Dict[str, Any]
    extraction_method: str
    alerts: List[ExtractionAlert] = field(default_factory=list)
    success: bool = True

    def add_alert(self, level: str, stage: str, message: str) -> None:
        """Adiciona um novo alerta à lista de avisos da extração."""
        self.alerts.append(ExtractionAlert(level=level, stage=stage, message=message))


class IExtractor(ABC):
    """Interface abstrata para módulos de extração de dados."""

    @abstractmethod
    def extract(self, text: str, **kwargs: Any) -> ExtractionResult:
        """Executa a extração estruturada a partir do texto."""
        pass
