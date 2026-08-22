# -*- coding: utf-8 -*-
"""
Cliente Ollama para processamento cognitivo local via LLM.
"""

import json
import logging
import requests
from typing import Any, Dict, Optional, Tuple
from src.engine.extractors.llm.llm_processor import ILlmProcessor
from src.dashboard.backend.core.entities import IncidentReport

logger = logging.getLogger(__name__)


class OllamaClient(ILlmProcessor):
    """
    Implementação concreta para processamento de linguagem natural usando
    o Ollama rodando localmente.
    """

    def __init__(self, model_name: str = "llama3.1:latest", base_url: str = "http://localhost:11434") -> None:
        self.model_name = model_name
        self.base_url = base_url

    def check_connection(self) -> Tuple[bool, str]:
        """
        Testa se o serviço Ollama está rodando localmente na URL base.
        Retorna uma tupla (sucesso: bool, mensagem: str).
        """
        try:
            url = f"{self.base_url}/api/tags"
            res = requests.get(url, timeout=3)
            if res.status_code == 200:
                models = res.json().get("models", [])
                if models:
                    model_names = ", ".join(m.get("name", "") for m in models[:3])
                    return True, f"Ollama online! Modelo(s) encontrado(s): {model_names}"
                return True, "Ollama online! Nenhum modelo instalado no momento."
            return False, f"Ollama respondeu com código de erro {res.status_code}."
        except Exception:
            return False, f"Serviço Ollama indisponível ou desativado em {self.base_url}"

    def process_text(self, text: str, questions: Optional[Dict[str, Any]] = None, schema_model: Optional[type] = None) -> dict:
        """
        Envia o texto limpo ao Ollama solicitando a estruturação em formato JSON
        baseado no JSON Schema do modelo IncidentReport (ou do schema_model se fornecido).
        """
        system_prompt = ""
        if questions and "system_prompt" in questions:
            system_prompt = questions["system_prompt"]
        
        # Gera o JSON Schema do modelo Pydantic para orientar a extração
        model_to_use = schema_model if schema_model else IncidentReport
        schema = model_to_use.model_json_schema()
        # Remove campos mantidos pelo sistema Python para não poluir nem confundir o Ollama
        if "properties" in schema:
            schema["properties"].pop("source_file", None)
            schema["properties"].pop("content", None)
            schema["properties"].pop("user_edited", None)
            
        schema_str = json.dumps(schema, indent=2, ensure_ascii=False)

        prompt = f"""
Você é um assistente especialista em análise de Relatórios de Inteligência (RELINT) e Ocorrências Policiais da Brigada Militar do Rio Grande do Sul.
O documento a seguir é um RELINT em Português (pt-BR). Analise o texto integralmente e extraia os dados solicitados com máxima precisão.

{system_prompt}

INSTRUÇÕES ESTRITAS DE EXTRAÇÃO:
1. Retorne EXATAMENTE UM objeto JSON válido em conformidade com o JSON Schema fornecido.
2. Não inclua texto, comentários ou formatações Markdown adicionais fora do JSON.
3. PARTICIPANTES (participants):
   - Extraia o NOME LIMPO de cada pessoa civil citada (sem prefixos narrativos como "Posteriormente identificado como", "a vítima", "o menor", "caroneiro da moto", "pelo senhor").
   - CLASSIFICAÇÃO DE PAPEL (participation_type): Você só pode classificar em UMA destas 3 opções:
     * "Vítima": Pessoa que sofreu a violência, teve bens subtraídos/furtados, foi alvejada, lesionada ou veio a óbito. Menores de idade vítimas de abuso/violência.
     * "Testemunha": Pessoas que presenciaram os fatos, comunicantes da ocorrência e familiares (ex: pai, mãe, cônjuge) que relataram o ocorrido.
     * "Autor/Suspeito": Autor do fato, indivíduo preso em flagrante, apreendido (inclusive menor infrator), formalmente indiciado, investigado, foragido ou abordado em atitude suspeita.
   - DOCUMENTOS (document): Extraia o RG ou CPF completo se citado no texto.
   - ALCUNHA (nickname): Extraia apelidos ou vulgos se mencionados (ex: "Caveirinha", "Gordinho").
   - ANTECEDENTES (background): Resuma antecedentes criminais mencionados no texto para a pessoa (se houver).
   - REGRA ANTI-PM: NUNCA inclua Policiais Militares (SD, SGT, CB, TEN, CAP, etc.) da guarnição ou delegados que atenderam a ocorrência como participantes.
4. RESUMO (summary): Escreva um resumo narrativo claro e conciso em 1 parágrafo contendo data, local, dinâmica dos fatos, prisões e apreensões.
5. LOCALIZAÇÃO: Extraia município (municipality), bairro (neighborhood), endereço completo (address) e unidade PM (police_unit).
6. REGISTRO POLICIAL: Extraia o número de registro (registry_number), órgão (registry_agency) e ano (registry_year).

JSON SCHEMA:
{schema_str}

TEXTO DO RELINT:
---
{text}
---
        """

        url = f"{self.base_url}/api/generate"
        payload = {
            "model": self.model_name,
            "prompt": prompt,
            "stream": False,
            "format": "json",
            "options": {
                "temperature": 0.0
            }
        }

        try:
            logger.info(f"Enviando texto do RELINT para processamento local via Ollama ({self.model_name})...")
            response = requests.post(url, json=payload, timeout=25)
            
            # Recuperação Automática: Se der 404 (model not found), tenta buscar modelos ativos no Ollama
            if response.status_code == 404:
                logger.warning(f"Modelo '{self.model_name}' não encontrado no Ollama. Buscando modelos alternativos...")
                tags_response = requests.get(f"{self.base_url}/api/tags", timeout=5)
                if tags_response.status_code == 200:
                    models = tags_response.json().get("models", [])
                    if models:
                        alternative_model = models[0]["name"]
                        logger.info(f"Alternando automaticamente para o modelo disponível: '{alternative_model}'")
                        self.model_name = alternative_model
                        payload["model"] = alternative_model
                        
                        # Segunda tentativa
                        response = requests.post(url, json=payload, timeout=25)
            
            response.raise_for_status()
            
            response_json = response.json()
            response_text = response_json.get("response", "{}")
            
            extracted_data = json.loads(response_text)
            return extracted_data
            
        except Exception as e:
            logger.error(f"Erro ao processar texto com Ollama: {e}")
            raise e
