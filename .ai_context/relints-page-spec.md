Especificação: Gerenciador de RELINTs (Master-Detail 30/70)
Este documento descreve a especificação técnica e comportamental da página de Gerenciamento Geral dos RELINTs, adotando o padrão Master-Detail (30% / 70%) alinhado ao nosso Design System em Svelte 5.

1. Arquitetura de Layout: Master-Detail (30% / 70%)
A interface elimina modais centrais para garantir navegação contínua e sem interrupções:

⬅️ Coluna Esquerda: Lista Master (30% da largura)
Barra de Controle Superior:
Campo de busca em tempo real (por assunto, código ou participante).
Filtros rápidos (Especialidade, Apenas Revisados, Status de IA).
Lista de Cards Compactos:
Exibe código do RELINT (ex: RELINT-2026-001), data do fato, especialidade e badge de status.
Badge de Revisão: Exibe <Badge variant="success"><CheckCircle /> Revisado</Badge> com ícone de check quando houver curadoria efetuada (user_edited = true).
Navegação Contínua: Seleção via clique ou teclas de atalho (setas ↑ e ↓), atualizando instantaneamente o painel de detalhes à direita.
➡️ Coluna Direita: Workspace de Detalhes (70% da largura)
Exibe o relatório completo selecionado, organizado em 5 Sub-Abas usando o componente Tabs.svelte:

Aba 1: Geral

Formulário de edição: Resumo, Assunto, Data do Fato, Número de Registro Policial (numero_registro), Órgão (orgao_registro) e Ano (ano_registro).
Botão de salvamento rápido com indicação visual de alteração pendente.
Aba 2: Localização

Endereço estruturado, Bairro, Município e nível de precisão geográfica.
Aba 3: Especialidade (Dinâmica)

Campos mutáveis que se adaptam conforme o grupo_bm (ex: campos específicos de Homicídios como motivação e DP responsável). A conversão polimórfica ocorre de forma transparente no backend.
Aba 4: Participantes (Cards em Cascata)

Visualização em Cards Policiais: Avatar/Foto + Nome/Alcunha + Tag de Função (Autor, Vítima, Testemunha).
CRUD simplificado para vincular novos participantes, associar fotos extraídas do PDF ou abrir o Dossiê Individual.
Aba 5: Transcrição Bruta

Texto integral do boletim com realce visual (highlight) nos nomes de participantes e locais capturados pela IA.
2. Indicadores e Estilização no Design System
Badge de Status "Revisado":
Ícone: CheckCircle (Phosphor Icons em formato fill ou bold).
Texto: Revisado.
Variante: success ou amber conforme o tema.
Transições: Uso de variáveis de tempo e easing nativos (var(--duration-fast) e var(--ease-standard)).
Responsividade: Em telas menores (mobile/tablet < 992px), a lista master recolhe automaticamente em um drawer deslizante.
3. Integração com a API REST (FastAPI)
GET /api/v1/relints: Carregamento e atualização da lista master e detalhes.
PUT /api/v1/relints/{id}: Envio das alterações editadas no workspace (atualiza user_edited = true e grava o badge "Revisado").