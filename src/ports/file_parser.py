from abc import ABC, abstractmethod
from pathlib import Path

class IFileParser(ABC):
    """
    Interface (Porta) para extração de texto a partir de arquivos.
    """

    @abstractmethod
    def extract_text(self, file_path: Path) -> str:
        """
        Extrai o conteúdo textual de um arquivo (ex: PDF).

        :param file_path: Caminho completo para o arquivo.
        :return: O texto extraído do arquivo.
        """
        pass
