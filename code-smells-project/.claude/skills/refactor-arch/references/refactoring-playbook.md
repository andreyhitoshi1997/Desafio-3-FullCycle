# Playbook de Refatoração (Fase 3)

Um padrão de transformação por anti-pattern do catálogo. Os exemplos usam Python/Flask e Node/Express (as stacks dos 3 projetos-alvo), mas o princípio de cada transformação é agnóstico de linguagem.

---

## 1. Hardcoded Credentials → Config a partir de variáveis de ambiente

**Antes** (Python)
```python
app.config["SECRET_KEY"] = "minha-chave-super-secreta-123"
```

**Depois**
```python
# config/settings.py
import os

class Settings:
    SECRET_KEY = os.environ["SECRET_KEY"]
    DEBUG = os.environ.get("DEBUG", "false").lower() == "true"

# app.py
from config.settings import Settings
app.config.from_object(Settings)
```
Crie `.env.example` com `SECRET_KEY=change-me` (sem valor real) e adicione `.env` ao `.gitignore`.

---

## 2. SQL Injection → Query parametrizada

**Antes** (Python)
```python
cursor.execute("SELECT * FROM produtos WHERE id = " + str(id))
```

**Depois**
```python
cursor.execute("SELECT * FROM produtos WHERE id = ?", (id,))
```
Com ORM (SQLAlchemy), prefira sempre `Model.query.get(id)`/`filter_by(...)` a SQL cru.

---

## 3. God Class → Split por camada e por domínio

**Antes** (Node — um único arquivo com DB + rotas + regra de negócio)
```javascript
class AppManager {
  constructor() { this.db = new sqlite3.Database(':memory:'); }
  initDb() { /* schema */ }
  setupRoutes(app) {
    app.post('/api/checkout', (req, res) => { /* 50 linhas de lógica */ });
  }
}
```

**Depois**
```javascript
// models/courseModel.js — só acesso a dados de courses
// controllers/checkoutController.js — orquestra checkout usando os models
// routes/checkoutRoutes.js
router.post('/api/checkout', checkoutController.checkout);
// app.js — composition root
app.use('/api', checkoutRoutes);
```
Cada domínio (`courses`, `users`, `payments`) ganha seu próprio model e controller.

---

## 4. Autenticação Quebrada → Hash real + token assinado

**Antes** (Python)
```python
def check_password(self, pwd):
    return self.password == hashlib.md5(pwd.encode()).hexdigest()
...
'token': 'fake-jwt-token-' + str(user.id)
```

**Depois**
```python
from werkzeug.security import generate_password_hash, check_password_hash
import jwt, datetime

def set_password(self, pwd):
    self.password = generate_password_hash(pwd)

def check_password(self, pwd):
    return check_password_hash(self.password, pwd)

token = jwt.encode(
    {"user_id": user.id, "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=8)},
    Settings.SECRET_KEY, algorithm="HS256"
)
```

---

## 5. Lógica de Negócio em Controller → Extrair para Model/Service

**Antes** (Python — dentro do controller/route)
```python
def relatorio_vendas():
    ...
    desconto = 0
    if faturamento > 10000: desconto = faturamento * 0.1
    elif faturamento > 5000: desconto = faturamento * 0.05
```

**Depois**
```python
# models/pedido_model.py
DESCONTO_FAIXAS = [(10000, 0.10), (5000, 0.05), (1000, 0.02)]

def calcular_desconto(faturamento: float) -> float:
    for limite, taxa in DESCONTO_FAIXAS:
        if faturamento > limite:
            return faturamento * taxa
    return 0

# controllers/relatorio_controller.py
def relatorio_vendas():
    dados = pedido_model.relatorio_vendas()
    return jsonify(dados), 200
```

---

## 6. Acoplamento Forte → Injeção de dependência

**Antes** (Python)
```python
# dentro da função de negócio
def criar_produto(...):
    db = get_db()   # acopla direto à conexão global
```

**Depois**
```python
# a conexão é resolvida uma vez no composition root e passada/injetada,
# ou o model recebe a sessão via contexto do app (Flask app context / SQLAlchemy session),
# nunca importando um singleton dentro da regra de negócio.
def criar_produto(session, nome, preco, estoque, categoria):
    produto = Produto(nome=nome, preco=preco, estoque=estoque, categoria=categoria)
    session.add(produto)
    session.commit()
    return produto.id
```

---

## 7. Estado Global Mutável → Estado por requisição/persistido

**Antes** (Node)
```javascript
let globalCache = {};
function logAndCache(key, data) { globalCache[key] = data; }
```

**Depois**
```javascript
// cache dedicado com escopo e TTL explícitos (ou removido, se não for
// realmente necessário), nunca um objeto mutável solto no módulo
// compartilhado implicitamente por todas as requisições concorrentes.
const cache = new Map(); // encapsulado em um serviço próprio, injetado onde necessário
class CacheService {
  set(key, value) { cache.set(key, value); }
  get(key) { return cache.get(key); }
}
```

---

## 8. Query N+1 → Busca em lote / eager load

**Antes** (Python)
```python
for t in Task.query.all():
    user = User.query.get(t.user_id)   # 1 query por task
```

**Depois**
```python
tasks = Task.query.options(db.joinedload(Task.user), db.joinedload(Task.category)).all()
# ou, sem ORM eager-load disponível: buscar todos os user_ids de uma vez
user_ids = {t.user_id for t in tasks if t.user_id}
users_by_id = {u.id: u for u in User.query.filter(User.id.in_(user_ids))}
```

---

## 9. API Deprecated → Substituir pelo equivalente atual

**Antes** (Python, deprecated desde 3.12)
```python
created_at = datetime.utcnow()
```

**Depois**
```python
from datetime import datetime, timezone
created_at = datetime.now(timezone.utc)
```

---

## 10. Falta de Paginação/Validação → Limite + schema de validação

**Antes** (Python)
```python
@task_bp.route('/tasks', methods=['GET'])
def get_tasks():
    tasks = Task.query.all()
```

**Depois**
```python
@task_bp.route('/tasks', methods=['GET'])
def get_tasks():
    page = int(request.args.get('page', 1))
    per_page = min(int(request.args.get('per_page', 20)), 100)
    tasks = Task.query.paginate(page=page, per_page=per_page, error_out=False).items
```

---

## 11. Duplicação de Código → Reuso do método já existente

**Antes** (lógica de "atrasado" repetida em 5 arquivos)
```python
if t.due_date:
    if t.due_date < datetime.utcnow():
        if t.status != 'done' and t.status != 'cancelled':
            overdue = True
```

**Depois**
```python
# já existe Task.is_overdue() no model — use-o em todo lugar
overdue = t.is_overdue()
```

---

## 12. Tratamento de erro espalhado → Error handler centralizado

**Antes** (Python — cada controller com seu próprio try/except)
```python
try:
    ...
except Exception as e:
    return jsonify({"erro": str(e)}), 500
```

**Depois**
```python
# middlewares/error_handler.py
@app.errorhandler(Exception)
def handle_error(e):
    app.logger.exception(e)
    return jsonify({"error": "internal_server_error"}), 500
```
Controllers deixam de precisar de `try/except` genérico repetido.

---

## Como usar este playbook na Fase 3

Para cada finding do relatório da Fase 2, localize o padrão correspondente aqui (o campo `Recommendation` do finding referencia o padrão), aplique a transformação adaptando nomes/entidades ao projeto real, e confirme visualmente que o comportamento do endpoint não mudou antes de seguir para o próximo finding.
