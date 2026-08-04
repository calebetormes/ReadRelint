# Diretório `src/` (Código Fonte)

Este diretório contém todo o código-fonte da aplicação **ReadRelint**, organizado rigorosamente segundo os princípios da **Arquitetura Limpa (Ports and Adapters / Hexagonal Architecture)**.

## 📂 Organização das Camadas:

* **[domain/](file:///d:/www/ReadRelint/src/domain):** O coração da aplicação. Contém as entidades e regras de negócio puras em Python sem dependências de infraestrutura ou frameworks.
* **[ports/](file:///d:/www/ReadRelint/src/ports):** Define as interfaces abstratas (contratos) que o domínio exige do mundo externo (banco de dados, LLMs, leitores de arquivo, registros).
* **[adapters/](file:///d:/www/ReadRelint/src/adapters):** As implementações concretas dos contratos definidos nas portas (PyMuPDF, Ollama local, TinyDB, Registro JSON).
* **[application/](file:///d:/www/ReadRelint/src/application):** Camada de orquestração de caso de uso (Serviço de ETL e higienização de texto bruto).
* **[infrastructure/](file:///d:/www/ReadRelint/src/infrastructure):** Serviços globais de infraestrutura (monitoramento de pastas via `watchdog`).
* **[presentation/](file:///d:/www/ReadRelint/src/presentation):** Interfaces com o usuário (Painel Desktop em CustomTkinter e Dashboard Web em Streamlit).
