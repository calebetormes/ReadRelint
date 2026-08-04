# Estrutura do Projeto e Estado Atual

Este arquivo documenta a organização física de pastas e arquivos no repositório, bem como o resumo do progresso do desenvolvimento.

## 1. Estrutura de Diretórios e Arquivos

### Raiz do Projeto
*   **[README.md](file:///d:/www/ReadRelint/README.md)**: Visão geral e guia rápido do projeto.
*   **[structure_viewer.html](file:///d:/www/ReadRelint/structure_viewer.html)**: Visualizador gráfico interativo e dinâmico da estrutura do repositório em tempo real.
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
*   **[data/](file:///d:/www/ReadRelint/data)**: Pasta contendo dados locais (relints.json, processed_registry.json).
    *   [README.md](file:///d:/www/ReadRelint/data/README.md): Documentação dos bancos de dados locais.
*   **[INSTALL.md](file:///d:/www/ReadRelint/INSTALL.md)**: Guia passo a passo de instalação e configuração do ambiente em outras máquinas.
*   **[pyrightconfig.json](file:///d:/www/ReadRelint/pyrightconfig.json)**: Configurações de análise estática de tipos do Pyright para garantir a integridade do código Python.
*   **[requirements.txt](file:///d:/www/ReadRelint/requirements.txt)**: Lista de bibliotecas externas utilizadas no projeto (como `customtkinter`, `pymupdf`, `watchdog`, etc.).

### Pasta de Código Fonte (`/src`)
O desenvolvimento segue o padrão de **Arquitetura Limpa (Ports & Adapters)**:
*   [README.md](file:///d:/www/ReadRelint/src/README.md): Visão geral da arquitetura limpa e divisões das camadas.
*   **[src/domain/](file:///d:/www/ReadRelint/src/domain)**: Contém o coração (regras de negócio e entidades) do sistema. É escrito em Python puro e não possui dependências de framework ou bibliotecas externas de infraestrutura.
    *   [README.md](file:///d:/www/ReadRelint/src/domain/README.md): Documentação da camada de domínio.
    *   [entities.py](file:///d:/www/ReadRelint/src/domain/entities.py): Define o contrato e validações do boletim de ocorrência estruturado (`IncidentReport`).
    *   **[src/domain/rules/](file:///d:/www/ReadRelint/src/domain/rules)**: Diretório contendo as definições de regras de filtragem e extração específicas por tipo de fato.
        *   [README.md](file:///d:/www/ReadRelint/src/domain/rules/README.md): Documentação das regras de filtragem.
        *   [base_rule.py](file:///d:/www/ReadRelint/src/domain/rules/base_rule.py): Classe abstrata base `IncidentRule`.
        *   [homicide_rule.py](file:///d:/www/ReadRelint/src/domain/rules/homicide_rule.py): Regra concreta `HomicideRule` especializada em ocorrências de homicídio.
        *   [relint_rule.py](file:///d:/www/ReadRelint/src/domain/rules/relint_rule.py): Regra genérica `RelintRule` para processar todos os RELINTs sem descarte.
*   **[src/ports/](file:///d:/www/ReadRelint/src/ports)**: Define as interfaces abstratas (contratos) das dependências externas do domínio.
    *   [README.md](file:///d:/www/ReadRelint/src/ports/README.md): Documentação das portas abstratas.
    *   [file_parser.py](file:///d:/www/ReadRelint/src/ports/file_parser.py): Interface `IFileParser` para extração de texto a partir de arquivos.
    *   [llm_processor.py](file:///d:/www/ReadRelint/src/ports/llm_processor.py): Interface `ILlmProcessor` para processar e estruturar o texto bruto com IA.
    *   [database_repo.py](file:///d:/www/ReadRelint/src/ports/database_repo.py): Interface `IDatabaseRepo` para persistência e consulta das entidades de incidentes estruturadas.
    *   [processed_registry.py](file:///d:/www/ReadRelint/src/ports/processed_registry.py): Interface `IProcessedRegistry` para controle de histórico de processamento de PDFs por regra.
*   **[src/adapters/](file:///d:/www/ReadRelint/src/adapters)**: Implementações concretas das portas da aplicação.
    *   [README.md](file:///d:/www/ReadRelint/src/adapters/README.md): Documentação das implementações concretas dos adaptadores.
    *   [pdf_reader.py](file:///d:/www/ReadRelint/src/adapters/pdf_reader.py): Leitor e extrator de PDFs usando a biblioteca `PyMuPDF`.
    *   [tinydb_repo.py](file:///d:/www/ReadRelint/src/adapters/tinydb_repo.py): Banco embutido baseado em TinyDB com gravação serverless em arquivo JSON.
    *   [ollama_client.py](file:///d:/www/ReadRelint/src/adapters/ollama_client.py): Processador de NLP e estruturação de IA local conectado à API do Ollama com auto-recuperação de modelo.
    *   [local_regex_processor.py](file:///d:/www/ReadRelint/src/adapters/local_regex_processor.py): Processador local baseado em regras Regex (fallback/desativado).
    *   [json_processed_registry.py](file:///d:/www/ReadRelint/src/adapters/json_processed_registry.py): Registro concreto em formato JSON contendo o histórico de análises de arquivos por regra.
*   **[src/application/](file:///d:/www/ReadRelint/src/application)**: Camada de aplicação que orquestra as regras de negócio e serviços.
    *   [README.md](file:///d:/www/ReadRelint/src/application/README.md): Documentação dos serviços de aplicação ETL.
    *   [etl_service.py](file:///d:/www/ReadRelint/src/application/etl_service.py): Serviço que coordena o pipeline de ETL (Extração, Limpeza, Processamento LLM e Persistência).
    *   [text_cleaner.py](file:///d:/www/ReadRelint/src/application/text_cleaner.py): Módulo com funções de limpeza do texto bruto dos RELINTs via regex.
*   **[src/infrastructure/](file:///d:/www/ReadRelint/src/infrastructure)**: Serviços de infraestrutura global do sistema.
    *   [README.md](file:///d:/www/ReadRelint/src/infrastructure/README.md): Documentação dos serviços de infraestrutura de SO.
    *   [folder_watcher.py](file:///d:/www/ReadRelint/src/infrastructure/folder_watcher.py): Monitorador de diretórios usando a biblioteca `watchdog` para detectar novos arquivos PDF adicionados.
*   **[src/presentation/](file:///d:/www/ReadRelint/src/presentation)**: Responsável pelas interfaces de usuário.
    *   [README.md](file:///d:/www/ReadRelint/src/presentation/README.md): Documentação geral das interfaces de usuário.
    *   **[src/presentation/desktop/](file:///d:/www/ReadRelint/src/presentation/desktop)**: Interface desktop local em CustomTkinter.
        *   [README.md](file:///d:/www/ReadRelint/src/presentation/desktop/README.md): Documentação da app desktop.
        *   [desktop_app.py](file:///d:/www/ReadRelint/src/presentation/desktop/desktop_app.py): Painel de controle desktop para selecionar diretórios, monitorar a fila e logs em tempo real.
    *   **[src/presentation/web_dashboard/](file:///d:/www/ReadRelint/src/presentation/web_dashboard)**: Interface web de relatórios e busca local.
        *   [README.md](file:///d:/www/ReadRelint/src/presentation/web_dashboard/README.md): Documentação do Dashboard Web em Streamlit.
        *   [dashboard_app.py](file:///d:/www/ReadRelint/src/presentation/web_dashboard/dashboard_app.py): Dashboard interativo em Streamlit com tela dividida (Master-Detail), busca, filtragem e curadoria de RELINTs.

### Pasta de Testes (`/tests`)
Contém todos os testes automatizados da aplicação estruturados usando o Pytest:
*   [README.md](file:///d:/www/ReadRelint/tests/README.md): Guia e documentação da suíte de testes.
*   [test_entities.py](file:///d:/www/ReadRelint/tests/test_entities.py): Validação em tempo de execução dos esquemas Pydantic.
*   [test_pdf_reader.py](file:///d:/www/ReadRelint/tests/test_pdf_reader.py): Testes unitários da classe `PdfReader` mockando o `fitz` (PyMuPDF).
*   [test_tinydb_repo.py](file:///d:/www/ReadRelint/tests/test_tinydb_repo.py): Testes de gravação e consulta do `TinyDbRepo` usando a fixture `tmp_path`.
*   [test_ollama_client.py](file:///d:/www/ReadRelint/tests/test_ollama_client.py): Testes unitários do adaptador OllamaClient mockando requests.
*   [test_text_cleaner.py](file:///d:/www/ReadRelint/tests/test_text_cleaner.py): Testes das regras de limpeza de cabeçalhos e termos de corte do texto bruto dos RELINTs.
*   [test_folder_watcher.py](file:///d:/www/ReadRelint/tests/test_folder_watcher.py): Testes de monitoramento de pastas e detecção de arquivos.
*   [test_rules.py](file:///d:/www/ReadRelint/tests/test_rules.py): Testes unitários das regras de filtragem rápida e orquestração do EtlService.
*   [test_local_regex_processor.py](file:///d:/www/ReadRelint/tests/test_local_regex_processor.py): Testes das regras locais do fallback.

### Scripts Utilitários e Scratch (`/scratch`)
*   [README.md](file:///d:/www/ReadRelint/scratch/README.md): Descrição das ferramentas utilitárias.
*   [read_pdf_test.py](file:///d:/www/ReadRelint/read_pdf_test.py): Script de testes manuais para validação de extração de texto de PDFs reais locais.
*   [run_pipeline_test.py](file:///d:/www/ReadRelint/run_pipeline_test.py): Script de testes manuais de integração de fluxo completo (Leitura PDF -> IA Ollama -> TinyDB).
