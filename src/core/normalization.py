from dataclasses import dataclass
from pathlib import Path

from src.core.csv_reader import read_csv_rows
from src.core.extracted_batch import ExtractedBatchSummary
from src.core.normalizers.empresas import normalize_empresa_row
from src.core.normalizers.estabelecimentos import normalize_estabelecimento_row
from src.core.normalizers.socios import normalize_socio_row
from src.core.normalizers.simples import normalize_simples_row
from src.core.parsers.empresas import parse_empresa_row
from src.core.parsers.estabelecimentos import parse_estabelecimento_row
from src.core.parsers.socios import parse_socio_row
from src.core.parsers.simples import parse_simples_row


@dataclass(slots=True)
class NormalizationSummary:
    empresas_count: int = 0
    estabelecimentos_count: int = 0
    socios_count: int = 0
    simples_count: int = 0


class NormalizationError(Exception):
    pass


def normalize_required_files(
    extracted_summary: ExtractedBatchSummary,
) -> NormalizationSummary:
    return NormalizationSummary(
        empresas_count=_normalize_empresas_files(extracted_summary.empresas),
        estabelecimentos_count=_normalize_estabelecimentos_files(
            extracted_summary.estabelecimentos
        ),
        socios_count=_normalize_socios_files(extracted_summary.socios),
        simples_count=_normalize_simples_files(extracted_summary.simples),
    )


def _normalize_empresas_files(files: list[Path]) -> int:
    total = 0

    for file_path in files:
        for row in read_csv_rows(file_path):
            parsed = parse_empresa_row(row)
            normalize_empresa_row(parsed)
            total += 1

    return total


def _normalize_estabelecimentos_files(files: list[Path]) -> int:
    total = 0

    for file_path in files:
        for row in read_csv_rows(file_path):
            parsed = parse_estabelecimento_row(row)
            normalize_estabelecimento_row(parsed)
            total += 1

    return total


def _normalize_socios_files(files: list[Path]) -> int:
    total = 0

    for file_path in files:
        for row in read_csv_rows(file_path):
            parsed = parse_socio_row(row)
            normalize_socio_row(parsed)
            total += 1

    return total


def _normalize_simples_files(files: list[Path]) -> int:
    total = 0

    for file_path in files:
        for row in read_csv_rows(file_path):
            parsed = parse_simples_row(row)
            normalize_simples_row(parsed)
            total += 1

    return total