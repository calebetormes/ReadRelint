import time
from pathlib import Path
from typing import Callable
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class NewPdfHandler(FileSystemEventHandler):
    """
    Manipulador de eventos do watchdog para interceptar novos arquivos PDF criados ou movidos.
    """
    def __init__(self, callback: Callable[[Path], None]):
        self.callback = callback

    def on_created(self, event):
        if not event.is_directory:
            self._process_file(event.src_path)

    def on_moved(self, event):
        # Abrange arquivos arrastados ou renomeados para o diretório
        if not event.is_directory:
            self._process_file(event.dest_path)

    def _process_file(self, file_path_str: str):
        file_path = Path(file_path_str)
        if file_path.suffix.lower() == ".pdf":
            # Delay curto para garantir que o sistema operacional concluiu a gravação física do arquivo
            time.sleep(1.0)
            self.callback(file_path)


class FolderWatcher:
    """
    Serviço de infraestrutura responsável por monitorar uma pasta específica no sistema operacional.
    """
    def __init__(self, folder_path: Path, callback: Callable[[Path], None]):
        """
        Inicializa o monitor de pastas.

        :param folder_path: Caminho da pasta a ser monitorada.
        :param callback: Função executada ao identificar um novo PDF.
        """
        self.folder_path = Path(folder_path)
        self.callback = callback
        self.observer = Observer()
        self.handler = NewPdfHandler(self.callback)

    def start(self):
        """
        Inicia o monitoramento da pasta em segundo plano.
        """
        if not self.folder_path.exists():
            raise FileNotFoundError(f"O diretório para monitoramento não existe: {self.folder_path}")

        # Configura o watcher para escutar apenas a pasta atual (recursive=False)
        self.observer.schedule(self.handler, path=str(self.folder_path), recursive=False)
        self.observer.start()

    def stop(self):
        """
        Para o monitoramento e aguarda a finalização das threads associadas.
        """
        self.observer.stop()
        self.observer.join()
