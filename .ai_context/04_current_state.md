# Estado Atual do Projeto

## O que já foi implementado:
- [x] Definição da stack (Python, TinyDB, Ollama local, PyMuPDF, CustomTkinter, Streamlit).
- [x] Configuração da Clean Architecture (Portas, Adaptadores, Domínio, Aplicação e Apresentação).
- [x] Implementação do leitor de PDF (`PyMuPDF`) e limpeza de texto bruto via regex.
- [x] Criação do painel desktop em CustomTkinter para monitorar diretórios via `FolderWatcher`.
- [x] Criação de testes automatizados com `pytest` para repositórios e leitores de PDF (36 testes passando com sucesso).
- [x] Registro centralizado de histórico de processamento (`processed_registry.json`) para evitar reprocessamentos desnecessários.
- [x] **Migração para o Administrador de RELINTs usando Ollama:**
  - [x] Criação da nova regra `RelintRule` e refatoração da entidade `IncidentReport` (incluindo `subject`, `date_of_fact`, `participants`, `content` literal, `summary`, `bm_group` e propriedades de compatibilidade retroativa).
  - [x] Implementação do `OllamaClient` com extração JSON estruturada local, com mecanismo inteligente de auto-recuperação (Self-Healing) que busca automaticamente os modelos de IA disponíveis na máquina (ex: `llama3.1:latest`) em caso de erros de modelo não encontrado (404).
  - [x] Ajuste do `EtlService` para extrair e mapear os novos campos com histórico original completo e controle de edições manuais.
  - [x] Ajuste do `main_controller.py` e componentes de UI desktop (`report_tab`, `control_panel_tab`) para suportar a nomenclatura e fluxo do administrador de RELINTs.
  - [x] Redesenho total do **Dashboard Streamlit em modo Split Screen (Master-Detail)** de tela inteira:
    - [x] Navegação rápida na esquerda com cards modernos dos arquivos, assuntos e enquadramentos de Grupo BM (Roubos, Furtos, Homicídios, Outros).
    - [x] Abas de detalhes na direita mostrando Resumo da ocorrência, histórico literal e envolvidos.
    - [x] Mecanismo de **Cruzamento de Vínculos (Cross-Referencing)** em tempo real sinalizando envolvidos comuns entre diferentes arquivos.
    - [x] Formulário unificado em grid para edição de qualquer campo do caso e participantes com persistência em TinyDB.

## O que está sendo feito agora:
- [x] Atualização da documentação de contexto da aplicação finalizada.

## Próximos Passos:
- [ ] Monitoramento contínuo de novas melhorias de UX e suporte a relatórios analíticos de inteligência.
