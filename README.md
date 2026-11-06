
<h1 align="center">☕ Starbucks — Data Pipeline & Business Analytics</h1>
<p align="center">
  <img src="https://img.shields.io/badge/Python-3.12-006241?style=flat-square&logo=python&logoColor=white" alt="Python 3.12">
  <img src="https://img.shields.io/badge/Gerenciamento-uv-006241?style=flat-square" alt="uv">
  <img src="https://img.shields.io/badge/Banco%20de%20Dados-DuckDB-006241?style=flat-square&logo=duckdb&logoColor=white" alt="DuckDB">
  <img src="https://img.shields.io/badge/Testes-14%2F14%20Passed-006241?style=flat-square&logo=pytest&logoColor=white" alt="pytest">
  <img src="https://img.shields.io/badge/Qualidade-Ruff-006241?style=flat-square" alt="Ruff">
  <img src="https://img.shields.io/badge/Interface-Streamlit-006241?style=flat-square&logo=streamlit&logoColor=white" alt="Streamlit">
</p>

# ☕ Starbucks Data Pipeline & Analytics

> Um pipeline de dados de ponta a ponta construído com arquitetura Medallion utilizando Python, DuckDB e Streamlit, processando dados do ecossistema Starbucks.

---

## 📋 Sobre o Projeto
Este projeto implementa um fluxo analítico completo (ELT) baseado no *Starbucks Store & Menu Dataset*, transformando dados brutos em marts de negócios estruturados para suporte à decisão e visualização em painel interativo.

---

> **Visão Geral:** Pipeline de dados ponta a ponta desenvolvido como projeto final da pós-graduação em Engenharia de Dados e IA. O sistema ingere, transforma e modela dados brutos do Starbucks utilizando uma arquitetura Medallion robusta, garantindo alta confiabilidade através de testes automatizados e entregando indicadores analíticos de alto valor.
## 🗂️ Arquitetura e Granularidade (Grão das Tabelas)
O pipeline segue rigorosamente a **Medallion Architecture**, dividida nas seguintes camadas:

1. **Bronze (Raw):** Ingestão fiel dos arquivos brutos originais do Kaggle, mantendo a estrutura original para auditoria.
2. **Silver (Transformed):** Limpeza, tipagem estrita, tratamento de nulos e padronização.
   * **Grão da tabela de Lojas (`silver_stores`):** Uma linha por loja única identificada pelo seu ID/código.
   * **Grão da tabela de Transações/Pedidos (`silver_orders`):** Uma linha por item/transação realizada.
3. **Gold (Marts):** 10 tabelas agregadas prontas para consumo de negócios (KPIs, faturamento por período, ticket médio, etc.).
   * **Grão dos Marts (ex: `01_vendas_mensais`):** Uma linha por mês/ano agregando o faturamento total da operação.

---

## 🤖 Reflexões e Desafios: Onde a IA Errou
Durante o desenvolvimento assistido por IA, alguns desafios técnicos exigiram intervenção humana crítica e correção de rotas:
* **Alucinação em Joins Complexos:** A IA inicialmente sugeriu um cruzamento entre tabelas na camada Gold que duplicava as métricas de faturamento devido a uma cardinalidade 1-N mal tratada. A correção exigiu reescrever a query utilizando agregações prévias (subconsultas) antes do `JOIN`.
* **Tipagem de Datas no DuckDB:** O modelo gerou funções de parsing de data incompatíveis com a tipagem estrita do DuckDB, sendo necessário ajustar manualmente para conversões explícitas (`CAST AS DATE`).

---

## 📂 Estrutura do Repositório
```text
starbucks/
├── data/               # (Ignorado pelo Git) Dados brutos e DuckDB local
├── pipeline/           # Scripts de ingestão, transformação e marts
├── sql/marts/          # Consultas SQL dos 10 marts analíticos
├── test/               # Suíte de testes automatizados (pytest)
├── ui.py               # Interface do Dashboard em Streamlit
├── pyproject.toml      # Gerenciamento de dependências
└── README.md
---

## 🏛️ Arquitetura do Pipeline

O fluxo de dados segue o padrão de maturidade analítica em camadas:

```text
CSV Bruto
   │
   ▼
[ Bronze ] ──> Preservação integral dos dados de origem
   │
   ▼
[ Silver ] ──> Limpeza, tipagem, normalização e relações
   │
   ▼
[  Gold  ] ──> Marts de negócio e agregação de indicadores
   │
   ▼
📊 Dashboard Streamlit
```

| Camada | Responsabilidade |
| --- | --- |
| **Bronze** | Preserva os dados de origem sem alterar nomes de colunas ou valores. |
| **Silver** | Limpa e tipa os dados, remove duplicidades, organiza as entidades relacionais e traduz nomes e categorias para português. |
| **Gold** | Gera tabelas agregadas e indicadores para análise de vendas, produtos, regiões, canais e satisfação. |

## 📊 Indicadores Disponíveis (Marts Gold)

Os marts da camada Gold incluem:

- `gold.kpi_vendas`: total de pedidos, faturamento e ticket médio.
- `gold.kpi_categoria_bebida`: indicadores agrupados por categoria de bebida.
- `gold.kpi_regiao`: indicadores por região, relacionando pedidos e lojas.
- `gold.kpi_canal`: indicadores por canal do pedido.
- `gold.kpi_satisfacao`: indicadores por satisfação e tempo de atendimento.

## 🛠️ Stack Tecnológica

- **Python 3.12+** e [`uv`](https://docs.astral.sh/uv/)
- **DuckDB** para armazenamento e consultas analíticas
- **Pandas** para leitura e processamento dos dados
- **pytest** para testes automatizados
- **Ruff** para lint e formatação
- **Streamlit** para o dashboard
- **MkDocs Material** para a documentação

## 🚀 Como Executar o Projeto

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

Com o `uv` configurado, podes executar a suíte completa de testes automatizados com suporte a relatório de cobertura:

```bash
# Testes automatizados com cobertura
uv run pytest --cov=pipeline -v

# Verificar o código com Ruff
uv run ruff check .

# Formatar o código com Ruff
uv run ruff format .

### Resultado dos Testes

A suíte foi expandida para **14 testes automatizados**, cobrindo validações estritas de dados, integridade referencial e consistência de negócios:

tests/test_gold_marts.py::test_gold_kpi_vendas_consistencia PASSED
tests/test_gold_marts.py::test_gold_kpi_categoria_bebida_nao_vazio PASSED
tests/test_marts.py::test_kpi_vendas PASSED
tests/test_marts.py::test_kpi_categoria_bebida PASSED
tests/test_marts.py::test_kpi_regiao_com_join PASSED
tests/test_marts.py::test_kpi_canal PASSED
tests/test_marts.py::test_kpi_satisfacao PASSED
tests/test_pipeline.py::test_camada_bronze PASSED
tests/test_pipeline.py::test_camada_silver_contagens_e_nulos PASSED
tests/test_pipeline.py::test_camada_silver_integridade_referencial PASSED
tests/test_pipeline.py::test_camada_gold_marts PASSED
tests/test_silver_validations.py::test_silver_pedidos_sem_valores_nulos_criticos PASSED
tests/test_silver_validations.py::test_silver_valores_totais_positivos PASSED
tests/test_utils.py::test_formatar_moeda PASSED

============================== 14 passed in ~2.14s ==============================
```

Os cinco testes de marts validam os indicadores de vendas, categorias, regiões (incluindo o `JOIN`), canais e satisfação em uma conexão DuckDB em memória. Os outros quatro verificam a quantidade de registros da camada Bronze, as tabelas e chaves da Silver, a integridade referencial e os marts da Gold, incluindo o faturamento total.

### 📖 Documentação Local

```bash
uv run mkdocs serve
```
📄 Origem dos Dados e Licença
Dataset: Obtido publicamente através do Kaggle (Starbucks Store & Menu Dataset).

Licença: Este projeto tem fins estritamente educacionais e de portfólio. O uso de logotipos oficiais foi evitado para respeitar diretrizes de propriedade intelectual e marcas registradas.

👤 Autor & Portfólio
Desenvolvido com foco em engenharia de dados, IA e arquitetura moderna por Wellington P. Marani

💼 LinkedIn (Portfólio Principal):https://www.linkedin.com/in/wellington-marani-634aab24/

🐙 GitHub: https://github.com/Well-cre