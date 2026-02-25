from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    openrouter_api_key: str = ""
    openrouter_model: str = "anthropic/claude-sonnet-4-20250514"
    cors_origins: list[str] = ["http://localhost:5573"]
    sandbox_timeout: int = 10
    sandbox_max_memory_mb: int = 256
    data_dir: str = "data/problems"
    sessions_dir: str = "sessions"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
