import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings
from pydantic import PostgresDsn, computed_field
from typing import Optional

load_dotenv()

class Settings(BaseSettings):
    PROJECT_NAME: str = "Uzbekistan Customs Calculator"
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = os.getenv("SECRET_KEY", "changethis")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_PORT: str = "5432"
    POSTGRES_DB: str = "customs_db"

    DATABASE_URL: str = os.getenv("DATABASE_URL", "")

    LEX_UZ_DUTY_URL: str = "https://lex.uz/docs/3802366"
    LEX_UZ_EXCISE_URL: str = "https://lex.uz/docs/6718877"
    
    @computed_field
    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        return "sqlite+aiosqlite:///./customs_app.db"

    @computed_field
    @property
    def SYNC_DATABASE_URI(self) -> str:
        return str(PostgresDsn.build(
            scheme="postgresql+psycopg2",
            username=self.POSTGRES_USER,
            password=self.POSTGRES_PASSWORD,
            host=self.POSTGRES_SERVER,
            port=int(self.POSTGRES_PORT),
            path=self.POSTGRES_DB,
        ))

    class Config:
        case_sensitive = True
        extra = "ignore"

settings = Settings()
