from __future__ import annotations

from dataclasses import dataclass
from datetime import date


@dataclass(slots=True)
class SocioNormalized:
    cnpj_basico: str
    identificador_socio: str | None
    nome_socio_razao_social: str
    cpf_cnpj_socio: str | None
    qualificacao_socio: str | None
    data_entrada_sociedade: date | None
    pais: str | None
    representante_legal: str | None
    nome_representante: str | None
    qualificacao_representante_legal: str | None
    faixa_etaria: str | None