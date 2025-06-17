# app.py
import streamlit as st
import pandas as pd
import os
import zipfile
import tempfile
from dotenv import load_dotenv

from agente import SafeDataAgent

# === 🛡️ Carrega a chave da OpenAI ===
load_dotenv()
openai_key = os.getenv("OPENAI_API_KEY")

st.set_page_config(page_title="Notas Fiscais IA", layout="centered")
st.title("📦 Consulta Inteligente de Notas Fiscais via ZIP")

st.markdown("Faça o upload de um `.zip` contendo os arquivos `202401_NFs_Cabecalho.csv` e `202401_NFs_Itens.csv`.")

# === Upload do ZIP ===
zip_file = st.file_uploader("📁 Faça upload do arquivo .zip", type="zip")

df_cabecalho = df_itens = None

if zip_file:
    with tempfile.TemporaryDirectory() as tmpdir:
        # Salva o .zip temporariamente
        zip_path = os.path.join(tmpdir, "upload.zip")
        with open(zip_path, "wb") as f:
            f.write(zip_file.getbuffer())

        # Extrai o conteúdo
        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            zip_ref.extractall(tmpdir)

        # Tenta ler os arquivos extraídos
        cab_path = os.path.join(tmpdir, "202401_NFs_Cabecalho.csv")
        itens_path = os.path.join(tmpdir, "202401_NFs_Itens.csv")

        if os.path.exists(cab_path) and os.path.exists(itens_path):
            df_cabecalho = pd.read_csv(cab_path)
            df_itens = pd.read_csv(itens_path)
            st.success("✔️ Arquivos extraídos e lidos com sucesso!")
        else:
            st.error("❌ Arquivos CSV não encontrados no ZIP. Verifique os nomes dos arquivos.")

# === Cria o agente se os dados foram carregados ===
if df_cabecalho is not None and df_itens is not None:
    try:
        agent = SafeDataAgent(openai_api_key=openai_key)
        agent.carregar_dataframes(df_cabecalho, df_itens)

        pergunta = st.text_input("❓ Faça sua pergunta:", placeholder="Ex: Qual item teve o maior volume entregue?")

        if pergunta:
            with st.spinner("Consultando os dados..."):
                resposta = agent.perguntar(pergunta)
                st.success("🧠 Resposta:")
                st.write(resposta)
    except Exception as e:
        st.error(f"Erro ao inicializar agente: {e}")