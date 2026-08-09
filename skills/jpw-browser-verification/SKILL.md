---
name: jpw-browser-verification
description: Verify JP Wealth UI changes in a real browser across workflows, state, themes, responsive viewports, console, and layout. Use for onboarding, modals, navigation, dashboard, accounting, notes, settings, PWA, or visual behavior.
---

# JP Wealth Browser Verification

## Prepare

Serve the repository with `python3 tools/serve.py`; do not rely on source reading alone. Use synthetic state and isolate browser storage from real operator data.

## Verify the workflow

- Execute entry, interaction, validation, persistence/reload and exit.
- Capture console errors, `pageerror` and failed requests.
- Check keyboard operation, focus return, Escape/outside-click behavior and modal inert state.
- Test affected desktop and mobile widths, both themes when supported.
- Check overflow, overlap, occlusion, fixed controls and text containment.
- For canvas/charts, verify nonblank pixels and dimensions, not just element presence.

## Evidence

Record viewport, initial state, steps, expected/actual behavior and screenshots for visual claims. A screenshot alone does not prove persistence or calculation; pair it with state assertions. Do not capture credentials or real balances.
