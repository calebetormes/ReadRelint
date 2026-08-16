# Decisões Técnicas e Fluxo da IA (ADR & Workflow)

Este documento contém os registros de decisões arquiteturais importantes (ADRs) que ditam a lógica técnica do projeto, e os roteiros operativos de como o Agente de IA deve atuar.

## 1. Roteiros de Fluxo da IA (AI Workflows)

### Prompt Inicial Recomendado (Sempre que reiniciar contexto)
```text
Olá! Vamos trabalhar no Administrador de RELINTs. Leia estritamente a nova estrutura consolidada da pasta `.ai_context` (`01_project_blueprint.md`, `02_project_state.md`, `03_decisions_and_workflow.md`) para absorver a arquitetura e entender em que passo estamos.
Lembre-se da REGRA DE IDIOMA HÍBRIDO: Código-fonte sempre em Inglês; Documentação e comentários em pt-BR. Não escreva código ainda. Apenas confirme o entendimento.
```

### Prompt de Encerramento (Finalização de Sessões)
Sempre que concluir grandes blocos de tarefas:
1. Atualize o `02_project_state.md`, movendo os itens de "Tarefas Futuras" para "Implementados".
2. Se criamos novos módulos arquiteturais, adicione um novo [ADR] na seção abaixo ou atualize o `01_project_blueprint.md`.
3. Ofereça um resumo legível e gere um `walkthrough.md` caso estivesse em Planning Mode.

---

## 2. Registro de Decisões de Arquitetura (ADRs)

- **[ADR-001] Clean Architecture e NLP Local:** Isolamento total via Ports e Adapters. Uso exclusivo do `Ollama` rodando localmente, evitando quebras de LGPD (nenhum PDF sai da máquina).
- **[ADR-002] Interface Híbrida:** FastAPI + SPA Web para leitura e cruzamento (Dashboard) e CustomTkinter para monitoramento de pastas OS-level (Desktop).
- **[ADR-003] Migração de TinyDB para SQLite (Persistência Principal):** Uso de `SQLite` nativo em modo WAL (Write-Ahead Logging) em `data/relints.db`. Motivo: Resiliência contra concorrência e tabelas estruturadas que permitem queries velozes para dossiês.
- **[ADR-004] Separação de Dados de Pessoas:** Criação da tabela e domínio independente de `Person` no SQLite (`persons`). Garante dossiês hiper-velozes e cruzamento de vínculos de pessoas através dos RELINTs.
- **[ADR-005] Exclusão de Guarnições PM e Transcrição Segura:** Policiais não são adicionados aos dossiês de pessoas investigadas. O histórico literal (`content`) do boletim é extraído via código determinístico (Python/Regex) e ocultado da IA (LLM).
- **[ADR-006] Prioridade da Curadoria Humana:** Uso do `processed_registry.json` para gravar edições efetuadas pelo usuário humano e forçar que a IA nunca sobrescreva alterações humanas caso o PDF seja reprocessado.
- **[ADR-007] Geolocalização Visual por 3 Níveis:** Cores indicando precisão da localização no Dashboard: Verde (GPS exato capturado do PDF), Azul (Link explícito capturado), Laranja (Endereço estruturado via fallback).
- **[ADR-008] Repositório Universal (Sem Descartes):** Nenhum boletim válido lido do diretório deve ser silenciado. Todos devem ir para o banco. A filtragem de "ocorrências indesejadas" ocorre apenas na UI.
- **[ADR-009] Suíte de Testes 100% Mockada:** O `pytest` usa fixtures de memória (`tmp_path`) e mocks simulando Ollama e PyMuPDF para executar CI instantâneo.
- **[ADR-017] Remoção da Tabela de Municípios (Cálculo On-The-Fly):** Eliminação da tabela `municipalities`. Os índices de criminalidade são agrupados dinamicamente diretamente a partir da tabela principal `relints`.
- **[ADR-018] Migração de Streamlit para FastAPI + Frontend Custom:** Decisão de substituir o Streamlit por uma arquitetura **FastAPI (backend API REST)** + **Frontend HTML/CSS/JS puro**.
- **[ADR-019] Acesso Online com E2EE (Cloudflare Tunnel):** Criptografia ponta-a-ponta (AES-256-GCM) na camada da aplicação.
- **[ADR-020] Descarte da Associação Automática de Fotos a Participantes:** Todas as imagens vão para a galeria geral do RELINT.
- **[ADR-021] Remoção Completa do Streamlit:** Limpeza de dependências e código do Streamlit.
- **[ADR-022] Especialidades Polimórficas (Homicídios):** Criação de modelos Pydantic estendidos (`HomicideReport` herdando de `IncidentReport`) para suportar dados especializados (motivação, registro policial, unidade BPM) sem alterar a estrutura da tabela SQLite.
- **[ADR-023] Schemas Dinâmicos na Camada Cognitiva (LLM):** O `ILlmProcessor` e `OllamaClient` passam a aceitar `schema_model: Optional[type]`, permitindo que cada regra (`IncidentRule`) defina via `get_schema_model()` qual estrutura Pydantic a IA deve preencher.
- **[ADR-024] Classificação Determinística por Regex (`bm_classifier.py`):** Adição de uma camada de segurança determinística pós-LLM que classifica o `bm_group` baseado em padrões de texto no nome do arquivo, assunto e conteúdo ordenados por especificidade.
- **[ADR-025] Adoção do Resend Design System (`Design.md`):** Reconstrução do tema CSS da aplicação Web com base nas diretrizes do `Design.md`: Canvas preto puro (`#000000`), hairlines translúcidas (`rgba(255,255,255,0.14)`), fontes Inter/Mono.
- **[ADR-026] Dashboard Analytics com ApexCharts Offline:** Adição do módulo `crimes_view.js` com KPIs dinâmicos, gráficos interativos de distribuição e linha do tempo usando **ApexCharts** mantido totalmente offline em `assets/vendor/`.
- **[ADR-027] Foco na Experiência Desktop Nativa (Tkinter / CustomTkinter):** Decisão de manter a interface Desktop nativa para gerenciamento do motor local e monitoramento de pastas.
- **[ADR-028] Tema Dark Slate Neutro para UI Desktop:** Eliminação completa de subtons de azul na interface CustomTkinter em favor de tons de carvão neutros (`#121212`, `#18181b`, `#27272a`) com acentos em Verde Esmeralda (`#10b981`), Teal (`#0d9488`) e Âmbar (`#d97706`), garantindo alto contraste de texto branco (`#ffffff`).
- **[ADR-029] Duas Barras de Progresso e Inspecção Instantânea de Diretório:** Inspecção imediata no `MainController.inspect_folder()` ao selecionar o diretório via `filedialog`. Separação em Barra 1 (`📄 Arquivos Lidos na Pasta`) atualizada em tempo real a cada leitura concluída, e Barra 2 (`⚡ Progresso da Leitura Atual`) monitorando a fila ativa da sessão.
- **[ADR-030] Rastreabilidade de Método de Extração (`Ollama (IA)` vs `Regex (Sem IA)`):** Adição da coluna `extraction_method` no banco SQLite para identificar a origem da extração de cada documento, permitindo que a aplicação opere com alta velocidade 100% sem LLM ou com IA local, exibindo badges visuais e relatórios atualizados em tempo real.
- **[ADR-031] Monitoramento de Conexão da LLM em Tempo Real (Heartbeat):** Execução de polling assíncrono leve a cada 4 segundos (`check_llm_heartbeat`). Em caso de interrupção ou fechamento do serviço Ollama, o sistema desativa o switch visual da IA, notifica no console de log e faz fallback instantâneo sem perda de dados para o pipeline Regex.
