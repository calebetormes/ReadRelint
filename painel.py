import os
import sys
import threading
import subprocess
import webbrowser
from pathlib import Path
import tkinter as _tk
from tkinter import filedialog

# Adiciona o diretório raiz ao sys.path de forma segura antes de carregar o app
project_root = Path(__file__).resolve().parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

import customtkinter as ctk
from PIL import Image, ImageDraw
import pystray
import uvicorn

# Inicializa o logger básico para arquivos temporários se necessário
data_dir = project_root / "data"
data_dir.mkdir(exist_ok=True)

# Importações do projeto (seguras após adição do project_root ao sys.path)
from backend.api.app import app as fastapi_app
from backend.api.dependencies import get_main_controller


def _create_tray_icon_image():
    """Gera o ícone para a bandeja do sistema (tray)."""
    image = Image.new('RGB', (64, 64), color=(18, 18, 18))
    draw = ImageDraw.Draw(image)
    draw.rounded_rectangle([4, 4, 60, 60], radius=14, fill=(16, 185, 129))
    draw.text((22, 12), "R", fill=(255, 255, 255))
    return image


class AppPanel(ctk.CTk):
    def __init__(self):
        super().__init__()

        # --- Tema e Config da Janela ---
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("green")

        self.title("ReadRelint • Painel de Controle")
        self.geometry("480x420")
        self.resizable(False, False)
        self.configure(fg_color="#121212")

        # --- Recupera Controlador de Domínio compartilhado ---
        self.controller = get_main_controller()

        # --- Subprocessos ---
        self.backend_server = None
        self.backend_thread = None
        self.frontend_process = None
        self.tray_icon = None

        # --- Layout ---
        self._build_ui()

        # Intercepta o botão X
        self.protocol("WM_DELETE_WINDOW", self._hide_to_tray)

        # Inicializações agendadas
        self.after(500, self._init_tray)
        self.after(800, self.start_services)
        self.after(1000, self._update_ui_state)

    def _build_ui(self):
        # Header
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=(20, 10))

        ctk.CTkLabel(
            header, text="ReadRelint • Serviços",
            font=ctk.CTkFont(family="Inter", size=20, weight="bold")
        ).pack(side="left")

        # Status Panel
        status_frame = ctk.CTkFrame(self, fg_color="#1e1e1e", corner_radius=10)
        status_frame.pack(fill="both", expand=True, padx=20, pady=10)

        # Backend Status
        self.lbl_backend = ctk.CTkLabel(
            status_frame, text="Backend (FastAPI): Aguardando...", font=("Inter", 14)
        )
        self.lbl_backend.pack(anchor="w", padx=15, pady=(20, 5))

        # Frontend Status
        self.lbl_frontend = ctk.CTkLabel(
            status_frame, text="Frontend (SvelteKit): Aguardando...", font=("Inter", 14)
        )
        self.lbl_frontend.pack(anchor="w", padx=15, pady=(0, 10))

        # Separador visual
        ctk.CTkFrame(status_frame, height=1, fg_color="#333333").pack(fill="x", padx=15, pady=5)

        # Pasta monitorada
        ctk.CTkLabel(
            status_frame, text="📁 Pasta Monitorada:", font=("Inter", 12), text_color="#888888"
        ).pack(anchor="w", padx=15, pady=(8, 0))

        self.lbl_pasta = ctk.CTkLabel(
            status_frame,
            text="Nenhuma pasta selecionada",
            font=("Inter", 12),
            text_color="#888888",
            wraplength=430,
            justify="left"
        )
        self.lbl_pasta.pack(anchor="w", padx=15, pady=(2, 20))

        # Action Buttons
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(fill="x", padx=20, pady=(10, 20))

        self.btn_toggle = ctk.CTkButton(
            btn_frame, text="Reiniciar Serviços",
            command=self.restart_services,
            fg_color="#10b981", hover_color="#059669"
        )
        self.btn_toggle.pack(side="left", expand=True, padx=(0, 10))

        self.btn_web = ctk.CTkButton(
            btn_frame, text="Abrir Navegador",
            command=self.open_browser,
            fg_color="#3b82f6", hover_color="#2563eb"
        )
        self.btn_web.pack(side="left", expand=True)

    def open_browser(self):
        webbrowser.open("http://localhost:5173")

    def _update_ui_state(self):
        """Atualiza a pasta monitorada e os status de forma dinâmica."""
        if self.controller:
            path = self.controller.monitoring_path
            if path:
                self.lbl_pasta.configure(text=path, text_color="#10b981")
            else:
                self.lbl_pasta.configure(text="Nenhuma pasta selecionada", text_color="#888888")

        # Atualiza status do backend
        if self.backend_thread and self.backend_thread.is_alive():
            self.lbl_backend.configure(text="Backend (FastAPI): Rodando (Em-processo)", text_color="#10b981")
        else:
            self.lbl_backend.configure(text="Backend (FastAPI): Parado", text_color="gray")

        # Atualiza status do frontend
        if self.frontend_process and self.frontend_process.poll() is None:
            self.lbl_frontend.configure(text="Frontend (SvelteKit): Rodando", text_color="#10b981")
        else:
            self.lbl_frontend.configure(text="Frontend (SvelteKit): Parado", text_color="gray")

        self.after(1000, self._update_ui_state)

    # --- Gerenciamento de Processos ---
    def start_services(self):
        self.lbl_backend.configure(text="Backend (FastAPI): Iniciando...", text_color="yellow")
        self.lbl_frontend.configure(text="Frontend (SvelteKit): Iniciando...", text_color="yellow")
        self.update()

        # Inicia Backend (Em-processo na mesma memória para permitir filedialog diretamente)
        if self.backend_thread is None or not self.backend_thread.is_alive():
            try:
                config = uvicorn.Config(
                    fastapi_app,
                    host="127.0.0.1",
                    port=8000,
                    log_level="warning"
                )
                self.backend_server = uvicorn.Server(config)
                self.backend_thread = threading.Thread(target=self.backend_server.run, daemon=True)
                self.backend_thread.start()
                self.lbl_backend.configure(text="Backend (FastAPI): Rodando (Em-processo)", text_color="#10b981")
            except Exception as e:
                self.lbl_backend.configure(text=f"Backend Erro: {e}", text_color="red")

        # Inicia Frontend
        if self.frontend_process is None or self.frontend_process.poll() is not None:
            frontend_dir = str(project_root / "frontend")
            try:
                self.frontend_process = subprocess.Popen(
                    "npm run dev",
                    cwd=frontend_dir,
                    shell=True,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    creationflags=subprocess.CREATE_NO_WINDOW
                )
                self.lbl_frontend.configure(text="Frontend (SvelteKit): Rodando", text_color="#10b981")
            except Exception as e:
                self.lbl_frontend.configure(text=f"Frontend Erro: {e}", text_color="red")

    def stop_services(self):
        if self.backend_server:
            self.backend_server.should_exit = True
            self.backend_server = None
            self.backend_thread = None

        if self.frontend_process:
            subprocess.call(
                ['taskkill', '/F', '/T', '/PID', str(self.frontend_process.pid)],
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
            )
            self.frontend_process = None

        self.lbl_backend.configure(text="Backend (FastAPI): Parado", text_color="gray")
        self.lbl_frontend.configure(text="Frontend (SvelteKit): Parado", text_color="gray")

    def restart_services(self):
        self.stop_services()
        self.after(1000, self.start_services)

    # --- System Tray ---
    def _init_tray(self):
        menu = pystray.Menu(
            pystray.MenuItem("🖥️ Mostrar Painel", self._restore_from_tray, default=True),
            pystray.MenuItem("🌐 Abrir Dashboard Web", lambda: self.open_browser()),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("❌ Encerrar Tudo", self._quit_app)
        )
        self.tray_icon = pystray.Icon("ReadRelint", _create_tray_icon_image(), "ReadRelint Painel", menu=menu)
        threading.Thread(target=self.tray_icon.run, daemon=True).start()

    def _hide_to_tray(self):
        self.withdraw()

    def _restore_from_tray(self, icon=None, item=None):
        self.after(0, self.deiconify)
        self.after(0, self.lift)
        self.after(0, self.focus_force)

    def _quit_app(self, icon=None, item=None):
        if self.tray_icon:
            self.tray_icon.stop()
        self.stop_services()
        self.destroy()
        sys.exit(0)


if __name__ == "__main__":
    app = AppPanel()
    app.mainloop()
