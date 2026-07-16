import time
from pathlib import Path
from typing import Callable, Optional
from src.ports.file_parser import IFileParser
from src.ports.llm_processor import ILlmProcessor
from src.ports.database_repo import IDatabaseRepo
from src.domain.entities import IncidentReport
from src.application.text_cleaner import clean_relint_text

class EtlService:
    """
    Serviço de aplicação responsável pela orquestração do pipeline simplificado de ETL.
    """

    def __init__(
        self,
        file_parser: IFileParser,
        llm_processor: ILlmProcessor,
        database_repo: IDatabaseRepo
    ):
        self.file_parser = file_parser
        self.llm_processor = llm_processor
        self.database_repo = database_repo

    def process_file(
        self,
        file_path: Path,
        on_progress: Optional[Callable[[str], None]] = None,
        on_success: Optional[Callable[[IncidentReport], None]] = None,
        on_error: Optional[Callable[[str], None]] = None
    ) -> Optional[IncidentReport]:
        """
        Executa o pipeline simplificado de processamento de um único arquivo PDF.

        :param file_path: Caminho do arquivo a ser processado.
        :param on_progress: Callback para notificar etapas do progresso.
        :param on_success: Callback acionado para o relatório estruturado com sucesso.
        :param on_error: Callback acionado em caso de falha geral.
        :return: A entidade IncidentReport gerada, ou None se falhar.
        """
        filename = file_path.name
        start_time = time.time()
        
        try:
            # 1. Verifica duplicidade antes de iniciar para não causar dualidade
            if self.database_repo.exists_by_source_file(filename):
                msg = f"[{filename}] Arquivo já cadastrado no banco. Pulando."
                if on_progress:
                    on_progress(msg)
                return None

            # 2. Leitura do texto bruto
            if on_progress:
                on_progress(f"[{filename}] -> Extraindo texto do PDF...")
            raw_text = self.file_parser.extract_text(file_path)
            
            # 3. Limpeza do texto (remover cabeçalho restrito, avisos, etc.)
            cleaned_text = clean_relint_text(raw_text)
            if not cleaned_text.strip():
                raise ValueError("O arquivo PDF está vazio ou não contém texto legível após a limpeza.")

            # 4. Leitura do arquivo via IA (Processamento LLM)
            if on_progress:
                on_progress(f"[{filename}] -> Processando com Inteligência Artificial local...")
            processed_content = self.llm_processor.process_text(cleaned_text)

            # 5. Instanciação da entidade com apenas nome do arquivo e conteúdo
            report = IncidentReport(
                source_file=filename,
                content=processed_content
            )

            # 6. Salvamento no banco de dados
            self.database_repo.save(report)
            
            elapsed_time = time.time() - start_time
            if on_progress:
                on_progress(f"[{filename}] -> Concluído com sucesso em {elapsed_time:.2f}s.")
            
            if on_success:
                on_success(report)

            return report

        except Exception as e:
            error_msg = f"Erro ao processar {filename}: {str(e)}"
            if on_error:
                on_error(error_msg)
            return None
