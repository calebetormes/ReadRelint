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
- [x] Registro formal das decisões [ADR-011] (repositório unificado e taxonomia), [ADR-012] (bancos dedicados para Participantes e Municípios) e [ADR-013] (Exclusão de PMs e isolamento da transcrição).
- [x] **Refatoração Estrutural (Taxonomia e Multi-bancos):**
  - [x] Definição de 12 campos rígidos e *Enums* (RelintType, BmGroup, ParticipationType) na entidade `IncidentReport`.
  - [x] Criação das entidades `Person` e `Municipality` no domínio para cadastros unificados.
  - [x] Implementação de `TinyDbPersonRepo` e `TinyDbMunicipalityRepo` e integração com `EtlService` (Upsert logic).
  - [x] Refatoração de `OllamaClient` para enviar o JSON Schema do Pydantic dinamicamente à IA.
  - [x] Aprimoramento da limpeza de texto (`text_cleaner.py`) para isolar blocos de texto a partir da chave "ANEXOS:".
  - [x] **Ajustes Finais de Qualidade do ETL:**
    - [x] Remoção do campo `content` da consulta LLM, atribuindo a transcrição integral diretamente via código Python/Regex.
    - [x] Tratamento de fallback de sanitização para o campo `summary`.
    - [x] **Redesenho do Dashboard Streamlit em 4 Abas Especializadas:**
  - [x] `📄 RELINTs (Edição)`: Interface Split Screen (Master-Detail) com busca, atalhos de seleção, histórico literal limpo, resumo e formulário de edição TinyDB.
  - [x] `👤 Participantes`: Dossiê de pessoas com apelidos/vulgos, documentos (CPF/RG), avatar e alerta de vínculos cruzados entre múltiplos RELINTs.
  - [x] `🗺️ Municípios`: Mapeamento de mancha territorial por cidade, ranking de incidência criminal e relatórios associados.
  - [x] `🚨 Crimes (Grupo BM)`: Painel estatístico com gráfico de barras por enquadramento criminal (Roubos, Furtos, Tráfico, Homicídios, etc.).
- [x] **Sanitização de Avisos Legais e Preservação de Cabeçalhos:**
  - [x] Remoção automatizada via Regex de avisos administrativos/disclaimers (`DOCUMENTO PREPARATÓRIO – ACESSO RESTRITO`, Lei 12.527/2011, Lei 9.883/1999, `Página X de Y`).
  - [x] Preservação integral da tabela introdutória do RELINT (`RELATÓRIO DE INTELIGÊNCIA Nº...`, `ASSUNTO...`, `ORIGEM...`, `DIFUSÃO...`, `ANEXOS:...`).
- [x] **Extração Espacial e Geolocalização de 3 Níveis:**
  - [x] Extração de `time_of_fact`, `municipality`, `street`, `number`, `neighborhood`, `map_url` e `coordinates`.
  - [x] Geração automática de links do Google Maps via busca de endereço estruturado em fallback.
  - [x] Sistema de cores e alertas de precisão garantidos no Dashboard (Verde Esmeralda para Coordenadas Exatas, Azul Cyan para Link Citado e Laranja Âmbar para Endereço Gerado).
  - [x] Resiliência de renderização HTML (`clean_html`) evitando blocos de código indesejados no Streamlit.
- [x] Registro formal das decisões [ADR-011] a [ADR-014].

## O que está sendo feito agora:
- [x] Atualização de todos os artefatos de documentação de contexto em `.ai_context`.

## Próximos Passos:
- [ ] Atualizar os testes unitários em `tests/` para corresponder à nova taxonomia, aos *Enums*, novos repositórios e funções de geolocalização.
- [ ] Implementar a extração automática de fotos dos quadros de participantes dos PDFs via PyMuPDF e vinculá-las aos Dossiês de Pessoas (`Person`).
- [ ] Criar relatórios de exportação em PDF/Docx dos Dossiês Consolidados de Pessoas e Municípios.

