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
    
    # Textos com termos de exclusão forte mas contrabalançados por homicídio/feminicídio/morte/óbito (devem passar no pré-filtro)
    assert rule.matches_filter("A vítima sofreu lesão corporal leve, mas acabou ocorrendo o homicídio consumado no local.") is True
    assert rule.matches_filter("Vítima de lesão corporal seguida de morte.") is True
    assert rule.matches_filter("Houve uma ocorrência de ameaça de morte.") is True
    assert rule.matches_filter("Vítima lesionada e veio a óbito.") is True
    assert rule.matches_filter("O suspeito possui antecedentes de roubo, mas cometeu homicídio.") is True
    assert rule.matches_filter("Consulta ao sistema de registros policiais e outros fatos. Ocorrência de morte violenta por disparos.") is True
    
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
    assert report.content == "Arquivo: dummy_homicidio.pdf\nConteúdo:\nResumo estruturado do homicídio."
    assert report.occurred_fact == "homicídio consumado"
    assert report.clean_content == "Suspeito desferiu tiros e cometeu homicídio."
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

def test_validate_qa_results_scenarios():
    rule = HomicideRule()
    
    # Caso 1: Natureza correta e confirmada
    assert rule.validate_qa_results({
        "natureza": "homicídio consumado",
        "resultado_morte": "óbito no local",
        "content": "A vítima foi encontrada sem vida com perfurações."
    }) is True

    # Caso 2: Lesão corporal seguida de morte (natureza tem exclusão, mas resultado confirma óbito)
    assert rule.validate_qa_results({
        "natureza": "lesão corporal seguida de morte",
        "resultado_morte": "óbito",
        "content": "Após agressões a vítima faleceu no hospital."
    }) is True

    # Caso 3: Ameaça de morte (natureza é ameaça, mas sem óbito real)
    assert rule.validate_qa_results({
        "natureza": "ameaça",
        "resultado_morte": "vítima ameaçada",
        "content": "Autor prometeu causar a morte da vítima."
    }) is False

    # Caso 4: Roubo simples sem latrocínio nem morte
    assert rule.validate_qa_results({
        "natureza": "roubo",
        "resultado_morte": "não informado",
        "content": "Subtração de celular mediante grave ameaça."
    }) is False


def test_etl_service_prioritizes_user_manual_edits():
    mock_parser = Mock()
    mock_parser.extract_text.return_value = "Suspeito cometeu homicídio."

    mock_llm = Mock()
    mock_llm.process_text.return_value = {"natureza": "homicídio consumado", "content": "Resumo estruturado."}

    mock_db = Mock()
    mock_db.exists_by_source_file.return_value = False

    mock_registry = Mock()
    mock_registry.is_processed.return_value = False
    # Simula que existe uma edição manual do usuário no histórico para o arquivo e regra
    mock_registry.get_user_edit.return_value = "Feminicídio Tentado"

    service = EtlService(mock_parser, mock_llm, mock_db, mock_registry)
    rule = HomicideRule()

    report = service.process_file(
        file_path=Path("dummy_homicidio.pdf"),
        rule=rule
    )

    assert report is not None
    # Deve usar "Feminicídio Tentado" em vez de "homicídio consumado" sugerido pela LLM
    assert report.occurred_fact == "Feminicídio Tentado"
    assert report.user_edited is True
    # O mock_registry deve ter sido consultado
    mock_registry.get_user_edit.assert_called_once_with("dummy_homicidio.pdf", "Homicídio")

