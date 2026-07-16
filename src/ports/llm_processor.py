from abc import ABC, abstractmethod

class ILlmProcessor(ABC):
    """
    Interface (Porta) para o processamento de linguagem natural e estruturação de boletins.
    """

    @abstractmethod
    def process_text(self, text: str) -> str:
        """
        Processa o texto de um boletim de ocorrência e extrai seu conteúdo principal.

        :param text: Texto completo extraído e limpo do boletim de ocorrência.
        :return: O conteúdo/resumo estruturado do fato.
        """
        pass
