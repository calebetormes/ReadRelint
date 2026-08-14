# Blueprint, Arquitetura e Estrutura do Projeto

Este documento unifica a visão geral, as regras de ouro, a arquitetura e a estrutura de diretórios do projeto **ReadRelint** (Administrador de RELINTs local).

## 1. Visão Geral e Regras de Ouro
- **Objetivo:** Software local para Windows que monitora uma pasta de documentos de inteligência (RELINTs) em formato PDF. Ele extrai e limpa o texto, utiliza uma LLM local (Ollama) para estruturar dados, e armazena-os em um banco de dados relacional embutido (SQLite).
- **Painel de Controle:** Oferece um dashboard interativo moderno (FastAPI backend + HTML/JS SPA frontend em tema escuro baseado no Resend Design System) para buscar, cruzar vínculos de participantes, exibir dossiês por especialidade, fotos/anexos com visualizador lightbox, métricas de inteligência e permitir a curadoria humana dos dados.

### Regras de Ouro (Core Principles)
1. **Privacidade e Segurança:** NENHUM dado pode ser enviado para a nuvem sem cifragem. O processamento é 100% offline por padrão.
2. **Arquitetura Limpa:** Padrão Ports and Adapters rigorosamente aplicado.
3. **Idioma (Padrão Híbrido):** O código-fonte (nomes, classes, variáveis) é estritamente em **Inglês**. A documentação, comentários e UI são em **Português do Brasil (pt-BR)**.
4. **Portabilidade:** Sem instalações de servidores complexos. SQLite embutido em modo WAL.
5. **Single Source of Truth:** Cada documento processado corresponde a um único registro no banco.
6. **Especialidades Polimórficas:** Suporte a modelos estendidos por tipo de crime (ex: Homicídios) preservando um esquema de banco limpo e extensível via JSON `data`.

---

## 2. Tecnologias Principais e Pipeline
- **Base:** Python 3.10+
- **Leitura de PDF:** `PyMuPDF` (fitz) para texto e extração de imagens (galeria).
- **Motor NLP Local:** `Ollama` local com JSON Schemas Pydantic dinâmicos por especialidade.
- **Classificador Determinístico:** Regex engine (`bm_classifier.py`) como camada de segurança pós-LLM.
- **Persistência:** `SQLite` (`relints.db`).
- **Interfaces:** `CustomTkinter` (Monitoramento/Desktop) e `FastAPI + Single Page Application HTML/JS` (Dashboard de Curadoria Web em Resend Dark Theme com ApexCharts e Lucide Icons).

### Pipeline ETL
1. **Extração:** Monitoramento de diretório. PyMuPDF extrai texto integral e varre imagens. Limpeza via regex de cabeçalhos institucionais.
2. **Cognitivo (Ollama):** Envio para a IA com o Pydantic JSON Schema específico da especialidade (`HomicideReport` ou `IncidentReport`).
3. **Classificação Determinística:** O `bm_classifier.py` aplica regras de padrões ordenados por especificidade (Homicídio, Tráfico, Roubos, Furtos) para garantir o `bm_group` correto mesmo se a IA oscilar.
4. **Persistência:** Entidades `IncidentReport` / `HomicideReport` e `Person` validadas por Pydantic e salvas via SQLite (coluna `data` JSON).
5. **Dashboard:** O Painel Web consome os endpoints do FastAPI para cruzar relacionamentos (pessoas/documentos), exibir Dossiês por Especialidade, Manchas Criminais (agregadas dinamicamente), Gráficos Analíticos ApexCharts e Galerias de anexos com zoom/lightbox.

---

## 3. Contrato de Dados (Esquema Principal & Especialidades)

### Entidade Base (`IncidentReport`)
- `source_file`, `modification_date_history`, `subject`, `main_fact`, `date_of_fact`, `time_of_fact`
- `relint_type`, `bm_group`, `location_types`
- Geolocalização: `address`, `municipality`, `street`, `number`, `neighborhood`, `map_url`, `coordinates`
- Dados Brutos: `images` (lista de caminhos e legendas normalizados para a rota estática `/media/`), `content` (texto literal), `summary`, `user_edited`
- `participants`: Lista contendo `name`, `nickname`, `document`, `background`, `participation_type`, `photo_path`.

### Entidade Especialidade (`HomicideReport` estende `IncidentReport`)
- `registry_number`, `registry_agency`, `registry_year`: Dados de registro policial (ex: 516/151641/2026 DP).
- `fact_type`: Tentado ou Consumado.
- `police_unit`: Unidade BPM responsável (16BPM, 37BPM, 39BPM).
- `motivation`: Feminicídio, Tráfico, Oposição à Ação PM, Desavença, Latrocínio, Desconhecido.

---

## 4. Estrutura Física do Código-Fonte (`/src`)
*   `data/`: Banco local `relints.db`, `processed_registry.json` e diretório `media/` contendo fotos.
*   `src/domain/`: Regras de negócio sem dependências (`entities.py`, regras em `/rules/` como `homicide_rule.py`).
*   `src/ports/`: Interfaces (`IFileParser`, `ILlmProcessor`, `IDatabaseRepo`, etc.).
*   `src/adapters/`: Implementações concretas (SQLite, Ollama, PyMuPDF, etc.).
*   `src/application/`: Orquestração do Pipeline (`etl_service.py`, `text_cleaner.py`, `geo_service.py`, `bm_classifier.py`).
*   `src/presentation/`:
    *   `/desktop/`: CustomTkinter UI (MainController, FolderWatcher, Tabs).
    *   `/api/`: Backend FastAPI (app.py, routers/, schemas/).
    *   `/web/`: SPA Frontend em Resend Dark Theme (`index.html`, `css/variables.css`, `css/main.css`, views em `js/views/`: `relints_view.js`, `homicides_view.js`, `crimes_view.js`, `gallery_view.js`).
*   `tests/`: Testes unitários com `pytest` (cobertura de entidades, regras, API, parser, classifier e repositório).
*   `scratch/`: Scripts temporários e utilitários da IA.
