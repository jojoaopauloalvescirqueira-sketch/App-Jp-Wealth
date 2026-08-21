# Mapa de contexto para agentes

## Camadas

| Camada | Fonte | Quando ler | Autoridade | Atualizacao |
|---|---|---|---|---|
| M0 | `docs/normative/` | Qualquer tarefa N3 | Maxima | Somente por decisao humana formal |
| M1 | `PROJECT-CONTEXT.md`, `CURRENT-STATE.md`, `docs/architecture/` | Toda tarefa material | Alta | Apos mudanca material |
| M2 | `docs/decisions/` | Regra ambigua ou decisao existente | Alta se aprovada | Uma decisao por arquivo |
| M3 | `docs/work/ACTIVE-TASK.md` e task brief | Tarefa em curso | Delimitada | Durante a tarefa |
| M4 | `SESSION_HANDOFF.md` | Retomada por outro agente | Informativa | Ao final de trabalho material |
| M5 | `docs/audit/`, `CHANGELOG.md`, historico Git | Investigacao e proveniencia | Evidencial | Conforme eventos |

## Rotas por area

- Risco, fases, MDD, LIFO, lote: M0 + M2 + `docs/architecture/CODE-MAP.md`.
- Persistencia/importacao/reset: `STATE-SCHEMA.md`, `DB-STORAGE-GOVERNANCE.md`, `DATA-RECOVERY.md`.
- PWA/cache: `PWA-UPDATE-LIFECYCLE.md`, `sw.js`, manifest e teste de upgrade.
- Interface: contratos DOM em `index.html`, CSS, script da tela e teste real no
  navegador; navegação global/contextual em
  `docs/architecture/NAVIGATION-HIERARCHY.md`.
- Estudos NoCoda: `docs/architecture/NOCODA-STUDIES.md` — geometria do canal,
  identidade de instrumento e o agregado `S.nocoda`.
- Estudos dos Pivots: `docs/architecture/PIVOT-STUDIES.md` — derivação,
  critério de correção, estatística descritiva e o agregado `S.pivotStudies`.
- Finanças Pessoais: `docs/architecture/PERSONAL-FINANCE.md` — contrato do agregado `S.personalFinance` (schema v1 congelado, BRL_CENTS, materialização de mês, dívida temporal).
- Alladin: `docs/architecture/ALLADIN.md` — contrato do agregado `S.alladin` (schema v2, quatro entidades cadastrais, dinheiro em unidade mínima, write gate transacional, fail-closed). Código em `src/js/10-domain/13-alladin.js` e `src/js/00-core/04-persistence.js`; suítes `tools/alladin_*_test.py`. Spec canônica: JPW-ALLADIN-SPEC V1.2.1 (vault de arquitetura, externa ao repo). Transações, posições, valuation, performance, UI e integrações: não iniciados.
- MEI-JP: fonte normativa aplicavel, implementacao MEI, historico patrimonial e auditoria matematica registrada.
- Governanca/agentes: `AGENTS.md`, esta pagina, `AI-WORKFLOW.md`, `QUALITY-GATES.md` e skills locais.

## Frescor e validade

- `PROJECT-CONTEXT.md` e estavel; altere apenas se arquitetura ou contratos mudarem.
- `CURRENT-STATE.md`, `ACTIVE-TASK.md` e `SESSION_HANDOFF.md` expiram quando o Git ou o runtime divergir.
- Uma auditoria antiga continua historica, mas nao confirma o estado atual.
- Uma evidencia de teste vale apenas para o candidato e ambiente registrados.
- Em conflito, verificar o arquivo atual; memoria de agente nunca vence o disco.

## Exclusoes de contexto

Nao carregar nem reproduzir backups reais, credenciais, exports de navegador, caches, binarios ou todo o historico da conversa. Referencie-os por metadados seguros quando necessario.
