"""SPEC DO pipeline/ingestao.py (CAMADA BRONZE)

Executável pela linha de comando via:
  uv run python -m pipeline.ingestao

1. ESCOPO E NOMES
   - Schema de destino no DuckDB: `bronze`
   - Tabela de destino: `bronze.pedidos_starbucks`
   - Arquivo fonte: `PASTA_DATA / "starbucks_customer_ordering_patterns.csv"`
     (100.000 registros e 20 colunas).

2. REGRAS E PROIBIÇÕES DA INGESTÃO (REGRAS ESTRITAS)
   - Nenhuma conversão de tipo na leitura: TODAS as 20 colunas devem entrar
     como texto (dtype=str / VARCHAR em todas as colunas).
   - Nenhuma linha descartada, alterada, corrigida ou deduplicada.
   - Nenhum nome de coluna alterado.
   - Nulos permanecem nulos (não transformar em string vazia `""`).
   - Leitura explícita declarando `encoding="utf-8"`.
   - Motivo: A camada Bronze deve ser uma cópia fiel da origem bruta
     (raw data).

3. REEXECUÇÃO IDEMPOTENTE
   - O script deve ser reexecutável. A cada execução, a tabela
     `bronze.pedidos_starbucks` é recriada (gravar usa a infraestrutura de
     db.py), nunca acumulada.

4. VALIDAÇÕES E TRATAMENTO DE ERROS
   - Antes de abrir o banco de dados, o script DEVE verificar se o arquivo CSV
     existe na `PASTA_DATA`.
   - Se o arquivo não existir: imprimir mensagem clara informando a ausência
     e o caminho procurado, e encerrar o script imediatamente com `sys.exit(1)`.
     Não ingira nada nem crie o banco.

5. SAÍDA NA TELA (STDOUT)
   - Reconfigurar o stdout para UTF-8
     (`sys.stdout.reconfigure(encoding='utf-8')`) para evitar erro de
     acentuação no terminal do Windows.
   - Imprimir uma mensagem clara contendo o nome qualificado da tabela
     (`bronze.pedidos_starbucks`) e a contagem de linhas retornada pela função
     `db.gravar()` (100.000 linhas com separador de milhar por ponto).

CRITÉRIOS DE ACEITE:
- Execução via `uv run python -m pipeline.ingestao` grava 100.000 registros no
  schema `bronze`.
- Execuções repetidas mantêm exatamente 100.000 registros.
- `SELECT * FROM bronze.pedidos_starbucks` no DuckDB retorna todas as colunas
  como VARCHAR.
- Caso o arquivo CSV seja renomeado ou removido, o script encerra com erro
  amigável sem criar a tabela.
"""

import sys

import pandas as pd

from pipeline import db

NOME_ARQUIVO = "starbucks_customer_ordering_patterns.csv"
SCHEMA_DESTINO = "bronze"
TABELA_DESTINO = "pedidos_starbucks"


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")

    caminho_csv = db.PASTA_DATA / NOME_ARQUIVO
    if not caminho_csv.is_file():
        print(f"Arquivo CSV não encontrado: {caminho_csv}")
        sys.exit(1)

    dataframe = pd.read_csv(
        caminho_csv,
        encoding="utf-8",
        dtype=str,
        keep_default_na=False,
        na_values=[""],
        skip_blank_lines=False,
    )

    conexao = db.conectar()
    try:
        db.criar_schema(conexao, SCHEMA_DESTINO)
        quantidade = db.gravar(
            conexao,
            dataframe,
            SCHEMA_DESTINO,
            TABELA_DESTINO,
        )
    finally:
        conexao.close()

    quantidade_formatada = f"{quantidade:,}".replace(",", ".")
    print(f"Ingestão concluída: tabela {SCHEMA_DESTINO}.{TABELA_DESTINO} com {quantidade_formatada} linhas.")


if __name__ == "__main__":
    main()


"""Premissas adotadas:
- Campos CSV vazios representam valores nulos; os demais textos são preservados
  sem a interpretação automática de marcadores como "NA" ou "NULL".
"""
