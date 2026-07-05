from abc import ABC, abstractmethod
from src.domain.entities import IncidentReport

class ILlmProcessor(ABC):
    """
    Interface (Porta) para o processamento de linguagem natural e estruturação de boletins.
    """

    @abstractmethod
    def extract_metadata(self, text: str) -> dict:
        """
        Extrai informações administrativas do cabeçalho do RELINT (número, assunto, difusão, anexo).

        :param text: Texto do cabeçalho ou texto completo.
        :return: Um dicionário contendo os metadados do documento.
        """
        pass

    @abstractmethod
    def segment_occurrences(self, text: str) -> list:
        """
        Analisa o texto e o divide em ocorrências policiais individuais estruturadas por grupo.

        :param text: Texto do RELINT.
        :return: Lista de dicionários representando as ocorrências identificadas.
        """
        pass

    @abstractmethod
    def process_incident_text(self, text: str) -> IncidentReport:
        """
        Processa o texto bruto de um boletim de ocorrência e extrai as informações estruturadas.

        :param text: Texto completo extraído do boletim de ocorrência.
        :return: Uma entidade de domínio IncidentReport com os dados estruturados.
        """
        pass


