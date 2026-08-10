import streamlit as st

CSS_STYLES = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');
    
    html, body, [data-testid="stAppViewContainer"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
        background-color: #080a10;
        color: #f1f5f9;
    }
    
    /* Header Principal Ultra Moderno */
    .hero-container {
        padding: 2rem;
        background: linear-gradient(135deg, #1e1b4b 0%, #030712 100%);
        border-radius: 16px;
        margin-bottom: 2rem;
        border: 1px solid #2e2a75;
        box-shadow: 0 10px 25px -5px rgba(99, 102, 241, 0.15);
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    
    .hero-text {
        text-align: left;
    }

    .hero-title {
        font-size: 2.2rem;
        font-weight: 700;
        background: linear-gradient(135deg, #818cf8 0%, #3b82f6 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0;
    }
    
    .hero-subtitle {
        color: #94a3b8;
        font-size: 1rem;
        margin-top: 0.5rem;
        font-weight: 400;
    }

    /* Cards de Métricas Premium */
    .metric-card {
        background: #111422;
        border: 1px solid #1f243a;
        padding: 1.25rem;
        border-radius: 12px;
        text-align: center;
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.2);
    }
    .metric-title {
        font-size: 0.8rem;
        color: #64748b;
        text-transform: uppercase;
        font-weight: 600;
        letter-spacing: 0.05em;
    }
    .metric-value {
        font-size: 2rem;
        font-weight: 700;
        color: #6366f1;
        margin-top: 0.25rem;
    }

    /* Cards de Navegação (Esquerda) */
    .nav-card {
        padding: 1.2rem;
        border-radius: 12px;
        margin-bottom: 0.8rem;
        border: 1px solid #1e293b;
        background-color: #0f172a;
        transition: all 0.2s ease-in-out;
        cursor: pointer;
    }
    
    .nav-card.selected {
        border-color: #6366f1;
        background: linear-gradient(135deg, #13172e 0%, #0f172a 100%);
        box-shadow: 0 0 15px rgba(99, 102, 241, 0.15);
    }
    
    .nav-card-title {
        font-size: 0.95rem;
        font-weight: 600;
        color: #f1f5f9;
        margin-bottom: 0.4rem;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }

    .nav-card-subject {
        font-size: 0.8rem;
        color: #94a3b8;
        margin-bottom: 0.6rem;
        line-height: 1.4;
        display: -webkit-box;
        -webkit-line-clamp: 2;
        -webkit-box-orient: vertical;
        overflow: hidden;
    }

    /* Detalhes do Relatório (Direita) */
    .detail-container {
        background-color: #0f172a;
        border: 1px solid #1e293b;
        border-radius: 16px;
        padding: 2rem;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
        min-height: 600px;
    }

    .detail-header {
        border-bottom: 1px solid #1e293b;
        padding-bottom: 1.5rem;
        margin-bottom: 1.5rem;
    }

    .detail-filename {
        font-size: 1.6rem;
        font-weight: 700;
        color: #ffffff;
    }

    .detail-subject {
        font-size: 1.15rem;
        font-weight: 500;
        color: #38bdf8;
        margin-top: 0.5rem;
    }

    /* Badges Operacionais */
    .badge-group {
        display: inline-flex;
        align-items: center;
        padding: 0.3rem 0.8rem;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 600;
        color: #ffffff;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .badge-roubos { background: linear-gradient(135deg, #e11d48, #be123c); }
    .badge-furtos { background: linear-gradient(135deg, #d97706, #b45309); }
    .badge-homicidios { background: linear-gradient(135deg, #7c3aed, #6d28d9); }
    .badge-outros { background: linear-gradient(135deg, #4b5563, #374151); }

    .detail-section-title {
        font-size: 1.1rem;
        font-weight: 600;
        color: #818cf8;
        margin-top: 1.5rem;
        margin-bottom: 0.75rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }

    /* Box de Histórico Literal */
    .literal-box {
        font-family: 'JetBrains Mono', monospace;
        background-color: #05070f;
        padding: 1.25rem;
        border-radius: 10px;
        border: 1px solid #1e293b;
        font-size: 0.9rem;
        line-height: 1.6;
        color: #e2e8f0;
        white-space: pre-wrap;
        max-height: 450px;
        overflow-y: auto;
    }

    /* Card de Participantes */
    .part-card {
        background-color: #070a13;
        border: 1px solid #1e293b;
        border-radius: 8px;
        padding: 1rem;
        margin-bottom: 0.75rem;
        transition: border-color 0.2s;
    }
    .part-card:hover {
        border-color: #4f46e5;
    }

    .vinculo-badge-alert {
        background-color: #1e1b4b;
        border: 1px solid #3730a3;
        color: #a5b4fc;
        padding: 0.4rem 0.8rem;
        border-radius: 6px;
        font-size: 0.8rem;
        margin-top: 0.6rem;
        display: inline-flex;
        align-items: center;
        gap: 0.4rem;
        font-weight: 500;
    }
    /* Card de Dossiê de Pessoas (Participantes) */
    .dossier-card {
        background: linear-gradient(145deg, #0d1322 0%, #070a14 100%);
        border: 1px solid #1e293b;
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
        transition: transform 0.2s, border-color 0.2s;
    }
    .dossier-card:hover {
        transform: translateY(-2px);
        border-color: #6366f1;
    }
    .dossier-header {
        display: flex;
        align-items: center;
        gap: 1rem;
        margin-bottom: 1rem;
        border-bottom: 1px solid #1e293b;
        padding-bottom: 0.75rem;
    }
    .dossier-avatar {
        width: 48px;
        height: 48px;
        border-radius: 50%;
        background: linear-gradient(135deg, #4f46e5 0%, #06b6d4 100%);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.4rem;
        font-weight: 700;
        color: white;
        flex-shrink: 0;
    }
    .dossier-name {
        font-size: 1.2rem;
        font-weight: 700;
        color: #f8fafc;
        margin: 0;
    }
    .dossier-vulgo {
        font-size: 0.9rem;
        color: #fbbf24;
        font-weight: 600;
    }
    .dossier-doc {
        font-size: 0.85rem;
        color: #94a3b8;
        font-family: 'JetBrains Mono', monospace;
    }
    
    /* Card de Município / Mancha Territorial */
    .muni-card {
        background: #0f172a;
        border: 1px solid #1e293b;
        border-radius: 12px;
        padding: 1.25rem;
        margin-bottom: 1rem;
        box-shadow: 0 4px 10px rgba(0,0,0,0.2);
    }
    .muni-title {
        font-size: 1.3rem;
        font-weight: 700;
        color: #38bdf8;
        margin-bottom: 0.5rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    .muni-badge {
        background-color: #0284c7;
        color: white;
        padding: 0.2rem 0.6rem;
        border-radius: 9999px;
        font-size: 0.8rem;
        font-weight: 600;
    }

    /* Card Estatístico de Crimes */
    .crime-card {
        background: linear-gradient(135deg, #1e1b4b 0%, #0f172a 100%);
        border: 1px solid #312e81;
        border-radius: 12px;
        padding: 1.25rem;
        text-align: center;
        margin-bottom: 1rem;
    }
    .crime-title {
        font-size: 0.9rem;
        color: #a5b4fc;
        font-weight: 600;
        text-transform: uppercase;
    }
    .crime-count {
        font-size: 2.2rem;
        font-weight: 800;
        color: #f43f5e;
        margin-top: 0.3rem;
    }
</style>
"""

def inject_styles():
    """Injeta as folhas de estilo personalizadas no Streamlit."""
    st.markdown(CSS_STYLES, unsafe_allow_html=True)

def get_badge_class(bm_group: str) -> str:
    """Retorna a classe CSS correspondente ao grupo BM."""
    val = (bm_group or 'Outros').lower()
    if 'roubo' in val:
        return "badge-roubos"
    elif 'furto' in val:
        return "badge-furtos"
    elif 'homic' in val or 'pris' in val or 'tráf' in val or 'traf' in val:
        return "badge-homicidios"
    return "badge-outros"

