import tkinter as tk
from tkinter import filedialog, messagebox
from datetime import datetime
import customtkinter as ctk


class ControlPanelTab(ctk.CTkFrame):
    """
    Componente visual que representa a aba 'Monitoramento'.
    Exibe seleção de pasta, destaque de IA Ollama, métricas com 2 barras de progresso,
    ações exclusivas do monitoramento de diretório e console de logs.
    """
    def __init__(self, master, controller, **kwargs):
        kwargs["fg_color"] = "#18181b"
        super().__init__(master, **kwargs)
        self.controller = controller

        # ---------------------------------------------------------------------
        # 1. Card: Seleção de Pasta & Status do Monitoramento
        # ---------------------------------------------------------------------
        self.dir_frame = ctk.CTkFrame(self, fg_color="#27272a", corner_radius=10)
        self.dir_frame.pack(pady=(10, 6), padx=14, fill="x")

        self.dir_label_title = ctk.CTkLabel(
            self.dir_frame, 
            text="📁 Diretório de Monitoramento dos RELINTs", 
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#a1a1aa"
        )
        self.dir_label_title.pack(anchor="w", padx=12, pady=(8, 2))

        self.dir_entry = ctk.CTkEntry(
            self.dir_frame, 
            placeholder_text="Selecione a pasta para monitorar os arquivos PDF...", 
            height=34,
            font=ctk.CTkFont(size=11)
        )
        self.dir_entry.pack(padx=10, pady=(2, 6), fill="x")

        self.browse_button = ctk.CTkButton(
            self.dir_frame, 
            text="📁 Procurar Pasta no PC", 
            command=self.browse_directory,
            height=34,
            fg_color="#3f3f46",
            hover_color="#52525b",
            text_color="#ffffff",
            text_color_disabled="#71717a",
            font=ctk.CTkFont(size=12, weight="bold")
        )
        self.browse_button.pack(padx=10, pady=(0, 10), fill="x")

        # ---------------------------------------------------------------------
        # 2. Card: Status, Métricas & Duas Barras de Progresso
        # ---------------------------------------------------------------------
        self.stats_card = ctk.CTkFrame(self, fg_color="#27272a", corner_radius=10)
        self.stats_card.pack(pady=6, padx=14, fill="x")

        self.status_header = ctk.CTkFrame(self.stats_card, fg_color="transparent")
        self.status_header.pack(fill="x", padx=12, pady=(8, 2))

        # Linha 1: Status Geral do Motor
        self.status_label = ctk.CTkLabel(
            self.status_header, 
            text="Status: Parado", 
            text_color="#f59e0b",
            font=ctk.CTkFont(size=12, weight="bold")
        )
        self.status_label.pack(anchor="w")

        # Linha 2: Sinalização Dedicada do Arquivo em Leitura Pós-Status
        self.reading_line_frame = ctk.CTkFrame(self.stats_card, fg_color="transparent")
        self.reading_line_frame.pack(fill="x", padx=12, pady=(2, 6))

        self.label_curr_file = ctk.CTkLabel(
            self.reading_line_frame, 
            text="Nenhum arquivo em leitura (Monitoramento Pausado)", 
            font=ctk.CTkFont(size=11),
            text_color="#71717a",
            anchor="w"
        )
        self.label_curr_file.pack(side="left")

        # BARRA DE PROGRESSO 1: Arquivos Lidos na Pasta (Banco / Histórico)
        self.prog1_frame = ctk.CTkFrame(self.stats_card, fg_color="transparent")
        self.prog1_frame.pack(fill="x", padx=12, pady=(4, 2))

        self.label_prog1 = ctk.CTkLabel(
            self.prog1_frame, 
            text="📄 Arquivos Já Lidos (Banco): 0 / 0 (0.0%)", 
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color="#10b981"
        )
        self.label_prog1.pack(anchor="w")

        self.progress_bar1 = ctk.CTkProgressBar(self.prog1_frame, height=8, progress_color="#10b981")
        self.progress_bar1.pack(pady=(2, 4), fill="x")
        self.progress_bar1.set(0)

        # BARRA DE PROGRESSO 2: Leitura Atual da Sessão de Monitoramento
        self.prog2_frame = ctk.CTkFrame(self.stats_card, fg_color="transparent")
        self.prog2_frame.pack(fill="x", padx=12, pady=(0, 8))

        self.label_prog2 = ctk.CTkLabel(
            self.prog2_frame, 
            text="⚡ Progresso Atual: 0 / 0 lidos (0.0%)", 
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color="#c084fc"
        )
        self.label_prog2.pack(anchor="w")

        self.progress_bar2 = ctk.CTkProgressBar(self.prog2_frame, height=8, progress_color="#a855f7")
        self.progress_bar2.pack(pady=(2, 4), fill="x")
        self.progress_bar2.set(0)

        # ---------------------------------------------------------------------
        # 3. Card em Destaque: IA Local (Ollama)
        # ---------------------------------------------------------------------
        self.ai_card = ctk.CTkFrame(self, fg_color="#202023", border_color="#10b981", border_width=1, corner_radius=8)
        self.ai_card.pack(pady=6, padx=14, fill="x")

        self.ai_card_inner = ctk.CTkFrame(self.ai_card, fg_color="transparent")
        self.ai_card_inner.pack(fill="x", padx=10, pady=6)

        self.ai_title = ctk.CTkLabel(
            self.ai_card_inner, 
            text="⚡ IA LOCAL (Ollama)", 
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#34d399"
        )
        self.ai_title.pack(side="left")

        self.switch_llm = ctk.CTkSwitch(
            self.ai_card_inner,
            text="Usar IA",
            command=self.toggle_llm_switch,
            font=ctk.CTkFont(size=12, weight="bold"),
            progress_color="#10b981",
            switch_height=20,
            switch_width=40
        )
        self.switch_llm.select()  # Ativado por padrão
        self.switch_llm.pack(side="right")

        self.ai_status_lbl = ctk.CTkLabel(
            self.ai_card, 
            text="Modo: 🟢 IA Local Habilitado", 
            font=ctk.CTkFont(size=11),
            text_color="#10b981"
        )
        self.ai_status_lbl.pack(anchor="w", padx=10, pady=(0, 6))

        # ---------------------------------------------------------------------
        # 4. Painel de Ações do Monitoramento (Apenas Botões do Monitor)
        # ---------------------------------------------------------------------
        self.action_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.action_frame.pack(pady=8, padx=14, fill="x")

        # Botão 1: Iniciar / Pausar Monitoramento
        self.action_button = ctk.CTkButton(
            self.action_frame, 
            text="▶️ Iniciar Monitoramento", 
            command=self.toggle_monitoring,
            fg_color="#10b981", hover_color="#059669", 
            text_color="#ffffff",
            text_color_disabled="#71717a",
            font=ctk.CTkFont(size=12, weight="bold"),
            height=36,
            corner_radius=8,
            state="disabled"
        )
        self.action_button.pack(fill="x", pady=4)

        # Botão 2: Resetar e Re-ler Todos
        self.btn_reset_all = ctk.CTkButton(
            self.action_frame, 
            text="🔄 Resetar & Re-ler Todos os RELINTs", 
            command=self.confirm_and_reset_all,
            fg_color="#27272a", hover_color="#3f3f46",
            border_color="#d97706", border_width=1,
            text_color="#f59e0b",
            text_color_disabled="#71717a",
            font=ctk.CTkFont(size=12, weight="bold"),
            height=36,
            corner_radius=8,
            state="disabled"
        )
        self.btn_reset_all.pack(fill="x", pady=4)

        # ---------------------------------------------------------------------
        # 5. Console de Logs / Caixa de Mensagens
        # ---------------------------------------------------------------------
        self.log_lbl = ctk.CTkLabel(
            self, 
            text="🖥️ Console de Logs do Sistema em Tempo Real",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color="#a1a1aa"
        )
        self.log_lbl.pack(anchor="w", padx=14, pady=(6, 2))

        self.log_textbox = ctk.CTkTextbox(
            self, 
            height=120, 
            state="disabled", 
            font=ctk.CTkFont(family="Consolas", size=11),
            fg_color="#121212",
            text_color="#f1f5f9"
        )
        self.log_textbox.pack(pady=(0, 10), padx=14, fill="both", expand=True)

        # Checagem automática na inicialização da aplicação
        self.after(300, self.initial_llm_check)

    def initial_llm_check(self):
        """Verifica a conexão com o Ollama na inicialização e ajusta o switch conforme o estado real."""
        success = self.controller.set_use_llm(True)
        if success:
            self.switch_llm.select()
            self.ai_status_lbl.configure(text="Modo: 🟢 IA Local Habilitado", text_color="#10b981")
        else:
            self.switch_llm.deselect()
            self.ai_status_lbl.configure(text="Modo: ⚡ Processamento Regex (Sem IA)", text_color="#f59e0b")
        
        # Inicia o monitor de saúde em tempo real (heartbeat a cada 4 segundos)
        self.after(4000, self.check_llm_heartbeat)

    def check_llm_heartbeat(self):
        """Monitor de saúde em tempo real do Ollama (executado periodicamente a cada 4s)."""
        try:
            if bool(self.switch_llm.get()) and getattr(self.controller, "use_llm", False):
                if hasattr(self.controller, "llm_processor") and hasattr(self.controller.llm_processor, "check_connection"):
                    is_ok, msg = self.controller.llm_processor.check_connection()
                    if not is_ok:
                        self.log_message("⚠️ [ALERTA EM TEMPO REAL] O serviço Ollama foi desligado. Switch de IA desativado.")
                        self.controller.set_use_llm(False)
                        self.switch_llm.deselect()
                        self.ai_status_lbl.configure(
                            text="Modo: ⚡ Processamento Regex (IA Desconectada)", 
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
                fg_color="#10b981", hover_color="#059669", 
                text_color="#ffffff", state="normal"
            )
            self.btn_reset_all.configure(state="normal")
            self.log_message(f"Pasta selecionada: {selected_dir}")

    def toggle_monitoring(self):
        if not self.controller.is_monitoring:
            self.controller.start_monitoring()
        else:
            self.controller.stop_monitoring()

    def toggle_llm_switch(self):
        """Dispara a alternância de uso do Ollama no controlador com teste de saúde."""
        use_llm = bool(self.switch_llm.get())
        success = self.controller.set_use_llm(use_llm)
        if use_llm:
            if success:
                self.ai_status_lbl.configure(text="Modo: 🟢 IA Local Habilitado", text_color="#10b981")
            else:
                self.switch_llm.deselect()
                self.ai_status_lbl.configure(text="Modo: ⚡ Processamento Regex (Sem IA)", text_color="#f59e0b")
        else:
            self.ai_status_lbl.configure(text="Modo: ⚡ Processamento Regex (Sem IA)", text_color="#f59e0b")

    def confirm_and_reset_all(self):
        """Solicita confirmação e executa o reset completo do banco, mídias e re-leitura."""
        answer = messagebox.askyesno(
            "Confirmar Reset Completo",
            "Atenção!\nEsta ação irá zerar todas as ocorrências salvas no banco de dados, limpar o cadastro de pessoas e apagar as mídias salvas.\n\nDeseja continuar e re-ler todos os RELINTs da pasta do zero?",
            icon="warning"
        )
        if answer:
            self.controller.reset_and_reprocess_all()

    def update_stats(self):
        """Atualiza os rótulos de status, estado dos botões e as 2 Barras de Progresso."""
        total_folder = getattr(self.controller, "total_files_in_folder", 0)
        skipped_cnt = getattr(self.controller, "skipped_count", 0)
        processed_cnt = getattr(self.controller, "processed_count", 0)
        discovered_cnt = getattr(self.controller, "total_discovered", 0)
        current_fn = getattr(self.controller, "current_filename", "")
        mon_path = getattr(self.controller, "monitoring_path", "")
        is_monitoring = getattr(self.controller, "is_monitoring", False)
        use_llm = getattr(self.controller, "use_llm", False)

        # 1. Sincroniza o campo de texto da pasta com o controlador
        if mon_path:
            cur_text = self.dir_entry.get()
            if cur_text != mon_path:
                self.dir_entry.delete(0, tk.END)
                self.dir_entry.insert(0, mon_path)

        # 2. Sincroniza o switch de IA
        if bool(self.switch_llm.get()) != use_llm:
            if use_llm:
                self.switch_llm.select()
            else:
                self.switch_llm.deselect()

        # 3. Estado do monitoramento, botões e campos de formulário
        if is_monitoring:
            self.status_label.configure(text="Status: 🟢 Monitoramento Ativo", text_color="#4ade80")
            self.action_button.configure(
                text="⏸️ Pausar Monitoramento", 
                fg_color="#dc2626", hover_color="#b91c1c", 
                text_color="#ffffff", state="normal"
            )
            self.dir_entry.configure(state="disabled")
            self.browse_button.configure(state="disabled")
            self.btn_reset_all.configure(state="normal")
        else:
            self.dir_entry.configure(state="normal")
            self.browse_button.configure(state="normal")
            if mon_path:
                self.status_label.configure(text="Status: ⏸️ Monitoramento Pausado", text_color="#f59e0b")
                self.action_button.configure(
                    text="▶️ Iniciar Monitoramento", 
                    fg_color="#10b981", hover_color="#059669", 
                    text_color="#ffffff", state="normal"
                )
                self.btn_reset_all.configure(state="normal")
            else:
                self.status_label.configure(text="Status: Parado", text_color="#f59e0b")
                self.action_button.configure(
                    text="▶️ Iniciar Monitoramento", 
                    fg_color="#10b981", hover_color="#059669", 
                    text_color="#ffffff", state="disabled"
                )
                self.btn_reset_all.configure(state="disabled")

        fname = current_fn
        if is_monitoring:
            if fname:
                fname_short = fname[:35] + "..." if len(fname) > 38 else fname
                self.label_curr_file.configure(
                    text=f"⏳ Lendo agora: {fname_short}", 
                    text_color="#34d399"
                )
            else:
                self.label_curr_file.configure(
                    text="📡 Vigilância de pasta ativa — Aguardando novos arquivos PDF...", 
                    text_color="#94a3b8"
                )
        else:
            self.label_curr_file.configure(
                text="Nenhum arquivo em leitura (Monitoramento Pausado)", 
                text_color="#71717a"
            )

        # 4. BARRA 1: Arquivos Lidos na Pasta
        total_read_cnt = skipped_cnt + processed_cnt
        if total_folder > 0:
            total_read_cnt = min(total_read_cnt, total_folder)

        if total_folder > 0:
            prog1 = min(max(total_read_cnt / total_folder, 0.0), 1.0)
        else:
            prog1 = 0.0
            
        self.progress_bar1.set(prog1)
        self.label_prog1.configure(
            text=f"📄 Arquivos Já Lidos (Banco): {total_read_cnt} / {total_folder} ({prog1 * 100:.1f}%)"
        )

        # 5. BARRA 2: Leitura Atual da Sessão
        if discovered_cnt > 0:
            prog2 = min(max(processed_cnt / discovered_cnt, 0.0), 1.0)
        else:
            prog2 = 1.0 if (total_folder > 0 and total_read_cnt == total_folder) else 0.0
        
        self.progress_bar2.set(prog2)
        if discovered_cnt > 0:
            self.label_prog2.configure(
                text=f"⚡ Progresso Atual: {processed_cnt} / {discovered_cnt} ({prog2 * 100:.1f}%)",
                text_color="#c084fc"
            )
        else:
            if total_folder > 0 and total_read_cnt == total_folder:
                self.label_prog2.configure(
                    text="⚡ Progresso Atual: Todos da pasta cadastrados",
                    text_color="#34d399"
                )
            else:
                self.label_prog2.configure(
                    text="⚡ Progresso Atual: Aguardando monitoramento",
                    text_color="#d4d4d8"
                )

    def log_message(self, message: str):
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_textbox.configure(state="normal")
        self.log_textbox.insert("end", f"[{timestamp}] {message}\n")
        self.log_textbox.see("end")
        self.log_textbox.configure(state="disabled")
