# Administrador de RELINTs (Ollama)

Este projeto é um software local para Windows desenvolvido para monitorar e processar relatórios de inteligência policial e boletins de ocorrência (**RELINTs**) em formato PDF.

## 🚀 Principais Funcionalidades
* **Processamento Cognitivo Local (Offline):** Utiliza LLMs locais rodando via **Ollama** (ex: `llama3.1`) para extração estruturada de dados (envolvidos, vulgos, documentos, assunto, resumo e enquadramento em grupos BM).
* **Zero Envio para Nuvem:** Garante sigilo e privacidade total, processando 100% dos dados na máquina local.
* **Monitoramento Automático de Pastas:** Observa diretórios configurados via `watchdog` para processar automaticamente novos arquivos PDF adicionados.
* **Dashboard Interativo (Streamlit):** Interface web com modo Split Screen (Master-Detail) para busca rápida, edição manual persistente em TinyDB e **Cruzamento de Vínculos (Cross-Referencing)** de participantes comuns entre diferentes relatórios em tempo real.
* **Painel Desktop (CustomTkinter):** Console desktop para gerenciar o monitoramento e acompanhar os logs de processamento.

## 🏗️ Arquitetura e Estrutura
O projeto adota rigorosamente o padrão **Clean Architecture (Ports & Adapters)**. Para entender a estrutura física de arquivos e diretórios:
* 📄 **[Documentação de Estrutura (.ai_context/07_structure.md)](file:///.ai_context/07_structure.md)**
* 🌐 **[Visualizador Gráfico Interativo (structure_viewer.html)](file:///structure_viewer.html)**

## 📜 Regra de Idioma do Projeto
* **Código-fonte:** Estritamente em **Inglês** (nomes de variáveis, funções, classes, arquivos, chaves JSON).
* **Documentação, Comentários, Logs e UI:** Estritamente em **Português do Brasil (pt-BR)**.
