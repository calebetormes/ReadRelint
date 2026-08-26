"""
FastAPI Router for WebSockets (Bidirectional) real-time notifications.
"""
import asyncio
import json
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

router = APIRouter(prefix="/events", tags=["events"])


class EventBroadcaster:
    """Gerenciador assíncrono de conexões WebSocket ativas e distribuição de eventos em tempo real."""

    def __init__(self):
        self._listeners: List[WebSocket] = []
        self._loop: Optional[asyncio.AbstractEventLoop] = None

    def set_loop(self, loop: asyncio.AbstractEventLoop):
        self._loop = loop

    def subscribe(self, websocket: WebSocket):
        self._listeners.append(websocket)
        try:
            self._loop = asyncio.get_running_loop()
        except RuntimeError:
            pass

    def unsubscribe(self, websocket: WebSocket):
        if websocket in self._listeners:
            self._listeners.remove(websocket)

    def broadcast(self, event_type: str, data: Dict[str, Any]):
        payload = {
            "event": event_type,
            "data": data
        }
        
        async def _send_to_all():
            print(f"[WS] Emitindo evento {event_type} para {len(self._listeners)} listeners", flush=True)
            for ws in list(self._listeners):
                try:
                    await ws.send_json(payload)
                except Exception as e:
                    print(f"[WS] Erro ao enviar para o websocket: {e}", flush=True)
                    self.unsubscribe(ws)

        if self._loop and self._loop.is_running():
            print(f"[WS] _loop exists and is running, scheduling _send...", flush=True)
            asyncio.run_coroutine_threadsafe(_send_to_all(), self._loop)
        else:
            print(f"[WS] _loop is missing or not running. Try to run it synchronously (may fail se não em contexto de loop).", flush=True)
            try:
                loop = asyncio.get_running_loop()
                loop.create_task(_send_to_all())
            except RuntimeError:
                asyncio.run(_send_to_all())


broadcaster = EventBroadcaster()


@router.get("/test_emit")
async def test_emit():
    import uuid
    broadcaster.broadcast("relint_created", {"id": str(uuid.uuid4()), "message": "teste ws ok"})
    return {"status": "disparado"}

@router.get("/debug")
async def get_broadcaster_debug():
    return {
        "broadcaster_id": id(broadcaster),
        "listeners_count": len(broadcaster._listeners),
        "loop_is_running": broadcaster._loop.is_running() if broadcaster._loop else None
    }


@router.websocket("")
async def websocket_endpoint(websocket: WebSocket):
    """
    Endpoint WebSocket que fornece uma conexão bidirecional em tempo real.
    """
    await websocket.accept()
    broadcaster.subscribe(websocket)
    try:
        # Envia mensagem inicial de conexão
        await websocket.send_json({
            "event": "connected",
            "data": {"status": "online"}
        })
        
        while True:
            # Mantém a conexão viva e processa mensagens recebidas do frontend
            data = await websocket.receive_text()
            try:
                msg = json.loads(data)
                print(f"[WS] Recebido do cliente: {msg}")
                # Aqui você pode rotear comandos do frontend para o backend, se necessário
            except json.JSONDecodeError:
                print(f"[WS] Recebido do cliente (texto bruto): {data}")
    except WebSocketDisconnect:
        broadcaster.unsubscribe(websocket)
    except Exception as e:
        print(f"[WS] Erro na conexão websocket: {e}")
        broadcaster.unsubscribe(websocket)
