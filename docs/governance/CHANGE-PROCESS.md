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

Editar, testar, revisar, commitar, enviar, integrar e publicar sao gates independentes. Nenhuma autorizacao e transitiva. Nao criar commit com gate aplicavel falhando, salvo commit explicitamente solicitado para preservar um baseline vermelho e identificado como tal.

Modelo de commit, quando autorizado:

```text
<tipo>(<area>): descricao objetiva

Nivel: N0-D | N0-V | N1 | N2 | N3
Regra: nenhuma | Art. X | ADR-NNN
Dados: sem mudanca | schema vX -> vY
Testes: comandos e resultado
```
