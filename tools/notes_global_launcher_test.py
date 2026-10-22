#!/usr/bin/env python3
"""Global Notes contract from CHG-JPW-PLANNING-THREE-TABS-20261020.

Real Chromium DOM, isolated synthetic contexts and the existing bootstrap fixture.
Opening, cancelling and projecting UI must preserve all persisted bytes. Native
dialog probes exercise browser lifecycle boundaries, not financial commands.
"""
import argparse
from datetime import datetime, timezone
from functools import partial
import hashlib
import json
from pathlib import Path
import threading
import traceback

from playwright.sync_api import expect, sync_playwright
from browser_fixture_server import BrowserFixtureServer
from notes_launcher_test import (Quiet, assert_clean, contained, geometry,
    launch_options, prepare, same_position, settle, snapshot, unchanged)

ROOT = Path(__file__).resolve().parents[1]
SOURCES = ('src/js/40-app/14-mvp-notes.js', 'src/styles/app.css',
           'tools/notes_global_launcher_test.py', 'tools/notes_launcher_test.py',
           'tools/browser_fixture_server.py', 'tools/browser_bootstrap_fixture.py')
FOREX_ROUTES = ('forex-consolidated', 'forex-management-accounts',
                'forex-operation', 'forex-history', 'forex-accounting', 'forex-reserves')


def hashes(root):
    return {name: hashlib.sha256((root / name).read_bytes()).hexdigest() for name in SOURCES}


def go(page, route):
    assert page.evaluate('r=>JPWNavigation.navigate(r)', route), route
    settle(page)


def hidden(page, label):
    expect(page.locator('#mvpNotesLauncher'), label).to_be_hidden()
    expect(page.locator('#headerNotesBtn'), label).to_be_hidden()


def global_matrix(page):
    # Availability changes are explicit synthetic setup, outside the no-write boundary.
    page.evaluate("() => {for(const id of ['personal-finance','alladin','forex']){const r=JPWModuleAvailability.setState(id,'active');if(!r.ok)throw Error(JSON.stringify(r));}}")
    page.evaluate("() => {mvpNotesUI.launcherPosition={x:.63,y:.71};mvpNotesPlaceLauncher();}")
    before = snapshot(page)
    rows = []
    routes = ('dashboard', 'research-forex', 'planning', 'personal-finance', 'alladin', 'tools') + FOREX_ROUTES
    for layout in ('sidebar', 'topbar', 'submenu', 'glass'):
        page.evaluate('x=>mountNavigationLayout(x)', layout)
        for width in (1440, 390):
            page.set_viewport_size({'width': width, 'height': 1000 if width == 1440 else 844})
            for theme in ('light', 'dark'):
                page.evaluate('t=>document.documentElement.dataset.theme=t', theme)
                for route in routes:
                    go(page, route)
                    expect(page.locator('#headerNotesBtn'), f'{layout}/{width}/{theme}/{route}').to_be_visible()
                    contained(page)
                    rows.append({'layout': layout, 'width': width, 'theme': theme, 'route': route})
    unchanged(page, before, 'global Notes route/layout/theme projections')
    assert page.evaluate('mvpNotesUI.launcherPosition') == {'x': .63, 'y': .71}
    return {'visits': len(rows), 'matrix': rows, 'noWrites': True}


def planning_native(page):
    go(page, 'planning')
    opener = page.locator('#planning [data-pl-start] [data-pl-action="configure"]')
    before = snapshot(page)
    rows = []
    for layout in ('sidebar', 'topbar', 'submenu', 'glass'):
        page.evaluate('x=>mountNavigationLayout(x)', layout)
        for width in (1440, 390):
            page.set_viewport_size({'width': width, 'height': 1000 if width == 1440 else 844})
            for theme in ('light', 'dark'):
                page.evaluate('t=>document.documentElement.dataset.theme=t', theme)
                settle(page)
                position = geometry(page)
                for close_parent in ('cancel', 'escape'):
                    opener.click()
                    expect(page.locator('.pl-dialog[open]')).to_be_visible()
                    hidden(page, 'Planning native account dialog')
                    page.locator('#pl-native-openProfiles').click()
                    expect(page.locator('#pl-native-profileDialog[open]')).to_be_visible()
                    hidden(page, 'nested Planning native profile dialog')
                    page.locator('#pl-native-closeProfiles').click()
                    expect(page.locator('#pl-native-openProfiles')).to_be_focused()
                    hidden(page, 'parent remains open after nested button close')
                    page.locator('#pl-native-openProfiles').click()
                    page.keyboard.press('Escape')
                    expect(page.locator('#pl-native-profileDialog')).to_have_count(0)
                    expect(page.locator('#pl-native-openProfiles')).to_be_focused()
                    hidden(page, 'parent remains open after nested Escape')
                    if close_parent == 'cancel':
                        page.locator('.pl-dialog [data-pl-action="close"]').last.click()
                    else:
                        page.keyboard.press('Escape')
                    expect(page.locator('.pl-dialog')).to_have_count(0)
                    expect(page.locator('#headerNotesBtn')).to_be_visible()
                    expect(opener).to_be_focused()
                    same_position(position, geometry(page))
                    rows.append({'layout': layout, 'width': width, 'theme': theme, 'parentClose': close_parent})
    unchanged(page, before, 'native Planning open/close, nested profiles, Escape and focus')
    return {'matrix': rows, 'nestedClosures': ['button', 'Escape'], 'parentClosures': ['cancel', 'Escape'], 'noWrites': True}


def native_lifecycle(page):
    go(page, 'dashboard')
    page.locator('#headerConfigBtn').focus()
    before = snapshot(page)
    position = geometry(page)
    page.evaluate("""() => {
      const wrap=document.createElement('section');wrap.id='notesProbeWrap';
      wrap.innerHTML='<dialog id="notesProbeDialog"><form method="dialog"><button id="notesProbeConfirm" value="confirm">Confirmar</button></form></dialog>';
      document.body.append(wrap);
    }""")
    settle(page)
    expect(page.locator('#headerNotesBtn')).to_be_visible()
    # Existing dialog: relevant open-attribute change, then native form confirmation.
    page.evaluate("document.querySelector('#notesProbeDialog').showModal()")
    hidden(page, 'existing native dialog opened')
    page.locator('#notesProbeConfirm').click()
    expect(page.locator('#notesProbeDialog')).not_to_have_attribute('open', '')
    expect(page.locator('#headerNotesBtn')).to_be_visible()
    expect(page.locator('#headerConfigBtn')).to_be_focused()
    # Mount already-open nested dialogs; removing only the inner one stays covered.
    page.evaluate("""() => {
      const d=document.querySelector('#notesProbeDialog');d.showModal();
      const nested=document.createElement('dialog');nested.id='notesProbeNested';
      nested.innerHTML='<button autofocus>Fechar</button>';d.append(nested);nested.showModal();
    }""")
    hidden(page, 'dynamically mounted nested native dialog')
    page.evaluate("document.querySelector('#notesProbeNested').remove()")
    hidden(page, 'outer native dialog remains open after nested removal')
    page.evaluate("document.querySelector('#notesProbeWrap').remove()")
    expect(page.locator('#headerNotesBtn')).to_be_visible()
    same_position(position, geometry(page))
    # A dialog can be mounted with open already set; close/remove must restore Notes.
    page.evaluate("""() => {const d=document.createElement('dialog');d.id='notesOpenProbe';d.open=true;document.body.append(d);}""")
    hidden(page, 'mounted dialog with existing open attribute')
    page.evaluate("document.querySelector('#notesOpenProbe').open=false")
    expect(page.locator('#headerNotesBtn')).to_be_visible()
    page.evaluate("document.querySelector('#notesOpenProbe').remove()")
    unchanged(page, before, 'native open/confirmation/removal lifecycle')
    return {'nativeConfirm': True, 'dynamicNestedRemoval': True, 'alreadyOpenMount': True, 'noWrites': True}


def visibility_and_shortcuts(page):
    go(page, 'forex-operation')
    expect(page.locator('#headerNotesBtn')).to_be_visible()
    before = snapshot(page)
    page.locator('#forexNotesToggle').click()
    expect(page.locator('#mvpNotesOverlay')).to_be_visible()
    hidden(page, 'Notes drawer opened from Forex internal shortcut')
    page.locator('#mvpNotesCloseBtn').click()
    expect(page.locator('#forexNotesToggle')).to_be_focused()
    expect(page.locator('#headerNotesBtn')).to_be_visible()
    unchanged(page, before, 'Forex shortcut and focus')
    page.locator('#headerConfigBtn').click()
    page.evaluate("settingsNavigateToLeaf('interface')")
    page.locator('[data-mvp-notes-visibility="hide"]').click()
    page.locator('#settingsCloseBtn').click()
    assert page.evaluate('S.mvpNotes.showHeaderIcon') is False
    before = snapshot(page)
    for route in ('planning', 'forex-consolidated', 'forex-operation', 'dashboard'):
        go(page, route)
        hidden(page, 'explicit hide preference on ' + route)
    page.locator('#headerConfigBtn').click()
    page.locator('#settingsCloseBtn').click()
    hidden(page, 'hide preference survives overlay restoration')
    unchanged(page, before, 'hidden preference route and modal projections')
    return {'internalForexShortcut': True, 'focusReturned': True, 'hidePreferencePreserved': True}


def observer_finalization(page):
    before = snapshot(page)
    # Queue a relevant DOM mutation, invalidate the old controller through the
    # actual finalization surface hook, then flush the queued browser callbacks.
    page.evaluate("""() => {
      window.__notesSyncCalls=0;const hidden=Object.getOwnPropertyDescriptor(HTMLElement.prototype,'hidden');
      Object.defineProperty(document.querySelector('#mvpNotesLauncher'),'hidden',{
        get(){return hidden.get.call(this);},set(value){window.__notesSyncCalls++;hidden.set.call(this,value);}
      });
      const d=document.createElement('dialog');d.id='notesWipeProbe';document.body.append(d);d.showModal();
      document.querySelector('#modalOverlay').classList.add('show');
      handleMvpNotesLauncherSessionWipe();window.__notesSyncCalls=0;
    }""")
    settle(page)
    assert page.evaluate('window.__notesSyncCalls') == 0, 'Cancelled launcher observers ran after finalization'
    page.evaluate("document.querySelector('#notesWipeProbe').remove()")
    page.evaluate("document.querySelector('#modalOverlay').classList.remove('show')")
    settle(page)
    assert page.evaluate('window.__notesSyncCalls') == 0, 'Detached native dialog revived old launcher observers'
    # The regular header render establishes a fresh observer controller.
    page.evaluate('renderMvpNotesHeader()')
    expect(page.locator('#headerNotesBtn')).to_be_visible()
    page.locator('#headerConfigBtn').click()
    hidden(page, 'new controller after finalization observes settings')
    page.locator('#settingsCloseBtn').click()
    expect(page.locator('#headerNotesBtn')).to_be_visible()
    page.evaluate("() => {const d=document.createElement('dialog');d.id='notesFreshObserver';document.body.append(d);d.showModal();}")
    hidden(page, 'fresh controller observes newly mounted native dialogs')
    page.evaluate("document.querySelector('#notesFreshObserver').remove()")
    expect(page.locator('#headerNotesBtn')).to_be_visible()
    unchanged(page, before, 'observer invalidation does not persist anything')
    return {'oldCallbacksCancelled': True, 'freshControllerOnRender': True, 'noWrites': True}


def keyboard_observation(page):
    go(page, 'dashboard')
    page.evaluate("""() => {
      const input=document.createElement('input');input.id='notesTypingProbe';document.body.append(input);
      window.__notesDocumentScans=[];window.__notesTypingSyncs=0;
      for(const method of ['querySelector','querySelectorAll']){
        const original=document[method];document[method]=function(selector,...args){
          if(String(selector).includes('dialog') && /mvpNotes/.test(new Error().stack))window.__notesDocumentScans.push({method,selector});
          return original.call(this,selector,...args);
        };
      }
      const sync=mvpNotesSyncLauncher;mvpNotesSyncLauncher=function(){window.__notesTypingSyncs++;return sync();};
    }""")
    settle(page)
    before = snapshot(page)
    page.locator('#notesTypingProbe').press_sequentially('Synthetic text 123')
    settle(page)
    assert page.evaluate('window.__notesDocumentScans') == [], 'Typing repeatedly scanned the document for native dialogs'
    assert page.evaluate('window.__notesTypingSyncs') == 0, 'Ordinary typing repeatedly recomputed Notes modal coverage'
    page.evaluate("() => {const d=document.createElement('dialog');d.id='notesTypingModal';document.body.append(d);d.showModal();}")
    hidden(page, 'the observer remains responsive after ordinary typing')
    assert page.evaluate('window.__notesTypingSyncs') > 0, 'Observer instrumentation did not observe the real controller'
    page.evaluate("document.querySelector('#notesTypingModal').remove();document.querySelector('#notesTypingProbe').remove()")
    expect(page.locator('#headerNotesBtn')).to_be_visible()
    unchanged(page, before, 'ordinary typing and modal observation')
    return {'typingScans': 0, 'typingSyncs': 0, 'modalSyncObserved': True, 'noWrites': True}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--root', type=Path, default=ROOT)
    ap.add_argument('--out', type=Path, required=True)
    ap.add_argument('--cases')
    args = ap.parse_args()
    args.root = args.root.resolve(); args.out = args.out.resolve()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    if args.out.exists():
        ap.error('Choose a fresh output path; prior evidence is preserved.')
    tests = {'global-matrix': global_matrix, 'planning-native': planning_native,
             'native-lifecycle': native_lifecycle, 'visibility-shortcuts': visibility_and_shortcuts,
             'observer-finalization': observer_finalization, 'keyboard-observation': keyboard_observation}
    selected = args.cases.split(',') if args.cases else list(tests)
    if not selected or any(name not in tests for name in selected):
        ap.error('Unknown or empty case selection')
    report = {'startedAt': datetime.now(timezone.utc).isoformat(), 'inputsBefore': hashes(args.root),
              'checks': [], 'limits': ['Synthetic Chromium contexts; no human acceptance, Safari or physical touch evidence.']}
    server = BrowserFixtureServer(('127.0.0.1', 0), partial(Quiet, directory=str(args.root)))
    threading.Thread(target=server.serve_forever, daemon=True).start()
    try:
        with sync_playwright() as pw:
            browser = pw.chromium.launch(**launch_options())
            for name in selected:
                context = browser.new_context(viewport={'width': 1440, 'height': 1000},
                    service_workers='block', reduced_motion='reduce')
                page = None
                try:
                    page, observed = prepare(context, f'http://127.0.0.1:{server.server_port}/index.html')
                    evidence = tests[name](page)
                    assert_clean(context, observed)
                    report['checks'].append({'name': name, 'result': 'PASS', 'evidence': evidence})
                except Exception as error:
                    report['checks'].append({'name': name, 'result': 'PRODUCT_FAIL', 'detail': str(error), 'trace': traceback.format_exc()})
                    if page:
                        page.screenshot(path=str(args.out.with_name(args.out.stem + '-' + name + '-failure.png')))
                finally:
                    context.close()
            browser.close()
    except Exception as error:
        report['checks'].append({'name': 'runtime', 'result': 'ENVIRONMENT_ERROR', 'detail': str(error)})
    finally:
        server.shutdown(); server.server_close()
        report['inputsAfter'] = hashes(args.root)
        report['sameBytes'] = report['inputsBefore'] == report['inputsAfter']
        if not report['sameBytes']:
            report['checks'].append({'name': 'candidate changed', 'result': 'TEST_HARNESS_FAIL'})
        results = {row['result'] for row in report['checks']}
        report['result'] = next((result for result in ('ENVIRONMENT_ERROR', 'TEST_HARNESS_FAIL', 'PRODUCT_FAIL') if result in results), 'PASS')
        report['finishedAt'] = datetime.now(timezone.utc).isoformat()
        args.out.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
        print(json.dumps({'result': report['result'], 'checks': [{k: v for k, v in r.items() if k not in ('evidence', 'trace')} for r in report['checks']], 'report': str(args.out)}, ensure_ascii=False))
    return 0 if report['result'] == 'PASS' else 1


if __name__ == '__main__':
    raise SystemExit(main())
