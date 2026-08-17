import sys
from pathlib import Path

# Adiciona o diretório raiz do projeto ao sys.path para suportar importações do pacote 'src'.
# Quando executado via `pythonw.exe src/presentation/desktop/desktop_app.py`,
# o Python usa o diretório do .py como __file__, não o CWD — por isso a resolução pelo parents[3].
project_root = str(Path(__file__).resolve().parents[3])
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Redireciona stdout e stderr para um arquivo de log quando não há console (pythonw.exe).
# Isso garante que qualquer erro fatal seja detectável.
if sys.stdout is None or not hasattr(sys.stdout, 'write'):
    _log_path = Path(project_root) / "data" / "desktop_app.log"
    _log_path.parent.mkdir(parents=True, exist_ok=True)
    _logfile = open(str(_log_path), "a", encoding="utf-8")
    sys.stdout = _logfile
    sys.stderr = _logfile

from src.infrastructure.utils.module_loader import ModuleLoader


def main():
    """
    Função inicializadora (Entry Point).
    Realiza o carregamento dinâmico (auto-discovery) de todos os componentes
    (Controllers, Views, Components) dentro da pasta 'src.presentation.desktop'
    eliminando a necessidade de dezenas de imports manuais.
    """
    try:
        # Faz a varredura da pasta desktop e injeta tudo dinamicamente no Registry
        desktop_dir = Path(__file__).parent
        ModuleLoader.load_modules_from_directory(base_dir=desktop_dir, package_prefix="src.presentation.desktop")

        # Recupera dinamicamente a MainWindow via Registry e inicia a aplicação
        MainWindowCls = ModuleLoader.get_class("MainWindow")
        app = MainWindowCls()
        app.mainloop()
    except Exception as e:
        import traceback
        _err_path = Path(project_root) / "data" / "desktop_app_crash.log"
        _err_path.parent.mkdir(parents=True, exist_ok=True)
        with open(str(_err_path), "a", encoding="utf-8") as f:
            f.write(f"\n{'='*60}\n")
            f.write(traceback.format_exc())
        raise


if __name__ == "__main__":
    main()
