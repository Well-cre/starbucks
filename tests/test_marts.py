import duckdb
import pytest

from pipeline.marts import _CRIAR_MARTS


@pytest.fixture
def conexao_memoria():
    """Cria uma conexão isolada em memória no DuckDB com schemas e dados fictícios (mockados)

    nas tabelas da Silver para testes unitários idempotentes.
    """
    conn = duckdb.connect(":memory:")

    # 1. Criação dos schemas necessários
    conn.execute("CREATE SCHEMA silver;")
    conn.execute("CREATE SCHEMA gold;")

    # 2. Criação da tabela silver.pedidos mockada
    conn.execute("""
        CREATE TABLE silver.pedidos (
            pedido_id INT,
            loja_id INT,
            categoria_bebida VARCHAR,
            valor_total DECIMAL(10,2),
            canal_pedido VARCHAR,
            satisfacao_cliente VARCHAR,
            tempo_atendimento_min INT
        );
    """)

    # 3. Inserção de dados mockados para testes
    conn.execute("""
        INSERT INTO silver.pedidos VALUES 
        (1, 101, 'Café', 20.00, 'Presencial', 'Satisfeito', 5),
        (2, 101, 'Café', 30.00, 'Presencial', 'Muito Satisfeito', 7),
        (3, 102, 'Chá', 10.00, 'Drive-Thru', 'Insatisfeito', 3);
    """)

    # 4. Criação e inserção da tabela silver.lojas mockada (usada no JOIN da kpi_regiao)
    conn.execute("""
        CREATE TABLE silver.lojas (
            loja_id INT,
            regiao VARCHAR
        );
    """)
    conn.execute("""
        INSERT INTO silver.lojas VALUES 
        (101, 'Sudeste'),
        (102, 'Sul');
    """)

    yield conn
    conn.close()


def _executar_query_mart(conn: duckdb.DuckDBPyConnection, nome_tabela: str) -> None:
    """Função auxiliar para localizar e executar a query de criação de um mart específico."""
    query = [q for q in _CRIAR_MARTS if f"gold.{nome_tabela}" in q][0]
    conn.execute(query)


def test_kpi_vendas(conexao_memoria):
    """Valida agregação geral de vendas (total_pedidos, faturamento_total, ticket_medio)."""
    _executar_query_mart(conexao_memoria, "kpi_vendas")

    resultado = conexao_memoria.execute(
        "SELECT total_pedidos, faturamento_total, ticket_medio FROM gold.kpi_vendas"
    ).fetchone()

    assert resultado[0] == 3  # 3 pedidos inseridos
    assert float(resultado[1]) == 60.00  # 20 + 30 + 10
    assert float(resultado[2]) == 20.00  # 60 / 3


def test_kpi_categoria_bebida(conexao_memoria):
    """Valida agrupamento por categoria de bebida."""
    _executar_query_mart(conexao_memoria, "kpi_categoria_bebida")

    resultado = conexao_memoria.execute(
        "SELECT categoria_bebida, quantidade_pedidos, faturamento_total FROM gold.kpi_categoria_bebida ORDER BY faturamento_total DESC"
    ).fetchall()

    assert len(resultado) == 2
    # Maior faturamento: Café (50.00)
    assert resultado[0][0] == "Café"
    assert resultado[0][1] == 2
    assert float(resultado[0][2]) == 50.00


def test_kpi_regiao_com_join(conexao_memoria):
    """Valida se o JOIN entre silver.pedidos e silver.lojas agrupa corretamente por região."""
    _executar_query_mart(conexao_memoria, "kpi_regiao")

    resultado = conexao_memoria.execute(
        "SELECT regiao, total_pedidos, faturamento_total FROM gold.kpi_regiao ORDER BY faturamento_total DESC"
    ).fetchall()

    assert len(resultado) == 2
    # Sudeste: 2 pedidos da loja 101 (20 + 30 = 50.00)
    assert resultado[0][0] == "Sudeste"
    assert resultado[0][1] == 2
    assert float(resultado[0][2]) == 50.00

    # Sul: 1 pedido da loja 102 (10.00)
    assert resultado[1][0] == "Sul"
    assert resultado[1][1] == 1
    assert float(resultado[1][2]) == 10.00


def test_kpi_canal(conexao_memoria):
    """Valida agrupamento por canal de pedido."""
    _executar_query_mart(conexao_memoria, "kpi_canal")

    resultado = conexao_memoria.execute(
        "SELECT canal_pedido, total_pedidos FROM gold.kpi_canal WHERE canal_pedido = 'Presencial'"
    ).fetchone()

    assert resultado[1] == 2


def test_kpi_satisfacao(conexao_memoria):
    """Valida métricas de satisfação e cálculo do tempo médio de atendimento."""
    _executar_query_mart(conexao_memoria, "kpi_satisfacao")

    resultado = conexao_memoria.execute(
        "SELECT satisfacao_cliente, quantidade_pedidos, tempo_medio_atendimento FROM gold.kpi_satisfacao WHERE satisfacao_cliente = 'Satisfeito'"
    ).fetchone()

    assert resultado[1] == 1  # 1 pedido
    assert float(resultado[2]) == 5.0  # tempo_atendimento_min = 5
