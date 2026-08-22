# -*- coding: utf-8 -*-
"""
Dicionários de exclusão e filtros negativos para extração determinística de participantes.
Evita falsos-positivos de órgãos públicos, veículos, patentes militares e vias urbanas.
"""

from typing import Set
import unicodedata
import re

# Patentes militares e termos de guarnição que nunca devem ser extraídos como pessoas investigadas
MILITARY_KEYWORDS: Set[str] = {
    "SD", "SD PM", "SGT", "SGT PM", "1 SGT", "2 SGT", "3 SGT", "1° SGT", "2° SGT", "3° SGT",
    "CB", "CB PM", "CAP", "CAP PM", "MAJ", "MAJ PM", "TEN", "TEN PM", "1 TEN", "2 TEN",
    "CEL", "CEL PM", "CORONEL", "POLICIAL MILITAR", "POLICIA MILITAR", "BRIGADA MILITAR",
    "GUARNICAO", "GUARNICAO PM", "VTR", "VIATURA", "EQUIPE VOLANTE", "PATRULHA"
}

# Órgãos públicos, hospitais, repartições e estabelecimentos institucionais
INSTITUTION_KEYWORDS: Set[str] = {
    "HOSPITAL", "HOSPITAL MUNICIPAL", "HOSPITAL REGIONAL", "POSTO DE SAUDE", "UPA", "UBS",
    "DELEGACIA", "DELEGACIA DE POLICIA", "DPPA", "DP", "DISTANCIA", "FORUM", "MINISTERIO PUBLICO",
    "DEFENSORIA PUBLICA", "CONSELHO TUTELAR", "IGP", "DML", "IML", "SAMU", "CORPO DE BOMBEIROS",
    "PREFEITURA", "SECRETARIA", "ESTADO DO RIO GRANDE DO SUL", "SECRETARIA DE SEGURANCA PUBLICA",
    "RELATORIO DE INTELIGENCIA", "CERTIDAO DE OCORRENCIA", "COMUNICACAO DE OCORRENCIA"
}

# Tipos de vias, logradouros e topônimos
LOCATION_KEYWORDS: Set[str] = {
    "RUA", "AVENIDA", "AV", "TRAVESSA", "BECO", "PASSO", "RODOVIA", "ESTRADA", "ALAMEDA",
    "PRACA", "LARGO", "LOTEAMENTO", "CONDOMINIO", "RESIDENCIAL", "BAIRRO", "VILA", "DISTRITO"
}

# Veículos, armas e termos materiais
OBJECT_KEYWORDS: Set[str] = {
    "CHEVROLET", "VOLKSWAGEN", "FIAT", "FORD", "HYUNDAI", "TOYOTA", "HONDA", "RENAULT", "NISSAN",
    "PISTOLA", "REVOLVER", "ESPINGARDA", "CARABINA", "FUZIL", "TAURUS", "GLOCK", "IMBEL",
    "CALIBRE", "MUNICAO", "ESTOJO", "DROGA", "COCAINA", "MACONHA", "CRACK"
}


# Termos de ocorrências, títulos de crimes e cabeçalhos de fatos
CRIME_KEYWORDS: Set[str] = {
    "LOCAL DO FATO", "HORARIO DO FATO", "QUANDO FOI ENCONTRADA", "TENTATIVA DE HOMICIDIO",
    "HOMICIDIO DOLOSO", "FURTO QUALIFICADO", "ROUBO A", "AMEACA CONTRA", "DISPAROS DE ARMA",
    "VEICULO EM SITUACAO", "ESTUPRO DE VULNERAVEL", "PRISAO EM FLAGRANTE", "OPERACAO CONJUNTA",
    "RELATORIO DE INTELIGENCIA", "CERTIDAO DE OCORRENCIA", "COMUNICACAO DE OCORRENCIA",
    "FORCA TATICA", "SALA DE OPERACOES", "SISTEMA DE INTELIGENCIA"
}

# Órgãos policiais, civis e periciais
CIVIL_POLICE_KEYWORDS: Set[str] = {
    "POLICIA CIVIL", "POLICIAL PENAL", "POLICIAL CIVIL", "DELEGADO", "DELEGADA",
    "AGENTE DA POLICIA", "DELEGACIA DE POLICIA CIVIL", "PERITO", "PERITA", "AGENTE PENITENCIARIO"
}


def normalize_text_for_filter(text: str) -> str:
    """Normaliza texto removendo acentuação e convertendo para maiúsculas."""
    if not text:
        return ""
    nfkd = unicodedata.normalize('NFKD', text)
    ascii_text = ''.join([c for c in nfkd if not unicodedata.combining(c)])
    return re.sub(r'\s+', ' ', ascii_text).strip().upper()


def is_blacklisted_name(name: str) -> bool:
    """
    Verifica se um nome candidato cai em qualquer lista negra (órgãos, patentes, vias, armas, crimes).
    Retorna True caso deva ser descartado imediatamente.
    """
    if not name or len(name.strip()) < 3:
        return True

    normalized = normalize_text_for_filter(name)
    tokens = normalized.split()

    if not tokens:
        return True

    # 1. Verifica patentes e guarnições
    for kw in MILITARY_KEYWORDS:
        norm_kw = normalize_text_for_filter(kw)
        if normalized == norm_kw or normalized.startswith(norm_kw + " ") or f" {norm_kw} " in f" {normalized} ":
            return True

    # 2. Verifica instituições e termos operacionais
    for inst in INSTITUTION_KEYWORDS:
        norm_inst = normalize_text_for_filter(inst)
        if norm_inst in normalized:
            return True

    # 3. Verifica termos de crimes e títulos de seções
    for crime_kw in CRIME_KEYWORDS:
        norm_crime = normalize_text_for_filter(crime_kw)
        if norm_crime in normalized:
            return True

    # 4. Verifica policiais civis e outros agentes públicos
    for pol_kw in CIVIL_POLICE_KEYWORDS:
        norm_pol = normalize_text_for_filter(pol_kw)
        if norm_pol in normalized:
            return True

    # 5. Verifica se inicia com tipo de via ou localização
    if tokens[0] in LOCATION_KEYWORDS:
        return True

    # 6. Verifica marcas de veículos e armas isoladas
    if tokens[0] in OBJECT_KEYWORDS and len(tokens) <= 3:
        return True

    return False
