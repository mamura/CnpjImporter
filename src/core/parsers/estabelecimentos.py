from dataclasses import dataclass


@dataclass
class EstabelecimentoRow:
    cnpj_basico: str
    cnpj_ordem: str
    cnpj_dv: str
    identificador_matriz_filial: str
    nome_fantasia: str
    situacao_cadastral: str
    data_situacao_cadastral: str
    motivo_situacao_cadastral: str
    nome_cidade_exterior: str
    pais: str
    data_inicio_atividade: str
    cnae_fiscal_principal: str
    cnae_fiscal_secundaria: str
    tipo_logradouro: str
    logradouro: str
    numero: str
    complemento: str
    bairro: str
    cep: str
    uf: str
    municipio: str
    ddd_1: str
    telefone_1: str
    ddd_2: str
    telefone_2: str
    ddd_fax: str
    fax: str
    correio_eletronico: str
    situacao_especial: str
    data_situacao_especial: str

    @property
    def cnpj_completo(self) -> str:
        return f"{self.cnpj_basico}{self.cnpj_ordem}{self.cnpj_dv}"


def parse_estabelecimento_row(row: list[str]) -> EstabelecimentoRow:
    if len(row) != 30:
        raise ValueError(
            f"Linha de estabelecimentos inválida. Esperado 30 colunas, recebido {len(row)}"
        )

    return EstabelecimentoRow(
        cnpj_basico=row[0],
        cnpj_ordem=row[1],
        cnpj_dv=row[2],
        identificador_matriz_filial=row[3],
        nome_fantasia=row[4],
        situacao_cadastral=row[5],
        data_situacao_cadastral=row[6],
        motivo_situacao_cadastral=row[7],
        nome_cidade_exterior=row[8],
        pais=row[9],
        data_inicio_atividade=row[10],
        cnae_fiscal_principal=row[11],
        cnae_fiscal_secundaria=row[12],
        tipo_logradouro=row[13],
        logradouro=row[14],
        numero=row[15],
        complemento=row[16],
        bairro=row[17],
        cep=row[18],
        uf=row[19],
        municipio=row[20],
        ddd_1=row[21],
        telefone_1=row[22],
        ddd_2=row[23],
        telefone_2=row[24],
        ddd_fax=row[25],
        fax=row[26],
        correio_eletronico=row[27],
        situacao_especial=row[28],
        data_situacao_especial=row[29],
    )