from pathlib import Path

import duckdb
import pytest

ROOT_DIR = Path(__file__).resolve().parent.parent
DATABASE_PATH = ROOT_DIR / "starbucks.duckdb"


@pytest.fixture(scope="module")
def conn():
    # Conexão em modo leitura com o DuckDB local
    if not DATABASE_PATH.is_file():
        pytest.skip("Banco de dados DuckDB não encontrado.")
    connection = duckdb.connect(str(DATABASE_PATH), read_only=True)
    yield connection
    connection.close()


def test_silver_pedidos_sem_valores_nulos_criticos(conn):
    """Garante que as chaves e valores totais dos pedidos na Silver não são nulos."""
    query = """
        SELECT COUNT(*) as nulos 
        FROM silver.pedidos 
        WHERE pedido_id IS NULL OR valor_total IS NULL OR cliente_id IS NULL
    """
    resultado = conn.execute(query).fetchone()[0]
    assert resultado == 0, "Existem registros com valores nulos críticos na tabela silver.pedidos."


def test_silver_valores_totais_positivos(conn):
    """Valida se todos os pedidos possuem valor total maior que zero."""
    query = """
        SELECT COUNT(*) as invalidos 
        FROM silver.pedidos 
        WHERE valor_total <= 0
    """
    resultado = conn.execute(query).fetchone()[0]
    assert resultado == 0, "Existem pedidos com valor total menor ou igual a zero."
