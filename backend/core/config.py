from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', extra='ignore')

    app_name: str = 'HAZM TUWAIQ'
    version: str = '5.0.0'
    api_prefix: str = '/api'
    secret_key: str = 'hazm-tuwaiq-dev-secret'
    access_token_minutes: int = 120
    cors_origins: list[str] = Field(
        default_factory=lambda: [
            'http://127.0.0.1:4173',
            'http://localhost:4173',
        ]
    )


settings = Settings()
