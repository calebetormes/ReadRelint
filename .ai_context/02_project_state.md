# Estado do Projeto e Backlog

Este documento documenta o que já foi construído, o que está sendo finalizado no momento e o backlog de tarefas futuras do **ReadRelint**.

## 1. O que já foi implementado (Checklist Final)
- [x] **Estrutura de Pastas Simplificada:** Organização limpa na raiz do projeto: `backend/` (contendo api, core, database, engine, task_manager e desktop controllers), `frontend/` (SvelteKit SPA integrado com CSS nativo no `app.css` / `variables.css`), `tests/` e `data/`.
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
- [x] **Painel de Controle Desktop Nativo em PyQt6 (`painel.py` / `desktop/ui/pyqt_app.py`):** Painel desktop construído em **PyQt6 (Qt6 nativo)** com tema escuro moderno (QSS), alta estabilidade e layout otimizado em **2 Abas Estratégicas**:
  - **Redimensionamento Livre da Janela + Coluna Esquerda com Largura Fixa (`410px`):** O usuário pode redimensionar a janela principal livremente sem que os controles e barras sofram deformações.
  - **Aba 1 (Operação & Leitura em Split View):** Coluna esquerda fixa com seletor nativo de pastas (`QFileDialog`), botão principal de monitoramento, **Barras Lineares Tradicionais de Progresso** (Total da Pasta e Sessão Atual com porcentagens e contadores), **Caixa de Status Estática com Extração Inteligente do Número/Código do RELINT (`RELINT Nº ...` + Tooltip com nome completo)**, **Indicador de Leitura Ativa Estilo Web** (animação contínua a 60 FPS com spinner e marquee animado com `RetainSizeWhenHidden` contra pulos de layout) e card de Ações Rápidas com alternador do Modo IA, botão do Dashboard Web e botão **`⛔ Encerrar Todos os Serviços & Sair`** posicionado estrategicamente abaixo do Dashboard. Coluna direita com **Console de logs com Efeito Typewriter Inteligente (Auto-Speed)**, **destaque de mensagens de erro em vermelho vívido (`#ef4444`)** e auto-scroll thread-safe.
  - **Aba 2 (Serviços & Relatórios):** Card de diagnóstico dos serviços com **ServiceWatcher assíncrono em background** (zero bloqueios de rede/subprocessos na UI thread) e **histórico limpo de RELINTs processados** (fonte compacta de 11px em até 2 linhas com `setWordWrap`, badge de método `IA`/`Regex`, badge de status `🟢 Lido com Sucesso`, **badge/card em vermelho `#451a1a` para falhas de leitura (`🔴 Falha na Leitura`)** e **botão largo de reprocessamento `🔄 Re-processar`**).
  - **Performance & Zero Latência:** Fila de logs em lote com Typewriter a 60 FPS acelerado ao fim da leitura eliminando engasgos de renderização do `QTextEdit`, proteção seletiva de botões de disco durante leitura e atualização ultrarrápida de progresso (< 0.1ms).
  - **Minimização na Bandeja do Sistema (`System Tray`):** Fechar a janela minimiza o app diretamente para o System Tray com menu de contexto (`Abrir Painel`, `Abrir Dashboard Web`, `Encerrar Todos os Serviços`). `setQuitOnLastWindowClosed(False)` garante permanência em background sem fechar o processo.
  - **Botão de Encerramento Total (`⛔ Encerrar Todos os Serviços & Sair`):** Finaliza com segurança todos os processos (Watchdog, FastAPI, Vite/Node na porta 5173), fecha o tray icon e encerra o app completamente.
- [x] **Limpeza de Arquivos Legados do Flet:** Expurgo total de arquivos e referências legadas do Flet (`flet_app.py`), concentrando a stack desktop exclusivamente no PyQt6 e o frontend no SvelteKit.
- [x] **Arquitetura de Especialidades Polimórficas:** Modelo `HomicideReport` estendendo `IncidentReport` com extração especializada (motivação, registro policial, unidade BPM) persistida no SQLite.
- [x] **Classificador Determinístico (`bm_classifier.py`):** Classificação regex por especificidade pós-LLM e fallback para processamento sem IA.
- [x] **Dashboard Web Completo (Resend Design System):**
  - Tema escuro puro (`#000000`), hairlines translúcidas, componentes modulares em `variables.css`.
  - Visualizador de dossiês por especialidade (`homicides_view.js`).
  - Dashboard de Crimes & Analytics com gráficos offline **ApexCharts** (`crimes_view.js`).
  - Galeria de imagens geral com visualizador Lightbox com zoom.
- [x] **Suíte de Testes Automatizados:** 110 testes unitários e de integração de API com `pytest` cobrindo 100% da aplicação.
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
- [x] **Unificação Global e Modularização de Abas (DRY Architecture):**
  - **Componente Único de Participantes (`ParticipantsTabComponent`):** Layout Master-Detail (40% Lista / 60% Dossiê) com busca em tempo real por nome/vulgo, badges de função e suporte a galeria de imagens vinculadas.
  - **Biblioteca Central de Abas (`RelintTabsComponents`):** Renderização padronizada de `Síntese` (caixa compacta invertida + resumo), `Especialidades` (atributos estruturados), `Fotos` (galeria com lightbox), `Localização` (dashboard geográfico com OSM iframe e badges de precisão) e `Transcrição` (leitor literal).
  - Eliminação de duplicação de código entre os painéis `relints_view.js` e `homicides_view.js`.
- [x] **Migração para SvelteKit & Sistema de Design Tokens do Penpot:**
  - Construção da biblioteca oficial de 10 componentes de UI em Svelte 5 (`Button`, `Badge`, `Card`, `StatCard`, `Input`, `Switch`, `Alert`, `Table`, `Modal`, `Tabs`) consumindo estritamente variáveis de tokens (`style.css`) e respeitando a grade base de 4px e interações táteis do Apple Design.
  - Ajustado o alinhamento vertical *Pixel-Perfect* de ícones e tipografia em todos os componentes (`Button`, `Badge`, `Input`, `Tabs`, `Alert`), isolando os nós SVG em `inline-flex` e fixando a linha base ótica com `line-height: 1`.
  - Implementado o **App Shell do Dashboard** modular em `src/lib/components/layout/` contendo `Sidebar.svelte` (retrátil com ícones Phosphor), `Header.svelte` (fixo) e `AppShell.svelte`.
  - Criada a nova rota dedicada **`/relints` ("Boletins RELINT")** no layout **Master-Detail (30% / 70%)**:
    - **Lista Master (30%)**: Busca em tempo real, filtros por especialidade e indicador `<Badge variant="success"><CheckCircle /> Revisado</Badge>`.
    - **Workspace (70%)**: 5 sub-abas modulares (`Geral`, `Localização`, `Especialidade`, `Participantes`, `Transcrição`) com CRUD de participantes e visualização em cards.
  - Reorganizada a estrutura de rotas: `/` tornou-se a "Visão Geral" do Dashboard (Estatísticas e KPIs) usando o novo App Shell, enquanto a biblioteca visual foi preservada na rota exclusiva `/design-system`.
  - Preservados todos os documentos de contexto e workflows na pasta `.agents/` e `.ai_context/`:
    - `.ai_context/05_design_system_penpot_guide.md` (Guia de Design System e sincronização com Penpot);
    - `.agents/workflows/sync-penpot.md` (`/sync-penpot`: Workflow de auditoria 1:1 e sincronização Penpot -> Código);
    - `.agents/workflows/export-to-penpot.md` (`/export-to-penpot`: Workflow de geração de componentes Código -> Penpot).


## 2. Próximas Etapas (Prioridade)

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
