import os
import sys
import threading
import subprocess
import webbrowser
import urllib.request
import json
from pathlib import Path
from tkinter import filedialog
import tkinter as _tk

import customtkinter as ctk
from PIL import Image, ImageDraw
import pystray

# --- Configurações Iniciais ---
project_root = Path(__file__).resolve().parent

# Garante que o diretório 'data' exista
data_dir = project_root / "data"
data_dir.mkdir(exist_ok=True)

# Arquivos IPC para comunicação com o endpoint /browse da API
_IPC_REQUEST  = data_dir / "browse_request.flag"
_IPC_RESPONSE = data_dir / "browse_response.txt"

# --- Funções de UI Auxiliares ---
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

        # --- Subprocessos e estado ---
        self.backend_process  = None
        self.frontend_process = None
        self.tray_icon        = None
        self._monitoring_path = "Nenhuma pasta selecionada"

        # --- Layout ---
        self._build_ui()

        # Intercepta o botão X — oculta ao invés de fechar
        self.protocol("WM_DELETE_WINDOW", self._hide_to_tray)

        # Inicializações agendadas
        self.after(500,  self._init_tray)
        self.after(800,  self.start_services)
        self.after(200,  self._check_browse_request)
        self.after(5000, self._poll_monitoring_status)

    def _build_ui(self):
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=(20, 10))
        ctk.CTkLabel(
            header, text="ReadRelint • Serviços",
            font=ctk.CTkFont(family="Inter", size=20, weight="bold")
        ).pack(side="left")

        status_frame = ctk.CTkFrame(self, fg_color="#1e1e1e", corner_radius=10)
        status_frame.pack(fill="both", expand=True, padx=20, pady=10)

        self.lbl_backend = ctk.CTkLabel(
            status_frame, text="Backend (FastAPI): Aguardando...", font=("Inter", 14)
        )
        self.lbl_backend.pack(anchor="w", padx=15, pady=(20, 5))

        self.lbl_frontend = ctk.CTkLabel(
            status_frame, text="Frontend (SvelteKit): Aguardando...", font=("Inter", 14)
        )
        self.lbl_frontend.pack(anchor="w", padx=15, pady=(0, 10))

        ctk.CTkFrame(status_frame, height=1, fg_color="#333333").pack(fill="x", padx=15, pady=5)

        ctk.CTkLabel(
            status_frame, text="📁 Pasta Monitorada:", font=("Inter", 12), text_color="#888888"
        ).pack(anchor="w", padx=15, pady=(8, 0))

        self.lbl_pasta = ctk.CTkLabel(
            status_frame,
            text=self._monitoring_path,
            font=("Inter", 12),
            text_color="#888888",
            wraplength=430,
            justify="left"
        )
        self.lbl_pasta.pack(anchor="w", padx=15, pady=(2, 20))

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

    def _check_browse_request(self):
        """Polling a cada 200ms — detecta o flag IPC e abre o filedialog na thread principal."""
        if _IPC_REQUEST.exists():
            try:
                _IPC_REQUEST.unlink(missing_ok=True)
                root = _tk.Tk()
                root.withdraw()
                root.attributes("-topmost", True)
                root.lift()
                root.focus_force()
                folder = filedialog.askdirectory(parent=root, title="Selecione a Pasta dos RELINTs")
                root.destroy()
                _IPC_RESPONSE.write_text(folder or "", encoding="utf-8")
                if folder:
                    self._monitoring_path = folder
                    self.lbl_pasta.configure(text=folder, text_color="#10b981")
            except Exception:
                _IPC_RESPONSE.write_text("", encoding="utf-8")
        self.after(200, self._check_browse_request)

    def _poll_monitoring_status(self):
        """Consulta a API a cada 5s para atualizar a pasta monitorada no painel."""
        def _fetch():
            try:
                with urllib.request.urlopen(
                    "http://localhost:8000/api/v1/monitoring/status", timeout=2
                ) as resp:
                    data = json.loads(resp.read().decode())
                    path = data.get("monitoring_path", "")
                    if path and path != self._monitoring_path:
                        self._monitoring_path = path
                        self.after(0, lambda p=path: self.lbl_pasta.configure(text=p, text_color="#10b981"))
                    elif not path:
                        self.after(0, lambda: self.lbl_pasta.configure(text="Nenhuma pasta selecionada", text_color="#888888"))
            except Exception:
                pass
        threading.Thread(target=_fetch, daemon=True).start()
        self.after(5000, self._poll_monitoring_status)

    def start_services(self):
        self.lbl_backend.configure(text="Backend (FastAPI): Iniciando...", text_color="yellow")
        self.lbl_frontend.configure(text="Frontend (SvelteKit): Iniciando...", text_color="yellow")
        self.update()

        if self.backend_process is None or self.backend_process.poll() is not None:
            venv_python = str(project_root / ".venv" / "Scripts" / "python.exe")
            try:
                self.backend_process = subprocess.Popen(
                    [venv_python, "-m", "uvicorn", "backend.api.app:app", "--reload"],
                    cwd=str(project_root),
                    env={**os.environ, "PYTHONPATH": str(project_root)},
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    creationflags=subprocess.CREATE_NO_WINDOW
                )
                self.lbl_backend.configure(text="Backend (FastAPI): Rodando", text_color="#10b981")
            except Exception as e:
                self.lbl_backend.configure(text=f"Backend Erro: {e}", text_color="red")

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
        if self.backend_process:
            self.backend_process.terminate()
            self.backend_process = None
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

    def _init_tray(self):
        menu = pystray.Menu(
            pystray.MenuItem("🖥️ Mostrar Painel", self._restore_from_tray, default=True),
            pystray.MenuItem("🌐 Abrir Dashboard Web", lambda: self.open_browser()),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("❌ Encerrar Tudo", self._quit_app)
        )
        self.tray_icon = pystray.Icon(
            "ReadRelint", _create_tray_icon_image(), "ReadRelint Painel", menu=menu
        )
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
