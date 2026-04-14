from __future__ import annotations

from psycopg import Connection


def mark_missing_records_as_inactive(
    conn: Connection,
    *,
    referencia: str,
) -> None:
    tables = [
        "empresas",
        "estabelecimentos",
        "socios",
        "simples",
    ]

    with conn.cursor() as cur:
        for table_name in tables:
            cur.execute(
                f"""
                update cnpj.{table_name}
                   set ativo = false
                 where referencia_ultima_carga is distinct from %s
                """,
                (referencia,),
            )