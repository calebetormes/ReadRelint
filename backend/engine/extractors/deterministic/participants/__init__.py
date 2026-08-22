# -*- coding: utf-8 -*-
from backend.engine.extractors.deterministic.participants.participant_extractor import ParticipantExtractor
from backend.engine.extractors.deterministic.participants.ibge_validator import is_valid_brazilian_name, is_valid_first_name
from backend.engine.extractors.deterministic.participants.role_detector import (
    detect_participation_role,
    extract_document_near_name,
    extract_nickname,
)
from backend.engine.extractors.deterministic.participants.spacy_ner import extract_person_entities_spacy
from backend.engine.extractors.deterministic.participants.structured_parser import extract_structured_blocks

__all__ = [
    "ParticipantExtractor",
    "is_valid_brazilian_name",
    "is_valid_first_name",
    "detect_participation_role",
    "extract_document_near_name",
    "extract_nickname",
    "extract_person_entities_spacy",
    "extract_structured_blocks",
]
