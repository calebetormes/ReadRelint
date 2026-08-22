"""
Testes unitários e de integração para o endpoint de eventos SSE em tempo real (/api/v1/events).
"""
import pytest
from fastapi.testclient import TestClient
from backend.api.app import app
from backend.api.routers.events import broadcaster

@pytest.mark.asyncio
async def test_events_stream_connection():
    from backend.api.routers.events import stream_events
    from unittest.mock import AsyncMock, MagicMock
    request = MagicMock()
    request.is_disconnected = AsyncMock(return_value=True)
    response = await stream_events(request)
    gen = response.body_iterator
    first_chunk = await gen.__anext__()
    assert "connected" in first_chunk

def test_broadcaster_subscribe_and_broadcast():
    queue = broadcaster.subscribe()
    assert queue in broadcaster._listeners
    
    broadcaster.broadcast("test_event", {"message": "hello"})
    
    item = queue.get_nowait()
    assert item["event"] == "test_event"
    assert item["data"]["message"] == "hello"
    
    broadcaster.unsubscribe(queue)
    assert queue not in broadcaster._listeners
