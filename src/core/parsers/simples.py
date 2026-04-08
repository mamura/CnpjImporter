from dataclasses import dataclass


@dataclass
class SimplesRow:
    cnpj_basico: str
    opcao_simples: str
    data_opcao_simples: str
    data_exclusao_simples: str
    opcao_mei: str
    data_opcao_mei: str
    data_exclusao_mei: str


def parse_simples_row(row: list[str]) -> SimplesRow:
    if len(row) != 7:
        raise ValueError(
            f"Linha de simples inválida. Esperado 7 colunas, recebido {len(row)}"
        )

    return SimplesRow(
        cnpj_basico=row[0],
        opcao_simples=row[1],
        data_opcao_simples=row[2],
        data_exclusao_simples=row[3],
        opcao_mei=row[4],
        data_opcao_mei=row[5],
        data_exclusao_mei=row[6],
    )