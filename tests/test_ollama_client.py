import pytest
from unittest.mock import patch, MagicMock
import requests
from src.adapters.ollama_client import OllamaClient

@patch("requests.post")
def test_ollama_client_success(mock_post):
    # Simula resposta de sucesso do Ollama
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "model": "llama3.1",
        "response": '{\n  "content": "Resumo estruturado e simplificado do fato."\n}',
        "done": True
    }
    mock_post.return_value = mock_response

    client = OllamaClient(model_name="llama3.1")
    content = client.process_text("Texto bruto do BO")

    assert content == "Resumo estruturado e simplificado do fato."
    mock_post.assert_called_once()

@patch("requests.post")
def test_ollama_client_connection_error(mock_post):
    mock_post.side_effect = requests.RequestException("Timeout")

    client = OllamaClient()
    with pytest.raises(RuntimeError, match="Erro na comunicação com a API local do Ollama"):
        client.process_text("Texto do BO")

@patch("requests.post")
def test_ollama_client_invalid_json_format(mock_post):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "model": "llama3.1",
        "response": "Texto comum que não é um JSON válido de jeito nenhum",
        "done": True
    }
    mock_post.return_value = mock_response

    client = OllamaClient()
    with pytest.raises(ValueError, match="Não foi possível decodificar a resposta em JSON"):
        client.process_text("Texto do BO")
