from dataclasses import dataclass


@dataclass
class EmpresaRow:
    cnpj_basico: str
    razao_social: str
    natureza_juridica: str
    qualificacao_responsavel: str
    capital_social: str
    porte_empresa: str
    ente_federativo_responsavel: str


def parse_empresa_row(row: list[str]) -> EmpresaRow:
    if len(row) != 7:
        raise ValueError(f"Linha de empresas inválida. Esperado 7 colunas, recebido {len(row)}")

    return EmpresaRow(
        cnpj_basico=row[0],
        razao_social=row[1],
        natureza_juridica=row[2],
        qualificacao_responsavel=row[3],
        capital_social=row[4],
        porte_empresa=row[5],
        ente_federativo_responsavel=row[6],
    )