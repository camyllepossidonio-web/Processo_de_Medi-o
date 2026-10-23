import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import json

# Configuração da Página
st.set_page_config(
    page_title="Gestão de Medições | Sala Técnica",
    page_icon="🏗️",
    layout="wide"
)

# Estilização CSS customizada para visual de Engenharia Civil
st.markdown("""
    <style>
    .main-header {
        font-size:2.2rem;
        font-weight:700;
        color:#1E3A8A;
        margin-bottom:0px;
    }
    .sub-header {
        font-size:1.1rem;
        color:#4B5563;
        margin-bottom:20px;
    }
    .card-metric {
        background-color: #F3F4F6;
        padding: 15px;
        border-radius: 8px;
        border-left: 5px solid #1E3A8A;
    }
    </style>
""", unsafe_allow_html=True)

# Título do Sistema
st.markdown('<p class="main-header">🏗️ Assistente de Sala Técnica: Medição de Obras</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Protótipo de Prova de Conceito (PoC) para controle e validação de serviços acumulados</p>', unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# SIMULAÇÃO DE DADOS FICTÍCIOS (Em conformidade com a Regra de Ouro)
# -----------------------------------------------------------------------------
@st.cache_data
def carregar_dados_iniciais():
    dados = [
        {"Item": "1.1", "Servico": "Escavação Mecânica de Valas", "Unidade": "m³", "Qtd_Contratada": 1200.0, "Preco_Unitario": 45.0, "Acumulado_Anterior": 800.0, "Medicao_Atual": 300.0},
        {"Item": "1.2", "Servico": "Reaterro Compactado", "Unidade": "m³", "Qtd_Contratada": 950.0, "Preco_Unitario": 35.0, "Acumulado_Anterior": 500.0, "Medicao_Atual": 200.0},
        {"Item": "2.1", "Servico": "Concreto Armado fck=30MPa (Infra)", "Unidade": "m³", "Qtd_Contratada": 450.0, "Preco_Unitario": 780.0, "Acumulado_Anterior": 400.0, "Medicao_Atual": 50.0},
        {"Item": "2.2", "Servico": "Forma em Chapa Resinada", "Unidade": "m²", "Qtd_Contratada": 3200.0, "Preco_Unitario": 62.0, "Acumulado_Anterior": 2800.0, "Medicao_Atual": 300.0},
        {"Item": "2.3", "Servico": "Armação Aço CA-50", "Unidade": "kg", "Qtd_Contratada": 45000.0, "Preco_Unitario": 12.5, "Acumulado_Anterior": 38000.0, "Medicao_Atual": 6500.0},
        {"Item": "3.1", "Servico": "Alvenaria de Vedação 9x19x19", "Unidade": "m²", "Qtd_Contratada": 2500.0, "Preco_Unitario": 85.0, "Acumulado_Anterior": 1200.0, "Medicao_Atual": 800.0},
        {"Item": "3.2", "Servico": "Chapisco / Emboço Interno", "Unidade": "m²", "Qtd_Contratada": 5000.0, "Preco_Unitario": 42.0, "Acumulado_Anterior": 1500.0, "Medicao_Atual": 1200.0},
        {"Item": "4.1", "Servico": "Impermeabilização Manta Asfáltica", "Unidade": "m²", "Qtd_Contratada": 800.0, "Preco_Unitario": 110.0, "Acumulado_Anterior": 300.0, "Medicao_Atual": 250.0}
    ]
    return pd.DataFrame(dados)

# Sidebar - Operações e Arquivos
st.sidebar.header("📂 Operações de Medição")
fonte_dados = st.sidebar.radio("Selecione a Origem dos Dados:", ["Usar Base Fictícia Padrão", "Carregar Arquivo CSV"])

if fonte_dados == "Carregar Arquivo CSV":
    uploaded_file = st.sidebar.file_uploader("Upload da Planilha (.csv)", type=["csv"])
    if uploaded_file is not None:
        df_raw = pd.read_csv(uploaded_file)
    else:
        st.info("Aguardando upload do CSV. Exibindo dados de simulação padrão.")
        df_raw = carregar_dados_iniciais()
else:
    df_raw = carregar_dados_iniciais()

# -----------------------------------------------------------------------------
# PROCESSAMENTO DOS DADOS (Pandas & NumPy)
# -----------------------------------------------------------------------------
df = df_raw.copy()

# Cálculos de Engenharia/Sala Técnica por Linha
df['Total_Acumulado_Qtd'] = df['Acumulado_Anterior'] + df['Medicao_Atual']
df['Valor_Contratado'] = df['Qtd_Contratada'] * df['Preco_Unitario']
df['Valor_Medicao_Atual'] = df['Medicao_Atual'] * df['Preco_Unitario']
df['Valor_Acumulado_Total'] = df['Total_Acumulado_Qtd'] * df['Preco_Unitario']
df['Avanço_Fisico_%'] = np.round((df['Total_Acumulado_Qtd'] / df['Qtd_Contratada']) * 100, 2)
df['Alerta_Excesso'] = df['Total_Acumulado_Qtd'] > df['Qtd_Contratada']

# Resumo Financeiro Geral
total_contrato = df['Valor_Contratado'].sum()
total_medido_atual = df['Valor_Medicao_Atual'].sum()
total_acumulado = df['Valor_Acumulado_Total'].sum()
avanco_geral_% = (total_acumulado / total_contrato) * 100

# -----------------------------------------------------------------------------
# PAINEL DE CONTROLE / METRICAS
# -----------------------------------------------------------------------------
m1, m2, m3, m4 = st.columns(4)
m1.metric("Valor Total Contratado", f"R$ {total_contrato:,.2f}")
m2.metric("Medição Atual (Período)", f"R$ {total_medido_atual:,.2f}")
m3.metric("Total Acumulado", f"R$ {total_acumulado:,.2f}")
m4.metric("Avanço Físico Global", f"{avanco_geral_:.2f}%")

st.divider()

# -----------------------------------------------------------------------------
# TABELA INTERATIVA DE MEDIÇÃO
# -----------------------------------------------------------------------------
st.subheader("📋 Planilha de Medição por Serviços")

# Tabela editável apenas para a medição atual
df_editado = st.data_editor(
    df,
    column_config={
        "Item": st.column_config.TextColumn("Item", disabled=True),
        "Servico": st.column_config.TextColumn("Serviço / Descrição", disabled=True),
        "Unidade": st.column_config.TextColumn("Unid.", disabled=True),
        "Qtd_Contratada": st.column_config.NumberColumn("Qtd. Contrato", format="%.2f", disabled=True),
        "Preco_Unitario": st.column_config.NumberColumn("Preço Unit. (R$)", format="R$ %.2f", disabled=True),
        "Acumulado_Anterior": st.column_config.NumberColumn("Acum. Anterior", format="%.2f", disabled=True),
        "Medicao_Atual": st.column_config.NumberColumn("Medição Atual", format="%.2f"),
        "Total_Acumulado_Qtd": st.column_config.NumberColumn("Qtd. Total Acum.", format="%.2f", disabled=True),
        "Valor_Medicao_Atual": st.column_config.NumberColumn("Valor Atual (R$)", format="R$ %.2f", disabled=True),
        "Valor_Acumulado_Total": st.column_config.NumberColumn("Valor Acum. (R$)", format="R$ %.2f", disabled=True),
        "Avanço_Fisico_%": st.column_config.ProgressColumn("Avanço (%)", format="%.1f%%", min_value=0, max_value=100),
        "Alerta_Excesso": st.column_config.CheckboxColumn("Extrapolou?", disabled=True)
    },
    hide_index=True,
    use_container_width=True
)

# Alertas de Validação TÉCNICA
itens_excedidos = df_editado[df_editado['Alerta_Excesso'] == True]
if not itens_excedidos.empty:
    st.error(f"⚠️ **Atenção Sala Técnica:** Há {len(itens_excedidos)} item(ns) em que o acumulado ultrapassa o quantitativo contratado! Verifique Aditivos.")
    st.dataframe(itens_excedidos[['Item', 'Servico', 'Qtd_Contratada', 'Total_Acumulado_Qtd']], use_container_width=True)

# -----------------------------------------------------------------------------
# GRÁFICOS VISUAIS (PLOTLY)
# -----------------------------------------------------------------------------
st.divider()
col_g1, col_g2 = st.columns(2)

with col_g1:
    st.subheader("📊 Valor Acumulado por Serviço (R$)")
    fig_bar = px.bar(
        df_editado,
        x='Item',
        y=['Valor_Acumulado_Total', 'Valor_Contratado'],
        barmode='group',
        labels={'value': 'Reais (R$)', 'variable': 'Tipo'},
        title="Comparativo: Contratado vs. Medido Acumulado",
        color_discrete_sequence=['#1E3A8A', '#9CA3AF']
    )
    st.plotly_chart(fig_bar, use_container_width=True)

with col_g2:
    st.subheader("🎯 Curva de Progresso Físico (%)")
    fig_gauge = px.bar(
        df_editado,
        y='Servico',
        x='Avanço_Fisico_%',
        orientation='h',
        color='Avanço_Fisico_%',
        color_continuous_scale='Viridis',
        title="Percentual Concluído por Item"
    )
    st.plotly_chart(fig_gauge, use_container_width=True)

# -----------------------------------------------------------------------------
# CÉREBRO DA OPERAÇÃO: ANÁLISE DE IA (System Prompt de Engenharia)
# -----------------------------------------------------------------------------
st.divider()
st.subheader("🤖 Assistente Virtual de Sala Técnica (Análise de IA)")

system_prompt = """
Você é um Engenheiro Civil Sênior especialista em Gestão de Sala Técnica e Controle de Medições Financeiras de Obras.
Sua função é analisar os dados consolidados das planilhas de medição e fornecer um Parecer Técnico sucinto e profissional.

Regras de Resposta:
1. Avalie o avanço físico acumulado.
2. Identifique gargalos ou itens com risco de aditivo (onde o acumulado superou a quantidade contratada).
3. Apresente sugestões práticas de gestão de obra para o engenheiro de campo.
4. Mantenha tom estritamente técnico, direto e profissional.
"""

def gerar_parecer_simulado(df_analise):
    """
    Função com IA / Simulação baseada nas regras de negócios da Sala Técnica.
    Pronta para integração via API (Ex: OpenAI / Gemini SDK).
    """
    excessos = df_analise[df_analise['Alerta_Excesso'] == True]
    total_med = df_analise['Valor_Acumulado_Total'].sum()
    total_cont = df_analise['Valor_Contratado'].sum()
    prog_geral = (total_med / total_cont) * 100

    parecer = f"### 📝 Parecer Técnico de Medição\n\n"
    parecer += f"- **Avanço Global:** A obra atingiu **{prog_geral:.2f}%** do saldo contratual executado.\n"
    
    if not excessos.empty:
        parecer += f"- **Alerta Crítico:** Foram identificados **{len(excessos)} serviço(s)** com quantidade acumulada superior ao contrato:\n"
        for _, row in excessos.iterrows():
            parecer += f"  - *{row['Item']} - {row['Servico']}*: Excesso de {row['Total_Acumulado_Qtd'] - row['Qtd_Contratada']:.2f} {row['Unidade']}.\n"
        parecer += "\n**Recomendação:** Paralisar a medição destes itens ou emitir Termo Aditivo de Rerratificação contratual antes da liberação do pagamento.\n"
    else:
        parecer += "- **Status das Quantidades:** Todos os serviços medidos encontram-se rigorosamente dentro dos limites contratuais.\n"
    
    parecer += "\n**Próximos Passos:** Validar os diários de obra anexos referentes aos itens de maior impacto financeiro."
    return parecer

if st.button("🔍 Gerar Parecer Técnico com IA"):
    with st.spinner("Analisando planilha de medição acumulada..."):
        parecer_texto = gerar_parecer_simulado(df_editado)
        st.markdown(parecer_texto)

# Exportação do relatório acumulado
st.sidebar.divider()
csv_export = df_editado.to_csv(index=False).encode('utf-8')
st.sidebar.download_button(
    label="📥 Baixar Planilha Consolidada (CSV)",
    data=csv_export,
    file_name="medicao_acumulada_sala_tecnica.csv",
    mime="text/csv"
)
