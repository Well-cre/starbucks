##(Desempenho dos Canais e Satisfação do Cliente)
Objetivo de Negócio: Analisar o desempenho dos diferentes canais de venda e sua relação com a satisfação do cliente.

CREATE OR REPLACE TABLE gold.kpi_desempenho_canais_satisfacao AS
SELECT
    canal_pedido,
    satisfacao_cliente,
    COUNT(*) AS total_pedidos,
    SUM(valor_total) AS faturamento_total,
    ROUND(AVG(tempo_atendimento_min), 2) AS tempo_medio_atendimento
FROM silver.pedidos
GROUP BY canal_pedido, satisfacao_cliente
ORDER BY canal_pedido, total_pedidos DESC;