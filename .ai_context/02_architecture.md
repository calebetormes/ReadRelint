# Arquitetura e Tech Stack

## Tecnologias Principais
- **Linguagem Base:** Python 3.10+
- **Leitura de PDF (Adapter):** `PyMuPDF` (fitz)
- **Motor de IA NLP (Adapter):** `Ollama` local (forçando saída estruturada via parâmetro `format='json'`, temperatura baixa).
- **Banco de Dados (Adapter):** `TinyDB` (NoSQL serverless, armazenado em arquivo JSON local. Sem MongoDB ou servidores externos).
- **Interface Desktop de Controle (UI):** `CustomTkinter`
- **Interface Web de Relatórios (UI):** `Streamlit` (rodando em localhost)
- **Visualizações e Gráficos:** `Plotly` (integrado ao dashboard)

## Contrato de Dados (Domínio)
A Entidade gerada pela IA e salva no TinyDB terá a seguinte estrutura em inglês (conforme regra de idioma do código):
- `incident_type` (string)
- `incident_time` (string ISO 8601 ou null)
- `address`: `street`, `number`, `neighborhood`, `city`
- `participants`: lista de objetos com `name` e `role`
- `vehicles`: lista de objetos com `plate`, `model`, `color`
- `attending_officer` (string)
- `history_summary` (string)
- `source_file` (string ou null)


## Pipeline de Processamento de IA em Fases

Para garantir alta precisão, mitigar alucinações e otimizar o uso da LLM local, a extração de dados dos RELINTs é realizada em quatro fases sucessivas:

1. **Fase 1: Extração de Metadados do Documento**
   - Extrai as informações de cabeçalho do documento: Número do RELINT, Assunto, Difusão e Anexos.
2. **Fase 2: Pré-processamento e Limpeza**
   - Extrai o texto bruto do PDF e aplica regras de limpeza automatizadas (ex: remoção de assinaturas e blocos administrativos finais via regex).
3. **Fase 3: Análise de Enquadramento e Segmentação**
   - A LLM analisa o texto limpo e classifica-o em grupos: *Ocorrências do AVANTE*, *Ocorrências Importantes fora do AVANTE* ou *Demais Fatos*. Divide os trechos textuais correspondentes a cada ocorrência identificada.
4. **Fase 4: Extração de Campos Específicos**
   - Para cada ocorrência segmentada na Fase 3, a LLM realiza uma extração detalhada e localizada dos campos estruturados (Endereço, Participantes, Veículos, Atendente e Resumo).


## Estrutura de Pastas Oficial
- `/data/logs` e `/data/temp`
- `/src/domain` (Entidades e Casos de Uso em Python puro - Código em Inglês)
- `/src/ports` (Interfaces de `IFileParser`, `ILlmProcessor`, `IDatabaseRepo` - Código em Inglês)
- `/src/adapters` (Implementações: `pdf_reader.py`, `ollama_client.py`, `tinydb_repo.py` - Código em Inglês)
- `/src/presentation/desktop` (Telas do CustomTkinter para selecionar a pasta)
- `/src/presentation/web_dashboard` (Telas do Streamlit para ler o TinyDB local)
- `/src/infrastructure` (`folder_watcher.py` e injeção de dependência)
