from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

from src.core.csv_reader import read_csv_rows
from src.core.extracted_batch import ExtractedBatchSummary
from src.core.normalizers.empresas import normalize_empresa_row
from src.core.normalizers.estabelecimentos import normalize_estabelecimento_row
from src.core.normalizers.simples import normalize_simples_row
from src.core.normalizers.socios import normalize_socio_row
from src.core.parsers.empresas import parse_empresa_row
from src.core.parsers.estabelecimentos import parse_estabelecimento_row
from src.core.parsers.simples import parse_simples_row
from src.core.parsers.socios import parse_socio_row


class NormalizationError(Exception):
    pass


@dataclass(slots=True)
class NormalizationSummary:
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


def normalize_required_files(
    extracted_summary: ExtractedBatchSummary,
    on_progress: Callable[[str], None] | None = None,
) -> NormalizationSummary:
    return NormalizationSummary(
        empresas_count=_normalize_empresas_files(
            extracted_summary.empresas,
            on_progress=on_progress,
        ),
        estabelecimentos_count=_normalize_estabelecimentos_files(
            extracted_summary.estabelecimentos,
            on_progress=on_progress,
        ),
        socios_count=_normalize_socios_files(
            extracted_summary.socios,
            on_progress=on_progress,
        ),
        simples_count=_normalize_simples_files(
            extracted_summary.simples,
            on_progress=on_progress,
        ),
    )


def _report(
    on_progress: Callable[[str], None] | None,
    message: str,
) -> None:
    if on_progress is not None:
        on_progress(message)


def _normalize_empresas_files(
    files: list[Path],
    on_progress: Callable[[str], None] | None = None,
) -> int:
    total = 0

    for file_path in files:
        _report(on_progress, f"Normalizando EMPRESAS: {file_path.name}")

        for row in read_csv_rows(file_path):
            parsed = parse_empresa_row(row)
            normalize_empresa_row(parsed)
            total += 1

            if total % 100_000 == 0:
                _report(on_progress, f"EMPRESAS: {total:,} linhas processadas")

    return total


def _normalize_estabelecimentos_files(
    files: list[Path],
    on_progress: Callable[[str], None] | None = None,
) -> int:
    total = 0

    for file_path in files:
        _report(on_progress, f"Normalizando ESTABELECIMENTOS: {file_path.name}")

        for row in read_csv_rows(file_path):
            parsed = parse_estabelecimento_row(row)
            normalize_estabelecimento_row(parsed)
            total += 1

            if total % 100_000 == 0:
                _report(on_progress, f"ESTABELECIMENTOS: {total:,} linhas processadas")

    return total


def _normalize_socios_files(
    files: list[Path],
    on_progress: Callable[[str], None] | None = None,
) -> int:
    total = 0

    for file_path in files:
        _report(on_progress, f"Normalizando SOCIOS: {file_path.name}")

        for row in read_csv_rows(file_path):
            parsed = parse_socio_row(row)
            normalize_socio_row(parsed)
            total += 1

            if total % 100_000 == 0:
                _report(on_progress, f"SOCIOS: {total:,} linhas processadas")

    return total


def _normalize_simples_files(
    files: list[Path],
    on_progress: Callable[[str], None] | None = None,
) -> int:
    total = 0

    for file_path in files:
        _report(on_progress, f"Normalizando SIMPLES: {file_path.name}")

        for row in read_csv_rows(file_path):
            parsed = parse_simples_row(row)
            normalize_simples_row(parsed)
            total += 1

            if total % 100_000 == 0:
                _report(on_progress, f"SIMPLES: {total:,} linhas processadas")

    return total