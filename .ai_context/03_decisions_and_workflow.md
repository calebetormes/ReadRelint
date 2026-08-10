# Decisões Técnicas e Fluxo da IA (ADR & Workflow)

Este documento contém os registros de decisões arquiteturais importantes (ADRs) que ditam a lógica técnica do projeto, e os roteiros operativos de como o Agente de IA deve atuar.

## 1. Roteiros de Fluxo da IA (AI Workflows)

### Prompt Inicial Recomendado (Sempre que reiniciar contexto)
```text
Olá! Vamos trabalhar no Administrador de RELINTs. Leia estritamente a nova estrutura consolidada da pasta `.ai_context` (`01_project_blueprint.md`, `02_project_state.md`, `03_decisions_and_workflow.md`) para absorver a arquitetura e entender em que passo estamos.
Lembre-se da REGRA DE IDIOMA HÍBRIDO: Código-fonte sempre em Inglês; Documentação e comentários em pt-BR. Não escreva código ainda. Apenas confirme o entendimento.
```

### Prompt de Encerramento (Finalização de Sessões)
Sempre que concluir grandes blocos de tarefas:
1. Atualize o `02_project_state.md`, movendo os itens de "Tarefas Futuras" para "Implementados".
2. Se criamos novos módulos arquiteturais, adicione um novo [ADR] na seção abaixo ou atualize o `01_project_blueprint.md`.
3. Ofereça um resumo legível e gere um `walkthrough.md` caso estivesse em Planning Mode.

---

## 2. Registro de Decisões de Arquitetura (ADRs)

- **[ADR-001] Clean Architecture e NLP Local:** Isolamento total via Ports e Adapters. Uso exclusivo do `Ollama` rodando localmente, evitando quebras de LGPD (nenhum PDF sai da máquina).
- **[ADR-002] Interface Híbrida:** Streamlit para leitura e cruzamento (Dashboard) e CustomTkinter para monitoramento de pastas OS-level (Desktop).
- **[ADR-003] Migração de TinyDB para SQLite (Persistência Principal):** Uso de `SQLite` nativo em modo WAL (Write-Ahead Logging) em `data/relints.db`. Motivo: Resiliência contra concorrência e tabelas estruturadas que permitem queries velozes para dossiês, abandonando o gargalo de O(N) do TinyDB.
- **[ADR-004] Separação de Dados Multibanco:** Criação das tabelas e domínios independentes de `IncidentReport`, `Person` e `Municipality` no SQLite. Garante dossiês hiper-velozes e cruzamento de vínculos de pessoas através dos RELINTs.
- **[ADR-005] Exclusão de Guarnições PM e Transcrição Segura:** Policiais não são adicionados aos dossiês de pessoas investigadas (apenas vítimas/testemunhas/acusados/civis). O histórico literal (`content`) do boletim é extraído via código determinístico (Python/Regex) e ocultado da IA (LLM), evitando que ela trunque ou resuma erroneamente a transcrição exata dos fatos.
- **[ADR-006] Prioridade da Curadoria Humana:** Uso do `processed_registry.json` para gravar edições efetuadas pelo usuário humano e forçar que a IA nunca sobrescreva alterações humanas caso o PDF seja reprocessado.
- **[ADR-007] Geolocalização Visual por 3 Níveis:** Cores indicando precisão da localização no Dashboard: Verde (GPS exato capturado do PDF), Azul (Link explícito capturado), Laranja (Endereço estruturado via fallback).
- **[ADR-008] Repositório Universal (Sem Descartes):** Nenhum boletim válido lido do diretório deve ser silenciado. Todos devem ir para o banco. A filtragem de "ocorrências indesejadas" ocorre apenas na UI do Streamlit.
- **[ADR-009] Suíte de Testes 100% Mockada:** O `pytest` usa fixtures de memória (`tmp_path`) e mocks simulando Ollama e PyMuPDF para executar CI instantâneo sem necessitar ambiente pesado pré-configurado.
