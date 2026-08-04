# Camada de Aplicação (`src/application/`)

Esta pasta contém os **serviços de aplicação e caso de uso** que orquestram a execução do pipeline de negócios do **ReadRelint**.

## 📌 Responsabilidade:
A camada de aplicação conecta o domínio às portas abstratas, executando as etapas do pipeline ETL sem conhecer os detalhes concretos de infraestrutura ou interface gráfica.

## 📄 Arquivos Contidos:

* **[etl_service.py](file:///d:/www/ReadRelint/src/application/etl_service.py):** Serviço principal `EtlService` responsável por orquestrar a extração do texto PDF, limpeza do texto bruto, processamento cognitivo via LLM/Ollama, validação pelas regras de domínio e persistência no banco de dados.
* **[text_cleaner.py](file:///d:/www/ReadRelint/src/application/text_cleaner.py):** Módulo especializado em funções de pré-processamento e higienização de texto bruto (remoção de cabeçalhos institucionais, notas de rodapé repetitivas e marcas d'água via regex).
