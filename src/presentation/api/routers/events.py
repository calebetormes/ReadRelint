"""
FastAPI Router for Server-Sent Events (SSE) real-time notifications.
"""
import asyncio
import json
from typing import AsyncGenerator, List, Dict, Any
from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse

router = APIRouter(prefix="/events", tags=["events"])


class EventBroadcaster:
    """Gerenciador assíncrono de conexões SSE ativas e distribuição de eventos em tempo real."""

    def __init__(self):
        self._listeners: List[asyncio.Queue] = []

    def subscribe(self) -> asyncio.Queue:
        queue = asyncio.Queue()
        self._listeners.append(queue)
        return queue

    def unsubscribe(self, queue: asyncio.Queue):
        if queue in self._listeners:
            self._listeners.remove(queue)

    def broadcast(self, event_type: str, data: Dict[str, Any]):
        payload = {
            "event": event_type,
            "data": data
        }
        for queue in list(self._listeners):
            try:
                queue.put_nowait(payload)
            except Exception:
                pass


broadcaster = EventBroadcaster()


@router.get("")
async def stream_events(request: Request):
    """
    Endpoint SSE que fornece uma transmissão persistente de eventos para o navegador.
    """
    queue = broadcaster.subscribe()

    async def event_generator() -> AsyncGenerator[str, None]:
        try:
            # Envia mensagem inicial de conexão
            yield f"event: connected\ndata: {json.dumps({'status': 'online'})}\n\n"
            
            while True:
                if await request.is_disconnected():
                    break
                
                try:
                    item = await asyncio.wait_for(queue.get(), timeout=15.0)
                    event_type = item.get("event", "message")
                    event_data = json.dumps(item.get("data", {}), ensure_ascii=False)
                    yield f"event: {event_type}\ndata: {event_data}\n\n"
                except asyncio.TimeoutError:
                    # Ping keep-alive para não derrubar a conexão no navegador
                    yield ": ping\n\n"

        finally:
            broadcaster.unsubscribe(queue)

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )
