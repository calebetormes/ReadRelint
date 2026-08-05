# Arquitetura e Tech Stack

## Tecnologias Principais
- **Linguagem Base:** Python 3.10+
- **Leitura de PDF (Adapter):** `PyMuPDF` (fitz)
- **Motor de IA/NLP (Adapter):** `Ollama` local (executando modelos leves de instrução como Llama 3 ou Qwen 2.5 localmente para estruturar os dados e classificar semântica).
- **Banco de Dados (Adapter):** `TinyDB` (NoSQL serverless em arquivo JSON local).
- **Interface Desktop de Controle (UI):** `CustomTkinter` (gerencia monitoramento de pastas e console de status).
- **Interface Web de Relatórios e Curadoria (UI):** `Streamlit` (rodando em localhost).

## Contrato de Dados (Domínio)
A Entidade gerada no domínio (`IncidentReport`) e salva no TinyDB (`relints.json`) possui a seguinte estrutura de campos:
- `source_file`: Nome do arquivo PDF de origem.
- `modification_date_history`: Sequência/histórico de datas de alteração do arquivo.
- `subject`: Texto extraído do campo ASSUNTO da seção introdutória do RELINT.
- `main_fact`: O evento central do relatório deduzido do assunto/contexto.
- `relint_type`: Classificação estrita em Enum (`Ocorrência`, `Disk Denúncia`, `Resposta a PB`, `Outros`).
- `bm_group`: Enquadramento em Enum restrito (`Roubo a Estabelecimento`, `Roubo a Residência`, etc).
- `location_types`: Lista identificando os tipos de local do fato.
- `address`: Endereço completo mencionado no fato.
- `coordinates`: Coordenadas geográficas, se presentes.
- `content`: Histórico literal e integral do arquivo, extraído pós-corte limpo (ex: após a seção ANEXOS).
- `summary`: Resumo em um parágrafo do fato.
- `user_edited`: Flag que indica edição manual.
- `participants` (lista de objetos, `Participant`):
  - `name`: Nome completo da pessoa.
  - `nickname`: Alcunha, apelido ou vulgo.
  - `document`: CPF ou RG.
  - `background`: Antecedentes criminais citados.
  - `participation_type`: Enum (`Vítima`, `Testemunha`, `Acusado`, `Parte da Guarnição`).

## Pipeline de Processamento de ETL
1. **Fase 1: Extração e Limpeza**
   - Monitoramento/Varredura de diretório via `watchdog` ou scan manual.
   - Extração do texto completo do PDF usando PyMuPDF.
   - Limpeza automatizada de cabeçalhos institucionais repetitivos e salvaguardas de sigilo para otimizar o prompt.
2. **Fase 2: Processamento Cognitivo (Ollama)**
   - O texto limpo é enviado ao Ollama com instruções estritas para extração estruturada de metadados em JSON (Assunto, Data, Participantes, Resumo e Grupo BM).
   - O texto original é mantido intacto no campo `content`.
3. **Fase 3: Persistência**
   - O objeto estruturado é validado pela entidade do domínio (`RelintReport`) usando Pydantic.
   - Salvamento no repositório TinyDB local, checando duplicidade de arquivo de origem.
4. **Fase 4: Cruzamento e Exibição (Dashboard)**
   - O Dashboard Streamlit lê a base de dados.
   - Realiza o cruzamento de vínculos (cross-referencing) de participantes: verifica se um mesmo documento/nome/alcunha aparece em outros arquivos processados e cria badges/tags de alerta de vínculo.
   - Fornece formulário completo para alteração de qualquer campo da entidade com salvamento persistente.

## Estrutura de Armazenamento de Dados (/data/)
A persistência local é dividida em arquivos JSON dedicados (TinyDB):
1. **`relints.json`**: Histórico completo e literal de relatórios, resumos e classificações.
2. **`participants.json`**: Cadastro unificado de pessoas de interesse, alcunhas, documentos e lista de RELINTs vinculados (`linked_relints`).
3. **`municipalities.json`**: Registro consolidado de municípios, estatísticas criminais locais e relatórios vinculados (`linked_relints`).
4. **`processed_registry.json`**: Registro de controle para prevenção de reprocessamento.

## Estrutura de Pastas Oficial
- `/data/` (Armazenamento dos bancos `.json`: `relints.json`, `participants.json`, `municipalities.json`, `processed_registry.json`)
- `/src/domain` (Entidades `IncidentReport`, `Person`, `Municipality` e regras de domínio em Python puro)
- `/src/ports` (Interfaces de `IFileParser`, `ILlmProcessor`, `IDatabaseRepo`, `IProcessedRegistry`)
- `/src/adapters` (Implementações concretas dos adaptadores)
- `/src/application` (Serviço orquestrador `EtlService`)
- `/src/presentation/desktop` (Painel em CustomTkinter para iniciar/parar monitoramento)
- `/src/presentation/web_dashboard` (Painel Streamlit para visualização, cruzamento, dossiês e edição)
