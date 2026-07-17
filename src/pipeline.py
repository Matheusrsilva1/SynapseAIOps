import os
import pandas as pd
from database import DBConnection

# Get paths dynamically
src_dir = os.path.dirname(os.path.abspath(__file__))
base_dir = os.path.dirname(src_dir)
faculdade_dir = os.path.dirname(base_dir)
dataset_path = os.path.join(faculdade_dir, "Material Locaweb", "LW-DATASET.xlsx")

print("Starting ETL Pipeline for Synapse AIOps...")

# Connect to database (Supabase or DuckDB fallback)
con = DBConnection()

# 1. READ EXCEL & CLEAN COLUMNS (BRONZE LAYER)
print("Reading raw Excel dataset...")
df_raw = pd.read_excel(dataset_path, sheet_name='Dataset Geral')

# Rename columns to avoid encoding issues and spaces
df_raw.columns = [
    'numero', 'prioridade', 'produto', 'categoria', 'subcategoria',
    'grupo_designado', 'item_configuracao', 'aberto', 'resolvido',
    'encerrado', 'duracao', 'codigo_fechamento', 'descricao_resumida',
    'solucao', 'aberto_por', 'incidente_pai', 'status', 'entrou_kpi', 'kpi_violado'
]

# Convert date columns
df_raw['aberto'] = pd.to_datetime(df_raw['aberto'])
df_raw['encerrado'] = pd.to_datetime(df_raw['encerrado'])
df_raw['resolvido'] = pd.to_datetime(df_raw['resolvido'])

# Fill Nulls in Classification Columns
df_raw['produto'] = df_raw['produto'].fillna('Nao Informado')
df_raw['categoria'] = df_raw['categoria'].fillna('Nao Informado')
df_raw['subcategoria'] = df_raw['subcategoria'].fillna('Nao Informado')
df_raw['item_configuracao'] = df_raw['item_configuracao'].fillna('Nao Informado')
df_raw['kpi_violado'] = df_raw['kpi_violado'].fillna('NAO')

# Create Bronze Table in DB
if con.using_supabase:
    print("Creating Bronze Layer (raw cleaned data) in Supabase...")
    df_raw.to_sql("bronze_incidentes", con.engine, if_exists="replace", index=False)
else:
    print("Creating Bronze Layer (raw cleaned data) in DuckDB...")
    con.execute("DROP TABLE IF EXISTS bronze_incidentes")
    con.duck_con.register('df_raw_temp', df_raw)
    con.execute("CREATE TABLE bronze_incidentes AS SELECT * FROM df_raw_temp")
print("Bronze Layer completed.")

# 2. CREATE SILVER LAYER (AGREEMENT & TIMELINE TABLES)
print("Creating Silver Layer...")

# Table 1: Daily Volumetric Summary (For Clarividência - time series prediction)
print("  Creating silver_daily_volumetry...")
con.execute("DROP TABLE IF EXISTS silver_daily_volumetry")
con.execute("""
    CREATE TABLE silver_daily_volumetry AS
    SELECT 
        CAST(aberto AS DATE) as data,
        COUNT(*) as total_incidentes,
        SUM(CASE WHEN prioridade LIKE '%2%' THEN 1 ELSE 0 END) as total_p2,
        SUM(CASE WHEN prioridade LIKE '%3%' THEN 1 ELSE 0 END) as total_p3
    FROM bronze_incidentes
    GROUP BY CAST(aberto AS DATE)
    ORDER BY data
""")

# Table 2: P2/P3 Incidentes for Clusterização (For Padrões - K-Means)
print("  Creating silver_incidentes_criticos (P2/P3)...")
con.execute("DROP TABLE IF EXISTS silver_incidentes_criticos")
con.execute("""
    CREATE TABLE silver_incidentes_criticos AS
    SELECT 
        numero, prioridade, produto, categoria, aberto, 
        duracao, descricao_resumida, grupo_designado
    FROM bronze_incidentes
    WHERE prioridade LIKE '%2%' OR prioridade LIKE '%3%'
""")

# Table 3: OLA Risk Features (For Motor de Risco - Classification)
print("  Creating silver_ola_features...")
con.execute("DROP TABLE IF EXISTS silver_ola_features")
con.execute("""
    CREATE TABLE silver_ola_features AS
    SELECT 
        numero,
        prioridade,
        produto,
        categoria,
        duracao,
        grupo_designado,
        aberto_por,
        kpi_violado,
        EXTRACT(hour FROM aberto) as hora_abertura,
        EXTRACT(dow FROM aberto) as dia_semana_abertura
    FROM bronze_incidentes
""")

print("Silver Layer completed.")
con.close()
print("ETL Pipeline completed successfully!")

