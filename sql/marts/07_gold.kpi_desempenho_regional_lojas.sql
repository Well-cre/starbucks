##(Ranking de Performance Por Região)
Objetivo de Negócio: Cruzamento (JOIN) entre as tabelas de dimensões e fatos para comparar o faturamento médio por loja em cada região geográfica.

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