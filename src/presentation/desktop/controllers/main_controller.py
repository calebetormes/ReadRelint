import threading
from pathlib import Path
from queue import Queue, Empty
from typing import Callable, Optional, Set

from src.adapters.pdf_reader import PdfReader
from src.adapters.ollama_client import OllamaClient
from src.adapters.sqlite_repo import SqliteRepo
from src.adapters.sqlite_person_repo import SqlitePersonRepo
from src.infrastructure.folder_watcher import FolderWatcher
from src.application.etl_service import EtlService
from src.domain.rules.relint_rule import RelintRule
from src.adapters.json_processed_registry import JsonProcessedRegistry
from src.presentation.desktop.controllers.web_app_manager import WebAppManager

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

        # Injeção de Dependências do Domínio e Aplicação (SQLite)
        self.pdf_reader = PdfReader()
        self.use_llm: bool = True
        self.llm_processor = OllamaClient()
        self.active_rule = RelintRule()
        
        db_path = Path("data/relints.db")
        self.db_repo = SqliteRepo(db_path)
        self.person_repo = SqlitePersonRepo(db_path)
        self.processed_registry = JsonProcessedRegistry(Path("data/processed_registry.json"))
        
        self.etl_service = EtlService(
            file_parser=self.pdf_reader, 
            llm_processor=self.llm_processor, 
            database_repo=self.db_repo, 
            processed_registry=self.processed_registry,
            person_repo=self.person_repo,
            use_llm=self.use_llm
        )


        # Gerenciador do servidor web
        self.web_app_manager = WebAppManager(log_callback=self.log)

        # Callbacks para atualizar a UI (devem ser configurados pela view)
        self.on_log_message: Optional[Callable[[str], None]] = None
        self.on_stats_updated: Optional[Callable[[], None]] = None

    def set_use_llm(self, use_llm: bool) -> bool:
        """
        Alterna a utilização da LLM (IA local) no serviço de ETL.
        Quando ativado (True), executa um teste de conexão em tempo real com o Ollama.
        Retorna True se ativado com sucesso ou False se falhar.
        """
        if use_llm:
            if hasattr(self.llm_processor, "check_connection"):
                self.log("🔍 Testando conexão com o Ollama local...")
                is_ok, msg = self.llm_processor.check_connection()
                if not is_ok:
                    self.log(f"⚠️ {msg}")
                    self.log("💡 Mantendo modo de extração rápida sem IA (Regex). Inicie o Ollama e tente ligar novamente.")
                    self.use_llm = False
                    if hasattr(self, "etl_service"):
                        self.etl_service.use_llm = False
                    return False
                else:
                    self.log(f"✅ {msg}")
            
            self.use_llm = True
            if hasattr(self, "etl_service"):
                self.etl_service.use_llm = True
            self.log("🟢 Modo de extração via IA Local (Ollama) ATIVADO.")
            return True
        else:
            self.use_llm = False
            if hasattr(self, "etl_service"):
                self.etl_service.use_llm = False
            self.log("⚡ Modo de extração rápida (Regex / Sem IA) ATIVADO.")
            return True

    def log(self, message: str):
        """Dispara o callback de log se estiver configurado."""
        if self.on_log_message:
            self.on_log_message(message)

    def update_ui(self):
        """Dispara o callback de atualização da UI."""
        if self.on_stats_updated:
            self.on_stats_updated()

    def reset_and_reprocess_all(self):
        """
        Interrompe o monitoramento, limpa o banco de dados SQLite, a tabela de pessoas,
        o registro de histórico e a pasta de mídias extraídas, e reinicia a leitura
        completa de todos os arquivos da pasta selecionada.
        """
        self.log("🔄 Iniciando Reset Completo da Base de Dados e Re-leitura de RELINTs...")
        if self.is_monitoring:
            self.stop_monitoring()

        # 1. Limpa o banco de dados relacional
        try:
            self.db_repo.clear_all()
            self.person_repo.clear_all()
            self.log("🧹 Banco de dados relacional (relints.db) zerado.")
        except Exception as exc:
            self.log(f"⚠️ Aviso ao limpar banco: {exc}")

        # 2. Limpa o registro de histórico
        try:
            self.processed_registry.clear()
            self.log("🧹 Histórico de controle de arquivos zerado.")
        except Exception as exc:
            self.log(f"⚠️ Aviso ao limpar registro de histórico: {exc}")

        # 3. Limpa arquivos de mídia salvos
        try:
            import shutil
            media_dir = Path("data/media")
            if media_dir.exists():
                shutil.rmtree(media_dir)
                media_dir.mkdir(parents=True, exist_ok=True)
                self.log("🧹 Galeria de mídias/fotos em data/media/ limpada.")
        except Exception as exc:
            self.log(f"⚠️ Aviso ao limpar pasta de mídias: {exc}")

        # 4. Reseta contadores e reinicia o monitoramento se houver pasta selecionada
        self.processed_count = 0
        self.total_discovered = 0
        self.total_bytes = 0
        self.processed_bytes = 0
        self.skipped_count = 0
        self.total_files_in_folder = 0
        self.current_filename = ""
        self.update_ui()

        if self.monitoring_path and Path(self.monitoring_path).exists():
            self.log(f"🚀 Reiniciando varredura e leitura do zero em: {self.monitoring_path}")
            self.start_monitoring()
        else:
            self.log("⚠️ Selecione uma pasta para iniciar a re-leitura.")

    def set_monitoring_path(self, path: str):
        self.monitoring_path = path
        self.inspect_folder(path)

    def inspect_folder(self, path: str):
        """
        Inspeciona a pasta selecionada imediatamente ao escolher o diretório,
        calculando o total de PDFs e quantos já constam no banco de dados.
        """
        self.monitoring_path = path
        self.skipped_count = 0
        self.total_files_in_folder = 0
        self.processed_count = 0
        self.total_discovered = 0
        
        try:
            folder = Path(path)
            if folder.exists() and folder.is_dir():
                existing_pdfs = [f for f in folder.iterdir() if f.is_file() and f.suffix.lower() == ".pdf"]
                self.total_files_in_folder = len(existing_pdfs)
                already_in_db = [f for f in existing_pdfs if self.db_repo.exists_by_source_file(f.name)]
                self.skipped_count = len(already_in_db)
                self.total_discovered = max(0, self.total_files_in_folder - self.skipped_count)
        except Exception as exc:
            self.log(f"Aviso ao inspecionar pasta: {exc}")
        
        self.update_ui()

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
            existing_pdfs = [f for f in folder.iterdir() if f.is_file() and f.suffix.lower() == ".pdf"]
            self.total_files_in_folder = len(existing_pdfs)

            to_process_pdfs = []
            
            # Otimização O(1): Cache de histórico e banco de dados para evitar leitura O(N²) de JSON
            all_records = self.processed_registry.get_all_records()
            db_reports = self.db_repo.get_all()
            db_files_set = {report.source_file for report in db_reports}
            
            for pdf_file in existing_pdfs:
                in_db = self.db_repo.exists_by_source_file(pdf_file.name)
                
                # Sincronização: se o arquivo não está no banco relints.json, limpa histórico antigo para forçar leitura
                if not in_db:
                    self.processed_registry.remove_record(pdf_file.name, self.active_rule.name)
                else:
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
        in_db = self.db_repo.exists_by_source_file(file_path.name)
        
        if not in_db:
            self.processed_registry.remove_record(file_path.name, self.active_rule.name)
        else:
            self.skipped_count += 1
            self.session_skipped_files.add(file_path.name)
            self.log(f"[{file_path.name}] Já cadastrado no banco relints.json. Pulando.")
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
                on_sent_to_llm=self.increment_llm_sent,
                on_llm_disconnected=self.handle_llm_disconnection
            )
            
            self.processed_count += 1
            self.processed_bytes += current_file_size
            self.current_filename = ""
            self.update_ui()
            self.processing_queue.task_done()

    def handle_llm_disconnection(self, reason: str = ""):
        """
        Trata a desconexão ou fechamento do Ollama durante o processamento de um RELINT.
        Desliga a chave da LLM no controlador e notifica a interface desktop.
        """
        self.use_llm = False
        if hasattr(self, 'etl_service'):
            self.etl_service.use_llm = False
            
        self.log(f"⚠️ [CONEXÃO IA PERDIDA] O serviço Ollama está inacessível. O botão da LLM foi DESLIGADO automaticamente e o sistema alternou para o modo Regex (Sem IA).")
        
        if hasattr(self, 'view') and hasattr(self.view, 'control_panel_tab'):
            try:
                self.view.control_panel_tab.after(0, self.view.control_panel_tab.on_llm_disconnected_ui)
            except Exception:
                pass

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
        """Limpa arquivo do banco e histórico e reprocessa imediatamente o PDF especificado."""
        self.processed_registry.remove_record(filename, rule_name)
        deleted = self.db_repo.delete_by_source_file(filename)
        if deleted:
            self.log(f"[{filename}] Removido do banco de dados para reprocessamento.")
            if self.confirmed_homicides_count > 0:
                self.confirmed_homicides_count -= 1
            if self.session_confirmed_count > 0:
                self.session_confirmed_count -= 1

        if filename in self.session_skipped_files:
            self.session_skipped_files.discard(filename)
            if self.skipped_count > 0:
                self.skipped_count -= 1

        if self.monitoring_path:
            file_path = Path(self.monitoring_path) / filename
            if file_path.exists():
                if self.is_monitoring:
                    self.log(f"[{filename}] Adicionado novamente à fila de monitoramento.")
                    self.total_discovered += 1
                    try:
                        self.total_bytes += file_path.stat().st_size
                    except Exception:
                        pass
                    self.processing_queue.put(file_path)
                    self.update_ui()
                else:
                    self.log(f"🚀 Reprocessando imediatamente o arquivo: {filename}...")
                    def _reprocess_job():
                        self.current_filename = filename
                        self.update_ui()
                        self.etl_service.process_file(
                            file_path=file_path,
                            rule=self.active_rule,
                            on_progress=self.log,
                            on_error=self.log,
                            on_success=self.increment_confirmed,
                            on_filtered=self.increment_filtered,
                            on_sent_to_llm=self.increment_llm_sent,
                            on_llm_disconnected=self.handle_llm_disconnection
                        )
                        self.current_filename = ""
                        self.processed_count += 1
                        self.update_ui()
                        self.log(f"✅ Reprocessamento de {filename} concluído com sucesso!")

                    threading.Thread(target=_reprocess_job, daemon=True).start()
            else:
                self.log(f"⚠️ Arquivo {filename} não encontrado no diretório: {self.monitoring_path}")
        else:
            self.log(f"⚠️ Selecione um diretório para reprocessar {filename}.")
            
        self.update_ui()

    def clear_all_history(self):
        """Remove todos os dados do banco e registros processados."""
        self.processed_registry.clear()
        if hasattr(self.db_repo, "clear_all"):
            self.db_repo.clear_all()
        if hasattr(self.person_repo, "clear_all"):
            self.person_repo.clear_all()

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

    def open_web_dashboard(self) -> None:
        """Abre o Painel Web (FastAPI + SPA) no navegador padrão."""
        self.web_app_manager.open()

    def close_web_dashboard(self) -> None:
        """Encerra o servidor web."""
        self.web_app_manager.close()

    def destroy(self) -> None:
        """Libera recursos ao fechar a aplicação."""
        if self.is_monitoring and self.watcher:
            self.watcher.stop()
        self.web_app_manager.destroy()
