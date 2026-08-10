from typing import Optional, List, Dict, Any, Union

from enum import Enum
from pydantic import BaseModel, Field, model_validator
from datetime import datetime

class ParticipationType(str, Enum):
    VITIMA = "Vítima"
    TESTEMUNHA = "Testemunha"
    ACUSADO = "Acusado"
    GUARNICAO = "Parte da Guarnição"

class BmGroup(str, Enum):
    ROUBO_ESTABELECIMENTO = "Roubo a Estabelecimento"
    ROUBO_RESIDENCIA = "Roubo a Residência"
    ROUBO_VEICULO = "Roubo de Veículo"
    ROUBO_PEDESTRE = "Roubo a Pedestre"
    FURTO_QUALIFICADO = "Furto Qualificado"
    FURTO_VEICULO = "Furto de Veículo"
    PRISAO_TRAFICO = "Prisão por Tráfico"
    OUTROS = "Outros"

class RelintType(str, Enum):
    OCORRENCIA = "Ocorrência"
    DISK_DENUNCIA = "Disk Denúncia"
    RESPOSTA_PB = "Resposta a PB"
    OUTROS = "Outros"

class Participant(BaseModel):
    """
    Representa um participante citado no RELINT, formatado para extração LLM.
    """
    name: Optional[str] = Field(default=None, description="Nome completo da pessoa")
    nickname: Optional[str] = Field(default=None, description="Alcunha, apelido ou vulgo")
    document: Optional[str] = Field(default=None, description="Documento de identificação (CPF ou RG)")
    background: Optional[str] = Field(default=None, description="Antecedentes mencionados (se houver)")
    participation_type: Optional[ParticipationType] = Field(default=None, description="Opções: Vítima, Testemunha, Acusado, Parte da Guarnição")
    photo_path: Optional[str] = Field(default=None, description="Caminho do arquivo da foto do participante")


class IncidentReport(BaseModel):
    """
    Representa a entidade de domínio de um relatório de inteligência (RELINT) processado.
    """
    source_file: str = Field(description="Nome do arquivo PDF de origem")
    date_of_fact: Optional[str] = Field(default=None, description="Extraia a data de ocorrência do fato (ex: DD/MM/AAAA ou DD de mês de AAAA) mencionada na introdução ou primeira frase do histórico")
    time_of_fact: Optional[str] = Field(default=None, description="Extraia a hora exata ou aproximada do fato (ex: 14h30min, 01:30h, por volta das 18h) mencionada no primeiro parágrafo")
    modification_date_history: Optional[str] = Field(default=None, description="Mapear a sequência/histórico de datas de alteração do arquivo ou data do fato")

    subject: Optional[str] = Field(default=None, description="Extraia exatamente o texto do campo ASSUNTO: presente na seção introdutória do RELINT")
    main_fact: Optional[str] = Field(default=None, description="Determine a partir do Assunto qual é o evento central do relatório")
    relint_type: Optional[RelintType] = Field(default=RelintType.OUTROS, description="Classifique estritamente em Ocorrência, Disk Denúncia, Resposta a PB ou Outros")
    bm_group: Optional[BmGroup] = Field(default=BmGroup.OUTROS, description="Escolha obrigatoriamente UMA das opções: Roubo a Estabelecimento, Roubo a Residência, Roubo de Veículo, Roubo a Pedestre, Furto Qualificado, Furto de Veículo, Prisão por Tráfico, Outros")
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

