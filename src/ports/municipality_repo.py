from abc import ABC, abstractmethod
from typing import List, Optional
from src.domain.entities import Municipality

class IMunicipalityRepo(ABC):
    """
    Interface para o repositório de Municípios (Mancha Criminal unificada).
    """

    @abstractmethod
    def save(self, municipality: Municipality) -> str:
        """Salva um novo município."""
        pass

    @abstractmethod
    def update(self, municipality: Municipality) -> None:
        """Atualiza um município existente."""
        pass

    @abstractmethod
    def get_by_name(self, name: str) -> Optional[Municipality]:
        """Busca um município pelo nome exato (case-insensitive)."""
        pass

    @abstractmethod
    def get_all(self) -> List[Municipality]:
        """Retorna todos os municípios cadastrados."""
        pass
