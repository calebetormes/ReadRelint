import pytest
from unittest.mock import Mock, MagicMock
from pathlib import Path
from src.domain.rules.homicide_rule import HomicideRule
from src.application.etl_service import EtlService
from src.domain.entities import IncidentReport

def test_homicide_rule_keywords():
    rule = HomicideRule()
    
    # Textos que devem passar na filtragem
    assert rule.matches_filter("Ocorrência de homicídio no centro da cidade.") is True
    assert rule.matches_filter("Foi constatado o óbito da vítima no local.") is True
    assert rule.matches_filter("Corpo da vítima encaminhado para necropsia (cadáver).") is True
    assert rule.matches_filter("Autores desferiram disparos de arma de fogo e a vítima veio a óbito.") is True
    assert rule.matches_filter("Latrocínio tentado contra estabelecimento.") is True
    assert rule.matches_filter("Caso grave de feminicídio tentado na residência.") is True
    assert rule.matches_filter("Encontro de cadáver na beira do rio com perfurações de tiros.") is True
    
    # Textos com termos de exclusão forte mas contrabalançados por homicídio/feminicídio (devem passar)
    assert rule.matches_filter("A vítima sofreu lesão corporal leve, mas acabou ocorrendo o homicídio consumado no local.") is True
    
    # Textos que não devem passar na filtragem (exclusões e outros crimes)
    assert rule.matches_filter("Furto simples de bicicleta em via pública.") is False
    assert rule.matches_filter("Apreensão de objeto ilícito com suspeito.") is False
    assert rule.matches_filter("Averiguação de atitude suspeita.") is False
    assert rule.matches_filter("Lesão corporal leve em briga de bar.") is False
    assert rule.matches_filter("A vítima teve ferimentos superficiais decorrentes de lesão leve.") is False
    assert rule.matches_filter("Resposta ao pedido de busca PB 1490-2026-CI-DINT referente a investigação social.") is False

def test_etl_service_with_rule_skips_processing():
    # Mocking dependencies
    mock_parser = Mock()
    mock_parser.extract_text.return_value = "Furto de veículo na garagem da residência."
    
    mock_llm = Mock()
    mock_db = Mock()
    mock_db.exists_by_source_file.return_value = False
    
    mock_registry = Mock()
    mock_registry.is_processed.return_value = False

    service = EtlService(mock_parser, mock_llm, mock_db, mock_registry)
    rule = HomicideRule()
    
    progress_calls = []
    def on_progress(msg):
        progress_calls.append(msg)
        
    filtered_calls = []
    sent_calls = []

    # Executa o processamento do arquivo
    report = service.process_file(
        file_path=Path("dummy_furto.pdf"),
        rule=rule,
        on_progress=on_progress,
        on_filtered=lambda f: filtered_calls.append(f),
        on_sent_to_llm=lambda f: sent_calls.append(f)
    )
    
    # Deve retornar None pois foi pulado pelo filtro rápido
    assert report is None
    # A LLM não deve ter sido chamada
    mock_llm.process_text.assert_not_called()
    # O banco de dados não deve ter sido alterado
    mock_db.save.assert_not_called()
    # Deve conter mensagem informando que foi pulado
    assert any("Pulado:" in msg for msg in progress_calls)
    assert len(filtered_calls) == 1
    assert len(sent_calls) == 0

def test_etl_service_with_rule_processes_matching_file():
    mock_parser = Mock()
    mock_parser.extract_text.return_value = "Suspeito desferiu tiros e cometeu homicídio."
    
    mock_llm = Mock()
    mock_llm.process_text.return_value = {"natureza": "homicídio consumado", "content": "Resumo estruturado do homicídio."}
    
    mock_db = Mock()
    mock_db.exists_by_source_file.return_value = False
    
    mock_registry = Mock()
    mock_registry.is_processed.return_value = False
 
    service = EtlService(mock_parser, mock_llm, mock_db, mock_registry)
    rule = HomicideRule()
    
    filtered_calls = []
    sent_calls = []
 
    report = service.process_file(
        file_path=Path("dummy_homicidio.pdf"),
        rule=rule,
        on_filtered=lambda f: filtered_calls.append(f),
        on_sent_to_llm=lambda f: sent_calls.append(f)
    )
    
    assert report is not None
    assert report.content == "Resumo estruturado do homicídio."
    # A LLM deve ter sido chamada com as perguntas específicas da regra
    mock_llm.process_text.assert_called_once_with("Suspeito desferiu tiros e cometeu homicídio.", questions=rule.questions)
    # O banco de dados deve ter sido salvo
    mock_db.save.assert_called_once()
    assert len(filtered_calls) == 0
    assert len(sent_calls) == 1
 
def test_etl_service_with_rule_discards_post_llm_false_positive():
    mock_parser = Mock()
    # Contém palavra de homicídio que passa no pré-filtro
    mock_parser.extract_text.return_value = "Foi registrado um homicídio consumado no local."
    
    mock_llm = Mock()
    # A LLM avalia semanticamente que NÃO é homicídio de verdade por algum motivo ou erro
    mock_llm.process_text.return_value = {"natureza": "lesão corporal leve", "content": "Apenas lesão leve."}
    
    mock_db = Mock()
    mock_db.exists_by_source_file.return_value = False
    
    mock_registry = Mock()
    mock_registry.is_processed.return_value = False
 
    service = EtlService(mock_parser, mock_llm, mock_db, mock_registry)
    rule = HomicideRule()
    
    filtered_calls = []
    sent_calls = []
    progress_calls = []
 
    report = service.process_file(
        file_path=Path("dummy_homicidio_falso.pdf"),
        rule=rule,
        on_progress=lambda m: progress_calls.append(m),
        on_filtered=lambda f: filtered_calls.append(f),
        on_sent_to_llm=lambda f: sent_calls.append(f)
    )
    
    assert report is None
    # A LLM deve ter sido chamada
    mock_llm.process_text.assert_called_once()
    # Mas o banco de dados NÃO deve ter sido salvo
    mock_db.save.assert_not_called()
    assert len(filtered_calls) == 1  # Conta como filtrado após LLM
    assert len(sent_calls) == 1      # E foi enviado ao LLM
    assert any("Descartado pelo QA" in msg for msg in progress_calls)

def test_etl_service_skips_when_already_processed_in_registry():
    mock_parser = Mock()
    mock_llm = Mock()
    mock_db = Mock()
    
    mock_registry = Mock()
    # Simula que o arquivo já foi processado/descartado anteriormente para a regra
    mock_registry.is_processed.return_value = True
    
    service = EtlService(mock_parser, mock_llm, mock_db, mock_registry)
    rule = HomicideRule()
    
    progress_calls = []
    report = service.process_file(
        file_path=Path("dummy_already_processed.pdf"),
        rule=rule,
        on_progress=lambda m: progress_calls.append(m)
    )
    
    assert report is None
    # Nenhuma leitura de texto bruto ou chamada LLM deve acontecer
    mock_parser.extract_text.assert_not_called()
    mock_llm.process_text.assert_not_called()
    # Deve conter log informando que foi pulado pelo histórico
    assert any("Já processado anteriormente" in msg for msg in progress_calls)
