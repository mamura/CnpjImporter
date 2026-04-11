from __future__ import annotations

from psycopg import Connection


def start_import_lote(
    conn: Connection,
    *,
    referencia: str,
    arquivo_origem: str | None,
) -> None:
    with conn.cursor() as cur:
        cur.execute(
            """
            insert into cnpj.import_lotes (
                referencia,
                arquivo_origem,
                status
            )
            values (%s, %s, 'running')
            on conflict (referencia)
            do update set
                arquivo_origem = excluded.arquivo_origem,
                iniciado_em = now(),
                finalizado_em = null,
                status = 'running',
                observacoes = null
            """,
            (referencia, arquivo_origem),
        )


def finish_import_lote(
    conn: Connection,
    *,
    referencia: str,
) -> None:
    with conn.cursor() as cur:
        cur.execute(
            """
            update cnpj.import_lotes
               set finalizado_em = now(),
                   status = 'finished'
             where referencia = %s
            """,
            (referencia,),
        )


def fail_import_lote(
    conn: Connection,
    *,
    referencia: str,
    observacoes: str,
) -> None:
    with conn.cursor() as cur:
        cur.execute(
            """
            update cnpj.import_lotes
               set finalizado_em = now(),
                   status = 'failed',
                   observacoes = %s
             where referencia = %s
            """,
            (observacoes[:4000], referencia),
        )