# app.py
import streamlit as st
import pandas as pd
import os
import zipfile
import tempfile
from dotenv import load_dotenv

from agente import SafeDataAgent

load_dotenv()
google_api_key = os.getenv("GOOGLE_API_KEY")

st.set_page_config(page_title="Notas Fiscais IA", layout="centered")
st.title("📦 Consulta Inteligente de Notas Fiscais via ZIP")

st.markdown("Faça o upload de um `.zip`")

if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'agent_initialized' not in st.session_state:
    st.session_state.agent_initialized = False
if 'df_cabecalho' not in st.session_state:
    st.session_state.df_cabecalho = None
if 'df_itens' not in st.session_state:
    st.session_state.df_itens = None
if 'safe_data_agent' not in st.session_state:
    st.session_state.safe_data_agent = None
if 'current_question_text' not in st.session_state:
    st.session_state.current_question_text = ""

zip_file = st.file_uploader("📁 Faça upload do arquivo .zip", type="zip", key="zip_uploader")

if zip_file and not st.session_state.agent_initialized:
    st.session_state.chat_history = []
    
    with tempfile.TemporaryDirectory() as tmpdir:
        zip_path = os.path.join(tmpdir, "upload.zip")
        with open(zip_path, "wb") as f:
            f.write(zip_file.getbuffer())

        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            zip_ref.extractall(tmpdir)

        cab_path = os.path.join(tmpdir, "202401_NFs_Cabecalho.csv")
        itens_path = os.path.join(tmpdir, "202401_NFs_Itens.csv")

        if os.path.exists(cab_path) and os.path.exists(itens_path):
            st.session_state.df_cabecalho = pd.read_csv(cab_path)
            st.session_state.df_itens = pd.read_csv(itens_path)
            st.success("✔️ Arquivos extraídos e lidos com sucesso!")
            try:
                agent_instance = SafeDataAgent(google_api_key=google_api_key)
                agent_instance.carregar_dataframes(st.session_state.df_cabecalho, st.session_state.df_itens)
                st.session_state.safe_data_agent = agent_instance
                st.session_state.agent_initialized = True
            except Exception as e:
                st.error(f"Erro ao inicializar agente: {e}")
                st.session_state.agent_initialized = False 
        else:
            st.error("❌ Arquivos CSV não encontrados no ZIP. Verifique os nomes dos arquivos.")
            st.session_state.agent_initialized = False 

for entry in st.session_state.chat_history:
    st.markdown(f"**❓ Você:** {entry['question']}")
    st.markdown(f"**🧠 Resposta:** {entry['answer']}")
    st.markdown("---") 


if st.session_state.safe_data_agent is not None:
    def handle_submit():
        user_question = st.session_state.input_text_key 
        if user_question:
            with st.spinner("Consultando os dados..."):
                try:
                    resposta = st.session_state.safe_data_agent.perguntar(user_question)
                    st.session_state.chat_history.append({"question": user_question, "answer": resposta})
                    st.session_state.input_text_key = "" 
                except Exception as e:
                    st.error(f"Erro ao consultar os dados: {e}")

    st.text_input(
        "❓ Faça sua pergunta:",
        placeholder="Ex: Qual item teve o maior volume entregue?",
        key="input_text_key", 
        on_change=handle_submit, 
        label_visibility="visible" 
    )

else:
    if st.session_state.df_cabecalho is None or st.session_state.df_itens is None:
        st.info("Por favor, faça o upload de um arquivo ZIP para começar.")