# CHG-JPW-EXECUTION-WORKBOOK-20261001

```yaml
{
  "schema": "jp-harness/chg/v1",
  "change_id": "CHG-JPW-EXECUTION-WORKBOOK-20261001",
  "status": "approved",
  "objective": "Execution Board adaptado com grade contínua e Matriz/Raiz N/Motor integrados",
  "risk_level": "N1",
  "authority_required": "A2",
  "approved_by": "Proprietário, instrução atual PLEASE IMPLEMENT THIS PLAN: JP Wealth — Operação como Execution Board, inclusive seção Motor e CHG N3/A4",
  "target": {
    "root": "/private/tmp/jpw-cockpit-ui-20260930",
    "branch": "codex/jpw-cockpit-ui-20260930",
    "baseline_sha": "deffc5061fe2eff3d83b6f6e742fa105ac9c5b06",
    "fingerprint": "e6d2d9cdfc61e2e908474b090b60222b73e3470f746c530eb27b94aba2326c32"
  },
  "scope": {
    "allowed_files": [
      "index.html (Forex only)",
      "src/styles/app.css (Execution Board only)",
      "src/js/20-ui/30-execution-board.js",
      "src/js/40-app/01-navigation.js (motor alias only)",
      "src/js/20-ui/13-exec-views.js (motor compatibility only)",
      "src/js/10-domain/04-stop-statistics.js (legacy motor editor forwarding only)",
      "tools/forex_execution_workbook_test.py",
      "tools/forex_execution_table_test.py",
      "tools/forex_execution_board_test.py",
      "tools/forex_clarity_test.py",
      "tools/forex_execution_identity_test.py",
      "tools/forex_execution_market_test.py",
      "tools/phases_visibility_test.py",
      "tools/operation_wiring_test.py",
      "tools/operation_identity_test.py (continuous grade selectors only)",
      "tools/research_navigation_test.py (motor alias expectation only)",
      "tools/exec_three_column_test.py (approved reading order; persisted preference invariant retained)",
      "tools/navigation_ia_test.py",
      "tools/exec_submenu_test.py",
      "docs/architecture/FOREX-EXECUTION-BOARD.md",
      "docs/architecture/FOREX-EXPERIENCE.md",
      "README.md (focal documentation)",
      "docs/work/ACTIVE-TASK.md",
      "docs/governance/CURRENT-STATE.md (focal append)",
      "docs/work/CHG-JPW-EXECUTION-WORKBOOK-20261001.md",
      "docs/work/BRIEF-JPW-EXECUTION-WORKBOOK-20261001.md"
    ],
    "forbidden_files": [
      "AGENTS.md",
      "skills/**",
      "docs/normative/**",
      "src/js/00-core/**",
      "src/js/10-domain/00-forex-engine.js",
      "src/js/10-domain/00-forex-state.js",
      "mt5/**",
      "downloads/**",
      "tools/quality_gate.py",
      "tools/browser_bootstrap_fixture.py",
      "tools/browser_fixture_server.py",
      ".github/**"
    ],
    "allowed_actions": [
      "bounded_edit",
      "synthetic_tests",
      "official_generation",
      "independent_audit"
    ],
    "forbidden_actions": [
      "commit",
      "push",
      "merge",
      "publish",
      "real_profile_reads",
      "real_data_mutation",
      "install_dependencies"
    ],
    "regressions_forbidden": [
      "account/period/currency identity",
      "legacy phases and saved preferences",
      "no financial formulas in UI",
      "no normative homologation or fallback pending parameters"
    ]
  },
  "derived_artifacts": {
    "allowed": [
      "src/js/manifest.json",
      "build-id.js",
      "dist/JP_Wealth_Risk_Terminal_V9.1_PORTABLE.html",
      "src/vendor/pdfjs/runtime-assets.js",
      "src/vendor/normative/statute-payload.js"
    ],
    "generation_commands": [
      "python3 tools/rebuild_monolith.py"
    ],
    "manual_edit": "forbidden"
  },
  "data": {
    "test_policy": "synthetic_only",
    "schema_change": "forbidden"
  },
  "external_side_effects": {
    "network": "allowed",
    "allowed_targets": [
      "isolated localhost fixtures"
    ],
    "temporary_artifacts": "allowed",
    "cleanup_required": true
  },
  "acceptance_criteria": [
    "20 columns; one input per field; scroll contained and fixed ID/instrument",
    "diagnostics RAM distinct from confirmed risk and totals",
    "existing commands, guards, facts, context, preference schemas preserved",
    "tools tabs preserve drafts and legacy motor accesses same implementation"
  ],
  "approved_tests": [
    "focused Execution Board/regressions",
    "synthetic browser tasks/layout matrix",
    "standard",
    "raw full",
    "MT5 host regression",
    "independent design and financial audit"
  ],
  "rollback": {
    "source": [
      "/Users/joaopauloalves/.codex/.chatgpt-projects/g-p-6a4fc0aa51dc8191af013579f37179a3/outputs/jpw-execution-board-20261001/baseline.tar.gz"
    ],
    "verification": [
      "restore only task delta",
      "protected hashes equal baseline"
    ]
  },
  "harness": {
    "path": "/Users/joaopauloalves/Library/Mobile Documents/iCloud~md~obsidian/Documents/2 - TRABALHO/6C - SOFTWARE/A0 - HARNESS - JP Wealth MASTER SPECIFICATION.md",
    "sha256": "b5680c22e44cf3f4a5cd3aa5deeb96f8b65c7908f14543e8c5d7f0c2f4e17b95"
  },
  "inherited_limit": "SOURCE REVISION UNKNOWN; 182 known changes preserved; no Git authority"
}
```

A aprovação vale para este delta candidato, não para homologação, aceite final ou integração. Expectativas visuais deliberadamente alteradas podem adaptar seletores e estrutura; fixtures, gates, clocks, deadlines e assertivas financeiras permanecem.

## Expectativas visuais deliberadas

O fluxo aprovado contexto → resumo → ferramentas → grade estabelece a ordem da superfície Operação. A ordem visual antiga de widgets não governa esta superfície; seu objeto salvo, IDs e tamanhos são preservados, sem migração ou regravação. O focal histórico conferirá a nova ordem e a invariância da preferência, sem alterar oráculos financeiros. Fases contínuas substituem os seletores de disclosure nos focais; o alias Motor retorna a Operação e sua aba Motor.

## Preparação dos focais

O teste Board reutiliza o servidor local já existente no focal de tabela (fila 128) para servir assets da fixture descartável. A adaptação não toca os arquivos compartilhados browser_bootstrap_fixture/browser_fixture_server, interceptações, dados, deadlines, tentativas, assertivas financeiras ou classificação. Os recibos anteriores de resets de transporte permanecem preservados. O focal Wiring prepara uma linha pelo comando Adicionar existente em vez de editar a cópia retornada por accountContext; valores, versões e invariantes anteriores permanecem.
