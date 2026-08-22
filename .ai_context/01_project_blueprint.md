# Blueprint, Arquitetura e Estrutura do Projeto

Este documento unifica a visão geral, as regras de ouro, a arquitetura e a estrutura de diretórios do projeto **ReadRelint** (Administrador de RELINTs local).

## 1. Visão Geral e Regras de Ouro
- **Objetivo:** Software local para Windows que monitora uma pasta de documentos de inteligência (RELINTs) em formato PDF. Ele extrai e limpa o texto, utiliza uma LLM local (Ollama) ou pipeline determinístico ultra-rápido (spaCy + IBGE + Regex) para estruturar dados, e armazena-os em um banco de dados relacional embutido (SQLite).
- **Painel de Controle Desktop:** Interface moderna em Tkinter/CustomTkinter atuando como *Service Launcher & Status Hub* ultraleve (480x580) para ligar/desligar serviços (Monitor de Pastas, Servidor Web e IA) com suporte a System Tray (Bandeja do Windows).
- **Dashboard Web de Curadoria:** Oferece um dashboard interativo (FastAPI backend + HTML/JS SPA frontend em tema escuro baseado no Resend Design System) para buscar, cruzar vínculos de participantes, exibir dossiês por especialidade, fotos/anexos com visualizador lightbox, métricas de inteligência e curadoria humana dos dados.

### Regras de Ouro (Core Principles)
1. **Privacidade e Segurança:** NENHUM dado pode ser enviado para a nuvem sem cifragem. O processamento é 100% offline por padrão.
2. **Arquitetura Limpa:** Padrão Ports and Adapters rigorosamente aplicado e organizado em módulos especializados (`src/engine`, `src/task_manager`, `src/dashboard`).
3. **Idioma (Padrão Híbrido):** O código-fonte (nomes, classes, variáveis) é estritamente em **Inglês**. A documentação, comentários e UI são em **Português do Brasil (pt-BR)**.
4. **Portabilidade:** Sem instalações de servidores complexos. SQLite embutido em modo WAL (`data/relints.db`).
5. **Single Source of Truth:** Cada documento processado corresponde a um único registro no banco relacional.
6. **Especialidades Polimórficas:** Suporte a modelos estendidos por tipo de crime (ex: Homicídios, Tráfico, Roubos e Furtos) preservando um esquema relacional limpo e extensível via JSON.
7. **Processamento Híbrido (IA vs Determinístico):** O sistema opera tanto com LLM local (Ollama) enriquecido por guardrails determinísticos quanto em modo 100% Determinístico sem IA, registrando explicitamente o método de extração utilizado (`"Ollama (IA)"` vs `"Regex (Sem IA)"`).
8. **Classificação Tripla de Participantes:** Padronização estrita em 3 papéis exclusivos: **`Vítima`**, **`Testemunha`** e **`Autor/Suspeito`**.

---

## 2. Tecnologias Principais e Pipeline
- **Base:** Python 3.10+
- **Leitura de PDF:** `PyMuPDF` (fitz) para extração limpa de texto bruto e recorte de imagens/anexos (galeria).
- **Motor NLP Local:** `Ollama` local com JSON Schemas Pydantic estruturados e prompts com regras estritas anti-PM.
- **Motor Determinístico:** Pipeline em 5 camadas (`src/engine/extractors/deterministic/`):
  1. Blocos verticais estruturados e padrões inline com idade/documento.
  2. Reconhecimento de entidades nomeadas via `spaCy` (`pt_core_news_sm`).
  3. Validação positiva de prenomes brasileiros via Censo IBGE em O(1).
  4. Detecção direcional de papéis e especificidade léxica (`role_detector.py`).
  5. Filtros negativos estritos contra patentes militares, órgãos públicos e termos veiculares.
- **Persistência:** `SQLite` em modo WAL (`relints.db`).
- **Interfaces:**
  - `Desktop Hub`: Python Tkinter/CustomTkinter (Status Hub compacto).
  - `Web Dashboard`: SvelteKit SPA (adapter-static) + Svelte 5 Runes (Resend Dark/Light Theme com ApexCharts e Lucide Icons).

### Pipeline ETL
1. **Extração:** Monitoramento de diretório. PyMuPDF extrai texto integral e varre imagens. Limpeza de cabeçalhos/rodapés institucionais via `clean_relint_text`.
2. **Cognitivo (Ollama / Determinístico):** Se o Ollama estiver ativo, envio para a IA com o JSON Schema específico da especialidade. Caso inativo ou em falha, extração ultra-rápida via motor determinístico.
3. **Pós-processamento e Guardrails:** Aplicação de `clean_person_name`, recuperação de documentos por proximidade (`extract_document_near_name`), normalização de papéis para o trio oficial (`Vítima`, `Testemunha`, `Autor/Suspeito`) e expurgo de falsos positivos de policiais.
4. **Classificação Determinística:** O `bm_classifier.py` aplica regras de padrões ordenados por especificidade (Homicídio, Tráfico, Roubos, Furtos) para garantir o `bm_group` correto.
5. **Persistência:** Entidades `IncidentReport` / `HomicideReport` e `Person` validadas por Pydantic e salvas no SQLite (`relints`, `pessoas`, `relint_participantes`).
6. **Dashboard:** O Painel Web consome os endpoints REST do FastAPI para cruzar relacionamentos, exibir Dossiês por Especialidade, Analytics de Crimes com ApexCharts e Galerias de anexos com lightbox.

---

## 3. Contrato de Dados (Esquema Principal & Especialidades)

### Entidade Base (`IncidentReport`)
- `source_file`, `modification_date_history`, `subject`, `main_fact`, `date_of_fact`, `time_of_fact`
- `relint_type`, `bm_group`, `location_types`
- `extraction_method`: `"Ollama (IA)"` ou `"Regex (Sem IA)"`
- Geolocalização: `address`, `municipality`, `street`, `number`, `neighborhood`, `map_url`, `coordinates`
- Dados Brutos: `images` (lista de caminhos e legendas `/media/`), `content` (texto literal), `summary`, `user_edited`
- `participants`: Lista de `Participant` contendo `name`, `nickname`, `document`, `background`, `participation_type` (`"Vítima"`, `"Testemunha"`, `"Autor/Suspeito"`), `photo_path`.

### Entidade Especialidade (`HomicideReport` estende `IncidentReport`)
- `registry_number`, `registry_agency`, `registry_year`: Dados de registro policial.
- `fact_type`: Tentado ou Consumado.
- `police_unit`: Unidade BPM responsável (16BPM, 37BPM, 39BPM).
- `motivation`: Feminicídio, Tráfico, Oposição à Ação PM, Desavença, Latrocínio, Desconhecido.

---

## 4. Estrutura Física do Código-Fonte (`/src`)
* `data/`: Banco relacional `relints.db`, `processed_registry.json`, `erros.md` e diretório `media/` contendo fotos recortadas dos PDFs.
* `src/engine/`:
  * `/parsers/`: Leitor PyMuPDF e extrator de imagens (`pdf_reader.py`).
  * `/cleaners/`: Higienização textual e sanitização de nomes (`text_cleaner.py`).
  * `/extractors/deterministic/`: Motor especialista sem IA (`pipeline.py`, `structured_parser.py`, `role_detector.py`, `spacy_ner.py`, `ibge_validator.py`).
  * `/extractors/llm/`: Cliente Ollama e schemas (`ollama_client.py`).
  * `/extractors/common/`: Filtros negativos e listas negras (`negative_filters.py`).
* `src/task_manager/`:
  * `/etl/`: Orquestrador de extração e guardrails (`etl_service.py`).
  * `/watcher/`: Monitor de pastas e eventos de arquivo (`folder_watcher.py`).
  * `/registry/`: Controle atômico de arquivos processados (`json_processed_registry.py`).
* `src/dashboard/`:
  * `/backend/`: Servidor FastAPI, routers REST, repositórios SQLite e entidades Pydantic.
  * `/frontend/`: SPA Web (HTML, CSS, views JavaScript em Resend Dark System).
  * `/desktop/`: Aplicativo de inicialização de serviços Tkinter (`desktop_app.py`, `status_tab.py`).
* `tests/`: Suíte completa de testes automatizados com `pytest`.
