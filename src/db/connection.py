from __future__ import annotations

import os
from contextlib import contextmanager
from collections.abc import Iterator

import psycopg
from psycopg import Connection


def build_postgres_dsn() -> str:
    host = os.getenv("POSTGRES_HOST", "localhost")
    port = os.getenv("POSTGRES_PORT", "5432")
    dbname = os.getenv("POSTGRES_DB", "apicnpj")
    user = os.getenv("POSTGRES_USER", "apicnpj")
    password = os.getenv("POSTGRES_PASSWORD", "apicnpj")

    return (
        f"host={host} "
        f"port={port} "
        f"dbname={dbname} "
        f"user={user} "
        f"password={password}"
    )


@contextmanager
def get_connection() -> Iterator[Connection]:
    conn = psycopg.connect(build_postgres_dsn())

    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()