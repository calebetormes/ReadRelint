from typing import List
from src.domain.rules.base_rule import IncidentRule

class HomicideRule(IncidentRule):
    """
    Regra específica para filtragem e extração de ocorrências de homicídio,
    incluindo feminicídios, latrocínios e encontros de cadáver com sinais de violência.
    """

    @property
    def name(self) -> str:
        return "Homicídio"

    @property
    def db_name(self) -> str:
        return "homicides.json"

    @property
    def keywords(self) -> List[str]:
        return [
            "homicidio", "homicídio", "homicidios", "homicídios",
            "obito", "óbito", "obitos", "óbitos",
            "cadaver", "cadáver", "cadaveres", "cadáveres",
            "assassinato", "assassinatos",
            "morte", "mortes", "morto", "morta", "mortos", "mortas",
            "disparo", "disparos",
            "arma de fogo", "armas de fogo",
            "arma branca", "armas brancas",
            "latrocinio", "latrocínio", "latrocinios", "latrocínios",
            "feminicidio", "feminicídio", "feminicidios", "feminicídios",
            "encontro de cadaver", "encontro de cadáver"
        ]

    def matches_filter(self, text: str) -> bool:
        """
        Verifica se o texto descreve preliminarmente um homicídio ou fato com óbito/violência.
        Busca por termos-chave básicos de homicídio, feminicídio, latrocínio, óbito ou cadáver.
        A validação precisa e detalhada ocorre posteriormente na etapa pós-filtro (validate_qa_results).
        """
        if not text:
            return False

        text_lower = text.lower()
        import re

        # Padrões essenciais de homicídio, mortes violentas e óbito
        target_patterns = [
            r"homic[ií]dio",
            r"feminic[ií]dio",
            r"latroc[ií]nio",
            r"\b[oó]bito\b",
            r"\bcad[aá]ver\b",
            r"assassinat",
            r"\bmorte\b", r"\bmorto\b", r"\bmorta\b",
            r"\bcorpo\b",
            r"alvejado", r"alvejada",
            r"executado", r"executada",
            r"disparo",
            r"arma de fogo",
            r"arma branca"
        ]

        return any(re.search(pat, text_lower) for pat in target_patterns)

    @property
    def questions(self) -> dict:
        return {
            "natureza": "Qual o crime ou fato principal ocorrido?",
            "resultado_morte": "Houve óbito, morte, cadáver ou vítima fatal?",
            "content": "Qual é a descrição resumida dos fatos ocorridos?"
        }

    def validate_qa_results(self, qa_results: dict) -> bool:
        """
        Valida se as respostas extraídas do QA realmente confirmam um homicídio
        ou uma tentativa de homicídio/latrocínio/feminicídio/óbito.
        """
        natureza = qa_results.get("natureza", "").lower()
        resultado_morte = qa_results.get("resultado_morte", "").lower()
        content = qa_results.get("content", "").lower()
        
        # Lista de termos válidos para confirmar
        valid_terms = [
            "homicidio", "homicídio", "óbito", "obito", "cadáver", "cadaver", 
            "morte", "morto", "morta", "assassinado", "assassinada", 
            "latrocínio", "latrocinio", "feminicídio", "feminicidio",
            "encontro de corpo", "corpo sem vida", "vítima fatal", "vitima fatal"
        ]
        
        # Verifica se alguma das palavras-chave de confirmação está presente nas respostas da IA
        has_valid_term = any(
            term in natureza or term in resultado_morte or term in content 
            for term in valid_terms
        )
        
        # Exclusões pós-QA: crimes que não são homicídios/tentativas a menos que haja óbito/morte real confirmado
        exclusions_post = [
            "ameaça", "ameaca",
            "vias de fato",
            "lesão corporal leve", "lesao corporal leve",
            "dano",
            "porte de arma", "porte ilegal",
            "apreensão", "apreensao",
            "furto"
        ]
        
        is_excluded_nature = any(exc in natureza for exc in exclusions_post)
        
        # Se a natureza contiver termos que confirmam diretamente homicídio/morte, não deve cair na exclusão automática
        strong_homicide_terms = ["homicidio", "homicídio", "latrocínio", "latrocinio", "feminicídio", "feminicidio", "óbito", "obito", "cadáver", "cadaver"]
        has_strong_term_in_nature = any(term in natureza for term in strong_homicide_terms)
        
        if is_excluded_nature and not has_strong_term_in_nature:
            # Se a natureza for um crime de exclusão (ex: ameaça ou lesão leve),
            # só aceitamos se houver menção explícita de óbito ou cadáver no resultado ou conteúdo
            has_confirmed_death = any(
                term in resultado_morte for term in ["óbito", "obito", "cadáver", "cadaver", "morto", "morta", "corpo sem vida", "vítima fatal", "vitima fatal"]
            ) or (
                any(term in content for term in ["óbito", "obito", "cadáver", "cadaver", "vítima fatal", "vitima fatal"])
                and not any(neg in content for neg in ["não houve óbito", "não houve obito", "sem óbito", "sem obito"])
            )
            if not has_confirmed_death:
                return False

        # Tratar roubo sem latrocínio
        if "roubo" in natureza and not any(term in natureza or term in resultado_morte for term in ["latrocinio", "latrocínio", "óbito", "obito", "morte", "morto", "morta", "cadáver", "cadaver"]):
            return False
        
        return has_valid_term

