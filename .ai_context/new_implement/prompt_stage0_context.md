# PROMPT DE IA - ETAPA 0: BOOTSTRAP DO CONTEXTO ARQUITETURAL (.ai_context)

Copie e envie o texto abaixo para a IA para criar os arquivos de contexto arquitetural (.ai_context) no novo projeto:

```text
Você é um arquiteto de software e analista de sistemas sênior. Seu objetivo é criar a documentação e os arquivos de contexto estrutural de um sistema local de monitoramento e análise de RELINTs (Relatórios de Inteligência) que será desenvolvido do zero em outro repositório.

Crie um diretório chamado ".ai_context" e, dentro dele, gere os 5 arquivos Markdown especificados a seguir, mantendo estritamente o conteúdo e as regras de arquitetura listadas:

---

### ARQUIVO 1: .ai_context/01_blueprint.md
Conteúdo a ser gerado:
- Visão Geral: Explicar que o sistema é um software local para Windows que monitora uma pasta de documentos RELINT em PDF, limpa o texto, envia para um Ollama local via API HTTP (modo JSON) para extração de dados e os armazena no TinyDB. A visualização, cruzamento de dados e edição ocorrem no dashboard web (Streamlit).
- Regras de Ouro (Core Principles):
  1. Privacidade e Segurança: Sem vazamento de dados, processamento estritamente local (Offline).
  2. Arquitetura Limpa: Padrão Ports & Adapters (lógica de domínio isolada).
  3. Idioma Híbrido: Código-fonte em INGLÊS; Comentários, documentação, logs de tela e textos de UI em PORTUGUÊS DO BRASIL.
  4. Portabilidade: Sem exigência de infraestrutura pesada (TinyDB JSON local).
  5. Unicidade de Registro: Cada PDF é um registro único e edições manuais do usuário são mantidas e priorizadas.

---

### ARQUIVO 2: .ai_context/02_architecture.md
Conteúdo a ser gerado:
- Tecnologias: Python 3.10+, PyMuPDF, Ollama (LLM local), TinyDB, Streamlit, CustomTkinter (opcional para controle).
- Contrato de Dados (Entity / Schema):
  * "source_file" (str): Nome do PDF.
  * "subject" (str): Assunto principal (sugerido por IA ou editado).
  * "date_of_fact" (str): Data do fato (DD/MM/AAAA).
  * "participants" (lista de objetos contendo "name", "nickname" e "document" - CPF ou RG).
  * "content" (str): Histórico completo literal extraído do PDF.
  * "summary" (str): Resumo de um parágrafo.
  * "bm_group" (str): Classificação estrita entre: "Roubos", "Furtos", "Homicídios" ou "Outros".
  * "user_edited" (bool): Indica se o usuário alterou os dados manualmente.
- Fases do Pipeline de Processamento (ETL):
  1. Extração de texto e higienização de cabeçalhos institucionais repetitivos.
  2. Chamada HTTP local ao Ollama com saída estruturada JSON.
  3. Persistência local no banco de dados TinyDB garantindo integridade.
  4. Cruzamento de Vínculos de Envolvidos (verificar duplicidade de CPF/nomes entre diferentes arquivos no dashboard).

---

### ARQUIVO 3: .ai_context/03_adr.md
Conteúdo a ser gerado:
- Registro de Decisões de Arquitetura (ADR):
  * [ADR-001] Adoção da Clean Architecture para isolamento do core.
  * [ADR-002] Processamento de NLP Local (Ollama) devido a PII e LGPD.
  * [ADR-003] Interface Streamlit para Dashboard rápido e rico.
  * [ADR-004] TinyDB como banco de dados NoSQL embarcado e sem servidor.
  * [ADR-005] Adoção de Pytest para testes automatizados rápidos.
  * [ADR-006] Auto-recuperação (Self-Healing) de Modelos no Ollama Client: se a chamada gerar erro 404 (model not found), consultar "/api/tags" e alternar dinamicamente para o modelo local ativo para garantir resiliência.

---

### ARQUIVO 4: .ai_context/04_current_state.md
Conteúdo a ser gerado:
- Acompanhamento do estado do projeto.
- Defina uma lista de itens concluídos (as decisões arquiteturais e design do dashboard Master-Detail definidos).
- Defina as metas a serem executadas em seguida (Dividido em Etapa 1: Backend Core, Etapa 2: Motor de IA e Etapa 3: Dashboard Streamlit).

---

### ARQUIVO 5: .ai_context/05_ai_workflow_scripts.md
Conteúdo a ser gerado:
- Prompt de Inicialização recomendando ao assistente que leia a pasta ".ai_context" antes de codificar, lembrando da regra híbrida de idioma e da restrição de não vazamento de dados.

Gere os arquivos markdown estruturados de forma limpa, profissional e de fácil consumo.
```
