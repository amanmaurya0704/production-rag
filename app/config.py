import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    PROJECT_ID: str = os.getenv("PROJECT_ID")
    LOCATION: str = os.getenv("LOCATION")
    GCP_DOC_AI_PROCESSOR_ID: str = os.getenv("GCP_DOC_AI_PROCESSOR_ID")
    GCP_DOC_AI_LOCATION: str = os.getenv("GCP_DOC_AI_LOCATION")
    RAW_BUCKET : str = os.getenv("GCP_RAW_BUCKET")
    PROCESSED_BUCKET : str = os.getenv("GCP_PROCESSED_BUCKET")

    QDRANT_URL: str = os.getenv("QDRANT_ENDPOINT")
    QDRANT_API_KEY: str = os.getenv("QDRANT_API_KEY")
    QDRANT_COLLECTION: str = "production-rag"

    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY")
    GROQ_MODEL: str = "llama-3.3-70b-versatile"

    LANGSMITH_TRACING = os.getenv("LANGSMITH_TRACING",  "true")
    LANGSMITH_API_KEY = os.getenv("LANGSMITH_API_KEY")
    LANGSMITH_PROJECT = os.getenv("LANGSMITH_PROJECT")
    LANGSMITH_ENDPOINT = os.getenv("LANGSMITH_ENDPOINT", "https://api.smith.langchain.com")

os.environ["LANGSMITH_TRACING_V2"] = os.getenv("LANGSMITH_TRACING", "true")
os.environ["LANGSMITH_API_KEY"] = os.getenv("LANGSMITH_API_KEY")
os.environ["LANGSMITH_PROJECT"] = os.getenv("LANGSMITH_PROJECT")
os.environ["LANGSMITH_ENDPOINT"] = os.getenv("LANGSMITH_ENDPOINT", "https://api.smith.langchain.com")

settings = Settings()


