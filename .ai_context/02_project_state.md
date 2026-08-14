# Estado do Projeto e Backlog

Este arquivo documenta o que já foi construído, o que está sendo finalizado no momento e o backlog de tarefas futuras do **ReadRelint**.

## 1. O que já foi implementado (Checklist Final)
- [x] Configuração da Clean Architecture (Portas, Adaptadores, Domínio, Aplicação e Apresentação).
- [x] Leitura de PDF (`PyMuPDF`) e monitoramento em tempo real (CustomTkinter + FolderWatcher).
- [x] Migração de Banco de Dados de JSON (TinyDB) para **SQLite nativo (WAL)**, com tabelas dedicadas (`relints` e `persons`).
- [x] Pipeline ETL com NLP Local (Ollama) para estruturação semântica, mantendo a extração literal (`content`) 100% via código Python.
- [x] **Arquitetura de Especialidades Polimórficas:** Modelo `HomicideReport` estendendo `IncidentReport` com extração de 6 campos extras (motivação, registro, ano, unidade BPM, tipo de fato) persistidos no JSON flexível do SQLite.
- [x] **Extração LLM com Schema Pydantic Dinâmico:** Atualização do `OllamaClient` e `ILlmProcessor` para receber o modelo Pydantic da regra via `get_schema_model()`.
- [x] **Classificador Determinístico (`bm_classifier.py`):** Sistema de classificação regex por hierarquia de especificidade que corrige o `bm_group` pós-LLM, eliminando o problema de ocorrências caírem indevidamente em "Outros".
- [x] **Redesign completo do Dashboard Web (Resend Design System):**
  - Implementação fiel ao `Design.md`: Canvas preto puro (`#000000`), hairlines translúcidas (`rgba(255,255,255,0.14)`), sem sombras pesadas.
  - Eliminação de todos os estilos de cores claras hardcoded.
  - Variáveis modulares em `variables.css` sem referências circulares.
- [x] **Aba e Controlador de Homicídios (`homicides_view.js`):** Visualizador de dossiês focado na especialidade policial com separação de vítimas, acusados e motivação.
- [x] **Dashboard de Crimes & Estatísticas (`crimes_view.js`):** Painel de Analytics com KPI Cards (Total, Homicídios, Tráfico, Top Município), Gráficos interativos Donut/Area via **ApexCharts** (100% offline) e feed de ocorrências recentes.
- [x] Implementação de visualizador de imagens (Lightbox) e galeria global integrada.
- [x] Suíte de Testes Automatizados (60 testes unitários passando em 100% com `pytest`).

## 2. Próximas Etapas (Prioridade)

### ETAPA 1 — Acesso Online Seguro (Cloudflare Tunnel + E2EE)
- [ ] Configurar **Cloudflare Tunnel** para expor o FastAPI local via domínio fixo com HTTPS.
- [ ] Implementar **Criptografia Ponta-a-Ponta (E2EE)** na camada da aplicação:
  - Backend (Python): criptografar respostas da API com AES-256-GCM usando chave derivada da senha do usuário (PBKDF2/HKDF).
  - Frontend (JavaScript): descriptografar dados no navegador via Web Crypto API.
  - Cloudflare vê apenas blobs cifrados — dados de inteligência nunca expostos em trânsito.
- [ ] Autenticação de usuário com hash seguro (bcrypt/argon2) separado da chave de criptografia.

## 3. Backlog Futuro
- [ ] **Exportação de Relatórios Estruturados:** Botões para exportar Dossiê e Casos para Excel, CSV ou PDF.
- [ ] **Grafos de Vínculos (Visualização Gráfica):** Plot interativo mostrando conexões em rede entre Pessoas e Relatórios.
- [ ] **Check de Hashes (SHA-256):** Hashing dos PDFs para re-processamento automático ao detectar modificações.
