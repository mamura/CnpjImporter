from __future__ import annotations

from collections.abc import Callable

from src.core.extracted_batch import ExtractedBatchSummary
from src.core.validators import validate_column_count


class RequiredFilesStructureValidationError(Exception):
    pass


def validate_required_files_structure(
    summary: ExtractedBatchSummary,
    on_progress: Callable[[str], None] | None = None,
) -> None:
    _validate_group(
        files=summary.empresas,
        expected_columns=7,
        group_name="empresas",
        on_progress=on_progress,
    )

    _validate_group(
        files=summary.estabelecimentos,
        expected_columns=30,
        group_name="estabelecimentos",
        on_progress=on_progress,
    )

    _validate_group(
        files=summary.socios,
        expected_columns=11,
        group_name="socios",
        on_progress=on_progress,
    )

    _validate_group(
        files=summary.simples,
        expected_columns=7,
        group_name="simples",
        on_progress=on_progress,
    )


def _validate_group(
    *,
    files: list,
    expected_columns: int,
    group_name: str,
    on_progress: Callable[[str], None] | None = None,
) -> None:
    for file_path in files:
        try:
            validate_column_count(
                file_path=file_path,
                expected_columns=expected_columns,
            )
        except Exception as exc:
            raise RequiredFilesStructureValidationError(
                f"Estrutura inválida no grupo '{group_name}' "
                f"para o arquivo '{file_path.name}': {exc}"
            ) from exc

        if on_progress:
            on_progress(
                f"{group_name}: {file_path.name} OK ({expected_columns} colunas)"
            )