# Estado do Projeto e Backlog

Este arquivo documenta o que já foi construído, o que está sendo finalizado no momento e o backlog de tarefas futuras do **ReadRelint**.

## 1. O que já foi implementado (Checklist Final)
- [x] Configuração da Clean Architecture (Portas, Adaptadores, Domínio, Aplicação e Apresentação).
- [x] Leitura de PDF (`PyMuPDF`) e monitoramento em tempo real (CustomTkinter + FolderWatcher).
- [x] Migração de Banco de Dados de JSON (TinyDB) para **SQLite nativo (WAL)**, com tabelas dedicadas (`relints` e `persons`). Refatoração final (Clean Code) para remoção da tabela redundante de municípios, calculando manchas criminais dinamicamente on-the-fly.
- [x] Pipeline ETL com NLP Local (Ollama) para estruturação semântica, mantendo a extração literal (`content`) 100% via código Python.
- [x] Tratamento de histórico (Self-Healing de modelos IA, fallback de JSON Pydantic e tolerância a erros).
- [x] Dashboard Streamlit com 4 Abas Especializadas:
  - `📄 RELINTs`: Master-Detail, formulário de edição persistente.
  - `👤 Participantes`: Dossiê de cruzamento de pessoas (cross-referencing de RG/CPF/Nomes).
  - `🗺️ Municípios`: Mancha criminal dinâmica com ranking geográfico por cidade e alertas de precisão visual.
  - `🚨 Crimes`: Gráficos estatísticos por Grupo BM.
- [x] Sanitização automática e avançada via Regex de rodapés, disclaimers legais e isolamento da seção "ANEXOS".
- [x] Extração *lazy* de imagens do PDF para pastas locais `data/media/` com integração nativa de galeria no Painel Streamlit.
- [x] Suíte de Testes Automatizados 100% funcional (Pytest).

## 2. Próximas Etapas (Prioridade)

### ETAPA 1 — Redesign de Interface (UX/UI)
- [ ] Substituir o Streamlit por uma interface custom com **FastAPI (backend API REST) + Frontend HTML/CSS/JS**.
- [ ] Estudo de UX: definir layout, paleta de cores, tipografia, responsividade e micro-animações.
- [ ] Recriar as 4 abas do dashboard (RELINTs, Participantes, Municípios, Crimes) com design premium.
- [ ] Manter o app desktop (CustomTkinter) para monitoramento de pastas (ETL local).

### ETAPA 2 — Acesso Online Seguro (Cloudflare Tunnel + E2EE)
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

## 4. Decisões Descartadas
- ~~**Extração de Fotos de Participantes (Rostos):**~~ Descartada por complexidade excessiva na associação heurística de imagens a indivíduos. Imagens extraídas dos PDFs vão todas para a galeria geral do RELINT.
