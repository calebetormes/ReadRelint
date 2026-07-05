import json
import requests
from typing import List
from src.domain.entities import IncidentReport
from src.ports.llm_processor import ILlmProcessor

class OllamaClient(ILlmProcessor):
    """
    Implementação concreta (Adapter) para processamento multifásico de RELINTs
    usando a API local de uma LLM rodando via Ollama.
    """

    OLLAMA_METADATA_PROMPT = (
        "You are an expert data parser. Parse the provided police report header and extract the following metadata "
        "into a JSON object matching this schema exactly:\n"
        "{\n"
        '  "relint_number": "Number of the RELINT (e.g. 001/2026) or null",\n'
        '  "subject": "Subject of the report or null",\n'
        '  "diffusion": "Diffusion channels or null",\n'
        '  "attachment": "Attachments mentioned or null"\n'
        "}\n"
        "Ensure the output conforms strictly to this JSON structure without markdown code blocks, backticks, or extra text."
    )

    OLLAMA_SEGMENT_PROMPT = (
        "You are an expert police analyst. Read the provided police report and identify all distinct crime occurrences/incidents described in the text.\n"
        "For each occurrence, segment the text and classify it into one of these groups:\n"
        "1. 'Ocorrências do AVANTE' (strictly when the crime type is one of: 'Homicídio Doloso Consumado', 'Homicídio Tentado', 'Roubo a Estabelecimento', 'Roubo de Veículo', 'Roubo a Pedestre', 'Roubo a Residência', 'Furto de Veículo', 'Furto Abigeato')\n"
        "2. 'Ocorrências Importantes fora do AVANTE' (strictly when the crime type is one of: 'Prisão de Foragido', 'Tráfico de Drogas', 'Resistência, Desacato e Desobediência')\n"
        "3. 'Demais Fatos' (any other crime or event)\n\n"
        "Also classify the nature of each occurrence ('incident_nature') as strictly one of:\n"
        "- 'Ocorrência' (for concrete occurrences that actually happened, either consummated or attempted)\n"
        "- 'Denúncia' (for anonymous reports/complaints without immediately verified facts)\n"
        "- 'Resposta a Pedido de Busca' (for formal replies to Search Requests - Pedidos de Busca)\n"
        "- 'Informação' (for purely informative or intelligence reports)\n"
        "- 'Outro' (for other administrative or non-criminal records)\n\n"
        "Format the output strictly as a JSON object matching this schema:\n"
        "{\n"
        '  "occurrences": [\n'
        "    {\n"
        '      "incident_nature": "Nature name (Ocorrência, Denúncia, Resposta a Pedido de Busca, Informação, Outro)",\n'
        '      "incident_group": "Group name (Ocorrências do AVANTE, Ocorrências Importantes fora do AVANTE, Demais Fatos)",\n'
        '      "incident_type": "Specific nature of the crime (e.g. Furto de Veículo, Tráfico de Drogas, Estelionato)",\n'
        '      "incident_text_segment": "The exact raw text segment from the report that describes this specific occurrence"\n'
        "    }\n"
        "  ]\n"
        "}\n"
        "Ensure the output conforms strictly to this JSON structure without markdown code blocks, backticks, or extra conversational text."
    )

    OLLAMA_INCIDENT_PROMPT = (
        "You are an expert data parser. Parse the provided police incident text segment and extract "
        "the structured details into a JSON object matching this schema exactly:\n"
        "{\n"
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
        "Ensure the output conforms strictly to this JSON structure without markdown code blocks, backticks, or extra text."
    )

    def __init__(self, model_name: str = "llama3.1", base_url: str = "http://localhost:11434"):
        """
        Inicializa o cliente Ollama com o modelo e a URL base desejada.

        :param model_name: Nome do modelo a ser chamado no Ollama (ex: llama3, mistral).
        :param base_url: URL base da API HTTP do Ollama.
        """
        self.model_name = model_name
        self.endpoint = f"{base_url.rstrip('/')}/api/generate"

    def _call_ollama_json(self, prompt: str, text: str) -> str:
        """
        Método auxiliar para chamar a API do Ollama forçando saída em JSON.
        """
        payload = {
            "model": self.model_name,
            "prompt": f"{prompt}\n\nInput Text:\n{text}",
            "format": "json",
            "stream": False,
            "options": {
                "temperature": 0.1
            }
        }
        try:
            response = requests.post(self.endpoint, json=payload, timeout=60)
            response.raise_for_status()
            response_json = response.json()
            raw_llm_response = response_json.get("response", "").strip()
            if not raw_llm_response:
                raise ValueError("Resposta do Ollama está vazia ou sem chave 'response'.")
            return raw_llm_response
        except requests.RequestException as e:
            raise RuntimeError(f"Erro na comunicação com a API local do Ollama: {e}")

    def extract_metadata(self, text: str) -> dict:
        """
        Extrai metadados gerais (Número do RELINT, Assunto, Difusão e Anexo) do cabeçalho.
        """
        # Foca nos primeiros 1500 caracteres para o cabeçalho
        header_sample = text[:1500]
        raw_response = self._call_ollama_json(self.OLLAMA_METADATA_PROMPT, header_sample)
        try:
            return json.loads(raw_response)
        except json.JSONDecodeError as e:
            raise ValueError(f"Não foi possível decodificar os metadados do documento: {e}. Resposta: {raw_response}")

    def segment_occurrences(self, text: str) -> list:
        """
        Analisa o texto do RELINT e o divide em ocorrências estruturadas por grupo.
        """
        raw_response = self._call_ollama_json(self.OLLAMA_SEGMENT_PROMPT, text)
        try:
            parsed = json.loads(raw_response)
            if isinstance(parsed, dict) and "occurrences" in parsed:
                return parsed["occurrences"]
            elif isinstance(parsed, list):
                return parsed
            else:
                raise ValueError("A resposta de segmentação não possui um formato de objeto ou lista esperado.")
        except json.JSONDecodeError as e:
            raise ValueError(f"Não foi possível decodificar a lista de ocorrências: {e}. Resposta: {raw_response}")

    def process_incident_text(self, text: str) -> IncidentReport:
        """
        Método de compatibilidade. Processa um segmento de texto e retorna IncidentReport.
        OBS: Para criar um IncidentReport válido de forma direta, injeta o grupo e o tipo como padrão provisório.
        """
        raw_response = self._call_ollama_json(self.OLLAMA_INCIDENT_PROMPT, text)
        try:
            parsed_data = json.loads(raw_response)
        except (json.JSONDecodeError, TypeError) as e:
            raise ValueError(f"Ollama não retornou um JSON de resposta decodificável: {e}. Resposta bruta: {raw_response}")

        try:
            # Injeta valores padrão caso o método seja chamado individualmente
            if "incident_nature" not in parsed_data:
                parsed_data["incident_nature"] = "Ocorrência"
            if "incident_group" not in parsed_data:
                parsed_data["incident_group"] = "Demais Fatos"
            if "incident_type" not in parsed_data:
                parsed_data["incident_type"] = "Fato Registrado"
            return IncidentReport(**parsed_data)
        except Exception as e:
            raise ValueError(f"O JSON retornado pela LLM não atende aos requisitos do domínio IncidentReport: {e}. Resposta: {raw_response}")

    def process_incident_segment(self, segment_text: str, group: str, incident_type: str, incident_nature: str = "Ocorrência") -> IncidentReport:
        """
        Processa um segmento específico de texto correspondente a uma única ocorrência já classificada.
        Injeta os metadados do enquadramento identificados na Fase 3.
        """
        raw_response = self._call_ollama_json(self.OLLAMA_INCIDENT_PROMPT, segment_text)
        try:
            parsed_data = json.loads(raw_response)
        except (json.JSONDecodeError, TypeError) as e:
            raise ValueError(f"Ollama não retornou um JSON de resposta decodificável: {e}. Resposta bruta: {raw_response}")

        try:
            # Garante que os campos de enquadramento da Fase 3 sejam injetados sem alucinações na Fase 4
            parsed_data["incident_nature"] = incident_nature
            parsed_data["incident_group"] = group
            parsed_data["incident_type"] = incident_type
            return IncidentReport(**parsed_data)
        except Exception as e:
            raise ValueError(f"Falha ao estruturar a ocorrência de {incident_type} ({group}): {e}. Resposta: {raw_response}")
