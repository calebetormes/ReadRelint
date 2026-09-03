"""
Testes unitários para o classificador determinístico de BmGroup.
"""
import pytest
from backend.engine.cleaners.bm_classifier import classify_bm_group


class TestBmClassifier:
    """Testes de classificação correta por padrões do arquivo e assunto."""

    # --- Homicídio ---
    def test_homicidio_por_filename(self):
        result = classify_bm_group(filename="RELINT 467 - Homicídio Doloso em Panambi - RS.pdf")
        assert result == "Homicídio"

    def test_homicidio_por_subject(self):
        result = classify_bm_group(subject="HOMICÍDIO DOLOSO EM PANAMBI - RS")
        assert result == "Homicídio"

    def test_homicidio_tentativa_por_subject(self):
        result = classify_bm_group(subject="Tentativa de Homicídio em Palmeira das Missões")
        assert result == "Homicídio"

    def test_feminicidio_por_subject(self):
        result = classify_bm_group(subject="Feminicídio em Ijuí - RS")
        assert result == "Homicídio"

    def test_latrocinio_por_subject(self):
        result = classify_bm_group(subject="Latrocínio - Santa Rosa RS")
        assert result == "Homicídio"

    def test_obito_por_content(self):
        result = classify_bm_group(
            subject="Ocorrência policial",
            content="Constatou-se o óbito da vítima no local."
        )
        assert result == "Homicídio"

    # --- Tráfico ---
    def test_trafico_por_subject(self):
        result = classify_bm_group(subject="Prisão por Tráfico de Drogas em Cruz Alta")
        assert result == "Prisão por Tráfico"

    def test_trafico_por_content(self):
        result = classify_bm_group(
            subject="Ocorrência Policial",
            content="Foram apreendidos 30g de crack e 50g de maconha durante abordagem."
        )
        assert result == "Prisão por Tráfico"

    # --- Roubo a Estabelecimento ---
    def test_roubo_estabelecimento_por_subject(self):
        result = classify_bm_group(subject="Roubo a Estabelecimento Comercial em Panambi")
        assert result == "Roubo a Estabelecimento"

    def test_roubo_banco_por_subject(self):
        result = classify_bm_group(subject="Roubo ao Banco do Brasil em Santa Rosa")
        assert result == "Roubo a Estabelecimento"

    # --- Roubo a Residência ---
    def test_roubo_residencia_por_subject(self):
        result = classify_bm_group(subject="Roubo a Residencia na Rua das Flores")
        assert result == "Roubo a Residência"

    def test_roubo_residencia_acentuado(self):
        result = classify_bm_group(subject="Roubo à Residência")
        assert result == "Roubo a Residência"

    # --- Roubo de Veículo ---
    def test_roubo_veiculo_por_subject(self):
        result = classify_bm_group(subject="Roubo de Veículo - GM Onix - Cruz Alta RS")
        assert result == "Roubo de Veículo"

    def test_roubo_moto_por_subject(self):
        result = classify_bm_group(subject="Roubo de Motocicleta Panambi")
        assert result == "Roubo de Veículo"

    # --- Roubo a Pedestre ---
    def test_roubo_pedestre_por_subject(self):
        result = classify_bm_group(subject="Roubo a Pedestre - Centro Palmeira das Missões")
        assert result == "Roubo a Pedestre"

    def test_roubo_celular_por_subject(self):
        result = classify_bm_group(subject="Roubo de Celular - Palmeira das Missões")
        assert result == "Roubo a Pedestre"

    # --- Furto de Veículo ---
    def test_furto_veiculo_por_subject(self):
        result = classify_bm_group(subject="Furto de Veículo - Peugeot 208 - Ijuí RS")
        assert result == "Furto de Veículo"

    # --- Furto Qualificado ---
    def test_furto_qualificado_por_subject(self):
        result = classify_bm_group(subject="Furto Qualificado mediante arrombamento")
        assert result == "Furto Qualificado"

    def test_furto_simples_por_subject(self):
        result = classify_bm_group(subject="Furto em estabelecimento comercial")
        assert result == "Furto Qualificado"

    # --- Outros / Fallback ---
    def test_outros_quando_nada_bate(self):
        result = classify_bm_group(filename="RELINT-001.pdf", subject="Ocorrência diversa")
        assert result == "Outros"

    def test_nao_confia_em_palpite_livre_da_llm(self):
        """
        Nunca deve haver um 3º fallback que preserve um palpite livre da LLM.
        100% determinístico: regex bateu ou "Outros", nunca um terceiro caminho.
        (bug real: 'Encontro de artefato explosivo' foi classificado como 'Roubo a
        Estabelecimento' porque o antigo fallback preservava a resposta legada não
        confiável da LLM quando as 2 camadas de regex não encontravam nada.)
        """
        result = classify_bm_group(
            filename="RELATÓRIO DE INTELIGÊNCIA Nº 424/2026/ADJ-CI",
            subject="Encontro de artefato explosivo em Cruz Alta - RS",
            content="A guarnição isolou o local e removeu o artefato para detonação."
        )
        assert result == "Outros"

    # --- Prioridade: Homicídio > Tráfico ---
    def test_homicidio_prevalece_sobre_trafico(self):
        """Latrocínio envolve tráfico e morte; deve classificar como Homicídio."""
        result = classify_bm_group(
            subject="Latrocínio - vítima fatal - droga"
        )
        assert result == "Homicídio"
