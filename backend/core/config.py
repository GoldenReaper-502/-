from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', extra='ignore')

    app_name: str = 'HAZM TUWAIQ'
    version: str = '4.0.0'
    api_prefix: str = '/api'
    cors_origins: list[str] = Field(
        default_factory=lambda: [
            'http://127.0.0.1:4173',
            'http://localhost:4173',
        ]
    )


settings = Settings()
