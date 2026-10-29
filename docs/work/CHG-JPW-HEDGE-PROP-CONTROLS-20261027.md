# CHG-JPW-HEDGE-PROP-CONTROLS-20261027

```json
{
  "schema": "jp-harness/chg/v1",
  "status": "approved",
  "change_id": "CHG-JPW-HEDGE-PROP-CONTROLS-20261027",
  "objective": "Dedicated new regressions and counterproofs, additive gate coverage; no weaker tolerances/timeouts",
  "risk_level": "N3",
  "authority_required": "A4",
  "approved_by": "human user",
  "approved_at": "2026-10-27",
  "target": {
    "root": "/Users/joaoalvescirqueira/Library/Mobile Documents/com~apple~CloudDocs/SOFTWARES & EAS/JP Wealth OS",
    "branch": "codex/mesas-proprietarias-hedge-20261027",
    "baseline_sha": "3e24f60f8cfe87f79335f40e95a0927379a9f834"
  },
  "scope": {
    "allowed_files": [
      "tools/hedge_prop*",
      "tools/ui_visual_quality_test.py",
      "tools/quality_gate.py",
      "tools/regression-memory.json",
      "approved obsolete Tools menu expectations only",
      "docs/work/*HEDGE-PROP*",
      "docs/validation/hedge-prop-20261027/"
    ],
    "forbidden_files": [
      "AGENTS.md",
      "skills/",
      "docs/normative/",
      "mt5/",
      "real user data",
      "financial policy/state/writers"
    ],
    "allowed_actions": [
      "bounded implementation approved in user PLEASE IMPLEMENT THIS PLAN",
      "synthetic focal tests and independent review",
      "official rebuild and full quality gate"
    ],
    "forbidden_actions": [
      "commit",
      "merge",
      "push",
      "publication",
      "new dependencies",
      "financial migration",
      "real-data deletion"
    ]
  },
  "approval": "User approved exact five-section Hedge plan, including formulas/tests; branch call_f53f183420e04e6eafadbc5e4717eebc authorized exact branch and preserving pending work",
  "data": {
    "test_policy": "synthetic_only",
    "approved_real_data": [],
    "schema_change": "none"
  },
  "rollback": {
    "source": [
      "Reverse only this task delta using /private/tmp/jpw-hedge-prop-20261027/baseline-pending.tar.gz and baseline hashes; no reset/stash"
    ],
    "data": [
      "RAM-only simulation; no persistent or financial writes"
    ]
  },
  "acceptance_criteria": [
    "Two screenshot oracles, inputs blank vs zero, costs by mutually exclusive path",
    "Forex-independent Tools navigation and no financial reads/writes",
    "New full suite on frozen candidate; human acceptance separate"
  ],
  "derived_artifacts": {
    "allowed": [
      "build-id.js",
      "dist/JP_Wealth_Risk_Terminal_V9.1_PORTABLE.html",
      "src/js/manifest.json",
      "sw.js",
      "src/vendor/ official build envelopes"
    ],
    "generation_commands": [
      "python3 tools/rebuild_monolith.py --refresh-manifest"
    ],
    "manual_edit": "forbidden"
  }
}
```

## Expectativas deliberadamente substituídas

A autorização do plano abrange a nova rota, a lição do Dante e os dois scripts locais, além da substituição apenas das expectativas superadas. `tools/nocuda_tools_test.py` acrescenta somente `tools-prop-firms` à lista exata de Tools. `tools/learning_guide_test.py` verifica62 lições, protegendo as61 identidades anteriores e a nova orientação sem prática, e valida os dois scripts Hedge antes de projetá-los para os oráculos históricos. SHA106, dependências,25 contraprovas anteriores e51 demais funções permanecem; sete contraprovas de scripts são acrescentadas.

Delta e revisão independente em `docs/validation/hedge-prop-20261027/legacy-PROPOSAL.patch` e `legacy-review.md`. O FULL2 bruto114PASS/2PRODUCT_FAIL permanece histórico; o ajuste não o converte em aprovação. Nenhuma mudança de tolerância, timeout, autoridade ou critério financeiro.
