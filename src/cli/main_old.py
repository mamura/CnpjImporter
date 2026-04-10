from pathlib import Path

import typer

from src.config.settings import get_settings
from src.core.extracted_batch import summarize_extracted_batch
from src.core.extraction import prepare_extracted_batch
from src.core.input_batch import summarize_input_batch
from src.core.file_inspector import inspect_text_file
from src.core.csv_reader import read_csv_rows
from src.core.validators import validate_column_count
from src.core.csv_reader import read_csv_rows
from src.core.parsers.empresas import parse_empresa_row
from src.core.validators import validate_column_count
from src.core.parsers.estabelecimentos import parse_estabelecimento_row
from src.core.csv_reader import read_csv_rows
from src.core.parsers.socios import parse_socio_row
from src.core.parsers.simples import parse_simples_row

app = typer.Typer(help="Ferramenta local de importação de dados de CNPJ.")


@app.command()
def info() -> None:
    settings = get_settings()

    typer.echo(f"app: {settings.app_name}")
    typer.echo(f"env: {settings.app_env}")
    typer.echo(f"input_dir: {settings.input_dir}")
    typer.echo(f"extracted_dir: {settings.extracted_dir}")
    typer.echo(f"temp_dir: {settings.temp_dir}")
    typer.echo(f"log_dir: {settings.log_dir}")


@app.command()
def check_dirs() -> None:
    settings = get_settings()

    directories = [
        settings.input_dir,
        settings.extracted_dir,
        settings.temp_dir,
        settings.log_dir,
    ]

    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        typer.echo(f"ok: {directory}")


@app.command("validate-input")
def validate_input() -> None:
    settings = get_settings()
    summary = summarize_input_batch(settings.input_dir)

    typer.echo(f"Pasta analisada: {summary.input_dir}")
    typer.echo(f"Arquivos zip encontrados: {summary.total_zip_files}")
    typer.echo(f"Outros arquivos encontrados: {len(summary.other_files)}")
    typer.echo("")

    if summary.has_single_zip_file:
        typer.secho(
            "Lote de entrada válido para iniciar o processamento.",
            fg=typer.colors.GREEN,
        )
        typer.echo(f"Arquivo selecionado: {summary.selected_zip_file.name}")
        return

    if summary.total_zip_files == 0:
        typer.secho(
            "Nenhum arquivo zip encontrado na pasta de entrada.",
            fg=typer.colors.RED,
        )
        raise typer.Exit(code=1)

    typer.secho(
        "Mais de um arquivo zip encontrado na pasta de entrada.",
        fg=typer.colors.RED,
    )

    for zip_file in summary.zip_files:
        typer.echo(f"- {zip_file.name}")

    raise typer.Exit(code=1)


@app.command("prepare-input")
def prepare_input() -> None:
    settings = get_settings()
    summary = summarize_input_batch(settings.input_dir)

    if not summary.has_single_zip_file:
        typer.secho(
            "Entrada inválida. Deve existir exatamente 1 arquivo zip em data/input.",
            fg=typer.colors.RED,
        )
        raise typer.Exit(code=1)

    input_zip = summary.selected_zip_file
    if input_zip is None:
        typer.secho("Não foi possível determinar o arquivo zip de entrada.", fg=typer.colors.RED)
        raise typer.Exit(code=1)

    typer.echo(f"Arquivo de entrada: {input_zip}")

    final_dir = prepare_extracted_batch(
        input_zip=input_zip,
        temp_dir=settings.temp_dir,
        extracted_dir=settings.extracted_dir,
    )

    typer.secho("Extração concluída com sucesso.", fg=typer.colors.GREEN)
    typer.echo(f"Lote extraído em: {final_dir}")


@app.command("validate-extracted")
def validate_extracted(
    reference: str | None = typer.Option(
        default=None,
        help="Mês de referência a validar, por exemplo: 2026-03",
    ),
) -> None:
    settings = get_settings()

    if reference:
        extracted_dir = settings.extracted_dir / reference
    else:
        extracted_dir = settings.extracted_dir

    summary = summarize_extracted_batch(extracted_dir)

    typer.echo(f"Pasta analisada: {summary.extracted_dir}")
    typer.echo(f"Total de arquivos: {summary.total_files}")
    typer.echo("")
    typer.echo(f"Empresas: {len(summary.empresas)}")
    typer.echo(f"Estabelecimentos: {len(summary.estabelecimentos)}")
    typer.echo(f"Socios: {len(summary.socios)}")
    typer.echo(f"Simples: {len(summary.simples)}")
    typer.echo(f"Cnaes: {len(summary.cnaes)}")
    typer.echo(f"Municipios: {len(summary.municipios)}")
    typer.echo(f"Paises: {len(summary.paises)}")
    typer.echo(f"Naturezas: {len(summary.naturezas)}")
    typer.echo(f"Qualificacoes: {len(summary.qualificacoes)}")
    typer.echo(f"Motivos: {len(summary.motivos)}")
    typer.echo(f"Outros: {len(summary.others)}")
    typer.echo("")

    if summary.has_minimum_required_files:
        typer.secho("Lote extraído válido para processamento.", fg=typer.colors.GREEN)
        return

    typer.secho("Lote extraído inválido.", fg=typer.colors.RED)

    for group in summary.missing_required_groups:
        typer.echo(f"- Grupo obrigatório ausente: {group}")

    raise typer.Exit(code=1)


@app.command("list-extracted")
def list_extracted(
    reference: str = typer.Option(
        ...,
        help="Mês de referência, por exemplo: 2026-03",
    ),
) -> None:
    settings = get_settings()
    extracted_dir = settings.extracted_dir / reference

    if not extracted_dir.exists():
        typer.secho(f"Pasta não encontrada: {extracted_dir}", fg=typer.colors.RED)
        raise typer.Exit(code=1)

    files = sorted([file for file in extracted_dir.iterdir() if file.is_file()])

    typer.echo(f"Pasta analisada: {extracted_dir}")
    typer.echo(f"Total de arquivos: {len(files)}")
    typer.echo("")

    for file in files:
        typer.echo(file.name)


@app.command("inspect-file")
def inspect_file(
    reference: str = typer.Option(
        ...,
        help="Mês de referência, por exemplo: 2026-03",
    ),
    filename: str = typer.Option(
        ...,
        help="Nome do arquivo a inspecionar dentro de data/extracted/<reference>",
    ),
) -> None:
    settings = get_settings()
    file_path = settings.extracted_dir / reference / filename

    result = inspect_text_file(file_path)

    typer.echo(f"Arquivo: {result.file_path}")
    typer.echo(f"Tamanho (bytes): {result.size_bytes}")
    typer.echo(f"Encoding detectado: {result.detected_encoding}")
    typer.echo(f"Separador detectado: {result.detected_separator}")
    typer.echo("")
    typer.echo("Amostra de linhas:")
    typer.echo("")

    for index, line in enumerate(result.sample_lines, start=1):
        typer.echo(f"{index:02d}: {line}")


@app.command("inspect-parsed")
def inspect_parsed(
    reference: str = typer.Option(
        ...,
        help="Mês de referência, por exemplo: 2026-03",
    ),
    filename: str = typer.Option(
        ...,
        help="Nome do arquivo a inspecionar dentro de data/extracted/<reference>",
    ),
    limit: int = typer.Option(
        5,
        help="Quantidade de linhas a exibir",
    ),
) -> None:
    settings = get_settings()
    file_path = settings.extracted_dir / reference / filename

    typer.echo(f"Arquivo: {file_path}")
    typer.echo("")

    for index, row in enumerate(read_csv_rows(file_path), start=1):
        typer.echo(f"Linha {index}: {row}")
        typer.echo(f"Colunas: {len(row)}")
        typer.echo("")

        if index >= limit:
            break


@app.command("validate-empresas")
def validate_empresas(
    reference: str = typer.Option(...),
) -> None:
    settings = get_settings()
    extracted_dir = settings.extracted_dir / reference

    files = sorted(
        [
            f
            for f in extracted_dir.iterdir()
            if f.is_file() and f.name.upper().endswith("EMPRECSV")
        ]
    )

    if not files:
        typer.secho("Nenhum arquivo EMPRECSV encontrado.", fg=typer.colors.RED)
        raise typer.Exit(code=1)

    typer.echo(f"Arquivos encontrados: {len(files)}")
    typer.echo("")

    for file in files:
        typer.echo(f"Validando: {file.name}")

        validate_column_count(
            file_path=file,
            expected_columns=7,
        )

        typer.secho("OK", fg=typer.colors.GREEN)

    typer.secho("\nTodos os arquivos de empresas são válidos.", fg=typer.colors.GREEN)


@app.command("inspect-empresas-mapped")
def inspect_empresas_mapped(
    reference: str = typer.Option(..., help="Mês de referência, por exemplo: 2026-03"),
    filename: str = typer.Option(..., help="Arquivo EMPRECSV a inspecionar"),
    limit: int = typer.Option(5, help="Quantidade de linhas a exibir"),
) -> None:
    settings = get_settings()
    file_path = settings.extracted_dir / reference / filename

    typer.echo(f"Arquivo: {file_path}")
    typer.echo("")

    for index, row in enumerate(read_csv_rows(file_path), start=1):
        empresa = parse_empresa_row(row)

        typer.echo(f"Linha {index}:")
        typer.echo(f"  cnpj_basico: {empresa.cnpj_basico}")
        typer.echo(f"  razao_social: {empresa.razao_social}")
        typer.echo(f"  natureza_juridica: {empresa.natureza_juridica}")
        typer.echo(f"  qualificacao_responsavel: {empresa.qualificacao_responsavel}")
        typer.echo(f"  capital_social: {empresa.capital_social}")
        typer.echo(f"  porte_empresa: {empresa.porte_empresa}")
        typer.echo(
            f"  ente_federativo_responsavel: {empresa.ente_federativo_responsavel}"
        )
        typer.echo("")

        if index >= limit:
            break


@app.command("validate-estabelecimentos")
def validate_estabelecimentos(
    reference: str = typer.Option(...),
) -> None:
    settings = get_settings()
    extracted_dir = settings.extracted_dir / reference

    files = sorted(
        [
            f
            for f in extracted_dir.iterdir()
            if f.is_file() and f.name.upper().endswith("ESTABELE")
        ]
    )

    if not files:
        typer.secho("Nenhum arquivo ESTABELE encontrado.", fg=typer.colors.RED)
        raise typer.Exit(code=1)

    typer.echo(f"Arquivos encontrados: {len(files)}")
    typer.echo("")

    for file in files:
        typer.echo(f"Validando: {file.name}")

        validate_column_count(
            file_path=file,
            expected_columns=30,
        )

        typer.secho("OK", fg=typer.colors.GREEN)

    typer.secho(
        "\nTodos os arquivos de estabelecimentos são válidos.",
        fg=typer.colors.GREEN,
    )


@app.command("inspect-estabelecimentos-mapped")
def inspect_estabelecimentos_mapped(
    reference: str = typer.Option(..., help="Mês de referência, por exemplo: 2026-03"),
    filename: str = typer.Option(..., help="Arquivo ESTABELE a inspecionar"),
    limit: int = typer.Option(5, help="Quantidade de linhas a exibir"),
) -> None:
    settings = get_settings()
    file_path = settings.extracted_dir / reference / filename

    typer.echo(f"Arquivo: {file_path}")
    typer.echo("")

    for index, row in enumerate(read_csv_rows(file_path), start=1):
        estabelecimento = parse_estabelecimento_row(row)

        typer.echo(f"Linha {index}:")
        typer.echo(f"  cnpj_basico: {estabelecimento.cnpj_basico}")
        typer.echo(f"  cnpj_ordem: {estabelecimento.cnpj_ordem}")
        typer.echo(f"  cnpj_dv: {estabelecimento.cnpj_dv}")
        typer.echo(f"  cnpj_completo: {estabelecimento.cnpj_completo}")
        typer.echo(
            f"  identificador_matriz_filial: {estabelecimento.identificador_matriz_filial}"
        )
        typer.echo(f"  nome_fantasia: {estabelecimento.nome_fantasia}")
        typer.echo(f"  situacao_cadastral: {estabelecimento.situacao_cadastral}")
        typer.echo(
            f"  data_situacao_cadastral: {estabelecimento.data_situacao_cadastral}"
        )
        typer.echo(
            f"  motivo_situacao_cadastral: {estabelecimento.motivo_situacao_cadastral}"
        )
        typer.echo(f"  cnae_fiscal_principal: {estabelecimento.cnae_fiscal_principal}")
        typer.echo(
            f"  cnae_fiscal_secundaria: {estabelecimento.cnae_fiscal_secundaria}"
        )
        typer.echo(f"  logradouro: {estabelecimento.tipo_logradouro} {estabelecimento.logradouro}")
        typer.echo(f"  numero: {estabelecimento.numero}")
        typer.echo(f"  bairro: {estabelecimento.bairro}")
        typer.echo(f"  cep: {estabelecimento.cep}")
        typer.echo(f"  uf: {estabelecimento.uf}")
        typer.echo(f"  municipio: {estabelecimento.municipio}")
        typer.echo(f"  email: {estabelecimento.correio_eletronico}")
        typer.echo("")

        if index >= limit:
            break


@app.command("validate-socios")
def validate_socios(
    reference: str = typer.Option(...),
) -> None:
    settings = get_settings()
    extracted_dir = settings.extracted_dir / reference

    files = sorted(
        [
            f
            for f in extracted_dir.iterdir()
            if f.is_file() and f.name.upper().endswith("SOCIOCSV")
        ]
    )

    if not files:
        typer.secho("Nenhum arquivo SOCIOCSV encontrado.", fg=typer.colors.RED)
        raise typer.Exit(code=1)

    typer.echo(f"Arquivos encontrados: {len(files)}")
    typer.echo("")

    for file in files:
        typer.echo(f"Validando: {file.name}")

        validate_column_count(
            file_path=file,
            expected_columns=11,
        )

        typer.secho("OK", fg=typer.colors.GREEN)

    typer.secho(
        "\nTodos os arquivos de sócios são válidos.",
        fg=typer.colors.GREEN,
    )


@app.command("inspect-socios-mapped")
def inspect_socios_mapped(
    reference: str = typer.Option(..., help="Mês de referência, por exemplo: 2026-03"),
    filename: str = typer.Option(..., help="Arquivo SOCIOCSV a inspecionar"),
    limit: int = typer.Option(5, help="Quantidade de linhas a exibir"),
) -> None:
    settings = get_settings()
    file_path = settings.extracted_dir / reference / filename

    typer.echo(f"Arquivo: {file_path}")
    typer.echo("")

    for index, row in enumerate(read_csv_rows(file_path), start=1):
        socio = parse_socio_row(row)

        typer.echo(f"Linha {index}:")
        typer.echo(f"  cnpj_basico: {socio.cnpj_basico}")
        typer.echo(f"  identificador_socio: {socio.identificador_socio}")
        typer.echo(f"  nome_socio_razao_social: {socio.nome_socio_razao_social}")
        typer.echo(f"  cpf_cnpj_socio: {socio.cpf_cnpj_socio}")
        typer.echo(f"  qualificacao_socio: {socio.qualificacao_socio}")
        typer.echo(f"  data_entrada_sociedade: {socio.data_entrada_sociedade}")
        typer.echo(f"  pais: {socio.pais}")
        typer.echo(f"  representante_legal: {socio.representante_legal}")
        typer.echo(f"  nome_representante: {socio.nome_representante}")
        typer.echo(
            f"  qualificacao_representante_legal: {socio.qualificacao_representante_legal}"
        )
        typer.echo(f"  faixa_etaria: {socio.faixa_etaria}")
        typer.echo("")

        if index >= limit:
            break


@app.command("validate-simples")
def validate_simples(
    reference: str = typer.Option(...),
) -> None:
    settings = get_settings()
    extracted_dir = settings.extracted_dir / reference

    files = sorted(
        [
            f
            for f in extracted_dir.iterdir()
            if f.is_file() and "SIMPLES.CSV" in f.name.upper()
        ]
    )

    if not files:
        typer.secho("Nenhum arquivo SIMPLES encontrado.", fg=typer.colors.RED)
        raise typer.Exit(code=1)

    typer.echo(f"Arquivos encontrados: {len(files)}")
    typer.echo("")

    for file in files:
        typer.echo(f"Validando: {file.name}")

        validate_column_count(
            file_path=file,
            expected_columns=7,
        )

        typer.secho("OK", fg=typer.colors.GREEN)

    typer.secho(
        "\nTodos os arquivos de simples são válidos.",
        fg=typer.colors.GREEN,
    )


@app.command("inspect-simples-mapped")
def inspect_simples_mapped(
    reference: str = typer.Option(..., help="Mês de referência, por exemplo: 2026-03"),
    filename: str = typer.Option(..., help="Arquivo de simples a inspecionar"),
    limit: int = typer.Option(5, help="Quantidade de linhas a exibir"),
) -> None:
    settings = get_settings()
    file_path = settings.extracted_dir / reference / filename

    typer.echo(f"Arquivo: {file_path}")
    typer.echo("")

    for index, row in enumerate(read_csv_rows(file_path), start=1):
        simples = parse_simples_row(row)

        typer.echo(f"Linha {index}:")
        typer.echo(f"  cnpj_basico: {simples.cnpj_basico}")
        typer.echo(f"  opcao_simples: {simples.opcao_simples}")
        typer.echo(f"  data_opcao_simples: {simples.data_opcao_simples}")
        typer.echo(f"  data_exclusao_simples: {simples.data_exclusao_simples}")
        typer.echo(f"  opcao_mei: {simples.opcao_mei}")
        typer.echo(f"  data_opcao_mei: {simples.data_opcao_mei}")
        typer.echo(f"  data_exclusao_mei: {simples.data_exclusao_mei}")
        typer.echo("")

        if index >= limit:
            break


if __name__ == "__main__":
    app()