# Processo de mudanca controlada

## 1. Congelar a fronteira

Registrar branch, `BASE_SHA`, arvore de trabalho, objetivo e arquivos permitidos. Para auditoria, nao editar. Para implementacao, usar branch de tarefa e preflight aprovado.

## 2. Classificar e autorizar

| Nivel | Superficie | Minimo exigido |
|---|---|---|
| N0-D | documentos informativos sem alterar obrigações, norma ou controles | A2, diff e gate fast |
| N0-V | CSS, texto, layout | A2, desktop/mobile e temas aplicaveis |
| N1 | comportamento nao normativo | A2, teste focado e standard |
| N2 | estado, backup, credencial, seguranca | A3, backup/fixture, ida e volta, full |
| N3 | regra financeira/normativa, segurança crítica ou control plane | A4, CHG dedicado, full, auditoria independente e aceite humano; evidências próprias do domínio |

Classificação e autoridade canônicas: [AGENTS.md](../../AGENTS.md), seções
"Classificação e autoridade" e "Política Git comum". Alterar instruções, políticas,
gates, validadores, CI/proteções, schemas de contrato, templates ou testes do Harness
é mudança de **control plane N3**, mesmo sem alterar runtime. Harness §28 exige
A3 no mínimo; a exigência local de **A4 para N3 permanece**. O rótulo A4 não
autoriza Git/publicação nem amplia o escopo recebido. O candidate de instruções
não pode autorizar seu próprio executor.

Exclusivamente para `CHG-HARNESS-HISTORICAL-UNRESOLVED-FAILURE-20260925`, a
autorização humana explícita A3 cobre edição reversível isolada, testes do control
plane e auditoria, conforme Harness §28. Isso não reclassifica o risco N3 nem
dispensa A4 para outro N3 ou ação futura irreversível/de produção.

A presença física da política §19.1 no Harness externo e o `status: approved`
desse CHG não a tornam vigente. Antes de aplicar `REASSESS_EXISTING_EVIDENCE`,
o auditor deve conferir o registro de ativação: versão/hash final da fonte,
fingerprint, parecer independente N3 e Human Acceptance do mesmo candidate de control plane,
integração autorizada das referências e ativação explícita da fonte externa.
Sem esse registro, a exceção fica bloqueada; recibo `PRODUCT_FAIL` segue falho.

N3 financeiro mantém decisão normativa citável, exemplos calculados e testes de
caracterização. N3 de control plane exige matriz antes/depois, testes estruturais,
carregamento/comportamento observável e auditoria independente focal; o full do
produto não substitui esses testes. Distinguir indisponibilidade de ambiente de
aprovação. Uma mudança de produto não pode enfraquecer seu próprio juiz.

Mudança de teste funcional pode ser N1 conforme efeito, exceto quando alcança
control plane ou contrato N2/N3. Alterar expectativa apenas para acompanhar o
produto exige evidência de comportamento deliberadamente aprovado; não ajustar
gates para obter aprovação.

## 3. Definir o contrato

Antes do codigo, registrar:

- estado atual observado;
- comportamento desejado;
- invariantes que nao podem mudar;
- dados antigos que devem continuar validos;
- criterio objetivo de sucesso;
- rollback ou recuperacao.

## 4. Implementar

- Menor diff coerente.
- Uma causa raiz por mudanca.
- Sem formatacao ou renomeacao ampla adjacente.
- Teste de regressao antes ou junto da correcao quando praticavel.
- `DEFAULTS`, `migrate()`, importacao e exclusao nunca mudam sem N2.
- Constantes e formulas nunca mudam sem N3.

## 5. Verificar o candidato

Use `docs/governance/QUALITY-GATES.md`. Evidencia e valida apenas para o conteudo testado; qualquer mudanca material posterior invalida o gate afetado.

## 6. Revisar o diff

```bash
git status --short
git diff --check
git diff --stat
git diff
```

Responder:

1. Qual causa foi resolvida?
2. Qual regra ou decisao foi aplicada?
3. O estado persistido mudou?
4. Quais cenarios foram realmente executados?
5. Qual risco residual permanece?
6. Como reverter sem perder dados?

## 7. Promover

Editar, testar, revisar, commitar, enviar, integrar e publicar sao gates independentes. Nenhuma autorizacao e transitiva. Nao criar commit com gate aplicavel falhando, salvo commit explicitamente solicitado para preservar um baseline vermelho e identificado como tal, ou a excecao formal e integral do Harness §19.1 ja vigente por registro de ativacao, apos `AUDIT_PASS_WITH_DEBT`, aceite humano e autorizacao especifica de commit. Um gate bruto com `PRODUCT_FAIL` continua falho e nao pode ser contado como verde. A politica `HISTORICAL_UNRESOLVED_FAILURE` satisfaz somente o gate de auditoria quando o finding estruturado e o parecer independente a reconhecerem; a promocao ainda depende dos demais gates, das protecoes tecnicas e de autorizacoes separadas. Executor, checklist ou validador nao podem autopromover o candidate.

Modelo de commit, quando autorizado:

```text
<tipo>(<area>): descricao objetiva

Nivel: N0-D | N0-V | N1 | N2 | N3
Regra: nenhuma | Art. X | ADR-NNN
Dados: sem mudanca | schema vX -> vY
Testes: comandos e resultado
```
