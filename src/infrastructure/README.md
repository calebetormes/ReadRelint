# Camada de Infraestrutura (`src/infrastructure/`)

Esta pasta contém os **serviços utilitários de infraestrutura** e integração com o sistema operacional.

## 📌 Responsabilidade:
Gerencia tarefas de nível de sistema de arquivos, concorrência, monitoramento de eventos de E/S e processos de segundo plano.

## 📄 Arquivos Contidos:

* **[folder_watcher.py](file:///d:/www/ReadRelint/src/infrastructure/folder_watcher.py):** Serviço de monitoramento continuo de diretórios baseado na biblioteca `watchdog`. Detecta a adição ou alteração de novos arquivos PDF na pasta monitorada e dispara o acionamento do pipeline ETL automaticamente.
