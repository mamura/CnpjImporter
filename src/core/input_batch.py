from dataclasses import dataclass
from pathlib import Path
import re


@dataclass
class InputBatchSummary:
    input_dir: Path
    zip_files: list[Path]
    other_files: list[Path]

    @property
    def total_zip_files(self) -> int:
        return len(self.zip_files)

    @property
    def has_single_zip_file(self) -> bool:
        return self.total_zip_files == 1

    @property
    def selected_zip_file(self) -> Path | None:
        if self.has_single_zip_file:
            return self.zip_files[0]
        return None

    @property
    def selected_zip_file_required(self) -> Path:
        file_path = self.selected_zip_file
        if file_path is None:
            raise ValueError("Nenhum arquivo zip único selecionado.")
        return file_path

    @property
    def reference(self) -> str:
        file_name = self.selected_zip_file_required.name

        match = re.search(r"(20\d{2}-\d{2})", file_name)
        if match:
            return match.group(1)

        raise ValueError(
            f"Não foi possível extrair a referência YYYY-MM do arquivo: {file_name}"
        )


def list_input_files(input_dir: Path) -> list[Path]:
    if not input_dir.exists():
        raise FileNotFoundError(f"Pasta não encontrada: {input_dir}")

    if not input_dir.is_dir():
        raise NotADirectoryError(f"O caminho não é uma pasta: {input_dir}")

    return sorted([file for file in input_dir.iterdir() if file.is_file()])


def summarize_input_batch(input_dir: Path) -> InputBatchSummary:
    files = list_input_files(input_dir)

    zip_files: list[Path] = []
    other_files: list[Path] = []

    for file_path in files:
        if file_path.suffix.lower() == ".zip":
            zip_files.append(file_path)
        else:
            other_files.append(file_path)

    return InputBatchSummary(
        input_dir=input_dir,
        zip_files=zip_files,
        other_files=other_files,
    )


def validate_input_batch(summary: InputBatchSummary) -> None:
    total_zip_files = summary.total_zip_files

    if total_zip_files == 0:
        raise ValueError("Nenhum arquivo zip encontrado na pasta de entrada.")

    if total_zip_files > 1:
        raise ValueError("Mais de um arquivo zip encontrado na pasta de entrada.")