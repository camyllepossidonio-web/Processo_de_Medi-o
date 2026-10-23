import io
import os
import pandas as pd
import pypdf
import streamlit as st
from openai import AzureOpenAI

# 1. Configuração inicial da página (DEVE ser o primeiro comando Streamlit)
st.set_page_config(
    page_title="ChatBot RAG - Microsoft Foundry", page_icon="🤖", layout="centered"
)

# 2. CSS Customizado para Estilização e Borda Profissional
st.markdown(
    """
    <style>
        .stApp {
            background-color: #f4f6f9;
        }
        [data-testid="stSidebar"] {
            background-color: #ffffff;
            border-right: 1px solid #e2e8f0;
        }
        h1 {
            color: #1e293b;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }
    </style>
""",
    unsafe_allow_html=True,
)

# 3. Configuração da API (Microsoft Foundry / Azure OpenAI)
API_KEY = "6t2pTNsmNafDyo53MDAFIrvvQRBZXP7dLcr5j3TLxMS34LQVq3ZUJQQJ99CHACHYHv6XJ3w3AAAAACOGT7os"
DEPLOYMENT_NAME = "gpt-4.1-mini"
ENDPOINT = "https://marcelomaffeis-05082026-resource.services.ai.azure.com/"

# Inicialização segura do cliente
client = None
try:
  client = AzureOpenAI(
      api_key=API_KEY, api_version="2024-02-01", azure_endpoint=ENDPOINT
  )
except Exception as e:
  st.error(f"Erro ao inicializar o cliente AzureOpenAI: {e}")

# 4. Gerenciamento de Estado (Session State)
if "document_text" not in st.session_state:
  st.session_state.document_text = ""

if "messages" not in st.session_state:
  st.session_state.messages = []

# Título da Aplicação
st.title("🤖 ChatBot Inteligente com RAG")
st.markdown(
    "Faça upload de um documento (**Excel**, **PDF** ou **TXT**) na barra"
    " lateral para utilizá-lo como contexto nas conversas."
)

# 5. Barra Lateral - Upload de Arquivos
st.sidebar.header("📁 Base de Conhecimento")
uploaded_file = st.sidebar.file_uploader(
    "Envie seu arquivo", type=["xlsx", "xls", "pdf", "txt"]
)

if uploaded_file is not None:
  file_extension = uploaded_file.name.split(".")[-1].lower()
  try:
    if file_extension == "txt":
      st.session_state.document_text = uploaded_file.getvalue().decode("utf-8")
      st.sidebar.success(f"TXT '{uploaded_file.name}' carregado!")

    elif file_extension == "pdf":
      pdf_reader = pypdf.PdfReader(io.BytesIO(uploaded_file.getvalue()))
      extracted_text = ""
      for page in pdf_reader.pages:
        text = page.extract_text()
        if text:
          extracted_text += text + "\n"
      st.session_state.document_text = extracted_text
      st.sidebar.success(f"PDF '{uploaded_file.name}' carregado!")

    elif file_extension in ["xlsx", "xls"]:
      df = pd.read_excel(uploaded_file)
      st.session_state.document_text = df.to_string(index=False)
      st.sidebar.success(f"Excel '{uploaded_file.name}' carregado!")

  except Exception as e:
    st.sidebar.error(f"Erro ao processar o arquivo: {e}")
    st.session_state.document_text = ""

if st.session_state.document_text:
  st.sidebar.info("📄 Contexto ativo pronto para consultas!")

# 6. Interface de Chat
for message in st.session_state.messages:
  with st.chat_message(message["role"]):
    st.markdown(message["content"])

# Captura de Entrada do Usuário
if prompt := st.chat_input("Digite sua mensagem ou pergunta sobre o arquivo..."):
  st.session_state.messages.append({"role": "user", "content": prompt})
  with st.chat_message("user"):
    st.markdown(prompt)

  # Montagem do Prompt RAG
  system_prompt = (
      "Você é um assistente virtual especialista e prestativo. Responda de"
      " maneira clara e objetiva com base no contexto fornecido."
  )

  if st.session_state.document_text:
    system_prompt += (
        "\n\nContexto do documento/planilha:\n--- INÍCIO DO CONTEXTO"
        f" ---\n{st.session_state.document_text}\n--- FIM DO CONTEXTO ---"
    )

  messages_payload = [{"role": "system", "content": system_prompt}]
  for m in st.session_state.messages:
    messages_payload.append({"role": m["role"], "content": m["content"]})

  # Chamada à API
  with st.chat_message("assistant"):
    with st.spinner("Analisando e gerando resposta..."):
      if client is None:
        st.error("Erro: Cliente da API não configurado.")
      else:
        try:
          response = client.chat.completions.create(
              model=DEPLOYMENT_NAME, messages=messages_payload, temperature=0.7
          )
          bot_response = response.choices[0].message.content
          st.markdown(bot_response)
          st.session_state.messages.append(
              {"role": "assistant", "content": bot_response}
          )
        except Exception as e:
          st.error(f"Erro na comunicação com a API: {e}")
