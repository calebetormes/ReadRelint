import pytest
from unittest.mock import MagicMock, patch
from pathlib import Path
from src.adapters.pdf_reader import PdfReader

def test_pdf_reader_extract_text_success():
    # Mock das páginas
    mock_page1 = MagicMock()
    mock_page1.get_text.return_value = "Texto da página 1."
    
    mock_page2 = MagicMock()
    mock_page2.get_text.return_value = "Texto da página 2."
    
    # Mock do documento PDF retornado pelo fitz.open
    mock_doc = MagicMock()
    mock_doc.__iter__.return_value = [mock_page1, mock_page2]
    
    reader = PdfReader()
    
    # Mockamos Path.exists para simular que o arquivo existe
    # e fitz.open para retornar o nosso mock_doc
    with patch.object(Path, "exists", return_value=True), \
         patch("fitz.open", return_value=mock_doc) as mock_open:
         
        text = reader.extract_text(Path("caminho/ficticio.pdf"))
        
        # O texto esperado deve ser a junção das páginas com quebra de linha
        assert text == "Texto da página 1.\nTexto da página 2."
        mock_open.assert_called_once_with(Path("caminho/ficticio.pdf"))
        mock_doc.close.assert_called_once()


def test_pdf_reader_file_not_found():
    reader = PdfReader()
    
    # Não mockando o path, um arquivo inexistente de fato deve lançar FileNotFoundError
    with pytest.raises(FileNotFoundError, match="Arquivo não encontrado"):
        reader.extract_text(Path("arquivo_inexistente_no_disco.pdf"))


def test_pdf_reader_corrupted_file():
    reader = PdfReader()
    
    # Forçamos o arquivo a "existir", mas a abertura pelo fitz falhará
    with patch.object(Path, "exists", return_value=True), \
         patch("fitz.open", side_effect=Exception("Formato inválido")):
         
        with pytest.raises(ValueError, match="Falha ao abrir o arquivo PDF"):
            reader.extract_text(Path("pdf_corrompido.pdf"))
