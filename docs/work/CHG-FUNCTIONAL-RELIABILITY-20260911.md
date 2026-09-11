# CHG-FUNCTIONAL-RELIABILITY-20260911 — campanha finita

```yaml
schema: jp-harness/chg/v1
change_id: CHG-FUNCTIONAL-RELIABILITY-20260911
status: approved
objective: Coerência entre resultado comunicado, memória e gravação nas seis jornadas delimitadas.
risk_level: N2
authority_required: A3
target:
  root: /Users/joaopauloalves/.codex/reliability-campaigns/20260911/product
  branch: codex/functional-reliability-20260911
  baseline_sha: 09c1427f4880ef7684b1a6fc4d2bc310e706380f
scope:
  allowed_files:
    - src/js/30-accounting/01-daily-ledger.js
    - src/js/30-accounting/04-patrimonial-simulation.js
    - src/js/30-accounting/05-fx-planning/03-fx-state.js
    - src/js/30-accounting/05-fx-planning/05-fx-ui.js
    - src/js/20-ui/14-nocoda-studies.js
    - src/js/20-ui/15-pivot-studies.js
    - src/js/40-app/14-mvp-notes.js
    - src/js/10-domain/13-alladin.js
    - tools/forex_persistence_contract_test.py
    - tools/studies_notes_persistence_contract_test.py
    - tools/alladin_civil_date_test.py
    - src/js/manifest.json
    - build-id.js
    - dist/JP_Wealth_Risk_Terminal_V9.1_PORTABLE.html
    - docs/work/ACTIVE-TASK.md
    - docs/work/CHG-FUNCTIONAL-RELIABILITY-20260911.md
  forbidden_files: [skills, AGENTS.md, CLAUDE.md, sw.js, .github, docs/normative, src/js/00-core/03-default-state.js, src/js/00-core/04-persistence.js]
  allowed_actions: [investigação, testes sintéticos, correções N1/N2 demonstradas, branch/worktree isolada, geração oficial, auditoria, checkpoint]
  forbidden_actions: [commit do produto, tag, push, PR, merge, deploy, reset, stash, rebase, alteração de schema, mudança normativa, reindexação]
  regressions_forbidden: [perda silenciosa, sucesso falso, duplicação, rollback global, enfraquecimento de proteção]
derived_artifacts:
  allowed: [build-id.js, dist/JP_Wealth_Risk_Terminal_V9.1_PORTABLE.html]
  generation_commands: [python3 tools/rebuild_monolith.py]
  manual_edit: forbidden
external_side_effects:
  network: allowed
  allowed_targets: [loopback com fixtures nominais existentes; consulta inicial origin main somente leitura]
  temporary_artifacts: allowed
  cleanup_required: true
data:
  test_policy: synthetic_only
  approved_real_data: []
  schema_change: forbidden
toolchain:
  dependency_changes: []
  allowed_processes: [Python existente, Chromium Playwright existente, servidor local, Git fixtures próprias]
acceptance_criteria:
  - Reavaliar seis achados em baseline atual; classificar resultado e evidência.
  - Falha comprovada não confirma nem conserva ato recusado na memória confirmada.
  - Rascunho de sessão recuperável; retry explícito único; outra gravação não incorpora recusado.
  - UNKNOWN conserva tentativa e barreira existente, sem rollback nem retry cego.
  - Sucesso preserva valores, IDs, logs, formatos, cálculos e consumidores.
  - Datas civis novas válidas no ledger Alladin sem alterar leitura histórica ou política temporal.
  - Reservas/clearance somente investigados, decisão N3 separada.
  - Candidate identificado, testes, auditoria e recuperação vinculados, sem aceite ou integração.
approved_tests:
  - Regressões focais antes/depois por API existente e interação real.
  - Quota, false, exceção anterior/posterior, UNKNOWN, conflito, retry, cancelamento, reload e gravação posterior.
  - Consumers e limites de sequência/log; entrada inválida; duas abas quando pertinente.
  - FAST, standard e FULL existentes no candidate final; reprodutibilidade e PWA.
  - Segurança/escopo/preservação/recuperação e auditoria independente read-only.
rollback:
  source: [baseline.tar identificado; diff e snapshot do delta para recuperação em cópia]
  application_state: [somente perfis sintéticos isolados; nenhum dado real tocado]
  data: [sem migração nem escrita em perfis do proprietário]
  environment: [encerrar somente processos próprios; preservar outras worktrees e stash]
  verification: [comparar hashes do checkpoint e alvos protegidos]
approved_by: proprietário; pedido /goal anexado 4067df9e-f8a4-4695-8926-3a127977a867
approved_at: 2026-09-11
expires_on: [drift material, ampliação material, N3 sem decisão, necessidade de alterar proteções]
```

## Brief específico e fontes
O JP Wealth é PWA local para gestão financeira/risco; esta tarefa reduz perda silenciosa e falsa confirmação. Forex grava fechamento diário e planejamento; Research conserva estudos analíticos; Notas conserva conteúdo e organização; Alladin registra fatos econômicos append-only. A base examinada tem mutações que ignoram save(), mas isso só autoriza patch após contraprova sintética atual.

Fontes comuns: AGENTS, README, PROJECT-CONTEXT, CONTEXT-MAP, STATE-SCHEMA (desfecho), DB-STORAGE-GOVERNANCE regra7, DATA-RECOVERY, SECURITY-MODEL, QUALITY-GATES; fontes específicas FX-PLANNING, NOCODA-STUDIES, PIVOT-STUDIES, ALLADIN e Feature Atlas parcial. Harness v2.0, SHA-256 c1b5ca9da4dfa2c9a9d1fa3d87a9f7ef9c4cb741fffeedee33d37978f5b800c8, §§12–20,23–24,36–57. Hashes dos arquivos de base estão no registro preservation-before e baseline.tar; leituras históricas são pistas, não novas execuções.

Antes/depois esperado: manter validações de domínio, aplicar ato, confirmar gravação antes de sucesso/limpeza. Recusa restaura somente agregado/efeitos próprios; exceção de save não prova ausência física. Preservar dados desconhecidos, log completo no limite400, referências, globais, recuperação e guarda concorrente. O global save(), PF e a finalização formal não serão reescritos.

OPEN-06 era listado N3 na revisão histórica. O recorte atual é N2 de validação de entrada expressamente coberto pelo proprietário quando contrato exigir data civil válida: ALLADIN §reversão exige data válida e UI declara AAAA-MM-DD. Não se escolhe data financeira, proibição futura, retroatividade ou migração. Restringir effectiveAt dos novos lançamentos/estornos; acquisitionDate e leitura dos históricos ficam preservadas. Divergência material interrompe o item.

OPEN-05 é N3/A4 apenas diagnóstico: snapshots de onboarding e cálculo de reservas vigente podem divergir; conflito PDF/Anexo e motor legado não serão arbitrados. A campanha pode terminar PARTIALLY_READY_FOR_HUMAN_DECISION com esse item delimitado.

## Delimitação técnica e consumidores
- Diário: salvar/sobrescrever/remover via bindContab e renderLedger; ledger, saldoAtu, log DG e resumos/MEI são consumidores. Não recalcular cadeia posterior nem mudar fórmulas.
- Planejamento: seis mutações de 03-fx-state e respectivos formulários 05-fx-ui; baseline/revisões/realizado/aportes e logs.
- NoCoda: salvar estudo vigente; geometria/catálogo/consumidores do Dashboard intactos.
- Pivots: criar/excluir estudo e salvar/excluir pivot, confirmando preservação de seleção/rascunho.
- Notas: CRUD e consumidores de salvar/concluir/excluir; pastas somente se contraprova demonstrar mesma causa/referências afetadas. Preferências existentes servem como gravação posterior, sem refatoração.
- Alladin: novos fatos e reversões com data civil; mantém leitura histórica, ID/sequência, regras de saldo e estorno.
Manifest: somente SHA-256 das fontes alteradas, sem mudar ordem ou formato. Nenhuma API pública criada apenas para teste. Novos testes em tools seguem fixtures e servidores existentes; sem infraestrutura nova de avaliação.

## Evidências, delegação e freeze
Destino durável: /Users/joaopauloalves/.codex/reliability-campaigns/20260911/evidence/.
Baseline fiel de arquivos rastreados em ../baseline; sem dados/backups ignorados. Primeiro fixar oráculos/testes e executar baseline. Cada lotista edita somente sua fronteira atribuída e registra comando, resultado bruto e limitações. Root mantém contrato/manifest/derivados. Auditor final independente dos autores, read-only. Não executar FULL por patch. Revisão após freeze gera nova identidade e revalidação afetada.

## CTX delimitado
```yaml
schema: jp-harness/ctx/v1
context_change_id: CTX-FUNCTIONAL-RELIABILITY-20260911
status: approved
root: /Users/joaopauloalves/.codex/reliability-campaigns/20260911/product
mode: SEQUENCIAL
approved_branch: codex/functional-reliability-20260911
create: [docs/work/CHG-FUNCTIONAL-RELIABILITY-20260911.md]
modify: [docs/work/ACTIVE-TASK.md — cabeçalho da tarefa somente]
preserve: [todo histórico de ACTIVE-TASK, checkpoints, stash, outras worktrees]
do_not_touch: [CURRENT-STATE, CODE-MAP, Feature Atlas, skills, Harness, índices, candidate nav-ref-context]
acceptance_criteria: [contrato limitado à autorização vigente; atualização geral somente recomendada]
approved_by: proprietário; formalização operacional do /goal
approved_at: 2026-09-11
```
