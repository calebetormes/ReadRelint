from typing import List
from src.domain.rules.base_rule import IncidentRule

class RelintRule(IncidentRule):
    """
    Regra para processar e classificar todos os RELINTs sem descarte.
    """

    @property
    def name(self) -> str:
        return "Relint"

    @property
    def db_name(self) -> str:
        return "relints.json"

    @property
    def keywords(self) -> List[str]:
        # Sem filtragem prévia por palavras-chave, queremos processar todos
        return []

    def matches_filter(self, text: str) -> bool:
        # Aceita todos os textos do PDF
        return True

    @property
    def questions(self) -> dict:
        return {
            "system_prompt": (
                "Você é um Analista de Inteligência Policial. Sua tarefa é analisar o Relatório de Inteligência "
                "(RELINT) fornecido e extrair os dados conforme o esquema JSON obrigatório.\n"
                "ETAPA 1: Ignore cabeçalhos institucionais, marcas d'água e avisos de confidencialidade.\n"
                "ETAPA 2: Extraia os campos com rigor, obedecendo às restrições de formatação e valores listados."
            )
        }

    def validate_qa_results(self, qa_results: dict) -> bool:
        # Não descarta nenhum arquivo após o processamento
        return True

