import re
import shutil
import zipfile
from pathlib import Path


def extract_zip(zip_path: Path, target_dir: Path) -> None:
    if not zipfile.is_zipfile(zip_path):
        raise ValueError(f"Arquivo não é um zip válido: {zip_path}")

    target_dir.mkdir(parents=True, exist_ok=True)

    with zipfile.ZipFile(zip_path, "r") as z:
        z.extractall(target_dir)


def find_reference_directory(base_dir: Path) -> Path:
    # procura pasta no formato YYYY-MM
    for item in base_dir.iterdir():
        if item.is_dir() and re.match(r"\d{4}-\d{2}", item.name):
            return item

    raise FileNotFoundError("Nenhuma pasta de referência (YYYY-MM) encontrada")


def find_inner_zip(reference_dir: Path) -> Path:
    zip_files = [f for f in reference_dir.iterdir() if f.suffix.lower() == ".zip"]

    if len(zip_files) == 0:
        raise FileNotFoundError("Nenhum zip mensal encontrado dentro da pasta de referência")

    if len(zip_files) > 1:
        raise ValueError("Mais de um zip encontrado dentro da pasta de referência")

    return zip_files[0]


def prepare_extraction(input_zip: Path, temp_dir: Path, extracted_dir: Path) -> Path:
    # limpa temp
    if temp_dir.exists():
        shutil.rmtree(temp_dir)

    temp_dir.mkdir(parents=True, exist_ok=True)

    # 1. extrai zip externo
    unpacked_dir = temp_dir / "input_unpacked"
    extract_zip(input_zip, unpacked_dir)

    # 2. encontra pasta de referência (YYYY-MM)
    reference_dir = find_reference_directory(unpacked_dir)

    # 3. encontra zip interno
    inner_zip = find_inner_zip(reference_dir)

    # 4. extrai zip mensal para data/extracted/<mes>
    final_dir = extracted_dir / reference_dir.name

    if final_dir.exists():
        shutil.rmtree(final_dir)

    extract_zip(inner_zip, final_dir)

    return final_dir