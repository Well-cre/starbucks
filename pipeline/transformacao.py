"""SPEC DO pipeline/transformacao.py (CAMADA SILVER)

Executável pela linha de comando via:
  uv run python -m pipeline.transformacao

1. ESCOPO E NOMES
   - Schema de destino no DuckDB: `silver`
   - O script deve ler a tabela `bronze.pedidos_starbucks` e criar 3 tabelas
     relacionais tipadas, aplicando deduplicação nas dimensões:

   a) `silver.clientes` (Dimensão Cliente)
      - Colunas:
        * customer_id: VARCHAR (Chave Primária)
        * customer_age_group: VARCHAR
        * customer_gender: VARCHAR
        * is_rewards_member: BOOLEAN (convertido de 'True'/'False')
      - Regra: Deduplicar por `customer_id` (retornando aproximadamente
        14.988 clientes únicos).

   b) `silver.lojas` (Dimensão Loja)
      - Colunas:
        * store_id: VARCHAR (Chave Primária)
        * store_location_type: VARCHAR
        * region: VARCHAR
      - Regra: Deduplicar por `store_id` (retornando aproximadamente 500 lojas
        únicas).

   c) `silver.pedidos` (Tabela Fato)
      - Colunas com conversão estrita de tipo:
        * order_id: VARCHAR (Chave Primária)
        * customer_id: VARCHAR (Chave Estrangeira -> silver.clientes)
        * store_id: VARCHAR (Chave Estrangeira -> silver.lojas)
        * order_date: DATE (cast de YYYY-MM-DD)
        * order_time: TIME (cast de HH:MM)
        * day_of_week: VARCHAR
        * order_channel: VARCHAR
        * cart_size: INTEGER
        * num_customizations: INTEGER
        * total_spend: DOUBLE
        * fulfillment_time_min: DOUBLE
        * drink_category: VARCHAR
        * has_food_item: BOOLEAN (convertido de 'True'/'False')
        * order_ahead: BOOLEAN (convertido de 'True'/'False')
        * customer_satisfaction: INTEGER
      - Regra: 100.000 registros vinculados às dimensões de clientes e lojas.

2. REEXECUÇÃO IDEMPOTENTE
   - As tabelas devem ser recriadas (`CREATE OR REPLACE TABLE`) a cada execução
     no schema `silver`.

3. SAÍDA NA TELA (STDOUT)
   - Reconfigurar o stdout para UTF-8 (`sys.stdout.reconfigure(encoding='utf-8')`).
   - Imprimir uma linha para cada tabela criada com a contagem exata de linhas
     gravadas no banco (utilizando separador de milhar por ponto).
   - Executar e imprimir o resultado de um teste de JOIN entre
     `silver.pedidos`, `silver.clientes` e `silver.lojas` validando a
     integridade referencial dos 100.000 registros.

CRITÉRIOS DE ACEITE:
- Execução grava com sucesso `silver.clientes`, `silver.lojas` e
  `silver.pedidos`.
- Consulta com JOIN entre pedidos, clientes e lojas retorna 100.000 registros
  gravados.
- As colunas de datas, números e booleanos estão nos tipos nativos e corretos
  do DuckDB.
"""

import sys

from pipeline import db

SCHEMA_DESTINO = "silver"
TABELA_ORIGEM = "bronze.pedidos_starbucks"


def _criar_tabelas(conexao) -> None:
    conexao.execute(f"CREATE SCHEMA IF NOT EXISTS {SCHEMA_DESTINO}")

    conexao.execute(
        f"""
        CREATE OR REPLACE TABLE {SCHEMA_DESTINO}.clientes AS
        SELECT
            CAST(customer_id AS VARCHAR) AS customer_id,
            CAST(customer_age_group AS VARCHAR) AS customer_age_group,
            CAST(customer_gender AS VARCHAR) AS customer_gender,
            CAST(is_rewards_member AS BOOLEAN) AS is_rewards_member
        FROM {TABELA_ORIGEM}
        QUALIFY ROW_NUMBER() OVER (
            PARTITION BY customer_id
            ORDER BY customer_age_group, customer_gender, is_rewards_member
        ) = 1
        """
    )
    conexao.execute(
        f"""
        CREATE OR REPLACE TABLE {SCHEMA_DESTINO}.lojas AS
        SELECT
            CAST(store_id AS VARCHAR) AS store_id,
            CAST(store_location_type AS VARCHAR) AS store_location_type,
            CAST(region AS VARCHAR) AS region
        FROM {TABELA_ORIGEM}
        QUALIFY ROW_NUMBER() OVER (
            PARTITION BY store_id
            ORDER BY store_location_type, region
        ) = 1
        """
    )
    conexao.execute(
        f"""
        CREATE OR REPLACE TABLE {SCHEMA_DESTINO}.pedidos AS
        SELECT
            CAST(order_id AS VARCHAR) AS order_id,
            CAST(customer_id AS VARCHAR) AS customer_id,
            CAST(store_id AS VARCHAR) AS store_id,
            CAST(order_date AS DATE) AS order_date,
            CAST(order_time AS TIME) AS order_time,
            CAST(day_of_week AS VARCHAR) AS day_of_week,
            CAST(order_channel AS VARCHAR) AS order_channel,
            CAST(cart_size AS INTEGER) AS cart_size,
            CAST(num_customizations AS INTEGER) AS num_customizations,
            CAST(total_spend AS DOUBLE) AS total_spend,
            CAST(fulfillment_time_min AS DOUBLE) AS fulfillment_time_min,
            CAST(drink_category AS VARCHAR) AS drink_category,
            CAST(has_food_item AS BOOLEAN) AS has_food_item,
            CAST(order_ahead AS BOOLEAN) AS order_ahead,
            CAST(customer_satisfaction AS INTEGER) AS customer_satisfaction
        FROM {TABELA_ORIGEM}
        """
    )


def _contar_linhas(conexao, tabela: str) -> int:
    return int(
        conexao.execute(f"SELECT COUNT(*) FROM {SCHEMA_DESTINO}.{tabela}").fetchone()[0]
    )


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")

    conexao = db.conectar()
    try:
        _criar_tabelas(conexao)

        contagens = {
            tabela: _contar_linhas(conexao, tabela)
            for tabela in ("clientes", "lojas", "pedidos")
        }
        for tabela, quantidade in contagens.items():
            quantidade_formatada = f"{quantidade:,}".replace(",", ".")
            print(f"Tabela {SCHEMA_DESTINO}.{tabela}: {quantidade_formatada} linhas.")

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
                f"o JOIN retornou {quantidade_join} registros; esperado 100.000."
            )

        quantidade_join_formatada = f"{quantidade_join:,}".replace(",", ".")
        print(
            "Teste de JOIN entre silver.pedidos, silver.clientes e silver.lojas: "
            f"{quantidade_join_formatada} registros."
        )
    finally:
        conexao.close()


if __name__ == "__main__":
    main()


"""Premissas adotadas:
- Os atributos de clientes e lojas são consistentes para cada identificador.
  Caso haja divergência, é mantida uma combinação determinística pela ordenação
  dos atributos da dimensão.
- Os identificadores de pedido, cliente e loja da Bronze são válidos e únicos
  onde a especificação os define como chaves.
"""
