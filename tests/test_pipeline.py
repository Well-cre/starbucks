"""SPEC DO tests/test_pipeline.py

Executável pela linha de comando via:
  uv run pytest

1. ESTRUTURA DOS TESTES (FIXTURES E COBERTURA)
   - Utilizar uma fixture de conexão do pytest para interagir com a base
     `starbucks.duckdb`.

2. CASOS DE TESTE OBRIGATÓRIOS

   a) `test_camada_bronze`
      - Verificar se a tabela `bronze.pedidos_starbucks` existe no DuckDB.
      - Garantir que a contagem total de registros é exatamente igual a
        100.000 linhas.

   b) `test_camada_silver_contagens_e_nulos`
      - Verificar se as tabelas `silver.clientes`, `silver.lojas` e
        `silver.pedidos` existem.
      - Validar a volumetria exata: `clientes` (14.988), `lojas` (500) e
        `pedidos` (100.000).
      - Garantir que não há valores nulos nas chaves primárias (`cliente_id`,
        `loja_id`, `pedido_id`).

   c) `test_camada_silver_integridade_referencial`
      - Executar um `INNER JOIN` entre `silver.pedidos`, `silver.clientes` e
        `silver.lojas`.
      - Confirmar que o total de registros resultantes do JOIN é exatamente
        igual a 100.000 (sem perda de integridade ou chaves órfãs).

   d) `test_camada_gold_marts`
      - Verificar a existência dos 5 marts: `gold.kpi_vendas`,
        `gold.kpi_categoria_bebida`, `gold.kpi_regiao`, `gold.kpi_canal` e
        `gold.kpi_satisfacao`.
      - Garantir que o `faturamento_total` retornado em `gold.kpi_vendas` bate
        com a soma de `valor_total` da tabela `silver.pedidos`
        (R$ 1.486.677,08).
      - Garantir que o total de pedidos em todos os marts agregados seja
        exatamente 100.000.
"""

import sys
from decimal import Decimal
from pathlib import Path

import pytest

raiz_projeto = str(Path(__file__).resolve().parents[1])
if raiz_projeto not in sys.path:
    sys.path.insert(0, raiz_projeto)

from pipeline import db


@pytest.fixture(scope="module")
def conexao():
    """Abre a conexão com o banco do pipeline e fecha-a ao final dos testes."""
    conexao = db.conectar()
    try:
        yield conexao
    finally:
        conexao.close()


def _tabela_existe(conexao, schema, tabela):
    return conexao.execute(
        """
        SELECT EXISTS (
            SELECT 1
            FROM information_schema.tables
            WHERE table_schema = ?
              AND table_name = ?
        )
        """,
        [schema, tabela],
    ).fetchone()[0]


def test_camada_bronze(conexao):
    assert _tabela_existe(conexao, "bronze", "pedidos_starbucks")
    total = conexao.execute("SELECT COUNT(*) FROM bronze.pedidos_starbucks").fetchone()[
        0
    ]
    assert total == 100_000


def test_camada_silver_contagens_e_nulos(conexao):
    tabelas = {
        "clientes": ("cliente_id", 14_988),
        "lojas": ("loja_id", 500),
        "pedidos": ("pedido_id", 100_000),
    }

    for tabela, (chave_primaria, total_esperado) in tabelas.items():
        assert _tabela_existe(conexao, "silver", tabela)

        total, total_nulos = conexao.execute(
            f"""
            SELECT COUNT(*), COUNT(*) FILTER (WHERE {chave_primaria} IS NULL)
            FROM silver.{tabela}
            """
        ).fetchone()
        assert total == total_esperado
        assert total_nulos == 0


def test_camada_silver_integridade_referencial(conexao):
    total = conexao.execute(
        """
        SELECT COUNT(*)
        FROM silver.pedidos AS p
        INNER JOIN silver.clientes AS c
            ON p.cliente_id = c.cliente_id
        INNER JOIN silver.lojas AS l
            ON p.loja_id = l.loja_id
        """
    ).fetchone()[0]
    assert total == 100_000


def test_camada_gold_marts(conexao):
    marts = {
        "kpi_vendas": (
            "SELECT total_pedidos FROM gold.kpi_vendas",
            100_000,
        ),
        "kpi_categoria_bebida": (
            """SELECT SUM(quantidade_pedidos)
               FROM gold.kpi_categoria_bebida""",
            100_000,
        ),
        "kpi_regiao": (
            "SELECT SUM(total_pedidos) FROM gold.kpi_regiao",
            100_000,
        ),
        "kpi_canal": (
            "SELECT SUM(total_pedidos) FROM gold.kpi_canal",
            100_000,
        ),
        "kpi_satisfacao": (
            """SELECT SUM(quantidade_pedidos)
               FROM gold.kpi_satisfacao""",
            100_000,
        ),
    }

    for mart in marts:
        assert _tabela_existe(conexao, "gold", mart)

    faturamento_mart = conexao.execute(
        "SELECT faturamento_total FROM gold.kpi_vendas"
    ).fetchone()[0]
    faturamento_pedidos = conexao.execute(
        "SELECT SUM(valor_total) FROM silver.pedidos"
    ).fetchone()[0]
    assert faturamento_mart == faturamento_pedidos == Decimal("1486677.08")

    for consulta, total_esperado in marts.values():
        total = conexao.execute(consulta).fetchone()[0]
        assert total == total_esperado


"""Premissas adotadas:
- Os nomes de schemas, tabelas e colunas correspondem ao esquema definido pelo
  pipeline.
- O faturamento é armazenado como DECIMAL e comparado sem tolerância de ponto
  flutuante.
- Cada mart agregado possui uma coluna de contagem de pedidos cujo total pode
  ser somado para validar os 100.000 pedidos.
- O caminho da raiz do projeto é incluído no `sys.path` para que `uv run
  pytest` importe `pipeline.db` sem depender de configuração externa.
"""
