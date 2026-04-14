from __future__ import annotations

from collections.abc import Callable, Iterable

from psycopg import Connection

from src.core.dto.socios import SocioNormalized


class SociosWriter:
    def __init__(
        self,
        conn: Connection,
        *,
        referencia: str,
        batch_size: int = 5000,
        delete_chunk_size: int = 1000,
        on_progress: Callable[[str], None] | None = None,
    ) -> None:
        self._conn = conn
        self._referencia = referencia
        self._batch_size = batch_size
        self._delete_chunk_size = delete_chunk_size
        self._on_progress = on_progress

    def write(self, rows: Iterable[SocioNormalized]) -> int:
        total = 0
        ignored = 0
        insert_buffer: list[dict[str, object]] = []
        delete_buffer: list[str] = []
        deleted_companies: set[str] = set()

        for row in rows:
            record = self._to_record(row)
            insert_buffer.append(record)

            if len(insert_buffer) >= self._batch_size:
                written, skipped = self._flush(insert_buffer, deleted_companies, delete_buffer)
                total += written
                ignored += skipped
                insert_buffer.clear()

                if self._on_progress is not None:
                    self._on_progress(
                        f"Persistência SOCIOS: {total:,} linhas gravadas, "
                        f"{ignored:,} ignoradas por ausência em EMPRESAS"
                    )

        if insert_buffer:
            written, skipped = self._flush(insert_buffer, deleted_companies, delete_buffer)
            total += written
            ignored += skipped

            if self._on_progress is not None:
                self._on_progress(
                    f"Persistência SOCIOS: {total:,} linhas gravadas, "
                    f"{ignored:,} ignoradas por ausência em EMPRESAS"
                )

        return total

    def _flush(
        self,
        rows: list[dict[str, object]],
        deleted_companies: set[str],
        delete_buffer: list[str],
    ) -> tuple[int, int]:
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

        for row in valid_rows:
            cnpj_basico = str(row["cnpj_basico"])

            if cnpj_basico not in deleted_companies:
                deleted_companies.add(cnpj_basico)
                delete_buffer.append(cnpj_basico)

        if delete_buffer:
            self._delete_existing_for_companies(delete_buffer)
            delete_buffer.clear()

        with self._conn.cursor() as cur:
            cur.executemany(
                """
                insert into cnpj.socios (
                    cnpj_basico,
                    identificador_socio,
                    nome_socio_razao_social,
                    cpf_cnpj_socio,
                    qualificacao_socio,
                    data_entrada_sociedade,
                    pais,
                    representante_legal,
                    nome_representante,
                    qualificacao_representante_legal,
                    faixa_etaria,
                    referencia_ultima_carga,
                    ativo
                )
                values (
                    %(cnpj_basico)s,
                    %(identificador_socio)s,
                    %(nome_socio_razao_social)s,
                    %(cpf_cnpj_socio)s,
                    %(qualificacao_socio)s,
                    %(data_entrada_sociedade)s,
                    %(pais)s,
                    %(representante_legal)s,
                    %(nome_representante)s,
                    %(qualificacao_representante_legal)s,
                    %(faixa_etaria)s,
                    %(referencia_ultima_carga)s,
                    %(ativo)s
                )
                """,
                valid_rows,
            )

        return len(valid_rows), skipped

    def _delete_existing_for_companies(self, companies: list[str]) -> None:
        with self._conn.cursor() as cur:
            cur.execute(
                """
                delete from cnpj.socios
                 where cnpj_basico = any(%s)
                """,
                (companies,),
            )

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

    def _to_record(self, row: SocioNormalized) -> dict[str, object]:
        return {
            "cnpj_basico": row.cnpj_basico,
            "identificador_socio": row.identificador_socio,
            "nome_socio_razao_social": row.nome_socio_razao_social,
            "cpf_cnpj_socio": row.cpf_cnpj_socio,
            "qualificacao_socio": row.qualificacao_socio,
            "data_entrada_sociedade": row.data_entrada_sociedade,
            "pais": row.pais,
            "representante_legal": row.representante_legal,
            "nome_representante": row.nome_representante,
            "qualificacao_representante_legal": row.qualificacao_representante_legal,
            "faixa_etaria": row.faixa_etaria,
            "referencia_ultima_carga": self._referencia,
            "ativo": True,
        }