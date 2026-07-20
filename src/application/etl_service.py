import time
from pathlib import Path
from typing import Callable, Optional
from src.ports.file_parser import IFileParser
from src.ports.llm_processor import ILlmProcessor
from src.ports.database_repo import IDatabaseRepo
from src.domain.entities import IncidentReport
from src.application.text_cleaner import clean_relint_text
from src.domain.rules.base_rule import IncidentRule
from src.ports.processed_registry import IProcessedRegistry

class EtlService:
    """
    Serviço de aplicação responsável pela orquestração do pipeline simplificado de ETL.
    """

    def __init__(
        self,
        file_parser: IFileParser,
        llm_processor: ILlmProcessor,
        database_repo: IDatabaseRepo,
        processed_registry: IProcessedRegistry
    ):
        self.file_parser = file_parser
        self.llm_processor = llm_processor
        self.database_repo = database_repo
        self.processed_registry = processed_registry

    def process_file(
        self,
        file_path: Path,
        rule: Optional[IncidentRule] = None,
        on_progress: Optional[Callable[[str], None]] = None,
        on_success: Optional[Callable[[IncidentReport], None]] = None,
        on_error: Optional[Callable[[str], None]] = None,
        on_filtered: Optional[Callable[[str], None]] = None,
        on_sent_to_llm: Optional[Callable[[str], None]] = None
    ) -> Optional[IncidentReport]:
        """
        Executa o pipeline simplificado de processamento de um único arquivo PDF.

        :param file_path: Caminho do arquivo a ser processado.
        :param rule: Regra opcional de filtragem e extração a ser aplicada.
        :param on_progress: Callback para notificar etapas do progresso.
        :param on_success: Callback acionado para o relatório estruturado com sucesso.
        :param on_error: Callback acionado em caso de falha geral.
        :param on_filtered: Callback acionado quando o arquivo é descartado pelo filtro.
        :param on_sent_to_llm: Callback acionado quando o arquivo é enviado ao LLM.
        :return: A entidade IncidentReport gerada, ou None se falhar.
        """
        filename = file_path.name
        start_time = time.time()
        
        try:
            # 0. Verifica histórico de processamento para evitar re-análise
            # 0. Verifica histórico de processamento para evitar re-análise
            if rule and self.processed_registry.is_processed(filename, rule.name):
                # Se foi confirmado, mas não está no banco (banco foi apagado/truncado),
                # remove do histórico para forçar reprocessamento.
                records = self.processed_registry.get_all_records()
                status = records.get(filename, {}).get(rule.name)
                if status == "confirmed" and not self.database_repo.exists_by_source_file(filename):
                    self.processed_registry.remove_record(filename, rule.name)
                else:
                    msg = f"[{filename}] Já processado anteriormente para a regra '{rule.name}'. Pulando."
                    if on_progress:
                        on_progress(msg)
                    return None

            # 1. Verifica duplicidade antes de iniciar para não causar dualidade
            if self.database_repo.exists_by_source_file(filename):
                msg = f"[{filename}] Arquivo já cadastrado no banco. Pulando."
                if on_progress:
                    on_progress(msg)
                # Registra no histórico para manter integridade
                if rule:
                    self.processed_registry.register_processed(filename, rule.name, "confirmed")
                return None

            # 2. Leitura do texto bruto
            if on_progress:
                on_progress(f"[{filename}] -> Extraindo texto do PDF...")
            raw_text = self.file_parser.extract_text(file_path)
            
            # 3. Limpeza do texto (remover cabeçalho restrito, avisos, etc.)
            cleaned_text = clean_relint_text(raw_text)
            if not cleaned_text.strip():
                raise ValueError("O arquivo PDF está vazio ou não contém texto legível após a limpeza.")

            # 3.5. Pré-filtragem rápida baseada na regra ativa
            if rule:
                if not rule.matches_filter(cleaned_text):
                    msg = f"[{filename}] Pulado: Não corresponde aos critérios da regra '{rule.name}'."
                    if on_progress:
                        on_progress(msg)
                    if on_filtered:
                        on_filtered(filename)
                    self.processed_registry.register_processed(filename, rule.name, "filtered_pre_llm")
                    return None

            # 4. Leitura do arquivo via IA (Processamento LLM - Segundo Filtro e Resumo)
            if on_progress:
                on_progress(f"[{filename}] -> Processando com Inteligência Artificial local...")
            
            if on_sent_to_llm:
                on_sent_to_llm(filename)
            
            questions = rule.questions if rule else None
            response_dict = self.llm_processor.process_text(cleaned_text, questions=questions)

            # 4.5. Validação pós-QA (Double-Check inteligente)
            is_target = True
            if rule:
                is_target = rule.validate_qa_results(response_dict)
                
            processed_content = response_dict.get("content", "")

            if not is_target:
                msg = f"[{filename}] Descartado pelo QA: Fato não confirmado como '{rule.name if rule else 'esperado'}'."
                if on_progress:
                    on_progress(msg)
                if on_filtered:
                    on_filtered(filename)
                if rule:
                    self.processed_registry.register_processed(filename, rule.name, "filtered_post_llm")
                return None


            # 5. Instanciação da entidade com apenas nome do arquivo e conteúdo resumido e filtrado pela IA
            report = IncidentReport(
                source_file=filename,
                content=processed_content
            )

            # 6. Salvamento no banco de dados
            self.database_repo.save(report)
            if rule:
                self.processed_registry.register_processed(filename, rule.name, "confirmed")
            
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
