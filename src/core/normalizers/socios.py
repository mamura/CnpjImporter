from __future__ import annotations

from src.core.dto.socios import SocioNormalized
from src.core.normalizers.common import (
    compose_cnpj_optional,
    compose_cpf,
    normalize_date_yyyymmdd,
    normalize_digits,
    normalize_text,
    require_digits,
)


def normalize_socio_row(row: dict[str, str]) -> SocioNormalized:
    cnpj_basico = require_digits(
        row.get("cnpj_basico"),
        field_name="cnpj_basico",
        expected_length=8,
    )

    nome_socio_razao_social = normalize_text(row.get("nome_socio_razao_social"))
    if nome_socio_razao_social is None:
        raise ValueError("nome_socio_razao_social é obrigatório")

    documento_socio = normalize_digits(row.get("cpf_cnpj_socio"))
    if documento_socio is not None:
        if len(documento_socio) == 11:
            documento_socio = compose_cpf(documento_socio)
        elif len(documento_socio) == 14:
            documento_socio = compose_cnpj_optional(documento_socio)
        else:
            raise ValueError(f"cpf_cnpj_socio inválido: {row.get('cpf_cnpj_socio')}")

    return SocioNormalized(
        cnpj_basico=cnpj_basico,
        identificador_socio=normalize_digits(row.get("identificador_socio")),
        nome_socio_razao_social=nome_socio_razao_social,
        cpf_cnpj_socio=documento_socio,
        qualificacao_socio=normalize_digits(row.get("qualificacao_socio")),
        data_entrada_sociedade=normalize_date_yyyymmdd(row.get("data_entrada_sociedade")),
        pais=normalize_digits(row.get("pais")),
        representante_legal=normalize_digits(row.get("representante_legal")),
        nome_representante=normalize_text(row.get("nome_representante")),
        qualificacao_representante_legal=normalize_digits(
            row.get("qualificacao_representante_legal")
        ),
        faixa_etaria=normalize_digits(row.get("faixa_etaria")),
    )