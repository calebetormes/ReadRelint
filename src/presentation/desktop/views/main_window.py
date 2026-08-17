import customtkinter as ctk
from PIL import Image, ImageDraw
import pystray
from src.infrastructure.utils.module_loader import ModuleLoader


def _create_tray_icon_image():
    """Gera uma imagem de ícone 64x64 em memória para o System Tray."""
    image = Image.new('RGB', (64, 64), color=(18, 18, 18))
    draw = ImageDraw.Draw(image)
    # Desenha um retângulo arredondado verde esmeralda com a letra 'R'
    draw.rounded_rectangle([4, 4, 60, 60], radius=14, fill=(16, 185, 129))
    draw.text((22, 12), "R", fill=(255, 255, 255))
    return image


class MainWindow(ctk.CTk):
    """
    Janela principal da aplicação (View raiz).
    Utiliza o ModuleLoader para recuperar componentes e controladores dinamicamente.
    Suporta minimização para a Bandeja do Sistema (System Tray) via pystray.
    """
    def __init__(self):
        super().__init__()

        # Configurações globais do tema
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("green")

        self.title("ReadRelint • Central de Serviços")
        self.geometry("480x580")
        self.resizable(True, True)
        self.minsize(440, 520)
        self.configure(fg_color="#121212")

        # 1. Recuperando as classes injetadas dinamicamente via Registry
        MainControllerCls = ModuleLoader.get_class("MainController")
        StatusTabCls = ModuleLoader.get_class("StatusTab")

        # 2. Inicializando o Controlador de Domínio
        self.controller = MainControllerCls()

        # 3. Construindo o Cabeçalho Compacto
        self.header_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.header_frame.pack(fill="x", padx=15, pady=(12, 2))

        self.title_label = ctk.CTkLabel(
            self.header_frame, 
            text="ReadRelint • Inteligência Local", 
            font=ctk.CTkFont(family="Inter", size=18, weight="bold"),
            text_color="#f8fafc"
        )
        self.title_label.pack(side="left")

        # 4. Construindo o Painel Principal de Status & Serviços
        self.status_panel = StatusTabCls(master=self, controller=self.controller)
        self.status_panel.pack(fill="both", expand=True, padx=15, pady=(4, 15))

        # 5. Registrando os callbacks (Eventos) para ligar o Controller à View
        self.controller.on_log_message = lambda msg: None
        self.controller.on_stats_updated = self._sync_ui_state

        # 6. Interceptação do evento de fechar janela (X) -> Minimizar para a Bandeja
        self.protocol("WM_DELETE_WINDOW", self._on_close_requested)

        # 7. Agendamento seguro do Ícone do System Tray para após a renderização da janela
        self.tray_icon = None
        self.after(800, self._init_system_tray)

    def _init_system_tray(self):
        """Inicializa o ícone do System Tray de forma assíncrona e não-bloqueante."""
        try:
            menu = pystray.Menu(
                pystray.MenuItem("🖥️ Abrir Painel / Restaurar", self._restore_from_tray, default=True),
                pystray.MenuItem("🌐 Abrir Dashboard Web", self._open_web_from_tray),
                pystray.Menu.SEPARATOR,
                pystray.MenuItem("❌ Encerrar Aplicação Totalmente", self._quit_from_tray)
            )
            self.tray_icon = pystray.Icon(
                "ReadRelint",
                _create_tray_icon_image(),
                "ReadRelint - Administrador de RELINTs",
                menu=menu
            )
            self.tray_icon.run_detached()
        except Exception as err:
            print(f"[Aviso] Não foi possível iniciar o System Tray: {err}")

    def _restore_from_tray(self, icon=None, item=None):
        """Restaura a janela minimizada a partir da bandeja do sistema."""
        self.after(0, self._do_restore)

    def _do_restore(self):
        self.deiconify()
        self.lift()
        self.focus_force()

    def _open_web_from_tray(self, icon=None, item=None):
        """Abre o Dashboard Web a partir do menu do tray."""
        if self.controller:
            self.controller.open_web_dashboard()

    def _quit_from_tray(self, icon=None, item=None):
        """Encerra a aplicação totalmente a partir do menu do tray."""
        self.after(0, self.force_quit)

    def _on_close_requested(self):
        """Callback executado ao clicar no botão 'X' da janela. Oculta a janela para a bandeja."""
        self.withdraw()

    def force_quit(self):
        """Encerra totalmente o aplicativo, liberando o tray e fechando processos."""
        if hasattr(self, "tray_icon") and self.tray_icon:
            try:
                self.tray_icon.stop()
            except Exception:
                pass
        if self.controller:
            self.controller.destroy()
        super().destroy()

    def _sync_ui_state(self):
        """Agenda a atualização thread-safe das views."""
        self.after(0, self._sync_ui_state_thread_safe)

    def _sync_ui_state_thread_safe(self):
        """Atualiza o estado do painel de status."""
        if hasattr(self, "status_panel"):
            self.status_panel.update_stats()

    def destroy(self):
        """Hook de encerramento da janela."""
        if hasattr(self, "tray_icon") and self.tray_icon:
            try:
                self.tray_icon.stop()
            except Exception:
                pass
        if self.controller:
            self.controller.destroy()
        super().destroy()
