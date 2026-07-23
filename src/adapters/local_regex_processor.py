import re
from typing import Dict, Optional
from src.ports.llm_processor import ILlmProcessor

class LocalRegexProcessor(ILlmProcessor):
    """
    Processador local baseado em regras Regex e Heurísticas que substitui o uso de LLM (IA).
    """

    def process_text(self, text: str, questions: Optional[Dict[str, str]] = None) -> dict:
        """
        Analisa o texto por meio de padrões de expressões regulares para preencher as informações estruturadas.
        """
        if not questions:
            return {"content": text}

        text_lower = text.lower()
        results = {}

        # 1. Identificar Natureza
        natureza = "não identificado"
        if re.search(r"homic[ií]dio\s+consumado", text_lower):
            natureza = "homicídio consumado"
        elif re.search(r"tentativa\s+de\s+homic[ií]dio|homic[ií]dio\s+tentado", text_lower):
            natureza = "tentativa de homicídio"
        elif re.search(r"feminic[ií]dio\s+consumado", text_lower):
            natureza = "feminicídio consumado"
        elif re.search(r"tentativa\s+de\s+feminic[ií]dio|feminic[ií]dio\s+tentado", text_lower):
            natureza = "tentativa de feminicídio"
        elif re.search(r"feminic[ií]dio", text_lower):
            natureza = "feminicídio"
        elif re.search(r"latroc[ií]nio\s+consumado", text_lower):
            natureza = "latrocínio consumado"
        elif re.search(r"tentativa\s+de\s+latroc[ií]nio|latroc[ií]nio\s+tentado", text_lower):
            natureza = "tentativa de latrocínio"
        elif re.search(r"latroc[ií]nio", text_lower):
            natureza = "latrocínio"
        elif re.search(r"les[aã]o\s+corporal\s+seguida\s+de\s+morte", text_lower):
            natureza = "lesão corporal seguida de morte"
        elif re.search(r"encontro\s+de\s+cad[aá]ver|encontro\s+de\s+corpo", text_lower):
            natureza = "encontro de cadáver"
        elif re.search(r"les[aã]o\s+corporal", text_lower):
            natureza = "lesão corporal"
        elif re.search(r"amea[cç]a", text_lower):
            natureza = "ameaça"
        elif re.search(r"roubo", text_lower):
            natureza = "roubo"

        # 2. Identificar Resultado Morte
        resultado_morte = "não informado"
        death_match = re.search(
            r"(?:veio\s+a\s+[oó]bito|constatado\s+[oó]bito|[oó]bito\s+no\s+local|corpo\s+sem\s+vida|v[ií]tima\s+fatal|\b[oó]bito\b|cad[aá]ver|\bmorte\b|\bmorto\b|\bmorta\b|\bcorpo\b|homic[ií]dio|feminic[ií]dio|latroc[ií]nio|assassinat)",
            text_lower
        )
        if death_match:
            start = max(0, death_match.start() - 30)
            end = min(len(text), death_match.end() + 30)
            snippet = text[start:end].strip().replace("\n", " ")
            if not re.search(r"n[ãa]o\s+houve|sem\s+[oó]bito|negativo", snippet.lower()):
                resultado_morte = f"confirmado ({snippet})"
            else:
                resultado_morte = "negado ou não confirmado"

        for key in questions.keys():
            if key == "natureza":
                results[key] = natureza
            elif key == "resultado_morte":
                results[key] = resultado_morte
            elif key == "content":
                results[key] = text
            else:
                results[key] = ""

        return results
