import fitz  # PyMuPDF
from pathlib import Path
from src.ports.file_parser import IFileParser

class PdfReader(IFileParser):
    """
    Implementação concreta (Adapter) para extração de texto de arquivos PDF
    utilizando a biblioteca PyMuPDF (fitz).
    """

    def extract_text(self, file_path: Path) -> str:
        """
        Abre o PDF informado, extrai o texto de todas as páginas e o concatena.

        :param file_path: Caminho completo para o arquivo PDF.
        :return: Texto bruto extraído e concatenado das páginas do PDF.
        :raises FileNotFoundError: Se o arquivo especificado não existir.
        :raises ValueError: Se o arquivo não puder ser lido ou estiver corrompido.
        """
        path_obj = Path(file_path)
        if not path_obj.exists():
            raise FileNotFoundError(f"Arquivo não encontrado: {file_path}")

        try:
            doc = fitz.open(path_obj)
        except Exception as e:
            raise ValueError(f"Falha ao abrir o arquivo PDF: {file_path}. Detalhes: {e}")

        text_pages = []
        try:
            for page in doc:
                text_pages.append(page.get_text())
        except Exception as e:
            raise ValueError(f"Erro ao ler conteúdo das páginas do PDF: {file_path}. Detalhes: {e}")
        finally:
            doc.close()

        return "\n".join(text_pages)
