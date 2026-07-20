from pathlib import Path
import customtkinter as ctk

class ReportTab(ctk.CTkFrame):
    """
    Componente visual que representa a aba 'Relatórios de Leitura'.
    Exibe uma tela de carregamento durante a leitura e o relatório estático consolidado quando concluído.
    """
    def __init__(self, master, controller, **kwargs):
        super().__init__(master, **kwargs)
        self.controller = controller

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # 1. Tela de Carregamento
        self.loading_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.loading_frame.grid(row=0, column=0, sticky="nsew")
        self.loading_frame.grid_columnconfigure(0, weight=1)
        self.loading_frame.grid_rowconfigure((0, 1), weight=1)

        self.loading_center = ctk.CTkFrame(self.loading_frame, fg_color="transparent")
        self.loading_center.grid(row=0, column=0, rowspan=2)

        self.lbl_loading_title = ctk.CTkLabel(
            self.loading_center, text="⏳ Leitura em Andamento...", 
            font=ctk.CTkFont(size=20, weight="bold"), text_color="orange"
        )
        self.lbl_loading_title.pack(pady=10)

        self.lbl_loading_subtitle = ctk.CTkLabel(
            self.loading_center,
            text="O processamento de arquivos pela IA está ativo.\nO relatório detalhado estará disponível assim que o monitoramento for parado ou concluído.",
            font=ctk.CTkFont(size=13), text_color="#94a3b8", justify="center"
        )
        self.lbl_loading_subtitle.pack(pady=5)

        # 2. Tela de Relatório
        self.report_content_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.report_content_frame.grid(row=0, column=0, sticky="nsew")
        
        # Cards de métricas
        self.cards_frame = ctk.CTkFrame(self.report_content_frame, fg_color="transparent")
        self.cards_frame.pack(fill="x", pady=(10, 5), padx=20)
        for i in range(3):
            self.cards_frame.grid_columnconfigure(i, weight=1)

        def create_card(parent, title, color, row, col):
            card = ctk.CTkFrame(parent, fg_color="#1e293b", corner_radius=8, height=80)
            card.grid(row=row, column=col, padx=5, pady=5, sticky="ew")
            card.pack_propagate(False)
            
            lbl_title = ctk.CTkLabel(card, text=title, font=ctk.CTkFont(size=11, weight="bold"), text_color="#94a3b8")
            lbl_title.pack(pady=(10, 0))
            
            lbl_val = ctk.CTkLabel(card, text="0", font=ctk.CTkFont(size=24, weight="bold"), text_color=color)
            lbl_val.pack(pady=(0, 5))
            return lbl_val

        self.val_total = create_card(self.cards_frame, "Total na Pasta", "#c084fc", 0, 0)
        self.val_skipped = create_card(self.cards_frame, "Lidos Anteriormente", "#06b6d4", 0, 1)
        self.val_confirmed = create_card(self.cards_frame, "Homicídios (Sessão)", "#4ade80", 0, 2)
        
        self.val_pref = create_card(self.cards_frame, "Descartes Pré-Filtro", "#fb923c", 1, 0)
        self.val_llmf = create_card(self.cards_frame, "Descartes IA", "#f87171", 1, 1)
        self.val_proc_sess = create_card(self.cards_frame, "Total Processados", "#60a5fa", 1, 2)

        # Barra de Busca e Botão de Limpeza
        self.report_toolbar = ctk.CTkFrame(self.report_content_frame, fg_color="transparent")
        self.report_toolbar.pack(fill="x", padx=20, pady=5)
        
        self.report_search_entry = ctk.CTkEntry(self.report_toolbar, placeholder_text="Buscar arquivo...", width=300)
        self.report_search_entry.pack(side="left", fill="x", expand=True)
        self.report_search_entry.bind("<KeyRelease>", lambda e: self.filter_history_ui())

        self.btn_clear_history = ctk.CTkButton(
            self.report_toolbar, text="Limpar Tudo", width=100, 
            fg_color="#b91c1c", hover_color="#991b1b",
            command=self.controller.clear_all_history
        )
        self.btn_clear_history.pack(side="right", padx=10)

        # Lista de Arquivos
        self.report_scroll = ctk.CTkScrollableFrame(self.report_content_frame, fg_color="transparent")
        self.report_scroll.pack(fill="both", expand=True, padx=20, pady=10)

        # Esconde o relatório inicialmente
        self.report_content_frame.grid_remove()
        self._report_drawn = False

    def refresh_state(self):
        pending = max(0, self.controller.total_discovered - self.controller.processed_count)
        is_reading = self.controller.is_monitoring and (pending > 0 or self.controller.current_filename != "")

        if is_reading:
            self.report_content_frame.grid_remove()
            self.loading_frame.grid()
            self._report_drawn = False
        else:
            self.loading_frame.grid_remove()
            self.report_content_frame.grid()
            
            self.val_total.configure(text=str(self.controller.total_files_in_folder))
            self.val_skipped.configure(text=str(self.controller.skipped_count))
            self.val_confirmed.configure(text=str(self.controller.session_confirmed_count))
            self.val_pref.configure(text=str(self.controller.session_pre_filtered_count))
            self.val_llmf.configure(text=str(self.controller.session_post_llm_filtered_count))
            self.val_proc_sess.configure(text=str(self.controller.processed_count))
            
            if not self._report_drawn:
                self.filter_history_ui()
                self._report_drawn = True

    def filter_history_ui(self):
        for widget in self.report_scroll.winfo_children():
            widget.destroy()

        query = self.report_search_entry.get().strip().lower()
        records = self.controller.processed_registry.get_all_records()

        folder_files = []
        if self.controller.monitoring_path:
            try:
                folder_files = sorted([p.name for p in Path(self.controller.monitoring_path).glob("*.pdf")])
            except Exception:
                pass

        if not folder_files:
            lbl_empty = ctk.CTkLabel(
                self.report_scroll, text="Nenhum PDF encontrado na pasta monitorada.",
                font=ctk.CTkFont(size=13, slant="italic"), text_color="#64748b"
            )
            lbl_empty.pack(pady=40)
            return

        current_session_files = []
        previous_session_files = []

        for filename in folder_files:
            if query and query not in filename.lower():
                continue
            
            if filename in self.controller.session_skipped_files:
                previous_session_files.append(filename)
            else:
                current_session_files.append(filename)

        def render_file_card(filename, is_previous):
            status_color = "#94a3b8"
            status_text = "Não Processado (Pendente)"
            
            if is_previous:
                status_text = "Lido em Sessão Anterior (Pulado)"
                status_color = "#06b6d4"
            else:
                file_record = records.get(filename, {}).get(self.controller.active_rule.name)
                if file_record == "confirmed":
                    status_text = "Confirmado (Homicídio Salvo)"
                    status_color = "#4ade80"
                elif file_record == "filtered_pre_llm":
                    status_text = "Descartado no Pré-Filtro"
                    status_color = "#fb923c"
                elif file_record == "filtered_post_llm":
                    status_text = "Descartado pela LLM"
                    status_color = "#f87171"

            row_frame = ctk.CTkFrame(self.report_scroll, fg_color="#1e293b", height=45)
            row_frame.pack(fill="x", pady=4, padx=5)
            row_frame.pack_propagate(False)

            short_name = filename if len(filename) <= 42 else filename[:39] + "..."
            
            lbl_name = ctk.CTkLabel(row_frame, text=short_name, font=ctk.CTkFont(size=12, weight="bold"), text_color="#e2e8f0")
            lbl_name.pack(side="left", padx=10, pady=10)

            lbl_status = ctk.CTkLabel(row_frame, text=status_text, font=ctk.CTkFont(size=11, weight="bold"), text_color=status_color)
            lbl_status.pack(side="left", padx=25, pady=10)

            pending = max(0, self.controller.total_discovered - self.controller.processed_count)
            is_reading = self.controller.is_monitoring and (pending > 0 or self.controller.current_filename != "")
            
            if not is_reading:
                btn_reprocess = ctk.CTkButton(
                    row_frame, text="Reprocessar", width=85, height=24,
                    fg_color="#334155", hover_color="#475569", font=ctk.CTkFont(size=11),
                    command=lambda f=filename, r=self.controller.active_rule.name: self.controller.reprocess_file_history(f, r)
                )
                btn_reprocess.pack(side="right", padx=10, pady=10)

        # Renderizar Sessão Atual
        if current_session_files:
            lbl_curr = ctk.CTkLabel(
                self.report_scroll, text="📌 Arquivos da Sessão Atual / Fila",
                font=ctk.CTkFont(size=14, weight="bold"), text_color="#cbd5e1"
            )
            lbl_curr.pack(anchor="w", pady=(10, 5), padx=5)
            for f in current_session_files:
                render_file_card(f, is_previous=False)

        # Renderizar Leituras Anteriores
        if previous_session_files:
            lbl_prev = ctk.CTkLabel(
                self.report_scroll, text="📂 Lidos em Sessões Anteriores (Pulados)",
                font=ctk.CTkFont(size=14, weight="bold"), text_color="#94a3b8"
            )
            lbl_prev.pack(anchor="w", pady=(20, 5), padx=5)
            for f in previous_session_files:
                render_file_card(f, is_previous=True)
