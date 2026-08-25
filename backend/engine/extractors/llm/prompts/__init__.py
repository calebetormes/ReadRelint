# -*- coding: utf-8 -*-
"""
Builder para montagem modular do prompt de extração da LLM.
"""

import json
from typing import Optional, Dict, Any, List
from backend.engine.extractors.llm.prompts.system_prompt import SYSTEM_PROMPT
from backend.engine.extractors.llm.prompts.summary_prompt import SUMMARY_PROMPT
from backend.engine.extractors.llm.prompts.address_prompt import ADDRESS_PROMPT


def build_extraction_prompt(
    text: str,
    schema_str: str,
    rule_system_prompt: str = "",
    pre_extracted_entities: Optional[List[Dict[str, Any]]] = None
) -> str:
    """
    Monta o prompt completo e estruturado para envio ao modelo LLM.
    """
    entities_section = ""
    if pre_extracted_entities:
        entities_section = f"""
ENTIDADES PRÉ-EXTRAÍDAS (ZERO-SHOT NER):
Utilize a lista de entidades abaixo identificadas no texto como auxílio de contexto:
{json.dumps(pre_extracted_entities, ensure_ascii=False, indent=2)}
"""

    rule_section = f"\n{rule_system_prompt}\n" if rule_system_prompt else ""

    prompt = f"""{SYSTEM_PROMPT}

{rule_section}
{SUMMARY_PROMPT}
{ADDRESS_PROMPT}
{entities_section}

INSTRUÇÕES DE FORMATAÇÃO:
1. Você DEVE retornar EXATAMENTE UM objeto JSON válido que obedeça estritamente ao JSON Schema fornecido.
2. Não inclua texto explicativo, blocos markdown adicionais ou comentários fora do JSON.
3. Se um campo do tipo Enum for exigido, use apenas os valores listados em 'enum'.

JSON SCHEMA:
{schema_str}

TEXTO DO RELINT PARA ANÁLISE:
---
{text}
---
"""
    return prompt.strip()
