# Blueprint do Projeto: Administrador de RELINTs (Ollama)

## Visão Geral
- **Objetivo:** Software local para Windows que monitora uma pasta de documentos de inteligência (RELINTs) em formato PDF. Ele extrai e limpa o texto, utiliza uma LLM local (via Ollama) para estruturar os dados chave em JSON, e armazena-os em um banco de dados NoSQL embutido.
- **Painel de Controle:** Oferece um dashboard interativo (Streamlit) para buscar, cruzar vínculos de participantes (ex: identificar CPFs/nomes comuns entre diferentes relatórios), visualizar o histórico completo do relatório e permitir a edição de qualquer campo gerado, garantindo curadoria humana sobre a classificação da IA.
- **Status:** Em migração de escopo estrutural. Estrutura Clean Architecture (Ports & Adapters) consolidada, adaptadores base e dashboard Streamlit operacionais.

## Regras de Ouro (Core Principles)
1. **Privacidade e Segurança:** NENHUM dado de relatório de inteligência pode ser enviado para a nuvem. O processamento de IA é estritamente local via Ollama (Offline).
2. **Arquitetura Limpa:** Padrão Ports and Adapters rigorosamente aplicado. A lógica de domínio e regras de negócio não conhecem PDF, Banco de Dados, Streamlit ou IA.
3. **Idioma (Padrão Híbrido):** O código-fonte (nomes de arquivos, classes, variáveis, chaves de JSON, métodos) deve ser escrito estritamente em **Inglês**. A documentação, os comentários no código, os logs de terminal e os textos da Interface do Usuário (UI) devem ser estritamente em **Português do Brasil (pt-BR)**.
4. **Portabilidade:** O software deve rodar sem exigir a instalação de infraestrutura complexa ou servidores de banco de dados na máquina do usuário. O banco de dados é embutido (TinyDB).
5. **Unicidade de Registro por Documento:** Cada documento PDF processado corresponde a exatamente **um único registro** no banco de dados. O reprocessamento preservará prioritariamente as edições manuais feitas pelo usuário.
