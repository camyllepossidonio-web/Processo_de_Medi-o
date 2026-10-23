import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

st.set_page_config(page_title="Gestão de Medição de Obras - Sala Técnica", layout="wide")

st.title("🏗️ Gestão de Medição de Obras - Sala Técnica")
st.markdown("Protótipo Educacional (PoC) para preenchimento de planilha de medição, cálculo de acumulados por linha e parecer técnico.")

# Sidebar para dados fictícios
st.sidebar.header("📁 Dados do Contrato")
uploaded_file = st.sidebar.file_uploader("Carregar CSV de Serviços (Fictício)", type=["csv"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
else:
    # Dados de exemplo padrão (fictícios)
    data = {
        "Item": [1.1, 1.2, 2.1, 2.2, 3.1],
        "Servico": [
            "Mobilização e Canteiro",
            "Locação da Obra",
            "Escavação Manual",
            "Concretagem de Fundações",
            "Alvenaria de Elevação"
        ],
        "Unidade": ["verba", "m2", "m3", "m3", "m2"],
        "Quantidade_Contrato": [1.0, 500.0, 120.0, 45.0, 300.0],
        "Preco_Unitario": [15000.00, 25.00, 85.00, 450.00, 120.00],
        "Quantidade_Mes_Anterior": [1.0, 300.0, 80.0, 20.0, 0.0],
        "Quantidade_Atual": [0.0, 200.0, 40.0, 25.0, 150.0]
    }
    df = pd.DataFrame(data)

# Cálculo automático de valores
df["Valor_Contrato"] = df["Quantidade_Contrato"] * df["Preco_Unitario"]
df["Quantidade_Acumulada"] = df["Quantidade_Mes_Anterior"] + df["Quantidade_Atual"]
df["Valor_Acumulado"] = df["Quantidade_Acumulada"] * df["Preco_Unitario"]
df["Saldo_Contratual"] = df["Quantidade_Contrato"] - df["Quantidade_Acumulada"]

st.subheader("📋 Tabela de Medição de Serviços")
st.markdown("Edite diretamente as colunas de **Quantidade Atual** na tabela abaixo para simular a medição do mês:")

# Editor de dados interativo
edited_df = st.data_editor(df, num_rows="dynamic", use_container_width=True)

# Recalcular com base nas edições do utilizador
edited_df["Quantidade_Acumulada"] = edited_df["Quantidade_Mes_Anterior"] + edited_df["Quantidade_Atual"]
edited_df["Valor_Acumulado"] = edited_df["Quantidade_Acumulada"] * edited_df["Preco_Unitario"]
edited_df["Saldo_Contratual"] = edited_df["Quantidade_Contrato"] - edited_df["Quantidade_Acumulada"]

# Totais gerais (Correção aplicada aqui: avanco_geral_pct sem o símbolo %)
total_contrato = edited_df["Valor_Contrato"].sum()
total_acumulado = edited_df["Valor_Acumulado"].sum()
avanco_geral_pct = (total_acumulado / total_contrato) * 100 if total_contrato > 0 else 0

st.markdown("---")
col1, col2, col3 = st.columns(3)
col1.metric("Valor Total do Contrato", f"R$ {total_contrato:,.2f}")
col2.metric("Valor Acumulado Medido", f"R$ {total_acumulado:,.2f}")
col3.metric("Avanço Físico Geral", f"{avanco_geral_pct:.2f}%")

st.markdown("---")
st.subheader("📊 Gráfico de Evolução Financeira por Serviço")
fig = px.bar(
    edited_df,
    x="Servico",
    y=["Valor_Acumulado", "Valor_Contrato"],
    barmode="group",
    labels={"value": "Valor (R$)", "Servico": "Serviço", "variable": "Legenda"},
    title="Comparativo: Valor Acumulado vs. Valor Contratado"
)
st.plotly_chart(fig, use_container_width=True)

st.markdown("---")
st.subheader("🤖 Parecer Técnico da Sala Técnica (IA / Análise)")
if st.button("Gerar Análise Crítica da Medição"):
    st.success("Análise gerada com sucesso com base nos dados atuais da medição:")
    if avanco_geral_pct > 80:
        st.info("A obra encontra-se em estágio avançado de execução. Recomenda-se verificação final de pendências e ensaios tecnológicos de entrega.")
    elif avanco_geral_pct > 30:
        st.info("O ritmo da medição está compatível com o cronograma planeado. Atenção aos itens com saldo contratual reduzido.")
    else:
        st.info("Fase inicial da obra. Acompanhar a mobilização e o rendimento das equipes de campo.")
