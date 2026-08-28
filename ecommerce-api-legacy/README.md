# ecommerce-api-legacy

LMS API (com fluxo de checkout) em Node.js/Express usada como entrada do desafio `refactor-arch`.

## Como rodar

```bash
npm install
npm start
```

A aplicacao sobe em `http://localhost:3000`. O banco SQLite e em memoria e ja carrega seeds automaticamente no boot.

## Configuracao

Copie `.env.example` para `.env` e ajuste os valores. As variaveis mais importantes:

| Variavel              | Descricao                                      | Default                     |
|-----------------------|------------------------------------------------|-----------------------------|
| `ADMIN_TOKEN`         | Token exigido nos endpoints admin via header `X-Admin-Token` | `change-me-in-production`   |
| `PORT`                | Porta HTTP                                     | `3000`                      |
| `DB_PATH`             | Caminho do banco SQLite (`:memory:` para dev)  | `:memory:`                  |
| `PAYMENT_GATEWAY_KEY` | Chave do gateway de pagamento                  | (vazio)                     |
| `BCRYPT_ROUNDS`       | Rounds do bcrypt para hash de senha            | `10`                        |
| `LOG_LEVEL`           | Nivel de log (`debug`, `info`, `warn`, `error`)| `info`                      |

## Endpoints

### POST /api/checkout
Realiza checkout: cria usuario (se nao existir), processa pagamento, cria matricula.

Corpo (JSON):
```json
{
  "usr": "Nome",
  "eml": "email@example.com",
  "pwd": "senha",
  "c_id": 1,
  "card": "4111222233334444"
}
```
Cartoes que comecam com `4` sao aprovados (mock).

### GET /api/admin/financial-report
Retorna receita por curso e lista de alunos. **Requer header `X-Admin-Token`**.

### DELETE /api/users/:id
Remove usuario e cascateia exclusao de matriculas e pagamentos. **Requer header `X-Admin-Token`**.

## Decisao de autenticacao admin

Este projeto nao possui sistema de login/JWT. A protecao dos endpoints administrativos usa um token estatico configurado via variavel de ambiente `ADMIN_TOKEN`, enviado no header `X-Admin-Token`. Esta abordagem e adequada para um ambiente de desenvolvimento/desafio; em producao, substitua por autenticacao baseada em JWT ou OAuth.

## Exemplos de requisicoes

Veja `api.http` para exemplos completos com e sem token de admin.
