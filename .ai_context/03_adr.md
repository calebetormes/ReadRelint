# Registro de Decisões de Arquitetura (ADR)

## [ADR-001] Adoção da Clean Architecture
- **Decisão:** Isolamento da lógica de negócios usando Ports e Adapters para facilitar a substituição de ferramentas (bancos, parsers de PDF) sem quebrar o core.

## [ADR-002] Processamento de NLP Local (Soberania de Dados)
- **Decisão:** Uso do Ollama rodando localmente na máquina servidora/cliente.
- **Motivo:** Boletins de ocorrência contêm PII e dados sensíveis que não podem ser enviados para APIs de nuvem por questões legais (LGPD).

## [ADR-003] Interface Híbrida (Múltiplos Delivery Mechanisms)
- **Decisão:** Uso de CustomTkinter para controle do sistema (seleção de pastas via OS) e Streamlit para visualização dos dados do banco.
- **Motivo:** Bibliotecas desktop nativas são ideais para interagir com o sistema de arquivos do Windows, mas são ineficientes para criar dashboards e tabelas dinâmicas, onde o Streamlit brilha.

## [ADR-004] TinyDB como Banco de Dados Embutido
- **Decisão:** Uso do TinyDB, descartando bancos baseados em servidor (como MongoDB).
- **Motivo:** Manter a estrutura NoSQL orientada a documentos (essencial para armazenar as saídas JSON do LLM), garantindo que o software seja totalmente portátil e fácil de instalar.

## [ADR-005] Adoção do Pytest para Testes Automatizados e Mocks
- **Decisão:** Adoção do `pytest` como o framework oficial de testes.
- **Motivo:** Assegurar a integridade do domínio Pydantic e o comportamento de comunicação externa dos adaptadores. O uso de fixtures (`tmp_path`) e mocks (`unittest.mock`) garante isolamento total dos testes sem depender de instâncias externas de IA ou criar arquivos de banco/PDF permanentes no repositório.
