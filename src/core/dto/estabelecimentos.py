from __future__ import annotations

from dataclasses import dataclass
from datetime import date


@dataclass(slots=True)
class EstabelecimentoNormalized:
    cnpj_basico: str
    cnpj_ordem: str
    cnpj_dv: str
    cnpj: str

    identificador_matriz_filial: str | None
    nome_fantasia: str | None
    situacao_cadastral: str | None
    data_situacao_cadastral: date | None
    motivo_situacao_cadastral: str | None
    nome_cidade_exterior: str | None
    pais: str | None
    data_inicio_atividade: date | None
    cnae_fiscal_principal: str | None
    cnae_fiscal_secundaria: str | None
    tipo_logradouro: str | None
    logradouro: str | None
    numero: str | None
    complemento: str | None
    bairro: str | None
    cep: str | None
    uf: str | None
    municipio: str | None
    ddd_1: str | None
    telefone_1: str | None
    ddd_2: str | None
    telefone_2: str | None
    ddd_fax: str | None
    fax: str | None
    correio_eletronico: str | None
    situacao_especial: str | None
    data_situacao_especial: date | None