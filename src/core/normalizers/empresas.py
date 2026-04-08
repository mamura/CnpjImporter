from __future__ import annotations

from src.core.dto.empresas import EmpresaNormalized
from src.core.normalizers.common import (
    normalize_decimal_br,
    normalize_digits,
    normalize_text,
)


def normalize_empresa_row(row: dict[str, str]) -> EmpresaNormalized:
    cnpj_basico = normalize_digits(row["cnpj_basico"])
    if cnpj_basico is None or len(cnpj_basico) != 8:
        raise ValueError(f"cnpj_basico inválido: {row['cnpj_basico']}")

    razao_social = normalize_text(row["razao_social"])
    if razao_social is None:
        raise ValueError("razao_social não pode ser vazio")

    natureza_juridica = normalize_digits(row["natureza_juridica"])
    if natureza_juridica is None:
        raise ValueError("natureza_juridica inválida")

    qualificacao_responsavel = normalize_digits(row["qualificacao_responsavel"])
    if qualificacao_responsavel is None:
        raise ValueError("qualificacao_responsavel inválida")

    return EmpresaNormalized(
        cnpj_basico=cnpj_basico,
        razao_social=razao_social,
        natureza_juridica=natureza_juridica,
        qualificacao_responsavel=qualificacao_responsavel,
        capital_social=normalize_decimal_br(row["capital_social"]),
        porte_empresa=normalize_digits(row["porte_empresa"]),
        ente_federativo_responsavel=normalize_text(row["ente_federativo_responsavel"]),
    )