from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    environment: str = "development"
    database_url: str = "postgresql+psycopg://postgres:postgres@localhost:5432/cerno"
    storage_connection_string: str = "UseDevelopmentStorage=true"
    ocr_queue_name: str = "cerno-ocr"
    ocr_container_name: str = "cerno-ocr"
    tesseract_cmd: str = "tesseract"
    tesseract_lang: str = "ind+eng"
    max_upload_bytes: int = 5_000_000
    session_days: int = 7
    allowed_origin: str = "http://localhost:3000"

    @property
    def production(self) -> bool:
        return self.environment.lower() == "production"


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
