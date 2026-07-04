# Arquitetura e Tech Stack

## Tecnologias Principais
- **Linguagem Base:** Python 3.10+
- **Leitura de PDF (Adapter):** `PyMuPDF` (fitz)
- **Motor de IA NLP (Adapter):** `Ollama` local (forçando saída estruturada via parâmetro `format='json'`, temperatura baixa).
- **Banco de Dados (Adapter):** `TinyDB` (NoSQL serverless, armazenado em arquivo JSON local. Sem MongoDB ou servidores externos).
- **Interface Desktop de Controle (UI):** `CustomTkinter`
- **Interface Web de Relatórios (UI):** `Streamlit` (rodando em localhost)

## Contrato de Dados (Domínio)
A Entidade gerada pela IA e salva no TinyDB terá a seguinte estrutura em inglês (conforme regra de idioma do código):
- `incident_type` (string)
- `incident_time` (string ISO 8601 ou null)
- `address`: `street`, `number`, `neighborhood`, `city`
- `participants`: lista de objetos com `name` e `role`
- `vehicles`: lista de objetos com `plate`, `model`, `color`
- `attending_officer` (string)
- `history_summary` (string)

## Estrutura de Pastas Oficial
- `/data/logs` e `/data/temp`
- `/src/domain` (Entidades e Casos de Uso em Python puro - Código em Inglês)
- `/src/ports` (Interfaces de `IFileParser`, `ILlmProcessor`, `IDatabaseRepo` - Código em Inglês)
- `/src/adapters` (Implementações: `pdf_reader.py`, `ollama_client.py`, `tinydb_repo.py` - Código em Inglês)
- `/src/presentation/desktop` (Telas do CustomTkinter para selecionar a pasta)
- `/src/presentation/web_dashboard` (Telas do Streamlit para ler o TinyDB local)
- `/src/infrastructure` (`folder_watcher.py` e injeção de dependência)
