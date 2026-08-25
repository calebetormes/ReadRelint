import sys
from pathlib import Path

# Adiciona o diretório raiz ao sys.path de forma segura para permitir imports absolutos
project_root = Path(__file__).resolve().parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from desktop.ui.pyqt_app import run

if __name__ == "__main__":
    run()
