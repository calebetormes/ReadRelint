from pathlib import Path
import customtkinter as ctk

class ReportTab(ctk.CTkFrame):
    """
    Componente visual que representa a aba 'Relatórios de Leitura'.
    Exibe uma tela de carregamento durante a leitura e o relatório estático consolidado quando concluído.
    """
    def __init__(self, master, controller, **kwargs):
        kwargs["fg_color"] = "#18181b"
        super().__init__(master, **kwargs)
        self.controller = controller

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # ---------------------------------------------------------------------
        # 1. Tela de Carregamento (Leitura Ativa)
        # ---------------------------------------------------------------------
        self.loading_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.loading_frame.grid(row=0, column=0, sticky="nsew")
        self.loading_frame.grid_columnconfigure(0, weight=1)
        self.loading_frame.grid_rowconfigure((0, 1), weight=1)

        self.loading_center = ctk.CTkFrame(self.loading_frame, fg_color="transparent")
        self.loading_center.grid(row=0, column=0, rowspan=2)

        self.lbl_loading_title = ctk.CTkLabel(
            self.loading_center, text="⏳ Leitura em Andamento...", 
            font=ctk.CTkFont(size=18, weight="bold"), text_color="#f59e0b"
        )
        self.lbl_loading_title.pack(pady=8)

        self.lbl_loading_subtitle = ctk.CTkLabel(
            self.loading_center,
            text="O processamento de arquivos está ativo.\nO relatório estará disponível quando concluído ou pausado.",
            font=ctk.CTkFont(size=12), text_color="#94a3b8", justify="center"
        )
        self.lbl_loading_subtitle.pack(pady=4)

        # ---------------------------------------------------------------------
        # 2. Tela de Relatório Consolidado
        # ---------------------------------------------------------------------
        self.report_content_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.report_content_frame.grid(row=0, column=0, sticky="nsew")
        
        # Cards de métricas superiores (3 Cards)
        self.cards_frame = ctk.CTkFrame(self.report_content_frame, fg_color="transparent")
        self.cards_frame.pack(fill="x", pady=(8, 4), padx=12)
        for i in range(3):
            self.cards_frame.grid_columnconfigure(i, weight=1)

        def create_card(parent, title, color, col):
            card = ctk.CTkFrame(parent, fg_color="#27272a", corner_radius=8, height=65)
            card.grid(row=0, column=col, padx=3, pady=3, sticky="ew")
            card.pack_propagate(False)
            
            lbl_title = ctk.CTkLabel(card, text=title, font=ctk.CTkFont(size=11, weight="bold"), text_color="#94a3b8")
            lbl_title.pack(pady=(6, 0))
            
            lbl_val = ctk.CTkLabel(card, text="0", font=ctk.CTkFont(size=18, weight="bold"), text_color=color)
            lbl_val.pack(pady=(0, 4))
            return lbl_val

        self.val_total = create_card(self.cards_frame, "📁 Total", "#c084fc", 0)
        self.val_llm = create_card(self.cards_frame, "🟢 Com IA", "#10b981", 1)
        self.val_regex = create_card(self.cards_frame, "⚡ Sem IA", "#f59e0b", 2)

        # Barra Superior de Título
        self.report_toolbar = ctk.CTkFrame(self.report_content_frame, fg_color="transparent")
        self.report_toolbar.pack(fill="x", padx=12, pady=4)

        self.lbl_list_title = ctk.CTkLabel(
            self.report_toolbar, text="📋 RELINTs Lidos & Status",
            font=ctk.CTkFont(size=13, weight="bold"), text_color="#f8fafc"
        )
        self.lbl_list_title.pack(anchor="w")

        # Lista de Arquivos com Scroll
        self.report_scroll = ctk.CTkScrollableFrame(self.report_content_frame, fg_color="transparent")
        self.report_scroll.pack(fill="both", expand=True, padx=12, pady=(4, 8))

        # Esconde o relatório inicialmente
        self.report_content_frame.grid_remove()
        self._report_drawn = False

    def refresh_state(self):
        pending = max(0, self.controller.total_discovered - self.controller.processed_count)
        is_reading = self.controller.is_monitoring and (pending > 0 or self.controller.current_filename != "")

        if is_reading:
            self.report_content_frame.grid_remove()
            self.loading_frame.grid()
        else:
            self.loading_frame.grid_remove()
            self.report_content_frame.grid()
            
            # Recalcula contagens dinâmicas do banco relacional
            all_reports = self.controller.db_repo.get_all()
            llm_cnt = sum(1 for r in all_reports if ("Ollama" in (getattr(r, "extraction_method", "") or "") or "LLM" in (getattr(r, "extraction_method", "") or "")) and "Sem IA" not in (getattr(r, "extraction_method", "") or ""))
            regex_cnt = sum(1 for r in all_reports if "Regex" in (getattr(r, "extraction_method", "") or "") or "Sem IA" in (getattr(r, "extraction_method", "") or ""))
            
            self.val_total.configure(text=str(self.controller.total_files_in_folder))
            self.val_llm.configure(text=str(llm_cnt))
            self.val_regex.configure(text=str(regex_cnt))
            
            self.render_report_list()

    def render_report_list(self):
        for widget in self.report_scroll.winfo_children():
            widget.destroy()

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
                font=ctk.CTkFont(size=12, slant="italic"), text_color="#64748b"
            )
            lbl_empty.pack(pady=30)
            return

        def render_file_card(filename):
            card_frame = ctk.CTkFrame(self.report_scroll, fg_color="#27272a", corner_radius=8)
            card_frame.pack(fill="x", pady=3, padx=2)

            top_row = ctk.CTkFrame(card_frame, fg_color="transparent")
            top_row.pack(fill="x", padx=10, pady=(6, 2))

            short_name = filename if len(filename) <= 32 else filename[:15] + "..." + filename[-14:]
            
            lbl_name = ctk.CTkLabel(top_row, text=short_name, font=ctk.CTkFont(size=11, weight="bold"), text_color="#e2e8f0")
            lbl_name.pack(side="left")

            # Identificação se foi lido com IA ou sem IA (Regex)
            report_db = self.controller.db_repo.get_by_source_file(filename)
            if report_db:
                method_str = str(getattr(report_db, "extraction_method", "") or "")
                is_llm = ("Ollama" in method_str or "LLM" in method_str) and "Sem IA" not in method_str
                method_badge = "🟢 Ollama" if is_llm else "⚡ Regex"
                method_color = "#10b981" if is_llm else "#f59e0b"

                lbl_method = ctk.CTkLabel(top_row, text=method_badge, font=ctk.CTkFont(size=10, weight="bold"), text_color=method_color)
                lbl_method.pack(side="right")
            else:
                lbl_status = ctk.CTkLabel(top_row, text="⏳ Pendente", font=ctk.CTkFont(size=10, weight="bold"), text_color="#94a3b8")
                lbl_status.pack(side="right")

            bot_row = ctk.CTkFrame(card_frame, fg_color="transparent")
            bot_row.pack(fill="x", padx=10, pady=(0, 6))

            pending = max(0, self.controller.total_discovered - self.controller.processed_count)
            is_reading = self.controller.is_monitoring and (pending > 0 or self.controller.current_filename != "")

            import re
            import hashlib
            stem_clean = re.sub(r'[^a-zA-Z0-9_-]', '_', Path(filename).stem)
            stem_clean = re.sub(r'_+', '_', stem_clean).strip('_')
            safe_hash = hashlib.md5(filename.encode('utf-8', errors='replace')).hexdigest()[:8]
            safe_folder_name = f"{stem_clean[:35]}_{safe_hash}"

            media_folder = Path("data/media") / safe_folder_name
            if not media_folder.exists():
                media_folder = Path("data/media") / Path(filename).stem

            image_files = list(media_folder.glob("*.*")) if media_folder.exists() else []

            if image_files:
                btn_photos = ctk.CTkButton(
                    bot_row, text=f"📷 Fotos ({len(image_files)})", height=26,
                    fg_color="#0284c7", hover_color="#0369a1", font=ctk.CTkFont(size=10),
                    command=lambda f=filename, imgs=image_files: self.show_photo_gallery_modal(f, imgs)
                )
                btn_photos.pack(side="left", padx=(0, 4))

            if not is_reading:
                btn_reprocess = ctk.CTkButton(
                    bot_row, text="🔄 Refazer", height=26,
                    fg_color="#d97706", hover_color="#b45309", font=ctk.CTkFont(size=10, weight="bold"),
                    command=lambda f=filename, r=self.controller.active_rule.name: self.controller.reprocess_file_history(f, r)
                )
                btn_reprocess.pack(side="right")

        for f in folder_files:
            render_file_card(f)

    def show_photo_gallery_modal(self, filename: str, image_files: list):
        """Abre uma janela modal CustomTkinter para visualizar as fotos do RELINT."""
        window = ctk.CTkToplevel(self)
        window.title(f"Fotos - {filename}")
        window.geometry("560x440")
        window.grab_set()

        lbl_title = ctk.CTkLabel(
            window, 
            text=f"📷 Fotos & Anexos ({len(image_files)}) — {filename}", 
            font=ctk.CTkFont(size=13, weight="bold")
        )
        lbl_title.pack(pady=8)

        scroll_frame = ctk.CTkScrollableFrame(window)
        scroll_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        from PIL import Image
        for img_path in image_files:
            try:
                pil_img = Image.open(img_path)
                w, h = pil_img.size
                ratio = w / h if h > 0 else 1.0
                thumb_w = 200
                thumb_h = int(thumb_w / ratio) if ratio > 0 else 150
                
                pil_img = pil_img.resize((thumb_w, thumb_h), Image.Resampling.LANCZOS)
                ctk_img = ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=(thumb_w, thumb_h))

                card = ctk.CTkFrame(scroll_frame, fg_color="#27272a", corner_radius=6)
                card.pack(pady=6, padx=6, fill="x")

                img_label = ctk.CTkLabel(card, image=ctk_img, text="")
                img_label.pack(side="left", padx=8, pady=8)

                info_frame = ctk.CTkFrame(card, fg_color="transparent")
                info_frame.pack(side="left", padx=8, pady=8, fill="both", expand=True)

                lbl_fname = ctk.CTkLabel(info_frame, text=img_path.name, font=ctk.CTkFont(size=11, weight="bold"), anchor="w")
                lbl_fname.pack(anchor="w", pady=(0, 2))

                lbl_path = ctk.CTkLabel(info_frame, text=f"Local: {img_path}", font=ctk.CTkFont(size=9), text_color="#94a3b8", anchor="w")
                lbl_path.pack(anchor="w")
            except Exception:
                pass
