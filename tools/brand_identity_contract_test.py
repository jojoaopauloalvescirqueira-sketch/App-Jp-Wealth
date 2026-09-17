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
    """Decode RGB/RGBA 8-bit PNGs as RGBA without depending on Pillow in CI."""
    raw = path.read_bytes()
    require(raw.startswith(b"\x89PNG\r\n\x1a\n"), f"PNG invalido: {path.name}")
    position = 8
    width = height = channels = 0
    compressed = bytearray()
    while position < len(raw):
        length = struct.unpack(">I", raw[position:position + 4])[0]
        kind = raw[position + 4:position + 8]
        payload = raw[position + 8:position + 8 + length]
        position += length + 12
        if kind == b"IHDR":
            width, height, depth, color_type, compression, filtering, interlace = struct.unpack(">IIBBBBB", payload)
            require((depth, compression, filtering, interlace) == (8, 0, 0, 0) and color_type in (2, 6), f"PNG deve ser RGB ou RGBA 8-bit: {path.name}")
            channels = 3 if color_type == 2 else 4
        elif kind == b"tRNS":
            raise AssertionError(f"transparencia por chave de cor nao permitida: {path.name}")
        elif kind == b"IDAT":
            compressed.extend(payload)
        elif kind == b"IEND":
            break
    require(width > 0 and height > 0 and channels in (3, 4), f"cabecalho PNG ausente: {path.name}")
    scanlines = zlib.decompress(bytes(compressed))
    stride = width * channels
    require(len(scanlines) == height * (stride + 1), f"dados PNG inesperados: {path.name}")
    decoded = bytearray(height * stride)
    previous = bytearray(stride)
    for row in range(height):
        offset = row * (stride + 1)
        filter_type = scanlines[offset]
        source = scanlines[offset + 1:offset + 1 + stride]
        target = bytearray(stride)
        for index, value in enumerate(source):
            left = target[index - channels] if index >= channels else 0
            above = previous[index]
            upper_left = previous[index - channels] if index >= channels else 0
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
    if channels == 3:
        rgba = bytearray(width * height * 4)
        rgba[0::4] = decoded[0::3]
        rgba[1::4] = decoded[1::3]
        rgba[2::4] = decoded[2::3]
        rgba[3::4] = b"\xff" * (width * height)
        return width, height, bytes(rgba)
    return width, height, bytes(decoded)


def require_solid_icon(path: Path, expected_size: int, variant: str) -> None:
    width, height, pixels = read_rgba_png(path)
    require((width, height) == (expected_size, expected_size), f"dimensao incorreta: {path.name}")
    require(variant in ("primary", "secondary"), f"variante desconhecida: {variant}")
    require(pixels[3::4] == b"\xff" * (width * height), f"todos os pixels devem ser opacos: {path.name}")
    # A faixa inteira precisa chegar ao limite da imagem na cor da marca.
    # O sistema operacional aplica sua propria mascara; o arquivo nao a embute.
    border = (expected_size * 2 + 99) // 100
    left, top, right, bottom = width, height, 0, 0
    invalid_border = 0
    for offset in range(0, len(pixels), 4):
        red, green, blue = pixels[offset:offset + 3]
        position = offset // 4
        x, y = position % width, position // width
        if x < border or x >= width - border or y < border or y >= height - border:
            solid = red >= 180 and green <= 40 and blue <= 40 if variant == "primary" else max(red, green, blue) <= 12
            if not solid:
                invalid_border += 1
        # A tolerancia conserva antialias e pequenas variacoes do branco.
        if min(red, green, blue) >= 220:
            left, top = min(left, x), min(top, y)
            right, bottom = max(right, x + 1), max(bottom, y + 1)
    require(invalid_border == 0, f"borda deve ter fundo solido da marca: {path.name}")
    require(right > left and bottom > top, f"letras brancas ausentes: {path.name}")
    require(0.82 <= (right - left) / width <= 0.93, f"largura das letras deve ficar entre 82% e 93%: {path.name}")
    require(0.35 <= (bottom - top) / height <= 0.43, f"altura das letras deve ficar entre 35% e 43%: {path.name}")
    require(min(left, width - right) >= width * 0.03 and min(top, height - bottom) >= height * 0.03,
            f"letras devem preservar margem minima de 3%: {path.name}")
    require(abs((left + right) / 2 - width / 2) <= width * 0.02 and
            abs((top + bottom) / 2 - height / 2) <= height * 0.02,
            f"letras devem permanecer centralizadas: {path.name}")


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
        require_solid_icon(ROOT / f"assets/pwa-icon-{variant}.png", 1254, variant)
        require_solid_icon(ROOT / f"assets/pwa-icon-{variant}-192.png", 192, variant)
        require_solid_icon(ROOT / f"assets/pwa-icon-{variant}-512.png", 512, variant)
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
