import tkinter as tk
from tkinter import filedialog
from datetime import datetime
import customtkinter as ctk

class ControlPanelTab(ctk.CTkFrame):
    """
    Componente visual que representa a aba 'Painel de Controle'.
    Exibe os status de monitoramento, barra de progresso, logs e contadores.
    """
    def __init__(self, master, controller, **kwargs):
        super().__init__(master, **kwargs)
        self.controller = controller

        # Container para a Seleção de Diretório
        self.dir_frame = ctk.CTkFrame(self)
        self.dir_frame.pack(pady=10, padx=20, fill="x")

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

        # Painel de Status
        self.status_frame = ctk.CTkFrame(self)
        self.status_frame.pack(pady=10, padx=20, fill="both", expand=True)

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

        # Arquivo atual
        self.curr_file_frame = ctk.CTkFrame(self.status_frame, fg_color="transparent")
        self.curr_file_frame.pack(pady=(5, 2), padx=15, fill="x")
        self.label_curr_file = ctk.CTkLabel(
            self.curr_file_frame, 
            text="Lendo: -", 
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="grey"
        )
        self.label_curr_file.pack(anchor="w", padx=10)

        # Contadores
        self.stats_frame = ctk.CTkFrame(self.status_frame, fg_color="transparent")
        self.stats_frame.pack(pady=2, padx=15, fill="x")

        self.label_processed = ctk.CTkLabel(self.stats_frame, text="Lidos: 0", font=ctk.CTkFont(size=12, weight="bold"), text_color="lightgreen")
        self.label_processed.pack(side="left", padx=10)

        self.label_pending = ctk.CTkLabel(self.stats_frame, text="Fila: 0", font=ctk.CTkFont(size=12, weight="bold"), text_color="yellow")
        self.label_pending.pack(side="left", padx=25)

        current_date = datetime.now().strftime("%d/%m/%Y")
        self.label_skipped = ctk.CTkLabel(self.stats_frame, text=f"Lidos em {current_date}: 0", font=ctk.CTkFont(size=12, weight="bold"), text_color="cyan")
        self.label_skipped.pack(side="left", padx=10)

        self.label_total_files = ctk.CTkLabel(self.stats_frame, text="Total Pasta: 0", font=ctk.CTkFont(size=12, weight="bold"), text_color="#c084fc")
        self.label_total_files.pack(side="left", padx=25)

        self.label_bytes = ctk.CTkLabel(self.stats_frame, text="Progresso: 0 B / 0 B (0%)", font=ctk.CTkFont(size=12, weight="bold"), text_color="orange")
        self.label_bytes.pack(side="right", padx=10)

        # Barra de Progresso
        self.progress_bar = ctk.CTkProgressBar(self.status_frame, height=10)
        self.progress_bar.pack(pady=5, padx=15, fill="x")
        self.progress_bar.set(0)

        # Botões de Ação
        self.action_frame = ctk.CTkFrame(self.status_frame, fg_color="transparent")
        self.action_frame.pack(pady=10, padx=15, fill="x")

        # Esquerda (Monitoramento e Atualização)
        self.action_button = ctk.CTkButton(
            self.action_frame, 
            text="Monitorar Homicídios", 
            command=self.toggle_monitoring,
            fg_color="green", hover_color="#006400", state="disabled"
        )
        self.action_button.pack(side="left", padx=(0, 10))

        self.btn_update = ctk.CTkButton(
            self.action_frame, 
            text="Atualizar Homicídios (Novo Filtro)", 
            command=self.controller.update_homicides_only,
            fg_color="#8b5cf6", hover_color="#7c3aed", state="disabled"
        )
        self.btn_update.pack(side="left", padx=10)

        # Direita (Dashboards)
        self.btn_dashboard_close = ctk.CTkButton(
            self.action_frame, 
            text="Encerrar Dashboards", 
            command=self.kill_all_dashboards,
            fg_color="#ef4444", hover_color="#b91c1c"
        )
        self.btn_dashboard_close.pack(side="right", padx=(10, 0))

        self.btn_dashboard = ctk.CTkButton(
            self.action_frame, 
            text="Abrir Dashboard (Web)", 
            command=self.open_dashboard,
            fg_color="#3b82f6", hover_color="#2563eb"
        )
        self.btn_dashboard.pack(side="right", padx=10)

        # Console de Logs
        self.log_textbox = ctk.CTkTextbox(self, height=120, state="disabled", font=ctk.CTkFont(family="Consolas", size=12))
        self.log_textbox.pack(pady=10, padx=15, fill="both", expand=True)

    def browse_directory(self):
        selected_dir = filedialog.askdirectory()
        if selected_dir:
            self.controller.set_monitoring_path(selected_dir)
            self.dir_entry.delete(0, tk.END)
            self.dir_entry.insert(0, selected_dir)
            self.status_label.configure(text=f"Pronto para iniciar monitoramento em: {selected_dir}", text_color="lightblue")
            self.action_button.configure(state="normal")
            self.btn_update.configure(state="normal")
            self.log_message(f"Pasta selecionada: {selected_dir}")

    def toggle_monitoring(self):
        if not self.controller.is_monitoring:
            self.status_label.configure(text=f"Monitorando ativamente: {self.controller.monitoring_path}", text_color="green")
            self.action_button.configure(text="Parar Monitoramento", fg_color="red", hover_color="#8B0000")
            self.dir_entry.configure(state="disabled")
            self.browse_button.configure(state="disabled")
            self.btn_update.configure(state="disabled")
            self.controller.start_monitoring()
        else:
            self.status_label.configure(text=f"Monitoramento parado em: {self.controller.monitoring_path}", text_color="orange")
            self.action_button.configure(text="Monitorar Homicídios", fg_color="green", hover_color="#006400")
            self.dir_entry.configure(state="normal")
            self.browse_button.configure(state="normal")
            self.btn_update.configure(state="normal")
            self.controller.stop_monitoring()

    def kill_all_dashboards(self):
        import subprocess
        self.log_message("Executando varredura para eliminar todos os processos fantasmas do Streamlit...")
        try:
            cmd = 'Get-CimInstance Win32_Process -Filter "CommandLine LIKE \'%streamlit%\'" | ForEach-Object { Stop-Process -Id $_.ProcessId -Force }'
            subprocess.run(["powershell", "-Command", cmd], capture_output=True, text=True, creationflags=0x08000000)
            self.log_message("Varredura concluída. Todos os Dashboards foram encerrados.")
        except Exception as e:
            self.log_message(f"Erro ao matar processos: {e}")
        self.controller.close_dashboard()

    def open_dashboard(self):
        self.controller.open_dashboard()

    def update_stats(self):
        pending = max(0, self.controller.total_discovered - self.controller.processed_count)
        
        fname = self.controller.current_filename
        if fname:
            fname = fname[:62] + "..." if len(fname) > 65 else fname
            self.label_curr_file.configure(text=f"Lendo: {fname}", text_color="lightblue")
        else:
            self.label_curr_file.configure(text="Lendo: -", text_color="grey")

        self.label_processed.configure(text=f"Lidos: {self.controller.processed_count}")
        self.label_pending.configure(text=f"Fila: {pending}")
        current_date = datetime.now().strftime("%d/%m/%Y")
        self.label_skipped.configure(text=f"Lidos em {current_date}: {self.controller.skipped_count}")
        self.label_total_files.configure(text=f"Total Pasta: {self.controller.total_files_in_folder}")

        def format_size(bytes_val: int) -> str:
            if bytes_val < 1024: return f"{bytes_val} B"
            elif bytes_val < 1024 * 1024: return f"{bytes_val / 1024:.1f} KB"
            else: return f"{bytes_val / (1024 * 1024):.1f} MB"

        if self.controller.total_bytes > 0:
            progress = self.controller.processed_bytes / self.controller.total_bytes
        else:
            progress = 0.0

        progress = min(max(progress, 0.0), 1.0)
        self.progress_bar.set(progress)
        self.label_bytes.configure(
            text=f"Progresso: {format_size(self.controller.processed_bytes)} / {format_size(self.controller.total_bytes)} ({progress * 100:.1f}%)"
        )

    def log_message(self, message: str):
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_textbox.configure(state="normal")
        self.log_textbox.insert("end", f"[{timestamp}] {message}\n")
        self.log_textbox.see("end")
        self.log_textbox.configure(state="disabled")
