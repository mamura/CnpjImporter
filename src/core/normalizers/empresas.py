from __future__ import annotations

from src.core.dto.empresas import EmpresaNormalized
from src.core.normalizers.common import (
    normalize_decimal_br,
    normalize_digits,
    normalize_text,
    require_digits,
)
from src.core.parsers.empresas import EmpresaRow


def normalize_empresa_row(row: EmpresaRow) -> EmpresaNormalized:
    cnpj_basico = require_digits(
        row.cnpj_basico,
        field_name="cnpj_basico",
        expected_length=8,
    )

    razao_social = normalize_text(row.razao_social)
    if razao_social is None:
        raise ValueError("razao_social não pode ser vazio")

    natureza_juridica = require_digits(
        row.natureza_juridica,
        field_name="natureza_juridica",
    )

    qualificacao_responsavel = require_digits(
        row.qualificacao_responsavel,
        field_name="qualificacao_responsavel",
    )

    return EmpresaNormalized(
        cnpj_basico=cnpj_basico,
        razao_social=razao_social,
        natureza_juridica=natureza_juridica,
        qualificacao_responsavel=qualificacao_responsavel,
        capital_social=normalize_decimal_br(row.capital_social),
        porte_empresa=normalize_digits(row.porte_empresa),
        ente_federativo_responsavel=normalize_text(
            row.ente_federativo_responsavel
        ),
    )