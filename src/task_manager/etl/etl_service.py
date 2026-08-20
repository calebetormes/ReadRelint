import time
from pathlib import Path
from typing import Callable, Optional, Dict, Any, List
from src.engine.parsers.file_parser import IFileParser
from src.engine.llm.llm_processor import ILlmProcessor
from src.dashboard.backend.database.database_repo import IDatabaseRepo
from src.dashboard.backend.database.person_repo import IPersonRepo
from src.dashboard.backend.core.entities import IncidentReport, Person, Participant
from src.engine.cleaners.text_cleaner import (
    clean_relint_text,
    extract_history_from_annex,
    extract_date_of_fact,
    extract_time_of_fact,
    extract_map_url,
    resolve_coordinates_and_map_info,
    extract_subject_fallback,
    extract_fallback_summary
)
from src.engine.rules.base_rule import IncidentRule
from src.task_manager.registry.processed_registry import IProcessedRegistry
from src.engine.cleaners.bm_classifier import classify_bm_group

class EtlService:
    """
    Serviço de aplicação responsável pela orquestração do pipeline completo de ETL.
    """

    def __init__(
        self,
        file_parser: IFileParser,
        llm_processor: ILlmProcessor,
        database_repo: IDatabaseRepo,
        processed_registry: IProcessedRegistry,
        person_repo: IPersonRepo,
        use_llm: bool = True
    ):
        self.file_parser = file_parser
        self.llm_processor = llm_processor
        self.database_repo = database_repo
        self.processed_registry = processed_registry
        self.person_repo = person_repo
        self.use_llm = use_llm

    def _normalize_response_dict(self, response_dict: dict) -> dict:
        """Normaliza chaves em Português/Inglês retornadas pela LLM para o padrão da entidade de domínio."""
        if not isinstance(response_dict, dict):
            return {}

        key_map = {
            "assunto": "subject",
            "fato_principal": "main_fact",
            "data_fato": "date_of_fact",
            "hora_fato": "time_of_fact",
            "grupo_bm": "bm_group",
            "tipo_relint": "relint_type",
            "municipio": "municipality",
            "bairro": "neighborhood",
            "endereco": "address",
            "unidade_policial": "police_unit",
            "coordenadas": "coordinates",
            "url_mapa": "map_url",
            "resumo": "summary",
            "participantes": "participants",
            "numero_registro": "registry_number",
            "orgao_registro": "registry_agency",
            "ano_registro": "registry_year",
            "tipo_fato": "fact_type",
            "motivacao": "motivation"
        }

        normalized = {}
        for k, v in response_dict.items():
            std_key = key_map.get(str(k).lower(), k)
            normalized[std_key] = v

        raw_parts = normalized.get("participants", [])
        if isinstance(raw_parts, list):
            from src.engine.cleaners.text_cleaner import clean_person_name
            norm_parts = []
            p_key_map = {
                "nome": "name",
                "alcunha": "nickname",
                "vulgo": "nickname",
                "documento": "document",
                "cpf": "document",
                "rg": "document",
                "antecedentes": "background",
                "tipo_participacao": "participation_type"
            }
            for p in raw_parts:
                if isinstance(p, dict):
                    norm_p = {}
                    for pk, pv in p.items():
                        norm_p[p_key_map.get(str(pk).lower(), pk)] = pv
                    if "name" in norm_p and norm_p["name"]:
                        norm_p["name"] = clean_person_name(str(norm_p["name"]))
                    norm_parts.append(norm_p)
                else:
                    norm_parts.append(p)
            normalized["participants"] = norm_parts

        return normalized

    def process_file(
        self,
        file_path: Path,
        rule: Optional[IncidentRule] = None,
        on_progress: Optional[Callable[[str], None]] = None,
        on_success: Optional[Callable[[IncidentReport], None]] = None,
        on_error: Optional[Callable[[str], None]] = None,
        on_filtered: Optional[Callable[[str], None]] = None,
        on_sent_to_llm: Optional[Callable[[str], None]] = None,
        on_llm_disconnected: Optional[Callable[[str], None]] = None
    ) -> Optional[IncidentReport]:
        """
        Executa o pipeline de processamento de um único arquivo PDF.
        """
        filename = file_path.name
        start_time = time.time()
        
        try:
            if self.database_repo.exists_by_source_file(filename) is True:
                if on_progress: on_progress(f"[{filename}] Já cadastrado no banco. Pulando.")
                if rule: self.processed_registry.register_processed(filename, rule.name, "confirmed")
                return None

            if rule and self.processed_registry.is_processed(filename, rule.name) is True:
                if on_progress: on_progress(f"[{filename}] Já processado. Pulando.")
                return None

            if on_progress: on_progress(f"[{filename}] -> Extraindo texto do PDF...")
            raw_text = self.file_parser.extract_text(file_path)
            
            cleaned_text = clean_relint_text(raw_text)
            if not cleaned_text.strip():
                raise ValueError("O arquivo PDF está vazio após a limpeza.")

            # Extração segura do histórico usando regra 11 (pós ANEXOS)
            history_from_annex = extract_history_from_annex(raw_text)
            
            questions = rule.questions if rule else None
            schema_model = None
            if rule and hasattr(rule, 'get_schema_model'):
                schema_model = rule.get_schema_model()
            else:
                schema_model = IncidentReport

            if self.use_llm and self.llm_processor:
                if on_progress: on_progress(f"[{filename}] -> Processando com IA local (Ollama)...")
                if on_sent_to_llm: on_sent_to_llm(filename)
                try:
                    response_dict = self.llm_processor.process_text(cleaned_text, questions=questions, schema_model=schema_model)
                    if not isinstance(response_dict, dict):
                        response_dict = {}
                    extraction_method = "Ollama (IA)"
                except Exception as llm_err:
                    self.use_llm = False
                    msg_disconnect = f"⚠️ Conexão com o Ollama perdida ({llm_err}). Alternando automaticamente para Regex (Sem IA)..."
                    if on_progress: on_progress(f"[{filename}] {msg_disconnect}")
                    if on_llm_disconnected: on_llm_disconnected(str(llm_err))
                    response_dict = {}
                    extraction_method = "Regex (Sem IA)"
            else:
                if on_progress: on_progress(f"[{filename}] ⚡ Processamento Ultra-Rápido (Regex / Sem IA)...")
                response_dict = {}
                extraction_method = "Regex (Sem IA)"

            response_dict = self._normalize_response_dict(response_dict)
            response_dict["extraction_method"] = extraction_method

            # 1. Definir o conteúdo integral do histórico preservando o cabeçalho introdutório do RELINT
            final_content = clean_relint_text(cleaned_text)
            if "content" in response_dict:
                del response_dict["content"]

            # 1.1 Classificação determinística por Regra específica
            rule_forced_bm = None
            if rule and hasattr(rule, 'get_bm_group'):
                rule_forced_bm = rule.get_bm_group(
                    filename=filename,
                    subject=response_dict.get("subject", "") or ""
                )
                if rule_forced_bm:
                    llm_bm = response_dict.get("bm_group", "Outros")
                    if llm_bm != rule_forced_bm:
                        if on_progress:
                            on_progress(f"[{filename}] ⚡ BM Group corrigido: '{llm_bm}' → '{rule_forced_bm}' (regra determinística)")
                    response_dict["bm_group"] = rule_forced_bm

            # 1.2 Classificação determinística por padrões regex
            current_bm = response_dict.get("bm_group", "Outros")
            if not rule_forced_bm and current_bm in ("Outros", "outros", None, ""):
                classified_bm = classify_bm_group(
                    filename=filename,
                    subject=response_dict.get("subject", "") or "",
                    content=final_content,
                    llm_bm_group=current_bm,
                )
                if classified_bm != current_bm:
                    if on_progress:
                        on_progress(f"[{filename}] 🎯 BM Group classificado: '{current_bm}' → '{classified_bm}' (classificador regex)")
                    response_dict["bm_group"] = classified_bm

            # 2. Extração / Sanitização da data e hora do fato
            extracted_date = extract_date_of_fact(final_content)
            date_val = response_dict.get("date_of_fact") or response_dict.get("modification_date_history")
            if not date_val or str(date_val).strip() in ["Não Informado", "None", ""]:
                date_val = extracted_date if extracted_date else "Não Informado"
            
            response_dict["date_of_fact"] = date_val
            response_dict["modification_date_history"] = date_val

            time_val = response_dict.get("time_of_fact")
            if not time_val or str(time_val).strip() in ["Não Informado", "None", ""]:
                extracted_time = extract_time_of_fact(final_content)
                time_val = extracted_time if extracted_time else "Não Informado"
            response_dict["time_of_fact"] = time_val

            # 3. Extração / Resolução de Links de Mapa e Coordenadas
            map_url = response_dict.get("map_url")
            coords = response_dict.get("coordinates")
            resolved_map, resolved_coords = resolve_coordinates_and_map_info(final_content, map_url=map_url or "")
            
            if not map_url or map_url == "None":
                response_dict["map_url"] = resolved_map
            if not coords or coords == "None":
                response_dict["coordinates"] = resolved_coords

            # 1.0 Fallback do Assunto caso venha nulo ou vazio
            subject_val = response_dict.get("subject")
            if not subject_val or str(subject_val).strip() in ["None", "null", ""]:
                subject_val = extract_subject_fallback(final_content, filename)
                response_dict["subject"] = subject_val

            # 4. Sanitiza o resumo caso venha nulo ou com texto de placeholder/cabeçalho
            summary_val = response_dict.get("summary")
            if not summary_val or "Resumo do Histórico" in str(summary_val) or len(str(summary_val).strip()) < 5 or "RELATÓRIO DE INTELIGÊNCIA" in str(summary_val):
                summary_val = response_dict.get("main_fact") or extract_fallback_summary(final_content, subject=response_dict.get("subject", ""))
            response_dict["summary"] = summary_val

            # 5. Filtragem de participantes: EXCLUIR Policiais Militares (PM / Guarnição)
            raw_participants = response_dict.get("participants", [])
            if not raw_participants:
                from src.engine.cleaners.text_cleaner import extract_fallback_participants
                raw_participants = extract_fallback_participants(final_content)

            filtered_participants = []
            pm_keywords = ["SD PM", "SGT PM", "CB PM", "CAP PM", "MAJ PM", "TEN PM", "POLICIAL MILITAR", "GUARNICAO", "GUARNICÃO", "2° SGT", "1° SGT", "3° SGT", " VTR "]
            
            for p in raw_participants:
                p_name = (p.get("name") if isinstance(p, dict) else getattr(p, "name", "")) or ""
                p_type = (p.get("participation_type") if isinstance(p, dict) else getattr(p, "participation_type", "")) or ""
                
                is_pm = False
                if str(p_type) in ["Parte da Guarnição", "GUARNICAO", "Parte da Guarnicao"]:
                    is_pm = True
                
                upper_name = p_name.upper()
                if any(kw in upper_name for kw in pm_keywords) or upper_name.startswith("SD ") or upper_name.startswith("SGT ") or upper_name.startswith("CB "):
                    is_pm = True
                    
                if not is_pm and p_name.strip():
                    filtered_participants.append(p)

            # 6. Extração de Imagens do PDF (Galeria do RELINT)
            import re
            import hashlib
            stem_clean = re.sub(r'[^a-zA-Z0-9_-]', '_', file_path.stem)
            stem_clean = re.sub(r'_+', '_', stem_clean).strip('_')
            safe_hash = hashlib.md5(file_path.name.encode('utf-8', errors='replace')).hexdigest()[:8]
            safe_folder_name = f"{stem_clean[:35]}_{safe_hash}"

            project_root = Path(__file__).resolve().parents[3]
            media_dir = project_root / "data" / "media" / safe_folder_name
            extracted_images = []
            try:
                if hasattr(self.file_parser, "extract_images"):
                    res = self.file_parser.extract_images(file_path, media_dir)
                    if isinstance(res, list):
                        extracted_images = res
            except Exception:
                extracted_images = []

            general_scene_images = []
            for img_info in extracted_images:
                path_str = img_info.get("file_path", "")
                caption_str = img_info.get("caption", "")
                if path_str:
                    general_scene_images.append({"path": path_str, "caption": caption_str})

            parsed_participants = []
            for p in filtered_participants:
                p_dict = p if isinstance(p, dict) else p.model_dump()
                p_dict["photo_path"] = None
                parsed_participants.append(p_dict)

            response_dict["participants"] = parsed_participants
            response_dict["images"] = general_scene_images

            # Instancia a entidade de domínio principal (RELINT)
            report_data = {
                "source_file": filename,
                **response_dict,
                "content": final_content
            }
            
            try:
                report = schema_model.model_validate(report_data)
            except Exception as model_err:
                if on_progress: on_progress(f"[{filename}] Aviso: IA não seguiu estritamente o Schema. Salvando com reconstrução segura.")
                report = schema_model.model_construct(**report_data)

            # Salva o RELINT no banco central
            self.database_repo.save(report)

            # Upsert de Participantes no banco de Pessoas
            for participant in report.participants:
                p_name = participant.name if isinstance(participant, Participant) else (participant.get("name") if isinstance(participant, dict) else "")
                if not p_name:
                    continue
                
                p_doc = participant.document if isinstance(participant, Participant) else (participant.get("document") if isinstance(participant, dict) else "")
                p_nick = participant.nickname if isinstance(participant, Participant) else (participant.get("nickname") if isinstance(participant, dict) else "")
                p_photo = participant.photo_path if isinstance(participant, Participant) else (participant.get("photo_path") if isinstance(participant, dict) else "")

                person_id = p_doc if p_doc else p_name.lower()
                existing_person = self.person_repo.get_by_id(person_id)
                
                if existing_person:
                    if filename not in existing_person.linked_relints:
                        existing_person.linked_relints.append(filename)
                    if p_nick and p_nick not in existing_person.aliases:
                        existing_person.aliases.append(p_nick)
                    if p_photo and p_photo not in existing_person.photos:
                        existing_person.photos.append(p_photo)
                    self.person_repo.update(existing_person)
                else:
                    new_person = Person(
                        person_id=person_id,
                        name=p_name,
                        aliases=[p_nick] if p_nick else [],
                        documents=[p_doc] if p_doc else [],
                        photos=[p_photo] if p_photo else [],
                        linked_relints=[filename]
                    )
                    self.person_repo.save(new_person)

            if rule:
                self.processed_registry.register_processed(filename, rule.name, "confirmed")
            
            elapsed_time = time.time() - start_time
            if on_progress:
                on_progress(f"[{filename}] -> Concluído em {elapsed_time:.2f}s.")
            
            if on_success:
                on_success(report)

            # Transmite o evento SSE em tempo real para atualização instantânea dos clientes Web
            try:
                from src.dashboard.backend.api.routers.events import broadcaster
                bm_str = report.bm_group.value if hasattr(report.bm_group, "value") else str(report.bm_group or "Outros")
                broadcaster.broadcast("relint_created", {
                    "id": str(report.id or ""),
                    "source_file": report.source_file or "",
                    "subject": report.subject or "",
                    "bm_group": bm_str,
                    "municipality": report.municipality or ""
                })
            except Exception:
                pass

            return report

        except Exception as e:
            error_msg = f"Erro ao processar {filename}: {str(e)}"
            if on_error:
                on_error(error_msg)
            return None
