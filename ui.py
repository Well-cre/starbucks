"""SPEC DO ui.py

Executável via:
  uv run python ui.py

1. FUNCIONALIDADE
   - Abre o banco `starbucks.duckdb` localizado na raiz do projeto.
   - Instala e carrega a extensão `ui` do DuckDB (`INSTALL ui; LOAD ui;`).
   - Executa `CALL start_ui()`, disponibilizando o servidor web em
     http://localhost:4213 e abrindo o navegador.

2. COMPORTAMENTO E CONTROLE DE PROCESSO
   - Mantém o processo rodando e imprime no terminal a URL e a mensagem
     "Pressione Ctrl+C para encerrar".
   - Intercepta `KeyboardInterrupt` (Ctrl+C), fecha a conexão de forma limpa
     e encerra sem exibir tracebacks no console.

3. TRATAMENTO DE ERROS
   - Se o arquivo `starbucks.duckdb` NÃO existir na raiz do projeto, exibe a mensagem "É necessário executar a ingestão antes (uv run python -m pipeline.ingestao)" e encerra com `sys.exit(1)`.
   - NÃO deve utilizar a função `conectar()` do `pipeline/db.py` para evitar
     que um banco vazio seja criado caso o arquivo não exista.

4. INDEPENDÊNCIA DE MÓDULOS
   - `ui.py` não importa `pipeline/ingestao.py` nem `pipeline/transformacao.py`.

5. SAÍDA NA TELA (STDOUT)
   - Reconfigurar o stdout para UTF-8 (`sys.stdout.reconfigure(encoding='utf-8')`).
"""

import sys
import threading
from pathlib import Path

import duckdb


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")

    database_path = Path(__file__).resolve().parent / "starbucks.duckdb"
    if not database_path.is_file():
        print(
            "É necessário executar a ingestão antes "
            "(uv run python -m pipeline.ingestao)"
        )
        sys.exit(1)

    connection: duckdb.DuckDBPyConnection | None = None
    try:
        connection = duckdb.connect(str(database_path))
        connection.execute("INSTALL ui;")
        connection.execute("LOAD ui;")
        connection.execute("CALL start_ui();")

        print("http://localhost:4213")
        print("Pressione Ctrl+C para encerrar")
        threading.Event().wait()
    except KeyboardInterrupt:
        pass
    finally:
        if connection is not None:
            connection.close()


if __name__ == "__main__":
    main()
