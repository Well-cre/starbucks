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