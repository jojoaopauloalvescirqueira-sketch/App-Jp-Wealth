---
name: jpw-preflight
description: Prepare any JP Wealth audit or implementation by checking Git, authority, context freshness, manifest integrity, scope, and stop conditions. Use before every material task in this repository.
---

# JP Wealth Preflight

## Execute

1. Read `AGENTS.md` and `docs/governance/CONTEXT-MAP.md`.
2. Run:

```bash
python3 tools/agent_preflight.py --mode audit
git status --short --branch
git diff --stat
git diff
git log --oneline -5
```

3. For edits, rerun with `--mode edit`.
4. Read `PROJECT-CONTEXT.md`, `CURRENT-STATE.md`, `ACTIVE-TASK.md` and only the routed sources.
5. Record `BASE_SHA`, requested authority, N-level, allowed files, invariants and acceptance criteria.

## Stop when

- edit mode is on `main`;
- unknown changes are present;
- the task exceeds the recorded scope or authority;
- normative sources conflict;
- required context or manifest files are invalid;
- real credentials or private exports may enter the worktree.

Never repair a preflight failure silently. Report the exact condition and preserve user changes.
