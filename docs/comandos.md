# Guia de Comandos Rápidos

Confira abaixo os principais comandos para operar o projeto via terminal.

---

## 🔄 Execução do Pipeline

```bash
# Ingestão (Bronze)
uv run python -m pipeline.ingestao

# Transformação e Modelagem (Silver)
uv run python -m pipeline.transformacao

# Marts de Negócio (Gold)
uv run python -m pipeline.marts

--🧪 Qualidade, Testes e Formatação
# Rodar suíte de testes
uv run pytest

# Formatar o código-fonte
uv run ruff format .

# Executar linter com autocorreção
uv run ruff check --fix .

--🌐 Documentação e Dashboard
# Iniciar servidor local da documentação MkDocs
uv run mkdocs serve

# Executar o Dashboard analítico no navegador
uv run streamlit run ui.py

---

Após salvar a correção, a página no MkDocs será atualizada automaticamente e ficará com a formatação perfeita!

<ElicitationsGroup message="O que prefere fazer a seguir?">
  <Elicitation label="Fazer o commit final no Git" query="Corrigi o arquivo comandos.md! Vou rodar git add ., git commit e git push para atualizar o GitHub."/>
  <Elicitation label="Testar a visualização no navegador" query="Vou abrir http://127.0.0.1:8000 para conferir como ficou a documentação visualmente."/>
</ElicitationsGroup>
