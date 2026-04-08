from pathlib import Path

from src.core.csv_reader import read_csv_rows


def validate_column_count(
    file_path: Path,
    expected_columns: int,
    encoding: str = "utf-8",
    delimiter: str = ";",
    max_errors: int = 10,
) -> None:
    errors = []

    for line_number, row in enumerate(
        read_csv_rows(file_path, encoding=encoding, delimiter=delimiter),
        start=1,
    ):
        if len(row) != expected_columns:
            errors.append((line_number, len(row)))

        if len(errors) >= max_errors:
            break

    if errors:
        error_messages = "\n".join(
            [f"Linha {line}: {cols} colunas" for line, cols in errors]
        )

        raise ValueError(
            f"Arquivo inválido: {file_path.name}\n"
            f"Esperado: {expected_columns} colunas\n"
            f"Erros encontrados:\n{error_messages}"
        )