from __future__ import annotations

from collections.abc import Callable

from src.core.extracted_batch import ExtractedBatchSummary
from src.core.persistence.empresas_pipeline import iter_normalized_empresas
from src.core.persistence.empresas_writer import EmpresasWriter
from src.core.persistence.import_lotes import (
    fail_import_lote,
    finish_import_lote,
    start_import_lote,
)
from src.db.connection import get_connection


def persist_empresas(
    extracted_summary: ExtractedBatchSummary,
    *,
    referencia: str,
    arquivo_origem: str | None = None,
    on_progress: Callable[[str], None] | None = None,
) -> int:
    with get_connection() as conn:
        start_import_lote(
            conn,
            referencia=referencia,
            arquivo_origem=arquivo_origem,
        )

        try:
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

            finish_import_lote(conn, referencia=referencia)
            return total

        except Exception as exc:
            fail_import_lote(
                conn,
                referencia=referencia,
                observacoes=str(exc),
            )
            raise