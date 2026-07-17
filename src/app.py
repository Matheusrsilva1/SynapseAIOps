import os
import streamlit as st
import pandas as pd
import numpy as np
from database import DBConnection
import datetime

# Page configuration
st.set_page_config(
    page_title="Synapse AIOps - Locaweb & FIAP",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Premium CSS Injection (AIOps Glassmorphism Dark Theme)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&family=Inter:wght@300;400;500;600&display=swap');
    
    /* Base styling */
    .stApp {
        background: linear-gradient(135deg, #090b11 0%, #111320 100%) !important;
        color: #e2e8f0 !important;
        font-family: 'Inter', sans-serif !important;
    }
    
    /* Sidebar styling */
    section[data-testid="stSidebar"] {
        background-color: #0b0c14 !important;
        border-right: 1px solid #1e2235 !important;
    }
    
    /* Title Styling */
    h1, h2, h3, h4, h5, h6 {
        font-family: 'Outfit', sans-serif !important;
        font-weight: 600 !important;
        letter-spacing: -0.02em !important;
    }
    
    .main-title {
        background: linear-gradient(90deg, #6366f1 0%, #a855f7 50%, #ec4899 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2.6rem;
        font-weight: 800 !important;
        margin-bottom: 0.2rem;
    }
    
    .section-subtitle {
        color: #94a3b8;
        font-size: 1.05rem;
        margin-bottom: 1.5rem;
        font-weight: 400;
    }
    
    /* Premium Glassmorphic Cards */
    .premium-card {
        background: rgba(20, 24, 43, 0.6);
        border: 1px solid rgba(99, 102, 241, 0.18);
        border-radius: 16px;
        padding: 22px;
        box-shadow: 0 10px 30px 0 rgba(0, 0, 0, 0.4);
        backdrop-filter: blur(12px);
        margin-bottom: 20px;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    .premium-card:hover {
        border-color: rgba(168, 85, 247, 0.4);
        transform: translateY(-3px);
        box-shadow: 0 15px 35px 0 rgba(99, 102, 241, 0.15);
    }
    
    .card-title {
        font-size: 0.85rem;
        color: #94a3b8;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        margin-bottom: 10px;
        font-weight: 600;
        display: flex;
        align-items: center;
        gap: 6px;
    }
    
    .card-value {
        font-size: 2.1rem;
        font-weight: 700;
        font-family: 'Outfit', sans-serif;
        color: #ffffff;
        line-height: 1.1;
    }
    
    .card-subtitle {
        font-size: 0.78rem;
        color: #64748b;
        margin-top: 8px;
        display: flex;
        align-items: center;
        gap: 4px;
    }
    
    /* Explainer Box Style */
    .explainer-box {
        background: rgba(99, 102, 241, 0.06);
        border-left: 4px solid #6366f1;
        border-radius: 4px 16px 16px 4px;
        padding: 20px;
        margin-bottom: 25px;
        border-top: 1px solid rgba(99, 102, 241, 0.08);
        border-right: 1px solid rgba(99, 102, 241, 0.08);
        border-bottom: 1px solid rgba(99, 102, 241, 0.08);
    }
    
    .explainer-title {
        font-family: 'Outfit', sans-serif;
        font-weight: 700;
        color: #818cf8;
        margin-bottom: 8px;
        font-size: 1.1rem;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    
    .explainer-text {
        font-size: 0.92rem;
        color: #cbd5e1;
        line-height: 1.6;
    }
    
    /* Table style corrections */
    div[data-testid="stTable"] table {
        background-color: rgba(15, 17, 28, 0.6) !important;
        border-collapse: separate !important;
        border-spacing: 0 !important;
        border: 1px solid rgba(255, 255, 255, 0.05) !important;
        border-radius: 8px !important;
        overflow: hidden !important;
    }
    
    div[data-testid="stTable"] th {
        background-color: rgba(99, 102, 241, 0.15) !important;
        color: #a5b4fc !important;
        font-family: 'Outfit', sans-serif !important;
        font-weight: 600 !important;
        padding: 12px !important;
    }
    
    div[data-testid="stTable"] td {
        padding: 10px 12px !important;
        border-bottom: 1px solid rgba(255, 255, 255, 0.03) !important;
    }
    
    /* Metrics display tweak */
    [data-testid="metric-container"] {
        background: rgba(20, 24, 43, 0.6) !important;
        border: 1px solid rgba(99, 102, 241, 0.18) !important;
        border-radius: 12px !important;
        padding: 12px 18px !important;
    }
</style>
""", unsafe_allow_html=True)

# Database Connection
@st.cache_resource
def get_db_connection():
    return DBConnection()

con = get_db_connection()

# Sidebar controls
st.sidebar.image("https://img.icons8.com/nolan/128/brain.png", width=80)
st.sidebar.markdown("<h2 style='margin-bottom:0px; padding-bottom:0px;'>Synapse AIOps</h2>", unsafe_allow_html=True)
st.sidebar.caption("Inteligência Preditiva e Estabilidade Digital")
st.sidebar.markdown("---")

menu = st.sidebar.radio(
    "Navegação Lateral",
    ["Visão Geral", "Motor de Clarividência", "Motor de Risco (OLA)", "Agrupamento de Causa Raiz"]
)

st.sidebar.markdown("---")
st.sidebar.info(
    "**FIAP Challenge 2026 | Locaweb**\n\n"
    "Grupo 69 (Turma 2TSCOA)\n\n"
    "• Ana Carolina Carvalho\n"
    "• Barbara Ayumi Kodama\n"
    "• Matheus Rodrigo Santos"
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
# If using local fallback and the file doesn't exist, show helpful error
if not con.using_supabase and not os.path.exists(con.db_path):
    st.error("Banco de dados local não encontrado e conexão com Supabase ausente.")
    st.info("Por favor, crie o arquivo `.env` na raiz do projeto com a chave `SUPABASE_DB_URL` ou execute o pipeline localmente para gerar o DuckDB local!")
    st.stop()

# ==========================================
# MENU: VISÃO GERAL
# ==========================================
if menu == "Visão Geral":
    st.markdown("<h1 class='main-title'>🧠 Dashboard de Monitoramento Preditivo</h1>", unsafe_allow_html=True)
    st.markdown("<p class='section-subtitle'>Visão analítica integrada da operação ITSM Locaweb e diagnóstico preditivo em tempo real.</p>", unsafe_allow_html=True)
    
    # Explainer Box
    st.markdown("""
    <div class="explainer-box">
        <div class="explainer-title">💡 Sobre esta Cabine Operacional</div>
        <div class="explainer-text">
            Esta tela consolida as análises preditivas geradas pelos <strong>três motores de Inteligência Artificial</strong>. 
            O objetivo é prover ao coordenador de operações da Locaweb uma visão antecipada de picos de incidentes, chamados críticos na fila com alta probabilidade de estouro de OLA, e as principais falhas crônicas mapeadas na infraestrutura técnica nas últimas 24 horas.
        </div>
    </div>
    """, unsafe_allow_html=True)

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
    
    # Render cards using columns
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"""
        <div class="premium-card">
            <div class="card-title">🔮 Clarividência (D+1)</div>
            <div class="card-value">{int(d_plus_1)}</div>
            <div class="card-subtitle">📊 Volumetria prevista para amanhã</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="premium-card">
            <div class="card-title" style="color: #ef4444;">🚦 Risco Crítico OLA</div>
            <div class="card-value" style="color: #f87171;">{alto_risco}</div>
            <div class="card-subtitle" style="color: #f87171;">⚠️ Incidentes com risco > 80%</div>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
        <div class="premium-card">
            <div class="card-title" style="color: #eab308;">📁 Padrões de Causa Raiz</div>
            <div class="card-value" style="color: #facc15;">{total_clusters}</div>
            <div class="card-subtitle">🔍 Assinaturas de falha ativas</div>
        </div>
        """, unsafe_allow_html=True)
    with col4:
        st.markdown(f"""
        <div class="premium-card">
            <div class="card-title" style="color: #3b82f6;">📥 Total de Chamados</div>
            <div class="card-value">{totais}</div>
            <div class="card-subtitle">⚙️ Incidentes ativos em triagem</div>
        </div>
        """, unsafe_allow_html=True)
        
    # Main columns layout for charts/tables
    col_left, col_right = st.columns([3, 2])
    
    with col_left:
        st.markdown("### ⚠️ Incidentes Prioritários na Fila (Por Risco de OLA)")
        st.caption("Fila reordenada dinamicamente pelo motor de IA baseado no risco real de estouro do tempo contratado.")
        
        df_high_risk = con.execute("""
            SELECT numero as "Nº Chamado", prioridade as "Prioridade", produto as "Produto", categoria as "Categoria", risco_ola_prob 
            FROM gold_risco_ola 
            ORDER BY risco_ola_prob DESC 
            LIMIT 5
        """).fetchdf()
        
        # Format percentage display
        df_high_risk['Probabilidade Risco'] = (df_high_risk['risco_ola_prob'] * 100).round(1).astype(str) + '%'
        df_high_risk = df_high_risk.drop(columns=['risco_ola_prob'])
        st.table(df_high_risk)
        
    with col_right:
        st.markdown("### 📈 Tendência de Chamados (Próximos 14 Dias)")
        st.caption("Visualização rápida das oscilações diárias de volume histórico e previsões.")
        
        df_chart = con.execute("""
            SELECT data, previsao 
            FROM gold_previsoes_volumetry 
            ORDER BY data DESC 
            LIMIT 14
        """).fetchdf()
        df_chart = df_chart.sort_values('data')
        # Rename column for nicer legend in line chart
        df_chart = df_chart.rename(columns={'previsao': 'Previsão de Incidentes'})
        st.line_chart(df_chart.set_index('data'), height=220)

# ==========================================
# MENU: CLARIVIDÊNCIA (FORECAST)
# ==========================================
elif menu == "Motor de Clarividência":
    st.markdown("<h1 class='main-title'>🔮 Motor de Clarividência (Volumetria)</h1>", unsafe_allow_html=True)
    st.markdown("<p class='section-subtitle'>Previsão de volume de incidentes com base em séries temporais (Prophet).</p>", unsafe_allow_html=True)
    
    # Explainer Box
    st.markdown("""
    <div class="explainer-box">
        <div class="explainer-title">🎯 Objetivo de Negócio & Modelo Utilizado</div>
        <div class="explainer-text">
            Este motor utiliza o algoritmo <strong>Prophet</strong> para analisar tendências e ciclos sazonais históricos de chamados na Locaweb (sazonalidades diárias, semanais e mensais). 
            Ao prever a carga de incidentes para os próximos <strong>7 dias (D+7)</strong>, a gerência ganha poder de planejamento para escalar analistas de suporte técnico de forma pró-ativa antes que gargalos e picos de chamados sobrecarreguem as operações.
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    df_forecast = con.execute("SELECT * FROM gold_previsoes_volumetry ORDER BY data").fetchdf()
    
    col_chart, col_table = st.columns([3, 2])
    
    with col_chart:
        st.markdown("### Projeção Preditiva com Intervalo de Confiança")
        st.caption("A linha central mostra a tendência média esperada. Os limites inferior (Min) e superior (Max) mostram o intervalo de incerteza da IA.")
        
        df_plot = df_forecast.tail(45).copy()
        df_plot['data'] = pd.to_datetime(df_plot['data'])
        df_plot = df_plot.set_index('data')
        
        # Rename columns for presentation
        df_plot = df_plot.rename(columns={
            'previsao': 'Previsão Esperada',
            'previsao_min': 'Intervalo Mínimo',
            'previsao_max': 'Intervalo Máximo'
        })
        
        st.line_chart(df_plot[['Previsão Esperada', 'Intervalo Mínimo', 'Intervalo Máximo']], height=380)
        
    with col_table:
        st.markdown("### Detalhamento das Projeções Futuras (D+7)")
        st.caption("Valores previstos detalhados para suporte ao planejamento de escalas e plantões.")
        
        future_only = df_forecast.tail(7).copy()
        future_only['Data'] = pd.to_datetime(future_only['data']).dt.strftime('%d/%m/%Y (%a)')
        future_only['Previsão Média'] = future_only['previsao'].round().astype(int)
        future_only['Mínimo Previsto'] = future_only['previsao_min'].round().astype(int)
        future_only['Máximo Previsto'] = future_only['previsao_max'].round().astype(int)
        
        future_only = future_only[['Data', 'Previsão Média', 'Mínimo Previsto', 'Máximo Previsto']]
        st.dataframe(future_only, use_container_width=True, hide_index=True)
        
        # KPI Callout in column
        max_prev = future_only['Previsão Média'].max()
        max_day = future_only.loc[future_only['Previsão Média'].idxmax(), 'Data']
        st.markdown(f"""
        <div class="premium-card" style="margin-top: 15px; border-color: rgba(236, 72, 153, 0.3);">
            <div class="card-title" style="color: #ec4899;">⚠️ Alerta de Pico de Demanda</div>
            <div class="card-value" style="font-size: 1.7rem;">{max_prev} <span style="font-size: 0.9rem; color: #cbd5e1;">incidentes</span></div>
            <div class="card-subtitle">Pico esperado em: <strong>{max_day}</strong></div>
        </div>
        """, unsafe_allow_html=True)

# ==========================================
# MENU: MOTOR DE RISCO (OLA CLASSIFICATION)
# ==========================================
elif menu == "Motor de Risco (OLA)":
    st.markdown("<h1 class='main-title'>🚦 Motor de Risco de Violabilidade (OLA)</h1>", unsafe_allow_html=True)
    st.markdown("<p class='section-subtitle'>Classificador probabilístico baseado em XGBoost para priorização inteligente de filas de suporte.</p>", unsafe_allow_html=True)
    
    # Explainer Box
    st.markdown("""
    <div class="explainer-box" style="border-left-color: #ef4444; background: rgba(239, 68, 68, 0.03);">
        <div class="explainer-title" style="color: #f87171;">🎯 Priorização Eficiente de Incidentes</div>
        <div class="explainer-text">
            Este motor utiliza um classificador supervisionado <strong>XGBoost</strong>. Em vez de ordenar os chamados apenas por ordem de chegada (First-in, First-out), a IA calcula em tempo real a probabilidade de estouro do OLA/SLA com base na categoria, produto, analista responsável, hora e dia da abertura. 
            Isso permite reorganizar a fila colocando os incidentes de maior risco no topo, minimizando prejuízos financeiros e contratuais.
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Main filters
    col_f1, col_f2 = st.columns([2, 3])
    with col_f1:
        produtos_list = list(con.execute("SELECT DISTINCT produto FROM gold_risco_ola").fetchdf()['produto'])
        produto_filter = st.selectbox("Selecione o Produto para Analisar", ["Todos"] + produtos_list)
    with col_f2:
        risco_filter = st.slider("Filtrar Risco Mínimo de Estouro (%)", 0, 100, 50)
        
    # Main columns layout
    col_chart, col_data = st.columns([2, 3])
    
    # Prepare query
    query = "SELECT numero, prioridade, produto, categoria, duracao, grupo_designado, aberto_por, risco_ola_prob FROM gold_risco_ola WHERE 1=1"
    if produto_filter != "Todos":
        query += f" AND produto = '{produto_filter}'"
    query += f" AND risco_ola_prob >= {risco_filter / 100}"
    query += " ORDER BY risco_ola_prob DESC"
    
    df_risk_results = con.execute(query).fetchdf()
    
    with col_chart:
        st.markdown("### 📊 Risco Operacional Médio por Produto")
        st.caption("Mostra a média ponderada de risco de estouro de acordos por linha de produto no filtro atual.")
        
        # Query risk averages per product
        df_risk_prod = con.execute("""
            SELECT produto as "Linha de Produto", AVG(risco_ola_prob) * 100 as "Risco Médio %" 
            FROM gold_risco_ola 
            GROUP BY produto 
            ORDER BY "Risco Médio %" DESC
        """).fetchdf()
        
        st.bar_chart(df_risk_prod.set_index("Linha de Produto"), y="Risco Médio %", color="#ef4444", height=280)
        
        # Add dynamic metric
        avg_risk_general = df_risk_prod["Risco Médio %"].mean()
        st.markdown(f"""
        <div class="premium-card" style="border-color: rgba(239, 68, 68, 0.3);">
            <div class="card-title" style="color: #ef4444;">⚠️ Risco Geral Operacional</div>
            <div class="card-value">{avg_risk_general.round(1)}%</div>
            <div class="card-subtitle">Probabilidade média geral de estouro de fila</div>
        </div>
        """, unsafe_allow_html=True)
        
    with col_data:
        st.markdown(f"### Fila Ordenada por Risco ({len(df_risk_results)} Chamados)")
        st.caption("Ações imediatas recomendadas no topo.")
        
        # Clean dataframe for user display
        df_clean = df_risk_results.copy()
        df_clean['Risco (%)'] = (df_clean['risco_ola_prob'] * 100).round(1).astype(str) + '%'
        df_clean['Ação Sugerida'] = np.where(
            df_clean['risco_ola_prob'] > 0.8, "🚨 Escalabilidade Imediata (N3)",
            np.where(df_clean['risco_ola_prob'] > 0.5, "⚠️ Monitorar Próximo da Fila (N2)", "✓ Operação Normal (N1)")
        )
        
        df_clean = df_clean.rename(columns={
            'numero': 'ID Chamado',
            'prioridade': 'Prioridade',
            'produto': 'Produto',
            'categoria': 'Categoria',
            'grupo_designado': 'Grupo Técnico'
        })
        
        # Keep presentation columns
        df_clean = df_clean[['ID Chamado', 'Prioridade', 'Produto', 'Grupo Técnico', 'Risco (%)', 'Ação Sugerida']]
        st.dataframe(df_clean, use_container_width=True, hide_index=True)

# ==========================================
# MENU: AGRUPAMENTO DE CAUSA RAIZ (K-MEANS)
# ==========================================
elif menu == "Agrupamento de Causa Raiz":
    st.markdown("<h1 class='main-title'>📁 Agrupamento Inteligente de Incidentes P2/P3</h1>", unsafe_allow_html=True)
    st.markdown("<p class='section-subtitle'>Machine Learning não-supervisionado (K-Means) para redução de reincidência de problemas crônicos.</p>", unsafe_allow_html=True)
    
    # Explainer Box
    st.markdown("""
    <div class="explainer-box" style="border-left-color: #eab308; background: rgba(234, 179, 8, 0.03);">
        <div class="explainer-title" style="color: #facc15;">🎯 Agrupamento e Diagnóstico de Falha Crônica</div>
        <div class="explainer-text">
            Este motor aplica o modelo <strong>K-Means</strong> combinado com processamento de linguagem natural (<strong>TF-IDF</strong>). 
            Ele realiza uma varredura nas descrições de chamados graves (P2 e P3) e os agrupa em <strong>assinaturas de falha comuns</strong>. Em vez do time de engenharia investigar e resolver centenas de chamados individuais e dispersos, o dashboard apresenta a causa raiz provável de forma agregada, aumentando a produtividade.
        </div>
    </div>
    """, unsafe_allow_html=True)
    
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
    
    col_chart, col_list = st.columns([2, 3])
    
    with col_chart:
        st.markdown("### 📊 Incidência de Falhas por Assinatura")
        st.caption("Volume relativo de ocorrências agrupados pela inteligência artificial.")
        
        df_chart_cluster = clusters_summary.copy()
        df_chart_cluster['Assinatura de Erro'] = "CLUSTER " + df_chart_cluster['cluster_id'].astype(str) + ": " + df_chart_cluster['cluster_nome']
        st.bar_chart(df_chart_cluster.set_index("Assinatura de Erro"), y="volume", color="#eab308", height=280)
        
        # Add aggregate KPI Card
        highest_volume = clusters_summary.iloc[0]['volume']
        highest_name = clusters_summary.iloc[0]['cluster_nome']
        st.markdown(f"""
        <div class="premium-card" style="border-color: rgba(234, 179, 8, 0.3);">
            <div class="card-title" style="color: #eab308;">⚠️ Gargalo Mais Crítico</div>
            <div class="card-value" style="font-size: 1.45rem; color: #facc15;">{highest_name}</div>
            <div class="card-subtitle">Lidera com <strong>{highest_volume}</strong> incidentes agrupados.</div>
        </div>
        """, unsafe_allow_html=True)
        
    with col_list:
        st.markdown("### Assinaturas de Erro e Causas Raiz")
        st.caption("Expanda os clusters abaixo para ver o tempo médio estimado de resolução (MTTR) e chamados de exemplo.")
        
        for idx, row in clusters_summary.iterrows():
            with st.expander(f"📌 CLUSTER {row['cluster_id']}: {row['cluster_nome']} ({row['volume']} incidentes parecidos)"):
                mttr_minutos = int(row['media_duracao_segundos'] / 60)
                st.markdown(f"⏱️ **Tempo Médio Histórico de Resolução (MTTR):** `{mttr_minutos} minutos`")
                
                # Fetch examples
                examples = con.execute(f"""
                    SELECT numero as "Nº Chamado", produto as "Produto", descricao_resumida as "Descrição da Falha" 
                    FROM gold_clusters_padroes 
                    WHERE cluster_id = {row['cluster_id']} 
                    LIMIT 3
                """).fetchdf()
                
                st.dataframe(examples, use_container_width=True, hide_index=True)



