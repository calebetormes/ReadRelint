# Histórico de Conversas (TalkIA Rec)

Este arquivo registra o resumo das interações, decisões e progresso discutidos no chat.

## Registro de Conversas

### [2026-07-04] Inicialização do Contexto e Estruturação

- **Assuntos Discutidos**:
  - Organização dos arquivos de contexto da IA (`.ai_context/`).
  - Criação do arquivo de histórico de conversas (`06_talkia_rec.md`) para centralizar os resumos.
  - Resumo do estado atual do projeto e descrição de cada pasta/arquivo do workspace.
  - Alinhamento sobre o próximo passo do projeto (definir as portas de arquitetura).
- **Decisões Tomadas**:
  - Criação deste documento para registrar a evolução do projeto e o alinhamento no chat.
  - Criação do arquivo de mapeamento da estrutura [07_structure.md](file:///d:/DEV26/ReadRelint/.ai_context/07_structure.md).
  - Criação de três interfaces abstratas (Ports): [file_parser.py](file:///d:/DEV26/ReadRelint/src/ports/file_parser.py), [llm_processor.py](file:///d:/DEV26/ReadRelint/src/ports/llm_processor.py) e [database_repo.py](file:///d:/DEV26/ReadRelint/src/ports/database_repo.py).
- **Status/Próximos Passos**:
  - Iniciar a implementação concreta dos adaptadores (`adapters`), especificamente o leitor de PDF usando `PyMuPDF` em `src/adapters/pdf_reader.py`.

### [2026-07-04] Configuração de Testes Automatizados com Pytest

- **Assuntos Discutidos**:
  - Como testar o que foi desenvolvido (interface e domínio).
  - Decisão de adotar o framework de testes `pytest`.
- **Decisões Tomadas**:
  - Adição do `pytest` no `requirements.txt` e instalação no ambiente virtual.
  - Implementação de testes de domínio em [test_entities.py](file:///d:/DEV26/ReadRelint/tests/test_entities.py) para validar a correta estrutura e restrições dos modelos Pydantic (`Address`, `Participant`, `Vehicle`, `IncidentReport`).
  - Execução validada dos testes via módulo de teste do python (`python -m pytest`).
- **Status/Próximos Passos**:
  - Prosseguir com a criação dos adaptadores (leitura de PDF, banco de dados TinyDB, conexão Ollama).

### [2026-07-04] Implementação do Leitor de PDF (PyMuPDF)

- **Assuntos Discutidos**:
  - Desenvolvimento do adaptador concreto de leitura e extração de texto de arquivos PDF.
- **Decisões Tomadas**:
  - Implementação de [pdf_reader.py](file:///d:/DEV26/ReadRelint/src/adapters/pdf_reader.py) utilizando `PyMuPDF` (`fitz`), que herda do port `IFileParser`.
  - Tratamento de exceções robusto (levantando `FileNotFoundError` para arquivos ausentes e `ValueError` para PDFs corrompidos/inválidos).
  - Escrita de testes unitários mockando o `fitz` e o sistema de arquivos no arquivo [test_pdf_reader.py](file:///d:/DEV26/ReadRelint/tests/test_pdf_reader.py).
  - Execução e validação de 100% de sucesso da suíte de testes (agora com 7 testes no total).
- **Status/Próximos Passos**:
  - Prosseguir com o desenvolvimento do repositório TinyDB (`src/adapters/tinydb_repo.py`) ou o processador LLM do Ollama (`src/adapters/ollama_client.py`).

### [2026-07-04] Implementação do Repositório TinyDB

- **Assuntos Discutidos**:
  - Desenvolvimento do repositório local de persistência para armazenar os relatórios estruturados obtidos.
- **Decisões Tomadas**:
  - Implementação de [tinydb_repo.py](file:///d:/DEV26/ReadRelint/src/adapters/tinydb_repo.py) utilizando `TinyDB` para armazenamento NoSQL leve e embutido baseado em um arquivo JSON.
  - O repositório herda do port `IDatabaseRepo`, convertendo os objetos Pydantic da camada de domínio para dicionários ao salvar, e fazendo o caminho inverso na recuperação.
  - Criação de testes unitários em [test_tinydb_repo.py](file:///d:/DEV26/ReadRelint/tests/test_tinydb_repo.py) utilizando a fixture `tmp_path` do pytest para criar instâncias isoladas e temporárias do banco.
  - Execução e validação com sucesso dos novos testes (total de 10 testes passando).
- **Status/Próximos Passos**:
  - Prosseguir com a integração do cliente local Ollama para processar textos por IA (`src/adapters/ollama_client.py`).

### [2026-07-04] Implementação do Cliente Ollama Local

- **Assuntos Discutidos**:
  - Integração do sistema de inteligência artificial usando uma LLM local via Ollama.
- **Decisões Tomadas**:
  - Implementação de [ollama_client.py](file:///d:/DEV26/ReadRelint/src/adapters/ollama_client.py) que implementa a interface `ILlmProcessor`.
  - Configuração do prompt do sistema com especificações claras de tipagem e formato, fazendo chamadas HTTP para o endpoint `/api/generate` com a opção `"format": "json"`.
  - Tratamento de exceções cobrindo falhas de conexão/HTTP e respostas malformatadas em JSON.
  - Escrita de testes unitários em [test_ollama_client.py](file:///d:/DEV26/ReadRelint/tests/test_ollama_client.py) usando `unittest.mock` para simular as respostas da API.
  - Execução e validação com sucesso dos novos testes (total de 14 testes passando).
- **Status/Próximos Passos**:
  - Implementar o watcher de pastas (`src/infrastructure/folder_watcher.py`) para monitorar o surgimento de novos PDFs.

### [2026-07-04] Atualização de Modelo Ollama (Llama 3.1) e Atalho do Windows

- **Assuntos Discutidos**:
  - Ajuste de modelo de IA local de `llama3` para `llama3.1` (modelo baixado pelo usuário).
  - Execução fácil do aplicativo desktop pelo Windows Explorer sem terminal ativo.
  - Criação de scripts para verificação da extração de PDFs reais e integração completa.
- **Decisões Tomadas**:
  - Alteração do modelo default no `OllamaClient` para `"llama3.1"`.
  - Criação de [Iniciar-Painel.bat](file:///d:/DEV26/ReadRelint/Iniciar-Painel.bat) para execução silenciosa do painel usando `pythonw.exe`.
  - Criação de scripts [read_pdf_test.py](file:///d:/DEV26/ReadRelint/read_pdf_test.py) e [run_pipeline_test.py](file:///d:/DEV26/ReadRelint/run_pipeline_test.py) para que o usuário execute e valide o funcionamento da leitura de PDFs e integração local com o Ollama `llama3.1` e gravação no TinyDB.
- **Status/Próximos Passos**:
  - Validar a execução local do pipeline.
  - Prosseguir com a criação do watcher de diretórios (`src/infrastructure/folder_watcher.py`).

### [2026-07-04] Implementação do Monitor de Pastas (Folder Watcher)

- **Assuntos Discutidos**:
  - Monitoramento de arquivos no diretório em tempo real para automação do ETL.
- **Decisões Tomadas**:
  - Implementação de [folder_watcher.py](file:///d:/DEV26/ReadRelint/src/infrastructure/folder_watcher.py) utilizando a biblioteca `watchdog`.
  - Tratamento de criação e movimentação de arquivos com um pequeno delay (`time.sleep`) para evitar concorrência com o sistema operacional enquanto o arquivo PDF está sendo gravado.
  - Escrita de testes unitários em [test_folder_watcher.py](file:///d:/DEV26/ReadRelint/tests/test_folder_watcher.py) simulando os callbacks de criação e movimentação de PDFs e descartando outros formatos de arquivos (.txt, etc.).
  - Execução e validação da suíte completa de testes no terminal (total de 19 testes passando com 100% de sucesso).
- **Status/Próximos Passos**:
  - Integrar o monitor de diretórios e o pipeline com o painel visual CustomTkinter em `src/presentation/desktop/app.py`.
  - Criar o dashboard Streamlit local para leitura dos dados cadastrados no TinyDB.

### [2026-07-04] Integração do ETL Pipeline na Interface Desktop

- **Assuntos Discutidos**:
  - Conectar os componentes de monitoramento e de processamento de dados (PDF, IA e TinyDB) à UI gráfica.
- **Decisões Tomadas**:
  - Atualização do painel [app.py](file:///d:/DEV26/ReadRelint/src/presentation/desktop/app.py).
  - Injeção das dependências concretas (`PdfReader`, `OllamaClient` utilizando o modelo `llama3.1`, e `TinyDbRepo`).
  - Criação de um console de log com `ctk.CTkTextbox` para exibição das etapas de processamento em tempo real.
  - Implementação de um manipulador de eventos thread-safe (`self.after(0, ...)`) para atualizar a tela sem travar a interface ao receber chamadas da thread em segundo plano do monitor de diretórios.
  - Execução e sucesso de todos os 19 testes automatizados do projeto.
- **Status/Próximos Passos**:
  - Validar a execução da interface copiando arquivos PDF e acompanhando os logs visuais.
  - Iniciar o desenvolvimento da interface web do dashboard em Streamlit (`src/presentation/web_dashboard/app.py`).

### [2026-07-04] Implementação de Contadores e Fila na Interface Desktop

- **Assuntos Discutidos**:
  - Adição de indicadores em tempo real para controle do fluxo de processamento de arquivos.
- **Decisões Tomadas**:
  - Implementação de um sistema de fila (`queue.Queue`) na interface desktop [app.py](file:///d:/DEV26/ReadRelint/src/presentation/desktop/app.py).
  - Criação de uma thread dedicada (worker) em segundo plano para ler e processar os arquivos da fila sequencialmente.
  - Varredura de arquivos PDF pré-existentes na pasta ao iniciar o monitoramento, inserindo-os diretamente na fila.
  - Adição de novos elementos gráficos na GUI: indicador do "Arquivo atual" que está sendo processado, contador de PDFs "Lidos" e contador de arquivos "Fila/Pendentes".
  - Execução e aprovação de todos os 19 testes automatizados do projeto.
- **Status/Próximos Passos**:
  - Prosseguir com a criação do Dashboard Web Streamlit (`src/presentation/web_dashboard/app.py`).

### [2026-07-05] Implementação do Dashboard Streamlit

- **Assuntos Discutidos**:
  - Estrutura e design do painel web de relatórios usando Streamlit.
  - Criação de mecanismos de busca livre e filtros por tipo de crime, cidades e datas.
  - Adição de gráficos analíticos de distribuição de incidentes.
- **Decisões Tomadas**:
  - Criação do arquivo [dashboard_app.py](file:///d:/DEV26/ReadRelint/src/presentation/web_dashboard/dashboard_app.py) para o dashboard.
  - Carregamento de dados cacheado com `@st.cache_data` e integração direta com o adaptador `TinyDbRepo`.
  - Exibição dos boletins de ocorrência em formato de sanfona expansível (`st.expander`) para fácil visualização das informações estruturadas.
  - Teste e validação local do dashboard subindo na porta `8501`.
- **Status/Próximos Passos**:
  - Permitir a exportação dos dados filtrados para formatos como CSV ou Excel.
  - Refinar visualizações temporais.

### [2026-07-05] Reestruturação para RELINTs e Classificação do Código Penal (CPB)

- **Assuntos Discutidos**:
  - Nova modelagem de dados para processar PDFs como RELINTs contendo múltiplos incidentes/ocorrências.
  - Classificação e estruturação de crimes conforme a estrutura de capítulos do Código Penal Brasileiro.
  - Atualizações necessárias nos adaptadores de IA, de banco e nas interfaces (desktop/dashboard).
- **Decisões Tomadas**:
  - Alteração do domínio: Criação de `RelintReport` e inserção de `crime_category` em `IncidentReport`.
  - Atualização dos ports `ILlmProcessor` e `IDatabaseRepo`.
  - Reestruturação do prompt no `OllamaClient` com instruções exaustivas para categorizar as ocorrências em 7 capítulos principais do CPB.
  - Ajuste do `TinyDbRepo` e do logger no painel desktop `desktop_app.py`.
  - Redesenho do dashboard Streamlit para achatar os dados e permitir filtragem rica por categoria do CPB, tipo de crime e dados gerais do RELINT.
  - Atualização completa de todos os testes automatizados (21/21 com 100% de sucesso).
- **Status/Próximos Passos**:
  - Testar com PDFs reais de RELINT e refinar prompt da IA.
  - Adicionar suporte a exportações CSV/Excel no dashboard.

### [2026-07-05] Reversão para Modelo de Ocorrência Simples (IncidentReport)

- **Assuntos Discutidos**:
  - Solicitação do usuário para desfazer a reestruturação hierárquica complexa de RELINTs e classificação de crimes CPB.
  - Focar no modelo simples de ocorrência individual com o nome do documento, data e dados originais extraídos.
- **Decisões Tomadas**:
  - Reversão completa do domínio: Remoção de `RelintReport` e restauração de `IncidentReport` em `src/domain/entities.py`.
  - Reversão das portas (`ILlmProcessor` e `IDatabaseRepo`) e adaptadores (`OllamaClient` e `TinyDbRepo`) para utilizarem a assinatura anterior baseada em `IncidentReport`.
  - Restauração do dashboard Streamlit e do console desktop para a estrutura plana simples original.
  - Ajuste e validação de todos os testes unitários da suíte (20/20 passando com sucesso).
- **Status/Próximos Passos**:
  - Refinar e validar o dashboard com dados simples extraídos.

### [2026-07-05] Classificação e Agrupamento de Ocorrências (AVANTE)

- **Assuntos Discutidos**:
  - Resolução de alucinações na classificação de crimes (ex: "Uso de impréu").
  - Mapeamento de ocorrências em grupos de interesse: Ocorrências do AVANTE, Ocorrências Importantes fora do AVANTE e Demais Fatos.
- **Decisões Tomadas**:
  - Adição de `incident_group` na entidade `IncidentReport` em `src/domain/entities.py`.
  - Atualização do prompt de sistema do `OllamaClient` para enquadrar ocorrências em grupos específicos, com lista estrita de tipos para AVANTE e fora do AVANTE, e padronizar outros crimes em "Demais Fatos".
  - Atualização do dashboard Streamlit com filtro dinâmico por grupo de ocorrência e gráfico de distribuição por grupo.
  - Correção e execução com 100% de sucesso da suíte de testes (20/20).
- **Status/Próximos Passos**:
  - Adicionar suporte a exportações no dashboard.

### [2026-07-05] Proposta e Acessibilidade do Pipeline em Fases

- **Assuntos Discutidos**:
  - Proposta de quebra do processo de ETL em 4 fases distintas (Metadados, Limpeza, Enquadramento/Segmentação, Extração de Campos) para evitar alucinações da LLM e simplificar a manutenção.
  - Otimizações como fatiamento de texto programático no Python e limpeza de cabeçalhos/assinaturas via Regex.
- **Decisões Tomadas**:
  - Aprovada a divisão do pipeline em 4 etapas estruturais de extração para futuros desenvolvimentos.
  - Atualização do arquivo `02_architecture.md` e do `04_current_state.md` documentando a definição do pipeline multifásico e seus passos futuros.
- **Status/Próximos Passos**:
  - Implementar o fatiamento e chamadas específicas no OllamaClient de acordo com o design multifásico.

### [2026-07-05] Refatoração Sob Princípios de Clean Code e SOLID

- **Assuntos Discutidos**:
  - Desacoplamento da interface de usuário da lógica de negócios/infraestrutura no pipeline de ETL.
  - Modularização de prompts e constantes nos adaptadores.
- **Decisões Tomadas**:
  - Criação da classe `EtlService` no pacote `src/application` para encapsular a orquestração de leitura, chamada à LLM e persistência de dados.
  - Refatoração de `src/presentation/desktop/desktop_app.py` para utilizar o serviço injetado de forma limpa via callbacks.
  - Extração de prompts extensos no `OllamaClient` para a constante de classe `OLLAMA_SYSTEM_PROMPT`.
  - Atualização com 100% de aprovação da suíte de testes unitários.
- **Status/Próximos Passos**:
  - Iniciar a especificação e desenvolvimento físico do pipeline multifásico no OllamaClient.

### [2026-07-05] Resolução de Conflitos de Nomenclatura (Renomeação de app.py)

- **Assuntos Discutidos**:
  - Conflito e duplicidade na nomenclatura de arquivos principais (dois arquivos `app.py` nas pastas desktop e web_dashboard).
- **Decisões Tomadas**:
  - Renomeado `src/presentation/desktop/app.py` para `desktop_app.py`.
  - Renomeado `src/presentation/web_dashboard/app.py` para `dashboard_app.py`.
  - Atualizadas as referências no atalho `Iniciar-Painel.bat` e arquivos de contexto (`04_current_state.md`).
- **Status/Próximos Passos**:
  - Relaunch do dashboard na nova estrutura.

### [2026-07-05] Implementação do Pré-processamento e Limpeza (Regex)

- **Assuntos Discutidos**:
  - Detalhes da implementação da Fase 2 de limpeza automatizada de textos para remover assinaturas, listas de distribuição e outros rodapés administrativos dos RELINTs.
- **Decisões Tomadas**:
  - Criada a biblioteca utilitária `clean_relint_text` em `src/application/text_cleaner.py` contendo uma regex robusta e tolerante a maiúsculas, minúsculas e acentuações.
  - Integrada a rotina de limpeza no `EtlService` logo após a leitura física do PDF pelo `PdfReader`.
  - Escritos testes unitários em `tests/test_text_cleaner.py` (5 testes aprovados).
  - Execução total da suíte obtendo 100% de sucesso (25/25 testes aprovados).
- **Status/Próximos Passos**:
  - Avançar com a divisão física das fases 1, 3 e 4 no OllamaClient.

### [2026-07-05] Desenvolvimento de Pipeline Multifásico e Logs em Tempo Real

- **Assuntos Discutidos**:
  - Divisão de responsabilidade da extração da IA em Fases: Metadados do Documento (Fase 1), Limpeza/Regex (Fase 2), Segmentação/Enquadramento em grupos (Fase 3), Extração localizada (Fase 4).
  - Cálculo do tempo de execução por documento e melhoria nos logs da UI.
- **Decisões Tomadas**:
  - Atualizada a entidade `IncidentReport` com os campos de metadados administrativos.
  - Implementados prompts e métodos estruturados em `OllamaClient` para as chamadas em fases.
  - Atualizada a lógica no `EtlService.process_file` para orquestrar as fases, monitorar a duração com o módulo `time` e emitir os logs descritivos.
  - Toda a suíte de testes foi adaptada e executada com 100% de sucesso (27/27 testes aprovados).
- **Status/Próximos Passos**:
  - Implementar suporte à exportação de dados filtrados para arquivos CSV/Excel.

### [2026-07-05] Classificação da Natureza do Registro (Ocorrência vs Outros)

- **Assuntos Discutidos**:
  - Distinção entre fatos policiais concretos ocorridos/tentados (Ocorrência) e outros registros de inteligência (Denúncia, Resposta a Pedido de Busca, Informação, Outro).
- **Decisões Tomadas**:
  - Adicionado o campo `incident_nature` no `IncidentReport` (com valor padrão `"Ocorrência"`).
  - Atualizado o prompt de segmentação do `OllamaClient` para mapear a natureza dos registros e ajustada a leitura de forma flexível (objeto ou lista JSON).
  - Atualizados `EtlService` para passar a natureza capturada e `dashboard_app.py` para incluir filtros interativos e exibições customizadas da natureza na interface do Streamlit.
  - Testes do sistema atualizados e com sucesso (28/28 testes aprovados).
- **Status/Próximos Passos**:
  - Implementar exportação de arquivos CSV/Excel e gráficos de linha temporal no Dashboard.

### [2026-07-15] Foco na IA e Regra de Unicidade de Registro
- **Assuntos Discutidos**:
  - Mudança de foco para aprimorar a leitura e estruturação da IA.
  - Alinhamento sobre a regra de que cada documento representa um único registro/fato principal.
- **Decisões Tomadas**:
  - Adição da "Regra de Unicidade do Registro por Documento" nas regras de ouro do blueprint.
  - Atualização do pipeline de processamento de IA em fases no arquivo de arquitetura para focar na extração e classificação de um único fato principal por documento (evitando a geração de múltiplas ocorrências fragmentadas por arquivo).
- **Status/Próximos Passos**:
  - Ajustar o prompt de extração da IA em `OllamaClient` para forçar o retorno de um único registro por documento.
  - Ajustar testes automatizados e o serviço ETL de acordo com essa restrição.
  - Adicionar o botão "Abrir Dashboard" no painel de controle do CustomTkinter.

### [2026-07-15] Reset e Simplificação da Leitura do ETL
- **Assuntos Discutidos**:
  - Reset da extração complexa baseada em quatro fases e regras estritas do Código Penal / AVANTE.
  - Substituição por uma leitura simplificada do PDF via IA, removendo previamente o cabeçalho administrativo confidencial.
  - Redução da persistência para guardar apenas o nome do arquivo (`source_file`) e o conteúdo resumido (`content`).
- **Decisões Tomadas**:
  - Overwrite de `entities.py` com o esquema simplificado contendo apenas `source_file` e `content`.
  - Simplificação da interface `ILlmProcessor` e de sua implementação concreta `OllamaClient` para expor o método `process_text`.
  - Atualização do `EtlService` para rodar o pipeline unificado.
  - Ajuste de toda a suíte de testes unitários e do script `run_pipeline_test.py` para compatibilidade com o novo modelo.
  - Atualização do painel Streamlit (`dashboard_app.py`) para renderizar de forma direta os arquivos e seus conteúdos processados.

### [2026-07-15] Botão de Atalho para o Dashboard no Painel Desktop
- **Assuntos Discutidos**:
  - Integração visual entre a interface de controle desktop (CustomTkinter) e a interface de visualização web (Streamlit).
- **Decisões Tomadas**:
  - Criação de um container de botões de ação (`actions_frame`) contendo o botão de monitoramento e o novo botão "Abrir Dashboard".
  - Implementação do método `open_dashboard` que invoca de forma assíncrona o Streamlit em um processo em segundo plano (usando a mesma instalação de Python da `.venv` de forma thread-safe).

### [2026-07-16] Correção de Erros de Validação e Simplificação Visual do Dashboard
- **Assuntos Discutidos**:
  - Erros de validação (`ValidationError`) no Streamlit decorrentes de dados legados no TinyDB e processos do Streamlit travados em cache/background.
  - Implementação de um controle robusto de ciclo de vida do processo Streamlit na aplicação desktop.
  - Simplificação total da interface e da lógica do dashboard do Streamlit.
- **Decisões Tomadas**:
  - Criação do botão **"Encerrar Dashboard"** e controle robusto via subprocesso (`subprocess.Popen`), integrando a terminação do Streamlit ao fechar o painel desktop.
  - Reescrever o Streamlit (`dashboard_app.py`) com um design premium simplificado e escuro (Dark Mode + Glassmorphism), removendo lógicas complexas de dataframes e oferecendo tolerância elegante a falhas de carregamento de esquemas de banco legados.
  - Limpeza dos caches e encerramento de processos em conflito em segundo plano.
- **Status/Próximos Passos**:
  - Continuar com o desenvolvimento refinado de extração e otimizações.
