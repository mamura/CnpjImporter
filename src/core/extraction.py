import re
import shutil
import zipfile
from pathlib import Path


def extract_zip(zip_path: Path, target_dir: Path) -> None:
    if not zipfile.is_zipfile(zip_path):
        raise ValueError(f"Arquivo não é um zip válido: {zip_path}")

    target_dir.mkdir(parents=True, exist_ok=True)

    with zipfile.ZipFile(zip_path, "r") as archive:
        archive.extractall(target_dir)


def find_reference_directory(base_dir: Path) -> Path:
    reference_dirs = [
        item
        for item in base_dir.iterdir()
        if item.is_dir() and re.fullmatch(r"\d{4}-\d{2}", item.name)
    ]

    if not reference_dirs:
        raise FileNotFoundError("Nenhuma pasta de referência (YYYY-MM) encontrada.")

    if len(reference_dirs) > 1:
        raise ValueError("Mais de uma pasta de referência encontrada.")

    return reference_dirs[0]


def find_monthly_zip_files(reference_dir: Path) -> list[Path]:
    zip_files = sorted(
        [item for item in reference_dir.iterdir() if item.is_file() and item.suffix.lower() == ".zip"]
    )

    if not zip_files:
        raise FileNotFoundError(
            "Nenhum arquivo zip encontrado dentro da pasta de referência."
        )

    return zip_files


def prepare_extracted_batch(input_zip: Path, temp_dir: Path, extracted_dir: Path) -> Path:
    unpacked_dir = temp_dir / "input_unpacked"

    if unpacked_dir.exists():
        shutil.rmtree(unpacked_dir)

    unpacked_dir.mkdir(parents=True, exist_ok=True)

    # 1. extrai zip externo
    extract_zip(input_zip, unpacked_dir)

    # 2. encontra pasta do mês
    reference_dir = find_reference_directory(unpacked_dir)

    # 3. encontra todos os zips internos
    monthly_zip_files = find_monthly_zip_files(reference_dir)

    # 4. extrai todos os zips internos para data/extracted/<mes>
    final_dir = extracted_dir / reference_dir.name

    if final_dir.exists():
        shutil.rmtree(final_dir)

    final_dir.mkdir(parents=True, exist_ok=True)

    for monthly_zip in monthly_zip_files:
        extract_zip(monthly_zip, final_dir)

    return final_dir