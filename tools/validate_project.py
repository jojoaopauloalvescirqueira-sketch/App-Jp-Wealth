#!/usr/bin/env python3
"""Validate repository structure, classic-script syntax and portable build."""

from __future__ import annotations

from collections import Counter
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
ERRORS: list[str] = []
ENVIRONMENT_ERRORS: list[str] = []


class IdParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.ids: list[str] = []

    def handle_starttag(self, _tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.ids.extend(value for key, value in attrs if key == "id" and value)


def display_path(path: Path) -> str:
    try:
        return path.relative_to(ROOT).as_posix()
    except ValueError:
        return str(path)


def validate_javascript(paths: list[Path]) -> None:
    node = shutil.which("node")
    if node:
        for path in paths:
            completed = subprocess.run(
                [node, "--check", str(path)], capture_output=True, text=True, check=False
            )
            if completed.returncode:
                detail = completed.stderr.strip() or completed.stdout.strip()
                ERRORS.append(f"sintaxe JS: {display_path(path)}: {detail}")
        return

    try:
        from playwright.sync_api import Error as PlaywrightError, sync_playwright
    except ModuleNotFoundError:
        ENVIRONMENT_ERRORS.append(
            "nem Node.js nem Playwright estao disponiveis para validar sintaxe JavaScript"
        )
        return

    try:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True)
            page = browser.new_page()
            for path in paths:
                source = path.read_text(encoding="utf-8")
                result = page.evaluate(
                    """source => {
                      try { new Function(source); return null; }
                      catch (error) { return `${error.name}: ${error.message}`; }
                    }""",
                    source,
                )
                if result:
                    ERRORS.append(f"sintaxe JS: {display_path(path)}: {result}")
            browser.close()
    except PlaywrightError as exc:
        ENVIRONMENT_ERRORS.append(f"Chromium/Playwright indisponivel para sintaxe JS: {exc}")


required = (
    "index.html",
    "src/styles/app.css",
    "src/js/manifest.json",
    "AGENTS.md",
    "docs/normative/Estatuto_JP_WEALTH_UNIFICADO.pdf",
    "sw.js",
)
for relative in required:
    if not (ROOT / relative).exists():
        ERRORS.append(f"ausente: {relative}")

manifest_path = ROOT / "src/js/manifest.json"
index_path = ROOT / "index.html"
manifest = {"files": []}
index = ""
if manifest_path.is_file():
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        if not isinstance(manifest.get("files"), list):
            raise ValueError("a chave files deve ser uma lista")
    except (json.JSONDecodeError, OSError, ValueError) as exc:
        ERRORS.append(f"manifest JS invalido: {exc}")
        manifest = {"files": []}
if index_path.is_file():
    index = index_path.read_text(encoding="utf-8")

positions: list[int] = []
javascript_paths: list[Path] = []
for item in manifest["files"]:
    relative = item.get("path", "") if isinstance(item, dict) else ""
    if not relative:
        ERRORS.append("entrada do manifest sem path")
        continue
    tag = f'<script src="{relative}"></script>'
    position = index.find(tag)
    if position < 0:
        ERRORS.append(f"script nao referenciado: {relative}")
    else:
        positions.append(position)
    path = ROOT / relative
    if not path.is_file():
        ERRORS.append(f"arquivo JS ausente: {relative}")
        continue
    javascript_paths.append(path)
    actual = hashlib.sha256(path.read_bytes()).hexdigest()
    if actual != item.get("sha256"):
        ERRORS.append(f"hash divergente: {relative}")

if positions != sorted(positions):
    ERRORS.append("ordem dos scripts diverge do manifest")
validate_javascript(javascript_paths)

assets = manifest.get("runtimeAssets", [])
expected = {"src/vendor/pdfjs/pdf.mjs": "module", "src/vendor/pdfjs/pdf.worker.mjs": "worker",
            "src/vendor/pdfjs/LICENSE.txt": "metadata", "src/vendor/pdfjs/PROVENANCE.json": "metadata"}
if not isinstance(assets, list):
    ERRORS.append("runtimeAssets deve ser lista")
    assets = []
paths = [item.get("path") for item in assets if isinstance(item, dict)]
required = any(item.get("path") == "src/js/40-app/25-fx-consolidated-pdf.js" for item in manifest.get("files", []))
if (required or assets) and (len(paths) != len(expected) or set(paths) != set(expected)):
    ERRORS.append("recursos PDF incompletos, duplicados ou inesperados")
for item in assets:
    if not isinstance(item, dict) or item.get("path") not in expected:
        ERRORS.append("recurso PDF nao permitido")
        continue
    relative = item["path"]
    resource = ROOT / relative
    if item.get("type") != expected[relative] or resource.is_symlink() or not resource.is_file() or resource.resolve() != ROOT.resolve() / relative:
        ERRORS.append(f"recurso PDF invalido ou fora da raiz: {relative}")
        continue
    if hashlib.sha256(resource.read_bytes()).hexdigest() != item.get("sha256"):
        ERRORS.append(f"hash de recurso PDF divergente: {relative}")
    if any(script.get("path") == relative for script in manifest.get("files", [])):
        ERRORS.append(f"ESM/worker nao pode ser script classico: {relative}")

joined_javascript = "".join(path.read_text(encoding="utf-8") for path in javascript_paths)
if "jpwealth_v9_state" not in joined_javascript:
    ERRORS.append("chave de persistencia principal nao localizada")
if re.search(r'(?:src|href)="https?://', index, re.I):
    ERRORS.append("dependencia externa de CSS/JS encontrada no index")

PWA_MANIFESTS = {
    "primary": ("manifests/jp-wealth.webmanifest", [("assets/pwa-icon-primary-192.png", "192x192"), ("assets/pwa-icon-primary-512.png", "512x512")]),
    "secondary": ("manifests/jp-wealth-black.webmanifest", [("assets/pwa-icon-secondary-192.png", "192x192"), ("assets/pwa-icon-secondary-512.png", "512x512")]),
}
manifest_identities: list[tuple[str | None, str | None, str | None]] = []
for variant, (relative_manifest, expected_icons) in PWA_MANIFESTS.items():
    webmanifest_path = ROOT / relative_manifest
    if not webmanifest_path.is_file():
        ERRORS.append(f"manifest PWA ausente: {relative_manifest}")
        continue
    try:
        pwa = json.loads(webmanifest_path.read_text(encoding="utf-8"))
        manifest_identities.append((pwa.get("id"), pwa.get("start_url"), pwa.get("scope")))
        icons = pwa.get("icons", [])
        actual_icons = [(str(icon.get("src", "")).removeprefix("../"), icon.get("sizes")) for icon in icons]
        if actual_icons != expected_icons:
            ERRORS.append(f"manifesto PWA {variant} aponta para icones incorretos: {actual_icons}")
        for icon in icons:
            icon_path = (webmanifest_path.parent / icon.get("src", "")).resolve()
            if not icon_path.is_file():
                ERRORS.append(f"icone PWA ausente: {display_path(icon_path)}")
            if icon.get("purpose") != "any":
                ERRORS.append(f"purpose inesperado: {icon.get('src')}")
    except (json.JSONDecodeError, OSError, AttributeError) as exc:
        ERRORS.append(f"manifest PWA invalido ({relative_manifest}): {exc}")
if len(manifest_identities) == 2 and len(set(manifest_identities)) != 1:
    ERRORS.append("manifestos PWA divergem em id, start_url ou scope")

for relative in ("assets/pwa-icon-primary.png", "assets/pwa-icon-primary-192.png", "assets/pwa-icon-primary-512.png", "assets/pwa-icon-secondary.png", "assets/pwa-icon-secondary-192.png", "assets/pwa-icon-secondary-512.png"):
    if not (ROOT / relative).is_file():
        ERRORS.append(f"ativo PWA ausente: {relative}")

if '<link rel="manifest"' not in index or "src/js/40-app/06-app-icons.js" not in index:
    ERRORS.append("integracao PWA/icones ausente no index")
service_worker = (ROOT / "sw.js").read_text(encoding="utf-8") if (ROOT / "sw.js").is_file() else ""
for relative_manifest, _expected_icons in PWA_MANIFESTS.values():
    if f"./{relative_manifest}" not in service_worker:
        ERRORS.append(f"service worker nao precacheia: {relative_manifest}")
for item in manifest["files"]:
    relative = item.get("path", "") if isinstance(item, dict) else ""
    if relative and f"./{relative}" not in service_worker:
        ERRORS.append(f"service worker nao precacheia script do manifest: {relative}")
for item in assets:
    if isinstance(item, dict) and item.get("type") in ("module", "worker") and item.get("path") in expected:
        if f'./{item["path"]}' not in service_worker:
            ERRORS.append(f'service worker nao precacheia recurso PDF: {item["path"]}')
for relative in ("assets/pwa-icon-primary.png", "assets/pwa-icon-primary-192.png", "assets/pwa-icon-primary-512.png", "assets/pwa-icon-secondary.png", "assets/pwa-icon-secondary-192.png", "assets/pwa-icon-secondary-512.png"):
    if f"./{relative}" not in service_worker:
        ERRORS.append(f"service worker nao precacheia: {relative}")

planck_path = ROOT / "src/vendor/planck/planck-1.5.0.min.js"
planck_sha256 = "69c6675a04121ec4042921b7d3d298058617d3211c243d8ea4d940a58af99974"
if not planck_path.is_file():
    ERRORS.append("dependencia vendorizada ausente: src/vendor/planck/planck-1.5.0.min.js")
elif hashlib.sha256(planck_path.read_bytes()).hexdigest() != planck_sha256:
    ERRORS.append("integridade divergente: Planck.js 1.5.0")
for relative in ("src/vendor/planck/LICENSE.txt", "src/vendor/planck/README.md"):
    if not (ROOT / relative).is_file():
        ERRORS.append(f"proveniencia/licenca ausente: {relative}")
galton_sources = [path for path in javascript_paths if "18-galton-board" in path.as_posix()]
math_random_call = re.compile(r"\bMath\s*\.\s*random\s*\(")
if any(math_random_call.search(path.read_text(encoding="utf-8")) for path in galton_sources):
    ERRORS.append("Galton Board usa Math.random; aleatoriedade deve passar pelo PRNG deterministico")

id_parser = IdParser()
id_parser.feed(index)
duplicates = sorted(value for value, count in Counter(id_parser.ids).items() if count > 1)
if duplicates:
    ERRORS.append("IDs estaticos duplicados: " + ", ".join(duplicates))

rebuild = subprocess.run(
    [sys.executable, str(ROOT / "tools/rebuild_monolith.py")],
    cwd=ROOT,
    capture_output=True,
    text=True,
    check=False,
)
if rebuild.returncode:
    ERRORS.append("rebuild portatil falhou: " + (rebuild.stderr.strip() or rebuild.stdout.strip()))
portable = ROOT / "dist/JP_Wealth_Risk_Terminal_V9.1_PORTABLE.html"
if not portable.is_file() or portable.stat().st_size < 500_000:
    ERRORS.append("rebuild portatil invalido")

if ERRORS:
    print("VALIDACAO FALHOU")
    for error in ERRORS:
        print("-", error)
    for error in ENVIRONMENT_ERRORS:
        print("- verificacao de ambiente adicional:", error)
    raise SystemExit(1)
if ENVIRONMENT_ERRORS:
    print("ENVIRONMENT_ERROR")
    for error in ENVIRONMENT_ERRORS:
        print("-", error)
    raise SystemExit(2)

print(
    f"VALIDACAO OK - {len(manifest['files'])} arquivos JS, "
    f"{len(id_parser.ids)} IDs estaticos, portatil reconstruido."
)
