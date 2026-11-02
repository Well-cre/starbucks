##(Curva ABC de Produtos)
Objetivo de Negócio: Classificar os produtos com base em sua contribuição para o faturamento e identificar os mais importantes.

CREATE OR REPLACE TABLE gold.kpi_curva_abc_produtos AS
SELECT
    categoria_bebida,
    COUNT(*) AS total_pedidos,
    SUM(valor_total) AS faturamento_total,
    ROUND(AVG(valor_total), 2) AS ticket_medio,
    ROUND(SUM(valor_total) * 100.0 / SUM(SUM(valor_total)) OVER (), 2) AS percentual_faturamento
FROM silver.pedidos
GROUP BY categoria_bebida
ORDER BY faturamento_total DESC;