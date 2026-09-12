#!/usr/bin/env python3
"""A10: real Editor controls, synthetic isolated preferences, no live APIs.

The default/order expectations were fixed before the runtime patch. --baseline
records the old default and missing control as PRODUCT_FAIL for the new A10
contract; that observation is not a regression or a successful new feature.
"""
import argparse
import hashlib
import itertools
import json
from pathlib import Path
import subprocess
import traceback

from playwright.sync_api import sync_playwright
from dashboard_macro_test import launch_browser
from dashboard_forex_relocation_test import serve
from browser_bootstrap_fixture import install_bootstrap, wait_bootstrap, assert_fixture_requests
from contextual_sidebar_test import LAYOUT_KEY, LAYOUT_RAW, UNKNOWN_KEY, UNKNOWN_RAW

ROOT = Path(__file__).resolve().parents[1]
KEY = 'jpw_nav_order'
DEFAULT = ['dashboard', 'research', 'forex', 'personal-finance', 'alladin']
LEGACY = ['dashboard', 'forex', 'personal-finance', 'research', 'alladin']
PROTECTED = {LAYOUT_KEY: LAYOUT_RAW, UNKNOWN_KEY: UNKNOWN_RAW,
             'jpw_nav': 'pill', 'jpw_rail': 'expanded', 'jpw_fs': '1', 'jpw_expl': 'off'}


def settle(page):
    page.evaluate('() => new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)))')


def checkpoint(page):
    page.evaluate("() => {window.__a10S=JSON.stringify(S);window.__a10SaveCount=0;const original=save;save=function(...args){window.__a10SaveCount++;return original.apply(this,args);};}")


def boot(browser, url, raw=None, width=1440, mode='sidebar', theme='dark', read_failure=False):
    context = browser.new_context(viewport={'width': width, 'height': 1000 if width > 900 else 844},
                                  service_workers='block', has_touch=width <= 900)
    seed = {**PROTECTED, 'jpw_nav_layout': mode}
    if raw is not None:
        seed[KEY] = raw
    context.add_init_script('''(() => {
      const seed=''' + json.dumps(seed, ensure_ascii=False) + ''';
      if(!sessionStorage.getItem('__a10_seeded')){
        Object.entries(seed).forEach(([key,value])=>localStorage.setItem(key,value));
        sessionStorage.setItem('__a10_seeded','1');
      }
      window.__onbShown=true;window.__a10Writes=[];window.__a10Failure='';
      window.__a10ReadFailure=''' + json.dumps(read_failure) + ''';
      const get=Storage.prototype.getItem,set=Storage.prototype.setItem;
      window.__a10Get=key=>get.call(localStorage,key);
      window.__a10Set=(key,value)=>set.call(localStorage,key,value);
      Storage.prototype.getItem=function(key){
        if(this===localStorage&&key==='jpw_nav_order'&&window.__a10ReadFailure)
          throw new DOMException('Synthetic read unavailable','SecurityError');
        return get.call(this,key);
      };
      Storage.prototype.setItem=function(key,value){
        if(this===localStorage){
          window.__a10Writes.push({key,value:String(value)});
          if(key==='jpw_nav_order'&&window.__a10Failure==='refused')
            throw new DOMException('Synthetic quota','QuotaExceededError');
          if(key==='jpw_nav_order'&&window.__a10Failure==='unknown'){
            set.call(this,key,value);window.__a10ReadFailure=true;
            throw new Error('Synthetic post-write uncertainty');
          }
        }
        return set.call(this,key,value);
      };
    })();''')
    install_bootstrap(context)
    page = context.new_page()
    errors = []
    page.on('pageerror', lambda error: errors.append(str(error)))
    page.on('console', lambda message: errors.append(message.text) if message.type == 'error' else None)
    page.goto(url, wait_until='load')
    page.wait_for_function('window.JPWNavigation && typeof compute === "function"')
    wait_bootstrap(page)
    page.evaluate("() => {document.documentElement.dataset.theme='" + theme + "';}")
    checkpoint(page)
    settle(page)
    return context, page, errors


def order(page):
    return page.locator('#nav > .tab[data-primary]').evaluate_all('els=>els.map(el=>el.dataset.primary)')


def stored(page):
    return page.evaluate('key=>window.__a10Get(key)', KEY)


def editor(page):
    page.evaluate("() => openSettingsModal('editor')")
    page.locator('#navOrderList').wait_for(state='visible')
    settle(page)


def move(page, module='dashboard', direction='down', keyboard=False):
    button = page.locator(f'[data-nav-order-id="{module}"] [data-nav-order-move="{direction}"]')
    if keyboard:
        button.focus()
        button.press('Enter')
    else:
        button.click()
    settle(page)


def pristine(page, before=None):
    assert page.evaluate('JSON.stringify(S)===window.__a10S && window.__a10SaveCount===0'), 'financial mutation/save'
    for key, value in PROTECTED.items():
        assert page.evaluate('key=>window.__a10Get(key)', key) == value, key
    if before is not None:
        assert stored(page) == before
    duplicate = page.evaluate("() => {const ids=[...document.querySelectorAll('[id]')].map(el=>el.id);return ids.filter((id,i)=>ids.indexOf(id)!==i);}")
    assert duplicate == [], duplicate


def finish(context, errors):
    assert_fixture_requests(context)
    assert errors == [], errors
    context.close()


def run(args):
    root = args.root.resolve()
    evidence = args.evidence.resolve()
    evidence.mkdir(parents=True, exist_ok=True)
    results = []
    report = {'root': str(root), 'baseline_mode': args.baseline,
              'head': subprocess.check_output(['git', '-C', str(root), 'rev-parse', 'HEAD'], text=True).strip(),
              'inputs': {p: hashlib.sha256((root / p).read_bytes()).hexdigest()
                         for p in ['index.html', 'src/js/20-ui/12-nav-style.js', 'src/js/40-app/11-operational-shell.js', 'src/js/40-app/09-settings-modal.js', 'build-id.js']},
              'results': results}

    def check(name, fn):
        try:
            detail = fn()
            results.append({'name': name, 'result': 'PASS', 'detail': detail})
            print('PASS', name, flush=True)
        except Exception:
            results.append({'name': name, 'result': 'PRODUCT_FAIL', 'traceback': traceback.format_exc()})
            raise

    server, url = serve(root)
    try:
        with sync_playwright() as pw:
            browser = launch_browser(pw)
            if args.baseline:
                context, page, errors = boot(browser, url)
                actual = order(page)
                has_controls = page.locator('#navOrderEditor').count() > 0
                assert actual == LEGACY and not has_controls and stored(page) is None
                results.append({'name': 'new A10 contract absent in verified baseline', 'result': 'PRODUCT_FAIL',
                                'expected_order': DEFAULT, 'observed_order': actual, 'editor_present': has_controls})
                finish(context, errors)
                print('BASELINE OBSERVED: old order and missing A10 controls', flush=True)
                browser.close()
                return 1

            def defaults_and_permutations():
                context, page, errors = boot(browser, url)
                assert order(page) == DEFAULT and stored(page) is None
                assert page.evaluate('JPWNavigation.current().canonical') == 'dashboard'
                editor(page)
                before = page.evaluate('JSON.stringify(JPWNavigation.current())')
                permutations = [list(p) for p in itertools.permutations(DEFAULT)]
                examined = page.evaluate('''permutations => {
                  const observed=[];
                  for(const desired of permutations){
                    for(let target=0;target<desired.length;target++){
                      let actual=[...document.querySelectorAll('#navOrderList > li')].map(el=>el.dataset.navOrderId);
                      while(actual.indexOf(desired[target])>target){
                        document.querySelector('[data-nav-order-id="'+desired[target]+'"] [data-nav-order-move="up"]').click();
                        actual=[...document.querySelectorAll('#navOrderList > li')].map(el=>el.dataset.navOrderId);
                      }
                    }
                    const actual=[...document.querySelectorAll('#nav > .tab[data-primary]')].map(el=>el.dataset.primary);
                    if(JSON.stringify(actual)!==JSON.stringify(desired))throw new Error('Wrong preview '+desired);
                    const numbers=[...document.querySelectorAll('#nav > .tab[data-primary] .n')].map(el=>el.textContent);
                    if(JSON.stringify(numbers)!==JSON.stringify(['01','02','03','04','05']))throw new Error('Wrong visible positions');
                    document.getElementById('navOrderSave').click();
                    const raw=window.__a10Get('jpw_nav_order');
                    if(raw===null&&JSON.stringify(desired)===JSON.stringify(['dashboard','research','forex','personal-finance','alladin'])){}
                    else if(JSON.stringify(JSON.parse(raw))!==JSON.stringify(desired))throw new Error('Wrong saved order '+desired);
                    observed.push({desired,actual,stored:raw});
                  }
                  return observed;
                }''', permutations)
                assert len(examined) == 120
                assert page.evaluate('JSON.stringify(JPWNavigation.current())') == before
                pristine(page)
                saved = stored(page)
                page.reload();wait_bootstrap(page);settle(page)
                assert order(page) == permutations[-1] and stored(page) == saved
                assert page.evaluate('JPWNavigation.current().canonical') == 'dashboard', 'order changed starting page'
                assert page.evaluate("window.__a10Writes.filter(x=>x.key==='jpw_nav_order').length") == 0, 'reload rewrote order'
                finish(context, errors)
                return {'permutations': examined}
            check('default, 120 permutations through DOM controls, same current and reload', defaults_and_permutations)

            def cancel_restore_and_failure():
                original = json.dumps(LEGACY, separators=(',', ':'))
                context, page, errors = boot(browser, url, original)
                editor(page);move(page, keyboard=True)
                assert order(page) != LEGACY and stored(page) == original
                assert page.evaluate("document.activeElement.closest('[data-nav-order-id]').dataset.navOrderId") == 'dashboard'
                page.locator('#navOrderCancel').click()
                assert order(page) == LEGACY and stored(page) == original
                page.locator('#navOrderReset').click()
                assert order(page) == DEFAULT and stored(page) == original
                page.keyboard.press('Escape');settle(page)
                assert order(page) == LEGACY and stored(page) == original
                editor(page);move(page)
                draft = order(page)
                page.evaluate("window.__a10Failure='refused'")
                page.locator('#navOrderSave').click()
                assert stored(page) == original and order(page) == draft
                assert 'prévia não salva' in page.locator('#navOrderStatus').inner_text()
                assert not page.locator('#navOrderSave').is_disabled()
                page.evaluate("window.__a10Failure=''")
                page.locator('#navOrderSave').click()
                assert json.loads(stored(page)) == draft
                assert 'Ordem salva' in page.locator('#navOrderStatus').inner_text()
                pristine(page)
                page.reload();wait_bootstrap(page)
                assert order(page) == draft
                finish(context, errors)
            check('keyboard, preview, cancel, Escape, restore-only-order, refusal and explicit retry', cancel_restore_and_failure)

            def invalid_and_read_failure():
                cases = ['{broken', '[]', '["dashboard","dashboard","forex","research","alladin"]',
                         '["dashboard","research","forex","personal-finance","unexpected"]',
                         '{"order":["dashboard","research","forex","personal-finance","alladin"]}']
                for value in cases:
                    context, page, errors = boot(browser, url, value)
                    assert order(page) == DEFAULT and stored(page) == value
                    editor(page)
                    assert 'não reconhecida' in page.locator('#navOrderStatus').inner_text()
                    page.evaluate('closeSettingsModal()')
                    page.evaluate("JPWNavigation.navigate('alladin');JPWNavigation.navigate('dashboard')")
                    page.reload();wait_bootstrap(page);checkpoint(page)
                    assert order(page) == DEFAULT and stored(page) == value
                    assert page.evaluate("window.__a10Writes.filter(x=>x.key==='jpw_nav_order').length") == 0
                    editor(page);move(page)
                    page.locator('#navOrderSave').click()
                    assert json.loads(stored(page)) == order(page), 'explicit replacement failed'
                    pristine(page)
                    finish(context, errors)
                context, page, errors = boot(browser, url, json.dumps(LEGACY), read_failure=True)
                editor(page)
                assert order(page) == DEFAULT and page.locator('#navOrderSave').is_disabled()
                assert 'Não foi possível ler' in page.locator('#navOrderStatus').inner_text()
                assert stored(page) == json.dumps(LEGACY)
                finish(context, errors)
                return {'invalid_inputs': cases, 'unavailable_read': True}
            check('invalid strict fallback without rewrite and unavailable read', invalid_and_read_failure)

            def unknown_and_conflict():
                context, page, errors = boot(browser, url, json.dumps(LEGACY))
                editor(page);move(page)
                draft = order(page)
                page.evaluate("window.__a10Failure='unknown'")
                page.locator('#navOrderSave').click()
                assert 'determinar o resultado' in page.locator('#navOrderStatus').inner_text()
                assert order(page) == draft and json.loads(stored(page)) == draft
                assert page.locator('#navOrderSave').is_disabled() and page.locator('#navOrderCancel').is_disabled()
                count = page.evaluate("window.__a10Writes.filter(x=>x.key==='jpw_nav_order').length")
                page.evaluate('saveNavOrderPreview();cancelNavOrderPreview();beginNavOrderPreview();saveNavOrderPreview()')
                assert page.evaluate("window.__a10Writes.filter(x=>x.key==='jpw_nav_order').length") == count
                page.evaluate('closeSettingsModal()');editor(page)
                assert page.locator('#navOrderSave').is_disabled() and order(page) == draft
                page.reload();wait_bootstrap(page);checkpoint(page);editor(page)
                assert order(page) == draft
                move(page, 'alladin', 'up')
                external = json.dumps(DEFAULT)
                page.evaluate('([k,v])=>window.__a10Set(k,v)', [KEY, external])
                page.locator('#navOrderSave').click()
                assert 'outra ação ou aba' in page.locator('#navOrderStatus').inner_text()
                assert stored(page) == external and page.locator('#navOrderSave').is_disabled()
                page.locator('#navOrderCancel').click()
                assert order(page) == DEFAULT and stored(page) == external
                # Closing during a conflict must end that edit session. A new
                # opening must read a further external change, not retain the
                # snapshot read while closing the previous session.
                move(page, 'alladin', 'up')
                page.evaluate('([k,v])=>window.__a10Set(k,v)', [KEY, json.dumps(LEGACY)])
                page.locator('#navOrderSave').click()
                assert 'outra ação ou aba' in page.locator('#navOrderStatus').inner_text()
                page.evaluate('closeSettingsModal()')
                after_close = list(reversed(DEFAULT))
                raw_after_close = json.dumps(after_close)
                page.evaluate('([k,v])=>window.__a10Set(k,v)', [KEY, raw_after_close])
                writes_before_open = page.evaluate('window.__a10Writes.length')
                editor(page)
                assert order(page) == after_close, 'reopened Editor retained conflict snapshot'
                assert stored(page) == raw_after_close
                assert page.evaluate('window.__a10Writes.length') == writes_before_open
                pristine(page)
                finish(context, errors)
            check('unknown outcome freezes without blind retry; concurrent change is not overwritten', unknown_and_conflict)

            def modes_and_routes():
                details = []
                desired = ['alladin', 'personal-finance', 'forex', 'research', 'dashboard']
                for width in [1440, 390]:
                    for mode in ['sidebar', 'topbar']:
                        for theme in ['light', 'dark']:
                            context, page, errors = boot(browser, url, json.dumps(desired), width, mode, theme)
                            editor(page)
                            if width <= 900:
                                page.locator('[data-nav-order-id="dashboard"] [data-nav-order-move="up"]').tap()
                            else:
                                move(page, 'dashboard', 'up', keyboard=True)
                            assert order(page)[-1] == 'research'
                            for button in page.locator('#navOrderList button').all():
                                box = button.bounding_box()
                                assert box and box['width'] >= 44 and box['height'] >= 44, box
                            assert page.locator('#settingsContent').evaluate('el=>el.scrollWidth<=el.clientWidth+1'), 'Editor overflow'
                            page.screenshot(path=str(evidence / f'editor-{mode}-{width}-{theme}.png'))
                            page.locator('#navOrderSave').click()
                            page.evaluate('closeSettingsModal()');settle(page)
                            expected = order(page)
                            destinations = {'dashboard': 'dashboard', 'research': 'research-forex',
                                            'forex': 'forex-overview', 'personal-finance': 'personal-finance', 'alladin': 'alladin'}
                            for module in expected:
                                if width <= 900:
                                    page.locator('[data-shell-menu-toggle]').click()
                                page.locator(f'#nav > [data-primary="{module}"]').click()
                                assert page.evaluate('JPWNavigation.current().primary') == module
                                assert page.evaluate('JPWNavigation.current().canonical') == destinations[module]
                                assert page.locator('#nav > .tab.active').get_attribute('data-primary') == module
                                assert order(page) == expected
                            pristine(page)
                            details.append({'width': width, 'mode': mode, 'theme': theme, 'order': expected})
                            finish(context, errors)
                return details
            check('side/topbar/mobile, themes, touch, focus, overflow and real navigation targets', modes_and_routes)
            browser.close()
    except Exception:
        report['exception'] = traceback.format_exc()
        print(report['exception'], flush=True)
        return 1
    finally:
        server.shutdown();server.server_close()
        report['counts'] = {label: sum(item['result'] == label for item in results) for label in ['PASS', 'PRODUCT_FAIL']}
        (evidence / 'results.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    return 0


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--root', type=Path, default=ROOT)
    parser.add_argument('--evidence', type=Path, default=ROOT / 'tools/.artifacts/navigation-order')
    parser.add_argument('--baseline', action='store_true')
    raise SystemExit(run(parser.parse_args()))
