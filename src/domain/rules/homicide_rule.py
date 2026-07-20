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
        Verifica se o texto descreve um homicídio ou tentativa legítima no fato principal atual.
        1. Trunca o texto antes do histórico de antecedentes criminais dos envolvidos.
        2. Procura termos-chave de homicídio/latrocínio/feminicídio/óbito/cadáver.
        3. Se contiver termos de exclusão (como lesão corporal, ameaça ou apreensão),
           exige a presença de termos de confirmação explícita de óbito ou tentativa de homicídio.
        """
        if not text:
            return False

        text_lower = text.lower()

        # 1. Truncar texto antes das seções de antecedentes e históricos criminais
        antecedent_patterns = [
            r"antecedentes\s+criminais",
            r"hist[oó]rico\s+criminal",
            r"registros\s+policiais",
            r"ocorr[eê]ncias\s+anteriores",
            r"passagens\s+policiais",
            r"prontu[aá]rio",
            r"outros\s+fatos",
            r"outras\s+ocorr[eê]ncias",
            r"consulta\s+integrada",
            r"antecedentes\s+de",
            r"possui\s+registro",
            r"registro\s+de\s+outras",
            r"hist[oó]rico\s+de\s+ocorr[eê]ncias"
        ]

        import re
        first_antecedent_idx = len(text_lower)
        for pattern in antecedent_patterns:
            match = re.search(pattern, text_lower)
            if match:
                first_antecedent_idx = min(first_antecedent_idx, match.start())

        current_fact_text = text_lower[:first_antecedent_idx]

        # 2. Exclusões Rápidas: Crimes que NÃO são homicídios/tentativas por padrão
        # (mas que podem conter palavras-chave como disparo, arma ou morte)
        exclusions = [
            r"les[aã]o\s+corporal",
            r"ferimentos\s+superficiais",
            r"amea[cç]a",
            r"uso\s+de\s+ainm",
            r"impo",
            r"apreens[aã]o\s+de\s+objeto",
            r"investiga[cç][aã]o\s+social",
            r"resposta\s+ao\s+pb",
            r"resposta\s+ao\s+pedido\s+de\s+busca",
            r"porte\s+ilegal",
            r"repasse\s+disque\s+den[uú]ncia",
            r"sem\s+conte[uú]do\s+dispon[ií]vel"
        ]

        # 3. Termos fortes que confirmam de fato um óbito ou uma legítima tentativa de assassinato
        strong_confirmations = [
            r"homic[ií]dio\s+consumado",
            r"tentativa\s+de\s+homic[ií]dio",
            r"homic[ií]dio\s+tentado",
            r"feminic[ií]dio\s+consumado",
            r"tentativa\s+de\s+feminic[ií]dio",
            r"feminic[ií]dio\s+tentado",
            r"latroc[ií]nio\s+consumado",
            r"tentativa\s+de\s+latroc[ií]nio",
            r"latroc[ií]nio\s+tentado",
            r"veio\s+a\s+[oó]bito",
            r"encontro\s+de\s+cad[aá]ver",
            r"encontro\s+de\s+corpo",
            r"corpo\s+sem\s+vida",
            r"v[ií]tima\s+fatal",
            r"assassinado",
            r"assassinada",
            r"encontrado\s+morto",
            r"encontrada\s+morta",
            r"[oó]bito\s+no\s+local",
            r"encontrou\s+morto",
            r"encontrou\s+morta"
        ]

        # Se houver um termo de exclusão rápida no fato atual
        has_exclusion = any(re.search(exc, current_fact_text) for exc in exclusions)
        if has_exclusion:
            # Só aceita se houver confirmação explícita de óbito ou de tentativa de homicídio/feminicídio/latrocínio no fato atual
            return any(re.search(conf, current_fact_text) for conf in strong_confirmations)

        # 4. Caso contrário, verifica se tem ao menos uma palavra-chave básica de homicídio/óbito/cadáver/morte
        # (evita falsos positivos de furtos/roubos que não envolvem morte)
        primary_keywords = [
            r"homic[ií]dio",
            r"latroc[ií]nio",
            r"feminic[ií]dio",
            r"cad[aá]ver",
            r"[oó]bito",
            r"assassinat",
            r"morte\s+violenta"
        ]
        
        # Aceita se contiver palavra-chave primária OU se for uma tentativa explícita
        has_primary = any(re.search(kw, current_fact_text) for kw in primary_keywords)
        if has_primary:
            return True
            
        return any(re.search(conf, current_fact_text) for conf in strong_confirmations)

    @property
    def questions(self) -> dict:
        return {
            "natureza": "Qual o crime ou fato principal ocorrido?",
            "content": "Qual é a descrição resumida dos fatos ocorridos?"
        }

    def validate_qa_results(self, qa_results: dict) -> bool:
        """
        Valida se as respostas extraídas do QA realmente confirmam um homicídio
        ou uma tentativa de homicídio/latrocínio/feminicídio/óbito.
        """
        natureza = qa_results.get("natureza", "").lower()
        content = qa_results.get("content", "").lower()
        
        # Lista de termos válidos para confirmar
        valid_terms = [
            "homicidio", "homicídio", "óbito", "obito", "cadáver", "cadaver", 
            "morte", "morto", "morta", "assassinado", "assassinada", 
            "latrocínio", "latrocinio", "feminicídio", "feminicidio"
        ]
        
        # Verifica se alguma das palavras-chave de confirmação está presente na resposta de natureza ou de conteúdo
        return any(term in natureza or term in content for term in valid_terms)

