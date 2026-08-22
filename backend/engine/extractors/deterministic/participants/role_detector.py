# -*- coding: utf-8 -*-
"""
Módulo de detecção contextual de papel policial (Vítima, Acusado, Testemunha, Suspeito),
vulgos/alcunhas e documentos associados por proximidade textual.
"""

import re
from typing import Optional


def detect_participation_role(text: str, name: str) -> str:
    """
    Identifica o papel do participante (Vítima, Acusado, Testemunha, Suspeito, Comunicante)
    analisando a proximidade das palavras-chave contextuais em torno da citação do nome no texto do RELINT.
    """
    if not text or not name:
        return "Suspeito"

    escaped_name = re.escape(name)
    match = re.search(r'(?is)(.{0,150})' + escaped_name + r'(.{0,150})', text)
    if not match:
        window_before, window_after = text, ""
    else:
        window_before, window_after = match.group(1), match.group(2)

    # 1. Elimina falso positivo quando "vítima" refere-se à guarnição/policial (ex: "PM vítima", "policial vítima")
    window_before = re.sub(
        r'(?i)\b(?:pm|pms|policial|policiais|militar|militares|guarni[çc][ãa]o|sd|sgt|cb|ten|cap)\s+v[íi]tima[s]?\b',
        '',
        window_before
    )
    window_before = re.sub(
        r'(?i)\bv[íi]tima[s]?\s+(?:pm|pms|policial|policiais|militar|militares|guarni[çc][ãa]o)\b',
        '',
        window_before
    )

    # 2. Mapeamento direcional de papéis e expressões de referência
    role_patterns_before = {
        "Vítima": [
            r'\bv[íi]tima\b', r'\bofendid[oa]\b', r'\bmenor\s+v[íi]tima\b', r'\bcrian[çc]a\s+v[íi]tima\b',
            r'\bv[íi]tima\s+menor\b', r'\balvejad[oa]\b', r'\batingid[oa]\b', r'\blesionad[oa]\b',
            r'\bveio a [óo]bito\b', r'\bmorte\b', r'\bmorreu\b', r'\bcad[áa]ver\b', r'\bsocorrid[oa]\b',
            r'\bferid[oa]\b', r'\babusad[oa]\b', r'\bestuprad[oa]\b', r'\bagredid[oa]\b',
            r'\bamea[çc]ad[oa]\b', r'\broubad[oa]\b', r'\bfurtad[oa]\b'
        ],
        "Testemunha": [
            r'\btestemunha\b', r'\bpresenciou\b', r'\binforma[çc][ãa]o d[ao]\b',
            r'\bconforme\s+relatou\b', r'\bcomunicante\b', r'\bsolicitante\b', r'\bdenunciante\b',
            r'\b(?:pai|m[ãa]e|familiar|respons[áa]vel|vizinh[oa])\s+d[aoe]\s+(?:crian[çc]a|v[íi]tima|menor|ofendid[oa])\b',
            r'\bflagrad[oa]\s+pel[oa]\b', r'\bpopulares\b'
        ],
        "Autor/Suspeito": [
            r'\bacusad[oa]\b', r'\bautor(?:es)?\b', r'\bpreso[s]?\b', r'\bpresa[s]?\b',
            r'\bflagrante\b', r'\bconduzid[oa]\b', r'\bapreendid[oa]\b', r'\batirador\b',
            r'\bexecutor\b', r'\bindiciad[oa]\b', r'\bagressor\b', r'\binfrator\b',
            r'\bmenor\s+infrator\b', r'\badolescente\s+infrator\b', r'\bapreens[ãa]o\s+de\s+menor\b',
            r'\bmenor\s+apreendid[oa]\b', r'\bdados do autor\b', r'\bdados do suspeito\b',
            r'\bdados do acusado\b',
            r'\b(?:relatou|informou|denunciou|comunicou|disse)\s+que\b'
        ]
    }

    role_patterns_after = {
        "Vítima": [
            r'\bveio a [óo]bito\b', r'\bmorte\b', r'\bmorreu\b', r'\bsocorrid[oa]\b',
            r'\batingid[oa]\b', r'\balvejad[oa]\b', r'\blesionad[oa]\b', r'\bferid[oa]\b'
        ],
        "Testemunha": [
            r'\brelatou\b', r'\binformou\b', r'\bcomunicou\b', r'\bpresenciou\b',
            r'\bcompareceram\s+para\s+relatar\b', r'\bafirmou\b', r'\bdisse\b'
        ],
        "Autor/Suspeito": [
            r'\bamea[çc]ando\b', r'\bagredindo\b', r'\bdesferiu\b', r'\bincomodando\b',
            r'\bresistindo\b', r'\bcorrendo\b', r'\btentou\b', r'\bjogou\b',
            r'\bfaccionad[oa]\b', r'\bdesferiu\s+amea[çc]as\b', r'\balterad[oa]\b',
            r'\bdesobedeceu\b', r'\bdesacatou\b', r'\bfugiu\b', r'\bportando\b',
            r'\bpossu[íi]a\b', r'\bcometeu\b', r'\bfurtou\b', r'\broubou\b', r'\bmatou\b',
            r'\bdisparou\b', r'\besfaqueou\b', r'\batirou\b', r'\bdanificou\b'
        ]
    }

    # 3. Ranqueia os papéis por proximidade física com o nome e maior especificidade do padrão
    candidates = []

    # Ocorrências antes do nome
    for role, patterns in role_patterns_before.items():
        for pat in patterns:
            for m in re.finditer(pat, window_before, re.IGNORECASE):
                distance = len(window_before) - m.end()
                match_len = len(m.group(0))
                candidates.append((distance, role, match_len))

    # Ocorrências após o nome (peso ligeiramente menor)
    for role, patterns in role_patterns_after.items():
        for pat in patterns:
            for m in re.finditer(pat, window_after, re.IGNORECASE):
                distance = m.start() + 10
                match_len = len(m.group(0))
                candidates.append((distance, role, match_len))

    if candidates:
        # Menor distância primeiro; se empatar, maior especificidade da expressão
        candidates.sort(key=lambda x: (x[0], -x[2]))
        return candidates[0][1]

    return "Autor/Suspeito"


def extract_nickname(text: str, name: str) -> str:
    """
    Extrai alcunhas ou vulgos associados a um participante no texto (ex: 'vulgo Gordo', 'conhecido como Caveira').
    """
    if not text or not name:
        return ""

    escaped_name = re.escape(name)
    # 1. Procura vulgo grudado no nome: "Nome (vulgo Caveirinha)" ou "Nome, vulgo Caveirinha"
    inline_match = re.search(
        r'(?i)' + escaped_name + r'\s*[\(,]?\s*(?:vulgo|alcunha|apelido|conhecido(?: como| por))\s*[:\"\'“]?([A-Za-zÀ-ÿ0-9\s]{2,25})[\"\'”\)]?',
        text
    )
    if inline_match:
        nick = inline_match.group(1).strip(" \"'()[].,;:")
        if nick and nick.upper() not in ["NÃO POSSUI", "NAO POSSUI", "N/I", "NENHUM", "-"]:
            return nick.title()

    # 2. Procura apelido entre aspas após o nome: 'João da Silva "Gordinho"'
    quote_match = re.search(
        r'(?i)' + escaped_name + r'\s+[\"\'“]([A-Za-zÀ-ÿ0-9\s]{2,20})[\"\'”]',
        text
    )
    if quote_match:
        nick = quote_match.group(1).strip()
        if nick and nick.upper() not in ["NÃO POSSUI", "NAO POSSUI", "N/I", "NENHUM", "-"]:
            return nick.title()

    return ""


def extract_document_near_name(text: str, name: str) -> str:
    """
    Busca menções de CPF ou RG na vizinhança imediata do nome.
    """
    if not text or not name:
        return ""

    escaped_name = re.escape(name)
    match = re.search(r'(?is)' + escaped_name + r'(.{0,80})', text)
    if not match:
        return ""

    after_text = match.group(1)

    # 1. Busca por CPF
    cpf_match = re.search(r'(?i)CPF(?:\s*n[º°]|\s*:\s*|\s+)?([\d\.\-]{11,14})', after_text)
    if cpf_match:
        return cpf_match.group(1).strip()

    # 2. Busca por RG
    rg_match = re.search(r'(?i)RG(?:\s*n[º°]|\s*:\s*|\s+)?([\d\.\-]{5,14})', after_text)
    if rg_match:
        return rg_match.group(1).strip()

    return ""
