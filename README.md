# 🧠 Synapse AIOps - Inteligência Preditiva e Estabilidade Digital

> **FIAP Enterprise Challenge 2026 | Parceria Locaweb**
> 
> Projeto desenvolvido pelo **Grupo 69 (Turma 2TSCOA)** para transitar a operação de ITSM da Locaweb de uma cultura reativa para uma abordagem preditiva, otimizando a estabilidade digital e garantindo a mitigação de riscos de quebra de OLA (Operational Level Agreement).

---

## 📋 Contextualização e Desafio

A Locaweb opera em um cenário dinâmico 24x7. Atualmente, a operação lida com um grande volume diário de incidentes. O principal problema é a **imprevisibilidade operacional**: a falta de ferramentas que antecipem picos de chamados gera sobrecarga nas equipes de suporte (N1, N2 e N3) e eleva o risco de quebra de OLA. 

Além disso, incidentes recorrentes de prioridade **P2 (Alta)** e **P3 (Média)** consomem tempo excessivo de análise manual para identificação de padrões ocultos e causas raiz.

---

## 🛠️ Proposta de Solução (Os 3 Motores)

O **Synapse AIOps** aborda o problema através de três pilares de Inteligência Artificial:

1. **Motor de Clarividência (Séries Temporais)**: Previsão do volume exato de incidentes para o próximo dia (D+1) e para a próxima semana (D+7) baseando-se em sazonalidade histórica e eventos cíclicos.
2. **Motor de Risco (Classificação de OLA)**: Modelo baseado em XGBoost que calcula, para cada chamado em aberto, a probabilidade matemática de violação de OLA, reordenando a fila de atendimento por risco real.
3. **Motor de Detecção de Padrões (Clusterização de Causa Raiz)**: Algoritmo de K-Means (Machine Learning não supervisionado) que agrupa chamados isolados P2/P3 por proximidade textual nas descrições de erros, identificando assinaturas de falha crônicas na infraestrutura.

---

## 🏗️ Arquitetura de Dados (Bronze, Prata e Ouro)

O fluxo de dados da aplicação está estruturado em camadas de engenharia de dados dentro de um banco de dados **DuckDB**:

```
[Fontes de Dados] -> (LW-DATASET.xlsx)
       │
       ▼
[Camada Bronze]  -> (Tabela de incidentes brutos limpos e padronizados)
       │
       ▼
[Camada Prata]   -> (Tabelas agregadas de volumetria diária, OLA features e P2/P3)
       │
       ▼
[Camada Ouro]    -> (Modelagem preditiva: previsões, probabilidades e clusterização)
       │
       ▼
[Visualização]   -> (Dashboard interativo Streamlit em Dark Mode)
```

---

## 🧰 Stack Tecnológica

* **Ingestão & ETL**: Python + DuckDB + Pandas
* **Modelagem de IA**: Scikit-Learn (K-Means, Random Forest) + XGBoost
* **Visualização & Dashboard**: Streamlit (Dark Mode)
* **Banco de Dados**: DuckDB (PostgreSQL-ready para Supabase Cloud)

---

## 🚀 Como Executar o Projeto Localmente

### 1. Clonar o repositório
```bash
git clone https://github.com/seu-usuario/SynapseAIOps.git
cd SynapseAIOps
```

### 2. Instalar as dependências
Certifique-se de usar o Python 3.12 ou superior.
```bash
pip install -r requirements.txt
```

### 3. Rodar o Pipeline de Dados (ETL)
Isso criará o banco de dados `data/synapse_aiops.db` e processará o dataset da Locaweb nas camadas Bronze e Silver:
```bash
python src/pipeline.py
```

### 4. Executar o Treinamento dos Modelos de IA
Este script executa as análises preditivas, calcula os scores de risco de OLA e agrupa as causas raiz, salvando as tabelas Gold no banco de dados local:
```bash
python src/models.py
```

### 5. Iniciar o Painel Streamlit
Suba a interface gráfica interativa do projeto:
```bash
python -m streamlit run src/app.py
```
Acesse a aplicação no navegador em: `http://localhost:8501`

---

## 👥 Integrantes do Grupo (Grupo 69)

* **Ana Carolina Carvalho de Paula** - RM 561917
* **Barbara Ayumi Leoni Kodama** - RM 565513
* **Matheus Rodrigo Da Silva Santos** - RM 562378
