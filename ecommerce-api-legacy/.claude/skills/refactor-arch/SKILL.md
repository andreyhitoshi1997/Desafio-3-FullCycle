---
name: refactor-arch
description: Analisa uma codebase de qualquer linguagem/framework, audita anti-patterns de arquitetura e segurança com severidade e arquivo:linha exatos, gera um relatório estruturado e refatora o projeto para o padrão MVC — validando que a aplicação continua funcionando. Use quando o usuário pedir para auditar, revisar arquitetura, encontrar code smells ou refatorar um projeto legado para MVC.
---

# refactor-arch — Auditoria e Refatoração Arquitetural

Você é um auditor e arquiteto de software sênior. Este skill roda em **3 fases sequenciais e obrigatórias**, sempre nesta ordem. Nunca pule uma fase, nunca combine Fase 2 e Fase 3 sem a confirmação explícita do humano.

Este skill é **agnóstico de tecnologia**: as heurísticas e o catálogo abaixo cobrem múltiplas linguagens/frameworks (Python/Flask, Node/Express, e qualquer outra stack similar) através de sinais textuais e estruturais, não de parsing específico de uma linguagem.

## Arquivos de referência

Carregue e use os seguintes arquivos (na pasta `references/` ao lado deste `SKILL.md`) durante as fases indicadas:

| Arquivo | Usado na fase | Conteúdo |
|---|---|---|
| `references/project-analysis.md` | Fase 1 | Heurísticas de detecção de linguagem, framework, banco de dados e arquitetura atual |
| `references/anti-patterns-catalog.md` | Fase 2 | Catálogo de anti-patterns com sinais de detecção e severidade |
| `references/report-template.md` | Fase 2 | Formato exato do relatório de auditoria |
| `references/architecture-guidelines.md` | Fase 3 | Regras do padrão MVC alvo (Models / Views-Routes / Controllers) |
| `references/refactoring-playbook.md` | Fase 3 | Padrões de transformação com exemplos de código antes/depois |

---

## FASE 1 — Análise do Projeto

Objetivo: entender a codebase antes de julgá-la.

1. Liste os arquivos-fonte do projeto (ignore `node_modules/`, `.venv/`, `__pycache__/`, `.git/`, arquivos de lock, bancos `.db`/`.sqlite`, e a própria pasta `.claude/skills/refactor-arch/`).
2. Aplique as heurísticas de `references/project-analysis.md` para determinar: linguagem, framework (+ versão, se disponível em um manifest), dependências relevantes, domínio de negócio (infira a partir de nomes de rotas/tabelas/entidades), arquitetura atual (monolítica em poucos arquivos vs. já parcialmente em camadas) e tabelas/coleções de banco de dados.
3. Conte os arquivos-fonte analisados e uma estimativa de linhas de código.
4. Imprima o resumo **exatamente** neste formato (adapte os valores, mantenha o layout):

```
================================
PHASE 1: PROJECT ANALYSIS
================================
Language:      <linguagem>
Framework:     <framework + versão se souber>
Dependencies:  <principais dependências relevantes>
Domain:        <domínio de negócio inferido>
Architecture:  <descrição curta da arquitetura atual>
Source files:  <N> files analyzed
DB tables:     <lista de tabelas/coleções, ou "none detected">
================================
```

Não peça confirmação nesta fase — ela é apenas informativa. Avance direto para a Fase 2.

---

## FASE 2 — Auditoria

Objetivo: cruzar o código, arquivo por arquivo, contra o catálogo de anti-patterns.

1. Para cada arquivo-fonte relevante, procure os sinais de detecção descritos em `references/anti-patterns-catalog.md` (todas as 14 entradas do catálogo, incluindo a detecção de APIs deprecated).
2. Para cada achado, registre: severidade (CRITICAL/HIGH/MEDIUM/LOW), título do anti-pattern, arquivo e **linha(s) exata(s)**, descrição do problema, impacto concreto, e recomendação de correção.
3. Monte o relatório completo seguindo **exatamente** `references/report-template.md`, com os findings **ordenados por severidade (CRITICAL → HIGH → MEDIUM → LOW)**.
4. Salve o relatório em `reports/audit-project-N.md` na raiz do repositório (pergunte ou infira N pela ordem de execução, ou use o nome do projeto se não houver numeração clara).
5. Imprima o relatório completo no terminal.
6. **Pare aqui.** Pergunte explicitamente:

```
Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]
```

**Nunca modifique, mova ou delete nenhum arquivo de código antes de receber uma resposta afirmativa explícita do humano a esta pergunta.** Se a resposta for negativa, pare e não prossiga.

---

## FASE 3 — Refatoração

Objetivo: eliminar os findings da Fase 2, reestruturando o projeto para MVC, sem quebrar o comportamento observável.

1. Siga `references/architecture-guidelines.md` para decidir a estrutura de diretórios alvo (Models / Views-Routes / Controllers / Config / Middlewares / entry point), adaptando ao que já existe no projeto — se o projeto já tem `models/`, `routes/`, etc., **mova e corrija o que já existe** em vez de recriar do zero.
2. Para cada finding da Fase 2, aplique a transformação correspondente descrita em `references/refactoring-playbook.md` (com exemplos de antes/depois). Nenhum finding CRITICAL ou HIGH deve sobrar sem correção. **Apenas mover ou renomear o código para outro arquivo, preservando exatamente a mesma lógica que o próprio finding apontou como falha (ex.: uma checagem hardcoded decidindo aprovação de pagamento), não conta como correção** — isso reprova o finding mesmo que o código agora esteja "isolado" em um service/model. Corrija o comportamento; só depois, se fizer sentido, isole-o.
3. Garanta que toda configuração sensível (secrets, chaves, credenciais de banco/SMTP/pagamento) saia do código-fonte e passe a vir de variáveis de ambiente, com um `.env.example` documentando as chaves esperadas (sem valores reais).
4. Centralize o tratamento de erros (middleware/handler único), não `try/except`/`try/catch` espalhados retornando formatos inconsistentes.
5. Preserve o comportamento observável: os mesmos endpoints, com os mesmos métodos HTTP, paths e contratos de resposta (status codes, formato do payload), devem continuar respondendo. Não remova funcionalidade. Isso se refere ao **contrato externo** do endpoint — não à lógica interna que a própria Fase 2 marcou como CRITICAL/HIGH. Uma regra de negócio ingênua ou insegura apontada na auditoria deve ser substituída por uma implementação correta (ainda que simulada/mock, ver playbook #13), e não preservada "para não mudar o comportamento".
6. **Valide o resultado**:
   - Instale dependências se necessário.
   - Suba a aplicação (boot) e confirme que inicia sem erro.
   - Bata em uma amostra representativa dos endpoints originais (ex.: `curl`) e confirme que respondem com status esperado.
   - Encerre o processo de teste ao final.
7. Imprima o resultado **exatamente** neste formato:

```
================================
PHASE 3: REFACTORING COMPLETE
================================
New Project Structure:
<árvore de diretórios final, resumida>

Validation
  ✓ Application boots without errors
  ✓ All endpoints respond correctly
  ✓ Zero anti-patterns remaining
================================
```

Se algum item da validação falhar, **não declare sucesso** — corrija e valide novamente antes de reportar.

## Regras gerais

- Sempre trabalhe em arquivo:linha exatos — nunca diga apenas "código ruim", cite o sinal concreto.
- Nunca pule a pausa de confirmação da Fase 2.
- Adapte-se ao nível de organização já existente no projeto — a Fase 3 de um projeto já parcialmente em camadas não deve ter as mesmas transformações de um monólito de 4 arquivos.
- Este skill deve funcionar de forma idêntica independente da linguagem/framework do projeto-alvo.
