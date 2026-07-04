from abc import ABC, abstractmethod
from src.domain.entities import IncidentReport

class ILlmProcessor(ABC):
    """
    Interface (Porta) para o processamento de linguagem natural e estruturação de boletins.
    """

    @abstractmethod
    def process_incident_text(self, text: str) -> IncidentReport:
        """
        Processa o texto bruto de um boletim de ocorrência e extrai as informações estruturadas.

        :param text: Texto completo extraído do boletim de ocorrência.
        :return: Uma entidade de domínio IncidentReport com os dados estruturados.
        """
        pass
