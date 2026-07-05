import pytest
from pydantic import ValidationError
from src.domain.entities import Address, Participant, Vehicle, IncidentReport

def test_address_validation():
    # Deve criar com sucesso passando apenas os dados obrigatórios (street)
    addr = Address(street="Rua das Flores")
    assert addr.street == "Rua das Flores"
    assert addr.number is None
    assert addr.neighborhood is None
    assert addr.city is None

    # Deve criar com sucesso com todos os dados
    addr_full = Address(
        street="Av. Paulista",
        number="1000",
        neighborhood="Bela Vista",
        city="São Paulo"
    )
    assert addr_full.street == "Av. Paulista"
    assert addr_full.number == "1000"
    assert addr_full.neighborhood == "Bela Vista"
    assert addr_full.city == "São Paulo"

    # Deve falhar se faltar o campo obrigatório street
    with pytest.raises(ValidationError):
        Address()  # type: ignore


def test_participant_validation():
    # Deve criar com sucesso com campos obrigatórios
    part = Participant(name="Maria Silva", role="Vítima")
    assert part.name == "Maria Silva"
    assert part.role == "Vítima"

    # Deve falhar se faltar name ou role
    with pytest.raises(ValidationError):
        Participant(name="Só Nome")  # type: ignore
        
    with pytest.raises(ValidationError):
        Participant(role="Só Papel")  # type: ignore


def test_vehicle_validation():
    # Todos os campos são opcionais, então deve iniciar vazio com sucesso
    veh_empty = Vehicle()
    assert veh_empty.plate is None
    assert veh_empty.model is None
    assert veh_empty.color is None

    # Deve preencher campos corretamente
    veh = Vehicle(plate="ABC-1234", model="Fusca", color="Azul")
    assert veh.plate == "ABC-1234"
    assert veh.model == "Fusca"
    assert veh.color == "Azul"


def test_incident_report_validation():
    # Setup de dados básicos corretos usando instância explícita de Address
    address_data = Address(street="Rua Humaitá")
    
    # Criando um report mínimo válido
    report = IncidentReport(
        incident_group="Ocorrências do AVANTE",
        incident_type="Furto de Veículo",
        address=address_data,
        history_summary="Subtração de bens sem violência."
    )
    
    assert report.incident_group == "Ocorrências do AVANTE"
    assert report.incident_type == "Furto de Veículo"
    assert report.address.street == "Rua Humaitá"
    assert report.history_summary == "Subtração de bens sem violência."
    assert report.incident_time is None
    assert report.participants == []
    assert report.vehicles == []
    assert report.attending_officer is None

    # Criando um report completo instanciando as classes explicitamente
    report_full = IncidentReport(
        incident_group="Ocorrências do AVANTE",
        incident_type="Roubo de Veículo",
        incident_time="2026-07-04T12:00:00Z",
        address=Address(street="Av. Brasil", number="500", city="Rio de Janeiro"),
        participants=[
            Participant(name="João", role="Autor"),
            Participant(name="Carlos", role="Vítima")
        ],
        vehicles=[
            Vehicle(plate="XYZ-9876", model="Gol")
        ],
        attending_officer="Sargento Silva",
        history_summary="Roubo de veículo sob ameaça de arma de fogo."
    )
    
    assert report_full.incident_group == "Ocorrências do AVANTE"
    assert report_full.incident_type == "Roubo de Veículo"
    assert report_full.incident_time == "2026-07-04T12:00:00Z"
    assert report_full.address.city == "Rio de Janeiro"
    assert len(report_full.participants) == 2
    assert report_full.participants[0].name == "João"
    assert report_full.participants[1].role == "Vítima"
    assert len(report_full.vehicles) == 1
    assert report_full.vehicles[0].plate == "XYZ-9876"
    assert report_full.attending_officer == "Sargento Silva"

    # Deve falhar sem os campos obrigatórios
    with pytest.raises(ValidationError):
        # Sem address (passando None onde se espera um Address)
        IncidentReport(incident_group="Ocorrências do AVANTE", incident_type="Furto de Veículo", address=None, history_summary="Resumo")  # type: ignore

    with pytest.raises(ValidationError):
        # Sem incident_type
        IncidentReport(incident_group="Ocorrências do AVANTE", address=address_data, incident_type=None, history_summary="Resumo")  # type: ignore

    with pytest.raises(ValidationError):
        # Sem incident_group
        IncidentReport(address=address_data, incident_type="Furto de Veículo", history_summary="Resumo")  # type: ignore

def test_incident_report_nature():
    address_data = Address(street="Rua A", number=None, neighborhood=None, city="Cachoeira")
    report = IncidentReport(
        incident_nature="Denúncia",
        incident_group="Demais Fatos",
        incident_type="Estelionato",
        address=address_data,
        history_summary="Relato de golpe por telefone."
    )
    assert report.incident_nature == "Denúncia"
    assert report.incident_group == "Demais Fatos"


