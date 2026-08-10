#!/usr/bin/env python3
from pathlib import Path
import hashlib
import json
import re

ROOT = Path(__file__).resolve().parents[1]
manifest = json.loads((ROOT / 'src/js/manifest.json').read_text(encoding='utf-8'))
build_id_path = ROOT / 'build-id.js'

# JPW-BUILD-DSSTORE — inputs OFICIAIS do fingerprint, declarados um a um.
#
# A versão anterior varria diretórios por glob (`manifests/*.webmanifest` e
# `icons/**`). O glob de `icons/` era código morto desde a migração dos ícones para
# `assets/` — nenhum arquivo ali é rastreado —, mas continuava lendo o que houvesse
# no disco. Bastava um `icons/.DS_Store` do Finder, invisível ao `git status` por
# casar com o .gitignore, para o mesmo commit produzir dois Build IDs diferentes.
#
# A regra agora é: o fingerprint depende SÓ desta lista mais os scripts declarados em
# src/js/manifest.json. Nada de varredura de diretório — é o glob que deixa lixo
# entrar. Input declarado e ausente é ERRO, nunca omissão silenciosa: sem isso, um
# arquivo removido mudaria o identificador sem ninguém perceber.
FINGERPRINT_FIXED_INPUTS = ('index.html', 'src/styles/app.css', 'src/js/manifest.json', 'sw.js')
FINGERPRINT_TAIL_INPUTS = ('manifests/jp-wealth.webmanifest',)

def build_id():
    files = [ROOT / rel for rel in FINGERPRINT_FIXED_INPUTS]
    files.extend(ROOT / item['path'] for item in manifest['files'])
    files.extend(ROOT / rel for rel in FINGERPRINT_TAIL_INPUTS)
    digest = hashlib.sha256()
    for path in files:
        relative = path.relative_to(ROOT).as_posix()
        if not path.is_file():
            raise SystemExit(f'ERRO: input oficial do build ausente: {relative}')
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
portable_bootstrap = build_id_source + "window.JP_WEALTH_PORTABLE_BUILD = true;\n"
html = html.replace('<script src="build-id.js"></script>', '<script>\n' + portable_bootstrap + '</script>', 1)
for item in manifest['files']:
    tag = f'<script src="{item["path"]}"></script>'
    html = html.replace(tag, '', 1)
html = html.replace('\n</body>', '<script>\n' + js + '\n</script>\n</body>', 1)

out = ROOT / 'dist/JP_Wealth_Risk_Terminal_V9.1_PORTABLE.html'
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(html, encoding='utf-8')
print(out)
