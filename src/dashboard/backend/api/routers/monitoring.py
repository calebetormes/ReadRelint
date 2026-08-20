"""
FastAPI Router para Gerenciamento do Motor de Monitoramento de Pastas & IA.
Expõe endpoints REST e SSE (Server-Sent Events) em tempo real para a interface Web.
"""
import asyncio
import json
from pathlib import Path
from typing import Dict, Any

from fastapi import APIRouter, Depends, HTTPException, Body
from fastapi.responses import StreamingResponse

from src.dashboard.backend.api.dependencies import get_main_controller

import time

router = APIRouter(prefix="/monitoring", tags=["monitoring"])

_ollama_cache: Dict[str, Any] = {"last_check": 0.0, "result": (False, "")}

def _cached_check_connection(controller) -> tuple[bool, str]:
    """Testa a conexão com o Ollama com cache TTL de 5 segundos."""
    # Se o controller estiver processando ativamente com IA, considera online para evitar falsos negativos por timeout de CPU
    if getattr(controller, "current_filename", "") and getattr(controller, "use_llm", False):
        return (True, "Ollama em processamento ativo")

    now = time.time()
    if now - _ollama_cache["last_check"] < 5.0:
        return _ollama_cache["result"]
    
    if hasattr(controller, "llm_processor") and hasattr(controller.llm_processor, "check_connection"):
        try:
            ok, msg = controller.llm_processor.check_connection()
            _ollama_cache["last_check"] = now
            _ollama_cache["result"] = (ok, msg)
            return (ok, msg)
        except Exception as exc:
            _ollama_cache["last_check"] = now
            _ollama_cache["result"] = (False, str(exc))
            return (False, str(exc))
    return (False, "IA Indisponível")


@router.get("/status")
def get_monitoring_status(controller=Depends(get_main_controller)) -> Dict[str, Any]:
    """Retorna o status completo e métricas atuais do motor de monitoramento."""
    total_folder = getattr(controller, "total_files_in_folder", 0)
    skipped_cnt = getattr(controller, "skipped_count", 0)
    processed_cnt = getattr(controller, "processed_count", 0)
    discovered_cnt = getattr(controller, "total_discovered", 0)

    # Verifica status de saúde do Ollama via cache leve
    ollama_ok, ollama_msg = _cached_check_connection(controller)

    # Obtém contagens agregadas ultrarrápidas (0.1ms) sem N+1 SQL queries
    counts = controller.db_repo.get_report_counts() if hasattr(controller.db_repo, "get_report_counts") else {"total": 0, "llm": 0, "regex": 0}
    logs_list = list(getattr(controller, "recent_logs", []))

    return {
        "monitoring_path": controller.monitoring_path or "",
        "is_monitoring": controller.is_monitoring,
        "use_llm": controller.use_llm,
        "current_filename": controller.current_filename or "",
        "total_files_in_folder": total_folder,
        "skipped_count": skipped_cnt,
        "processed_count": processed_cnt,
        "total_discovered": discovered_cnt,
        "read_files_in_folder": min(skipped_cnt + processed_cnt, total_folder) if total_folder > 0 else 0,
        "ollama_online": ollama_ok,
        "ollama_message": ollama_msg,
        "reports_total": counts.get("total", 0),
        "reports_llm": counts.get("llm", 0),
        "reports_regex": counts.get("regex", 0),
        "logs": logs_list,
    }


@router.post("/browse")
def browse_folder_dialog(controller=Depends(get_main_controller)) -> Dict[str, Any]:
    """Abre a janela nativa do Windows (filedialog) no servidor local para selecionar pasta."""
    import tkinter as tk
    from tkinter import filedialog
    import concurrent.futures

    def _open_dialog():
        root = tk.Tk()
        root.withdraw()
        root.attributes('-topmost', True)
        folder = filedialog.askdirectory(title="Selecione a Pasta dos RELINTs")
        root.destroy()
        return folder

    try:
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(_open_dialog)
            selected_path = future.result(timeout=120)

        if selected_path:
            controller.set_monitoring_path(selected_path)
            return {
                "status": "success",
                "path": selected_path,
                "total_files": controller.total_files_in_folder,
                "skipped_count": controller.skipped_count,
            }
        return {"status": "cancelled", "path": ""}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Erro ao abrir seletor de pasta: {exc}")


@router.post("/path")
def set_monitoring_path(
    payload: Dict[str, str] = Body(...),
    controller=Depends(get_main_controller)
) -> Dict[str, Any]:
    """Define o diretório de monitoramento de RELINTs e realiza inspecção instantânea."""
    path_str = payload.get("path", "").strip()
    if not path_str:
        raise HTTPException(status_code=400, detail="Caminho da pasta é obrigatório.")

    target_path = Path(path_str)
    if not target_path.exists() or not target_path.is_dir():
        raise HTTPException(status_code=404, detail=f"Diretório não encontrado: {path_str}")

    controller.set_monitoring_path(path_str)
    return {
        "status": "success",
        "message": f"Diretório definido para: {path_str}",
        "total_files": controller.total_files_in_folder,
        "skipped_count": controller.skipped_count,
    }


@router.post("/start")
def start_monitoring(controller=Depends(get_main_controller)) -> Dict[str, str]:
    """Inicia ou retoma o monitoramento contínuo da pasta selecionada."""
    if not controller.monitoring_path:
        raise HTTPException(status_code=400, detail="Selecione ou informe uma pasta antes de iniciar.")

    if not controller.is_monitoring:
        controller.start_monitoring()
    return {"status": "success", "message": "Monitoramento ativado com sucesso."}


@router.post("/stop")
def stop_monitoring(controller=Depends(get_main_controller)) -> Dict[str, str]:
    """Pausa o monitoramento contínuo da pasta."""
    if controller.is_monitoring:
        controller.stop_monitoring()
    return {"status": "success", "message": "Monitoramento pausado."}


@router.post("/reset")
def reset_all_data(controller=Depends(get_main_controller)) -> Dict[str, str]:
    """Executa o reset completo do banco relacional, tabela de pessoas, mídias e re-leitura."""
    controller.reset_and_reprocess_all()
    return {"status": "success", "message": "Reset completo executado e re-leitura iniciada."}


@router.post("/reprocess-file")
def reprocess_single_file(
    payload: Dict[str, str] = Body(...),
    controller=Depends(get_main_controller)
) -> Dict[str, str]:
    """Remove o registro de um arquivo PDF específico e dispara sua re-leitura imediata."""
    filename = payload.get("filename", "").strip()
    if not filename:
        raise HTTPException(status_code=400, detail="Nome do arquivo é obrigatório.")

    rule_name = controller.active_rule.name if hasattr(controller, "active_rule") else "default"
    controller.reprocess_file_history(filename, rule_name)
    return {"status": "success", "message": f"Re-leitura de {filename} disparada com sucesso."}


@router.post("/toggle-llm")
def toggle_llm(
    payload: Dict[str, bool] = Body(...),
    controller=Depends(get_main_controller)
) -> Dict[str, Any]:
    """Alterna o switch do Ollama (IA) e executa o teste de saúde em tempo real."""
    use_llm = payload.get("use_llm", False)
    success = controller.set_use_llm(use_llm)
    return {
        "status": "success" if success else "warning",
        "use_llm": controller.use_llm,
        "message": "IA ativada" if controller.use_llm else "Modo Regex ativado",
    }


@router.get("/events", response_class=StreamingResponse)
async def stream_monitoring_events(controller=Depends(get_main_controller)):
    """
    Endpoint Server-Sent Events (SSE) transmitindo em tempo real:
    - Status das barras de progresso
    - Arquivo em leitura
    - Eventos de saúde do Ollama
    """
    async def event_generator():
        while True:
            total_folder = getattr(controller, "total_files_in_folder", 0)
            skipped_cnt = getattr(controller, "skipped_count", 0)
            processed_cnt = getattr(controller, "processed_count", 0)
            discovered_cnt = getattr(controller, "total_discovered", 0)

            # Teste de conexão não bloqueante com cache
            ollama_ok, _ = _cached_check_connection(controller)

            event_data = {
                "is_monitoring": controller.is_monitoring,
                "use_llm": controller.use_llm,
                "current_filename": controller.current_filename or "",
                "total_files_in_folder": total_folder,
                "skipped_count": skipped_cnt,
                "processed_count": processed_cnt,
                "total_discovered": discovered_cnt,
                "read_files_in_folder": min(skipped_cnt + processed_cnt, total_folder) if total_folder > 0 else 0,
                "ollama_online": ollama_ok,
                "logs": list(getattr(controller, "recent_logs", [])),
            }

            yield f"data: {json.dumps(event_data, ensure_ascii=False)}\n\n"
            await asyncio.sleep(1.5)

    return StreamingResponse(event_generator(), media_type="text/event-stream")
