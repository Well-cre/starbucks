# Testes Automatizados e Boas Práticas

---

## 🧪 Suíte de Testes Automatizados (`tests/test_pipeline.py`)

Garantimos a qualidade e a integridade do pipeline através de testes automatizados com o **Pytest**.

### Casos de Teste Executados:

1. **`test_camada_bronze`**
   * Confirma a existência da tabela `bronze.pedidos_starbucks`.
   * Assegura que o total de linhas ingeridas é exatamente equal a 100.000.

2. **`test_camada_silver_contagens_e_nulos`**
   * Valida a volumetria exata das dimensões (`clientes`: 14.988; `lojas`: 500; `pedidos`: 100.000).
   * Garante a ausência de valores nulos nas Chaves Primárias.

3. **`test_camada_silver_integridade_referencial`**
   * Realiza um `INNER JOIN` entre as tabelas de Fato e Dimensões.
   * Valida que 100% dos 100.000 pedidos mantêm integridade referencial sem chaves órfãs.

4. **`test_camada_gold_marts`**
   * Valida a existência dos 5 marts do schema `gold`.
   * Confirma que o faturamento acumulado bate com o total da camada Silver (R$ 1.486.677,08).

---

## 🛡️ Guia de Boas Práticas Adotadas

* **Spec-Driven Development (SDD)**: Código derivado estritamente de especificações formais.
* **Idempotência**: Todos os scripts podem reexecutar sem duplicar dados (`CREATE OR REPLACE TABLE`).
* **Tipagem Estrita**: Nomes padronizados em português snake_case e tipos explícitos no DuckDB.
* **Isolamento de Conexão**: Conexões de testes em modo de leitura para evitar bloqueios de arquivo no DuckDB.

---

## 🛠️ Qualidade de Código e Padrões

O projeto **Starbucks Data Pipeline** segue as normas globais de desenvolvimento em Python para garantir legibilidade, manutenção e confiabilidade, com apoio de testes e ferramentas automatizadas.

### Padrão de Estilo (PEP 8)

O código segue o guia de estilo oficial **PEP 8**. O projeto utiliza o gerenciador de pacotes **`uv`** e o **Ruff** como formatador e linter. O Ruff aplica, entre outras, as regras `E`, que verificam erros de estilo da PEP 8, além das regras do Pyflakes (`F`) e do isort (`I`).

As regras de lint e o limite de linha (`line-length = 150`) estão centralizados no arquivo `pyproject.toml`.

### Verificação de Lint

Para verificar se o código está livre de violações das regras configuradas, execute:

```bash
uv run ruff check .
```

Para formatar o código:

```bash
uv run ruff format .
```