#!/usr/bin/env python3
"""Header focus-return regression, CHG-HEADER-FOCUS-20260923.

Runs the same assertions against --root before and after the localized fix.
New disposable browser contexts, synthetic draft, no financial saves or real
profile. Existing fixture server/boot assertions are reused unchanged. Receipts
stay outside the tested root; no screenshots are evidence of financial validity.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import sys
import time
import traceback

sys.dont_write_bytecode = True
from playwright.sync_api import sync_playwright
from navigation_layout_choice_test import boot, go, settle
from dashboard_forex_relocation_test import serve
from dashboard_macro_test import launch_browser

ROOT = Path(__file__).resolve().parents[1]
FLOWS = [("finalizeSessionBtn", "sessionCancel", way) for way in ("button", "Escape", "backdrop")]
FLOWS += [(opener, closer, way) for opener, closer in (
    ("headerNotificationsBtn", "notificationClose"),
    ("headerConfigBtn", "settingsCloseBtn"),
    ("headerProfileBtn", "settingsCloseBtn")) for way in ("button", "Escape")]

AVAILABLE = """el=>{if(!el?.isConnected||el.disabled||el.getAttribute('aria-disabled')==='true'||el.closest('[inert],[hidden],[aria-hidden="true"]'))return false;
 const c=getComputedStyle(el),r=el.getBoundingClientRect();
 return c.display!=='none'&&c.visibility!=='hidden'&&r.width>0&&r.height>0;}"""


def pause(page):
    settle(page)
    page.wait_for_timeout(80)
    settle(page)


def expose(page, opener):
    page.evaluate("window.scrollTo(0,0)")
    if not page.locator('#' + opener).is_visible():
        page.locator('[data-shell-menu-toggle]').click()
        page.wait_for_function("document.documentElement.dataset.shellMenu==='open'")
        page.wait_for_timeout(260)


def focus_state(page):
    return page.evaluate("""()=>{const el=document.activeElement;return {id:el.id,tag:el.tagName,
      menu:el.hasAttribute('data-shell-menu-toggle'),available:(""" + AVAILABLE + """)(el),
      owner:el.closest('dialog[open],#settingsOverlay.show,#modalOverlay.show,#mvpNotesOverlay.show')?.id||null};}""")


def expect_return(page, opener, desktop_fallback=False):
    pause(page)
    result = focus_state(page)
    expected = page.evaluate("""([id,fallback])=>{const available=""" + AVAILABLE + """;
      const original=document.getElementById(id);
      if(available(original))return id;
      const toggle=document.querySelector('[data-shell-menu-toggle]');
      if(available(toggle))return 'shell-toggle';
      return fallback?'brandHomeBtn':id;}""", [opener, desktop_fallback])
    matches = result['menu'] if expected == 'shell-toggle' else result['id'] == expected
    assert matches and result['available'] and result['tag'] != 'BODY', {'expected': expected, 'actual': result}
    return result


def painted_focus(page):
    result = page.evaluate("""()=>{const e=document.activeElement,c=getComputedStyle(e),r=e.getBoundingClientRect();
      return {id:e.id,pseudo:e.matches(':focus-visible'),style:c.outlineStyle,width:parseFloat(c.outlineWidth),
        color:c.outlineColor,offset:c.outlineOffset,shadow:c.boxShadow,rect:{width:r.width,height:r.height}};}""")
    color = result['color'].strip().lower()
    alpha = 1.0
    if color == 'transparent':
        alpha = 0.0
    elif color.startswith('rgba('):
        alpha = float(color.rstrip(')').rsplit(',', 1)[1])
    elif '/' in color:
        token = color.rstrip(')').rsplit('/', 1)[1].strip()
        alpha = float(token.rstrip('%')) / (100 if token.endswith('%') else 1)
    assert (result['pseudo'] and result['style'] == 'solid' and result['width'] >= 2 and alpha > 0
            and result['rect']['width'] > 0 and result['rect']['height'] > 0), result
    return result


def direct_paint(page, opener):
    expose(page, opener)
    page.locator('#' + opener).focus()
    page.keyboard.press('Shift+Tab')
    page.keyboard.press('Tab')
    pause(page)
    assert focus_state(page)['id'] == opener, focus_state(page)
    return painted_focus(page)


def seed_draft(page):
    page.evaluate("""()=>{localStorage.setItem('jpwealth_base_epoch_v1','BASE-V0-LEGACY');
      const n=document.createElement('textarea');n.id='focusRegressionDraft';
      n.setAttribute('aria-label','Rascunho sintético do teste de foco');n.value='Texto sintético não salvo • 001';
      document.getElementById('appMain').append(n);n.setSelectionRange(6,15);
      window.__focusNodes=['nav','appMain','exec','research','alladin','focusRegressionDraft'].map(id=>[id,document.getElementById(id)]);
    }""")


def preserved(page):
    return page.evaluate("""()=>({route:JPWNavigation.current(),state:JSON.stringify(S),raw:window.__nlRaw(),
      draft:document.getElementById('focusRegressionDraft').value,
      selection:[document.getElementById('focusRegressionDraft').selectionStart,document.getElementById('focusRegressionDraft').selectionEnd],
      identities:window.__focusNodes.map(([id,n])=>[id,n===document.getElementById(id)])})""")


def cleanup(page):
    # Only between independently recorded cases; never clears browser errors.
    page.evaluate("""()=>{if(typeof closeSettingsModal==='function')closeSettingsModal({restoreFocus:false});
      JPWNotifications.close(false);closeModal();
      if(typeof closeMvpNotesDrawer==='function')closeMvpNotesDrawer({restoreFocus:false});}""")
    pause(page)


def record(receipt, name, fn):
    item = {'name': name, 'started': time.time()}
    receipt['checks'].append(item)
    try:
        item['detail'] = fn()
        item['result'] = 'PASS'
    except Exception as error:
        item.update(result='FAIL', error=str(error), trace=traceback.format_exc())
    item['ended'] = time.time()
    print(name, item['result'], flush=True)
    return item


def matrix_case(page, opener, closer, way):
    cleanup(page)
    expose(page, opener)
    before = preserved(page)
    page.locator('#' + opener).focus()
    page.keyboard.press('Enter')
    page.locator('#' + closer).wait_for(state='visible')
    if way == 'button':
        page.locator('#' + closer).click()
    elif way == 'Escape':
        page.locator('#' + closer).focus()
        page.keyboard.press('Escape')
    else:
        page.locator('#modalOverlay').click(position={'x': 3, 'y': 3})
    pause(page)
    assert not page.locator('#' + closer).is_visible(), 'dismissal did not close its surface'
    after = preserved(page)
    assert after == before, {'preservationChanged': [k for k in before if before[k] != after[k]]}
    result = expect_return(page, opener)
    if way == 'Escape':
        result['paint'] = painted_focus(page)
    return result


def open_action(page, opener):
    expose(page, opener)
    page.locator('#' + opener).focus()
    page.keyboard.press('Enter')
    pause(page)


def adversarial(page, name):
    opener = 'finalizeSessionBtn'
    if name == 'session-entry-focus':
        open_action(page, opener)
        result = focus_state(page)
        assert result['id'] == 'sessionCancel' and result['available'], result
        return result
    if name == 'session-escape-after-tab-out':
        open_action(page, opener)
        page.locator('#sessionCancel').focus()
        for _ in range(12):
            page.keyboard.press('Tab')
            if focus_state(page)['owner'] != 'modalOverlay':
                break
        assert focus_state(page)['owner'] != 'modalOverlay', 'fixture could not move focus outside modal'
        page.keyboard.press('Escape')
        assert not page.locator('#sessionCancel').is_visible()
        return expect_return(page, opener)
    if name == 'notification-detached-opener':
        open_action(page, 'headerNotificationsBtn')
        page.evaluate("document.getElementById('headerNotificationsBtn').remove()")
        page.locator('#notificationClose').click()
        return expect_return(page, 'headerNotificationsBtn', desktop_fallback=True)
    if name.startswith('settings-opener-'):
        open_action(page, 'headerConfigBtn')
        mutation = name.removeprefix('settings-opener-')
        page.evaluate("""kind=>{const e=document.getElementById('headerConfigBtn');
          if(kind==='hidden')e.hidden=true;else if(kind==='inert')e.inert=true;else e.setAttribute('aria-hidden','true');}""", mutation)
        page.locator('#settingsCloseBtn').click()
        return expect_return(page, 'headerConfigBtn', desktop_fallback=True)
    if name.startswith('unavailable-'):
        open_action(page, opener)
        mutation = name.split('-')[1]
        page.evaluate("""kind=>{const e=document.getElementById('finalizeSessionBtn');
          if(kind==='hidden')e.hidden=true;else if(kind==='disabled')e.disabled=true;else e.remove();}""", mutation)
        page.locator('#sessionCancel').click()
        return expect_return(page, opener, desktop_fallback=True)
    if name == 'glass-resize':
        open_action(page, 'headerConfigBtn')
        page.set_viewport_size({'width': 1024, 'height': 1000})
        pause(page)
        page.locator('#settingsCloseBtn').click()
        return expect_return(page, 'headerConfigBtn')
    if name == 'rapid-reopen':
        open_action(page, opener)
        page.evaluate("""()=>{document.getElementById('sessionCancel').click();openFinalizeSessionFlow();}""")
        pause(page)
        assert page.locator('#sessionCancel').is_visible()
        result = focus_state(page)
        assert result['owner'] == 'modalOverlay', result
        page.locator('#sessionCancel').click()
        return expect_return(page, opener)
    if name == 'active-native-dialog':
        open_action(page, opener)
        page.evaluate("""()=>{document.getElementById('sessionCancel').click();const d=document.createElement('dialog');
          d.id='focusRegressionDialog';d.innerHTML='<button id="focusRegressionDialogAction">Continuar demonstração</button>';
          document.body.append(d);d.showModal();document.getElementById('focusRegressionDialogAction').focus();}""")
        pause(page)
        result = focus_state(page)
        assert result['id'] == 'focusRegressionDialogAction', result
        return result
    if name == 'active-settings':
        open_action(page, opener)
        page.evaluate("""()=>{document.getElementById('sessionCancel').click();openSettingsModal('general',document.getElementById('headerConfigBtn'));}""")
        pause(page)
        result = focus_state(page)
        assert result['owner'] == 'settingsOverlay', result
        return result
    if name == 'settings-to-notes':
        open_action(page, 'headerConfigBtn')
        page.evaluate("""()=>{closeSettingsModal();openMvpNotesDrawer(document.getElementById('headerConfigBtn'));}""")
        pause(page)
        result = focus_state(page)
        assert result['owner'] == 'mvpNotesOverlay', result
        return result
    if name == 'settings-no-restore':
        open_action(page, 'headerConfigBtn')
        page.evaluate("""()=>{closeSettingsModal({restoreFocus:false});document.getElementById('focusRegressionDraft').focus();}""")
    elif name == 'notifications-no-restore':
        open_action(page, 'headerNotificationsBtn')
        page.evaluate("""()=>{JPWNotifications.close(false);document.getElementById('focusRegressionDraft').focus();}""")
    elif name == 'notification-to-settings':
        open_action(page, 'headerNotificationsBtn')
        page.evaluate("""()=>{JPWNotifications.close(false);openSettingsModal('general',document.getElementById('headerNotificationsBtn'));}""")
        pause(page)
        result = focus_state(page)
        assert result['owner'] == 'settingsOverlay', result
        return result
    else:
        raise ValueError(name)
    pause(page)
    result = focus_state(page)
    assert result['id'] == 'focusRegressionDraft', result
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=ROOT)
    parser.add_argument('--artifact', type=Path, required=True)
    parser.add_argument('--only', choices=('all', 'matrix', 'adversarial', 'paint'), default='all')
    args = parser.parse_args()
    args.root = args.root.resolve()
    args.artifact = args.artifact.resolve()
    if args.artifact.is_relative_to(args.root):
        parser.error('--artifact must be outside the tested root')
    args.artifact.parent.mkdir(parents=True, exist_ok=True)
    build = (args.root / 'build-id.js').read_text()
    build_id = re.search(r"const JP_WEALTH_BUILD_ID = '([^']+)'", build).group(1)
    receipt = {'root': str(args.root), 'selection': args.only, 'testSha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
               'buildId': build_id, 'buildIdFileSha256': hashlib.sha256(build.encode()).hexdigest(),
               'checks': [], 'browserErrors': [],
               'limits': ['Synthetic disposable contexts only; no Safari, physical iPhone or assistive technology claim.',
                          'DOM draft verifies value/selection/node preservation; no financial transaction or calculation is validated.']}
    server, url = serve(args.root)
    try:
        with sync_playwright() as pw:
            browser = launch_browser(pw)
            receipt['browser'] = browser.version
            for mode in (() if args.only == 'adversarial' else ('sidebar', 'topbar', 'glass', 'submenu')):
                for width in ((1440, 1024, 390) if args.only == 'paint' else (1440, 1024, 390, 320)):
                    for theme in ('light', 'dark'):
                        name = f'{mode}-{width}-{theme}'
                        context = None
                        try:
                            context, page, observed = boot(browser, url, mode, width=width, submenu_rail='expanded')
                            page.evaluate('theme=>document.documentElement.dataset.theme=theme', theme)
                            go(page, 'forex-operation')
                            seed_draft(page)
                            if args.only == 'paint':
                                for opener in ('finalizeSessionBtn', 'headerNotificationsBtn', 'headerConfigBtn', 'headerProfileBtn'):
                                    record(receipt, f'{name}/direct-paint/{opener}', lambda: direct_paint(page, opener))
                            for opener, closer, way in ([] if args.only == 'paint' else FLOWS):
                                record(receipt, f'{name}/{opener}/{way}', lambda: matrix_case(page, opener, closer, way))
                            if args.only != 'paint' and (mode, width, theme) in [('sidebar', 1440, 'light'), ('glass', 1024, 'dark'), ('glass', 390, 'light')]:
                                cleanup(page)
                                matrix = record(receipt, name + '/focus-visible', lambda: matrix_case(page, 'finalizeSessionBtn', 'sessionCancel', 'Escape'))
                                page.screenshot(path=str(args.artifact.parent / (args.artifact.stem + '-' + name + '.png')), animations='disabled')
                                matrix['focusVisible'] = page.evaluate("document.activeElement.matches(':focus-visible')")
                                if matrix['result'] == 'PASS' and not matrix['focusVisible']:
                                    matrix.update(result='FAIL', error='keyboard return has no :focus-visible target')
                            record(receipt, name + '/browser-errors', lambda: assert_clean(observed))
                            receipt['browserErrors'].append({'scenario': name, 'observed': observed})
                        except Exception as error:
                            receipt['checks'].append({'name': name + '/setup', 'result': 'FAIL', 'error': str(error), 'trace': traceback.format_exc()})
                        finally:
                            if context:
                                context.close()
                            args.artifact.write_text(json.dumps(receipt, ensure_ascii=False, indent=2))
            names = ['session-entry-focus', 'session-escape-after-tab-out', 'notification-detached-opener', 'settings-opener-hidden',
                     'settings-opener-inert', 'settings-opener-aria-hidden',
                     'unavailable-hidden', 'unavailable-disabled', 'unavailable-disconnected', 'glass-resize',
                     'rapid-reopen', 'active-native-dialog', 'active-settings', 'settings-to-notes',
                     'settings-no-restore', 'notifications-no-restore', 'notification-to-settings']
            for name in ([] if args.only in ('matrix', 'paint') else names):
                context = None
                try:
                    context, page, observed = boot(browser, url, 'glass' if name == 'glass-resize' else 'sidebar', width=1440)
                    go(page, 'forex-operation')
                    seed_draft(page)
                    record(receipt, 'adversarial/' + name, lambda: adversarial(page, name))
                    record(receipt, 'adversarial/' + name + '/browser-errors', lambda: assert_clean(observed))
                except Exception as error:
                    receipt['checks'].append({'name': name + '/setup', 'result': 'FAIL', 'error': str(error), 'trace': traceback.format_exc()})
                finally:
                    if context:
                        context.close()
                    args.artifact.write_text(json.dumps(receipt, ensure_ascii=False, indent=2))
            browser.close()
    finally:
        server.shutdown()
        server.server_close()
    receipt['summary'] = {status: sum(row['result'] == status for row in receipt['checks']) for status in ('PASS', 'FAIL')}
    args.artifact.write_text(json.dumps(receipt, ensure_ascii=False, indent=2))
    print(json.dumps(receipt['summary']), flush=True)
    return 1 if receipt['summary']['FAIL'] else 0


def assert_clean(observed):
    assert not any(observed.values()), observed
    return observed


if __name__ == '__main__':
    raise SystemExit(main())
