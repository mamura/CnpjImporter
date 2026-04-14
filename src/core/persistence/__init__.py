from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from src.core.extracted_batch import ExtractedBatchSummary
from src.core.input_batch import InputBatchSummary
from src.core.persistence.empresas_pipeline import iter_normalized_empresas
from src.core.persistence.empresas_writer import EmpresasWriter
from src.core.persistence.estabelecimentos_pipeline import (
    iter_normalized_estabelecimentos,
)
from src.core.persistence.estabelecimentos_writer import EstabelecimentosWriter
from src.core.persistence.finalization import mark_missing_records_as_inactive
from src.core.persistence.import_lotes import (
    fail_import_lote,
    finish_import_lote,
    start_import_lote,
)
from src.core.persistence.simples_pipeline import iter_normalized_simples
from src.core.persistence.simples_writer import SimplesWriter
from src.core.persistence.socios_pipeline import iter_normalized_socios
from src.core.persistence.socios_writer import SociosWriter
from src.db.connection import get_connection


class PersistenceError(Exception):
    pass


@dataclass(slots=True)
class PersistenceSummary:
    empresas_count: int
    estabelecimentos_count: int
    socios_count: int
    simples_count: int

    @property
    def total_count(self) -> int:
        return (
            self.empresas_count
            + self.estabelecimentos_count
            + self.socios_count
            + self.simples_count
        )


def persist_required_files(
    *,
    input_summary: InputBatchSummary,
    extracted_summary: ExtractedBatchSummary,
    on_progress: Callable[[str], None] | None = None,
) -> PersistenceSummary:
    referencia = input_summary.reference
    arquivo_origem = str(input_summary.selected_zip_file_required)

    try:
        with get_connection() as conn:
            start_import_lote(
                conn,
                referencia=referencia,
                arquivo_origem=arquivo_origem,
            )

            empresas_count = _persist_empresas(
                conn=conn,
                extracted_summary=extracted_summary,
                referencia=referencia,
                on_progress=on_progress,
            )

            estabelecimentos_count = _persist_estabelecimentos(
                conn=conn,
                extracted_summary=extracted_summary,
                referencia=referencia,
                on_progress=on_progress,
            )

            socios_count = _persist_socios(
                conn=conn,
                extracted_summary=extracted_summary,
                referencia=referencia,
                on_progress=on_progress,
            )

            simples_count = _persist_simples(
                conn=conn,
                extracted_summary=extracted_summary,
                referencia=referencia,
                on_progress=on_progress,
            )

            mark_missing_records_as_inactive(
                conn,
                referencia=referencia,
            )

            finish_import_lote(conn, referencia=referencia)

            return PersistenceSummary(
                empresas_count=empresas_count,
                estabelecimentos_count=estabelecimentos_count,
                socios_count=socios_count,
                simples_count=simples_count,
            )

    except Exception as exc:
        try:
            with get_connection() as conn:
                fail_import_lote(
                    conn,
                    referencia=referencia,
                    observacoes=str(exc),
                )
        except Exception:
            pass

        raise PersistenceError(
            f"Erro na persistência dos arquivos obrigatórios: {exc}"
        ) from exc


def _persist_empresas(
    *,
    conn,
    extracted_summary: ExtractedBatchSummary,
    referencia: str,
    on_progress: Callable[[str], None] | None = None,
) -> int:
    if on_progress is not None:
        on_progress("Persistindo EMPRESAS...")

    writer = EmpresasWriter(
        conn,
        referencia=referencia,
        batch_size=5000,
        on_progress=on_progress,
    )

    total = writer.write(
        iter_normalized_empresas(
            extracted_summary.empresas,
            on_progress=on_progress,
        )
    )

    if on_progress is not None:
        on_progress(f"EMPRESAS persistidas: {total:,}")

    return total


def _persist_estabelecimentos(
    *,
    conn,
    extracted_summary: ExtractedBatchSummary,
    referencia: str,
    on_progress: Callable[[str], None] | None = None,
) -> int:
    if on_progress is not None:
        on_progress("Persistindo ESTABELECIMENTOS...")

    writer = EstabelecimentosWriter(
        conn,
        referencia=referencia,
        batch_size=5000,
        on_progress=on_progress,
    )

    total = writer.write(
        iter_normalized_estabelecimentos(
            extracted_summary.estabelecimentos,
            on_progress=on_progress,
        )
    )

    if on_progress is not None:
        on_progress(f"ESTABELECIMENTOS persistidos: {total:,}")

    return total


def _persist_socios(
    *,
    conn,
    extracted_summary: ExtractedBatchSummary,
    referencia: str,
    on_progress: Callable[[str], None] | None = None,
) -> int:
    if on_progress is not None:
        on_progress("Persistindo SOCIOS...")

    writer = SociosWriter(
        conn,
        referencia=referencia,
        batch_size=5000,
        delete_chunk_size=1000,
        on_progress=on_progress,
    )

    total = writer.write(
        iter_normalized_socios(
            extracted_summary.socios,
            on_progress=on_progress,
        )
    )

    if on_progress is not None:
        on_progress(f"SOCIOS persistidos: {total:,}")

    return total


def _persist_simples(
    *,
    conn,
    extracted_summary: ExtractedBatchSummary,
    referencia: str,
    on_progress: Callable[[str], None] | None = None,
) -> int:
    if on_progress is not None:
        on_progress("Persistindo SIMPLES...")

    writer = SimplesWriter(
        conn,
        referencia=referencia,
        batch_size=5000,
        on_progress=on_progress,
    )

    total = writer.write(
        iter_normalized_simples(
            extracted_summary.simples,
            on_progress=on_progress,
        )
    )

    if on_progress is not None:
        on_progress(f"SIMPLES persistidos: {total:,}")

    return total