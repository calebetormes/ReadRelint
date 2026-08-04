# Arquitetura e Tech Stack

## Tecnologias Principais
- **Linguagem Base:** Python 3.10+
- **Leitura de PDF (Adapter):** `PyMuPDF` (fitz)
- **Motor de IA/NLP (Adapter):** `Ollama` local (executando modelos leves de instrução como Llama 3 ou Qwen 2.5 localmente para estruturar os dados e classificar semântica).
- **Banco de Dados (Adapter):** `TinyDB` (NoSQL serverless em arquivo JSON local).
- **Interface Desktop de Controle (UI):** `CustomTkinter` (gerencia monitoramento de pastas e console de status).
- **Interface Web de Relatórios e Curadoria (UI):** `Streamlit` (rodando em localhost).

## Contrato de Dados (Domínio)
A Entidade gerada no domínio (`RelintReport`) e salva no TinyDB possui a seguinte estrutura de campos:
- `source_file` (string, obrigatório): Nome do arquivo PDF de origem.
- `subject` (string, obrigatório): Assunto Principal sugerido pela IA ou editado pelo usuário.
- `date_of_fact` (string, obrigatório): Data do Fato identificada pela IA ou corrigida.
- `participants` (lista de objetos, obrigatório): Lista de pessoas citadas, onde cada elemento contém:
  - `name` (string): Nome completo da pessoa.
  - `nickname` (string): Alcunha ou vulgo.
  - `document` (string): CPF ou RG.
- `content` (string, obrigatório): Histórico completo literal igual ao contido no RELINT (extraído diretamente do PDF).
- `summary` (string, obrigatório): Resumo de um parágrafo sobre do que se trata o RELINT, gerado pela IA.
- `bm_group` (string, obrigatório): Enquadramento do fato em um dos grupos pré-definidos: `Roubos`, `Furtos`, `Homicídios`, `Outros`.
- `user_edited` (boolean, obrigatório): Flag que indica se o registro foi editado manualmente pelo usuário no Dashboard.

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

## Estrutura de Pastas Oficial
- `/data/` (Armazenamento dos bancos `.json` e histórico de processamento)
- `/src/domain` (Entidade `RelintReport` e regras de domínio em Python puro)
- `/src/ports` (Interfaces de `IFileParser`, `ILlmProcessor`, `IDatabaseRepo`, `IProcessedRegistry`)
- `/src/adapters` (Implementações concretas dos adaptadores)
- `/src/application` (Serviço orquestrador `EtlService`)
- `/src/presentation/desktop` (Painel em CustomTkinter para iniciar/parar monitoramento)
- `/src/presentation/web_dashboard` (Painel Streamlit para visualização, cruzamento e edição)
