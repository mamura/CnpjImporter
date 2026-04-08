import psycopg

from src.config.settings import get_settings


def get_connection() -> psycopg.Connection:
    settings = get_settings()
    return psycopg.connect(settings.db_dsn)