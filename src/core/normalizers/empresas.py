from __future__ import annotations

from src.core.dto.empresas import EmpresaNormalized
from src.core.normalizers.common import (
    normalize_decimal_br,
    normalize_digits,
    normalize_text,
    require_digits,
)
from src.core.parsers.empresas import EmpresaRow


def normalize_empresa_row(row: EmpresaRow) -> EmpresaNormalized | None:
    try:
        cnpj_basico = require_digits(
            row.cnpj_basico,
            field_name="cnpj_basico",
            expected_length=8,
        )
    except ValueError:
        return None

    razao_social = normalize_text(row.razao_social)
    if razao_social is None:
        return None

    natureza_juridica = _normalize_required_digits(
        row.natureza_juridica,
        field_name="natureza_juridica",
    )
    if natureza_juridica is None:
        return None

    qualificacao_responsavel = _normalize_required_digits(
        row.qualificacao_responsavel,
        field_name="qualificacao_responsavel",
    )
    if qualificacao_responsavel is None:
        return None

    try:
        capital_social = normalize_decimal_br(row.capital_social)
    except ValueError:
        return None

    return EmpresaNormalized(
        cnpj_basico=cnpj_basico,
        razao_social=razao_social,
        natureza_juridica=natureza_juridica,
        qualificacao_responsavel=qualificacao_responsavel,
        capital_social=capital_social,
        porte_empresa=normalize_digits(row.porte_empresa),
        ente_federativo_responsavel=normalize_text(
            row.ente_federativo_responsavel
        ),
    )


def _normalize_required_digits(
    value: str | None,
    *,
    field_name: str,
) -> str | None:
    try:
        return require_digits(value, field_name=field_name)
    except ValueError:
        return None