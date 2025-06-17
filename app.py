# app.py
import streamlit as st
import pandas as pd
import os
from dotenv import load_dotenv

from agente import SafeDataAgent  # Certifique-se de que a classe esteja em agente.py

# === Carrega a chave da API ===
load_dotenv()
openai_key = os.getenv("OPENAI_API_KEY")

# === Interface ===
st.set_page_config(page_title="Consulta NFs", layout="centered")
st.title("📊 Consulta Inteligente de Notas Fiscais")
st.markdown("Faça perguntas sobre os dados de notas fiscais carregando os arquivos ou usando a pasta local.")

# === Escolha do modo de carregamento ===
modo = st.radio("Como deseja carregar os arquivos?", ["📁 Usar diretório atual", "📤 Fazer upload manual"])

df_cabecalho = df_itens = None

# === Opção 1: Usar arquivos locais no diretório atual ===
if modo == "📁 Usar diretório atual":
    pasta = os.getcwd()
    st.write(f"🔍 Procurando arquivos em: `{pasta}`")

    # Caminhos esperados
    cab_path = os.path.join(pasta, "202401_NFs_Cabecalho.csv")
    itens_path = os.path.join(pasta, "202401_NFs_Itens.csv")

    if os.path.exists(cab_path) and os.path.exists(itens_path):
        df_cabecalho = pd.read_csv(cab_path)
        df_itens = pd.read_csv(itens_path)
        st.success("Arquivos encontrados e carregados com sucesso!")
    else:
        st.error("⚠️ Arquivos CSV não encontrados no diretório atual.")

# === Opção 2: Upload manual ===
else:
    uploaded_cabecalho = st.file_uploader("📄 Upload do arquivo de Cabeçalho", type="csv")
    uploaded_itens = st.file_uploader("📄 Upload do arquivo de Itens", type="csv")

    if uploaded_cabecalho and uploaded_itens:
        df_cabecalho = pd.read_csv(uploaded_cabecalho)
        df_itens = pd.read_csv(uploaded_itens)
        st.success("Arquivos enviados e lidos com sucesso!")

# === Inicializa agente e executa pergunta ===
if df_cabecalho is not None and df_itens is not None:
    try:
        agent = SafeDataAgent(openai_api_key=openai_key)
        agent.carregar_dataframes(df_cabecalho, df_itens)

        pergunta = st.text_input("❓ Faça sua pergunta:", placeholder="Ex: Qual item teve maior volume entregue?")
        if pergunta:
            with st.spinner("Consultando..."):
                resposta = agent.perguntar(pergunta)
                st.success("🧠 Resposta do agente:")
                st.write(resposta)
    except Exception as e:
        st.error(f"Erro ao processar os dados: {e}")
