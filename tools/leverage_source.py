"""Load the actual JPWealth include graph for source/extraction tests.

No fallback copies of extracted functions are kept by the host tests. Only
owned local includes are expanded; foreign/system includes are left intact.
"""

from pathlib import Path
import re


def expanded_source(entry: Path) -> str:
    mql = next(parent for parent in entry.parents if parent.name == "MQL5")
    include_root = (mql / "Include" / "JPWealth").resolve()
    visited: set[Path] = set()

    def read(path: Path) -> str:
        resolved = path.resolve()
        if resolved in visited:
            return ""
        visited.add(resolved)
        source = path.read_text(encoding="utf-8")

        def include(match: re.Match[str]) -> str:
            target = (include_root / match.group(1)).resolve()
            if target.parent != include_root or not target.is_file():
                raise ValueError(f"Invalid or missing JPWealth include: {target.name}")
            return read(target)

        return re.sub(r"^\s*#include\s*[<\"]JPWealth/([^>\"\n]+)[>\"]\s*(?://[^\n]*)?$",
                      include, source, flags=re.MULTILINE)

    return read(entry)
