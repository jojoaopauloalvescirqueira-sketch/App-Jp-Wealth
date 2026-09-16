#!/usr/bin/env python3
"""Static contract for the coordinated JP Wealth brand and PWA variants."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def main() -> None:
    index = (ROOT / "index.html").read_text(encoding="utf-8")
    app = (ROOT / "src/js/40-app/06-app-icons.js").read_text(encoding="utf-8")
    worker = (ROOT / "sw.js").read_text(encoding="utf-8")
    manifests = [
        ("manifests/jp-wealth.webmanifest", "../assets/pwa-icon-primary.png"),
        ("manifests/jp-wealth-black.webmanifest", "../assets/pwa-icon-secondary.png"),
    ]
    identity = []
    for relative, icon in manifests:
        path = ROOT / relative
        require(path.is_file(), f"manifest ausente: {relative}")
        data = json.loads(path.read_text(encoding="utf-8"))
        identity.append((data.get("id"), data.get("start_url"), data.get("scope")))
        require(len(data.get("icons", [])) == 1, f"icone unico exigido: {relative}")
        require(data["icons"][0].get("src") == icon, f"icone incorreto: {relative}")
    require(len(set(identity)) == 1, "id/start_url/scope devem ser iguais entre variantes")
    for asset in ("assets/jp-wealth-brand-red.png", "assets/jp-wealth-brand-black.png", "assets/pwa-icon-primary.png", "assets/pwa-icon-secondary.png"):
        raw = (ROOT / asset).read_bytes()
        require(raw.startswith(b"\x89PNG\r\n\x1a\n"), f"PNG invalido: {asset}")
    require('data-jp-brand-wordmark' in index and 'jp-wealth-brand-red.png' in index, "wordmark inicial vermelho ausente")
    require("primary:{ label:'Vermelho'" in app and "secondary:{ label:'Preto'" in app, "mapeamento primary/secondary incorreto")
    require("jpwealth_v9_icon_choice" in app, "chave auxiliar legado deve permanecer")
    require("manifestLink.href=withIconCacheBust(icon.manifest)" in app, "manifesto nao acompanha escolha")
    require("data-jp-brand-wordmark" in app and "document.documentElement.dataset.brandChoice=key" in app, "cabecalho nao acompanha escolha")
    require("window.location.reload" not in app, "aplicar marca nao pode recarregar")
    require("Aplicar marca" in app and "Cancelar" in app, "acoes explicitas ausentes")
    require("skipWaiting" not in worker, "politica conservadora do worker foi alterada")
    for relative, _icon in manifests:
        require(f"./{relative}" in worker, f"manifesto fora do precache: {relative}")
    for asset in ("assets/jp-wealth-brand-red.png", "assets/jp-wealth-brand-black.png", "assets/pwa-icon-primary.png", "assets/pwa-icon-secondary.png"):
        require(f"./{asset}" in worker, f"asset fora do precache: {asset}")
    print("BRAND_IDENTITY_CONTRACT PASS")


if __name__ == "__main__":
    main()
