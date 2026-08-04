import json
import logging
import requests
from typing import Dict, Optional
from src.ports.llm_processor import ILlmProcessor

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
        Envia o texto limpo ao Ollama solicitando a estruturação em formato JSON.
        """
        prompt = f"""
        Você é um analista de inteligência especializado. Analise o documento RELINT abaixo e extraia as informações estruturadas no formato JSON especificado.

        REGRAS DE EXTRAÇÃO:
        1. "subject" (Assunto Principal): Identifique o assunto principal ou o fato principal do relatório em uma frase curta de até 15 palavras.
        2. "date_of_fact" (Data do Fato): Identifique a data em que os fatos relatados ocorreram no formato DD/MM/AAAA. Se houver mais de uma data (como a data de emissão ou data de nascimento), identifique a data principal da ocorrência dos fatos. Se não encontrar nenhuma data de ocorrência, retorne null.
        3. "bm_group" (Grupo BM): Enquadre o fato estritamente em uma destas opções: "Roubos", "Furtos", "Homicídios" ou "Outros". Use lógica jurídica básica (se houver agressão/ameaça/violência para roubar, enquadre como Roubos; se houver morte violenta, tentativa de homicídio ou encontro de cadáver, enquadre como Homicídios; se houver furto simples/arrombamento sem contato ou violência, enquadre como Furtos; senão, Outros).
        4. "summary" (Resumo): Escreva um resumo conciso do caso de exatamente um único parágrafo simples e explicativo.
        5. "participants" (Participantes): Extraia a lista de todas as pessoas citadas (vítimas, suspeitos, autores, testemunhas). Para cada participante, preencha:
           - "name" (Nome completo da pessoa, se disponível. Se houver apenas prenome, use-o).
           - "nickname" (Alcunha, vulgo ou apelido, se citado. Caso contrário, null).
           - "document" (CPF no formato 000.000.000-00 ou número de RG se citado. Caso contrário, null).

        Retorne estritamente um objeto JSON válido, sem comentários e sem formatação markdown extra, contendo exatamente as chaves abaixo:
        {{
            "subject": "Resumo do assunto principal",
            "date_of_fact": "DD/MM/AAAA ou null",
            "bm_group": "Roubos / Furtos / Homicídios / Outros",
            "summary": "Resumo em um parágrafo...",
            "participants": [
                {{
                    "name": "Nome Completo ou null",
                    "nickname": "Vulgo ou null",
                    "document": "CPF/RG ou null"
                }}
            ]
        }}

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
            response = requests.post(url, json=payload, timeout=60)
            
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
                        response = requests.post(url, json=payload, timeout=60)
            
            response.raise_for_status()
            
            response_json = response.json()
            response_text = response_json.get("response", "{}")
            
            extracted_data = json.loads(response_text)
            
            # Formata e higieniza a saída estruturada
            return {
                "subject": extracted_data.get("subject"),
                "date_of_fact": extracted_data.get("date_of_fact"),
                "bm_group": extracted_data.get("bm_group", "Outros"),
                "summary": extracted_data.get("summary"),
                "participants": extracted_data.get("participants", []),
                "content": text
            }
        except Exception as e:
            logger.error(f"Erro ao processar texto com Ollama: {e}")
            return {
                "subject": "Erro de processamento da IA",
                "date_of_fact": None,
                "bm_group": "Outros",
                "summary": f"Erro de processamento local da LLM: {str(e)}",
                "participants": [],
                "content": text
            }
