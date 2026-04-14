from __future__ import annotations

from collections.abc import Callable, Iterable

from psycopg import Connection

from src.core.dto.estabelecimentos import EstabelecimentoNormalized


class EstabelecimentosWriter:
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

    def write(self, rows: Iterable[EstabelecimentoNormalized]) -> int:
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
                        f"Persistência ESTABELECIMENTOS: {total:,} linhas gravadas, "
                        f"{ignored:,} ignoradas por ausência em EMPRESAS"
                    )

        if buffer:
            written, skipped = self._flush(buffer)
            total += written
            ignored += skipped

            if self._on_progress is not None:
                self._on_progress(
                    f"Persistência ESTABELECIMENTOS: {total:,} linhas gravadas, "
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
                insert into cnpj.estabelecimentos (
                    cnpj,
                    cnpj_basico,
                    cnpj_ordem,
                    cnpj_dv,
                    identificador_matriz_filial,
                    nome_fantasia,
                    situacao_cadastral,
                    data_situacao_cadastral,
                    motivo_situacao_cadastral,
                    nome_cidade_exterior,
                    pais,
                    data_inicio_atividade,
                    cnae_fiscal_principal,
                    cnae_fiscal_secundaria,
                    tipo_logradouro,
                    logradouro,
                    numero,
                    complemento,
                    bairro,
                    cep,
                    uf,
                    municipio,
                    ddd_1,
                    telefone_1,
                    ddd_2,
                    telefone_2,
                    ddd_fax,
                    fax,
                    correio_eletronico,
                    situacao_especial,
                    data_situacao_especial,
                    referencia_ultima_carga,
                    ativo
                )
                values (
                    %(cnpj)s,
                    %(cnpj_basico)s,
                    %(cnpj_ordem)s,
                    %(cnpj_dv)s,
                    %(identificador_matriz_filial)s,
                    %(nome_fantasia)s,
                    %(situacao_cadastral)s,
                    %(data_situacao_cadastral)s,
                    %(motivo_situacao_cadastral)s,
                    %(nome_cidade_exterior)s,
                    %(pais)s,
                    %(data_inicio_atividade)s,
                    %(cnae_fiscal_principal)s,
                    %(cnae_fiscal_secundaria)s,
                    %(tipo_logradouro)s,
                    %(logradouro)s,
                    %(numero)s,
                    %(complemento)s,
                    %(bairro)s,
                    %(cep)s,
                    %(uf)s,
                    %(municipio)s,
                    %(ddd_1)s,
                    %(telefone_1)s,
                    %(ddd_2)s,
                    %(telefone_2)s,
                    %(ddd_fax)s,
                    %(fax)s,
                    %(correio_eletronico)s,
                    %(situacao_especial)s,
                    %(data_situacao_especial)s,
                    %(referencia_ultima_carga)s,
                    %(ativo)s
                )
                on conflict (cnpj)
                do update set
                    cnpj_basico = excluded.cnpj_basico,
                    cnpj_ordem = excluded.cnpj_ordem,
                    cnpj_dv = excluded.cnpj_dv,
                    identificador_matriz_filial = excluded.identificador_matriz_filial,
                    nome_fantasia = excluded.nome_fantasia,
                    situacao_cadastral = excluded.situacao_cadastral,
                    data_situacao_cadastral = excluded.data_situacao_cadastral,
                    motivo_situacao_cadastral = excluded.motivo_situacao_cadastral,
                    nome_cidade_exterior = excluded.nome_cidade_exterior,
                    pais = excluded.pais,
                    data_inicio_atividade = excluded.data_inicio_atividade,
                    cnae_fiscal_principal = excluded.cnae_fiscal_principal,
                    cnae_fiscal_secundaria = excluded.cnae_fiscal_secundaria,
                    tipo_logradouro = excluded.tipo_logradouro,
                    logradouro = excluded.logradouro,
                    numero = excluded.numero,
                    complemento = excluded.complemento,
                    bairro = excluded.bairro,
                    cep = excluded.cep,
                    uf = excluded.uf,
                    municipio = excluded.municipio,
                    ddd_1 = excluded.ddd_1,
                    telefone_1 = excluded.telefone_1,
                    ddd_2 = excluded.ddd_2,
                    telefone_2 = excluded.telefone_2,
                    ddd_fax = excluded.ddd_fax,
                    fax = excluded.fax,
                    correio_eletronico = excluded.correio_eletronico,
                    situacao_especial = excluded.situacao_especial,
                    data_situacao_especial = excluded.data_situacao_especial,
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

    def _to_record(self, row: EstabelecimentoNormalized) -> dict[str, object]:
        return {
            "cnpj": row.cnpj,
            "cnpj_basico": row.cnpj_basico,
            "cnpj_ordem": row.cnpj_ordem,
            "cnpj_dv": row.cnpj_dv,
            "identificador_matriz_filial": row.identificador_matriz_filial,
            "nome_fantasia": row.nome_fantasia,
            "situacao_cadastral": row.situacao_cadastral,
            "data_situacao_cadastral": row.data_situacao_cadastral,
            "motivo_situacao_cadastral": row.motivo_situacao_cadastral,
            "nome_cidade_exterior": row.nome_cidade_exterior,
            "pais": row.pais,
            "data_inicio_atividade": row.data_inicio_atividade,
            "cnae_fiscal_principal": row.cnae_fiscal_principal,
            "cnae_fiscal_secundaria": row.cnae_fiscal_secundaria,
            "tipo_logradouro": row.tipo_logradouro,
            "logradouro": row.logradouro,
            "numero": row.numero,
            "complemento": row.complemento,
            "bairro": row.bairro,
            "cep": row.cep,
            "uf": row.uf,
            "municipio": row.municipio,
            "ddd_1": row.ddd_1,
            "telefone_1": row.telefone_1,
            "ddd_2": row.ddd_2,
            "telefone_2": row.telefone_2,
            "ddd_fax": row.ddd_fax,
            "fax": row.fax,
            "correio_eletronico": row.correio_eletronico,
            "situacao_especial": row.situacao_especial,
            "data_situacao_especial": row.data_situacao_especial,
            "referencia_ultima_carga": self._referencia,
            "ativo": True,
        }