# Arquitetura e Tech Stack

## Tecnologias Principais
- **Linguagem Base:** Python 3.10+
- **Leitura de PDF (Adapter):** `PyMuPDF` (fitz)
- **Motor de IA NLP (Adapter):** QA Extrativo local (Hugging Face `transformers` com modelo BERT adaptado para Português, ex: `pierreguillou/bert-large-cased-squad-v1.1-portuguese`).
- **Banco de Dados (Adapter):** `TinyDB` (NoSQL serverless, armazenado em arquivo JSON local. Sem MongoDB ou servidores externos).
- **Interface Desktop de Controle (UI):** `CustomTkinter`
- **Interface Web de Relatórios (UI):** `Streamlit` (rodando em localhost)
- **Visualizações e Gráficos:** `Plotly` (integrado ao dashboard)

## Contrato de Dados (Domínio)
A Entidade gerada pela IA e salva no TinyDB possui os seguintes campos principais:
- `source_file` (string, obrigatório): Nome do arquivo PDF de origem.
- `occurred_fact` (string, opcional): Fato ocorrido (natureza classificada ou editada).
- `clean_content` (string, opcional): Texto limpo e completo extraído do PDF.
- `user_edited` (boolean, padrão False): Indica se o fato foi modificado manualmente pelo usuário.
- `content` (string, opcional/legado): O conteúdo ou resumo formatado.
- *Campos Legados (opcionais para retrocompatibilidade):* `relint_number`, `subject`, `diffusion`, `attachment`, `incident_nature`, `incident_group`, `incident_type`, `incident_time`, `address`, `participants`, `vehicles`, `attending_officer`, `history_summary`.

## Pipeline de Processamento de IA Simplificado
A extração de dados foi consolidada para maximizar a velocidade e a confiabilidade de leitura local:
1. **Fase 1: Pré-processamento e Limpeza**
   - Extração do texto do arquivo PDF com PyMuPDF.
   - Limpeza automática via regex, removendo salvaguardas administrativas e assinaturas repetitivas.
2. **Fase 2: Extração e Resumo Estruturado**
   - Processamento do texto limpo pela LLM local para extrair o fato principal (gravado em formato estruturado no campo `content`).
3. **Fase 3: Persistência de Dados**
   - Armazenamento em TinyDB validando a unicidade de processamento do arquivo de origem (`source_file`).


## Estrutura de Pastas Oficial
- `/data/logs` e `/data/temp`
- `/src/domain` (Entidades e Casos de Uso em Python puro - Código em Inglês)
- `/src/ports` (Interfaces de `IFileParser`, `ILlmProcessor`, `IDatabaseRepo` - Código em Inglês)
- `/src/adapters` (Implementações: `pdf_reader.py`, `ollama_client.py`, `tinydb_repo.py` - Código em Inglês)
- `/src/presentation/desktop` (Telas do CustomTkinter para selecionar a pasta)
- `/src/presentation/web_dashboard` (Telas do Streamlit para ler o TinyDB local)
- `/src/infrastructure` (`folder_watcher.py` e injeção de dependência)
