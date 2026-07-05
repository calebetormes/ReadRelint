from typing import List, Optional
from pydantic import BaseModel, Field

class Address(BaseModel):
    """
    Representa o endereço do incidente.
    """
    street: str = Field(description="Nome do logradouro/rua")
    number: Optional[str] = Field(default=None, description="Número do endereço, se disponível")
    neighborhood: Optional[str] = Field(default=None, description="Bairro do ocorrido")
    city: Optional[str] = Field(default=None, description="Cidade do ocorrido")

class Participant(BaseModel):
    """
    Representa uma pessoa participante envolvida no incidente.
    """
    name: str = Field(description="Nome completo do participante")
    role: str = Field(description="Papel do participante no incidente (ex: Vítima, Autor, Testemunha, Comunicante)")

class Vehicle(BaseModel):
    """
    Representa um veículo envolvido no incidente.
    """
    plate: Optional[str] = Field(default=None, description="Placa do veículo")
    model: Optional[str] = Field(default=None, description="Modelo e marca do veículo")
    color: Optional[str] = Field(default=None, description="Cor do veículo")

class IncidentReport(BaseModel):
    """
    Representa a entidade de domínio de um relatório de boletim de ocorrência policial estruturado.
    """
    # Metadados Gerais do RELINT (Compartilhados por todas as ocorrências do mesmo arquivo)
    relint_number: Optional[str] = Field(default=None, description="Número de identificação do RELINT")
    subject: Optional[str] = Field(default=None, description="Assunto do relatório")
    diffusion: Optional[str] = Field(default=None, description="Canais de difusão do relatório")
    attachment: Optional[str] = Field(default=None, description="Anexos descritos no relatório")

    # Campos específicos da ocorrência
    incident_nature: str = Field(default="Ocorrência", description="Natureza do fato (Ocorrência, Denúncia, Resposta a Pedido de Busca, Informação, Outro)")
    incident_group: str = Field(description="Grupo do incidente (Ocorrências do AVANTE, Ocorrências Importantes fora do AVANTE, Demais Fatos)")
    incident_type: str = Field(description="Tipo de fato ou natureza da ocorrência (ex: Roubo, Furto, Estelionato)")
    incident_time: Optional[str] = Field(default=None, description="Data e horário do incidente no formato ISO 8601 ou null")
    address: Address = Field(description="Endereço detalhado onde ocorreu o incidente")
    participants: List[Participant] = Field(default_factory=list, description="Lista de participantes envolvidos no incidente")
    vehicles: List[Vehicle] = Field(default_factory=list, description="Lista de veículos envolvidos no incidente")
    attending_officer: Optional[str] = Field(default=None, description="Nome da autoridade policial ou policial que atendeu a ocorrência")
    history_summary: str = Field(description="Resumo do histórico ou narrativa dos fatos extraídos")
    source_file: Optional[str] = Field(default=None, description="Nome do arquivo PDF de origem")




