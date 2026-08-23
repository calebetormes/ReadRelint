# Módulo `backend/` (Serviços e Domínio)

Este diretório contém o código-fonte dos serviços de backend, banco de dados relacional e motor de extração da aplicação **ReadRelint**, organizado segundo os princípios da **Arquitetura Limpa (Ports and Adapters)**:

## 📂 Organização dos Módulos Backend:

* **`api/`**: Camada de endpoints REST FastAPI e dependências HTTP (`/api/v1/relints`, `/api/v1/monitoring`, `/api/v1/events`).
* **`core/`**: Entidades de domínio (`IncidentReport`, `HomicideReport`, `Person`, `Participant`) e serviços de suporte geométrico/geocodificação.
* **`database/`**: Camada de persistência relacional em SQLite nativo (`SqliteRepo`, `SqlitePersonRepo`) com suporte a migração automática de esquemas.
* **`engine/`**: Motores de processamento e extração de dados:
  * `cleaners/`: Higienização e sanitização de texto bruto (`text_cleaner.py`) e classificadores de grupo BM (`bm_classifier.py`).
  * `parsers/`: Leitura e extração de texto e imagens de documentos PDF (`PdfReader`).
  * `extractors/`: Motores de extração cognitivos via Ollama local (`OllamaClient`) e determinísticos (`pipeline.py`).
* **`task_manager/`**: Orquestração de tarefas assíncronas e monitoramento:
  * `etl/`: Pipeline de ingestão, orquestração e sanitização (`EtlService`).
  * `watcher/`: Monitoramento de diretório de arquivos no Windows via `watchdog` (`FolderWatcher`).
  * `registry/`: Controle de histórico de arquivos processados (`JsonProcessedRegistry`).
