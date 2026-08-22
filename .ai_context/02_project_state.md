# Estado do Projeto e Backlog

Este documento documenta o que já foi construído, o que está sendo finalizado no momento e o backlog de tarefas futuras do **ReadRelint**.

## 1. O que já foi implementado (Checklist Final)
- [x] **Arquitetura Limpa e Modular:** Organização rigorosa em três pilares independentes: `src/engine/` (motores de parsing, NLP e regex), `src/task_manager/` (pipeline ETL, monitor de pastas e controle de estado) e `src/dashboard/` (backend FastAPI, frontend SPA Resend e desktop Tkinter launcher).
- [x] **Banco de Dados Relacional SQLite (WAL):** SQLite nativo (`relints.db`) com tabelas em Português (`relints`, `pessoas`, `relint_participantes`, `homicidio_detalhes`, `relint_imagens`) e auto-migração de schema.
- [x] **Processamento Híbrido (Ollama Local / Pipeline Determinístico):** Suporte a modo com IA e 100% sem IA via chave/switch no app Desktop e na Web, com monitor de saúde do Ollama em tempo real (heartbeat) e fallback gracioso.
- [x] **Rastreabilidade de Método de Leitura (`extraction_method`):** Gravação explícita de `"Ollama (IA)"` vs `"Regex (Sem IA)"` no banco relacional e exibição de badges coloridos na interface.
- [x] **Aba Web de Monitoramento & IA (`monitoring_view.js`):**
  - Réplica completa do motor de monitoramento do Tkinter na Web em tema **Resend Dark System**.
  - **Layout Split View:** Painel de controle responsivo com terminal de logs em tempo real (SSE Streaming) na coluna da direita.
  - **Medidores Circulares SVG (Apple Watch Style):** Cards individuais com medidores em anel, porcentagem centralizada e animações em tempo real de `stroke-dashoffset`.
  - **Seletor Nativo do Windows (`📁 Procurar Pasta no PC`):** Aciona a janela `filedialog.askdirectory()` do Windows via API local (`POST /api/v1/monitoring/browse`).
  - **Pausa Imediata de Leitura:** Limpeza instantânea da fila de processamento (`processing_queue.queue.clear()`).
  - **Relatório em 2 Colunas:** Gauges SVG verticais na coluna esquerda e lista de RELINTs com scroll adaptativo na coluna direita.
- [x] **Redesign Compacto do App Desktop (480x580 - Service Launcher & Status Hub):** Interface Tkinter ultraleve com foco em ligar/desligar serviços (Monitor de Pastas, Servidor Web e IA) e suporte a minimizado para a Bandeja do Sistema (System Tray) via `pystray`.
- [x] **Arquitetura de Especialidades Polimórficas:** Modelo `HomicideReport` estendendo `IncidentReport` com extração especializada (motivação, registro policial, unidade BPM) persistida no SQLite.
- [x] **Classificador Determinístico (`bm_classifier.py`):** Classificação regex por especificidade pós-LLM e fallback para processamento sem IA.
- [x] **Dashboard Web Completo (Resend Design System):**
  - Tema escuro puro (`#000000`), hairlines translúcidas, componentes modulares em `variables.css`.
  - Dossiês de especialidades (`homicides_view.js`), Dossiês de pessoas (`participants_view.js` com layout 40%/60%), Analytics de crimes (`crimes_view.js` com gráficos ApexCharts) e Galeria geral com lightbox e zoom.
- [x] **Modal de Edição de RELINTs em 5 Sub-Abas:** Interface completa para edição humana (`user_edited = True`) com vinculação de fotos a participantes e formulários dinâmicos por tipo de crime.
- [x] **Arquitetura Reativa em Tempo Real (SSE):** Barramento pub/sub `EventBroadcaster` atualizando abas da SPA instantaneamente sem recarregar a página ao processar novos PDFs.
- [x] **Motor Modular Especialista de Participantes em 5 Camadas:**
  1. Blocos estruturados e padrões inline com qualificadores de idade.
  2. Reconhecimento de entidades via `spaCy` (`pt_core_news_sm`).
  3. Validação positiva de prenomes brasileiros via Censo IBGE (`ibge_names.json`) em O(1).
  4. Detecção direcional de papéis e especificidade léxica (`role_detector.py`).
  5. Filtros negativos estritos de patentes militares, órgãos públicos e termos veiculares (`negative_filters.py`).
- [x] **Auditoria em Massa (222 RELINTs) & Calibração Especialista Baseada em Dados:**
  - Varredura completa de 222 relatórios reais, mapeando mais de 650 pessoas e reduzindo anomalias de nomes em **92.3%** (de 169 para 13 casos residuais).
  - Algoritmo de desempate por proximidade e especificidade léxica (`role_detector.py`).
  - Diferenciação precisa de menores infratores vs menores vítimas e relações familiares (*Pai da Vítima* $\rightarrow$ Testemunha).
  - Isolamento de sequências em caixa alta e expurgo de prefixos narrativos em `clean_person_name`.
- [x] **Pipeline Híbrido com LLM (Cognição Profunda + Guardrails Determinísticos):**
  - Envio da transcrição limpa ao Ollama com instruções estritas de papéis, antecedentes (`background`) e regra anti-PM.
  - Pós-processamento e fusão em `etl_service.py` aplicando sanitização de nomes, recuperação de documentos por proximidade (`extract_document_near_name`), validação contextual de papéis e filtro anti-alucinação de policiais.
- [x] **Unificação das Classificações de Participantes para 3 Papéis Oficiais:**
  - Unificação de *Acusado*, *Autor*, *Suspeito*, *Infrator* e *Preso* na categoria oficial **`Autor/Suspeito`**.
  - Definição do trio fechado: **`Vítima`**, **`Testemunha`** e **`Autor/Suspeito`** em todos os contratos Pydantic (`ParticipationType`), detectores determinísticos, prompts de LLM, formulários modais de edição Web e registros no banco SQLite (`relint_participantes`).
  - Criação do relatório detalhado de erros por caso em [`data/erros.md`](file:///e:/www/ReadRelint/data/erros.md).
- [x] **Suíte de Testes Automatizados:** 100% de cobertura nos testes críticos de extração, limpeza de texto, detecção de papéis e persistência.

## 2. Próximas Etapas (Prioridade)

### ETAPA 1 — Migração para SvelteKit
- [ ] Inicializar projeto SvelteKit na pasta `src/dashboard/frontend`.
- [ ] Configurar modo SPA (adapter-static) e Vite proxy para o backend FastAPI.
- [ ] Reimplementar layout responsivo e temas (Resend Dark/Light) baseados em `design-system.html` e `04_dashboard_ui_ux_spec.md`.

### ETAPA 2 — Recursos Avançados de Vinculação e Edição
- [ ] Implementar seletor interativo para vincular fotos específicas a participantes durante o modal de edição do RELINT.
- [ ] Refinar feedback visual e notificações de conclusão de arquivos na Web.
- [ ] Adicionar ordenação rápida e filtros por status de erro no relatório de leitura.

### ETAPA 2 — Acesso Online Seguro (Cloudflare Tunnel + E2EE)
- [ ] Configurar **Cloudflare Tunnel** para expor o FastAPI local via domínio fixo com HTTPS.
- [ ] Implementar **Criptografia Ponta-a-Ponta (E2EE)** na camada da aplicação.

## 3. Backlog Futuro (Planejado / Aguardando Ordem de Execução)
- [ ] **Dashboard Público Anonimizado (Hostinger):**
  - Gerenciador de layouts e páginas de dashboards no app local (ReadRelint).
  - Botão de publicação inicial com geração de payload 100% anonimizado (apenas totais/KPIs numéricos, 0% PII ou textos de RELINTs).
  - Sincronização automática em tempo real: após publicado, novos PDFs lidos localmente disparam PUSH dos deltas estatísticos para a Hostinger.
  - Hospedagem pública Hostinger com autenticação por senha e logs de visualização no futuro.
- [ ] **Exportação de Relatórios Estruturados:** Botões para exportar Dossiê e Casos para Excel, CSV ou PDF.
- [ ] **Grafos de Vínculos (Visualização Gráfica):** Plot interativo mostrando conexões em rede entre Pessoas e Relatórios.
- [ ] **Check de Hashes (SHA-256):** Hashing dos PDFs para re-processamento automático ao detectar modificações no arquivo.
