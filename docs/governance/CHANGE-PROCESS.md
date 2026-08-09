# Processo de mudanca controlada

## 1. Congelar a fronteira

Registrar branch, `BASE_SHA`, arvore de trabalho, objetivo e arquivos permitidos. Para auditoria, nao editar. Para implementacao, usar branch de tarefa e preflight aprovado.

## 2. Classificar e autorizar

| Nivel | Superficie | Minimo exigido |
|---|---|---|
| N0-D | documentos, governanca, harness | A2, diff e gate fast |
| N0-V | CSS, texto, layout | A2, desktop/mobile e temas aplicaveis |
| N1 | comportamento nao normativo | A2, teste focado e standard |
| N2 | estado, backup, credencial, seguranca | A3, backup/fixture, ida e volta, full |
| N3 | regra financeira/normativa | A4, decisao citavel, exemplos, full e aceite humano |

Mudanca documental que altera obrigacoes dos agentes e N0-D; mudanca em um teste pode ser N1 se reduzir ou ampliar contrato funcional. Alterar expectativa apenas para acompanhar o produto exige evidencia de que o novo comportamento foi deliberadamente aprovado.

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
