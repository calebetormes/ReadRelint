# Estrutura do Projeto e Estado Atual

Este arquivo documenta a organização física de pastas e arquivos no repositório, bem como o resumo do progresso do desenvolvimento.

## 1. Estrutura de Diretórios e Arquivos

### Raiz do Projeto
*   **[.ai_context/](file:///d:/DEV26/ReadRelint/.ai_context)**: Diretório contendo os arquivos de documentação e contexto que guiam a IA na arquitetura e evolução do projeto.
    *   [01_blueprint.md](file:///d:/DEV26/ReadRelint/.ai_context/01_blueprint.md): Visão geral do projeto, objetivos e princípios fundamentais (regras de ouro de privacidade e idioma).
    *   [02_architecture.md](file:///d:/DEV26/ReadRelint/.ai_context/02_architecture.md): Descrição detalhada da arquitetura (Ports and Adapters), Stack Tecnológica e o Contrato de Dados (JSON do banco).
    *   [03_adr.md](file:///d:/DEV26/ReadRelint/.ai_context/03_adr.md): Registro de Decisões de Arquitetura (ADRs), explicando as escolhas técnicas feitas (ex: por que usar TinyDB, Ollama local, etc.).
    *   [04_current_state.md](file:///d:/DEV26/ReadRelint/.ai_context/04_current_state.md): Acompanhamento em tempo real do que foi implementado e dos próximos passos.
    *   [05_ai_workflow_scripts.md](file:///d:/DEV26/ReadRelint/.ai_context/05_ai_workflow_scripts.md): Scripts e diretrizes para automações e fluxos assistidos por IA.
    *   [06_talkia_rec.md](file:///d:/DEV26/ReadRelint/.ai_context/06_talkia_rec.md): Nosso histórico de conversas e alinhamentos efetuados no chat.
    *   [07_structure.md](file:///d:/DEV26/ReadRelint/.ai_context/07_structure.md): Este documento de estrutura e estado do projeto.
    *   [08_future_tasks.md](file:///d:/DEV26/ReadRelint/.ai_context/08_future_tasks.md): Registro e backlog de melhorias e tarefas futuras para discussão posterior.
*   **[.venv/](file:///d:/DEV26/ReadRelint/.venv)**: Ambiente virtual do Python, isolando as dependências externas do projeto.
*   **[.vscode/](file:///d:/DEV26/ReadRelint/.vscode)**: Configurações locais do editor VS Code (como o interpretador do Python).
*   **[.gitignore](file:///d:/DEV26/ReadRelint/.gitignore)**: Regras de exclusão de arquivos e pastas locais para controle de versão do Git.
*   **[INSTALL.md](file:///d:/DEV26/ReadRelint/INSTALL.md)**: Guia passo a passo de instalação e configuração do ambiente em outras máquinas.
*   **[pyrightconfig.json](file:///d:/DEV26/ReadRelint/pyrightconfig.json)**: Configurações de análise estática de tipos do Pyright para garantir a integridade do código Python.
*   **[requirements.txt](file:///d:/DEV26/ReadRelint/requirements.txt)**: Lista de bibliotecas externas utilizadas no projeto (como `customtkinter`, `pymupdf`, `watchdog`, etc.).



### Pasta de Código Fonte (`/src`)
O desenvolvimento segue o padrão de **Arquitetura Limpa (Ports & Adapters)**:
*   **[src/domain/](file:///d:/DEV26/ReadRelint/src/domain)**: Contém o coração (regras de negócio e entidades) do sistema. É escrito em Python puro e não possui dependências de framework ou bibliotecas externas de infraestrutura.
    *   [entities.py](file:///d:/DEV26/ReadRelint/src/domain/entities.py): Define o contrato e validações do boletim de ocorrência estruturado (`IncidentReport`).
    *   **[src/domain/rules/](file:///d:/DEV26/ReadRelint/src/domain/rules)**: Diretório contendo as definições de regras de filtragem e extração específicas por tipo de fato.
        *   [base_rule.py](file:///d:/DEV26/ReadRelint/src/domain/rules/base_rule.py): Classe abstrata base `IncidentRule`.
        *   [homicide_rule.py](file:///d:/DEV26/ReadRelint/src/domain/rules/homicide_rule.py): Regra concreta `HomicideRule` especializada em ocorrências de homicídio.
*   **[src/ports/](file:///d:/DEV26/ReadRelint/src/ports)**: Define as interfaces abstratas (contratos) das dependências externas do domínio.
    *   [file_parser.py](file:///d:/DEV26/ReadRelint/src/ports/file_parser.py): Interface `IFileParser` para extração de texto a partir de arquivos.
    *   [llm_processor.py](file:///d:/DEV26/ReadRelint/src/ports/llm_processor.py): Interface `ILlmProcessor` para processar e estruturar o texto bruto com IA.
    *   [database_repo.py](file:///d:/DEV26/ReadRelint/src/ports/database_repo.py): Interface `IDatabaseRepo` para persistência e consulta das entidades de incidentes estruturadas.
    *   [processed_registry.py](file:///d:/DEV26/ReadRelint/src/ports/processed_registry.py): Interface `IProcessedRegistry` para controle de histórico de processamento de PDFs por regra.
*   **[src/adapters/](file:///d:/DEV26/ReadRelint/src/adapters)**: Implementações concretas das portas da aplicação.
    *   [pdf_reader.py](file:///d:/DEV26/ReadRelint/src/adapters/pdf_reader.py): Leitor e extrator de PDFs usando a biblioteca `PyMuPDF`.
    *   [tinydb_repo.py](file:///d:/DEV26/ReadRelint/src/adapters/tinydb_repo.py): Banco embutido baseado em TinyDB com gravação serverless em arquivo JSON.
    *   [ollama_client.py](file:///d:/DEV26/ReadRelint/src/adapters/ollama_client.py): Processador de NLP e estruturação de IA local conectado à API do Ollama.
    *   [json_processed_registry.py](file:///d:/DEV26/ReadRelint/src/adapters/json_processed_registry.py): Registro concreto em formato JSON contendo o histórico de análises de arquivos por regra.
*   **[src/application/](file:///d:/DEV26/ReadRelint/src/application)**: Camada de aplicação que orquestra as regras de negócio e serviços.
    *   [etl_service.py](file:///d:/DEV26/ReadRelint/src/application/etl_service.py): Serviço que coordena o pipeline de ETL (Extração, Limpeza, Processamento LLM e Persistência).
    *   [text_cleaner.py](file:///d:/DEV26/ReadRelint/src/application/text_cleaner.py): Módulo com funções de limpeza do texto bruto dos RELINTs via regex.
*   **[src/infrastructure/](file:///d:/DEV26/ReadRelint/src/infrastructure)**: Serviços de infraestrutura global do sistema.
    *   [folder_watcher.py](file:///d:/DEV26/ReadRelint/src/infrastructure/folder_watcher.py): Monitorador de diretórios usando a biblioteca `watchdog` para detectar novos arquivos PDF adicionados.
*   **[src/presentation/](file:///d:/DEV26/ReadRelint/src/presentation)**: Responsável pelas interfaces de usuário.
    *   **[src/presentation/desktop/](file:///d:/DEV26/ReadRelint/src/presentation/desktop)**: Interface desktop local em CustomTkinter.
        *   [desktop_app.py](file:///d:/DEV26/ReadRelint/src/presentation/desktop/desktop_app.py): Painel de controle desktop para selecionar diretórios, monitorar a fila e logs em tempo real.
    *   **[src/presentation/web_dashboard/](file:///d:/DEV26/ReadRelint/src/presentation/web_dashboard)**: Interface web de relatórios e busca local.
        *   [dashboard_app.py](file:///d:/DEV26/ReadRelint/src/presentation/web_dashboard/dashboard_app.py): Dashboard interativo em Streamlit para busca, filtragem e agrupamento de boletins armazenados.

### Pasta de Testes (`/tests`)
Contém todos os testes automatizados da aplicação estruturados usando o Pytest:
*   [test_entities.py](file:///d:/DEV26/ReadRelint/tests/test_entities.py): Validação em tempo de execução dos esquemas Pydantic.
*   [test_pdf_reader.py](file:///d:/DEV26/ReadRelint/tests/test_pdf_reader.py): Testes unitários da classe `PdfReader` mockando o `fitz` (PyMuPDF).
*   [test_tinydb_repo.py](file:///d:/DEV26/ReadRelint/tests/test_tinydb_repo.py): Testes de gravação e consulta do `TinyDbRepo` usando a fixture `tmp_path`.
*   [test_ollama_client.py](file:///d:/DEV26/ReadRelint/tests/test_ollama_client.py): Testes da API HTTP do Ollama mockando o módulo `requests`.
*   [test_text_cleaner.py](file:///d:/DEV26/ReadRelint/tests/test_text_cleaner.py): Testes das regras de limpeza de cabeçalhos e termos de corte do texto bruto dos RELINTs.
*   [test_folder_watcher.py](file:///d:/DEV26/ReadRelint/tests/test_folder_watcher.py): Testes de monitoramento de pastas e detecção de arquivos.
*   [test_rules.py](file:///d:/DEV26/ReadRelint/tests/test_rules.py): Testes unitários das regras de filtragem rápida e orquestração do EtlService.

### Scripts Utilitários (Raiz)
*   [read_pdf_test.py](file:///d:/DEV26/ReadRelint/read_pdf_test.py): Script de testes manuais para validação de extração de texto de PDFs reais locais.
*   [run_pipeline_test.py](file:///d:/DEV26/ReadRelint/run_pipeline_test.py): Script de testes manuais de integração de fluxo completo (Leitura PDF -> IA Ollama -> TinyDB).
