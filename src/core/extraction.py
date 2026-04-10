import re
import shutil
import zipfile
from collections.abc import Callable
from pathlib import Path



class ExtractedBatchPreparationError(Exception):
    pass



def extract_zip(zip_path: Path, target_dir: Path) -> None:
    if not zipfile.is_zipfile(zip_path):
        raise ExtractedBatchPreparationError(f"Arquivo não é um zip válido: {zip_path}")

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
        raise ExtractedBatchPreparationError("Nenhuma pasta de referência (YYYY-MM) encontrada.")

    if len(reference_dirs) > 1:
        raise ExtractedBatchPreparationError("Mais de uma pasta de referência encontrada.")

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


def prepare_extracted_batch(
        input_zip: Path,
        temp_dir: Path,
        extracted_dir: Path,
        on_progress: Callable[[str], None] | None = None,
) -> Path:
    def report(messge:str) -> None:
        if on_progress is not None:
            on_progress(messge)

    unpacked_dir = temp_dir / "input_unpacked"

    if unpacked_dir.exists():
        shutil.rmtree(unpacked_dir)

    unpacked_dir.mkdir(parents=True, exist_ok=True)

    if unpacked_dir.exists():
        report(f"Limpando diretório temporário: {unpacked_dir}")
        shutil.rmtree(unpacked_dir)

    unpacked_dir.mkdir(parents=True, exist_ok=True)

    report(f"Extraindo zip principal: {input_zip.name}")
    extract_zip(input_zip, unpacked_dir)

    report("Localizando pasta de referência...")
    reference_dir = find_reference_directory(unpacked_dir)
    report(f"Pasta de referência encontrada: {reference_dir.name}")

    report("Localizando arquivos zip internos...")
    monthly_zip_files = find_monthly_zip_files(reference_dir)
    report(f"{len(monthly_zip_files)} arquivos zip internos encontrados.")

    final_dir = extracted_dir / reference_dir.name

    if final_dir.exists():
        report(f"Limpando diretório de saída anterior: {final_dir}")
        shutil.rmtree(final_dir)

    final_dir.mkdir(parents=True, exist_ok=True)

    total_files = len(monthly_zip_files)

    for index, monthly_zip in enumerate(monthly_zip_files, start=1):
        report(f"Extraindo arquivo interno {index}/{total_files}: {monthly_zip.name}")
        extract_zip(monthly_zip, final_dir)

    return final_dir