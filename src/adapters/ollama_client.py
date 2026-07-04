import json
import requests
from src.domain.entities import IncidentReport
from src.ports.llm_processor import ILlmProcessor

class OllamaClient(ILlmProcessor):
    """
    Implementação concreta (Adapter) para estruturação de dados de Boletins de Ocorrência
    usando a API local de uma LLM rodando via Ollama.
    """

    def __init__(self, model_name: str = "llama3.1", base_url: str = "http://localhost:11434"):
        """
        Inicializa o cliente Ollama com o modelo e a URL base desejada.

        :param model_name: Nome do modelo a ser chamado no Ollama (ex: llama3, mistral).
        :param base_url: URL base da API HTTP do Ollama.
        """
        self.model_name = model_name
        self.endpoint = f"{base_url.rstrip('/')}/api/generate"

    def process_incident_text(self, text: str) -> IncidentReport:
        """
        Envia o texto bruto do Boletim de Ocorrência para a LLM via API do Ollama,
        forçando a saída estruturada em JSON e mapeando para o IncidentReport.

        :param text: Texto bruto do BO.
        :return: Uma entidade de domínio IncidentReport preenchida.
        :raises RuntimeError: Se a chamada HTTP falhar ou o serviço estiver inacessível.
        :raises ValueError: Se a resposta da LLM não for um JSON válido ou não estiver no formato esperado.
        """
        system_instructions = (
            "You are an expert data parser. Parse the provided police report and extract "
            "the structured information into a JSON object matching this schema exactly:\n"
            "{\n"
            '  "incident_type": "Nature of the incident (e.g. Roubo, Furto, Estelionato)",\n'
            '  "incident_time": "Date/time in ISO 8601 format or null",\n'
            '  "address": {\n'
            '    "street": "Street name",\n'
            '    "number": "Number or null",\n'
            '    "neighborhood": "Neighborhood or null",\n'
            '    "city": "City or null"\n'
            '  },\n'
            '  "participants": [\n'
            '    {"name": "Full name", "role": "Role (e.g. Vítima, Autor, Testemunha, Comunicante)"}\n'
            '  ],\n'
            '  "vehicles": [\n'
            '    {"plate": "Plate or null", "model": "Model/brand or null", "color": "Color or null"}\n'
            '  ],\n'
            '  "attending_officer": "Name of the officer/authority or null",\n'
            '  "history_summary": "A concise summary of the facts in Brazilian Portuguese"\n'
            "}\n"
            "Ensure the output conforms strictly to this JSON model without markdown wraps or extra conversational text."
        )

        payload = {
            "model": self.model_name,
            "prompt": f"{system_instructions}\n\nReport Text:\n{text}",
            "format": "json",
            "stream": False,
            "options": {
                "temperature": 0.1
            }
        }

        try:
            response = requests.post(self.endpoint, json=payload, timeout=60)
            response.raise_for_status()
        except requests.RequestException as e:
            raise RuntimeError(f"Erro na comunicação com a API local do Ollama: {e}")

        try:
            response_json = response.json()
            raw_llm_response = response_json.get("response", "")
            if not raw_llm_response:
                raise ValueError("Resposta do Ollama está vazia ou sem chave 'response'.")
            
            # Decodifica o texto JSON gerado pelo modelo
            parsed_data = json.loads(raw_llm_response)
        except (json.JSONDecodeError, TypeError, KeyError) as e:
            raise ValueError(f"Ollma não retornou um JSON de resposta decodificável: {e}. Resposta bruta: {response.text}")

        try:
            # Converte o dicionário decodificado na entidade de domínio
            return IncidentReport(**parsed_data)
        except Exception as e:
            raise ValueError(f"O JSON retornado pela LLM não atende aos requisitos do domínio IncidentReport: {e}")
