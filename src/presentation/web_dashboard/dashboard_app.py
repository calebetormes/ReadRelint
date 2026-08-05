import sys
from pathlib import Path
import streamlit as st

# Adiciona a raiz do projeto ao sys.path para importações absolutas
project_root = Path(__file__).resolve().parent.parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from src.adapters.tinydb_repo import TinyDbRepo
from src.domain.entities import IncidentReport, Participant, BmGroup
from src.presentation.web_dashboard.styles import inject_styles, get_badge_class
from src.presentation.web_dashboard.helpers import (
    get_participant_field,
    load_data,
    find_vinculos,
    filter_reports
)

# Configuração da Página para usar toda a largura da tela (Wide mode)
st.set_page_config(
    page_title="ReadRelint - Central de Inteligência",
    page_icon="🔮",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilização CSS Premium
inject_styles()

# Título Principal do Dashboard
st.markdown("""
<div class="hero-container">
    <div class="hero-text">
        <h1 class="hero-title">🔮 Central Analítica de Inteligência</h1>
        <p class="hero-subtitle">Visualização e curadoria em tempo real de documentos e vínculos operacionais</p>
    </div>
</div>
""", unsafe_allow_html=True)

reports, active_db_path = load_data()

if not reports:
    st.info("Nenhum RELINT processado até o momento. Por favor, inicie o monitorador de pasta para analisar arquivos.")
else:
    # Sidebar Filtros
    st.sidebar.markdown("### 🔍 Painel de Filtros")
    search_query = st.sidebar.text_input("Buscar nos relatórios:", placeholder="Nome, documento, assunto...")
    
    # Extrair os grupos BM existentes ou usar o Enum
    all_bm_groups = [g.value for g in BmGroup]
    selected_groups = st.sidebar.multiselect("Filtrar por Grupo BM:", options=all_bm_groups, default=all_bm_groups)

    # Filtragem
    filtered_reports = filter_reports(reports, search_query, selected_groups)

    # Métricas Gerais no Topo
    col_m1, col_m2, col_m3, col_m4 = st.columns(4)
    with col_m1:
        st.markdown(f'<div class="metric-card"><div class="metric-title">Total Processado</div><div class="metric-value">{len(reports)}</div></div>', unsafe_allow_html=True)
    with col_m2:
        st.markdown(f'<div class="metric-card"><div class="metric-title">Resultados Filtrados</div><div class="metric-value" style="color: #60a5fa;">{len(filtered_reports)}</div></div>', unsafe_allow_html=True)
    with col_m3:
        homicides_count = sum(1 for r in reports if getattr(r, "bm_group", "") == "Homicídios") # TODO: Ajustar pra nova taxonomia, ou usar len de Prisao Traico
        st.markdown(f'<div class="metric-card"><div class="metric-title">Homicídios (Legado)</div><div class="metric-value" style="color: #a78bfa;">{homicides_count}</div></div>', unsafe_allow_html=True)
    with col_m4:
        robberies_count = sum(1 for r in reports if getattr(r, "bm_group", "") == BmGroup.ROUBO_ESTABELECIMENTO.value)
        st.markdown(f'<div class="metric-card"><div class="metric-title">Roubo a Estabelecimento</div><div class="metric-value" style="color: #f87171;">{robberies_count}</div></div>', unsafe_allow_html=True)

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
                bm_group = getattr(r, "bm_group", "Outros")
                if hasattr(bm_group, "value"):
                    bm_group = bm_group.value
                elif not bm_group:
                    bm_group = "Outros"
                
                date_of_fact = getattr(r, "modification_date_history", "Não Informado") or "Não Informado"
                
                is_selected = (st.session_state.selected_idx == idx)
                selected_class = "selected" if is_selected else ""
                
                bg_class = get_badge_class(bm_group)
                
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
            
            r_bm_group = getattr(selected_report, "bm_group", "Outros")
            if hasattr(r_bm_group, "value"): r_bm_group = r_bm_group.value
            
            r_date_of_fact = getattr(selected_report, "modification_date_history", "Não Informado") or "Não Informado"
            r_summary = getattr(selected_report, "summary", "Sem resumo gerado.") or "Sem resumo gerado."
            r_content = getattr(selected_report, "content", "") or ""
            r_participants = selected_report.participants or []

            bg_class = get_badge_class(r_bm_group)

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
                        p_type = get_participant_field(p, "participation_type", "-")
                        
                        # Vínculos operacionais
                        links = find_vinculos(r_filename, p_name, p_doc, reports)
                        links_str = ""
                        if links:
                            links_str = f'<div class="vinculo-badge-alert">🔗 Vinculado a outros arquivos: {", ".join(links)}</div>'
                        
                        target_col = col_p1 if p_idx % 2 == 0 else col_p2
                        with target_col:
                            st.markdown(f"""
                            <div class="part-card">
                                <strong>Nome:</strong> {p_name}<br>
                                <strong>Tipo de Envolvimento:</strong> {p_type}<br>
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
                    edit_date = col_ed1.text_input("Data do Histórico:", value=r_date_of_fact)
                    
                    bm_options = [g.value for g in BmGroup]
                    edit_bm_group = col_ed2.selectbox("Grupo BM:", options=bm_options, index=bm_options.index(r_bm_group) if r_bm_group in bm_options else 7)
                    
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
                            modification_date_history=edit_date.strip(),
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
