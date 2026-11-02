##(Consolidado de Alto Nível)
Objetivo de Negócio: Uma visão em linha única contendo os principais cartões (KPI Cards) para o topo do seu dashboard no Streamlit.

CREATE OR REPLACE TABLE gold.kpi_resumo_executivo_diretoria AS
SELECT
    COUNT(DISTINCT pedido_id) AS total_pedidos,
    COUNT(DISTINCT cliente_id) AS total_clientes_unicos,
    COUNT(DISTINCT loja_id) AS total_lojas_ativas,
    ROUND(SUM(valor_total), 2) AS faturamento_total,
    ROUND(AVG(valor_total), 2) AS ticket_medio_global,
    ROUND(AVG(tempo_atendimento_min), 2) AS tempo_medio_atendimento_global
FROM silver.pedidos;