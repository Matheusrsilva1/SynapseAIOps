import os
import streamlit as st
import pandas as pd
import numpy as np
import duckdb
import datetime

# Page configuration
st.set_page_config(
    page_title="Synapse AIOps - Locaweb & FIAP",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Premium CSS Injection
st.markdown("""
<style>
    /* Dark mode styling */
    .stApp {
        background-color: #0c0f1d;
        color: #e2e8f0;
    }
    
    /* Sidebar styling */
    section[data-testid="stSidebar"] {
        background-color: #13172d !important;
    }
    
    /* Metrics container */
    div[data-testid="stMetricValue"] {
        font-size: 2.2rem;
        font-weight: 700;
        color: #6366f1;
    }
    
    /* Header fonts */
    h1, h2, h3 {
        font-family: 'Outfit', 'Inter', sans-serif !important;
        color: #f8fafc !important;
    }
    
    /* Custom Card Style */
    .metric-card {
        background-color: #1e293b;
        border-radius: 12px;
        padding: 20px;
        border: 1px solid #334155;
        box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1);
        margin-bottom: 20px;
    }
    
    .metric-title {
        font-size: 0.875rem;
        color: #94a3b8;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 8px;
    }
    
    .metric-value {
        font-size: 1.875rem;
        font-weight: 700;
        color: #38bdf8;
    }
</style>
""", unsafe_allow_html=True)

# Database Connection
base_dir = r"D:\second_brain\knowledge\faculdade\SynapseAIOps"
db_path = os.path.join(base_dir, "data", "synapse_aiops.db")

@st.cache_resource
def get_db_connection():
    if os.path.exists(db_path):
        return duckdb.connect(db_path, read_only=True)
    return None

con = get_db_connection()

# Sidebar controls
st.sidebar.image("https://img.icons8.com/nolan/128/brain.png", width=80)
st.sidebar.title("Synapse AIOps")
st.sidebar.caption("Inteligência Preditiva e Estabilidade Digital")
st.sidebar.markdown("---")

menu = st.sidebar.radio(
    "Navegação Lateral",
    ["Visão Geral", "Motor de Clarividência", "Motor de Risco (OLA)", "Agrupamento de Causa Raiz"]
)

# Helper function to check if tables exist
def table_exists(con, table_name):
    if not con:
        return False
    try:
        con.execute(f"SELECT 1 FROM {table_name} LIMIT 1")
        return True
    except Exception:
        return False

# Main Layout
if con is None:
    st.error("Banco de dados local não encontrado. Por favor, execute o script de pipeline e modelos primeiro!")
    st.info("Caminho esperado: `D:\\second_brain\\knowledge\\faculdade\\SynapseAIOps\\data\\synapse_aiops.db`")
    st.stop()

# ==========================================
# MENU: VISÃO GERAL
# ==========================================
if menu == "Visão Geral":
    st.title("🧠 Dashboard de Monitoramento Preditivo")
    st.markdown("Bem-vindo à Central de Operações da Synapse AIOps para a **Locaweb**. Aqui você visualiza anomalias e riscos operacionais antes que eles afetem os usuários finais.")
    st.markdown("---")
    
    # Check tables
    if not table_exists(con, "gold_risco_ola") or not table_exists(con, "gold_previsoes_volumetry") or not table_exists(con, "gold_clusters_padroes"):
        st.warning("As tabelas Gold da IA não foram encontradas no banco. Por favor, execute o treinamento dos modelos (`models.py`).")
        st.stop()
        
    # Get Metrics from DB
    totais = con.execute("SELECT COUNT(*) FROM gold_risco_ola").fetchone()[0]
    alto_risco = con.execute("SELECT COUNT(*) FROM gold_risco_ola WHERE risco_ola_prob > 0.8").fetchone()[0]
    total_clusters = con.execute("SELECT COUNT(DISTINCT cluster_id) FROM gold_clusters_padroes").fetchone()[0]
    
    # Previsão D+1
    d_plus_1 = con.execute("SELECT previsao FROM gold_previsoes_volumetry WHERE data = (SELECT MAX(data) FROM gold_previsoes_volumetry)").fetchone()[0]
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Volumetria Prevista D+1</div>
            <div class="metric-value">{int(d_plus_1)} <span style="font-size: 1rem; color: #10b981;">chamados</span></div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Risco Crítico OLA</div>
            <div class="metric-value" style="color: #ef4444;">{alto_risco} <span style="font-size: 1rem; color: #ef4444;">incidentes</span></div>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Padrões de Causa Raiz</div>
            <div class="metric-value" style="color: #eab308;">{total_clusters} <span style="font-size: 1rem; color: #eab308;">ativos</span></div>
        </div>
        """, unsafe_allow_html=True)
    with col4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Chamados em Análise</div>
            <div class="metric-value" style="color: #6366f1;">{totais} <span style="font-size: 1rem; color: #6366f1;">total</span></div>
        </div>
        """, unsafe_allow_html=True)
        
    st.subheader("⚠️ Incidentes Recentes com Alto Risco de OLA")
    df_high_risk = con.execute("""
        SELECT numero, prioridade, produto, categoria, risco_ola_prob 
        FROM gold_risco_ola 
        ORDER BY risco_ola_prob DESC 
        LIMIT 5
    """).fetchdf()
    
    # Format probabilities
    df_high_risk['risco_ola_prob'] = (df_high_risk['risco_ola_prob'] * 100).round(2).astype(str) + '%'
    st.table(df_high_risk)
    
    st.subheader("📉 Resumo Preditivo da Semana")
    df_chart = con.execute("""
        SELECT data, previsao 
        FROM gold_previsoes_volumetry 
        ORDER BY data DESC 
        LIMIT 14
    """).fetchdf()
    df_chart = df_chart.sort_values('data')
    st.line_chart(df_chart.set_index('data'))

# ==========================================
# MENU: CLARIVIDÊNCIA (FORECAST)
# ==========================================
elif menu == "Motor de Clarividência":
    st.title("🔮 Motor de Clarividência (Séries Temporais)")
    st.markdown("Previsão e exploração de volumetria de chamados baseadas em sazonalidade histórica, com projeção para os próximos **7 dias (D+7)**.")
    st.markdown("---")
    
    df_forecast = con.execute("SELECT * FROM gold_previsoes_volumetry ORDER BY data").fetchdf()
    
    # Filter view to last 30 days of data + 7 days forecast
    st.subheader("Previsão Volumétrica e Intervalos de Confiança")
    
    # Interactive line chart using matplotlib/native streamlit line_chart
    # (Using pandas plot for better visualization styling)
    df_plot = df_forecast.tail(45).copy()
    df_plot['data'] = pd.to_datetime(df_plot['data'])
    df_plot = df_plot.set_index('data')
    
    st.line_chart(df_plot[['previsao', 'previsao_min', 'previsao_max']])
    
    st.markdown("#### Detalhamento das Projeções Futuras (D+7)")
    future_only = df_forecast.tail(7).copy()
    future_only['previsao'] = future_only['previsao'].round().astype(int)
    future_only['previsao_min'] = future_only['previsao_min'].round().astype(int)
    future_only['previsao_max'] = future_only['previsao_max'].round().astype(int)
    st.dataframe(future_only, use_container_width=True)

# ==========================================
# MENU: MOTOR DE RISCO (OLA CLASSIFICATION)
# ==========================================
elif menu == "Motor de Risco (OLA)":
    st.title("🚦 Motor de Risco de Violabilidade (OLA)")
    st.markdown("Score de risco probabilístico gerado dinamicamente para incidentes abertos, orientando priorizações e mitigando o estouro de acordos operacionais.")
    st.markdown("---")
    
    # Filters
    col1, col2 = st.columns(2)
    with col1:
        produto_filter = st.selectbox("Filtrar por Produto", ["Todos"] + list(con.execute("SELECT DISTINCT produto FROM gold_risco_ola").fetchdf()['produto']))
    with col2:
        risco_filter = st.slider("Probabilidade Mínima de Risco (%)", 0, 100, 50)
        
    query = "SELECT numero, prioridade, produto, categoria, duracao, grupo_designado, risco_ola_prob FROM gold_risco_ola WHERE 1=1"
    
    if produto_filter != "Todos":
        query += f" AND produto = '{produto_filter}'"
        
    query += f" AND risco_ola_prob >= {risco_filter / 100}"
    query += " ORDER BY risco_ola_prob DESC"
    
    df_risk_results = con.execute(query).fetchdf()
    df_risk_results['risco_ola_prob'] = (df_risk_results['risco_ola_prob'] * 100).round(2).astype(str) + '%'
    
    st.markdown(f"**Total de chamados identificados:** {len(df_risk_results)}")
    st.dataframe(df_risk_results, use_container_width=True)

# ==========================================
# MENU: AGRUPAMENTO DE CAUSA RAIZ (K-MEANS)
# ==========================================
elif menu == "Agrupamento de Causa Raiz":
    st.title("📁 Agrupamento Inteligente de Incidentes P2/P3")
    st.markdown("Clusterização não supervisionada das descrições de falhas graves, agrupando incidentes isolados em assinaturas comuns de causa raiz.")
    st.markdown("---")
    
    # Fetch clusters summaries
    clusters_summary = con.execute("""
        SELECT 
            cluster_id, 
            cluster_nome, 
            COUNT(*) as volume,
            ROUND(AVG(duracao)) as media_duracao_segundos
        FROM gold_clusters_padroes 
        GROUP BY cluster_id, cluster_nome
        ORDER BY volume DESC
    """).fetchdf()
    
    st.subheader("Assinaturas de Falha Detectadas na Infraestrutura")
    for idx, row in clusters_summary.iterrows():
        with st.expander(f"⚠️ CLUSTER {row['cluster_id']}: {row['cluster_nome']} (Recorrência: {row['volume']} incidentes)"):
            st.markdown(f"**MTTR Médio Estimado para Mitigação:** {int(row['media_duracao_segundos'] / 60)} minutos")
            st.markdown("**Incidentes Exemplo neste Padrão:**")
            
            examples = con.execute(f"""
                SELECT numero, produto, descricao_resumida 
                FROM gold_clusters_padroes 
                WHERE cluster_id = {row['cluster_id']} 
                LIMIT 4
            """).fetchdf()
            st.table(examples)

con.close()
