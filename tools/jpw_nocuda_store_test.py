#!/usr/bin/env python3
"""Exercise the SQLite statements shipped in JPW_NoCuda_Store.mqh.

This checks the actual DDL and compare-and-swap SQL against SQLite. It cannot
execute MQL5 or prove MT5's Database* bindings; native tests cover that boundary.
"""

from __future__ import annotations

import ast
import re
import sqlite3
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "mt5/jpw-alavancagem-atual/MQL5/Include/JPWealth/JPW_NoCuda_Store.mqh"


def statements(text: str, function: str) -> list[str]:
    expression = re.compile(
        rf"{function}\(db,\s*((?:\"(?:[^\"\\]|\\.)*\"\s*)+)\)"
    )
    return [
        "".join(ast.literal_eval(literal) for literal in re.findall(r'"(?:[^"\\]|\\.)*"', match.group(1)))
        for match in expression.finditer(text)
    ]


def check(condition: bool, label: str) -> None:
    if not condition:
        raise AssertionError(label)


def main() -> None:
    source = SOURCE.read_text(encoding="utf-8")
    open_source = source.split("JPWNoCudaStoreOpen(", 1)[1].split(
        "JPWNoCudaStoreReadRevisionInDb(", 1
    )[0]
    check("const bool existed=FileIsExist(path);" in open_source,
          "file existence must be captured before DatabaseOpen(CREATE)")
    check(re.search(r"if\(tested\s*&&\s*empty\s*&&\s*write\s*&&\s*!existed\)", open_source)
          is not None, "an existing empty database must never be initialized")
    with tempfile.TemporaryDirectory(prefix="jpw-nocuda-store-synthetic-") as tmp:
        existing = Path(tmp) / "truncated.sqlite"
        existing.write_bytes(b"")
        existed = existing.exists()
        db = sqlite3.connect(existing)
        empty = db.execute("SELECT COUNT(*) FROM sqlite_master").fetchone()[0] == 0
        db.close()
        check(existed and empty and not (empty and True and not existed),
              "preexisting zero-byte file must take CORRUPT path")
        check(existing.read_bytes() == b"", "corrupt bytes must remain unchanged")
        fresh = Path(tmp) / "new.sqlite"
        existed = fresh.exists()
        db = sqlite3.connect(fresh)
        empty = db.execute("SELECT COUNT(*) FROM sqlite_master").fetchone()[0] == 0
        db.close()
        check(not existed and empty and (empty and True and not existed),
              "genuinely absent file may initialize")

    ddl = [sql for sql in statements(source, "DatabaseExecute") if sql.startswith("CREATE ")]
    check(len(ddl) == 5, "expected three tables and two immutable-revision triggers")
    connection = sqlite3.connect(":memory:", isolation_level=None)
    for sql in ddl:
        connection.execute(sql)
    tables = {row[0] for row in connection.execute("SELECT name FROM sqlite_master WHERE type='table'")}
    check({"nocuda_meta", "nocuda_heads", "nocuda_revisions"} <= tables, "missing store table")
    record_type = source.split("struct JPWNoCudaRecord", 1)[1].split("};", 1)[0]
    record_fields = re.findall(r"\b(?:int|long|double|string)\s+(\w+)\s*;", record_type)
    db_fields = [row[1] for row in connection.execute("PRAGMA table_info(nocuda_revisions)")]
    check(db_fields == record_fields, "MQL record and SQLite column order drift")

    revision_reader = source.split("JPWNoCudaStoreReadRevisionInDb(", 1)[1]
    select_revision = next(sql for sql in statements(revision_reader, "DatabasePrepare")
                           if sql.startswith("SELECT store_key,study_id,revision"))
    read_fields = [part.strip() for part in
                   select_revision.split("FROM nocuda_revisions", 1)[0].removeprefix("SELECT ").split(",")]
    check(read_fields == record_fields, "DatabaseReadBind SELECT order drift")

    prepared = statements(source, "DatabasePrepare")
    insert_revision = next(sql for sql in prepared if sql.startswith("INSERT INTO nocuda_revisions VALUES"))
    insert_head = next(sql for sql in prepared if sql.startswith("INSERT INTO nocuda_heads VALUES"))
    update_head = next(sql for sql in prepared if sql.startswith("UPDATE nocuda_heads SET generation"))
    list_studies = next(sql for sql in prepared if sql.startswith("SELECT h.study_id FROM nocuda_heads h"))
    check(insert_revision.count("?") == 27, "record bind count drift")
    check(insert_head.count("?") == 7, "head bind count drift")
    check("WHERE study_id=?4 AND generation=?5 AND checksum=?6" in update_head,
          "head update must compare generation and checksum")

    # Use the production column order; the values are synthetic study data.
    values = (
        "a" * 64, "b" * 64, 1, 0, "NZDUSD.synthetic", "SYNTHETIC.FEED", 16385,
        "AB0_C1_BARS_V1", 1_700_000_000, 1_700_014_400, 5, "c" * 64,
        1_700_000_000, 1_700_003_600, 0, 1.1000,
        1_700_014_400, 1_700_018_000, 4, 1.1020,
        1_700_007_200, 1_700_010_800, 2, 1.1050,
        1_700_020_000, "Synthetic", "d" * 64,
    )
    connection.execute(insert_revision, values)
    connection.execute(insert_head, (values[1], values[4], values[5], values[6], 1, 1, values[-1]))
    revised = list(values)
    revised[2] = 2
    revised[3] = 1
    revised[23] = 1.1060
    revised[-1] = "e" * 64
    connection.execute("BEGIN")
    connection.execute(insert_revision, revised)
    updated = connection.execute(update_head, (2, 2, revised[-1], values[1], 1, values[-1]))
    check(updated.rowcount == 1, "fresh writer must advance one generation")
    connection.execute("COMMIT")
    check([row[0] for row in connection.execute(list_studies, ("NZDUSD.synthetic", 0))] ==
          [values[1]], "exact symbol should list its study")
    check(not list(connection.execute(list_studies, ("EURUSD.synthetic", 0))),
          "another symbol must not list the study")
    stale = connection.execute(update_head, (3, 3, "f" * 64, values[1], 1, values[-1]))
    check(stale.rowcount == 0, "stale writer cannot advance generation")
    check(connection.execute("SELECT COUNT(*) FROM nocuda_revisions").fetchone()[0] == 2,
          "two immutable versions should survive")
    for statement in (
        "UPDATE nocuda_revisions SET c_close=0 WHERE revision=1",
        "DELETE FROM nocuda_revisions WHERE revision=1",
    ):
        try:
            connection.execute(statement)
        except sqlite3.IntegrityError:
            pass
        else:
            raise AssertionError("confirmed revisions must be immutable")
    connection.close()
    print("JPW NoCuda store SQL PASS: fail-closed existing file, schema, bind count, CAS, immutable versions")


if __name__ == "__main__":
    main()
