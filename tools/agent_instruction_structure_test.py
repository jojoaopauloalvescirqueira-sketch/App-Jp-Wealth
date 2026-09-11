#!/usr/bin/env python3
"""Validate instruction structure and bounded CHG/CTX contracts, using stdlib.

This checks references, imports, approvals and Git anchors. It does NOT prove
that a client loaded instructions, that an agent understood them, or that a
written restriction is technically enforced. Populated approved_by/approved_at
fields establish structure only, not actual human authorization. Negative controls run only in
temporary synthetic repositories; the supplied --root is never modified.
Without --contract, the inline historical contracts remain the validation source.
An explicit source must be a canonical, nonsymlink docs/work/*.md file and its
contracts must be approved on the current branch. No referenced files are followed.
"""
import argparse
import copy
from datetime import datetime
import json
from pathlib import Path, PurePosixPath
import re
import shutil
import subprocess
import tempfile
import unicodedata


CORE = (
    "AGENTS.md", "CLAUDE.md", "docs/governance/CONTEXT-MAP.md",
    "docs/governance/AI-WORKFLOW.md", "docs/templates/TASK-BRIEF.md",
    "docs/governance/CHANGE-PROCESS.md", "docs/governance/CURRENT-STATE.md",
    "docs/work/ACTIVE-TASK.md",
)
ACTIVE = "docs/work/ACTIVE-TASK.md"
STATE = "docs/governance/CURRENT-STATE.md"
CHG_FIELDS = {
    "schema": str, "change_id": str, "status": str, "objective": str,
    "risk_level": str, "authority_required": str, "target": dict,
    "scope": dict, "derived_artifacts": dict, "external_side_effects": dict,
    "data": dict, "toolchain": dict, "acceptance_criteria": list,
    "approved_tests": list, "rollback": dict, "expires_on": list,
}
CTX_FIELDS = {
    "schema": str, "context_change_id": str, "status": str, "root": str,
    "mode": str, "approved_branch": str, "create": list, "modify": list,
    "merge": list, "preserve": list, "do_not_touch": list,
    "archive_requires_confirmation": list, "source_of_truth": dict,
    "information_promotion": list, "expiration_rules": list,
    "privacy_actions": list, "acceptance_criteria": list, "expires_on": list,
}

# Canonical containers from Harness §§12/24, not a human-approval verifier.
CHG_CONTAINERS = {
    "derived_artifacts": {"allowed": list, "generation_commands": list, "manual_edit": str},
    "external_side_effects": {"network": str, "allowed_targets": list,
                              "temporary_artifacts": str, "cleanup_required": bool},
    "data": {"test_policy": str, "approved_real_data": list, "schema_change": str},
    "toolchain": {"dependency_changes": list, "allowed_processes": list},
    "rollback": {"source": list, "application_state": list, "data": list,
                 "environment": list, "verification": list},
}
CHG_ENUMS = {
    ("derived_artifacts", "manual_edit"): ("forbidden", "allowed"),
    ("external_side_effects", "network"): ("forbidden", "allowed"),
    ("external_side_effects", "temporary_artifacts"): ("forbidden", "allowed"),
    ("data", "test_policy"): ("synthetic_only", "explicitly_approved"),
    ("data", "schema_change"): ("forbidden", "approved"),
}


def git(root, *args):
    return subprocess.run(["git", "-C", str(root), *args], text=True,
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE)


def prose(text):
    """Imports in examples/code fences are not actual Claude imports."""
    return re.sub(r"(?ms)^\s*(```|~~~)[^\n]*\n.*?^\s*\1\s*$", "", text)


def imports(text):
    return re.findall(r"(?<![\w`])@([\w./-]+\.md)\b", prose(text))


def normalize(text):
    return "".join(c for c in unicodedata.normalize("NFD", text.lower())
                   if not unicodedata.combining(c))


def reference_paths(text):
    refs = re.findall(r"`([^`\n]+\.md)`", prose(text))
    refs += re.findall(r"\]\(<?([^\n)>]+\.md)(?:#[^)>]*)?>?\)", prose(text))
    return refs + imports(text)


def contracts(text, source="ACTIVE-TASK"):
    found = {}
    for block in re.findall(r"(?ms)^```ya?ml\s*\n(.*?)^```\s*$", text):
        try:
            value = json.loads(block)
        except json.JSONDecodeError as exc:
            raise ValueError("contract fence must contain JSON (YAML 1.2 subset)") from exc
        if not isinstance(value, dict) or value.get("schema") not in {
                "jp-harness/chg/v1", "jp-harness/ctx/v1"}:
            raise ValueError("unknown/missing contract schema")
        if value["schema"] in found:
            raise ValueError("duplicate contract schema")
        found[value["schema"]] = value
    if set(found) != {"jp-harness/chg/v1", "jp-harness/ctx/v1"}:
        raise ValueError(source + " must contain one CHG and one CTX")
    return found["jp-harness/chg/v1"], found["jp-harness/ctx/v1"]


def explicit_contract_text(root, source):
    """Read only one canonical contract file, never a link or arbitrary path."""
    if not isinstance(source, str) or not re.fullmatch(
            r"docs/work/[A-Za-z0-9][A-Za-z0-9_.-]*\.md", source):
        raise ValueError("explicit contract must be a canonical docs/work/*.md file")
    path = root
    for part in PurePosixPath(source).parts:
        path = path / part
        if path.is_symlink():
            raise ValueError("explicit contract path contains symlink: " + source)
    if not path.resolve().is_relative_to(root) or not path.is_file():
        raise ValueError("explicit contract missing/escaped source: " + source)
    return path.read_text(encoding="utf-8")


def safe_target(root, value):
    if not isinstance(value, str) or not value or "\\" in value:
        return False
    p = PurePosixPath(value)
    if p.is_absolute() or any(x in {"..", ".", "~"} for x in p.parts):
        return False
    if any(c in value for c in "*?[]"):
        return False
    # This test governs instruction/context changes, not product or global config.
    permitted = value in {"AGENTS.md", "CLAUDE.md", "SESSION_HANDOFF.md",
                          "tools/agent_instruction_structure_test.py"}
    permitted |= (value.startswith("docs/") and value.endswith(".md")
                  and not value.startswith(("docs/normative/", "docs/decisions/")))
    permitted |= value == "skills/jpw-normative-audit/SKILL.md"
    if not permitted:
        return False
    return (root / value).resolve().is_relative_to(root)


def validate(root, contract_file=None):
    root = Path(root).resolve()
    errors, notices = [], []

    def require(ok, message):
        if not ok:
            errors.append(message)

    texts = {}
    for name in CORE:
        p = root / name
        require(p.is_file() and p.resolve().is_relative_to(root), "missing/escaped source: " + name)
        if p.is_file() and p.resolve().is_relative_to(root):
            texts[name] = p.read_text(encoding="utf-8")
    if len(texts) != len(CORE):
        return errors, notices
    repository = git(root, "rev-parse", "--show-toplevel")
    require(repository.returncode == 0 and Path(repository.stdout.strip()).resolve() == root,
            "--root must be the real Git repository root")

    require(imports(texts["CLAUDE.md"]) == ["AGENTS.md"],
            "CLAUDE must have exactly one import: @AGENTS.md")
    visited, visiting = set(), set()

    def visit(path):
        path = path.resolve()
        if not path.is_relative_to(root) or not path.is_file():
            errors.append("missing/escaped import: " + str(path))
            return
        if path in visiting:
            errors.append("cyclic instruction import: " + str(path.relative_to(root)))
            return
        if path in visited:
            return
        visiting.add(path)
        for target in imports(path.read_text(encoding="utf-8")):
            visit(path.parent / target)
        visiting.remove(path)
        visited.add(path)

    visit(root / "CLAUDE.md")
    required_links = {
        "AGENTS.md": ["docs/governance/CONTEXT-MAP.md", "docs/governance/AI-WORKFLOW.md",
                      "docs/templates/TASK-BRIEF.md"],
        "docs/governance/CONTEXT-MAP.md": ["AGENTS.md", "docs/governance/AI-WORKFLOW.md",
                                          "docs/templates/TASK-BRIEF.md"],
        "docs/templates/TASK-BRIEF.md": ["AGENTS.md", "docs/governance/CONTEXT-MAP.md"],
        "docs/governance/AI-WORKFLOW.md": ["AGENTS.md", "docs/governance/CONTEXT-MAP.md",
                                          "docs/templates/TASK-BRIEF.md"],
    }
    for source, targets in required_links.items():
        resolved = set()
        for value in reference_paths(texts[source]):
            for candidate in (root / value, (root / source).parent / value):
                if candidate.is_file() and candidate.resolve().is_relative_to(root):
                    resolved.add(candidate.resolve().relative_to(root).as_posix())
        for target in targets:
            require(target in resolved, source + " must reference " + target)

    try:
        source = ACTIVE if contract_file is None else contract_file
        contract_text = (texts[ACTIVE] if contract_file is None else
                         explicit_contract_text(root, contract_file))
        chg, ctx = contracts(contract_text, "ACTIVE-TASK" if contract_file is None else source)
    except ValueError as exc:
        return errors + [str(exc)], notices
    notices.append("contract selection: " + json.dumps({
        "mode": "historical-inline" if contract_file is None else "explicit-current",
        "source": source, "change_id": chg.get("change_id"),
        "context_change_id": ctx.get("context_change_id"),
    }, ensure_ascii=True, sort_keys=True))
    for obj, fields, label in [(chg, CHG_FIELDS, "CHG"), (ctx, CTX_FIELDS, "CTX")]:
        if contract_file is not None:
            require(obj.get("status") == "approved", label + " explicit contract must be approved")
        for field, kind in fields.items():
            empty_allowed = label == "CTX" and field in {
                "create", "modify", "merge", "archive_requires_confirmation"}
            require(isinstance(obj.get(field), kind) and (empty_allowed or bool(obj[field])),
                    label + " missing/invalid field: " + field)
        if obj.get("status") == "approved":
            require(isinstance(obj.get("approved_by"), str) and bool(obj["approved_by"].strip()),
                    label + " approved without approved_by")
            try:
                stamp = datetime.fromisoformat(obj["approved_at"].replace("Z", "+00:00"))
                require(stamp.tzinfo is not None, label + " approved_at requires timezone")
            except (KeyError, TypeError, ValueError, AttributeError):
                errors.append(label + " approved without valid approved_at")
        require(obj.get("status") in ("proposed", "approved", "expired", "completed", "rejected"),
                label + " unknown status")
    for container, fields in CHG_CONTAINERS.items():
        value = chg.get(container)
        if not isinstance(value, dict):
            continue  # The outer required-field check already reports this.
        for field, kind in fields.items():
            item = value.get(field)
            valid = isinstance(item, kind)
            if kind is list and valid:
                valid = all(isinstance(entry, str) and bool(entry.strip()) for entry in item)
            require(valid, "CHG invalid container field: " + container + "." + field)
    for (container, field), choices in CHG_ENUMS.items():
        value = chg.get(container)
        if isinstance(value, dict):
            require(value.get(field) in choices, "CHG invalid enum: " + container + "." + field)
    require(ctx.get("mode") in ("SEQUENCIAL", "INTERMEDIARIO", "CONCORRENTE"),
            "CTX invalid mode")
    for field in ["create", "modify", "preserve", "do_not_touch", "archive_requires_confirmation",
                  "privacy_actions", "acceptance_criteria", "expires_on"]:
        value = ctx.get(field)
        require(isinstance(value, list) and
                all(isinstance(item, str) and bool(item.strip()) for item in value),
                "CTX invalid string list: " + field)
    source = ctx.get("source_of_truth")
    require(isinstance(source, dict) and bool(source) and
            all(isinstance(key, str) and bool(key.strip()) and
                isinstance(value, str) and bool(value.strip()) for key, value in source.items()),
            "CTX invalid source_of_truth mapping")
    for field, keys in [("information_promotion", ("from", "to", "reason")),
                        ("expiration_rules", ("artifact", "event"))]:
        value = ctx.get(field)
        require(isinstance(value, list) and all(isinstance(item, dict) and
                all(isinstance(item.get(key), str) and bool(item[key].strip()) for key in keys)
                for item in value), "CTX invalid object list: " + field)
    target, scope = chg.get("target"), chg.get("scope")
    if not isinstance(target, dict) or not isinstance(scope, dict):
        return errors, notices
    require(chg.get("risk_level") == "N3" and chg.get("authority_required") == "A4",
            "control-plane CHG requires N3/A4")
    require(target.get("root") == ctx.get("root") == str(root), "CHG/CTX root mismatch")
    branch = target.get("branch")
    require(isinstance(branch, str) and bool(branch) and branch == ctx.get("approved_branch"),
            "CHG/CTX branch mismatch")
    allowed = scope.get("allowed_files")
    if not isinstance(allowed, list) or not allowed:
        return errors + ["CHG allowed_files must be nonempty list"], notices
    require(all(safe_target(root, p) for p in allowed), "CHG allowlist contains unsafe/product/global target")
    require(all(isinstance(p, str) for p in allowed) and len(set(map(str, allowed))) == len(allowed),
            "CHG allowlist contains duplicate/invalid paths")
    allowed_set = set(p for p in allowed if isinstance(p, str))
    touched = []
    for kind in ["create", "modify"]:
        values = ctx.get(kind, [])
        if isinstance(values, list):
            touched.extend(values)
    for item in ctx.get("merge", []) if isinstance(ctx.get("merge"), list) else []:
        if not isinstance(item, dict):
            errors.append("CTX merge entry must be object")
            continue
        touched.extend([item.get("source"), item.get("target")])
        require(item.get("source_must_remain") is True, "CTX merge must preserve source adapter")
    require(all(isinstance(p, str) and p in allowed_set and safe_target(root, p) for p in touched),
            "CTX target outside CHG allowlist")
    protected = ctx.get("do_not_touch")
    if isinstance(protected, list):
        # Compare explicit relative paths/directories. Free prose restrictions are
        # retained, but their meaning cannot be established by this structural test.
        for entry in protected:
            if isinstance(entry, str) and entry:
                prefix = entry.rstrip("/")
                require(not any(isinstance(path, str) and
                                (path == prefix or path.startswith(prefix + "/"))
                                for path in touched), "CTX edit conflicts with do_not_touch: " + entry)
    if isinstance(ctx.get("create"), list) and isinstance(ctx.get("modify"), list):
        created = set(p for p in ctx["create"] if isinstance(p, str))
        modified = set(p for p in ctx["modify"] if isinstance(p, str))
        require(not created.intersection(modified), "CTX create/modify overlap")
    for key in ["forbidden_files", "allowed_actions", "forbidden_actions", "regressions_forbidden"]:
        require(isinstance(scope.get(key), list) and bool(scope[key]), "CHG scope missing " + key)
    baseline = target.get("baseline_sha", "")
    require(isinstance(baseline, str) and bool(re.fullmatch(r"[0-9a-f]{40}", baseline)),
            "CHG baseline must be full commit SHA")
    if isinstance(baseline, str) and re.fullmatch(r"[0-9a-f]{40}", baseline):
        require(git(root, "cat-file", "-e", baseline + "^{commit}").returncode == 0,
                "CHG baseline commit unavailable")
        require(git(root, "merge-base", "--is-ancestor", baseline, "HEAD").returncode == 0,
                "CHG baseline not ancestor of checkout")
    # Historical contracts keep the feature branch name after legitimate merge.
    current = git(root, "branch", "--show-current").stdout.strip()
    if contract_file is not None:
        require(current == branch, "explicit contract branch differs from checkout")
    elif current != branch:
        notices.append("checkout differs from historical contract branch; no edit authority inferred")
    revisions = re.findall(r"(?im)^.*Source revision[^\n]*?`([0-9a-f]{40})`", texts[STATE])
    require(len(revisions) == 1, "CURRENT-STATE requires one full Source revision")
    for rev in revisions:
        require(git(root, "cat-file", "-e", rev + "^{commit}").returncode == 0,
                "CURRENT-STATE Source revision unavailable")
    for name in ["AGENTS.md", "docs/governance/CHANGE-PROCESS.md"]:
        text = normalize(texts[name])
        paragraphs = re.split(r"\n\s*\n", text)
        require(any(re.search(r"control[ -]plane|plano de controle", p) and "n3" in p and "a4" in p
                    for p in paragraphs), name + " lacks explicit control-plane N3/A4 classification")
        for line in text.splitlines():
            if ("n0-d" in line and re.search(r"control[ -]plane|plano de controle|harness|governanca", line)
                    and not re.search(r"\bnao\b|excet|exclu|sem alterar|sem mudanca.*autoridade", line)):
                errors.append(name + " contradicts control-plane classification with N0-D")
    return errors, notices


def synthetic_fixture(root):
    for name in CORE:
        p = root / name
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text("# Synthetic fixture\n", encoding="utf-8")
    links = "\n".join("`" + p + "`" for p in CORE if p != "CLAUDE.md")
    for name in ["AGENTS.md", "docs/governance/CONTEXT-MAP.md", "docs/governance/AI-WORKFLOW.md",
                 "docs/templates/TASK-BRIEF.md", "docs/governance/CHANGE-PROCESS.md"]:
        (root / name).write_text(links + "\n\nControl plane: N3 / A4.\n", encoding="utf-8")
    (root / "CLAUDE.md").write_text("@AGENTS.md\n", encoding="utf-8")
    git(root, "init", "-q")
    git(root, "add", ".")
    result = git(root, "-c", "user.name=Synthetic Fixture", "-c", "user.email=fixture@example.invalid",
                 "-c", "core.hooksPath=/dev/null", "commit", "-qm", "synthetic baseline")
    if result.returncode:
        raise RuntimeError("unable to create isolated synthetic Git fixture")
    sha = git(root, "rev-parse", "HEAD").stdout.strip()
    branch = git(root, "branch", "--show-current").stdout.strip()
    chg = {key: ({} if kind is dict else ["synthetic"] if kind is list else "synthetic")
           for key, kind in CHG_FIELDS.items()}
    ctx = {key: ({} if kind is dict else ["synthetic"] if kind is list else "synthetic")
           for key, kind in CTX_FIELDS.items()}
    for obj in [chg, ctx]:
        obj.update(status="approved", approved_by="synthetic owner", approved_at="2026-01-01T00:00:00Z")
    chg.update(schema="jp-harness/chg/v1", risk_level="N3", authority_required="A4",
               target={"root": str(root), "branch": branch, "baseline_sha": sha},
               scope={"allowed_files": list(CORE), "forbidden_files": ["outside"],
                      "allowed_actions": ["synthetic"], "forbidden_actions": ["publish"],
                      "regressions_forbidden": ["scope expansion"]})
    chg.update(
        derived_artifacts={"allowed": [], "generation_commands": [], "manual_edit": "forbidden"},
        external_side_effects={"network": "forbidden", "allowed_targets": [],
                               "temporary_artifacts": "allowed", "cleanup_required": True},
        data={"test_policy": "synthetic_only", "approved_real_data": [], "schema_change": "forbidden"},
        toolchain={"dependency_changes": [], "allowed_processes": ["python3"]},
        rollback={"source": ["Revert fixture delta only"], "application_state": [], "data": [],
                  "environment": ["Remove synthetic temporary directory"], "verification": ["Compare baseline"]})
    ctx.update(schema="jp-harness/ctx/v1", root=str(root), approved_branch=branch, mode="SEQUENCIAL",
               create=[], modify=list(CORE), merge=[], archive_requires_confirmation=[],
               preserve=["synthetic baseline"], do_not_touch=["src/"],
               source_of_truth={"instructions": "AGENTS.md"},
               information_promotion=[{"from": "CLAUDE.md", "to": "AGENTS.md", "reason": "Synthetic check"}],
               expiration_rules=[{"artifact": ACTIVE, "event": "Scope changes"}])
    (root / STATE).write_text("Source revision: `" + sha + "`\n", encoding="utf-8")
    return chg, ctx


def write_contracts(root, chg, ctx, source=ACTIVE):
    (root / source).write_text("\n\n".join("```yaml\n" + json.dumps(c) + "\n```"
                                            for c in [chg, ctx]), encoding="utf-8")


def explicit_controls(folder, base, chg, ctx):
    """Exercise source selection separately from the unchanged inline history."""
    source = "docs/work/CHG-SYNTHETIC.md"
    count = 0

    def fresh(name):
        root = folder / ("explicit-" + name)
        shutil.copytree(base, root)
        c, x = copy.deepcopy(chg), copy.deepcopy(ctx)
        c["target"]["root"] = x["root"] = str(root)
        write_contracts(root, c, x, source)
        return root, c, x

    def rejected(root, selected, cause, name):
        nonlocal count
        errors, _ = validate(root, selected)
        if not any(cause in error for error in errors):
            raise RuntimeError("explicit negative lacked expected cause: " + name +
                               "; observed: " + repr(errors))
        count += 1

    root, _, _ = fresh("valid")
    # The copy retains the old root in its inline contracts. Only the explicitly
    # selected pair describes this checkout; do not silently repair the history.
    errors, notices = validate(root, source)
    if errors or not any('"source": "' + source + '"' in notice for notice in notices):
        raise RuntimeError("explicit positive failed: " + repr(errors))
    rejected(root, None, "CHG/CTX root mismatch", "historical source still fails")

    for selected in [str(root / source), "../" + source, "./" + source,
                     "docs//work/CHG-SYNTHETIC.md", "docs/work/../CHG-SYNTHETIC.md",
                     "docs\\work\\CHG-SYNTHETIC.md", "docs/work/*.md",
                     "docs/work/nested/CHG-SYNTHETIC.md", "docs/governance/contract.md",
                     "docs/work/CHG-SYNTHETIC.txt", "docs/work/CHG-SYNTHETIC.md/", ""]:
        rejected(root, selected, "explicit contract must be a canonical", repr(selected))
    rejected(root, "docs/work/MISSING.md", "explicit contract missing/escaped source", "missing file")

    for field in ["chg", "ctx"]:
        for status in ["proposed", "expired", "completed", "rejected"]:
            root, c, x = fresh(field + "-" + status)
            (c if field == "chg" else x)["status"] = status
            write_contracts(root, c, x, source)
            rejected(root, source, field.upper() + " explicit contract must be approved", status)

    root, c, x = fresh("wrong-checkout-root")
    c["target"]["root"] = x["root"] = str(root.parent)
    write_contracts(root, c, x, source)
    rejected(root, source, "CHG/CTX root mismatch", "matching roots outside checkout")

    root, c, x = fresh("wrong-checkout-branch")
    c["target"]["branch"] = x["approved_branch"] = "synthetic-other"
    write_contracts(root, c, x, source)
    rejected(root, source, "explicit contract branch differs from checkout", "matching branches outside checkout")

    root, c, x = fresh("missing-baseline")
    c["target"]["baseline_sha"] = "0" * 40
    write_contracts(root, c, x, source)
    rejected(root, source, "CHG baseline commit unavailable", "missing baseline")

    root, c, x = fresh("unrelated-baseline")
    tree = git(root, "rev-parse", "HEAD^{tree}")
    orphan = git(root, "-c", "user.name=Synthetic Fixture", "-c", "user.email=fixture@example.invalid",
                 "-c", "core.hooksPath=/dev/null", "commit-tree", tree.stdout.strip(),
                 "-m", "Unrelated synthetic baseline")
    if tree.returncode or orphan.returncode:
        raise RuntimeError("unable to create unrelated synthetic baseline")
    c["target"]["baseline_sha"] = orphan.stdout.strip()
    write_contracts(root, c, x, source)
    rejected(root, source, "CHG baseline not ancestor of checkout", "unrelated baseline")

    bad_contents = {
        "missing-pair": ("# No contracts\n", source + " must contain one CHG and one CTX"),
        "duplicate-schema": ("```yaml\n" + json.dumps(chg) + "\n```\n" +
                             "```yaml\n" + json.dumps(chg) + "\n```\n", "duplicate contract schema"),
        "unknown-schema": ('```yaml\n{"schema":"unknown"}\n```\n', "unknown/missing contract schema"),
        "invalid-json": ("```yaml\nnot json\n```\n", "contract fence must contain JSON"),
    }
    for name, (content, cause) in bad_contents.items():
        root, _, _ = fresh(name)
        (root / source).write_text(content, encoding="utf-8")
        rejected(root, source, cause, name)

    for name in ["internal-link", "external-link", "work-link", "docs-link", "directory"]:
        root, _, _ = fresh(name)
        path = root / source
        if name == "directory":
            path.unlink()
            path.mkdir()
            cause = "explicit contract missing/escaped source"
        elif name in {"internal-link", "external-link"}:
            target = (root / "docs/work/original.md" if name == "internal-link" else
                      folder / "external-contract.md")
            path.rename(target)
            path.symlink_to(target)
            cause = "explicit contract path contains symlink"
        else:
            directory = root / ("docs/work" if name == "work-link" else "docs")
            target = root / ("original-work" if name == "work-link" else "original-docs")
            directory.rename(target)
            directory.symlink_to(target, target_is_directory=True)
            cause = "explicit contract path contains symlink"
        rejected(root, source, cause, name)
    return count


def negative_controls():
    mutations = {
        "missing import": lambda r, c, x: (r / "CLAUDE.md").write_text("@missing.md\n"),
        "duplicate import": lambda r, c, x: (r / "CLAUDE.md").write_text("@AGENTS.md\n@AGENTS.md\n"),
        "cyclic import": lambda r, c, x: (r / "AGENTS.md").write_text((r / "AGENTS.md").read_text() + "\n@CLAUDE.md\n"),
        "missing required source": lambda r, c, x: (r / "docs/templates/TASK-BRIEF.md").unlink(),
        "unapproved CHG": lambda r, c, x: c.pop("approved_by"),
        "unapproved CTX": lambda r, c, x: x.pop("approved_at"),
        "invented status": lambda r, c, x: c.update(status="invented-status"),
        "invalid mode": lambda r, c, x: x.update(mode="INVALID"),
        "missing data policy": lambda r, c, x: c.update(data={"synthetic": True}),
        "missing data container": lambda r, c, x: c.pop("data"),
        "invalid network": lambda r, c, x: c["external_side_effects"].update(network="INVALID"),
        "invalid manual edit": lambda r, c, x: c["derived_artifacts"].update(manual_edit="INVALID"),
        "invalid cleanup type": lambda r, c, x: c["external_side_effects"].update(cleanup_required="true"),
        "invalid data policy": lambda r, c, x: c["data"].update(test_policy="INVALID"),
        "invalid schema permission": lambda r, c, x: c["data"].update(schema_change="INVALID"),
        "invalid temporary artifacts": lambda r, c, x: c["external_side_effects"].update(temporary_artifacts="INVALID"),
        "invalid real data type": lambda r, c, x: c["data"].update(approved_real_data=True),
        "invalid process list": lambda r, c, x: c["toolchain"].update(allowed_processes=[True]),
        "invalid rollback type": lambda r, c, x: c["rollback"].update(source="INVALID"),
        "invalid source mapping": lambda r, c, x: x.update(source_of_truth={"synthetic": True}),
        "invalid promotion": lambda r, c, x: x.update(information_promotion=["synthetic"]),
        "invalid expiration": lambda r, c, x: x.update(expiration_rules=[{"artifact": ACTIVE}]),
        "protected edit": lambda r, c, x: x.update(do_not_touch=["AGENTS.md"]),
        "protected directory edit": lambda r, c, x: x.update(do_not_touch=["docs/"]),
        "unsafe allowlist": lambda r, c, x: c["scope"]["allowed_files"].append("src/js/new.js"),
        "global allowlist": lambda r, c, x: c["scope"]["allowed_files"].append("../global.md"),
        "CTX outside CHG": lambda r, c, x: x["modify"].append("docs/extra.md"),
        "weakened risk": lambda r, c, x: c.update(risk_level="N0-D"),
        "weakened authority": lambda r, c, x: c.update(authority_required="A2"),
        "contradictory classification": lambda r, c, x: (r / "AGENTS.md").write_text((r / "AGENTS.md").read_text() + "\nN0-D: governança e Harness.\n"),
        "root mismatch": lambda r, c, x: x.update(root=str(r.parent)),
        "branch mismatch": lambda r, c, x: x.update(approved_branch="synthetic-other"),
        "invalid source revision": lambda r, c, x: (r / STATE).write_text("Source revision: `" + "0" * 40 + "`\n"),
    }
    expected_causes = {
        "missing import": "missing/escaped import:",
        "duplicate import": "CLAUDE must have exactly one import:",
        "cyclic import": "cyclic instruction import:",
        "missing required source": "missing/escaped source: docs/templates/TASK-BRIEF.md",
        "unapproved CHG": "CHG approved without approved_by",
        "unapproved CTX": "CTX approved without valid approved_at",
        "invented status": "CHG unknown status",
        "invalid mode": "CTX invalid mode",
        "missing data policy": "CHG invalid container field: data.test_policy",
        "missing data container": "CHG missing/invalid field: data",
        "invalid network": "CHG invalid enum: external_side_effects.network",
        "invalid manual edit": "CHG invalid enum: derived_artifacts.manual_edit",
        "invalid cleanup type": "CHG invalid container field: external_side_effects.cleanup_required",
        "invalid data policy": "CHG invalid enum: data.test_policy",
        "invalid schema permission": "CHG invalid enum: data.schema_change",
        "invalid temporary artifacts": "CHG invalid enum: external_side_effects.temporary_artifacts",
        "invalid real data type": "CHG invalid container field: data.approved_real_data",
        "invalid process list": "CHG invalid container field: toolchain.allowed_processes",
        "invalid rollback type": "CHG invalid container field: rollback.source",
        "invalid source mapping": "CTX invalid source_of_truth mapping",
        "invalid promotion": "CTX invalid object list: information_promotion",
        "invalid expiration": "CTX invalid object list: expiration_rules",
        "protected edit": "CTX edit conflicts with do_not_touch: AGENTS.md",
        "protected directory edit": "CTX edit conflicts with do_not_touch: docs/",
        "unsafe allowlist": "CHG allowlist contains unsafe/product/global target",
        "global allowlist": "CHG allowlist contains unsafe/product/global target",
        "CTX outside CHG": "CTX target outside CHG allowlist",
        "weakened risk": "control-plane CHG requires N3/A4",
        "weakened authority": "control-plane CHG requires N3/A4",
        "contradictory classification": "AGENTS.md contradicts control-plane classification with N0-D",
        "root mismatch": "CHG/CTX root mismatch",
        "branch mismatch": "CHG/CTX branch mismatch",
        "invalid source revision": "CURRENT-STATE Source revision unavailable",
    }
    if set(mutations) != set(expected_causes):
        raise RuntimeError("every negative control must name its expected cause")
    with tempfile.TemporaryDirectory(prefix="jpw-instruction-structure-") as folder:
        folder = Path(folder).resolve()
        base = folder / "valid"
        base.mkdir()
        chg, ctx = synthetic_fixture(base)
        write_contracts(base, chg, ctx)
        errors, _ = validate(base)
        if errors:
            raise RuntimeError("positive synthetic control failed: " + "; ".join(errors))
        for number, (name, mutate) in enumerate(mutations.items()):
            root = folder / str(number)
            shutil.copytree(base, root)
            c, x = copy.deepcopy(chg), copy.deepcopy(ctx)
            c["target"]["root"] = x["root"] = str(root)
            mutate(root, c, x)
            write_contracts(root, c, x)
            source = "docs/work/CHG-SYNTHETIC.md"
            write_contracts(root, c, x, source)
            for selected in [None, source]:
                errors, _ = validate(root, selected)
                if not any(expected_causes[name] in error for error in errors):
                    raise RuntimeError("negative control lacked expected cause: " + name +
                                       "; source: " + repr(selected) + "; observed: " + repr(errors))
        count = 2 * len(mutations) + explicit_controls(folder, base, chg, ctx)
    return count


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--contract", help="Explicit current contract: canonical docs/work/*.md file")
    args = parser.parse_args()
    try:
        count = negative_controls()
        errors, notices = validate(args.root, args.contract)
    except (OSError, ValueError, RuntimeError) as exc:
        print("ENVIRONMENT_ERROR: " + str(exc))
        return 2
    print("SYNTHETIC CONTROLS PASS: positive fixtures + " + str(count) + " rejected negatives")
    for notice in notices:
        print("NOTICE: " + notice)
    for error in errors:
        print("PRODUCT_FAIL: " + error)
    print("LIMIT: structural evidence only; not proof of client loading, comprehension or enforcement")
    print("LIMIT: populated approval fields do not prove actual human authorization")
    if errors:
        return 1
    print("AGENT INSTRUCTION STRUCTURE PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
