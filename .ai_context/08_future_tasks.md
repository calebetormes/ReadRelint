# Tarefas Futuras e Backlog (Ideias de Melhoria)

Este arquivo serve como repositório de ideias, discussões de arquitetura e futuras melhorias que foram levantadas durante as sessões de desenvolvimento.

---

## 1. Verificação de Alteração de Arquivos via Hash (SHA-256)
* **Objetivo:** Identificar se um arquivo PDF que já foi processado/descartado sofreu alguma modificação posterior no conteúdo e, caso positivo, forçar a sua releitura automática.
* **Proposta de Solução:**
  * Calcular o hash criptográfico SHA-256 do arquivo no momento do processamento.
  * Armazenar o hash no banco de histórico `processed_registry.json`.
  * Na varredura ou detecção do monitorador, comparar o hash atual com o armazenado. Se houver divergência, limpar a entrada e mandar o arquivo de volta à fila de leitura.

---

## 2. Visualização de Grafos de Vínculos no Dashboard
* **Objetivo:** Facilitar a análise de inteligência através da visualização gráfica das conexões entre participantes e relatórios.
* **Proposta de Solução:**
  * Usar bibliotecas como `streamlit-agraph` ou renderizações em HTML/D3 para plotar um grafo interativo de nós (Participantes e Arquivos) conectando-os por vínculos comuns (nomes ou documentos iguais).

---

## 3. Exportação de Relatórios Estruturados
* **Objetivo:** Permitir ao analista exportar as informações consolidadas no dashboard.
* **Proposta de Solução:**
  * Implementar botões de download para arquivos Excel (`.xlsx`), CSV ou PDF formatados com o resumo dos casos selecionados ou filtrados no painel.

---

## 4. Dossiê Unificado de Pessoas (UI Dashboard) [CONCLUÍDO]
* **Objetivo:** Criar uma tela dedicada no Streamlit para pesquisar e visualizar a ficha completa de uma pessoa.
* **Status:** Implementado na Aba 2 (`👤 Participantes`) do Dashboard Streamlit com cartões de dossiê, avatares, apelidos, documentos e cross-referencing de vínculos.

---

## 5. Mancha Criminal Territorial (UI Dashboard) [CONCLUÍDO]
* **Objetivo:** Criar uma visualização agregada da distribuição dos RELINTs por município.
* **Status:** Implementado na Aba 3 (`🗺️ Municípios`) do Dashboard Streamlit com estatísticas por cidade, ranking de incidência e mancha espacial.


---

## 6. Extração e Galeria de Fotos dos Participantes
* **Objetivo:** Extrair imagens/fotos dos quadros de envolvidos nos PDFs do RELINT e associá-las aos participantes.
* **Proposta de Solução:**
  * Usar a capacidade do PyMuPDF (`fitz`) para extrair raster de imagens dos PDFs durante a leitura.
  * Armazenar os arquivos de imagem em `data/media/<relint_filename>/`.
  * Associar fotos aos participantes por proximidade de coordenadas no layout do PDF ou confirmação no Dashboard.
  * Exibir galeria de fotos acumulada no Dossiê Unificado de Pessoas (`Person`).
