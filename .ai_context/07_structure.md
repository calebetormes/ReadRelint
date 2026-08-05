# Estrutura do Projeto e Estado Atual

Este arquivo documenta a organização física de pastas e arquivos no repositório, bem como o resumo do progresso do desenvolvimento.

## 1. Estrutura de Diretórios e Arquivos

### Raiz do Projeto
*   **[README.md](file:///d:/www/ReadRelint/README.md)**: Visão geral e guia rápido do projeto.
*   **[Iniciar-Painel.bat](file:///d:/www/ReadRelint/Iniciar-Painel.bat)**: Script em lote para inicialização rápida do painel desktop e do dashboard web.
*   **[.ai_context/](file:///d:/www/ReadRelint/.ai_context)**: Diretório contendo os arquivos de documentação e contexto que guiam a IA na arquitetura e evolução do projeto.
    *   [README.md](file:///d:/www/ReadRelint/.ai_context/README.md): Documentação interna do diretório de contexto.
    *   [01_blueprint.md](file:///d:/www/ReadRelint/.ai_context/01_blueprint.md): Visão geral do projeto, objetivos e princípios fundamentais (regras de ouro de privacidade e idioma).
    *   [02_architecture.md](file:///d:/www/ReadRelint/.ai_context/02_architecture.md): Descrição detalhada da arquitetura (Ports and Adapters), Stack Tecnológica e o Contrato de Dados (JSON do banco).
    *   [03_adr.md](file:///d:/www/ReadRelint/.ai_context/03_adr.md): Registro de Decisões de Arquitetura (ADRs), explicando as escolhas técnicas feitas (ex: por que usar TinyDB, Ollama local, etc.).
    *   [04_current_state.md](file:///d:/www/ReadRelint/.ai_context/04_current_state.md): Acompanhamento em tempo real do que foi implementado e dos próximos passos.
    *   [05_ai_workflow_scripts.md](file:///d:/www/ReadRelint/.ai_context/05_ai_workflow_scripts.md): Scripts e diretrizes para automações e fluxos assistidos por IA.
    *   [06_talkia_rec.md](file:///d:/www/ReadRelint/.ai_context/06_talkia_rec.md): Nosso histórico de conversas e alinhamentos efetuados no chat.
    *   [07_structure.md](file:///d:/www/ReadRelint/.ai_context/07_structure.md): Este documento de estrutura e estado do projeto.
    *   [08_future_tasks.md](file:///d:/www/ReadRelint/.ai_context/08_future_tasks.md): Registro e backlog de melhorias e tarefas futuras para discussão posterior.
    *   **[new_implement/](file:///d:/www/ReadRelint/.ai_context/new_implement)**: Pasta de planos e contextos de migração/desenvolvimento.
        *   [00_migration_plan.md](file:///d:/www/ReadRelint/.ai_context/new_implement/00_migration_plan.md)
        *   [prompt_stage0_context.md](file:///d:/www/ReadRelint/.ai_context/new_implement/prompt_stage0_context.md)
        *   [prompt_stage1_backend.md](file:///d:/www/ReadRelint/.ai_context/new_implement/prompt_stage1_backend.md)
        *   [prompt_stage2_ollama.md](file:///d:/www/ReadRelint/.ai_context/new_implement/prompt_stage2_ollama.md)
        *   [prompt_stage3_frontend.md](file:///d:/www/ReadRelint/.ai_context/new_implement/prompt_stage3_frontend.md)
*   **[data/](file:///d:/www/ReadRelint/data)**: Pasta contendo dados locais (relints.json, processed_registry.json).
    *   [README.md](file:///d:/www/ReadRelint/data/README.md): Documentação dos bancos de dados locais.
*   **[INSTALL.md](file:///d:/www/ReadRelint/INSTALL.md)**: Guia passo a passo de instalação e configuração do ambiente em outras máquinas.
*   **[pyrightconfig.json](file:///d:/www/ReadRelint/pyrightconfig.json)**: Configurações de análise estática de tipos do Pyright.
*   **[requirements.txt](file:///d:/www/ReadRelint/requirements.txt)**: Lista de dependências Python do projeto.

### Pasta de Código Fonte (`/src`)
O desenvolvimento segue o padrão de **Arquitetura Limpa (Ports & Adapters)**:
*   [README.md](file:///d:/www/ReadRelint/src/README.md): Visão geral da arquitetura limpa e divisões das camadas.
*   **[src/domain/](file:///d:/www/ReadRelint/src/domain)**: Contém o coração (regras de negócio e entidades) do sistema.
    *   [README.md](file:///d:/www/ReadRelint/src/domain/README.md): Documentação da camada de domínio.
    *   [entities.py](file:///d:/www/ReadRelint/src/domain/entities.py): Define o contrato e validações do boletim de ocorrência estruturado (`IncidentReport`).
    *   **[src/domain/rules/](file:///d:/www/ReadRelint/src/domain/rules)**: Definições de regras de filtragem e extração específicas por tipo de fato.
        *   [README.md](file:///d:/www/ReadRelint/src/domain/rules/README.md): Documentação das regras de filtragem.
        *   [base_rule.py](file:///d:/www/ReadRelint/src/domain/rules/base_rule.py): Classe abstrata base `IncidentRule`.
        *   [homicide_rule.py](file:///d:/www/ReadRelint/src/domain/rules/homicide_rule.py): Regra concreta `HomicideRule` para homicídios.
        *   [relint_rule.py](file:///d:/www/ReadRelint/src/domain/rules/relint_rule.py): Regra genérica `RelintRule` para processamento total sem descarte.
*   **[src/ports/](file:///d:/www/ReadRelint/src/ports)**: Interfaces abstratas (contratos) das dependências externas.
    *   [README.md](file:///d:/www/ReadRelint/src/ports/README.md): Documentação das portas abstratas.
    *   [file_parser.py](file:///d:/www/ReadRelint/src/ports/file_parser.py): Interface `IFileParser`.
    *   [llm_processor.py](file:///d:/www/ReadRelint/src/ports/llm_processor.py): Interface `ILlmProcessor`.
    *   [database_repo.py](file:///d:/www/ReadRelint/src/ports/database_repo.py): Interface `IDatabaseRepo`.
    *   [person_repo.py](file:///d:/www/ReadRelint/src/ports/person_repo.py): Interface `IPersonRepo`.
    *   [municipality_repo.py](file:///d:/www/ReadRelint/src/ports/municipality_repo.py): Interface `IMunicipalityRepo`.
    *   [processed_registry.py](file:///d:/www/ReadRelint/src/ports/processed_registry.py): Interface `IProcessedRegistry`.
*   **[src/adapters/](file:///d:/www/ReadRelint/src/adapters)**: Implementações concretas das portas da aplicação.
    *   [README.md](file:///d:/www/ReadRelint/src/adapters/README.md): Documentação das implementações.
    *   [pdf_reader.py](file:///d:/www/ReadRelint/src/adapters/pdf_reader.py): Leitor de PDFs usando `PyMuPDF`.
    *   [tinydb_repo.py](file:///d:/www/ReadRelint/src/adapters/tinydb_repo.py): Banco principal de relints baseado em TinyDB.
    *   [tinydb_person_repo.py](file:///d:/www/ReadRelint/src/adapters/tinydb_person_repo.py): Banco secundário de participantes baseado em TinyDB.
    *   [tinydb_municipality_repo.py](file:///d:/www/ReadRelint/src/adapters/tinydb_municipality_repo.py): Banco secundário de municípios baseado em TinyDB.
    *   [ollama_client.py](file:///d:/www/ReadRelint/src/adapters/ollama_client.py): Processador NLP conectado à API do Ollama local.
    *   [json_processed_registry.py](file:///d:/www/ReadRelint/src/adapters/json_processed_registry.py): Registro concreto em JSON do histórico de processamento.
*   **[src/application/](file:///d:/www/ReadRelint/src/application)**: Camada que orquestra as regras de negócio.
    *   [README.md](file:///d:/www/ReadRelint/src/application/README.md): Documentação dos serviços ETL.
    *   [etl_service.py](file:///d:/www/ReadRelint/src/application/etl_service.py): Coordenador do pipeline de ETL.
    *   [text_cleaner.py](file:///d:/www/ReadRelint/src/application/text_cleaner.py): Módulo com funções de limpeza do texto bruto dos RELINTs.
*   **[src/infrastructure/](file:///d:/www/ReadRelint/src/infrastructure)**: Serviços de infraestrutura global.
    *   [README.md](file:///d:/www/ReadRelint/src/infrastructure/README.md): Documentação dos serviços de infraestrutura.
    *   [folder_watcher.py](file:///d:/www/ReadRelint/src/infrastructure/folder_watcher.py): Monitorador de arquivos usando `watchdog`.
    *   **[src/infrastructure/utils/](file:///d:/www/ReadRelint/src/infrastructure/utils)**: Módulos utilitários de infraestrutura.
        *   [module_loader.py](file:///d:/www/ReadRelint/src/infrastructure/utils/module_loader.py): Carregador dinâmico de regras e módulos.
*   **[src/presentation/](file:///d:/www/ReadRelint/src/presentation)**: Responsável pelas interfaces de usuário.
    *   [README.md](file:///d:/www/ReadRelint/src/presentation/README.md): Documentação geral de UI.
    *   **[src/presentation/desktop/](file:///d:/www/ReadRelint/src/presentation/desktop)**: Interface desktop local em CustomTkinter.
        *   [README.md](file:///d:/www/ReadRelint/src/presentation/desktop/README.md): Documentação da app desktop.
        *   [desktop_app.py](file:///d:/www/ReadRelint/src/presentation/desktop/desktop_app.py): Entrypoint da aplicação desktop CustomTkinter.
        *   **[components/](file:///d:/www/ReadRelint/src/presentation/desktop/components)**: Componentes e abas visuais do painel desktop.
            *   [control_panel_tab.py](file:///d:/www/ReadRelint/src/presentation/desktop/components/control_panel_tab.py): Aba de configurações e monitoramento de pastas.
            *   [report_tab.py](file:///d:/www/ReadRelint/src/presentation/desktop/components/report_tab.py): Aba de visualização de logs, relatórios e fila de processamento.
        *   **[controllers/](file:///d:/www/ReadRelint/src/presentation/desktop/controllers)**: Controladores para a interface desktop.
            *   [main_controller.py](file:///d:/www/ReadRelint/src/presentation/desktop/controllers/main_controller.py): Controlador principal responsável pelo fluxo ETL e orquestração de threads.
            *   [dashboard_manager.py](file:///d:/www/ReadRelint/src/presentation/desktop/controllers/dashboard_manager.py): Gerenciador de inicialização do processo Streamlit.
        *   **[views/](file:///d:/www/ReadRelint/src/presentation/desktop/views)**: Janelas e visualizações principais.
            *   [main_window.py](file:///d:/www/ReadRelint/src/presentation/desktop/views/main_window.py): Definição da janela principal da aplicação CustomTkinter.
    *   **[src/presentation/web_dashboard/](file:///d:/www/ReadRelint/src/presentation/web_dashboard)**: Interface web de relatórios e busca local.
        *   [README.md](file:///d:/www/ReadRelint/src/presentation/web_dashboard/README.md): Documentação do Dashboard Web em Streamlit.
        *   [dashboard_app.py](file:///d:/www/ReadRelint/src/presentation/web_dashboard/dashboard_app.py): Dashboard interativo Streamlit em modo Split Screen (Master-Detail).
        *   [helpers.py](file:///d:/www/ReadRelint/src/presentation/web_dashboard/helpers.py): Funções auxiliares para formatação e manipulação de dados na interface web.
        *   [styles.py](file:///d:/www/ReadRelint/src/presentation/web_dashboard/styles.py): Estilos CSS customizados embutidos e paleta de cores.

### Pasta de Testes (`/tests`)
Contém todos os testes automatizados estruturados usando Pytest:
*   [README.md](file:///d:/www/ReadRelint/tests/README.md): Guia e documentação da suíte de testes.
*   [test_entities.py](file:///d:/www/ReadRelint/tests/test_entities.py): Validação em tempo de execução dos esquemas Pydantic.
*   [test_folder_watcher.py](file:///d:/www/ReadRelint/tests/test_folder_watcher.py): Testes de monitoramento de pastas.
*   [test_ollama_client.py](file:///d:/www/ReadRelint/tests/test_ollama_client.py): Testes unitários do OllamaClient.
*   [test_pdf_reader.py](file:///d:/www/ReadRelint/tests/test_pdf_reader.py): Testes unitários do PdfReader mockando fitz (PyMuPDF).
*   [test_rules.py](file:///d:/www/ReadRelint/tests/test_rules.py): Testes unitários das regras de filtragem e processamento.
*   [test_text_cleaner.py](file:///d:/www/ReadRelint/tests/test_text_cleaner.py): Testes de limpeza de texto dos RELINTs.
*   [test_tinydb_repo.py](file:///d:/www/ReadRelint/tests/test_tinydb_repo.py): Testes do TinyDbRepo.

### Scripts Utilitários e Scratch (`/scratch`)
*   [README.md](file:///d:/www/ReadRelint/scratch/README.md): Descrição das ferramentas utilitárias.
*   [check_entities.py](file:///d:/www/ReadRelint/scratch/check_entities.py): Script de verificação rápida e validação de entidades.
*   [kill_streamlit.py](file:///d:/www/ReadRelint/scratch/kill_streamlit.py): Utilitário para forçar o encerramento do processo do Streamlit em segundo plano.
