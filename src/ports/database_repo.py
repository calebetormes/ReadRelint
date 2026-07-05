from abc import ABC, abstractmethod
from typing import List, Optional
from src.domain.entities import IncidentReport

class IDatabaseRepo(ABC):
    """
    Interface (Porta) para persistência e consulta de boletins de ocorrência estruturados.
    """

    @abstractmethod
    def save(self, report: IncidentReport) -> str:
        """
        Salva um relatório de incidente no banco de dados.

        :param report: A entidade IncidentReport a ser persistida.
        :return: O ID único gerado/atribuído ao relatório salvo.
        """
        pass

    @abstractmethod
    def get_by_id(self, report_id: str) -> Optional[IncidentReport]:
        """
        Busca um relatório de incidente pelo seu ID único.

        :param report_id: ID do relatório no banco.
        :return: A entidade IncidentReport correspondente, ou None se não for encontrada.
        """
        pass

    @abstractmethod
    def get_all(self) -> List[IncidentReport]:
        """
        Retorna todos os relatórios de incidentes cadastrados no banco de dados.

        :return: Lista contendo todas as entidades IncidentReport.
        """
        pass

    @abstractmethod
    def exists_by_source_file(self, filename: str) -> bool:
        """
        Verifica se um relatório originado do arquivo fornecido já existe no banco de dados.

        :param filename: Nome do arquivo PDF.
        :return: True se já existir, False caso contrário.
        """
        pass



