# Diretório `data/`

Esta pasta é responsável por armazenar os **dados locais persistes** da aplicação.

## 💾 Arquivos Contidos:

* **`relints.json`:** Banco de dados NoSQL embutido em arquivo JSON gerenciado pelo **TinyDB**. Armazena as entidades de boletins de ocorrência/RELINTs estruturados (`RelintReport`), incluindo metadados extraídos pela IA e edições manuais efetuadas no Dashboard.

* **`processed_registry.json`:** Registro em JSON do histórico de processamento dos PDFs por regra. Evita que o sistema reprocesse desnecessariamente arquivos que já foram analisados.

> ⚠️ **Nota de Segurança:** Por conter dados locais extraídos dos relatórios de inteligência, esta pasta é tratada estritamente em ambiente local e não deve ser versionada com dados sensíveis de produção.
