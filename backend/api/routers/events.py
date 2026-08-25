"""
FastAPI Router for Server-Sent Events (SSE) real-time notifications.
"""
import asyncio
import json
from typing import AsyncGenerator, List, Dict, Any, Optional
from fastapi import APIRouter, Request

from fastapi.responses import StreamingResponse

router = APIRouter(prefix="/events", tags=["events"])


class EventBroadcaster:
    """Gerenciador assíncrono de conexões SSE ativas e distribuição de eventos em tempo real."""

    def __init__(self):
        self._listeners: List[asyncio.Queue] = []
        self._loop: Optional[asyncio.AbstractEventLoop] = None

    def set_loop(self, loop: asyncio.AbstractEventLoop):
        self._loop = loop

    def subscribe(self) -> asyncio.Queue:
        queue = asyncio.Queue()
        self._listeners.append(queue)
        try:
            self._loop = asyncio.get_running_loop()
        except RuntimeError:
            pass
        return queue

    def unsubscribe(self, queue: asyncio.Queue):
        if queue in self._listeners:
            self._listeners.remove(queue)

    def broadcast(self, event_type: str, data: Dict[str, Any]):
        payload = {
            "event": event_type,
            "data": data
        }
        
        def _send():
            print(f"[SSE] Emitindo evento {event_type} para {len(self._listeners)} listeners", flush=True)
            for queue in list(self._listeners):
                try:
                    queue.put_nowait(payload)
                except Exception as e:
                    print(f"[SSE] Erro ao colocar na fila: {e}", flush=True)

        if self._loop and self._loop.is_running():
            print(f"[SSE] _loop exists and is running, scheduling _send...", flush=True)
            self._loop.call_soon_threadsafe(_send)
        else:
            print(f"[SSE] _loop is missing or not running. Sending sync.", flush=True)
            _send()


broadcaster = EventBroadcaster()


@router.get("/test_emit")
async def test_emit():
    import uuid
    broadcaster.broadcast("relint_created", {"id": str(uuid.uuid4()), "message": "teste sse ok"})
    return {"status": "disparado"}

@router.get("/debug")
async def get_broadcaster_debug():
    return {
        "broadcaster_id": id(broadcaster),
        "listeners_count": len(broadcaster._listeners),
        "loop_is_running": broadcaster._loop.is_running() if broadcaster._loop else None
    }


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
