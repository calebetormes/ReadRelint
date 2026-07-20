import customtkinter as ctk
from src.infrastructure.utils.module_loader import ModuleLoader

class MainWindow(ctk.CTk):
    """
    Janela principal da aplicação (View raiz).
    Utiliza o ModuleLoader para recuperar componentes e controladores
    dinamicamente, mantendo o SRP e o baixo acoplamento.
    """
    def __init__(self):
        super().__init__()

        # Configurações globais do tema
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.title("ETL de Boletins de Ocorrência - Painel de Controle")
        self.geometry("1024x720")
        self.resizable(True, True)
        self.minsize(850, 640)

        # 1. Recuperando as classes injetadas dinamicamente via Registry
        MainControllerCls = ModuleLoader.get_class("MainController")
        ControlPanelTabCls = ModuleLoader.get_class("ControlPanelTab")
        ReportTabCls = ModuleLoader.get_class("ReportTab")

        # 2. Inicializando o Controlador de Domínio
        self.controller = MainControllerCls()

        # 3. Construindo a UI
        self.title_label = ctk.CTkLabel(
            self, text="Painel de Controle - ETL de BOs", 
            font=ctk.CTkFont(family="Inter", size=22, weight="bold")
        )
        self.title_label.pack(pady=10)

        self.tabview = ctk.CTkTabview(self, width=720, height=480)
        self.tabview.pack(pady=5, padx=25, fill="both", expand=True)

        self.tabview.add("Painel de Controle")
        self.tabview.add("Relatórios de Leitura")

        # Injetando o controlador nos componentes visuais
        self.control_panel = ControlPanelTabCls(master=self.tabview.tab("Painel de Controle"), controller=self.controller)
        self.control_panel.pack(fill="both", expand=True)

        self.report_panel = ReportTabCls(master=self.tabview.tab("Relatórios de Leitura"), controller=self.controller)
        self.report_panel.pack(fill="both", expand=True)

        # 4. Registrando os callbacks (Eventos) para ligar o Controller à View
        self.controller.on_log_message = self.control_panel.log_message
        self.controller.on_stats_updated = self._sync_ui_state

    def _sync_ui_state(self):
        """
        Método central para sincronizar a View com o Estado atual do Controller.
        """
        # Como o tk/ctk não é thread-safe de forma rígida, esse método 
        # pode ser agendado com 'after', mas o CTK lida bem com calls diretos.
        self.after(0, self._sync_ui_state_thread_safe)

    def _sync_ui_state_thread_safe(self):
        self.control_panel.update_stats()
        self.report_panel.refresh_state()

    def destroy(self):
        """
        Hook de encerramento da janela para garantir a destruição de processos filhos.
        """
        if self.controller:
            self.controller.destroy()
        super().destroy()
