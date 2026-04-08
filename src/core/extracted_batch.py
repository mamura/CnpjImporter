from dataclasses import dataclass
from pathlib import Path


@dataclass
class ExtractedBatchSummary:
    extracted_dir: Path
    total_files: int
    empresas: list[Path]
    estabelecimentos: list[Path]
    socios: list[Path]
    simples: list[Path]
    cnaes: list[Path]
    municipios: list[Path]
    paises: list[Path]
    naturezas: list[Path]
    qualificacoes: list[Path]
    motivos: list[Path]
    others: list[Path]

    @property
    def missing_required_groups(self) -> list[str]:
        missing: list[str] = []

        if not self.empresas:
            missing.append("empresas")
        if not self.estabelecimentos:
            missing.append("estabelecimentos")
        if not self.socios:
            missing.append("socios")
        if not self.simples:
            missing.append("simples")

        return missing

    @property
    def has_minimum_required_files(self) -> bool:
        return len(self.missing_required_groups) == 0


def list_extracted_files(extracted_dir: Path) -> list[Path]:
    if not extracted_dir.exists():
        raise FileNotFoundError(f"Pasta não encontrada: {extracted_dir}")

    if not extracted_dir.is_dir():
        raise NotADirectoryError(f"O caminho não é uma pasta: {extracted_dir}")

    return sorted([file for file in extracted_dir.iterdir() if file.is_file()])


def classify_extracted_file(file_path: Path) -> str:
    name = file_path.name.upper()

    if name.endswith("EMPRECSV"):
        return "empresas"

    if name.endswith("ESTABELE"):
        return "estabelecimentos"

    if name.endswith("SOCIOCSV"):
        return "socios"

    if "SIMPLES.CSV" in name:
        return "simples"

    if name.endswith("CNAECSV"):
        return "cnaes"

    if name.endswith("MUNICCSV"):
        return "municipios"

    if name.endswith("PAISCSV"):
        return "paises"

    if name.endswith("NATJUCSV"):
        return "naturezas"

    if name.endswith("QUALSCSV"):
        return "qualificacoes"

    if name.endswith("MOTICSV"):
        return "motivos"

    return "others"


def summarize_extracted_batch(extracted_dir: Path) -> ExtractedBatchSummary:
    files = list_extracted_files(extracted_dir)

    empresas: list[Path] = []
    estabelecimentos: list[Path] = []
    socios: list[Path] = []
    simples: list[Path] = []
    cnaes: list[Path] = []
    municipios: list[Path] = []
    paises: list[Path] = []
    naturezas: list[Path] = []
    qualificacoes: list[Path] = []
    motivos: list[Path] = []
    others: list[Path] = []

    for file_path in files:
        category = classify_extracted_file(file_path)

        if category == "empresas":
            empresas.append(file_path)
        elif category == "estabelecimentos":
            estabelecimentos.append(file_path)
        elif category == "socios":
            socios.append(file_path)
        elif category == "simples":
            simples.append(file_path)
        elif category == "cnaes":
            cnaes.append(file_path)
        elif category == "municipios":
            municipios.append(file_path)
        elif category == "paises":
            paises.append(file_path)
        elif category == "naturezas":
            naturezas.append(file_path)
        elif category == "qualificacoes":
            qualificacoes.append(file_path)
        elif category == "motivos":
            motivos.append(file_path)
        else:
            others.append(file_path)

    return ExtractedBatchSummary(
        extracted_dir=extracted_dir,
        total_files=len(files),
        empresas=empresas,
        estabelecimentos=estabelecimentos,
        socios=socios,
        simples=simples,
        cnaes=cnaes,
        municipios=municipios,
        paises=paises,
        naturezas=naturezas,
        qualificacoes=qualificacoes,
        motivos=motivos,
        others=others,
    )