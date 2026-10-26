# Counterproof menu width — scratch proposal only

Observed receipt: full-after-bound-value/full-relocated-evidence/ui-visual-quality/ui-visual-quality-results.json. The positive control completed. The recorded error is `deliberate violation incorrectly accepted by runtime oracle`, at wrapping_menu → rejected, with no page errors. This proves the negative invocation did not raise an assertion; it does not identify the measured width or prove which event changed it. Earlier body/scroll positioning overwrite remains a hypothesis until a reproducer captures it.

The proposal changes only the mutation inside wrapping_menu from inline width322px!important to min-width322px!important and asserts getBoundingClientRect().width equals322 before entering the existing rejected(menu_geometry) call. Runtime positionMenu assigns width but does not assign min-width, so its ordinary positioning write cannot remove that CSS minimum. The existing geometry oracle still requires width <=320.25 CSS px; it is not edited. The mutation verification is outside rejected(), preventing a failed stimulus assertion from counting as a successful negative oracle. The full previous inline style is restored by the unchanged finally block on success or any exception.

No required IDs, 413-case registration,2px alignment threshold, .25 rounding allowance,900-second timeout, gate, application runtime or other assertions are edited in this scratch delta. Existing positive control and menu_geometry remain unchanged. The active repo file is untouched.

Risks and proof still required:

- This remains a proposed stimulus repair, not proof of causality or runtime correctness. Run the original and candidate against a controlled width-reposition event after current full execution ends and only in the newly authorized scope.
- Confirm computed322 in the actual700px context, the unchanged width-limit rejection, and exact original style restoration on every exit. A callback replacing the whole style attribute or node could still defeat min-width; no such callback was identified in the inspected positionMenu path.
- min-width can override width/max-width when CSS constraints conflict. That is deliberate synthetic corruption, confined to this test and reverted afterward. The current700px viewport accommodates322, but the explicit stimulus check makes a different layout fail instead of silently counting as a valid counterproof.
- No test, browser, GUI, app rebuild, source mutation or gate execution was performed for this proposal. Independent review, fresh specific human A4 approval and authorized proof are separate pending steps.

Artifacts: PROPOSAL.patch, before/candidate copies and fingerprints.json in this directory. Do not apply while full is running or without the separate authorization.
