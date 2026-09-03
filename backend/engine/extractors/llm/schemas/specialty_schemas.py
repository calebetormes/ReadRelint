# -*- coding: utf-8 -*-
"""
Schemas Pydantic leves e dedicados para a extração de campos de especialidade
(Passo 3 do Pipeline Multi-Pass). Cada schema contém APENAS os campos que a
classificação determinística de bm_group e os guardrails regex ainda não resolvem
(ex: injured_victims/hostage_victim/location_type/recovered NÃO entram aqui —
são resolvidos deterministicamente em specialty_extractor.py, sem LLM).
"""

from typing import Optional
from pydantic import BaseModel, Field


class HomicideSpecialtyExtraction(BaseModel):
    fact_type: Optional[str] = Field(
        default=None,
        description="Tipo do fato: 'Tentado' ou 'Consumado'. Se não houver certeza, retorne null."
    )
    motivation: Optional[str] = Field(
        default=None,
        description=(
            "Motivação do homicídio. Escolha ESTRITAMENTE uma: 'Feminicídio', "
            "'Envolvimento com o Tráfico', 'Oposição a Ação PM', 'Desavença', 'Latrocídio'. "
            "Se não houver evidência clara no texto, retorne null."
        )
    )


class DrugTraffickingSpecialtyExtraction(BaseModel):
    drug_quantity: Optional[str] = Field(
        default=None,
        description="Quantidade total de entorpecentes apreendidos, exatamente como consta no texto (ex: '500g', '2kg', '5 buchas'). Se não houver, retorne null."
    )
    drug_types: Optional[str] = Field(
        default=None,
        description="Tipos de drogas apreendidas citados no texto (ex: 'Cocaína', 'Maconha', 'Crack'). Se não houver, retorne null."
    )


class EstablishmentRobberySpecialtyExtraction(BaseModel):
    establishment_type: Optional[str] = Field(
        default=None,
        description="Tipo de estabelecimento roubado, exatamente como descrito no texto (ex: 'Farmácia', 'Posto de Combustível', 'Banco'). Se não houver, retorne null."
    )


class VehicleSpecialtyExtraction(BaseModel):
    """Reutilizado tanto para Roubo de Veículo quanto para Furto de Veículo."""
    vehicle_model: Optional[str] = Field(
        default=None,
        description="Marca e modelo do veículo, exatamente como consta no texto. Se não houver, retorne null."
    )
    license_plate: Optional[str] = Field(
        default=None,
        description="Placa do veículo, exatamente como consta no texto. Se não houver, retorne null."
    )
    recovery_location: Optional[str] = Field(
        default=None,
        description="Local ou endereço de recuperação do veículo, apenas se o texto confirmar que ele foi recuperado. Se não houver, retorne null."
    )


class PedestrianRobberySpecialtyExtraction(BaseModel):
    weapon_used: Optional[str] = Field(
        default=None,
        description="Arma utilizada no roubo. Escolha ESTRITAMENTE uma: 'Arma de fogo', 'Arma branca', 'Agressão física'. Se não houver certeza, retorne null."
    )
    stolen_object: Optional[str] = Field(
        default=None,
        description="Objeto(s) roubado(s) da vítima, exatamente como descrito no texto (ex: celular, carteira, bolsa). Se não houver, retorne null."
    )
