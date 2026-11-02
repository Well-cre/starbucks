##(Análise de Pico e Turnos)
Objetivo de Negócio: Mapear o faturamento e o volume de vendas por faixa horária/período do dia (Manhã, Tarde, Noite) para otimização de escalas de funcionários e estoque.

CREATE OR REPLACE TABLE gold.kpi_faturamento_por_periodo_dia AS
SELECT
    CASE 
        WHEN EXTRACT(HOUR FROM data_hora_pedido) BETWEEN 6 AND 11 THEN 'Manhã'
        WHEN EXTRACT(HOUR FROM data_hora_pedido) BETWEEN 12 AND 17 THEN 'Tarde'
        ELSE 'Noite'
    END AS periodo_dia,
    COUNT(pedido_id) AS total_pedidos,
    SUM(valor_total) AS faturamento_total,
    ROUND(AVG(valor_total), 2) AS ticket_medio
FROM silver.pedidos
GROUP BY periodo_dia
ORDER BY faturamento_total DESC;