# Guia de Reconstrução do Sistema: Prompts de Inteligência Artificial

Este diretório contém o plano e os **prompts estruturados de IA** necessários para reconstruir o sistema de administração e análise de RELINTs do zero em outro repositório.

A arquitetura foi dividida em **Backend** e **Frontend** para garantir portabilidade e facilitar a manutenção.

---

## 🏗️ Divisão Backend & Frontend

1. **Backend (API + ETL):**
   * Processa arquivos PDF físicos usando `PyMuPDF`.
   * Realiza chamadas locais e determinísticas de inteligência artificial via `Ollama`.
   * Salva os resultados no banco de dados NoSQL embutido `TinyDB`.
   * Expõe endpoints RESTful com `FastAPI`.
   * Executa monitoramento de pastas usando a biblioteca `watchdog`.

2. **Frontend (Dashboard):**
   * Interface de usuário rodando em `Streamlit`.
   * Utiliza um design de **tela inteira Split-Screen (Master-Detail)** altamente intuitivo.
   * Realiza cruzamento dinâmico de vínculos de envolvidos em tempo real.
   * Disponibiliza formulários para edição manual de dados sugeridos pela IA.

---

## 🛣️ Como usar os Prompts de IA

Envie os prompts contidos nesta pasta consecutivamente para o seu assistente de programação (Gemini, Claude, GPT, etc.), esperando que ele conclua cada etapa antes de avançar para a próxima:

### 🚀 [Etapa 1] Criar a API Backend, Persistência Local e Parsers de PDF
* **Objetivo:** Subir o core do backend (FastAPI), banco embutido (TinyDB) e leitura de texto em PDF.
* **Arquivo do Prompt:** [prompt_stage1_backend.md](file:///d:/DEV26/ReadRelint/.ai_context/new_implement/prompt_stage1_backend.md)

### 🧠 [Etapa 2] Motor de Extração Inteligente Ollama com Auto-Recuperação
* **Objetivo:** Adicionar a integração HTTP com o Ollama local, a estrutura do prompt JSON determinístico e o mecanismo de auto-recuperação de falhas de modelo (Self-Healing).
* **Arquivo do Prompt:** [prompt_stage2_ollama.md](file:///d:/DEV26/ReadRelint/.ai_context/new_implement/prompt_stage2_ollama.md)

### 💻 [Etapa 3] Dashboard Split-Screen, Cruzador de Vínculos e Watcher
* **Objetivo:** Criar a interface Streamlit em Master-Detail, a aba de histórico literal, os forms de edição interativos com persistência e o monitorador de diretórios em background.
* **Arquivo do Prompt:** [prompt_stage3_frontend.md](file:///d:/DEV26/ReadRelint/.ai_context/new_implement/prompt_stage3_frontend.md)
