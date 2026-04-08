from __future__ import annotations

from dataclasses import dataclass
from datetime import date


@dataclass(slots=True)
class SimplesNormalized:
    cnpj_basico: str
    opcao_simples: bool | None
    data_opcao_simples: date | None
    data_exclusao_simples: date | None
    opcao_mei: bool | None
    data_opcao_mei: date | None
    data_exclusao_mei: date | None