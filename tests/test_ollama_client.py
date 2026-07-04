import pytest
from unittest.mock import patch, MagicMock
import requests
from src.adapters.ollama_client import OllamaClient
from src.domain.entities import IncidentReport

@patch("requests.post")
def test_ollama_client_success(mock_post):
    # Mocking a successful response from Ollama API
    mock_response = MagicMock()
    mock_response.status_code = 200
    
    # Simulates the JSON structure returned by Ollama's /api/generate
    mock_response.json.return_value = {
        "model": "llama3",
        "response": (
            '{\n'
            '  "incident_type": "Roubo",\n'
            '  "incident_time": "2026-07-04T15:00:00Z",\n'
            '  "address": {\n'
            '    "street": "Rua Augusta",\n'
            '    "number": "500",\n'
            '    "neighborhood": "Consolação",\n'
            '    "city": "São Paulo"\n'
            '  },\n'
            '  "participants": [\n'
            '    {"name": "Alice Silva", "role": "Vítima"}\n'
            '  ],\n'
            '  "vehicles": [],\n'
            '  "attending_officer": "Policial Militar Santos",\n'
            '  "history_summary": "Roubo de carteira na via pública."\n'
            '}'
        ),
        "done": True
    }
    mock_post.return_value = mock_response

    client = OllamaClient(model_name="llama3")
    report = client.process_incident_text("Texto do boletim de ocorrência fictício")

    assert isinstance(report, IncidentReport)
    assert report.incident_type == "Roubo"
    assert report.address.street == "Rua Augusta"
    assert len(report.participants) == 1
    assert report.participants[0].name == "Alice Silva"
    assert report.history_summary == "Roubo de carteira na via pública."
    mock_post.assert_called_once()


@patch("requests.post")
def test_ollama_client_connection_error(mock_post):
    # Simulates a connection timeout or network issue
    mock_post.side_effect = requests.RequestException("Timeout")

    client = OllamaClient()
    with pytest.raises(RuntimeError, match="Erro na comunicação com a API local do Ollama"):
        client.process_incident_text("Texto do BO")


@patch("requests.post")
def test_ollama_client_invalid_json_format(mock_post):
    # Simulates response where the generated text is not valid JSON
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "model": "llama3",
        "response": "Texto comum que não é um JSON válido de jeito nenhum",
        "done": True
    }
    mock_post.return_value = mock_response

    client = OllamaClient()
    with pytest.raises(ValueError, match="Ollma não retornou um JSON de resposta decodificável"):
        client.process_incident_text("Texto do BO")


@patch("requests.post")
def test_ollama_client_validation_error(mock_post):
    # Simulates a valid JSON response from LLM, but missing required domain fields (like address)
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "model": "llama3",
        "response": '{"incident_type": "Furto", "history_summary": "Faltando o endereço"}',
        "done": True
    }
    mock_post.return_value = mock_response

    client = OllamaClient()
    with pytest.raises(ValueError, match="não atende aos requisitos do domínio IncidentReport"):
        client.process_incident_text("Texto do BO")
