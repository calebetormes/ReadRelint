import pytest
from pydantic import ValidationError
from src.domain.entities import (
    IncidentReport,
    Person,
    Participant,
    RelintType,
    BmGroup,
    ParticipationType
)

def test_incident_report_validation():
    # Criando um report mínimo válido
    report = IncidentReport(
        source_file="test_report.pdf",
        content="Resumo narrativo estruturado do fato."
    )
    
    assert report.source_file == "test_report.pdf"
    assert report.content == "Resumo narrativo estruturado do fato."
    assert report.relint_type == RelintType.OUTROS
    assert report.bm_group == BmGroup.OUTROS
    assert report.user_edited is False

    # Deve falhar sem os campos obrigatórios (source_file é obrigatório)
    with pytest.raises(ValidationError):
        IncidentReport(content="Resumo apenas")  # sem source_file

    # Sem content deve criar normalmente pois content é opcional agora
    report_no_content = IncidentReport(source_file="test.pdf")
    assert report_no_content.source_file == "test.pdf"
    assert report_no_content.content is None

def test_incident_report_with_full_fields():
    participant = Participant(
        name="João da Silva",
        nickname="Zé",
        document="123.456.789-00",
        background="Furto",
        participation_type=ParticipationType.ACUSADO
    )
    report = IncidentReport(
        source_file="relint_completo.pdf",
        subject="ROUBO A RESIDÊNCIA",
        main_fact="Roubo consumado",
        relint_type=RelintType.OCORRENCIA,
        bm_group=BmGroup.ROUBO_RESIDENCIA,
        date_of_fact="10/08/2026",
        time_of_fact="14h30min",
        municipality="Panambi",
        address="Rua Brasil, 100, Centro",
        neighborhood="Centro",
        police_unit="39º BPM",
        map_url="https://maps.google.com/?q=-28.23,-53.60",
        coordinates="-28.23, -53.60",
        participants=[participant]
    )
    assert report.municipality == "Panambi"
    assert report.police_unit == "39º BPM"
    assert report.time_of_fact == "14h30min"
    assert report.relint_type == RelintType.OCORRENCIA
    assert report.bm_group == BmGroup.ROUBO_RESIDENCIA
    assert len(report.participants) == 1
    assert report.participants[0].participation_type == ParticipationType.ACUSADO

def test_person_entity():
    person = Person(
        person_id="123.456.789-00",
        name="João da Silva",
        aliases=["Zé"],
        documents=["123.456.789-00"],
        linked_relints=["relint_completo.pdf"]
    )
    assert person.person_id == "123.456.789-00"
    assert person.name == "João da Silva"
    assert "Zé" in person.aliases
    assert "relint_completo.pdf" in person.linked_relints


