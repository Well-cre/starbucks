"""SPEC DO pipeline/db.py

O módulo deve expor EXATAMENTE os seguintes 4 elementos, com estes nomes exatos:
1. PASTA_DATA (constante): Path apontando para a pasta data/ na raiz do projeto.
2. conectar(): Função que abre e devolve a conexão com o banco starbucks.duckdb.
3. criar_schema(con, nome): Função que executa CREATE SCHEMA IF NOT EXISTS.
4. gravar(con, df, schema, tabela): Função que recria a tabela com as colunas/tipos
   do DataFrame e devolve a contagem de linhas gravadas lida do próprio banco.

REGRAS DE DESIGN (ESTRITAS):
D1. RESOLUÇÃO DE CAMINHOS
    Tanto a PASTA_DATA quanto o arquivo starbucks.duckdb devem ser resolvidos
    dinamicamente a partir da localização física do db.py (pasta raiz = pai de
    pipeline/), e NUNCA a partir do diretório de execução atual (os.getcwd()).
    Motivo: Executar o script de dentro de subpastas não pode criar bancos vazios
    em locais indesejados.

D2. RESPONSABILIDADE ÚNICA (SEM REGRAS DE NEGÓCIO)
    O arquivo db.py NÃO deve ler arquivos CSV, NÃO deve conhecer nomes de tabelas
    de negócio, NÃO deve imprimir mensagens na tela (print) e NÃO deve converter
    tipos de dados.
    Motivo: Isolamento total da infraestrutura em relação às regras de negócio.

D3. COMPORTAMENTO DA FUNÇÃO gravar
    Deverá utilizar CREATE OR REPLACE TABLE schema.tabela gravando o DataFrame
    sem alterar colunas nem tipos (string permanece VARCHAR, nulo permanece NULL).
    Após gravar, DEVE executar SELECT count(*) FROM schema.tabela no banco e
    retornar o valor inteiro da contagem lida da tabela recém-criada.
    Motivo: A contagem retornada deve ser a do dado persistido em disco, não do que
    estava na memória RAM.

D4. GERENCIAMENTO DE CONEXÃO
    A função conectar() devolve a conexão aberta. Quem invoca a função é o
    responsável por fechá-la (con.close()). O db.py NÃO deve armazenar conexões
    em variáveis globais.

CRITÉRIOS DE ACEITE:
- Importar pipeline.db no terminal não deve abrir o banco nem criar nenhum arquivo.
- Invocar conectar() de qualquer diretório cria o starbucks.duckdb exclusivamente
  na raiz do projeto.
- Invocação da função gravar() com um DataFrame de 3 linhas retorna o número
  inteiro 3.
"""

from pathlib import Path as _Path
from uuid import uuid4 as _uuid4

import duckdb as _duckdb

PASTA_DATA = _Path(__file__).resolve().parent.parent / "data"


def conectar():
    """Abre e devolve a conexão com o banco DuckDB na raiz do projeto."""
    caminho_banco = _Path(__file__).resolve().parent.parent / "starbucks.duckdb"
    return _duckdb.connect(str(caminho_banco))


def criar_schema(con, nome):
    """Cria o schema caso ainda não exista."""
    nome_sql = '"' + nome.replace('"', '""') + '"'
    con.execute(f"CREATE SCHEMA IF NOT EXISTS {nome_sql}")


def gravar(con, df, schema, tabela):
    """Recria a tabela com o DataFrame e retorna sua contagem persistida."""
    schema_sql = '"' + schema.replace('"', '""') + '"'
    tabela_sql = '"' + tabela.replace('"', '""') + '"'
    nome_df = f"_dataframe_{_uuid4().hex}"
    nome_df_sql = '"' + nome_df + '"'

    con.register(nome_df, df)
    try:
        con.execute(f"CREATE OR REPLACE TABLE {schema_sql}.{tabela_sql} AS SELECT * FROM {nome_df_sql}")
    finally:
        con.unregister(nome_df)

    contagem = con.execute(f"SELECT count(*) FROM {schema_sql}.{tabela_sql}").fetchone()[0]
    return int(contagem)


"""Premissas adotadas:
- O DataFrame passado a gravar() é compatível com o registro nativo do DuckDB.
- O schema deve existir antes de gravar() ser chamada.
"""
