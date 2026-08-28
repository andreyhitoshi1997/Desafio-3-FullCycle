# Guidelines de Arquitetura MVC Alvo (Fase 3)

A refatoração sempre mira nesta estrutura, adaptada ao ecossistema da linguagem (nomes de pasta podem variar levemente, mas as responsabilidades abaixo não mudam):

```
src/  (ou raiz do projeto, se o ecossistema não usar pasta src/)
├── config/          # configuração centralizada, lida de variáveis de ambiente
├── models/          # uma unidade de persistência/domínio por arquivo
├── views/  (routes/) # definição de rotas HTTP — só roteamento
├── controllers/     # orquestração: recebe request já roteado, chama models/services, monta response
├── middlewares/      # cross-cutting: tratamento de erro centralizado, auth, CORS, logging
└── app.py / app.js / index.js   # composition root — monta tudo, não contém lógica de negócio
```

## Responsabilidade de cada camada

### Models
- Um arquivo por entidade/domínio (`produto_model.py`, `usuario_model.py`, não um `models.py` único para tudo).
- Contém: definição de dados (schema/ORM), acesso a persistência daquela entidade, e regras de domínio intrínsecas à entidade (ex.: `is_overdue()`, `validate_priority()`).
- **Não conhece HTTP** — nunca importa `request`/`response`, nunca formata JSON de resposta, nunca sabe de status code.
- Toda query usa parâmetros/bind (nunca concatenação de string com dado externo).

### Views / Routes
- Só declara rotas e qual controller cada uma chama (`app.add_url_rule(...)`, `@blueprint.route(...)`, `router.get(...)`).
- **Não contém lógica** — nem validação de negócio, nem cálculo, nem acesso direto a models.
- Pode agrupar rotas por domínio em arquivos/blueprints/routers separados.

### Controllers
- Recebe a requisição já roteada, extrai/valida entrada básica, chama o(s) model(s)/service(s) necessário(s), monta a resposta HTTP (status + corpo) e devolve.
- Orquestra múltiplos models quando um caso de uso cruza entidades (ex.: criar pedido = checar produto + atualizar estoque + criar pedido).
- Não contém SQL/query direta — sempre delega ao model correspondente.
- Não contém segredos/config hardcoded — lê de `config/`.

### Config
- Único ponto que lê variáveis de ambiente (`os.environ`/`process.env`).
- Nenhum outro arquivo do projeto deve conter uma credencial, chave ou URL de conexão literal.
- Deve existir um `.env.example` (sem valores reais) documentando as chaves esperadas.

### Middlewares
- Tratamento de erro centralizado: uma função/handler único que captura exceções não tratadas e devolve um formato de erro consistente — controllers não fazem `try/except` genérico devolvendo formatos diferentes cada um.
- Outras preocupações transversais (CORS, logging de requisição, autenticação) também vivem aqui, não espalhadas pelos controllers.

### Entry point (composition root)
- Cria a instância do framework, registra middlewares, registra rotas, inicializa a conexão de banco.
- Não implementa regra de negócio nem acesso a dados diretamente.
- Deve permanecer o ponto de entrada que o comando de boot original usava (ex.: se o projeto rodava com `python app.py`, o `app.py` final deve continuar sendo executável do mesmo jeito e escutando na mesma porta).

## Regra de adaptação (importante)

Se o projeto já tiver algumas dessas pastas (ex.: `task-manager-api` já tem `models/`, `routes/`, `services/`, `utils/`):

- **Não recrie do zero.** Avalie se o conteúdo de cada pasta realmente respeita a responsabilidade da camada (ex.: um `route` que também faz cálculo de negócio ainda viola a regra, mesmo estando na pasta certa).
- Adicione as camadas que faltam (tipicamente `controllers/` e `config/` costumam faltar em projetos "parcialmente organizados").
- Mova código para a camada correta em vez de duplicá-lo.
- Preserve nomes de arquivo/módulo que já fazem sentido — o objetivo é corrigir responsabilidade, não reescrever por reescrever.

## Compatibilidade obrigatória

- Os mesmos endpoints (mesmo path, mesmo método HTTP) devem continuar existindo e respondendo após a refatoração.
- O comando de boot original (ex.: `python app.py`, `npm start`) deve continuar funcionando, apontando para o novo entry point.
- Dados semeados/seeds existentes devem continuar sendo carregados da mesma forma esperada pelo README do projeto.
