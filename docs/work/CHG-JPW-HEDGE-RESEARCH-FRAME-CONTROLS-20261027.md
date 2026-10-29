# Ajuste autorizado — sincronização Research

```json
{
  "schema": "jp-harness/chg/v1",
  "status": "approved",
  "change_id": "CHG-JPW-HEDGE-RESEARCH-FRAME-CONTROLS-20261027",
  "risk_level": "N3",
  "authority_required": "A4",
  "authority_received": "Human user call_7c89767f19364792a2af99d97b9ce7c5: Autorizar ajuste delimitado e validação",
  "objective": "Synchronize existing mobile drawer assertion with the existing shell completion frame; no app change",
  "target": {
    "branch": "codex/mesas-proprietarias-hedge-20261027",
    "head": "3e24f60f8cfe87f79335f40e95a0927379a9f834",
    "build": "09cfa4f7b8a8dbed"
  },
  "allowed_files": [
    "tools/research_navigation_test.py",
    "this proposal and validation receipts"
  ],
  "allowed_delta": "Three lines: explanatory comment and one RAF await only in mobile branch; retain exact original state assertion",
  "forbidden": [
    "product/financial/schema/data changes",
    "other test assertions",
    "timeouts/tolerances/coverage reductions",
    "AGENTS or skill edits",
    "commit/merge/push/publication"
  ],
  "before_sha256": "bde95554a825b026eca744ce45d6c89f690bcd13b62c93a4d27a61013ee674ae",
  "candidate_sha256": "2315d2aaf8c41ebfd36e0d3571a821ce80923566bc41f6a931d41c5c2add0dc7",
  "patch_sha256": "a3ea4a1590ac099d819e5d99c3c293f1756cee71d36c6e87e767b2c2f435279d",
  "evidence": [
    "DIAGNOSTIC-RESULT.json reproduced original assert failure followed by natural closure in next frame",
    "COUNTERPROOF-RESULT.json four controls pass/three injected failures rejected/six source hashes unchanged",
    "independent static review confirms AST identical after removing only new await"
  ],
  "acceptance": [
    "specific human approval to apply",
    "repeat unchanged remaining oracles and full tier on frozen candidate",
    "do not close Epoch/Alladin incidents merely on later PASS"
  ],
  "rollback": "restore only original Research checker from preserved exact source; no reset/stash; preserve all pending work",
  "approved_by": "human user",
  "approved_at": "2026-10-27"
}
```

Aplicado somente o patch de três linhas aprovado, após conferência de hash. Contraprovas e revisão independente preservadas em docs/validation/hedge-prop-20261027/research-frame-*. Nenhuma mudança no aplicativo, tolerância ou timeout. Epoch/Alladin continuam incidentes abertos.
