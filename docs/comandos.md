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

🧪 Qualidade, Testes e Formatação
# Rodar suíte de testes
uv run pytest

# Formatar o código-fonte
uv run ruff format .

# Executar linter com autocorreção
uv run ruff check --fix .

🌐 Documentação e Dashboard
# Iniciar servidor local da documentação MkDocs
uv run mkdocs serve

# Executar o Dashboard analítico no navegador
uv run streamlit run ui.py

---

Depois de salvar os arquivos, o servidor do MkDocs (que já está rodando no seu terminal) atualizará as páginas instantaneamente!

<ElicitationsGroup message="O que deseja fazer a seguir?">
  <Elicitation label="Fazer o commit final no Git" query="Preenchi todos os arquivos md! Vou rodar git add ., git commit e git push para atualizar o GitHub."/>
  <Elicitation label="Gerar a build estática do MkDocs" query="Como faço para gerar os arquivos estáticos HTML do MkDocs com o comando mkdocs build?"/>
</ElicitationsGroup>