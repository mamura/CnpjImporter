from __future__ import annotations

from collections.abc import Callable, Iterable

from psycopg import Connection

from src.core.dto.simples import SimplesNormalized


class SimplesWriter:
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

    def write(self, rows: Iterable[SimplesNormalized]) -> int:
        total = 0
        ignored = 0
        buffer: list[dict[str, object]] = []

        for row in rows:
            buffer.append(self._to_record(row))

            if len(buffer) >= self._batch_size:
                written, skipped = self._flush(buffer)
                total += written
                ignored += skipped
                buffer.clear()

                if self._on_progress is not None:
                    self._on_progress(
                        f"Persistência SIMPLES: {total:,} linhas gravadas, "
                        f"{ignored:,} ignoradas por ausência em EMPRESAS"
                    )

        if buffer:
            written, skipped = self._flush(buffer)
            total += written
            ignored += skipped

            if self._on_progress is not None:
                self._on_progress(
                    f"Persistência SIMPLES: {total:,} linhas gravadas, "
                    f"{ignored:,} ignoradas por ausência em EMPRESAS"
                )

        return total

    def _flush(self, rows: list[dict[str, object]]) -> tuple[int, int]:
        existing = self._load_existing_empresas(
            [str(row["cnpj_basico"]) for row in rows]
        )

        valid_rows = [
            row for row in rows
            if str(row["cnpj_basico"]) in existing
        ]

        skipped = len(rows) - len(valid_rows)

        if not valid_rows:
            return 0, skipped

        with self._conn.cursor() as cur:
            cur.executemany(
                """
                insert into cnpj.simples (
                    cnpj_basico,
                    opcao_simples,
                    data_opcao_simples,
                    data_exclusao_simples,
                    opcao_mei,
                    data_opcao_mei,
                    data_exclusao_mei,
                    referencia_ultima_carga,
                    ativo
                )
                values (
                    %(cnpj_basico)s,
                    %(opcao_simples)s,
                    %(data_opcao_simples)s,
                    %(data_exclusao_simples)s,
                    %(opcao_mei)s,
                    %(data_opcao_mei)s,
                    %(data_exclusao_mei)s,
                    %(referencia_ultima_carga)s,
                    %(ativo)s
                )
                on conflict (cnpj_basico)
                do update set
                    opcao_simples = excluded.opcao_simples,
                    data_opcao_simples = excluded.data_opcao_simples,
                    data_exclusao_simples = excluded.data_exclusao_simples,
                    opcao_mei = excluded.opcao_mei,
                    data_opcao_mei = excluded.data_opcao_mei,
                    data_exclusao_mei = excluded.data_exclusao_mei,
                    referencia_ultima_carga = excluded.referencia_ultima_carga,
                    ativo = true
                """,
                valid_rows,
            )

        return len(valid_rows), skipped

    def _load_existing_empresas(self, cnpjs_basicos: list[str]) -> set[str]:
        with self._conn.cursor() as cur:
            cur.execute(
                """
                select cnpj_basico
                  from cnpj.empresas
                 where cnpj_basico = any(%s)
                """,
                (cnpjs_basicos,),
            )
            return {row[0] for row in cur.fetchall()}

    def _to_record(self, row: SimplesNormalized) -> dict[str, object]:
        return {
            "cnpj_basico": row.cnpj_basico,
            "opcao_simples": row.opcao_simples,
            "data_opcao_simples": row.data_opcao_simples,
            "data_exclusao_simples": row.data_exclusao_simples,
            "opcao_mei": row.opcao_mei,
            "data_opcao_mei": row.data_opcao_mei,
            "data_exclusao_mei": row.data_exclusao_mei,
            "referencia_ultima_carga": self._referencia,
            "ativo": True,
        }