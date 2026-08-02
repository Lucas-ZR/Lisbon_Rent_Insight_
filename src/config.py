# src/config.py
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env.test", extra="ignore")

    database_name: str
    schema_name: str
    proxy_username: str
    password: str
    domain_name: str
    port: int

    motherduck_token: str
