# Independent post-fix source review

Verdict: **PASS for exact applied startup-oracle repair and focused evidence**. Final FULL technical closure remains pending; the prior completed round remains101PASS/1PRODUCT_FAIL, exit1.

Current `tools/learning_guide_test.py` is byte-identical to the independently reviewed candidate SHA-256 `9145dcbb9966e600112c50a30eba4086b318c4448e33c6fcf2edd401897993a6`. Its original106-path hash and all66 case IDs remain unchanged; current actual122-script list must omit the retired Nocuda script. Historical reinsertion is confined to the explicit identity and unique original predecessor. The active count subtracts exactly1. The prior13 negative cases plus2 retired-wire negatives remain enforced.

Inspected actual `startup-source-manifest.json` and `offline-sw-four-guide-modules.json`: each1PASS, zero failures, source_unchanged=true, current test hash, no pageErrors,15 rejected counterproofs and registeredCaseCount66. All declared input hashes match live sources. Offline receipt identifies the four guide modules and three Calendar/Agenda modules in the actual precache. These are headless browser executions by the test agent, not launches by this reviewer.

Compared live sources against prior678-input freeze: only `tools/learning_guide_test.py` and `tools/regression-memory.json` differ; all11 expected retired files remain absent. Application build remains5cd40fe879de6727, official gate hash074fd1d63154b50a1eefcbc3feac4c9f41e1d6356615bc089e04b5adffb2cd2a and UI verifier hashf5cee3d6442bbb95901afed953ca9ea504c6c30873fd6e0751a274c8b3c5c69c unchanged. `git diff --check` PASS.

The regression registry now has113 entries. Independently compared all111 pre-task entries against the preserved baseline: unchanged. The two additions identify retirement and the startup-oracle adjustment; their referenced persisted receipts exist.

Minor receipt metadata observation: at inspection, `proof-after-apply.json` field `baseGuideSHA256` pointed at current9145dc rather than the actually executed preserved `learning_guide_test.before.py`332ffc. `final-receipt.json` correctly identifies both hashes, and before/current bytes are independently verified, so this does not change the code/proof verdict. Owner notified to align that metadata with the actual baseline source.

No repository/source/test/Git changes, no browser launches and no process signals by reviewer. New complete FULL requires the corrected candidate freeze and coordination of the native zoom window; human visual acceptance remains separate.

Metadata erratum independently checked: owner preserved raw `proof-after-apply.json`, then executed corrected proof using the actual before-file hash. `proof-after-apply-corrected.json` now identifies baseline332ffc/current9145dc correctly, retaining2RED/2GREEN,15 rejected mutants and66 unchanged IDs. Observation resolved without changing product/test inputs. New full-after-startup-fix round is prepared, execution/acceptance still pending.
