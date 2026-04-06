from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    openai_api_key: str
    model_name: str = "gpt-4o-mini"
    embedding_model: str = "text-embedding-3-small"
    chunk_size: int = 1000
    chunk_overlap: int = 200
    top_k: int = 4
    webshare_proxy_username: str = ""
    webshare_proxy_password: str = ""
    faiss_index_path: str = "artifacts/faiss_index"

    class Config:
        env_file = ".env"

settings = Settings()