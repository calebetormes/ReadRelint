from abc import ABC, abstractmethod
from typing import Optional

class IProcessedRegistry(ABC):
    """
    Interface (Porta) para rastreamento de histórico de processamento de arquivos.
    """

    @abstractmethod
    def is_processed(self, filename: str, rule_name: str) -> bool:
        """
        Verifica se um arquivo específico já foi processado sob uma determinada regra.

        :param filename: Nome do arquivo analisado.
        :param rule_name: Nome da regra aplicada.
        :return: True se já processado, False caso contrário.
        """
        pass

    @abstractmethod
    def register_processed(self, filename: str, rule_name: str, status: str) -> None:
        """
        Registra que um arquivo foi processado com uma regra e status específicos.

        :param filename: Nome do arquivo analisado.
        :param rule_name: Nome da regra aplicada.
        :param status: O status final do processamento (ex: 'confirmed', 'filtered_pre_llm', 'filtered_post_llm').
        """
        pass

    @abstractmethod
    def clear(self) -> None:
        """
        Limpa todos os registros do histórico de processamento.
        """
        pass

    @abstractmethod
    def remove_record(self, filename: str, rule_name: str) -> None:
        """
        Remove um registro específico de arquivo processado sob uma regra.

        :param filename: Nome do arquivo analisado.
        :param rule_name: Nome da regra aplicada.
        """
        pass

    @abstractmethod
    def get_all_records(self) -> dict:
        """
        Retorna todo o dicionário de registros salvos no histórico.
        """
        pass

    @abstractmethod
    def save_user_edit(self, filename: str, rule_name: str, fact: str) -> None:
        """
        Salva a edição manual do usuário para o fato ocorrido de um arquivo específico.

        :param filename: Nome do arquivo original.
        :param rule_name: Nome da regra de incidentes.
        :param fact: Novo fato ocorrido definido pelo usuário.
        """
        pass

    @abstractmethod
    def get_user_edit(self, filename: str, rule_name: str) -> Optional[str]:
        """
        Recupera a edição manual do usuário para o fato ocorrido se existir.

        :param filename: Nome do arquivo original.
        :param rule_name: Nome da regra de incidentes.
        :return: O fato editado ou None.
        """
        pass
