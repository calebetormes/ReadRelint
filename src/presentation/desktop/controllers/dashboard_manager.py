import sys
import subprocess
from pathlib import Path
from typing import Callable, Optional

class DashboardManager:
    """
    Gerenciador especializado para iniciar, monitorar e parar o processo secundário do Streamlit.
    """
    def __init__(self, log_callback: Callable[[str], None]):
        self.log_callback = log_callback
        self.dashboard_process: Optional[subprocess.Popen] = None

    def log(self, message: str):
        if self.log_callback:
            self.log_callback(message)

    def open_dashboard(self) -> bool:
        """Inicia o dashboard web Streamlit. Retorna True se iniciado, False caso contrário."""
        if self.dashboard_process is not None and self.dashboard_process.poll() is None:
            self.log("O Dashboard já está em execução.")
            return True
        
        self.log("Iniciando o Dashboard Web do Streamlit...")
        try:
            dashboard_path = Path("src/presentation/web_dashboard/dashboard_app.py")
            python_exe = sys.executable
            if python_exe.endswith("pythonw.exe"):
                python_exe = python_exe.replace("pythonw.exe", "python.exe")
            elif python_exe.endswith("pythonw"):
                python_exe = python_exe.replace("pythonw", "python")
                
            cmd = [python_exe, "-m", "streamlit", "run", str(dashboard_path)]
            creationflags = 0x08000000 if sys.platform == "win32" else 0
            self.dashboard_process = subprocess.Popen(cmd, creationflags=creationflags)
            self.log("Dashboard solicitado com sucesso (abrirá no navegador padrão).")
            return True
        except Exception as e:
            self.log(f"Erro ao abrir o dashboard: {e}")
            return False

    def close_dashboard(self):
        """Encerra o dashboard web."""
        if self.dashboard_process is not None:
            if self.dashboard_process.poll() is None:
                self.log("Encerrando o Dashboard Web...")
                try:
                    self.dashboard_process.terminate()
                    self.dashboard_process.wait(timeout=2)
                    self.log("Dashboard encerrado com sucesso.")
                except subprocess.TimeoutExpired:
                    self.dashboard_process.kill()
                    self.log("Dashboard forçado a encerrar.")
                except Exception as e:
                    self.log(f"Erro ao encerrar o dashboard: {e}")
            self.dashboard_process = None

    def destroy(self):
        """Libera recursos do processo."""
        if self.dashboard_process is not None and self.dashboard_process.poll() is None:
            try:
                self.dashboard_process.terminate()
            except Exception:
                pass
            self.dashboard_process = None
