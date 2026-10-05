# CHG-JPW-OPERATION-PROPORTIONS-20261005

```yaml
{
  "schema": "jp-harness/chg/v1",
  "change_id": "CHG-JPW-OPERATION-PROPORTIONS-20261005",
  "status": "approved",
  "objective": "Operação com proporções de planilha: vinte colunas, controles compactos, estados e detalhes acessíveis",
  "risk_level": "N1",
  "authority_required": "A2",
  "approved_by": "Proprietário: PLEASE IMPLEMENT THIS PLAN: JP Wealth — Operação com proporções de planilha (2026-10-05), inclusive contrato próprio de expectativas visuais",
  "target": {
    "root": "/Users/joaopauloalves/.codex/.chatgpt-projects/g-p-6a4fc0aa51dc8191af013579f37179a3/outputs/jpw-operation-proportions-20261005/candidate",
    "branch": "codex/operation-proportions-20261005",
    "baseline_sha": "a47ebee5a041e990b627dd3319f382ff0fc14add"
  },
  "scope": {
    "allowed_files": [
      "src/styles/app.css",
      "src/js/20-ui/30-execution-board.js",
      "docs/work/ACTIVE-TASK.md",
      "docs/work/BRIEF-JPW-OPERATION-PROPORTIONS-20261005.md",
      "docs/work/CHG-JPW-OPERATION-PROPORTIONS-20261005.md",
      "docs/work/CHG-JPW-OPERATION-PROPORTIONS-TEST-20261005.md",
      "docs/architecture/FOREX-EXECUTION-BOARD.md",
      "README.md"
    ],
    "forbidden_files": [
      "AGENTS.md",
      "skills/**",
      "src/js/10-domain/**",
      "src/js/00-core/**",
      "mt5/**",
      "tools/quality_gate.py",
      ".github/**"
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
    "20 columns and one editor per field",
    "14px/36px desktop;16px/48px touch scaled by font preference",
    "phase heading compact; closed detail no reserved space",
    "Save/Cancel only with draft; focus/scroll preserved",
    "confirmed totals unaffected by draft"
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
      "/Users/joaopauloalves/.codex/.chatgpt-projects/g-p-6a4fc0aa51dc8191af013579f37179a3/outputs/jpw-operation-proportions-20261005/baseline.tar.gz"
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
  "approved_at": "2026-10-05T11:20:16-03:00",
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

```yaml
{
  "schema": "jp-harness/ctx/v1",
  "context_change_id": "CTX-JPW-OPERATION-PROPORTIONS-20261005",
  "status": "approved",
  "root": "/Users/joaopauloalves/.codex/.chatgpt-projects/g-p-6a4fc0aa51dc8191af013579f37179a3/outputs/jpw-operation-proportions-20261005/candidate",
  "mode": "CONCORRENTE",
  "approved_branch": "codex/operation-proportions-20261005",
  "create": [
    "docs/work/CHG-JPW-OPERATION-PROPORTIONS-20261005.md"
  ],
  "modify": [
    "docs/work/ACTIVE-TASK.md",
    "docs/architecture/FOREX-EXECUTION-BOARD.md",
    "README.md"
  ],
  "merge": [],
  "preserve": [
    "AGENTS.md",
    "skills/**",
    "docs/normative/**",
    "mt5/**"
  ],
  "do_not_touch": [
    "src/js/10-domain/**",
    "src/js/00-core/**",
    ".github/**",
    "tools/quality_gate.py"
  ],
  "archive_requires_confirmation": [],
  "source_of_truth": {
    "task": "current user approved plan",
    "finance": "unchanged normative/policy/engine"
  },
  "information_promotion": {
    "rule": "only current scoped behavior; no normative promotion"
  },
  "expiration_rules": {
    "candidate": "revalidate after source change"
  },
  "privacy_actions": [
    "synthetic data only"
  ],
  "acceptance_criteria": [
    "scoped factual context, historic results preserved"
  ],
  "approved_by": "Proprietário: PLEASE IMPLEMENT THIS PLAN: JP Wealth — Operação com proporções de planilha (2026-10-05), inclusive contrato próprio de expectativas visuais",
  "approved_at": "2026-10-05T11:20:16-03:00",
  "expires_on": [
    "target root/branch/base changes",
    "scope or authority changes"
  ]
}
```

Autorização: pedido humano vigente de implementação do plano. approved_at é o instante de registro local dessa autorização conversacional, não o horário da mensagem nem recibo de aceite final. Base e candidate anterior preservados. Sem commit/publicação.
