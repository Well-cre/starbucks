##(Eficiência Operacional por Loja)
Objetivo de Negócio: Avaliar o desempenho operacional das lojas com base em métricas de eficiência e tempo de atendimento.

CREATE OR REPLACE TABLE gold.kpi_eficiencia_operacional_loja AS
SELECT
    l.loja_id,
    l.regiao,
    COUNT(p.pedido_id) AS total_pedidos,
    SUM(p.valor_total) AS faturamento_total,
    ROUND(AVG(p.tempo_atendimento_min), 2) AS tempo_medio_espera_min,
    ROUND(MAX(p.tempo_atendimento_min), 2) AS tempo_maximo_espera_min
FROM silver.pedidos AS p
INNER JOIN silver.lojas AS l
    ON p.loja_id = l.loja_id
GROUP BY l.loja_id, l.regiao
ORDER BY faturamento_total DESC;