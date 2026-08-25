# -*- coding: utf-8 -*-
"""
Validador positivo de prenomes brasileiros utilizando a base do Censo IBGE.
Garante em O(1) que o primeiro nome do participante é um prenome autêntico.
"""

import json
import os
import unicodedata
from typing import Optional, Set

_IBGE_NAMES_CACHE: Optional[Set[str]] = None


def _normalize_name_token(token: str) -> str:
    """Normaliza um token removendo acentos e convertendo para minúsculas."""
    if not token:
        return ""
    nfkd = unicodedata.normalize('NFKD', token)
    ascii_token = ''.join([c for c in nfkd if not unicodedata.combining(c)])
    return ascii_token.strip().lower()


def get_ibge_names_set() -> Set[str]:
    """Carrega em cache (singleton) o conjunto de prenomes brasileiros do IBGE."""
    global _IBGE_NAMES_CACHE
    if _IBGE_NAMES_CACHE is not None:
        return _IBGE_NAMES_CACHE

    json_path = os.path.join(
        os.path.dirname(__file__), "..", "resources", "ibge_names.json"
    )
    json_path = os.path.normpath(json_path)


    try:
        with open(json_path, "r", encoding="utf-8") as f:
            names_list = json.load(f)
            _IBGE_NAMES_CACHE = {_normalize_name_token(n) for n in names_list if n}
    except Exception:
        _IBGE_NAMES_CACHE = {
            "maria", "jose", "ana", "joao", "antonio", "francisco", "carlos", "paulo",
            "pedro", "lucas", "luiz", "marcos", "luis", "gabriel", "rafael", "daniel",
            "marcelo", "bruno", "eduardo", "felipe", "rodrigo", "manoel", "mateus",
            "andre", "fernando", "fabio", "leonardo", "gustavo", "guilherme", "leandro",
            "tiago", "anderson", "alessandro", "alexandre", "adriano", "juliana", "aline",
            "patricia", "camila", "amanda", "bruna", "jessica", "leticia", "julia"
        }

    return _IBGE_NAMES_CACHE


def is_valid_first_name(first_name: str) -> bool:
    """Verifica se o prenome fornecido existe na base de nomes do IBGE."""
    if not first_name:
        return False
    norm = _normalize_name_token(first_name)
    return norm in get_ibge_names_set()


def is_valid_brazilian_name(full_name: str) -> bool:
    """
    Verifica se um nome completo tem estrutura de nome brasileiro válido:
    - Pelo menos 2 palavras (prenome + sobrenome)
    - Primeiro nome presente na base do IBGE
    """
    if not full_name:
        return False

    tokens = [t.strip() for t in full_name.split() if t.strip()]
    if len(tokens) < 2:
        return False

    first_token = tokens[0]
    return is_valid_first_name(first_token)
