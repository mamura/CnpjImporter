from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal


@dataclass(slots=True)
class EmpresaNormalized:
    cnpj_basico: str
    razao_social: str
    natureza_juridica: str
    qualificacao_responsavel: str
    capital_social: Decimal | None
    porte_empresa: str | None
    ente_federativo_responsavel: str | None