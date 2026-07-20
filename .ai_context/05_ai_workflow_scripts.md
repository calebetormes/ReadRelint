# Scripts de Gerenciamento de Contexto da IA

*Use os prompts abaixo para manter o contexto entre sessões.*

## 1. Prompt de Inicialização
```text
Olá! Vamos trabalhar no ETL de Boletins de Ocorrência. Leia os arquivos da pasta `.ai_context` para absorver a arquitetura. 
Lembre-se da REGRA DE IDIOMA: Código-fonte sempre em Inglês; Documentação e comentários sempre em pt-BR. Não escreva código ainda. Responda apenas confirmando o entendimento e me diga qual é o primeiro item da lista de "Próximos Passos Pendentes".
```

## 1. Prompt de Encerramento
Sessão concluída. Com base no que fizemos hoje:
1. Atualize o `.ai_context/04_current_state.md` marcando as tarefas feitas e adicionando os próximos passos lógicos.
2. Atualize o `.ai_context/03_adr.md` ou `02_architecture.md` se tivermos tomado alguma decisão técnica nova ou adicionado bibliotecas.
3. Imprima o código Markdown completo dos arquivos alterados em blocos de código separados para que eu possa atualizar meu repositório local.

