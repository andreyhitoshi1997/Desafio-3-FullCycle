# Desafio — Skill de Auditoria e Refatoração Arquitetural

Este repositório é a entrega do desafio "Criação de Skills — Refatoração Arquitetural Automatizada" do MBA em Engenharia de IA (Full Cycle), baseado em [devfullcycle/mba-ia-refactor-projects-skill](https://github.com/devfullcycle/mba-ia-refactor-projects-skill).

A skill `refactor-arch` (Claude Code, `.claude/skills/refactor-arch/`) analisa uma codebase, audita anti-patterns de arquitetura/segurança com severidade e arquivo:linha exatos, gera um relatório estruturado e refatora o projeto para o padrão MVC — de forma agnóstica de tecnologia. Ela foi construída em `code-smells-project/` e copiada, sem alterações, para `ecommerce-api-legacy/` e `task-manager-api/`.

## Estrutura do repositório

```
.
├── code-smells-project/     # Projeto 1 — Python/Flask (E-commerce API)
├── ecommerce-api-legacy/    # Projeto 2 — Node.js/Express (LMS API com checkout)
├── task-manager-api/        # Projeto 3 — Python/Flask (Task Manager, já parcialmente organizado)
└── reports/                 # Relatórios de auditoria (saída da Fase 2 da skill)
    ├── audit-project-1.md
    ├── audit-project-2.md
    └── audit-project-3.md
```

Cada projeto contém sua própria cópia de `.claude/skills/refactor-arch/`.

---

## A) Análise Manual

Análise feita lendo o código dos 3 projetos antes de escrever a skill, para entender concretamente quais padrões ela precisaria detectar. A lista completa (com todos os findings, não só os destacados aqui) está em `reports/audit-project-{1,2,3}.md` — a auditoria automatizada da skill encontrou os mesmos problemas listados abaixo, além de outros.

### Projeto 1 — code-smells-project (Python/Flask, E-commerce API)

| Severidade | Problema | Por que é relevante |
|---|---|---|
| CRITICAL | SQL Injection generalizada — toda query em `models.py` é montada por concatenação de string (ex.: `models.py:28`, `:48-50`, `:109-111`) | Um atacante controla parte da query; em `login_usuario` (`models.py:109-111`) isso permite **bypass completo de autenticação** só com o payload de login. |
| CRITICAL | `SECRET_KEY` hardcoded (`app.py:7`) e devolvida em texto puro pelo endpoint público `/health` (`controllers.py:289`) | Qualquer cliente não autenticado obtém a chave de sessão da aplicação em produção. |
| CRITICAL | Endpoint `POST /admin/query` executa SQL arbitrário do corpo da requisição sem autenticação (`app.py:59-78`) | Equivale a dar acesso total e não autenticado ao banco de dados a qualquer visitante da API. |
| MEDIUM | Query N+1 ao montar pedidos (`models.py:171-233`) — uma query por item, dentro de um loop por pedido | Degrada performance proporcionalmente ao volume de pedidos; não escala. |
| MEDIUM | Bloco `try/except` idêntico duplicado em ~16 funções de `controllers.py` | Qualquer mudança no formato de erro precisa ser replicada manualmente em 16 lugares. |
| LOW | Magic numbers para faixas de desconto e limites de validação (`models.py:257-262`, `controllers.py:47-50`) | Valores sem nome tornam a regra de negócio difícil de entender e alterar com segurança. |
| LOW | Lista de categorias válidas hardcoded inline em vez de constante compartilhada (`controllers.py:52`) | Se outra função precisar validar categoria, a lista tende a ser duplicada e divergir. |

*(Relatório completo: 8 CRITICAL / 4 HIGH / 4 MEDIUM / 3 LOW — 19 findings, ver `reports/audit-project-1.md`.)*

### Projeto 2 — ecommerce-api-legacy (Node.js/Express, LMS com checkout)

| Severidade | Problema | Por que é relevante |
|---|---|---|
| CRITICAL | God Class `AppManager` (`src/AppManager.js:4-142`) concentra conexão de banco, schema, roteamento **e** toda a lógica de checkout/relatório financeiro | Impossível testar ou evoluir uma parte sem risco de quebrar as outras; nenhuma fronteira de responsabilidade. |
| CRITICAL | "Hash" de senha falso — `badCrypto()` (`src/utils.js:17-23`) não é um algoritmo criptográfico real | Não protege a senha de forma nenhuma; qualquer vazamento do banco expõe efetivamente as senhas. |
| CRITICAL | `GET /api/admin/financial-report` sem autenticação expõe receita por curso e dados pessoais de alunos (`AppManager.js:80-129`) | Vazamento de dados financeiros e PII para qualquer requisição não autenticada. |
| HIGH | Estado global mutável — `globalCache`/`totalRevenue` no escopo do módulo (`src/utils.js:9-10`), mutado a cada checkout | Estado compartilhado entre requisições concorrentes gera comportamento não determinístico. |
| MEDIUM | Pirâmide de callbacks com N+1 aninhado em 3 níveis no relatório financeiro (`AppManager.js:83-127`), com contadores manuais de "pending" | Frágil e difícil de manter; degrada com o volume de dados. |
| LOW | Nomenclatura de variável de uma letra no checkout (`u`, `e`, `p`, `cid`, `cc` — `AppManager.js:29-33`) | Reduz legibilidade e aumenta risco de troca acidental de variável. |
| LOW | `totalRevenue` declarado/exportado mas nunca usado em lugar nenhum (`src/utils.js:10,25`) | Código morto — sugere integração abandonada pela metade. |

*(Relatório completo: 5 CRITICAL / 4 HIGH / 3 MEDIUM / 3 LOW — 15 findings, ver `reports/audit-project-2.md`. Diferente do projeto 1, aqui as queries já são parametrizadas — não há SQL Injection.)*

### Projeto 3 — task-manager-api (Python/Flask, Task Manager, parcialmente organizado)

| Severidade | Problema | Por que é relevante |
|---|---|---|
| CRITICAL | Hash de senha com MD5 (`models/user.py:27-32`) | MD5 é criptograficamente quebrado para senhas — vulnerável a rainbow tables. |
| CRITICAL | Token de login previsível (`fake-jwt-token-<id>`) **e nenhuma rota valida token nenhum** (`routes/user_routes.py:210` + ausência total de checagem em `task_routes.py`/`user_routes.py`/`report_routes.py`) | Controle de acesso inexistente na prática — login existe, mas nada depende dele. |
| MEDIUM | Uso de API deprecated — `datetime.utcnow()` chamado dezenas de vezes (deprecated desde Python 3.12) | Funciona hoje com aviso de depreciação; quebra quando a API for removida em versão futura. |
| MEDIUM | Duplicação da lógica de "atrasado" em 5 arquivos diferentes, em vez de reusar `Task.is_overdue()` que já existe no model | Correções precisam ser replicadas manualmente; já divergiu (cada cópia chama `datetime.utcnow()` direto). |
| MEDIUM | `marshmallow` está em `requirements.txt` mas nenhuma rota a usa — validação manual duplicada, inclusive reimplementando constantes já definidas em `utils/helpers.py` | Sinal de dependência planejada e nunca finalizada; validação inconsistente entre rotas. |
| LOW | Imports não utilizados (`routes/task_routes.py:7`; `utils/helpers.py:2-7`) | Ruído, sugere ausência de lint no projeto. |
| LOW | `utils/helpers.py` inteiro (constantes e funções) não é importado por nenhuma rota | Módulo de utilitários é código morto — e sua não-utilização é a causa raiz dos MEDIUM de duplicação/validação acima. |

*(Relatório completo: 4 CRITICAL / 3 HIGH / 5 MEDIUM / 3 LOW — 15 findings, ver `reports/audit-project-3.md`. Este é o único dos 3 projetos com um achado real de API deprecated.)*

---

## B) Construção da Skill

### Decisões de design

A skill segue as 3 fases exigidas pelo desafio, implementadas em `code-smells-project/.claude/skills/refactor-arch/SKILL.md`, que funciona como o "prompt" orquestrador — ele nunca embute conhecimento de domínio diretamente, apenas referencia 5 arquivos Markdown em `references/`:

- `project-analysis.md` — heurísticas de detecção de linguagem/framework/DB/domínio/arquitetura, baseadas em sinais textuais (extensão de arquivo, manifest de dependências, imports, `CREATE TABLE`/classes de model) em vez de parsing específico de uma linguagem.
- `anti-patterns-catalog.md` — **14 anti-patterns** (acima do mínimo de 8), com severidade fixa por definição do desafio e sinais de detecção concretos e acionáveis (ex.: "concatenação de string formando SQL", não "código inseguro"). Inclui a entrada 11, dedicada a **detecção de APIs deprecated**, com exemplos concretos por linguagem (`datetime.utcnow()` em Python, `new Buffer()` em Node).
- `report-template.md` — formato fixo do relatório (idêntico ao exemplo do enunciado), com regra explícita de ordenação por severidade e exigência de `arquivo:linha` em todo finding.
- `architecture-guidelines.md` — regras da estrutura MVC alvo por camada (Models/Views-Routes/Controllers/Config/Middlewares/entry point) **e uma regra de adaptação explícita**: se o projeto já tem parte da estrutura (caso do projeto 3), mover/corrigir em vez de recriar do zero.
- `refactoring-playbook.md` — **12 padrões de transformação** (acima do mínimo de 8) com exemplo de código antes/depois para cada anti-pattern do catálogo.

### Anti-patterns incluídos e por quê

O catálogo foi construído a partir da análise manual dos 3 projetos (seção A), não de uma lista genérica — cada entrada corresponde a um problema real encontrado em pelo menos um dos projetos-alvo: hardcoded credentials e SQL Injection (projeto 1), God Class e criptografia quebrada (projetos 1 e 2), estado global mutável (projeto 2), APIs deprecated (projeto 3), N+1 e duplicação de código (todos). A escala de severidade usada é exatamente a definida no enunciado do desafio (CRITICAL/HIGH/MEDIUM/LOW com os mesmos critérios), para que o relatório gerado seja diretamente comparável entre os 3 projetos.

### Como garantimos que a skill é agnóstica de tecnologia

- Nenhuma heurística de `project-analysis.md` depende de uma linguagem específica — todas são "se existe sinal X, então Y", cobrindo Python e Node.js explicitamente e generalizáveis a outras stacks (Ruby, Go, Java) sem alterar o arquivo.
- O catálogo de anti-patterns descreve sinais estruturais (concatenação de string em query, classe fazendo DB+rotas+lógica, variável mutável em escopo de módulo) que existem em qualquer linguagem imperativa de backend, não sintaxe de uma linguagem só.
- A prova concreta: a mesma pasta `.claude/skills/refactor-arch/`, **sem nenhuma alteração**, foi copiada para `ecommerce-api-legacy/` (Node/Express) e `task-manager-api/` (Flask, mas já parcialmente organizado) e produziu relatórios de auditoria (`reports/audit-project-2.md`, `reports/audit-project-3.md`) tão completos quanto o do projeto 1 — inclusive reconhecendo corretamente que o projeto 2 **não tem** SQL Injection (porque já usa queries parametrizadas) em vez de forçar um falso positivo.

### Desafios encontrados

- **Evitar falsos positivos ao reusar o mesmo catálogo em 3 stacks diferentes**: o risco de uma skill "genérica" é forçar um achado onde não existe (ex.: reportar "API deprecated" mesmo sem uma ocorrência real). A skill foi instruída a não inventar findings sem sinal concreto — por isso os relatórios dos projetos 1 e 2 documentam explicitamente que nenhuma API deprecated foi encontrada neles, e apontam para o projeto 3 como o caso real.
- **Adaptar a Fase 3 ao nível de organização existente**: o projeto 3 já tem `models/`/`routes/`/`services/`/`utils/`, então a mesma transformação "criar estrutura MVC do zero" usada nos projetos 1 e 2 seria errada — a `architecture-guidelines.md` precisou de uma seção explícita de "regra de adaptação" para instruir mover/corrigir em vez de recriar.
- **Manter a Fase 2 pausando de verdade**: como a skill roda dentro de uma sessão do Claude Code operada por um agente, foi necessário deixar explícito no `SKILL.md`, em letras maiúsculas, que a Fase 3 nunca pode iniciar sem uma resposta afirmativa explícita à pergunta de confirmação — sem isso, um agente ansioso por "terminar a tarefa" tenderia a pular a pausa.
- **Rate limit em execução paralela**: a Fase 3 dos 3 projetos foi disparada em paralelo via subagentes; dois deles (projetos 1 e 2) terminaram a refatoração e ficaram só validando o boot quando a sessão bateu o limite de uso do modelo usado pelos subagentes. O trabalho parcial de cada um foi revisado arquivo a arquivo, validado (venv/npm install + boot + `curl` nos endpoints) e finalizado manualmente na mesma sessão; o projeto 3 (que ainda não tinha sido iniciado pelo subagente) foi refatorado inteiramente dessa forma. Nenhum dos três teve o resultado aceito sem essa validação ponta a ponta.

---

## C) Resultados

### Resumo das auditorias (Fase 2)

| Projeto | Stack | Arquivos | CRITICAL | HIGH | MEDIUM | LOW | Total |
|---|---|---|---|---|---|---|---|
| 1 — code-smells-project | Python/Flask | 4 (~784 LOC) | 8 | 4 | 4 | 3 | 19 |
| 2 — ecommerce-api-legacy | Node/Express | 3 (~182 LOC) | 5 | 4 | 3 | 3 | 15 |
| 3 — task-manager-api | Python/Flask | 15 (~1163 LOC) | 4 | 3 | 5 | 3 | 15 |

Relatórios completos: `reports/audit-project-1.md`, `reports/audit-project-2.md`, `reports/audit-project-3.md`.

### Antes / depois — estrutura de diretórios

**Projeto 1 — code-smells-project**
```
Antes                          Depois
app.py                         app.py                    (composition root)
controllers.py  (293 LOC,      config/{settings,constants}.py
  4 domínios)                  models/{produto,usuario,pedido}_model.py
models.py       (315 LOC,      controllers/{produto,usuario,pedido,admin}_controller.py
  4 domínios, SQL cru)         routes/{produto,usuario,pedido,admin}_routes.py
database.py                    middlewares/{error_handler,auth}.py
                                database.py
                                .env.example
```

**Projeto 2 — ecommerce-api-legacy**
```
Antes                          Depois
src/app.js                     src/app.js                 (composition root)
src/AppManager.js (142 LOC,    src/config/settings.js
  God Class: DB+rotas+lógica)  src/models/{course,user,enrollment,payment,auditLog}Model.js
src/utils.js (secrets,         src/controllers/{checkout,financialReport,user}Controller.js
  badCrypto, estado global)    src/routes/{checkout,admin,user}Routes.js
                                src/services/paymentService.js
                                src/middlewares/{adminAuth,errorHandler}.js
                                src/lib/{database,seed,logger}.js
                                .env.example
```

**Projeto 3 — task-manager-api** (adaptado, não recriado — já tinha `models/`, `routes/`, `services/`, `utils/`)
```
Antes                          Depois
app.py                         app.py                     (composition root, agora lê config/)
models/{task,user,category}.py models/{task,user,category}.py  (MD5→hash real, datetime fixo)
routes/{task,user,report}_     config/settings.py          (novo)
  routes.py (lógica pesada,    controllers/{task,user,report,category}_controller.py (novo)
  duplicação, sem auth)        routes/{task,user,report,category}_routes.py (agora finas)
services/notification_         schemas/{task,user}_schema.py (novo, marshmallow)
  service.py (SMTP hardcoded)  middlewares/{auth,error_handler}.py (novo)
utils/helpers.py (morto)       services/notification_service.py (config via env)
                                utils/helpers.py (agora usado de verdade)
                                .env.example
```

### Checklist de validação

**Fase 1 — Análise** (3/3 projetos)
- [x] Linguagem detectada corretamente (Python nos projetos 1 e 3, JavaScript/Node no projeto 2)
- [x] Framework detectado corretamente (Flask 3.1.1, Express ^4.18.2, Flask 3.0.0+SQLAlchemy)
- [x] Domínio da aplicação descrito corretamente (E-commerce, LMS/checkout, Task Manager)
- [x] Número de arquivos analisados condiz com a realidade (4, 3, 15)

**Fase 2 — Auditoria** (3/3 projetos)
- [x] Relatório segue o template de `report-template.md`
- [x] Cada finding tem arquivo e linhas exatos
- [x] Findings ordenados por severidade (CRITICAL → LOW)
- [x] Mínimo de 5 findings identificados (19 / 15 / 15)
- [x] Detecção de API deprecated incluída — achado real no projeto 3 (`datetime.utcnow()`); projetos 1 e 2 auditados e sem ocorrência (documentado explicitamente nos relatórios, sem falso positivo)
- [x] Skill pausou e pediu confirmação antes da Fase 3 nos 3 projetos

**Fase 3 — Refatoração** (3/3 projetos)
- [x] Estrutura de diretórios segue padrão MVC
- [x] Configuração extraída para módulo de config, sem hardcoded (`.env.example` nos 3)
- [x] Models criados/corrigidos para abstrair dados
- [x] Views/Routes separadas para roteamento
- [x] Controllers concentram o fluxo da aplicação
- [x] Error handling centralizado (`@app.errorhandler` / Express `errorHandler` middleware)
- [x] Entry point claro (`app.py` / `src/app.js` como composition root)
- [x] Aplicação inicia sem erros (validado em venv/npm install limpos)
- [x] Endpoints originais respondem corretamente (validado com `curl`)

### Logs reais (boot + validação)

**Projeto 1**
```
$ PORT=5001 .venv/bin/python app.py
SECRET_KEY using default dev value — set SECRET_KEY env var for production
2026-08-28 16:02:31 [INFO] database: Seed data loaded: 10 products, 3 users
2026-08-28 16:02:31 [INFO] __main__: SERVIDOR INICIADO — Rodando em http://localhost:5001

$ curl -X POST /login -d '{"email":"admin@loja.com","senha":"admin123"}'   → 200 Login OK
$ curl -X POST /login -d '{"email":"admin@loja.com'"'"' -- ","senha":"x"}' → 401 (bypass de SQLi corrigido, antes autenticava)
$ curl -X POST /admin/query                                                → 404 (endpoint removido)
$ curl -X POST /admin/reset-db                                             → 403 sem X-Admin-Token
$ curl /health                                                             → sem secret_key/debug no corpo (antes vazava)
```

**Projeto 2**
```
$ node src/app.js
Frankenstein LMS started {"port":3000}

$ curl -X POST /api/checkout (cartão 4111...)     → 200 {"msg":"Sucesso","enrollment_id":3}
$ curl -X POST /api/checkout (cartão 5111...)     → 400 "Pagamento recusado"
$ curl GET /api/admin/financial-report            → 401 sem X-Admin-Token, 200 com token correto
$ curl DELETE /api/users/1 (com token)             → 200 {"message":"User deleted","cascaded":{"enrollments":0,"payments":0}}
```

**Projeto 3**
```
$ .venv/bin/python seed.py
Seed concluído com sucesso!  3 usuários / 4 categorias / 10 tasks   (zero DeprecationWarning)

$ PORT=5002 .venv/bin/python app.py
SERVIDOR INICIADO — Rodando em http://localhost:5002

$ curl -X POST /login -d '{"email":"joao@email.com","password":"1234"}'
  → 200, token JWT real (eyJhbGciOiJIUzI1NiIs...), sem "password" no corpo
$ curl -X POST /tasks (sem Authorization)          → 401 "Token de autenticação ausente"
$ curl -X POST /tasks (com Bearer token)           → 201
$ curl -X POST /tasks -d '{"title":"a"}' (token ok) → 400, validação marshmallow ("Length must be between 3 and 200")
$ curl /reports/summary                            → 200, sem N+1 (grouping em memória de 1 query)
```

### Observações — comportamento da skill em stacks diferentes

- A mesma skill, **sem alteração**, funcionou nos 2 monólitos (projetos 1 e 2, Python e Node) e no projeto parcialmente organizado (projeto 3) — nos dois primeiros ela criou a estrutura MVC do zero; no terceiro, seguiu a regra de adaptação e só moveu/corrigiu o que já existia, sem duplicar `models/`/`routes/`/`services/`/`utils/`.
- O catálogo não forçou falsos positivos: reconheceu corretamente que o projeto 2 já usava queries parametrizadas (sem SQL Injection) e que só o projeto 3 tinha uma API deprecated real.
- A profundidade dos findings variou com a stack — projeto 2 (Node/callback) gerou achados de "pirâmide de callbacks"/N+1 que não fazem sentido em Python, enquanto o `datetime.utcnow()` deprecated só existe no ecossistema Python — a skill não tentou aplicar sinais de uma stack a outra.

---

## D) Como Executar

### Pré-requisitos

- [Claude Code](https://docs.anthropic.com/en/docs/claude-code) instalado e autenticado (`claude` no PATH).
- Python 3.11+ e `pip` (projetos 1 e 3).
- Node.js 18+ e `npm` (projeto 2).

### Rodar a skill em cada projeto

```bash
# Projeto 1
cd code-smells-project
claude "/refactor-arch"
# Fase 1 imprime o resumo da stack; Fase 2 gera o relatório e pergunta
# "Proceed with refactoring (Phase 3)? [y/n]" — responda y para refatorar.

# Projeto 2 (a skill já está copiada em ecommerce-api-legacy/.claude/skills/refactor-arch/)
cd ../ecommerce-api-legacy
claude "/refactor-arch"

# Projeto 3 (a skill já está copiada em task-manager-api/.claude/skills/refactor-arch/)
cd ../task-manager-api
claude "/refactor-arch"
```

Os relatórios já commitados em `reports/` e o código já refatorado em cada projeto são o resultado real dessa execução (rodada nesta sessão); rodar o comando novamente re-audita o código já refatorado (a expectativa é um relatório com poucos ou nenhum finding CRITICAL/HIGH remanescente).

### Como validar manualmente que a refatoração funciona

**Projeto 1**
```bash
cd code-smells-project
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
.venv/bin/python app.py                       # sobe em :5000 (ou defina PORT=... no ambiente)
curl http://localhost:5000/health
curl http://localhost:5000/produtos
curl -X POST http://localhost:5000/login -H "Content-Type: application/json" \
  -d '{"email":"admin@loja.com","senha":"admin123"}'
```

**Projeto 2**
```bash
cd ecommerce-api-legacy
npm install
npm start                                     # sobe em :3000
curl -X POST http://localhost:3000/api/checkout -H "Content-Type: application/json" \
  -d '{"usr":"Teste","eml":"t@t.com","pwd":"123456","c_id":2,"card":"4111222233334444"}'
curl http://localhost:3000/api/admin/financial-report -H "X-Admin-Token: change-me-in-production"
```

**Projeto 3**
```bash
cd task-manager-api
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
.venv/bin/python seed.py
.venv/bin/python app.py                       # sobe em :5000 (ou defina PORT=... no ambiente)
curl http://localhost:5000/tasks
TOKEN=$(curl -s -X POST http://localhost:5000/login -H "Content-Type: application/json" \
  -d '{"email":"joao@email.com","password":"1234"}' | python3 -c "import sys,json;print(json.load(sys.stdin)['token'])")
curl -X POST http://localhost:5000/tasks -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" -d '{"title":"Nova tarefa"}'
```

Em todos os 3, copie `.env.example` para `.env` e ajuste os valores antes de rodar em qualquer ambiente que não seja local/dev.
