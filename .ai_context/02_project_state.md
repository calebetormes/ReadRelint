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

## 2. O que está sendo feito agora
- [x] Refatoração da pasta `.ai_context` para reduzir redundância e aglutinar arquivos em um padrão de 3 documentos.

## 3. Backlog e Tarefas Futuras
- [ ] **Exportação de Relatórios Estruturados:** Criar botões no dashboard para exportar o Dossiê e os Casos Selecionados para Excel, CSV ou PDF.
- [ ] **Extração de Fotos Específicas de Participantes (Rostos):** Evoluir a galeria geral do caso para recortar/associar rostos diretamente às entidades de pessoas e exibir no dossiê `Person`.
- [ ] **Grafos de Vínculos (Visualização Gráfica):** Adicionar um plot interativo (ex: `streamlit-agraph`) mostrando conexões em rede entre Pessoas e Relatórios.
- [ ] **Check de Hashes (SHA-256):** Hashing dos PDFs durante ingestão para que modificações posteriores do mesmo arquivo triggerem re-processamento automático.
