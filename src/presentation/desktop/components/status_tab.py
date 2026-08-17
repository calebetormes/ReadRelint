from tkinter import messagebox
import customtkinter as ctk

class StatusTab(ctk.CTkFrame):
    """
    Componente visual que representa a primeira aba 'STATUS'.
    Exibe o estado em tempo real do Monitoramento de Pastas, Painel Web (FastAPI)
    e Inteligência Artificial (Ollama), métricas rápidas e botões de ação dinâmica.
    """
    def __init__(self, master, controller, **kwargs):
        kwargs["fg_color"] = "#18181b"
        super().__init__(master, **kwargs)
        self.controller = controller

        # Título da Aba
        self.title_lbl = ctk.CTkLabel(
            self,
            text="📊 STATUS GERAL DO SISTEMA",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#f8fafc"
        )
        self.title_lbl.pack(anchor="w", padx=15, pady=(12, 6))

        # ---------------------------------------------------------------------
        # 1. Card: Status do Monitoramento de Pastas
        # ---------------------------------------------------------------------
        self.card_monitor = ctk.CTkFrame(self, fg_color="#27272a", corner_radius=10)
        self.card_monitor.pack(pady=5, padx=15, fill="x")

        self.lbl_mon_title = ctk.CTkLabel(
            self.card_monitor,
            text="📁 Monitoramento de Diretório",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="#a1a1aa"
        )
        self.lbl_mon_title.pack(anchor="w", padx=12, pady=(8, 2))

        self.lbl_mon_status = ctk.CTkLabel(
            self.card_monitor,
            text="Status: ⏹️ Parado - Nenhuma pasta selecionada",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#f59e0b",
            wraplength=440,
            justify="left"
        )
        self.lbl_mon_status.pack(anchor="w", padx=12, pady=(0, 8))

        # ---------------------------------------------------------------------
        # 2. Card: Status do Painel Web (FastAPI)
        # ---------------------------------------------------------------------
        self.card_web = ctk.CTkFrame(self, fg_color="#27272a", corner_radius=10)
        self.card_web.pack(pady=5, padx=15, fill="x")

        self.lbl_web_title = ctk.CTkLabel(
            self.card_web,
            text="🌐 Painel Web (Servidor FastAPI)",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="#a1a1aa"
        )
        self.lbl_web_title.pack(anchor="w", padx=12, pady=(8, 2))

        self.lbl_web_status = ctk.CTkLabel(
            self.card_web,
            text="Status: 🔴 Offline (Servidor Web Desligado)",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#ef4444",
            wraplength=440,
            justify="left"
        )
        self.lbl_web_status.pack(anchor="w", padx=12, pady=(0, 8))

        # ---------------------------------------------------------------------
        # 3. Card: Status da IA Local (Ollama)
        # ---------------------------------------------------------------------
        self.card_ai = ctk.CTkFrame(self, fg_color="#27272a", corner_radius=10)
        self.card_ai.pack(pady=5, padx=15, fill="x")

        self.lbl_ai_title = ctk.CTkLabel(
            self.card_ai,
            text="⚡ Inteligência Artificial (Ollama Local)",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="#a1a1aa"
        )
        self.lbl_ai_title.pack(anchor="w", padx=12, pady=(8, 2))

        self.lbl_ai_status = ctk.CTkLabel(
            self.card_ai,
            text="Modo: 🟢 IA Local (Ollama) Habilitado",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#10b981",
            wraplength=440,
            justify="left"
        )
        self.lbl_ai_status.pack(anchor="w", padx=12, pady=(0, 8))

        # ---------------------------------------------------------------------
        # 4. Resumo de Métricas Rápidas (3 Sub-cards)
        # ---------------------------------------------------------------------
        self.metrics_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.metrics_frame.pack(fill="x", padx=15, pady=(8, 4))
        for i in range(3):
            self.metrics_frame.grid_columnconfigure(i, weight=1)

        def create_metric_card(parent, title, color, col):
            card = ctk.CTkFrame(parent, fg_color="#27272a", corner_radius=8, height=65)
            card.grid(row=0, column=col, padx=4, pady=2, sticky="ew")
            card.pack_propagate(False)

            lbl_t = ctk.CTkLabel(card, text=title, font=ctk.CTkFont(size=11, weight="bold"), text_color="#a1a1aa")
            lbl_t.pack(pady=(6, 0))

            lbl_v = ctk.CTkLabel(card, text="0", font=ctk.CTkFont(size=18, weight="bold"), text_color=color)
            lbl_v.pack(pady=(0, 4))
            return lbl_v

        self.val_total_folder = create_metric_card(self.metrics_frame, "Total na Pasta", "#c084fc", 0)
        self.val_lidos_llm = create_metric_card(self.metrics_frame, "Lidos c/ IA", "#10b981", 1)
        self.val_lidos_regex = create_metric_card(self.metrics_frame, "Lidos s/ IA", "#f59e0b", 2)

        # ---------------------------------------------------------------------
        # 5. Painel de Ações Rápidas (Botão Dinâmico do Servidor Web)
        # ---------------------------------------------------------------------
        self.action_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.action_frame.pack(pady=(8, 12), padx=15, fill="x")

        # Botão Dinâmico de Iniciar/Parar Servidor Web
        self.btn_web_toggle = ctk.CTkButton(
            self.action_frame,
            text="🌐 Iniciar & Abrir Painel Web",
            command=self.toggle_web_server,
            fg_color="#0d9488", hover_color="#0f766e",
            text_color="#ffffff",
            font=ctk.CTkFont(size=12, weight="bold"),
            height=36,
            corner_radius=8
        )
        self.btn_web_toggle.pack(fill="x", pady=3)

        # Botão secundário de reabrir navegador se o servidor já estiver online
        self.btn_reopen_web = ctk.CTkButton(
            self.action_frame,
            text="🔗 Reabrir Dashboard no Navegador",
            command=self.reopen_web_browser,
            fg_color="#27272a", hover_color="#3f3f46",
            border_color="#0d9488", border_width=1,
            text_color="#2dd4bf",
            font=ctk.CTkFont(size=11, weight="bold"),
            height=32,
            corner_radius=8
        )

        # Botão de encerramento total da aplicação
        self.btn_exit_app = ctk.CTkButton(
            self.action_frame,
            text="❌ Encerrar Aplicação Totalmente",
            command=self.exit_application_total,
            fg_color="#18181b", hover_color="#27272a",
            border_color="#52525b", border_width=1,
            text_color="#a1a1aa",
            font=ctk.CTkFont(size=12, weight="bold"),
            height=36,
            corner_radius=8
        )
        self.btn_exit_app.pack(fill="x", pady=3)

        self.update_stats()

    def toggle_web_server(self):
        """Alterna dinamicamente entre iniciar/abrir o servidor web e pará-lo."""
        web_manager = getattr(self.controller, "web_app_manager", None)
        if web_manager and web_manager.is_running:
            self.controller.close_web_dashboard()
        else:
            self.controller.open_web_dashboard()
        self.update_stats()

    def reopen_web_browser(self):
        """Reabre o navegador na URL do servidor Web caso ele já esteja online."""
        web_manager = getattr(self.controller, "web_app_manager", None)
        if web_manager:
            web_manager._open_browser()

    def exit_application_total(self):
        """Solicita confirmação e encerra totalmente a aplicação (processos + janela)."""
        answer = messagebox.askyesno(
            "Encerrar Aplicação Totalmente",
            "Deseja fechar completamente o ReadRelint e parar o monitoramento e o servidor Web?",
            icon="warning"
        )
        if answer:
            root = self.winfo_toplevel()
            if hasattr(root, "force_quit"):
                root.force_quit()
            else:
                if self.controller:
                    self.controller.destroy()
                root.destroy()

    def update_stats(self):
        """Sincroniza os rótulos de status e altera dinamicamente os botões de ação."""
        # 1. Monitoramento
        path = getattr(self.controller, "monitoring_path", "")
        is_mon = getattr(self.controller, "is_monitoring", False)

        if is_mon:
            path_short = path if len(path) <= 45 else path[:20] + "..." + path[-22:]
            self.lbl_mon_status.configure(
                text=f"Status: 🟢 Monitorando pasta: \"{path_short}\"",
                text_color="#4ade80"
            )
        elif path:
            path_short = path if len(path) <= 45 else path[:20] + "..." + path[-22:]
            self.lbl_mon_status.configure(
                text=f"Status: ⏸️ Monitoramento Pausado: \"{path_short}\"",
                text_color="#f59e0b"
            )
        else:
            self.lbl_mon_status.configure(
                text="Status: ⏹️ Parado - Nenhuma pasta selecionada",
                text_color="#f59e0b"
            )

        # 2. Status do Painel Web & Botão Dinâmico
        web_manager = getattr(self.controller, "web_app_manager", None)
        is_web_running = False
        if web_manager:
            is_web_running = bool(getattr(web_manager, "is_running", False))

        if is_web_running:
            self.lbl_web_status.configure(
                text="Status: 🟢 Online — http://127.0.0.1:8000",
                text_color="#4ade80"
            )
            self.btn_web_toggle.configure(
                text="⛔ Parar Servidor Web",
                fg_color="#27272a", hover_color="#3f3f46",
                border_color="#991b1b", border_width=1,
                text_color="#f87171"
            )
            self.btn_reopen_web.pack(before=self.btn_exit_app, fill="x", pady=2)
        else:
            self.lbl_web_status.configure(
                text="Status: 🔴 Offline (Servidor Web Desligado)",
                text_color="#ef4444"
            )
            self.btn_web_toggle.configure(
                text="🌐 Iniciar & Abrir Painel Web",
                fg_color="#0d9488", hover_color="#0f766e",
                border_color="#0d9488", border_width=1,
                text_color="#ffffff"
            )
            self.btn_reopen_web.pack_forget()

        # 3. IA Ollama
        use_llm = getattr(self.controller, "use_llm", False)
        if use_llm:
            self.lbl_ai_status.configure(
                text="Modo: 🟢 IA Local (Ollama) Habilitado",
                text_color="#10b981"
            )
        else:
            self.lbl_ai_status.configure(
                text="Modo: ⚡ Processamento Ultra-Rápido (Regex / Sem IA)",
                text_color="#f59e0b"
            )

        # 4. Métricas Rápidas
        total_folder = getattr(self.controller, "total_files_in_folder", 0)
        self.val_total_folder.configure(text=str(total_folder))

        try:
            all_reports = self.controller.db_repo.get_all()
            llm_cnt = sum(1 for r in all_reports if ("Ollama" in (getattr(r, "extraction_method", "") or "") or "LLM" in (getattr(r, "extraction_method", "") or "")) and "Sem IA" not in (getattr(r, "extraction_method", "") or ""))
            regex_cnt = sum(1 for r in all_reports if "Regex" in (getattr(r, "extraction_method", "") or "") or "Sem IA" in (getattr(r, "extraction_method", "") or ""))
            self.val_lidos_llm.configure(text=str(llm_cnt))
            self.val_lidos_regex.configure(text=str(regex_cnt))
        except Exception:
            self.val_lidos_llm.configure(text="0")
            self.val_lidos_regex.configure(text="0")
