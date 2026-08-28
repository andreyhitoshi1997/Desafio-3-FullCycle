================================
ARCHITECTURE AUDIT REPORT
================================
Project: code-smells-project
Stack:   Python + Flask 3.1.1
Files:   4 analyzed | ~784 lines of code

Summary
CRITICAL: 8 | HIGH: 4 | MEDIUM: 4 | LOW: 3

Findings

[CRITICAL] Hardcoded SECRET_KEY
File: app.py:7
Description: `app.config["SECRET_KEY"]` recebe o literal `"minha-chave-super-secreta-123"` diretamente no código-fonte.
Impact: Qualquer pessoa com acesso ao repositório tem a chave de assinatura de sessão da aplicação; permite forjar sessões/cookies assinados.
Recommendation: Playbook #1 — mover para variável de ambiente via módulo de config, nunca literal no código.

[CRITICAL] Segredos e flags de debug expostos via endpoint público
File: controllers.py:285-289
Description: `health_check()` devolve no corpo da resposta JSON os campos `"debug": True` e `"secret_key": "minha-chave-super-secreta-123"` — um endpoint `/health` sem autenticação vaza a config interna da aplicação.
Impact: Qualquer cliente HTTP não autenticado obtém a SECRET_KEY em produção só chamando `/health`.
Recommendation: Nunca incluir config sensível na resposta de health check; health check deve retornar apenas status operacional.

[CRITICAL] SQL Injection por concatenação de string
File: models.py:28, 48-50, 68, 92, 140, 148-151, 158-161, 163-166, 220, 280, 291-297
Description: Praticamente toda query do arquivo é montada concatenando `str(id)` ou valores de entrada diretamente na string SQL (ex.: `"SELECT * FROM produtos WHERE id = " + str(id)`, `buscar_produtos` concatenando `termo`/`categoria` recebidos da querystring linha 291-297).
Impact: Um atacante controla parte da query SQL executada — pode ler, alterar ou apagar qualquer dado do banco (ex.: `id=1 OR 1=1`, `id=1; DROP TABLE produtos;--`, dependendo do driver).
Recommendation: Playbook #2 — usar query parametrizada (`?`/bind params) em toda função de acesso a dados.

[CRITICAL] SQL Injection permitindo bypass de autenticação
File: models.py:109-111
Description: `login_usuario` monta `"SELECT * FROM usuarios WHERE email = '" + email + "' AND senha = '" + senha + "'"` — email/senha vêm direto do payload de `/login` (controllers.py:170-171) sem sanitização.
Impact: Um payload como `email = "admin@loja.com' -- "` autentica sem saber a senha — bypass completo de autenticação.
Recommendation: Playbook #2 e #4 — query parametrizada + comparação de hash (nunca senha em texto puro na query).

[CRITICAL] Endpoint não autenticado de execução arbitrária de SQL
File: app.py:59-78
Description: `POST /admin/query` recebe `sql` no corpo da requisição e executa via `cursor.execute(query)` sem qualquer autenticação/autorização.
Impact: Qualquer requisição não autenticada pode executar SQL arbitrário no banco de produção — controle total do banco de dados.
Recommendation: Remover o endpoint (não deve existir em produção) ou, se necessário para administração, protegê-lo com autenticação forte e nunca aceitar SQL livre do cliente.

[CRITICAL] Endpoint não autenticado de destruição de dados
File: app.py:47-57
Description: `POST /admin/reset-db` apaga todas as linhas de `itens_pedido`, `pedidos`, `produtos` e `usuarios` sem exigir autenticação.
Impact: Qualquer cliente não autenticado pode apagar todos os dados da aplicação.
Recommendation: Remover de produção ou proteger com autenticação/autorização de administrador.

[CRITICAL] God Class / God Module
File: models.py:1-315, controllers.py:1-293
Description: `models.py` concentra acesso a dados, SQL cru e regra de negócio (incluindo cálculo de desconto) para 4 entidades diferentes (produtos, usuários, pedidos, itens_pedido) em um único arquivo de 315 linhas; `controllers.py` espelha o mesmo problema na camada HTTP, com as 4 entidades e toda a lógica de request/response em um único arquivo de 293 linhas.
Impact: Impossível testar uma entidade isoladamente; qualquer mudança em um domínio arrisca efeitos colaterais em todos os outros; nenhuma fronteira de responsabilidade.
Recommendation: Playbook #3 — dividir em um model e um controller por domínio (produto, usuario, pedido).

[CRITICAL] Senha armazenada e comparada em texto puro
File: database.py:76-83, models.py:105-120, models.py:122-131
Description: Os usuários seed são inseridos com `senha` em texto puro (database.py:76-83); `criar_usuario` insere a senha recebida sem hash (models.py:122-131); `login_usuario` compara a senha do payload diretamente contra a coluna `senha` em texto puro (models.py:109-111).
Impact: Vazamento do banco expõe todas as senhas em claro; nenhuma proteção mesmo contra acesso interno indevido.
Recommendation: Playbook #4 — hash com `werkzeug.security.generate_password_hash`/`check_password_hash` (ou equivalente), nunca armazenar/comparar texto puro.

[HIGH] Regra de negócio (cálculo de desconto) dentro da camada de acesso a dados
File: models.py:256-262
Description: `relatorio_vendas()` implementa as faixas de desconto (`> 10000 → 10%`, `> 5000 → 5%`, `> 1000 → 2%`) misturadas com as queries SQL de agregação, dentro do que deveria ser apenas a camada de dados.
Impact: Regra de negócio não pode ser testada nem reutilizada sem executar SQL; qualquer mudança na regra de desconto exige tocar em código de acesso a dados.
Recommendation: Playbook #5 — extrair a regra para uma função de domínio pura, chamada pelo controller/model.

[HIGH] Acoplamento forte à conexão global de banco (sem injeção de dependência)
File: database.py:4, 7-11
Description: `db_connection` é um singleton global em nível de módulo; toda função de `models.py` chama `get_db()` diretamente, acoplando cada função de negócio à conexão concreta.
Impact: Impossível substituir a conexão por um mock/fake em teste unitário sem monkeypatch do módulo inteiro.
Recommendation: Playbook #6 — receber a conexão/sessão como parâmetro/injeção em vez de importar o singleton dentro da lógica.

[HIGH] `DEBUG=True` hardcoded
File: app.py:8, 88
Description: `app.config["DEBUG"] = True` e `app.run(..., debug=True)` fixos no código-fonte, sem depender de ambiente.
Impact: Em produção, o debugger interativo do Werkzeug fica acessível e stack traces detalhados (incluindo variáveis locais) vazam em respostas de erro — risco conhecido de execução remota de código via o debugger do Werkzeug.
Recommendation: Ler de variável de ambiente (`DEBUG=false` por padrão) via módulo de config.

[HIGH] CORS totalmente aberto
File: app.py:9
Description: `CORS(app)` é chamado sem nenhuma restrição de origem, liberando todas as origens para todos os endpoints, incluindo os administrativos.
Impact: Qualquer site de terceiros pode fazer requisições autenticadas via browser à API.
Recommendation: Restringir `CORS` às origens conhecidas do frontend, via config.

[MEDIUM] Query N+1 ao montar pedidos
File: models.py:171-201, 203-233
Description: `get_pedidos_usuario` e `get_todos_pedidos` iteram sobre os pedidos e, para cada item de cada pedido, abrem um novo cursor (`cursor2`, `cursor3`) para buscar o item e o nome do produto — uma query adicional por item, dentro de um loop por pedido.
Impact: Tempo de resposta cresce linearmente com o número de pedidos × itens; não escala.
Recommendation: Playbook #8 — join único (ou buscar itens/produtos em lote pelos IDs coletados antes do loop).

[MEDIUM] Ausência de paginação nos endpoints de listagem
File: controllers.py:5-12, 128-134, 229-235
Description: `listar_produtos`, `listar_usuarios` e `listar_todos_pedidos` sempre retornam a tabela inteira (`models.get_todos_*()`), sem parâmetros de página/limite.
Impact: Resposta cresce sem limite conforme o volume de dados aumenta; risco de payloads muito grandes.
Recommendation: Playbook #10 — adicionar `page`/`per_page` com limite máximo.

[MEDIUM] Bloco try/except duplicado em praticamente todo controller
File: controllers.py:6-12, 15-22, 60-62, 95-96, 108-109, 125-126, 133-134, 143-144, 164-165, 185-186, 218-220, 226-227, 234-235, 254-255, 261-262, 291-292
Description: O mesmo padrão `try: ... except Exception as e: return jsonify({"erro": str(e)}), 500` é copiado em praticamente todas as ~16 funções do arquivo, cada uma formatando a resposta de erro manualmente.
Impact: Qualquer mudança no formato de erro (ex.: adicionar um campo `code`) exige editar 16 lugares; alto risco de divergência.
Recommendation: Playbook #12 — error handler centralizado (`@app.errorhandler`), controllers deixam de precisar de try/except genérico.

[MEDIUM] Logging via print() em vez de logger estruturado
File: controllers.py:8, 11, 57, 61, 106, 161, 179, 182, 208-210, 219, 248, 250; app.py:56, 83-86
Description: Erros e eventos de negócio (criação de produto/usuário, login, "envio" de email/SMS/push) são registrados com `print(...)` em vez do módulo `logging`.
Impact: Sem níveis de log, sem formatação estruturada, sem destino configurável — inutilizável para observabilidade em produção.
Recommendation: Playbook — substituir por `logging` configurado no composition root, com nível por ambiente.

[LOW] Magic numbers para faixas de desconto e validação de nome
File: models.py:257-262, controllers.py:47-50
Description: Limiares de desconto (`10000`, `5000`, `1000`, `0.1`, `0.05`, `0.02`) e limites de tamanho de nome (`2`, `200`) são literais soltos no meio da lógica, sem constante nomeada.
Impact: Não é óbvio de onde vêm esses valores nem como alterá-los com segurança; fácil de digitar errado ao duplicar.
Recommendation: Extrair para constantes nomeadas no topo do módulo/config.

[LOW] Lista de categorias válidas hardcoded inline
File: controllers.py:52
Description: `categorias_validas = ["informatica", "moveis", "vestuario", "geral", "eletronicos", "livros"]` é declarada dentro da função `criar_produto`, sem ser uma constante compartilhada nem vir do banco/config.
Impact: Se outra função precisar validar categoria (ex.: `atualizar_produto`), a lista provavelmente será duplicada e pode divergir.
Recommendation: Extrair para uma constante única reutilizada em todos os pontos que validam categoria.

[LOW] Nomenclatura inconsistente entre PT-BR e convenções de código
File: models.py, controllers.py, app.py (em geral)
Description: Identificadores de domínio em português (`nome`, `preco`, `erro`, `sucesso`) convivem com estrutura de código em inglês, sem um padrão único documentado — não é um erro funcional, mas reduz previsibilidade para quem só lê parte do código.
Impact: Aumenta a chance de inconsistência de nomenclatura conforme o projeto cresce.
Recommendation: Documentar e seguir um padrão único (ex.: manter nomes de domínio em PT-BR, mas nomes técnicos/estruturais em inglês).

Nota — verificação de APIs deprecated: Flask 3.1.1 e o módulo `sqlite3` da stdlib usados neste projeto estão atualizados; nenhuma API deprecated foi encontrada em `code-smells-project`. (A skill inclui essa verificação no catálogo — ela apenas não encontrou ocorrência aqui; ver `reports/audit-project-3.md` para um caso real de API deprecated.)

================================
Total: 19 findings
================================

Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]
