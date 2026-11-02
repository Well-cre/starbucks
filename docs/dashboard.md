# Painel de Inteligência de Negócios (UI)

O painel interativo foi desenvolvido com **Streamlit** e consome os dados diretamente da camada Gold do DuckDB. Ele fornece uma visão analítica abrangente sobre o desempenho das lojas, comportamento dos clientes e fluxo de vendas da Starbucks.

## Identidade Visual e Layout

O painel incorpora a identidade visual da Starbucks, utilizando o logo oficial no cabeçalho executivo e uma paleta de cores baseada no icônico verde da marca (como `#006241` e `#1E3932`). A interface utiliza um layout fluido (wide) estruturado para facilitar a leitura de métricas financeiras e operacionais.

## Funcionalidades Principais

* **Resumo do Negócio:** Métricas globais fixas mostrando o total de clientes, lojas, pedidos e faturamento.
* **Insights Automáticos:** Destaques dinâmicos apontando o produto líder, o canal mais utilizado, a região de destaque e a base ativa de clientes.
* **Navegação por Abas:**
    * **Comercial:** Desempenho detalhado por categoria de bebidas e participação dos canais de venda (Mobile, Drive, Presencial).
    * **Regiões e Lojas:** Faturamento segmentado pelas regiões geográficas.
    * **Clientes e Operação:** Distribuição da satisfação dos clientes e volume de pedidos agrupados por turnos (Manhã, Tarde, Noite, Madrugada).
    * **Fluxo das Entidades:** Um diagrama de Sankey interativo mapeando a proporção de registros no fluxo `Clientes → Lojas → Pedidos → Vendas e Satisfação`.

## Motor de Buscas Inteligentes (Filtros Compostos)

A barra de exploração de dados permite buscar informações em linguagem natural. O sistema normaliza a entrada do usuário e mapeia o texto para consultas SQL predefinidas. 

O motor de busca (`buscar_consulta`) foi aprimorado para suportar **filtros compostos**, cruzando dimensões essenciais. Exemplos de buscas suportadas:

* **Produto + Região:** *"Quais as bebidas mais vendidas na região oeste?"*
* **Canal + Região:** *"Qual o canal com mais pedidos na regional sul?"*
* **Lojas + Região:** *"Quais são as melhores lojas do norte?"*
* **Faixa Etária:** *"Qual é a idade e perfil dos nossos clientes?"*
* **Satisfação:** *"Como está a avaliação e notas gerais?"*
* **Turnos:** *"Qual é o horário de pico com mais vendas?"*

Com base na intenção detectada, o painel renderiza automaticamente o gráfico mais adequado (Barras, Linhas ou Donut) e exibe a tabela de dados detalhada correspondente.    