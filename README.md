# Desafio — Skill de Auditoria e Refatoração Arquitetural

Entrega do desafio "Criação de Skills — Refatoração Arquitetural Automatizada" (MBA Engenharia de IA, Full Cycle), baseado em [devfullcycle/mba-ia-refactor-projects-skill](https://github.com/devfullcycle/mba-ia-refactor-projects-skill).

A skill `refactor-arch` (Claude Code, `.claude/skills/refactor-arch/`) analisa uma codebase, audita anti-patterns com severidade e arquivo:linha exatos, gera relatório e refatora para MVC — agnóstica de tecnologia. Construída em `code-smells-project/` e copiada sem alterações para `ecommerce-api-legacy/` e `task-manager-api/`.

## Estrutura

```
.
├── code-smells-project/     # Projeto 1 — Python/Flask (E-commerce API)
├── ecommerce-api-legacy/    # Projeto 2 — Node.js/Express (LMS + checkout)
├── task-manager-api/        # Projeto 3 — Python/Flask (Task Manager, parcialmente organizado)
└── reports/                 # audit-project-{1,2,3}.md
```

Cada projeto tem sua própria cópia de `.claude/skills/refactor-arch/`.

---

## A) Análise Manual

Lista completa em `reports/audit-project-{1,2,3}.md`; abaixo os destaques por severidade.

### Projeto 1 — code-smells-project

| Sev. | Problema | Relevância |
|---|---|---|
| CRITICAL | SQL Injection em `models.py` (concatenação de string); em `login_usuario` (`:109-111`) permite bypass de autenticação | Controle total do banco / login sem senha |
| CRITICAL | `SECRET_KEY` hardcoded (`app.py:7`) e vazada via `/health` (`controllers.py:289`) | Chave de sessão exposta publicamente |
| CRITICAL | `POST /admin/query` executa SQL arbitrário sem auth (`app.py:59-78`) | Acesso total e não autenticado ao banco |
| MEDIUM | N+1 ao montar pedidos (`models.py:171-233`) | Não escala com volume de dados |
| MEDIUM | `try/except` duplicado em ~16 funções (`controllers.py`) | Formato de erro precisa mudar em 16 lugares |
| LOW | Magic numbers de desconto/validação (`models.py:257-262`) | Regra de negócio difícil de entender/alterar |
| LOW | Lista de categorias hardcoded inline (`controllers.py:52`) | Tende a divergir se duplicada |

*Total: 19 findings (8 CRITICAL / 4 HIGH / 4 MEDIUM / 3 LOW).*

### Projeto 2 — ecommerce-api-legacy

| Sev. | Problema | Relevância |
|---|---|---|
| CRITICAL | God Class `AppManager` — DB + rotas + lógica de negócio no mesmo arquivo (`src/AppManager.js:4-142`) | Impossível testar/evoluir uma parte isolada |
| CRITICAL | "Hash" de senha falso, `badCrypto()` (`src/utils.js:17-23`) | Não protege senha nenhuma |
| CRITICAL | `GET /api/admin/financial-report` sem auth expõe receita + PII (`:80-129`) | Vazamento de dados financeiros/pessoais |
| HIGH | Estado global mutável `globalCache`/`totalRevenue` (`src/utils.js:9-10`) | Comportamento não determinístico sob concorrência |
| MEDIUM | Pirâmide de callbacks N+1 no relatório financeiro (`:83-127`) | Frágil, degrada com volume |
| MEDIUM | `DELETE /users/:id` não cascateia `enrollments`/`payments` (`:131-137`) | Dados órfãos no banco |
| LOW | Variáveis de uma letra no checkout (`:29-33`) | Legibilidade |

*Total: 15 findings (5 CRITICAL / 4 HIGH / 3 MEDIUM / 3 LOW). Sem SQL Injection — já usa queries parametrizadas.*

### Projeto 3 — task-manager-api

| Sev. | Problema | Relevância |
|---|---|---|
| CRITICAL | Hash de senha com MD5 (`models/user.py:27-32`) | Quebrado para senhas — rainbow tables |
| CRITICAL | Token de login previsível e **nenhuma rota valida token** | Controle de acesso inexistente na prática |
| MEDIUM | API deprecated — `datetime.utcnow()` (dezenas de usos, deprecated desde Python 3.12) | Quebra em versão futura da linguagem |
| MEDIUM | Lógica de "atrasado" duplicada em 5 arquivos em vez de usar `Task.is_overdue()` | Já divergiu entre cópias |
| MEDIUM | `marshmallow` listada mas não usada; validação manual duplicada | Validação inconsistente entre rotas |
| LOW | Imports não usados | Ausência de lint |
| LOW | `utils/helpers.py` inteiro não é importado por nenhuma rota | Código morto, causa raiz da duplicação acima |

*Total: 15 findings (4 CRITICAL / 3 HIGH / 5 MEDIUM / 3 LOW). Único com achado real de API deprecated.*

---

## B) Construção da Skill

`SKILL.md` orquestra as 3 fases e referencia 5 arquivos em `references/`:

- **`project-analysis.md`** — heurísticas de detecção (linguagem/framework/DB/domínio/arquitetura) por sinais textuais, sem depender de uma linguagem específica.
- **`anti-patterns-catalog.md`** — 14 anti-patterns (mín. 8), severidade fixa conforme enunciado, inclui detecção de APIs deprecated.
- **`report-template.md`** — formato fixo, ordenação por severidade, `arquivo:linha` obrigatório.
- **`architecture-guidelines.md`** — camadas MVC alvo + regra de adaptação (mover/corrigir estrutura já existente em vez de recriar).
- **`refactoring-playbook.md`** — 12 padrões antes/depois (mín. 8).

**Anti-patterns escolhidos**: derivados diretamente da análise manual (seção A) — hardcoded credentials/SQLi (projeto 1), God Class/crypto quebrada (1 e 2), estado global (2), API deprecated (3), N+1/duplicação (todos). Severidade idêntica à do enunciado, para relatórios comparáveis entre projetos.

**Agnosticismo de tecnologia**: heurísticas e sinais de detecção são estruturais ("string concatenada em query", "classe fazendo DB+rotas+lógica"), não sintaxe de uma linguagem. Prova: a mesma pasta, sem alteração, gerou auditorias completas em Node e nos dois Flask — inclusive reconhecendo corretamente que o projeto 2 não tem SQLi, sem forçar falso positivo.

**Desafios**:
- Evitar falso positivo de "API deprecated" nos projetos 1/2 (a skill documenta explicitamente quando não encontra nada, em vez de inventar).
- Projeto 3 já tinha `models/`/`routes/`/`services/`/`utils/` — a Fase 3 precisou de uma regra de adaptação explícita para mover/corrigir em vez de recriar.
- A pausa da Fase 2 precisou ser reforçada em maiúsculas no `SKILL.md` para não ser pulada por um agente "ansioso por terminar".
- Rate limit no subagente usado na Fase 3 (paralelo, nos 3 projetos): o trabalho parcial de cada um foi revisado e finalizado manualmente, sempre com validação de boot + endpoints antes de aceitar o resultado.

---

## C) Resultados

| Projeto | Stack | Arquivos | CRITICAL | HIGH | MEDIUM | LOW | Total |
|---|---|---|---|---|---|---|---|
| 1 — code-smells-project | Python/Flask | 4 (~784 LOC) | 8 | 4 | 4 | 3 | 19 |
| 2 — ecommerce-api-legacy | Node/Express | 3 (~182 LOC) | 5 | 4 | 3 | 3 | 15 |
| 3 — task-manager-api | Python/Flask | 15 (~1163 LOC) | 4 | 3 | 5 | 3 | 15 |

### Antes → Depois

- **Projeto 1**: `app.py`+`controllers.py`(293L)+`models.py`(315L) → `config/`, `models/`, `controllers/`, `routes/`, `middlewares/` por domínio (produto/usuario/pedido/admin).
- **Projeto 2**: `AppManager.js`(142L, God Class) + `utils.js` → `config/`, `models/`, `controllers/`, `routes/`, `services/`, `middlewares/`, `lib/`.
- **Projeto 3** (adaptado, não recriado): `routes/` com lógica pesada e sem auth → `config/` e `controllers/` novos, `routes/` finas, `schemas/` (marshmallow), `middlewares/auth.py` (JWT real).

### Checklist de validação (3/3 projetos)

**Fase 1**: linguagem, framework, domínio e nº de arquivos detectados corretamente.
**Fase 2**: relatório no template, `arquivo:linha` exato, ordenado por severidade, ≥5 findings, detecção de deprecated incluída, pausa antes da Fase 3.
**Fase 3**: estrutura MVC, config sem hardcoded (`.env.example`), models/routes/controllers separados, error handling centralizado, entry point claro, app sobe sem erro, endpoints originais respondem.

Todos os itens ✅ nos 3 projetos.

### Evidência (boot + curl reais)

```
# Projeto 1 (:5001)                                # Projeto 2 (:3000)
POST /login (correto)        → 200                 POST /api/checkout (cartão 4...) → 200
POST /login (SQLi payload)   → 401 (antes: 200)     POST /api/checkout (cartão 5...) → 400 recusado
POST /admin/query            → 404 (removido)       GET /admin/financial-report sem token → 401
POST /admin/reset-db s/token → 403                  DELETE /users/1 com token → 200, cascade ok
GET /health                  → sem secret_key/debug

# Projeto 3 (:5002)
python seed.py           → zero DeprecationWarning
POST /login               → 200, JWT real (antes: token fake previsível)
POST /tasks sem token      → 401
POST /tasks com token      → 201
POST /tasks título curto   → 400 (validação marshmallow)
GET /reports/summary       → 200, sem N+1
```

### Observações entre stacks

A mesma skill, sem alteração, criou MVC do zero nos projetos 1/2 e adaptou a estrutura já existente no projeto 3. Não forçou achados inexistentes (SQLi ausente no 2, deprecated só real no 3) — sinais de detecção são estruturais, não amarrados a uma linguagem.

---

## D) Como Executar

**Pré-requisitos**: [Claude Code](https://docs.anthropic.com/en/docs/claude-code) instalado; Python 3.11+ (projetos 1 e 3); Node.js 18+ (projeto 2).

```bash
cd code-smells-project && claude "/refactor-arch"       # Fase 2 pergunta y/n antes de refatorar
cd ../ecommerce-api-legacy && claude "/refactor-arch"    # skill já copiada
cd ../task-manager-api && claude "/refactor-arch"        # skill já copiada
```

O código já está refatorado e os relatórios já commitados (resultado desta execução). Rodar de novo re-audita o código já corrigido.

**Validar manualmente:**

```bash
# Projeto 1
cd code-smells-project && python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
.venv/bin/python app.py   # :5000
curl localhost:5000/health && curl localhost:5000/produtos

# Projeto 2
cd ecommerce-api-legacy && npm install && npm start   # :3000
curl -X POST localhost:3000/api/checkout -H "Content-Type: application/json" \
  -d '{"usr":"Teste","eml":"t@t.com","pwd":"123456","c_id":2,"card":"4111222233334444"}'

# Projeto 3
cd task-manager-api && python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
.venv/bin/python seed.py && .venv/bin/python app.py   # :5000
curl localhost:5000/tasks
```

Copie `.env.example` para `.env` em qualquer ambiente fora de local/dev.
