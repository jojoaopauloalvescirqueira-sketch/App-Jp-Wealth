# CHG-JPW-VISUAL-MEASUREMENT-CONTROLS-20261025

Autorização humana específica registrada; não concede autoridade Git ou para alterar o produto.

```yaml
{
  "schema": "jp-harness/chg/v1",
  "change_id": "CHG-JPW-VISUAL-MEASUREMENT-CONTROLS-20261025",
  "status": "approved",
  "objective": "Reduce repeated remote DOM reads in visual verifier without reducing its criteria, coverage or timeout",
  "risk_level": "N3",
  "authority_required": "A4",
  "target": {
    "root": "/Users/joaoalvescirqueira/Library/Mobile Documents/com~apple~CloudDocs/SOFTWARES & EAS/JP Wealth OS",
    "branch": "codex/dante-guia-20261024",
    "baseline_sha": "a4bf278cd4dc38bbaa5b905ed17a79e33684fb67"
  },
  "scope": {
    "allowed_files": [
      "tools/ui_visual_quality_test.py: centered/controls_geometry exact reviewed batching; additive permanent counterproof within existing ID; additive helper hash in SOURCE_FILES",
      "tools/ui_visual_measurement_test.py: permanent real-browser equivalence/counterproof/RPC test",
      "docs/work/CHG-JPW-VISUAL-MEASUREMENT-CONTROLS-20261025.md",
      "docs/work/ACTIVE-TASK.md: prepend factual scope/status only",
      "docs/validation/dante-20261024/visual-measurement-20261025/",
      "docs/validation/dante-20261024/README.md: execution index only",
      "docs/validation/dante-20261024/POST-CHANGE-AUDIT.md: execution index only"
    ],
    "forbidden_files": [
      "application sources and assets",
      "tools/quality_gate.py",
      "AGENTS.md",
      "skills/",
      "docs/normative/",
      ".github/",
      "tools/regression-memory.json",
      "financial data and writers"
    ],
    "allowed_actions": [
      "apply reviewed two-function patch after relevant baseline proof",
      "add permanent browser counterproof/equivalence tests through existing counterproof ID, preserving 413 required IDs",
      "run focused/all visual/full with same900s cap",
      "record actual results and scope-specific review"
    ],
    "forbidden_actions": [
      "commit",
      "merge",
      "push",
      "publish",
      "dependency installation",
      "real data mutation",
      "change existing financial or visual assertions",
      "raise timeout or tolerance",
      "reduce or skip cases"
    ],
    "regressions_forbidden": [
      "any reduction of 413 required/executed case IDs, 102 gate checks, 2CSSpx tolerance,900second cap",
      "any application bytes changed"
    ]
  },
  "derived_artifacts": {
    "allowed": [
      "scratch and scoped validation receipts/captures"
    ],
    "manual_edit": "allowed"
  },
  "external_side_effects": {
    "network": "allowed",
    "allowed_targets": [
      "loopback synthetic test servers only"
    ],
    "temporary_artifacts": "allowed",
    "cleanup_required": false
  },
  "data": {
    "test_policy": "synthetic_only",
    "approved_real_data": [],
    "schema_change": "forbidden"
  },
  "toolchain": {
    "dependency_changes": [],
    "allowed_processes": [
      "existing isolated Python/Playwright",
      "existing Node/Chrome",
      "read-only Git"
    ]
  },
  "acceptance_criteria": [
    "Baseline actual-browser RPC-budget RED before batch patch; GREEN after",
    "Real-page old versus batched geometry/decisions equivalent for declared mainframe stable controls",
    "Batched controls_geometry rejects text/SVG5px, close20px, ancestor clipping, missing content; fresh mutation and wrong/stale snapshot counterproofs",
    "All original assertions/matrices/required413IDs/102check IDs,2CSSpx/900s preserved",
    "Official full executed on final frozen candidate; independent review; human acceptance separate"
  ],
  "approved_tests": [
    "tools/ui_visual_measurement_test.py",
    "tools/ui_visual_quality_test.py --case regressions / --case all; direct existing counterproofs entry; same900s cap",
    "tools/quality_gate.py --tier full",
    "validate_project.py; agent_preflight; diff-check"
  ],
  "rollback": {
    "source": [
      "/private/tmp/jpw-visual-measurement-20261025/ui_visual_quality_test.before.py",
      "reverse only authorized verifier/contract delta; preserve92oldentries"
    ],
    "application_state": [
      "no application writes"
    ],
    "data": [
      "synthetic profiles only"
    ],
    "environment": [
      "no global changes"
    ],
    "verification": [
      "baseline679hash comparison excluding explicit allowlist"
    ]
  },
  "approved_by": "human user",
  "approved_at": "2026-10-25",
  "approval": "call_2fef00bbd89f4bdf8537108cae962427: Autorizar otimização e nova validação",
  "harness_source": {
    "path": "A0 - HARNESS - JP Wealth MASTER SPECIFICATION.md",
    "sha256": "b5680c22e44cf3f4a5cd3aa5deeb96f8b65c7908f14543e8c5d7f0c2f4e17b95",
    "sections": "12-14,28-30,36-49"
  },
  "expires_on": [
    "scope/root/branch/baseline materially changes"
  ]
}
```

Finalidade: o JP Wealth preserva registros e apresenta controles; esta tarefa atua apenas no juiz de geometria em tools/. Hoje cada botão exige leituras redundantes; depois as mesmas medidas serão lidas juntas após o mesmo scroll e dois frames. Consumidores diretos: centered/controls_geometry e jornadas UI que os chamam. Ficam intactos aplicativo, dados, fórmulas, catálogo de casos, gate e timeout. Baseline e rollback estão no scratch indicado. Fontes: AGENTS.md §§81/93; UI-VISUAL-QUALITY; proposta revisada e hashes em /private/tmp/jpw-dante-calendar-20261025/visual-budget-proposal/.
