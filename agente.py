# agente.py
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_experimental.agents import create_pandas_dataframe_agent

class SafeDataAgent:
    def __init__(self, google_api_key: str):
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash",
            google_api_key=google_api_key,
            temperature=0
        )
        self.agent = None

    def carregar_dataframes(self, *dataframes):
        if len(dataframes) == 2:
            df_merged = dataframes[0].merge(dataframes[1], on="CHAVE DE ACESSO", how="left")
        else:
            df_merged = dataframes[0]

        self.agent = create_pandas_dataframe_agent(
            self.llm,
            df_merged,
            verbose=True,
            allow_dangerous_code=True
        )

    def perguntar(self, pergunta: str):
        if not self.agent:
            raise Exception("Nenhum DataFrame carregado.")

        # Adiciona uma instrução ao prompt para encorajar uma resposta mais detalhada
        # ou com múltiplos pontos.
        # Você pode ajustar esta instrução conforme a necessidade.
        instrucao_adicional = "Responda sempre em português do Brasil, de forma objetiva. Forneça pelo menos 3 pontos ou aspectos relevantes, se aplicável à pergunta."
        pergunta_completa = f"{pergunta} {instrucao_adicional}"

        return self.agent.run(pergunta_completa) # Usa a pergunta_completa