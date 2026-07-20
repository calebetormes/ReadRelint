import sys
from pathlib import Path
import streamlit as st
from src.adapters.tinydb_repo import TinyDbRepo

# Adiciona a raiz do projeto ao sys.path para importações absolutas
project_root = Path(__file__).resolve().parent.parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Configuração da Página
st.set_page_config(
    page_title="ReadRelint - Painel Simplificado",
    page_icon="📄",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Estilização CSS Premium (Dark Theme, Glassmorphism, Typografia Inter)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');
    
    html, body, [data-testid="stAppViewContainer"] {
        font-family: 'Inter', sans-serif;
        background-color: #0d0e12;
        color: #e2e8f0;
    }
    
    /* Cabeçalho com Gradiente */
    .header-container {
        text-align: center;
        padding: 2.5rem 1rem 1.5rem 1rem;
        background: linear-gradient(135deg, #1f2937 0%, #111827 100%);
        border-radius: 16px;
        margin-bottom: 2rem;
        border: 1px solid #374151;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.3);
    }
    
    .header-title {
        font-size: 2.2rem;
        font-weight: 700;
        background: linear-gradient(to right, #60a5fa, #3b82f6);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
    }
    
    .header-subtitle {
        color: #9ca3af;
        font-size: 1rem;
        font-weight: 300;
    }

    /* Cards com Efeito Moderno */
    .document-card {
        background-color: #1f2937;
        padding: 1.5rem;
        border-radius: 12px;
        border: 1px solid #374151;
        margin-bottom: 1.25rem;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        transition: transform 0.2s, border-color 0.2s;
    }
    
    .document-card:hover {
        transform: translateY(-2px);
        border-color: #3b82f6;
    }

    .document-badge {
        display: inline-block;
        background-color: #3b82f6;
        color: #ffffff;
        font-size: 0.75rem;
        font-weight: 600;
        padding: 0.25rem 0.75rem;
        border-radius: 9999px;
        margin-bottom: 0.75rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }

    .document-filename {
        font-size: 1.15rem;
        font-weight: 600;
        color: #f3f4f6;
        margin-bottom: 0.75rem;
    }

    .document-content {
        background-color: #111827;
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid #374151;
        font-size: 0.95rem;
        line-height: 1.6;
        color: #d1d5db;
        white-space: pre-wrap;
    }

    /* Input do Search */
    div[data-testid="stTextInput"] input {
        background-color: #1f2937;
        border: 1px solid #374151;
        color: #ffffff;
        border-radius: 8px;
    }
    
    div[data-testid="stTextInput"] input:focus {
        border-color: #3b82f6;
        box-shadow: 0 0 0 1px #3b82f6;
    }
</style>
""", unsafe_allow_html=True)

# Título Principal do Dashboard
st.markdown("""
<div class="header-container">
    <div class="header-title">📋 Documentos Processados</div>
    <div class="header-subtitle">Visualização rápida e simplificada das extrações de IA local</div>
</div>
""", unsafe_allow_html=True)

# Carregamento de dados com TinyDbRepo
def load_data():
    db_path = Path("data/homicides.json")
    if not db_path.exists():
        return []
    repo = TinyDbRepo(db_path)
    return repo.get_all()

reports = load_data()

if not reports:
    st.info("Nenhum boletim de ocorrência processado até o momento. Inicie o monitoramento no Painel Desktop para processar arquivos.")
else:
    # Barra de busca simplificada e bonita
    search_query = st.text_input("", placeholder="🔍 Digite para pesquisar nos relatórios...")

    # Filtra relatórios com base no termo buscado
    filtered_reports = []
    for r in reports:
        # Extrai conteúdo (respeita novos e legados de forma simplificada)
        content = getattr(r, "content", None)
        if not content:
            # Reconstrói conteúdo simples para registros legados
            parts = []
            if getattr(r, "incident_nature", None): parts.append(f"Natureza: {r.incident_nature}")
            if getattr(r, "incident_type", None): parts.append(f"Tipo: {r.incident_type}")
            if getattr(r, "history_summary", None): parts.append(f"Histórico:\n{r.history_summary}")
            content = "\n\n".join(parts) if parts else "Sem conteúdo disponível."
        
        source_file = getattr(r, "source_file", "Desconhecido")
        
        # Filtro de busca simples
        if not search_query or (search_query.lower() in source_file.lower() or search_query.lower() in content.lower()):
            filtered_reports.append((source_file, content))

    # Exibição de Métricas
    col1, col2 = st.columns(2)
    col1.metric("Total Cadastrados", len(reports))
    col2.metric("Encontrados", len(filtered_reports))

    st.markdown("---")

    # Listagem de Documentos
    if not filtered_reports:
        st.warning("Nenhum documento atende aos critérios da sua pesquisa.")
    else:
        for idx, (source_file, content) in enumerate(filtered_reports):
            # Renderiza cada documento de forma elegante usando HTML personalizado
            st.markdown(f"""
            <div class="document-card">
                <div class="document-badge">Documento #{idx + 1}</div>
                <div class="document-filename">📄 {source_file}</div>
                <div class="document-content">{content}</div>
            </div>
            """, unsafe_allow_html=True)
