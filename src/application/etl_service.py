import time
from pathlib import Path
from typing import Callable, Optional
from src.ports.file_parser import IFileParser
from src.ports.llm_processor import ILlmProcessor
from src.ports.database_repo import IDatabaseRepo
from src.ports.person_repo import IPersonRepo
from src.ports.municipality_repo import IMunicipalityRepo
from src.domain.entities import IncidentReport, Person, Municipality
from src.application.text_cleaner import (
    clean_relint_text,
    extract_history_from_annex,
    extract_date_of_fact,
    extract_time_of_fact,
    extract_map_url,
    resolve_coordinates_and_map_info
)
from src.domain.rules.base_rule import IncidentRule
from src.ports.processed_registry import IProcessedRegistry

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
        municipality_repo: IMunicipalityRepo
    ):
        self.file_parser = file_parser
        self.llm_processor = llm_processor
        self.database_repo = database_repo
        self.processed_registry = processed_registry
        self.person_repo = person_repo
        self.municipality_repo = municipality_repo

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
            
            if on_progress: on_progress(f"[{filename}] -> Processando com IA local...")
            if on_sent_to_llm: on_sent_to_llm(filename)
            
            questions = rule.questions if rule else None
            response_dict = self.llm_processor.process_text(cleaned_text, questions=questions)

            # 1. Definir o conteúdo integral do histórico preservando o cabeçalho introdutório do RELINT (RELATÓRIO DE INTELIGÊNCIA Nº, ASSUNTO, ORIGEM, DIFUSÃO, ANEXOS)
            final_content = clean_relint_text(cleaned_text)
            if "content" in response_dict:
                del response_dict["content"]

            # 2. Extração / Sanitização da data e hora do fato (date_of_fact, time_of_fact)
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

            # 4. Sanitiza o resumo caso venha nulo ou com texto de placeholder
            summary_val = response_dict.get("summary")
            if not summary_val or "Resumo do Histórico" in str(summary_val) or len(str(summary_val).strip()) < 5:
                summary_val = response_dict.get("main_fact") or response_dict.get("subject") or (final_content[:300] + "...")
            response_dict["summary"] = summary_val

            # 5. Filtragem de participantes: EXCLUIR Policiais Militares (PM / Guarnição)

            raw_participants = response_dict.get("participants", [])
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

            # 6. Extração e Classificação de Imagens do PDF (Fotos de Participantes vs Cenas do Fato)
            media_dir = Path("data/media") / file_path.stem
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

            # Atribuição de participantes (sem foto individual nesta etapa)
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
                report = IncidentReport(**report_data)
            except Exception as model_err:
                # Se falhar o parse direto do Pydantic (IA fugiu muito do schema), injeta de forma relaxada
                if on_progress: on_progress(f"[{filename}] Aviso: IA não seguiu estritamente o Schema. Salvando relaxado.")
                report = IncidentReport(
                    source_file=filename,
                    content=final_content,
                    subject=response_dict.get("subject", ""),
                    summary=summary_val,
                    main_fact=response_dict.get("main_fact", ""),
                    address=response_dict.get("address", ""),
                    date_of_fact=date_val,
                    modification_date_history=date_val,
                    participants=parsed_participants,
                    images=general_scene_images
                )


            # Salva o RELINT no banco central
            self.database_repo.save(report)

            # Upsert de Participantes no banco de Pessoas
            for participant in report.participants:
                if not participant.name:
                    continue
                
                # Tenta buscar por documento ou por nome como fallback simplificado
                person_id = participant.document if participant.document else participant.name.lower()
                existing_person = self.person_repo.get_by_id(person_id)
                
                if existing_person:
                    if filename not in existing_person.linked_relints:
                        existing_person.linked_relints.append(filename)
                    if participant.nickname and participant.nickname not in existing_person.aliases:
                        existing_person.aliases.append(participant.nickname)
                    if participant.photo_path and participant.photo_path not in existing_person.photos:
                        existing_person.photos.append(participant.photo_path)
                    self.person_repo.update(existing_person)
                else:
                    new_person = Person(
                        person_id=person_id,
                        name=participant.name,
                        aliases=[participant.nickname] if participant.nickname else [],
                        documents=[participant.document] if participant.document else [],
                        photos=[participant.photo_path] if participant.photo_path else [],
                        linked_relints=[filename]
                    )
                    self.person_repo.save(new_person)


            # Upsert de Locais no banco de Municípios (baseado nos Tipos de Local ou extraindo cidade, 
            # Como a extração de cidade exata é complexa e não temos um campo 'city', usaremos 
            # uma aproximação no futuro. Por enquanto, criamos uma lógica mockada pro endereço.)
            # Nota: Podemos extrair da string de 'address', ou futuramente exigir da IA.
            # Vamos buscar no address se tem algum municipio, pra fim de teste:
            if report.address:
                # Mock simplificado: pegar primeira palavra do endereço como se fosse município
                city_mock = report.address.split(',')[0].strip()[:20] if ',' in report.address else "Não Informado"
                
                mun = self.municipality_repo.get_by_name(city_mock)
                if not mun:
                    mun = Municipality(name=city_mock, linked_relints=[])
                
                if filename not in mun.linked_relints:
                    mun.linked_relints.append(filename)
                
                bm_val = getattr(report.bm_group, "value", report.bm_group)
                group = str(bm_val) if bm_val else "Outros"
                mun.stats_by_group[group] = mun.stats_by_group.get(group, 0) + 1
                
                if self.municipality_repo.get_by_name(city_mock):
                    self.municipality_repo.update(mun)
                else:
                    self.municipality_repo.save(mun)


            if rule:
                self.processed_registry.register_processed(filename, rule.name, "confirmed")
            
            elapsed_time = time.time() - start_time
            if on_progress:
                on_progress(f"[{filename}] -> Concluído em {elapsed_time:.2f}s.")
            
            if on_success:
                on_success(report)

            return report

        except Exception as e:
            error_msg = f"Erro ao processar {filename}: {str(e)}"
            if on_error:
                on_error(error_msg)
            return None
