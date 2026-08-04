# PROMPT DE IA - ETAPA 2: MOTOR OLLAMA RESILIENTE E INTEGRAÇÃO ETL

Copie e envie o texto abaixo para a IA para iniciar a Etapa 2 da reconstrução:

```text
Você é um desenvolvedor especialista em Inteligência Artificial e integrações locais. Com base no backend estruturado na Etapa 1, precisamos criar a integração com o motor de NLP local (Ollama) e a rota de processamento de arquivos.

Escreva o código em Python seguindo estritamente as diretrizes abaixo:

1. CLIENTE OLLAMA E PROMPT STRUCTURING (OllamaClient):
- Crie uma classe "OllamaClient" para interagir com o serviço local do Ollama via requisições HTTP (usando a biblioteca "requests").
- Por padrão, tente conectar na URL "http://localhost:11434" e utilizar o modelo "llama3.1:latest".
- Use o endpoint "/api/generate" passando "format": "json" no payload para forçar a LLM a retornar exclusivamente um objeto JSON estruturado válido.
- Configure o parâmetro "temperature" em 0.0 nas opções para obter comportamento totalmente determinístico.
- Desenhe um prompt de instrução rigoroso que ordene que a IA retorne um JSON contendo exatamente as chaves:
  * "subject" (Assunto Principal): Frase curta de até 15 palavras resumindo o caso.
  * "date_of_fact" (Data do Fato): Data de ocorrência dos fatos em formato brasileiro DD/MM/AAAA. Se houver mais de uma data, extraia a data em que o crime/fato ocorreu. Se não encontrar nenhuma, retorne null.
  * "bm_group" (Grupo BM): Enquadramento semântico estrito do crime em um dos grupos: "Roubos", "Furtos", "Homicídios" ou "Outros".
  * "summary" (Resumo): Um resumo executivo do caso em exatamente um único parágrafo simples.
  * "participants" (Participantes): Lista contendo dicionários com "name" (Nome completo ou prenome), "nickname" (Alcunha/vulgo ou null) e "document" (RG/CPF apenas números ou null).

2. MECANISMO DE AUTO-RECUPERAÇÃO (Self-Healing de Modelos):
- Se a chamada HTTP retornar erro HTTP 404 (Not Found), significa que o modelo padrão solicitado ("llama3.1:latest") não está instalado/pulado no Ollama do usuário.
- Ao detectar um 404, o cliente deve automaticamente fazer uma chamada GET para o endpoint "/api/tags" do Ollama para consultar a lista de modelos atualmente baixados na máquina do usuário.
- Se houver qualquer modelo disponível na lista retornada, o cliente deve escolher o primeiro modelo encontrado (ex: "llama3:latest", "qwen2.5:7b", etc.), atualizar dinamicamente o parâmetro "model" e refazer a tentativa de processamento automaticamente.
- Se não houver nenhum modelo disponível ou a API falhar completamente, o cliente deve retornar um dicionário estruturado com dados genéricos de erro para não travar o pipeline.

3. ROTA DE PROCESSAMENTO NO FASTAPI (/relints/process):
- Crie um endpoint HTTP POST "/relints/process" que recebe a string de caminho físico para o arquivo PDF local.
- O endpoint deve orquestrar o pipeline de ETL:
  1. Verificar duplicidade: se o arquivo já foi processado no banco TinyDB, ignorar.
  2. Extrair o texto bruto do PDF usando o PdfReader (Etapa 1).
  3. Limpar o texto bruto com a função clean_relint_text (Etapa 1).
  4. Enviar o texto limpo para o OllamaClient estruturar e obter a resposta do modelo.
  5. Instanciar a entidade "IncidentReport", mantendo o texto original completo e limpo no campo "content" e inserindo os demais campos estruturados mapeados da IA.
  6. Salvar o registro final no banco local TinyDB e retornar sucesso com o status do processamento.

Implemente tratamentos de erro adequados para precaver falhas em PDFs protegidos, JSON corrompido retornado pela LLM, ou timeouts da chamada HTTP.
```
