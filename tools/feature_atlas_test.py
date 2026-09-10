#!/usr/bin/env python3
"""Read-only structural validation of the bounded, three-record Feature Atlas.

Hashes, literal symbol anchors and known relation endpoints do not establish
call semantics, runtime behavior, feature completeness or agent comprehension.
No Graphify, model service or external request is used. --self-test writes only
its own TemporaryDirectory fixtures; normal validation writes JSON to stdout.
"""
import argparse
import copy
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import subprocess
import tempfile

ATLAS = "docs/architecture/FEATURE-ATLAS.md"
SKILL = "skills/jpw-feature-atlas"
LINKS = (".agents/skills/jpw-feature-atlas", ".claude/skills/jpw-feature-atlas")
IMPLEMENTATIONS = ("available", "partial", "internal", "disabled", "placeholder", "proposed")
EVIDENCE = ("declared", "code-inspected", "observed", "tested")
FRESHNESS = ("verified-for-revision", "needs-review", "historical")
RELATIONS = ("NAVEGA_PARA", "CHAMA", "LE", "GRAVA", "EMITE", "CONSOME", "DERIVA", "VALIDA", "DEPENDE_DE")
SHA = re.compile(r"[0-9a-f]{40}\Z")
HASH = re.compile(r"[0-9a-f]{64}\Z")
LIMIT = "Structural evidence only: literal anchors do not prove semantics, runtime behavior, comprehension or human authorization."


def nonempty(value):
    return isinstance(value, str) and bool(value.strip())


def inside_file(root, value):
    if not nonempty(value) or "\\" in value or "\x00" in value:
        return None
    path = PurePosixPath(value)
    if path.is_absolute() or any(p in ("", ".", "..", "~") for p in value.split("/")):
        return None
    try:
        resolved = (root / value).resolve()
        if resolved.is_relative_to(root) and resolved.is_file():
            return resolved
    except (OSError, RuntimeError, ValueError):
        pass
    return None


def revision_exists(root, revision):
    result = subprocess.run(
        ["git", "--no-optional-locks", "-C", str(root), "cat-file", "-e", revision + "^{commit}"],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False,
    )
    return result.returncode == 0


def validate(root, revision_check=None):
    """Return diagnostics without changing the supplied tree or its metadata."""
    root = Path(root).resolve()
    errors = []
    examined = []

    def require(ok, code, detail):
        if not ok:
            errors.append({"code": code, "detail": detail})

    atlas_path = inside_file(root, ATLAS)
    if atlas_path is None:
        return {"result": "PRODUCT_FAIL", "errors": [{"code": "ATLAS_PATH", "detail": ATLAS}], "records": 0, "examined_sources": []}
    text = atlas_path.read_text(encoding="utf-8")
    blocks = re.findall(r"(?ms)^```atlas-json[ \t]*\n(.*?)^```[ \t]*$", text)
    require(len(blocks) == 3 and len(re.findall(r"(?m)^```atlas-json\b", text)) == 3,
            "RECORD_COUNT", "Exactly three complete atlas-json blocks are required")
    records = []
    for number, block in enumerate(blocks, 1):
        try:
            obj = json.loads(block)
            if not isinstance(obj, dict):
                raise ValueError("record must be an object")
            records.append(obj)
        except (ValueError, json.JSONDecodeError) as exc:
            require(False, "PAYLOAD", "block " + str(number) + ": " + str(exc))
    ids = set()
    revisions = set()
    for number, record in enumerate(records, 1):
        label = "record " + str(number)
        fid = record.get("feature_id")
        require(nonempty(fid), "FEATURE_ID", label)
        if nonempty(fid):
            require(fid not in ids, "DUPLICATE_ID", fid)
            ids.add(fid)
            label = fid
        require(nonempty(record.get("name")), "NAME", label)
        for field, choices in (("implementation", IMPLEMENTATIONS), ("evidence_level", EVIDENCE), ("freshness", FRESHNESS)):
            require(record.get(field) in choices, "DIMENSION", label + ": " + field)
        revision = record.get("revision")
        good_revision = isinstance(revision, str) and SHA.fullmatch(revision) is not None
        require(good_revision, "REVISION", label + ": full commit SHA required")
        if good_revision and revision not in revisions:
            check = revision_check or (lambda value: revision_exists(root, value))
            require(check(revision), "REVISION_UNAVAILABLE", revision)
            revisions.add(revision)
        sources = record.get("sources")
        if not isinstance(sources, list) or not sources:
            require(False, "SOURCES", label)
            sources = []
        anchors = set()
        source_paths = set()
        for source in sources:
            if not isinstance(source, dict):
                require(False, "SOURCE_OBJECT", label)
                continue
            path = source.get("path")
            file = inside_file(root, path)
            require(file is not None, "SOURCE_PATH", label + ": " + repr(path))
            if isinstance(path, str):
                require(path not in source_paths, "DUPLICATE_SOURCE", label + ": " + path)
                source_paths.add(path)
            symbols = source.get("symbols")
            valid_symbols = isinstance(symbols, list) and bool(symbols) and all(nonempty(s) and "#" not in s and "\n" not in s for s in symbols)
            require(valid_symbols, "SYMBOL_LIST", label + ": " + repr(path))
            if file is None:
                continue  # Never read a source before checking containment.
            raw = file.read_bytes()
            expected = source.get("sha256")
            require(isinstance(expected, str) and HASH.fullmatch(expected) is not None,
                    "SOURCE_HASH_FORMAT", label + ": " + path)
            actual = hashlib.sha256(raw).hexdigest()
            require(expected == actual, "SOURCE_HASH_DRIFT", label + ": " + path)
            examined.append({"feature_id": fid, "path": path, "sha256": actual})
            try:
                content = raw.decode("utf-8")
            except UnicodeDecodeError:
                require(False, "SOURCE_ENCODING", label + ": " + path)
                continue
            if valid_symbols:
                require(len(symbols) == len(set(symbols)), "DUPLICATE_SYMBOL", label + ": " + path)
                for symbol in symbols:
                    # Literal anchors, with identifier boundaries, including state paths.
                    present = re.search(r"(?<![\w$])" + re.escape(symbol) + r"(?![\w$])", content) is not None
                    require(present, "SYMBOL_MISSING", path + "#" + symbol)
                    if present:
                        anchors.add(path + "#" + symbol)
        relations = record.get("relations")
        if not isinstance(relations, list) or not relations:
            require(False, "RELATIONS", label)
            relations = []
        for relation in relations:
            if not isinstance(relation, dict):
                require(False, "RELATION_OBJECT", label)
                continue
            require(relation.get("type") in RELATIONS, "RELATION_TYPE", label)
            require(nonempty(relation.get("condition")), "RELATION_CONDITION", label)
            for field in ("origin", "target", "evidence"):
                value = relation.get(field)
                require(isinstance(value, str) and value in anchors,
                        "RELATION_ORPHAN", label + ": " + field + "=" + repr(value))
    for name in LINKS:
        link = root / name
        try:
            target = os.readlink(link) if link.is_symlink() else None
            safe = target is not None and not Path(target).is_absolute()
            resolved = link.resolve()
            safe = safe and resolved.is_relative_to(root) and resolved == (root / SKILL).resolve()
            safe = safe and inside_file(root, SKILL + "/SKILL.md") is not None
        except (OSError, RuntimeError, ValueError):
            safe = False
        require(safe, "NATIVE_LINK", name)
    return {"result": "PRODUCT_FAIL" if errors else "PASS", "errors": errors,
            "records": len(records), "examined_sources": examined,
            "effects": {"repository_writes_requested": False, "network_requested": False,
                        "git_operations": ["cat-file -e <revision>^{commit}"] if revision_check is None else [],
                        "note": "These fields describe the validator; they are not a universal process audit."}}


def snapshot(root):
    """Measure all synthetic fixture paths, content and modification metadata."""
    result = {}
    for path in [root] + sorted(root.rglob("*")):
        stat = path.lstat()
        kind = "symlink" if path.is_symlink() else "directory" if path.is_dir() else "file"
        payload = os.readlink(path) if kind == "symlink" else hashlib.sha256(path.read_bytes()).hexdigest() if kind == "file" else None
        result[str(path.relative_to(root))] = (kind, stat.st_mode, stat.st_mtime_ns, payload)
    return result


def self_test():
    """Counterexamples use fixed diagnostic codes, never arbitrary failure."""
    cases = []
    with tempfile.TemporaryDirectory(prefix="jpw-atlas-structure-") as folder:
        root = Path(folder).resolve() / "fixture"
        root.mkdir()
        source = root / "source.js"
        source.write_text("const fixtureValue = 1; function fixtureRead(){ return fixtureValue; }\n", encoding="utf-8")
        atlas = root / ATLAS
        atlas.parent.mkdir(parents=True)
        skill = root / SKILL
        skill.mkdir(parents=True)
        (skill / "SKILL.md").write_text("Synthetic procedure\n", encoding="utf-8")
        for name in LINKS:
            link = root / name
            link.parent.mkdir(parents=True)
            link.symlink_to("../../skills/jpw-feature-atlas", target_is_directory=True)
        base = [{"feature_id": "SYNTHETIC-" + str(i), "name": "Synthetic",
                 "implementation": "available", "evidence_level": "code-inspected",
                 "freshness": "verified-for-revision", "revision": "a" * 40,
                 "sources": [{"path": "source.js", "sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
                              "symbols": ["fixtureValue", "fixtureRead"]}],
                 "relations": [{"origin": "source.js#fixtureRead", "type": "LE", "target": "source.js#fixtureValue",
                                "condition": "Synthetic read", "evidence": "source.js#fixtureRead"}]} for i in range(3)]

        def write(records):
            atlas.write_text("\n\n".join("```atlas-json\n" + json.dumps(r) + "\n```" for r in records), encoding="utf-8")

        def run(name, records, expected=None, prepare=None, malformed=False):
            write(records)
            undo = prepare() if prepare else None
            if malformed:
                atlas.write_text("```atlas-json\n{bad}\n```\n", encoding="utf-8")
            before = snapshot(root)
            result = validate(root, revision_check=lambda value: value == "a" * 40)
            unchanged = snapshot(root) == before
            codes = [e["code"] for e in result["errors"]]
            good = unchanged and (expected in codes if expected else result["result"] == "PASS")
            cases.append({"case": name, "result": "PASS" if good else "TEST_HARNESS_FAIL",
                          "expected_diagnostic": expected, "observed_diagnostics": codes,
                          "fixture_unchanged_during_validation": unchanged})
            if undo:
                undo()

        run("valid fixture and structural read does not write", base)
        changes = (
            ("source hash drift", "SOURCE_HASH_DRIFT", lambda r: r[0]["sources"][0].update(sha256="0" * 64)),
            ("missing symbol", "SYMBOL_MISSING", lambda r: r[0]["sources"][0]["symbols"].append("missingSymbol")),
            ("orphan relation", "RELATION_ORPHAN", lambda r: r[0]["relations"][0].update(target="source.js#missingSymbol")),
            ("duplicate ID", "DUPLICATE_ID", lambda r: r[1].update(feature_id=r[0]["feature_id"])),
            ("external path", "SOURCE_PATH", lambda r: r[0]["sources"][0].update(path="../outside.js")),
            ("invalid dimension", "DIMENSION", lambda r: r[0].update(implementation="invented")),
            ("invalid relation type", "RELATION_TYPE", lambda r: r[0]["relations"][0].update(type="invented")),
        )
        for name, expected, change in changes:
            records = copy.deepcopy(base)
            change(records)
            run(name, records, expected)
        outside = root.parent / "outside.js"
        outside.write_text(source.read_text(), encoding="utf-8")

        def external_source():
            original = source.read_bytes()
            source.unlink()
            source.symlink_to(outside)
            def undo():
                source.unlink()
                source.write_bytes(original)
            return undo

        run("external source symlink", base, "SOURCE_PATH", external_source)

        def external_link():
            link = root / LINKS[0]
            link.unlink()
            link.symlink_to(root.parent, target_is_directory=True)
            def undo():
                link.unlink()
                link.symlink_to("../../skills/jpw-feature-atlas", target_is_directory=True)
            return undo

        run("external native symlink", base, "NATIVE_LINK", external_link)
        run("malformed payload", base, "PAYLOAD", malformed=True)
    return {"result": "PASS" if all(c["result"] == "PASS" for c in cases) else "TEST_HARNESS_FAIL",
            "cases": cases, "effects": {"writes": "Only self-owned temporary synthetic fixtures, removed at exit; no Git commit or model session."}}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    try:
        report = {"schema": "jpw/feature-atlas-structure/v1", "root": str(args.root.resolve()),
                  "limit": LIMIT, "validation": validate(args.root)}
        if args.self_test:
            report["self_test"] = self_test()
        report["result"] = "PASS" if report["validation"]["result"] == "PASS" and report.get("self_test", {"result": "PASS"})["result"] == "PASS" else "PRODUCT_FAIL" if report["validation"]["result"] != "PASS" else "TEST_HARNESS_FAIL"
    except (OSError, ValueError, RuntimeError) as exc:
        report = {"result": "ENVIRONMENT_ERROR", "detail": str(exc), "limit": LIMIT}
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["result"] == "PASS" else 2 if report["result"] == "ENVIRONMENT_ERROR" else 1


if __name__ == "__main__":
    raise SystemExit(main())
