# -*- coding: utf-8 -*-
"""
Interface abstrata para o processamento de linguagem natural e estruturação via LLM.
"""

from abc import ABC, abstractmethod
from typing import Any, Optional


class ILlmProcessor(ABC):
    """
    Interface (Porta) para o processamento de linguagem natural e estruturação de boletins.
    """

    @abstractmethod
    def process_text(self, text: str, questions: dict = None, schema_model: type = None, pre_extracted_entities: list = None) -> dict:
        """
        Processa o texto de um boletim de ocorrência respondendo a perguntas estruturadas.

        :param text: Texto completo extraído e limpo do boletim de ocorrência.
        :param questions: Dicionário mapeando chaves para perguntas de linguagem natural.
        :param schema_model: Opcional, classe Pydantic a ser usada para gerar o schema de saída.
        :param pre_extracted_entities: Opcional, lista de entidades previamente extraídas (Zero-Shot).
        :return: Dicionário contendo as respostas extraídas correspondentes a cada chave.
        """
        pass
