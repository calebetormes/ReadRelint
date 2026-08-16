import tkinter as tk
from tkinter import filedialog, messagebox
from datetime import datetime
import customtkinter as ctk


class ControlPanelTab(ctk.CTkFrame):
    """
    Componente visual moderno que representa a aba 'Painel de Controle'.
    Exibe seleção de pasta, destaque de IA Ollama, métricas com 2 barras de progresso,
    ações de controle (monitoramento, reset completo e servidor web) e logs.
    """
    def __init__(self, master, controller, **kwargs):
        kwargs["fg_color"] = "#18181b"
        super().__init__(master, **kwargs)
        self.controller = controller

        # ---------------------------------------------------------------------
        # 1. Card: Seleção de Pasta & Status do Monitoramento
        # ---------------------------------------------------------------------
        self.dir_frame = ctk.CTkFrame(self, fg_color="#27272a", corner_radius=10)
        self.dir_frame.pack(pady=(10, 5), padx=15, fill="x")

        self.dir_label_title = ctk.CTkLabel(
            self.dir_frame, 
            text="📁 Diretório de Monitoramento dos RELINTs", 
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="#a1a1aa"
        )
        self.dir_label_title.pack(anchor="w", padx=15, pady=(8, 2))

        self.dir_inner_frame = ctk.CTkFrame(self.dir_frame, fg_color="transparent")
        self.dir_inner_frame.pack(fill="x", padx=10, pady=(0, 8))

        self.dir_entry = ctk.CTkEntry(
            self.dir_inner_frame, 
            placeholder_text="Selecione a pasta para monitorar os arquivos PDF...", 
            height=36,
            font=ctk.CTkFont(size=12)
        )
        self.dir_entry.pack(side="left", padx=(5, 10), expand=True, fill="x")

        self.browse_button = ctk.CTkButton(
            self.dir_inner_frame, 
            text="Buscar Pasta", 
            command=self.browse_directory,
            height=36,
            fg_color="#3f3f46",
            hover_color="#52525b",
            text_color="#ffffff",
            text_color_disabled="#71717a",
            font=ctk.CTkFont(weight="bold")
        )
        self.browse_button.pack(side="right", padx=5)

        # ---------------------------------------------------------------------
        # 2. Card: Status, Métricas & Duas Barras de Progresso
        # ---------------------------------------------------------------------
        self.stats_card = ctk.CTkFrame(self, fg_color="#27272a", corner_radius=10)
        self.stats_card.pack(pady=5, padx=15, fill="x")

        # Cabeçalho do Card de Status
        self.status_header = ctk.CTkFrame(self.stats_card, fg_color="transparent")
        self.status_header.pack(fill="x", padx=15, pady=(8, 2))

        self.status_label = ctk.CTkLabel(
            self.status_header, 
            text="Status: Parado - Aguardando seleção de diretório", 
            text_color="#f59e0b",
            font=ctk.CTkFont(size=13, weight="bold")
        )
        self.status_label.pack(side="left")

        self.label_curr_file = ctk.CTkLabel(
            self.status_header, 
            text="Lendo: -", 
            font=ctk.CTkFont(size=12),
            text_color="#d4d4d8"
        )
        self.label_curr_file.pack(side="right")

        # BARRA DE PROGRESSO 1: Arquivos Lidos Anteriormente (Banco / Histórico)
        self.prog1_frame = ctk.CTkFrame(self.stats_card, fg_color="transparent")
        self.prog1_frame.pack(fill="x", padx=15, pady=(6, 2))

        self.label_prog1 = ctk.CTkLabel(
            self.prog1_frame, 
            text="📄 Arquivos Já Lidos (Banco): 0 / 0 (0.0%)", 
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#10b981"
        )
        self.label_prog1.pack(anchor="w")

        self.progress_bar1 = ctk.CTkProgressBar(self.prog1_frame, height=10, progress_color="#10b981")
        self.progress_bar1.pack(pady=(2, 6), fill="x")
        self.progress_bar1.set(0)

        # BARRA DE PROGRESSO 2: Leitura Atual da Sessão de Monitoramento
        self.prog2_frame = ctk.CTkFrame(self.stats_card, fg_color="transparent")
        self.prog2_frame.pack(fill="x", padx=15, pady=(0, 8))

        self.label_prog2 = ctk.CTkLabel(
            self.prog2_frame, 
            text="⚡ Progresso da Leitura Atual: 0 / 0 novos arquivos lidos (0.0%)", 
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#c084fc"
        )
        self.label_prog2.pack(anchor="w")

        self.progress_bar2 = ctk.CTkProgressBar(self.prog2_frame, height=10, progress_color="#a855f7")
        self.progress_bar2.pack(pady=(2, 4), fill="x")
        self.progress_bar2.set(0)

        # ---------------------------------------------------------------------
        # 3. Card: Painel de Ações (Botões Principais)
        # ---------------------------------------------------------------------
        self.action_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.action_frame.pack(pady=5, padx=15, fill="x")

        # Botão Principal: Monitorar
        self.action_button = ctk.CTkButton(
            self.action_frame, 
            text="▶️ Iniciar Monitoramento", 
            command=self.toggle_monitoring,
            fg_color="#059669", hover_color="#047857", 
            text_color="#ffffff",
            text_color_disabled="#71717a",
            font=ctk.CTkFont(weight="bold"),
            height=38,
            state="disabled"
        )
        self.action_button.pack(side="left", padx=(0, 10))

        # Novo Botão: Resetar e Re-ler Todos os RELINTs
        self.btn_reset_all = ctk.CTkButton(
            self.action_frame, 
            text="🔄 Resetar & Re-ler Todos os RELINTs", 
            command=self.confirm_and_reset_all,
            fg_color="#d97706", hover_color="#b45309",
            text_color="#ffffff",
            text_color_disabled="#71717a",
            font=ctk.CTkFont(weight="bold"),
            height=38,
            state="disabled"
        )
        self.btn_reset_all.pack(side="left", padx=10)

        # Servidor e Painel Web (Direita)
        self.btn_dashboard_close = ctk.CTkButton(
            self.action_frame,
            text="⛔ Parar Servidor Web",
            command=self.stop_web_server,
            fg_color="#dc2626", hover_color="#b91c1c",
            text_color="#ffffff",
            font=ctk.CTkFont(weight="bold"),
            height=38
        )
        self.btn_dashboard_close.pack(side="right", padx=(5, 0))

        self.btn_dashboard = ctk.CTkButton(
            self.action_frame,
            text="🌐 Abrir Painel Web",
            command=self.open_web_dashboard,
            fg_color="#0d9488", hover_color="#0f766e",
            text_color="#ffffff",
            font=ctk.CTkFont(weight="bold"),
            height=38
        )
        self.btn_dashboard.pack(side="right", padx=5)

        # ---------------------------------------------------------------------
        # 4. Console de Logs / Caixa de Mensagens
        # ---------------------------------------------------------------------
        self.log_textbox = ctk.CTkTextbox(
            self, 
            height=140, 
            state="disabled", 
            font=ctk.CTkFont(family="Consolas", size=12),
            fg_color="#121212",
            text_color="#f1f5f9"
        )
        self.log_textbox.pack(pady=5, padx=15, fill="both", expand=True)

        # ---------------------------------------------------------------------
        # 5. Card em Destaque: Inteligência Artificial (Ollama)
        # (Posicionado ABAIXO da caixa de mensagens/logs do sistema)
        # ---------------------------------------------------------------------
        self.ai_card = ctk.CTkFrame(self, fg_color="#202023", border_color="#10b981", border_width=1.5, corner_radius=10)
        self.ai_card.pack(pady=(5, 10), padx=15, fill="x")

        self.ai_card_left = ctk.CTkFrame(self.ai_card, fg_color="transparent")
        self.ai_card_left.pack(side="left", padx=15, pady=10)

        self.ai_title = ctk.CTkLabel(
            self.ai_card_left, 
            text="⚡ INTELIGÊNCIA ARTIFICIAL (Ollama Local)", 
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#34d399"
        )
        self.ai_title.pack(anchor="w")

        self.ai_status_lbl = ctk.CTkLabel(
            self.ai_card_left, 
            text="Modo Ativo: 🟢 IA Local (Ollama) Habilitado", 
            font=ctk.CTkFont(size=12),
            text_color="#10b981"
        )
        self.ai_status_lbl.pack(anchor="w", pady=(2, 0))

        self.switch_llm = ctk.CTkSwitch(
            self.ai_card,
            text="Usar Processamento por IA",
            command=self.toggle_llm_switch,
            font=ctk.CTkFont(size=13, weight="bold"),
            progress_color="#10b981",
            switch_height=22,
            switch_width=44
        )
        self.switch_llm.select()  # Ativado por padrão
        self.switch_llm.pack(side="right", padx=20, pady=10)

        # Checagem automática na inicialização da aplicação
        self.after(300, self.initial_llm_check)

    def initial_llm_check(self):
        """Verifica a conexão com o Ollama na inicialização e ajusta o switch conforme o estado real."""
        success = self.controller.set_use_llm(True)
        if success:
            self.switch_llm.select()
            self.ai_status_lbl.configure(text="Modo Ativo: 🟢 IA Local (Ollama) Habilitado", text_color="#10b981")
        else:
            self.switch_llm.deselect()
            self.ai_status_lbl.configure(text="Modo Ativo: ⚡ Processamento Ultra-Rápido (Regex / Sem IA)", text_color="#f59e0b")
        
        # Inicia o monitor de saúde em tempo real (heartbeat a cada 4 segundos)
        self.after(4000, self.check_llm_heartbeat)

    def check_llm_heartbeat(self):
        """Monitor de saúde em tempo real do Ollama (executado periodicamente a cada 4s)."""
        try:
            if bool(self.switch_llm.get()) and getattr(self.controller, "use_llm", False):
                if hasattr(self.controller, "llm_processor") and hasattr(self.controller.llm_processor, "check_connection"):
                    is_ok, msg = self.controller.llm_processor.check_connection()
                    if not is_ok:
                        self.log_message("⚠️ [ALERTA DE DESCONEXÃO EM TEMPO REAL] O serviço Ollama foi desligado ou encerrado. O botão de IA foi DESLIGADO automaticamente.")
                        self.controller.set_use_llm(False)
                        self.switch_llm.deselect()
                        self.ai_status_lbl.configure(
                            text="Modo Ativo: ⚡ Processamento Ultra-Rápido (Regex / Sem IA) — [IA Desconectada]", 
                            text_color="#f59e0b"
                        )
        except Exception:
            pass
        finally:
            self.after(4000, self.check_llm_heartbeat)

    def browse_directory(self):
        selected_dir = filedialog.askdirectory()
        if selected_dir:
            self.controller.set_monitoring_path(selected_dir)
            self.dir_entry.delete(0, tk.END)
            self.dir_entry.insert(0, selected_dir)
            self.status_label.configure(text="Status: ⏸️ Monitoramento Pausado", text_color="#f59e0b")
            self.action_button.configure(
                text="▶️ Iniciar Monitoramento", 
                fg_color="#059669", hover_color="#047857", 
                text_color="#ffffff", state="normal"
            )
            self.btn_reset_all.configure(state="normal")
            self.log_message(f"Pasta selecionada: {selected_dir}")

    def toggle_monitoring(self):
        if not self.controller.is_monitoring:
            self.status_label.configure(text="Status: 🟢 Monitoramento Ativo", text_color="#4ade80")
            self.action_button.configure(
                text="⏸️ Pausar Monitoramento", 
                fg_color="#dc2626", hover_color="#b91c1c", 
                text_color="#ffffff", state="normal"
            )
            self.dir_entry.configure(state="disabled")
            self.browse_button.configure(state="disabled")
            self.controller.start_monitoring()
        else:
            self.status_label.configure(text="Status: ⏸️ Monitoramento Pausado", text_color="#f59e0b")
            self.action_button.configure(
                text="▶️ Iniciar Monitoramento", 
                fg_color="#059669", hover_color="#047857", 
                text_color="#ffffff", state="normal"
            )
            self.dir_entry.configure(state="normal")
            self.browse_button.configure(state="normal")
            self.controller.stop_monitoring()

    def toggle_llm_switch(self):
        """Dispara a alternância de uso do Ollama no controlador com teste de saúde."""
        use_llm = bool(self.switch_llm.get())
        success = self.controller.set_use_llm(use_llm)
        if use_llm:
            if success:
                self.ai_status_lbl.configure(text="Modo Ativo: 🟢 IA Local (Ollama) Habilitado", text_color="#10b981")
            else:
                self.switch_llm.deselect()
                self.ai_status_lbl.configure(text="Modo Ativo: ⚡ Processamento Ultra-Rápido (Regex / Sem IA)", text_color="#f59e0b")
        else:
            self.ai_status_lbl.configure(text="Modo Ativo: ⚡ Processamento Ultra-Rápido (Regex / Sem IA)", text_color="#f59e0b")

    def on_llm_disconnected_ui(self):
        """Desativa o switch da IA e atualiza o rótulo quando o Ollama é fechado/desconectado durante a leitura."""
        self.switch_llm.deselect()
        self.ai_status_lbl.configure(
            text="Modo Ativo: ⚡ Processamento Ultra-Rápido (Regex / Sem IA) — [IA Desconectada]", 
            text_color="#f59e0b"
        )

    def confirm_and_reset_all(self):
        """Solicita confirmação e executa o reset completo do banco, mídias e re-leitura."""
        answer = messagebox.askyesno(
            "Confirmar Reset Completo",
            "Atenção!\nEsta ação irá zerar todas as ocorrências salvas no banco de dados, limpar o cadastro de pessoas e apagar as mídias salvas.\n\nDeseja continuar e re-ler todos os RELINTs da pasta do zero?",
            icon="warning"
        )
        if answer:
            self.controller.reset_and_reprocess_all()

    def stop_web_server(self) -> None:
        """Encerra o processo do servidor Uvicorn via PowerShell e pelo controlador."""
        import subprocess
        self.log_message("Encerrando processos Uvicorn do Servidor Web...")
        try:
            cmd = (
                'Get-CimInstance Win32_Process '
                '-Filter "CommandLine LIKE \'%uvicorn%\'" '
                '| ForEach-Object { Stop-Process -Id $_.ProcessId -Force }'
            )
            subprocess.run(
                ["powershell", "-Command", cmd],
                capture_output=True,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW,
            )
            self.log_message("Servidor Web encerrado.")
        except Exception as exc:
            self.log_message(f"Erro ao encerrar processos: {exc}")
        self.controller.close_web_dashboard()

    def open_web_dashboard(self) -> None:
        """Abre o Painel Web no navegador padrão."""
        self.controller.open_web_dashboard()

    def update_stats(self):
        """Atualiza os rótulos de status, estado dos botões e as 2 Barras de Progresso."""
        total_folder = getattr(self.controller, "total_files_in_folder", 0)
        skipped_cnt = getattr(self.controller, "skipped_count", 0)
        processed_cnt = getattr(self.controller, "processed_count", 0)
        discovered_cnt = getattr(self.controller, "total_discovered", 0)
        current_fn = getattr(self.controller, "current_filename", "")

        # Estado do monitoramento e status
        if self.controller.is_monitoring:
            self.status_label.configure(text="Status: 🟢 Monitoramento Ativo", text_color="#4ade80")
            self.action_button.configure(
                text="⏸️ Pausar Monitoramento", 
                fg_color="#dc2626", hover_color="#b91c1c", 
                text_color="#ffffff", state="normal"
            )
        else:
            if self.controller.monitoring_path:
                self.status_label.configure(text="Status: ⏸️ Monitoramento Pausado", text_color="#f59e0b")
                self.action_button.configure(
                    text="▶️ Iniciar Monitoramento", 
                    fg_color="#059669", hover_color="#047857", 
                    text_color="#ffffff", state="normal"
                )
            else:
                self.status_label.configure(text="Status: Parado - Aguardando seleção de diretório", text_color="#f59e0b")
                self.action_button.configure(
                    text="▶️ Iniciar Monitoramento", 
                    fg_color="#059669", hover_color="#047857", 
                    text_color="#ffffff", state="disabled"
                )

        fname = current_fn
        if fname:
            fname_short = fname[:60] + "..." if len(fname) > 65 else fname
            self.label_curr_file.configure(text=f"Lendo: {fname_short}", text_color="#34d399")
        else:
            self.label_curr_file.configure(text="Lendo: -", text_color="#d4d4d8")

        # 1. BARRA 1 (Barra de Cima: Arquivos Lidos na Pasta):
        # Atualizada em tempo real sempre que uma leitura for concluída!
        total_read_cnt = skipped_cnt + processed_cnt
        if total_folder > 0:
            total_read_cnt = min(total_read_cnt, total_folder)

        if total_folder > 0:
            prog1 = min(max(total_read_cnt / total_folder, 0.0), 1.0)
        else:
            prog1 = 0.0
            
        self.progress_bar1.set(prog1)
        self.label_prog1.configure(
            text=f"📄 Arquivos Lidos na Pasta: {total_read_cnt} / {total_folder} arquivos ({prog1 * 100:.1f}%)"
        )

        # 2. BARRA 2 (Barra de Baixo: Leitura Atual da Sessão)
        if discovered_cnt > 0:
            prog2 = min(max(processed_cnt / discovered_cnt, 0.0), 1.0)
        else:
            prog2 = 1.0 if (total_folder > 0 and total_read_cnt == total_folder) else 0.0
        
        self.progress_bar2.set(prog2)
        if discovered_cnt > 0:
            self.label_prog2.configure(
                text=f"⚡ Progresso da Leitura Atual: {processed_cnt} / {discovered_cnt} novos arquivos lidos ({prog2 * 100:.1f}%)",
                text_color="#c084fc"
            )
        else:
            if total_folder > 0 and total_read_cnt == total_folder:
                self.label_prog2.configure(
                    text="⚡ Progresso da Leitura Atual: Todos os arquivos da pasta já estão cadastrados",
                    text_color="#34d399"
                )
            else:
                self.label_prog2.configure(
                    text="⚡ Progresso da Leitura Atual: Aguardando início do monitoramento",
                    text_color="#d4d4d8"
                )

    def log_message(self, message: str):
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_textbox.configure(state="normal")
        self.log_textbox.insert("end", f"[{timestamp}] {message}\n")
        self.log_textbox.see("end")
        self.log_textbox.configure(state="disabled")
