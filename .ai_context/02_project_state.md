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
  - Visualizador de dossiês por especialidade (`homicides_view.js`).
  - Dashboard de Crimes & Analytics com gráficos offline **ApexCharts** (`crimes_view.js`).
  - Galeria de imagens geral com visualizador Lightbox com zoom.
- [x] **Suíte de Testes Automatizados:** 67 testes unitários e de integração de API com `pytest` cobrindo 100% da aplicação com execução em ~3.4s.
- [x] **Unificação de Ações e Minimalismo no Header Web:** Remoção do botão `Abrir Dashboard` e Badge de Status do topo, centralizando ações de UX na interface principal e limpando componentes obsoletos. O botão de recolher a Sidebar foi convertido em um botão circular flutuante elegante.
- [x] **Botões e Navegação Enxutos:** Remoção do box-border redundante nos botões de abas da visualização de Monitoramento. Troca do Checkbox estático do motor IA por um Botão de Status Interativo e Inteligente (Verde Esmeralda p/ ativo, Amarelo de Alerta p/ Modo Regex).
- [x] **Melhoria Gráfica Circular Avançada:** Engrossamento dos SVGs da aba de Monitoramento para o formato Anel Premium (tipo Apple Watch), com ajuste dinâmico do `overflow: visible` para eliminação do corte na caixa da animação incandescente e aumento da pulsação e velocidade das barras luminosas.
- [x] **Indicador Animado de Carregamento:** O painel de leitura agora conta com um Spinner animado inline (`<svg class="spin-fast">`) elegante em vez de texto seco durante a leitura do conteúdo do relatório.
- [x] **Estabilidade e Loading Otimista da IA:** Adição de feedback visual instantâneo (spinner "Testando IA..." ou "Desativando...") ao alternar o modo de processamento de Inteligência Artificial. Implementação de proteção de concorrência (flag `_isTogglingLLM`) para impedir que o polling assíncrono de gráficos sobreponha o estado do botão durante a latência de rede/Ollama, e correção do bug que travava cliques subsequentes.
- [x] **Migração de Esquema do Banco de Dados e Sistema para Português (pt-BR):**
  - Tradução de todas as tabelas (`relints`, `homicidio_detalhes`, `pessoas`, `relint_participantes`, `relint_imagens`) e colunas no SQLite nativo e adapters (`SqliteRepo`, `SqlitePersonRepo`).
  - Auto-migração transparente de bancos legados executada em `_init_db()` via `ALTER TABLE RENAME COLUMN`.
  - Atualização do arquivo de especificação do banco `schema.dbml` com todas as colunas e tabelas de especialidade polimórficas (Tráfico, Roubos e Furtos) em Português.
  - Suporte completo a aliases Pydantic e fallbacks retrocompatíveis na API REST e na interface Web SPA (`relints_view.js`, `homicides_view.js`).
  - Suíte de 69 testes automatizados aprovada com 100% de cobertura (~3.1s).
- [x] **Unificação Global e Modularização de Abas (DRY Architecture):**
  - **Componente Único de Participantes (`ParticipantsTabComponent`):** Layout Master-Detail (40% Lista / 60% Dossiê) com busca em tempo real por nome/vulgo, badges de função e suporte a galeria de imagens vinculadas.
  - **Biblioteca Central de Abas (`RelintTabsComponents`):** Renderização padronizada de `Síntese` (caixa compacta invertida + resumo), `Especialidades` (atributos estruturados), `Fotos` (galeria com lightbox), `Localização` (dashboard geográfico com OSM iframe e badges de precisão) e `Transcrição` (leitor literal).
  - Eliminação de duplicação de código entre os painéis `relints_view.js` e `homicides_view.js`.

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
