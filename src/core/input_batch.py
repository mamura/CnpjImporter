from dataclasses import dataclass
from pathlib import Path


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