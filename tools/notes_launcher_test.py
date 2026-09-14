#!/usr/bin/env python3
"""NOTES-LAUNCHER-01: real inputs, modal isolation and ephemeral position.

Uses the existing economic bootstrap fixtures and Chromium runtime. Position is
observed through geometry, never through a replacement implementation. No real
browser profile or financial data is inspected. --baseline checks the frozen
recovery before the new host exists; --native-zoom adds a fresh 200% profile.
"""
import argparse
from datetime import datetime, timezone
from functools import partial
import hashlib
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
import math
import os
from pathlib import Path
import tempfile
import threading

from playwright.sync_api import sync_playwright, expect
from browser_bootstrap_fixture import install_bootstrap, wait_bootstrap, assert_fixture_requests

ROOT = Path(__file__).resolve().parents[1]
SOURCE_FILES = ('index.html', 'src/styles/app.css', 'src/js/40-app/14-mvp-notes.js',
                'src/js/40-app/09-settings-modal.js', 'build-id.js',
                'dist/JP_Wealth_Risk_Terminal_V9.1_PORTABLE.html')


class Quiet(SimpleHTTPRequestHandler):
    def log_message(self, *_):
        pass


def hashes(root):
    return {name: hashlib.sha256((root / name).read_bytes()).hexdigest()
            for name in SOURCE_FILES if (root / name).exists()}


def launch_options():
    executable = next((item for item in (os.environ.get('JP_WEALTH_CHROMIUM'),
        '/usr/bin/chromium', '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome')
        if item and Path(item).exists()), None)
    return {'headless': True, **({'executable_path': executable} if executable else {})}


def settle(page):
    page.evaluate('() => new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve)))')


def instrument(page):
    page.evaluate("""() => {
      window.__notesLauncherWrites=[];
      if(window.__notesLauncherInstrumented)return;
      window.__notesLauncherInstrumented=true;
      for(const method of ['setItem','removeItem','clear']){
        const original=Storage.prototype[method];
        Storage.prototype[method]=function(...args){
          window.__notesLauncherWrites.push({method,area:this===localStorage?'local':'session',key:args[0]||null});
          return original.apply(this,args);
        };
      }
    }""")


def snapshot(page):
    return page.evaluate("""() => ({state:JSON.stringify(S),
      local:JSON.stringify(Object.fromEntries(Object.keys(localStorage).sort().map(k=>[k,localStorage.getItem(k)]))),
      session:JSON.stringify(Object.fromEntries(Object.keys(sessionStorage).sort().map(k=>[k,sessionStorage.getItem(k)]))),
      writes:window.__notesLauncherWrites.length})""")


def unchanged(page, before, label):
    after = snapshot(page)
    assert after == before, {'case': label, 'changed': [k for k in before if after[k] != before[k]],
                             'writes': page.evaluate('window.__notesLauncherWrites')}


def prepare(context, url, theme='light', seed=True):
    install_bootstrap(context)
    context.add_init_script('window.__onbShown=true')
    page = context.pages[0] if context.pages else context.new_page()
    observed = {'pageerror': [], 'console': []}
    page.on('pageerror', lambda error: observed['pageerror'].append(str(error)))
    page.on('console', lambda msg: observed['console'].append(msg.text) if msg.type == 'error' else None)
    page.route('**/dist/assets/**', lambda route: route.continue_(url=route.request.url.replace('/dist/assets/', '/assets/')))
    page.goto(url, wait_until='load')
    wait_bootstrap(page)
    page.evaluate("""theme => {
      window.__onbShown=true;closeModal();
      document.documentElement.dataset.theme=theme;
      window.alert=()=>{};window.confirm=()=>false;window.prompt=()=>null;
    }""", theme)
    if seed:
        page.evaluate("""() => {
          S.onboarding={...S.onboarding,done:true};
          S.mvpNotes.showHeaderIcon=true;
          if(save()!==true)throw Error('Synthetic setup could not persist');
          localStorage.setItem('notes_launcher_unrelated','synthetic-preserved');
          // Finalization lazily establishes its preexisting causal epoch on a
          // virgin origin. Establish it through the real protocol before the
          // no-write boundary; never attribute that bootstrap to the launcher.
          const stateBeforeEpoch=JSON.stringify(S),rawBeforeEpoch=localStorage.getItem(LSKEY);
          if(!sessionEpochCurrent())throw Error('Synthetic setup could not establish the base epoch');
          if(JSON.stringify(S)!==stateBeforeEpoch || localStorage.getItem(LSKEY)!==rawBeforeEpoch)
            throw Error('Epoch preparation changed the operational document');
          renderMvpNotesHeader();
        }""")
    settle(page)
    instrument(page)
    return page, observed


def assert_clean(context, observed):
    assert not observed['pageerror'] and not observed['console'], observed
    assert_fixture_requests(context)


def geometry(page):
    return page.locator('#headerNotesBtn').evaluate("""e => {
      const r=e.getBoundingClientRect(),v=window.visualViewport;
      return {x:r.left,y:r.top,w:r.width,h:r.height,right:r.right,bottom:r.bottom,
        vw:innerWidth,vh:innerHeight,visual:v?{x:v.offsetLeft,y:v.offsetTop,w:v.width,h:v.height,scale:v.scale}:null};
    }""")


def contained(page):
    r = geometry(page)
    assert r['w'] >= 44 and r['h'] >= 44, r
    left, top, right, bottom = visible_bounds(r)
    assert r['x'] >= left and r['y'] >= top and r['right'] <= right + 1 and r['bottom'] <= bottom + 1, r
    assert page.evaluate('document.documentElement.scrollWidth <= innerWidth + 1'), r
    return r


def visible_bounds(r):
    # Native zoom can reserve scrollbar width inside innerWidth; pinch zoom also
    # changes the visible region. Keep the button inside both actual viewports.
    v = r['visual']
    if not v:
        return 0, 0, r['vw'], r['vh']
    return max(0, v['x']), max(0, v['y']), min(r['vw'], v['x'] + v['w']), min(r['vh'], v['y'] + v['h'])


def same_position(first, second, tolerance=1):
    assert abs(first['x'] - second['x']) <= tolerance and abs(first['y'] - second['y']) <= tolerance, (first, second)


def default_position(page):
    r = contained(page)
    assert abs(r['w'] - 56) <= 1 and abs(r['h'] - 56) <= 1, r
    # Synthetic desktop/mobile contexts have zero safe-area insets.
    _, _, right, bottom = visible_bounds(r)
    assert 19 <= right - r['right'] <= 21 and 19 <= bottom - r['bottom'] <= 21, r
    return r


def structure(page):
    assert page.locator('body > #mvpNotesLauncher').count() == 1, 'NOTES-LAUNCHER-01: required floating host absent'
    assert page.locator('#mvpNotesLauncher #headerNotesBtn').count() == 1
    assert page.locator('#headerNotesBtn').count() == 1
    assert page.locator('#headerActions #headerNotesBtn').count() == 0
    assert page.locator('#headerActions .header-action').count() == 3
    expect(page.locator('#headerNotesBtn')).to_have_attribute('title', 'Notas')
    assert (page.locator('#headerNotesBtn').get_attribute('aria-label') or '').startswith('Abrir notas')
    assert page.locator('#headerNotesBtn svg[aria-hidden="true"]').count() == 1
    assert page.locator('#headerNotesBadge').count() == 1
    assert page.locator('#headerNotesBtn').get_attribute('aria-describedby'), 'keyboard/movement help is required'
    expect(page.locator('#headerNotesBtn')).to_be_visible()
    return default_position(page)


def launcher_icon_contrast(page, themes=('light', 'dark')):
    """Only the opaque icon/button source colors, including actual hover filter.

    This does not measure antialiased edge pixels or certify general WCAG conformance.
    """
    original = page.evaluate('document.documentElement.dataset.theme')
    measurements = []
    button = page.locator('#headerNotesBtn')
    try:
        for theme in themes:
            page.evaluate('theme=>document.documentElement.dataset.theme=theme', theme)
            for state in ('normal', 'hover'):
                page.mouse.move(1, 1)
                if state == 'hover':
                    button.hover()
                settle(page)
                assert button.evaluate("e=>e.matches(':hover')") == (state == 'hover'), (theme, state)
                values = button.evaluate(r"""e=>{
                  const b=getComputedStyle(e),s=getComputedStyle(e.querySelector('svg'));
                  const rgb=value=>{
                    const match=value.match(/^rgba?\(([^)]+)\)$/);
                    if(!match)throw Error('Unsupported contrast color: '+value);
                    const values=match[1].split(',').map(Number);
                    if((values.length!==3 && values.length!==4) || values.some(v=>!Number.isFinite(v)) ||
                       (values.length===4 && values[3]!==1))throw Error('Contrast requires opaque RGB: '+value);
                    return values.slice(0,3);
                  };
                  if(b.backgroundImage!=='none' || b.opacity!=='1' || s.opacity!=='1' ||
                     s.strokeOpacity!=='1' || s.filter!=='none')throw Error('Unsupported icon/background composition');
                  const filter=b.filter.match(/^brightness\((\d*\.?\d+)(%)?\)$/);
                  if(b.filter!=='none' && !filter)throw Error('Unsupported launcher filter: '+b.filter);
                  const brightness=filter?Number(filter[1])/(filter[2]?100:1):1;
                  const filtered=value=>rgb(value).map(c=>Math.max(0,Math.min(255,c*brightness)));
                  const luminance=colors=>colors.map(c=>c/255).map(c=>c<=0.04045?c/12.92:((c+0.055)/1.055)**2.4)
                    .reduce((sum,c,i)=>sum+c*[0.2126,0.7152,0.0722][i],0);
                  const background=filtered(b.backgroundColor),icon=filtered(s.stroke);
                  const a=luminance(background),z=luminance(icon);
                  return {sourceBackground:b.backgroundColor,sourceIcon:s.stroke,filter:b.filter,
                    effectiveBackground:background,effectiveIcon:icon,ratio:(Math.max(a,z)+0.05)/(Math.min(a,z)+0.05)};
                }""")
                values.update(theme=theme, state=state)
                measurements.append(values)
                assert values['ratio'] >= 3, {'case': 'launcher icon/background contrast >= 3', **values}
    finally:
        page.mouse.move(1, 1)
        page.evaluate('theme=>document.documentElement.dataset.theme=theme', original)
        settle(page)
    return measurements


def unavailable(page, label):
    expect(page.locator('#mvpNotesLauncher')).to_be_hidden()
    previous = page.evaluate('document.activeElement.id')
    page.locator('#headerNotesBtn').evaluate('e=>e.focus()')
    assert page.evaluate('document.activeElement.id') != 'headerNotesBtn', label
    assert page.evaluate('document.activeElement.id') == previous, label


def click_and_keyboard(page):
    button = page.locator('#headerNotesBtn')
    for trigger in ('click', 'Enter', 'Space'):
        button.focus()
        if trigger == 'click':
            button.click()
        else:
            button.press(trigger)
        expect(page.locator('#mvpNotesOverlay')).to_be_visible()
        expect(page.locator('#mvpNotesTitle')).to_have_text('Notas')
        unavailable(page, 'launcher covered by Notes')
        expect(page.locator('#mvpNotesCloseBtn')).to_be_focused()
        page.locator('#mvpNotesCloseBtn').click()
        expect(button).to_be_visible()
        expect(button).to_be_focused()


def mouse_move(page, dx, dy, finish='up'):
    first = geometry(page)
    x, y = first['x'] + first['w']/2, first['y'] + first['h']/2
    page.locator('#headerNotesBtn').evaluate("e=>e.addEventListener('pointerdown',event=>window.__notesLauncherPointerId=event.pointerId,{once:true})")
    page.mouse.move(x, y)
    page.mouse.down()
    page.mouse.move(x + dx, y + dy, steps=8)
    if finish == 'escape':
        page.keyboard.press('Escape')
    elif finish == 'cancel':
        page.locator('#headerNotesBtn').dispatch_event('pointercancel', {'pointerId': page.evaluate('window.__notesLauncherPointerId')})
    elif finish == 'lostcapture':
        page.locator('#headerNotesBtn').evaluate('e=>e.releasePointerCapture(window.__notesLauncherPointerId)')
        settle(page)
    page.mouse.up()
    settle(page)
    return first, geometry(page)


def movement(page):
    first, after = mouse_move(page, -180, -125)
    assert abs(after['x'] - first['x'] + 180) <= 2 and abs(after['y'] - first['y'] + 125) <= 2, (first, after)
    expect(page.locator('#mvpNotesOverlay')).to_be_hidden()
    for cancel in ('escape', 'cancel', 'lostcapture'):
        before, after = mouse_move(page, -45, -35, cancel)
        same_position(before, after)
        expect(page.locator('#mvpNotesOverlay')).to_be_hidden()
    # Cancelling before crossing the drag threshold must also consume the
    # pointer gesture; the residual pointerup click must not open Notes.
    before, after = mouse_move(page, 0, 0, 'escape')
    same_position(before, after)
    expect(page.locator('#mvpNotesOverlay')).to_be_hidden()
    # Below the six-pixel drag threshold remains a real click.
    mouse_move(page, 2, 2)
    expect(page.locator('#mvpNotesOverlay')).to_be_visible()
    page.locator('#mvpNotesCloseBtn').click()
    button = page.locator('#headerNotesBtn')
    button.focus()
    before = geometry(page)
    button.press('Alt+ArrowLeft')
    after = geometry(page)
    assert abs(after['x'] - before['x'] + 24) <= 1 and abs(after['y'] - before['y']) <= 1, (before, after)
    button.press('Alt+Shift+ArrowUp')
    next_position = geometry(page)
    assert abs(next_position['y'] - after['y'] + 8) <= 1, (after, next_position)
    button.press('Alt+Home')
    default_position(page)
    expect(page.locator('#mvpNotesOverlay')).to_be_hidden()


def settings_flow(page):
    page.locator('#headerConfigBtn').click()
    unavailable(page, 'launcher covered by Settings')
    page.locator('#settingsSearch').fill('bloco de notas')
    expect(page.locator('#settingsSearchResults [data-settings-result]').first).to_be_visible()
    page.locator('#settingsSearchResults [data-settings-result]').first.click()
    expect(page.locator('#mvpNotesSettingsCard')).to_be_visible()
    page.locator('#mvpNotesOpenFromSettingsBtn').click()
    expect(page.locator('#mvpNotesOverlay')).to_be_visible()
    assert page.locator('#settingsModal').evaluate('e=>e.inert')
    unavailable(page, 'launcher covered by nested Notes')
    page.locator('#mvpNotesCloseBtn').click()
    expect(page.locator('#mvpNotesOpenFromSettingsBtn')).to_be_focused()
    assert not page.locator('#settingsModal').evaluate('e=>e.inert')
    for ident in ('mvpNotesPositionX', 'mvpNotesPositionY'):
        slider = page.locator('#' + ident)
        expect(slider).to_have_attribute('type', 'range')
        expect(slider).to_have_attribute('min', '0')
        expect(slider).to_have_attribute('max', '100')
        slider.focus()
        slider.press('Home')
        for _ in range(20):
            slider.press('ArrowRight')
        expect(slider).to_have_value('20')
    page.locator('#settingsCloseBtn').click()
    expect(page.locator('#headerConfigBtn')).to_be_focused()
    r = contained(page)
    assert r['x'] < r['vw'] / 2 and r['y'] < r['vh'] / 2, r
    page.locator('#headerConfigBtn').click()
    page.evaluate("settingsNavigateToLeaf('interface')")
    page.locator('#mvpNotesPositionReset').click()
    page.locator('#settingsCloseBtn').click()
    default_position(page)


def overlay_isolation(page):
    # Real shared-modal entry: cancelling must preserve the operational session.
    page.locator('#finalizeSessionBtn').click()
    expect(page.locator('#modalOverlay')).to_be_visible()
    unavailable(page, 'launcher covered by shared finalization modal')
    page.locator('#sessionCancel').click()
    expect(page.locator('#headerNotesBtn')).to_be_visible()
    # These are contract probes of each overlay's visibility boundary; not a
    # claim that the Alladin/calendar business workflows were rerun here.
    for ident in ('alladinModalOverlay', 'ecalOverlay'):
        overlay = page.locator('#' + ident)
        overlay.evaluate("e=>e.classList.add('show')")
        settle(page)
        unavailable(page, ident)
        overlay.evaluate("e=>e.classList.remove('show')")
        settle(page)
        expect(page.locator('#headerNotesBtn')).to_be_visible()


def rendering_navigation(page):
    mouse_move(page, -100, -80)
    position = geometry(page)
    for route in ('personal-finance', 'research-forex', 'dashboard') * 3:
        assert page.evaluate('route=>JPWNavigation.navigate(route)', route)
        page.evaluate('renderMvpNotesHeader()')
        settle(page)
        same_position(position, geometry(page))
    for width in (768, 390, 320, 1440):
        page.set_viewport_size({'width': width, 'height': 900})
        settle(page)
        contained(page)
    page.locator('#headerNotesBtn').press('Alt+Home')
    default_position(page)


def visibility_and_reload(page):
    notes = page.evaluate('JSON.stringify(S.mvpNotes)')
    page.locator('#headerConfigBtn').click()
    page.evaluate("settingsNavigateToLeaf('interface')")
    page.locator('[data-mvp-notes-visibility="hide"]').click()
    assert page.evaluate('S.mvpNotes.showHeaderIcon') is False
    page.locator('#settingsCloseBtn').click()
    expect(page.locator('#mvpNotesLauncher')).to_be_hidden()
    page.reload(wait_until='load')
    wait_bootstrap(page)
    page.evaluate('() => {window.__onbShown=true;closeModal();}')
    expect(page.locator('#mvpNotesLauncher')).to_be_hidden()
    assert page.evaluate('S.mvpNotes.showHeaderIcon') is False
    page.locator('#headerConfigBtn').click()
    page.evaluate("settingsNavigateToLeaf('interface')")
    page.locator('#mvpNotesOpenFromSettingsBtn').click()
    expect(page.locator('#mvpNotesOverlay')).to_be_visible()
    page.locator('#mvpNotesCloseBtn').click()
    page.locator('[data-mvp-notes-visibility="show"]').click()
    page.locator('#settingsCloseBtn').click()
    default_position(page)
    assert page.evaluate('JSON.stringify(S.mvpNotes)') == notes, 'Visibility round-trip changes no note data/schema/preferences'
    mouse_move(page, -95, -85)
    page.reload(wait_until='load')
    wait_bootstrap(page)
    page.evaluate('() => {window.__onbShown=true;closeModal();}')
    default_position(page)
    assert page.evaluate('JSON.stringify(S.mvpNotes)') == notes


def touch_move(page):
    before = geometry(page)
    x, y = before['x'] + before['w']/2, before['y'] + before['h']/2
    cdp = page.context.new_cdp_session(page)
    point = lambda a, b: [{'x': a, 'y': b, 'id': 1, 'radiusX': 2, 'radiusY': 2, 'force': 1}]
    cdp.send('Input.dispatchTouchEvent', {'type': 'touchStart', 'touchPoints': point(x, y)})
    for step in range(1, 7):
        cdp.send('Input.dispatchTouchEvent', {'type': 'touchMove', 'touchPoints': point(x - 90*step/6, y - 110*step/6)})
    cdp.send('Input.dispatchTouchEvent', {'type': 'touchEnd', 'touchPoints': []})
    settle(page)
    after = contained(page)
    assert abs(after['x'] - before['x'] + 90) <= 2 and abs(after['y'] - before['y'] + 110) <= 2, (before, after)
    expect(page.locator('#mvpNotesOverlay')).to_be_hidden()
    x, y = after['x'] + after['w']/2, after['y'] + after['h']/2
    cdp.send('Input.dispatchTouchEvent', {'type': 'touchStart', 'touchPoints': point(x, y)})
    cdp.send('Input.dispatchTouchEvent', {'type': 'touchMove', 'touchPoints': point(x - 35, y - 25)})
    cdp.send('Input.dispatchTouchEvent', {'type': 'touchCancel', 'touchPoints': []})
    settle(page)
    same_position(after, geometry(page))
    expect(page.locator('#mvpNotesOverlay')).to_be_hidden()
    cdp.detach()


def run(args):
    report = {'started_at': datetime.now(timezone.utc).isoformat(), 'root': str(args.root),
        'inputs_before': hashes(args.root), 'test_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'checks': [], 'limits': ['Synthetic Chromium contexts only; no user browser or personal data.',
            'Alladin/calendar overlay probes test the launcher boundary, not their domain workflows.',
            'Native 200% runs only with --native-zoom; CSS zoom is never substituted.']}
    server = ThreadingHTTPServer(('127.0.0.1', 0), partial(Quiet, directory=str(args.root)))
    threading.Thread(target=server.serve_forever, daemon=True).start()
    prefix = f'http://127.0.0.1:{server.server_port}/'
    failed = False
    try:
        with sync_playwright() as pw:
            browser = pw.chromium.launch(**launch_options())
            artifacts = ['index.html', 'dist/JP_Wealth_Risk_Terminal_V9.1_PORTABLE.html'] if args.artifact == 'both' else [
                'index.html' if args.artifact == 'source' else 'dist/JP_Wealth_Risk_Terminal_V9.1_PORTABLE.html']
            for artifact in artifacts:
                context = browser.new_context(viewport={'width': 1440, 'height': 900}, service_workers='block', reduced_motion='reduce')
                label = artifact + '/desktop'
                try:
                    page, observed = prepare(context, prefix + artifact, seed=not args.baseline)
                    structure(page)
                    if args.baseline:
                        raise AssertionError('Baseline unexpectedly already has the floating launcher')
                    before = snapshot(page)
                    for name, test in [('icon-background-contrast', launcher_icon_contrast), ('click-keyboard', click_and_keyboard), ('movement-cancellation', movement),
                            ('settings-ranges-focus', settings_flow), ('overlay-isolation', overlay_isolation),
                            ('render-navigation-resize', rendering_navigation)]:
                        measurements = test(page)
                        unchanged(page, before, name)
                        report['checks'].append({'name': artifact + '/' + name, 'result': 'PASS',
                            **({'measurements': measurements} if measurements is not None else {})})
                    visibility_and_reload(page)
                    assert_clean(context, observed)
                    report['checks'].append({'name': artifact + '/visibility-reload-schema', 'result': 'PASS'})
                except Exception as error:
                    result = 'BASELINE_FAIL' if args.baseline and 'floating host absent' in str(error) else 'PRODUCT_FAIL' if isinstance(error, AssertionError) else 'TEST_HARNESS_FAIL'
                    report['checks'].append({'name': label, 'result': result, 'detail': str(error)})
                    failed = True
                finally:
                    context.close()
                if args.baseline:
                    continue
                # Two touch cases complement desktop and the 768/390/320 resize
                # sequence above; this focal does not repeat a full visual suite.
                for width, theme in [(390, 'light'), (320, 'dark')]:
                    context = browser.new_context(viewport={'width': width, 'height': 900}, has_touch=width < 768,
                        is_mobile=width < 768, service_workers='block', reduced_motion='reduce')
                    label = f'{artifact}/{width}/{theme}'
                    try:
                        page, observed = prepare(context, prefix + artifact, theme)
                        structure(page)
                        before = snapshot(page)
                        contrast = launcher_icon_contrast(page, (theme,))
                        if width < 768:
                            touch_move(page)
                            page.locator('[data-shell-menu-toggle]').click()
                            unavailable(page, 'mobile navigation menu')
                            page.locator('#sidebarClose').click()
                            expect(page.locator('#headerNotesBtn')).to_be_visible()
                        else:
                            page.locator('#headerNotesBtn').press('Alt+ArrowLeft')
                        contained(page)
                        unchanged(page, before, label)
                        assert_clean(context, observed)
                        report['checks'].append({'name': label, 'result': 'PASS', 'icon_contrast': contrast})
                    except Exception as error:
                        report['checks'].append({'name': label, 'result': 'PRODUCT_FAIL' if isinstance(error, AssertionError) else 'TEST_HARNESS_FAIL', 'detail': str(error)})
                        failed = True
                    finally:
                        context.close()
            if args.native_zoom and not args.baseline:
                for theme in ('dark',):
                    profile = Path(tempfile.mkdtemp(prefix='notes-native-200-', dir=args.out.parent))
                    (profile / 'Default').mkdir()
                    (profile / 'Default/Preferences').write_text(json.dumps({'partition': {'default_zoom_level': {'x': math.log(2)/math.log(1.2)}}}))
                    options = launch_options(); options.update(headless=False, no_viewport=True, args=['--window-size=1440,1000'], service_workers='block', reduced_motion='reduce')
                    context = pw.chromium.launch_persistent_context(str(profile), **options)
                    try:
                        page, observed = prepare(context, prefix + 'index.html', theme)
                        assert page.evaluate('Math.abs(outerWidth/innerWidth-2)<0.01 && getComputedStyle(document.documentElement).zoom==="1"'), 'Native 200% was not established'
                        structure(page)
                        before = snapshot(page)
                        movement(page)
                        contained(page)
                        unchanged(page, before, 'native-200')
                        assert_clean(context, observed)
                        report['checks'].append({'name': 'native-200/' + theme, 'result': 'PASS'})
                    except Exception as error:
                        report['checks'].append({'name': 'native-200/' + theme, 'result': 'PRODUCT_FAIL' if isinstance(error, AssertionError) else 'TEST_HARNESS_FAIL', 'detail': str(error)})
                        failed = True
                    finally:
                        context.close()
            browser.close()
    except Exception as error:
        failed = True
        report['checks'].append({'name': 'runtime execution', 'result': 'ENVIRONMENT_ERROR', 'detail': str(error)})
    finally:
        server.shutdown();server.server_close()
        report['inputs_after'] = hashes(args.root)
        report['source_unchanged'] = report['inputs_before'] == report['inputs_after']
        if not report['source_unchanged']:
            report['checks'].append({'name': 'candidate changed during execution', 'result': 'TEST_HARNESS_FAIL'})
            failed = True
        report['finished_at'] = datetime.now(timezone.utc).isoformat()
        results = {row['result'] for row in report['checks']}
        report['result'] = ('BASELINE_FAIL' if args.baseline and results == {'BASELINE_FAIL'} else
            'ENVIRONMENT_ERROR' if 'ENVIRONMENT_ERROR' in results else
            'TEST_HARNESS_FAIL' if 'TEST_HARNESS_FAIL' in results else 'PRODUCT_FAIL' if failed else 'PASS')
        args.out.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
        print(json.dumps({'result': report['result'], 'checks': report['checks'], 'report': str(args.out)}, ensure_ascii=False), flush=True)
    return 1 if failed else 0


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=ROOT)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--artifact', choices=('source', 'portable', 'both'), default='both')
    parser.add_argument('--baseline', action='store_true')
    parser.add_argument('--native-zoom', action='store_true')
    args = parser.parse_args()
    args.root = args.root.resolve();args.out = args.out.resolve();args.out.parent.mkdir(parents=True, exist_ok=True)
    if args.out.exists():
        parser.error('Choose a new output path; prior evidence is never overwritten.')
    raise SystemExit(run(args))
