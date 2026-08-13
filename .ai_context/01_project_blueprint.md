# Blueprint, Arquitetura e Estrutura do Projeto

Este documento unifica a visão geral, as regras de ouro, a arquitetura e a estrutura de diretórios do projeto **ReadRelint** (Administrador de RELINTs local).

## 1. Visão Geral e Regras de Ouro
- **Objetivo:** Software local para Windows que monitora uma pasta de documentos de inteligência (RELINTs) em formato PDF. Ele extrai e limpa o texto, utiliza uma LLM local (Ollama) para estruturar dados, e armazena-os em um banco de dados relacional embutido (SQLite).
- **Painel de Controle:** Oferece um dashboard interativo moderno (FastAPI backend + HTML/JS SPA frontend) para buscar, cruzar vínculos de participantes, exibir dossiês, fotos/anexos com visualizador lightbox e permitir a edição de dados extraídos pela IA.

### Regras de Ouro (Core Principles)
1. **Privacidade e Segurança:** NENHUM dado pode ser enviado para a nuvem sem cifragem. O processamento é 100% offline por padrão.
2. **Arquitetura Limpa:** Padrão Ports and Adapters rigorosamente aplicado.
3. **Idioma (Padrão Híbrido):** O código-fonte (nomes, classes, variáveis) é estritamente em **Inglês**. A documentação, comentários e UI são em **Português do Brasil (pt-BR)**.
4. **Portabilidade:** Sem instalações de servidores complexos. SQLite embutido em modo WAL.
5. **Single Source of Truth:** Cada documento processado corresponde a um único registro.

---

## 2. Tecnologias Principais e Pipeline
- **Base:** Python 3.10+
- **Leitura de PDF:** `PyMuPDF` (fitz) para texto e extração de imagens (galeria).
- **Motor NLP Local:** `Ollama` local.
- **Persistência:** `SQLite` (`relints.db`).
- **Interfaces:** `CustomTkinter` (Monitoramento/Desktop) e `FastAPI + Single Page Application HTML/JS` (Dashboard de Curadoria Web).

### Pipeline ETL
1. **Extração:** Monitoramento de diretório. PyMuPDF extrai texto integral e varre imagens. Limpeza via regex de cabeçalhos institucionais.
2. **Cognitivo (Ollama):** Envio para a IA com instruções Pydantic JSON para estruturar metadados, ignorando transcrição literal que é mantida pelo Python.
3. **Persistência:** Entidades `IncidentReport` e `Person` validadas por Pydantic e salvas via SQLite.
4. **Dashboard:** O Painel Web consome os endpoints do FastAPI para cruzar relacionamentos (pessoas/documentos) e mostra Dossiês, Manchas Criminais (agregadas dinamicamente) e Galerias de anexos com zoom/lightbox.

---

## 3. Contrato de Dados (Esquema Principal)
A entidade `IncidentReport` salva no SQLite:
- `source_file`, `modification_date_history`, `subject`, `main_fact`, `date_of_fact`, `time_of_fact`
- `relint_type`, `bm_group`, `location_types`
- Geolocalização: `address`, `municipality`, `street`, `number`, `neighborhood`, `map_url`, `coordinates`
- Dados Brutos: `images` (lista de caminhos e legendas normalizados para a rota estática `/media/`), `content` (texto literal), `summary`, `user_edited`
- `participants`: Lista contendo `name`, `nickname`, `document`, `background`, `participation_type`, `photo_path`.

---

## 4. Estrutura Física do Código-Fonte (`/src`)
*   `data/`: Banco local `relints.db`, `processed_registry.json` e diretório `media/` contendo fotos.
*   `src/domain/`: Regras de negócio sem dependências (`entities.py`, regras em `/rules/`).
*   `src/ports/`: Interfaces (`IFileParser`, `ILlmProcessor`, `IDatabaseRepo`, etc.).
*   `src/adapters/`: Implementações concretas (SQLite, Ollama, PyMuPDF, etc.).
*   `src/application/`: Orquestração do Pipeline (`etl_service.py`, `text_cleaner.py`, `geo_service.py`).
*   `src/presentation/`:
    *   `/desktop/`: CustomTkinter UI (MainController, FolderWatcher, Tabs).
    *   `/api/`: Backend FastAPI (app.py, routers/, schemas/).
    *   `/web/`: SPA Frontend (index.html, css/, js/views/).
*   `tests/`: Testes unitários com `pytest`.
*   `scratch/`: Scripts temporários e utilitários da IA.
