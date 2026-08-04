# Camada de Portas (`src/ports/`)

As **Portas (Ports)** definem os contratos abstratos e interfaces que desacoplam a camada de domínio e aplicação de qualquer dependência tecnológica concreta.

## 📌 Papel na Arquitetura:
Seguindo o padrão *Ports and Adapters*, o domínio e os serviços utilizam estas interfaces abstratas sem saber qual ferramenta concreta (TinyDB, PostgreSQL, PyMuPDF, Ollama, OpenAI) está realizando o trabalho de fato.

## 📄 Arquivos Contidos:

* **[file_parser.py](file:///d:/www/ReadRelint/src/ports/file_parser.py):** Interface `IFileParser` para leitura e extração de texto a partir de arquivos em disco.
* **[llm_processor.py](file:///d:/www/ReadRelint/src/ports/llm_processor.py):** Interface `ILlmProcessor` para processamento semântico e extração estruturada de dados usando modelos de linguagem (IA).
* **[database_repo.py](file:///d:/www/ReadRelint/src/ports/database_repo.py):** Interface `IDatabaseRepo` para persistência, consulta e atualização de registros de incidentes/RELINTs.
* **[processed_registry.py](file:///d:/www/ReadRelint/src/ports/processed_registry.py):** Interface `IProcessedRegistry` para consulta e gravação do histórico de arquivos processados.
