import sys
from pathlib import Path
import streamlit as st

# Adiciona a raiz do projeto ao sys.path para importações absolutas
project_root = Path(__file__).resolve().parent.parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from src.adapters.tinydb_repo import TinyDbRepo
from src.domain.entities import IncidentReport, Participant

# Configuração da Página para usar toda a largura da tela (Wide mode)
st.set_page_config(
    page_title="ReadRelint - Central de Inteligência",
    page_icon="🔮",
    layout="wide",
    initial_sidebar_state="expanded"
)

def get_participant_field(p, field_name: str, default: str = "") -> str:
    """Extrai campo de participante de forma segura, seja ele dicionário ou objeto Pydantic."""
    if isinstance(p, dict):
        return p.get(field_name) or default
    return getattr(p, field_name, default) or default

# Estilização CSS Premium (Dark Theme, Glows, Glassmorphism, Fontes Customizadas)
st.markdown("""
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
</style>
""", unsafe_allow_html=True)

# Título Principal do Dashboard
st.markdown("""
<div class="hero-container">
    <div class="hero-text">
        <h1 class="hero-title">🔮 Central Analítica de Inteligência</h1>
        <p class="hero-subtitle">Visualização e curadoria em tempo real de documentos e vínculos operacionais</p>
    </div>
</div>
""", unsafe_allow_html=True)

# Carregamento de dados com TinyDbRepo
def load_data():
    db_path = Path("data/relints.json")
    if not db_path.exists():
        db_path = Path("data/homicides.json")
        if not db_path.exists():
            return [], Path("data/relints.json")
    repo = TinyDbRepo(db_path)
    return repo.get_all(), db_path

reports, active_db_path = load_data()

# Função para encontrar vínculos de participantes
def find_vinculos(current_file: str, name: str, doc: str, all_reports: list) -> list:
    vinculos = []
    clean_name = (name or "").strip().lower()
    clean_doc = (doc or "").strip().replace(".", "").replace("-", "")
    
    if not clean_name and not clean_doc:
        return vinculos
        
    for r in all_reports:
        if r.source_file == current_file:
            continue
        parts = r.participants or []
        for p in parts:
            p_name = get_participant_field(p, "name")
            p_doc = get_participant_field(p, "document")
            
            p_clean_name = p_name.strip().lower()
            p_clean_doc = p_doc.strip().replace(".", "").replace("-", "")
            
            if clean_doc and p_clean_doc and clean_doc == p_clean_doc:
                vinculos.append(r.source_file)
                break
            elif clean_name and p_clean_name and clean_name == p_clean_name and len(clean_name) > 4:
                vinculos.append(r.source_file)
                break
    return sorted(list(set(vinculos)))

if not reports:
    st.info("Nenhum RELINT processado até o momento. Por favor, inicie o monitorador de pasta para analisar arquivos.")
else:
    # Sidebar Filtros
    st.sidebar.markdown("### 🔍 Painel de Filtros")
    search_query = st.sidebar.text_input("Buscar nos relatórios:", placeholder="Nome, documento, assunto...")
    
    bm_groups = sorted(list(set(getattr(r, "bm_group", "Outros") or "Outros" for r in reports)))
    selected_groups = st.sidebar.multiselect("Filtrar por Grupo BM:", options=bm_groups, default=bm_groups)

    # Filtragem
    filtered_reports = []
    for r in reports:
        subject = getattr(r, "subject", "Sem Assunto") or "Sem Assunto"
        bm_group = getattr(r, "bm_group", "Outros") or "Outros"
        date_of_fact = getattr(r, "date_of_fact", "Não Informado") or "Não Informado"
        summary = getattr(r, "summary", "") or ""
        content = getattr(r, "content", "") or ""
        
        if bm_group not in selected_groups:
            continue
            
        match_search = True
        if search_query:
            query = search_query.lower()
            participants_text = ""
            for p in (r.participants or []):
                p_name = get_participant_field(p, "name")
                p_nick = get_participant_field(p, "nickname")
                p_doc = get_participant_field(p, "document")
                participants_text += f" {p_name} {p_nick} {p_doc}"
                
            match_search = (
                query in r.source_file.lower() or
                query in subject.lower() or
                query in summary.lower() or
                query in content.lower() or
                query in bm_group.lower() or
                query in date_of_fact.lower() or
                query in participants_text.lower()
            )
            
        if match_search:
            filtered_reports.append(r)

    # Métricas Gerais no Topo
    col_m1, col_m2, col_m3, col_m4 = st.columns(4)
    with col_m1:
        st.markdown(f'<div class="metric-card"><div class="metric-title">Total Processado</div><div class="metric-value">{len(reports)}</div></div>', unsafe_allow_html=True)
    with col_m2:
        st.markdown(f'<div class="metric-card"><div class="metric-title">Resultados Filtrados</div><div class="metric-value" style="color: #60a5fa;">{len(filtered_reports)}</div></div>', unsafe_allow_html=True)
    with col_m3:
        homicides_count = sum(1 for r in reports if getattr(r, "bm_group", "") == "Homicídios")
        st.markdown(f'<div class="metric-card"><div class="metric-title">Casos de Homicídio</div><div class="metric-value" style="color: #a78bfa;">{homicides_count}</div></div>', unsafe_allow_html=True)
    with col_m4:
        robberies_count = sum(1 for r in reports if getattr(r, "bm_group", "") == "Roubos")
        st.markdown(f'<div class="metric-card"><div class="metric-title">Casos de Roubo</div><div class="metric-value" style="color: #f87171;">{robberies_count}</div></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Inicializa estado do selecionado se necessário
    if "selected_idx" not in st.session_state or st.session_state.selected_idx >= len(filtered_reports):
        st.session_state.selected_idx = 0

    # Layout Split Screen (Master-Detail) usando 2 colunas principais (40% e 60%)
    col_left, col_right = st.columns([2, 3])

    with col_left:
        st.markdown("### 📁 Arquivos Processados")
        if not filtered_reports:
            st.warning("Nenhum RELINT corresponde aos filtros de busca.")
        else:
            # Lista de navegação lateral (Master)
            for idx, r in enumerate(filtered_reports):
                subject = getattr(r, "subject", "Sem Assunto") or "Sem Assunto"
                bm_group = getattr(r, "bm_group", "Outros") or "Outros"
                date_of_fact = getattr(r, "date_of_fact", "Não Informado") or "Não Informado"
                
                is_selected = (st.session_state.selected_idx == idx)
                selected_class = "selected" if is_selected else ""
                
                # Badge color
                bg_class = f"badge-{bm_group.lower()}"
                if bg_class not in ["badge-roubos", "badge-furtos", "badge-homicidios", "badge-outros"]:
                    bg_class = "badge-outros"
                
                # Renderiza Card em HTML
                st.markdown(f"""
                <div class="nav-card {selected_class}">
                    <div class="nav-card-title">📄 {r.source_file}</div>
                    <div class="nav-card-subject">{subject}</div>
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <span class="badge-group {bg_class}" style="font-size: 0.65rem; padding: 0.15rem 0.5rem;">{bm_group}</span>
                        <span style="font-size: 0.75rem; color: #64748b;">📅 {date_of_fact}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # Botão invisível sobreposto ou botão de seleção limpo
                if st.button("👁️ Visualizar Detalhes", key=f"select_btn_{idx}", use_container_width=True):
                    st.session_state.selected_idx = idx
                    st.rerun()

    with col_right:
        st.markdown("### 🔍 Detalhes do Documento Selecionado")
        if filtered_reports:
            # Recupera o registro selecionado
            selected_report = filtered_reports[st.session_state.selected_idx]
            
            r_filename = selected_report.source_file
            r_subject = getattr(selected_report, "subject", "Sem Assunto") or "Sem Assunto"
            r_bm_group = getattr(selected_report, "bm_group", "Outros") or "Outros"
            r_date_of_fact = getattr(selected_report, "date_of_fact", "Não Informado") or "Não Informado"
            r_summary = getattr(selected_report, "summary", "Sem resumo gerado.") or "Sem resumo gerado."
            r_content = getattr(selected_report, "content", "") or ""
            r_participants = selected_report.participants or []

            bg_class = f"badge-{r_bm_group.lower()}"
            if bg_class not in ["badge-roubos", "badge-furtos", "badge-homicidios", "badge-outros"]:
                bg_class = "badge-outros"

            # Container de Detalhe Premium
            st.markdown(f"""
            <div class="detail-container">
                <div class="detail-header">
                    <div class="detail-filename">📄 {r_filename}</div>
                    <div style="display: flex; gap: 0.8rem; margin-top: 0.75rem; align-items: center;">
                        <span class="badge-group {bg_class}">{r_bm_group}</span>
                        <span style="color: #64748b; font-size: 0.9rem;">📅 Ocorrido em: <strong>{r_date_of_fact}</strong></span>
                    </div>
                    <div class="detail-subject">{r_subject}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            # Abas para Organização dos Dados
            tab_summary, tab_content, tab_edit = st.tabs([
                "📖 Resumo & Participantes", 
                "📄 Histórico Completo", 
                "✏️ Editar Dados"
            ])

            with tab_summary:
                st.markdown('<div class="detail-section-title">Resumo do Caso</div>', unsafe_allow_html=True)
                st.markdown(f'<div style="font-style: italic; color: #cbd5e1; line-height: 1.6; margin-bottom: 1.5rem;">"{r_summary}"</div>', unsafe_allow_html=True)
                
                st.markdown('<div class="detail-section-title">Participantes Identificados</div>', unsafe_allow_html=True)
                if not r_participants:
                    st.write("*Nenhum participante citado neste relatório.*")
                else:
                    col_p1, col_p2 = st.columns(2)
                    for p_idx, p in enumerate(r_participants):
                        p_name = get_participant_field(p, "name", "Não Informado")
                        p_nick = get_participant_field(p, "nickname", "-")
                        p_doc = get_participant_field(p, "document", "-")
                        
                        # Vínculos operacionais
                        links = find_vinculos(r_filename, p_name, p_doc, reports)
                        links_str = ""
                        if links:
                            links_str = f'<div class="vinculo-badge-alert">🔗 Vinculado a outros arquivos: {", ".join(links)}</div>'
                        
                        # Escolhe coluna alternadamente
                        target_col = col_p1 if p_idx % 2 == 0 else col_p2
                        with target_col:
                            st.markdown(f"""
                            <div class="part-card">
                                <strong>Nome:</strong> {p_name}<br>
                                <strong>Alcunha/Vulgo:</strong> {p_nick}<br>
                                <strong>Documento:</strong> {p_doc}
                                {links_str}
                            </div>
                            """, unsafe_allow_html=True)

            with tab_content:
                st.markdown('<div class="detail-section-title">Histórico Literal do RELINT</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="literal-box">{r_content}</div>', unsafe_allow_html=True)

            with tab_edit:
                st.markdown('<div class="detail-section-title">Editar Informações</div>', unsafe_allow_html=True)
                with st.form(key=f"edit_form_split_{r_filename}"):
                    col_ed1, col_ed2 = st.columns(2)
                    edit_subject = col_ed1.text_input("Assunto Principal:", value=r_subject)
                    edit_date = col_ed1.text_input("Data do Fato:", value=r_date_of_fact)
                    edit_bm_group = col_ed2.selectbox("Grupo BM:", options=["Roubos", "Furtos", "Homicídios", "Outros"], index=["Roubos", "Furtos", "Homicídios", "Outros"].index(r_bm_group) if r_bm_group in ["Roubos", "Furtos", "Homicídios", "Outros"] else 3)
                    
                    edit_summary = st.text_area("Resumo (1 Parágrafo):", value=r_summary, height=100)
                    edit_content = st.text_area("Histórico Completo Literal:", value=r_content, height=180)
                    
                    # Participantes Editáveis
                    st.write("**Editar Participantes:**")
                    updated_participants = []
                    for p_idx, p in enumerate(r_participants):
                        p_name = get_participant_field(p, "name")
                        p_nick = get_participant_field(p, "nickname")
                        p_doc = get_participant_field(p, "document")
                        
                        st.markdown(f"*Participante #{p_idx+1}:*")
                        col_pt1, col_pt2, col_pt3 = st.columns(3)
                        e_name = col_pt1.text_input("Nome", value=p_name, key=f"form_pname_{p_idx}")
                        e_nick = col_pt2.text_input("Alcunha", value=p_nick, key=f"form_pnick_{p_idx}")
                        e_doc = col_pt3.text_input("Doc (CPF/RG)", value=p_doc, key=f"form_pdoc_{p_idx}")
                        
                        if e_name.strip() or e_nick.strip() or e_doc.strip():
                            updated_participants.append(Participant(name=e_name.strip(), nickname=e_nick.strip(), document=e_doc.strip()))
                    
                    # Adicionar novo participante
                    st.markdown("*Adicionar Novo Participante:*")
                    col_new_p1, col_new_p2, col_new_p3 = st.columns(3)
                    new_pname = col_new_p1.text_input("Nome", value="", key="form_newname")
                    new_pnick = col_new_p2.text_input("Alcunha", value="", key="form_newnick")
                    new_pdoc = col_new_p3.text_input("Doc (CPF/RG)", value="", key="form_newdoc")
                    if new_pname.strip() or new_pnick.strip() or new_pdoc.strip():
                        updated_participants.append(Participant(name=new_pname.strip(), nickname=new_pnick.strip(), document=new_pdoc.strip()))

                    submit_btn = st.form_submit_button(label="💾 Salvar Alterações", use_container_width=True)
                    
                    if submit_btn:
                        updated_report = IncidentReport(
                            source_file=r_filename,
                            subject=edit_subject.strip(),
                            date_of_fact=edit_date.strip(),
                            participants=updated_participants,
                            content=edit_content,
                            summary=edit_summary.strip(),
                            bm_group=edit_bm_group,
                            user_edited=True
                        )
                        
                        repo = TinyDbRepo(active_db_path)
                        repo.delete_by_source_file(r_filename)
                        repo.save(updated_report)
                        
                        st.success(f"Alterações no arquivo '{r_filename}' salvas com sucesso!")
                        st.rerun()
