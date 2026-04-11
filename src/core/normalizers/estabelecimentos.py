from __future__ import annotations

from src.core.dto.estabelecimentos import EstabelecimentoNormalized
from src.core.normalizers.common import (
    compose_cnpj,
    normalize_date_yyyymmdd,
    normalize_digits,
    normalize_text,
    require_digits,
)
from src.core.parsers.estabelecimentos import EstabelecimentoRow


def normalize_estabelecimento_row(
    row: EstabelecimentoRow,
) -> EstabelecimentoNormalized | None:
    cnpj_basico = _normalize_required_digits(
        row.cnpj_basico,
        field_name="cnpj_basico",
        expected_length=8,
    )
    if cnpj_basico is None:
        return None

    cnpj_ordem = _normalize_required_digits(
        row.cnpj_ordem,
        field_name="cnpj_ordem",
        expected_length=4,
    )
    if cnpj_ordem is None:
        return None

    cnpj_dv = _normalize_required_digits(
        row.cnpj_dv,
        field_name="cnpj_dv",
        expected_length=2,
    )
    if cnpj_dv is None:
        return None

    try:
        cnpj = compose_cnpj(cnpj_basico, cnpj_ordem, cnpj_dv)
    except ValueError:
        return None

    try:
        data_situacao_cadastral = normalize_date_yyyymmdd(
            row.data_situacao_cadastral
        )
        data_inicio_atividade = normalize_date_yyyymmdd(
            row.data_inicio_atividade
        )
        data_situacao_especial = normalize_date_yyyymmdd(
            row.data_situacao_especial
        )
    except ValueError:
        return None

    return EstabelecimentoNormalized(
        cnpj_basico=cnpj_basico,
        cnpj_ordem=cnpj_ordem,
        cnpj_dv=cnpj_dv,
        cnpj=cnpj,
        identificador_matriz_filial=normalize_digits(
            row.identificador_matriz_filial
        ),
        nome_fantasia=normalize_text(row.nome_fantasia),
        situacao_cadastral=normalize_digits(row.situacao_cadastral),
        data_situacao_cadastral=data_situacao_cadastral,
        motivo_situacao_cadastral=normalize_digits(
            row.motivo_situacao_cadastral
        ),
        nome_cidade_exterior=normalize_text(row.nome_cidade_exterior),
        pais=normalize_digits(row.pais),
        data_inicio_atividade=data_inicio_atividade,
        cnae_fiscal_principal=normalize_digits(row.cnae_fiscal_principal),
        cnae_fiscal_secundaria=normalize_text(row.cnae_fiscal_secundaria),
        tipo_logradouro=normalize_text(row.tipo_logradouro),
        logradouro=normalize_text(row.logradouro),
        numero=normalize_text(row.numero),
        complemento=normalize_text(row.complemento),
        bairro=normalize_text(row.bairro),
        cep=normalize_digits(row.cep),
        uf=normalize_text(row.uf),
        municipio=normalize_digits(row.municipio),
        ddd_1=normalize_digits(row.ddd_1),
        telefone_1=normalize_digits(row.telefone_1),
        ddd_2=normalize_digits(row.ddd_2),
        telefone_2=normalize_digits(row.telefone_2),
        ddd_fax=normalize_digits(row.ddd_fax),
        fax=normalize_digits(row.fax),
        correio_eletronico=normalize_text(row.correio_eletronico),
        situacao_especial=normalize_text(row.situacao_especial),
        data_situacao_especial=data_situacao_especial,
    )


def _normalize_required_digits(
    value: str | None,
    *,
    field_name: str,
    expected_length: int | None = None,
) -> str | None:
    try:
        return require_digits(
            value,
            field_name=field_name,
            expected_length=expected_length,
        )
    except ValueError:
        return None