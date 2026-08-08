import os

from dotenv import load_dotenv

load_dotenv()


class Settings:
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    LANGCHAIN_TRACING_V2: str = os.getenv("LANGCHAIN_TRACING_V2", "false")
    LANGCHAIN_API_KEY: str = os.getenv("LANGCHAIN_API_KEY", "")
    LANGCHAIN_PROJECT: str = os.getenv("LANGCHAIN_PROJECT", "ABIA")

    # Model
    MODEL_NAME: str = "llama-3.3-70b-versatile"
    MAX_RETRIES: int = 3

    # Paths
    DATA_DIR: str = os.path.join(os.path.dirname(__file__), "../../data")


settings = Settings()
