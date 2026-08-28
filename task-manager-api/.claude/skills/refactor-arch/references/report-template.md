# Template do Relatório de Auditoria (Fase 2)

Use **exatamente** este formato ao gerar o relatório e ao salvá-lo em `reports/audit-project-N.md`. Não altere os separadores `====`.

```
================================
ARCHITECTURE AUDIT REPORT
================================
Project: <nome do projeto>
Stack:   <linguagem + framework>
Files:   <N> analyzed | ~<LOC> lines of code

Summary
CRITICAL: <n> | HIGH: <n> | MEDIUM: <n> | LOW: <n>

Findings

[<SEVERITY>] <Título curto do anti-pattern>
File: <caminho/arquivo.ext>:<linha ou linha-inicial-linha-final>
Description: <o que foi encontrado, concreto e específico ao trecho de código>
Impact: <consequência prática — segurança, manutenção, performance, etc.>
Recommendation: <o que fazer para corrigir, referenciando o padrão do playbook>

[<SEVERITY>] <próximo achado...>
File: ...
Description: ...
Impact: ...
Recommendation: ...

(... um bloco por finding, sempre com os 4 campos: File, Description, Impact, Recommendation ...)

================================
Total: <N> findings
================================
```

Ao final do relatório impresso no terminal (não no arquivo salvo), acrescente a pergunta de confirmação obrigatória da Fase 2:

```
Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]
```

## Regras de formatação

1. **Ordenação obrigatória**: os findings devem aparecer agrupados e ordenados por severidade, na ordem CRITICAL → HIGH → MEDIUM → LOW. Dentro da mesma severidade, ordene pela ordem em que os arquivos aparecem no projeto.
2. **`File:` sempre com linha exata** — nunca "em algum lugar do arquivo X". Use `arquivo:linha` para um ponto único, ou `arquivo:linha_inicial-linha_final` para um trecho/bloco.
3. **`Description:` é factual** — descreva o que o código faz, não uma opinião genérica ("código ruim" não é aceitável; "query monta SQL concatenando `id` recebido da URL sem sanitização" é aceitável).
4. **`Impact:`** conecta o achado a uma consequência real (segurança, dado corrompido, impossibilidade de testar, degradação de performance, etc.).
5. **`Recommendation:`** deve apontar para a transformação correspondente no `refactoring-playbook.md` (pode citar o nome do padrão de transformação).
6. O `Summary` deve bater exatamente com a contagem real de findings por severidade listados abaixo dele.
7. O `Total` no rodapé deve ser a soma do `Summary`.
