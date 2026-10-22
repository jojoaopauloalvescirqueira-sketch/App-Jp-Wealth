# Independent initial review — 2026-10-22

Scope: read-only product/test inspection; only this reviewer directory may be written. Sources actually read: brief, approved closure plan, root AGENTS, JP engineering entry/regras-regressoes/validacao, complete PLANNING contract, new browser test file, state query cases Q01–06, current previewFinalizeMonth, visual coverage function. README/CONTEXT-MAP output was truncated and is not claimed as complete reading. Audit preflight PASS on branch codex/planejamento-patrimonial-20261020 at ea15afc9c6a9; 132 dirty entries (128 preexisting plus authorized current additions reported by root). No product/real-data/Git changes.

## Findings and remaining proof

1. TEST_HARNESS_FAIL (oracle gap): units_validation accepts positive `12,50` as evidence of a loss preview; substring does not assert minus sign. Tighten exact signed financial outcome. This does not establish a product defect.
2. Coverage gap: missing_recovery asserts only start year in context, not account identity and exact month. Immutable account/month is an explicit plan requirement; test actual ID/month in draft or contextual text and adversarial account changes.
3. Coverage gap: changed_review covers contribution revision but not reset/archival of account or plan replacement while modal exists. Those are key identity/token boundaries for manual explicit refresh; test no reuse against another plan, preserving editable drafts or clearly cancelling invalid target.
4. Current new browser file claims imported by existing default entry, but as inspected integration has not yet occurred. Existing ui_visual_quality_test.py and quality_gate.py are byte-identical to baseline.json. Runtime import yielded exactly 240 visual IDs and 96 FULL runner checks. Preserve baseline and add eight closure IDs through existing visual entry. This is work-in-progress, not rejected completed implementation.
5. Q01–Q06 oracles are contract-grounded: zero differs from absent, first pending month after Jan finalized is Feb, 1000-25+20-5=990, no FX dependency, additive errors/status and cloned read data. No observed invalid financial oracle. NOT_COMPUTABLE not yet explicitly exercised; useful only if a valid accepted input can trigger it.
6. Refusal/unknown browser scenario mocks writer output; establishes UI reaction only. Actual writer success is instrumented in missing_recovery; existing real-writer tests should remain, and completed review must distinguish outcome simulation from real storage failure.

## Boundaries

No executed browser or full-suite PASS claimed by this review. Product source was still baseline at inspection; completed-candidate review, independent browser probes, regression preservation and frozen-full receipt verification remain NOT_RUN. Existing PDF footer/focus debts are distinct and were not investigated here.
