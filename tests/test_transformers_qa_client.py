import pytest
from unittest.mock import patch, MagicMock
from src.adapters.transformers_qa_client import TransformersQaClient

@patch("src.adapters.transformers_qa_client.pipeline")
def test_transformers_qa_client_success(mock_pipeline):
    mock_qa = MagicMock()
    mock_qa.return_value = {"answer": "Homicídio qualificado"}
    mock_pipeline.return_value = mock_qa

    client = TransformersQaClient()
    questions = {"natureza": "Qual o crime?"}
    
    result = client.process_text("Texto do BO", questions=questions)
    
    assert isinstance(result, dict)
    assert result["natureza"] == "Homicídio qualificado"
    mock_pipeline.assert_called_once_with(
        "question-answering",
        model="pierreguillou/bert-large-cased-squad-v1.1-portuguese",
        device=-1
    )
    mock_qa.assert_called_once_with(
        question="Qual o crime?",
        context="Texto do BO",
        max_answer_len=150,
        handle_impossible_answer=True
    )

@patch("src.adapters.transformers_qa_client.pipeline")
def test_transformers_qa_client_empty_questions(mock_pipeline):
    client = TransformersQaClient()
    result = client.process_text("Texto do BO", questions=None)
    
    assert result == {"content": "Texto do BO"}
    mock_pipeline.assert_not_called()

