"""
Gerenciador do servidor web da aplicação (FastAPI + SPA).

Responsabilidade única: iniciar, monitorar e encerrar o processo Uvicorn
que serve a API REST e o frontend SPA em http://localhost:8000.
"""
import sys
import subprocess
import time
import webbrowser
from typing import Callable, Optional


class WebAppManager:
    """
    Gerencia o ciclo de vida do servidor web (FastAPI / Uvicorn).

    Recebe um callback de log para desacoplar completamente da camada de UI.
    """

    _SERVER_MODULE = "src.presentation.api.app:app"
    _DEFAULT_HOST = "127.0.0.1"
    _DEFAULT_PORT = 8000

    def __init__(self, log_callback: Callable[[str], None]) -> None:
        self._log = log_callback
        self._process: Optional[subprocess.Popen] = None

    # ─────────────────────────────────────────────
    # Propriedades de estado
    # ─────────────────────────────────────────────

    @property
    def is_running(self) -> bool:
        """Retorna True se o processo do servidor ainda esta em execucao."""
        return self._process is not None and self._process.poll() is None

    @property
    def url(self) -> str:
        return f"http://{self._DEFAULT_HOST}:{self._DEFAULT_PORT}"

    # ─────────────────────────────────────────────
    # Operacoes publicas
    # ─────────────────────────────────────────────

    def open(self) -> bool:
        """
        Inicia o servidor Uvicorn (caso nao esteja rodando) e abre no navegador.

        Retorna True em caso de sucesso, False em caso de falha.
        """
        if self.is_running:
            self._log("Painel Web ja esta em execucao. Reabrindo no navegador...")
            self._open_browser()
            return True

        self._log("Iniciando o servidor Painel Web (FastAPI / Uvicorn)...")
        return self._start_server()

    def close(self) -> None:
        """Encerra o processo do servidor de forma segura."""
        if not self.is_running:
            return

        self._log("Encerrando o servidor Painel Web...")
        try:
            self._process.terminate()
            self._process.wait(timeout=3)
            self._log("Servidor encerrado com sucesso.")
        except subprocess.TimeoutExpired:
            self._process.kill()
            self._log("Servidor forcado a encerrar (timeout).")
        except Exception as exc:
            self._log(f"Erro ao encerrar o servidor: {exc}")
        finally:
            self._process = None

    def destroy(self) -> None:
        """Libera todos os recursos — deve ser chamado ao fechar a aplicacao."""
        self.close()

    # ─────────────────────────────────────────────
    # Metodos privados
    # ─────────────────────────────────────────────

    def _start_server(self) -> bool:
        try:
            cmd = [
                self._resolve_python_exe(),
                "-m", "uvicorn",
                self._SERVER_MODULE,
                "--host", self._DEFAULT_HOST,
                "--port", str(self._DEFAULT_PORT),
            ]
            creation_flags = subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
            self._process = subprocess.Popen(cmd, creationflags=creation_flags)

            time.sleep(1.0)
            self._open_browser()
            self._log(f"Painel Web iniciado em {self.url}")
            return True
        except Exception as exc:
            self._log(f"Erro ao iniciar o Painel Web: {exc}")
            return False

    def _open_browser(self) -> None:
        try:
            webbrowser.open(self.url)
        except Exception as exc:
            self._log(f"Erro ao abrir navegador: {exc}")

    @staticmethod
    def _resolve_python_exe() -> str:
        """Retorna o caminho do executavel Python (garante uso de python.exe, nao pythonw.exe)."""
        exe = sys.executable
        return exe.replace("pythonw.exe", "python.exe").replace("pythonw", "python")
