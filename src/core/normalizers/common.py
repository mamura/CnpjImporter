from __future__ import annotations

from datetime import date
from decimal import Decimal, InvalidOperation


def sanitize_text(value: str | None) -> str | None:
    if value is None:
        return None

    # Remove byte NUL, que o PostgreSQL não aceita em campos text/varchar
    return value.replace("\x00", "")


def empty_to_none(value: str | None) -> str | None:
    value = sanitize_text(value)
    if value is None:
        return None

    value = value.strip()
    return value if value != "" else None


def normalize_text(value: str | None) -> str | None:
    value = empty_to_none(value)
    if value is None:
        return None

    return value


def normalize_text_upper(value: str | None) -> str | None:
    value = normalize_text(value)
    if value is None:
        return None

    return value.upper()


def normalize_text_with_max_length(
    value: str | None,
    *,
    max_length: int,
) -> str | None:
    value = normalize_text(value)
    if value is None:
        return None

    if len(value) > max_length:
        return None

    return value


def normalize_digits(value: str | None) -> str | None:
    value = empty_to_none(value)
    if value is None:
        return None

    digits = "".join(ch for ch in value if ch.isdigit())
    return digits or None


def normalize_digits_with_max_length(
    value: str | None,
    *,
    max_length: int,
) -> str | None:
    digits = normalize_digits(value)
    if digits is None:
        return None

    if len(digits) > max_length:
        return None

    return digits


def require_digits(
    value: str | None,
    *,
    field_name: str,
    expected_length: int | None = None,
) -> str:
    digits = normalize_digits(value)

    if digits is None:
        raise ValueError(f"{field_name} é obrigatório")

    if expected_length is not None and len(digits) != expected_length:
        raise ValueError(
            f"{field_name} deve conter {expected_length} dígitos: {value}"
        )

    return digits


def normalize_int(value: str | None) -> int | None:
    digits = normalize_digits(value)
    if digits is None:
        return None

    return int(digits)


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
    digits = normalize_digits(value)

    if digits is None or digits == "0":
        return None

    if len(digits) != 8:
        raise ValueError(f"Data inválida no formato YYYYMMDD: {value}")

    year = int(digits[0:4])
    month = int(digits[4:6])
    day = int(digits[6:8])

    try:
        return date(year, month, day)
    except ValueError as exc:
        raise ValueError(f"Data inválida no formato YYYYMMDD: {value}") from exc


def normalize_flag(value: str | None) -> bool | None:
    value = empty_to_none(value)
    if value is None:
        return None

    normalized = value.strip().upper()

    truthy = {"S", "SIM", "1", "Y", "YES", "T", "TRUE"}
    falsy = {"N", "NAO", "NÃO", "0", "F", "FALSE", "NO"}

    if normalized in truthy:
        return True

    if normalized in falsy:
        return False

    raise ValueError(f"Flag inválida: {value}")


def normalize_uf(value: str | None) -> str | None:
    value = normalize_text_upper(value)
    if value is None:
        return None

    if len(value) != 2:
        return None

    return value


def compose_cnpj(cnpj_basico: str, cnpj_ordem: str, cnpj_dv: str) -> str:
    basico = require_digits(
        cnpj_basico,
        field_name="cnpj_basico",
        expected_length=8,
    )
    ordem = require_digits(
        cnpj_ordem,
        field_name="cnpj_ordem",
        expected_length=4,
    )
    dv = require_digits(
        cnpj_dv,
        field_name="cnpj_dv",
        expected_length=2,
    )

    return f"{basico}{ordem}{dv}"


def compose_cpf(cpf: str | None) -> str | None:
    digits = normalize_digits(cpf)
    if digits is None:
        return None

    if set(digits) == {"0"}:
        return None

    if len(digits) != 11:
        raise ValueError(f"CPF inválido: {cpf}")

    return digits


def compose_cnpj_optional(cnpj: str | None) -> str | None:
    digits = normalize_digits(cnpj)
    if digits is None:
        return None

    if set(digits) == {"0"}:
        return None

    if len(digits) != 14:
        raise ValueError(f"CNPJ inválido: {cnpj}")

    return digits