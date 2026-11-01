### 2. `docs/camadas.md`

```markdown
# Detalhamento das Camadas do Pipeline

---

## 🤎 1. Camada Bronze (`pipeline/ingestao.py`)

A Camada Bronze é responsável pela ingestão *raw* (bruta) do arquivo CSV original.

* **Schema**: `bronze`
* **Tabela**: `pedidos_starbucks`
* **Volumetria**: 100.000 registros
* **Regra de Ingestão**: Reexecução idempotente utilizando `CREATE OR REPLACE TABLE` diretamente da leitura do arquivo `data/pedidos_starbucks.csv`.

---

## 🥈 2. Camada Silver (`pipeline/transformacao.py`)

A Camada Silver limpa, deduplica e traduz todo o esquema para o português, separando os dados brutos em uma modelagem dimensional relacional (Fato e Dimensões).

### Tabelas Criadas:

### `silver.clientes` (Dimensão Cliente)
* **Volumetria**: 14.988 clientes únicos (Deduplicados)
* **Atributos**: `cliente_id` (PK), `faixa_etaria`, `genero`, `membro_fidelidade` (BOOLEAN).

### `silver.lojas` (Dimensão Loja)
* **Volumetria**: 500 lojas únicas (Deduplicadas)
* **Atributos**: `loja_id` (PK), `tipo_localizacao`, `regiao`.

### `silver.pedidos` (Tabela Fato)
* **Volumetria**: 100.000 pedidos
* **Atributos**: `pedido_id` (PK), `cliente_id` (FK), `loja_id` (FK), `data_pedido` (DATE), `hora_pedido` (TIME), `dia_semana`, `canal_pedido`, `tamanho_carrinho`, `qtd_customizacoes`, `valor_total` (DECIMAL(10,2)), `tempo_atendimento_min`, `categoria_bebida`, `possui_alimento` (BOOLEAN), `pedido_antecipado` (BOOLEAN), `satisfacao_cliente`.

---

## 🥇 3. Camada Gold (`pipeline/marts.py`)

A Camada Gold consolida as métricas de negócio em tabelas de KPIs prontas para consumo.

### Marts de Negócio:
1. `gold.kpi_vendas`: Totais consolidados de faturamento, pedidos e ticket médio.
2. `gold.kpi_categoria_bebida`: Desempenho financeiro e volumetria agrupados por categoria de bebida.
3. `gold.kpi_regiao`: Total de pedidos e faturamento por região geográfica.
4. `gold.kpi_canal`: Indicadores por canal de venda (*In-store*, *Drive-thru*, etc.).
5. `gold.kpi_satisfacao`: Avaliação da satisfação do cliente cruzada com o tempo médio de atendimento.

### 📊 Métricas Consolidadas Validadas:
* **Faturamento Total**: R$ 1.486.677,08
* **Total de Pedidos**: 100.000
* **Ticket Médio**: R$ 14,87