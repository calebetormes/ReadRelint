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

from src.presentation.api.routers import relints

# ─────────────────────────────────────────────────────────────────────────────
# Paths resolvidos relativos a este arquivo para evitar dependência de CWD
# ─────────────────────────────────────────────────────────────────────────────
_HERE = Path(__file__).resolve().parent
_PROJECT_ROOT = _HERE.parents[2]

WEB_DIR: Path = (_HERE.parent / "web").resolve()
MEDIA_DIR: Path = (_PROJECT_ROOT / "data" / "media").resolve()

MEDIA_DIR.mkdir(parents=True, exist_ok=True)

# ─────────────────────────────────────────────────────────────────────────────
# Aplicação FastAPI
# ─────────────────────────────────────────────────────────────────────────────
app = FastAPI(
    title="ReadRelint API",
    description="Administrador de RELINTs — Backend REST API",
    version="2.0.0",
)

# Arquivos estáticos do frontend (CSS, JS, assets)
app.mount("/static", StaticFiles(directory=str(WEB_DIR)), name="static")

# Imagens extraídas dos PDFs servidas em /media/...
app.mount("/media", StaticFiles(directory=str(MEDIA_DIR)), name="media")

# Rotas da API REST
app.include_router(relints.router, prefix="/api/v1")


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
