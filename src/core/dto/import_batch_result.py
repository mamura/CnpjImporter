from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path


@dataclass(slots=True)
class ImportBatchResult:
    reference: str
    input_zip: Path
    extracted_dir: Path

    started_at: datetime
    finished_at: datetime

    empresas_imported: int = 0
    estabelecimentos_imported: int = 0
    socios_imported: int = 0
    simples_imported: int = 0

    warnings: list[str] = field(default_factory=list)

    @property
    def total_imported(self) -> int:
        return (
            self.empresas_imported
            + self.estabelecimentos_imported
            + self.socios_imported
            + self.simples_imported
        )