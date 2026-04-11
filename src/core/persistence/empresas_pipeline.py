from __future__ import annotations

from collections.abc import Callable, Iterator
from pathlib import Path

from src.core.csv_reader import read_csv_rows
from src.core.dto.empresas import EmpresaNormalized
from src.core.normalizers.empresas import normalize_empresa_row
from src.core.parsers.empresas import parse_empresa_row


def iter_normalized_empresas(
    files: list[Path],
    on_progress: Callable[[str], None] | None = None,
) -> Iterator[EmpresaNormalized]:
    total = 0
    errors = 0

    for file_path in files:
        if on_progress is not None:
            on_progress(f"Persistência EMPRESAS: lendo {file_path.name}")

        for row in read_csv_rows(file_path):
            try:
                parsed = parse_empresa_row(row)
                normalized = normalize_empresa_row(parsed)

                if normalized is None:
                    errors += 1
                    continue

                total += 1

                if on_progress is not None and total % 100_000 == 0:
                    on_progress(
                        f"Persistência EMPRESAS: {total:,} linhas preparadas"
                    )

                yield normalized

            except Exception as exc:
                errors += 1

                if on_progress is not None and (errors <= 10 or errors % 1_000 == 0):
                    on_progress(
                        f"Persistência EMPRESAS: erro #{errors:,}: {exc}"
                    )

    if on_progress is not None:
        on_progress(
            f"Persistência EMPRESAS: finalizado preparo "
            f"({total:,} válidas, {errors:,} ignoradas)"
        )