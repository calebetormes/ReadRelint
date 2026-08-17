# Estado do Projeto e Backlog

Este arquivo documenta o que já foi construído, o que está sendo finalizado no momento e o backlog de tarefas futuras do **ReadRelint**.

## 1. O que já foi implementado (Checklist Final)
- [x] **Arquitetura Limpa:** Padrão Ports and Adapters rigorosamente isolado em `src/domain`, `src/ports`, `src/adapters`, `src/application` e `src/presentation`.
- [x] **Banco de Dados Relacional SQLite (WAL):** Migração para SQLite nativo (`relints.db`) com tabelas estruturadas (`relints` e `persons`) e migração automática de schema (`ALTER TABLE` para `extraction_method`).
- [x] **Processamento Híbrido (Ollama Local / Regex Sem IA):** Suporte a modo 100% sem LLM via chave/switch no app Desktop e na Web, com teste de integridade/saúde do Ollama.
- [x] **Monitor de Saúde da LLM em Tempo Real (Heartbeat):** Polling assíncrono executado a cada 4s no Desktop e via SSE/cache de 5s no FastAPI na Web. Caso o serviço do Ollama seja encerrado/fechado pelo usuário no Windows, o sistema desativa automaticamente o switch de IA, emite alerta de desconexão e comuta sem perda de dados para o modo Regex.
- [x] **Rastreabilidade de Método de Leitura (`extraction_method`):** Gravação explícita de `"Ollama (IA)"` vs `"Regex (Sem IA)"` no banco relacional e exibição de badges coloridos na interface.
- [x] **Aba Web de Monitoramento & IA (`monitoring_view.js`):**
  - Réplica completa do motor de monitoramento do Tkinter na Web em tema **Resend Dark System**.
  - **Layout Split View (60% Controle / 40% Relatório Retrátil):** Divisão de tela responsiva com botão no cabeçalho `📋 Ocultar / Exibir Relatório` que expande o painel de controle para 100%.
  - **Medidores Circulares Ampliados (SVG Circular Gauges):** Dois cards individuais em grid contendo medidores em rosca SVG (diâmetro de 140px) com porcentagem centralizada em negrito (`22px`) e animações em tempo real de `stroke-dashoffset`.
  - **Botões Estilizados Fiéis ao Menu Lateral (`.nav-item.active`):** Superfícies escuras elevadas (`var(--surface-elevated)`), hairlines translúcidas, cantos de 8px e ícones vetoriais Lucide SVG brancos.
  - **Console de Logs do Sistema em Tempo Real (SSE Streaming):** Transmissão contínua dos logs do motor do sistema (`MainController.recent_logs`) para o terminal web preto (`🖥️ Console de Logs do Sistema em Tempo Real`).
  - **Resiliência a Timeout da IA & Fila Ininterrupta:** Eliminação de falsos-positivos na desconexão do Ollama durante inferência pesada. O motor realiza fallback gracioso para Regex por arquivo se necessário e nunca trava nem força o usuário a reiniciar o monitoramento.
  - **Seletor Nativo do Windows (`📁 Procurar Pasta no PC`):** Aciona a janela `filedialog.askdirectory()` do Windows via API local (`POST /api/v1/monitoring/browse`).
  - **Pausa Imediata de Leitura:** Botão *Pausar Monitoramento* limpa instantaneamente a fila de processamento (`processing_queue.queue.clear()`), interrompendo a leitura no mesmo momento.
  - **Relatório Minimalista Enxuto:** Exibição focada (Nome do PDF, Badge do Método `🟢 Ollama` / `⚡ Regex` / `🔴 Erro`, mensagem de falha se houver e botão `🔄 Refazer Leitura`).
- [x] **Redesign Compacto do App Desktop (480x580 - Service Launcher & Status Hub):** Transformação da interface Tkinter em um gerenciador de serviços ultraleve. Remoção completa das abas pesadas de monitoramento (`control_panel_tab.py`) e relatórios (`report_tab.py`), eliminando gargalos de renderização na Main Thread e mantendo a exibição em tempo real da pasta em monitoramento, status do servidor web, status da IA e atalhos na bandeja (System Tray).
- [x] **Organização em Visão Única de Status:** Painel único `StatusTab` exibindo o estado em tempo real do Monitoramento de Pastas, Painel Web (FastAPI) e IA Local (Ollama) ao iniciar o aplicativo.
- [x] **Botão Dinâmico do Servidor Web (StatusTab):** Botão único e dinâmico que alterna entre `🌐 Iniciar & Abrir Painel Web` quando desligado e `⛔ Parar Servidor Web` com opção `🔗 Reabrir Dashboard` quando online.
- [x] **Linha Dedicada & Loading Dinâmico de Leitura (UX Web & Desktop):** Remoção do rótulo estático `"Lendo: -"` e exibição em linha própria abaixo do status com ícone de spinner animado (`loader-2` girando em tempo real) durante o processamento do PDF para eliminação da sensação de travamento.
- [x] **Sub-Abas no Monitoramento Web (Console na Direita & Relatório Dedicado):** Reposicionamento do **Console de Logs do Sistema em Tempo Real para a coluna da direita** (onde antes ficava o relatório).
- [x] **Eliminação da Oscilação (Flicker/Bounce) do Botão de Iniciar Monitoramento:**
  - Substituição da checagem frágil por parsing de string (`statusBadge.innerText.includes('Ativo')`) por controle booleano otimista do motor (`_isWebMonitoringActive`).
  - Atualização do estado do botão para vermelho (`⛔ Pausar Monitoramento`) imediatamente no momento do clique, mantendo a transição limpa e contínua sem recuos visuais.
- [x] **Relatório em 2 Colunas (20% Gráficos Circulares / 80% Lista com Scroll):** Reorganização da Sub-Aba 2 do Relatório com 3 gráficos circulares SVG verticais (`Total na Pasta`, `🟢 Lidos com IA`, `⚡ Lidos com Regex`) na coluna esquerda de 20%, e lista de RELINTs na coluna direita de 80% com altura adaptada à tela (`calc(100vh - 200px)`) e barra de rolagem customizada.
- [x] **Eliminação da Latência de 5s no Iniciar Monitoramento (E/S Bulk em Registro):**
  - Identificação e eliminação do gargalo de 5+ segundos causado por 50+ escritas síncronas em disco no arquivo `processed_registry.json` durante o loop de `start_monitoring()`.
  - Criação do método `remove_records_bulk()` permitindo escrita única em disco ou remoção 100% em memória quando os arquivos já não existem no histórico.
  - Redução do tempo de resposta do comando "Iniciar Leitura" de > 5.000ms para 0.00ms.
- [x] **Ajuste Proporcional do Console de Logs Web:** Aplicação de limite de altura dinâmico (`max-height: calc(100vh - 240px)`), altura base compacta de `380px`, barra de rolagem customizada e auto-scroll ao final para que o terminal nunca extrapole o viewport da tela.
- [x] **Limpeza da Aba de Monitoramento (ControlPanelTab):** Remoção dos botões do servidor web da aba de monitoramento, deixando a tela limpa com foco exclusivo no monitoramento de diretório.
- [x] **Suporte ao System Tray (Bandeja do Sistema Windows):** Minimizado automático ao fechar a janela (`X`), mantendo o monitoramento e o servidor web ativos em segundo plano via `pystray` com menu de contexto.
- [x] **Remoção do Botão Limpar Tudo:** Remoção do botão de limpeza de histórico no relatório para evitar inconsistências nos dados.
- [x] **Botões e Componentes no Resend Dark System (`Design.md`):**
  - Estilização minimalista com bordas finas translúcidas (`border: 1px solid var(--hairline-strong)`), superfícies escuras elevadas (`var(--surface-elevated)`), tipografia branca de alto contraste, animação hover suave (`translateY(-1px)`) e efeito tátil ao clicar (`scale(0.98)`).
- [x] **Arquitetura de Especialidades Polimórficas:** Modelo `HomicideReport` estendendo `IncidentReport` com extração especializada (motivação, registro policial, unidade BPM) persistida no JSON do SQLite.
- [x] **Classificador Determinístico (`bm_classifier.py`):** Classificação regex por especificidade pós-LLM e fallback para processamento sem IA.
- [x] **Redesign completo do Dashboard Web (Resend Design System):**
  - Tema escuro puro (`#000000`), hairlines translúcidas, componentes modulares em `variables.css`.
  - Visualizador de dossiês por especialidade (`homicides_view.js`).
  - Dashboard de Crimes & Analytics com gráficos offline **ApexCharts** (`crimes_view.js`).
  - Galeria de imagens geral com visualizador Lightbox com zoom.
- [x] **Suíte de Testes Automatizados:** 67 testes unitários e de integração de API com `pytest` cobrindo 100% da aplicação com execução em ~3.4s.
- [x] **Unificação de Ações e Minimalismo no Header Web:** Remoção do botão `Abrir Dashboard` e Badge de Status do topo, centralizando ações de UX na interface principal e limpando componentes obsoletos. O botão de recolher a Sidebar foi convertido em um botão circular flutuante elegante.
- [x] **Botões e Navegação Enxutos:** Remoção do box-border redundante nos botões de abas da visualização de Monitoramento. Troca do Checkbox estático do motor IA por um Botão de Status Interativo e Inteligente (Verde Esmeralda p/ ativo, Amarelo de Alerta p/ Modo Regex).
- [x] **Melhoria Gráfica Circular Avançada:** Engrossamento dos SVGs da aba de Monitoramento para o formato Anel Premium (tipo Apple Watch), com ajuste dinâmico do `overflow: visible` para eliminação do corte na caixa da animação incandescente e aumento da pulsação e velocidade das barras luminosas.
- [x] **Indicador Animado de Carregamento:** O painel de leitura agora conta com um Spinner animado inline (`<svg class="spin-fast">`) elegante em vez de texto seco durante a leitura do conteúdo do relatório.

## 2. Próximas Etapas (Prioridade)

### ETAPA 1 — Melhoria Avançada da UX do Monitoramento (Aba Web & Desktop)
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
