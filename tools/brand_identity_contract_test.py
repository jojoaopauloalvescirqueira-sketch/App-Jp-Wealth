#!/usr/bin/env python3
"""Static contract for the coordinated JP Wealth brand and PWA variants."""
from __future__ import annotations

import json
from pathlib import Path
import struct
import zlib

ROOT = Path(__file__).resolve().parents[1]


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def read_rgba_png(path: Path) -> tuple[int, int, bytes]:
    """Decode the alpha contract without depending on Pillow in CI."""
    raw = path.read_bytes()
    require(raw.startswith(b"\x89PNG\r\n\x1a\n"), f"PNG invalido: {path.name}")
    position = 8
    width = height = 0
    compressed = bytearray()
    while position < len(raw):
        length = struct.unpack(">I", raw[position:position + 4])[0]
        kind = raw[position + 4:position + 8]
        payload = raw[position + 8:position + 8 + length]
        position += length + 12
        if kind == b"IHDR":
            width, height, depth, color_type, compression, filtering, interlace = struct.unpack(">IIBBBBB", payload)
            require((depth, color_type, compression, filtering, interlace) == (8, 6, 0, 0, 0), f"PNG deve ser RGBA 8-bit: {path.name}")
        elif kind == b"IDAT":
            compressed.extend(payload)
        elif kind == b"IEND":
            break
    scanlines = zlib.decompress(bytes(compressed))
    stride = width * 4
    require(len(scanlines) == height * (stride + 1), f"dados PNG inesperados: {path.name}")
    decoded = bytearray(height * stride)
    previous = bytearray(stride)
    for row in range(height):
        offset = row * (stride + 1)
        filter_type = scanlines[offset]
        source = scanlines[offset + 1:offset + 1 + stride]
        target = bytearray(stride)
        for index, value in enumerate(source):
            left = target[index - 4] if index >= 4 else 0
            above = previous[index]
            upper_left = previous[index - 4] if index >= 4 else 0
            if filter_type == 0:
                predictor = 0
            elif filter_type == 1:
                predictor = left
            elif filter_type == 2:
                predictor = above
            elif filter_type == 3:
                predictor = (left + above) // 2
            elif filter_type == 4:
                estimate = left + above - upper_left
                distances = (abs(estimate - left), abs(estimate - above), abs(estimate - upper_left))
                predictor = (left, above, upper_left)[distances.index(min(distances))]
            else:
                raise AssertionError(f"filtro PNG inesperado: {path.name}")
            target[index] = (value + predictor) & 255
        decoded[row * stride:(row + 1) * stride] = target
        previous = target
    return width, height, bytes(decoded)


def require_transparent_icon(path: Path, expected_size: int) -> None:
    width, height, pixels = read_rgba_png(path)
    require((width, height) == (expected_size, expected_size), f"dimensao incorreta: {path.name}")
    alpha = pixels[3::4]
    corners = (alpha[0], alpha[width - 1], alpha[(height - 1) * width], alpha[-1])
    require(corners == (0, 0, 0, 0), f"cantos devem ser transparentes: {path.name}")
    require(alpha[(height // 2) * width + width // 2] == 255, f"centro deve ser opaco: {path.name}")
    require(alpha.count(0) > width * height // 20, f"area transparente insuficiente: {path.name}")
    pale_partial = 0
    for offset in range(0, len(pixels), 4):
        red, green, blue, opacity = pixels[offset:offset + 4]
        if 0 < opacity < 255 and min(red, green, blue) > 220:
            pale_partial += 1
    require(pale_partial == 0, f"halo claro detectado na borda: {path.name}")


def main() -> None:
    index = (ROOT / "index.html").read_text(encoding="utf-8")
    app = (ROOT / "src/js/40-app/06-app-icons.js").read_text(encoding="utf-8")
    worker = (ROOT / "sw.js").read_text(encoding="utf-8")
    manifests = [
        ("manifests/jp-wealth.webmanifest", [("../assets/pwa-icon-primary-192.png", "192x192"), ("../assets/pwa-icon-primary-512.png", "512x512")]),
        ("manifests/jp-wealth-black.webmanifest", [("../assets/pwa-icon-secondary-192.png", "192x192"), ("../assets/pwa-icon-secondary-512.png", "512x512")]),
    ]
    identity = []
    for relative, expected_icons in manifests:
        path = ROOT / relative
        require(path.is_file(), f"manifest ausente: {relative}")
        data = json.loads(path.read_text(encoding="utf-8"))
        identity.append((data.get("id"), data.get("start_url"), data.get("scope")))
        icons = data.get("icons", [])
        require(len(icons) == 2, f"dois tamanhos de icone exigidos: {relative}")
        require([(icon.get("src"), icon.get("sizes")) for icon in icons] == expected_icons, f"icones incorretos: {relative}")
        require(all(icon.get("type") == "image/png" and icon.get("purpose") == "any" for icon in icons), f"contrato PNG/purpose incorreto: {relative}")
    require(len(set(identity)) == 1, "id/start_url/scope devem ser iguais entre variantes")
    for asset in ("assets/jp-wealth-brand-red.png", "assets/jp-wealth-brand-black.png", "assets/pwa-icon-primary.png", "assets/pwa-icon-secondary.png"):
        raw = (ROOT / asset).read_bytes()
        require(raw.startswith(b"\x89PNG\r\n\x1a\n"), f"PNG invalido: {asset}")
    for variant in ("primary", "secondary"):
        require_transparent_icon(ROOT / f"assets/pwa-icon-{variant}.png", 1254)
        require_transparent_icon(ROOT / f"assets/pwa-icon-{variant}-192.png", 192)
        require_transparent_icon(ROOT / f"assets/pwa-icon-{variant}-512.png", 512)
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
    for asset in ("assets/jp-wealth-brand-red.png", "assets/jp-wealth-brand-black.png", "assets/pwa-icon-primary.png", "assets/pwa-icon-primary-192.png", "assets/pwa-icon-primary-512.png", "assets/pwa-icon-secondary.png", "assets/pwa-icon-secondary-192.png", "assets/pwa-icon-secondary-512.png"):
        require(f"./{asset}" in worker, f"asset fora do precache: {asset}")
    print("BRAND_IDENTITY_CONTRACT PASS")


if __name__ == "__main__":
    main()
