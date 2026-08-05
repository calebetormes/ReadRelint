import json
import logging
import requests
from typing import Dict, Optional
from src.ports.llm_processor import ILlmProcessor
from src.domain.entities import IncidentReport

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

    def process_text(self, text: str, questions: Optional[Dict[str, str]] = None) -> dict:
        """
        Envia o texto limpo ao Ollama solicitando a estruturação em formato JSON
        baseado no JSON Schema do modelo IncidentReport.
        """
        system_prompt = ""
        if questions and "system_prompt" in questions:
            system_prompt = questions["system_prompt"]
        
        # Gera o JSON Schema do modelo Pydantic para orientar a extração
        schema = IncidentReport.model_json_schema()
        # Remove campos mantidos pelo sistema Python para não poluir nem confundir o Ollama
        if "properties" in schema:
            schema["properties"].pop("source_file", None)
            schema["properties"].pop("content", None)
            schema["properties"].pop("user_edited", None)
            
        schema_str = json.dumps(schema, indent=2, ensure_ascii=False)

        prompt = f"""
{system_prompt}

INSTRUÇÕES DE SAÍDA:
1. Você DEVE retornar EXATAMENTE UM objeto JSON válido que obedeça ao seguinte JSON Schema.
2. Não inclua comentários, explicações ou texto fora do JSON.
3. Se um campo do tipo Enum for exigido, você só pode usar os valores listados em 'enum'.
4. PARTICIPANTES: Extraia apenas civis envolvidos (vítimas, acusados, suspeitos, testemunhas). NUNCA inclua os Policiais Militares que atenderam a ocorrência.
5. RESUMO (summary): Escreva um resumo narrativo explicativo em 1 parágrafo com os fatos principais.

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
            response = requests.post(url, json=payload, timeout=90)
            
            # Recuperação Automática: Se der 404 (model not found), tenta buscar modelos ativos no Ollama
            if response.status_code == 404:
                logger.warning(f"Modelo '{self.model_name}' não encontrado no Ollama. Buscando modelos alternativos...")
                tags_response = requests.get(f"{self.base_url}/api/tags", timeout=10)
                if tags_response.status_code == 200:
                    models = tags_response.json().get("models", [])
                    if models:
                        alternative_model = models[0]["name"]
                        logger.info(f"Alternando automaticamente para o modelo disponível: '{alternative_model}'")
                        self.model_name = alternative_model
                        payload["model"] = alternative_model
                        
                        # Segunda tentativa
                        response = requests.post(url, json=payload, timeout=90)
            
            response.raise_for_status()
            
            response_json = response.json()
            response_text = response_json.get("response", "{}")
            
            extracted_data = json.loads(response_text)
            return extracted_data
            
        except Exception as e:
            logger.error(f"Erro ao processar texto com Ollama: {e}")
            return {}

