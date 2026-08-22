"""
Gerenciador do servidor web da aplicação (FastAPI + SPA).

Responsabilidade única: iniciar, monitorar e encerrar o servidor Uvicorn
em-processo (na mesma memória e thread pool que a UI Desktop),
garantindo sincronização 100% bidirecional em tempo real entre Tkinter e Web.
"""
import os
import sys
import time
import threading
import subprocess
import webbrowser
from typing import Callable, Optional
import uvicorn

from backend.api.app import app


class WebAppManager:
    """
    Gerencia o ciclo de vida do servidor web (FastAPI / Uvicorn em-processo).
    Roda como thread daemon compartilhando a mesma instância de MainController.
    """

    _DEFAULT_HOST = "127.0.0.1"
    _DEFAULT_PORT = 8000

    def __init__(self, log_callback: Callable[[str], None]) -> None:
        self._log = log_callback
        self._server: Optional[uvicorn.Server] = None
        self._thread: Optional[threading.Thread] = None

    @property
    def is_running(self) -> bool:
        """Retorna True se o servidor Uvicorn estiver rodando."""
        return self._thread is not None and self._thread.is_alive()

    @property
    def url(self) -> str:
        return f"http://{self._DEFAULT_HOST}:{self._DEFAULT_PORT}"

    def open(self) -> bool:
        """
        Inicia o servidor Uvicorn em-processo (caso não esteja rodando) e abre no navegador.
        """
        if self.is_running:
            self._log("Painel Web já está em execução. Reabrindo no navegador...")
            self._open_browser()
            return True

        self._log("Iniciando o servidor Painel Web (FastAPI em-processo)...")
        return self._start_server(open_browser=True)

    def start_background_silent(self) -> bool:
        """Inicia o servidor web em segundo plano sem abrir o navegador automaticamente."""
        if self.is_running:
            return True
        return self._start_server(open_browser=False)

    def close(self) -> None:
        """Encerra o servidor de forma segura."""
        if not self.is_running or not self._server:
            return

        self._log("Encerrando o servidor Painel Web...")
        try:
            self._server.should_exit = True
            self._log("Servidor Web encerrado com sucesso.")
        except Exception as exc:
            self._log(f"Erro ao encerrar o servidor Web: {exc}")
        finally:
            self._server = None
            self._thread = None

    def destroy(self) -> None:
        """Libera todos os recursos ao fechar a aplicação."""
        self.close()

    def _start_server(self, open_browser: bool = True) -> bool:
        try:
            config = uvicorn.Config(
                app,
                host=self._DEFAULT_HOST,
                port=self._DEFAULT_PORT,
                log_level="warning"
            )
            self._server = uvicorn.Server(config)
            self._thread = threading.Thread(target=self._server.run, daemon=True)
            self._thread.start()

            if open_browser:
                def _deferred_open():
                    time.sleep(0.5)
                    self._open_browser()
                threading.Thread(target=_deferred_open, daemon=True).start()

            self._log(f"Painel Web ativo em {self.url}")
            return True
        except Exception as exc:
            self._log(f"Erro ao iniciar o Painel Web: {exc}")
            return False

    def _open_browser(self) -> None:
        """Abre o navegador padrão no Windows para a URL do Painel Web."""
        try:
            opened = webbrowser.open(self.url)
            if not opened and sys.platform == "win32":
                subprocess.Popen(["cmd", "/c", "start", self.url], creationflags=subprocess.CREATE_NO_WINDOW)
        except Exception:
            if sys.platform == "win32":
                try:
                    subprocess.Popen(["cmd", "/c", "start", self.url], creationflags=subprocess.CREATE_NO_WINDOW)
                except Exception as exc:
                    self._log(f"Erro ao abrir navegador: {exc}")
