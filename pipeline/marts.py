"""SPEC DO pipeline/marts.py (CAMADA GOLD - PORTUGUÊS)

Executável pela linha de comando via:
  uv run python -m pipeline.marts

1. ESCOPO E NOMES
   - Schema de destino no DuckDB: `gold`
   - Ler as tabelas traduzidas `silver.pedidos`, `silver.clientes` e
     `silver.lojas`, criando 5 tabelas/marts de negócio:

   a) `gold.kpi_vendas`
      - total_pedidos (COUNT), faturamento_total (SUM de valor_total),
        ticket_medio (AVG de valor_total).

   b) `gold.kpi_categoria_bebida`
      - Agrupar por `categoria_bebida`: categoria_bebida,
        quantidade_pedidos, faturamento_total, ticket_medio; ordenar por
        faturamento_total DESC.

   c) `gold.kpi_regiao`
      - Agrupar por `regiao` via JOIN com `silver.lojas`: regiao,
        total_pedidos, faturamento_total, ticket_medio; ordenar por
        faturamento_total DESC.

   d) `gold.kpi_canal`
      - Agrupar por `canal_pedido`: canal_pedido, total_pedidos,
        faturamento_total, ticket_medio; ordenar por total_pedidos DESC.

   e) `gold.kpi_satisfacao`
      - Agrupar por `satisfacao_cliente`: satisfacao_cliente,
        quantidade_pedidos, faturamento_total, ticket_medio e
        tempo_medio_atendimento (AVG de tempo_atendimento_min).

2. REEXECUÇÃO IDEMPOTENTE
   - Recriar os marts (`CREATE OR REPLACE TABLE`) a cada execução no schema
     `gold`.

3. SAÍDA NA TELA (STDOUT)
   - Reconfigurar o stdout para UTF-8
     (`sys.stdout.reconfigure(encoding='utf-8')`).
   - Imprimir uma linha para cada mart criado, com a contagem de linhas e
     métricas formatadas com ponto de milhar.
"""

import sys
from decimal import Decimal

from pipeline import db

SCHEMA_DESTINO = "gold"

_CRIAR_MARTS = (
    """
    CREATE OR REPLACE TABLE gold.kpi_vendas AS
    SELECT
        COUNT(*) AS total_pedidos,
        SUM(valor_total) AS faturamento_total,
        AVG(valor_total) AS ticket_medio
    FROM silver.pedidos
    """,
    """
    CREATE OR REPLACE TABLE gold.kpi_categoria_bebida AS
    SELECT
        categoria_bebida,
        COUNT(*) AS quantidade_pedidos,
        SUM(valor_total) AS faturamento_total,
        AVG(valor_total) AS ticket_medio
    FROM silver.pedidos
    GROUP BY categoria_bebida
    ORDER BY faturamento_total DESC
    """,
    """
    CREATE OR REPLACE TABLE gold.kpi_regiao AS
    SELECT
        l.regiao,
        COUNT(*) AS total_pedidos,
        SUM(p.valor_total) AS faturamento_total,
        AVG(p.valor_total) AS ticket_medio
    FROM silver.pedidos AS p
    INNER JOIN silver.lojas AS l
        ON p.loja_id = l.loja_id
    GROUP BY l.regiao
    ORDER BY faturamento_total DESC
    """,
    """
    CREATE OR REPLACE TABLE gold.kpi_canal AS
    SELECT
        canal_pedido,
        COUNT(*) AS total_pedidos,
        SUM(valor_total) AS faturamento_total,
        AVG(valor_total) AS ticket_medio
    FROM silver.pedidos
    GROUP BY canal_pedido
    ORDER BY total_pedidos DESC
    """,
    """
    CREATE OR REPLACE TABLE gold.kpi_satisfacao AS
    SELECT
        satisfacao_cliente,
        COUNT(*) AS quantidade_pedidos,
        SUM(valor_total) AS faturamento_total,
        AVG(valor_total) AS ticket_medio,
        AVG(tempo_atendimento_min) AS tempo_medio_atendimento
    FROM silver.pedidos
    GROUP BY satisfacao_cliente
    """,
)

_RESUMOS = {
    "kpi_vendas": """
        SELECT COUNT(*), SUM(total_pedidos), SUM(faturamento_total),
               AVG(ticket_medio)
        FROM gold.kpi_vendas
    """,
    "kpi_categoria_bebida": """
        SELECT COUNT(*), SUM(quantidade_pedidos), SUM(faturamento_total),
               SUM(faturamento_total) / NULLIF(SUM(quantidade_pedidos), 0)
        FROM gold.kpi_categoria_bebida
    """,
    "kpi_regiao": """
        SELECT COUNT(*), SUM(total_pedidos), SUM(faturamento_total),
               SUM(faturamento_total) / NULLIF(SUM(total_pedidos), 0)
        FROM gold.kpi_regiao
    """,
    "kpi_canal": """
        SELECT COUNT(*), SUM(total_pedidos), SUM(faturamento_total),
               SUM(faturamento_total) / NULLIF(SUM(total_pedidos), 0)
        FROM gold.kpi_canal
    """,
    "kpi_satisfacao": """
        SELECT
            (SELECT COUNT(*) FROM gold.kpi_satisfacao),
            SUM(quantidade_pedidos),
            SUM(faturamento_total),
            SUM(faturamento_total) / NULLIF(SUM(quantidade_pedidos), 0),
            (SELECT AVG(tempo_atendimento_min) FROM silver.pedidos)
        FROM gold.kpi_satisfacao
    """,
}


def _formatar_quantidade(valor: int) -> str:
    return f"{valor:,}".replace(",", ".")


def _formatar_metrica(
    nome: str,
    valor: float | Decimal | None,
) -> str:
    if valor is None:
        return "nulo"
    if nome == "total_pedidos":
        return _formatar_quantidade(int(valor))
    return f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")

    conexao = db.conectar()
    try:
        db.criar_schema(conexao, SCHEMA_DESTINO)
        for comando in _CRIAR_MARTS:
            conexao.execute(comando)

        for tabela, consulta in _RESUMOS.items():
            resumo = conexao.execute(consulta).fetchone()
            quantidade_linhas = int(resumo[0])
            metricas = "; ".join(
                f"{nome}={_formatar_metrica(nome, valor)}"
                for nome, valor in zip(
                    (
                        "total_pedidos",
                        "faturamento_total",
                        "ticket_medio",
                        "tempo_medio_atendimento",
                    ),
                    resumo[1:],
                )
            )
            print(
                f"Mart {SCHEMA_DESTINO}.{tabela}: "
                f"{_formatar_quantidade(quantidade_linhas)} linhas; {metricas}."
            )
    finally:
        conexao.close()


if __name__ == "__main__":
    main()

import sys
from pathlib import Path

from pipeline import db

SCHEMA_DESTINO = "gold"
PASTA_SQL = Path("sql/marts")


def executar_queries_marts(conexao) -> None:
    """Lê todos os arquivos .sql da pasta sql/marts e executa no DuckDB."""
    if not PASTA_SQL.exists():
        raise FileNotFoundError(f"A pasta {PASTA_SQL} não foi encontrada!")

    arquivos_sql = sorted(PASTA_SQL.glob("*.sql"))

    for arquivo in arquivos_sql:
        query = arquivo.read_text(encoding="utf-8")
        conexao.execute(query)
        print(f"Executado com sucesso: {arquivo.name}")


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")

    conexao = db.conectar()
    try:
        # Garante que o schema gold exista
        db.criar_schema(conexao, SCHEMA_DESTINO)

        # Executa cada arquivo .sql contido em sql/marts/
        executar_queries_marts(conexao)

        print(f"\nCamada {SCHEMA_DESTINO} (Marts) processada com sucesso!")
    finally:
        conexao.close()


if __name__ == "__main__":
    main()

"""Premissas adotadas:
- Os marts agrupados exibem no resumo o total de pedidos e faturamento e o
  ticket médio global ponderado pelo número de pedidos, além da contagem de
  grupos gravados.
- O tempo médio de atendimento exibido no resumo de satisfação é calculado
  diretamente sobre `silver.pedidos`, respeitando o comportamento de AVG para
  valores nulos.
- Valores métricos nulos são apresentados como `nulo`; valores decimais usam
  duas casas e vírgula decimal, com ponto como separador de milhar.
"""
