from __future__ import annotations

from collections.abc import Callable, Iterator
from pathlib import Path

from src.core.csv_reader import read_csv_rows
from src.core.dto.socios import SocioNormalized
from src.core.normalizers.socios import normalize_socio_row
from src.core.parsers.socios import parse_socio_row


def iter_normalized_socios(
    files: list[Path],
    on_progress: Callable[[str], None] | None = None,
) -> Iterator[SocioNormalized]:
    total = 0
    errors = 0

    for file_path in files:
        if on_progress is not None:
            on_progress(f"Persistência SOCIOS: lendo {file_path.name}")

        for row in read_csv_rows(file_path):
            try:
                parsed = parse_socio_row(row)
                normalized = normalize_socio_row(parsed)

                if normalized is None:
                    errors += 1
                    continue

                total += 1

                if on_progress is not None and total % 100_000 == 0:
                    on_progress(
                        f"Persistência SOCIOS: {total:,} linhas preparadas"
                    )

                yield normalized

            except Exception as exc:
                errors += 1

                if on_progress is not None and (errors <= 10 or errors % 1_000 == 0):
                    on_progress(
                        f"Persistência SOCIOS: erro #{errors:,}: {exc}"
                    )

    if on_progress is not None:
        on_progress(
            f"Persistência SOCIOS: finalizado preparo "
            f"({total:,} válidas, {errors:,} ignoradas)"
        )