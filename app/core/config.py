from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "AI Knowledge & Action Platform"
    app_version: str = "0.1.0"
    rag_rate_limit_requests: int = 10
    rag_rate_limit_window_seconds: int = 60
    app_description: str = (
        "Backend platform for RAG, AI agents and knowledge-driven actions."
        
    )
    redis_url: str = (
        "redis://localhost:6379/0"
    )

    query_embedding_cache_ttl_seconds: int = (
        3600
    )

    environment: str = "development"
    database_url: str
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "qwen3.5:4b"
    

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
