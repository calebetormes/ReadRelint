# -*- coding: utf-8 -*-
"""
Parser de blocos formais e seções estruturadas de participantes em boletins (NOME:, RG:, CPF:, VÍTIMA:).
"""

import re
from typing import Any, Dict, List
from src.engine.cleaners.text_cleaner import clean_person_name
from src.engine.extractors.common.negative_filters import is_blacklisted_name


from src.engine.extractors.deterministic.participants.role_detector import detect_participation_role


def extract_structured_blocks(text: str) -> List[Dict[str, Any]]:
    """
    Extrai participantes de seções e blocos verticais clássicos (NOME: ..., RG: ..., ALCUNHA: ...).
    """
    if not text:
        return []

    participants: List[Dict[str, Any]] = []
    seen_names = set()

    # 1. Padrão de bloco vertical formal
    block_pattern = re.compile(
        r'(?i)NOME:[ \t]*([A-Z\u00C0-\u00FF\s\.]{3,60})\s*[\r\n]+(?:[ \t]*RG:[ \t]*([\d\.\-]+)\s*[\r\n]+)?(?:[ \t]*CPF:[ \t]*([\d\.\-]+)\s*[\r\n]+)?(?:[ \t]*ALCUNHA:[ \t]*([^\r\n]+))?',
        re.MULTILINE
    )
    for m in block_pattern.finditer(text):
        raw_target = m.group(1).strip()
        if is_blacklisted_name(raw_target):
            continue
        name = clean_person_name(raw_target)
        rg = (m.group(2) or "").strip()
        cpf = (m.group(3) or "").strip()
        nick = (m.group(4) or "").strip()
        if not nick or nick.upper() in ["-", "-.", "NÃO POSSUI", "NAO POSSUI", "N/I", "NONE", "NENHUM", "NADA", "XXX"] or ":" in nick:
            nick = ""
        elif nick:
            nick = nick.title() if nick.isupper() or nick.islower() else nick
        doc = cpf if cpf else rg

        if not name or is_blacklisted_name(name):
            continue

        upper_name = name.upper()
        if upper_name not in seen_names:
            seen_names.add(upper_name)
            role = detect_participation_role(text, name)
            participants.append({
                "name": name,
                "nickname": nick,
                "document": doc,
                "participation_type": role
            })

    # 2. Padrão inline com RG ou CPF: "NOME COMPLETO, RG: 123456" ou "NOME - CPF 123456"
    inline_pattern = re.compile(
        r'(?i)\b([A-Z\u00C0-\u00FF]{2,}(?:\s+[A-Z\u00C0-\u00FF]{2,})+)\s*(?:[,\-\–\s]+)(?:RG|CPF)(?:\s*n[º°]|\s*:\s*|\s+)\s*([\d\.\-]+)',
        re.MULTILINE
    )
    for m in inline_pattern.finditer(text):
        raw_target = m.group(1).strip()
        if is_blacklisted_name(raw_target):
            continue
        name = clean_person_name(raw_target)
        doc = m.group(2).strip()

        if not name or is_blacklisted_name(name):
            continue

        upper_name = name.upper()
        if upper_name not in seen_names:
            seen_names.add(upper_name)
            role = detect_participation_role(text, name)
            participants.append({
                "name": name,
                "nickname": "",
                "document": doc,
                "participation_type": role
            })

    # 3. Padrão de Seções do Boletim: "VÍTIMA(S): NOME..." ou "ACUSADO(S): NOME..."
    section_patterns = [
        (r'(?i)(?:V[ÍI]TIMA|OFENDID[OA])(?:S|\(S\))?\s*:\s*([A-Z\u00C0-\u00FF\s\.]{3,50})', "Vítima"),
        (r'(?i)(?:ACUSAD[OA]|AUTOR(?:ES)?|PRESO(?:S)?)(?:S|\(S\))?\s*:\s*([A-Z\u00C0-\u00FF\s\.]{3,50})', "Acusado"),
        (r'(?i)(?:TESTEMUNHA|COMUNICANTE)(?:S|\(S\))?\s*:\s*([A-Z\u00C0-\u00FF\s\.]{3,50})', "Testemunha"),
    ]
    for pattern, role in section_patterns:
        for m in re.finditer(pattern, text):
            raw_target = m.group(1).split("\n")[0].split("-")[0].strip()
            name = clean_person_name(raw_target)
            if not name or is_blacklisted_name(name):
                continue
            upper_name = name.upper()
            if upper_name not in seen_names:
                seen_names.add(upper_name)
                participants.append({
                    "name": name,
                    "nickname": "",
                    "document": "",
                    "participation_type": role
                })

    # 4. Padrão narrativo com qualificadores e nomes em maiúsculas (ex: "menor ERIKA VITORIA...", "senhor EDIPO...")
    from src.engine.extractors.deterministic.participants.role_detector import extract_document_near_name
    narrative_pattern = re.compile(
        r'\b(?:menor(?:\s+de\s+idade)?|crian[çc]a|v[íi]tima|ofendid[oa]|autor[a]?|acusad[oa]|testemunha|suspeit[oa]|identificad[oa]\s+como|senhor[a]?)\s+([A-ZÀ-Ú]{2,}(?:\s+[A-ZÀ-Ú]{2,})+)',
        re.IGNORECASE
    )
    for m in narrative_pattern.finditer(text):
        raw_name = m.group(1).strip()
        if not raw_name.isupper():
            continue
        name = clean_person_name(raw_name)
        if not name or is_blacklisted_name(name):
            continue
        upper_name = name.upper()
        if upper_name not in seen_names:
            seen_names.add(upper_name)
            role = detect_participation_role(text, name)
            doc = extract_document_near_name(text, name)
            participants.append({
                "name": name,
                "nickname": "",
                "document": doc,
                "participation_type": role
            })

    return participants
