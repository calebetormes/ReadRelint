import os
import sys
import threading
import subprocess
import webbrowser
from pathlib import Path

import customtkinter as ctk
from PIL import Image, ImageDraw
import pystray

# --- Configurações Iniciais ---
project_root = Path(__file__).resolve().parent

# Tenta garantir que o diretório 'data' exista para possíveis logs
data_dir = project_root / "data"
data_dir.mkdir(exist_ok=True)

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
        self.geometry("450x380")
        self.resizable(False, False)
        self.configure(fg_color="#121212")

        # --- Subprocessos ---
        self.backend_process = None
        self.frontend_process = None
        self.tray_icon = None

        # --- Layout ---
        self._build_ui()

        # Intercepta o evento do botão X
        self.protocol("WM_DELETE_WINDOW", self._hide_to_tray)
        
        # Agenda inicialização do Tray e inicialização automática dos serviços
        self.after(500, self._init_tray)
        self.after(800, self.start_services)

    def _build_ui(self):
        # Header
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=(20, 10))
        
        title = ctk.CTkLabel(
            header, text="ReadRelint • Serviços", 
            font=ctk.CTkFont(family="Inter", size=20, weight="bold")
        )
        title.pack(side="left")

        # Status Panel
        status_frame = ctk.CTkFrame(self, fg_color="#1e1e1e", corner_radius=10)
        status_frame.pack(fill="both", expand=True, padx=20, pady=10)

        # Backend Status
        self.lbl_backend = ctk.CTkLabel(status_frame, text="Backend (FastAPI): Aguardando...", font=("Inter", 14))
        self.lbl_backend.pack(anchor="w", padx=15, pady=(20, 10))
        
        # Frontend Status
        self.lbl_frontend = ctk.CTkLabel(status_frame, text="Frontend (SvelteKit): Aguardando...", font=("Inter", 14))
        self.lbl_frontend.pack(anchor="w", padx=15, pady=(0, 20))

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

    # --- Gerenciamento de Processos ---
    def start_services(self):
        self.lbl_backend.configure(text="Backend (FastAPI): Iniciando...", text_color="yellow")
        self.lbl_frontend.configure(text="Frontend (SvelteKit): Iniciando...", text_color="yellow")
        self.update()

        # Inicia Backend
        if self.backend_process is None or self.backend_process.poll() is not None:
            venv_python = str(project_root / ".venv" / "Scripts" / "python.exe")
            try:
                self.backend_process = subprocess.Popen(
                    [venv_python, "-m", "uvicorn", "backend.api.app:app", "--reload"],
                    cwd=str(project_root),
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    creationflags=subprocess.CREATE_NO_WINDOW
                )
                self.lbl_backend.configure(text="Backend (FastAPI): Rodando", text_color="#10b981")
            except Exception as e:
                self.lbl_backend.configure(text=f"Backend Erro: {e}", text_color="red")

        # Inicia Frontend
        if self.frontend_process is None or self.frontend_process.poll() is not None:
            frontend_dir = str(project_root / "frontend")
            # Usa shell=True para o npm ser encontrado no Windows
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
            # Terminar subprocessos shell no Windows requer 'taskkill' se child processes foram criados (como node.exe)
            subprocess.call(['taskkill', '/F', '/T', '/PID', str(self.frontend_process.pid)], 
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
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
        
        # Roda o tray em uma thread separada para não bloquear o mainloop do Tkinter
        threading.Thread(target=self.tray_icon.run, daemon=True).start()

    def _hide_to_tray(self):
        self.withdraw() # Oculta a janela

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
