#!/usr/bin/env python3
"""Teste dedicado do frescor material do preflight (tooling, sem navegador).

Cada cenario roda em repositorio Git sintetico e descartavel; o script real
`tools/agent_preflight.py` e copiado para dentro dele, de modo que ROOT
resolva para o repo sintetico. Asserta-se apenas sobre os facts/warnings de
source revision — errors de contexto minimo sao esperados e ignorados
(o payload JSON e sempre impresso, mesmo com resultado BLOCKED).

Regra institucional sob teste: TRUE / FALSE / UNKNOWN sao distintos e,
especialmente, UNKNOWN != FALSE.
"""
from pathlib import Path
import json
import shutil
import subprocess
import sys
import tempfile

REAL_PREFLIGHT = Path(__file__).resolve().parent / "agent_preflight.py"
CTX = ("docs/governance/CURRENT-STATE.md", "docs/work/ACTIVE-TASK.md", "SESSION_HANDOFF.md")


def sh(repo: Path, *args: str) -> str:
    r = subprocess.run(list(args), cwd=repo, text=True, capture_output=True)
    assert r.returncode == 0, f"{args}: {r.stderr or r.stdout}"
    return r.stdout.strip()


def novo_repo(tmp: str) -> Path:
    repo = Path(tmp) / "repo"
    (repo / "tools").mkdir(parents=True)
    for rel in CTX:
        p = repo / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text("# stub\n", encoding="utf-8")
    shutil.copy(REAL_PREFLIGHT, repo / "tools/agent_preflight.py")
    sh(repo, "git", "init", "-q")
    sh(repo, "git", "config", "user.email", "t@t")
    sh(repo, "git", "config", "user.name", "t")
    sh(repo, "git", "add", "-A")
    sh(repo, "git", "commit", "-qm", "base")
    return repo


def declara(repo: Path, valor: str) -> None:
    (repo / CTX[0]).write_text(
        f"# Estado\nData da fotografia: 2026-08-10\nSource revision representada: {valor}\n",
        encoding="utf-8",
    )


def preflight(repo: Path) -> dict:
    r = subprocess.run(
        [sys.executable, "tools/agent_preflight.py", "--mode", "audit", "--allow-dirty", "--json"],
        cwd=repo, text=True, capture_output=True,
    )
    return json.loads(r.stdout)


def frescor(payload: dict):
    f = payload["facts"]
    return f["source_revision_status"], f["potential_material_changes_since_source_revision"], payload["warnings"]


def warn_material(ws) -> bool:
    return any("POTENTIAL MATERIAL CHANGE" in w for w in ws)


def warn_unknown(ws) -> bool:
    return any("SOURCE REVISION UNKNOWN" in w for w in ws)


def caso1_head_igual_source(repo: Path) -> None:
    declara(repo, "placeholder")
    sh(repo, "git", "add", "-A")
    sh(repo, "git", "commit", "-qm", "ctx")
    declara(repo, f"`{sh(repo, 'git', 'rev-parse', 'HEAD')}`")  # source == HEAD atual
    s, pot, ws = frescor(preflight(repo))
    assert (s, pot) == ("valid", False) and not warn_material(ws), (s, pot, ws)


def caso2_context_only(repo: Path) -> None:
    a = sh(repo, "git", "rev-parse", "HEAD")
    declara(repo, f"`{a}`")
    (repo / CTX[1]).write_text("# tarefa nova\n", encoding="utf-8")
    (repo / CTX[2]).write_text("# handoff novo\n", encoding="utf-8")
    sh(repo, "git", "add", "-A")
    sh(repo, "git", "commit", "-qm", "reconciliacao contextual")
    s, pot, ws = frescor(preflight(repo))  # HEAD != source, so os 3 paths de contexto
    assert a != sh(repo, "git", "rev-parse", "HEAD")
    assert (s, pot) == ("valid", False) and not warn_material(ws), (s, pot, ws)


def caso3_fora_da_allowlist(repo: Path) -> None:
    a = sh(repo, "git", "rev-parse", "HEAD")
    declara(repo, f"`{a}`")
    (repo / "src_sintetico.js").write_text("// mudanca\n", encoding="utf-8")
    sh(repo, "git", "add", "-A")
    sh(repo, "git", "commit", "-qm", "mudanca potencialmente material")
    s, pot, ws = frescor(preflight(repo))
    assert (s, pot) == ("valid", True) and warn_material(ws), (s, pot, ws)


def caso4a_campo_ausente(repo: Path) -> None:
    (repo / CTX[0]).write_text("# Estado sem source revision\n", encoding="utf-8")
    s, pot, ws = frescor(preflight(repo))
    assert (s, pot) == ("missing", None) and warn_unknown(ws) and not warn_material(ws), (s, pot, ws)


def caso4b_malformado(repo: Path) -> None:
    declara(repo, "`nao-e-um-sha`")
    s, pot, ws = frescor(preflight(repo))
    assert (s, pot) == ("malformed", None) and warn_unknown(ws), (s, pot, ws)


def caso4c_sha_inexistente(repo: Path) -> None:
    declara(repo, "`deadbeefdeadbeefdeadbeefdeadbeefdeadbeef`")
    s, pot, ws = frescor(preflight(repo))
    assert (s, pot) == ("unknown-sha", None) and warn_unknown(ws), (s, pot, ws)


def caso5_nao_ancestral(repo: Path) -> None:
    sh(repo, "git", "checkout", "-qb", "lateral")
    (repo / "lateral.txt").write_text("x\n", encoding="utf-8")
    sh(repo, "git", "add", "-A")
    sh(repo, "git", "commit", "-qm", "lateral")
    lateral = sh(repo, "git", "rev-parse", "HEAD")
    sh(repo, "git", "checkout", "-q", "-")  # volta; lateral nao e ancestral do HEAD original
    declara(repo, f"`{lateral}`")
    s, pot, ws = frescor(preflight(repo))
    assert (s, pot) == ("not-ancestor", None) and warn_unknown(ws), (s, pot, ws)


CASOS = [
    caso1_head_igual_source,
    caso2_context_only,
    caso3_fora_da_allowlist,
    caso4a_campo_ausente,
    caso4b_malformado,
    caso4c_sha_inexistente,
    caso5_nao_ancestral,
]
# CASO 6 (falha de git/diff) nao e simulavel sem monkeypatch artificial desproporcional
# para um ramo defensivo simples: diff-error defensive path NOT DIRECTLY TESTED.


def main() -> int:
    for caso in CASOS:
        with tempfile.TemporaryDirectory() as tmp:
            caso(novo_repo(tmp))
            print(f"[PASS] {caso.__name__}")
    print(
        "PREFLIGHT CONTEXT OK — TRUE/FALSE/UNKNOWN distintos; UNKNOWN != FALSE; "
        "reconciliacao contextual (context-only) nao dispara falso positivo."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
