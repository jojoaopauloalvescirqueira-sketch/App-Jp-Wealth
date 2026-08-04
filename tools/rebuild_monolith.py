#!/usr/bin/env python3
from pathlib import Path
import hashlib
import json
import re

ROOT = Path(__file__).resolve().parents[1]
manifest = json.loads((ROOT / 'src/js/manifest.json').read_text(encoding='utf-8'))
build_id_path = ROOT / 'build-id.js'

def build_id():
    files = [ROOT / 'index.html', ROOT / 'src/styles/app.css', ROOT / 'src/js/manifest.json', ROOT / 'sw.js']
    files.extend(ROOT / item['path'] for item in manifest['files'])
    files.extend(sorted((ROOT / 'manifests').glob('*.webmanifest')))
    files.extend(sorted((ROOT / 'icons').rglob('*')))
    digest = hashlib.sha256()
    for path in files:
        if not path.is_file(): continue
        relative = path.relative_to(ROOT).as_posix()
        content = path.read_bytes()
        if relative == 'index.html': content = content.replace(b'<script src="build-id.js"></script>', b'')
        digest.update(relative.encode('utf-8') + b'\0' + content + b'\0')
    return digest.hexdigest()[:16]

current_build_id = build_id()
build_id_source = f"// Gerado por tools/rebuild_monolith.py. Não editar manualmente.\nconst JP_WEALTH_BUILD_ID = '{current_build_id}';\n"
build_id_path.write_text(build_id_source, encoding='utf-8')

index = (ROOT / 'index.html').read_text(encoding='utf-8')
css = (ROOT / 'src/styles/app.css').read_text(encoding='utf-8').rstrip()
js = '\n'.join((ROOT / item['path']).read_text(encoding='utf-8').rstrip() for item in manifest['files'])

html = re.sub(r'<link rel="stylesheet" href="src/styles/app\.css">', '<style>\n' + css + '\n</style>', index, count=1)
html = html.replace('<script src="build-id.js"></script>', '<script>\n' + build_id_source + '</script>', 1)
for item in manifest['files']:
    tag = f'<script src="{item["path"]}"></script>'
    html = html.replace(tag, '', 1)
html = html.replace('\n</body>', '<script>\n' + js + '\n</script>\n</body>', 1)

out = ROOT / 'dist/JP_Wealth_Risk_Terminal_V9.1_PORTABLE.html'
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(html, encoding='utf-8')
print(out)
