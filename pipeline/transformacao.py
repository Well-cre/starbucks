"""SPEC DO pipeline/transformacao.py (CAMADA SILVER TRADUZIDA)

Executável pela linha de comando via:
  uv run python -m pipeline.transformacao

1. ESCOPO E REGRAS DE ISOLAMENTO
   - Ler `bronze.pedidos_starbucks`. Nunca alterar nem escrever no schema
     `bronze`.
   - Criar e popular no schema `silver` as tabelas relacionais:
     `silver.clientes`, `silver.lojas` e `silver.pedidos`.

2. MAPEAMENTO, TRADUÇÃO E TIPAGEM ESTRITA DE COLUNAS
   a) `silver.clientes`
      - customer_id -> cliente_id (VARCHAR - Chave Primária)
      - customer_age_group -> faixa_etaria (VARCHAR)
      - customer_gender -> genero (VARCHAR)
      - is_rewards_member -> membro_fidelidade (BOOLEAN)
      - Deduplicar por `cliente_id` usando MAX(membro_fidelidade),
        MAX(faixa_etaria) e MAX(genero), com uma linha por cliente.
   b) `silver.lojas`
      - store_id -> loja_id (VARCHAR - Chave Primária)
      - store_location_type -> tipo_localizacao (VARCHAR)
      - region -> regiao (VARCHAR)
      - Deduplicar por `loja_id` usando FIRST(tipo_localizacao) e FIRST(regiao),
        com uma linha por loja.
   c) `silver.pedidos`
      - order_id -> pedido_id (VARCHAR - Chave Primária)
      - customer_id -> cliente_id (VARCHAR - FK -> silver.clientes)
      - store_id -> loja_id (VARCHAR - FK -> silver.lojas)
      - order_date -> data_pedido (DATE - strptime/CAST '%Y-%m-%d')
      - order_time -> hora_pedido (TIME - strptime/CAST '%H:%M')
      - day_of_week -> dia_semana (VARCHAR), traduzindo:
        Monday -> Segunda-feira, Tuesday -> Terça-feira,
        Wednesday -> Quarta-feira, Thursday -> Quinta-feira,
        Friday -> Sexta-feira, Saturday -> Sábado, Sunday -> Domingo.
      - order_channel -> canal_pedido (VARCHAR)
      - cart_size -> tamanho_carrinho (INTEGER)
      - num_customizations -> qtd_customizacoes (INTEGER)
      - total_spend -> valor_total (DECIMAL(10,2))
      - fulfillment_time_min -> tempo_atendimento_min (DOUBLE)
      - drink_category -> categoria_bebida (VARCHAR)
      - has_food_item -> possui_alimento (BOOLEAN)
      - order_ahead -> pedido_antecipado (BOOLEAN)
      - customer_satisfaction -> satisfacao_cliente (INTEGER)
      - Manter todos os 100.000 registros de pedidos tipados.

3. CONVERSÃO QUE FALHA (SEM NULOS FABRICADOS)
   - Usar `strptime` e `CAST` nativos do DuckDB. Nunca usar `TRY_CAST` ou
     `try_strptime`.

4. REEXECUÇÃO IDEMPOTENTE
   - Usar `CREATE OR REPLACE TABLE` para todas as tabelas no schema `silver`.

5. SAÍDA NA TELA (STDOUT)
   - Reconfigurar stdout para UTF-8 (`sys.stdout.reconfigure(encoding='utf-8')`).
   - Imprimir a contagem de linhas e nulos de cada tabela em `silver`.
   - Executar e exibir um JOIN entre `silver.pedidos`, `silver.clientes` e
     `silver.lojas`, validando os 100.000 registros.
"""

import sys

from pipeline import db

SCHEMA_DESTINO = "silver"
TABELA_ORIGEM = "bronze.pedidos_starbucks"

COLUNAS_TABELAS = {
    "clientes": (
        "cliente_id",
        "faixa_etaria",
        "genero",
        "membro_fidelidade",
    ),
    "lojas": ("loja_id", "tipo_localizacao", "regiao"),
    "pedidos": (
        "pedido_id",
        "cliente_id",
        "loja_id",
        "data_pedido",
        "hora_pedido",
        "dia_semana",
        "canal_pedido",
        "tamanho_carrinho",
        "qtd_customizacoes",
        "valor_total",
        "tempo_atendimento_min",
        "categoria_bebida",
        "possui_alimento",
        "pedido_antecipado",
        "satisfacao_cliente",
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


def _criar_tabelas(conexao) -> None:
    conexao.execute("BEGIN TRANSACTION")
    try:
        conexao.execute(f"CREATE SCHEMA IF NOT EXISTS {SCHEMA_DESTINO}")
        conexao.execute(f"DROP TABLE IF EXISTS {SCHEMA_DESTINO}.pedidos")

        conexao.execute(
            f"""
            CREATE OR REPLACE TABLE {SCHEMA_DESTINO}.clientes (
                cliente_id VARCHAR PRIMARY KEY,
                faixa_etaria VARCHAR,
                genero VARCHAR,
                membro_fidelidade BOOLEAN
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
                loja_id VARCHAR PRIMARY KEY,
                tipo_localizacao VARCHAR,
                regiao VARCHAR
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
                pedido_id VARCHAR PRIMARY KEY,
                cliente_id VARCHAR REFERENCES
                    {SCHEMA_DESTINO}.clientes(cliente_id),
                loja_id VARCHAR REFERENCES {SCHEMA_DESTINO}.lojas(loja_id),
                data_pedido DATE,
                hora_pedido TIME,
                dia_semana VARCHAR,
                canal_pedido VARCHAR,
                tamanho_carrinho INTEGER,
                qtd_customizacoes INTEGER,
                valor_total DECIMAL(10, 2),
                tempo_atendimento_min DOUBLE,
                categoria_bebida VARCHAR,
                possui_alimento BOOLEAN,
                pedido_antecipado BOOLEAN,
                satisfacao_cliente INTEGER
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
                CASE CAST(day_of_week AS VARCHAR)
                    WHEN 'Monday' THEN 'Segunda-feira'
                    WHEN 'Mon' THEN 'Segunda-feira'
                    WHEN 'Tuesday' THEN 'Terça-feira'
                    WHEN 'Tue' THEN 'Terça-feira'
                    WHEN 'Wednesday' THEN 'Quarta-feira'
                    WHEN 'Wed' THEN 'Quarta-feira'
                    WHEN 'Thursday' THEN 'Quinta-feira'
                    WHEN 'Thu' THEN 'Quinta-feira'
                    WHEN 'Friday' THEN 'Sexta-feira'
                    WHEN 'Fri' THEN 'Sexta-feira'
                    WHEN 'Saturday' THEN 'Sábado'
                    WHEN 'Sat' THEN 'Sábado'
                    WHEN 'Sunday' THEN 'Domingo'
                    WHEN 'Sun' THEN 'Domingo'
                    ELSE CAST(day_of_week AS VARCHAR)
                END,
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
    contagem_nulos = " + ".join(f"COUNT(*) FILTER (WHERE {coluna} IS NULL)" for coluna in colunas)
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
            print("Execute primeiro a ingestão bronze: uv run python -m pipeline.ingestao")
            sys.exit(1)

        _criar_tabelas(conexao)

        for tabela in ("clientes", "lojas", "pedidos"):
            quantidade, nulos = _contagem_e_nulos(conexao, tabela)
            print(f"Tabela {SCHEMA_DESTINO}.{tabela}: {_formatar_quantidade(quantidade)} linhas; {_formatar_quantidade(nulos)} nulos.")

        quantidade_join = int(
            conexao.execute(
                f"""
                SELECT COUNT(*)
                FROM {SCHEMA_DESTINO}.pedidos AS p
                INNER JOIN {SCHEMA_DESTINO}.clientes AS c
                    ON p.cliente_id = c.cliente_id
                INNER JOIN {SCHEMA_DESTINO}.lojas AS l
                    ON p.loja_id = l.loja_id
                """
            ).fetchone()[0]
        )
        if quantidade_join != 100_000:
            raise RuntimeError(
                f"Teste de integridade referencial falhou: o JOIN retornou {_formatar_quantidade(quantidade_join)} registros; esperado 100.000."
            )

        print(f"Teste de JOIN entre silver.pedidos, silver.clientes e silver.lojas: {_formatar_quantidade(quantidade_join)} registros.")
    finally:
        conexao.close()


if __name__ == "__main__":
    main()


"""Premissas adotadas:
- A contagem de nulos exibida corresponde ao total de células nulas somadas em
  todas as colunas da respectiva tabela, e não ao número de linhas que contêm
  ao menos um nulo.
- A coluna `day_of_week` da Bronze contém abreviações inglesas (Mon, Tue, Wed,
  Thu, Fri, Sat, Sun); elas são traduzidas como as formas completas
  especificadas.
- A tabela fato existente é removida dentro da transação antes de recriar as
  dimensões, permitindo recriar as chaves estrangeiras sem alterar `bronze`.
- Dias da semana não listados no mapeamento permanecem com o valor original.
"""
