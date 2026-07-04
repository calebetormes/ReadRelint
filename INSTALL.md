# Guia de Instalação e Configuração do Sistema ETL de BOs

Este documento descreve o passo a passo necessário para clonar, configurar e executar a aplicação em uma nova máquina a partir do repositório no GitHub.

---

## 📋 Pré-requisitos

Antes de iniciar, certifique-se de que a máquina de destino possui os seguintes softwares instalados:

1. **Python (versão 3.10 ou superior)**
   * Baixe em: [python.org](https://www.python.org/downloads/)
   * **Importante (Windows):** Durante a instalação, marque a caixa **"Add Python to PATH"** (Adicionar Python às variáveis de ambiente).
2. **Ollama**
   * Baixe e instale o Ollama em: [ollama.com](https://ollama.com/)
   * O Ollama é necessário para rodar o modelo de inteligência artificial de forma local e offline na máquina.
3. **Git**
   * Baixe e instale em: [git-scm.com](https://git-scm.com/)

---

## 🛠️ Passo a Passo de Instalação

### 1. Clonar o Repositório
Abra o terminal (Prompt de Comando ou PowerShell no Windows, Terminal no Linux/macOS) e execute:
```bash
git clone <URL_DO_SEU_REPOSITORIO_NO_GITHUB>
cd ReadRelint
```
*(Substitua `<URL_DO_SEU_REPOSITORIO_NO_GITHUB>` pelo link de clone gerado no GitHub).*

### 2. Baixar o Modelo de IA no Ollama
Certifique-se de que o Ollama está em execução em segundo plano na barra de tarefas. No terminal, execute o seguinte comando para baixar e carregar o modelo de linguagem utilizado pelo sistema:
```bash
ollama run llama3.1
```
*(Aguarde a conclusão do download do modelo, que possui aproximadamente 4.7 GB. Você pode fechar o prompt interativo do Ollama digitando `/bye` após o término).*

### 3. Configurar o Ambiente Virtual do Python
Garante o isolamento das dependências para evitar conflitos no sistema operacional.

**No Windows:**
```powershell
python -m venv .venv
.venv\Scripts\activate
```

**No Linux/macOS:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 4. Instalar as Dependências do Projeto
Com o ambiente virtual ativado (indicado pelo prefixo `(.venv)` no terminal), instale todas as bibliotecas requeridas:
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

---

## 🧪 Validar a Instalação (Opcional)

Para garantir que toda a infraestrutura e os testes de integração e domínio estão funcionando corretamente na nova máquina, execute a suíte de testes:
```bash
pytest
```
*Todos os 20 testes automatizados devem passar com sucesso.*

---

## 🚀 Como Executar o Sistema

### Iniciar o Painel Desktop de Monitoramento
Você pode abrir o painel principal de duas maneiras no Windows:

* **Método Rápido:** Dê um duplo clique no atalho [Iniciar-Painel.bat](file:///d:/DEV26/ReadRelint/Iniciar-Painel.bat) na raiz do projeto.
* **Via Terminal (com ambiente virtual ativado):**
  ```bash
  python src/presentation/desktop/app.py
  ```

---

## 📂 Organização das Pastas pós-instalação
* Ao iniciar o monitoramento, selecione uma pasta local contendo os PDFs de Boletins de Ocorrência.
* O banco de dados local estruturado será gerado automaticamente no caminho `data/database.json`.
