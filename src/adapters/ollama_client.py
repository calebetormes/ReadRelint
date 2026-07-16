import json
import requests
from src.ports.llm_processor import ILlmProcessor

class OllamaClient(ILlmProcessor):
    """
    Implementação concreta (Adapter) para processamento simplificado de RELINTs
    usando a API local de uma LLM rodando via Ollama.
    """

    OLLAMA_SYSTEM_PROMPT = (
        "You are an expert police analyst. Read the provided police report and extract the main content/facts "
        "into a structured JSON object matching this schema exactly:\n"
        "{\n"
        '  "content": "A clear, detailed summary of the main incident/facts in Brazilian Portuguese."\n'
        "}\n"
        "Ensure the output conforms strictly to this JSON structure without markdown code blocks, backticks, or extra text."
    )

    def __init__(self, model_name: str = "llama3.1", base_url: str = "http://localhost:11434"):
        """
        Inicializa o cliente Ollama com o modelo e a URL base desejada.

        :param model_name: Nome do modelo a ser chamado no Ollama (ex: llama3.1).
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

    def process_text(self, text: str) -> str:
        """
        Processa o texto do relatório policial e retorna o resumo estruturado dos fatos.
        """
        raw_response = self._call_ollama_json(self.OLLAMA_SYSTEM_PROMPT, text)
        try:
            parsed = json.loads(raw_response)
            if isinstance(parsed, dict) and "content" in parsed:
                return parsed["content"]
            else:
                # Se não contiver a chave "content" mas for dicionário, tenta retornar a representação em string ou dar erro
                raise ValueError("A resposta não possui a chave 'content' no JSON retornado.")
        except json.JSONDecodeError as e:
            raise ValueError(f"Não foi possível decodificar a resposta em JSON: {e}. Resposta bruta: {raw_response}")
