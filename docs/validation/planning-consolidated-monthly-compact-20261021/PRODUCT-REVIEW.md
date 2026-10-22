# Independent product review — compact Planning

## Follow-up — narrow account selector (current source review)

**Specification/source review: PASS for the updated bounded delta. Code-quality review: PASS.** Current source applicability is UI `7405635f20dfc9fd49f3ec65d0b2b0a91c5d5244ad9ed220a748e7a7dde3c23b` plus CSS `697d62a9211d586970b5bde0fc0eabf6b026ee519aa9e153bd7108914a41e40f`, independently read and then confirmed stable by the controller. The earlier runtime probes below belong to the previous CSS/build and are not silently promoted to executions of this update.

The controller's subsequent focal run discovered a real320px overflow case outside the monthly table, beyond this reviewer's earlier390px/1440px runtime sample. Builder diagnostic receipt `task-2-overflow-diagnosis/result.json` was read: the account toolbar is256px wide, but its label flex item has `min-width:auto` and expands to279.09375px around the233px intrinsic selector. This increases shell scrollWidth291 over clientWidth280. Expected: the account control fits the available toolbar without making the shell scroll horizontally. Source location: existing toolbar flex/label styles at `app.css:10863–10866`; existing select override at11200 already allows the select to shrink, while its parent label previously prevented it.

The exact fix at `app.css:11256–11257` is one comment and `#planning .pl-toolbar>label{min-width:0;max-width:100%}`. Removing exactly these appended bytes reproduces the previously reviewed CSS SHA256 `94898fde8f27e1c530d23ff015af5f487c6fe03b490d24aca033687ba92b024c`. UI source is unchanged. This is the smallest coherent parent-flex constraint: it allows the existing selector to shrink within available space, without overflow hiding, financial text formatting, node replacement, new behavior or effect on other modules. It also applies to the same account toolbar on Consolidado, so the controller's accumulated layout matrix remains required.

The builder's browser-only hypothesis receipt, attributed to that builder rather than this reviewer, reports toolbar client/scroll256/256, shell280/280, monthly wrapper/table228px,120three-cell month rows, no reported truncations, no page errors, zero real writer/command calls and unchanged financial snapshot. The receipt records2026-10-21T23:00:33.522524Z–23:00:39.555973Z and unchanged disk sources during diagnosis. It establishes a targeted hypothesis result, not a final official-build run. No additional runtime was launched by this reviewer for this follow-up, per controller scope.

No additional source concern was found in this bounded rule. Root must perform the authorized official rebuild and new focal/matrix/FULL receipts before package approval. The discovered original product failure remains a historical failure; neither the source verdict nor the hypothesis changes its raw result. Only this ignored review was updated.

## Original review — preceding CSS/build, retained as evidence

## Verdict and scope

**Specification review: PASS for the inspected product delta.**
**Code-quality review: PASS for the inspected product delta.**
No confirmed material defect or out-of-scope product change was found. These are bounded review verdicts, not approval of the final package, the test oracles, the complete required matrix, FULL, publication or human acceptance.

Reviewed the current two-file candidate against `candidate-a971-before.tar.gz`, the approved compact plan and the current Planning presentation contract. No product, test, generated file, governance document, dependency or Git state was edited. This ignored report is the only file written by this reviewer. No agent was spawned. All browser sessions were new synthetic Chromium contexts with service workers blocked; no owner profile/storage was accessed.

Root: `/Users/joaoalvescirqueira/Library/Mobile Documents/com~apple~CloudDocs/SOFTWARES & EAS/JP Wealth OS`.
Branch/HEAD confirmed by actual preflight: `codex/planejamento-patrimonial-20261020`, `ea15afc9c6a9`. Current coordinated dirty count:122; no cleanup/reset was attempted. Baseline117 preservation across the whole repository remains the controller's archive/freeze responsibility.

## Candidate identity

- UI: `7405635f20dfc9fd49f3ec65d0b2b0a91c5d5244ad9ed220a748e7a7dde3c23b`.
- CSS: `94898fde8f27e1c530d23ff015af5f487c6fe03b490d24aca033687ba92b024c`.
- Engine, independently compared byte-for-byte with archive: `d698bf884e8dce907c255f20170f76e5919938cde755f575847f63ce7dbba5b2`, identical.
- State, independently compared byte-for-byte with archive: `138b90185a9abaaef50f5cc83d86362592d5a8319ff471094a17f7ec223948f3`, identical.
- Native form/profile/stop template block: archive-identical.
- Entire UI block from `function monthActionsHTML` up to `function onClick`, including financial actions, native forms, drafts, `saveFutureCell` and PDF composition: archive-identical.

The controller reported official build `fd3e6dbc76e7b1e9` completed before authorizing the browser probes. Product hashes were independently checked before and after probes. The probes reuse bootstrap/seed helpers; the separately edited oracle files were not considered frozen or certified by importing them.

## Specification and source evidence

The user journey remains account selection → monthly table → month trigger/detail → existing action/confirmation, with the same financial read-model and writer. Consolidado reads confirmed facts, projection/goals and FX in three groups. Selecting a month changes local selection/context only; resizing moves controls between principal cells and detail slots. A deliberate field change still reaches the original `saveFutureCell` command path.

- `03-ui.js:112–116`: three summary groups, existing goals/projection selector and FX provenance. Financial amounts come from the existing read-model, without new conversion/formula.
- `03-ui.js:134–135`: current annual marker derives from local `monthNow`, separately from projection year; the renderer creates no artificial year row.
- `03-ui.js:147–168`: seven headers,120 month identities,12-month phase groups/subtotals and complementary facts. Compact values are moved rather than discarded. Zero/blank/nonfinite values keep distinct formatting. Current/finalized statuses coexist; passage of time does not finalize a month.
- `03-ui.js:171–186`: one detail expansion, `aria-expanded`/`aria-controls`, selected-row/context synchronization and guarded focus transfer when closing an edited detail.
- `03-ui.js:188–217`: useful-width900 breakpoint, existing-node movement, selection/focus restoration, safe fragment storage for omitted cells, observer/listener cleanup and no persistence in the resize path.
- `03-ui.js:47,57,64,68,547`: cleanup across mount/content replacement/incompatible state/deactivation; observer restarts after monthly render.
- `03-ui.js:534`: presentation-only synchronous changes are suppressed under the movement guard; ordinary user changes retain the existing delegate.
- `app.css:11203–11255`: additions are Planning-scoped, including dark current-year highlighting, stable table widths, wrapping, readable detail labels and separate wide/compact slots. No unrelated styles were changed by this delta.

Existing global/form/PDF mechanisms outside this delta remain protected rather than being reimplemented. No new schema, storage key, network request, dependency, public financial API or ongoing timer was introduced.

## Independent executions

### Preflight

Actual `python3 tools/agent_preflight.py --mode audit` before the official build exited1 with the then-unrefreshed UI manifest hash and122 dirty entries. No repair was attempted by this reviewer. After the controller's official build, the same command exited0, `PREFLIGHT PASS`; it still correctly reports the coordinated dirty tree. The first receipt is not silently relabeled as a pass.

### Focus/draft compatibility probe — PASS, actual exit0

Runtime: `/private/tmp/jpw-pf-default-frozen-runtime-20261017/bin/python3`, Playwright Chromium148.0.7778.96; `PYTHONDONTWRITEBYTECODE=1`; supplied `JP_WEALTH_CHROMIUM` path. Inline Python uses existing `planning_proportions_test.setup`, compact synthetic seed and real writer/command observation from `ui_visual_quality_test`; local `BrowserFixtureServer` serves the official index. No app responses or financial command implementations were replaced.

Procedure:1440×1000 monthly page → edit January2027 future contribution to exact partial text `12,` and select offsets2..3 → explicitly disable `Element.prototype.moveBefore` in this disposable browser to exercise the insertion fallback →390×844 →1440×1000 →390×844 → open November2026 → reopen January2027.

Observed at both width transitions: same focused connected input, exact `12,`, selectionStart2/selectionEnd3, expected compact/wide mode. Compact transition opened the owning January detail before migration. After switching details/reopening, same connected node and same partial text. Geometry check observed120 unique months, correct3/7 cell counts and no horizontal overflow in those two layouts. Actual writer calls `[]`; actual command calls `[]`; complete existing financial-family snapshot unchanged; page errors `[]`. This deliberately tested fallback does not constitute Safari execution.

### Keyboard/reopening/lifecycle probe — PASS, actual exit0

Fresh390×844 synthetic context. Opened current finalized account and used focus + keyboard Enter on October2026 month trigger. Observed `Em andamento · ✓ Finalizado`, `aria-expanded=true`, `aria-controls=pl-month-details-2026-10`.

Changed the visible moved Finalizado control to Não. The existing **Reabrir mês** dialog appeared with reason field and explicit confirmation. Escape cancelled it; actual writer calls `[]`, command calls `[]`, financial snapshot unchanged. Three subsequent Consolidado↔Mensal cycles left one monthly observer active (`created5/disconnected4`); final exit to Consolidado left none (`created5/disconnected5`). This instrumentation delegates to the real ResizeObserver. No page errors and no writes throughout the measured sequence. Consolidado exposed groups in confirmed/projection/FX order.

### Visual evidence viewed

Opened builder's `task-2-expansion-probe/compact.png` and `consolidated.png`. They show the intended grouping/currency hierarchy and inline detail presentation. They predate some final refinements and are supplementary visual context only, not final-candidate visual acceptance. Current runtime probe geometry above was independently executed after the official build.

## Limits and next gates

The scoped source and two supplemental browser journeys have no material findings. The final accumulated matrix, all scenarios/counterproofs,96-check FULL, distribution/offline/file/portable/PDF runtime, native200% zoom, full theme/layout coverage, screen reader, Safari and physical touch were not executed by this reviewer; the controller owns final required validation. No historical7/8 or previous package GREEN is transferred to these bytes. Human acceptance remains NOT_RUN.

Read/applied AGENTS, routed preflight/change-control/critical-review/browser/post-change skills, JP Engineering and its validation reference, task brief, approved plan, task2 report, relevant Planning contract/read-model/CSS and regression index. Harness provenance/hash is attributed to the controller's `source-authority.json`; the external Harness was not independently reread by this reviewer.

Agentic representation impact is already identified by the approved task: compact presentation replaces the documented18-column contract and affects visual/parity tests. The controller owns the separately authorized documentation/test reconciliation; this product review neither edits nor certifies those files. Product review PASS alone does not close that separate work.
