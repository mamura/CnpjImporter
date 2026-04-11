from __future__ import annotations

from src.core.dto.simples import SimplesNormalized
from src.core.normalizers.common import (
    normalize_date_yyyymmdd,
    normalize_flag,
    require_digits,
)
from src.core.parsers.simples import SimplesRow


def normalize_simples_row(row: SimplesRow) -> SimplesNormalized | None:
    try:
        cnpj_basico = require_digits(
            row.cnpj_basico,
            field_name="cnpj_basico",
            expected_length=8,
        )
    except ValueError:
        return None

    try:
        opcao_simples = normalize_flag(row.opcao_simples)
        data_opcao_simples = normalize_date_yyyymmdd(row.data_opcao_simples)
        data_exclusao_simples = normalize_date_yyyymmdd(
            row.data_exclusao_simples
        )
        opcao_mei = normalize_flag(row.opcao_mei)
        data_opcao_mei = normalize_date_yyyymmdd(row.data_opcao_mei)
        data_exclusao_mei = normalize_date_yyyymmdd(row.data_exclusao_mei)
    except ValueError:
        return None

    return SimplesNormalized(
        cnpj_basico=cnpj_basico,
        opcao_simples=opcao_simples,
        data_opcao_simples=data_opcao_simples,
        data_exclusao_simples=data_exclusao_simples,
        opcao_mei=opcao_mei,
        data_opcao_mei=data_opcao_mei,
        data_exclusao_mei=data_exclusao_mei,
    )