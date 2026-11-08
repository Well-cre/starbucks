import base64
import unicodedata
from dataclasses import dataclass
from decimal import Decimal
from pathlib import Path

import duckdb
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

ROOT_DIR = Path(__file__).resolve().parent
DATABASE_PATH = ROOT_DIR / "starbucks.duckdb"
GREEN = "#006241"
GREEN_DARK = "#1E3932"
TEXT = "#0F172A"
MUTED = "#64748B"
GRID = "#E2E8F0"
CHART_COLORS = [GREEN, "#2D8063", "#78A98F", "#A9C9B8", "#D5E7DE"]

st.set_page_config(
    page_title="Starbucks | Inteligência de negócios",
    page_icon="☕",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown(
    """
    <style>
    .stApp {
        background: #F8FAFC;
        color: #0F172A;
        font-family: Inter, system-ui, sans-serif;
    }
    .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
    }
    .dashboard-header {
        background: linear-gradient(120deg, #006241 0%, #1E3932 100%);
        border-radius: 18px;
        color: #FFFFFF;
        padding: 1.8rem 2rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 12px 30px rgba(0, 98, 65, 0.14);
    }
    .dashboard-header h1 {
        color: #FFFFFF !important;
        font-size: 2rem;
        line-height: 1.2;
        margin: 0;
    }
    .dashboard-header p {
        color: #D5E7DE;
        font-size: 1rem;
        margin: .45rem 0 0;
    }
    h1, h2, h3, h4 {
        color: #0F172A !important;
        letter-spacing: -0.02em;
    }
    div[data-testid="stMetric"] {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 16px;
        padding: 1rem 1.2rem;
        box-shadow: 0 4px 14px rgba(15, 23, 42, .04);
    }
    div[data-testid="stMetricLabel"] p {
        color: #64748B !important;
        font-size: .82rem !important;
        font-weight: 650 !important;
    }
    div[data-testid="stMetricValue"] div {
        color: #006241 !important;
        font-size: 1.8rem !important;
        font-weight: 750 !important;
    }
    div[data-testid="stVerticalBlockBorderWrapper"] {
        background: #FFFFFF;
        border-color: #E2E8F0 !important;
        border-radius: 16px;
    }
    div[data-testid="stTextInput"] input {
        border-radius: 12px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_resource
def get_connection(database_path: str) -> duckdb.DuckDBPyConnection:
    return duckdb.connect(database_path, read_only=True)


@st.cache_data(ttl=60, max_entries=32)
def carregar_dados(sql: str, parametros: tuple[str, ...] = ()) -> pd.DataFrame:
    return get_connection(str(DATABASE_PATH)).execute(sql, list(parametros)).df()


@dataclass
class RespostaAnalitica:
    texto: str
    df: pd.DataFrame | None = None


@dataclass(frozen=True)
class Consulta:
    titulo: str
    sql: str
    x: str
    y: str
    tipo_grafico: str
    descricao_grafico: str
    parametros: tuple[str, ...] = ()


def normalizar(texto: str) -> str:
    texto = unicodedata.normalize("NFKD", texto.casefold())
    return "".join(caractere for caractere in texto if not unicodedata.combining(caractere))


def regiao_solicitada(pergunta: str) -> str | None:
    termos = {
        "west": ("oeste", "west", "zona oeste"),
        "north": ("norte", "north", "zona norte"),
        "south": ("sul", "south", "zona sul"),
        "east": ("leste", "east", "zona leste"),
    }
    for valor, sinonimos in termos.items():
        if any(termo in pergunta for termo in sinonimos):
            return f"%{valor}%"
    return None


# ==========================================
# FAIXAS DE CONSULTA MODULARIZADAS (CLEAN CODE)
# ==========================================


def _consultar_produto_regiao(texto: str, filtro_regiao: str | None) -> Consulta | None:
    if any(t in texto for t in ("produto", "produtos", "bebida", "bebidas")) and filtro_regiao:
        return Consulta(
            "Produtos por região",
            """
            SELECT
                p.categoria_bebida AS produto,
                COUNT(*) AS total_pedidos,
                SUM(p.valor_total) AS faturamento_total
            FROM silver.pedidos p
            INNER JOIN silver.lojas l
                ON p.loja_id = l.loja_id
            WHERE LOWER(l.regiao) LIKE ?
            GROUP BY p.categoria_bebida
            ORDER BY faturamento_total DESC
            """,
            "produto",
            "faturamento_total",
            "bar",
            "Produtos mais vendidos na região",
            (filtro_regiao,),
        )
    return None


def _consultar_canal_regiao(texto: str, filtro_regiao: str | None) -> Consulta | None:
    if any(t in texto for t in ("canal", "canais", "mobile", "drive", "presencial")) and filtro_regiao:
        return Consulta(
            "Canais por região",
            """
            SELECT
                p.canal_pedido,
                COUNT(*) AS total_pedidos,
                SUM(p.valor_total) AS faturamento_total
            FROM silver.pedidos p
            INNER JOIN silver.lojas l
                ON p.loja_id = l.loja_id
            WHERE LOWER(l.regiao) LIKE ?
            GROUP BY p.canal_pedido
            ORDER BY faturamento_total DESC
            """,
            "canal_pedido",
            "faturamento_total",
            "bar",
            "Desempenho dos canais por região",
            (filtro_regiao,),
        )
    return None


def _consultar_clientes(texto: str) -> Consulta | None:
    if any(termo in texto for termo in ("idade", "faixa etaria", "faixa etária", "cliente", "clientes")):
        return Consulta(
            "Perfil dos clientes",
            """
            SELECT
                c.faixa_etaria,
                COUNT(*) AS total_pedidos,
                SUM(p.valor_total) AS faturamento_total
            FROM silver.pedidos p
            INNER JOIN silver.clientes c
                ON p.cliente_id = c.cliente_id
            GROUP BY c.faixa_etaria
            ORDER BY faturamento_total DESC
            """,
            "faixa_etaria",
            "faturamento_total",
            "bar",
            "Faturamento por faixa etária",
        )
    return None


def _consultar_satisfacao(texto: str) -> Consulta | None:
    if any(termo in texto for termo in ("satisfacao", "satisfação", "avaliacao", "avaliação", "nota")):
        return Consulta(
            "Satisfação dos clientes",
            """
            SELECT
                satisfacao_cliente AS nota_satisfacao,
                quantidade_pedidos AS total_pedidos,
                faturamento_total,
                tempo_medio_atendimento AS tempo_medio_min
            FROM gold.kpi_satisfacao
            ORDER BY nota_satisfacao
            """,
            "nota_satisfacao",
            "total_pedidos",
            "donut",
            "Pedidos por nota de satisfação",
        )
    return None


def _consultar_turnos(texto: str) -> Consulta | None:
    if any(termo in texto for termo in ("turno", "turnos", "hora", "horario", "horário", "pico")):
        return Consulta(
            "Pedidos por turno",
            """
            WITH pedidos_por_turno AS (
                SELECT
                    CASE
                        WHEN EXTRACT(HOUR FROM hora_pedido) < 6 THEN 'Madrugada'
                        WHEN EXTRACT(HOUR FROM hora_pedido) < 12 THEN 'Manhã'
                        WHEN EXTRACT(HOUR FROM hora_pedido) < 18 THEN 'Tarde'
                        ELSE 'Noite'
                    END AS turno,
                    valor_total
                FROM silver.pedidos
            )
            SELECT
                turno,
                COUNT(*) AS total_pedidos,
                SUM(valor_total) AS faturamento_total
            FROM pedidos_por_turno
            GROUP BY turno
            ORDER BY total_pedidos DESC
            """,
            "turno",
            "total_pedidos",
            "bar",
            "Pedidos por turno",
        )
    return None


def _consultar_lojas(texto: str, menciona_lojas: bool, filtro_regiao: str | None) -> Consulta | None:
    if menciona_lojas:
        filtro_sql = "WHERE LOWER(l.regiao) LIKE ?" if filtro_regiao else ""
        parametros = (filtro_regiao,) if filtro_regiao else ()
        return Consulta(
            "Lojas com maior faturamento",
            f"""
            SELECT
                l.loja_id AS loja,
                l.regiao,
                COUNT(*) AS total_pedidos,
                SUM(p.valor_total) AS faturamento_total
            FROM silver.pedidos p
            INNER JOIN silver.lojas l
                ON p.loja_id = l.loja_id
            {filtro_sql}
            GROUP BY l.loja_id, l.regiao
            ORDER BY faturamento_total DESC
            LIMIT 10
            """,
            "loja",
            "faturamento_total",
            "bar",
            "Lojas com maior faturamento",
            parametros,
        )
    return None


def _consultar_regioes(texto: str, filtro_regiao: str | None) -> Consulta | None:
    if any(termo in texto for termo in ("regiao", "região", "regional", "oeste", "west", "norte", "north", "sul", "south", "leste", "east")):
        filtro_sql = "WHERE LOWER(regiao) LIKE ?" if filtro_regiao else ""
        parametros = (filtro_regiao,) if filtro_regiao else ()
        return Consulta(
            "Vendas por região",
            f"""
            SELECT
                regiao,
                total_pedidos,
                faturamento_total,
                ticket_medio
            FROM gold.kpi_regiao
            {filtro_sql}
            ORDER BY faturamento_total DESC
            """,
            "regiao",
            "faturamento_total",
            "bar",
            "Faturamento por região",
            parametros,
        )
    return None


def _consultar_produtos_geral(texto: str) -> Consulta | None:
    if any(termo in texto for termo in ("produto", "produtos", "bebida", "bebidas", "categoria")):
        return Consulta(
            "Produtos",
            """
            SELECT
                categoria_bebida AS produto,
                quantidade_pedidos AS total_pedidos,
                faturamento_total,
                ticket_medio
            FROM gold.kpi_categoria_bebida
            ORDER BY faturamento_total DESC
            """,
            "produto",
            "faturamento_total",
            "bar",
            "Faturamento por produto",
        )
    return None


def _consultar_canais_geral(texto: str) -> Consulta | None:
    if any(termo in texto for termo in ("canal", "canais", "mobile", "drive", "presencial")):
        return Consulta(
            "Canais",
            """
            SELECT
                canal_pedido AS canal,
                total_pedidos,
                faturamento_total
            FROM gold.kpi_canal
            ORDER BY total_pedidos DESC
            """,
            "canal",
            "total_pedidos",
            "donut",
            "Participação dos canais",
        )
    return None


def buscar_consulta(pergunta: str) -> Consulta:
    """Função principal orquestradora: delega a busca para funções de domínio específicas."""
    texto = normalizar(pergunta)
    filtro_regiao = regiao_solicitada(texto)
    menciona_lojas = any(termo in texto for termo in ("loja", "lojas", "melhor loja", "melhores lojas"))

    # Orquestração limpa das regras de negócio
    for funcao_consulta in [
        lambda: _consultar_produto_regiao(texto, filtro_regiao),
        lambda: _consultar_canal_regiao(texto, filtro_regiao),
        lambda: _consultar_clientes(texto),
        lambda: _consultar_satisfacao(texto),
        lambda: _consultar_turnos(texto),
        lambda: _consultar_lojas(texto, menciona_lojas, filtro_regiao),
        lambda: _consultar_regioes(texto, filtro_regiao),
        lambda: _consultar_produtos_geral(texto),
        lambda: _consultar_canais_geral(texto),
    ]:
        resultado = funcao_consulta()
        if resultado is not None:
            return resultado

    # Padrão (Fallback) caso nenhuma condição seja satisfeita
    return Consulta(
        "Vendas ao longo do tempo",
        """
        SELECT
            DATE_TRUNC('month', data_pedido)::DATE AS mes,
            COUNT(*) AS total_pedidos,
            SUM(valor_total) AS faturamento_total
        FROM silver.pedidos
        GROUP BY mes
        ORDER BY mes
        """,
        "mes",
        "faturamento_total",
        "line",
        "Evolução mensal do faturamento",
    )


def formatar_moeda(valor: float | Decimal) -> str:
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def renderizar_grafico(df: pd.DataFrame, consulta: Consulta, chave: str) -> None:
    if df.empty:
        return

    x = consulta.x if consulta.x in df.columns else df.select_dtypes(include=["object", "string", "datetime"]).columns[0]
    y = consulta.y if consulta.y in df.columns else df.select_dtypes(include=["number"]).columns[0]
    moeda = any(termo in y for termo in ("faturamento", "ticket"))

    if consulta.tipo_grafico == "donut":
        fig = px.pie(
            df,
            names=x,
            values=y,
            hole=0.62,
            color_discrete_sequence=CHART_COLORS,
            labels={x: "Categoria", y: "Pedidos"},
        )
        fig.update_traces(
            textposition="outside",
            texttemplate="%{label}<br>%{value:,.0f} · %{percent:.1%}",
            textfont={"size": 12, "color": TEXT},
            hovertemplate="%{label}<br>Pedidos: %{value:,.0f}<br>Participação: %{percent:.1%}<extra></extra>",
            sort=False,
        )
        fig.update_layout(
            showlegend=False,
            margin={"l": 24, "r": 24, "t": 30, "b": 24},
        )
    elif consulta.tipo_grafico == "line":
        fig = px.line(
            df,
            x=x,
            y=y,
            markers=True,
            color_discrete_sequence=[GREEN],
            labels={x: "Mês", y: "Faturamento (R$)" if moeda else "Quantidade"},
        )
        fig.update_traces(
            line={"width": 3},
            marker={"size": 7},
            texttemplate="R$ %{y:.2s}" if moeda else "%{y:.2s}",
            textposition="top center",
            textfont={"size": 10, "color": GREEN_DARK},
            hovertemplate="%{x|%b %Y}<br>Faturamento: R$ %{y:,.2f}<extra></extra>",
        )
        fig.update_xaxes(tickformat="%b\n%Y")
        fig.update_layout(margin={"l": 24, "r": 20, "t": 42, "b": 36})
    else:
        fig = px.bar(
            df,
            x=x,
            y=y,
            color=y,
            color_continuous_scale=["#D5E7DE", GREEN],
            labels={
                x: x.replace("_", " ").title(),
                y: ("Faturamento (R$)" if "faturamento" in y else "Ticket médio (R$)" if "ticket" in y else y.replace("_", " ").title()),
            },
        )
        fig.update_traces(
            text=df[y],
            texttemplate="R$ %{y:,.2f}" if moeda else "%{y:,.0f}",
            textposition="outside",
            textfont={"size": 11, "color": TEXT},
            cliponaxis=False,
            hovertemplate=("%{x}<br>Faturamento: R$ %{y:,.2f}<extra></extra>" if moeda else "%{x}<br>Quantidade: %{y:,.0f}<extra></extra>"),
        )
        fig.update_xaxes(tickangle=-20, automargin=True)
        fig.update_yaxes(
            tickformat=",.2s" if moeda else ",.0f",
            range=[0, max(float(df[y].max()), 1) * 1.2],
            automargin=True,
        )
        fig.update_layout(
            coloraxis_colorbar={"title": "Faturamento (R$)" if moeda else "Quantidade"},
            margin={"l": 24, "r": 36, "t": 60, "b": 76},
        )

    fig.update_layout(
        title={
            "text": consulta.descricao_grafico,
            "font": {"size": 16, "color": GREEN_DARK},
        },
        font={"family": "Inter, system-ui, sans-serif", "size": 12, "color": TEXT},
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        hoverlabel={"bgcolor": "#FFFFFF", "font_color": TEXT},
    )
    fig.update_yaxes(showgrid=True, gridcolor=GRID, zeroline=False)
    st.plotly_chart(
        fig,
        width="stretch",
        alt=consulta.descricao_grafico,
        key=chave,
        config={"displaylogo": False},
    )


if not DATABASE_PATH.is_file():
    st.error("Banco de dados não encontrado. Execute a ingestão antes de abrir o painel.")
    st.stop()

# --- CARREGA O LOGO EM BASE64 PARA DENTRO DA CAIXA VERDE ---
logo_path = ROOT_DIR / "logo_cafe.png"
logo_src = ""
if logo_path.is_file():
    with open(logo_path, "rb") as f:
        encoded_image = base64.b64encode(f.read()).decode("utf-8")
    logo_src = f"data:image/png;base64,{encoded_image}"

st.markdown(
    f"""
    <div class="dashboard-header" style="display: flex; align-items: center; gap: 1.5rem;">
        <img src="{logo_src}" width="75" alt="Logo Café" style="border-radius: 12px; background: #FFFFFF; padding: 4px; object-fit: cover;">
        <div>
            <h1>Inteligência de negócios</h1>
            <p>Uma visão clara de clientes, lojas, produtos, pedidos e vendas.</p>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.subheader("Explore os dados")
st.caption("Faça uma pergunta sobre vendas, melhores lojas, região oeste, satisfação, produtos ou turnos.")
pergunta = st.text_input(
    "Pergunta",
    placeholder="Ex.: Quais foram as melhores lojas da região oeste?",
    type="search",
    label_visibility="collapsed",
)

if pergunta.strip():
    consulta = buscar_consulta(pergunta)
    resultado = carregar_dados(consulta.sql, consulta.parametros)
    st.markdown(f"#### {consulta.titulo}")
    if resultado.empty:
        st.info("Não há resultados para essa pesquisa.")
    else:
        renderizar_grafico(resultado, consulta, "resultado_busca")
        st.dataframe(
            resultado,
            hide_index=True,
            width="stretch",
            alt=f"Resultados da pesquisa: {consulta.titulo}",
        )

st.subheader("Resumo do negócio")
resumo = carregar_dados(
    """
    SELECT COUNT(DISTINCT cliente_id) AS total_clientes,
           COUNT(DISTINCT loja_id) AS total_lojas,
           COUNT(*) AS total_pedidos,
           SUM(valor_total) AS faturamento_total,
           AVG(valor_total) AS ticket_medio
    FROM silver.pedidos
    """
)

if not resumo.empty:
    indicadores = resumo.iloc[0]
    colunas = st.columns(4)
    colunas[0].metric("Clientes", f"{indicadores['total_clientes']:,.0f}".replace(",", "."))
    colunas[1].metric("Lojas", f"{indicadores['total_lojas']:,.0f}".replace(",", "."))
    colunas[2].metric("Pedidos", f"{indicadores['total_pedidos']:,.0f}".replace(",", "."))
    colunas[3].metric("Faturamento", formatar_moeda(indicadores["faturamento_total"]))

# ==========================
# INSIGHTS AUTOMÁTICOS
# ==========================

st.subheader("📊 Insights Automáticos")

produtos_insight = carregar_dados(
    """
    SELECT categoria_bebida AS produto,
           quantidade_pedidos,
           faturamento_total
    FROM gold.kpi_categoria_bebida
    ORDER BY faturamento_total DESC
    LIMIT 1
    """
)

canais_insight = carregar_dados(
    """
    SELECT canal_pedido AS canal,
           total_pedidos,
           faturamento_total
    FROM gold.kpi_canal
    ORDER BY total_pedidos DESC
    LIMIT 1
    """
)

regioes_insight = carregar_dados(
    """
    SELECT regiao,
           total_pedidos,
           faturamento_total
    FROM gold.kpi_regiao
    ORDER BY faturamento_total DESC
    LIMIT 1
    """
)

if not produtos_insight.empty and not canais_insight.empty and not regioes_insight.empty:
    produto_top = produtos_insight.iloc[0]
    canal_top = canais_insight.iloc[0]
    regiao_top = regioes_insight.iloc[0]

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.metric("🏆 Produto líder", produto_top["produto"])
        st.caption(f"Faturamento: {formatar_moeda(produto_top['faturamento_total'])}")

    with c2:
        st.metric("📱 Canal líder", canal_top["canal"])
        st.caption(f"{int(canal_top['total_pedidos']):,} pedidos".replace(",", "."))

    with c3:
        st.metric("🌎 Região destaque", regiao_top["regiao"])
        st.caption(f"Faturamento: {formatar_moeda(regiao_top['faturamento_total'])}")

    with c4:
        st.metric(
            "👥 Clientes ativos",
            f"{int(indicadores['total_clientes']):,}".replace(",", "."),
        )
        st.caption("Base de clientes")

tab_comercial, tab_regional, tab_experiencia, tab_fluxo = st.tabs(["Comercial", "Regiões e lojas", "Clientes e operação", "Fluxo das entidades"])

with tab_comercial:
    coluna_produtos, coluna_canais = st.columns(2)
    produtos = carregar_dados(
        """
        SELECT categoria_bebida AS produto,
               quantidade_pedidos AS total_pedidos,
               faturamento_total
        FROM gold.kpi_categoria_bebida
        ORDER BY faturamento_total DESC
        """
    )
    canais = carregar_dados(
        """
        SELECT canal_pedido AS canal, total_pedidos, faturamento_total
        FROM gold.kpi_canal
        ORDER BY total_pedidos DESC
        """
    )
    with coluna_produtos, st.container(border=True):
        st.subheader("Produtos")
        renderizar_grafico(
            produtos,
            Consulta(
                "Produtos",
                "",
                "produto",
                "faturamento_total",
                "bar",
                "Faturamento por produto",
            ),
            "grafico_produtos",
        )
        st.dataframe(produtos, hide_index=True, width="stretch", alt="Vendas por produto")
    with coluna_canais, st.container(border=True):
        st.subheader("Canais de venda")
        renderizar_grafico(
            canais,
            Consulta(
                "Canais",
                "",
                "canal",
                "total_pedidos",
                "donut",
                "Participação dos pedidos por canal",
            ),
            "grafico_canais",
        )
        st.dataframe(canais, hide_index=True, width="stretch", alt="Vendas por canal")

with tab_regional:
    regioes = carregar_dados(
        """
        SELECT regiao, total_pedidos, faturamento_total, ticket_medio
        FROM gold.kpi_regiao
        ORDER BY faturamento_total DESC
        """
    )
    with st.container(border=True):
        st.subheader("Vendas por região")
        renderizar_grafico(
            regioes,
            Consulta(
                "Vendas por região",
                "",
                "regiao",
                "faturamento_total",
                "bar",
                "Faturamento por região",
            ),
            "grafico_regioes",
        )
        st.dataframe(regioes, hide_index=True, width="stretch", alt="Indicadores por região")

with tab_experiencia:
    coluna_satisfacao, coluna_turnos = st.columns(2)
    satisfacao = carregar_dados(
        """
        SELECT satisfacao_cliente AS nota_satisfacao,
               quantidade_pedidos AS total_pedidos,
               faturamento_total
        FROM gold.kpi_satisfacao
        ORDER BY nota_satisfacao
        """
    )
    turnos = carregar_dados(
        """
        WITH pedidos_por_turno AS (
            SELECT
                CASE
                    WHEN EXTRACT(HOUR FROM hora_pedido) < 6 THEN 'Madrugada'
                    WHEN EXTRACT(HOUR FROM hora_pedido) < 12 THEN 'Manhã'
                    WHEN EXTRACT(HOUR FROM hora_pedido) < 18 THEN 'Tarde'
                    ELSE 'Noite'
                END AS turno,
                hora_pedido,
                valor_total
            FROM silver.pedidos
        )
        SELECT turno, COUNT(*) AS total_pedidos, SUM(valor_total) AS faturamento_total
        FROM pedidos_por_turno
        GROUP BY turno
        ORDER BY CASE turno
            WHEN 'Madrugada' THEN 1
            WHEN 'Manhã' THEN 2
            WHEN 'Tarde' THEN 3
            ELSE 4
        END
        """
    )
    with coluna_satisfacao, st.container(border=True):
        st.subheader("Satisfação")
        renderizar_grafico(
            satisfacao,
            Consulta(
                "Satisfação",
                "",
                "nota_satisfacao",
                "total_pedidos",
                "donut",
                "Pedidos por nota de satisfação",
            ),
            "grafico_satisfacao",
        )
        st.dataframe(
            satisfacao,
            hide_index=True,
            width="stretch",
            alt="Pedidos e vendas por nota de satisfação",
        )
    with coluna_turnos, st.container(border=True):
        st.subheader("Pedidos por turno")
        renderizar_grafico(
            turnos,
            Consulta(
                "Pedidos por turno",
                "",
                "turno",
                "total_pedidos",
                "bar",
                "Pedidos em cada turno do dia",
            ),
            "grafico_turnos",
        )
        st.dataframe(turnos, hide_index=True, width="stretch", alt="Pedidos por turno")

with tab_fluxo:
    totais = carregar_dados(
        """
        SELECT COUNT(*) AS total_pedidos,
               COUNT(valor_total) AS total_vendas,
               COUNT(satisfacao_cliente) AS total_satisfacoes
        FROM silver.pedidos
        """
    ).iloc[0]
    valor_pedidos = int(totais["total_pedidos"])
    valor_vendas = int(totais["total_vendas"])
    valor_satisfacoes = int(totais["total_satisfacoes"])

    fluxo = go.Figure(
        go.Sankey(
            arrangement="snap",
            node={
                "pad": 28,
                "thickness": 24,
                "line": {"color": "#FFFFFF", "width": 1.5},
                "label": ["Clientes", "Lojas", "Pedidos", "Vendas", "Satisfação"],
                "color": [GREEN_DARK, "#2D8063", GREEN, "#78A98F", "#A9C9B8"],
                "hovertemplate": "%{label}<extra></extra>",
            },
            link={
                "source": [0, 1, 2, 2],
                "target": [1, 2, 3, 4],
                "value": [
                    valor_pedidos,
                    valor_pedidos,
                    valor_vendas,
                    valor_satisfacoes,
                ],
                "color": [
                    "rgba(0, 98, 65, .20)",
                    "rgba(45, 128, 99, .24)",
                    "rgba(0, 98, 65, .28)",
                    "rgba(120, 169, 143, .35)",
                ],
                "hovertemplate": "%{value:,.0f} registros<extra></extra>",
            },
        )
    )
    fluxo.update_layout(
        font={"family": "Inter, system-ui, sans-serif", "size": 13, "color": TEXT},
        paper_bgcolor="rgba(0,0,0,0)",
        margin={"l": 24, "r": 24, "t": 24, "b": 24},
        height=470,
    )
    with st.container(border=True):
        st.subheader("Clientes → Lojas → Pedidos → Vendas e satisfação")
        st.plotly_chart(
            fluxo,
            width="stretch",
            alt="Fluxo entre clientes, lojas, pedidos, vendas e satisfação",
            key="fluxo_entidades",
            config={"displaylogo": False},
        )
