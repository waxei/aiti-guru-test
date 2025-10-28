from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Настройки приложения"""
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")
    
    # PostgreSQL
    POSTGRES_USER: str = "aiti_user"
    POSTGRES_PASSWORD: str = "aiti_password"
    POSTGRES_DB: str = "aiti_db"
    POSTGRES_HOST: str = "postgres"
    POSTGRES_PORT: int = 5432
    
    # API
    API_V1_PREFIX: str = "/api/v1"
    PROJECT_NAME: str = "AITI Guru Test API"
    DEBUG: bool = True
    
    @property
    def database_url(self) -> str:
        """Формирование URL подключения к БД"""
        return (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )


settings = Settings()

