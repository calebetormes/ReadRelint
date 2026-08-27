# -*- coding: utf-8 -*-
"""
Schema Pydantic estruturado para extração isolada e dedicada de Localização, Endereço e Coordenadas.
"""

from typing import Optional
from pydantic import BaseModel, Field


class LocationExtraction(BaseModel):
    """
    Schema focado exclusivamente na extração da geografia da ocorrência policial.
    """
    street: Optional[str] = Field(
        default=None,
        description="Nome do logradouro onde o fato ocorreu (ex: Rua General Osório, Av. Presidente Vargas, BR-386, Linha Santa Ana)."
    )
    number: Optional[str] = Field(
        default=None,
        description="Número predial do imóvel ou 'S/N' (ou indicação de Km, ex: Km 47)."
    )
    neighborhood: Optional[str] = Field(
        default=None,
        description="Nome do bairro ou localidade rural (ex: Centro, São Cristóvão, Fátima, Interior)."
    )
    municipality: Optional[str] = Field(
        default=None,
        description="Nome da cidade/município da ocorrência (ex: Porto Alegre, Frederico Westphalen, Seberi, Panambi)."
    )
    police_unit: Optional[str] = Field(
        default=None,
        description="Batalhão ou fração da Brigada Militar mencionada/responsável (ex: 39º BPM, 37º BPM, 16º BPM)."
    )
    coordinates: Optional[str] = Field(
        default=None,
        description="Coordenadas decimais de GPS mencionadas no texto no padrão '-29.xxxx, -51.xxxx' ou DMS."
    )
    map_url: Optional[str] = Field(
        default=None,
        description="Link ou URL explícita do Google Maps presente no documento (ex: https://maps.app.goo.gl/...)."
    )
