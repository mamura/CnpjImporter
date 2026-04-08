from __future__ import annotations

from collections.abc import Iterator

from src.core.csv_reader import iter_csv_rows
from src.core.parsers.empresas import parse_empresa_row
from src.core.parsers.estabelecimentos import parse_estabelecimento_row
from src.core.parsers.socios import parse_socio_row
from src.core.parsers.simples import parse_simples_row
from src.core.normalizers.empresas import normalize_empresa_row
from src.core.normalizers.estabelecimentos import normalize_estabelecimento_row
from src.core.normalizers.socios import normalize_socio_row
from src.core.normalizers.simples import normalize_simples_row


def iter_empresas_from_file(file_path) -> Iterator:
    for raw_row in iter_csv_rows(file_path):
        yield normalize_empresa_row(parse_empresa_row(raw_row))


def iter_estabelecimentos_from_file(file_path) -> Iterator:
    for raw_row in iter_csv_rows(file_path):
        yield normalize_estabelecimento_row(parse_estabelecimento_row(raw_row))


def iter_socios_from_file(file_path) -> Iterator:
    for raw_row in iter_csv_rows(file_path):
        yield normalize_socio_row(parse_socio_row(raw_row))


def iter_simples_from_file(file_path) -> Iterator:
    for raw_row in iter_csv_rows(file_path):
        yield normalize_simples_row(parse_simples_row(raw_row))