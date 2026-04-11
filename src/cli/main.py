from pathlib import Path

import typer
from src.config.settings import get_settings
from src.core.extracted_batch import summarize_extracted_batch, ExtractedBatchSummary, validate_extracted_batch, \
    ExtractedBatchValidationError
from src.core.extraction import prepare_extracted_batch, ExtractedBatchPreparationError
from src.core.input_batch import summarize_input_batch, validate_input_batch, InputBatchSummary
from src.core.persistence import PersistenceSummary, PersistenceError, persist_required_files
from src.core.required_files_validation import validate_required_files_structure, RequiredFilesStructureValidationError
from src.core.normalization import normalize_required_files, NormalizationError, NormalizationSummary

app = typer.Typer(help="Ferramenta local de importação de dados de CNPJ.")

@app.command()
def run() -> None:
    typer.secho("Iniciando o processamento do lote CNPJ...", fg=typer.colors.CYAN)
    typer.secho("[1/7] Garantindo diretórios...", fg=typer.colors.BLUE)
    _ensure_directories()

    typer.secho("[2/7] Validando arquivo de entrada...", fg=typer.colors.BLUE)
    input_summary = _phase_validate_input()

    typer.secho("[3/7] Extraindo lote...", fg=typer.colors.BLUE)
    final_dir = _phase_prepare_input(input_summary)

    typer.secho("[4/7] Validando arquivos extraídos...", fg=typer.colors.BLUE)
    extracted_summary = _phase_validate_extracted(final_dir.name)

    typer.secho("[5/7] Validando estrutura dos arquivos obrigatórios...", fg=typer.colors.BLUE)
    _phase_validate_required_files_structure(extracted_summary)

    typer.secho("[6/7] Normalizando dados...", fg=typer.colors.BLUE)
    normalization_summary = _phase_normalize_required_files(extracted_summary)

    typer.secho("[7/7] Inserindo no banco de dados...", fg=typer.colors.BLUE)
    persistence_summary = _phase_persist_required_files(
        input_summary=input_summary,
        extracted_summary=extracted_summary,
    )




# -----------------
#      Helpers
# -----------------
def _ensure_directories() -> None:
    settings = get_settings()
    directories = [
        settings.input_dir,
        settings.extracted_dir,
        settings.temp_dir,
        settings.log_dir,
    ]

    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)



def _phase_validate_input() -> InputBatchSummary:
    settings    = get_settings()
    summary     = summarize_input_batch(settings.input_dir)

    try:
        validate_input_batch(summary)
    except ValueError as exc:
        typer.secho(str(exc), fg=typer.colors.RED)

        if summary.total_zip_files > 1:
            for zip_file in summary.zip_files:
                typer.secho(f"- {zip_file.name}")

        raise typer.Exit(code=1)

    typer.secho("    - Lote de entrada válido.", fg=typer.colors.GREEN)
    typer.secho(f"    - Arquivo selecionado: {summary.selected_zip_file.name}", fg=typer.colors.GREEN)

    return summary



def _phase_prepare_input(input_summary) -> Path:
    settings = get_settings()

    input_zip = input_summary.selected_zip_file
    if input_zip is None:
        typer.secho(
            "Não foi possível determinar o arquivo zip de entrada.",
            fg=typer.colors.RED,
        )
        raise typer.Exit(code=1)

    try:
        final_dir = prepare_extracted_batch(
            input_zip=input_zip,
            temp_dir=settings.temp_dir,
            extracted_dir=settings.extracted_dir,
            on_progress=lambda message: typer.secho(f"    - {message}", fg=typer.colors.GREEN),
        )
    except ExtractedBatchPreparationError as exc:
        typer.secho(str(exc), fg=typer.colors.RED)
        raise typer.Exit(code=1)

    typer.secho("    - Lote extraído com sucesso.", fg=typer.colors.GREEN)
    typer.secho(f"    - Diretório de saída: {final_dir}", fg=typer.colors.GREEN)

    return final_dir



def _phase_validate_extracted(reference: str | None = None) -> ExtractedBatchSummary:
    settings = get_settings()

    extracted_dir = settings.extracted_dir / reference if reference else settings.extracted_dir
    summary = summarize_extracted_batch(extracted_dir)

    try:
        validate_extracted_batch(summary)
    except ExtractedBatchValidationError as exc:
        typer.secho(str(exc), fg=typer.colors.RED)

        for group in summary.missing_required_groups:
            typer.secho(
                f"    - Grupo obrigatório ausente: {group}",
                fg=typer.colors.RED,
            )

        raise typer.Exit(code=1)

    typer.secho("    - Lote extraído válido.", fg=typer.colors.GREEN)
    typer.secho(f"    - Diretório validado: {summary.extracted_dir}", fg=typer.colors.GREEN)
    typer.secho(f"    - Total de arquivos: {summary.total_files}", fg=typer.colors.GREEN)

    return summary



def _phase_validate_required_files_structure(extracted_summary: ExtractedBatchSummary) -> None:
    try:
        validate_required_files_structure(
            extracted_summary,
            on_progress=lambda message: typer.secho(f"    - {message}", fg=typer.colors.GREEN),
        )
    except RequiredFilesStructureValidationError as exc:
        typer.secho(str(exc), fg=typer.colors.RED)
        raise typer.Exit(code=1)

    typer.secho("    - Estrutura dos arquivos obrigatórios válida.", fg=typer.colors.GREEN)



def _phase_normalize_required_files(extracted_summary: ExtractedBatchSummary) -> NormalizationSummary:
    try:
        summary = normalize_required_files(
            extracted_summary,
            on_progress=lambda message: typer.secho(
                f"    - {message}",
                fg=typer.colors.GREEN,
            ),
        )
    except NormalizationError as exc:
        typer.secho(str(exc), fg=typer.colors.RED)
        raise typer.Exit(code=1)

    typer.secho(
        f"    - Normalização concluída. Total: {summary.total_count:,} linhas.",
        fg=typer.colors.GREEN,
    )

    return summary



def _phase_persist_required_files(
    input_summary: InputBatchSummary,
    extracted_summary: ExtractedBatchSummary,
) -> PersistenceSummary:
    try:
        summary = persist_required_files(
            input_summary=input_summary,
            extracted_summary=extracted_summary,
            on_progress=lambda message: typer.secho(
                f"    - {message}",
                fg=typer.colors.GREEN,
            ),
        )
    except PersistenceError as exc:
        typer.secho(str(exc), fg=typer.colors.RED)
        raise typer.Exit(code=1)

    typer.secho(
        (
            "    - Persistência concluída. "
            f"Empresas: {summary.empresas_count:,}"
        ),
        fg=typer.colors.GREEN,
    )

    return summary




if __name__ == "__main__":
    app()