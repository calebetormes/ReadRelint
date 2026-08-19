"""
Schemas Pydantic para os endpoints da API REST dos RELINTs em Português e Inglês com suporte a propriedades duplas.
"""
from typing import List, Optional, Any, Dict
from pydantic import BaseModel, Field, AliasChoices, computed_field

class ParticipantDTO(BaseModel):
    """Informações de um participante no RELINT."""
    model_config = {"populate_by_name": True}

    name: str = Field(validation_alias=AliasChoices("name", "nome"))
    nickname: Optional[str] = Field(default="", validation_alias=AliasChoices("nickname", "alcunha"))
    document: Optional[str] = Field(default="", validation_alias=AliasChoices("document", "documento"))
    background: Optional[str] = Field(default="", validation_alias=AliasChoices("background", "antecedentes"))
    participation_type: Optional[str] = Field(default="Acusado", validation_alias=AliasChoices("participation_type", "tipo_participacao"))
    photo_path: Optional[str] = Field(default="", validation_alias=AliasChoices("photo_path", "caminho_foto"))

    @computed_field
    @property
    def nome(self) -> str:
        return self.name

    @computed_field
    @property
    def alcunha(self) -> str:
        return self.nickname or ""

    @computed_field
    @property
    def documento(self) -> str:
        return self.document or ""

    @computed_field
    @property
    def antecedentes(self) -> str:
        return self.background or ""

    @computed_field
    @property
    def tipo_participacao(self) -> str:
        return self.participation_type or "Acusado"

    @computed_field
    @property
    def caminho_foto(self) -> str:
        return self.photo_path or ""


class RelintSummaryResponse(BaseModel):
    """Representação resumida de um RELINT para listagem/tabela."""
    model_config = {"populate_by_name": True}

    id: str
    source_file: str = Field(validation_alias=AliasChoices("source_file", "arquivo_origem"))
    registry_number: Optional[str] = Field(default="", validation_alias=AliasChoices("registry_number", "numero_registro"))
    registry_agency: Optional[str] = Field(default="", validation_alias=AliasChoices("registry_agency", "orgao_registro"))
    registry_year: Optional[str] = Field(default="", validation_alias=AliasChoices("registry_year", "ano_registro"))
    subject: Optional[str] = Field(default="", validation_alias=AliasChoices("subject", "assunto"))
    date_of_fact: Optional[str] = Field(default="", validation_alias=AliasChoices("date_of_fact", "data_fato"))
    time_of_fact: Optional[str] = Field(default="", validation_alias=AliasChoices("time_of_fact", "hora_fato"))
    bm_group: Optional[str] = Field(default="Outros", validation_alias=AliasChoices("bm_group", "grupo_bm"))
    relint_type: Optional[str] = Field(default="Outros", validation_alias=AliasChoices("relint_type", "tipo_relint"))
    municipality: Optional[str] = Field(default="", validation_alias=AliasChoices("municipality", "municipio"))
    neighborhood: Optional[str] = Field(default="", validation_alias=AliasChoices("neighborhood", "bairro"))
    police_unit: Optional[str] = Field(default="", validation_alias=AliasChoices("police_unit", "unidade_policial"))
    summary: Optional[str] = Field(default="", validation_alias=AliasChoices("summary", "resumo"))
    extraction_method: Optional[str] = Field(default="Regex (Sem IA)", validation_alias=AliasChoices("extraction_method", "metodo_extracao"))
    participants: Optional[List[ParticipantDTO]] = Field(default_factory=list, validation_alias=AliasChoices("participants", "participantes"))
    participants_count: int = Field(default=0, validation_alias=AliasChoices("participants_count", "total_participantes"))
    images_count: int = Field(default=0, validation_alias=AliasChoices("images_count", "total_imagens"))
    user_edited: bool = Field(default=False, validation_alias=AliasChoices("user_edited", "editado_usuario"))

    @computed_field
    @property
    def arquivo_origem(self) -> str:
        return self.source_file

    @computed_field
    @property
    def numero_registro(self) -> str:
        return self.registry_number or ""

    @computed_field
    @property
    def orgao_registro(self) -> str:
        return self.registry_agency or ""

    @computed_field
    @property
    def ano_registro(self) -> str:
        return self.registry_year or ""

    @computed_field
    @property
    def assunto(self) -> str:
        return self.subject or ""

    @computed_field
    @property
    def data_fato(self) -> str:
        return self.date_of_fact or ""

    @computed_field
    @property
    def hora_fato(self) -> str:
        return self.time_of_fact or ""

    @computed_field
    @property
    def grupo_bm(self) -> str:
        return self.bm_group or "Outros"

    @computed_field
    @property
    def tipo_relint(self) -> str:
        return self.relint_type or "Outros"

    @computed_field
    @property
    def municipio(self) -> str:
        return self.municipality or ""

    @computed_field
    @property
    def bairro(self) -> str:
        return self.neighborhood or ""

    @computed_field
    @property
    def unidade_policial(self) -> str:
        return self.police_unit or ""

    @computed_field
    @property
    def resumo(self) -> str:
        return self.summary or ""

    @computed_field
    @property
    def metodo_extracao(self) -> str:
        return self.extraction_method or "Regex (Sem IA)"

    @computed_field
    @property
    def participantes(self) -> List[ParticipantDTO]:
        return self.participants or []

    @computed_field
    @property
    def total_participantes(self) -> int:
        return self.participants_count

    @computed_field
    @property
    def total_imagens(self) -> int:
        return self.images_count

    @computed_field
    @property
    def editado_usuario(self) -> bool:
        return self.user_edited


class RelintDetailResponse(BaseModel):
    """Representação detalhada completa de um IncidentReport."""
    model_config = {"extra": "allow", "populate_by_name": True}
    
    id: str
    source_file: str = Field(validation_alias=AliasChoices("source_file", "arquivo_origem"))
    registry_number: Optional[str] = Field(default="", validation_alias=AliasChoices("registry_number", "numero_registro"))
    registry_agency: Optional[str] = Field(default="", validation_alias=AliasChoices("registry_agency", "orgao_registro"))
    registry_year: Optional[str] = Field(default="", validation_alias=AliasChoices("registry_year", "ano_registro"))
    subject: Optional[str] = Field(default="", validation_alias=AliasChoices("subject", "assunto"))
    main_fact: Optional[str] = Field(default="", validation_alias=AliasChoices("main_fact", "fato_principal"))
    date_of_fact: Optional[str] = Field(default="", validation_alias=AliasChoices("date_of_fact", "data_fato"))
    time_of_fact: Optional[str] = Field(default="", validation_alias=AliasChoices("time_of_fact", "hora_fato"))
    bm_group: Optional[str] = Field(default="Outros", validation_alias=AliasChoices("bm_group", "grupo_bm"))
    relint_type: Optional[str] = Field(default="Outros", validation_alias=AliasChoices("relint_type", "tipo_relint"))
    municipality: Optional[str] = Field(default="", validation_alias=AliasChoices("municipality", "municipio"))
    neighborhood: Optional[str] = Field(default="", validation_alias=AliasChoices("neighborhood", "bairro"))
    address: Optional[str] = Field(default="", validation_alias=AliasChoices("address", "endereco"))
    police_unit: Optional[str] = Field(default="", validation_alias=AliasChoices("police_unit", "unidade_policial"))
    coordinates: Optional[str] = Field(default="", validation_alias=AliasChoices("coordinates", "coordenadas"))
    map_url: Optional[str] = Field(default="", validation_alias=AliasChoices("map_url", "url_mapa"))
    precision_level: Optional[str] = "unknown"
    precision_label: Optional[str] = "Sem Dados de Localização"
    summary: Optional[str] = Field(default="", validation_alias=AliasChoices("summary", "resumo"))
    content: Optional[str] = Field(default="", validation_alias=AliasChoices("content", "conteudo"))
    extraction_method: Optional[str] = Field(default="Regex (Sem IA)", validation_alias=AliasChoices("extraction_method", "metodo_extracao"))
    user_edited: bool = Field(default=False, validation_alias=AliasChoices("user_edited", "editado_usuario"))
    images: List[Dict[str, Any]] = Field(default_factory=list, validation_alias=AliasChoices("images", "imagens"))
    participants: List[ParticipantDTO] = Field(default_factory=list, validation_alias=AliasChoices("participants", "participantes"))
    homicide_details: Optional[Any] = Field(default=None, validation_alias=AliasChoices("homicide_details", "homicidio_detalhes"))
    drug_trafficking_details: Optional[Any] = Field(default=None, validation_alias=AliasChoices("drug_trafficking_details", "trafico_detalhes"))
    establishment_robbery_details: Optional[Any] = Field(default=None, validation_alias=AliasChoices("establishment_robbery_details", "roubo_estabelecimento_detalhes"))
    residence_robbery_details: Optional[Any] = Field(default=None, validation_alias=AliasChoices("residence_robbery_details", "roubo_residencia_detalhes"))
    vehicle_robbery_details: Optional[Any] = Field(default=None, validation_alias=AliasChoices("vehicle_robbery_details", "roubo_veiculo_detalhes"))
    pedestrian_robbery_details: Optional[Any] = Field(default=None, validation_alias=AliasChoices("pedestrian_robbery_details", "roubo_pedestre_detalhes"))
    vehicle_theft_details: Optional[Any] = Field(default=None, validation_alias=AliasChoices("vehicle_theft_details", "furto_veiculo_detalhes"))
    @computed_field
    @property
    def arquivo_origem(self) -> str:
        return self.source_file

    @computed_field
    @property
    def numero_registro(self) -> str:
        return self.registry_number or ""

    @computed_field
    @property
    def orgao_registro(self) -> str:
        return self.registry_agency or ""

    @computed_field
    @property
    def ano_registro(self) -> str:
        return self.registry_year or ""

    @computed_field
    @property
    def assunto(self) -> str:
        return self.subject or ""

    @computed_field
    @property
    def fato_principal(self) -> str:
        return self.main_fact or ""

    @computed_field
    @property
    def data_fato(self) -> str:
        return self.date_of_fact or ""

    @computed_field
    @property
    def hora_fato(self) -> str:
        return self.time_of_fact or ""

    @computed_field
    @property
    def grupo_bm(self) -> str:
        return self.bm_group or "Outros"

    @computed_field
    @property
    def tipo_relint(self) -> str:
        return self.relint_type or "Outros"

    @computed_field
    @property
    def municipio(self) -> str:
        return self.municipality or ""

    @computed_field
    @property
    def bairro(self) -> str:
        return self.neighborhood or ""

    @computed_field
    @property
    def endereco(self) -> str:
        return self.address or ""

    @computed_field
    @property
    def unidade_policial(self) -> str:
        return self.police_unit or ""

    @computed_field
    @property
    def coordenadas(self) -> str:
        return self.coordinates or ""

    @computed_field
    @property
    def url_mapa(self) -> str:
        return self.map_url or ""

    @computed_field
    @property
    def resumo(self) -> str:
        return self.summary or ""

    @computed_field
    @property
    def conteudo(self) -> str:
        return self.content or ""

    @computed_field
    @property
    def metodo_extracao(self) -> str:
        return self.extraction_method or "Regex (Sem IA)"

    @computed_field
    @property
    def editado_usuario(self) -> bool:
        return self.user_edited

    @computed_field
    @property
    def imagens(self) -> List[Dict[str, Any]]:
        return self.images or []

    @computed_field
    @property
    def participantes(self) -> List[ParticipantDTO]:
        return self.participants or []


class HomicideUpdateDTO(BaseModel):
    """Detalhes específicos para Homicídio."""
    model_config = {"populate_by_name": True}

    registry_number: Optional[str] = Field(default=None, validation_alias=AliasChoices("registry_number", "numero_registro"))
    registry_agency: Optional[str] = Field(default=None, validation_alias=AliasChoices("registry_agency", "orgao_registro"))
    registry_year: Optional[str] = Field(default=None, validation_alias=AliasChoices("registry_year", "ano_registro"))
    fact_type: Optional[str] = Field(default="", validation_alias=AliasChoices("fact_type", "tipo_fato"))
    motivation: Optional[str] = Field(default="Desconhecido", validation_alias=AliasChoices("motivation", "motivacao"))


class DrugTraffickingUpdateDTO(BaseModel):
    model_config = {"populate_by_name": True}
    drug_quantity: Optional[str] = Field(default=None, validation_alias=AliasChoices("drug_quantity", "quantidade_drogas"))
    drug_types: Optional[str] = Field(default=None, validation_alias=AliasChoices("drug_types", "tipo_drogas"))


class EstablishmentRobberyUpdateDTO(BaseModel):
    model_config = {"populate_by_name": True}
    establishment_type: Optional[str] = Field(default=None, validation_alias=AliasChoices("establishment_type", "tipo_estabelecimento"))
    location_type: Optional[str] = Field(default="Urbano", validation_alias=AliasChoices("location_type", "tipo_local"))
    injured_victims: Optional[int] = Field(default=0, validation_alias=AliasChoices("injured_victims", "vitimas_lesionadas"))
    hostage_victim: Optional[int] = Field(default=0, validation_alias=AliasChoices("hostage_victim", "vitima_refem"))


class ResidenceRobberyUpdateDTO(BaseModel):
    model_config = {"populate_by_name": True}
    location_type: Optional[str] = Field(default="Urbano", validation_alias=AliasChoices("location_type", "tipo_local"))
    injured_victims: Optional[int] = Field(default=0, validation_alias=AliasChoices("injured_victims", "vitimas_lesionadas"))
    hostage_victim: Optional[int] = Field(default=0, validation_alias=AliasChoices("hostage_victim", "vitima_refem"))


class VehicleRobberyUpdateDTO(BaseModel):
    model_config = {"populate_by_name": True}
    vehicle_model: Optional[str] = Field(default=None, validation_alias=AliasChoices("vehicle_model", "modelo_veiculo"))
    license_plate: Optional[str] = Field(default=None, validation_alias=AliasChoices("license_plate", "placa"))
    recovered: Optional[int] = Field(default=0, validation_alias=AliasChoices("recovered", "recuperado"))
    recovery_location: Optional[str] = Field(default=None, validation_alias=AliasChoices("recovery_location", "local_recuperacao"))


class PedestrianRobberyUpdateDTO(BaseModel):
    model_config = {"populate_by_name": True}
    injured_victims: Optional[int] = Field(default=0, validation_alias=AliasChoices("injured_victims", "vitimas_lesionadas"))
    weapon_used: Optional[str] = Field(default=None, validation_alias=AliasChoices("weapon_used", "arma_utilizada"))
    stolen_object: Optional[str] = Field(default=None, validation_alias=AliasChoices("stolen_object", "objeto_roubado"))


class VehicleTheftUpdateDTO(BaseModel):
    model_config = {"populate_by_name": True}
    vehicle_model: Optional[str] = Field(default=None, validation_alias=AliasChoices("vehicle_model", "modelo_veiculo"))
    license_plate: Optional[str] = Field(default=None, validation_alias=AliasChoices("license_plate", "placa"))
    recovered: Optional[int] = Field(default=0, validation_alias=AliasChoices("recovered", "recuperado"))
    recovery_location: Optional[str] = Field(default=None, validation_alias=AliasChoices("recovery_location", "local_recuperacao"))


class RelintUpdateRequest(BaseModel):
    """Payload para atualização de um RELINT existente."""
    model_config = {"extra": "allow", "populate_by_name": True}

    registry_number: Optional[str] = Field(default=None, validation_alias=AliasChoices("registry_number", "numero_registro"))
    registry_agency: Optional[str] = Field(default=None, validation_alias=AliasChoices("registry_agency", "orgao_registro"))
    registry_year: Optional[str] = Field(default=None, validation_alias=AliasChoices("registry_year", "ano_registro"))
    subject: Optional[str] = Field(default=None, validation_alias=AliasChoices("subject", "assunto"))
    main_fact: Optional[str] = Field(default=None, validation_alias=AliasChoices("main_fact", "fato_principal"))
    date_of_fact: Optional[str] = Field(default=None, validation_alias=AliasChoices("date_of_fact", "data_fato"))
    time_of_fact: Optional[str] = Field(default=None, validation_alias=AliasChoices("time_of_fact", "hora_fato"))
    bm_group: Optional[str] = Field(default=None, validation_alias=AliasChoices("bm_group", "grupo_bm"))
    relint_type: Optional[str] = Field(default=None, validation_alias=AliasChoices("relint_type", "tipo_relint"))
    municipality: Optional[str] = Field(default=None, validation_alias=AliasChoices("municipality", "municipio"))
    neighborhood: Optional[str] = Field(default=None, validation_alias=AliasChoices("neighborhood", "bairro"))
    address: Optional[str] = Field(default=None, validation_alias=AliasChoices("address", "endereco"))
    police_unit: Optional[str] = Field(default=None, validation_alias=AliasChoices("police_unit", "unidade_policial"))
    coordinates: Optional[str] = Field(default=None, validation_alias=AliasChoices("coordinates", "coordenadas"))
    map_url: Optional[str] = Field(default=None, validation_alias=AliasChoices("map_url", "url_mapa"))
    summary: Optional[str] = Field(default=None, validation_alias=AliasChoices("summary", "resumo"))
    content: Optional[str] = Field(default=None, validation_alias=AliasChoices("content", "conteudo"))
    homicide_details: Optional[HomicideUpdateDTO] = Field(default=None, validation_alias=AliasChoices("homicide_details", "homicidio_detalhes"))
    drug_trafficking_details: Optional[DrugTraffickingUpdateDTO] = Field(default=None, validation_alias=AliasChoices("drug_trafficking_details", "trafico_detalhes"))
    establishment_robbery_details: Optional[EstablishmentRobberyUpdateDTO] = Field(default=None, validation_alias=AliasChoices("establishment_robbery_details", "roubo_estabelecimento_detalhes"))
    residence_robbery_details: Optional[ResidenceRobberyUpdateDTO] = Field(default=None, validation_alias=AliasChoices("residence_robbery_details", "roubo_residencia_detalhes"))
    vehicle_robbery_details: Optional[VehicleRobberyUpdateDTO] = Field(default=None, validation_alias=AliasChoices("vehicle_robbery_details", "roubo_veiculo_detalhes"))
    pedestrian_robbery_details: Optional[PedestrianRobberyUpdateDTO] = Field(default=None, validation_alias=AliasChoices("pedestrian_robbery_details", "roubo_pedestre_detalhes"))
    vehicle_theft_details: Optional[VehicleTheftUpdateDTO] = Field(default=None, validation_alias=AliasChoices("vehicle_theft_details", "furto_veiculo_detalhes"))
    participants: Optional[List[ParticipantDTO]] = Field(default=None, validation_alias=AliasChoices("participants", "participantes"))
    specialty_data: Optional[Dict[str, Any]] = Field(default=None, validation_alias=AliasChoices("specialty_data", "dados_especialidade"))
