import pytest
from src.adapters.local_regex_processor import LocalRegexProcessor

def test_local_regex_processor_homicide():
    processor = LocalRegexProcessor()
    text = "O autor desferiu disparos de arma de fogo e cometeu homicídio consumado no local."
    questions = {
        "natureza": "Qual o crime?",
        "resultado_morte": "Houve óbito?",
        "content": "Resumo"
    }
    result = processor.process_text(text, questions=questions)
    
    assert result["natureza"] == "homicídio consumado"
    assert "confirmado" in result["resultado_morte"]
    assert result["content"] == text

def test_local_regex_processor_threat():
    processor = LocalRegexProcessor()
    text = "A vítima sofreu uma ameaça e temeu pela sua vida."
    questions = {
        "natureza": "Qual o crime?",
        "resultado_morte": "Houve óbito?",
        "content": "Resumo"
    }
    result = processor.process_text(text, questions=questions)
    
    assert result["natureza"] == "ameaça"
    assert result["resultado_morte"] == "não informado"

def test_local_regex_processor_empty():
    processor = LocalRegexProcessor()
    result = processor.process_text("Texto", questions=None)
    assert result == {"content": "Texto"}
