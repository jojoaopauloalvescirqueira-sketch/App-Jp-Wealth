#!/usr/bin/env python3
"""Rasterize the approved vector signature; do not redraw the JP Wealth mark.

Requires the existing Playwright/Chromium QA runtime. No network is used.
SVGs are the editable source; BMPs use the MT5 header background at each DPI.
"""
from pathlib import Path
import base64
import hashlib
import json
import struct
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / 'assets/stoikus'
IMAGES = ROOT / 'mt5/jpw-alavancagem-atual/MQL5/Images/JPWealth'


def bmp24(width, height, rgba):
    stride = (width * 3 + 3) & ~3
    pixels = bytearray()
    for y in reversed(range(height)):
        row = bytearray()
        for x in range(width):
            i = (y * width + x) * 4
            row.extend((rgba[i + 2], rgba[i + 1], rgba[i]))
        row.extend(bytes(stride - len(row)))
        pixels.extend(row)
    return (b'BM' + struct.pack('<IHHI', 54 + len(pixels), 0, 0, 54)
            + struct.pack('<IiiHHIIiiII', 40, width, height, 1, 24, 0, len(pixels), 3780, 3780, 0, 0)
            + pixels)


def main():
    records = []
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        for theme, name, background in [('clara', 'Light', '#e9eef4'), ('escura', 'Dark', '#272d36')]:
            source = ASSETS / ('stoikus-assinatura-' + theme + '.svg')
            uri = 'data:image/svg+xml;base64,' + base64.b64encode(source.read_bytes()).decode()
            for dpi in (100, 125, 150, 200):
                width, height = 240 * dpi // 100, 28 * dpi // 100
                rendered = page.evaluate('''async ({uri,width,height,background}) => {
                  const im=new Image(); im.src=uri; await im.decode();
                  const c=document.createElement('canvas'); c.width=width; c.height=height;
                  const g=c.getContext('2d'); g.fillStyle=background; g.fillRect(0,0,width,height);
                  g.drawImage(im,0,0,width,height);
                  const rgba=Array.from(g.getImageData(0,0,width,height).data);
                  g.clearRect(0,0,width,height); g.drawImage(im,0,0,width,height);
                  return {rgba,png:c.toDataURL('image/png').split(',')[1]};
                }''', dict(uri=uri, width=width, height=height, background=background))
                bmp = IMAGES / ('JPW_Stoikus_Logo_' + name + '_' + str(dpi) + '.bmp')
                bmp.write_bytes(bmp24(width, height, rendered['rgba']))
                png = ASSETS / ('stoikus-assinatura-' + theme + '-' + str(dpi) + '.png')
                png.write_bytes(base64.b64decode(rendered['png']))
                records.append(dict(bmp=str(bmp.relative_to(ROOT)), png=str(png.relative_to(ROOT)),
                                    dpi=dpi, width=width, height=height,
                                    bmp_sha256=hashlib.sha256(bmp.read_bytes()).hexdigest(),
                                    png_sha256=hashlib.sha256(png.read_bytes()).hexdigest()))
        browser.close()
    (ASSETS / 'raster-provenance.json').write_text(json.dumps(dict(
        source_logo_sha256=hashlib.sha256((ROOT/'assets/jp-wealth-brand-red.png').read_bytes()).hexdigest(),
        logical_size=[240,28], native_mt5='NOT_RUN', records=records), indent=2)+'\n')
    print('Generated 8 BMP and 8 transparent PNG assets from approved SVGs.')


if __name__ == '__main__':
    main()
