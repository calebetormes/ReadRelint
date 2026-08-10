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


def test_pdf_reader_extract_images(tmp_path: Path):
    reader = PdfReader()
    mock_doc = MagicMock()
    mock_page = MagicMock()
    mock_page.rect.height = 842.0
    mock_rect = MagicMock()
    mock_rect.y0 = 300.0
    mock_page.get_images.return_value = [(123, 0, 0, 0, 0)]
    mock_page.get_image_rects.return_value = [mock_rect]
    mock_doc.__iter__.return_value = [mock_page]
    mock_doc.extract_image.return_value = {
        "image": b"X" * 5000,
        "ext": "png",
        "width": 300,
        "height": 400
    }

    with patch.object(Path, "exists", return_value=True), \
         patch("fitz.open", return_value=mock_doc):
        images = reader.extract_images(Path("test.pdf"), tmp_path)
        assert len(images) == 1
        assert images[0]["width"] == 300
        assert images[0]["height"] == 400
        assert images[0]["aspect_ratio"] == 0.75

def test_pdf_reader_extract_images_no_dir_created_when_empty(tmp_path: Path):
    reader = PdfReader()
    mock_doc = MagicMock()
    mock_page = MagicMock()
    mock_page.get_images.return_value = []
    mock_doc.__iter__.return_value = [mock_page]

    output_dir = tmp_path / "empty_media"
    dummy_pdf = tmp_path / "dummy.pdf"
    dummy_pdf.write_text("pdf dummy content")

    with patch("fitz.open", return_value=mock_doc):
        images = reader.extract_images(dummy_pdf, output_dir)
        assert len(images) == 0
        assert output_dir.exists() is False

