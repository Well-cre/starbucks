CREATE OR REPLACE TABLE gold.kpi_segmentacao_fidelidade_cliente AS
SELECT
    p.cliente_id,
    COUNT(p.pedido_id) AS frequencia_pedidos,
    SUM(p.valor_total) AS total_gasto_cliente,
    ROUND(AVG(p.valor_total), 2) AS ticket_medio_cliente
FROM silver.pedidos AS p
GROUP BY p.cliente_id
ORDER BY total_gasto_cliente DESC;