import streamlit as st
import pandas as pd
import plotly.express as px

# Configuração da página
st.set_page_config(page_title="Consolidador de Medições & NFs", layout="wide")

st.title("🏗️ MedSoli - Consolidador de Medições e Gestão de NFs")
st.caption("Protótipo Educacional (Prova de Conceito - PoC)")

# Barra lateral para upload dos dados fictícios
st.sidebar.header("📂 Importação de Dados Fictícios")
uploaded_med = st.sidebar.file_uploader("Upload: Planilha de Medições (CSV/XLSX)", type=["csv", "xlsx"])
uploaded_nfs = st.sidebar.file_uploader("Upload: Planilha de NFs (CSV/XLSX)", type=["csv", "xlsx"])

# Dados Fictícios Exemplo (caso o usuário não suba arquivos)
if not uploaded_med or not uploaded_nfs:
    st.info("💡 Carregando dados fictícios demonstrativos...")
    
    df_med = pd.DataFrame({
        "ID_Medicao": ["MED-001", "MED-002", "MED-003", "MED-004"],
        "Periodo": ["2026-01", "2026-01", "2026-02", "2026-02"],
        "Centro_de_Custo": ["CC-101 - Hospital", "CC-102 - Escola", "CC-101 - Hospital", "CC-103 - Pavimentação"],
        "Valor_Total": [150000.00, 85000.00, 210000.00, 120000.00]
    })

    df_nfs = pd.DataFrame({
        "ID_NF": ["NF-1001", "NF-1002", "NF-1003", "NF-1004", "NF-1005"],
        "ID_Medicao": ["MED-001", "MED-001", "MED-002", "MED-003", "MED-004"],
        "Numero_NF": ["000123", "000124", "000456", "000789", "000990"],
        "Municipio": ["Sorocaba", "Sorocaba", "Campinas", "Sorocaba", "Itu"],
        "Centro_de_Custo": ["CC-101 - Hospital", "CC-101 - Hospital", "CC-102 - Escola", "CC-101 - Hospital", "CC-103 - Pavimentação"],
        "Valor_NF": [100000.00, 50000.00, 85000.00, 210000.00, 120000.00]
    })
else:
    df_med = pd.read_csv(uploaded_med) if uploaded_med.name.endswith('.csv') else pd.read_excel(uploaded_med)
    df_nfs = pd.read_csv(uploaded_nfs) if uploaded_nfs.name.endswith('.csv') else pd.read_excel(uploaded_nfs)

# Criação das Abas da Aplicação
tab1, tab2 = st.tabs(["📊 Resumo de Medições (Período & Centro de Custo)", "🧾 Notas Fiscais (Município & Centro de Custo)"])

# ----------------------------------------------------
# ABA 1: Medições por Período e Centro de Custo
# ----------------------------------------------------
with tab1:
    st.subheader("Consolidado de Valores de Medição")
    
    # Filtros
    col1, col2 = st.columns(2)
    with col1:
        periodo_sel = st.multiselect("Filtrar por Período:", options=df_med["Periodo"].unique(), default=df_med["Periodo"].unique())
    with col2:
        cc_sel = st.multiselect("Filtrar por Centro de Custo:", options=df_med["Centro_de_Custo"].unique(), default=df_med["Centro_de_Custo"].unique())

    df_med_filtered = df_med[(df_med["Periodo"].isin(periodo_sel)) & (df_med["Centro_de_Custo"].isin(cc_sel))]

    # Métricas gerais
    st.metric("Valor Total Medido", f"R$ {df_med_filtered['Valor_Total'].sum():,.2f}")

    # Tabela Agrupada
    resumo_med = df_med_filtered.groupby(["Periodo", "Centro_de_Custo"])["Valor_Total"].sum().reset_index()
    st.dataframe(resumo_med, use_container_width=True)

    # Gráfico
    fig_med = px.bar(resumo_med, x="Periodo", y="Valor_Total", color="Centro_de_Custo", barmode="group", title="Valores Medidos por Período e Centro de Custo")
    st.plotly_chart(fig_med, use_container_width=True)

# ----------------------------------------------------
# ABA 2: Separação de NFs por Município e Centro de Custo
# ----------------------------------------------------
with tab2:
    st.subheader("Gestão e Detalhamento de Notas Fiscais")
    
    col_m, col_cc = st.columns(2)
    with col_m:
        mun_sel = st.multiselect("Filtrar por Município:", options=df_nfs["Municipio"].unique(), default=df_nfs["Municipio"].unique())
    with col_cc:
        cc_nf_sel = st.multiselect("Filtrar por Centro de Custo (NFs):", options=df_nfs["Centro_de_Custo"].unique(), default=df_nfs["Centro_de_Custo"].unique())

    df_nfs_filtered = df_nfs[(df_nfs["Municipio"].isin(mun_sel)) & (df_nfs["Centro_de_Custo"].isin(cc_nf_sel))]

    # Exibição de Resumo Agrupado
    st.markdown("### 📌 Resumo de NFs por Município e Centro de Custo")
    resumo_nfs = df_nfs_filtered.groupby(["Municipio", "Centro_de_Custo"])["Valor_NF"].sum().reset_index()
    st.dataframe(resumo_nfs, use_container_width=True)

    # Detalhamento Tabela
    st.markdown("### 📄 Lista Detalhada das Notas Fiscais")
    st.dataframe(df_nfs_filtered, use_container_width=True)
