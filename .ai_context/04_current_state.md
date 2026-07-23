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
- [x] Integrar o `FolderWatcher` e o Pipeline de ETL (PdfReader, OllamaClient, TinyDbRepo) no painel desktop `src/presentation/desktop/desktop_app.py` com console de log.
- [x] Implementar fila de processamento (`queue.Queue`) e contadores estatísticos em tempo real (Lendo, Lidos, Fila) no painel desktop.
- [x] Configurar o TinyDB para gravação em UTF-8 e impedir escape de caracteres unicode.
- [x] Desenvolver barra de carregamento (`CTkProgressBar`) e cálculo de progresso por bytes na UI.
- [x] Adicionar rastreamento de arquivo de origem (`source_file`) e verificação de duplicidade antes do processamento.
- [x] Incluir contador visual na UI para arquivos já cadastrados (pulados).
- [x] Criar configuração de versionamento Git com o arquivo `.gitignore`.
- [x] Desenvolvimento da interface web de relatórios (UI) com Streamlit em `src/presentation/web_dashboard/dashboard_app.py` para visualizar e buscar boletins cadastrados na base TinyDB.
- [x] Implementar recursos de busca por palavras-chave, filtros por tipo de crime, participantes ou cidades no dashboard Streamlit.
- [x] Desenvolver sistema de classificação e agrupamento de ocorrências (AVANTE, Outras Ocorrências Importantes e Demais Fatos) no OllamaClient e no Dashboard.
- [x] Refatorar a base de código do projeto de acordo com princípios de Clean Code e SOLID (criação do `EtlService` para isolar lógica de negócio da interface gráfica).
- [x] Desenvolver a etapa de pré-processamento e limpeza de texto bruto (Fase 2) usando expressões regulares para remover assinaturas e listas de distribuição.
- [x] Implementar a extração em fases (Fase 1: metadados, Fase 3: segmentação/enquadramento, Fase 4: estruturação localizada) no `OllamaClient` e `EtlService`.
- [x] Otimizar a interface do CustomTkinter para logs em tempo real por fase e registro de tempo total.
- [x] Implementar classificação da natureza do registro (Ocorrência vs Denúncia vs Informação vs Resposta a PB) no OllamaClient, EtlService e Dashboard.
- [x] Adicionar botão no Painel Desktop (CustomTkinter) para abrir o Dashboard Web (Streamlit) automaticamente no navegador.
- [x] Resetar a extração multifásica e simplificar o pipeline de leitura da IA (para focar apenas no conteúdo e arquivo de origem).
- [x] Implementar limpeza automatizada do cabeçalho restrito de salvaguarda administrativa.
- [x] Criação de um Motor de Regras (Rule Engine) na camada de domínio (`IncidentRule` e `HomicideRule`).
- [x] Desenvolvimento da filtragem rápida de texto bruto (pré-filtro) no `EtlService` para evitar processamento desnecessário na LLM local.
- [x] Suporte a gravação em múltiplos arquivos de banco do TinyDB baseado no tipo de fato monitorado (ex: `homicides.json`).
- [x] Atualização do painel desktop (botão "Monitorar Homicídios") e do dashboard Streamlit para leitura focada do banco de homicídios.
- [x] Implementação de filtro inteligente pós-LLM (Double-Check) validando o campo booleano `is_target_incident` no JSON gerado pelo Ollama para descartar falsos positivos semânticos.
- [x] Refinamento das regras de Homicídios para abranger Feminicídios (tentados/consumados) e Encontros de Cadáver violentos.
- [x] Implementação de pré-filtro de exclusão rápida (excluindo lesões leves, investigações sociais, etc., sem óbitos) para otimizar o reprocessamento de diretórios.
- [x] Criação de registro central de histórico de processamento (`processed_registry.json`) para evitar re-análise de PDFs processados ou descartados.
- [x] Criação de aba única "Relatórios de Leitura" com tela de carregamento animada durante monitoramento ativo e renderização estática otimizada ao finalizar.
- [x] Criação de contadores e listas estáticas para o relatório de Homicídios (Totais, Já Lidos, Descartados em Pré-Filtro, Descartados por LLM, e Confirmados) com busca e reprocessamento individual de arquivos.
- [x] Transição de LLM para processamento local: substituição do `TransformersQaClient` pelo `LocalRegexProcessor` para remover dependências de IA (Hugging Face / PyTorch).
- [x] Otimização e alívio do pré-filtro em `HomicideRule` para evitar falsos negativos em casos com múltiplos fatos (ex: lesão seguida de morte).
- [x] Aprimoramento do pós-filtro local para descartar falsos positivos semânticos (ex: "ameaça de morte" sem óbito) com regras detalhadas de cruzamento de natureza e letalidade.
- [x] Aprimoramento da limpeza de texto bruto para remover numerações de página em diversos formatos (Página X de Y, Pág X, etc.) e números isolados.
- [x] Alteração no formato do campo `content` salvo no TinyDB para conter o prefixo `"Arquivo: {filename}\nConteúdo:\n"`.
- [x] Adição do campo `user_edited` em `IncidentReport` e métodos no repositório/registro para suportar rastreamento de modificações manuais do usuário.
- [x] Implementação no `EtlService` de lógica para priorizar as edições do usuário sobre o processamento da IA/Regex ao reprocessar arquivos.
- [x] Criação de formulário interativo de edição de Fato (Natureza) para cada ocorrência no Dashboard Streamlit, salvando as alterações no TinyDB e no histórico central.

## O que está sendo feito agora:
- [ ] Classificação dos RELINTs (ajustes finos nas heurísticas de classificação).

## Próximos Passos Pendentes:
- [ ] Melhorias no Layout e Design Visual do Dashboard Streamlit.
- [ ] Adicionar suporte a exportação de dados em CSV ou Excel diretamente pelo dashboard do Streamlit simplificado.
- [ ] [Discussão de Arquitetura] Avaliar regra de precedência para que fatos classificados como Homicídio não sejam reprocessados para outras regras de menor prioridade.
