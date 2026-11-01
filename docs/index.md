# Visão Geral e Arquitetura do Projeto

Bem-vindo à documentação oficial do pipeline de dados da **Starbucks**. Este projeto foi desenvolvido utilizando os princípios de **Engenharia de Dados moderna**, adotando a **Medallion Architecture** sobre o banco analítico **DuckDB**.

---

## 🏗️ Arquitetura do Pipeline (Medallion)

O pipeline transforma dados brutos de transações em conjuntos de dados analíticos altamente estruturados e prontos para tomada de decisão:

```text
[ CSV Bruto ] ──► [ Bronze (Raw) ] ──► [ Silver (Refined) ] ──► [ Gold (Marts) ] ──► [ Dashboard Streamlit ]

Principais Componentes:
Bronze (bronze.pedidos_starbucks): Ingestão integral dos dados sem perda de granularidade.

Silver (silver.clientes, silver.lojas, silver.pedidos): Modelagem dimensional relacional, deduplicação rigorosa, tradução de esquema para o português e tipagem de colunas.

Gold (gold.kpi_*): Tabelas agregadas com KPIs de vendas, canais, regiões e satisfação.

🛠️ Stack Tecnológica
Linguagem: Python 3.12+ (gerenciado via uv)

Engine de Banco de Dados: DuckDB

Formatador / Linter: Ruff

Suíte de Testes: Pytest

Interface Gráfica: Streamlit

Documentação: MkDocs com tema Material