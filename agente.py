from langchain_openai import ChatOpenAI
from langchain_experimental.agents import create_pandas_dataframe_agent

class SafeDataAgent:
    def __init__(self, openai_api_key: str):
        self.llm = ChatOpenAI(
            temperature=0,
            openai_api_key=openai_api_key,
            model="gpt-3.5-turbo"  
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
        return self.agent.run(pergunta)