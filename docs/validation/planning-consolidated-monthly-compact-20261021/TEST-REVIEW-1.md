# Independent Task1 oracle review — 2026-10-21

Scope: bounded tests/control plane only. Inspected final test hashes, full review diff, current test sources, approved brief/plan/CHG, real RED receipts, and original recovery tar members. Root/branch/HEAD are those supplied by controller (CloudDocs; codex/planejamento-patrimonial-20261020; ea15afc); no Git command/mutation, browser run against the moving product, dependency change, product/test/doc edit or other-agent delegation performed. Only this ignored report is written. Read routed project review/test/preflight/change-control/engineering instructions. Controller-supplied audit/edit preflight receipts remain historical; this review does not claim a fresh preflight or full Harness reread. Restriction to source inspection comes from the explicit review packet.

## Verdicts

**Specification compliance: CHANGES REQUIRED.** The intended control-plane scope, old protection preservation and real RED provenance are supported, but the wide-detail label requirement exceeds the approved contract and numeric preservation coverage is incomplete.

**Oracle/code quality: CHANGES REQUIRED.** Four concrete findings below. This is not a product implementation verdict. GREEN, new104/default202 browser execution, native zoom/touch and runtime injected counterproofs remain NOT_RUN for this review.

## Findings

### R1 — P1 — Wide detail oracle rejects a compliant primary-column layout

`tools/planning_compact_table_test.py:221–225` requires every DETAIL_LABELS entry inside the details element alone, including Saldo inicial, Resultado, Saque, Aporte and Finalizado. `tools/planning_parity_test.py:219–222` reuses this for all120 months in its ordinary desktop journey. Approved plan lines35–37 put those primary values/controls in wide columns and require them in the compact detail, whereas both modes require the complementary cost/FX fields in detail. The next block already deliberately checks values using principal+detail.

A conforming wide row with its single Finalizado control in the Finalizado column and only complementary detail labels is rejected at line225. Repeating all primary labels in wide details is not required by the plan; cloning controls would conflict with uniqueness. Minimal fix: scope primary labels to the union of principal+details or to their expected mode; keep complementary detail labels required in details, and verify actual control location/value without duplication. Treat this as a harness-contract correction, not weakened product acceptance.

### R2 — P1 — The claimed all120-month preservation skips most future editable values

`tools/planning_compact_table_test.py:239–241` skips both rate and contributionUsd for every future month, with a comment saying actual inputs are checked below. No such input reads occur below in this function. `scenario_values:363–369` checks only blank/zero/negative (three months), while `unique_controls:210–218` checks counts only. `complete_details:279` and the replacement old parity block therefore accept wrong or empty input values for every other future month, even though those columns have been removed from the compact principal grid.

Minimal fix: read each future month’s actual unique rate/contribution input while visiting that month, preserving the model’s blank-versus-zero distinction. Check this in both modes. Add a bounded same-oracle counterexample that changes a future month outside those three scenarios and requires rejection. No new financial maths are needed.

### R3 — P2 — Numeric cost/subtotal preservation is not established, and field values are matched anywhere

`detail_values:238–248` searches all formatted values anywhere in the concatenated month text. It cannot associate a value with its label; an unavailable FX field represented by an em dash can pass because a different field has an em dash, and equal monetary values can hide a missing field. `costCoverage` is never read: only the label Cobertura and the separate `costStatus` string are checked. `complete_details:280–291` checks subtotal count, location and labels, but none of the actual subtotal amounts (`phaseTotals` contains open/result/withdrawal/contribution/close USD and BRL, see unchanged engine lines665–673). A subtotal that retains its period label while replacing every number with zero remains acceptable to this oracle.

Minimal fix: compare each moved field in its own labeled/value container (including explicit unavailable state and actual coverage), and compare displayed phase amounts to the existing read-model values. Preserve the approved reduced-column arrangement; do not demand old18 simultaneous columns. A removed/wrong cost value and wrong subtotal should each fail the relevant unchanged positive oracle.

### R4 — P2 — Missing current-year row can be mistaken for an out-of-horizon account

`current_year:144–151` infers whether the current year belongs to the horizon solely from currently rendered table labels. If the renderer omits the current row and its marker, it returns success with not_in_horizon=true. `year_independence:166–177` never checks that its normal account (seeded today minus2months, guaranteed to contain today) actually contains the current year; it only positively checks the separate future-only account at lines178–180. The wrong-visible-year counterproof retains the marker and therefore does not cover this omission.

A pure-source execution of the exact current_year function using locator doubles with local year2026, visible years2027/2028, and0 markers returns not_in_horizon=true (receipt below). This is an oracle counterexample, not an application runtime claim. Minimal fix: derive expected horizon membership from the existing read-model/fixture and require the current row/marker when it belongs; preserve zero markers when it genuinely does not.

## Positive evidence and preservation

- Independent SHA256 checks match all3 final test files to task-1-final-test-hashes.json. RED-final-v3 records those exact compact/visual hashes,8/8 PRODUCT_FAIL, zero page errors, stable source hashes and exit1; its failures are concrete absent groups/current marker/details/labels or18 versus7/3 geometry, not setup failures. Several downstream checks were not reached, as the implementer properly states.
- RED provenance does not execute planning_parity_test.py; its hash is independently matched to the final hash manifest rather than misattributed to the RED run. The first RED receipt independently confirms PRODUCT_FAIL with8/8 cases and stable sources; it does not fingerprint planning_parity_test.py, so the asserted before-adaptation sequencing remains attributed to the implementer’s report. Final adaptation correctness remains pending GREEN.
- Recovery archive comparison confirms old visual functions unchanged except native_zoom/required_ids/main; old parity changes only monthly_journey and the supplied diff is the localized18-column replacement. quality_gate.py, planning_parity_layout_test.py, engine and state are byte-identical to the original archive. Exact98 old IDs/order are retained and104 are appended, total202; original3 regression selection stays3.
- Executed existing pure control-plane coverage guards: empty, missing, NOT_RUN and duplicate cases rejected; runner wiring identifies55STANDARD/96FULL entries, one visual entry each; focal substitution/removal rejected; matrix dimensions remain4layouts×2themes×10sizes.
- Writer instrumentation in ui_visual_quality_test.py:91–94 wraps real writer/execute delegates and calls originals; guard snapshots all existing financial families and checks delegates in finally. No financial writer is stubbed. Runtime effectiveness still requires built-UI runs.
- Geometry checks120 unique rows and matching cell counts, useful-width7/3, wrapper/table/shell overflow and clipping. Full120 details/controls count are checked compact; draft roundtrip checks same-node identity, partial12, focus and caret going compact, restores wide and rechecks unique controls. Counterproofs use the same positive oracles with mutations restored and positive recheck; no false-finalization mutation is erased by re-rendering inside its DOM-only oracle.

## Execution receipt

All executed commands used explicit CloudDocs workdir. Pure Python checks used `PYTHONDONTWRITEBYTECODE=1 /private/tmp/jpw-pf-default-frozen-runtime-20261017/bin/python3 -` with inline read-only archive/hash/AST inspection and imported source-oracle calls. Exit0. No newUI browser execution or full-suite claim. Exact reviewed test hashes:

{
  "tools/planning_compact_table_test.py": "b9872ab9a39c2b169ec17212e0c48e96aacd311ef88c89e5da5a07c9d3297811",
  "tools/ui_visual_quality_test.py": "08a66550b75e8d812340749d888a6260f5f9b82f47123bb7b56c0b6aa76fd847",
  "tools/planning_parity_test.py": "e32c4bade47d4bbfdf269c5539be5b0f5224d96e2c67e3f3e539e1538ae4d19d"
}

Independent inspection/control-plane receipt (PASS for these limited checks only):

```json
{
  "test_hashes_match": true,
  "old98_ids_exact_order": true,
  "new104_ids_exact": true,
  "default202_ids_unique": true,
  "protected_archive_bytes": {
    "tools/quality_gate.py": true,
    "tools/planning_parity_layout_test.py": true,
    "src/js/30-accounting/06-planning/01-engine.js": true,
    "src/js/30-accounting/06-planning/02-state.js": true
  },
  "red_cases": 8,
  "red_all_product_fail": true,
  "red_zero_page_errors": true,
  "red_stable_sources": true,
  "red_exact_executed_compact_and_visual_hashes": true,
  "year_missing_row_counterexample": {
    "calendar_year": "2026",
    "not_in_horizon": true
  },
  "coverage_guards": {
    "positive": {
      "executed": 1,
      "required": 1,
      "unique": true
    },
    "zero_cases": {
      "rejected": true,
      "measurement_failure": "empty coverage is invalid"
    },
    "zero_expected": {
      "rejected": true,
      "measurement_failure": "empty coverage is invalid"
    },
    "missing": {
      "rejected": true,
      "measurement_failure": "('missing/unexpected cases', ['missing'], [])"
    },
    "not_run": {
      "rejected": true,
      "measurement_failure": "unexecuted/unknown classification"
    },
    "gate_wiring": {
      "positive": {
        "STANDARD": {
          "entries": 55,
          "visual_entries": 1
        },
        "FULL": {
          "entries": 96,
          "visual_entries": 1
        }
      },
      "removed_new_entry_other95_preserved": {
        "rejected": true,
        "measurement_failure": "('visual check must run exactly once', 'STANDARD', 0)"
      },
      "focal_instead_of_default": {
        "rejected": true,
        "measurement_failure": "('visual gate must invoke default complete CLI and unique output', 'STANDARD')"
      }
    },
    "matrix_dimensions": {
      "positive": {
        "layouts": 4,
        "themes": 2,
        "viewports": 10,
        "native_zoom": 200
      },
      "empty_layouts": {
        "rejected": true,
        "measurement_failure": "('four approved layout identities required', [])"
      },
      "empty_themes": {
        "rejected": true,
        "measurement_failure": "('both approved themes required', [])"
      },
      "empty_sizes": {
        "rejected": true,
        "measurement_failure": "('nonempty valid viewport pairs required', [])"
      },
      "missing_short_size": {
        "rejected": true,
        "measurement_failure": "('approved320..1440/short/boundary viewports required', [(320, 700), (390, 844), (700, 600), (701, 601), (1099, 720), (1100, 719), (1100, 720), (1101, 721), (1440, 1000)])"
      }
    }
  },
  "duplicate_guard_rejected": "('duplicate case identity', ['x', 'x'])"
}
```

## Remaining completion evidence

After fixes, capture revised exact test hashes and preserve old RED history. Revised tests need a matching historical-baseline RED identity (or explicit defect-specific source counterproof where appropriate), then actual built candidate GREEN focal8, all104, default202, old parity monthly, and required final FULL/freeze evidence supplied by controller. Verify runtime counterproofs reject the intended violations after a valid positive candidate and restore cleanly. Neither old98 green nor source/control-plane PASS substitutes for this evidence. Human acceptance/publication remain separate.
