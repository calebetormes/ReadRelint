# Regras do Domínio (`src/domain/rules/`)

Esta pasta contém as definições das **regras de negócio especificas** para processamento e filtragem de relatórios de inteligência / boletins de ocorrência.

## 📄 Arquivos Contidos:

* **[base_rule.py](file:///d:/www/ReadRelint/src/domain/rules/base_rule.py):** Interface abstrata base `IncidentRule`, definindo a estrutura e contrato que qualquer regra de filtragem ou classificação de ocorrências deve implementar.
* **[relint_rule.py](file:///d:/www/ReadRelint/src/domain/rules/relint_rule.py):** Regra concreta `RelintRule` utilizada no escopo principal do projeto para processar todos os RELINTs sem descarte prévio de categorias.
* **[homicide_rule.py](file:///d:/www/ReadRelint/src/domain/rules/homicide_rule.py):** Regra especializada `HomicideRule` para filtragem direcionada a casos de homicídios e crimes violentos letais intencionais.
