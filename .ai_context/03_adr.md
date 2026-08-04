# Registro de Decisões de Arquitetura (ADR)

## [ADR-001] Adoção da Clean Architecture
- **Decisão:** Isolamento da lógica de negócios usando Ports e Adapters para facilitar a substituição de ferramentas (bancos, parsers de PDF) sem quebrar o core.

## [ADR-002] Processamento de NLP Local (Soberania de Dados)
- **Decisão:** Uso do Ollama rodando localmente na máquina servidora/cliente.
- **Motivo:** Boletins de ocorrência contêm PII e dados sensíveis que não podem ser enviados para APIs de nuvem por questões legais (LGPD).

## [ADR-003] Interface Híbrida (Múltiplos Delivery Mechanisms)
- **Decisão:** Uso de CustomTkinter para controle do sistema (seleção de pastas via OS) e Streamlit para visualização dos dados do banco.
- **Motivo:** Bibliotecas desktop nativas são ideais para interagir com o sistema de arquivos do Windows, mas são ineficientes para criar dashboards e tabelas dinâmicas, onde o Streamlit brilha.

## [ADR-004] TinyDB como Banco de Dados Embutido
- **Decisão:** Uso do TinyDB, descartando bancos baseados em servidor (como MongoDB).
- **Motivo:** Manter a estrutura NoSQL orientada a documentos (essencial para armazenar as saídas JSON do LLM), garantindo que o software seja totalmente portátil e fácil de instalar.

## [ADR-005] Adoção do Pytest para Testes Automatizados e Mocks
- **Decisão:** Adoção do `pytest` como o framework oficial de testes.
- **Motivo:** Assegurar a integridade do domínio Pydantic e o comportamento de comunicação externa dos adaptadores. O uso de fixtures (`tmp_path`) e mocks (`unittest.mock`) garante isolamento total dos testes sem depender de instâncias externas de IA ou criar arquivos de banco/PDF permanentes no repositório.

## [ADR-006] Simplificação do Pipeline e Contrato de Dados
- **Decisão:** Unificação e simplificação da entidade `IncidentReport` para exigir apenas os campos `source_file` e o resumo textual `content`. Todos os outros campos complexos (como endereço mapeado por objeto, participantes e veículos) foram marcados como opcionais/legados.
- **Motivo:** Aumentar a resiliência e estabilidade do processamento por IA, reduzindo a complexidade de validações que geravam erros de parsing em documentos com estruturas heterogêneas. A simplificação também permite que registros salvos com schemas diferentes coexistam sem falhar na leitura do TinyDB.

## [ADR-007] Transição de LLM (Ollama) para QA Extrativo Local (Transformers)
- **Decisão:** Substituição do cliente Ollama por um pipeline local de Question Answering (QA) extrativo utilizando a biblioteca `transformers` e um modelo BERT específico para pt-BR.
- **Motivo:** Reduzir a dependência de um serviço externo rodando em paralelo (Ollama background service), diminuir o consumo de recursos computacionais (memória RAM/VRAM), permitir execução ágil em CPU e obter respostas direcionadas diretamente do texto original, eliminando alucinações comuns em LLMs gerativas.

## [ADR-008] Priorização de Edição Manual do Usuário
- **Decisão:** Criação de métodos no registro central de histórico (`JsonProcessedRegistry`) para persistir modificações de "Fato Principal" efetuadas pelos usuários e priorizá-las sobre as extrações da IA/Regex em qualquer reprocessamento futuro.
- **Motivo:** Garantir que o trabalho de curadoria manual do usuário tenha precedência absoluta e não seja sobrescrito se o sistema reanalisar os PDFs.

## [ADR-009] Processamento Completo de Documentos Sem Descarte
- **Decisão:** Remoção dos filtros de descarte no pipeline do ETL (pré-filtro e pós-filtro), transferindo a responsabilidade de exclusão e filtragem de tipos de fatos para a interface do usuário (Dashboard Streamlit via multiselect).
- **Motivo:** Evitar a perda de boletins de ocorrência legítimos por falsos negativos de classificação automatizada, mantendo uma base de dados completa de todas as leituras e permitindo visualização sob demanda.

## [ADR-010] Retorno ao Ollama para Extração Estruturada no Administrador de RELINTs
- **Decisão:** Retorno ao uso do adaptador `Ollama` com LLM local para extração estruturada multicampos, definindo um novo schema estruturado (`RelintReport`) para a aplicação.
- **Motivo:** Heurísticas puras ou QA extrativo local simples não possuem flexibilidade suficiente para identificar participantes dispersos no texto (capturando correlações entre nomes, alcunhas e CPFs), resumir de forma coesa a ocorrência em um único parágrafo e classificar o fato em categorias semânticas complexas como "Grupo BM" (Roubos, Furtos, Homicídios, Outros) com alta precisão. O uso do Ollama local em modo de saída estruturada (JSON) resolve esses pontos mantendo a segurança dos dados.
