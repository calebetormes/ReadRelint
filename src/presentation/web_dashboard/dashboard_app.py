import sys
import textwrap
from pathlib import Path
import streamlit as st


# Adiciona a raiz do projeto ao sys.path para importações absolutas
project_root = Path(__file__).resolve().parent.parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from src.adapters.sqlite_repo import SqliteRepo
from src.domain.entities import IncidentReport, Participant, BmGroup
from src.application.text_cleaner import clean_relint_text
from src.presentation.web_dashboard.styles import inject_styles, get_badge_class

from src.presentation.web_dashboard.helpers import (
    clean_html,
    get_participant_field,
    get_report_date_of_fact,
    get_report_time_of_fact,
    get_report_structured_address,
    get_report_map_info,
    load_data,
    find_vinculos,
    filter_reports,
    get_persons_data,
    get_municipalities_data,
    get_crime_stats
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
        <p class="hero-subtitle">Plataforma unificada para curadoria de relatórios, dossiês de pessoas, mancha territorial e análise de crimes</p>
    </div>
</div>
""", unsafe_allow_html=True)

reports, active_db_path = load_data()
persons_data = get_persons_data(reports) if reports else []

if not reports:
    st.info("Nenhum RELINT processado até o momento. Por favor, inicie o monitorador de pasta para analisar arquivos.")
else:
    # Definição das 4 Abas Principais
    tab_relints, tab_participants, tab_municipalities, tab_crimes = st.tabs([
        "📄 RELINTs (Edição)",
        "👤 Participantes",
        "🗺️ Municípios",
        "🚨 Crimes (Grupo BM)"
    ])

    # =========================================================================
    # ABA 1: RELINTS (EDIÇÃO E MASTER-DETAIL)
    # =========================================================================
    with tab_relints:
        st.markdown("### 📄 Gestão e Curadoria de RELINTs")
        
        # Filtros no topo da aba
        col_f1, col_f2 = st.columns([2, 1])
        with col_f1:
            search_query = st.text_input("🔍 Buscar nos relatórios:", placeholder="Nome, CPF/RG, assunto, texto...", key="relint_search")
        with col_f2:
            all_bm_groups = [g.value for g in BmGroup]
            selected_groups = st.multiselect("Filtrar por Grupo BM:", options=all_bm_groups, default=all_bm_groups, key="relint_bm_filter")

        filtered_reports = filter_reports(reports, search_query, selected_groups)

        # Métricas no topo da aba
        col_m1, col_m2, col_m3, col_m4 = st.columns(4)
        with col_m1:
            st.markdown(f'<div class="metric-card"><div class="metric-title">Total Processado</div><div class="metric-value">{len(reports)}</div></div>', unsafe_allow_html=True)
        with col_m2:
            st.markdown(f'<div class="metric-card"><div class="metric-title">Resultados Filtrados</div><div class="metric-value" style="color: #60a5fa;">{len(filtered_reports)}</div></div>', unsafe_allow_html=True)
        with col_m3:
            traffic_count = sum(1 for r in reports if getattr(r, "bm_group", "") in [BmGroup.PRISAO_TRAFICO.value, "Prisão por Tráfico"])
            st.markdown(f'<div class="metric-card"><div class="metric-title">Prisão por Tráfico</div><div class="metric-value" style="color: #a78bfa;">{traffic_count}</div></div>', unsafe_allow_html=True)
        with col_m4:
            robberies_count = sum(1 for r in reports if "Roubo" in str(getattr(r, "bm_group", "")))
            st.markdown(f'<div class="metric-card"><div class="metric-title">Total de Roubos</div><div class="metric-value" style="color: #f87171;">{robberies_count}</div></div>', unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        if "selected_idx" not in st.session_state:
            st.session_state.selected_idx = 0

        if filtered_reports:
            if st.session_state.selected_idx >= len(filtered_reports) or st.session_state.selected_idx < 0:
                st.session_state.selected_idx = 0

        # Layout Split Screen (Master-Detail)
        col_left, col_right = st.columns([2, 3])

        with col_left:
            st.markdown("#### 📁 Lista de Arquivos Processados")
            if not filtered_reports:
                st.warning("Nenhum RELINT corresponde aos filtros de busca.")
            else:
                for idx, r in enumerate(filtered_reports):
                    subject = getattr(r, "subject", "Sem Assunto") or "Sem Assunto"
                    bm_group = getattr(r, "bm_group", "Outros")
                    if hasattr(bm_group, "value"):
                        bm_group = bm_group.value
                    elif not bm_group:
                        bm_group = "Outros"
                    
                    date_of_fact = get_report_date_of_fact(r)
                    is_selected = (st.session_state.selected_idx == idx)
                    selected_class = "selected" if is_selected else ""
                    bg_class = get_badge_class(bm_group)
                    
                    st.markdown(clean_html(f"""
                    <div class="nav-card {selected_class}">
                        <div class="nav-card-title">📄 {r.source_file}</div>
                        <div class="nav-card-subject">{subject}</div>
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <span class="badge-group {bg_class}" style="font-size: 0.65rem; padding: 0.15rem 0.5rem;">{bm_group}</span>
                            <span style="font-size: 0.75rem; color: #64748b;">📅 {date_of_fact}</span>
                        </div>
                    </div>
                    """), unsafe_allow_html=True)

                    if st.button("👁️ Selecionar para Edição", key=f"select_btn_{idx}", use_container_width=True):
                        st.session_state.selected_idx = idx
                        st.rerun()

        with col_right:
            st.markdown("#### 🔍 Visualização e Edição de Detalhes")
            if not filtered_reports:
                st.info("Nenhum relatório encontrado para exibição de detalhes.")
            else:
                try:
                    selected_report = filtered_reports[st.session_state.selected_idx]
                except Exception:
                    st.session_state.selected_idx = 0
                    selected_report = filtered_reports[0]

                
                r_filename = selected_report.source_file
                r_subject = getattr(selected_report, "subject", "Sem Assunto") or "Sem Assunto"
                r_bm_group = getattr(selected_report, "bm_group", "Outros")
                if hasattr(r_bm_group, "value"): r_bm_group = r_bm_group.value
                
                r_date_of_fact = get_report_date_of_fact(selected_report)
                r_time_of_fact = get_report_time_of_fact(selected_report)
                r_addr = get_report_structured_address(selected_report)
                map_info = get_report_map_info(selected_report)

                if len(map_info) == 4:
                    r_map_url, r_coords, precision_level, precision_label = map_info
                elif len(map_info) == 3:
                    r_map_url, r_coords, flag = map_info
                    if flag == "exact_coords" or flag is True:
                        precision_level, precision_label = "exact_coords", "Alta Precisão (Coordenadas Exatas)"
                    elif flag == "direct_link":
                        precision_level, precision_label = "direct_link", "Precisão Média (Link Citado no RELINT)"
                    else:
                        precision_level, precision_label = "address_inferred", "Precisão Estimada (Busca por Endereço)"
                else:
                    r_map_url = map_info[0] if len(map_info) > 0 else ""
                    r_coords = map_info[1] if len(map_info) > 1 else ""
                    precision_level, precision_label = "unknown", "Sem Dados de Localização"


                r_summary = getattr(selected_report, "summary", "Sem resumo gerado.") or "Sem resumo gerado."
                r_content = clean_relint_text(getattr(selected_report, "content", "") or "")
                r_participants = selected_report.participants or []

                bg_class = get_badge_class(r_bm_group)

                if precision_level == "exact_coords":
                    map_link_html = f'<a href="{r_map_url}" target="_blank" style="background: #059669; color: white; padding: 0.25rem 0.65rem; border-radius: 6px; text-decoration: none; font-size: 0.8rem; font-weight: 700; border: 1px solid #34d399;">🗺️ Abrir Google Maps (Ponto Exato)</a>'
                    coords_html = f'<span style="color: #34d399; font-size: 0.88rem; font-family: monospace; font-weight: 700;">📍 Coordenadas Exatas: {r_coords} | <span style="font-weight: 400; font-family: sans-serif;">Nível: {precision_label}</span></span>'
                elif precision_level == "direct_link":
                    map_link_html = f'<a href="{r_map_url}" target="_blank" style="background: #0284c7; color: white; padding: 0.25rem 0.65rem; border-radius: 6px; text-decoration: none; font-size: 0.8rem; font-weight: 600; border: 1px solid #38bdf8;">🗺️ Abrir Google Maps (Link Citado)</a>'
                    coords_html = f'<span style="color: #38bdf8; font-size: 0.85rem;">📍 Link direto citado no RELINT | <span style="font-weight: 400;">Nível: {precision_label}</span></span>'
                elif precision_level == "address_inferred":
                    map_link_html = f'<a href="{r_map_url}" target="_blank" style="background: #d97706; color: white; padding: 0.25rem 0.65rem; border-radius: 6px; text-decoration: none; font-size: 0.8rem; font-weight: 600; border: 1px solid #f59e0b;">🗺️ Abrir Google Maps (Gerado p/ Endereço)</a>'
                    coords_html = f'<span style="color: #fbbf24; font-size: 0.82rem; font-style: italic;">📍 Endereço estimado | Nível: {precision_label}</span>'
                else:
                    map_link_html = ""
                    coords_html = f'<span style="color: #94a3b8; font-size: 0.82rem; font-style: italic;">📍 {precision_label}</span>'

                coords_block = f'<div style="margin-top: 0.35rem;">{coords_html}</div>'



                st.markdown(clean_html(f"""
                <div class="detail-container">
                    <div class="detail-header">
                        <div class="detail-filename">📄 {r_filename}</div>
                        <div style="display: flex; gap: 0.8rem; margin-top: 0.75rem; align-items: center; flex-wrap: wrap;">
                            <span class="badge-group {bg_class}">{r_bm_group}</span>
                            <span style="color: #64748b; font-size: 0.9rem;">📅 Data: <strong>{r_date_of_fact}</strong></span>
                            <span style="color: #64748b; font-size: 0.9rem;">⏰ Hora: <strong>{r_time_of_fact}</strong></span>
                            {map_link_html}
                        </div>
                        <div style="font-size: 0.85rem; color: #94a3b8; margin-top: 0.5rem;">
                            📍 <strong>Localidade:</strong> {r_addr['municipality']} | <strong>Bairro:</strong> {r_addr['neighborhood']} | <strong>Logradouro:</strong> {r_addr['street']}, nº {r_addr['number']}
                        </div>
                        {coords_block}
                        <div class="detail-subject">{r_subject}</div>
                    </div>
                </div>
                """), unsafe_allow_html=True)





                subtab_summary, subtab_images, subtab_content, subtab_edit = st.tabs([
                    "📖 Resumo & Participantes", 
                    "🖼️ Imagens do Fato",
                    "📄 Histórico Completo", 
                    "✏️ Editar Dados"
                ])

                with subtab_summary:
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

                            links = find_vinculos(r_filename, p_name, p_doc, reports)
                            links_str = f'<div class="vinculo-badge-alert">🔗 Vinculado a outros arquivos: {", ".join(links)}</div>' if links else ""
                            
                            target_col = col_p1 if p_idx % 2 == 0 else col_p2
                            with target_col:
                                st.markdown(clean_html(f"""
                                <div class="part-card">
                                    <strong>Nome:</strong> {p_name}<br>
                                    <strong>Tipo de Envolvimento:</strong> {p_type}<br>
                                    <strong>Alcunha/Vulgo:</strong> {p_nick}<br>
                                    <strong>Documento:</strong> {p_doc}
                                    {links_str}
                                </div>
                                """), unsafe_allow_html=True)

                with subtab_images:
                    st.markdown('<div class="detail-section-title">🖼️ Galeria de Imagens do Fato / Cenas do Local</div>', unsafe_allow_html=True)
                    r_images = getattr(selected_report, "images", []) or []
                    if not r_images:
                        st.info("Nenhuma imagem geral de cena ou evidência registrada para este RELINT.")
                    else:
                        cols_img = st.columns(3)
                        for i_idx, img_item in enumerate(r_images):
                            if isinstance(img_item, dict):
                                img_path = img_item.get("path") or img_item.get("file_path") or ""
                                img_caption = img_item.get("caption") or f"Imagem #{i_idx+1}"
                            else:
                                img_path = str(img_item)
                                img_caption = f"Imagem #{i_idx+1}"

                            if img_path and Path(img_path).exists():
                                with cols_img[i_idx % 3]:
                                    st.image(img_path, caption=img_caption, use_container_width=True)


                with subtab_content:
                    st.markdown('<div class="detail-section-title">Histórico Literal do RELINT</div>', unsafe_allow_html=True)
                    st.markdown(f'<div class="literal-box">{r_content}</div>', unsafe_allow_html=True)

                with subtab_edit:
                    st.markdown('<div class="detail-section-title">Editar Informações e Salvar</div>', unsafe_allow_html=True)
                    with st.form(key=f"edit_form_{r_filename}"):
                        col_ed1, col_ed2 = st.columns(2)
                        edit_subject = (col_ed1.text_input("Assunto Principal:", value=r_subject) or "").strip()
                        edit_date = (col_ed1.text_input("Data do Histórico:", value=r_date_of_fact) or "").strip()
                        
                        bm_options = [g.value for g in BmGroup]
                        edit_bm_group = col_ed2.selectbox("Grupo BM:", options=bm_options, index=bm_options.index(r_bm_group) if r_bm_group in bm_options else 7)
                        
                        edit_summary = (st.text_area("Resumo (1 Parágrafo):", value=r_summary, height=100) or "").strip()
                        edit_content = st.text_area("Histórico Completo Literal:", value=r_content, height=180)
                        
                        st.write("**Editar Participantes:**")
                        updated_participants = []
                        for p_idx, p in enumerate(r_participants):
                            p_name = get_participant_field(p, "name")
                            p_nick = get_participant_field(p, "nickname")
                            p_doc = get_participant_field(p, "document")
                            p_photo = get_participant_field(p, "photo_path")
                            
                            st.markdown(f"*Participante #{p_idx+1}:*")
                            col_pt1, col_pt2, col_pt3 = st.columns(3)
                            e_name = col_pt1.text_input("Nome", value=p_name, key=f"form_pname_{p_idx}")
                            e_nick = col_pt2.text_input("Alcunha", value=p_nick, key=f"form_pnick_{p_idx}")
                            e_doc = col_pt3.text_input("Doc (CPF/RG)", value=p_doc, key=f"form_pdoc_{p_idx}")
                            
                            if e_name.strip() or e_nick.strip() or e_doc.strip():
                                updated_participants.append(Participant(name=e_name.strip(), nickname=e_nick.strip(), document=e_doc.strip(), photo_path=p_photo))
                        
                        st.markdown("*Adicionar Novo Participante:*")
                        col_new_p1, col_new_p2, col_new_p3 = st.columns(3)
                        new_pname = col_new_p1.text_input("Nome", value="", key="form_newname")
                        new_pnick = col_new_p2.text_input("Alcunha", value="", key="form_newnick")
                        new_pdoc = col_new_p3.text_input("Doc (CPF/RG)", value="", key="form_newdoc")
                        if new_pname.strip() or new_pnick.strip() or new_pdoc.strip():
                            updated_participants.append(Participant(name=new_pname.strip(), nickname=new_pnick.strip(), document=new_pdoc.strip()))
 
                        submit_btn = st.form_submit_button(label="💾 Salvar Alterações no Banco", use_container_width=True)
                        
                        if submit_btn:
                            updated_report = IncidentReport(
                                source_file=r_filename,
                                subject=edit_subject,
                                modification_date_history=edit_date,
                                participants=updated_participants,
                                images=getattr(selected_report, "images", []),
                                content=edit_content,
                                summary=edit_summary,
                                bm_group=edit_bm_group,
                                user_edited=True
                            )
                            
                            repo = SqliteRepo(active_db_path)
                            repo.delete_by_source_file(r_filename)
                            repo.save(updated_report)
                            
                            st.success(f"Alterações no arquivo '{r_filename}' salvas com sucesso!")
                            st.rerun()

    # =========================================================================
    # ABA 2: PARTICIPANTES (DOSSIÊ DE PESSOAS)
    # =========================================================================
    with tab_participants:
        st.markdown("### 👤 Dossiê Cadastral de Participantes")
        st.markdown("Ficha unificada de pessoas registradas em relatórios de inteligência, vulgos, documentos e redes de vínculos.")

        persons_data = get_persons_data(reports)

        p_search = st.text_input("🔍 Pesquisar indivíduo:", placeholder="Nome, alcunha/vulgo ou CPF/RG...", key="person_search")

        # Filtro de busca
        filtered_persons = []
        if p_search:
            q = p_search.lower()
            for p in persons_data:
                name_match = q in p["name"].lower()
                alias_match = any(q in a.lower() for a in p["aliases"])
                doc_match = any(q in d.lower() for d in p["documents"])
                if name_match or alias_match or doc_match:
                    filtered_persons.append(p)
        else:
            filtered_persons = persons_data

        # Métricas da aba Participantes
        col_pm1, col_pm2, col_pm3, col_pm4 = st.columns(4)
        with col_pm1:
            st.markdown(f'<div class="metric-card"><div class="metric-title">Total de Indivíduos</div><div class="metric-value">{len(persons_data)}</div></div>', unsafe_allow_html=True)
        with col_pm2:
            with_aliases = sum(1 for p in persons_data if p["aliases"])
            st.markdown(f'<div class="metric-card"><div class="metric-title">Possuem Alcunha/Vulgo</div><div class="metric-value" style="color: #fbbf24;">{with_aliases}</div></div>', unsafe_allow_html=True)
        with col_pm3:
            with_docs = sum(1 for p in persons_data if p["documents"])
            st.markdown(f'<div class="metric-card"><div class="metric-title">Possuem Documento</div><div class="metric-value" style="color: #34d399;">{with_docs}</div></div>', unsafe_allow_html=True)
        with col_pm4:
            linked_multi = sum(1 for p in persons_data if len(p["linked_relints"]) > 1)
            st.markdown(f'<div class="metric-card"><div class="metric-title">Vínculos Múltiplos</div><div class="metric-value" style="color: #f87171;">{linked_multi}</div></div>', unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        if not filtered_persons:
            st.info("Nenhum participante encontrado com os termos pesquisados.")
        else:
            col_d1, col_d2 = st.columns(2)
            for idx, p in enumerate(filtered_persons):
                target_col = col_d1 if idx % 2 == 0 else col_d2
                with target_col:
                    first_letter = p["name"][0].upper() if p["name"] else "👤"
                    aliases_str = f"Apelido / Vulgo: <strong>{', '.join(p['aliases'])}</strong>" if p["aliases"] else "Sem vulgo cadastrado"
                    docs_str = f"Documento: <strong>{', '.join(p['documents'])}</strong>" if p["documents"] else "Sem documento"
                    types_str = f"Envolvimento: {', '.join(set(p['participation_types']))}" if p.get("participation_types") else ""
                    
                    multi_badge = ""
                    if len(p["linked_relints"]) > 1:
                        multi_badge = f'<div class="vinculo-badge-alert">🚨 Alerta: Citado em {len(p["linked_relints"])} RELINTs diferentes!</div>'

                    st.markdown(clean_html(f"""
                    <div class="dossier-card">
                        <div class="dossier-header">
                            <div class="dossier-avatar">{first_letter}</div>
                            <div>
                                <div class="dossier-name">{p["name"]}</div>
                                <div class="dossier-vulgo">{aliases_str}</div>
                                <div class="dossier-doc">{docs_str}</div>
                            </div>
                        </div>
                        <div style="font-size: 0.85rem; color: #cbd5e1; margin-top: 0.5rem;">
                            {types_str}
                            {multi_badge}
                        </div>
                    </div>
                    """), unsafe_allow_html=True)
                    


                    with st.expander(f"📁 Ver RELINTs vinculados ({len(p['linked_relints'])})"):
                        for relint_file in p["linked_relints"]:
                            st.write(f"- 📄 `{relint_file}`")


    # =========================================================================
    # ABA 3: MUNICÍPIOS (MANCHA TERRITORIAL)
    # =========================================================================
    with tab_municipalities:
        st.markdown("### 🗺️ Mancha Criminal Territorial por Município")
        st.markdown("Mapeamento espacial das ocorrências por cidade e agrupamento estatístico.")

        muni_data = get_municipalities_data(reports)

        # Ordenar municípios por número de relatórios vinculados
        muni_data.sort(key=lambda m: len(m["linked_relints"]), reverse=True)

        col_mm1, col_mm2, col_mm3 = st.columns(3)
        with col_mm1:
            st.markdown(f'<div class="metric-card"><div class="metric-title">Municípios Mapeados</div><div class="metric-value">{len(muni_data)}</div></div>', unsafe_allow_html=True)
        with col_mm2:
            top_muni = muni_data[0]["name"] if muni_data else "N/A"
            st.markdown(f'<div class="metric-card"><div class="metric-title">Maior Incidência</div><div class="metric-value" style="color: #38bdf8;">{top_muni}</div></div>', unsafe_allow_html=True)
        with col_mm3:
            total_cases = sum(len(m["linked_relints"]) for m in muni_data)
            st.markdown(f'<div class="metric-card"><div class="metric-title">Ocorrências Territorializadas</div><div class="metric-value" style="color: #6366f1;">{total_cases}</div></div>', unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        muni_search = st.text_input("🔍 Pesquisar cidade:", placeholder="Nome da cidade...", key="muni_search")

        filtered_munis = [m for m in muni_data if muni_search.lower() in m["name"].lower()] if muni_search else muni_data

        col_mu1, col_mu2 = st.columns(2)
        for idx, m in enumerate(filtered_munis):
            target_col = col_mu1 if idx % 2 == 0 else col_mu2
            with target_col:
                stats_html = ""
                for grp, count in m["stats_by_group"].items():
                    stats_html += f'<span class="badge-group badge-outros" style="margin-right: 0.3rem; margin-bottom: 0.3rem;">{grp}: {count}</span>'

                st.markdown(clean_html(f"""
                <div class="muni-card">
                    <div class="muni-title">
                        📍 {m["name"]} - {m["state"]}
                        <span class="muni-badge">{len(m["linked_relints"])} Ocorrências</span>
                    </div>
                    <div style="margin-top: 0.75rem;">
                        {stats_html}
                    </div>
                </div>
                """), unsafe_allow_html=True)

                with st.expander(f"📄 Ver relatórios de {m['name']}"):
                    for rf in m["linked_relints"]:
                        st.write(f"- 📄 `{rf}`")

    # =========================================================================
    # ABA 4: CRIMES (PAINEL ANALÍTICO DO GRUPO BM)
    # =========================================================================
    with tab_crimes:
        st.markdown("### 🚨 Painel Analítico de Ocorrências por Grupo BM")
        st.markdown("Estatísticas e análise detalhada dos enquadramentos criminais registrados.")

        crime_info = get_crime_stats(reports)
        group_counts = crime_info["group_counts"]
        reports_by_group = crime_info["reports_by_group"]

        # Gráfico de barras estatístico nativo do Streamlit
        st.markdown("#### 📊 Distribuição de Fatos por Grupo BM")
        if group_counts:
            st.bar_chart(group_counts)

        st.markdown("---")

        # Seleção detalhada por Grupo BM
        selected_crime = st.selectbox("Selecione um Grupo BM para explorar:", options=list(BmGroup.__members__.values()))

        crime_reports = reports_by_group.get(selected_crime, [])

        st.markdown(f"#### 📄 Ocorrências Registradas em **{selected_crime}** ({len(crime_reports)})")

        if not crime_reports:
            st.info(f"Nenhum relatório classificado como '{selected_crime}'.")
        else:
            for r in crime_reports:
                r_subj = getattr(r, "subject", "Sem Assunto") or "Sem Assunto"
                r_sum = getattr(r, "summary", "Sem resumo.") or "Sem resumo."
                r_date = get_report_date_of_fact(r)
                r_time = get_report_time_of_fact(r)
                r_addr = get_report_structured_address(r)

                parts_names = [get_participant_field(p, "name") for p in (r.participants or []) if get_participant_field(p, "name")]
                parts_str = ", ".join(parts_names) if parts_names else "Nenhum civil citado"

                with st.container():
                    st.markdown(clean_html(f"""
                    <div class="part-card">
                        <div style="font-size: 1.1rem; font-weight: 700; color: #38bdf8;">📄 {r.source_file}</div>
                        <div style="font-size: 0.95rem; font-weight: 600; color: #f1f5f9; margin-top: 0.2rem;">{r_subj}</div>
                        <div style="font-size: 0.85rem; color: #94a3b8; margin-top: 0.4rem;">
                            📅 Data: <strong>{r_date}</strong> | ⏰ Hora: <strong>{r_time}</strong> | 📍 Cidade: <strong>{r_addr['municipality']}</strong> (Bairro: {r_addr['neighborhood']})
                        </div>
                        <div style="font-style: italic; color: #cbd5e1; margin-top: 0.5rem; line-height: 1.5;">"{r_sum}"</div>
                        <div style="font-size: 0.85rem; color: #a5b4fc; margin-top: 0.5rem;">👥 Envolvidos: {parts_str}</div>
                    </div>
                    """), unsafe_allow_html=True)



