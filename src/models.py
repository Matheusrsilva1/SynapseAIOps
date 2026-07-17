import os
import pandas as pd
import numpy as np
from database import DBConnection
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans

print("Starting Model Training for Synapse AIOps...")

# Connect to database (Supabase or DuckDB fallback)
con = DBConnection()

# ==========================================
# 1. MOTOR DE CLARIVIDÊNCIA (VOLUMETRIA PREDICT)
# ==========================================
print("Training Motor de Clarividência (Daily Volumetry)...")
df_vol = con.execute("SELECT data, total_incidentes FROM silver_daily_volumetry ORDER BY data").fetchdf()

if len(df_vol) > 10:
    # Check if Prophet is installed, fallback to Scikit-Learn if not
    try:
        from prophet import Prophet
        print("  Using Prophet model for forecasting...")
        df_prophet = df_vol.rename(columns={'data': 'ds', 'total_incidentes': 'y'})
        model = Prophet(yearly_seasonality=True, weekly_seasonality=True, daily_seasonality=False)
        model.fit(df_prophet)
        
        # Predict D+1 to D+7
        future = model.make_future_dataframe(periods=7)
        forecast = model.predict(future)
        df_forecast = forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].rename(columns={
            'ds': 'data', 'yhat': 'previsao', 'yhat_lower': 'previsao_min', 'yhat_upper': 'previsao_max'
        })
        # Keep only the last year + forecast for dashboard speed
        df_forecast = df_forecast.tail(372) 
    except ImportError:
        print("  Prophet not installed. Falling back to Random Forest Regressor with date features...")
        from sklearn.ensemble import RandomForestRegressor
        df_vol['data'] = pd.to_datetime(df_vol['data'])
        df_vol['year'] = df_vol['data'].dt.year
        df_vol['month'] = df_vol['data'].dt.month
        df_vol['day'] = df_vol['data'].dt.day
        df_vol['dayofweek'] = df_vol['data'].dt.dayofweek
        
        X = df_vol[['year', 'month', 'day', 'dayofweek']]
        y = df_vol['total_incidentes']
        
        rf = RandomForestRegressor(n_estimators=100, random_state=42)
        rf.fit(X, y)
        
        # Generate next 7 days
        last_date = df_vol['data'].max()
        future_dates = [last_date + pd.Timedelta(days=i) for i in range(1, 8)]
        future_df = pd.DataFrame({'data': future_dates})
        future_df['year'] = future_df['data'].dt.year
        future_df['month'] = future_df['data'].dt.month
        future_df['day'] = future_df['data'].dt.day
        future_df['dayofweek'] = future_df['data'].dt.dayofweek
        
        preds = rf.predict(future_df[['year', 'month', 'day', 'dayofweek']])
        
        # Join historical and predictions
        hist_df = df_vol[['data', 'total_incidentes']].copy()
        hist_df = hist_df.rename(columns={'total_incidentes': 'previsao'})
        hist_df['previsao_min'] = hist_df['previsao'] * 0.9
        hist_df['previsao_max'] = hist_df['previsao'] * 1.1
        
        future_df_final = pd.DataFrame({
            'data': future_dates,
            'previsao': preds,
            'previsao_min': preds * 0.85,
            'previsao_max': preds * 1.15
        })
        
        df_forecast = pd.concat([hist_df, future_df_final], ignore_index=True)
        df_forecast = df_forecast.tail(372)

    # Save to Database
    if con.using_supabase:
        df_forecast.to_sql("gold_previsoes_volumetry", con.engine, if_exists="replace", index=False)
    else:
        con.execute("DROP TABLE IF EXISTS gold_previsoes_volumetry")
        con.duck_con.register('df_forecast_temp', df_forecast)
        con.execute("CREATE TABLE gold_previsoes_volumetry AS SELECT * FROM df_forecast_temp")
    print("  Clarividência model predictions saved to Database.")
else:
    print("  Insufficient historical data for Clarividência.")

# ==========================================
# 2. MOTOR DE RISCO (OLA BREACH RISK)
# ==========================================
print("Training Motor de Risco (OLA Breach probability)...")
df_risk = con.execute("SELECT * FROM silver_ola_features").fetchdf()

if len(df_risk) > 0:
    # Target definition
    df_risk['y'] = (df_risk['kpi_violado'] == 'SIM').astype(int)
    
    # Categorical Columns to encode
    cat_cols = ['prioridade', 'produto', 'categoria', 'grupo_designado', 'aberto_por']
    encoders = {}
    
    for col in cat_cols:
        le = LabelEncoder()
        df_risk[col] = le.fit_transform(df_risk[col].astype(str))
        encoders[col] = le
        
    # Convert numerical features from PostgreSQL (like Numeric/Decimal) to float for XGBoost
    df_risk['hora_abertura'] = pd.to_numeric(df_risk['hora_abertura'], errors='coerce').fillna(0).astype(float)
    df_risk['dia_semana_abertura'] = pd.to_numeric(df_risk['dia_semana_abertura'], errors='coerce').fillna(0).astype(float)
        
    X_cols = cat_cols + ['hora_abertura', 'dia_semana_abertura']
    X = df_risk[X_cols].fillna(0)
    y = df_risk['y']
    
    try:
        from xgboost import XGBClassifier
        print("  Using XGBoost Classifier for OLA Risk...")
        clf = XGBClassifier(n_estimators=100, max_depth=5, learning_rate=0.1, random_state=42, eval_metric='logloss')
    except ImportError:
        print("  XGBoost not installed. Falling back to Random Forest Classifier...")
        from sklearn.ensemble import RandomForestClassifier
        clf = RandomForestClassifier(n_estimators=100, max_depth=8, random_state=42)
        
    clf.fit(X, y)
    
    # Predict probability of OLA breach for all rows to save back
    probs = clf.predict_proba(X)[:, 1]
    
    # Reload original text columns for output
    df_risk_output = con.execute("SELECT numero, prioridade, produto, categoria, duracao, grupo_designado, aberto_por, kpi_violado FROM silver_ola_features").fetchdf()
    df_risk_output['risco_ola_prob'] = probs
    
    # Save to Database
    if con.using_supabase:
        df_risk_output.to_sql("gold_risco_ola", con.engine, if_exists="replace", index=False)
    else:
        con.execute("DROP TABLE IF EXISTS gold_risco_ola")
        con.duck_con.register('df_risk_temp', df_risk_output)
        con.execute("CREATE TABLE gold_risco_ola AS SELECT * FROM df_risk_temp")
    print("  Motor de Risco predictions saved to Database.")
else:
    print("  No risk features available.")

# ==========================================
# 3. MOTOR DE DETECÇÃO DE PADRÕES (CLUSTERIZAÇÃO DE CAUSA RAIZ)
# ==========================================
print("Training Motor de Detecção de Padrões (K-Means for P2/P3)...")
df_pat = con.execute("SELECT * FROM silver_incidentes_criticos").fetchdf()

if len(df_pat) > 0:
    # Text vectorization using TF-IDF
    vectorizer = TfidfVectorizer(max_features=500, stop_words=['de', 'o', 'a', 'e', 'que', 'do', 'da', 'em', 'um', 'para', 'com', 'na', 'no', 'se', 'por', 'problem', 'alarm'])
    X_text = vectorizer.fit_transform(df_pat['descricao_resumida'].astype(str))
    
    # Run KMeans with 5 clusters
    n_clusters = 5
    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init='auto')
    df_pat['cluster_id'] = kmeans.fit_transform(X_text).argmin(axis=1) # assigning labels
    df_pat['cluster_id'] = kmeans.labels_
    
    # Identify top words per cluster to name them dynamically
    order_centroids = kmeans.cluster_centers_.argsort()[:, ::-1]
    terms = vectorizer.get_feature_names_out()
    
    cluster_names = {}
    for i in range(n_clusters):
        top_terms = [terms[ind] for ind in order_centroids[i, :3]]
        cluster_names[i] = " & ".join(top_terms).upper()
        print(f"  Cluster {i} top words: {cluster_names[i]}")
        
    df_pat['cluster_nome'] = df_pat['cluster_id'].map(cluster_names)
    
    # Save to Database
    if con.using_supabase:
        df_pat.to_sql("gold_clusters_padroes", con.engine, if_exists="replace", index=False)
    else:
        con.execute("DROP TABLE IF EXISTS gold_clusters_padroes")
        con.duck_con.register('df_pat_temp', df_pat)
        con.execute("CREATE TABLE gold_clusters_padroes AS SELECT * FROM df_pat_temp")
    print("  Motor de Detecção de Padrões clusters saved to Database.")
else:
    print("  No critical incidents for pattern clustering.")

con.close()
print("Model training pipeline completed successfully!")

