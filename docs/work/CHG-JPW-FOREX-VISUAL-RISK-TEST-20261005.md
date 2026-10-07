# CHG-JPW-FOREX-VISUAL-RISK-TEST-20261005

```yaml
{
  "schema": "jp-harness/chg/v1",
  "change_id": "CHG-JPW-FOREX-VISUAL-RISK-TEST-20261005",
  "status": "approved",
  "objective": "Novo focal visual e atualização apenas das expectativas de apresentação deliberadamente aprovadas; oráculos financeiros e gates preservados",
  "risk_level": "N3",
  "authority_required": "A4",
  "approved_by": "Proprietário: PLEASE IMPLEMENT THIS PLAN: JP Wealth — evolução da conta e risco visual no Forex, incluindo contrato separado para expectativas de testes (2026-10-05)",
  "target": {
    "root": "/Users/joaopauloalves/.codex/.chatgpt-projects/g-p-6a4fc0aa51dc8191af013579f37179a3/outputs/jpw-forex-visual-risk-20261005/candidate",
    "branch": "codex/forex-visual-risk-20261005",
    "baseline_sha": "ac3a2faffeb398357ff105adbf1d47f70ca309bd"
  },
  "scope": {
    "allowed_files": [
      "tools/forex_visual_risk_test.py",
      "tools/fx_consolidated_ui_test.py"
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
    "Single main chart; temporal axis only for unambiguous dates; accessible exact values and gaps",
    "Confirmed saved open operationalRisk equals workbook; zero is distinct from absent; partial coverage explicit",
    "Risk chart expansion transient and responsive by useful width; draft/input preserved",
    "No financial/domain/MT5 changes; existing 20-column proportions preserved"
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
      "/Users/joaopauloalves/.codex/.chatgpt-projects/g-p-6a4fc0aa51dc8191af013579f37179a3/outputs/jpw-forex-visual-risk-20261005/baseline.tar.gz"
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
  "approved_at": "2026-10-05T19:13:12.308973+00:00",
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
  "context_change_id": "CTX-JPW-FOREX-VISUAL-RISK-TEST-20261005",
  "status": "approved",
  "root": "/Users/joaopauloalves/.codex/.chatgpt-projects/g-p-6a4fc0aa51dc8191af013579f37179a3/outputs/jpw-forex-visual-risk-20261005/candidate",
  "mode": "CONCORRENTE",
  "approved_branch": "codex/forex-visual-risk-20261005",
  "create": [
    "docs/work/CHG-JPW-FOREX-VISUAL-RISK-TEST-20261005.md"
  ],
  "modify": [],
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
  "approved_by": "Proprietário: PLEASE IMPLEMENT THIS PLAN: JP Wealth — evolução da conta e risco visual no Forex, incluindo contrato separado para expectativas de testes (2026-10-05)",
  "approved_at": "2026-10-05T19:13:12.308973+00:00",
  "expires_on": [
    "target root/branch/base changes",
    "scope or authority changes"
  ]
}
```

A aprovação conversacional autoriza somente este escopo. Horário acima é o registro local. Aceite e Git/publicação permanecem separados. DD14 herdado não é reclassificado.
