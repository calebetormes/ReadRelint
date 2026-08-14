from typing import Optional, List, Dict, Any, Union
from enum import Enum
from datetime import datetime
from pydantic import BaseModel, Field, field_validator, model_validator


class ParticipationType(str, Enum):
    VITIMA = "Vítima"
    TESTEMUNHA = "Testemunha"
    ACUSADO = "Acusado"
    SUSPEITO = "Suspeito"
    GUARNICAO = "Parte da Guarnição"


class BmGroup(str, Enum):
    ROUBO_ESTABELECIMENTO = "Roubo a Estabelecimento"
    ROUBO_RESIDENCIA = "Roubo a Residência"
    ROUBO_VEICULO = "Roubo de Veículo"
    ROUBO_PEDESTRE = "Roubo a Pedestre"
    FURTO_QUALIFICADO = "Furto Qualificado"
    FURTO_VEICULO = "Furto de Veículo"
    PRISAO_TRAFICO = "Prisão por Tráfico"
    HOMICIDIO = "Homicídio"
    OUTROS = "Outros"


class RelintType(str, Enum):
    OCORRENCIA = "Ocorrência"
    DISK_DENUNCIA = "Disk Denúncia"
    RESPOSTA_PB = "Resposta a PB"
    OUTROS = "Outros"


class HomicideMotivation(str, Enum):
    FEMINICIDIO = "Feminicídio"
    TRAFICO = "Envolvimento com o Tráfico"
    OPOSICAO_PM = "Oposição a Ação PM"
    DESAVENCA = "Desavença"
    LATROCINIO = "Latrocídio"
    DESCONHECIDO = "Desconhecido"


class Participant(BaseModel):
    """
    Representa um participante citado no RELINT, formatado para extração LLM.
    """
    name: Optional[str] = Field(default=None, description="Nome completo da pessoa")
    nickname: Optional[str] = Field(default=None, description="Alcunha, apelido ou vulgo")
    document: Optional[str] = Field(default=None, description="Documento de identificação (CPF ou RG)")
    background: Optional[str] = Field(default=None, description="Antecedentes mencionados (se houver)")
    participation_type: Optional[Union[ParticipationType, str]] = Field(default="Acusado", description="Opções: Vítima, Testemunha, Acusado, Suspeito, Parte da Guarnição")
    photo_path: Optional[str] = Field(default=None, description="Caminho do arquivo da foto do participante")

    @field_validator("participation_type", mode="before")
    @classmethod
    def normalize_participation_type(cls, v):
        if not v:
            return "Acusado"
        if hasattr(v, "value"):
            return v.value
        val_str = str(v).strip()
        lower = val_str.lower()
        if "vitima" in lower or "vítima" in lower:
            return "Vítima"
        if "testemunha" in lower:
            return "Testemunha"
        if "suspeito" in lower:
            return "Suspeito"
        if any(w in lower for w in ["acusado", "autor", "indiciado", "reu", "réu"]):
            return "Acusado"
        if any(w in lower for w in ["guarnicao", "guarnição", "pm", "policial"]):
            return "Parte da Guarnição"
        return val_str.title() if val_str else "Acusado"


class IncidentReport(BaseModel):
    """
    Representa a entidade de domínio de um relatório de inteligência (RELINT) processado.
    """
    id: Optional[str] = Field(default=None, description="ID único no banco de dados")
    source_file: str = Field(description="Nome do arquivo PDF de origem")
    date_of_fact: Optional[str] = Field(default=None, description="Extraia a data de ocorrência do fato (ex: DD/MM/AAAA ou DD de mês de AAAA) mencionada na introdução ou primeira frase do histórico")
    time_of_fact: Optional[str] = Field(default=None, description="Extraia a hora exata ou aproximada do fato (ex: 14h30min, 01:30h, por volta das 18h) mencionada no primeiro parágrafo")
    modification_date_history: Optional[str] = Field(default=None, description="Mapear a sequência/histórico de datas de alteração do arquivo ou data do fato")

    subject: Optional[str] = Field(default=None, description="Extraia exatamente o texto do campo ASSUNTO: presente na seção introdutória do RELINT")
    main_fact: Optional[str] = Field(default=None, description="Determine a partir do Assunto qual é o evento central do relatório")
    relint_type: Optional[Union[RelintType, str]] = Field(default="Outros", description="Classifique em Ocorrência, Disk Denúncia, Resposta a PB ou Outros")
    bm_group: Optional[Union[BmGroup, str]] = Field(default="Outros", description="Escolha uma das opções: Roubo a Estabelecimento, Roubo a Residência, Roubo de Veículo, Roubo a Pedestre, Furto Qualificado, Furto de Veículo, Prisão por Tráfico, Homicídio, Outros")
    location_types: Optional[List[str]] = Field(default=[], description="Identifique o local do fato (ex: Propriedade Rural, Escolas, Residência)")
    participants: Optional[List[Participant]] = Field(default=[], description="Lista de pessoas de interesse citadas (vítimas, suspeitos, acusados, testemunhas). NUNCA inclua Policiais Militares da guarnição que atenderam o fato.")
    address: Optional[str] = Field(default=None, description="Endereço completo mencionado no fato")
    municipality: Optional[str] = Field(default=None, description="Nome da cidade/município da ocorrência (ex: Panambi, Palmeira das Missões, Ibirubá)")
    street: Optional[str] = Field(default=None, description="Nome do logradouro/rua/avenida da ocorrência (ex: Rua Oscar Waeschter, Av. Brasil)")
    number: Optional[str] = Field(default=None, description="Número do imóvel ou S/N")
    neighborhood: Optional[str] = Field(default=None, description="Nome do bairro da ocorrência (ex: Arco-Íris, Centro)")
    map_url: Optional[str] = Field(default=None, description="URL ou link do Google Maps presente no texto")
    coordinates: Optional[str] = Field(default=None, description="Coordenadas geográficas no formato Latitude, Longitude (ex: -28.2612, -53.4912)")
    images: Optional[List[Union[str, Dict[str, Any]]]] = Field(default=[], description="Lista de caminhos ou objetos de imagens do fato/local com legenda")

    content: Optional[str] = Field(default=None, description="Histórico completo e literal do RELINT")
    summary: Optional[str] = Field(default=None, description="Escreva um resumo claro e explicativo dos fatos descritos no RELINT em 1 parágrafo")
    user_edited: bool = Field(default=False, description="Indica se o relatório foi editado manualmente pelo usuário")

    @field_validator("relint_type", mode="before")
    @classmethod
    def normalize_relint_type(cls, v):
        if not v:
            return "Outros"
        if hasattr(v, "value"):
            return v.value
        val = str(v).strip()
        lower = val.lower()
        if "ocorrencia" in lower or "ocorrência" in lower:
            return "Ocorrência"
        if "disk" in lower or "denuncia" in lower or "denúncia" in lower:
            return "Disk Denúncia"
        if "resposta" in lower or "pb" in lower:
            return "Resposta a PB"
        return val.title() if val else "Outros"

    @field_validator("bm_group", mode="before")
    @classmethod
    def normalize_bm_group(cls, v):
        if not v:
            return "Outros"
        if hasattr(v, "value"):
            return v.value
        val = str(v).strip()
        lower = val.lower()
        if "homicid" in lower:
            return "Homicídio"
        if "trafico" in lower or "tráfico" in lower:
            return "Prisão por Tráfico"
        if "estabelecimento" in lower:
            return "Roubo a Estabelecimento"
        if "residencia" in lower or "residência" in lower:
            return "Roubo a Residência"
        if "veiculo" in lower or "veículo" in lower:
            if "furto" in lower:
                return "Furto de Veículo"
            return "Roubo de Veículo"
        if "pedestre" in lower:
            return "Roubo a Pedestre"
        if "furto" in lower:
            return "Furto Qualificado"
        return val.title() if val else "Outros"


class HomicideReport(IncidentReport):
    """
    Entidade especializada para relatórios de homicídio.
    """
    registry_number: Optional[str] = Field(default=None, description="Número do registro Policial ou DP (ex: 516/151641/2026)")
    registry_agency: Optional[str] = Field(default=None, description="Órgão de Registro Policial (ex: DP)")
    registry_year: Optional[str] = Field(default=None, description="Ano de registro Policial (ex: 2026)")
    fact_type: Optional[str] = Field(default=None, description="Determine o Tipo de Fato (Tentado ou Consumado)")
    police_unit: Optional[str] = Field(default=None, description="Identifique a Unidade Policial Militar (ex: 16BPM, 37BPM, 39BPM)")
    motivation: Optional[Union[HomicideMotivation, str]] = Field(default="Desconhecido", description="Determine a Motivação baseada nas opções fornecidas")

    @field_validator("motivation", mode="before")
    @classmethod
    def normalize_motivation(cls, v):
        if not v:
            return "Desconhecido"
        if hasattr(v, "value"):
            return v.value
        val = str(v).strip()
        lower = val.lower()
        if "feminicidio" in lower or "feminicídio" in lower:
            return "Feminicídio"
        if "trafico" in lower or "tráfico" in lower:
            return "Envolvimento com o Tráfico"
        if "oposicao" in lower or "oposição" in lower or "pm" in lower:
            return "Oposição a Ação PM"
        if "desavenca" in lower or "desavença" in lower:
            return "Desavença"
        if "latrocinio" in lower or "latrocínio" in lower:
            return "Latrocídio"
        return val.title() if val else "Desconhecido"


class Person(BaseModel):
    """
    Representa a entidade agregada e única de um Participante ao longo de vários RELINTs.
    """
    person_id: str = Field(description="Chave única de identificação baseada no nome ou documento")
    name: str = Field(description="Nome principal consolidado")
    aliases: List[str] = Field(default=[], description="Lista de alcunhas e vulgos acumulados")
    documents: List[str] = Field(default=[], description="Lista de documentos acumulados (CPF, RG)")
    photos: List[str] = Field(default=[], description="Lista de fotos acumuladas deste participante ao longo dos RELINTs")
    linked_relints: List[str] = Field(default=[], description="Lista de nomes de arquivos PDF (RELINTs) vinculados a esta pessoa")
    last_updated: str = Field(default_factory=lambda: datetime.now().isoformat())

