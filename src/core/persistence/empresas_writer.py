from __future__ import annotations

from collections.abc import Callable, Iterable
from decimal import Decimal

from psycopg import Connection
from psycopg.extras import execute_batch

from src.core.dto.empresas import EmpresaNormalized


class EmpresasWriter:
    def __init__(
        self,
        conn: Connection,
        *,
        referencia: str,
        batch_size: int = 5000,
        on_progress: Callable[[str], None] | None = None,
    ) -> None:
        self._conn = conn
        self._referencia = referencia
        self._batch_size = batch_size
        self._on_progress = on_progress

    def write(self, rows: Iterable[EmpresaNormalized]) -> int:
        total = 0
        buffer: list[dict[str, str | Decimal | None | bool]] = []

        for row in rows:
            buffer.append(self._to_record(row))

            if len(buffer) >= self._batch_size:
                total += self._flush(buffer)
                buffer.clear()

                if self._on_progress is not None:
                    self._on_progress(
                        f"Persistência EMPRESAS: {total:,} linhas gravadas"
                    )

        if buffer:
            total += self._flush(buffer)

            if self._on_progress is not None:
                self._on_progress(
                    f"Persistência EMPRESAS: {total:,} linhas gravadas"
                )

        return total

    def _flush(
        self,
        rows: list[dict[str, str | Decimal | None | bool]],
    ) -> int:
        with self._conn.cursor() as cur:
            execute_batch(
                cur,
                """
                insert into cnpj.empresas (
                    cnpj_basico,
                    razao_social,
                    natureza_juridica,
                    qualificacao_responsavel,
                    capital_social,
                    porte_empresa,
                    ente_federativo_responsavel,
                    referencia_ultima_carga,
                    ativo
                )
                values (
                    %(cnpj_basico)s,
                    %(razao_social)s,
                    %(natureza_juridica)s,
                    %(qualificacao_responsavel)s,
                    %(capital_social)s,
                    %(porte_empresa)s,
                    %(ente_federativo_responsavel)s,
                    %(referencia_ultima_carga)s,
                    %(ativo)s
                )
                on conflict (cnpj_basico)
                do update set
                    razao_social = excluded.razao_social,
                    natureza_juridica = excluded.natureza_juridica,
                    qualificacao_responsavel = excluded.qualificacao_responsavel,
                    capital_social = excluded.capital_social,
                    porte_empresa = excluded.porte_empresa,
                    ente_federativo_responsavel = excluded.ente_federativo_responsavel,
                    referencia_ultima_carga = excluded.referencia_ultima_carga,
                    ativo = true
                """,
                rows,
                page_size=self._batch_size,
            )

        return len(rows)

    def _to_record(
        self,
        row: EmpresaNormalized,
    ) -> dict[str, str | Decimal | None | bool]:
        return {
            "cnpj_basico": row.cnpj_basico,
            "razao_social": row.razao_social,
            "natureza_juridica": row.natureza_juridica,
            "qualificacao_responsavel": row.qualificacao_responsavel,
            "capital_social": row.capital_social,
            "porte_empresa": row.porte_empresa,
            "ente_federativo_responsavel": row.ente_federativo_responsavel,
            "referencia_ultima_carga": self._referencia,
            "ativo": True,
        }