from abc import ABC, abstractmethod

class ILlmProcessor(ABC):
    """
    Interface (Porta) para o processamento de linguagem natural e estruturação de boletins.
    """

    @abstractmethod
    def process_text(self, text: str, questions: dict = None) -> dict:
        """
        Processa o texto de um boletim de ocorrência respondendo a perguntas estruturadas.

        :param text: Texto completo extraído e limpo do boletim de ocorrência.
        :param questions: Dicionário mapeando chaves para perguntas de linguagem natural.
        :return: Dicionário contendo as respostas extraídas correspondentes a cada chave.
        """
        pass

