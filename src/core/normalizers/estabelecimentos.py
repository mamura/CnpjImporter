from __future__ import annotations

from src.core.dto.estabelecimentos import EstabelecimentoNormalized
from src.core.normalizers.common import (
    compose_cnpj,
    normalize_date_yyyymmdd,
    normalize_digits,
    normalize_text,
)


def normalize_estabelecimento_row(row: dict[str, str]) -> EstabelecimentoNormalized:
    cnpj_basico = normalize_digits(row["cnpj_basico"])
    cnpj_ordem = normalize_digits(row["cnpj_ordem"])
    cnpj_dv = normalize_digits(row["cnpj_dv"])

    if cnpj_basico is None or len(cnpj_basico) != 8:
        raise ValueError("cnpj_basico inválido")

    if cnpj_ordem is None or len(cnpj_ordem) != 4:
        raise ValueError("cnpj_ordem inválido")

    if cnpj_dv is None or len(cnpj_dv) != 2:
        raise ValueError("cnpj_dv inválido")

    return EstabelecimentoNormalized(
        cnpj_basico=cnpj_basico,
        cnpj_ordem=cnpj_ordem,
        cnpj_dv=cnpj_dv,
        cnpj=compose_cnpj(cnpj_basico, cnpj_ordem, cnpj_dv),

        identificador_matriz_filial=normalize_digits(row["identificador_matriz_filial"]),
        nome_fantasia=normalize_text(row["nome_fantasia"]),
        situacao_cadastral=normalize_digits(row["situacao_cadastral"]),
        data_situacao_cadastral=normalize_date_yyyymmdd(row["data_situacao_cadastral"]),
        motivo_situacao_cadastral=normalize_digits(row["motivo_situacao_cadastral"]),
        nome_cidade_exterior=normalize_text(row["nome_cidade_exterior"]),
        pais=normalize_digits(row["pais"]),
        data_inicio_atividade=normalize_date_yyyymmdd(row["data_inicio_atividade"]),
        cnae_fiscal_principal=normalize_digits(row["cnae_fiscal_principal"]),
        cnae_fiscal_secundaria=normalize_text(row["cnae_fiscal_secundaria"]),
        tipo_logradouro=normalize_text(row["tipo_logradouro"]),
        logradouro=normalize_text(row["logradouro"]),
        numero=normalize_text(row["numero"]),
        complemento=normalize_text(row["complemento"]),
        bairro=normalize_text(row["bairro"]),
        cep=normalize_digits(row["cep"]),
        uf=normalize_text(row["uf"]),
        municipio=normalize_digits(row["municipio"]),
        ddd_1=normalize_digits(row["ddd_1"]),
        telefone_1=normalize_digits(row["telefone_1"]),
        ddd_2=normalize_digits(row["ddd_2"]),
        telefone_2=normalize_digits(row["telefone_2"]),
        ddd_fax=normalize_digits(row["ddd_fax"]),
        fax=normalize_digits(row["fax"]),
        correio_eletronico=normalize_text(row["correio_eletronico"]),
        situacao_especial=normalize_text(row["situacao_especial"]),
        data_situacao_especial=normalize_date_yyyymmdd(row["data_situacao_especial"]),
    )