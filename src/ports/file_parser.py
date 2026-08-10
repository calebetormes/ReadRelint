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

    def extract_images(self, file_path: Path, output_dir: Path) -> list:
        """
        Extrai imagens incorporadas em um arquivo e as salva no diretório informado.

        :param file_path: Caminho para o arquivo original.
        :param output_dir: Pasta onde as imagens serão gravadas.
        :return: Lista de dicionários contendo metadados das imagens salvas.
        """
        return []

