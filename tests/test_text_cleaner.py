import pytest
from src.application.text_cleaner import clean_relint_text

def test_clean_relint_text_no_cut():
    # Texto sem nenhuma palavra-chave de corte não deve ser modificado
    raw_text = "Ocorrência de roubo a pedestre no centro de Cruz Alta."
    assert clean_relint_text(raw_text) == raw_text

def test_clean_relint_text_with_distribuicao():
    # Deve cortar tudo a partir de Distribuição:
    raw_text = (
        "Ocorrência de roubo a pedestre.\n"
        "Distribuição:\n"
        "- 1º Batalhão\n"
        "- Delegacia de Polícia"
    )
    expected = "Ocorrência de roubo a pedestre."
    assert clean_relint_text(raw_text) == expected

def test_clean_relint_text_with_assinatura():
    # Deve cortar tudo a partir de Assinatura:
    raw_text = (
        "Fato ocorrido no dia 01/01.\n"
        " Assinatura:\n"
        "Cap. PM João da Silva"
    )
    expected = "Fato ocorrido no dia 01/01."
    assert clean_relint_text(raw_text) == expected

def test_clean_relint_text_case_insensitive_and_accent():
    # Deve reconhecer variações acentuadas e maiúsculas
    raw_text = (
        "Texto principal da ocorrência.\n"
        "DISTRIBUIÇÃO: Geral"
    )
    expected = "Texto principal da ocorrência."
    assert clean_relint_text(raw_text) == expected

    raw_text_accent = (
        "Texto principal da ocorrência.\n"
        "instruções: ler com atenção"
    )
    assert clean_relint_text(raw_text_accent) == expected

def test_clean_relint_text_with_disclaimer():
    raw_text = (
        "Início da ocorrência.\n"
        "DOCUMENTO PREPARATÓRIO – ACESSO RESTRITO\n"
        "Nos termos do Art. 7, § 3º da Lei nº 12.527/2011, os documentos...\n"
        "pessoas ou órgãos não autorizados.\n"
        "Meio do texto da ocorrência."
    )
    expected = "Início da ocorrência.\n\nMeio do texto da ocorrência."
    assert clean_relint_text(raw_text) == expected

def test_clean_relint_text_with_header():
    raw_text = (
        "ESTADO DO RIO GRANDE DO SUL\n"
        "SECRETARIA DA SEGURANÇA PÚBLICA\n"
        "BRIGADA MILITAR\n"
        "SISTEMA DE INTELIGÊNCIA\n"
        "Relatório de inteligência número 01."
    )
    expected = "\n\n\n\nRelatório de inteligência número 01."
    assert clean_relint_text(raw_text) == expected.strip()

def test_clean_relint_text_empty():
    assert clean_relint_text("") == ""
    assert clean_relint_text(None) == ""  # type: ignore

def test_clean_relint_text_pagination():
    # Testar se "Página 1 de 5", "Pág. 3", "Pg 10", "Page 2" e números de linha isolados são removidos
    raw_text = (
        "Página 1 de 5\n"
        "Ocorrência de teste.\n"
        "Pág. 2\n"
        "Conteúdo da segunda página.\n"
        " 12 \n"
        "Fim do documento.\n"
        "pg 3\n"
        "Page 4 of 4"
    )
    # 12 isolado, Página 1 de 5, Pág. 2, pg 3, Page 4 of 4 devem ser removidos.
    # O texto restante deve conter a essência sem esses termos.
    cleaned = clean_relint_text(raw_text)
    assert "Página 1 de 5" not in cleaned
    assert "Pág. 2" not in cleaned
    assert "pg 3" not in cleaned
    assert "Page 4 of 4" not in cleaned
    assert "12" not in cleaned.split("\n")
    assert "Ocorrência de teste." in cleaned
    assert "Conteúdo da segunda página." in cleaned
    assert "Fim do documento." in cleaned
