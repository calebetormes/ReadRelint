import os
import re
from pathlib import Path
from typing import List, Dict, Any, Optional

try:
    from unstructured.partition.pdf import partition_pdf
    from unstructured.documents.elements import NarrativeText, Title, ListItem, Text
    UNSTRUCTURED_AVAILABLE = True
except ImportError:
    UNSTRUCTURED_AVAILABLE = False

try:
    from gliner import GLiNER
    GLINER_AVAILABLE = True
except ImportError:
    GLINER_AVAILABLE = False

class HybridCleaner:
    _gliner_model = None

    @classmethod
    def get_gliner_model(cls):
        if not GLINER_AVAILABLE:
            return None
        if cls._gliner_model is None:
            # Carrega o modelo de forma preguiçosa (Singleton)
            cls._gliner_model = GLiNER.from_pretrained("urchade/gliner_small-v2.1")
        return cls._gliner_model

    @staticmethod
    def extract_structural_text(pdf_path: Path) -> str:
        """
        Usa particionamento de ML visual para extrair o texto, filtrando 
        cabeçalhos e rodapés institucionais.
        """
        if not UNSTRUCTURED_AVAILABLE:
            from src.engine.cleaners.text_cleaner import clean_relint_text
            import fitz
            doc = fitz.open(str(pdf_path))
            raw_text = chr(12).join([page.get_text() for page in doc])
            return clean_relint_text(raw_text)
            
        try:
            # strategy='fast' evita OCR pesado e usa pdfminer (ideal para PDF digital)
            elements = partition_pdf(filename=str(pdf_path), strategy="fast")
            
            clean_blocks = []
            for element in elements:
                # Unstructured classifica automaticamente Headers e Footers. 
                # Pegamos apenas blocos de conteúdo útil:
                if isinstance(element, (NarrativeText, Title, ListItem, Text)):
                    text_content = str(element).strip()
                    if text_content:
                        clean_blocks.append(text_content)
            
            # Reagrupa mantendo separação de parágrafos
            final_text = "\n\n".join(clean_blocks)
            
            # Um pequeno retoque final para garantir
            from src.engine.cleaners.text_cleaner import normalize_whitespace_and_paragraphs
            return normalize_whitespace_and_paragraphs(final_text)
            
        except Exception as e:
            print(f"Erro no Unstructured, fazendo fallback para PyMuPDF: {e}")
            from src.engine.cleaners.text_cleaner import clean_relint_text
            import fitz
            doc = fitz.open(str(pdf_path))
            raw_text = chr(12).join([page.get_text() for page in doc])
            return clean_relint_text(raw_text)

    @classmethod
    def extract_entities_gliner(cls, text: str) -> List[Dict[str, Any]]:
        """
        Extrai Nomes, CPFs, RGs e Localizações usando modelo GLiNER Zero-Shot NER.
        """
        model = cls.get_gliner_model()
        if not model or not text.strip():
            return []

        labels = ["Nome e Sobrenome da Pessoa", "RG", "CPF", "Alcunha ou Vulgo", "Data", "Endereço Completo", "Unidade Policial", "Crime"]
        
        try:
            # Analisamos um pedaço considerável do texto
            text_to_analyze = text[:4000]
            entities_found = model.predict_entities(text_to_analyze, labels)
            
            formatted_entities = []
            for ent in entities_found:
                if ent.get("score", 0) > 0.5: # Limite de confiança
                    label_name = ent["label"]
                    if label_name == "Nome e Sobrenome da Pessoa":
                        label_name = "Pessoa"
                    elif label_name == "Alcunha ou Vulgo":
                        label_name = "Alcunha"
                    elif label_name == "Endereço Completo":
                        label_name = "Endereço"
                        
                    formatted_entities.append({
                        "label": label_name,
                        "text": ent["text"],
                        "score": ent.get("score")
                    })
            
            return formatted_entities
        except Exception as e:
            print(f"Erro no GLiNER: {e}")
            return []

    @classmethod
    def process_hybrid(cls, pdf_path: Path) -> tuple[str, List[Dict[str, Any]]]:
        """Processamento consolidado."""
        text = cls.extract_structural_text(pdf_path)
        entities = cls.extract_entities_gliner(text)
        return text, entities
