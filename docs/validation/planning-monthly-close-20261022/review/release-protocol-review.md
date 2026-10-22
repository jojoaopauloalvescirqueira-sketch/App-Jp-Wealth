# Task-private release protocol review, before FULL

Read release_protocol.py, run_logged.py, both CLOSE CHGs, and relevant report-producing fields in quality_gate/ui_visual_quality_test. No product/control edits performed.

## Corrections needed for stated binding claims

1. Receipt identity/freshness: receipt accepts exit0 command record without asserting command argv (existing Python + tools/quality_gate.py --tier full --artifact task/full.json), cwd, or times after freeze. It checks visual source_unchanged but not report.source_sha256/test_sha256 against frozen inputs. A stale compatible report can satisfy counts and PASS while describing different source. Bind exact invocation/cwd, freeze <= command start <= raw suite times <= command finish (allow second-resolution timestamps), visual times within run, recorded source/test fingerprints to frozen inputs, and raw full path selected by exact invocation. Existing runner full JSON has no comprehensive source fingerprint, so immutable before/after inventory and real wrapper invocation are needed as evidence boundary.
2. Symlinks: baseline link entries are skipped and inventory excludes symlinks; link deletion/retarget is invisible. Preserve link targets in inventory and compare against baseline. Current code does not establish all-baseline-files preservation despite regular-file coverage.
3. Comparator archive: candidate-e08c-before.tar.gz supplies original state/visual/runner/regression bytes but is absent from task_controls. Hash it at freeze (prefer verify its compared entries against baseline hashes) so comparison source cannot drift after freeze unnoticed.
4. Preservation claim precision: AST rule skips all of main and required_ids, not merely additive statements. Current manual diff is additive and preserves old calls, but helper cannot itself substantiate that stronger assertion. Either enforce narrowly allowed additive delta or record this as independent manual review backed by frozen file hash. Names/counts alone cannot prove invocation of old oracles.
5. Branch/HEAD: CHG expires on drift, but verify does not check current branch/HEAD. Add exact baseline identity assertions at freeze and verify, or make external live checks an explicit required gate.

## Adequacy and authority

Separation of N1 product/A2 and N3 tests/A4 matches approved scope; CHGs state they confer no authority. Both preserve human acceptance and independent review; no self-approved control waiver or exception19.1 activation found. Generated output allowances match plan, but path permission alone does not establish official generation; build receipts/reproducibility check supply that separately. V/dynamic evidence exclusion is reasonable provided final hashes bind consumed receipts and the temporal/source checks above are applied. Existing runner96 byte preservation and state-prefix/suffix constraints are useful and directly test the stated invariants.

Outcome: corrections or explicit independently verified boundaries required before treating helper receipt as final frozen-full binding. This is an evidence-helper finding, not a discovered product financial defect.
