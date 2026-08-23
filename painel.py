import sys
from pathlib import Path

# Adiciona o diretório raiz ao sys.path de forma segura para permitir imports absolutos
project_root = Path(__file__).resolve().parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from PyQt6.QtWidgets import QApplication
from desktop.ui.pyqt_app import MainWindow
from backend.api.dependencies import get_main_controller

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    controller = get_main_controller()
    window = MainWindow(controller)
    window.show()
    sys.exit(app.exec())
