# 📋 Checklist de Conformidade do Projeto

Esta página registra a validação final de todos os requisitos técnicos exigidos para a entrega do projeto final da pós-graduação.

---

| Item do Curso | Requisito Exigido | Status | Implementação no Projeto |
| :--- | :--- | :---: | :--- |
| **1. Arquitetura em 3 Camadas** | Separação clara dos dados em 3 etapas isoladas (Raw/Bronze, Refined/Silver, Marts/Gold). | ✅ **100% OK** | `ingestao.py` (Bronze/Raw), `transformacao.py` (Silver/Refined) e `marts.py` (Gold/Marts). |
| **2. Camada Bruta Intacta** | Ingestão pura dos arquivos CSV/JSON sem alteração de valores na Bronze. | ✅ **100% OK** | A camada Bronze preserva os dados brutos exatamente como foram extraídos da fonte. |
| **3. Tradução para o Português** | Termos categóricos e colunas traduzidos na camada Silver/Gold. | ✅ **100% OK** | Nomes de colunas, marts e categorias mapeados e traduzidos para o português em `transformacao.py` e `marts.py`. |
| **4. Relacionamento por JOIN** | Existência de pelo menos 1 JOIN entre tabelas relacionais na camada Gold. | ✅ **100% OK** | Marts como `gold.kpi_regiao` e `gold.kpi_eficiencia_operacional_loja` realizam `INNER JOIN` entre `silver.pedidos` e `silver.lojas` por `loja_id`. |
| **5. Queries SQL Organizadas** | Consultas da camada Gold em arquivos `.sql` individuais. | ✅ **100% OK** | Pasta `sql/marts/` estruturada com arquivos `.sql` executados dinamicamente pelo Python. |
| **6. Suíte de Testes (`pytest`)** | Testes unitários com dados mockados em memória, sem depender do banco físico. | ✅ **100% OK** | 9 testes passando em memória isolada via `duckdb.connect(":memory:")`. |
| **7. Qualidade de Código (`ruff`)** | Código formatado sem avisos ou violações de estilo. | ✅ **100% OK** | Regras de linting e formatação validadas com `ruff check` e `ruff format`. |
| **8. Histórico de Commits por Etapa** | Histórico progressivo demonstrando a evolução do projeto em múltiplos commits. | ✅ **100% OK** | Histórico no Git com mensagens estruturadas por etapas (`feat`, `docs`, `chore`). |
| **9. Documentação e README** | README principal detalhando arquitetura, execução e testes. | ✅ **100% OK** | `README.md` formatado com especificações completas do pipeline e blocos de código Markdown. |
| **10. Repositório Público Pessoal** | Repositório hosted na conta pessoal do GitHub (não em conta corporativa nem fork). | ✅ **100% OK** | Repositório público sincronizado diretamente na sua conta pessoal. |