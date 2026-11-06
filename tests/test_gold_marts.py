from decimal import Decimal
from pathlib import Path

import duckdb
import pytest

ROOT_DIR = Path(__file__).resolve().parent.parent
DATABASE_PATH = ROOT_DIR / "starbucks.duckdb"


@pytest.fixture(scope="module")
def conn():
    """Fixture para conectar ao DuckDB local em modo leitura."""
    if not DATABASE_PATH.is_file():
        pytest.skip("Banco de dados DuckDB não encontrado.")
    connection = duckdb.connect(str(DATABASE_PATH), read_only=True)
    yield connection
    connection.close()


def test_gold_kpi_vendas_consistencia(conn):
    """Valida se o faturamento total da Gold bate com a soma da Silver."""
    faturamento_silver = conn.execute("SELECT SUM(valor_total) FROM silver.pedidos").fetchone()[0]
    faturamento_gold = conn.execute("SELECT SUM(faturamento_total) FROM gold.kpi_vendas").fetchone()[0]

    assert pytest.approx(faturamento_silver, rel=Decimal("0.01")) == pytest.approx(faturamento_gold, rel=Decimal("0.01"))


def test_gold_kpi_categoria_bebida_nao_vazio(conn):
    """Garante que o mart de categorias de bebidas possui registros válidos."""
    df = conn.execute("SELECT * FROM gold.kpi_categoria_bebida").df()
    assert not df.empty
    assert "categoria_bebida" in df.columns
    assert "faturamento_total" in df.columns
