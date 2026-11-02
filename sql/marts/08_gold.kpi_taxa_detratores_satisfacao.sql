##(Indicador de Risco / NPS)
Objetivo de Negócio: Identificar a proporção de clientes insatisfeitos por canal de venda para acionar planos de ação de melhoria no atendimento.

CREATE OR REPLACE TABLE gold.kpi_taxa_detratores_satisfacao AS
SELECT
    canal_pedido,
    COUNT(*) AS total_pedidos,
    COUNT(CASE WHEN satisfacao_cliente IN ('Insatisfeito', 'Muito Insatisfeito') THEN 1 END) AS pedidos_insatisfeitos,
    ROUND(
        COUNT(CASE WHEN satisfacao_cliente IN ('Insatisfeito', 'Muito Insatisfeito') THEN 1 END) * 100.0 / COUNT(*), 
        2
    ) AS percentual_insatisfacao
FROM silver.pedidos
GROUP BY canal_pedido
ORDER BY percentual_insatisfacao DESC;