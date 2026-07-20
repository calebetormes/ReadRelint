import logging
from typing import Dict, Optional
from transformers import pipeline
from src.ports.llm_processor import ILlmProcessor

logger = logging.getLogger(__name__)

class TransformersQaClient(ILlmProcessor):
    """
    Implementação concreta (Adapter) para processamento de linguagem natural usando
    um modelo de Question Answering (QA) extrativo local do Hugging Face.
    """

    def __init__(self, model_name: str = "pierreguillou/bert-large-cased-squad-v1.1-portuguese"):
        """
        Inicializa o pipeline de QA do Hugging Face. O modelo é baixado automaticamente
        na primeira execução se não estiver em cache local.

        :param model_name: Nome do modelo no Hugging Face Hub.
        """
        self.model_name = model_name
        self.qa_pipeline = None

    def _lazy_init(self):
        """
        Carrega o pipeline apenas quando necessário (lazy initialization) para evitar
        lentidão no início da aplicação caso o modelo não seja utilizado imediatamente.
        """
        if self.qa_pipeline is None:
            logger.info(f"Inicializando pipeline de QA com o modelo: {self.model_name}")
            self.qa_pipeline = pipeline(
                "question-answering",
                model=self.model_name,
                device=-1  # Força CPU por padrão (mais portável, evita problemas com CUDA)
            )


    def process_text(self, text: str, questions: Optional[Dict[str, str]] = None) -> dict:
        """
        Processa o texto respondendo a cada uma das perguntas fornecidas.

        :param text: O texto da ocorrência (contexto).
        :param questions: Dicionário mapeando chaves para perguntas (ex: {'content': 'Qual o fato?'}).
        :return: Dicionário contendo as respostas para cada chave.
        """
        if not questions:
            return {"content": text}

        self._lazy_init()
        results = {}

        for key, question in questions.items():
            try:
                # O pipeline resolve automaticamente o fatiamento de textos longos
                response = self.qa_pipeline(
                    question=question,
                    context=text,
                    max_answer_len=150,
                    handle_impossible_answer=True
                )
                answer = response.get("answer", "").strip()
                results[key] = answer
            except Exception as e:
                logger.error(f"Erro ao obter resposta para a pergunta '{question}': {e}")
                results[key] = ""

        return results
