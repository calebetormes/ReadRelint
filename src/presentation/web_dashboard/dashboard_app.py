import sys
from pathlib import Path

# Adiciona a raiz do projeto ao sys.path para permitir importações absolutas de src
project_root = Path(__file__).resolve().parent.parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from src.adapters.tinydb_repo import TinyDbRepo

# Configuração da página e visual
st.set_page_config(
    page_title="Relatórios de Incidentes - Dashboard",
    page_icon="🚨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Customização de estilos com CSS para visual premium
st.markdown("""
<style>
    .main {
        background-color: #0f1116;
        color: #e2e8f0;
    }
    .stMetric {
        background-color: #1a1f29;
        padding: 15px;
        border-radius: 8px;
        border: 1px solid #2d3748;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .report-card {
        background-color: #1a1f29;
        padding: 20px;
        border-radius: 8px;
        border: 1px solid #2d3748;
        margin-bottom: 15px;
    }
    .report-title {
        font-size: 1.2rem;
        font-weight: bold;
        color: #63b3ed;
    }
    .section-title {
        font-size: 1rem;
        font-weight: bold;
        color: #cbd5e0;
        border-bottom: 1px solid #4a5568;
        padding-bottom: 5px;
        margin-top: 10px;
        margin-bottom: 10px;
    }
</style>
""", unsafe_allow_html=True)

# Função cacheada para carregar os dados
@st.cache_data(ttl=5)
def load_data():
    db_path = Path("data/database.json")
    if not db_path.exists():
        return []
    repo = TinyDbRepo(db_path)
    return repo.get_all()

# Título do Dashboard
st.title("📊 Painel de Análise de Boletins de Ocorrência")
st.markdown("Visualização, busca e análise estatística dos incidentes estruturados por inteligência artificial local.")

# Carrega os dados
reports = load_data()

if not reports:
    st.info("Nenhum boletim de ocorrência cadastrado na base de dados no momento. Inicie o monitoramento na interface desktop para processar arquivos.")
else:
    # Transforma para DataFrame para manipulação fácil
    data_list = []
    for idx, r in enumerate(reports):
        r_dict = r.model_dump()
        r_dict["internal_id"] = idx + 1
        
        # Natureza e Grupo do incidente (garante compatibilidade com registros antigos)
        r_dict["incident_nature"] = getattr(r, "incident_nature", "Ocorrência")
        r_dict["incident_group"] = getattr(r, "incident_group", "Legado / Não Categorizado")
        
        # Endereço estruturado
        r_dict["street"] = r.address.street
        r_dict["number"] = r.address.number or "S/N"
        r_dict["neighborhood"] = r.address.neighborhood or "Não Informado"
        r_dict["city"] = r.address.city or "Não Informado"
        r_dict["full_address"] = f"{r.address.street}, {r.address.number or 'S/N'} - {r.address.neighborhood or ''}, {r.address.city or ''}"
        
        # Participantes
        parts = [f"{p.name} ({p.role})" for p in r.participants]
        r_dict["participants_summary"] = ", ".join(parts) if parts else "Nenhum participante identificado"
        
        # Veículos
        vehs = [f"{v.model or 'Modelo não informado'} (Placa: {v.plate or 'S/P'}, Cor: {v.color or 'N/I'})" for v in r.vehicles]
        r_dict["vehicles_summary"] = ", ".join(vehs) if vehs else "Nenhum veículo identificado"
        
        # Data do incidente
        parsed_date = None
        if r.incident_time:
            try:
                dt_str = r.incident_time.replace("Z", "")
                parsed_date = datetime.fromisoformat(dt_str)
                if parsed_date.tzinfo is not None:
                    parsed_date = parsed_date.replace(tzinfo=None)
            except Exception:
                pass
        r_dict["parsed_date"] = parsed_date
        r_dict["formatted_date"] = parsed_date.strftime("%d/%m/%Y %H:%M") if parsed_date else "Não Informado"
        
        data_list.append(r_dict)
        
    df = pd.DataFrame(data_list)

    # BARRA LATERAL - Filtros
    st.sidebar.header("🔍 Filtros de Busca")
    
    # Campo de busca livre
    search_query = st.sidebar.text_input("Busca textual livre", "", placeholder="Nome, crime, placa, histórico...")

    # Filtro de natureza do registro
    all_natures = sorted(list(df["incident_nature"].unique()))
    selected_natures = st.sidebar.multiselect("Natureza do Registro", options=all_natures)

    # Filtro de grupo de ocorrência
    all_groups = sorted(list(df["incident_group"].unique()))
    selected_groups = st.sidebar.multiselect("Grupos de Ocorrência", options=all_groups)

    # Filtro de tipo de crime
    all_crimes = sorted(list(df["incident_type"].unique()))
    selected_crimes = st.sidebar.multiselect("Tipos de Incidente", options=all_crimes)

    # Filtro de cidade
    all_cities = sorted(list(df["city"].unique()))
    selected_cities = st.sidebar.multiselect("Cidades", options=all_cities)

    # Filtro de data (se houver datas válidas)
    valid_dates = df[df["parsed_date"].notna()]
    if not valid_dates.empty:
        min_date = valid_dates["parsed_date"].min().date()
        max_date = valid_dates["parsed_date"].max().date()
        
        # Evita crash se min_date e max_date forem iguais
        if min_date == max_date:
            st.sidebar.info(f"Ocorrências apenas em: {min_date.strftime('%d/%m/%Y')}")
            selected_dates = (min_date, max_date)
        else:
            selected_dates = st.sidebar.date_input(
                "Período do Incidente",
                value=(min_date, max_date),
                min_value=min_date,
                max_value=max_date
            )
    else:
        selected_dates = None

    # Aplicação dos Filtros
    df_filtered = df.copy()

    if selected_natures:
        df_filtered = df_filtered[df_filtered["incident_nature"].isin(selected_natures)]

    if selected_groups:
        df_filtered = df_filtered[df_filtered["incident_group"].isin(selected_groups)]

    if selected_crimes:
        df_filtered = df_filtered[df_filtered["incident_type"].isin(selected_crimes)]
        
    if selected_cities:
        df_filtered = df_filtered[df_filtered["city"].isin(selected_cities)]
        
    if selected_dates and len(selected_dates) == 2:
        start_d, end_d = selected_dates
        # Compara apenas a data (sem hora)
        df_filtered = df_filtered[
            (df_filtered["parsed_date"].isna()) | 
            ((df_filtered["parsed_date"].dt.date >= start_d) & (df_filtered["parsed_date"].dt.date <= end_d))
        ]

    if search_query:
        q = search_query.lower()
        df_filtered = df_filtered[
            df_filtered["incident_nature"].str.lower().str.contains(q, na=False) |
            df_filtered["incident_group"].str.lower().str.contains(q, na=False) |
            df_filtered["incident_type"].str.lower().str.contains(q, na=False) |
            df_filtered["history_summary"].str.lower().str.contains(q, na=False) |
            df_filtered["participants_summary"].str.lower().str.contains(q, na=False) |
            df_filtered["vehicles_summary"].str.lower().str.contains(q, na=False) |
            df_filtered["full_address"].str.lower().str.contains(q, na=False) |
            df_filtered["attending_officer"].str.lower().str.contains(q, na=False) |
            df_filtered["source_file"].str.lower().str.contains(q, na=False)
        ]

    # SEÇÃO DE MÉTRICAS (KPIs)
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Cadastrado", len(df))
    with col2:
        st.metric("Filtrados / Exibidos", len(df_filtered))
    with col3:
        unique_crimes_count = df_filtered["incident_type"].nunique() if not df_filtered.empty else 0
        st.metric("Variedade de Crimes", unique_crimes_count)
    with col4:
        cidades_count = df_filtered["city"].nunique() if not df_filtered.empty else 0
        st.metric("Cidades Envolvidas", cidades_count)

    st.markdown("---")

    # SEÇÃO DE GRÁFICOS
    if not df_filtered.empty:
        g1, g2 = st.columns(2)
        
        with g1:
            st.markdown("### 📊 Ocorrências por Agrupamento")
            group_counts = df_filtered["incident_group"].value_counts().reset_index()
            group_counts.columns = ["Grupo de Ocorrência", "Quantidade"]
            fig_group = px.bar(
                group_counts, 
                x="Quantidade", 
                y="Grupo de Ocorrência", 
                orientation="h",
                color="Quantidade",
                color_continuous_scale="Reds",
                template="plotly_dark"
            )
            fig_group.update_layout(yaxis={'categoryorder':'total ascending'}, showlegend=False)
            st.plotly_chart(fig_group, use_container_width=True)
            
        with g2:
            st.markdown("### 🏙️ Distribuição de Ocorrências por Cidade")
            city_counts = df_filtered["city"].value_counts().reset_index()
            city_counts.columns = ["Cidade", "Quantidade"]
            fig_city = px.pie(
                city_counts, 
                values="Quantidade", 
                names="Cidade",
                color_discrete_sequence=px.colors.qualitative.Pastel,
                template="plotly_dark"
            )
            st.plotly_chart(fig_city, use_container_width=True)
    else:
        st.warning("Sem dados suficientes com os filtros selecionados para gerar os gráficos.")

    st.markdown("---")

    # LISTAGEM DETALHADA E EXPANSÍVEL
    st.markdown(f"### 📋 Ocorrências Encontradas ({len(df_filtered)})")
    
    if df_filtered.empty:
        st.info("Nenhum boletim atende aos critérios dos filtros selecionados.")
    else:
        # Loop para renderizar os cards expansíveis
        for idx, row in df_filtered.iterrows():
            # Título amigável para o expander
            time_str = f" em {row['formatted_date']}" if row['formatted_date'] != "Não Informado" else ""
            title = f"#{row['internal_id']} - [{row['incident_nature']} - {row['incident_group']}] {row['incident_type']} em {row['city']}{time_str}"
            
            with st.expander(title):
                st.markdown("#### 📝 Resumo do Histórico (Extraído por IA)")
                st.info(row["history_summary"])
                
                det1, det2 = st.columns(2)
                with det1:
                    st.markdown("<div class='section-title'>👥 Participantes</div>", unsafe_allow_html=True)
                    if row["participants"]:
                        for p in row["participants"]:
                            st.write(f"- **{p['name']}**: {p['role']}")
                    else:
                        st.write("Nenhum participante identificado.")
                        
                    st.markdown("<div class='section-title'>🚗 Veículos</div>", unsafe_allow_html=True)
                    if row["vehicles"]:
                        for v in row["vehicles"]:
                            plate_info = f" (Placa: {v['plate']})" if v['plate'] else " (Sem Placa)"
                            color_info = f" - Cor: {v['color']}" if v['color'] else ""
                            st.write(f"- **{v['model'] or 'Veículo'}**{plate_info}{color_info}")
                    else:
                        st.write("Nenhum veículo identificado.")
                        
                with det2:
                    st.markdown("<div class='section-title'>📍 Endereço</div>", unsafe_allow_html=True)
                    st.write(f"**Rua/Logradouro:** {row['street']}")
                    st.write(f"**Número:** {row['number']}")
                    st.write(f"**Bairro:** {row['neighborhood']}")
                    st.write(f"**Cidade:** {row['city']}")
                    
                    st.markdown("<div class='section-title'>👤 Informações do Registro</div>", unsafe_allow_html=True)
                    st.write(f"**Natureza do Registro:** {row['incident_nature']}")
                    st.write(f"**Atendido por:** {row['attending_officer'] or 'Não Informado'}")
                    st.write(f"**Arquivo de Origem:** `{row['source_file'] or 'Desconhecido'}`")
