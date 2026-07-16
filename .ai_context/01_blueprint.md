# Blueprint do Projeto: Sistema ETL de Boletins de Ocorrência

## Visão Geral
- **Objetivo:** Software desktop para Windows que monitora diretórios, extrai texto de Boletins de Ocorrência em PDF, estrutura os dados usando Inteligência Artificial (NLP) e os armazena em um banco NoSQL embutido.
- **Público-alvo:** Usuários internos que precisam analisar dados de ocorrências policiais de forma estruturada.
- **Status:** Em desenvolvimento avançado. Camada de domínio, portas de arquitetura, adaptadores concretos (PdfReader, TinyDbRepo, OllamaClient), monitoramento de diretórios, testes unitários, e dashboard Web (Streamlit) simplificado com controle de ciclo de vida integrado ao painel desktop implementados.

## Regras de Ouro (Core Principles)
1. **Privacidade e Segurança:** NENHUM dado de ocorrência pode ser enviado para a nuvem. O processamento de IA é estritamente local (Offline).
2. **Arquitetura Limpa:** Padrão Ports and Adapters rigorosamente aplicado. A lógica de domínio não conhece PDF, Banco de Dados ou IA.
3. **Idioma (Padrão Híbrido):** O código-fonte (nomes de arquivos, classes, variáveis, chaves de JSON, métodos) deve ser escrito estritamente em **Inglês**. A documentação, os comentários no código, os logs de terminal e os textos da Interface do Usuário (UI) devem ser estritamente em **Português do Brasil (pt-BR)**.
4. **Portabilidade:** O software deve rodar sem exigir a instalação de infraestrutura pesada na máquina do usuário. O banco de dados deve ser embutido (serverless).
5. **Unicidade de Registro por Documento:** Cada documento PDF processado deve corresponder a exatamente **um único "REGISTRO" ou "FATO" principal**. O sistema não deve segmentar um único documento em múltiplas ocorrências independentes no banco/dashboard para evitar a inflação artificial de dados (por exemplo, 3 documentos de homicídio processados devem resultar em exatamente 3 registros de homicídio no dashboard).
