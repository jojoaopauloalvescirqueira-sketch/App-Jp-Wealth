# CHG-JPW-CAIXA-ANUAL-NAME-20261028

```json
{
  "schema": "jp-harness/chg/v1",
  "change_id": "CHG-JPW-CAIXA-ANUAL-NAME-20261028",
  "status": "approved",
  "risk_level": "N1",
  "authority_required": "A2",
  "approved_by": "human user",
  "approval": "call_04e699dcb5fb4ad5ace8760f62dafd8c, branch and bounded rename",
  "branch": "codex/caixa-anual-revisao-20261028",
  "baseline_sha": "3e24f60f8cfe87f79335f40e95a0927379a9f834",
  "allowed": [
    "public labels for annual management in index.html, navigation, Dashboard/layout, Notes, Dante, Forex shortcut, annual info",
    "current annual/navigation docs names",
    "docs/work/*CAIXA-ANUAL*",
    "docs/work/ACTIVE-TASK.md bounded current pointer",
    "docs/validation/caixa-anual-revisao-20261028/",
    "official generated artifacts"
  ],
  "invariants": [
    "IDs/aliases/progress/data unchanged",
    "annual engine/state and financial writers unchanged",
    "all preexisting work preserved",
    "review findings reported, not repaired"
  ],
  "forbidden": [
    "financial formulas/data/migration",
    "new dependencies",
    "AGENTS/skills/global memory edits",
    "commit/merge/push/publication"
  ],
  "rollback": "Selective reverse rename only using scratch baseline and patch; no global reset/stash"
}
```
