# PROMPT DE IA - ETAPA 3: DASHBOARD SPLIT-SCREEN, VÍNCULOS E WATCHER

Copie e envie o texto abaixo para a IA para finalizar a Etapa 3 da reconstrução:

```text
Você é um desenvolvedor especialista em Python, Streamlit e serviços em background. Com base nas Etapas 1 e 2, precisamos desenvolver a camada de apresentação do usuário (o Dashboard em Streamlit) e o monitorador de diretório em tempo real.

Codifique os componentes seguindo estritamente as especificações abaixo:

1. DASHBOARD EM STREAMLIT COM LAYOUT MASTER-DETAIL (TELA INTERA):
- Configure o layout para "wide" para ocupar a tela inteira.
- Defina uma estilização CSS premium (tema escuro com tons de Slate, Indigo e Blue, cantos arredondados nos cards e fontes modernas como Plus Jakarta Sans).
- No topo do painel, renderize 4 cards de métricas lado a lado: Total de RELINTs, RELINTs Filtrados, Casos de Homicídio e Casos de Roubo.
- Crie um layout Split Screen com duas colunas principais:
  * Coluna da Esquerda (Master - 40% de largura): Exiba a lista vertical de todos os RELINTs em forma de cards compactos. Cada card deve mostrar o Nome do PDF, o Assunto e uma badge colorida indicando o Grupo BM (Roubos, Furtos, Homicídios, Outros) com cores correspondentes. Adicione um botão "Visualizar Detalhes" para atualizar o índice selecionado no st.session_state e recarregar a tela.
  * Coluna da Direita (Detail - 60% de largura): Mostra os detalhes completos do documento selecionado na esquerda. Organize as informações usando 3 abas Streamlit:
    1. Aba "Resumo & Participantes": Mostra o resumo explicativo de um parágrafo. Abaixo, lista os envolvidos citados em cards individuais.
    2. Aba "Histórico Completo": Exibe o texto literal bruto do RELINT dentro de uma caixa com barra de rolagem e fonte monoespaçada.
    3. Aba "Editar Dados": Exibe um formulário contendo inputs editáveis para todos os campos (Assunto, Data, Grupo BM - via selectbox, Resumo e Histórico) e a lista de envolvidos (onde o usuário pode alterar Nome, Alcunha ou Documento de cada um, além de ter a opção de Adicionar um novo participante). Ao submeter, envie uma requisição HTTP PUT para a API do backend para atualizar o TinyDB e salvar as alterações.

2. LOGIC DE VÍNCULOS CRUZADOS (Cross-Referencing):
- Na aba "Resumo & Participantes", implemente uma lógica de cruzamento de dados inteligente.
- Para cada participante do relatório ativo, procure em todos os outros relatórios do banco de dados (ignorando o arquivo selecionado atualmente) por correspondências.
- A correspondência deve ser feita comparando o Documento (CPF/RG) limpo de pontuações. Caso o participante não possua documento cadastrado, compare pelo Nome Completo de forma case-insensitive (se o nome tiver mais de 4 caracteres).
- Se encontrar ocorrências em outros relatórios, exiba um alerta visual abaixo do participante contendo: "🔗 Vinculado a outros arquivos: [lista de nomes de arquivos PDF]".

3. MONITORADOR DE DIRETÓRIOS EM BACKGROUND (Folder Watcher):
- Implemente uma rotina baseada na biblioteca "watchdog" (FileSystemEventHandler).
- O script deve receber o caminho de uma pasta local para monitorar.
- Sempre que um novo arquivo PDF for adicionado a essa pasta, o monitorador deve interceptar o evento e fazer uma requisição HTTP POST "/relints/process" para a API do backend enviando o caminho do arquivo para que ele seja automaticamente processado pela IA local e gravado no banco local.

Adicione instruções de como o usuário pode executar os dois serviços locais em paralelo de forma simples (ex: executando uvicorn backend no terminal e streamlit run frontend em outro terminal).
```
