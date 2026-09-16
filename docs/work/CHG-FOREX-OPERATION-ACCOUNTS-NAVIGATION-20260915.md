# CHG-FOREX-OPERATION-ACCOUNTS-NAVIGATION-20260915 — contrato e compreensão

```text
schema: jp-harness/chg/v1
change_id: CHG-FOREX-OPERATION-ACCOUNTS-NAVIGATION-20260915
status: approved
objective: Mover a única superfície de Contas para a navegação local de Operação, na ordem Painel, Contas e Motor, sem alterar o cadastro ou seus dados.
risk_level: N1
authority_required: A2
target:
  root: /Users/joaopauloalves/.codex/forex-operation-accounts/20260915/product
  branch: codex/forex-operation-accounts-navigation-20260915
  baseline_sha: 8b2ef27120f6f42e273241541d76957a6910e7df
scope:
  allowed_files:
    - index.html
    - src/js/20-ui/13-exec-views.js
    - src/js/40-app/01-navigation.js
    - src/js/40-app/13-dashboard-layout.js
    - src/js/manifest.json
    - tools/exec_submenu_test.py
    - tools/forex_navigation_journey_test.py
    - tools/fx_consolidated_ui_test.py
    - tools/fx_planning_test.py
    - tools/navigation_ia_test.py
    - docs/architecture/NAVIGATION-HIERARCHY.md
    - docs/architecture/CODE-MAP.md
    - docs/work/CHG-FOREX-OPERATION-ACCOUNTS-NAVIGATION-20260915.md
    - build-id.js
    - dist/JP_Wealth_Risk_Terminal_V9.1_PORTABLE.html
  allowed_actions:
    - edição N1 delimitada
    - testes focais e regressões pertinentes
    - derivados oficiais
    - recuperação e evidência externas
  forbidden_actions:
    - staging
    - commit
    - push
    - pull
    - PR
    - merge
    - deploy
    - schema, migração, persistência ou cálculo financeiro
    - reset, stash ou alteração de worktrees concorrentes
data:
  source_of_truth: A única árvore DOM e os escritores cadastrais existentes de Contas.
  schema_change: forbidden
  persistence_change: forbidden
derived_artifacts:
  generation_command: python3 tools/rebuild_monolith.py
  manual_edit: forbidden
rollback:
  scope: Somente este delta na worktree autorizada; não tocar main, stashes ou outras worktrees.
approved_by: Proprietário, plano Forex — Contas como subseção de Operação, seguido de Autorizo implementação.
approved_at: 2026-09-15
```

```text
schema: jp-harness/ctx/v1
context_change_id: CTX-FOREX-OPERATION-ACCOUNTS-NAVIGATION-20260915
status: approved
mode: CONCORRENTE
create:
  - docs/work/CHG-FOREX-OPERATION-ACCOUNTS-NAVIGATION-20260915.md
modify:
  - docs/architecture/NAVIGATION-HIERARCHY.md
  - docs/architecture/CODE-MAP.md
preserve:
  - main, stash, evidências e worktrees concorrentes
  - cadastro, vínculos MT5, importações, backup e Finalizar Sessão
  - preferências existentes do Editor, rascunhos e foco
do_not_touch:
  - AGENTS, Harness, skills, CI ou gates
  - Estatuto, Anexo e parâmetros financeiros
```

## Brief

**Finalidade.** JP Wealth mantém um registro local auditável de operação e
cadastros. A mudança reduz a distância entre a conta que o operador gerencia e
a tela na qual prepara a operação; não altera qualquer decisão V11.

**Comportamento.** Na base `8b2ef27120f6`, Contas é um filho N2 visível de
Forex e já possui uma árvore única com `#contas`, `#contasWidgetGrid`, os
formulários e os listeners cadastrais. Depois deste delta, Forex terá cinco
filhos. `#contas` continuará a ser a mesma árvore, alternada por
`hidden`/`inert` como a visão local `accounts` de `#exec`, na sequência Painel,
Contas e Motor. Histórico permanece local de Contabilidade.

**Consumidores e compatibilidade.** `01-navigation.js` é o resolver canônico;
`13-exec-views.js` já controla as visões locais; `13-dashboard-layout.js`
reconhece o proprietário físico dos widgets para preservar as preferências v6.
Os aliases `contas` e `forex-account` passam pelo mesmo plano de navegação de
Operação/Contas. Dashboard, Consolidado, Motor, busca e Configurações seguem
esses aliases sem rota, store, cópia ou migração nova.

**Limites.** Não mudar dados de conta, vínculo MT5, importação, backup,
Finalizar Sessão, cálculos, parâmetros, contas ativas ou preferências gravadas.
Rascunhos da Operação devem pedir decisão explícita antes de trocar para Contas
ou Motor; o fechamento de qualquer diálogo devolve foco ao acionador existente.

**Fontes e evidência de leitura.** `AGENTS.md` (regras A2/N1 e separação de
gates), `README.md`, `docs/governance/CONTEXT-MAP.md`,
`docs/architecture/NAVIGATION-HIERARCHY.md`, `01-navigation.js`,
`13-exec-views.js` e `13-dashboard-layout.js` foram lidos na base declarada.
O preflight de edição passou na branch indicada com árvore inicialmente limpa.
O plano fornecido pelo proprietário é a decisão de produto; nenhuma fonte
financeira é consumida nem reinterpretada neste lote.

## Critérios e provas

- Cinco filhos Forex na ordem aprovada; três visões locais de Operação na ordem
  Painel, Contas e Motor.
- `contas` e `forex-account` selecionam `Forex → Operação → Contas` sem um
  destino visível de segundo nível.
- A árvore e renderizador de Contas são únicos; cadastro, edição, remoção,
  importação e atalhos existentes continuam funcionais.
- Um rascunho de Operação bloqueia Contas e Motor até Salvar ou Descartar;
  preferências do Editor não são regravadas pela navegação.
- Regressões de navegação, Contas, Consolidado/importação, Planejamento e
  jornada real em temas e larguras distintas passam antes de candidate.

Aceite humano, candidate, commit, push, PR, CI remota, merge e deploy são
gates posteriores e não são criados por este contrato.
