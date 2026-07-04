# Estado Atual do Projeto

## O que já foi implementado:
- [x] Definição completa do escopo, regras de negócio e limites de domínio.
- [x] Tech Stack definida (Python, TinyDB, Ollama, PyMuPDF, CustomTkinter, Streamlit).
- [x] Consolidação do repositório de contexto da IA.
- [x] Arquivo `requirements.txt` criado e atualizado com as dependências do projeto (incluindo `watchdog`).
- [x] Criação da camada de domínio com a entidade `IncidentReport` em `src/domain/entities.py`.
- [x] Implementação do esqueleto visual com CustomTkinter para o painel desktop em `src/presentation/desktop/app.py`.
- [x] Criação do ambiente virtual Python `.venv` e atualização do `pip`.
- [x] Criação das portas (interfaces) do sistema (`IFileParser`, `ILlmProcessor`, `IDatabaseRepo`) em `src/ports/`.
- [x] Configuração do framework `pytest` e implementação de testes unitários para os modelos de domínio em `tests/test_entities.py`.
- [x] Desenvolver a implementação concreta do leitor de PDF usando `PyMuPDF` em `src/adapters/pdf_reader.py`.
- [x] Desenvolver a implementação do repositório `TinyDB` em `src/adapters/tinydb_repo.py`.
- [x] Implementar o cliente local para chamadas ao `Ollama` em `src/adapters/ollama_client.py`.
- [x] Desenvolver a infraestrutura de monitoramento de diretórios em `src/infrastructure/folder_watcher.py`.
- [x] Integrar o `FolderWatcher` e o Pipeline de ETL (PdfReader, OllamaClient, TinyDbRepo) no painel desktop `src/presentation/desktop/app.py` com console de log.
- [x] Implementar fila de processamento (`queue.Queue`) e contadores estatísticos em tempo real (Lendo, Lidos, Fila) no painel desktop.

## O que está sendo feito agora:
- [ ] Desenvolvimento do Dashboard Web de relatórios usando Streamlit.

## Próximos Passos Pendentes:
- [ ] Desenvolver a interface web de relatórios (UI) com Streamlit em `src/presentation/web_dashboard/app.py` para visualizar e buscar boletins cadastrados na base TinyDB.
