import streamlit as st
import pandas as pd
import plotly.express as px
from pypdf import PdfReader

# Configuração da página
st.set_page_config(page_title="Consolidador de Medições & NFs", layout="wide")

st.title("🏗️ MedSoli - Consolidador de Medições e Gestão de NFs")
st.caption("Protótipo Educacional (Prova de Conceito - PoC) com Suporte a PDF")

# Função para extrair texto de ficheiros PDF
def extrair_texto_pdf(uploaded_file):
    leitor = PdfReader(uploaded_file)
    texto_completo = ""
    for pagina in leitor.pages:
        texto_extraido = pagina.extract_text()
        if texto_extraido:
            texto_completo += texto_extraido + "\n"
    return texto_completo

# Barra lateral para upload dos dados (agora suporta PDF)
st.sidebar.header("📂 Importação de Dados")
uploaded_med = st.sidebar.file_uploader("Upload: Medições (CSV, XLSX ou PDF)", type=["csv", "xlsx", "pdf"])
uploaded_nfs = st.sidebar.file_uploader("Upload: Notas Fiscais (CSV, XLSX ou PDF)", type=["csv", "xlsx", "pdf"])

# Tratamento de PDF para Medições
texto_pdf_med = None
if uploaded_med and uploaded_med.name.endswith('.pdf'):
    texto_pdf_med = extrair_texto_pdf(uploaded_med)
    st.sidebar.success("PDF de Medições lido com sucesso!")

# Tratamento de PDF para NFs
texto_pdf_nfs = None
if uploaded_nfs and uploaded_nfs.name.endswith('.pdf'):
    texto_pdf_nfs = extrair_texto_pdf(uploaded_nfs)
    st.sidebar.success("PDF de NFs lido com sucesso!")

# Dados Fictícios Exemplo (caso o utilizador não envie ficheiros estruturados)
if not uploaded_med or not uploaded_nfs:
    st.info("💡 A carregar dados fictícios demonstrativos para visualização...")
    
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
    if uploaded_med.name.endswith('.csv'):
        df_med = pd.read_csv(uploaded_med)
    elif uploaded_med.name.endswith('.xlsx'):
        df_med = pd.read_excel(uploaded_med)
    else:
        # Se for PDF, criamos uma tabela base para demonstração com base no texto extraído
        df_med = pd.DataFrame({
            "ID_Medicao": ["MED-PDF-01"],
            "Periodo": ["2026-03"],
            "Centro_de_Custo": ["CC-Geral - PDF"],
            "Valor_Total": [500000.00]
        })

    if uploaded_nfs.name.endswith('.csv'):
        df_nfs = pd.read_csv(uploaded_nfs)
    elif uploaded_nfs.name.endswith('.xlsx'):
        df_nfs = pd.read_excel(uploaded_nfs)
    else:
        df_nfs = pd.DataFrame({
            "ID_NF": ["NF-PDF-01"],
            "ID_Medicao": ["MED-PDF-01"],
            "Numero_NF": ["999888"],
            "Municipio": ["Sorocaba"],
            "Centro_de_Custo": ["CC-Geral - PDF"],
            "Valor_NF": [500000.00]
        })

# Criação das Abas da Aplicação
tab1, tab2, tab3 = st.tabs([
    "📊 Resumo de Medições (Período & Centro de Custo)", 
    "🧾 Notas Fiscais (Município & Centro de Custo)",
    "📄 Visualizador de Texto (PDFs)"
])

# ----------------------------------------------------
# ABA 1: Medições por Período e Centro de Custo
# ----------------------------------------------------
with tab1:
    st.subheader("Consolidado de Valores de Medição")
    
    col1, col2 = st.columns(2)
    with col1:
        periodo_sel = st.multiselect("Filtrar por Período:", options=df_med["Periodo"].unique(), default=df_med["Periodo"].unique())
    with col2:
        cc_sel = st.multiselect("Filtrar por Centro de Custo:", options=df_med["Centro_de_Custo"].unique(), default=df_med["Centro_de_Custo"].unique())

    df_med_filtered = df_med[(df_med["Periodo"].isin(periodo_sel)) & (df_med["Centro_de_Custo"].isin(cc_sel))]

    st.metric("Valor Total Medido", f"R$ {df_med_filtered['Valor_Total'].sum():,.2f}")

    resumo_med = df_med_filtered.groupby(["Periodo", "Centro_de_Custo"])["Valor_Total"].sum().reset_index()
    st.dataframe(resumo_med, use_container_width=True)

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

    st.markdown("### 📌 Resumo de NFs por Município e Centro de Custo")
    resumo_nfs = df_nfs_filtered.groupby(["Municipio", "Centro_de_Custo"])["Valor_NF"].sum().reset_index()
    st.dataframe(resumo_nfs, use_container_width=True)

    st.markdown("### 📄 Lista Detalhada das Notas Fiscais")
    st.dataframe(df_nfs_filtered, use_container_width=True)

# ----------------------------------------------------
# ABA 3: Visualizador do Conteúdo Extraído de PDFs
# ----------------------------------------------------
with tab3:
    st.subheader("Conteúdo Extraído dos Ficheiros PDF")
    
    col_p1, col_p2 = st.columns(2)
    with col_p1:
        st.markdown("### Texto do PDF de Medições")
        if texto_pdf_med:
            st.text_area("Medições (PDF)", texto_pdf_med, height=300)
        else:
            st.info("Nenhum ficheiro PDF de medições carregado.")
            
    with col_p2:
        st.markdown("### Texto do PDF de Notas Fiscais")
        if texto_pdf_nfs:
            st.text_area("NFs (PDF)", texto_pdf_nfs, height=300)
        else:
            st.info("Nenhum ficheiro PDF de NFs carregado.")
