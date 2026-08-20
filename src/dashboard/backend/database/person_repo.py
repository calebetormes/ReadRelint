from abc import ABC, abstractmethod
from typing import List, Optional
from src.dashboard.backend.core.entities import Person

class IPersonRepo(ABC):
    """
    Interface para o repositório de Pessoas (Participantes unificados).
    """

    @abstractmethod
    def save(self, person: Person) -> str:
        """Salva uma nova pessoa."""
        pass

    @abstractmethod
    def update(self, person: Person) -> None:
        """Atualiza uma pessoa existente."""
        pass

    @abstractmethod
    def get_by_id(self, person_id: str) -> Optional[Person]:
        """Busca uma pessoa pelo ID."""
        pass

    @abstractmethod
    def get_by_document(self, document: str) -> Optional[Person]:
        """Busca uma pessoa pelo documento (CPF/RG)."""
        pass

    @abstractmethod
    def get_all(self) -> List[Person]:
        """Retorna todas as pessoas cadastradas."""
        pass
