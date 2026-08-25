# -*- coding: utf-8 -*-
"""
Schema Pydantic estruturado para decomposição e validação de Endereço/Localização.
"""

from typing import Optional
from pydantic import BaseModel, Field


class AddressStructure(BaseModel):
    """Estrutura granular de localização para extração via LLM."""
    street: Optional[str] = Field(None, description="Nome da rua, avenida, rodovia, beco ou estrada.")
    number: Optional[str] = Field(None, description="Número predial do imóvel ou 'S/N'.")
    municipality: Optional[str] = Field(None, description="Nome do município ou cidade do fato.")
    coordinates: Optional[str] = Field(None, description="Coordenadas decimais no formato '-29.xxxx, -51.xxxx'.")
    map_url: Optional[str] = Field(None, description="Link do Google Maps se presente no documento.")
