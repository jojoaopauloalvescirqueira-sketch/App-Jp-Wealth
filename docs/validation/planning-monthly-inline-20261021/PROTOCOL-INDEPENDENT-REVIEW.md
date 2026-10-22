# Task 3 — independent protocol review, before final freeze

Reviewer: separate `inline_protocol_reviewer` agent, delegated by root. Product, tests, documentation, configuration, Git and previous evidence were read-only. The reviewer wrote only this ignored report. Root implemented the reconciliations described below. This is an independent N3 protocol/oracle review, not human acceptance or final release validation.

## Verdict

**Scoped protocol review: AUDIT_PASS. No remaining blocking defect identified in the reviewed protocol revision.** Final candidate validation remains **NOT_RUN**: Task2 UI/default-browser integration, final official build, freeze, current FULL96 and final candidate review were not available at review time. This report cannot approve their future results or replace those gates.

Target: CloudDocs `SOFTWARES & EAS/JP Wealth OS`, branch `codex/planejamento-patrimonial-20261020`, HEAD `ea15afc9c6a9c30cc69c5b98a8b85c85211ffb34`. Preserve the inherited dirty worktree; no Git action was performed. The current scope is measured against the task's full 2dd snapshot, not against clean HEAD.

Reviewed final helper SHA-256: `67bfcb4c80cb4e406ce9b715daa18b1f4189c5f3b3a53cbb356bf4234b8237d9`.

Other reviewed identities:

| Input | SHA-256 |
|---|---|
| Immediate previous protocol | `819584fa8d88e3339cbfb5153fb04654a669843300a1d38eeaf4dfbb87202d3b` |
| Current and previous wrapper, byte-identical | `5dd217f6218fe0a17d7b3f64cf46a934dc291bbfd502e61261f6007d22ca33bd` |
| Current baseline.json | `142178f9d87ec8afc49af3a78d2fbb6db273bd51969ae3e4f4c875239c4ffcae` |
| Recovery archive | `445c7b652ffd8e2db5f9fa6a0babc65edaf814b21e049922d63da5ea589679d8` |
| protocol-provenance.json after reconciliation | `73f26f6d0df3df12693f7420090fea28c578a5146a16767e9339f775462339c8` |
| source-authority.json | `d2613be7e4d60b8150cc0036113b563a14d845b7c37bf214e4e67e681fc4b3de` |
| Canonical external Harness, read at its moved path | `b5680c22e44cf3f4a5cd3aa5deeb96f8b65c7908f14543e8c5d7f0c2f4e17b95` |

## Sources and method

Read AGENTS, README, context-map/project-context, local skill routing, preflight/change-control/test-triage, JP Engenharia and its regression/validation references; relevant Harness source sections 8,12–19,28–30; current brief, Task2/Task3 briefs, plan, source-authority, baseline/bootstrap, both current CHGs, provenance, current/prior protocols and wrappers, and actual quality runner. The global memory registry was consulted only for audit discipline/context routing; it was not authority or current proof.

Executed only read-only inspection, hashing, archive-member verification, AST inspection, actual `scope` and check-ID evaluation, and two in-memory negative probes. Did not call freeze, verify or finalize and did not launch FULL or product/browser suites. Negative probes changed only the hash function in an ephemeral Python namespace, leaving candidate, baseline, archive and evidence bytes untouched.

## Preservation and identity findings

1. Baseline contains **1921 regular files and 8 symlinks**. Its embedded `prior_freeze` identities equal the actual immediately previous freeze identities exactly. The recovery archive contains exactly1929 members; every regular member hashes to its baseline digest and each symlink retains its recorded target. Archive SHA also matches baseline. This independently checks recovery/preservation, without rewriting the previous task.
2. `scope()` rejects non-allowlisted changes, checks all8 inherited links, branch, HEAD and exact quality-runner hash; the root-added archive check now rejects recovery drift. Actual latest scope returned8 modified baseline files and only authorized created files;1913 baseline regular files remained identical at that observation. These are interim counts, not final UI candidate counts.
3. Allowlist matches the current Product/Test CHGs and generated-artifact permissions. The bounded navigation hook is explicitly present in the single current Product CHG. No AGENTS, skill, normative file, engine or quality-runner edit is authorized. Existing generated-directory prefixes are inherited; no broader prefix was introduced.
4. Actual runner AST produces exactly96 unique FULL IDs in the same order as the previous freeze, and runner bytes match the baseline hash. The entire runner hash protects command expressions as well as IDs. No check was removed, renamed, waived or replaced by a historical result.
5. Every explicitly allowed runtime/test/document path and every inherited generated path covered by the artifact prefixes is represented in the candidate's source/runtime/test/control maps. The new JS oracle and new browser oracle are added to the test identities. Existing navigation/finalization scripts are already in both source ordering and runtime identities. Expected final map populations are runtime397, tests264, runner1, controls37 and checks96; these are expected identities, not executed test counts.

## Issues found and resolved by root before freeze

- **Identity input omission — resolved.** The first copied revision did not hash its own `baseline.json`, provenance and delegated contract/evidence inputs. Root added exactly9 control entries: baseline, provenance, Task1/2/3 briefs, Product CHG reconciliation receipt, preserved duplicate source, factual-heads preservation receipt, and this independent report. Baseline now participates in freeze/verify/finalize equality, and scope also checks the archive SHA from that baseline. No previous evidence changed.
- **Contradictory Product CHG bodies — resolved.** Initial Product CHG had two top-level schema objects, one omitting navigation. Current record has exactly one, including the approved bounded hook. Root preserved original bytes and before/after hashes separately. This correction adds no new authority.
- **Exported scope receipt omission — resolved.** Finalizer now checks `SCOPE.json == frozen.identities.scope`, alongside the five exported identity maps.
- **Receipt-validity message ambiguity — resolved.** Finalizer now prints `VALID current final receipt; suite PASS/FAIL; actual exit ...`. It may preserve a failed execution receipt, but cannot announce suitePASS for that failure. Technical completion still requires actual exit0 and96 PASS/returncode0 entries.
- **Provenance description stale after hardening — resolved.** Current provenance records added archive/scope predicates and9 control identities; it no longer claims every predicate is unchanged. Inherited checks remain intact and wrapper is byte-identical.

## Actual-exit, time, hash and source binding

Inspection of current wrapper/finalizer confirms: unique log/command receipt names; no preexisting FULL artifact at launch; freeze hash captured before subprocess; actual subprocess exit recorded; actual log/artifact hashes; exact Python/runner/full/artifact command; branch/HEAD agreement; raw timestamps bounded by observed process interval and after freeze; frozen identities recalculated before finalization; five exported maps and SCOPE equality; exact96 raw check order; and equivalence between exit0 and every check having PASS/returncode0.

These are local integrity checks, not signed provenance or protection against an executor rewriting every file. Scope enforcement and receipt capture depend on running the reviewed helpers. Finalizer copies the actual result/summary; it does not execute tests, reinterpret a failure or activate Harness§19.1. Previous Alladin timeout stays historical/open. New FULL evidence must be generated against the final current freeze; the previous96/96 result cannot satisfy it. Human visual/N3 acceptance and all Git/publication actions remain separate.

## Commands observed and limits

| Observation | Result |
|---|---|
| Initial `python3 tools/agent_preflight.py --mode audit` | Actual exit1: stale manifest hash for02-state.js during authorized Task1 work; dirty127-entry warning. This is an interim build/preflight blocker until official rebuild, not evidence that a browser or FULL check ran. |
| `python3 .../release_protocol.py scope`, initial and hardened revisions | PASS, actual exit0; only authorized task deltas at observed times. |
| Read-only archive digest/member/link comparison | PASS,1921files +8links, no mismatch. |
| Actual runner hash and AST FULL ID comparison | PASS,96unique IDs/order equal baseline. |
| In-memory negative probe: substitute mismatched recovery-archive hash | PASS: actual scope raises `recovery archive drift`. |
| In-memory negative probe: substitute changed AGENTS hash | PASS: actual scope raises `unapproved delta AGENTS.md`. |
| Freeze/FULL/verify/finalize, post-Task2 browser integration and new final candidate | NOT_RUN in this review, deliberately deferred. |

`diff -u` returned1 because intended current/prior deltas exist; that is ordinary comparison status, not a product failure. No product/source/test/doc/config/Git/installation mutation was made by this reviewer.

## Required final proof and recommendations

Before freeze, verify Task2's new browser suite is called by the **default** existing `ui_visual_quality_test.py` path and cannot be silently skipped; preserve all206 inherited visual IDs and their unchanged criteria except explicit approved contracts. Task1's state test already directly imports and runs the14 new JS cases through the existing FULL planning-state command; this was checked in source. The separate Task1 review's fresh68/68/mutation result was reported by root, not re-executed here.

Complete Task2, official build and focal/independent reviews first; finish this report and all37 control inputs before freezing. Then execute the exact current FULL command through the reviewed wrapper, preserve initial failures, verify unchanged identities and finalize using the captured actual exit. Treat any material later edit as a new candidate requiring applicable reruns. Recheck this helper hash against this report before freezing; a later helper change needs a corresponding review delta.

Nonblocking recommendation: include runtime versions/origins and relevant environment values in final receipts, especially Python/Node/Chromium and any baseline override. Wrapper currently supplies the intended Node/Chromium paths and Python command but does not persist a complete environment/version attestation. This limits reproducibility rather than weakening the96 mandatory checks. No universal stability, browser-human acceptance or release approval is claimed.
