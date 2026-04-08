from dataclasses import dataclass
from pathlib import Path


@dataclass
class FileInspectionResult:
    file_path: Path
    size_bytes: int
    detected_encoding: str
    sample_lines: list[str]
    detected_separator: str | None


def read_sample_lines(file_path: Path, encoding: str, limit: int = 5) -> list[str]:
    lines: list[str] = []

    with file_path.open("r", encoding=encoding, errors="replace") as file:
        for _ in range(limit):
            line = file.readline()
            if not line:
                break
            lines.append(line.rstrip("\n").rstrip("\r"))

    return lines


def detect_separator(sample_lines: list[str]) -> str | None:
    candidates = [";", ",", "\t", "|"]

    best_separator: str | None = None
    best_count = 0

    for candidate in candidates:
        total = sum(line.count(candidate) for line in sample_lines)

        if total > best_count:
            best_count = total
            best_separator = candidate

    if best_count == 0:
        return None

    return best_separator


def inspect_text_file(file_path: Path) -> FileInspectionResult:
    if not file_path.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {file_path}")

    if not file_path.is_file():
        raise ValueError(f"O caminho não é um arquivo: {file_path}")

    encodings_to_try = ["utf-8", "latin-1", "cp1252"]
    detected_encoding = "utf-8"
    sample_lines: list[str] = []

    for encoding in encodings_to_try:
        try:
            sample_lines = read_sample_lines(file_path, encoding=encoding)
            detected_encoding = encoding
            break
        except UnicodeDecodeError:
            continue

    detected_separator = detect_separator(sample_lines)

    return FileInspectionResult(
        file_path=file_path,
        size_bytes=file_path.stat().st_size,
        detected_encoding=detected_encoding,
        sample_lines=sample_lines,
        detected_separator=detected_separator,
    )