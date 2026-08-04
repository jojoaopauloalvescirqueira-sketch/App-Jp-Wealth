#!/usr/bin/env python3
from pathlib import Path
import json
import re

ROOT = Path(__file__).resolve().parents[1]
index = (ROOT / 'index.html').read_text(encoding='utf-8')
css = (ROOT / 'src/styles/app.css').read_text(encoding='utf-8').rstrip()
manifest = json.loads((ROOT / 'src/js/manifest.json').read_text(encoding='utf-8'))
js = '\n'.join((ROOT / item['path']).read_text(encoding='utf-8').rstrip() for item in manifest['files'])

html = re.sub(r'<link rel="stylesheet" href="src/styles/app\.css">', '<style>\n' + css + '\n</style>', index, count=1)
for item in manifest['files']:
    tag = f'<script src="{item["path"]}"></script>'
    html = html.replace(tag, '', 1)
html = html.replace('\n</body>', '<script>\n' + js + '\n</script>\n</body>', 1)

out = ROOT / 'dist/JP_Wealth_Risk_Terminal_V9.1_PORTABLE.html'
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(html, encoding='utf-8')
print(out)
