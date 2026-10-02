# CHG-JPW-LOT-REFERENCES-20261001

```yaml
{
  "schema": "jp-harness/chg/v1",
  "change_id": "CHG-JPW-LOT-REFERENCES-20261001",
  "status": "approved",
  "objective": "Separar referência inicial SI e teto corrente por regime min(SI,Equity)",
  "risk_level": "N3",
  "authority_required": "A4",
  "approved_by": "Proprietário, instrução atual PLEASE IMPLEMENT THIS PLAN: JP Wealth — Operação como Execution Board, inclusive seção Motor e CHG N3/A4",
  "target": {
    "root": "/private/tmp/jpw-cockpit-ui-20260930",
    "branch": "codex/jpw-cockpit-ui-20260930",
    "baseline_sha": "deffc5061fe2eff3d83b6f6e742fa105ac9c5b06",
    "fingerprint": "e6d2d9cdfc61e2e908474b090b60222b73e3470f746c530eb27b94aba2326c32"
  },
  "scope": {
    "allowed_files": [
      "src/js/10-domain/18-execution-board-model.js (lot reference outputs only)",
      "tools/forex_lot_references_test.py",
      "tools/forex_execution_projection_test.py (explicit reference semantics only)",
      "docs/work/CHG-JPW-LOT-REFERENCES-20261001.md",
      "docs/architecture/FOREX-EXECUTION-BOARD.md (two reference meanings only)"
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
    "reference initial = factor * SI / identified notional per lot",
    "current cap = factor * min(SI, equity) / identified notional per lot",
    "existing normal/restrictive current outputs preserved for compatibility",
    "neither reference authorizes lot, rounds to symbol step or fills order; pending policy unchanged"
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
