#!/usr/bin/env python3
"""Header avatar and compact finalize: disposable browser contexts only."""
import argparse
import base64
import json
import threading
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from playwright.sync_api import sync_playwright
from browser_bootstrap_fixture import install_bootstrap, wait_bootstrap

ROOT = Path(__file__).resolve().parents[1]

class Quiet(SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass
    def translate_path(self, path):
        if path.startswith('/dist/assets/'):
            path = path.replace('/dist/assets/', '/assets/', 1)
        return super().translate_path(path)

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=ROOT)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--baseline', action='store_true')
    args = parser.parse_args()
    if args.output.resolve().is_relative_to(args.root.resolve()):
        parser.error('Evidence must be outside the product')
    args.output.mkdir(parents=True, exist_ok=True)
    server = ThreadingHTTPServer(('127.0.0.1', 0), partial(Quiet, directory=str(args.root)))
    threading.Thread(target=server.serve_forever, daemon=True).start()
    results = []
    try:
        with sync_playwright() as pw:
            browser = pw.chromium.launch()
            for entry in (['index.html'] if args.baseline else ['index.html', 'dist/JP_Wealth_Risk_Terminal_V9.1_PORTABLE.html']):
                context = browser.new_context(service_workers='block', viewport={'width':1440, 'height':950})
                install_bootstrap(context)
                context.add_init_script('window.__onbShown=true;')
                page = context.new_page()
                errors = []
                page.on('pageerror', lambda e: errors.append(str(e)))
                page.goto(f'http://127.0.0.1:{server.server_port}/{entry}')
                wait_bootstrap(page)
                page.wait_for_timeout(700)
                page.evaluate("() => {closeModal();window.__onbShown=true;S.onboarding.done=true;save();}")
                if not args.baseline:
                    assert page.locator('#headerProfileAvatar').inner_text() == 'JP'
                    page.locator('#headerProfileBtn').focus()
                    assert page.locator('#headerProfileBtn').evaluate("e=>e.matches(':focus-visible')")
                    page.keyboard.press('Enter')
                    assert page.evaluate('settingsState.active') == 'account'
                    page.locator('#settingsProfileNameInput').fill('Perfil Teste')
                    assert page.locator('#headerProfileAvatar').inner_text() == 'JP'
                    page.locator('#settingsProfileSaveBtn').click()
                    page.wait_for_function("document.querySelector('#headerProfileAvatar').textContent==='PT'")
                    page.locator('#settingsCloseBtn').click()
                    page.wait_for_function("document.activeElement.id==='headerProfileBtn'")
                    page.locator('#headerProfileBtn').click()
                    page.locator('#settingsProfileNameInput').fill('Rascunho Cancelado')
                    page.keyboard.press('Escape')
                    assert page.locator('#headerProfileAvatar').inner_text() == 'PT'
                    page.locator('#headerProfileBtn').click()
                    page.locator('#settingsProfileGallery summary').click()
                    page.locator('[data-profile-avatar]').first.click()
                    assert page.locator('#headerProfileAvatar img').count() == 0
                    page.locator('#settingsProfileSaveBtn').click()
                    page.wait_for_function("document.querySelector('#headerProfileAvatar img')?.naturalWidth>0")
                    page.locator('#settingsCloseBtn').click()
                    page.reload(); wait_bootstrap(page)
                    page.wait_for_function("document.querySelector('#headerProfileAvatar img')?.naturalWidth>0")
                    assert page.locator('#headerProfileBtn').get_attribute('aria-label').endswith('Perfil Teste')
                    page.locator('#headerProfileAvatar img').evaluate("e=>e.dispatchEvent(new Event('error'))")
                    assert page.locator('#headerProfileAvatar').inner_text() == 'PT'
                    page.locator('#headerProfileBtn').click()
                    page.locator('#settingsProfileRemovePhotoBtn').click()
                    assert page.locator('#headerProfileAvatar img').count() == 1
                    page.locator('#settingsProfileSaveBtn').click()
                    page.wait_for_function("!document.querySelector('#headerProfileAvatar img')")
                    # Real file input/raster path, using an image synthesized in the disposable page.
                    data = page.evaluate("() => {const c=document.createElement('canvas');c.width=c.height=64;const x=c.getContext('2d');x.fillStyle='#a32024';x.fillRect(0,0,64,64);return c.toDataURL('image/png').split(',')[1]}")
                    page.locator('#settingsProfilePhotoInput').set_input_files({'name':'synthetic.png','mimeType':'image/png','buffer':base64.b64decode(data)})
                    page.wait_for_function('!settingsProfileState.busy && !!settingsProfileState.draft.avatarDataUrl')
                    assert page.locator('#headerProfileAvatar img').count() == 0
                    page.locator('#settingsProfileSaveBtn').click()
                    page.wait_for_function("document.querySelector('#headerProfileAvatar img')?.naturalWidth>0")
                    page.locator('#settingsCloseBtn').click()
                    page.locator('#finalizeSessionBtn').click()
                    assert page.locator('#modalBox').is_visible()
                    assert page.locator('#sessionExport').count() == 1
                    page.evaluate('closeModal()')
                    results.append({'entry':entry,'behavior':'save/cancel/gallery/upload/remove/reload/fallback/keyboard/focus/finalize','result':'PASS'})
                # Same confirmed synthetic portrait and preferences for before/after visual comparisons.
                page.evaluate("() => {localStorage.setItem(SETTINGS_PROFILE_KEY,JSON.stringify({schemaVersion:1,displayName:'Perfil Teste',avatarDataUrl:SETTINGS_PROFILE_AVATARS[0].avatarDataUrl}));settingsProfileReload();}")
                for nav in ['sidebar','topbar']:
                    page.evaluate("n=>localStorage.setItem('jpw_nav_layout',n)", nav)
                    page.reload(); wait_bootstrap(page); page.evaluate('closeModal();window.__onbShown=true')
                    for width in [320,390,768,1440]:
                        page.set_viewport_size({'width':width,'height':950})
                        for theme in ['light','dark']:
                            page.evaluate('t=>{S.theme=t;applyTheme()}', theme)
                            page.wait_for_timeout(180)
                            facts = page.evaluate("""() => {
                              const ids=['headerNotificationsBtn','headerConfigBtn','headerProfileBtn','finalizeSessionBtn'];
                              return {nav:document.documentElement.dataset.navigation,buttons:ids.filter(id=>document.getElementById(id)).map(id=>{const e=document.getElementById(id),r=e.getBoundingClientRect(),svg=e.querySelector('svg'),avatar=e.querySelector('.header-profile-avatar');return {id,x:r.x,y:r.y,w:r.width,h:r.height,right:r.right,bottom:r.bottom,visual:svg?svg.getBoundingClientRect().width:(avatar?avatar.getBoundingClientRect().width:0)}})};
                            }""")
                            if not args.baseline:
                                assert facts['nav']==nav, facts
                                buttons=facts['buttons']
                                assert len(buttons)==4 and all(b['x']>=0 and b['right']<=width for b in buttons), facts
                                assert all(buttons[i]['right']<=buttons[i+1]['x']+1 for i in range(3)), facts
                                assert all(abs(b['w']-44)<1 and abs(b['h']-44)<1 for b in buttons), facts
                                assert all(abs(b['visual']-17)<1 for b in (buttons[0],buttons[1],buttons[3])), facts
                                assert abs(buttons[2]['visual']-30)<1, facts
                                assert page.locator('#headerActions .header-action-label').count()==0
                                for selector in ('#headerNotificationsBtn','#headerConfigBtn','#headerProfileBtn','#finalizeSessionBtn'):
                                    button=page.locator(selector)
                                    assert button.get_attribute('title') and button.get_attribute('aria-label')
                            tag=('baseline' if args.baseline else 'after')+('-portable' if entry.startswith('dist/') else '')+f'-{nav}-{width}-{theme}'
                            page.locator('body > header').screenshot(path=str(args.output/(tag+'.png')))
                            results.append({'entry':entry,'width':width,'nav':nav,'theme':theme,'result':'CAPTURE' if args.baseline else 'PASS','geometry':facts})
                assert not errors, errors
                context.close()
            browser.close()
        (args.output/'results.json').write_text(json.dumps(results,ensure_ascii=False,indent=2)+'\n')
        print(f'HEADER PROFILE PASS: {len(results)} scenarios; {args.output}', flush=True)
    finally:
        server.shutdown();server.server_close()

if __name__=='__main__':
    main()
