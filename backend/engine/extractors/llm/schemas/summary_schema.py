# -*- coding: utf-8 -*-
"""
Schema Pydantic estruturado para extração isolada e dedicada de Síntese e Assunto.
"""

from typing import Optional
from pydantic import BaseModel, Field


class SummaryExtraction(BaseModel):
    """
    Schema focado exclusivamente na extração do assunto e redação da síntese factual.
    """
    subject: Optional[str] = Field(
        default=None,
        description="Extraia com precisão o ASSUNTO do relatório de inteligência."
    )
    summary: str = Field(
        description="Redija uma síntese factual explicativa e coesa (2 a 4 frases) narrando o que aconteceu, dinâmica dos fatos e desfecho da ação."
    )
