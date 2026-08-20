import json
import logging
import requests
from typing import Dict, Optional
from src.engine.llm.llm_processor import ILlmProcessor
from src.dashboard.backend.core.entities import IncidentReport

logger = logging.getLogger(__name__)

class OllamaClient(ILlmProcessor):
    """
    Implementação concreta (Adapter) para processamento de linguagem natural usando
    o Ollama rodando localmente. Exige o serviço Ollama ativo.
    """

    def __init__(self, model_name: str = "llama3.1:latest", base_url: str = "http://localhost:11434"):
        """
        Inicializa o cliente Ollama.

        :param model_name: Nome do modelo local no Ollama (ex: llama3.1, qwen2.5, phi3, etc.)
        :param base_url: URL base do serviço local do Ollama.
        """
        self.model_name = model_name
        self.base_url = base_url

    def check_connection(self) -> tuple[bool, str]:
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

    def process_text(self, text: str, questions: Optional[Dict[str, str]] = None, schema_model: type = None) -> dict:
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
Você é um assistente especialista em análise de Relatórios de Inteligência (RELINT) e Ocorrências Policiais do Brasil.
O documento a seguir é um RELINT em Português (pt-BR). Analise o texto integralmente e extraia os dados solicitados.

{system_prompt}

INSTRUÇÕES DE SAÍDA:
1. Você DEVE retornar EXATAMENTE UM objeto JSON válido que obedeça ao seguinte JSON Schema.
2. Não inclua comentários, explicações ou texto fora do JSON.
3. Se um campo do tipo Enum for exigido, você só pode usar os valores listados em 'enum'.
4. PARTICIPANTES (participants): Extraia o NOME LIMPO de cada pessoa civil citada (ex: "Johnny Schroeder" e NÃO "Posteriormente Identificado Como Johnny Schroeder", "João Witor Fagundes Garmatz" e NÃO "Estavam João Witor Fagundes Garmatz", "Mariane da Silva" e NÃO "momento em que foi feito contato com Mariane"). NUNCA inclua prefixos narrativos policiais ("Posteriormente identificado como", "Estavam", "Conforme relato", "Vítima", "Contato com"). NUNCA inclua Policiais Militares que atenderam a ocorrência.
5. RESUMO (summary): Escreva um resumo narrativo explicativo em 1 parágrafo com os fatos principais.
6. LOCALIZAÇÃO: Extraia município (municipality), bairro (neighborhood), endereço completo (address) e unidade policial (police_unit) quando citados.
7. REGISTRO POLICIAL: Extraia o número de registro (registry_number), órgão (registry_agency) e ano (registry_year) se identificados no texto.

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

