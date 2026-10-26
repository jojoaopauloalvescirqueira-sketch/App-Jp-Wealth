# CHG-JPW-CALENDAR-MARKETS-TESTS-20261024

Human approval is the authority; this record grants none.

```yaml
{
  "schema": "jp-harness/chg/v1",
  "status": "approved",
  "target": {
    "root": "/Users/joaoalvescirqueira/Library/Mobile Documents/com~apple~CloudDocs/SOFTWARES & EAS/JP Wealth OS",
    "branch": "codex/calendario-mercados-20261024",
    "baseline_sha": "a4bf278cd4dc38bbaa5b905ed17a79e33684fb67"
  },
  "approved_by": "human user",
  "approved_at": "2026-10-24",
  "approval": {
    "evidence": "PLEASE IMPLEMENT THIS PLAN: Calendário e Mercados — integração com consulta rápida; resposta explícita Autorizar essa branch e a implementação delimitada",
    "limits": "No commit, merge, push, publication, dependency additions or financial changes."
  },
  "rollback": {
    "source": "Reverse only this task delta against a4bf278, preserving other work. Official rebuild restores derived outputs. No data mutation by this change."
  },
  "harness_source": {
    "path": "A0 - HARNESS - JP Wealth MASTER SPECIFICATION.md",
    "sha256": "b5680c22e44cf3f4a5cd3aa5deeb96f8b65c7908f14543e8c5d7f0c2f4e17b95",
    "sections": "12-14,19,24,28-30,36-49"
  },
  "data": {
    "test_policy": "synthetic_only",
    "schema_change": "forbidden"
  },
  "acceptance_criteria": [
    "approved combined host and legacy-route compatibility",
    "single controller/catalog/snapshot, lazy full view and visible renderer",
    "calendar and now remain independent; no financial writes",
    "focus/drafts/state preservation, explicit stale/failure recovery",
    "focused current receipts, full final gate, independent review, human acceptance separate"
  ],
  "change_id": "CHG-JPW-CALENDAR-MARKETS-TESTS-20261024",
  "objective": "Protect approved navigation, overview, lifecycle and integration; replace only superseded standalone-menu expectations",
  "risk_level": "N3",
  "authority_required": "A4",
  "scope": {
    "allowed_files": [
      "tools/calendar_markets_test.py",
      "tools/market_hours_integration_test.py",
      "tools/navigation_ia_test.py",
      "tools/nocuda_tools_test.py",
      "tools/minigames_test.py",
      "tools/calendar_visual_quality_test.py",
      "tools/regression-memory.json"
    ],
    "forbidden_files": [
      "AGENTS.md",
      "skills/",
      "docs/normative/",
      "src/js/10-domain/",
      "src/js/30-accounting/",
      "tools/quality_gate.py",
      ".github/"
    ],
    "allowed_actions": [
      "bounded implementation",
      "synthetic tests",
      "scoped factual evidence"
    ],
    "forbidden_actions": [
      "commit",
      "merge",
      "push",
      "publication",
      "real-data mutation",
      "global-memory mutation"
    ]
  },
  "approved_tests": [
    "calendar_markets_test.py",
    "market_hours_integration_test.py --distributions",
    "all affected market/calendar focals",
    "quality_gate.py --tier full"
  ],
  "derived_artifacts": {
    "allowed": [
      "build-id.js",
      "src/js/manifest.json",
      "dist/",
      "sw.js fingerprint",
      "src/vendor/downloads/",
      "src/vendor/market-hours/runtime-payload.js"
    ],
    "generation_commands": [
      "python3 tools/rebuild_monolith.py --refresh-manifest"
    ],
    "manual_edit": "forbidden"
  },
  "test_contract": "Before: standalone tools-market-hours child required. After: single tools-calendar child labelled Calendário e Mercados; old targets retain requested/local intent but canonicalize to tools-calendar and expand. NoCuda and MiniGames exact children lists change from six to five, removing only tools-market-hours. NoCuda keyboard adjacency changes from NoCuda-Up-MarketHours-Up-Calendar to NoCuda-Up-Calendar-Down-NoCuda-Up-Calendar-Enter. Preserve all valid lifecycle, guards, downloads, games, data, rendering and distribution oracles. New tests need RED/GREEN and counterproofs; runner/gates unchanged."
}
```

## Reconciliation of superseded submenu expectations

The first full run is preserved unchanged: 100 PASS and two raw PRODUCT_FAIL results, in `full-first.json` under the validation evidence. Both failures compare the new five-child Tools registry with the former six-child registry. Their causal classification is TEST_HARNESS_FAIL; the runner's original classifications are not rewritten.

The approved removal of the standalone submenu requires the same bounded oracle replacement in NoCuda and MiniGames consumers. NoCuda retains three HTTP/file/portable modes, offline PWA, binary downloads, source generation, storage and keyboard protections. MiniGames retains game controls, singleton, pause, guide, storage and distribution protections. RED originals, exact diffs, GREEN results and independent review accompany these substitutions. A new full run is required on the final tests; these explanations do not turn the first full run green.
