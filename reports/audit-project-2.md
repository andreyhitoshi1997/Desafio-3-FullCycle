================================
PHASE 1: PROJECT ANALYSIS
================================
Language:      JavaScript (Node.js)
Framework:     Express ^4.18.2
Dependencies:  sqlite3 ^5.1.6
Domain:        LMS API com fluxo de checkout (cursos, matrículas, pagamentos) — "Frankenstein LMS"
Architecture:  Monolítica — praticamente toda a lógica em uma única classe (AppManager.js), sem pastas de camada (models/routes/controllers)
Source files:  3 files analyzed (~182 lines of code)
DB tables:     users, courses, enrollments, payments, audit_logs
================================

================================
ARCHITECTURE AUDIT REPORT
================================
Project: ecommerce-api-legacy
Stack:   Node.js + Express ^4.18.2
Files:   3 analyzed | ~182 lines of code

Summary
CRITICAL: 5 | HIGH: 4 | MEDIUM: 3 | LOW: 3

Findings

[CRITICAL] Hardcoded Credentials / Secrets
File: src/utils.js:2-6
Description: `config` exporta em texto puro `dbPass: "senha_super_secreta_prod_123"`, `paymentGatewayKey: "pk_live_1234567890abcdef"` (formato de chave live de gateway de pagamento) e `smtpUser`.
Impact: Qualquer pessoa com acesso ao repositório tem credenciais de produção, incluindo uma chave de gateway de pagamento live.
Recommendation: Playbook #1 — mover para variáveis de ambiente via módulo de config, com `.env.example` sem valores reais.

[CRITICAL] God Class
File: src/AppManager.js:4-142
Description: A classe `AppManager` cria e gerencia a conexão SQLite (`constructor`), define o schema de 5 tabelas (`initDb`), e registra E implementa toda a lógica de negócio de checkout, relatório financeiro e exclusão de usuário dentro de `setupRoutes` — persistência, roteamento e regra de negócio no mesmo arquivo/classe.
Impact: Impossível testar checkout ou relatório isoladamente; qualquer mudança de schema, rota ou regra de negócio acontece no mesmo lugar, sem fronteiras.
Recommendation: Playbook #3 — separar em models (courses, users, enrollments, payments), controllers (checkout, financialReport, users) e routes.

[CRITICAL] Hash de senha falso/quebrado
File: src/utils.js:17-23, src/AppManager.js:68
Description: `badCrypto(pwd)` não é um algoritmo criptográfico — repete um slice de base64 10.000 vezes e trunca para 10 caracteres. É usada para "hashear" a senha do usuário no cadastro implícito durante o checkout.
Impact: Não protege a senha de forma alguma (alta chance de colisão, sem salt, trivialmente reversível/adivinhável); qualquer vazamento do banco expõe efetivamente as senhas.
Recommendation: Playbook #4 — usar `bcrypt`/`argon2` (hash real com salt).

[CRITICAL] Endpoint não autenticado expõe dados financeiros e pessoais
File: src/AppManager.js:80-129
Description: `GET /api/admin/financial-report` não exige nenhuma autenticação/autorização e devolve, por curso, a lista de alunos com nome e valor pago.
Impact: Qualquer requisição não autenticada obtém receita por curso e dados pessoais + financeiros de todos os alunos.
Recommendation: Exigir autenticação/autorização de administrador antes de expor este relatório.

[CRITICAL] Endpoint destrutivo sem autenticação
File: src/AppManager.js:131-137
Description: `DELETE /api/users/:id` apaga um usuário sem qualquer checagem de autenticação/autorização.
Impact: Qualquer cliente não autenticado pode apagar a conta de qualquer usuário só sabendo o id.
Recommendation: Proteger com autenticação/autorização antes de qualquer mutação destrutiva.

[HIGH] Lógica de negócio pesada dentro do handler de rota
File: src/AppManager.js:28-78
Description: O handler de `POST /api/checkout` implementa, tudo dentro do callback da rota: criação de usuário, hash de senha, decisão de aprovação de pagamento, matrícula, registro de pagamento e log de auditoria — uma pirâmide de callbacks fazendo orquestração completa de um caso de uso.
Impact: Impossível reutilizar ou testar o fluxo de checkout fora do contexto HTTP; qualquer novo passo aumenta ainda mais o aninhamento.
Recommendation: Playbook #5 — extrair para um `CheckoutController`/service que orquestra chamadas aos models, mantendo a rota fina.

[HIGH] Estado global mutável
File: src/utils.js:9-10
Description: `globalCache = {}` e `totalRevenue = 0` são declarados no escopo do módulo e `globalCache` é mutado a cada checkout (via `logAndCache`), compartilhado por todas as requisições concorrentes.
Impact: Estado "vaza" entre requisições/usuários; comportamento não determinístico sob uso concorrente; impossível isolar em teste.
Recommendation: Playbook #7 — encapsular em um serviço com escopo e ciclo de vida explícitos (ou remover, se não for essencial).

[HIGH] Lógica de aprovação de pagamento ingênua e embutida na rota
File: src/AppManager.js:46
Description: A decisão de aprovar ou negar o pagamento é `cc.startsWith("4")` — nenhuma integração real com gateway de pagamento, a "regra de negócio" mais crítica do fluxo é uma checagem de prefixo de cartão hardcoded na rota.
Impact: Qualquer cartão começando com "4" é aprovado, sem validação real; lógica de pagamento não é testável nem substituível.
Recommendation: Extrair para um serviço de pagamento isolado (ainda que mock/simulado), nunca embutido na rota.

[HIGH] Acoplamento forte / sem injeção de dependência
File: src/AppManager.js:4-8
Description: O construtor de `AppManager` instancia diretamente `new sqlite3.Database(':memory:')` — não há como injetar outra conexão (ex.: um banco de teste) sem alterar a classe.
Impact: Impossível testar `AppManager` com um double de banco de dados.
Recommendation: Playbook #6 — receber a conexão/repositório via injeção no construtor.

[MEDIUM] Pirâmide de callbacks com padrão N+1
File: src/AppManager.js:83-127
Description: `GET /api/admin/financial-report` itera cursos, e para cada curso itera matrículas, e para cada matrícula faz mais 2 queries (usuário + pagamento) — N+1 aninhado em 3 níveis, com contadores manuais (`coursesPending`, `enrPending`) para saber quando finalizar a resposta.
Impact: Degrada rapidamente com o volume de dados; o controle manual de contadores é frágil e propenso a bugs de sincronização se qualquer callback disparar fora da ordem esperada.
Recommendation: Playbook #8 — substituir por queries em lote (join ou `IN (...)`) em vez de N+1 aninhado.

[MEDIUM] Banco "em memória" hardcoded, sem config
File: src/AppManager.js:7
Description: `new sqlite3.Database(':memory:')` está fixo no código — não há variável de ambiente para apontar a um arquivo persistente em produção.
Impact: Todo dado é perdido a cada reinício do processo; decisão de infraestrutura embutida no código sem possibilidade de configuração.
Recommendation: Ler o caminho do banco de uma variável de ambiente (`DB_PATH`), com `:memory:` como default apenas para testes.

[MEDIUM] Exclusão de usuário deixa dados órfãos
File: src/AppManager.js:131-137
Description: O próprio código reconhece o problema na mensagem de resposta ("mas as matrículas e pagamentos ficaram sujos no banco") — `enrollments`/`payments` do usuário não são limpos/cascateados ao deletar.
Impact: Dados órfãos se acumulam no banco, referenciando um `user_id` que não existe mais; relatórios futuros podem quebrar ou mentir.
Recommendation: Cascatear a exclusão (ou fazer soft-delete) dentro do model de usuário.

[LOW] Nomenclatura de variáveis abreviada e pouco clara
File: src/AppManager.js:29-33
Description: `u`, `e`, `p`, `cid`, `cc` para usuário, email, senha, id do curso e número do cartão.
Impact: Reduz legibilidade e aumenta a chance de troca acidental de variável.
Recommendation: Nomes descritivos (`userName`, `email`, `password`, `courseId`, `cardNumber`).

[LOW] Logging via console.log em vez de logger estruturado
File: src/app.js:13, src/utils.js:13, src/AppManager.js:45
Description: Eventos de negócio e cache são registrados com `console.log` puro, sem nível/formatação.
Impact: Sem controle de nível de log nem destino configurável em produção.
Recommendation: Logger estruturado (ex.: `pino`/`winston`) configurado no composition root.

[LOW] Código morto / utilitário sem uso real
File: src/utils.js:9-10, 12-15
Description: `totalRevenue` é declarado e exportado, mas nunca incrementado ou lido em nenhum lugar do projeto; `logAndCache` só grava em um cache global sem nenhum consumidor visível do valor salvo.
Impact: Complexidade e confusão sem benefício — sugere funcionalidade abandonada pela metade.
Recommendation: Remover se realmente não usado, ou completar/documentar o propósito.

Nota — verificação de APIs deprecated: `express@^4.18.2` e o driver `sqlite3@^5.1.6` (usados via API de callback, mas não uma API oficialmente deprecated do pacote) estão atualizados; nenhuma API deprecated foi encontrada em `ecommerce-api-legacy`. Ver `reports/audit-project-3.md` para um caso real de API deprecated (`datetime.utcnow()` do Python).

================================
Total: 15 findings
================================

Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]
