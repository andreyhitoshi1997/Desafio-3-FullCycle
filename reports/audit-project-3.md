================================
PHASE 1: PROJECT ANALYSIS
================================
Language:      Python
Framework:     Flask 3.0.0 + Flask-SQLAlchemy 3.1.1
Dependencies:  flask-cors 4.0.0, marshmallow 3.20.1 (listada mas não utilizada), requests 2.31.0, python-dotenv 1.0.0 (listada mas não utilizada)
Domain:        Task Manager API (tasks, usuários, categorias, relatórios de produtividade)
Architecture:  Parcialmente organizada — já possui models/, routes/, services/, utils/, mas com lógica duplicada nas rotas e problemas de segurança dentro de cada camada
Source files:  15 files analyzed (11 com lógica relevante; 4 __init__.py vazios) | ~1163 lines of code
DB tables:     tasks, users, categories
================================

================================
ARCHITECTURE AUDIT REPORT
================================
Project: task-manager-api
Stack:   Python + Flask 3.0.0 + Flask-SQLAlchemy
Files:   15 analyzed | ~1163 lines of code

Summary
CRITICAL: 4 | HIGH: 3 | MEDIUM: 5 | LOW: 3

Findings

[CRITICAL] Hardcoded SECRET_KEY
File: app.py:13
Description: `app.config['SECRET_KEY'] = 'super-secret-key-123'` fixo no código-fonte — mesmo com `python-dotenv` listado em `requirements.txt`, nenhum `load_dotenv()` é chamado em lugar nenhum do projeto.
Impact: Chave de assinatura exposta a qualquer pessoa com acesso ao repositório.
Recommendation: Playbook #1 — carregar de variável de ambiente via `python-dotenv`/config, já que a dependência já existe mas não é usada.

[CRITICAL] Hash de senha com MD5 (criptografia quebrada)
File: models/user.py:27-32
Description: `set_password`/`check_password` usam `hashlib.md5(pwd.encode()).hexdigest()` para armazenar e comparar senhas.
Impact: MD5 é criptograficamente quebrado para senhas — vulnerável a rainbow tables e colisão; vazamento do banco expõe senhas de forma prática.
Recommendation: Playbook #4 — `werkzeug.security.generate_password_hash`/`check_password_hash`.

[CRITICAL] Token de autenticação falso e ausência total de verificação de autorização
File: routes/user_routes.py:185-211 (token em 210); task_routes.py, user_routes.py, report_routes.py (nenhum arquivo checa token/Authorization em nenhuma rota)
Description: `POST /login` devolve `'token': 'fake-jwt-token-' + str(user.id)` — um valor previsível, não assinado. Pior: nenhuma rota de `tasks`, `users` ou `reports` valida esse (ou qualquer) token — todos os endpoints CRUD estão completamente abertos independentemente de login.
Impact: Qualquer cliente pode forjar `fake-jwt-token-<id>` para qualquer usuário, e nem precisaria — nenhum endpoint protegido realmente checa autenticação. Controle de acesso inexistente.
Recommendation: Playbook #4 — token assinado real (JWT com `pyjwt`) + middleware/decorator de autenticação aplicado às rotas que precisam de usuário autenticado.

[CRITICAL] Credenciais SMTP hardcoded
File: services/notification_service.py:9-10
Description: `email_user = 'taskmanager@gmail.com'` e `email_password = 'senha123'` fixos no construtor de `NotificationService`.
Impact: Credencial de e-mail de produção exposta no código-fonte.
Recommendation: Playbook #1 — mover para config/env.

[HIGH] Rotas reimplementam lógica que já existe no Model
File: routes/task_routes.py:16-40, 66-81 (vs. models/task.py:23-49)
Description: `get_tasks()`/`get_task()` reconstroem manualmente, campo por campo, o mesmo dicionário que `Task.to_dict()` já monta, e recalculam "atrasado" em vez de chamar `Task.is_overdue()` (que já existe e é usado apenas 1 vez no próprio model).
Impact: Duas implementações da mesma serialização podem divergir silenciosamente; qualquer novo campo precisa ser adicionado em múltiplos lugares.
Recommendation: Playbook #11 — rotas/controllers chamam `task.to_dict()`/`task.is_overdue()` em vez de duplicar a lógica.

[HIGH] Acoplamento forte à sessão global do SQLAlchemy, sem camada de serviço
File: routes/task_routes.py:1-9 (e igualmente em user_routes.py, report_routes.py)
Description: Toda rota importa `db` diretamente do módulo global e o usa para consultar/persistir, sem nenhuma camada de repositório/serviço entre a rota e o ORM.
Impact: Impossível testar a lógica de uma rota sem um banco real; toda regra de acesso a dados está espalhada pelas rotas.
Recommendation: Playbook #6 — introduzir uma camada de controller/service que encapsula o acesso ao `db`, rotas só chamam o controller.

[HIGH] Configuração hardcoded apesar de já ter a ferramenta para evitar isso
File: app.py:9-13
Description: `SQLALCHEMY_DATABASE_URI` e `SECRET_KEY` são strings literais, e `python-dotenv` está no `requirements.txt` mas nunca é importado/chamado (`load_dotenv()` não existe no projeto).
Impact: A dependência de configuração via `.env` já foi prevista mas nunca implementada — sinal de configuração inacabada, sem nenhuma variável de ambiente realmente controlando o app.
Recommendation: Playbook #1 — usar `python-dotenv` de fato: `load_dotenv()` + `os.environ` no módulo de config.

[MEDIUM] Uso de API deprecated — `datetime.utcnow()`
File: models/task.py:15-16; routes/task_routes.py:31, 37, 72, 78, 285-287; routes/user_routes.py:172, 178; routes/report_routes.py:35, 42, 46, 48, 50, 71
Description: `datetime.utcnow()` é chamado dezenas de vezes no projeto. Esta API é **deprecated desde Python 3.12** (emite `DeprecationWarning`, será removida futuramente) em favor de `datetime.now(timezone.utc)`, pois `utcnow()` retorna um datetime "naive" (sem timezone), fonte comum de bugs de fuso horário.
Impact: Funciona hoje mas já emite aviso de depreciação no ambiente atual (Python 3.14) e vai quebrar quando a API for removida em uma versão futura; datetimes naive também são uma fonte real de bugs de comparação de fuso horário.
Recommendation: Playbook #9 — substituir todas as ocorrências por `datetime.now(timezone.utc)`.

[MEDIUM] Duplicação da lógica de "task atrasada" em 5 lugares
File: models/task.py:50-60 (definição original, `is_overdue()`, subutilizada); routes/task_routes.py:30-39, 71-80; routes/user_routes.py:171-180; routes/report_routes.py:33-43
Description: O mesmo bloco `if due_date: if due_date < utcnow(): if status not in (done, cancelled): overdue = True` é copiado quase identicamente em 5 lugares diferentes, embora o model já tenha um método pronto para isso.
Impact: Qualquer correção na regra de "atrasado" precisa ser replicada manualmente em 5 arquivos — alto risco de divergência (e já diverge: cada cópia usa `datetime.utcnow()` diretamente em vez do método do model).
Recommendation: Playbook #11 — usar `task.is_overdue()` em todos os pontos.

[MEDIUM] Queries N+1
File: routes/task_routes.py:41-57 (`get_tasks`: `User.query.get()`/`Category.query.get()` dentro do loop sobre todas as tasks); routes/report_routes.py:53-68 (`summary_report`: `Task.query.filter_by(user_id=u.id)` dentro do loop sobre todos os usuários)
Description: Uma query adicional por task/usuário dentro de um loop, em vez de join/eager load ou busca em lote.
Impact: Tempo de resposta cresce linearmente com o número de tasks/usuários.
Recommendation: Playbook #8 — `joinedload`/`in_()` em lote.

[MEDIUM] Biblioteca de validação disponível mas não usada; validação manual repetida
File: requirements.txt:4 (`marshmallow`); routes/task_routes.py:89-145; routes/user_routes.py:42-72
Description: `marshmallow` está listada como dependência, mas nenhuma rota a importa — cada rota reimplementa validação com cadeias longas de `if`/`elif` (título, status, prioridade, email, senha), inclusive duplicando listas de valores válidos que já existem em `utils/helpers.py` (`VALID_STATUSES`, `VALID_ROLES`) sem reutilizá-las.
Impact: Validação inconsistente entre criar e atualizar (ex.: regras de e-mail duplicadas em `create_user`/`update_user` com a mesma regex copiada); manutenção cara.
Recommendation: Usar `marshmallow` (já disponível) para schemas de validação únicos por entidade, reaproveitando as constantes já definidas em `utils/helpers.py`.

[MEDIUM] Ausência de paginação nos endpoints de listagem
File: routes/task_routes.py:11-14; routes/user_routes.py:10-13
Description: `get_tasks()`/`get_users()` sempre retornam `Model.query.all()`, sem `page`/`per_page`.
Impact: Resposta cresce sem limite conforme o volume de dados.
Recommendation: Playbook #10 — adicionar paginação.

[LOW] Retorno booleano não idiomático
File: models/task.py:38-43 (`validate_status`); models/user.py:34-38 (`is_admin`)
Description: Padrão `if condição: return True else: return False` em vez de `return condição`.
Impact: Verboso, sem impacto funcional.
Recommendation: Simplificar para `return condição`.

[LOW] Imports não utilizados
File: routes/task_routes.py:7 (`time`, `sys`); utils/helpers.py:2-7 (`os`, `sys`, `math`, `hashlib` — nenhum usado no arquivo)
Description: Módulos importados e nunca referenciados no arquivo.
Impact: Ruído, sugere falta de revisão/lint no projeto.
Recommendation: Remover imports não utilizados (ou configurar um linter para pegar isso automaticamente).

[LOW] Constantes e helpers definidos e nunca usados
File: utils/helpers.py:9-117 (todo o arquivo: `VALID_STATUSES`, `VALID_ROLES`, `MAX_TITLE_LENGTH`, `MIN_TITLE_LENGTH`, `MIN_PASSWORD_LENGTH`, `DEFAULT_PRIORITY`, `DEFAULT_COLOR`, `process_task_data()`, `validate_email()`, `sanitize_string()`, `generate_id()`, `log_action()`)
Description: Nenhuma dessas constantes/funções é importada por nenhum arquivo em `routes/` — as rotas duplicam os mesmos valores/validações inline em vez de reaproveitar o que já foi escrito.
Impact: Módulo inteiro de utilitários é código morto na prática atual, ao mesmo tempo em que sua ausência de uso é a causa raiz de vários dos MEDIUM acima (validação e magic values duplicados).
Recommendation: Reconectar as rotas a `utils/helpers.py` (ou remover o que realmente não fizer sentido manter).

================================
Total: 15 findings
================================

Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]
