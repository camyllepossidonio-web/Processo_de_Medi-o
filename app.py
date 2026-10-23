import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Sala Técnica - Medição de Obras", layout="wide")

st.title("🏗️ Gestão de Medições e Memória de Cálculo - Sala Técnica")
st.caption("Protótipo Educacional (PoC) para acompanhamento e cálculo acumulado de serviços em obras lineares.")

# --- DATAFRAMES FICTÍCIOS (Simulação de Dados) ---
@st.cache_data
def carregar_dados_iniciais():
    # Planilha Base / Contrato
    contrato_data = {
        'Item': ['1.1', '2.1', '3.1'],
        'Cod_Servico': ['SERV-01', 'SERV-02', 'SERV-03'],
        'Descricao_Servico': [
            'Escavação de Solo - 1ª Categoria',
            'Camada de Base de Brita Graduada',
            'Concretagem de OAE (Bueiros)'
        ],
        'Unid': ['m³', 'm³', 'm³'],
        'Qtd_Contratada': [1500.0, 800.0, 250.0],
        'Preco_Unit': [25.00, 110.00, 450.00],
        'Qtd_Acum_Anterior': [300.0, 150.0, 50.0]
    }
    
    # Memória de Cálculo Atual (Período) com KM e Estacas
    memoria_data = {
        'ID_Medicao': ['M-001', 'M-002', 'M-003'],
        'Cod_Servico': ['SERV-01', 'SERV-01', 'SERV-02'],
        'KM': ['KM 12+200', 'KM 12+400', 'KM 13+000'],
        'Estaca_Inicial': [244, 248, 260],
        'Fracao_Inicial': [0.0, 5.0, 0.0],
        'Estaca_Final': [248, 252, 265],
        'Fracao_Final': [5.0, 0.0, 10.0],
        'Qtd_Calculada': [150.0, 120.0, 85.0],
        'Data_Medicao': ['2026-10-10', '2026-10-12', '2026-10-15']
    }
    
    return pd.DataFrame(contrato_data), pd.DataFrame(memoria_data)

df_contrato, df_memoria = carregar_dados_iniciais()

# --- NAVEGAÇÃO POR ABAS ---
tab1, tab2, tab3 = st.tabs(["📋 Aba de Medição (Sintética)", "📐 Memória de Cálculo (Analítica)", "📊 Dashboards e Resumos"])

# --- ABA 1: SINTÉTICA DE MEDIÇÃO ---
with tab1:
    st.subheader("Planilha de Medição Acumulada")
    
    # Processamento: Agrupar Memória de Cálculo por Código de Serviço
    memoria_agrupada = df_memoria.groupby('Cod_Servico')['Qtd_Calculada'].sum().reset_index()
    memoria_agrupada.rename(columns={'Qtd_Calculada': 'Qtd_Periodo'}, inplace=True)
    
    # Merge com o Contrato
    df_medicao = pd.merge(df_contrato, memoria_agrupada, on='Cod_Servico', how='left')
    df_medicao['Qtd_Periodo'] = df_medicao['Qtd_Periodo'].fillna(0.0)
    
    # Cálculos Automáticos de Sala Técnica
    df_medicao['Qtd_Acum_Atual'] = df_medicao['Qtd_Acum_Anterior'] + df_medicao['Qtd_Periodo']
    df_medicao['Valor_Acumulado (R$)'] = df_medicao['Qtd_Acum_Atual'] * df_medicao['Preco_Unit']
    df_medicao['Valor_Periodo (R$)'] = df_medicao['Qtd_Periodo'] * df_medicao['Preco_Unit']
    df_medicao['Saldo_Qtd'] = df_medicao['Qtd_Contratada'] - df_medicao['Qtd_Acum_Atual']
    df_medicao['% Avanço'] = (df_medicao['Qtd_Acum_Atual'] / df_medicao['Qtd_Contratada']) * 100
    
    # Exibição Formatada
    st.dataframe(
        df_medicao.style.format({
            'Qtd_Contratada': '{:.2f}',
            'Qtd_Acum_Anterior': '{:.2f}',
            'Qtd_Periodo': '{:.2f}',
            'Qtd_Acum_Atual': '{:.2f}',
            'Saldo_Qtd': '{:.2f}',
            'Preco_Unit': 'R$ {:.2f}',
            'Valor_Periodo (R$)': 'R$ {:.2f}',
            'Valor_Acumulado (R$)': 'R$ {:.2f}',
            '% Avanço': '{:.1f}%'
        }),
        use_container_width=True
    )

# --- ABA 2: MEMÓRIA DE CÁLCULO ---
with tab2:
    st.subheader("Memória de Cálculo de Campo (Alimentação por Localização Linear)")
    st.write("Detalhamento geométrico e de estacamento que suporta os quantitativos medidos.")
    
    st.dataframe(df_memoria, use_container_width=True)
    
    st.markdown("---")
    st.write("### ➕ Adicionar Nova Linha de Memória de Cálculo")
    with st.form("form_memoria"):
        col1, col2, col3 = st.columns(3)
        with col1:
            cod_serv = st.selectbox("Selecione o Serviço", df_contrato['Cod_Servico'] + " - " + df_contrato['Descricao_Servico'])
            km = st.text_input("KM", "KM 12+500")
        with col2:
            est_ini = st.number_input("Estaca Inicial", min_value=0, value=250, step=1)
            frac_ini = st.number_input("Fração Inicial (m)", min_value=0.0, value=0.0, format="%.2f")
            est_fin = st.number_input("Estaca Final", min_value=0, value=255, step=1)
        with col3:
            frac_fin = st.number_input("Fração Final (m)", min_value=0.0, value=0.0, format="%.2f")
            qtd = st.number_input("Quantidade Calculada (Un/m³/m²)", min_value=0.0, value=50.0, format="%.2f")
            data_med = st.date_input("Data da Medição")
            
        btn_salvar = st.form_submit_button("Inserir na Memória")
        if btn_salvar:
            st.success("Nova medição por estacamento adicionada com sucesso! (Modo Simulação)")

# --- ABA 3: DASHBOARDS ---
with tab3:
    st.subheader("Resumo Financeiro e Avanço Físico")
    
    val_total_contrato = (df_medicao['Qtd_Contratada'] * df_medicao['Preco_Unit']).sum()
    val_total_acumulado = df_medicao['Valor_Acumulado (R$)'].sum()
    val_total_periodo = df_medicao['Valor_Periodo (R$)'].sum()
    
    col_m1, col_m2, col_m3 = st.columns(3)
    col_m1.metric("Valor Total do Contrato", f"R$ {val_total_contrato:,.2f}")
    col_m2.metric("Medido no Período", f"R$ {val_total_periodo:,.2f}")
    col_m3.metric("Total Acumulado Medido", f"R$ {val_total_acumulado:,.2f}", delta=f"{(val_total_acumulado/val_total_contrato)*100:.1f}% do Total")
    
    st.markdown("---")
    fig = px.bar(
        df_medicao, 
        x='Cod_Servico', 
        y=['Valor_Acumulado (R$)', 'Valor_Periodo (R$)'],
        barmode='group',
        title="Comparativo de Valores Medidos por Serviço (Acumulado x Período)",
        labels={'value': 'Valor (R$)', 'Cod_Servico': 'Código do Serviço'}
    )
    st.plotly_chart(fig, use_container_width=True)
