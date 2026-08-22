# -*- coding: utf-8 -*-
"""
Coordenador do pipeline determinístico especialista de extração de participantes.
Combina parser de blocos estruturados, spaCy NER, validação positiva IBGE e filtros negativos.
"""

from typing import Any, Dict, List, Tuple
from backend.engine.cleaners.text_cleaner import clean_person_name
from backend.engine.extractors.base import ExtractionAlert
from backend.engine.extractors.common.negative_filters import is_blacklisted_name
from backend.engine.extractors.deterministic.participants.ibge_validator import is_valid_brazilian_name
from backend.engine.extractors.deterministic.participants.role_detector import (
    detect_participation_role,
    extract_document_near_name,
    extract_nickname,
)
from backend.engine.extractors.deterministic.participants.spacy_ner import extract_person_entities_spacy
from backend.engine.extractors.deterministic.participants.structured_parser import extract_structured_blocks


class ParticipantExtractor:
    """Extrator especialista de participantes com pipeline de 5 camadas e rastreamento de alertas."""

    def extract_participants(self, text: str) -> Tuple[List[Dict[str, Any]], List[ExtractionAlert]]:
        """
        Executa o pipeline completo de extração de participantes a partir do texto do RELINT.
        Retorna a lista de participantes e os alertas gerados no processo.
        """
        alerts: List[ExtractionAlert] = []
        if not text or not text.strip():
            return [], alerts

        participants_by_name: Dict[str, Dict[str, Any]] = {}

        # 1. Camada 1: Extração Estruturada (Blocos e Seções Formais)
        structured_list = extract_structured_blocks(text)
        for p in structured_list:
            norm_key = p["name"].strip().upper()
            participants_by_name[norm_key] = p

        # 2. Camada 2: Detecção Sintática com spaCy NER
        spacy_candidates, spacy_alerts = extract_person_entities_spacy(text)
        alerts.extend(spacy_alerts)

        # 3. Camada 3: Validação Positiva IBGE e Enriquecimento
        for raw_name in spacy_candidates:
            clean_name = clean_person_name(raw_name)
            if not clean_name or is_blacklisted_name(clean_name):
                continue

            # Valida se possui estrutura e prenome brasileiro autêntico
            if not is_valid_brazilian_name(clean_name):
                continue

            norm_key = clean_name.strip().upper()

            # Detecta atributos contextuais
            role = detect_participation_role(text, clean_name)
            nick = extract_nickname(text, clean_name)
            doc = extract_document_near_name(text, clean_name)

            if norm_key in participants_by_name:
                # Enriquece dados existentes se estiverem vazios
                existing = participants_by_name[norm_key]
                if not existing.get("nickname") and nick:
                    existing["nickname"] = nick
                if not existing.get("document") and doc:
                    existing["document"] = doc
                if role != "Autor/Suspeito" or existing.get("participation_type") == "Autor/Suspeito":
                    existing["participation_type"] = role
            else:
                participants_by_name[norm_key] = {
                    "name": clean_name,
                    "nickname": nick,
                    "document": doc,
                    "participation_type": role
                }

        # 4. Camada 4 & 5: Filtro Final Anti-PM e Sanitização de Saída
        final_participants: List[Dict[str, Any]] = []
        for p in participants_by_name.values():
            p_name = p.get("name", "")
            if not is_blacklisted_name(p_name):
                final_participants.append(p)

        return final_participants, alerts
