from dataclasses import dataclass


@dataclass
class SocioRow:
    cnpj_basico: str
    identificador_socio: str
    nome_socio_razao_social: str
    cpf_cnpj_socio: str
    qualificacao_socio: str
    data_entrada_sociedade: str
    pais: str
    representante_legal: str
    nome_representante: str
    qualificacao_representante_legal: str
    faixa_etaria: str


def parse_socio_row(row: list[str]) -> SocioRow:
    if len(row) != 11:
        raise ValueError(
            f"Linha de sócios inválida. Esperado 11 colunas, recebido {len(row)}"
        )

    return SocioRow(
        cnpj_basico=row[0],
        identificador_socio=row[1],
        nome_socio_razao_social=row[2],
        cpf_cnpj_socio=row[3],
        qualificacao_socio=row[4],
        data_entrada_sociedade=row[5],
        pais=row[6],
        representante_legal=row[7],
        nome_representante=row[8],
        qualificacao_representante_legal=row[9],
        faixa_etaria=row[10],
    )