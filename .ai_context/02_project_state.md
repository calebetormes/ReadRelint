# Estado do Projeto e Backlog

Este arquivo documenta o que já foi construído, o que está sendo finalizado no momento e o backlog de tarefas futuras do **ReadRelint**.

## 1. O que já foi implementado (Checklist Final)
- [x] **Arquitetura Limpa:** Padrão Ports and Adapters rigorosamente isolado em `src/domain`, `src/ports`, `src/adapters`, `src/application` e `src/presentation`.
- [x] **Banco de Dados Relacional SQLite (WAL):** Migração para SQLite nativo (`relints.db`) com tabelas estruturadas (`relints` e `persons`) e migração automática de schema (`ALTER TABLE` para `extraction_method`).
- [x] **Processamento Híbrido (Ollama Local / Regex Sem IA):** Suporte a modo 100% sem LLM via chave/switch no app Desktop com teste de integridade/saúde do Ollama.
- [x] **Monitor de Saúde da LLM em Tempo Real (Heartbeat):** Polling assíncrono executado a cada 4s (`check_llm_heartbeat`). Caso o serviço do Ollama seja encerrado/fechado pelo usuário no Windows, o sistema desativa automaticamente o switch de IA, emite alerta de desconexão no console e comuta sem perda de dados para o modo Regex.
- [x] **Rastreabilidade de Método de Leitura (`extraction_method`):** Gravação explícita de `"Ollama (IA)"` vs `"Regex (Sem IA)"` no banco relacional e exibição de badges coloridos na interface.
- [x] **Redesign Completo da Interface Desktop (CustomTkinter):**
  - Paleta Dark Slate neutra elegante (`#121212`, `#18181b`, `#27272a`) sem tons de azul.
  - Inspecção instantânea de pasta no `MainController.inspect_folder()` ao selecionar o diretório.
  - **Duas Barras de Progresso Dinâmicas:** Barra 1 (`📄 Arquivos Lidos na Pasta`) atualizada em tempo real a cada PDF concluído, e Barra 2 (`⚡ Leitura Atual`) monitorando a fila da sessão.
  - **Ações de Re-leitura:** Botão para reset completo (`🔄 Resetar & Re-ler Todos os RELINTs`) e botão individual por arquivo (`🔄 Refazer Leitura`).
  - Botão interativo de monitoramento com estados claros (`▶️ Iniciar Monitoramento` / `⏸️ Pausar Monitoramento`) e status visual (`🟢 Monitoramento Ativo` / `⏸️ Monitoramento Pausado`).
- [x] **Arquitetura de Especialidades Polimórficas:** Modelo `HomicideReport` estendendo `IncidentReport` com extração especializada (motivação, registro policial, unidade BPM) persistida no JSON do SQLite.
- [x] **Classificador Determinístico (`bm_classifier.py`):** Classificação regex por especificidade pós-LLM e fallback para processamento sem IA.
- [x] **Redesign completo do Dashboard Web (Resend Design System):**
  - Tema escuro puro (`#000000`), hairlines translúcidas, componentes modulares em `variables.css`.
  - Visualizador de dossiês por especialidade (`homicides_view.js`).
  - Dashboard de Crimes & Analytics com gráficos offline **ApexCharts** (`crimes_view.js`).
  - Galeria de imagens geral com visualizador Lightbox com zoom.
- [x] **Suíte de Testes Automatizados:** 63 testes unitários com `pytest` cobrindo 100% da aplicação com execução em ~1.2s.

## 2. Próximas Etapas (Prioridade)

### ETAPA 1 — Acesso Online Seguro (Cloudflare Tunnel + E2EE)
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
