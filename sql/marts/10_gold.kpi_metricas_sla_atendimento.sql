-- Gargalos de Espera na Operação
-- Objetivo de negócio: classificar os pedidos por tempo de atendimento.

CREATE OR REPLACE TABLE gold.kpi_metricas_sla_atendimento AS
SELECT
    CASE
        WHEN tempo_atendimento_min <= 3 THEN 'Atendimento Rápido (<= 3 min)'
        WHEN tempo_atendimento_min <= 8 THEN 'Atendimento Normal (> 3-8 min)'
        ELSE 'Atendimento Lento (> 8 min)'
    END AS faixa_espera,
    COUNT(*) AS quantidade_pedidos,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 2) AS percentual_total,
    ROUND(AVG(valor_total), 2) AS ticket_medio
FROM silver.pedidos
GROUP BY faixa_espera
ORDER BY quantidade_pedidos DESC;