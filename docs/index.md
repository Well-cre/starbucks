# Visão Geral e Arquitetura do Projeto

Bem-vindo à documentação oficial do pipeline de dados da **Starbucks**. Este projeto foi desenvolvido utilizando os princípios de **Engenharia de Dados moderna**, adotando a **Medallion Architecture** sobre o banco analítico **DuckDB**.

---

## 🏗️ Arquitetura do Pipeline (Medallion)

O pipeline transforma dados brutos de transações em conjuntos de dados analíticos altamente estruturados e prontos para tomada de decisão:

```text
[ CSV Bruto ] ──► [ Bronze (Raw) ] ──► [ Silver (Refined) ] ──► [ Gold (Marts) ] ──► [ Dashboard Streamlit ]
```

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

##📂 Estrutura do Projeto

Abaixo está a organização de diretórios e arquivos do repositório starbucks:

```text
starbucks/
├── .streamlit/             # Configurações do painel Streamlit
├── data/                   # Dados locais e arquivos CSV de origem
│   └── starbucks_customer_ordering_patterns.csv
├── docs/                   # Documentação do projeto gerada com MkDocs
│   ├── camadas.md          # Documentação das camadas de dados
│   ├── checklist.md        # Checklist de validação e entregas
│   ├── comandos.md         # Guia de comandos úteis (uv, pytest, ruff)
│   ├── dashboard.md        # Documentação da interface e métricas do Streamlit
│   ├── index.md            # Página inicial e visão geral do projeto
│   ├── marts.md            # Documentação dos Data Marts e KPIs de negócios
│   ├── testes.md           # Guia e estratégias de testes automatizados
│   ├── assets/             # Recursos visuais e imagens da documentação
│   │   └── images/
│   │       └── starbucks-logo.png  # Logótipo do Starbucks
│   └── stylesheets/        # Folhas de estilo personalizadas
│       └── extra.css       # Ajustes visuais (ex: tamanho do logótipo)
├── pipeline/               # Scripts Python do fluxo de dados e ETL
│   ├── db.py               # Conexão e gerenciamento do banco DuckDB
│   ├── ingestao.py         # Ingestão de dados brutos
│   ├── marts.py            # Construção e carga dos Data Marts
│   └── transformacao.py    # Transformação e modelagem nas camadas
├── site/                   # Arquivos estáticos compilados da documentação
├── sql/                    # Consultas SQL para os KPIs da camada Gold
│   └── marts/
│       └── ...
├── tests/                  # Suite de testes automatizados (pytest)
├── mkdocs.yml              # Configuração e navegação do MkDocs
├── pyproject.toml          # Configuração do projeto, uv e ruff
├── README.md               # Visão geral e introdução rápida ao repositório
├── starbucks.duckdb        # Banco de dados analítico local (DuckDB)
└── ui.py                   # Aplicação principal do dashboard Streamlit
```
