# Diretório de Testes (`tests/`)

Esta pasta contém toda a **suíte de testes automatizados** da aplicação **ReadRelint**, desenvolvida utilizando a biblioteca `pytest`.

## 🧪 Suíte de Testes (36+ testes passando):

* **[test_entities.py](file:///d:/www/ReadRelint/tests/test_entities.py):** Validação dos contratos de dados e esquemas Pydantic (`IncidentReport` e envolvidos).
* **[test_pdf_reader.py](file:///d:/www/ReadRelint/tests/test_pdf_reader.py):** Testes unitários do leitor `PdfReader` utilizando mocks do PyMuPDF (`fitz`).
* **[test_tinydb_repo.py](file:///d:/www/ReadRelint/tests/test_tinydb_repo.py):** Testes das operações de leitura, gravação e atualização no `TinyDbRepo` com diretórios temporários (`tmp_path`).
* **[test_ollama_client.py](file:///d:/www/ReadRelint/tests/test_ollama_client.py):** Testes do adaptador OllamaClient mockando as requisições HTTP da API local.
* **[test_text_cleaner.py](file:///d:/www/ReadRelint/tests/test_text_cleaner.py):** Testes das regras de higienização e remoção de cabeçalhos institucionais do texto bruto dos RELINTs.
* **[test_folder_watcher.py](file:///d:/www/ReadRelint/tests/test_folder_watcher.py):** Testes de integração do monitorador de pastas e envio de eventos.
* **[test_rules.py](file:///d:/www/ReadRelint/tests/test_rules.py):** Testes unitários das regras de filtragem (`RelintRule`, `HomicideRule`) e orquestração do `EtlService`.
* **[test_local_regex_processor.py](file:///d:/www/ReadRelint/tests/test_local_regex_processor.py):** Testes do processador determinístico local (fallback).

## 🚀 Como Executar os Testes:
No terminal, na raiz do projeto, execute:
```bash
pytest
```
