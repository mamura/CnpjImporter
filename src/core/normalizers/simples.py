from __future__ import annotations

from src.core.dto.simples import SimplesNormalized
from src.core.normalizers.common import (
    normalize_date_yyyymmdd,
    normalize_flag,
    require_digits,
)


def normalize_simples_row(row: dict[str, str]) -> SimplesNormalized:
    cnpj_basico = require_digits(
        row.get("cnpj_basico"),
        field_name="cnpj_basico",
        expected_length=8,
    )

    return SimplesNormalized(
        cnpj_basico=cnpj_basico,
        opcao_simples=normalize_flag(row.get("opcao_simples")),
        data_opcao_simples=normalize_date_yyyymmdd(row.get("data_opcao_simples")),
        data_exclusao_simples=normalize_date_yyyymmdd(row.get("data_exclusao_simples")),
        opcao_mei=normalize_flag(row.get("opcao_mei")),
        data_opcao_mei=normalize_date_yyyymmdd(row.get("data_opcao_mei")),
        data_exclusao_mei=normalize_date_yyyymmdd(row.get("data_exclusao_mei")),
    )