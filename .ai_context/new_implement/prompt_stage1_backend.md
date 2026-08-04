# PROMPT DE IA - ETAPA 1: BACKEND CORE, PERSISTÊNCIA E PARSERS

Copie e envie o texto abaixo para a IA para iniciar a Etapa 1 da reconstrução:

```text
Você é um desenvolvedor especialista em Python. Seu objetivo é criar a estrutura inicial e o backend de um sistema local de administração de RELINTs (Relatórios de Inteligência) utilizando Clean Architecture (Ports & Adapters).

Crie o código-fonte seguindo estritamente as especificações abaixo:

1. REQUISITOS TÉCNICOS:
- Use Python 3.10+ e Pydantic v2 para validação de dados.
- Utilize TinyDB como banco de dados embutido (NoSQL serverless baseado em JSON local).
- Use a biblioteca PyMuPDF (fitz) para extração de texto de arquivos PDF.
- Use FastAPI e Uvicorn para expor a API REST local.

2. ENTIDADES DE DOMÍNIO (Pydantic):
- Crie a classe "Participant" com os campos opcionais: "name" (str), "nickname" (str) e "document" (str) (que representará CPF ou RG).
- Crie a classe "IncidentReport" com os campos:
  * "source_file" (str, obrigatório): Nome do arquivo PDF original.
  * "subject" (str, opcional): Assunto principal do relatório.
  * "date_of_fact" (str, opcional): Data do fato.
  * "participants" (List[Participant]): Lista de envolvidos.
  * "content" (str, opcional): Histórico literal completo do PDF.
  * "summary" (str, opcional): Resumo de um parágrafo.
  * "bm_group" (str, opcional, default "Outros"): Classificação do crime ("Roubos", "Furtos", "Homicídios" ou "Outros").
  * "user_edited" (bool, default False): Indica se o usuário alterou os dados manualmente.
  * Adicione compatibilidade retroativa para mapear chaves antigas (como "main_fact" mapeando para "subject" e "clean_content" para "content") através de validadores de modelo antes da validação da classe.

3. ADAPTADOR DE BANCO DE DADOS (TinyDbRepo):
- Implemente uma classe de repositório para salvar, atualizar e consultar no TinyDB local.
- Métodos necessários:
  * "save(report: IncidentReport) -> str": Converte a entidade em dicionário e insere no banco, retornando o ID do documento.
  * "get_all() -> List[IncidentReport]": Retorna todos os registros cadastrados.
  * "get_by_source_file(filename: str) -> Optional[IncidentReport]": Busca pelo nome do arquivo de origem.
  * "exists_by_source_file(filename: str) -> bool": Retorna True se o arquivo já foi processado/cadastrado no banco.
  * "delete_by_source_file(filename: str) -> bool": Exclui registro pelo nome do arquivo.

4. EXTRATOR E HIGIENIZAÇÃO DE PDF (ETL Core):
- Implemente uma classe "PdfReader" que lê um arquivo PDF local e extrai todo o seu texto de forma literal usando PyMuPDF.
- Implemente uma função "clean_relint_text(text: str) -> str" usando expressões regulares (re) para limpar o texto bruto:
  * Remova salvaguardas institucionais administrativas como "RESTRITO", "CONFIDENCIAL", "SECRET" ou "RESERVADO".
  * Remova rodapés repetitivos de numeração de página no formato "Página X de Y" ou semelhantes.

5. API REST COM FASTAPI:
- Configure um servidor FastAPI local executando na porta 8000.
- Disponibilize os seguintes endpoints:
  * GET "/relints": Retorna a lista de todas as entidades "IncidentReport" salvas.
  * GET "/relints/{filename}": Retorna o relatório detalhado de um arquivo específico.
  * PUT "/relints/{filename}": Substitui/atualiza as informações do relatório no banco local (usado para salvar edições manuais).

Crie o código-fonte limpo, bem documentado em Português (com nomes de classes e variáveis em Inglês, respeitando o padrão híbrido) e modularizado de acordo com o Ports & Adapters.
```
