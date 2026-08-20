"""
FastAPI Application Entry Point — ReadRelint Web API.

Responsabilidades:
  - Montar o frontend SPA (HTML/CSS/JS) como arquivos estáticos.
  - Montar o diretório de midia (imagens extraídas de PDFs) em /media.
  - Registrar os roteadores da API REST.
  - Disponibilizar um endpoint de health-check.
"""
import os
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from src.dashboard.backend.api.routers import relints, monitoring, events, participants

# ─────────────────────────────────────────────────────────────────────────────
# Paths resolvidos relativos a este arquivo para evitar dependência de CWD
# ─────────────────────────────────────────────────────────────────────────────
# Define caminhos para a estrutura unificada
BASE_DIR = Path(__file__).resolve().parents[3]  # Aponta para src/
PROJECT_ROOT = Path(__file__).resolve().parents[4]  # Aponta para a raiz do projeto ReadRelint
WEB_DIR = BASE_DIR / "dashboard" / "frontend"
MEDIA_DIR = PROJECT_ROOT / "data" / "media"

MEDIA_DIR.mkdir(parents=True, exist_ok=True)

# ─────────────────────────────────────────────────────────────────────────────
# Aplicação FastAPI
# ─────────────────────────────────────────────────────────────────────────────
app = FastAPI(
    title="ReadRelint API",
    description="Administrador de RELINTs — Backend REST API",
    version="2.0.0",
)

@app.middleware("http")
async def add_no_cache_headers(request, call_next):
    response = await call_next(request)
    if request.url.path.startswith("/static/") or request.url.path == "/":
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
    return response

# Arquivos estáticos do frontend (CSS, JS, assets)
app.mount("/static", StaticFiles(directory=str(WEB_DIR)), name="static")

# Imagens extraídas dos PDFs servidas em /media/...
app.mount("/media", StaticFiles(directory=str(MEDIA_DIR)), name="media")

# Rotas da API REST
app.include_router(relints.router, prefix="/api/v1")
app.include_router(monitoring.router, prefix="/api/v1")
app.include_router(events.router, prefix="/api/v1")
app.include_router(participants.router, prefix="/api/v1")


# ─────────────────────────────────────────────────────────────────────────────
# Endpoints de sistema
# ─────────────────────────────────────────────────────────────────────────────

@app.get("/api/v1/health", tags=["system"])
def health_check() -> dict:
    """Retorna o status do servidor e informações básicas do serviço."""
    return {
        "status": "online",
        "service": "ReadRelint API",
        "version": "2.0.0",
    }


@app.get("/", include_in_schema=False)
def serve_spa() -> FileResponse:
    """Serve o shell HTML do Single Page Application."""
    index_path = WEB_DIR / "index.html"
    if index_path.exists():
        return FileResponse(str(index_path))
    return FileResponse(str(index_path))  # FastAPI lida com 404 automaticamente
