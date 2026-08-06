#!/usr/bin/env python3
from pathlib import Path
from html.parser import HTMLParser
import hashlib
import json
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
errors = []
required = ['index.html','src/styles/app.css','src/js/manifest.json','AGENTS.md','docs/normative/Estatuto_JP_WEALTH_UNIFICADO.pdf','sw.js']
for rel in required:
    if not (ROOT/rel).exists(): errors.append(f'ausente: {rel}')

manifest = json.loads((ROOT/'src/js/manifest.json').read_text(encoding='utf-8'))
index = (ROOT/'index.html').read_text(encoding='utf-8')
expected_tags = [f'<script src="{x["path"]}"></script>' for x in manifest['files']]
positions = []
for item, tag in zip(manifest['files'], expected_tags):
    p=index.find(tag)
    if p<0: errors.append(f'script não referenciado: {item["path"]}')
    positions.append(p)
    path=ROOT/item['path']
    if not path.exists():
        errors.append(f'arquivo JS ausente: {item["path"]}')
        continue
    actual=hashlib.sha256(path.read_bytes()).hexdigest()
    if actual!=item['sha256']: errors.append(f'hash divergente: {item["path"]}')
    cp=subprocess.run(['node','--check',str(path)],capture_output=True,text=True)
    if cp.returncode: errors.append(f'sintaxe JS: {item["path"]}: {cp.stderr.strip()}')
if positions != sorted(positions): errors.append('ordem dos scripts diverge do manifest')
if 'jpwealth_v9_state' not in ''.join((ROOT/x['path']).read_text(encoding='utf-8') for x in manifest['files']):
    errors.append('chave de persistência principal não localizada')
if re.search(r'(?:src|href)="https?://', index, re.I):
    errors.append('dependência externa de CSS/JS encontrada no index')

# Identidade única de ícone PWA (sem biblioteca de temas): um manifesto,
# dois arquivos em assets/, ambos purpose "any" (nenhum tem margem segura
# para "maskable" — ver auditoria registrada com o usuário).
manifest_path=ROOT/'manifests/jp-wealth.webmanifest'
if not manifest_path.exists():
    errors.append(f'manifest PWA ausente: {manifest_path.relative_to(ROOT)}')
else:
    try:
        pwa=json.loads(manifest_path.read_text(encoding='utf-8'))
        icon_srcs=[icon['src'] for icon in pwa.get('icons',[])]
        for icon in pwa.get('icons',[]):
            icon_path=(manifest_path.parent/icon['src']).resolve()
            if not icon_path.exists(): errors.append(f'ícone PWA ausente: {icon_path.relative_to(ROOT)}')
            if icon.get('purpose')!='any': errors.append(f'purpose inesperado (sem margem segura para maskable): {icon.get("src")}')
        if len(icon_srcs)!=2: errors.append(f'manifesto PWA deveria declarar exatamente 2 ícones, achou {len(icon_srcs)}')
    except Exception as exc:
        errors.append(f'manifest PWA inválido: {manifest_path.relative_to(ROOT)} ({exc})')
for rel in ['assets/pwa-icon-primary.png','assets/pwa-icon-secondary.png']:
    if not (ROOT/rel).exists(): errors.append(f'ativo PWA ausente: {rel}')

if '<link rel="manifest"' not in index or 'src/js/40-app/06-app-icons.js' not in index:
    errors.append('integração PWA/ícones ausente no index')
sw=(ROOT/'sw.js').read_text(encoding='utf-8') if (ROOT/'sw.js').exists() else ''
if './manifests/jp-wealth.webmanifest' not in sw: errors.append('service worker não precacheia: manifests/jp-wealth.webmanifest')
for rel in ['assets/pwa-icon-primary.png','assets/pwa-icon-secondary.png']:
    if f'./{rel}' not in sw: errors.append(f'service worker não precacheia: {rel}')

class IdParser(HTMLParser):
    def __init__(self): super().__init__(); self.ids=[]
    def handle_starttag(self, tag, attrs):
        for k,v in attrs:
            if k=='id': self.ids.append(v)
p=IdParser(); p.feed(index)
dups=sorted({x for x in p.ids if p.ids.count(x)>1})
if dups: errors.append('IDs estáticos duplicados: '+', '.join(dups))

subprocess.run([sys.executable, str(ROOT/'tools/rebuild_monolith.py')], check=True, capture_output=True, text=True)
out=ROOT/'dist/JP_Wealth_Risk_Terminal_V9.1_PORTABLE.html'
cp=subprocess.run(['node','--check',str(ROOT/'src/js/40-app/06-boot.js')],capture_output=True,text=True)
if not out.exists() or out.stat().st_size<500_000: errors.append('rebuild portátil inválido')

if errors:
    print('VALIDAÇÃO FALHOU')
    for e in errors: print('-',e)
    raise SystemExit(1)
print(f'VALIDAÇÃO OK — {len(manifest["files"])} arquivos JS, {len(p.ids)} IDs estáticos, portátil reconstruído.')
