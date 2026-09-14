#!/usr/bin/env python3
"""Apple Notes presentation and explicit local appearance preferences.

Oracles fixed before the product patch in CHG-APPLE-NOTES-MATCH-20260914.
Uses only an isolated loopback origin and the target's nominal bootstrap/SEED.
--baseline preserves missing-interface failures as BASELINE_FAIL and exits 1.
--native-zoom uses the established disposable Chromium profile at real 200%.
"""
import argparse
from datetime import datetime, timezone
from functools import partial
import hashlib
from http.server import ThreadingHTTPServer
import importlib.util
import json
import math
from pathlib import Path
import sys
import tempfile
import threading

from playwright.sync_api import sync_playwright, expect, TimeoutError as PlaywrightTimeout

ROOT = Path(__file__).resolve().parents[1]
KEY = 'jpwealth_notes_appearance_v1'
POSITION_KEY = 'jpwealth_notes_launcher_position_v1'
DEFAULT = dict(theme='app', density='comfortable', preview='show', sidebar='show',
               reading='full', text='standard')
CHOICES = dict(theme=('app', 'light', 'dark'), density=('comfortable', 'compact'),
               preview=('show', 'hide'), sidebar=('show', 'hide'),
               reading=('full', 'comfortable'), text=('standard', 'large', 'larger'))
SOURCE_FILES = ('index.html', 'src/styles/app.css', 'src/js/40-app/14-mvp-notes.js',
                'src/js/40-app/09-settings-modal.js', 'src/js/40-app/07-finalize-session.js',
                'src/js/manifest.json', 'build-id.js',
                'dist/JP_Wealth_Risk_Terminal_V9.1_PORTABLE.html')
launcher = experience = finalizer = None


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def hashes(root):
    return {name: digest(root / name) for name in SOURCE_FILES if (root / name).exists()}


def load_helpers(root):
    global launcher, experience, finalizer
    # Imports inside either helper must resolve to the target, not the candidate
    # beside this newly written focal when --root points at frozen baseline.
    sys.path.insert(0, str(root / 'tools'))
    for name in ('notes_launcher_test', 'notes_experience_test', 'finalize_session_test'):
        spec = importlib.util.spec_from_file_location(name, root / 'tools' / (name + '.py'))
        module = importlib.util.module_from_spec(spec)
        sys.modules[name] = module
        spec.loader.exec_module(module)
        if name == 'notes_launcher_test':
            launcher = module
        elif name == 'notes_experience_test':
            experience = module
        else:
            finalizer = module
    experience.launcher = launcher


def control(field):
    return '#mvpNotesAppearance' + field.title()


def raw(page):
    return page.evaluate('(key)=>localStorage.getItem(key)', KEY)


def state(page):
    return page.evaluate('JSON.parse(JSON.stringify(mvpNotesAppearanceState))')


def snapshot(page):
    return launcher.snapshot(page)


def assert_unchanged(page, before, label):
    launcher.unchanged(page, before, label)


def assert_only_appearance(page, before, label, expected_writes=None):
    after = snapshot(page)
    a, b = json.loads(before['local']), json.loads(after['local'])
    a.pop(KEY, None); b.pop(KEY, None)
    assert a == b, (label, 'changed another localStorage key', experience.concrete_diff(a, b))
    assert before['state'] == after['state'], (label, 'changed S')
    assert before['session'] == after['session'], (label, 'changed sessionStorage')
    changes = page.evaluate('window.__notesLauncherWrites')[before['writes']:]
    assert all(x['area'] == 'local' and x['key'] == KEY and x['method'] == 'setItem'
               for x in changes), (label, changes)
    if expected_writes is not None:
        assert len(changes) == expected_writes, (label, changes, expected_writes)


def settings(page):
    if not page.locator('#settingsOverlay').is_visible():
        page.locator('#headerConfigBtn').click()
    page.evaluate("settingsNavigateToLeaf('interface')")
    for field, choices in CHOICES.items():
        element = page.locator(control(field))
        assert element.count() == 1, 'Missing unique appearance control: ' + field
        expect(element).to_be_visible()
        assert element.locator('option').evaluate_all('(xs)=>xs.map(x=>x.value)') == list(choices), field
    for ident in ('Save', 'Cancel', 'Reset', 'Reload'):
        assert page.locator('#mvpNotesAppearance' + ident).count() == 1, ident


def choose(page, **values):
    for field, value in values.items():
        page.locator(control(field)).select_option(value)
    launcher.settle(page)


def saved(page):
    page.locator('#mvpNotesAppearanceSave').click()
    page.wait_for_function('!mvpNotesAppearanceState.saving')
    assert not state(page)['blocked'], state(page)
    payload = json.loads(raw(page))
    assert payload['schemaVersion'] == 1
    assert state(page)['confirmed'] == state(page)['draft'], state(page)
    for field in DEFAULT:
        assert payload[field] == state(page)['confirmed'][field], (field, payload, state(page))
    return payload


def reload_page(page):
    page.reload(wait_until='load')
    launcher.wait_bootstrap(page)
    page.evaluate('window.__onbShown=true;closeModal();window.alert=()=>{};window.confirm=()=>false;window.prompt=()=>null;')
    launcher.settle(page)
    launcher.instrument(page)


def boot_raw(page, value):
    page.evaluate('({key,value})=>value===null?localStorage.removeItem(key):localStorage.setItem(key,value)',
                  dict(key=KEY, value=value))
    reload_page(page)


def appearance_attrs(page):
    return page.locator('#mvpNotesDrawer').evaluate("""e=>Object.fromEntries(
      ['theme','density','preview','sidebar','reading','text'].map(k=>[k,e.getAttribute('data-notes-'+k)]))""")


def open_from_settings(page):
    page.locator('#mvpNotesOpenFromSettingsBtn').click()
    expect(page.locator('#mvpNotesCloseBtn')).to_be_focused()
    assert page.locator('#settingsModal').evaluate('e=>e.inert')


def close_notes(page):
    page.locator('#mvpNotesCloseBtn').click()
    expect(page.locator('#mvpNotesOverlay')).not_to_be_visible()


def anatomy(page):
    settings(page)
    assert raw(page) is None, 'Opening appearance created a preference'
    open_from_settings(page)
    g = experience.usable(page)
    assert experience.visible_panes(page) == list(experience.PANES), g
    folders, notes, editor = g['panes']
    assert editor['width'] > notes['width'] > folders['width'], g
    # Settings deliberately reserves a stable scrollbar gutter on html. A fixed
    # inset:0 overlay then measures 1425px at innerWidth=1440 in Chromium. The
    # window must center in its actual containing overlay; experience.usable()
    # independently keeps it inside the viewport. Computed-style proof and a
    # rejected +12px displacement: evidence/anatomy-gutter-probe-v2.json.
    overlay = page.locator('#mvpNotesOverlay').evaluate("""e=>{const r=e.getBoundingClientRect();
      return {x:r.x,y:r.y,right:r.right,bottom:r.bottom,width:r.width,height:r.height};}""")
    window = g['window']
    assert abs((window['x']-overlay['x'])-(overlay['right']-window['right'])) <= 2, (g, overlay)
    assert abs((window['y']-overlay['y'])-(overlay['bottom']-window['bottom'])) <= 2, (g, overlay)
    assert min(window['x']-overlay['x'],overlay['right']-window['right'],
               window['y']-overlay['y'],overlay['bottom']-window['bottom']) >= 12, (g, overlay)
    heads = page.locator('.mvpn-head-folders,.mvpn-head-list,.mvpn-head-editor')
    assert heads.count() == 3, 'Three contextual toolbar zones are required'
    geometry = heads.evaluate_all("""xs=>xs.map(e=>{const r=e.getBoundingClientRect();
      return {x:r.x,right:r.right,y:r.y,h:r.height,w:r.width};})""")
    for pane, head in zip(g['panes'], geometry):
        assert abs(pane['x']-head['x']) <= 8 and abs(pane['right']-head['right']) <= 8, (g, geometry)
        assert 44 <= head['h'] <= 72, geometry
    assert max(x['y'] for x in geometry)-min(x['y'] for x in geometry) <= 2, geometry
    for ident in ('mvpNotesOverlay', 'mvpNotesDrawer', 'mvpNoteContent', 'mvpNotesFolderNavList'):
        assert page.locator('#'+ident).count() == 1, ident
    assert appearance_attrs(page) == {**DEFAULT, 'theme':page.evaluate('document.documentElement.dataset.theme')}
    return dict(geometry=g, overlay=overlay, headers=geometry)


def responsive(page):
    settings(page)
    choose(page, sidebar='hide', text='larger', reading='comfortable')
    page.locator('#mvpNotesAppearanceCancel').click()
    page.locator('#settingsCloseBtn').click()
    result = experience.responsive(page)
    # Every size uses the existing real stages, save and long-text editor path.
    assert page.locator('#mvpNoteContent').count() == 1
    assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1')
    return result


def preview_preserves_editor(page):
    settings(page)
    open_from_settings(page)
    experience.select_first(page)
    page.locator('#mvpNoteContent').fill(experience.LONG_BODY)
    page.locator('#mvpNoteContent').evaluate('e=>{e.focus();e.setSelectionRange(18,37);e.scrollTop=130;}')
    before = experience.draft_snapshot(page); stored = snapshot(page)
    page.evaluate('window.__matchEditor=document.getElementById("mvpNoteContent")')
    # Settings is legitimately inert under Notes. This is a direct projection
    # contract probe, not a claim that a user can click the covered settings UI.
    for field, value in (('preview','hide'), ('density','compact'), ('theme','dark'), ('preview','show')):
        page.locator(control(field)).evaluate("""(e,v)=>{e.value=v;e.dispatchEvent(new Event('change',{bubbles:true}));}""", value)
        launcher.settle(page)
        experience.assert_draft(page, before)
        assert page.evaluate('window.__matchEditor===document.getElementById("mvpNoteContent")')
        assert appearance_attrs(page)[field] == value
    assert_unchanged(page, stored, 'appearance projection preserves storage and draft')
    return dict(probe='direct change dispatch to covered Settings controls', draft_preserved=True)


def no_write_cancel_navigation(page):
    before = snapshot(page)
    settings(page)
    choose(page, theme='dark', density='compact', preview='hide', sidebar='hide', reading='comfortable', text='larger')
    assert state(page)['draft'] != state(page)['confirmed']
    page.locator('#mvpNotesAppearanceCancel').click()
    assert state(page)['draft'] == state(page)['confirmed']
    assert_unchanged(page, before, 'cancel')
    choose(page, density='compact')
    page.evaluate("settingsNavigateToLeaf('appearance')")
    settings(page)
    assert state(page)['draft'] == state(page)['confirmed'], 'Leaving Notes appearance retained unsaved preview'
    choose(page, preview='hide')
    page.locator('#settingsCloseBtn').click()
    settings(page)
    assert state(page)['draft'] == state(page)['confirmed'], 'Closing Settings retained unsaved preview'
    assert_unchanged(page, before, 'opening, preview, navigation and closing')


def save_reload(page):
    settings(page); before = snapshot(page)
    choose(page, theme='dark', density='compact', preview='hide', sidebar='hide', reading='comfortable', text='large')
    payload = saved(page)
    assert_only_appearance(page, before, 'explicit appearance save', 1)
    before = snapshot(page)
    reload_page(page)
    after = snapshot(page)
    assert before['state'] == after['state'] and before['local'] == after['local'] and before['session'] == after['session'], 'Reload changed saved data'
    settings(page)
    for field in DEFAULT:
        expect(page.locator(control(field))).to_have_value(payload[field])
    open_from_settings(page)
    assert appearance_attrs(page) == {key:payload[key] for key in DEFAULT}
    assert not experience.visible(page, 'mvpNotesFolderSidebar')
    return payload


def theme_override(page):
    settings(page); before = snapshot(page)
    for app_theme, local_theme, expected in (('dark','light','light'), ('light','dark','dark'),
                                            ('dark','app','dark'), ('light','app','light')):
        page.evaluate('t=>document.documentElement.dataset.theme=t', app_theme)
        choose(page, theme=local_theme)
        open_from_settings(page)
        assert appearance_attrs(page)['theme'] == expected
        assert page.evaluate('document.documentElement.dataset.theme') == app_theme
        color = page.locator('#mvpNotesEditorPane').evaluate('e=>getComputedStyle(e).backgroundColor')
        assert color not in ('rgba(0, 0, 0, 0)', 'transparent'), ('Editor must provide its own readable surface', expected, color)
        close_notes(page)
    assert_unchanged(page, before, 'crossed appearance themes')


def display_choices(page):
    page.evaluate('mvpNotesPersistDrawerWidth(1600)')
    settings(page); open_from_settings(page); experience.select_first(page)
    page.locator('#mvpNoteContent').fill(experience.LONG_BODY)
    stored = snapshot(page)
    sizes = []
    for value in CHOICES['text']:
        page.locator(control('text')).evaluate('(e,v)=>{e.value=v;e.dispatchEvent(new Event("change",{bubbles:true}));}', value)
        launcher.settle(page)
        sizes.append(page.locator('#mvpNoteContent').evaluate('e=>parseFloat(getComputedStyle(e).fontSize)'))
    assert sizes[0] < sizes[1] < sizes[2] <= 28, sizes
    row = page.locator('.mvpn-card').first
    comfortable = row.bounding_box()['height']
    page.locator(control('density')).evaluate('e=>{e.value="compact";e.dispatchEvent(new Event("change",{bubbles:true}));}')
    launcher.settle(page)
    compact = row.bounding_box()['height']
    assert 44 <= compact < comfortable, (comfortable, compact)
    page.locator(control('preview')).evaluate('e=>{e.value="hide";e.dispatchEvent(new Event("change",{bubbles:true}));}')
    assert page.locator('.mvpn-card-preview:visible').count() == 0
    page.locator(control('preview')).evaluate('e=>{e.value="show";e.dispatchEvent(new Event("change",{bubbles:true}));}')
    assert page.locator('.mvpn-card-preview:visible').count() > 0
    # Reading measure may be padding or width. Compare the actual writable box.
    writable = "e=>{const s=getComputedStyle(e);return e.clientWidth-parseFloat(s.paddingLeft)-parseFloat(s.paddingRight);}"
    full = page.locator('#mvpNoteContent').evaluate(writable)
    page.locator(control('reading')).evaluate('e=>{e.value="comfortable";e.dispatchEvent(new Event("change",{bubbles:true}));}')
    launcher.settle(page)
    measured = page.locator('#mvpNoteContent').evaluate(writable)
    assert 240 <= measured <= full, (full, measured)
    if full >= 900:
        assert measured < full, 'Comfortable reading must constrain a genuinely wide editor'
    assert page.locator('#mvpNoteContent').input_value() == experience.LONG_BODY
    assert_unchanged(page, stored, 'text/density/preview/reading are unsaved presentation')
    return dict(text_sizes=sizes, rows=[comfortable,compact], reading=[full,measured])


def sidebar_toggle(page):
    settings(page); choose(page, sidebar='hide'); saved(page)
    open_from_settings(page)
    before = snapshot(page)
    assert not experience.visible(page, 'mvpNotesFolderSidebar')
    expect(page.locator('#mvpNotesSidebarToggleBtn')).to_be_visible()
    page.locator('#mvpNotesSidebarToggleBtn').click()
    assert experience.visible(page, 'mvpNotesFolderSidebar')
    page.locator('#mvpNotesSidebarToggleBtn').click()
    assert not experience.visible(page, 'mvpNotesFolderSidebar')
    assert_unchanged(page, before, 'temporary sidebar toggle')
    page.set_viewport_size(dict(width=390,height=900)); launcher.settle(page)
    assert page.locator('#mvpNotesBackBtn').is_visible() or experience.visible(page, 'mvpNotesFolderSidebar')
    page.set_viewport_size(dict(width=1440,height=900)); launcher.settle(page)
    assert json.loads(raw(page))['sidebar'] == 'hide'
    assert_unchanged(page, before, 'sidebar viewport changes')


FAULT = """key=>{
  const get=Storage.prototype.getItem,set=Storage.prototype.setItem;
  const f={mode:'normal',unreadable:false,attempts:[],raw:()=>get.call(localStorage,key)};
  window.__matchFault=f;
  Storage.prototype.getItem=function(k){
    if(this===localStorage&&k===key&&f.unreadable)throw new DOMException('Synthetic read failure','SecurityError');
    return get.call(this,k);
  };
  Storage.prototype.setItem=function(k,v){
    if(this===localStorage&&k===key){
      f.attempts.push(v);
      if(f.mode==='quota')throw new DOMException('Synthetic refusal','QuotaExceededError');
      if(f.mode==='noop')return;
      const out=set.call(this,k,v);if(f.mode==='unknown')f.unreadable=true;return out;
    }
    return set.call(this,k,v);
  };
}"""


def fault_state(page):
    return page.evaluate('({raw:__matchFault.raw(),attempts:[...__matchFault.attempts],state:JSON.parse(JSON.stringify(mvpNotesAppearanceState))})')


def refused_retry(page):
    settings(page); page.evaluate(FAULT, KEY)
    for mode, density in (('quota','compact'), ('noop','comfortable')):
        choose(page, density=density)
        before = fault_state(page); stored = snapshot(page)
        page.evaluate('m=>__matchFault.mode=m', mode)
        page.locator('#mvpNotesAppearanceSave').click(); page.wait_for_function('!mvpNotesAppearanceState.saving')
        after = fault_state(page)
        assert after['raw'] == before['raw'] and after['state']['confirmed'] == before['state']['confirmed'], after
        assert after['state']['draft'] == before['state']['draft'], after
        assert len(after['attempts']) == len(before['attempts'])+1, after
        expect(page.locator('#mvpNotesAppearanceSave')).to_be_enabled()
        # The rejected boundary deliberately prevents the instrumentation wrapper
        # from receiving this call; the independent attempt counter proves it ran.
        assert_unchanged(page, stored, 'refused appearance '+mode)
        page.evaluate('__matchFault.mode="normal"')
        saved(page)
        assert len(fault_state(page)['attempts']) == len(before['attempts'])+2
        assert_only_appearance(page, stored, 'one explicit retry', 1)


def unknown_block(page):
    settings(page); page.evaluate(FAULT, KEY)
    choose(page, density='compact')
    confirmed = state(page)['confirmed']
    page.evaluate('__matchFault.mode="unknown"')
    page.locator('#mvpNotesAppearanceSave').click(); page.wait_for_function('!mvpNotesAppearanceState.saving')
    after = fault_state(page)
    assert after['state']['blocked'] and after['state'].get('reason') == 'unknown' and after['state']['confirmed'] == confirmed, after
    assert after['state']['draft']['density'] == 'compact' and len(after['attempts']) == 1, after
    expect(page.locator('#mvpNotesAppearanceSave')).to_be_disabled()
    page.evaluate('mvpNotesSaveAppearance();mvpNotesCancelAppearance()')
    assert len(fault_state(page)['attempts']) == 1
    assert state(page)['blocked'] and state(page).get('reason') == 'unknown'
    page.evaluate('__matchFault.unreadable=false;__matchFault.mode="normal"')
    # Navigation is not the explicitly requested readback/recovery action.
    # Restoring the read boundary here makes an accidental implicit reload visible.
    page.evaluate("settingsNavigateToLeaf('appearance')")
    settings(page)
    assert state(page)['blocked'] and state(page).get('reason') == 'unknown', 'Returning to Interface silently cleared UNKNOWN'
    assert state(page)['confirmed'] == confirmed, 'Navigation announced the uncertain candidate as confirmed'
    assert len(fault_state(page)['attempts']) == 1
    page.locator('#mvpNotesAppearanceReload').click()
    assert not state(page)['blocked']
    assert state(page)['confirmed']['density'] == 'compact'
    assert len(fault_state(page)['attempts']) == 1, 'Explicit reread wrote instead of reading'


def invalid_raw(page):
    examples = ('{synthetic-invalid', json.dumps(dict(schemaVersion=999, **DEFAULT)),
                json.dumps(dict(schemaVersion=1, **{**DEFAULT,'density':'unknown-density'})))
    for value in examples:
        boot_raw(page, value); before = snapshot(page); settings(page)
        assert raw(page) == value
        assert state(page)['blocked'], 'Incompatible preference must not silently normalize to a writable state'
        expect(page.locator('#mvpNotesAppearanceSave')).to_be_disabled()
        page.locator('#mvpNotesAppearanceReload').click()
        assert raw(page) == value
        assert_unchanged(page, before, 'incompatible appearance remains intact')


def unreadable_raw(page):
    settings(page); page.evaluate(FAULT, KEY)
    page.evaluate('__matchFault.unreadable=true')
    page.locator('#mvpNotesAppearanceReload').click()
    assert state(page)['blocked'], state(page)
    expect(page.locator('#mvpNotesAppearanceSave')).to_be_disabled()
    page.evaluate('mvpNotesSaveAppearance()')
    assert not fault_state(page)['attempts']
    page.evaluate('__matchFault.unreadable=false')
    page.locator('#mvpNotesAppearanceReload').click()
    assert not state(page)['blocked']


def extensions(page):
    envelope = dict(schemaVersion=1, **DEFAULT, futurePresentation=dict(marker='synthetic-preserved',number=0))
    boot_raw(page, json.dumps(envelope)); settings(page)
    choose(page, density='compact'); payload = saved(page)
    assert payload['futurePresentation'] == envelope['futurePresentation']
    page.locator('#mvpNotesAppearanceReset').click()
    reset_raw = raw(page)
    payload = saved(page)
    assert payload['futurePresentation'] == envelope['futurePresentation']
    assert reset_raw != raw(page)


def peer_conflict(page):
    settings(page); choose(page, density='compact')
    before = snapshot(page)
    peer = page.context.new_page()
    peer.goto(page.url, wait_until='load'); launcher.wait_bootstrap(peer)
    value = json.dumps(dict(schemaVersion=1, **{**DEFAULT,'theme':'dark'}))
    try:
        peer.evaluate('({key,value})=>localStorage.setItem(key,value)', dict(key=KEY,value=value))
        page.locator('#mvpNotesAppearanceSave').click()
        page.wait_for_function('!mvpNotesAppearanceState.saving')
        page.wait_for_function('!!mvpNotesAppearanceState.blocked')
        assert state(page)['draft']['density'] == 'compact'
        page.evaluate('mvpNotesSaveAppearance()')
        assert raw(page) == value
        assert_only_appearance(page, before, 'peer change blocks stale preview', 0)
        page.locator('#mvpNotesAppearanceReload').click()
        assert not state(page)['blocked']
        assert state(page)['confirmed']['theme'] == 'dark'
        assert state(page)['draft'] == state(page)['confirmed']
        assert raw(page) == value
    finally:
        peer.close()


def epoch_while_lock(page):
    settings(page); choose(page, density='compact'); page.evaluate(FAULT,KEY)
    before = snapshot(page)
    page.evaluate("""()=>{
      const acquire=sessionAcquireWriteLock;
      window.__matchRelease=null;
      sessionAcquireWriteLock=callback=>new Promise((resolve,reject)=>{
        window.__matchRelease=()=>{sessionAcquireWriteLock=acquire;Promise.resolve(acquire(callback)).then(resolve,reject);};
      });
    }""")
    page.locator('#mvpNotesAppearanceSave').click()
    page.wait_for_function('typeof __matchRelease==="function"')
    assert not fault_state(page)['attempts']
    # Causal probe of the existing session epoch; no destructive session action.
    page.evaluate('window.JP_WEALTH_SESSION_WIPE_EPOCH=(Number(window.JP_WEALTH_SESSION_WIPE_EPOCH)||0)+1;__matchRelease()')
    page.wait_for_function('!mvpNotesAppearanceState.saving')
    assert not fault_state(page)['attempts'] and raw(page) is None
    assert state(page)['confirmed'] == DEFAULT
    assert_unchanged(page, before, 'stale appearance callback after session epoch')


def cancel_while_lock(page):
    settings(page); choose(page,density='compact'); page.evaluate(FAULT,KEY)
    before = snapshot(page)
    page.evaluate("""()=>{
      const acquire=sessionAcquireWriteLock;
      window.__matchRelease=null;window.__matchSettled=false;
      sessionAcquireWriteLock=callback=>new Promise((resolve,reject)=>{
        window.__matchRelease=()=>{sessionAcquireWriteLock=acquire;
          Promise.resolve(acquire(callback)).then(value=>{window.__matchSettled=true;resolve(value);},reject);};
      });
    }""")
    page.locator('#mvpNotesAppearanceSave').click()
    page.wait_for_function('typeof __matchRelease==="function"')
    assert not fault_state(page)['attempts']
    page.locator('#mvpNotesAppearanceCancel').click()
    assert state(page)['draft'] == state(page)['confirmed'] == DEFAULT
    page.evaluate('__matchRelease()')
    page.wait_for_function('__matchSettled===true')
    assert not fault_state(page)['attempts'] and raw(page) is None
    assert state(page)['confirmed'] == DEFAULT
    assert_unchanged(page,before,'cancelled pending appearance cannot write later')


def durable_epoch_while_lock(page):
    settings(page); choose(page,density='compact'); page.evaluate(FAULT,KEY)
    before = snapshot(page)
    page.evaluate("""()=>{
      const acquire=sessionAcquireWriteLock;
      window.__matchEpoch={before:sessionEpochRead(),ram:Number(window.JP_WEALTH_SESSION_WIPE_EPOCH)||0,key:BASE_EPOCH_STORAGE_KEY};
      window.__matchRelease=null;window.__matchSettled=false;
      sessionAcquireWriteLock=callback=>new Promise((resolve,reject)=>{
        window.__matchRelease=()=>{sessionAcquireWriteLock=acquire;
          Promise.resolve(acquire(callback)).then(value=>{window.__matchSettled=true;resolve(value);},reject);};
      });
      window.__matchRotate=()=>acquire(()=>{
        const next=sessionEpochGenerate();
        if(!next||sessionEpochWriteAndConfirm(next)!==next)throw Error('Synthetic durable epoch rotation failed');
        window.__matchEpoch.after=sessionEpochRead();
      });
    }""")
    page.locator('#mvpNotesAppearanceSave').click()
    page.wait_for_function('typeof __matchRelease==="function"')
    assert not fault_state(page)['attempts']
    page.evaluate('__matchRotate()')
    epoch = page.evaluate('__matchEpoch')
    assert epoch['before'] != epoch['after']
    assert page.evaluate('Number(window.JP_WEALTH_SESSION_WIPE_EPOCH)||0') == epoch['ram']
    # Snapshot after the deliberate fixture epoch write; the delayed callback
    # must not write or change S/session/any preference from this point.
    rotated = snapshot(page)
    assert rotated['state'] == before['state'] and rotated['session'] == before['session']
    local_before, local_rotated = json.loads(before['local']),json.loads(rotated['local'])
    local_before[epoch['key']] = epoch['after']
    assert local_before == local_rotated
    page.evaluate('__matchRelease()'); page.wait_for_function('__matchSettled===true')
    assert not fault_state(page)['attempts'] and raw(page) is None
    assert state(page)['confirmed'] == DEFAULT
    assert_unchanged(page,rotated,'durable epoch blocks before RAM notification')
    return epoch


def restore_limited(page):
    settings(page)
    choose(page, theme='dark', density='compact', preview='hide', sidebar='hide', reading='comfortable', text='larger')
    saved(page); before = snapshot(page)
    page.locator('#mvpNotesAppearanceReset').click()
    assert state(page)['draft'] == DEFAULT
    assert_unchanged(page, before, 'reset only prepares defaults')
    page.locator('#mvpNotesAppearanceCancel').click()
    assert state(page)['draft'] == state(page)['confirmed']
    assert_unchanged(page, before, 'cancel default preview')
    page.locator('#mvpNotesAppearanceReset').click(); payload = saved(page)
    assert {key:payload[key] for key in DEFAULT} == DEFAULT
    assert_only_appearance(page, before, 'confirm appearance defaults', 1)


def widths_restore_clamp(page):
    page.evaluate("""()=>{
      S.mvpNotes.ui={...S.mvpNotes.ui,drawerWidth:1600,foldersPaneWidth:320,notesPaneWidth:520};
      if(save()!==true)throw Error('Synthetic width setup refused');
    }""")
    launcher.settle(page); launcher.instrument(page)
    settings(page); choose(page,density='compact'); saved(page)
    before = snapshot(page)
    original = json.loads(before['state'])
    appearance = raw(page)
    page.locator('#mvpNotesWidthsReset').click()
    after = snapshot(page)
    expected = json.loads(json.dumps(original))
    expected['mvpNotes']['ui'].update(drawerWidth=980,foldersPaneWidth=190,notesPaneWidth=300)
    # save() may update operational bookkeeping outside Notes. The aggregate
    # oracle remains exact, while unchanged non-Notes data is checked separately
    # by the established save/persistence regression suites.
    assert json.loads(after['state'])['mvpNotes'] == expected['mvpNotes']
    assert raw(page) == appearance
    assert json.loads(after['local']).get(POSITION_KEY) == json.loads(before['local']).get(POSITION_KEY)
    assert after['session'] == before['session']
    writes = page.evaluate('window.__notesLauncherWrites')[before['writes']:]
    main_key = page.evaluate('LSKEY')
    assert sum(w['key']==main_key and w['method']=='setItem' for w in writes) == 1, writes
    assert all(w['key'] != KEY and w['key'] != POSITION_KEY for w in writes), writes
    open_from_settings(page)
    checkpoint = snapshot(page)
    for width in (320,390,768,1024,1440):
        page.set_viewport_size(dict(width=width,height=900)); launcher.settle(page)
        experience.usable(page)
        assert page.evaluate('S.mvpNotes.ui') == expected['mvpNotes']['ui']
    assert_unchanged(page, checkpoint, 'width clamp never rewrites saved widths')


def finalize_cleanup(page):
    settings(page)
    choose(page,theme='dark',density='compact',reading='comfortable',text='large')
    saved(page)
    page.evaluate('mvpNotesPersistDrawerWidth(1260);mvpNotesPersistPaneWidth("foldersPaneWidth",260);mvpNotesPersistPaneWidth("notesPaneWidth",380)')
    page.locator('#settingsCloseBtn').click()
    # Reuse the established safe-copy checkpoint and human-phrase path. All
    # accounts/notes in this context were generated by the nominal fixtures.
    finalizer.assert_safe_copy_checkpoint(page)
    notes = page.evaluate('JSON.stringify(S.mvpNotes)')
    assert raw(page) is not None
    peer = page.context.new_page()
    peer_errors = {'pageerror':[], 'console':[]}
    peer.on('pageerror',lambda error:peer_errors['pageerror'].append(str(error)))
    peer.on('console',lambda message:peer_errors['console'].append(message.text) if message.type=='error' else None)
    # Same portable-server asset mapping as launcher.prepare() on page A.
    # It is page-scoped, so the new tab needs it before its first navigation.
    peer.route('**/dist/assets/**',lambda route:route.continue_(url=route.request.url.replace('/dist/assets/','/assets/')))
    try:
        peer.goto(page.url,wait_until='load');launcher.wait_bootstrap(peer)
        peer.evaluate('window.__onbShown=true;closeModal();window.alert=()=>{};window.confirm=()=>false;window.prompt=()=>null;')
        launcher.settle(peer);launcher.instrument(peer)
        settings(peer);choose(peer,density='comfortable',preview='hide')
        assert state(peer)['draft'] != state(peer)['confirmed']
        page.evaluate('fxAutoFetchedThisSession=true;markSessionCheckpoint()')
        page.locator('#finalizeSessionBtn').click()
        expect(page.locator('#sessionHasCopy')).to_be_visible()
        page.locator('#sessionHasCopy').click()
        finalizer.finish_with_phrase(page)
        peer.wait_for_function("document.getElementById('sessionNotice')?.textContent.includes('outra aba')")
        for tab in (page,peer):
            assert raw(tab) is None, 'Finalization did not remove the auxiliary appearance'
            assert tab.evaluate('JSON.stringify(S.mvpNotes)') == notes, 'Finalization changed Notes content, folders or widths'
            disk = tab.evaluate('JSON.stringify(JSON.parse(localStorage.getItem(LSKEY)).mvpNotes)')
            assert disk == notes, 'Preserved Notes were not durably retained'
            assert tab.evaluate("localStorage.getItem('notes_launcher_unrelated')") == 'synthetic-preserved'
            assert state(tab)['confirmed'] == state(tab)['draft'] == DEFAULT, 'Finalization left stale appearance in RAM'
        assert state(peer)['blocked'], 'The peer draft must be invalidated by the session change'
        expect(peer.locator('#mvpNotesAppearanceSave')).to_be_disabled()
        writes_before = snapshot(peer)
        peer.evaluate('mvpNotesSaveAppearance()')
        assert_unchanged(peer,writes_before,'peer cannot resurrect finalized appearance')
        peer.locator('#mvpNotesAppearanceReload').click()
        assert not state(peer)['blocked'] and state(peer)['draft'] == DEFAULT
        assert raw(peer) is None, 'Explicit reread must not create a default preference'
        reload_page(page)
        assert raw(page) is None
        assert page.evaluate('JSON.stringify(S.mvpNotes)') == notes
        launcher.assert_clean(page.context,peer_errors)
        return dict(notes_preserved=True,appearance_removed=True,peer_draft_invalidated=True,
                    reload_preserved=True,peer_observed_errors=peer_errors)
    finally:
        peer.close()


CASES = {
    'anatomy': anatomy, 'responsive': responsive,
    'preview-preserves-editor': preview_preserves_editor,
    'no-write-cancel-navigation': no_write_cancel_navigation, 'save-reload': save_reload,
    'theme-override': theme_override, 'display-choices': display_choices,
    'sidebar-toggle': sidebar_toggle, 'refusal-retry': refused_retry,
    'unknown-block': unknown_block, 'invalid-raw': invalid_raw,
    'unreadable-raw': unreadable_raw, 'extensions': extensions,
    'peer-conflict': peer_conflict, 'epoch-while-lock': epoch_while_lock,
    'cancel-while-lock': cancel_while_lock, 'durable-epoch-while-lock': durable_epoch_while_lock,
    'restore-limited': restore_limited, 'widths-restore-clamp': widths_restore_clamp,
    'finalize-cleanup': finalize_cleanup,
}


def prepare(context, url, theme):
    page, observed = launcher.prepare(context, url, theme)
    page.evaluate(experience.SEED, 12)
    # First reload characterizes the established nominal bootstrap normalization
    # before checkpoints. No field is excluded to hide a post-checkpoint change.
    warmup_before = experience.domain(page)
    reload_page(page)
    warmup_diff = experience.domain_diff(warmup_before, experience.domain(page))
    page.evaluate('t=>document.documentElement.dataset.theme=t', theme)
    launcher.settle(page); launcher.instrument(page)
    return page, observed, warmup_diff


def result_for(error, baseline, booted):
    if isinstance(error, AssertionError) or isinstance(error, PlaywrightTimeout) and booted:
        return 'BASELINE_FAIL' if baseline else 'PRODUCT_FAIL'
    return 'TEST_HARNESS_FAIL'


def run(args):
    args.root = args.root.resolve(); args.out = args.out.resolve()
    args.out.parent.mkdir(parents=True,exist_ok=True)
    if args.out.exists():
        raise FileExistsError('Evidence exists; choose a new --out: '+str(args.out))
    load_helpers(args.root)
    selected = args.cases.split(',') if args.cases else list(CASES)
    if set(selected)-set(CASES):
        raise ValueError('Unknown cases: '+','.join(sorted(set(selected)-set(CASES))))
    helper_paths = [args.root/'tools'/name for name in ('notes_launcher_test.py','notes_experience_test.py','browser_bootstrap_fixture.py','finalize_session_test.py')]
    report = dict(started_at=datetime.now(timezone.utc).isoformat(),root=str(args.root),baseline=args.baseline,
                  test_sha256=digest(Path(__file__)),inputs_before=hashes(args.root),
                  helpers_before={str(path):digest(path) for path in helper_paths},checks=[],
                  limits=['Synthetic Chromium and loopback fixtures only; service workers blocked.',
                          'Projection while the editor is dirty uses identified direct change dispatch on the covered Settings controls.',
                          'Native 200% is opt-in and uses a fresh headed profile; CSS zoom is never substituted.',
                          'This focal does not replace Notes save/recovery, full CI, PWA, accessibility or human visual acceptance.'])
    server = ThreadingHTTPServer(('127.0.0.1',0),partial(launcher.Quiet,directory=str(args.root)))
    threading.Thread(target=server.serve_forever,daemon=True).start()
    prefix = f'http://127.0.0.1:{server.server_port}/'
    artifacts = ['index.html','dist/JP_Wealth_Risk_Terminal_V9.1_PORTABLE.html'] if args.artifact=='both' else [
        'index.html' if args.artifact=='source' else 'dist/JP_Wealth_Risk_Terminal_V9.1_PORTABLE.html']

    def check(context, artifact, name, width, theme, native=False):
        label = f'{artifact}/{name}/{width}/{theme}'+('/native-200' if native else '')
        row = dict(name=label); page = observed = None
        try:
            context.set_default_timeout(12000)
            page, observed, warmup = prepare(context,prefix+artifact,theme)
            row.update(build=page.evaluate('JP_WEALTH_BUILD_ID'),warmup_reload_diff=warmup)
            if native:
                assert page.evaluate('Math.abs(outerWidth/innerWidth-2)<0.01 && getComputedStyle(document.documentElement).zoom==="1"'), 'Native 200% was not established'
                row['native_geometry'] = page.evaluate('({outerWidth,innerWidth,devicePixelRatio})')
            detail = CASES[name](page)
            if native:
                # no-write-cancel-navigation leaves the real Settings page open.
                # Verify the Notes window itself in the same native-zoom context,
                # without CSS zoom or Playwright viewport emulation.
                open_from_settings(page)
                row['native_notes_geometry'] = experience.usable(page)
                experience.select_first(page)
                page.locator('#mvpNoteContent').fill(experience.LONG_BODY)
                original = experience.draft_snapshot(page)
                assert page.locator('#mvpNoteContent').evaluate('e=>e.scrollHeight>e.clientHeight')
                page.locator('#mvpNotesCloseBtn').click()
                expect(page.locator('#mvpNotesOverlay')).to_be_visible()
                experience.assert_draft(page,original)
                for key in ('Tab','Shift+Tab'):
                    for _ in range(12):
                        page.keyboard.press(key)
                        assert page.evaluate('document.getElementById("mvpNotesOverlay").contains(document.activeElement)')
                page.locator('#mvpNotesSaveBtn').click()
                assert not page.evaluate('mvpNotesUI.draftDirty')
                assert page.locator('#mvpNoteContent').input_value() == experience.LONG_BODY
                close_notes(page)
            launcher.assert_clean(context,observed)
            row.update(result='PASS',detail=detail)
        except Exception as error:
            row.update(result=result_for(error,args.baseline,'build' in row),error_type=type(error).__name__,detail=str(error))
        finally:
            if page:
                try:
                    capture = args.out.with_name(args.out.stem+'-'+label.replace('/','-').replace('.html','')+'.png')
                    page.screenshot(path=str(capture)); row.update(screenshot=str(capture),screenshot_sha256=digest(capture))
                except Exception as error:
                    row['capture_error'] = str(error)
            if observed:
                row['observed_errors'] = observed
            report['checks'].append(row)
            print(json.dumps({key:row[key] for key in ('name','result','detail') if key in row},ensure_ascii=False),flush=True)

    try:
        with sync_playwright() as pw:
            browser = pw.chromium.launch(**launcher.launch_options())
            try:
                for artifact in artifacts:
                    for name in selected:
                        configs = [(1440,'light')]
                        if name=='responsive':
                            configs = [(width,theme) for width in (320,390,768,1024,1440) for theme in ('light','dark')]
                        elif name=='anatomy':
                            configs = [(1440,theme) for theme in ('light','dark')]
                        elif name=='display-choices':
                            configs = [(1920,'light')]
                        for width,theme in configs:
                            context = browser.new_context(viewport=dict(width=width,height=900),service_workers='block',reduced_motion='reduce')
                            try:
                                check(context,artifact,name,width,theme)
                            finally:
                                context.close()
            finally:
                browser.close()
            if args.native_zoom:
                profile = Path(tempfile.mkdtemp(prefix='apple-notes-native-200-',dir=args.out.parent))
                (profile/'Default').mkdir()
                (profile/'Default/Preferences').write_text(json.dumps({'partition':{'default_zoom_level':{'x':math.log(2)/math.log(1.2)}}}))
                options = launcher.launch_options()
                options.update(headless=False,no_viewport=True,args=['--window-size=1440,1000'],service_workers='block',reduced_motion='reduce')
                context = pw.chromium.launch_persistent_context(str(profile),**options)
                try:
                    # Responsive helper reads viewport_size; the real browser's
                    # innerWidth becomes the test's metadata, not a viewport override.
                    check(context,'index.html','no-write-cancel-navigation','native','dark',native=True)
                finally:
                    context.close()
    except Exception as error:
        report['checks'].append(dict(name='runtime',result='ENVIRONMENT_ERROR',detail=str(error)))
    finally:
        server.shutdown(); server.server_close()
        report['inputs_after'] = hashes(args.root)
        report['helpers_after'] = {str(path):digest(path) for path in helper_paths}
        report['source_unchanged'] = report['inputs_before']==report['inputs_after'] and report['helpers_before']==report['helpers_after'] and report['test_sha256']==digest(Path(__file__))
        if not report['source_unchanged']:
            report['checks'].append(dict(name='candidate stable during execution',result='TEST_HARNESS_FAIL',detail='Input, helper or focal hashes changed during execution'))
        statuses = {row['result'] for row in report['checks']}
        report['result'] = ('PASS' if statuses=={'PASS'} else 'ENVIRONMENT_ERROR' if 'ENVIRONMENT_ERROR' in statuses
                            else 'TEST_HARNESS_FAIL' if 'TEST_HARNESS_FAIL' in statuses
                            else 'BASELINE_FAIL' if args.baseline else 'PRODUCT_FAIL')
        report['finished_at'] = datetime.now(timezone.utc).isoformat()
        with args.out.open('x') as out:
            json.dump(report,out,ensure_ascii=False,indent=2); out.write('\n')
        print(json.dumps(dict(result=report['result'],checks=len(report['checks']),output=str(args.out)),ensure_ascii=False),flush=True)
    return 0 if report['result']=='PASS' else 1


if __name__=='__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root',type=Path,default=ROOT)
    parser.add_argument('--out','--output',type=Path,required=True)
    parser.add_argument('--artifact',choices=('source','portable','both'),default='both')
    parser.add_argument('--cases',help=','.join(CASES))
    parser.add_argument('--baseline',action='store_true')
    parser.add_argument('--native-zoom',action='store_true')
    raise SystemExit(run(parser.parse_args()))
