from abc import ABC, abstractmethod
from typing import List

class IncidentRule(ABC):
    """
    Classe abstrata base para regras de filtragem e extração de ocorrências.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """
        Retorna o nome legível da regra (ex: 'Homicídio').
        """
        pass

    @property
    @abstractmethod
    def db_name(self) -> str:
        """
        Retorna o nome do arquivo do banco de dados correspondente (ex: 'homicides.json').
        """
        pass

    @property
    @abstractmethod
    def keywords(self) -> List[str]:
        """
        Retorna a lista de palavras-chave usadas para a filtragem rápida do texto bruto.
        """
        pass

    @property
    @abstractmethod
    def questions(self) -> dict:
        """
        Retorna as perguntas de linguagem natural mapeadas por chave para o processamento de QA.
        """
        pass

    def validate_qa_results(self, qa_results: dict) -> bool:
        """
        Valida as respostas do QA para confirmar se realmente é o incidente alvo da regra.
        Por padrão, retorna True. Sobrescrever nas subclasses com lógica específica.
        """
        return True



    def matches_filter(self, text: str) -> bool:
        """
        Verifica se o texto contém alguma das palavras-chave configuradas (case-insensitive).
        
        :param text: O texto limpo a ser verificado.
        :return: True se contiver pelo menos uma palavra-chave, False caso contrário.
        """
        if not text:
            return False
        
        text_lower = text.lower()
        for kw in self.keywords:
            if kw.lower() in text_lower:
                return True
        return False
