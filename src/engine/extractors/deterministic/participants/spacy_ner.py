# -*- coding: utf-8 -*-
"""
Módulo de Reconhecimento de Entidades Nomeadas (NER) utilizando spaCy com o modelo 'pt_core_news_sm'.
Executa detecção de entidades do tipo PER (Pessoa) com captura resiliente de erros e emissão de alertas.
"""

from typing import Any, List, Optional, Tuple
from src.engine.extractors.base import ExtractionAlert

_SPACY_NLP: Optional[Any] = None
_SPACY_INITIALIZATION_ATTEMPTED: bool = False
_SPACY_LOAD_ERROR_MSG: Optional[str] = None


def get_spacy_nlp() -> Tuple[Optional[Any], Optional[str]]:
    """
    Carrega o modelo spaCy 'pt_core_news_sm' em cache singleton.
    Retorna uma tupla (nlp_instance, error_message).
    """
    global _SPACY_NLP, _SPACY_INITIALIZATION_ATTEMPTED, _SPACY_LOAD_ERROR_MSG
    if _SPACY_INITIALIZATION_ATTEMPTED:
        return _SPACY_NLP, _SPACY_LOAD_ERROR_MSG

    _SPACY_INITIALIZATION_ATTEMPTED = True
    try:
        import spacy
        try:
            _SPACY_NLP = spacy.load("pt_core_news_sm")
            _SPACY_LOAD_ERROR_MSG = None
        except Exception as e:
            _SPACY_NLP = None
            _SPACY_LOAD_ERROR_MSG = (
                f"Modelo spaCy 'pt_core_news_sm' não encontrado no ambiente ({e}). "
                "Execute 'python -m spacy download pt_core_news_sm' para habilitar o NER avançado."
            )
    except ImportError:
        _SPACY_NLP = None
        _SPACY_LOAD_ERROR_MSG = (
            "Biblioteca 'spacy' não está instalada no ambiente Python. "
            "O extrator operará em modo determinístico estruturado (Regex + IBGE)."
        )

    return _SPACY_NLP, _SPACY_LOAD_ERROR_MSG


def extract_person_entities_spacy(text: str) -> Tuple[List[str], List[ExtractionAlert]]:
    """
    Extrai nomes de pessoas candidatas do texto utilizando o modelo spaCy pt-BR.
    Se o spaCy falhar ou não estiver presente, emite alertas e retorna lista vazia.
    """
    alerts: List[ExtractionAlert] = []
    if not text or not text.strip():
        return [], alerts

    nlp, err = get_spacy_nlp()
    if err or nlp is None:
        alerts.append(ExtractionAlert(
            level="warning",
            stage="spacy_ner",
            message=err or "Falha desconhecida ao inicializar o spaCy NER."
        ))
        return [], alerts

    try:
        doc = nlp(text)
        candidates: List[str] = []
        for ent in doc.ents:
            if ent.label_ == "PER":
                clean_name = ent.text.strip().strip(".,;:\"'()-")
                if len(clean_name) >= 3 and "\n" not in clean_name:
                    candidates.append(clean_name)
        return candidates, alerts
    except Exception as exc:
        alerts.append(ExtractionAlert(
            level="error",
            stage="spacy_ner",
            message=f"Erro durante execução do NER do spaCy: {exc}"
        ))
        return [], alerts
