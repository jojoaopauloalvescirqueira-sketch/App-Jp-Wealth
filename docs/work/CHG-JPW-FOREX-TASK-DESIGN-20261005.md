# CHG-JPW-FOREX-TASK-DESIGN-20261005

```yaml
{
  "schema": "jp-harness/chg/v1",
  "change_id": "CHG-JPW-FOREX-TASK-DESIGN-20261005",
  "status": "approved",
  "objective": "Forex sóbrio com navegação por tarefa, consulta histórica independente e ferramentas sob demanda",
  "risk_level": "N1",
  "authority_required": "A2",
  "approved_by": "Proprietário: PLEASE IMPLEMENT THIS PLAN — JP Wealth Forex com design sóbrio e navegação por tarefa",
  "target": {
    "root": "/Users/joaopauloalves/Library/Mobile Documents/com~apple~CloudDocs/99X - Codex/Migracao-2026-10-05/Projetos Work/g-p-6a4fc0aa51dc8191af013579f37179a3/outputs/jpw-forex-task-design-20261005/candidate",
    "branch": "codex/forex-professional-panel-20261005",
    "baseline_sha": "ac3a2faffeb398357ff105adbf1d47f70ca309bd",
    "baseline_build": "df2caa32013cb2cc"
  },
  "scope": {
    "allowed_files": [
      "index.html",
      "src/styles/app.css",
      "src/js/40-app/01-navigation.js",
      "src/js/40-app/11-operational-shell.js",
      "src/js/40-app/13-dashboard-layout.js",
      "src/js/20-ui/16-operation-history.js",
      "src/js/20-ui/26-forex-engine-views.js",
      "src/js/20-ui/28-fx-consolidated.js",
      "src/js/20-ui/30-execution-board.js",
      "src/js/20-ui/31-forex-accounts.js",
      "src/js/30-accounting/02-accounting-engine.js",
      "src/js/30-accounting/05-fx-planning/05-fx-ui.js",
      "README.md",
      "docs/architecture/FOREX-CONSOLIDATED.md",
      "docs/architecture/FOREX-EXECUTION-BOARD.md",
      "docs/work/ACTIVE-TASK.md",
      "docs/work/*JPW-FOREX-TASK-DESIGN-20261005*"
    ],
    "forbidden_files": [
      "AGENTS.md",
      "skills/**",
      "src/js/00-core/**",
      "mt5/**",
      "tools/quality_gate.py",
      ".github/**",
      "src/js/10-domain/17-fx-consolidated-model.js",
      "src/js/10-domain/00-forex-engine.js",
      "src/js/10-domain/00-forex-state.js",
      "src/js/10-domain/**"
    ],
    "allowed_actions": [
      "bounded_edit",
      "synthetic_tests",
      "independent_audit",
      "official_generation"
    ],
    "forbidden_actions": [
      "commit",
      "push",
      "merge",
      "publish",
      "real_data_reads",
      "real_data_mutation"
    ],
    "regressions_forbidden": [
      "financial formulas",
      "persistence and schemas",
      "twenty columns",
      "drafts and financial guards"
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
    "schema_change": "forbidden",
    "approved_real_data": []
  },
  "acceptance_criteria": [
    "Mesmas fórmulas, dados e registros; 20 colunas14/36desktop16/48touch",
    "Ferramentas inicialmente recolhidas preservam identidade de campos, rascunhos, cursor e seleção",
    "Histórico consulta contas ativas/arquivadas em RAM, sem trocar operacional",
    "Sete destinos e aliases com agrupamento não interativo; quatro layouts e mobile",
    "Cabeçalhos compactos, tabs visíveis e ausência de sobreposição das ações flutuantes no Forex",
    "Medições comparáveis mostram aproximação dos gráficos/grade",
    "DD14 continua falha financeira separada; raw gates preservados"
  ],
  "approved_tests": [
    "focal baseline and candidate",
    "browser dimensions and tasks",
    "financial regressions",
    "standard",
    "raw full",
    "independent audit"
  ],
  "rollback": {
    "source": [
      "/Users/joaopauloalves/Library/Mobile Documents/com~apple~CloudDocs/99X - Codex/Migracao-2026-10-05/Projetos Work/g-p-6a4fc0aa51dc8191af013579f37179a3/outputs/jpw-forex-task-design-20261005/baseline.tar.gz"
    ],
    "application_state": [
      "unchanged; synthetic disposable browser only"
    ],
    "data": [
      "no real-data access or financial schema change"
    ],
    "environment": [
      "close only disposable test processes"
    ],
    "verification": [
      "compare baseline hashes and rerun affected tests"
    ]
  },
  "approved_at": "2026-10-06T02:01:32.512979+00:00",
  "expires_on": [
    "target root/branch/base changes",
    "scope or authority changes"
  ],
  "external_side_effects": {
    "network": "allowed",
    "allowed_targets": [
      "isolated localhost synthetic fixtures"
    ],
    "temporary_artifacts": "allowed",
    "cleanup_required": true
  },
  "toolchain": {
    "dependency_changes": [],
    "allowed_processes": [
      "Python test runners",
      "existing Playwright Chromium",
      "official generator",
      "local fixture servers"
    ]
  }
}
```
