import csv
from pathlib import Path


def read_csv_rows(
    file_path: Path,
    encoding: str = "utf-8",
    delimiter: str = ";",
):
    if not file_path.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {file_path}")

    with file_path.open("r", encoding=encoding, errors="replace", newline="") as file:
        reader = csv.reader(
            file,
            delimiter=delimiter,
            quotechar='"',
        )

        for row in reader:
            yield row