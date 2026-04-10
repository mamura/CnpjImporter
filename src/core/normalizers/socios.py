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
from src.core.parsers.socios import SocioRow


def normalize_socio_row(row: SocioRow) -> SocioNormalized:
    cnpj_basico = require_digits(
        row.cnpj_basico,
        field_name="cnpj_basico",
        expected_length=8,
    )

    nome_socio_razao_social = normalize_text(row.nome_socio_razao_social)
    if nome_socio_razao_social is None:
        raise ValueError("nome_socio_razao_social é obrigatório")

    documento_socio = normalize_digits(row.cpf_cnpj_socio)
    if documento_socio is not None:
        if len(documento_socio) == 11:
            documento_socio = compose_cpf(documento_socio)
        elif len(documento_socio) == 14:
            documento_socio = compose_cnpj_optional(documento_socio)
        else:
            raise ValueError(f"cpf_cnpj_socio inválido: {row.cpf_cnpj_socio}")

    return SocioNormalized(
        cnpj_basico=cnpj_basico,
        identificador_socio=normalize_digits(row.identificador_socio),
        nome_socio_razao_social=nome_socio_razao_social,
        cpf_cnpj_socio=documento_socio,
        qualificacao_socio=normalize_digits(row.qualificacao_socio),
        data_entrada_sociedade=normalize_date_yyyymmdd(
            row.data_entrada_sociedade
        ),
        pais=normalize_digits(row.pais),
        representante_legal=normalize_digits(row.representante_legal),
        nome_representante=normalize_text(row.nome_representante),
        qualificacao_representante_legal=normalize_digits(
            row.qualificacao_representante_legal
        ),
        faixa_etaria=normalize_digits(row.faixa_etaria),
    )