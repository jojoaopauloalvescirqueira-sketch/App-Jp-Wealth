# Independent A0 timeout review

Checkpoint UTC: 2026-10-26T13:37:09.897196+00:00.

## Finding and classification

The current official FULL log records `ui-visual-quality` as **ENVIRONMENT_ERROR at900.033s**. Source `tools/quality_gate.py:163–184` uses the unchanged900second subprocess limit; timeout preserves stdout, assigns returncode124 and an ENVIRONMENT_ERROR marker. The UI final result JSON is absent at this checkpoint. The FULL is still running, so no final overall check count/exit is asserted here.

If all other101checks finishPASS, the defensible delivery remains **101PASS +1ENVIRONMENT_ERROR, FULL not approved**, with runtime/source/focal review described separately. Do not combine prior413PASS with the new101PASS to fabricate a102PASS candidate. The Harness historical-product-failure exception does not waive ENVIRONMENT_ERROR, and no activation/approval for a waiver has been established. Human visual acceptance is separate.

## What existing evidence establishes

- All678 files in the current freeze still match, and all11 expected retired files remain absent. No runtime/build/gate/UI-verifier edits occurred during the run.
- All153 source hashes declared by the earlier complete UI receipt still match current files. UI test hash and2px criterion are unchanged. The two changes between complete FULL rounds were the approved guide startup oracle and additive regression registry, neither a change to the UI sources covered by the previous receipt.
- The earlier UI check passed413/413 at835.103s (report-internal elapsed834.518s), leaving only64.897s before the unchanged cap: approximately7.8% extra elapsed time would exhaust that margin.
- Current screenshot birth/mtime sequence shows continued work through the calendar matrix and all eight native-calendar screenshots. The final native-calendar screenshot was written2026-10-26T13:31:28.375824Z. A retained synthetic `visual-native200-62u8kdni` profile was created13:32:25.922029Z. Source main() performs several native phases after calendar, so partial visual artifacts do not demonstrate final coverage.
- Read-only process inspection at the checkpoint found no remaining process matching this UI script/profile; the official full wrapper was still running. This is a snapshot, not evidence of process/resource conditions at the timeout or proof of complete cleanup.
- Timing comparisons from matching artifact writes show an accumulated cost increase before the last native phases: [('headless review to notifications', 195.288, 220.437, 25.15), ('final calendar matrix to final calendar native', 46.895, 51.822, 4.926)]. This is consistent with slower aggregate execution and insufficient deadline margin, rather than evidence of a single900second stall.

## Causal limits and residual risk

**Confirmed trigger:** the outer900second deadline expired. **Supported inference:** aggregate duration was higher; the prior passing run already had little margin. **Unproven root cause:** CPU/memory/GPU load, cloud-file I/O, browser/native-window scheduling, user focus interaction, or one particular internal wait. No contemporaneous resource telemetry or completed per-case report for this attempt establishes any of those explanations. Do not blame the user or label a specific environment cause as confirmed.

The previous complete receipt had a particularly long `compact-month-details-complete` case (67.581s), and total UI work includes headless matrices plus multiple separate native contexts. These observations identify places where future measurement could be useful; they do not establish where this attempt lost time. Screenshot times are phase evidence, not assertions about passed cases.

`record()` accumulates case detail in memory and prints one result per completed case; JSON is written in finally only at full process completion. The outer timeout prevents that final evidence. Once the gate finishes, inspect its retained UI stdout to determine the exact completed case prefix, any preceding failures and the last case reached. Missing final coverage/source-stability receipt means the current visual gate remains incomplete even if the printed prefix is allPASS.

## Bounded next step

Preserve this round and allow the current FULL to finish without source/process interference. Audit the resulting command exit, all102 IDs, current678hashes/11absences and captured UI stdout. Deliver the actual failure classification and unresolved verification requirement. A retry alone cannot erase this timeout. Any proposal to improve runtime must first identify the measured bottleneck and preserve413cases, source checks,2px criteria, original negative oracles and900second gate; any control-plane change requires its existing approval/review process. This A0 review does not authorize implementation, increasing limits, skipping native cases, disabling checks or publishing.

No new test/browser, environment mutation, process signal, repository edit or Git mutation was performed by this reviewer. Only this scratch report was written.
