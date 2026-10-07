from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "AI Knowledge & Action Platform"
    app_version: str = "0.1.0"
    app_description: str = (
        "Backend platform for RAG, AI agents and knowledge-driven actions."
    )
    environment: str = "development"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )


settings = Settings()