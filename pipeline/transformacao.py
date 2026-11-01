"""SPEC DO pipeline/transformacao.py (CAMADA SILVER)

Executável pela linha de comando via:
  uv run python -m pipeline.transformacao

1. ESCOPO E REGRAS DE ISOLAMENTO
   - Ler `bronze.pedidos_starbucks` sem alterar nem escrever no schema `bronze`.
   - Criar e popular no schema `silver` as tabelas relacionais `clientes`,
     `lojas` e `pedidos`.

2. MAPEAMENTO E TIPAGEM ESTRITA DE COLUNAS
   a) `silver.clientes`: customer_id VARCHAR (PK), customer_age_group VARCHAR,
      customer_gender VARCHAR e is_rewards_member BOOLEAN. Deduplicar por
      customer_id com MAX(is_rewards_member), MAX(customer_age_group) e
      MAX(customer_gender), garantindo uma linha por cliente.
   b) `silver.lojas`: store_id VARCHAR (PK), store_location_type VARCHAR e
      region VARCHAR. Deduplicar por store_id usando FIRST(store_location_type)
      e FIRST(region), garantindo uma linha por loja.
   c) `silver.pedidos`: order_id VARCHAR (PK), customer_id e store_id VARCHAR,
      order_date DATE, order_time TIME, day_of_week e order_channel VARCHAR,
      cart_size e num_customizations INTEGER, total_spend DECIMAL(10,2),
      fulfillment_time_min DOUBLE, drink_category VARCHAR,
      has_food_item e order_ahead BOOLEAN e customer_satisfaction INTEGER.
      Manter todos os 100.000 pedidos tipados.

3. CONVERSÃO QUE FALHA (SEM NULOS FABRICADOS)
   - Usar strptime e CAST nativos do DuckDB. Nunca usar TRY_CAST ou
     try_strptime.

4. REEXECUÇÃO IDEMPOTENTE
   - Usar CREATE OR REPLACE TABLE para todas as tabelas no schema `silver`.

5. SAÍDA NA TELA (STDOUT)
   - Reconfigurar stdout para UTF-8.
   - Imprimir a contagem de linhas e nulos de cada tabela em `silver`.
   - Executar e exibir um JOIN entre pedidos, clientes e lojas, validando os
     100.000 registros.
"""

import sys

import duckdb

from pipeline import db

SCHEMA_DESTINO = "silver"
TABELA_ORIGEM = "bronze.pedidos_starbucks"

CONVERSOES = {
    "order_date": (
        "CAST(strptime(order_date, '%Y-%m-%d') AS DATE)",
        "CAST(strptime(?, '%Y-%m-%d') AS DATE)",
    ),
    "order_time": (
        "CAST(strptime(order_time, '%H:%M') AS TIME)",
        "CAST(strptime(?, '%H:%M') AS TIME)",
    ),
    "is_rewards_member": (
        "CAST(is_rewards_member AS BOOLEAN)",
        "CAST(? AS BOOLEAN)",
    ),
    "cart_size": ("CAST(cart_size AS INTEGER)", "CAST(? AS INTEGER)"),
    "num_customizations": (
        "CAST(num_customizations AS INTEGER)",
        "CAST(? AS INTEGER)",
    ),
    "total_spend": (
        "CAST(total_spend AS DECIMAL(10, 2))",
        "CAST(? AS DECIMAL(10, 2))",
    ),
    "fulfillment_time_min": (
        "CAST(fulfillment_time_min AS DOUBLE)",
        "CAST(? AS DOUBLE)",
    ),
    "has_food_item": (
        "CAST(has_food_item AS BOOLEAN)",
        "CAST(? AS BOOLEAN)",
    ),
    "order_ahead": ("CAST(order_ahead AS BOOLEAN)", "CAST(? AS BOOLEAN)"),
    "customer_satisfaction": (
        "CAST(customer_satisfaction AS INTEGER)",
        "CAST(? AS INTEGER)",
    ),
}

COLUNAS_TABELAS = {
    "clientes": (
        "customer_id",
        "customer_age_group",
        "customer_gender",
        "is_rewards_member",
    ),
    "lojas": ("store_id", "store_location_type", "region"),
    "pedidos": (
        "order_id",
        "customer_id",
        "store_id",
        "order_date",
        "order_time",
        "day_of_week",
        "order_channel",
        "cart_size",
        "num_customizations",
        "total_spend",
        "fulfillment_time_min",
        "drink_category",
        "has_food_item",
        "order_ahead",
        "customer_satisfaction",
    ),
}


def _tabela_origem_existe(conexao) -> bool:
    return conexao.execute(
        """
            SELECT EXISTS (
                SELECT 1
                FROM information_schema.tables
                WHERE table_schema = 'bronze'
                  AND table_name = 'pedidos_starbucks'
            )
            """
    ).fetchone()[0]


def _validar_conversoes(conexao) -> None:
    for coluna, (expressao, expressao_valor) in CONVERSOES.items():
        try:
            conexao.execute(
                f"""
                SELECT {expressao}
                FROM {TABELA_ORIGEM}
                WHERE {coluna} IS NOT NULL
                """
            ).fetchall()
        except duckdb.Error:
            valores = conexao.execute(
                f"""
                SELECT DISTINCT {coluna}
                FROM {TABELA_ORIGEM}
                WHERE {coluna} IS NOT NULL
                """
            ).fetchall()
            for (valor,) in valores:
                try:
                    conexao.execute(f"SELECT {expressao_valor}", [valor]).fetchone()
                except duckdb.Error:
                    print(
                        f"Falha de conversão em {TABELA_ORIGEM}, "
                        f"coluna {coluna}: valor inválido {valor!r}."
                    )
                    sys.exit(1)
            raise


def _criar_tabelas(conexao) -> None:
    conexao.execute("BEGIN TRANSACTION")
    try:
        conexao.execute(f"CREATE SCHEMA IF NOT EXISTS {SCHEMA_DESTINO}")

        # A tabela fato referencia as dimensões; removê-la dentro da transação
        # permite recriar as dimensões também quando o script já foi executado.
        conexao.execute(f"DROP TABLE IF EXISTS {SCHEMA_DESTINO}.pedidos")

        conexao.execute(
            f"""
            CREATE OR REPLACE TABLE {SCHEMA_DESTINO}.clientes (
                customer_id VARCHAR PRIMARY KEY,
                customer_age_group VARCHAR,
                customer_gender VARCHAR,
                is_rewards_member BOOLEAN
            )
            """
        )
        conexao.execute(
            f"""
            INSERT INTO {SCHEMA_DESTINO}.clientes
            SELECT
                CAST(customer_id AS VARCHAR),
                MAX(CAST(customer_age_group AS VARCHAR)),
                MAX(CAST(customer_gender AS VARCHAR)),
                MAX(CAST(is_rewards_member AS BOOLEAN))
            FROM {TABELA_ORIGEM}
            GROUP BY CAST(customer_id AS VARCHAR)
            """
        )

        conexao.execute(
            f"""
            CREATE OR REPLACE TABLE {SCHEMA_DESTINO}.lojas (
                store_id VARCHAR PRIMARY KEY,
                store_location_type VARCHAR,
                region VARCHAR
            )
            """
        )
        conexao.execute(
            f"""
            INSERT INTO {SCHEMA_DESTINO}.lojas
            SELECT
                CAST(store_id AS VARCHAR),
                FIRST(CAST(store_location_type AS VARCHAR)),
                FIRST(CAST(region AS VARCHAR))
            FROM {TABELA_ORIGEM}
            GROUP BY CAST(store_id AS VARCHAR)
            """
        )

        conexao.execute(
            f"""
            CREATE OR REPLACE TABLE {SCHEMA_DESTINO}.pedidos (
                order_id VARCHAR PRIMARY KEY,
                customer_id VARCHAR REFERENCES {SCHEMA_DESTINO}.clientes(customer_id),
                store_id VARCHAR REFERENCES {SCHEMA_DESTINO}.lojas(store_id),
                order_date DATE,
                order_time TIME,
                day_of_week VARCHAR,
                order_channel VARCHAR,
                cart_size INTEGER,
                num_customizations INTEGER,
                total_spend DECIMAL(10, 2),
                fulfillment_time_min DOUBLE,
                drink_category VARCHAR,
                has_food_item BOOLEAN,
                order_ahead BOOLEAN,
                customer_satisfaction INTEGER
            )
            """
        )
        conexao.execute(
            f"""
            INSERT INTO {SCHEMA_DESTINO}.pedidos
            SELECT
                CAST(order_id AS VARCHAR),
                CAST(customer_id AS VARCHAR),
                CAST(store_id AS VARCHAR),
                CAST(strptime(order_date, '%Y-%m-%d') AS DATE),
                CAST(strptime(order_time, '%H:%M') AS TIME),
                CAST(day_of_week AS VARCHAR),
                CAST(order_channel AS VARCHAR),
                CAST(cart_size AS INTEGER),
                CAST(num_customizations AS INTEGER),
                CAST(total_spend AS DECIMAL(10, 2)),
                CAST(fulfillment_time_min AS DOUBLE),
                CAST(drink_category AS VARCHAR),
                CAST(has_food_item AS BOOLEAN),
                CAST(order_ahead AS BOOLEAN),
                CAST(customer_satisfaction AS INTEGER)
            FROM {TABELA_ORIGEM}
            """
        )
        conexao.execute("COMMIT")
    except BaseException:
        conexao.execute("ROLLBACK")
        raise


def _contagem_e_nulos(conexao, tabela: str) -> tuple[int, int]:
    colunas = COLUNAS_TABELAS[tabela]
    contagem_nulos = " + ".join(
        f"COUNT(*) FILTER (WHERE {coluna} IS NULL)" for coluna in colunas
    )
    quantidade, nulos = conexao.execute(
        f"""
        SELECT COUNT(*), {contagem_nulos}
        FROM {SCHEMA_DESTINO}.{tabela}
        """
    ).fetchone()
    return int(quantidade), int(nulos)


def _formatar_quantidade(quantidade: int) -> str:
    return f"{quantidade:,}".replace(",", ".")


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")

    conexao = db.conectar()
    try:
        if not _tabela_origem_existe(conexao):
            print(
                "Execute primeiro a ingestão bronze: uv run python -m pipeline.ingestao"
            )
            sys.exit(1)

        _validar_conversoes(conexao)
        _criar_tabelas(conexao)

        for tabela in ("clientes", "lojas", "pedidos"):
            quantidade, nulos = _contagem_e_nulos(conexao, tabela)
            print(
                f"Tabela {SCHEMA_DESTINO}.{tabela}: "
                f"{_formatar_quantidade(quantidade)} linhas; "
                f"{_formatar_quantidade(nulos)} nulos mantidos."
            )

        quantidade_join = int(
            conexao.execute(
                f"""
                SELECT COUNT(*)
                FROM {SCHEMA_DESTINO}.pedidos AS p
                INNER JOIN {SCHEMA_DESTINO}.clientes AS c
                    ON p.customer_id = c.customer_id
                INNER JOIN {SCHEMA_DESTINO}.lojas AS l
                    ON p.store_id = l.store_id
                """
            ).fetchone()[0]
        )
        if quantidade_join != 100_000:
            raise RuntimeError(
                "Teste de integridade referencial falhou: "
                f"o JOIN retornou {_formatar_quantidade(quantidade_join)} "
                "registros; esperado 100.000."
            )

        print(
            "Teste de JOIN entre silver.pedidos, silver.clientes e silver.lojas: "
            f"{_formatar_quantidade(quantidade_join)} registros."
        )
    finally:
        conexao.close()


if __name__ == "__main__":
    main()


"""Premissas adotadas:
- A contagem de nulos exibida corresponde ao total de células nulas somadas em
  todas as colunas da respectiva tabela, e não ao número de linhas que contêm
  ao menos um nulo.
"""
