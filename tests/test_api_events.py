"""
Testes unitários e de integração para o endpoint de eventos SSE em tempo real (/api/v1/events).
"""
import pytest
from fastapi.testclient import TestClient
from src.presentation.api.app import app
from src.presentation.api.routers.events import broadcaster

def test_events_stream_connection():
    client = TestClient(app)
    with client.stream("GET", "/api/v1/events") as response:
        assert response.status_code == 200
        assert "text/event-stream" in response.headers["content-type"]
        
        # Lê o primeiro evento de conexão enviada pelo servidor
        lines = []
        for line in response.iter_lines():
            if line:
                lines.append(line)
            if len(lines) >= 2:
                break
        
        assert any("event: connected" in l for l in lines)
        assert any("online" in l for l in lines)

def test_broadcaster_subscribe_and_broadcast():
    queue = broadcaster.subscribe()
    assert queue in broadcaster._listeners
    
    broadcaster.broadcast("test_event", {"message": "hello"})
    
    item = queue.get_nowait()
    assert item["event"] == "test_event"
    assert item["data"]["message"] == "hello"
    
    broadcaster.unsubscribe(queue)
    assert queue not in broadcaster._listeners
