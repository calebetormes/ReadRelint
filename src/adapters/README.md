# Camada de Adaptadores (`src/adapters/`)

Esta pasta armazena as **implementações concretas (Adapters)** para as interfaces definidas em `src/ports/`.

## 📌 Tecnologias Adaptadas:
É nesta camada que residem as bibliotecas externas e chamadas de API concretas (como PyMuPDF, Ollama, TinyDB e expressões regulares).

## 📄 Arquivos Contidos:

* **[pdf_reader.py](file:///d:/www/ReadRelint/src/adapters/pdf_reader.py):** Adaptador concreto de `IFileParser` utilizando a biblioteca `PyMuPDF` (fitz) para extração de texto bruto de documentos PDF.
* **[ollama_client.py](file:///d:/www/ReadRelint/src/adapters/ollama_client.py):** Adaptador concreto de `ILlmProcessor` que se comunica com a API local do **Ollama**, realizando extração estruturada de JSON com mecânica de auto-recuperação (Self-Healing).
* **[tinydb_repo.py](file:///d:/www/ReadRelint/src/adapters/tinydb_repo.py):** Adaptador concreto de `IDatabaseRepo` que implementa a persistência serverless NoSQL utilizando a biblioteca `TinyDB`.
* **[json_processed_registry.py](file:///d:/www/ReadRelint/src/adapters/json_processed_registry.py):** Adaptador concreto de `IProcessedRegistry` que grava e lê o histórico de arquivos analisados em arquivo JSON local com thread-safety.
* **[local_regex_processor.py](file:///d:/www/ReadRelint/src/adapters/local_regex_processor.py):** Adaptador alternativo baseado em expressões regulares locais (utilizado como fallback determinístico sem IA).
