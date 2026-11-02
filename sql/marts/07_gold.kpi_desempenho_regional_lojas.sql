-- Ranking de Performance por Região
-- Objetivo de negócio: comparar o faturamento e o volume de pedidos por região.

CREATE OR REPLACE TABLE gold.kpi_desempenho_regional_lojas AS
SELECT
    l.regiao,
    COUNT(DISTINCT l.loja_id) AS quantidade_lojas,
    COUNT(p.pedido_id) AS total_pedidos,
    SUM(p.valor_total) AS faturamento_total,
    ROUND(SUM(p.valor_total) / COUNT(DISTINCT l.loja_id), 2) AS faturamento_medio_por_loja
FROM silver.pedidos AS p
INNER JOIN silver.lojas AS l
    ON p.loja_id = l.loja_id
GROUP BY l.regiao
ORDER BY faturamento_total DESC;