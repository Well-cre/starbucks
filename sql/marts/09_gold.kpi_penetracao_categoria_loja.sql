-- Mix de Produtos por Loja
-- Objetivo de negócio: analisar a venda de cada categoria por loja e região.

CREATE OR REPLACE TABLE gold.kpi_penetracao_categoria_loja AS
SELECT
    l.loja_id,
    l.regiao,
    p.categoria_bebida,
    COUNT(p.pedido_id) AS quantidade_vendida,
    SUM(p.valor_total) AS faturamento_categoria
FROM silver.pedidos AS p
INNER JOIN silver.lojas AS l
    ON p.loja_id = l.loja_id
GROUP BY l.loja_id, l.regiao, p.categoria_bebida
ORDER BY l.loja_id, faturamento_categoria DESC;
