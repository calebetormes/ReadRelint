# Camada de Domínio (`src/domain/`)

Esta pasta representa o **coração (Core Business Domain)** da aplicação **ReadRelint**.

## 📌 Princípios do Domínio:
* É escrito em **Python puro**.
* **NÃO possui dependências** de frameworks, bancos de dados, leitor de PDF, Ollama ou bibliotecas de UI.
* Define os modelos de dados centrais e as regras de negócio puras do sistema.

## 📄 Arquivos e Subdiretórios:
* **[entities.py](file:///d:/www/ReadRelint/src/domain/entities.py):** Contém as entidades e esquemas de dados da aplicação (`IncidentReport`, envolvidos/participantes e regras de validação via Pydantic).
* **[rules/](file:///d:/www/ReadRelint/src/domain/rules):** Diretório que reúne as regras de negócio para filtragem e extração de ocorrências.
