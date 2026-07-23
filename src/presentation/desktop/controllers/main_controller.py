import threading
from pathlib import Path
from queue import Queue, Empty
from typing import Callable, Optional, Set, Any
import subprocess
import sys

from src.adapters.pdf_reader import PdfReader
from src.adapters.local_regex_processor import LocalRegexProcessor
from src.adapters.tinydb_repo import TinyDbRepo
from src.infrastructure.folder_watcher import FolderWatcher
from src.application.etl_service import EtlService
from src.domain.rules.homicide_rule import HomicideRule
from src.adapters.json_processed_registry import JsonProcessedRegistry

class MainController:
    """
    Controlador principal que orquestra a lógica de negócio, a fila de processamento,
    as chamadas à LLM e o monitoramento de pastas (FolderWatcher).
    As interações com a interface gráfica (UI) são feitas por meio de callbacks injetados.
    """
    def __init__(self):
        # Configuração do Estado da Aplicação
        self.monitoring_path: str = ""
        self.is_monitoring: bool = False
        self.watcher: Optional[FolderWatcher] = None
        self.worker_thread: Optional[threading.Thread] = None
        self.dashboard_process: Optional[subprocess.Popen] = None

        # Fila de processamento e Contadores Globais
        self.processing_queue: Queue = Queue()
        self.processed_count: int = 0
        self.total_discovered: int = 0
        self.total_bytes: int = 0
        self.processed_bytes: int = 0
        self.skipped_count: int = 0
        self.llm_sent_count: int = 0
        self.rule_filtered_count: int = 0
        self.confirmed_homicides_count: int = 0
        self.total_files_in_folder: int = 0
        self.current_filename: str = ""

        # Contadores específicos da sessão atual para o relatório estático
        self.session_confirmed_count: int = 0
        self.session_pre_filtered_count: int = 0
        self.session_post_llm_filtered_count: int = 0
        self.session_skipped_files: Set[str] = set()

        # Injeção de Dependências do Domínio e Aplicação
        self.pdf_reader = PdfReader()
        self.llm_processor = LocalRegexProcessor()
        self.active_rule = HomicideRule()
        self.db_repo = TinyDbRepo(Path("data") / self.active_rule.db_name)
        self.processed_registry = JsonProcessedRegistry(Path("data/processed_registry.json"))
        self.etl_service = EtlService(
            self.pdf_reader, 
            self.llm_processor, 
            self.db_repo, 
            self.processed_registry
        )

        # Callbacks para atualizar a UI (devem ser configurados pela view)
        self.on_log_message: Optional[Callable[[str], None]] = None
        self.on_stats_updated: Optional[Callable[[], None]] = None

    def log(self, message: str):
        """Dispara o callback de log se estiver configurado."""
        if self.on_log_message:
            self.on_log_message(message)

    def update_ui(self):
        """Dispara o callback de atualização da UI."""
        if self.on_stats_updated:
            self.on_stats_updated()

    def set_monitoring_path(self, path: str):
        self.monitoring_path = path

    def toggle_monitoring(self):
        """Inicia ou para o monitoramento de diretório."""
        if not self.is_monitoring:
            self.start_monitoring()
        else:
            self.stop_monitoring()

    def start_monitoring(self):
        """Inicializa o monitoramento, varredura de arquivos e thread do trabalhador."""
        self.skipped_count = 0
        self.total_files_in_folder = 0
        self.current_filename = ""
        
        self.session_confirmed_count = 0
        self.session_pre_filtered_count = 0
        self.session_post_llm_filtered_count = 0
        self.session_skipped_files = set()
        
        # Esvazia a fila
        while not self.processing_queue.empty():
            try:
                self.processing_queue.get_nowait()
            except Empty:
                break

        try:
            folder = Path(self.monitoring_path)
            existing_pdfs = list(folder.glob("*.pdf"))
            self.total_files_in_folder = len(existing_pdfs)
            to_process_pdfs = []
            
            # Otimização O(1): Cache de histórico e banco de dados para evitar leitura O(N²) de JSON
            all_records = self.processed_registry.get_all_records()
            db_reports = self.db_repo.get_all()
            db_files_set = {report.source_file for report in db_reports}
            
            for pdf_file in existing_pdfs:
                status = all_records.get(pdf_file.name, {}).get(self.active_rule.name)
                in_db = pdf_file.name in db_files_set
                
                # Sincronização: limpar histórico se banco foi limpo
                if status == "confirmed" and not in_db:
                    self.processed_registry.remove_record(pdf_file.name, self.active_rule.name)
                    status = None

                if (in_db or status is not None):
                    self.skipped_count += 1
                    self.session_skipped_files.add(pdf_file.name)
                    continue
                    
                to_process_pdfs.append(pdf_file)
                try:
                    self.total_bytes += pdf_file.stat().st_size
                except Exception:
                    pass
                self.processing_queue.put(pdf_file)
            
            self.total_discovered = len(to_process_pdfs)
            self.update_ui()
            
            if existing_pdfs:
                self.log("=" * 60)
                self.log(f">> Varredura inicial concluída em: {self.monitoring_path}")
                self.log(f">> Encontrados {len(existing_pdfs)} arquivos PDF.")
                self.log(f">> [OK] {self.skipped_count} arquivos já analisados pulados.")
                self.log(f">> [FILA] {self.total_discovered} novos arquivos para IA.")
                self.log("=" * 60)

            self.watcher = FolderWatcher(folder_path=folder, callback=self.on_pdf_detected)
            self.watcher.start()
            self.is_monitoring = True
            
            self.worker_thread = threading.Thread(target=self.process_queue_worker, daemon=True)
            self.worker_thread.start()
            
            self.log("Serviço de monitoramento de diretório INICIADO.")
            self.update_ui()
            
        except Exception as e:
            self.log(f"Erro ao iniciar monitoramento: {e}")

    def stop_monitoring(self):
        """Interrompe o monitoramento de diretório e esvazia o watcher."""
        self.is_monitoring = False
        if self.watcher:
            self.watcher.stop()
            self.watcher = None
        
        self.current_filename = ""
        self.total_bytes = 0
        self.processed_bytes = 0
        self.skipped_count = 0
        self.llm_sent_count = 0
        self.rule_filtered_count = 0
        self.confirmed_homicides_count = 0
        
        self.update_ui()
        self.log("Serviço de monitoramento de diretório PARADO.")

    def on_pdf_detected(self, file_path: Path):
        """Callback acionado pelo FolderWatcher ao identificar novo PDF."""
        records = self.processed_registry.get_all_records()
        status = records.get(file_path.name, {}).get(self.active_rule.name)
        
        if status == "confirmed" and not self.db_repo.exists_by_source_file(file_path.name):
            self.processed_registry.remove_record(file_path.name, self.active_rule.name)
            status = None

        if (self.db_repo.exists_by_source_file(file_path.name) or status is not None):
            self.skipped_count += 1
            self.session_skipped_files.add(file_path.name)
            self.log(f"[{file_path.name}] Novo arquivo detectado, mas já analisado/descartado. Pulando.")
            self.update_ui()
            return

        self.log(f"Novo arquivo detectado pelo monitor: {file_path.name}")
        self.total_discovered += 1
        self.total_files_in_folder += 1
        try:
            self.total_bytes += file_path.stat().st_size
        except Exception:
            pass
        self.processing_queue.put(file_path)
        self.update_ui()

    def process_queue_worker(self):
        """Consome a fila de arquivos PDF executando o ETL em uma thread."""
        while self.is_monitoring:
            try:
                file_path = self.processing_queue.get(timeout=1.0)
            except Empty:
                continue

            self.current_filename = file_path.name
            try:
                current_file_size = file_path.stat().st_size
            except Exception:
                current_file_size = 0
                
            self.update_ui()
            
            self.etl_service.process_file(
                file_path=file_path,
                rule=self.active_rule,
                on_progress=self.log,
                on_error=self.log,
                on_success=self.increment_confirmed,
                on_filtered=self.increment_filtered,
                on_sent_to_llm=self.increment_llm_sent
            )
            
            self.processed_count += 1
            self.processed_bytes += current_file_size
            self.current_filename = ""
            self.update_ui()
            self.processing_queue.task_done()

    def increment_confirmed(self, report):
        self.confirmed_homicides_count += 1
        self.session_confirmed_count += 1
        self.update_ui()

    def increment_filtered(self, filename: str):
        self.rule_filtered_count += 1
        status = self.processed_registry.get_all_records().get(filename, {}).get(self.active_rule.name)
        if status == "filtered_pre_llm":
            self.session_pre_filtered_count += 1
        elif status == "filtered_post_llm":
            self.session_post_llm_filtered_count += 1
        self.update_ui()

    def increment_llm_sent(self, filename: str):
        self.llm_sent_count += 1
        self.update_ui()

    def reprocess_file_history(self, filename: str, rule_name: str):
        """Limpa arquivo do banco e histórico, enfileirando novamente se possível."""
        self.processed_registry.remove_record(filename, rule_name)
        deleted = self.db_repo.delete_by_source_file(filename)
        if deleted:
            self.log(f"[{filename}] Removido do banco de dados local para reprocessamento.")
            if self.confirmed_homicides_count > 0:
                self.confirmed_homicides_count -= 1
            if self.session_confirmed_count > 0:
                self.session_confirmed_count -= 1

        if filename in self.session_skipped_files:
            self.session_skipped_files.discard(filename)
            if self.skipped_count > 0:
                self.skipped_count -= 1

        if self.is_monitoring and self.monitoring_path:
            file_path = Path(self.monitoring_path) / filename
            if file_path.exists():
                self.log(f"[{filename}] Adicionado novamente à fila de processamento.")
                self.total_discovered += 1
                try:
                    self.total_bytes += file_path.stat().st_size
                except Exception:
                    pass
                self.processing_queue.put(file_path)
            else:
                self.log(f"[{filename}] Arquivo físico não encontrado na pasta monitorada.")
        else:
            self.log(f"[{filename}] Removido do histórico. Inicie o monitoramento para reprocessá-lo.")
            
        self.update_ui()

    def clear_all_history(self):
        """Remove todos os dados do banco e registros processados."""
        self.processed_registry.clear()
        self.db_repo.db.truncate()
        self.confirmed_homicides_count = 0
        self.processed_count = 0
        self.skipped_count = 0
        self.llm_sent_count = 0
        self.rule_filtered_count = 0
        self.total_discovered = 0
        self.total_bytes = 0
        self.processed_bytes = 0
        self.session_confirmed_count = 0
        self.session_pre_filtered_count = 0
        self.session_post_llm_filtered_count = 0
        self.session_skipped_files = set()
        self.log("Todo o histórico de processamento e banco de dados local foram LIMPOS.")
        self.update_ui()

    def update_homicides_only(self):
        """
        Rotina especial que reavalia apenas os arquivos que têm chance de ser homicídio:
        1. Os confirmados atuais (para ver se a nova LLM os derruba).
        2. Os barrados no antigo pré-filtro (para ver se a nova LLM os aceita).
        Ignora os que já foram rejeitados pela LLM antes.
        """
        if not self.monitoring_path:
            self.log("Por favor, selecione a pasta de monitoramento primeiro.")
            return

        self.log("=" * 60)
        self.log("Iniciando Atualização Filtrada de Homicídios (Novo Filtro)...")
        
        db_reports = self.db_repo.get_all()
        target_files = {report.source_file for report in db_reports}
        
        all_records = self.processed_registry.get_all_records()
        for filename, rules_dict in all_records.items():
            if rules_dict.get(self.active_rule.name) == "filtered_pre_llm":
                target_files.add(filename)

        if not target_files:
            self.log("Nenhum arquivo elegível para atualização encontrado.")
            return

        # Força o inicio da fila caso o monitoramento estivesse parado
        if not self.is_monitoring:
            self.is_monitoring = True
            self.worker_thread = threading.Thread(target=self.process_queue_worker, daemon=True)
            self.worker_thread.start()

        folder = Path(self.monitoring_path)
        count = 0
        for filename in target_files:
            file_path = folder / filename
            if file_path.exists():
                self.reprocess_file_history(filename, self.active_rule.name)
                count += 1
                
        self.log(f"Foram injetados {count} arquivos suspeitos na fila para reavaliação da LLM.")
        self.log("=" * 60)
        self.update_ui()

    def open_dashboard(self):
        """Inicia o dashboard web Streamlit."""
        if self.dashboard_process is not None and self.dashboard_process.poll() is None:
            self.log("O Dashboard já está em execução.")
            return
        
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
        except Exception as e:
            self.log(f"Erro ao abrir o dashboard: {e}")

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
            else:
                self.dashboard_process = None

    def destroy(self):
        """Cleanup."""
        if self.is_monitoring and self.watcher:
            self.watcher.stop()
        if self.dashboard_process is not None and self.dashboard_process.poll() is None:
            try:
                self.dashboard_process.terminate()
            except Exception:
                pass
