import sys
from pathlib import Path

# Adiciona o diretório raiz do projeto ao sys.path para suportar importações do pacote 'src'
project_root = str(Path(__file__).resolve().parents[3])
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.infrastructure.utils.module_loader import ModuleLoader

def main():
    """
    Função inicializadora (Entry Point).
    Realiza o carregamento dinâmico (auto-discovery) de todos os componentes
    (Controllers, Views, Components) dentro da pasta 'src.presentation.desktop'
    eliminando a necessidade de dezenas de imports manuais.
    """
    print("[INIT] Inicializando o Carregador Dinâmico de Módulos (ModuleLoader)...")
    
    # Faz a varredura da pasta desktop e injeta tudo dinamicamente no Registry
    desktop_dir = Path(__file__).parent
    ModuleLoader.load_modules_from_directory(base_dir=desktop_dir, package_prefix="src.presentation.desktop")
    
    print(f"[INIT] Total de classes registradas dinamicamente: {len(ModuleLoader._registry)}")

    # Recupera dinamicamente a MainWindow via Registry e inicia a aplicação
    try:
        MainWindowCls = ModuleLoader.get_class("MainWindow")
        app = MainWindowCls()
        print("[INIT] GUI carregada com sucesso. Iniciando mainloop()...")
        app.mainloop()
    except Exception as e:
        print(f"[ERRO] Falha fatal na inicialização via ModuleLoader: {e}")

if __name__ == "__main__":
    main()
