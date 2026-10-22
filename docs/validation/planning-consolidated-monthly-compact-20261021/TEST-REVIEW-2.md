# Independent oracle review, round2 — release protocol

Status: release-protocol review plus final revised Task1 source review. Revised compact test identity9ab355a… was announced stable by controller and independently verified. Runtime acceptance remains separate.

Boundary: no browser, product execution, source freeze, Git commands, generated/source/test/instruction edits, dependencies or extra agents. Only this ignored report is written. Read current task-private release_protocol.py, run_logged.py, baseline.json, official builder path construction and raw quality_gate semantics. Earlier planning-controls release helper was used solely as a comparison, not authority. Factual documentation and regression-registry changes remain the already authorized bounded N3 scope; this review neither requires repeat authorization nor grants human acceptance.

## Release helper verdict

**PASS for this bounded source/control-plane review.** All three identified provenance gaps were corrected by controller and independently closed below. No final FULL execution exists in this review; no release acceptance is implied.

### RP1 — P2, CLOSED by source inspection — new generated files now hashed

Original scope() retained created files only by name, while identity categories reused fixed prior file lists. An allowed new dist/vendor file could change bytes after freeze without changing any recorded identity. Current scope() includes created_sha256 for every nonreceipt created file; final equality now detects such byte changes. All existing generated baseline files were independently confirmed covered by the old runtime/fingerprint/test/control union. Existing baseline links are separately checked against their original targets.

### RP2 — P2, CLOSED by source inspection — exported maps now compared to freeze

Originally finalize hashed exported *-INPUTS.json without ensuring their decoded content matched frozen identity maps. Current finalize explicitly compares each published fingerprint/runtime/tests/runner/control map to frozen identities before referencing its SHA256. This closes ordinary mistaken/stale export mapping. Snapshot content is independently bound before inclusion.

### RP3 — P2, CLOSED by source inspection and isolated predicate execution — raw FULL artifact bound to process

The initial wrapper bound the log but not the raw report. The amended wrapper now requires full-final.json absent before invocation and captures artifact SHA after the actual process completes. Finalize compares that SHA, tier, branch/head and raw started/finished timestamps to the observed process interval; the lower bound truncates only the wrapper start to account for raw second precision. Existing exact command, exit, log and freeze bindings remain. This closes the identified report association gap. No actual FULL has been run by this reviewer.

The final result file still relies on the task-private command receipt as supporting evidence; retain that receipt with the review package at delivery (its process exit was verified during finalize). This is a packaging recommendation, not a remaining blocking defect.

## Timer, process and artifact semantics verified

- quality_gate.py run_check uses a monotonic900second timeout per subprocess; it continues sequentially through all checks after a timeout/failure, preserving returncode and output tail. A timeout yields124 and appends ENVIRONMENT_ERROR text. Classification has preexisting precedence for HARNESS_ERROR/explicit failure strings, so inspect raw returncode/output rather than assuming every124 result label must be ENVIRONMENT_ERROR. No change to this existing behavior is requested here.
- main captures started_at before running checks and finished_at after them, both ISO timestamps at seconds precision. Its raw artifact is written at the end (not incrementally); interrupted runs may leave no new raw artifact. Full case artifacts are in a separately generated microsecond-specific tools/.artifacts/app-efficiency-full-* directory. The JSON includes that directory, command strings, durations, output tails and branch/head/status.
- Runner exit is0 only if every case result PASS; otherwise1. The helper additionally requires each passing check returncode0 and exact96 names/order, and compares the CLI-provided exit with the new actual process receipt. A helper message saying receipt PASS with exit1 means evidence packaging succeeded, not that product/FULL passed.
- Freeze now preserves microseconds. run_logged waits until the next whole second before the FULL process; therefore raw started_at at seconds precision can be later than the precise freeze without a false stale failure. This is an appropriate bounded solution to the old same-second ambiguity, assuming the normal local clock does not move backwards.

## Identity and scope evidence

Read-only Python/AST inspection, existing frozen Python with PYTHONDONTWRITEBYTECODE=1, explicit CloudDocs workdir, exit0:

1. Independently reconstructed official input order from current builder declarations and current JSON manifests without executing/importing the builder. All327 paths exactly equal prior fingerprint ordered_paths reused by helper;120 classic-script paths retain order. The helper uses the same relative-path+NUL+bytes+NUL digest and strips only the build-id script from index.html, matching official builder.
2. Prior identity categories cover397 runtime files,261 tests,1 runner and14 controls; the new compact test and current plan/contracts/helpers are explicitly appended. Every existing generated baseline file under dist/vendor-downloads is hashed. All authorized existing versioned targets are in the category union; the four new scoped files are explicitly added. No missing scoped existing target was found.
3. check_ids parses FULL additions and compares exactly96 unique names/order to baseline; scope additionally requires runner bytes unchanged. Thus command wiring cannot silently change while preserving names.
4. Scope compares all1787 recorded baseline file bytes,8 baseline links, detects created nonignored files, bounds changes by allowlist/prefix, and checks supplied branch/HEAD. Ignored task helper itself and run_logged are explicitly included in control hashes. Public validation receipts are deliberately dynamic; they do not change the product build fingerprint.
5. The earlier helper’s prior receipt is not treated as present execution or authority. Current source acceptance does not establish actual immutable identities during FULL; controller must freeze, run and verify the final candidate, then supply receipts.

## Reviewed helper hashes

- `release_protocol.py`: `e115b4608e2f2b3f7ea95700fe546e1a8c539598ca7a6c5c732e41f0fbdbe8fe`
- `run_logged.py`: `5dd217f6218fe0a17d7b3f64cf46a934dc291bbfd502e61261f6007d22ca33bd`

## Isolated finalization predicate execution

Executed the exact current dispatch/finalize AST with in-memory synthetic artifacts, identities, hash providers and captured exports. No helper import/top-level execution, Git, browser, product files, freeze files or validation artifacts were written. This tests packaging acceptance/rejection only, not the application, freeze acquisition or real subprocess behavior. Existing frozen Python, PYTHONDONTWRITEBYTECODE=1, explicit CloudDocs workdir, exit0. Valid96-check receipt accepted; nine deliberate violations rejected. The exported-map case was rerun with independently copied in-memory maps to isolate that predicate from freeze identity equality:

```json
{
  "valid": {
    "accepted": true,
    "exports": [
      "FULL-RAW.json",
      "FULL-RESULT.json"
    ]
  },
  "wrong_actual_exit": {
    "accepted": false,
    "reason": "process receipt exit mismatch"
  },
  "wrong_freeze": {
    "accepted": false,
    "reason": "FULL process receipt was not started against this freeze"
  },
  "wrong_log": {
    "accepted": false,
    "reason": "FULL process log drift"
  },
  "wrong_artifact": {
    "accepted": false,
    "reason": "FULL process artifact drift"
  },
  "wrong_command": {
    "accepted": false,
    "reason": "unexpected FULL process command"
  },
  "stale_process": {
    "accepted": false,
    "reason": "process receipt predates freeze"
  },
  "wrong_export_map": {
    "accepted": false,
    "reason": "exported identity map drift tests"
  },
  "wrong_tier": {
    "accepted": false,
    "reason": "raw FULL target mismatch"
  },
  "raw_outside_interval": {
    "accepted": false,
    "reason": "raw FULL timestamps outside observed process interval"
  }
}
```

## Pending

Receive final stable revised compact/visual/parity hashes and report; rereview R1–R4 fixes and new source counterproof semantics; inspect exact baseline RED identity. After official build, verify actual GREEN/allcompact/defaultvisual/FULL receipt bytes against freeze and real process completion. Human visual/N3 acceptance and publication remain separate.

## Final revised Task1 source review — R1–R4 closure

**Specification compliance: PASS for bounded source review. Oracle/code quality: PASS for bounded source review.** All four concrete original findings are addressed. No additional blocking source finding was identified in this rereview. This is not a GREEN/runtime acceptance claim.

Reviewed compact SHA256: `9ab355a32085d4a3b78c9e6e8c46b8b7435fb26abbbe0f4606cc090b29fb5a83`. Visual/parity hashes remain respectively `08a66550b75e8d812340749d888a6260f5f9b82f47123bb7b56c0b6aa76fd847` and `e32c4bade47d4bbfdf269c5539be5b0f5224d96e2c67e3f3e539e1538ae4d19d`. Read implementation-report.md, full revised source and targeted existing read-model/actual markup to confirm field contracts; implementer claims were not substituted for inspection.

- R1 CLOSED: detail_values lines309–322 distinguish compact primary labels from wide header/principal/detail union; complementary fields remain mandatory in details. Unique real controls are required, never clones.
- R2 CLOSED: future_input_values lines233–249 reads each future row’s unique visible actual rate/contribution values, derives only formatting from existing read-model flags/values, and distinguishes blank/zero. detail_values always invokes it. complete_details lines404–436 explicitly traverses all120 rows in both modes under the existing no-write guard and restores viewport. The three previous special scenarios remain.
- R3 CLOSED: bound_value/month_field_values bind individual values to unique visible containers rather than accepting a matching numeral elsewhere; coverage is explicit, missing USD/BRL/FX states remain local to each field. Finalization is checked as an actual visible control value. subtotal_values compares all displayed phase amounts and FX to phaseTotals with no recreated finance formulas. Both modes and the presentation matrix invoke it. Residual union text assertions are redundant checks, not a bypass of the stronger comparisons.
- R4 CLOSED: current_year derives annual membership from actual selected-account read-model, not rendered DOM. If the model contains today’s year, the visible row and unique marker must exist. Future-only account still rejects fabricated current row/marker. Existing year/green/text checks remain.

Counterproof source review: all four new IDs establish valid positive first; mutate actual DOM input/value/node without financial events; call the identical positive oracle; restore in finally; and require restored positive. The future case selects a month outside the three special scenarios and independently corrupts both fields. Cost case independently corrupts paidBrl and costCoverage. Subtotal changes actual balance span while leaving label intact. Missing-year case removes and reinserts the same row node. Because details are already expanded, repeated detail_values does not click/re-render away the mutation. Existing false-finalization oracle remains DOM-only. Read-model queries used by year/numeric checks do not mutate or normalize away DOM corruption. Real writer/command delegates and multifamily snapshot guards are unchanged.

Independent executed source checks, existing frozen Python/PYTHONDONTWRITEBYTECODE=1/explicit CloudDocs cwd, exit0:

- Reconstructed prior compact module from the original review diff and verified its b9872ab… hash; its104 IDs remain the exact prefix of108.
- Extracted original required_ids from verified archive; original98 IDs/order remain the exact prefix of206 default IDs, all unique. Runner96 and other test bytes are unchanged from prior review.
- Executed current_year with an in-memory locator double where read-model includes2026 but rendered row/marker is missing; exact original false-positive is now rejected.
- Executed bound_value with a correct coverage field (accepted) and wrong0% field against expected100% (rejected). This is source predicate execution only, not product browser evidence.

```json
{
  "compact_required": 108,
  "default_required": 206,
  "old104_exact_prefix": true,
  "legacy98_exact_prefix": true,
  "missing_current_row_rejected": "('read-model current year missing from rendered annual table', '2026', ['2027', '2028'], ['2026', '2027', '2028'])",
  "wrong_bound_coverage_rejected": "('value in its named container', 'synthetic', 'costCoverage', ['100%'], '0%')"
}
```

Baseline override script was inspected: exact archived UI/CSS bytes are SHA-checked before serving as HTTP overrides; final live oracle files remain unchanged; explicit receipts distinguish overridden served bytes from disk source hashes. The actual final baseline RED and new206 default execution were being run by controller, not this reviewer. Their results, source stability and command exits must be independently inspected when supplied; the earlier b9872ab RED must not be attributed to9ab355a. Runtime counterproof effectiveness, full120-mode numeric journeys and complete206 coverage remain NOT_RUN in this source verdict.
