# Heurísticas de Análise de Projeto (Fase 1)

Objetivo: identificar stack e arquitetura **sem assumir uma linguagem específica** — use sinais textuais/estruturais que existem na maioria dos ecossistemas de backend.

## 1. Detecção de linguagem

| Sinal | Linguagem |
|---|---|
| Arquivos `*.py`, presença de `requirements.txt` / `pyproject.toml` / `Pipfile` | Python |
| Arquivos `*.js`/`*.ts`, presença de `package.json` | Node.js / TypeScript |
| Arquivos `*.rb`, `Gemfile` | Ruby |
| Arquivos `*.go`, `go.mod` | Go |
| Arquivos `*.java`, `pom.xml`/`build.gradle` | Java |

Regra geral: conte a extensão predominante entre os arquivos-fonte (excluindo dependências instaladas) e cruze com o manifest de pacotes presente na raiz do projeto.

## 2. Detecção de framework

Leia o manifest de dependências (o que existir):

- **Python**: `requirements.txt` / `pyproject.toml`. `flask` → Flask (a versão pode ser lida do pin `flask==X.Y.Z`); `django` → Django; `fastapi` → FastAPI.
- **Node.js**: `package.json` → campo `dependencies`. `express` → Express; `fastify` → Fastify; `koa` → Koa.

Se a versão não estiver pinada no manifest, não invente — reporte a dependência sem versão ou "não especificada".

Também confirme por import/require no código-fonte (ex.: `from flask import Flask`, `require('express')`) — o manifest pode estar desatualizado em relação ao código real.

## 3. Detecção de banco de dados

Procure por:
- Imports/requires de driver: `sqlite3`, `psycopg2`/`psycopg`, `pymongo`, `mysql-connector`, `sequelize`, `mongoose`, `sqlite3` (npm), `flask_sqlalchemy`.
- Comandos `CREATE TABLE` / definições de schema (classes `db.Model`, `Schema(...)`, migrations).
- String de conexão (`sqlite:///`, `postgres://`, `mongodb://`) em configuração ou código.

Liste as tabelas/coleções encontradas a partir dos `CREATE TABLE` (SQL cru) ou das classes de model (ORM) — o nome da classe/tabela geralmente indica a entidade de domínio.

## 4. Inferência de domínio de negócio

Não peça ao usuário — infira a partir de:
- Nomes das rotas/endpoints (ex.: `/produtos`, `/pedidos`, `/checkout`, `/tasks`, `/courses`).
- Nomes das tabelas/models (ex.: `produtos`, `usuarios`, `pedidos` → e-commerce; `courses`, `enrollments`, `payments` → LMS/cursos; `tasks`, `categories` → gestão de tarefas).
- Texto de mensagens de boas-vindas/README do projeto, se existir.

Descreva o domínio em uma frase curta e concreta (ex.: "E-commerce API (produtos, pedidos, usuários)", não apenas "API REST").

## 5. Mapeamento da arquitetura atual

Classifique como um dos dois perfis (ou um intermediário, descrevendo o que falta):

- **Monolítica em poucos arquivos**: toda a lógica (rotas + regras de negócio + acesso a dados) concentrada em ≤4-5 arquivos na raiz, sem pastas dedicadas por camada.
- **Parcialmente em camadas**: já existem pastas como `models/`, `routes/`, `services/`, `controllers/`, `utils/`, mas isso não garante que a separação de responsabilidades dentro de cada arquivo esteja correta — a Fase 2 ainda deve auditar o conteúdo de cada camada.

Descreva a arquitetura em uma linha (ex.: "Monolítica — tudo em 4 arquivos, sem separação de camadas" ou "Parcialmente organizada — models/routes/services existem, mas routes contêm lógica de negócio e queries N+1").

## 6. Contagem de arquivos e linhas

- Conte apenas arquivos-fonte do projeto (ignore dependências instaladas, bancos de dados binários, lockfiles, artefatos de build, e a própria pasta da skill `.claude/skills/refactor-arch/`).
- Estime linhas de código somando as linhas de cada arquivo-fonte contado.

## 7. Saída da Fase 1

Preencha o template definido em `SKILL.md` com os valores encontrados nos passos acima. Não avalie qualidade nesta fase — isso é trabalho da Fase 2.
