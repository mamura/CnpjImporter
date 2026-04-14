from functools import lru_cache
from pathlib import Path
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name:   str = Field(default="cnpj-importer", alias="APP_NAME")
    app_env:    str = Field(default="local", alias="APP_ENV")
    app_debug:  bool = Field(default=True, alias="APP_DEBUG")

    input_dir:      Path = Field(default=Path("./data/input"), alias="INPUT_DIR")
    extracted_dir:  Path = Field(default=Path("./data/extracted"), alias="EXTRACTED_DIR")
    temp_dir:       Path = Field(default=Path("./data/temp"), alias="TEMP_DIR")
    log_dir:        Path = Field(default=Path("./logs"), alias="LOG_DIR")

    db_host:        str = Field(alias="DB_HOST")
    db_port:        int = Field(default=5432, alias="DB_PORT")
    db_name:        str = Field(alias="DB_NAME")
    db_user:        str = Field(alias="DB_USER")
    db_password:    str = Field(alias="DB_PASSWORD")
    db_sslmode:     str = Field(default="prefer", alias="DB_SSLMODE")

    @property
    def db_dsn(self) -> str:
        return (
            f"host={self.db_host} "
            f"port={self.db_port} "
            f"dbname={self.db_name} "
            f"user={self.db_user} "
            f"password={self.db_password} "
            f"sslmode={self.db_sslmode}"
        )


@lru_cache
def get_settings() -> Settings:
    return Settings()

settings = Settings()