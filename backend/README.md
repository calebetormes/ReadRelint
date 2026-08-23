# Diretório `src/` (Código Fonte)

Este diretório contém todo o código-fonte da aplicação **ReadRelint**, organizado modularmente segundo os princípios da **Arquitetura Limpa (Ports and Adapters)**:

## 📂 Organização dos Módulos:

* **[dashboard/](file:///e:/www/ReadRelint/src/dashboard):** Camadas de apresentação e persistência do sistema:
  * `backend/`: API REST FastAPI, banco de dados relacional SQLite (`SqliteRepo`, `SqlitePersonRepo`) e entidades de domínio (`IncidentReport`, `Person`, `Participant`).
  * `desktop/`: Interface gráfica desktop em CustomTkinter (Service Launcher & Status Hub) e controle de serviços.
  * `frontend/`: SPA Web moderna em Resend Dark System (HTML5, Vanilla CSS, JS views).
* **[engine/](file:///e:/www/ReadRelint/src/engine):** Motores de processamento e extração de dados:
  * `cleaners/`: Higienização e sanitização de texto bruto (`text_cleaner.py`) e classificadores de grupo BM (`bm_classifier.py`).
  * `parsers/`: Leitura e extração de texto e imagens de documentos PDF (`PdfReader`).
  * `extractors/`: Motores de extração e especialidades polimórficas:
    * `llm/`: Motor cognitivo via Ollama local (`OllamaClient`) e regras de IA (`rules/`) com prompts e schemas Pydantic.
    * `deterministic/`: Motor determinístico sem IA (`pipeline.py`), extrator de participantes em 5 camadas (`participants/`), endereços, síntese e regras de crimes determinísticas (`rules/`).
    * `common/`: Dicionários de exclusão negativos e base estática de prenomes IBGE.
* **[task_manager/](file:///e:/www/ReadRelint/src/task_manager):** Orquestração de tarefas assíncronas e monitoramento:
  * `etl/`: Pipeline de ingestão, orquestração e sanitização (`EtlService`).
  * `watcher/`: Monitoramento de diretório de arquivos no Windows via `watchdog` (`FolderWatcher`).
  * `registry/`: Registro de histórico de processamento e proteção de curadoria humana (`JsonProcessedRegistry`).
  .
