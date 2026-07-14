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

## 💡 Como Funciona o Synapse AIOps (De forma super simples)

Imagine que a Locaweb é um pronto-socorro digital gigante. Em vez de pacientes, ela atende chamados de servidores e sites com problemas. Veja como nossa solução resolve a confusão do início ao fim:

1. **A Chegada dos Dados (A Triagem):** O sistema recebe a planilha bruta com o histórico de tudo o que deu errado no passado.
2. **A Organização (A Faxina Digital):** Nosso organizador de dados ([pipeline.py](file:///D:/second_brain/knowledge/faculdade/SynapseAIOps/src/pipeline.py)) entra em ação. Ele limpa as informações bagunçadas e separa tudo em tabelas organizadas por data, produto e gravidade.
3. **O Cérebro da Inteligência Artificial ([models.py](file:///D:/second_brain/knowledge/faculdade/SynapseAIOps/src/models.py)):**
   - **Previsão do Tempo:** Ele descobre quantos problemas devem chegar amanhã. Isso ajuda o hospital digital a se preparar com analistas suficientes antes de o pico de chamados acontecer.
   - **Quem Atender Primeiro:** Ele calcula a chance matemática de cada chamado em aberto estourar o limite de tempo contratado. Assim, o chamado com maior risco fura a fila automaticamente para ser resolvido rápido.
   - **Descobrindo o Culpado Comum:** Em vez de olhar 100 reclamações isoladas, a IA junta as reclamações parecidas em grupos automáticos. Ela avisa: "Olha, essas 100 reclamações são causadas pelo mesmo servidor que caiu."
4. **O Painel Visual ([app.py](file:///D:/second_brain/knowledge/faculdade/SynapseAIOps/src/app.py)):** Em vez de telas cheias de códigos, o gestor de suporte olha para um dashboard simples e colorido que indica os próximos passos da operação de forma visual.

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

## 📁 Estrutura de Arquivos (De forma super simples)

Para fazer toda essa inteligência funcionar, o projeto é dividido em três arquivos principais de código:

* **[pipeline.py](file:///D:/second_brain/knowledge/faculdade/SynapseAIOps/src/pipeline.py) (O Organizador de Dados):** Ele pega a planilha de dados brutos da Locaweb, limpa as informações bagunçadas e as organiza em tabelas prontas dentro do nosso banco de dados local.
* **[models.py](file:///D:/second_brain/knowledge/faculdade/SynapseAIOps/src/models.py) (O Cérebro da IA):** Ele lê os dados organizados e treina a nossa inteligência artificial para prever o volume de chamados futuros, calcular o risco de atraso (estouro de OLA) e agrupar problemas semelhantes automaticamente.
* **[app.py](file:///D:/second_brain/knowledge/faculdade/SynapseAIOps/src/app.py) (A Tela do Dashboard):** É a interface visual interativa (criada com Streamlit) que consome essas previsões e mostra de forma simples para a equipe de suporte onde focar as suas ações.

---

## 💻 Painéis do Dashboard (O que você encontra na tela)

Ao acessar a interface visual desenvolvida em [app.py](file:///D:/second_brain/knowledge/faculdade/SynapseAIOps/src/app.py), você terá quatro abas de controle:

* **Visão Geral:** Um resumo rápido de tudo o que está acontecendo, mostrando o volume previsto para amanhã, o número total de chamados graves na fila e os alertas críticos de risco de atraso.
* **Motor de Clarividência:** A previsão do volume de chamados futuros (próximos 7 dias) para ajudar a coordenação a organizar a equipe antes de acontecer um pico de chamados.
* **Motor de Risco (OLA):** A lista de chamados em aberto classificada pelo risco matemático de atraso (estouro de OLA), garantindo que os técnicos saibam exatamente qual priorizar primeiro.
* **Agrupamento de Causa Raiz:** O detetive de falhas que junta problemas semelhantes e recorrentes (via clusterização) para que a engenharia resolva a causa raiz comum de uma vez só, em vez de atuar em erros isolados.

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
