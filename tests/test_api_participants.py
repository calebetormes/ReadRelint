"""
Testes unitários e de integração para os endpoints de Participantes e Dossiês (/api/v1/participants).
"""
import pytest
from fastapi.testclient import TestClient
from src.dashboard.backend.api.app import app

def test_list_participants_endpoint():
    client = TestClient(app)
    response = client.get("/api/v1/participants")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    if len(data) > 0:
        first = data[0]
        assert "person_id" in first or "chave_pessoa" in first
        assert "name" in first or "nome" in first
        assert "photos" in first or "galeria_fotos" in first
        assert "linked_relints_count" in first or "quantidade_relints" in first

def test_list_participants_search_filter():
    client = TestClient(app)
    response = client.get("/api/v1/participants?search=Luana")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

def test_list_participants_recurrent_filter():
    client = TestClient(app)
    response = client.get("/api/v1/participants?recurrent_only=true")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    for p in data:
        cnt = p.get("linked_relints_count", p.get("quantidade_relints", 0))
        assert cnt > 1

def test_get_participant_dossier_not_found():
    client = TestClient(app)
    response = client.get("/api/v1/participants/invalido_999999")
    assert response.status_code == 404
