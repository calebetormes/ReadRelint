import tkinter as tk
from tkinter import filedialog
import customtkinter as ctk
import threading
from pathlib import Path
from datetime import datetime
from queue import Queue, Empty

# Importações dos adaptadores e infraestrutura
from src.adapters.pdf_reader import PdfReader
from src.adapters.ollama_client import OllamaClient
from src.adapters.tinydb_repo import TinyDbRepo
from src.infrastructure.folder_watcher import FolderWatcher

# Configurações globais do tema e estilo
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class IncidentEtlApp(ctk.CTk):
    """
    Interface Gráfica do Usuário (GUI) usando CustomTkinter para controle
    do pipeline de monitoramento de boletins de ocorrência.
    """
    def __init__(self):
        super().__init__()

        # Configurações da janela principal
        self.title("ETL de Boletins de Ocorrência - Painel de Controle")
        self.geometry("750x600")
        self.resizable(False, False)

        # Estado da aplicação
        self.monitoring_path = ""
        self.is_monitoring = False
        self.watcher = None
        self.worker_thread = None

        # Fila de processamento e contadores
        self.processing_queue = Queue()
        self.processed_count = 0
        self.total_discovered = 0
        self.total_bytes = 0
        self.processed_bytes = 0
        self.skipped_count = 0

        # Inicialização dos adaptadores (Injeção de dependências)
        self.pdf_reader = PdfReader()
        self.llm_processor = OllamaClient(model_name="llama3.1")
        self.db_repo = TinyDbRepo(Path("data/database.json"))

        # Título da Interface
        self.title_label = ctk.CTkLabel(
            self, 
            text="Painel de Controle - ETL de BOs", 
            font=ctk.CTkFont(family="Inter", size=22, weight="bold")
        )
        self.title_label.pack(pady=20)

        # Container para a Seleção de Diretório
        self.dir_frame = ctk.CTkFrame(self)
        self.dir_frame.pack(pady=10, padx=40, fill="x")

        self.dir_entry = ctk.CTkEntry(
            self.dir_frame, 
            placeholder_text="Selecione a pasta para monitorar...", 
            width=350
        )
        self.dir_entry.pack(side="left", padx=10, pady=10, expand=True, fill="x")

        self.browse_button = ctk.CTkButton(
            self.dir_frame, 
            text="Buscar Pasta", 
            command=self.browse_directory
        )
        self.browse_button.pack(side="right", padx=10, pady=10)

        # Painel de Status e Console de Log
        self.status_frame = ctk.CTkFrame(self)
        self.status_frame.pack(pady=15, padx=40, fill="both", expand=True)

        self.status_title = ctk.CTkLabel(
            self.status_frame, 
            text="Status do Monitoramento:", 
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.status_title.pack(anchor="w", padx=15, pady=5)

        self.status_label = ctk.CTkLabel(
            self.status_frame, 
            text="Parado - Aguardando seleção de diretório", 
            text_color="orange",
            font=ctk.CTkFont(size=13)
        )
        self.status_label.pack(anchor="w", padx=15, pady=5)

        # Container para o Arquivo Atual sendo processado (linha própria)
        self.curr_file_frame = ctk.CTkFrame(self.status_frame, fg_color="transparent")
        self.curr_file_frame.pack(pady=(5, 2), padx=15, fill="x")

        self.label_curr_file = ctk.CTkLabel(
            self.curr_file_frame, 
            text="Lendo: -", 
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="grey"
        )
        self.label_curr_file.pack(anchor="w", padx=10)

        # Container para Contadores Estatísticos em Tempo Real (outras métricas)
        self.stats_frame = ctk.CTkFrame(self.status_frame, fg_color="transparent")
        self.stats_frame.pack(pady=2, padx=15, fill="x")

        # Rótulos dos contadores
        self.label_processed = ctk.CTkLabel(
            self.stats_frame, 
            text="Lidos: 0", 
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="lightgreen"
        )
        self.label_processed.pack(side="left", padx=10)

        self.label_pending = ctk.CTkLabel(
            self.stats_frame, 
            text="Fila: 0", 
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="yellow"
        )
        self.label_pending.pack(side="left", padx=25)

        self.label_skipped = ctk.CTkLabel(
            self.stats_frame, 
            text="Já Lidos: 0", 
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="cyan"
        )
        self.label_skipped.pack(side="left", padx=10)

        # Rótulo para o progresso em bytes
        self.label_bytes = ctk.CTkLabel(
            self.stats_frame, 
            text="Progresso: 0 B / 0 B (0%)", 
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="orange"
        )
        self.label_bytes.pack(side="right", padx=10)

        # Barra de progresso baseada em bytes
        self.progress_bar = ctk.CTkProgressBar(self.status_frame, height=10)
        self.progress_bar.pack(pady=5, padx=15, fill="x")
        self.progress_bar.set(0.0)

        # Caixa de logs em tempo real
        self.log_textbox = ctk.CTkTextbox(
            self.status_frame,
            height=180,
            font=ctk.CTkFont(family="Consolas", size=12)
        )
        self.log_textbox.pack(pady=10, padx=15, fill="both", expand=True)
        self.log_textbox.configure(state="disabled")

        # Botão de Ação (Iniciar/Parar)
        self.action_button = ctk.CTkButton(
            self, 
            text="Iniciar Monitoramento", 
            command=self.toggle_monitoring,
            state="disabled",
            fg_color="green",
            hover_color="#006400"
        )
        self.action_button.pack(pady=20)

        self.log_message("Sistema inicializado. Pronto para configuração.")

    def log_message(self, message: str):
        """
        Adiciona uma mensagem formatada ao console de logs de maneira thread-safe.
        """
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted_message = f"[{timestamp}] {message}\n"
        self.after(0, self._append_log, formatted_message)

    def _append_log(self, text: str):
        """
        Método interno de escrita na caixa de logs (executado sempre na thread principal).
        """
        self.log_textbox.configure(state="normal")
        self.log_textbox.insert(tk.END, text)
        self.log_textbox.see(tk.END)
        self.log_textbox.configure(state="disabled")

    def update_stats_ui(self):
        """
        Atualiza as labels dos contadores estatísticos na UI de maneira thread-safe.
        """
        self.after(0, self._apply_stats_ui)

    def _apply_stats_ui(self):
        """
        Aplica os valores das estatísticas às labels (executado sempre na thread principal).
        """
        # Se a fila de pendentes for menor que zero por algum erro de concorrência, exibe 0
        pending = max(0, self.total_discovered - self.processed_count)
        
        # Nome do arquivo truncado para caber no layout caso seja muito longo
        if hasattr(self, 'current_filename') and self.current_filename:
            fname = self.current_filename
            if len(fname) > 65:
                fname = fname[:62] + "..."
            self.label_curr_file.configure(text=f"Lendo: {fname}", text_color="lightblue")
        else:
            self.label_curr_file.configure(text="Lendo: -", text_color="grey")

        self.label_processed.configure(text=f"Lidos: {self.processed_count}")
        self.label_pending.configure(text=f"Fila: {pending}")
        self.label_skipped.configure(text=f"Já Lidos: {self.skipped_count}")

        # Atualiza a barra de progresso e rótulo de bytes
        def format_size(bytes_val: int) -> str:
            if bytes_val < 1024:
                return f"{bytes_val} B"
            elif bytes_val < 1024 * 1024:
                return f"{bytes_val / 1024:.1f} KB"
            else:
                return f"{bytes_val / (1024 * 1024):.1f} MB"

        if self.total_bytes > 0:
            progress = self.processed_bytes / self.total_bytes
        else:
            progress = 0.0

        progress = min(max(progress, 0.0), 1.0)
        self.progress_bar.set(progress)
        self.label_bytes.configure(
            text=f"Progresso: {format_size(self.processed_bytes)} / {format_size(self.total_bytes)} ({progress * 100:.1f}%)"
        )

    def browse_directory(self):
        """
        Abre uma caixa de diálogo nativa para seleção de diretório.
        """
        selected_dir = filedialog.askdirectory()
        if selected_dir:
            self.monitoring_path = selected_dir
            self.dir_entry.delete(0, tk.END)
            self.dir_entry.insert(0, selected_dir)
            self.status_label.configure(
                text=f"Pronto para iniciar monitoramento em: {selected_dir}",
                text_color="lightblue"
            )
            self.action_button.configure(state="normal")
            self.log_message(f"Pasta selecionada: {selected_dir}")

    def toggle_monitoring(self):
        """
        Alterna o estado de monitoramento (Ativo / Inativo), inicializando ou destruindo o Watcher e a fila.
        """
        if not self.is_monitoring:
            # Reset de contadores
            self.processed_count = 0
            self.total_discovered = 0
            self.total_bytes = 0
            self.processed_bytes = 0
            self.skipped_count = 0
            self.current_filename = ""
            
            # Limpa qualquer resíduo na fila de processamento
            while not self.processing_queue.empty():
                try:
                    self.processing_queue.get_nowait()
                except Empty:
                    break

            # Varredura inicial de PDFs pré-existentes na pasta
            try:
                folder = Path(self.monitoring_path)
                existing_pdfs = list(folder.glob("*.pdf"))
                to_process_pdfs = []
                for pdf_file in existing_pdfs:
                    if self.db_repo.exists_by_source_file(pdf_file.name):
                        self.skipped_count += 1
                        self.log_message(f"[{pdf_file.name}] Já cadastrado no banco de dados. Pulando.")
                        continue
                    to_process_pdfs.append(pdf_file)
                    try:
                        self.total_bytes += pdf_file.stat().st_size
                    except Exception:
                        pass
                    self.processing_queue.put(pdf_file)
                
                self.total_discovered = len(to_process_pdfs)
                self.update_stats_ui()
                
                if existing_pdfs:
                    self.log_message(f"Varredura inicial: Encontrados {len(existing_pdfs)} arquivos PDF. A processar: {self.total_discovered} (já cadastrados/pulados: {self.skipped_count}).")

                # Inicia o FolderWatcher
                self.watcher = FolderWatcher(
                    folder_path=folder,
                    callback=self.on_pdf_detected
                )
                self.watcher.start()
                self.is_monitoring = True
                
                # Inicia a thread de consumo da fila
                self.worker_thread = threading.Thread(target=self.process_queue_worker, daemon=True)
                self.worker_thread.start()

                self.status_label.configure(
                    text=f"Monitorando ativamente: {self.monitoring_path}",
                    text_color="green"
                )
                self.action_button.configure(
                    text="Parar Monitoramento",
                    fg_color="red",
                    hover_color="#8B0000"
                )
                self.dir_entry.configure(state="disabled")
                self.browse_button.configure(state="disabled")
                self.log_message("Serviço de monitoramento de diretório INICIADO.")
            except Exception as e:
                self.log_message(f"Erro ao iniciar monitoramento: {e}")
                self.status_label.configure(text="Erro ao iniciar monitoramento", text_color="red")
        else:
            # Parar Monitoramento
            self.is_monitoring = False
            
            if self.watcher:
                self.watcher.stop()
                self.watcher = None
            
            self.current_filename = ""
            self.total_bytes = 0
            self.processed_bytes = 0
            self.skipped_count = 0
            self.update_stats_ui()
            
            self.status_label.configure(
                text=f"Monitoramento parado em: {self.monitoring_path}",
                text_color="orange"
            )
            self.action_button.configure(
                text="Iniciar Monitoramento",
                fg_color="green",
                hover_color="#006400"
            )
            self.dir_entry.configure(state="normal")
            self.browse_button.configure(state="normal")
            self.log_message("Serviço de monitoramento de diretório PARADO.")

    def on_pdf_detected(self, file_path: Path):
        """
        Callback acionado quando o FolderWatcher identifica um novo PDF.
        Adiciona o arquivo à fila de processamento.
        """
        if self.db_repo.exists_by_source_file(file_path.name):
            self.skipped_count += 1
            self.log_message(f"[{file_path.name}] Novo arquivo detectado, mas já consta no banco de dados. Pulando.")
            self.update_stats_ui()
            return

        self.log_message(f"Novo arquivo detectado pelo monitor: {file_path.name}")
        self.total_discovered += 1
        try:
            self.total_bytes += file_path.stat().st_size
        except Exception:
            pass
        self.processing_queue.put(file_path)
        self.update_stats_ui()

    def process_queue_worker(self):
        """
        Worker em segundo plano que consome a fila de arquivos de forma sequencial.
        """
        while self.is_monitoring:
            try:
                # Timeout curto para permitir que a thread saia caso self.is_monitoring vire False
                file_path = self.processing_queue.get(timeout=1.0)
            except Empty:
                continue

            self.current_filename = file_path.name
            
            try:
                current_file_size = file_path.stat().st_size
            except Exception:
                current_file_size = 0
                
            self.update_stats_ui()
            
            # Executa o pipeline de processamento para o arquivo atual
            self._run_etl_pipeline(file_path)
            
            self.processed_count += 1
            self.processed_bytes += current_file_size
            self.current_filename = ""
            self.update_stats_ui()
            self.processing_queue.task_done()

    def _run_etl_pipeline(self, file_path: Path):
        """
        Executa os passos do ETL para o arquivo fornecido.
        """
        filename = file_path.name
        try:
            # Passo 1: Extração de texto do PDF
            self.log_message(f"[{filename}] [1/3] Extraindo texto do arquivo...")
            text = self.pdf_reader.extract_text(file_path)
            self.log_message(f"[{filename}] Texto extraído com sucesso ({len(text)} caracteres).")

            # Passo 2: Processamento com Ollama (IA)
            self.log_message(f"[{filename}] [2/3] Enviando text para estruturação com LLM (Ollama)...")
            report = self.llm_processor.process_incident_text(text)
            report.source_file = filename
            self.log_message(f"[{filename}] IA estruturou os dados com sucesso. Tipo: {report.incident_type}.")

            # Passo 3: Persistência no TinyDB
            self.log_message(f"[{filename}] [3/3] Persistindo dados no banco local...")
            doc_id = self.db_repo.save(report)
            self.log_message(f"[{filename}] Processamento CONCLUÍDO. Salvo no banco com ID: {doc_id}")

        except FileNotFoundError:
            self.log_message(f"[{filename}] ERRO: Arquivo não pôde ser aberto (removido ou inacessível).")
        except ValueError as ve:
            self.log_message(f"[{filename}] ERRO DE ESTRUTURAÇÃO: {ve}")
        except RuntimeError as re:
            self.log_message(f"[{filename}] ERRO DE COMUNICAÇÃO (IA): {re}")
        except Exception as e:
            self.log_message(f"[{filename}] ERRO INESPERADO: {e}")

if __name__ == "__main__":
    app = IncidentEtlApp()
    app.mainloop()
