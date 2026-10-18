#!/usr/bin/env python3
"""Opt-in structural checks for the frozen local JP Engenharia import.

Only main() creates isolated temporary fixtures. Importing this module and
validate(root) never execute project tests, load a gate, or modify the project.
"""

import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import shutil
import tempfile


PACKAGE = "skills/jp-ai-engineering"
LOCK = "skills/jp-ai-engineering.lock.json"
MEMORY = "tools/regression-memory.json"
ALIASES = (".agents/skills/jp-ai-engineering", ".claude/skills/jp-ai-engineering")
LINK_TARGET = "../../skills/jp-ai-engineering"
EXPECTED_FILES = frozenset((
    "SKILL.md",
    "agents/openai.yaml",
    "assets/AGENTS.template.md",
    "assets/personas/critico-integracao.toml",
    "assets/personas/engenheiro-integracao.toml",
    "assets/personas/operador-adversidades.toml",
    "assets/personas/operador-informado.toml",
    "assets/personas/usuario-iniciante.toml",
    "assets/protections.example.json",
    "assets/report.example.json",
    "references/contratos.md",
    "references/diagnostico.md",
    "references/fronteiras.md",
    "references/integracao-personas.md",
    "references/jp-wealth.md",
    "references/orquestracao.md",
    "references/provenance.json",
    "references/regras-regressoes.md",
    "references/validacao.md",
    "scripts/verify_protections.py",
))
STATES = {"fixed_regression", "open_incident", "baseline_limitation"}
LIMIT = ("LIMIT: structural integrity/references only; no model discovery, "
         "behavior, Git tracking, or full/CI gate coverage is established.")


def _text(value):
    return isinstance(value, str) and bool(value.strip())


def _relative(value):
    """Require canonical portable relative names, never Git metadata."""
    if not _text(value) or "\\" in value or "\0" in value:
        return False
    path = PurePosixPath(value)
    return (not path.is_absolute() and path.as_posix() == value
            and not any(part in (".", "..", ".git") for part in value.split("/"))
            and not re.match(r"^[A-Za-z]:", value))


def _physical(root, relative, errors, label, directory=False):
    if not _relative(relative):
        errors.append(f"{label}: unsafe relative path {relative!r}")
        return None
    path = root
    try:
        for part in PurePosixPath(relative).parts:
            path = path / part
            if path.is_symlink():
                errors.append(f"{label}: symlink component {relative!r}")
                return None
        resolved = path.resolve(strict=True)
        if not resolved.is_relative_to(root):
            errors.append(f"{label}: escaping path {relative!r}")
            return None
        if not (path.is_dir() if directory else path.is_file()):
            errors.append(f"{label}: expected physical {'directory' if directory else 'file'} {relative!r}")
            return None
        return path
    except (OSError, RuntimeError) as exc:
        errors.append(f"{label}: missing or unreadable path {relative!r}: {exc}")
        return None


def _unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key {key!r}")
        result[key] = value
    return result


def _read_json(root, relative, errors):
    path = _physical(root, relative, errors, relative)
    if path is None:
        return None
    try:
        value = json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=_unique_object)
    except (OSError, UnicodeError, ValueError) as exc:
        errors.append(f"{relative}: invalid JSON: {exc}")
        return None
    if not isinstance(value, dict):
        errors.append(f"{relative}: expected JSON object")
        return None
    return value


def _inventory(directory, errors):
    found = set()

    def visit(folder):
        try:
            for child in sorted(folder.iterdir()):
                relative = child.relative_to(directory).as_posix()
                if child.is_symlink():
                    errors.append(f"package: symlink is forbidden: {relative!r}")
                    found.add(relative)
                elif child.is_dir():
                    visit(child)
                elif child.is_file():
                    found.add(relative)
                else:
                    errors.append(f"package: nonregular entry {relative!r}")
                    found.add(relative)
        except OSError as exc:
            errors.append(f"package: cannot inspect inventory: {exc}")

    visit(directory)
    return found


def _check_import(root, errors):
    lock = _read_json(root, LOCK, errors)
    package = _physical(root, PACKAGE, errors, "package", directory=True)
    if package is not None:
        found = _inventory(package, errors)
        for name in sorted(EXPECTED_FILES - found):
            errors.append(f"package: missing file {name!r}")
        for name in sorted(found - EXPECTED_FILES):
            errors.append(f"package: unexpected file {name!r}")
    if lock is None:
        return
    for key, expected in (("schema", "jpwealth/skill-import/v1"),
                          ("name", "jp-ai-engineering"), ("version", "1.3.0"),
                          ("policy", "frozen_import")):
        if lock.get(key) != expected:
            errors.append(f"lock: invalid {key}")
    source = lock.get("source")
    if not isinstance(source, dict) or source.get("plugin") != "jp-ai-engineering" or source.get("version") != "1.3.0":
        errors.append("lock: invalid source identity")
    files = lock.get("files")
    if not isinstance(files, dict) or not files:
        errors.append("lock: files must be a nonempty object with the exact 20 files")
        return
    if set(files) != EXPECTED_FILES:
        errors.append("lock: file inventory differs from the exact 20-file package")
    for name, expected_hash in files.items():
        if not _relative(name):
            errors.append(f"lock: unsafe file path {name!r}")
            continue
        if not isinstance(expected_hash, str) or re.fullmatch(r"[0-9a-f]{64}", expected_hash) is None:
            errors.append(f"lock: invalid sha256 for {name!r}")
            continue
        path = _physical(root, f"{PACKAGE}/{name}", errors, "lock file")
        if path is not None:
            try:
                actual = hashlib.sha256(path.read_bytes()).hexdigest()
                if actual != expected_hash:
                    errors.append(f"lock: hash mismatch for {name!r}")
            except OSError as exc:
                errors.append(f"lock: cannot hash {name!r}: {exc}")


def _check_aliases(root, errors):
    expected = root / PACKAGE
    for relative in ALIASES:
        link = root / relative
        parent = _physical(root, str(PurePosixPath(relative).parent), errors, "alias parent", directory=True)
        if parent is None:
            continue
        try:
            if not link.is_symlink():
                errors.append(f"alias: expected symlink {relative!r}")
                continue
            if str(link.readlink()) != LINK_TARGET:
                errors.append(f"alias: wrong relative target for {relative!r}")
            resolved = link.resolve(strict=True)
            if not resolved.is_relative_to(root) or resolved != expected.resolve(strict=True):
                errors.append(f"alias: escaping or incorrect resolution for {relative!r}")
        except (OSError, RuntimeError) as exc:
            errors.append(f"alias: cannot resolve {relative!r}: {exc}")


def _check_memory(root, errors):
    memory = _read_json(root, MEMORY, errors)
    if memory is None:
        return
    if memory.get("schema") != "jpwealth/regression-memory/v1":
        errors.append("memory: invalid schema")
    entries = memory.get("entries")
    if not isinstance(entries, list) or not entries:
        errors.append("memory: entries must be a nonempty array")
        return
    identifiers = set()
    for index, entry in enumerate(entries):
        label = f"memory entry {index}"
        if not isinstance(entry, dict):
            errors.append(f"{label}: expected object")
            continue
        for field in ("id", "state", "summary", "stimulus", "expected", "cause"):
            if not _text(entry.get(field)):
                errors.append(f"{label}: missing nonempty {field}")
        identifier = entry.get("id")
        if _text(identifier):
            if identifier in identifiers:
                errors.append(f"{label}: duplicate id {identifier!r}")
            identifiers.add(identifier)
        state = entry.get("state")
        if not isinstance(state, str) or state not in STATES:
            errors.append(f"{label}: invalid state")
        source = entry.get("source")
        if not isinstance(source, dict):
            errors.append(f"{label}: missing source object")
        else:
            _physical(root, source.get("path"), errors, f"{label} source.path")
            if not _text(source.get("section")):
                errors.append(f"{label}: missing source.section")
        protection = entry.get("protection")
        if not isinstance(protection, dict):
            errors.append(f"{label}: missing protection object")
        else:
            for field in ("path", "case", "command"):
                if field not in protection or (protection[field] is not None and not _text(protection[field])):
                    errors.append(f"{label}: protection.{field} must be a nonempty string or null")
            if protection.get("path") is not None:
                _physical(root, protection.get("path"), errors, f"{label} protection.path")
            if state == "fixed_regression" and not all(_text(protection.get(field)) for field in ("path", "case", "command")):
                errors.append(f"{label}: fixed regression requires protection path, specific case and command")
            if protection.get("path") is None and any(protection.get(field) is not None for field in ("case", "command")):
                errors.append(f"{label}: protection case/command requires a path")
            gate = protection.get("full_gate")
            if not isinstance(gate, dict) or not isinstance(gate.get("included"), bool):
                errors.append(f"{label}: full_gate requires boolean included")
            elif (gate["included"] and not _text(gate.get("check_id"))) or (not gate["included"] and gate.get("check_id") is not None):
                errors.append(f"{label}: inconsistent full_gate check_id")
            elif "check_id" not in gate:
                errors.append(f"{label}: full_gate requires check_id string or null")
        evidence = entry.get("evidence")
        if not isinstance(evidence, list) or not all(isinstance(item, dict) for item in evidence):
            errors.append(f"{label}: evidence must be an array of objects")
        # Optional evidence receipts are deliberately never required or executed.
        verified = entry.get("last_verified")
        if not isinstance(verified, dict) or not _text(verified.get("build")):
            errors.append(f"{label}: last_verified requires a nonempty build")


def validate(root):
    """Return structural errors without mutation or execution of project code."""
    errors = []
    try:
        root = Path(root).resolve(strict=True)
        if not root.is_dir():
            return ["root: expected directory"]
    except (OSError, RuntimeError) as exc:
        return [f"root: cannot resolve directory: {exc}"]
    _check_import(root, errors)
    _check_aliases(root, errors)
    _check_memory(root, errors)
    return errors


def _write_json(path, data):
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _fixture(source, destination):
    """Copy only import metadata and mandatory references, never Git/receipts."""
    memory = json.loads((source / MEMORY).read_text(encoding="utf-8"))
    files = {LOCK, MEMORY} | {f"{PACKAGE}/{name}" for name in EXPECTED_FILES}
    for entry in memory["entries"]:
        files.add(entry["source"]["path"])
        if entry["protection"]["path"] is not None:
            files.add(entry["protection"]["path"])
    for relative in files:
        target = destination / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source / relative, target)
    for relative in ALIASES:
        target = destination / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.symlink_to(LINK_TARGET, target_is_directory=True)


def _counterproofs(source):
    """Each mutation starts from an independently valid miniature install."""
    failures = []
    controls = 0
    with tempfile.TemporaryDirectory(prefix="jpw-engineering-integration-") as directory:
        temp = Path(directory)
        template = temp / "template"
        _fixture(source, template)
        positive = validate(template)
        if positive:
            return [f"counterproof true-positive: {positive}"], 0
        controls += 1

        def run(name, mutate, expected):
            nonlocal controls
            target = temp / name
            shutil.copytree(template, target, symlinks=True)
            mutate(target)
            errors = validate(target)
            if not any(expected in error for error in errors):
                failures.append(f"counterproof {name}: expected {expected!r}; got {errors}")
            controls += 1

        def edit_json(target, relative, mutate):
            path = target / relative
            data = json.loads(path.read_text(encoding="utf-8"))
            mutate(data)
            _write_json(path, data)

        def altered_byte(target):
            path = target / PACKAGE / "SKILL.md"
            data = path.read_bytes()
            path.write_bytes(bytes([data[0] ^ 1]) + data[1:])

        def escaping_link(target):
            link = target / ALIASES[0]
            link.unlink()
            link.symlink_to(temp, target_is_directory=True)

        def escaping_file(target):
            path = target / PACKAGE / "SKILL.md"
            path.unlink()
            path.symlink_to(source / PACKAGE / "SKILL.md")

        run("bad-byte", altered_byte, "hash mismatch")
        run("missing-file", lambda target: (target / PACKAGE / "SKILL.md").unlink(), "package: missing file")
        run("extra-file", lambda target: (target / PACKAGE / "extra.txt").write_text("extra", encoding="utf-8"), "package: unexpected file")
        run("path-escape", lambda target: edit_json(target, LOCK, lambda data: data["files"].update({"../escape.md": "0" * 64})), "lock: unsafe file path")
        run("absolute-path", lambda target: edit_json(target, LOCK, lambda data: data["files"].update({str(temp / "escape.md"): "0" * 64})), "lock: unsafe file path")
        run("invalid-hash", lambda target: edit_json(target, LOCK, lambda data: data["files"].update({"SKILL.md": "invalid"})), "lock: invalid sha256")
        run("link-escape", escaping_link, "alias: escaping or incorrect resolution")
        run("file-link-escape", escaping_file, "package: symlink is forbidden")
        run("missing-regression-ref", lambda target: edit_json(target, MEMORY, lambda data: data["entries"][0]["source"].update({"path": "docs/missing-regression-source.md"})), "source.path: missing or unreadable")
        run("duplicate-id", lambda target: edit_json(target, MEMORY, lambda data: data["entries"].append(data["entries"][0].copy())), "duplicate id")
        run("empty-manifest", lambda target: edit_json(target, LOCK, lambda data: data.update({"files": {}})), "lock: files must be a nonempty object")
        run("empty-memory", lambda target: edit_json(target, MEMORY, lambda data: data.update({"entries": []})), "memory: entries must be a nonempty array")
    return failures, controls


def main():
    root = Path(__file__).resolve().parents[1]
    errors = validate(root)
    controls = 0
    if not errors:
        errors, controls = _counterproofs(root)
    if errors:
        print(f"FAIL: {len(errors)} structural/counterproof error(s)")
        for error in errors:
            print(f"- {error}")
        print(LIMIT)
        return 1
    memory = json.loads((root / MEMORY).read_text(encoding="utf-8"))
    print(f"PASS: files={len(EXPECTED_FILES)} aliases={len(ALIASES)} regression_entries={len(memory['entries'])} controls={controls}")
    print(LIMIT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
