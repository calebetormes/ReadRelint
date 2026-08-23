import sys
import time
import subprocess
from pathlib import Path

# Adiciona o diretório raiz ao sys.path para garantir imports absolutos corretos
project_root = Path(__file__).resolve().parents[2]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QTabWidget,
    QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTextEdit, QLineEdit, QProgressBar, QMessageBox,
    QFileDialog, QScrollArea, QFrame, QCheckBox,
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QObject
from PyQt6.QtGui import QTextCursor, QCloseEvent

from desktop.controllers.main_controller import MainController
from backend.api.dependencies import get_main_controller

# --- Constantes de Cores e Estilo ---
GREEN = "#10b981"
ORANGE = "#d97706"
RED = "#ef4444"
GREY = "#a3a3a3"
BG = "#121212"
CARD = "#1e1e1e"
BORDER = "#333333"
WHITE = "#ffffff"

QSS = f"""
QMainWindow, QWidget {{
    background-color: {BG};
    color: {WHITE};
    font-family: 'Segoe UI', 'Inter', sans-serif;
    font-size: 13px;
}}
QTabWidget::pane {{
    border: 1px solid {BORDER};
    border-radius: 8px;
    background: {BG};
}}
QTabBar::tab {{
    background: {CARD};
    color: {GREY};
    padding: 10px 20px;
    border: 1px solid {BORDER};
    border-bottom: none;
    border-radius: 6px 6px 0 0;
    min-width: 120px;
    font-weight: 600;
}}
QTabBar::tab:selected {{
    background: {BG};
    color: {WHITE};
    border-bottom: 2px solid {GREEN};
}}
QTabBar::tab:hover {{
    color: {WHITE};
    background: #2a2a2a;
}}
QPushButton {{
    background-color: {GREEN};
    color: {WHITE};
    border: none;
    border-radius: 6px;
    padding: 8px 16px;
    font-weight: 600;
    font-size: 13px;
}}
QPushButton:hover {{
    background-color: #0ea272;
}}
QPushButton:pressed {{
    background-color: #059669;
}}
QLineEdit {{
    background-color: {CARD};
    border: 1px solid {BORDER};
    border-radius: 6px;
    padding: 8px;
    color: {WHITE};
}}
QTextEdit {{
    background-color: #0d0d0d;
    border: 1px solid {BORDER};
    border-radius: 8px;
    color: #a3a3a3;
    font-family: Consolas, monospace;
    font-size: 12px;
    padding: 8px;
}}
QProgressBar {{
    border: 2px solid {BORDER};
    border-radius: 8px;
    background-color: {CARD};
    color: {WHITE};
    text-align: center;
    font-weight: 600;
    height: 22px;
}}
QProgressBar::chunk {{
    border-radius: 6px;
    background-color: {GREEN};
}}
QScrollArea {{
    border: none;
    background: transparent;
}}
QScrollBar:vertical {{
    background: {CARD};
    width: 8px;
    border-radius: 4px;
}}
QScrollBar::handle:vertical {{
    background: {BORDER};
    border-radius: 4px;
    min-height: 20px;
}}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0px;
}}
QCheckBox {{
    color: {WHITE};
    spacing: 8px;
}}
QCheckBox::indicator {{
    width: 18px;
    height: 18px;
    border: 2px solid {BORDER};
    border-radius: 4px;
    background: {CARD};
}}
QCheckBox::indicator:checked {{
    background-color: {GREEN};
    border-color: {GREEN};
}}
QFrame[card="true"] {{
    background-color: {CARD};
    border: 1px solid {BORDER};
    border-radius: 8px;
}}
"""


class LogEmitter(QObject):
    """Emissor para transmissão thread-safe de mensagens de log para a UI."""
    message_received = pyqtSignal(str)


def make_card(layout: QVBoxLayout | QHBoxLayout) -> QFrame:
    """Cria um QFrame estilizado como card de dashboard."""
    card = QFrame()
    card.setProperty("card", True)
    card.setLayout(layout)
    return card


class MainWindow(QMainWindow):
    """Janela principal do Painel de Controle ReadRelint em PyQt6."""

    def __init__(self, controller: MainController):
        super().__init__()
        self.controller = controller
        self.frontend_process = None

        # Configuração de Logs Thread-Safe
        self._log_emitter = LogEmitter()
        self._log_emitter.message_received.connect(self._append_log)

        self.setWindowTitle("ReadRelint • Painel de Controle")
        self.setMinimumSize(860, 680)
        self.resize(920, 720)

        # Injeta callbacks no controller compartilhado
        self.controller.on_log_message = self._emit_log
        self.controller.on_stats_updated = self._on_stats_updated

        # Constrói UI e aplica estilo
        self._build_ui()
        self.setStyleSheet(QSS)

        # Timer para atualização periódica de status dos serviços
        self._status_timer = QTimer(self)
        self._status_timer.timeout.connect(self._update_services_status)
        self._status_timer.start(2000)

        # Inicializa estado visual inicial
        self._update_services_status()
        self._update_etl_stats()
        self._emit_log("Painel de controle iniciado com sucesso.")

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        root_layout = QVBoxLayout(central)
        root_layout.setContentsMargins(12, 12, 12, 12)

        tabs = QTabWidget()
        tabs.addTab(self._build_tab_services(), "⚡  Serviços")
        tabs.addTab(self._build_tab_etl(), "📊  ETL / Monitor")
        tabs.addTab(self._build_tab_logs(), "🖥  Logs")
        tabs.addTab(self._build_tab_reports(), "📋  Relatórios")
        tabs.currentChanged.connect(self._on_tab_changed)

        root_layout.addWidget(tabs)

    # --- Aba 1: Serviços ---

    def _build_tab_services(self) -> QWidget:
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)

        title = QLabel("Gerenciamento de Serviços")
        title.setStyleSheet(f"font-size: 16px; font-weight: 700; color: {WHITE};")
        layout.addWidget(title)
        layout.addWidget(self._make_divider())

        # Cards lado a lado: Backend e Frontend
        row = QHBoxLayout()
        row.setSpacing(16)
        row.addWidget(self._build_backend_card())
        row.addWidget(self._build_frontend_card())
        layout.addLayout(row)

        # Card: Ollama / LLM
        layout.addWidget(self._build_llm_card())

        # Seletor de Diretório
        layout.addWidget(self._make_divider())
        layout.addLayout(self._build_dir_picker())

        layout.addStretch()
        return tab

    def _build_backend_card(self) -> QFrame:
        vbox = QVBoxLayout()
        vbox.setContentsMargins(16, 16, 16, 16)
        vbox.setSpacing(10)

        title = QLabel("Servidor Web (FastAPI Backend)")
        title.setStyleSheet(f"font-weight: 700; color: {WHITE};")

        self._icon_backend = QLabel("●")
        self._icon_backend.setStyleSheet(f"color: {GREY}; font-size: 14px;")
        self._lbl_backend_status = QLabel("Parado")
        self._lbl_backend_status.setStyleSheet(f"color: {GREY}; font-weight: 700;")

        status_row = QHBoxLayout()
        status_row.addWidget(self._icon_backend)
        status_row.addWidget(self._lbl_backend_status)
        status_row.addStretch()

        self._btn_backend = QPushButton("Iniciar Servidor Web")
        self._btn_backend.setFixedHeight(36)
        self._btn_backend.clicked.connect(self._toggle_backend)

        vbox.addWidget(title)
        vbox.addLayout(status_row)
        vbox.addWidget(self._btn_backend)

        return make_card(vbox)

    def _build_frontend_card(self) -> QFrame:
        vbox = QVBoxLayout()
        vbox.setContentsMargins(16, 16, 16, 16)
        vbox.setSpacing(10)

        title = QLabel("Interface Web (SvelteKit Frontend)")
        title.setStyleSheet(f"font-weight: 700; color: {WHITE};")

        self._icon_frontend = QLabel("●")
        self._icon_frontend.setStyleSheet(f"color: {GREY}; font-size: 14px;")
        self._lbl_frontend_status = QLabel("Parado")
        self._lbl_frontend_status.setStyleSheet(f"color: {GREY}; font-weight: 700;")

        status_row = QHBoxLayout()
        status_row.addWidget(self._icon_frontend)
        status_row.addWidget(self._lbl_frontend_status)
        status_row.addStretch()

        self._btn_frontend = QPushButton("Iniciar Frontend")
        self._btn_frontend.setFixedHeight(36)
        self._btn_frontend.clicked.connect(self._toggle_frontend)

        vbox.addWidget(title)
        vbox.addLayout(status_row)
        vbox.addWidget(self._btn_frontend)

        return make_card(vbox)

    def _build_llm_card(self) -> QFrame:
        vbox = QVBoxLayout()
        vbox.setContentsMargins(16, 16, 16, 16)
        vbox.setSpacing(10)

        title = QLabel("Motor Cognitivo & LLM")
        title.setStyleSheet(f"font-weight: 700; color: {WHITE};")

        self._icon_ollama = QLabel("●")
        self._icon_ollama.setStyleSheet(f"color: {GREY}; font-size: 14px;")
        self._lbl_ollama_status = QLabel("Testando...")
        self._lbl_ollama_status.setStyleSheet(f"color: {GREY}; font-weight: 700;")

        status_row = QHBoxLayout()
        status_row.addWidget(QLabel("Serviço Ollama Local:"))
        status_row.addWidget(self._icon_ollama)
        status_row.addWidget(self._lbl_ollama_status)
        status_row.addStretch()

        self._chk_llm = QCheckBox("Modo IA (Ollama)")
        self._chk_llm.setChecked(self.controller.use_llm)
        self._chk_llm.stateChanged.connect(
            lambda state: self._toggle_llm(state == Qt.CheckState.Checked.value or state == 2)
        )

        vbox.addWidget(title)
        vbox.addLayout(status_row)
        vbox.addWidget(self._chk_llm)

        return make_card(vbox)

    def _build_dir_picker(self) -> QHBoxLayout:
        row = QHBoxLayout()
        self._txt_path = QLineEdit(
            self.controller.monitoring_path or "Nenhuma pasta selecionada"
        )
        self._txt_path.setReadOnly(True)
        self._txt_path.setPlaceholderText("Diretório de RELINTs Monitorado")

        btn = QPushButton("📁  Selecionar Pasta")
        btn.setFixedWidth(160)
        btn.clicked.connect(self._pick_directory)

        row.addWidget(self._txt_path)
        row.addWidget(btn)
        return row

    # --- Aba 2: ETL / Monitor ---

    def _build_tab_etl(self) -> QWidget:
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)

        title = QLabel("Progresso da Leitura e ETL")
        title.setStyleSheet(f"font-size: 16px; font-weight: 700; color: {WHITE};")
        layout.addWidget(title)
        layout.addWidget(self._make_divider())

        # Cards de progresso
        progress_row = QHBoxLayout()
        progress_row.setSpacing(16)
        progress_row.addWidget(self._build_general_progress_card())
        progress_row.addWidget(self._build_session_progress_card())
        layout.addLayout(progress_row)

        # Arquivo ativo
        active_vbox = QVBoxLayout()
        active_vbox.setContentsMargins(16, 12, 16, 12)
        active_vbox.setSpacing(4)
        lbl_active_title = QLabel("Arquivo Ativo")
        lbl_active_title.setStyleSheet(f"color: {GREY}; font-size: 12px;")
        self._lbl_current = QLabel("Aguardando início...")
        self._lbl_current.setStyleSheet(f"color: {GREEN}; font-weight: 700; font-size: 14px;")
        active_vbox.addWidget(lbl_active_title)
        active_vbox.addWidget(self._lbl_current)
        layout.addWidget(make_card(active_vbox))

        # Botões de controle
        btn_row = QHBoxLayout()
        self._btn_monitoring = QPushButton("▶  Iniciar Monitoramento")
        self._btn_monitoring.setFixedHeight(38)
        self._btn_monitoring.clicked.connect(self._toggle_etl_monitoring)

        self._btn_reset = QPushButton("↺  Resetar Banco & Re-ler Tudo")
        self._btn_reset.setFixedHeight(38)
        self._btn_reset.setFixedWidth(240)
        self._btn_reset.setStyleSheet(
            f"background-color: transparent; color: {RED}; border: 1px solid {RED}; border-radius: 6px; font-weight: 600;"
        )
        self._btn_reset.clicked.connect(self._reset_etl_data)

        btn_row.addWidget(self._btn_monitoring)
        btn_row.addWidget(self._btn_reset)
        layout.addLayout(btn_row)

        layout.addStretch()
        return tab

    def _build_general_progress_card(self) -> QFrame:
        vbox = QVBoxLayout()
        vbox.setContentsMargins(16, 16, 16, 16)
        vbox.setSpacing(10)

        title = QLabel("Progresso Geral da Pasta")
        title.setStyleSheet(f"font-weight: 700; color: {WHITE};")

        self._bar_general = QProgressBar()
        self._bar_general.setRange(0, 100)
        self._bar_general.setValue(0)
        self._bar_general.setFormat("%p%")

        self._lbl_count_general = QLabel("0 / 0 PDFs analisados")
        self._lbl_count_general.setStyleSheet(f"color: {GREY}; font-size: 12px;")

        vbox.addWidget(title)
        vbox.addWidget(self._bar_general)
        vbox.addWidget(self._lbl_count_general)

        return make_card(vbox)

    def _build_session_progress_card(self) -> QFrame:
        vbox = QVBoxLayout()
        vbox.setContentsMargins(16, 16, 16, 16)
        vbox.setSpacing(10)

        title = QLabel("Progresso da Fila Ativa")
        title.setStyleSheet(f"font-weight: 700; color: {WHITE};")

        self._bar_session = QProgressBar()
        self._bar_session.setRange(0, 100)
        self._bar_session.setValue(0)
        self._bar_session.setFormat("%p%")
        self._bar_session.setStyleSheet(
            f"QProgressBar::chunk {{ border-radius: 6px; background-color: {ORANGE}; }}"
        )

        self._lbl_count_session = QLabel("0 / 0 Novos nesta sessão")
        self._lbl_count_session.setStyleSheet(f"color: {GREY}; font-size: 12px;")

        vbox.addWidget(title)
        vbox.addWidget(self._bar_session)
        vbox.addWidget(self._lbl_count_session)

        return make_card(vbox)

    # --- Aba 3: Logs ---

    def _build_tab_logs(self) -> QWidget:
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        header = QHBoxLayout()
        title = QLabel("Terminal de Logs do Sistema")
        title.setStyleSheet(f"font-size: 16px; font-weight: 700; color: {WHITE};")

        btn_clear = QPushButton("🗑  Limpar")
        btn_clear.setFixedWidth(100)
        btn_clear.setFixedHeight(32)
        btn_clear.setStyleSheet(
            f"background-color: transparent; color: {RED}; border: 1px solid {RED}; border-radius: 6px; font-weight: 600;"
        )
        btn_clear.clicked.connect(self._clear_logs)

        header.addWidget(title)
        header.addStretch()
        header.addWidget(btn_clear)

        self._log_view = QTextEdit()
        self._log_view.setReadOnly(True)

        layout.addLayout(header)
        layout.addWidget(self._make_divider())
        layout.addWidget(self._log_view)

        return tab

    # --- Aba 4: Relatórios ---

    def _build_tab_reports(self) -> QWidget:
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        header = QHBoxLayout()
        title = QLabel("RELINTs Processados no Banco")
        title.setStyleSheet(f"font-size: 16px; font-weight: 700; color: {WHITE};")

        btn_refresh = QPushButton("↻  Atualizar")
        btn_refresh.setFixedWidth(110)
        btn_refresh.setFixedHeight(32)
        btn_refresh.clicked.connect(self._update_reports_list)

        header.addWidget(title)
        header.addStretch()
        header.addWidget(btn_refresh)

        layout.addLayout(header)
        layout.addWidget(self._make_divider())

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self._reports_container = QWidget()
        self._reports_layout = QVBoxLayout(self._reports_container)
        self._reports_layout.setSpacing(8)
        self._reports_layout.addStretch()

        scroll.setWidget(self._reports_container)
        layout.addWidget(scroll)

        return tab

    # --- Helpers de Layout ---

    def _make_divider(self) -> QFrame:
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setStyleSheet(f"color: {BORDER};")
        return line

    # --- Lógica de Operações ---

    def _toggle_backend(self):
        if self.controller.web_app_manager.is_running:
            self.controller.close_web_dashboard()
            self._emit_log("⛔ Servidor FastAPI parado pelo usuário.")
        else:
            self.controller.open_web_dashboard()
            self._emit_log("🌐 Servidor FastAPI iniciado.")
        self._update_services_status()

    def _toggle_frontend(self):
        if self.frontend_process and self.frontend_process.poll() is None:
            try:
                subprocess.call(
                    ["taskkill", "/F", "/T", "/PID", str(self.frontend_process.pid)],
                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
                )
                self.frontend_process = None
                self._emit_log("⛔ Servidor Frontend SvelteKit parado.")
            except Exception as exc:
                self._emit_log(f"⚠️ Erro ao encerrar Frontend: {exc}")
        else:
            frontend_dir = str(project_root / "frontend")
            self._emit_log("🚀 Iniciando dev server do SvelteKit...")
            try:
                self.frontend_process = subprocess.Popen(
                    "npm run dev",
                    cwd=frontend_dir,
                    shell=True,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    creationflags=subprocess.CREATE_NO_WINDOW
                )
                self._emit_log("🟢 Servidor Frontend SvelteKit ativo em http://localhost:5173")
            except Exception as exc:
                self._emit_log(f"⚠️ Falha ao iniciar Frontend: {exc}")
        self._update_services_status()

    def _toggle_llm(self, value: bool):
        success = self.controller.set_use_llm(value)
        if not success:
            self._chk_llm.setChecked(False)

    def _pick_directory(self):
        path = QFileDialog.getExistingDirectory(
            self,
            "Selecione a Pasta dos RELINTs",
            str(project_root),
        )
        if path:
            self.controller.set_monitoring_path(path)
            self._txt_path.setText(path)
            self._emit_log(f"📁 Pasta selecionada: {path}")
            self._update_etl_stats()

    def _toggle_etl_monitoring(self):
        if not self.controller.monitoring_path or not Path(self.controller.monitoring_path).exists():
            self._emit_log("⚠️ Selecione uma pasta válida antes de iniciar o monitoramento.")
            return

        if self.controller.is_monitoring:
            self.controller.stop_monitoring()
        else:
            self.controller.start_monitoring()
        self._update_etl_stats()

    def _reset_etl_data(self):
        reply = QMessageBox.question(
            self,
            "Aviso de Reset Completo",
            "Isso limpará permanentemente o banco relacional, os contatos extraídos e as mídias.\n\nDeseja prosseguir?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.Cancel,
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.controller.reset_and_reprocess_all()

    # --- Atualização de Estados Visuais ---

    def _update_services_status(self):
        btn_style_green = (
            f"background-color: {GREEN}; color: white; border-radius: 6px; padding: 8px 16px; font-weight: 600;"
        )
        btn_style_red = (
            f"background-color: {RED}; color: white; border-radius: 6px; padding: 8px 16px; font-weight: 600;"
        )

        # Backend Status
        if self.controller.web_app_manager.is_running:
            self._icon_backend.setStyleSheet(f"color: {GREEN}; font-size: 14px;")
            self._lbl_backend_status.setText("Rodando")
            self._lbl_backend_status.setStyleSheet(f"color: {GREEN}; font-weight: 700;")
            self._btn_backend.setText("Parar Servidor Web")
            self._btn_backend.setStyleSheet(btn_style_red)
        else:
            self._icon_backend.setStyleSheet(f"color: {GREY}; font-size: 14px;")
            self._lbl_backend_status.setText("Parado")
            self._lbl_backend_status.setStyleSheet(f"color: {GREY}; font-weight: 700;")
            self._btn_backend.setText("Iniciar Servidor Web")
            self._btn_backend.setStyleSheet(btn_style_green)

        # Frontend Status
        if self.frontend_process and self.frontend_process.poll() is None:
            self._icon_frontend.setStyleSheet(f"color: {GREEN}; font-size: 14px;")
            self._lbl_frontend_status.setText("Rodando")
            self._lbl_frontend_status.setStyleSheet(f"color: {GREEN}; font-weight: 700;")
            self._btn_frontend.setText("Parar Frontend")
            self._btn_frontend.setStyleSheet(btn_style_red)
        else:
            self._icon_frontend.setStyleSheet(f"color: {GREY}; font-size: 14px;")
            self._lbl_frontend_status.setText("Parado")
            self._lbl_frontend_status.setStyleSheet(f"color: {GREY}; font-weight: 700;")
            self._btn_frontend.setText("Iniciar Frontend")
            self._btn_frontend.setStyleSheet(btn_style_green)

        # Ollama Status
        if hasattr(self.controller.llm_processor, "check_connection"):
            try:
                is_ok, _ = self.controller.llm_processor.check_connection()
                if is_ok:
                    self._icon_ollama.setStyleSheet(f"color: {GREEN}; font-size: 14px;")
                    self._lbl_ollama_status.setText("Online")
                    self._lbl_ollama_status.setStyleSheet(f"color: {GREEN}; font-weight: 700;")
                else:
                    self._icon_ollama.setStyleSheet(f"color: {RED}; font-size: 14px;")
                    self._lbl_ollama_status.setText("Offline")
                    self._lbl_ollama_status.setStyleSheet(f"color: {RED}; font-weight: 700;")
            except Exception:
                pass

    def _update_etl_stats(self):
        total_folder = getattr(self.controller, "total_files_in_folder", 0)
        skipped = getattr(self.controller, "skipped_count", 0)
        processed = getattr(self.controller, "processed_count", 0)

        read_total = min(skipped + processed, total_folder)
        general_percent = int((read_total / total_folder) * 100) if total_folder > 0 else 0
        self._bar_general.setValue(general_percent)
        self._lbl_count_general.setText(f"{read_total} / {total_folder} PDFs analisados")

        discovered = getattr(self.controller, "total_discovered", 0)
        session_percent = int((processed / discovered) * 100) if discovered > 0 else 0
        self._bar_session.setValue(session_percent)
        self._lbl_count_session.setText(f"{processed} / {discovered} Novos nesta sessão")

        # Arquivo ativo
        if self.controller.current_filename:
            self._lbl_current.setText(f"📄 Lendo: {self.controller.current_filename}")
            self._lbl_current.setStyleSheet(f"color: {ORANGE}; font-weight: 700; font-size: 14px;")
        else:
            if self.controller.is_monitoring:
                self._lbl_current.setText("🟢 Aguardando novos arquivos...")
                self._lbl_current.setStyleSheet(f"color: {GREEN}; font-weight: 700; font-size: 14px;")
            else:
                self._lbl_current.setText("⏸️ Fila de leitura pausada")
                self._lbl_current.setStyleSheet(f"color: {GREY}; font-weight: 700; font-size: 14px;")

        # Botão de monitoramento
        btn_style_green = (
            f"background-color: {GREEN}; color: white; border-radius: 6px; padding: 8px 16px; font-weight: 600;"
        )
        btn_style_orange = (
            f"background-color: {ORANGE}; color: white; border-radius: 6px; padding: 8px 16px; font-weight: 600;"
        )
        if self.controller.is_monitoring:
            self._btn_monitoring.setText("⏸  Pausar Monitoramento")
            self._btn_monitoring.setStyleSheet(btn_style_orange)
        else:
            self._btn_monitoring.setText("▶  Iniciar Monitoramento")
            self._btn_monitoring.setStyleSheet(btn_style_green)

    def _update_reports_list(self):
        while self._reports_layout.count() > 1:
            item = self._reports_layout.takeAt(0)
            if item is not None:
                widget = item.widget()
                if widget is not None:
                    widget.deleteLater()

        try:
            reports = self.controller.db_repo.get_all()
            for rpt in reports:
                is_llm = (
                    "Ollama" in getattr(rpt, "extraction_method", "")
                    or "IA" in getattr(rpt, "extraction_method", "")
                )
                badge_color = GREEN if is_llm else RED
                badge_text = "IA" if is_llm else "Regex"

                card_layout = QHBoxLayout()
                card_layout.setContentsMargins(12, 10, 12, 10)

                info_col = QVBoxLayout()
                lbl_file = QLabel(rpt.source_file)
                lbl_file.setStyleSheet("font-weight: 700; font-size: 13px;")
                lbl_subject = QLabel(rpt.subject or "Sem Assunto")
                lbl_subject.setStyleSheet(f"color: {GREY}; font-size: 12px;")
                info_col.addWidget(lbl_file)
                info_col.addWidget(lbl_subject)

                badge = QLabel(badge_text)
                badge.setStyleSheet(
                    f"background-color: {badge_color}; color: white; border-radius: 4px;"
                    " padding: 2px 8px; font-size: 11px; font-weight: 700;"
                )
                badge.setFixedWidth(52)
                badge.setAlignment(Qt.AlignmentFlag.AlignCenter)

                btn_reprocess = QPushButton("Repr.")
                btn_reprocess.setToolTip("Reprocessar arquivo")
                btn_reprocess.setFixedSize(54, 32)
                btn_reprocess.setStyleSheet(
                    f"background-color: transparent; color: {GREEN}; border: 1px solid {GREEN}; border-radius: 6px; font-weight: 700;"
                )
                filename = rpt.source_file
                btn_reprocess.clicked.connect(
                    lambda _, f=filename: self.controller.reprocess_file_history(
                        f, self.controller.active_rule.name
                    )
                )

                card_layout.addLayout(info_col, stretch=1)
                card_layout.addWidget(badge)
                card_layout.addWidget(btn_reprocess)

                card = QFrame()
                card.setProperty("card", True)
                card.setLayout(card_layout)
                self._reports_layout.insertWidget(self._reports_layout.count() - 1, card)

        except Exception as exc:
            err_label = QLabel(f"Erro ao carregar relatórios: {exc}")
            err_label.setStyleSheet(f"color: {RED};")
            self._reports_layout.insertWidget(0, err_label)

    # --- Logs ---

    def _emit_log(self, message: str):
        """Emite o log através do sinal Qt thread-safe."""
        self._log_emitter.message_received.emit(message)

    def _append_log(self, message: str):
        """Atualiza a caixa de texto de logs na thread da UI."""
        now = time.strftime("%H:%M:%S")
        self._log_view.append(f"[{now}] {message}")
        self._log_view.moveCursor(QTextCursor.MoveOperation.End)

    def _clear_logs(self):
        self._log_view.clear()

    # --- Callbacks do Controller ---

    def _on_stats_updated(self):
        self._update_etl_stats()

    def _on_tab_changed(self, index: int):
        if index == 3:
            self._update_reports_list()

    def closeEvent(self, a0: QCloseEvent | None):
        """Finaliza processos filhos ao fechar a janela."""
        self._status_timer.stop()
        if self.frontend_process and self.frontend_process.poll() is None:
            subprocess.call(
                ["taskkill", "/F", "/T", "/PID", str(self.frontend_process.pid)],
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
            )
        super().closeEvent(a0)


def run():
    """Ponto de entrada para execução da aplicação PyQt6."""
    from backend.api.dependencies import get_main_controller
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    controller = get_main_controller()
    window = MainWindow(controller)
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    run()
