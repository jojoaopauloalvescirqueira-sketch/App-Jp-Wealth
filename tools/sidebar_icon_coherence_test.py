#!/usr/bin/env python3
"""CHG-JPW-SIDEBAR-ICONS-20261022: coerência dos ícones da lateral.

Oráculo: a proposta aprovada (um desenho Lucide por área; recolher/expandir e
abrir grupo na mesma família) e UI-VISUAL-QUALITY (centralização <= 2 px CSS).
Somente origens sintéticas locais; nenhuma regra financeira, dado, gate ou
schema é tocado. Teste focal; não integra quality_gate (alterar gates exige CHG
próprio de control plane).
"""
import argparse
import hashlib
import json
import re
import sys
import tempfile
from pathlib import Path
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
LUCIDE = ROOT / 'src/vendor/lucide'
PORTABLE = 'dist/JP_Wealth_Risk_Terminal_V9.1_PORTABLE.html'
TOL = 2.0
EXPECTED = {'dashboard': 'layout-dashboard', 'research': 'microscope', 'planning': 'target',
            'forex': 'chart-candlestick', 'personal-finance': 'wallet', 'alladin': 'briefcase-business',
            'tools': 'wrench'}
GROUPS = ['researchNavTrigger', 'execNavTrigger', 'finpesNavTrigger', 'toolsNavTrigger']
RESULTS = []


def check(name, ok, detail=None):
    RESULTS.append({'check': name, 'result': 'PASS' if ok else 'PRODUCT_FAIL', 'detail': detail})
    print(('PASS ' if ok else 'FAIL ') + name + ('' if ok or detail is None else f' :: {detail}'))
    return ok


def geometry(markup):
    return sorted(re.sub(r'\s+', ' ', m.strip().rstrip('/').strip()) for m in re.findall(r'<(?:path|rect|circle|line|polyline|polygon|ellipse)\b[^>]*?/?>', markup))


def static_checks():
    html = (ROOT / 'index.html').read_text(encoding='utf-8')
    prov = json.loads((LUCIDE / 'PROVENANCE.json').read_text(encoding='utf-8'))
    symbols = dict(re.findall(r'<symbol id="shell-icon-([a-z0-9-]+)" viewBox="0 0 24 24">(.*?)</symbol>', html, re.S))
    names = {e['name'] for e in prov['icons']}
    check('static: PROVENANCE lista exatamente os símbolos shell-icon-*', names == set(symbols), sorted(names ^ set(symbols)))
    files = {p.stem for p in (LUCIDE / 'icons').glob('*.svg')}
    check('static: arquivos vendorizados == PROVENANCE', files == names, sorted(files ^ names))
    for e in prov['icons']:
        b = (LUCIDE / e['local_file']).read_bytes()
        check(f"static: hash {e['name']}", hashlib.sha256(b).hexdigest() == e['vendored_sha256'] == e['source_sha256'] and len(b) == e['bytes'])
        src = re.search(r'<svg[^>]*>(.*)</svg>', b.decode(), re.S).group(1)
        check(f"static: geometria {e['name']} idêntica ao Lucide", geometry(src) == geometry(symbols.get(e['name'], '')))
        root = ET.fromstring(b)
        check(f"static: {e['name']} sem script/foreignObject/url", not any(el.tag.split('}')[-1] in ('script', 'foreignObject', 'image', 'use') for el in root.iter()) and b'url(' not in b)
    uses = {}
    for m in re.finditer(r'<button class="tab[^"]*"[^>]*data-primary="([a-z-]+)"[^>]*>\s*<svg class="nav-area-icon shell-lucide"[^>]*><use href="#shell-icon-([a-z0-9-]+)"/>', html):
        uses[m.group(1)] = m.group(2)
    check('static: ícone esperado por área', uses == EXPECTED, uses)
    check('static: nenhum desenho repetido entre áreas', len(set(uses.values())) == len(uses), uses)
    check('static: sem glifo de texto no #railToggle', re.search(r'id="railToggle"[^>]*>\s*<svg class="shell-lucide"[^>]*><use href="#shell-icon-panel-left-close"/></svg> <span class="lbl">Recolher</span></button>', html) is not None)
    for tid in GROUPS:
        check(f'static: chevron Lucide em {tid}', re.search(r'id="' + tid + r'"(?:(?!</button>).)*<svg class="nav-disclosure-icon shell-lucide" viewBox="0 0 24 24" aria-hidden="true" focusable="false"><use href="#shell-icon-chevron-right"/></svg></button>', html, re.S) is not None)
    js = (ROOT / 'src/js/20-ui/02-sidebar.js').read_text(encoding='utf-8')
    check('static: renderRailToggle sem ‹ ›', '‹' not in js and '›' not in js and "shell-icon-panel-left-'+(collapsed?'open':'close')" in js)
    man = json.loads((ROOT / 'src/js/manifest.json').read_text(encoding='utf-8'))
    entry = next(x for x in man['files'] if x.get('path') == 'src/js/20-ui/02-sidebar.js')
    check('static: digest de 02-sidebar.js no manifest', entry['sha256'] == hashlib.sha256((ROOT / 'src/js/20-ui/02-sidebar.js').read_bytes()).hexdigest())


MEASURE = """() => {
  const vis=e=>e&&e.getClientRects().length&&getComputedStyle(e).display!=='none'&&getComputedStyle(e).visibility!=='hidden';
  const box=e=>{const r=e.getBoundingClientRect();return {x:r.x,y:r.y,w:r.width,h:r.height,cx:r.x+r.width/2,cy:r.y+r.height/2,r:r.right,b:r.bottom};};
  const tabs=[...document.querySelectorAll('#nav > .tab')].filter(vis).map(t=>{
    const icon=t.querySelector('.nav-area-icon'), dis=t.querySelector('.nav-disclosure-icon'), lbl=t.querySelector('.lbl');
    const cs=icon?getComputedStyle(icon):null, after=getComputedStyle(t,'::after');
    return {primary:t.dataset.primary, use:icon?.querySelector('use')?.getAttribute('href'), tab:box(t),
      icon:icon&&vis(icon)?box(icon):null, iconStroke:cs?.strokeWidth, iconColor:cs?.stroke, tabColor:getComputedStyle(t).color,
      dis:dis&&vis(dis)?box(dis):null, disTransform:dis?getComputedStyle(dis).transform:null,
      disStroke:dis?getComputedStyle(dis).strokeWidth:null,
      after:after.content, afterDisplay:after.display,
      lbl:lbl&&vis(lbl)?box(lbl):null, lblOverflow:lbl?lbl.scrollWidth>lbl.clientWidth+1:null, text:t.innerText.trim()};
  });
  const rail=document.getElementById('railToggle'), rsvg=rail?.querySelector('svg.shell-lucide');
  return {navigation:document.documentElement.dataset.navigation, rail:document.documentElement.dataset.rail,
    tabs, railVisible:vis(rail), railBox:rail&&vis(rail)?box(rail):null, railSvg:rsvg&&vis(rsvg)?box(rsvg):null,
    railUse:rsvg?.querySelector('use')?.getAttribute('href'), railText:rail?.textContent.replace(/\\s+/g,' ').trim(),
    railLabel:rail?.getAttribute('aria-label'), railLbl:(()=>{const l=rail?.querySelector('.lbl');return l&&vis(l)?box(l):null;})()};
}"""


def near(a, b):
    return abs(a - b) <= TOL


def browser_checks(browser, url, tag, out):
    from navigation_layout_choice_test import boot, settle, finish_context
    context, page, observed = boot(browser, url, 'sidebar', alladin_active=True, personal_finance_active=True)
    try:
        m = page.evaluate(MEASURE)
        page.screenshot(path=str(out / f'{tag}-expanded-light.png'), clip={'x': 0, 'y': 0, 'width': 420, 'height': 1000})
        check(f'{tag}: layout lateral padrão expandida', m['navigation'] == 'sidebar' and m['rail'] == 'expanded', [m['navigation'], m['rail']])
        uses = {t['primary']: (t['use'] or '').replace('#shell-icon-', '') for t in m['tabs']}
        check(f'{tag}: ícones visíveis esperados (7 áreas)', all(EXPECTED[k] == v for k, v in uses.items()) and set(uses) == set(EXPECTED), uses)
        check(f'{tag}: ícones visíveis distintos', len(set(uses.values())) == len(uses), uses)
        for t in m['tabs']:
            i = t['icon']
            check(f"{tag}: {t['primary']} ícone 20 px traço 1,75 currentColor", i and near(i['w'], 20) and near(i['h'], 20) and t['iconStroke'] == '1.75px' and t['iconColor'] == t['tabColor'], [i, t['iconStroke'], t['iconColor'], t['tabColor']])
            check(f"{tag}: {t['primary']} ícone centrado na vertical", i and near(i['cy'], t['tab']['cy']), [i, t['tab']])
            grouped = t['primary'] in ('research', 'forex', 'personal-finance', 'tools')
            if grouped:
                d = t['dis']
                check(f"{tag}: {t['primary']} chevron Lucide 16 px à direita, sem ::after", d and near(d['w'], 16) and near(d['cy'], t['tab']['cy']) and t['after'] in ('none', 'normal') and t['lbl'] and t['lbl']['r'] <= d['x'] + 0.5 and d['r'] <= t['tab']['r'], [d, t['after'], t['lbl']])
                check(f"{tag}: {t['primary']} chevron fechado sem rotação", t['disTransform'] in ('none', 'matrix(1, 0, 0, 1, 0, 0)'), t['disTransform'])
            check(f"{tag}: {t['primary']} rótulo sem corte", t['lblOverflow'] is False, t['lblOverflow'])
            # Linhas observadas na baseline d517be0 a 1440 px: só "Ferramentas e Serviços" quebra.
            lines = round(t['lbl']['h'] / 21) if t['lbl'] else None
            check(f"{tag}: {t['primary']} rótulo com as mesmas linhas da baseline", lines == (2 if t['primary'] == 'tools' else 1), [lines, t['lbl']])
        r = m['railBox'], m['railSvg']
        check(f'{tag}: recolher = panel-left-close centrado', m['railUse'] == '#shell-icon-panel-left-close' and r[1] and near(r[1]['cx'], r[0]['cx']) and near(r[1]['cy'], r[0]['cy']) and near(r[1]['w'], 20) and '‹' not in m['railText'] and m['railLabel'] == 'Recolher barra lateral', [m['railUse'], r, m['railText']])
        # abrir grupo: chevron gira 90°
        page.locator('#researchNavTrigger').click(); settle(page); page.wait_for_timeout(260)
        tr = page.locator('#researchNavTrigger .nav-disclosure-icon').evaluate('e=>getComputedStyle(e).transform')
        opened = page.locator('#researchNavTrigger').evaluate("e=>e.classList.contains('sidebar-group-open')")
        check(f'{tag}: grupo aberto gira o chevron 90°', opened and re.match(r'matrix\((6\.1\d*e-17|0|-?1\.8\d*e-16), 1, -1, (6\.1\d*e-17|0|-?1\.8\d*e-16), 0, 0\)', tr or '') is not None, [opened, tr])
        page.screenshot(path=str(out / f'{tag}-group-open.png'), clip={'x': 0, 'y': 0, 'width': 420, 'height': 1000})
        page.keyboard.press('Escape'); settle(page)
        # recolher
        page.locator('#railToggle').click(); settle(page); page.wait_for_timeout(260)
        m = page.evaluate(MEASURE)
        page.screenshot(path=str(out / f'{tag}-collapsed-light.png'), clip={'x': 0, 'y': 0, 'width': 160, 'height': 1000})
        check(f'{tag}: recolhida', m['rail'] == 'collapsed', m['rail'])
        for t in m['tabs']:
            i = t['icon']
            check(f"{tag}: recolhida {t['primary']} ícone centrado (<=2 px)", i and near(i['cx'], t['tab']['cx']) and near(i['cy'], t['tab']['cy']), [i, t['tab']])
            check(f"{tag}: recolhida {t['primary']} sem chevron", t['dis'] is None, t['dis'])
        r = m['railBox'], m['railSvg']
        check(f'{tag}: expandir = panel-left-open centrado', m['railUse'] == '#shell-icon-panel-left-open' and r[1] and near(r[1]['cx'], r[0]['cx']) and near(r[1]['cy'], r[0]['cy']) and m['railLabel'] == 'Expandir barra lateral' and '›' not in m['railText'], [m['railUse'], r, m['railText']])
        page.evaluate("document.documentElement.dataset.theme='dark'"); settle(page)
        page.screenshot(path=str(out / f'{tag}-collapsed-dark.png'), clip={'x': 0, 'y': 0, 'width': 160, 'height': 1000})
        page.locator('#railToggle').click(); settle(page); page.wait_for_timeout(260)
        m = page.evaluate(MEASURE)
        page.screenshot(path=str(out / f'{tag}-expanded-dark.png'), clip={'x': 0, 'y': 0, 'width': 420, 'height': 1000})
        check(f'{tag}: escuro — ícones seguem a cor do texto', all(t['iconColor'] == t['tabColor'] for t in m['tabs']), [(t['primary'], t['iconColor'], t['tabColor']) for t in m['tabs']])
        check(f'{tag}: expandida de novo restaura recolher', m['rail'] == 'expanded' and m['railUse'] == '#shell-icon-panel-left-close')
        page.evaluate("document.documentElement.dataset.theme='light'")
        # Configurações: o mesmo nó com ícone e rótulo visível
        page.locator('#headerConfigBtn').click(); page.locator('#settingsModal').wait_for(state='visible'); page.wait_for_timeout(300)
        page.evaluate("() => activateSettingsCategory('interface')"); settle(page)
        s = page.evaluate(MEASURE)
        check(f'{tag}: Configurações — ícone e rótulo alinhados', s['railSvg'] and s['railLbl'] and near(s['railSvg']['cy'], s['railLbl']['cy']) and s['railSvg']['r'] <= s['railLbl']['x'], [s['railSvg'], s['railLbl'], s['railText']])
        page.locator('#railToggle').screenshot(path=str(out / f'{tag}-settings-rail.png'))
        page.evaluate("() => activateSettingsCategory('editor')"); settle(page)
        # outros layouts: sem chevron Lucide; submenu mantém seu ::after
        for layout in ['topbar', 'glass', 'submenu']:
            page.locator('#navLayoutSeg [data-nav-layout="' + layout + '"]').click(); settle(page)
            hidden = page.evaluate("() => [...document.querySelectorAll('.nav-disclosure-icon')].every(e=>getComputedStyle(e).display==='none')")
            check(f'{tag}: {layout} não exibe o chevron da lateral padrão', hidden)
            if layout == 'submenu':
                aft = page.evaluate("() => getComputedStyle(document.getElementById('researchNavTrigger'),'::after').content")
                check(f'{tag}: submenu mantém seu ::after', aft not in ('none', 'normal'), aft)
        page.locator('#navLayoutSeg [data-nav-layout="sidebar"]').click(); settle(page)
        page.locator('#settingsCloseBtn').click(); settle(page)
        check(f'{tag}: sem erros de página/console', not any(observed.values()), observed)
    finally:
        finish_context(context)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', default=None)
    ap.add_argument('--static-only', action='store_true')
    args = ap.parse_args()
    out = Path(args.out) if args.out else Path(tempfile.mkdtemp(prefix='jpw-sidebar-icons-'))
    out.mkdir(parents=True, exist_ok=True)
    static_checks()
    if not args.static_only:
        from playwright.sync_api import sync_playwright
        from dashboard_macro_test import launch_browser
        from dashboard_forex_relocation_test import serve
        server, url = serve(ROOT)
        try:
            with sync_playwright() as p:
                browser = launch_browser(p)
                try:
                    browser_checks(browser, url, 'source', out)
                    browser_checks(browser, url.replace('/index.html', '/' + PORTABLE), 'portable', out)
                finally:
                    browser.close()
        finally:
            server.shutdown()
    fails = [r for r in RESULTS if r['result'] != 'PASS']
    (out / 'sidebar-icon-coherence.json').write_text(json.dumps({'results': RESULTS, 'failures': len(fails)}, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(f"{len(RESULTS) - len(fails)}/{len(RESULTS)} PASS · evidência em {out}")
    sys.exit(1 if fails else 0)


if __name__ == '__main__':
    main()
