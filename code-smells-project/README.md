# code-smells-project

API de E-commerce em Python/Flask refatorada para arquitetura MVC.

## Estrutura

```
config/          Configuracao centralizada (env vars)
models/          Acesso a dados por dominio (produto, usuario, pedido)
controllers/     Orquestracao request/response
routes/          Blueprints de roteamento
middlewares/     Error handler centralizado, auth
database.py      Lifecycle do banco (init, schema, seed)
app.py           Composition root
```

## Como rodar

```bash
pip install -r requirements.txt
python app.py
```

A aplicacao sobe em `http://localhost:5000`.  
O banco SQLite (`loja.db`) e criado automaticamente no primeiro boot, com produtos e usuarios de exemplo.

## Configuracao

Copie `.env.example` para `.env` e ajuste os valores:

| Variavel      | Descricao                             | Default                             |
|---------------|---------------------------------------|-------------------------------------|
| SECRET_KEY    | Chave de assinatura de sessao         | dev-only-change-me-in-production    |
| DEBUG         | Habilita modo debug (true/false)      | false                               |
| CORS_ORIGINS  | Origens permitidas (separadas por ,)  | *                                   |
| ADMIN_TOKEN   | Token para endpoints admin            | dev-admin-token                     |
| DB_PATH       | Caminho do banco SQLite               | loja.db (na raiz do projeto)        |
| PORT          | Porta HTTP do servidor                | 5000                                |

## Endpoints admin protegidos

`POST /admin/reset-db` requer o header `X-Admin-Token` com o valor configurado em `ADMIN_TOKEN`.

```bash
curl -X POST http://localhost:5000/admin/reset-db \
  -H "X-Admin-Token: dev-admin-token"
```
