#!/usr/bin/env python3
"""Read-only repository preflight for human and AI contributors."""

from __future__ import annotations

import argparse
from datetime import date, datetime
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
REQUIRED_CONTEXT = (
    "AGENTS.md",
    "CLAUDE.md",
    "docs/governance/PROJECT-CONTEXT.md",
    "docs/governance/CURRENT-STATE.md",
    "docs/governance/CONTEXT-MAP.md",
    "docs/governance/QUALITY-GATES.md",
    "docs/work/ACTIVE-TASK.md",
    "SESSION_HANDOFF.md",
    "src/js/manifest.json",
)
PRIVATE_PATH_PATTERNS = (
    re.compile(r"(^|/)(?:\.env)(?:\.|$)", re.I),
    re.compile(r"(^|/)(?:data/(?:backups|exports|private))(?:/|$)", re.I),
    re.compile(r"(?:credential|password|secret|token)", re.I),
    re.compile(r"jpwealth_v9_state.*\.json$", re.I),
)


def git(*args: str, check: bool = True) -> str:
    completed = subprocess.run(
        ["git", *args], cwd=ROOT, text=True, capture_output=True, check=False
    )
    if check and completed.returncode:
        detail = completed.stderr.strip() or completed.stdout.strip()
        raise RuntimeError(f"git {' '.join(args)}: {detail}")
    return completed.stdout.rstrip()


def parse_snapshot_date(path: Path) -> date | None:
    match = re.search(r"(?:Data da fotografia|Atualizado em):\s*(\d{4}-\d{2}-\d{2})", path.read_text(encoding="utf-8"))
    if not match:
        return None
    try:
        return date.fromisoformat(match.group(1))
    except ValueError:
        return None


def inspect_manifest(errors: list[str], facts: dict[str, object]) -> None:
    manifest_path = ROOT / "src/js/manifest.json"
    index_path = ROOT / "index.html"
    if not manifest_path.exists() or not index_path.exists():
        return
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        errors.append(f"manifest invalido: {exc}")
        return

    index = index_path.read_text(encoding="utf-8")
    positions: list[int] = []
    for item in manifest.get("files", []):
        relative = item.get("path", "")
        source = ROOT / relative
        if not relative or not source.is_file():
            errors.append(f"script do manifest ausente: {relative or '<sem path>'}")
            continue
        actual = hashlib.sha256(source.read_bytes()).hexdigest()
        if actual != item.get("sha256"):
            errors.append(f"hash divergente: {relative}")
        tag = f'<script src="{relative}"></script>'
        position = index.find(tag)
        if position < 0:
            errors.append(f"script nao referenciado no index: {relative}")
        positions.append(position)
    if positions != sorted(positions):
        errors.append("ordem dos scripts diverge de src/js/manifest.json")
    facts["manifest_scripts"] = len(manifest.get("files", []))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=("audit", "edit"), default="audit")
    parser.add_argument(
        "--allow-dirty",
        action="store_true",
        help="Aceita alteracoes conhecidas; use somente em retomada explicitamente coordenada.",
    )
    parser.add_argument("--json", action="store_true", dest="as_json")
    args = parser.parse_args()

    errors: list[str] = []
    warnings: list[str] = []
    facts: dict[str, object] = {
        "root": str(ROOT),
        "mode": args.mode,
        "checked_at": datetime.now().astimezone().isoformat(timespec="seconds"),
    }

    try:
        git_root = Path(git("rev-parse", "--show-toplevel")).resolve()
        branch = git("branch", "--show-current") or "DETACHED"
        head = git("rev-parse", "--short=12", "HEAD")
        status_lines = [line for line in git("status", "--porcelain=v1").splitlines() if line]
        tracked = [line for line in git("ls-files").splitlines() if line]
        candidates = [
            line for line in git("ls-files", "--cached", "--others", "--exclude-standard").splitlines()
            if line
        ]
    except RuntimeError as exc:
        errors.append(str(exc))
        git_root, branch, head, status_lines, tracked, candidates = ROOT, "UNKNOWN", "UNKNOWN", [], [], []

    facts.update(
        {
            "git_root": str(git_root),
            "branch": branch,
            "head": head,
            "dirty_entries": len(status_lines),
            "tracked_files": len(tracked),
            "versionable_files": len(candidates),
        }
    )
    if git_root != ROOT.resolve():
        errors.append(f"raiz Git inesperada: {git_root}")
    if args.mode == "edit" and branch in {"main", "master", "DETACHED", "UNKNOWN"}:
        errors.append(f"edicao bloqueada na branch {branch}")
    if status_lines:
        message = f"arvore possui {len(status_lines)} alteracao(oes); confirme autoria e escopo"
        if args.mode == "edit" and not args.allow_dirty:
            errors.append(message)
        else:
            warnings.append(message)

    missing = [relative for relative in REQUIRED_CONTEXT if not (ROOT / relative).is_file()]
    if missing:
        errors.append("contexto obrigatorio ausente: " + ", ".join(missing))

    current_state = ROOT / "docs/governance/CURRENT-STATE.md"
    if current_state.is_file():
        snapshot_date = parse_snapshot_date(current_state)
        facts["current_state_date"] = snapshot_date.isoformat() if snapshot_date else None
        if snapshot_date is None:
            warnings.append("CURRENT-STATE.md nao declara data da fotografia")
        else:
            age = (date.today() - snapshot_date).days
            facts["current_state_age_days"] = age
            if age > 30:
                warnings.append(f"CURRENT-STATE.md tem {age} dias; revalidar antes de confiar")

    sensitive = [
        path for path in candidates
        if path != ".gitignore"
        and not path.endswith("/.gitkeep")
        and any(pattern.search(path) for pattern in PRIVATE_PATH_PATTERNS)
    ]
    if sensitive:
        errors.append("caminhos potencialmente sensiveis rastreados: " + ", ".join(sensitive))
    facts["sensitive_candidate_paths"] = sensitive

    inspect_manifest(errors, facts)
    result = "PASS" if not errors else "BLOCKED"
    payload = {"result": result, "facts": facts, "warnings": warnings, "errors": errors}

    if args.as_json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print(f"PREFLIGHT {result}")
        print(f"- branch: {branch}")
        print(f"- HEAD: {head}")
        print(f"- rastreados: {len(tracked)}")
        print(f"- alteracoes: {len(status_lines)}")
        print(f"- scripts no manifest: {facts.get('manifest_scripts', 0)}")
        for warning in warnings:
            print(f"- AVISO: {warning}")
        for error in errors:
            print(f"- BLOQUEIO: {error}")
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
