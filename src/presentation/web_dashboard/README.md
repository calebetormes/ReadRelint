# Dashboard Web (`src/presentation/web_dashboard/`)

Esta pasta contém o **Dashboard Web interativo de curadoria e inteligência**.

## 📌 Tecnologia Utilizada:
* **Streamlit:** Framework Python para construção rápida de aplicações web interativas voltadas para análise de dados.

## 📄 Arquivos Contidos:

* **[dashboard_app.py](file:///d:/www/ReadRelint/src/presentation/web_dashboard/dashboard_app.py):** Interface Web em tela inteira (Split Screen / Master-Detail).
  * **Painel Esquerdo (Navegação Master):** Lista de cards dos relatórios por arquivo, assunto e enquadramento de Grupo BM (Roubos, Furtos, Homicídios, Outros).
  * **Painel Direito (Detalhes & Curadoria):** Abas com o Resumo da IA, histórico literal original, lista de envolvidos, formulário unificado de edição com salvamento persistente no TinyDB e **Cruzamento de Vínculos (Cross-Referencing)** em tempo real.
