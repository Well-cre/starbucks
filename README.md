<!-- Logo centralizado do projeto -->
<p align="center">
  <img src="https://upload.wikimedia.org/wikipedia/en/d/d3/Starbucks_Corporation_Logo_2011.svg" alt="Starbucks Logo" width="120" height="120">
</p>

<h1 align="center">☕ Starbucks — Engenharia de Dados e Business Analytics</h1>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.12-006241?style=flat-square&logo=python&logoColor=white" alt="Python 3.12">
  <img src="https://img.shields.io/badge/Gerenciamento-uv-006241?style=flat-square" alt="uv">
  <img src="https://img.shields.io/badge/Banco%20de%20Dados-DuckDB-006241?style=flat-square&logo=duckdb&logoColor=white" alt="DuckDB">
  <img src="https://img.shields.io/badge/Testes-pytest-006241?style=flat-square&logo=pytest&logoColor=white" alt="pytest">
  <img src="https://img.shields.io/badge/Qualidade-Ruff-006241?style=flat-square" alt="Ruff">
  <img src="https://img.shields.io/badge/Arquitetura-Medallion-006241?style=flat-square" alt="Medallion">
</p>

Pipeline de dados ponta a ponta desenvolvido como projeto final da pós-graduação em Engenharia de Dados e IA. O projeto usa Python, DuckDB e a arquitetura Medallion para transformar dados brutos em indicadores de negócio e disponibilizá-los em um dashboard.

## Arquitetura

```text
CSV bruto
   |
   v
Bronze (bronze.pedidos_starbucks)
   |
   v
Silver (silver.pedidos, silver.clientes, silver.lojas)
   |
   v
Gold (marts de negócio)
   |
   v
Dashboard Streamlit
```

| Camada | Responsabilidade |
| --- | --- |
| **Bronze** | Preserva os dados de origem sem alterar nomes de colunas ou valores. |
| **Silver** | Limpa e tipa os dados, remove duplicidades, organiza as entidades relacionais e traduz nomes e categorias para português. |
| **Gold** | Gera tabelas agregadas e indicadores para análise de vendas, produtos, regiões, canais e satisfação. |

## Indicadores disponíveis

Os marts da camada Gold incluem:

- `gold.kpi_vendas`: total de pedidos, faturamento e ticket médio.
- `gold.kpi_categoria_bebida`: indicadores agrupados por categoria de bebida.
- `gold.kpi_regiao`: indicadores por região, relacionando pedidos e lojas.
- `gold.kpi_canal`: indicadores por canal do pedido.
- `gold.kpi_satisfacao`: indicadores por satisfação e tempo de atendimento.

## Tecnologias

- **Python 3.12+** e [`uv`](https://docs.astral.sh/uv/)
- **DuckDB** para armazenamento e consultas analíticas
- **Pandas** para leitura e processamento dos dados
- **pytest** para testes automatizados
- **Ruff** para lint e formatação
- **Streamlit** para o dashboard
- **MkDocs Material** para a documentação

## Como executar

### Instalar as dependências

Com o Python 3.12 ou superior e o `uv` instalados, execute na pasta do projeto:

```bash
uv sync
```

### Executar o pipeline

Rode as etapas na ordem indicada:

```bash
# Ingestão dos dados na camada Bronze
uv run python -m pipeline.ingestao

# Transformação dos dados para a camada Silver
uv run python -m pipeline.transformacao

# Geração dos indicadores na camada Gold
uv run python -m pipeline.marts
```

### Iniciar o dashboard

```bash
uv run streamlit run ui.py
```

### Executar testes e verificações

```bash
# Testes automatizados
uv run pytest

# Verificar o código com Ruff
uv run ruff check .

# Formatar o código com Ruff
uv run ruff format .
```

### Resultado dos testes

Os testes foram executados com `uv run pytest -v`. Na última execução, os 9 testes passaram em 0,44 segundo:

```text
tests/test_marts.py::test_kpi_vendas PASSED
tests/test_marts.py::test_kpi_categoria_bebida PASSED
tests/test_marts.py::test_kpi_regiao_com_join PASSED
tests/test_marts.py::test_kpi_canal PASSED
tests/test_marts.py::test_kpi_satisfacao PASSED
tests/test_pipeline.py::test_camada_bronze PASSED
tests/test_pipeline.py::test_camada_silver_contagens_e_nulos PASSED
tests/test_pipeline.py::test_camada_silver_integridade_referencial PASSED
tests/test_pipeline.py::test_camada_gold_marts PASSED

============================== 9 passed in 0.44s ==============================
```

Os cinco testes de marts validam os indicadores de vendas, categorias, regiões (incluindo o `JOIN`), canais e satisfação em uma conexão DuckDB em memória. Os outros quatro verificam a quantidade de registros da camada Bronze, as tabelas e chaves da Silver, a integridade referencial e os marts da Gold, incluindo o faturamento total.

### Visualizar a documentação

```bash
uv run mkdocs serve
```
👤 Autor & Portfólio
Desenvolvido com foco em engenharia de dados, IA e arquitetura moderna por Wellington P. Marani

LinkedIn (Portfólio Principal):https://www.linkedin.com/in/wellington-marani-634aab24/

GitHub: https://github.com/Well-cre