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
*   **[src/ports/](file:///d:/DEV26/ReadRelint/src/ports)**: Define as interfaces abstratas (contratos) das dependências externas do domínio.
    *   [file_parser.py](file:///d:/DEV26/ReadRelint/src/ports/file_parser.py): Interface `IFileParser` para extração de texto a partir de arquivos.
    *   [llm_processor.py](file:///d:/DEV26/ReadRelint/src/ports/llm_processor.py): Interface `ILlmProcessor` para processar e estruturar o texto bruto com IA.
    *   [database_repo.py](file:///d:/DEV26/ReadRelint/src/ports/database_repo.py): Interface `IDatabaseRepo` para persistência e consulta das entidades de incidentes estruturadas.
*   **[src/adapters/](file:///d:/DEV26/ReadRelint/src/adapters)**: Implementações concretas das portas da aplicação.
    *   [pdf_reader.py](file:///d:/DEV26/ReadRelint/src/adapters/pdf_reader.py): Leitor e extrator de PDFs usando a biblioteca `PyMuPDF`.
    *   [tinydb_repo.py](file:///d:/DEV26/ReadRelint/src/adapters/tinydb_repo.py): Banco embutido baseado em TinyDB com gravação serverless em arquivo JSON.
    *   [ollama_client.py](file:///d:/DEV26/ReadRelint/src/adapters/ollama_client.py): Processador de NLP e estruturação de IA local conectado à API do Ollama.
*   **[src/presentation/](file:///d:/DEV26/ReadRelint/src/presentation)**: Responsável pelas interfaces de usuário.
    *   **[src/presentation/desktop/](file:///d:/DEV26/ReadRelint/src/presentation/desktop)**: Telas locais em CustomTkinter.
        *   [app.py](file:///d:/DEV26/ReadRelint/src/presentation/desktop/app.py): Interface desktop para que o usuário final selecione diretórios a serem monitorados e acompanhe o processamento de PDFs.

### Pasta de Testes (`/tests`)
Contém todos os testes automatizados da aplicação estruturados usando o Pytest:
*   [test_entities.py](file:///d:/DEV26/ReadRelint/tests/test_entities.py): Validação em tempo de execução dos esquemas Pydantic.
*   [test_pdf_reader.py](file:///d:/DEV26/ReadRelint/tests/test_pdf_reader.py): Testes unitários da classe `PdfReader` mockando o `fitz` (PyMuPDF).
*   [test_tinydb_repo.py](file:///d:/DEV26/ReadRelint/tests/test_tinydb_repo.py): Testes de gravação e consulta do `TinyDbRepo` usando a fixture `tmp_path`.
*   [test_ollama_client.py](file:///d:/DEV26/ReadRelint/tests/test_ollama_client.py): Testes da API HTTP do Ollama mockando o módulo `requests`.

### Scripts Utilitários (Raiz)
*   [read_pdf_test.py](file:///d:/DEV26/ReadRelint/read_pdf_test.py): Script de testes manuais para validação de extração de texto de PDFs reais locais.
*   [run_pipeline_test.py](file:///d:/DEV26/ReadRelint/run_pipeline_test.py): Script de testes manuais de integração de fluxo completo (Leitura PDF -> IA Ollama -> TinyDB).
