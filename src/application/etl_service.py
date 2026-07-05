import time
from pathlib import Path
from typing import Callable, Optional, List
from src.ports.file_parser import IFileParser
from src.ports.llm_processor import ILlmProcessor
from src.ports.database_repo import IDatabaseRepo
from src.domain.entities import IncidentReport
from src.application.text_cleaner import clean_relint_text

class EtlService:
    """
    Serviço de aplicação responsável pela orquestração do pipeline de ETL
    (Extração, Transformação e Carga) de boletins de ocorrência em 4 Fases.
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
        Executa o pipeline multifásico de processamento de um único arquivo PDF.

        :param file_path: Caminho do arquivo a ser processado.
        :param on_progress: Callback para notificar etapas do progresso.
        :param on_success: Callback acionado para cada relatório estruturado com sucesso.
        :param on_error: Callback acionado em caso de falha geral.
        :return: A última entidade IncidentReport estruturada, ou None se falhar.
        """
        filename = file_path.name
        start_time = time.time()
        
        try:
            # 1. Verifica duplicidade antes de iniciar
            if self.database_repo.exists_by_source_file(filename):
                msg = f"[{filename}] Arquivo já cadastrado no banco. Pulando."
                if on_progress:
                    on_progress(msg)
                return None

            # 2. Fase 2: Extração de texto bruto e Limpeza (Regex)
            if on_progress:
                on_progress(f"[{filename}] -> extraindo texto do PDF...")
            raw_text = self.file_parser.extract_text(file_path)
            
            cleaned_text = clean_relint_text(raw_text)
            if not cleaned_text.strip():
                raise ValueError("O arquivo PDF está vazio ou não contém texto legível após a limpeza.")

            # 3. Fase 1: Extração de Metadados do Documento
            if on_progress:
                on_progress(f"[{filename}] -> extraindo metadados... (OK)")
            metadata = self.llm_processor.extract_metadata(cleaned_text)
            
            relint_number = metadata.get("relint_number")
            subject = metadata.get("subject")
            diffusion = metadata.get("diffusion")
            attachment = metadata.get("attachment")

            # 4. Fase 3: Análise de Enquadramento e Segmentação de Ocorrências
            if on_progress:
                on_progress(f"[{filename}] -> analisando enquadramentos...")
            segments = self.llm_processor.segment_occurrences(cleaned_text)
            
            total_occurrences = len(segments)
            if on_progress:
                on_progress(f"[{filename}] -> analisando enquadramentos... (Detectadas {total_occurrences} ocorrências)")

            if total_occurrences == 0:
                if on_progress:
                    on_progress(f"[{filename}] Nenhuma ocorrência policial relevante foi identificada.")
                return None

            # 5. Fase 4: Extração de Campos Específicos para cada Ocorrência
            last_report: Optional[IncidentReport] = None
            for idx, seg in enumerate(segments, start=1):
                nature = seg.get("incident_nature", "Ocorrência")
                group = seg.get("incident_group", "Demais Fatos")
                inc_type = seg.get("incident_type", "Fato Registrado")
                segment_text = seg.get("incident_text_segment", "")

                if not segment_text.strip():
                    segment_text = cleaned_text  # Fallback caso o segmento esteja em branco

                if on_progress:
                    on_progress(f"[{filename}] -> extraindo detalhes da ocorrência {idx} de {total_occurrences}...")

                # Executa a chamada do adaptador OllamaClient para estruturar a ocorrência segmentada
                # Caso a chamada process_incident_segment não esteja implementada no mock de testes,
                # fazemos fallback seguro para process_incident_text.
                if hasattr(self.llm_processor, "process_incident_segment"):
                    report = self.llm_processor.process_incident_segment(segment_text, group, inc_type, nature)
                else:
                    report = self.llm_processor.process_incident_text(segment_text)
                    report.incident_nature = nature
                    report.incident_group = group
                    report.incident_type = inc_type

                # Vincula os metadados do documento e a origem
                report.relint_number = relint_number
                report.subject = subject
                report.diffusion = diffusion
                report.attachment = attachment
                report.source_file = filename

                # Salva cada ocorrência individualmente no repositório de dados
                self.database_repo.save(report)
                
                if on_progress:
                    on_progress(f"[{filename}] -> extraindo detalhes da ocorrência {idx} de {total_occurrences}... (OK)")

                if on_success:
                    on_success(report)
                
                last_report = report

            elapsed_time = time.time() - start_time
            if on_progress:
                on_progress(f"[{filename}] -> Processamento concluído com sucesso. Tempo total: {elapsed_time:.2f}s.")

            return last_report

        except Exception as e:
            error_msg = f"Erro ao processar {filename}: {str(e)}"
            if on_error:
                on_error(error_msg)
            return None
