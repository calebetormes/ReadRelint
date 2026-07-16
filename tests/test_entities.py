import pytest
from pydantic import ValidationError
from src.domain.entities import IncidentReport

def test_incident_report_validation():
    # Criando um report mínimo válido
    report = IncidentReport(
        source_file="test_report.pdf",
        content="Resumo narrativo estruturado do fato."
    )
    
    assert report.source_file == "test_report.pdf"
    assert report.content == "Resumo narrativo estruturado do fato."

    # Deve falhar sem os campos obrigatórios (source_file é obrigatório)
    with pytest.raises(ValidationError):
        IncidentReport(content="Resumo apenas")  # sem source_file

    # Sem content deve criar normalmente pois content é opcional agora
    report_no_content = IncidentReport(source_file="test.pdf")
    assert report_no_content.source_file == "test.pdf"
    assert report_no_content.content is None
