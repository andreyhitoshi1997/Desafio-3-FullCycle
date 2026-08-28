# Catálogo de Anti-Patterns (Fase 2)

Escala de severidade (fixa para todo o catálogo):

- **CRITICAL**: falha grave de arquitetura/segurança que expõe dados sensíveis, permite execução arbitrária de comandos/queries, ou é um "God Class" completo (DB + lógica + roteamento juntos).
- **HIGH**: forte violação de MVC/SOLID que dificulta muito manutenção/teste (lógica de negócio em Controllers, acoplamento forte sem DI, estado global mutável).
- **MEDIUM**: padronização, duplicação, performance moderada (N+1, middleware mal usado, validação ausente).
- **LOW**: legibilidade, nomenclatura, magic numbers.

Cada entrada abaixo lista: sinais de detecção concretos (o que procurar no código) + severidade + por quê.

---

### 1. [CRITICAL] Hardcoded Credentials / Secrets
**Sinais**: literais de string atribuídos a variáveis/chaves de configuração com nomes como `secret`, `password`, `senha`, `key`, `token`, `api_key`, `db_pass`, `smtp_password`; valores que parecem chaves reais (`pk_live_...`, `sk_...`) escritos direto no `.py`/`.js`; segredo também retornado em uma resposta HTTP (endpoint que devolve config interna).
**Por quê CRITICAL**: qualquer pessoa com acesso ao repositório (ou a uma resposta de API que vaze config) tem a credencial de produção.

### 2. [CRITICAL] SQL Injection
**Sinais**: concatenação de string (`+`, f-string, `%`) formando uma query SQL com dado vindo de `request`/`req.body`/parâmetro de rota; endpoint que recebe SQL bruto do cliente e executa (`cursor.execute(query)` onde `query` vem do payload).
**Por quê CRITICAL**: permite leitura/escrita/exclusão arbitrária no banco por um atacante não autenticado.

### 3. [CRITICAL] God Class / God Object
**Sinais**: um único arquivo/classe/módulo que (a) cria/gerencia a conexão de banco, (b) define o schema, (c) registra rotas HTTP, e (d) implementa a lógica de negócio de múltiplos domínios — tudo junto, sem separação. Também conta um único arquivo de "models" com >250 linhas cobrindo ≥3 entidades de domínio diferentes.
**Por quê CRITICAL**: viola completamente a separação de responsabilidades; qualquer mudança em um domínio arrisca quebrar os outros; impossível testar em isolamento.

### 4. [CRITICAL] Autenticação/Criptografia Quebrada
**Sinais**: senha comparada em texto puro (`senha == input`); hash de senha com `md5`/`sha1`; função de "hash" caseira que não é um algoritmo criptográfico reconhecido; token de sessão/JWT construído por concatenação de string previsível (ex.: `"fake-token-" + user_id`) em vez de um token assinado.
**Por quê CRITICAL**: quebra de autenticação — credenciais são recuperáveis/forjáveis, permitindo impersonar qualquer usuário.

### 5. [HIGH] Lógica de Negócio em Controllers/Routes
**Sinais**: handler de rota com >25-30 linhas contendo cálculos de negócio (descontos, totais, regras de status), múltiplos passos de orquestração, ou validações complexas que deveriam viver em Model/Service — o handler faz "tudo" em vez de delegar.
**Por quê HIGH**: impede reuso e teste unitário da regra de negócio fora do contexto HTTP.

### 6. [HIGH] Acoplamento Forte / Ausência de Injeção de Dependência
**Sinais**: função de lógica de negócio importa e usa diretamente uma conexão de banco global (`from database import get_db` usado dentro da regra de negócio, não recebido como parâmetro); impossível substituir a dependência em um teste sem tocar no módulo.
**Por quê HIGH**: dificulta muito testes automatizados e a evolução da camada de dados.

### 7. [HIGH] Estado Global Mutável
**Sinais**: variável mutável declarada no escopo do módulo (`let cache = {}`, `contador = 0`, dicionário/lista no topo do arquivo) e alterada dentro de handlers de requisição, compartilhada entre requisições concorrentes.
**Por quê HIGH**: causa condições de corrida e comportamento não determinístico sob concorrência; estado "vaza" entre usuários/requisições.

### 8. [MEDIUM] Query N+1
**Sinais**: um `for` que itera sobre uma lista de resultados e, dentro do loop, dispara uma nova query (`cursor.execute`, `Model.query.get(...)`, `db.get(...)`) por item, em vez de um JOIN/eager load/busca em lote.
**Por quê MEDIUM**: degrada performance proporcionalmente ao tamanho dos dados; não quebra a aplicação, mas não escala.

### 9. [MEDIUM] Falta de Paginação / Validação de Entrada
**Sinais**: endpoint de listagem que retorna `Model.query.all()`/`SELECT *` sem `LIMIT`/`OFFSET`; ausência de validação de schema em rotas que recebem payload, mesmo quando uma lib de validação (ex.: `marshmallow`) está nas dependências mas não é usada.
**Por quê MEDIUM**: risco de payloads gigantes, respostas lentas, e dados inconsistentes por falta de validação — mas a aplicação continua funcionando.

### 10. [MEDIUM] Duplicação de Código
**Sinais**: o mesmo bloco de lógica (ex.: cálculo de "atrasado", serialização de um objeto) copiado quase identicamente em ≥3 lugares diferentes, especialmente quando já existe um método/função equivalente definido e subutilizado.
**Por quê MEDIUM**: qualquer correção precisa ser replicada manualmente em todos os pontos, gerando divergência com o tempo.

### 11. [MEDIUM] Uso de API Deprecated/Obsoleta
**Sinais** (exemplos concretos, não exaustivo):
- Python: `datetime.utcnow()` / `datetime.utcnow` (deprecated desde Python 3.12 — usar `datetime.now(timezone.utc)`); `@app.before_first_request` do Flask (removido no Flask ≥2.3); uso do parser de query string antigo do Werkzeug.
- Node.js: `new Buffer(...)` (deprecated — usar `Buffer.from(...)`); driver de banco 100% callback-based quando existe uma API baseada em Promise/`async`/`await` mantida pelo mesmo pacote; middleware `body-parser` standalone quando o framework já embute o equivalente (`express.json()`).
**Por quê MEDIUM**: a API ainda funciona hoje mas emite aviso de depreciação e pode ser removida em uma versão futura da linguagem/framework, quebrando a aplicação sem aviso se não for corrigido.

### 12. [LOW] Nomenclatura Inconsistente / Magic Numbers e Strings
**Sinais**: nomes de variáveis de uma letra (`u`, `e`, `p`, `cc`) fora de escopos triviais; números/strings literais repetidos (limites, thresholds, listas de valores válidos) espalhados pelo código em vez de uma constante nomeada — inclusive quando já existe um módulo de constantes definido, mas não utilizado.
**Por quê LOW**: não afeta funcionamento, mas piora legibilidade e facilita erros de digitação/inconsistência.

### 13. [LOW] Retorno Booleano Não Idiomático / Código Morto
**Sinais**: padrão `if condição: return True else: return False` em vez de `return condição`; imports não utilizados; constantes definidas e nunca importadas/usadas em nenhum lugar do projeto.
**Por quê LOW**: verboso e sinaliza falta de revisão, mas sem impacto funcional.

### 14. [LOW] Logging via print() em vez de logger estruturado
**Sinais**: uso de `print(...)`/`console.log(...)` para registrar erros e eventos de negócio em vez do módulo de logging padrão da linguagem/framework (`logging` em Python, um logger como `pino`/`winston` em Node).
**Por quê LOW**: funciona em desenvolvimento, mas não oferece níveis de log, formatação estruturada nem destino configurável em produção.

---

## Como aplicar este catálogo

Para cada arquivo-fonte do projeto, percorra as 14 entradas e registre um finding sempre que um sinal de detecção estiver presente, citando o arquivo e a(s) linha(s) exata(s). Um mesmo arquivo pode (e normalmente vai) acionar várias entradas. Não invente achados que não têm um sinal concreto correspondente no código.
