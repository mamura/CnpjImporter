from __future__ import annotations

from datetime import date
from decimal import Decimal, InvalidOperation
from typing import Optional


def empty_to_none(value: str | None) -> str | None:
    if value is None:
        return None

    value = value.strip()
    return value if value != "" else None


def normalize_text(value: str | None) -> str | None:
    value = empty_to_none(value)
    if value is None:
        return None
    return value.strip()


def normalize_digits(value: str | None) -> str | None:
    value = empty_to_none(value)
    if value is None:
        return None
    return "".join(ch for ch in value if ch.isdigit())


def normalize_decimal_br(value: str | None) -> Decimal | None:
    value = empty_to_none(value)
    if value is None:
        return None

    normalized = value.replace(".", "").replace(",", ".").strip()

    try:
        return Decimal(normalized)
    except InvalidOperation as exc:
        raise ValueError(f"Valor decimal inválido: {value}") from exc


def normalize_date_yyyymmdd(value: str | None) -> date | None:
    value = empty_to_none(value)
    if value is None:
        return None

    digits = normalize_digits(value)
    if digits is None or len(digits) != 8:
        raise ValueError(f"Data inválida no formato YYYYMMDD: {value}")

    year = int(digits[0:4])
    month = int(digits[4:6])
    day = int(digits[6:8])

    return date(year, month, day)


def normalize_int(value: str | None) -> int | None:
    value = empty_to_none(value)
    if value is None:
        return None

    digits = normalize_digits(value)
    if digits is None:
        return None

    return int(digits)


def compose_cnpj(cnpj_basico: str, cnpj_ordem: str, cnpj_dv: str) -> str:
    basico = normalize_digits(cnpj_basico)
    ordem = normalize_digits(cnpj_ordem)
    dv = normalize_digits(cnpj_dv)

    if basico is None or len(basico) != 8:
        raise ValueError(f"CNPJ básico inválido: {cnpj_basico}")

    if ordem is None or len(ordem) != 4:
        raise ValueError(f"Ordem do CNPJ inválida: {cnpj_ordem}")

    if dv is None or len(dv) != 2:
        raise ValueError(f"DV do CNPJ inválido: {cnpj_dv}")

    return f"{basico}{ordem}{dv}"