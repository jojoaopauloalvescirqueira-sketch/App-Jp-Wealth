#!/usr/bin/env python3
"""NOTES EXPERIENCE COMPLETION: isolated behavioral UI contract.

Only synthetic data and the established economic bootstrap are used. The three
baseline cases deliberately exit nonzero when the requested behavior is absent.
No full gate or production/browser-profile operation is performed here.
"""
import argparse
from datetime import datetime, timezone
from functools import partial
from http.server import ThreadingHTTPServer
from browser_fixture_server import BrowserFixtureServer as ThreadingHTTPServer
import hashlib
import importlib.util
import json
from pathlib import Path
import threading

from playwright.sync_api import sync_playwright, expect, TimeoutError as PlaywrightTimeout
import notes_launcher_test as launcher

ROOT = Path(__file__).resolve().parents[1]
POSITION_KEY = 'jpwealth_notes_launcher_position_v1'
PANES = ('mvpNotesFolderSidebar', 'mvpNotesListPane', 'mvpNotesEditorPane')
LONG_TITLE = 'Nota sintética com título muito longo para conferir leitura e alinhamento ' * 3
LONG_BODY = LONG_TITLE + '\n' + '\n'.join('Linha %03d — conteúdo sintético preservado.' % n for n in range(180))
SEED = """count => {
  const first=mvpNotesCreateFolder('Planejamento sintético de uma pasta com nome extenso para leitura e organização');
  const second=mvpNotesCreateFolder('Segunda pasta');
  if(!first || !second)throw Error('Synthetic folder setup was refused');
  const ids=[];
  for(let i=0;i<count;i++){
    const n=mvpNotesCreate({content:'Nota sintética '+String(i+1).padStart(2,'0')+'\\nCorpo de demonstração '+i,
      type:'task',priority:'medium',status:'open',folderId:i<10?first.id:second.id});
    if(!n)throw Error('Synthetic note setup was refused');ids.push(n.id);
  }
  window.__notesExperienceSeed={ids,first:first.id,second:second.id};
  renderMvpNotesHeader();
}"""


def domain(page):
    return page.evaluate("""() => ({state:JSON.stringify(S),
      local:Object.fromEntries(Object.keys(localStorage).sort().filter(k=>k!=='jpwealth_notes_launcher_position_v1')
        .map(k=>[k,localStorage.getItem(k)])),
      session:Object.fromEntries(Object.keys(sessionStorage).sort().map(k=>[k,sessionStorage.getItem(k)]))})""")


def concrete_diff(before, after, path='$'):
    if type(before) is not type(after):
        return [{'path':path,'before':before,'after':after}]
    if isinstance(before,dict):
        rows=[]
        for key in sorted(set(before)|set(after)):
            if key not in before or key not in after:
                rows.append({'path':path+'.'+str(key),'before':before.get(key,'<absent>'),'after':after.get(key,'<absent>')})
            else:rows.extend(concrete_diff(before[key],after[key],path+'.'+str(key)))
        return rows
    if isinstance(before,list):
        if len(before)!=len(after):return [{'path':path+'.length','before':len(before),'after':len(after)}]
        return [row for i,(a,b) in enumerate(zip(before,after)) for row in concrete_diff(a,b,path+'['+str(i)+']')]
    return [] if before==after else [{'path':path,'before':before,'after':after}]


def domain_diff(before, after):
    result={'changed':[k for k in before if after[k]!=before[k]],
      'state_diff':concrete_diff(json.loads(before['state']),json.loads(after['state'])),'local_diff':[]}
    for key in sorted(set(before['local'])|set(after['local'])):
        a,b=before['local'].get(key),after['local'].get(key)
        if a==b:continue
        try:a,b=json.loads(a),json.loads(b)
        except (TypeError,ValueError):pass
        result['local_diff'].extend(concrete_diff(a,b,'localStorage.'+key))
    result['session_diff']=concrete_diff(before['session'],after['session'],'sessionStorage')
    return result


def no_domain_change(page, before, label):
    after = domain(page)
    assert after == before, {'case': label, **domain_diff(before,after)}


def clear_writes(page):
    page.evaluate('window.__notesLauncherWrites=[]')


def writes(page):
    return page.evaluate('window.__notesLauncherWrites')


def position(page):
    return page.evaluate('(key)=>JSON.parse(localStorage.getItem(key))', POSITION_KEY)


def valid_position(value):
    assert isinstance(value, dict) and set(value) == {'schemaVersion', 'x', 'y'}, value
    assert value['schemaVersion'] == 1 and type(value['schemaVersion']) is int, value
    assert all(type(value[k]) in (int, float) and 0 <= value[k] <= 1 for k in ('x', 'y')), value


def geometry(page):
    return page.evaluate("""() => {
      const rect=id=>{const r=document.getElementById(id).getBoundingClientRect();return {x:r.x,y:r.y,width:r.width,height:r.height,right:r.right,bottom:r.bottom}};
      return {window:rect('mvpNotesDrawer'),body:rect('mvpNotesBody'),
        panes:['mvpNotesFolderSidebar','mvpNotesListPane','mvpNotesEditorPane'].map(rect),
        vw:innerWidth,vh:innerHeight,scrollWidth:document.documentElement.scrollWidth,
        stage:document.getElementById('mvpNotesDrawer').dataset.mobileStage,
        layout:document.getElementById('mvpNotesDrawer').dataset.notesLayout};
    }""")


def visible(page, ident):
    return page.locator('#' + ident).is_visible()


def visible_panes(page):
    return [ident for ident in PANES if visible(page, ident)]


def usable(page):
    g = geometry(page)
    r = g['window']
    assert r['x'] >= -1 and r['y'] >= -1 and r['right'] <= g['vw'] + 1 and r['bottom'] <= g['vh'] + 1, g
    assert g['body']['height'] >= 44 and g['scrollWidth'] <= g['vw'] + 1, g
    expect(page.locator('#mvpNotesCloseBtn')).to_be_visible()
    page.locator('#mvpNotesCloseBtn').click(trial=True)
    return g


def open_notes(page):
    if page.locator('#headerNotesBtn').is_visible():
        page.locator('#headerNotesBtn').click()
    else:
        page.evaluate("openSettingsModal('interface')")
        page.locator('#mvpNotesOpenFromSettingsBtn').click()
    expect(page.locator('#mvpNotesOverlay')).to_be_visible()


def select_first(page):
    if not visible(page, 'mvpNotesListPane'):
        page.locator('[data-mvp-folder="all"]').click()
    page.locator('.mvpn-card[data-mvp-note-id]').first.click()
    expect(page.locator('#mvpNoteContent')).to_be_visible()


def dirty(page):
    open_notes(page)
    select_first(page)
    page.locator('#mvpNoteContent').fill(LONG_BODY)
    page.locator('#mvpNoteContent').evaluate('e=>{e.focus();e.setSelectionRange(18,37);e.scrollTop=130;}')
    assert page.evaluate('mvpNotesUI.draftDirty')


def draft_snapshot(page):
    return page.evaluate("""() => {
      const e=document.getElementById('mvpNoteContent');
      return {draft:JSON.stringify(mvpNotesUI.draft),original:JSON.stringify(mvpNotesUI.draftOriginal),
        dirty:mvpNotesUI.draftDirty,selected:mvpNotesUI.selectedId,folder:mvpNotesUI.activeFolder,
        query:mvpNotesUI.query,value:e.value,start:e.selectionStart,end:e.selectionEnd,scroll:e.scrollTop,
        widths:JSON.stringify(S.mvpNotes.ui)};
    }""")


def assert_draft(page, before, scroll=True):
    after = draft_snapshot(page)
    for k in before:
        if k == 'scroll' and not scroll:
            continue
        assert after[k] == before[k], {'changed': k, 'expected': str(before[k])[:240], 'actual': str(after[k])[:240]}


def center(page):
    open_notes(page)
    g = usable(page); r = g['window']
    assert r['x'] >= 12 and r['y'] >= 12 and g['vw']-r['right'] >= 12 and g['vh']-r['bottom'] >= 12, g
    assert abs(r['x'] - (g['vw']-r['right'])) <= 2, {'message': 'Notes is not horizontally centered', **g}
    assert abs(r['y'] - (g['vh']-r['bottom'])) <= 2, {'message': 'Notes is not vertically centered', **g}
    assert visible_panes(page) == list(PANES), g
    f, n, e = g['panes']
    assert e['width'] > n['width'] > f['width'], g
    assert page.locator('#mvpNotesOverlay').count() == 1 and page.locator('#mvpNotesDrawer').count() == 1
    return g


def reopen_dirty(page):
    dirty(page)
    before = draft_snapshot(page); saved = domain(page)
    page.evaluate("""() => {
      window.__notesExperienceIdentity={opener:mvpNotesUI.opener,inert:mvpNotesUI.inertSnapshot,
        hosts:mvpNotesUI.persistenceHosts,editor:document.getElementById('mvpNoteContent')};
      openMvpNotesDrawer(document.getElementById('mvpNotesOpenFromSettingsBtn'));
      openMvpNotesDrawer(document.getElementById('headerNotesBtn'));
    }""")
    assert_draft(page, before)
    assert page.evaluate("""() => {
      const old=window.__notesExperienceIdentity;
      return old.opener===mvpNotesUI.opener && old.inert===mvpNotesUI.inertSnapshot &&
        old.hosts===mvpNotesUI.persistenceHosts && old.editor===document.getElementById('mvpNoteContent');
    }"""), 'Reactivation replaced opener, inert snapshot, persistence hosts or editor'
    no_domain_change(page, saved, 'reopen dirty')
    assert page.locator('#mvpNotesOverlay').count() == 1
    identity=page.evaluate('mvpNotesUI.selectedId')
    page.locator('#mvpNotesCloseBtn').click()
    expect(page.locator('#headerNotesBtn')).to_be_focused()
    assert not visible(page,'mvpNotesOverlay')
    assert page.evaluate('(id)=>JSON.parse(localStorage.getItem(LSKEY)).mvpNotes.items.find(n=>n.id===id).content',identity)==LONG_BODY
    open_notes(page);page.evaluate('(id)=>mvpNotesSelectNote(id)',identity)
    assert page.locator('#mvpNoteContent').input_value()==LONG_BODY
    assert not page.evaluate('mvpNotesUI.draftDirty')


def position_reload(page):
    # The established economic fixture is normalized on its first real reload.
    # Capture that setup effect before the position-integrity checkpoint rather
    # than excluding activeOperation or any main-document bytes from comparison.
    warmup_before = domain(page)
    page.reload(wait_until='load'); launcher.wait_bootstrap(page)
    page.evaluate('window.__onbShown=true;closeModal()'); launcher.settle(page)
    page.notes_experience_warmup_diff = domain_diff(warmup_before, domain(page))
    launcher.instrument(page)
    saved = domain(page)
    launcher.mouse_move(page, -135, -115)
    moved = launcher.geometry(page)
    pref = position(page)
    page.reload(wait_until='load'); launcher.wait_bootstrap(page)
    page.evaluate('window.__onbShown=true;closeModal()'); launcher.settle(page)
    launcher.same_position(moved, launcher.contained(page), tolerance=2)
    valid_position(pref)
    assert position(page) == pref
    no_domain_change(page, saved, 'position reload')
    for width in (1024, 390, 320, 1440):
        page.set_viewport_size({'width': width, 'height': 900}); launcher.settle(page)
        launcher.contained(page)
        assert position(page) == pref, 'Resize rewrote the saved normalized preference'
    launcher.same_position(moved, launcher.geometry(page), tolerance=2)
    no_domain_change(page, saved, 'position reload and viewport changes')
    return {'preference': pref, 'restored': launcher.geometry(page)}


def reopen_recovery_focus(page):
    dirty(page)
    page.evaluate("""() => {
      jpWealthLoadRecovery.active=true;
      jpWealthLoadRecovery.raw='{"syntheticRecovery":true}';
      renderLoadRecoveryWarning();
      mvpNotesDockPersistence(true);
      const action=document.getElementById('persistenceRecoveryDownloadBtn');
      action.focus({preventScroll:true});
      window.__notesRecoveryIdentity={action,opener:mvpNotesUI.opener,
        inert:mvpNotesUI.inertSnapshot,hosts:mvpNotesUI.persistenceHosts,
        recovery:document.getElementById('persistenceRecovery'),
        alert:document.getElementById('persistenceAlert'),
        editor:document.getElementById('mvpNoteContent')};
    }""")
    expect(page.locator('#persistenceRecoveryDownloadBtn')).to_be_visible()
    expect(page.locator('#persistenceRecoveryDownloadBtn')).to_be_focused()
    before=draft_snapshot(page);saved=domain(page)
    page.evaluate("""() => {
      openMvpNotesDrawer(document.getElementById('mvpNotesOpenFromSettingsBtn'));
      openMvpNotesDrawer(document.getElementById('headerNotesBtn'));
      mvpNotesDockPersistence(true);
    }""")
    identity=page.evaluate("""() => {
      const old=window.__notesRecoveryIdentity,overlay=document.getElementById('mvpNotesOverlay');
      return {sameAction:old.action===document.getElementById('persistenceRecoveryDownloadBtn'),
        focused:old.action===document.activeElement,opener:old.opener===mvpNotesUI.opener,
        inert:old.inert===mvpNotesUI.inertSnapshot,hosts:old.hosts===mvpNotesUI.persistenceHosts,
        recovery:old.recovery===document.getElementById('persistenceRecovery'),
        alert:old.alert===document.getElementById('persistenceAlert'),
        editor:old.editor===document.getElementById('mvpNoteContent'),
        docked:overlay.contains(old.recovery)&&overlay.contains(old.alert)};
    }""")
    assert all(identity.values()),identity
    assert_draft(page,before)
    no_domain_change(page,saved,'reopening preserves focused real recovery action')
    assert page.locator('#mvpNotesOverlay').count()==1
    assert page.locator('#persistenceRecovery').count()==1 and page.locator('#persistenceAlert').count()==1
    expect(page.locator('#persistenceRecoveryDownloadBtn')).to_be_focused()
    return identity


def responsive(page):
    width = page.viewport_size['width']
    open_notes(page)
    g = usable(page)
    if width > 1100:
        assert visible_panes(page) == list(PANES), g
    elif width > 600:
        assert len(visible_panes(page)) == 2, g
    else:
        assert visible_panes(page) == [PANES[0]], g
    if visible(page, 'mvpNotesFolderSidebar'):
        page.locator('[data-mvp-folder="all"]').click()
    if width <= 600:
        assert visible_panes(page) == [PANES[1]], geometry(page)
    elif width <= 1100:
        assert visible_panes(page) == [PANES[1], PANES[2]], geometry(page)
    select_first(page)
    page.locator('#mvpNoteContent').fill(LONG_BODY)
    before = draft_snapshot(page)
    if width <= 600:
        assert visible_panes(page) == [PANES[2]], geometry(page)
        expect(page.locator('#mvpNotesBackBtn')).to_be_visible()
        identity=before['selected']
        page.locator('#mvpNotesBackBtn').click()
        assert visible_panes(page) == [PANES[1]]
        assert page.evaluate('(id)=>JSON.parse(localStorage.getItem(LSKEY)).mvpNotes.items.find(n=>n.id===id).content',identity)==LONG_BODY
        page.locator('.mvpn-card[data-mvp-note-id="'+identity+'"]').click()
        assert visible_panes(page) == [PANES[2]]
    elif width <= 1100:
        assert visible_panes(page) == [PANES[1], PANES[2]], geometry(page)
        assert geometry(page)['panes'][2]['width'] >= 320
    else:
        assert visible_panes(page) == list(PANES)
    if page.locator('#mvpNotesSaveBtn').is_visible():page.locator('#mvpNotesSaveBtn').click()
    assert not page.evaluate('mvpNotesUI.draftDirty')
    for ident in PANES:
        if not visible(page, ident):
            assert page.locator('#'+ident).evaluate("e=>[...e.querySelectorAll('button,input,textarea,select,[tabindex]')].every(n=>n.getClientRects().length===0)"), ident
    g = usable(page)
    assert page.locator('#mvpNoteContent').input_value() == LONG_BODY
    assert page.locator('#mvpNoteContent').evaluate('e=>e.scrollHeight>e.clientHeight')
    return g


def resize_dirty(page):
    dirty(page)
    before = draft_snapshot(page); saved = domain(page); clear_writes(page)
    observations = []
    for width in (1024, 390, 320, 1440):
        page.set_viewport_size({'width': width, 'height': 900}); launcher.settle(page)
        assert_draft(page, before, scroll=False)
        g = usable(page); observations.append(g)
        expected = [PANES[2]] if width <= 600 else list(PANES[1:]) if width <= 1100 else list(PANES)
        assert visible_panes(page) == expected, g
        if width <= 600:
            expect(page.locator('#mvpNotesBackBtn')).to_be_visible()
        assert page.evaluate("() => {const e=document.activeElement;return document.getElementById('mvpNotesOverlay').contains(e) && e.getClientRects().length>0}"), 'Resize stranded focus outside visible Notes'
    no_domain_change(page, saved, 'resize dirty')
    assert not writes(page), writes(page)
    return observations


def focus_settings(page):
    page.locator('#headerConfigBtn').click()
    page.evaluate("settingsNavigateToLeaf('interface')")
    page.locator('#mvpNotesOpenFromSettingsBtn').click()
    expect(page.locator('#mvpNotesCloseBtn')).to_be_focused()
    assert page.locator('#settingsModal').evaluate('e=>e.inert')
    assert page.locator('#mvpNotesLauncher').is_hidden()
    focusables = page.evaluate("mvpNotesFocusables(document.getElementById('mvpNotesOverlay')).map(e=>e.id)")
    assert focusables
    for direction in ('Tab', 'Shift+Tab'):
        for _ in range(len(focusables)+2):
            page.keyboard.press(direction)
            assert page.evaluate("() => {const e=document.activeElement;return document.getElementById('mvpNotesOverlay').contains(e) && e.getClientRects().length>0}"), direction
    page.locator('#mvpNotesCloseBtn').click()
    expect(page.locator('#mvpNotesOpenFromSettingsBtn')).to_be_focused()
    assert not page.locator('#settingsModal').evaluate('e=>e.inert')
    page.locator('#settingsCloseBtn').click()
    expect(page.locator('#headerConfigBtn')).to_be_focused()


def icon_labels(page):
    uses = ['#headerNotesBtn', '#mvpNotesSettingsCard', '#mvpNotesDrawer .mvp-notes-head-text']
    hrefs=[]
    for selector in uses:
        icons=page.locator(selector+' svg use')
        assert icons.count()>0, 'Missing shared Notes symbol in '+selector
        hrefs.append(icons.first.get_attribute('href'))
    assert hrefs[0] and len(set(hrefs)) == 1, {'shared_symbol': hrefs}
    symbol = page.locator(hrefs[0]); assert symbol.count() == 1
    assert page.locator('#headerActions #headerNotesBtn').count() == 0
    assert page.locator('#mvpNotesPositionHelp').inner_text().find('Ao recarregar, ele volta') == -1
    open_notes(page)
    for selector in ('#mvpNotesTitle','#mvpNotesViewTitle','#mvpNotesNewBtn','#mvpNotesCloseBtn'):
        e=page.locator(selector)
        label=' '.join([e.inner_text(),e.get_attribute('aria-label') or '',e.get_attribute('title') or ''])
        assert 'ticket' not in label.lower(), (selector,label)
    assert 'ticket' not in page.locator('#mvpNotesSearch').get_attribute('placeholder').lower()
    # Geometry/path licensing and optical recognition remain part of visual review.
    return {'shared_symbol': hrefs[0], 'symbol_markup': symbol.inner_html()}


def reduced_motion(page):
    assert page.evaluate("matchMedia('(prefers-reduced-motion:reduce)').matches")
    open_notes(page)
    active=page.locator('#mvpNotesDrawer').evaluate("e=>e.getAnimations({subtree:true}).filter(a=>a.playState==='running').map(a=>({name:a.animationName||null,duration:a.effect.getTiming().duration}))")
    assert not active, active
    return {'running_animations':active}


def empty_search(page):
    assert page.evaluate('S.mvpNotes.items.length') == 0
    open_notes(page)
    expect(page.locator('#mvpNotesList .mvpn-empty')).to_be_visible()
    saved=domain(page)
    page.locator('#mvpNotesSearch').fill('texto sem correspondência')
    assert page.locator('.mvpn-card').count() == 0
    expect(page.locator('#mvpNotesList .mvpn-empty')).to_be_visible()
    page.locator('#mvpNotesSearch').fill('')
    no_domain_change(page,saved,'empty search')


def long_search(page):
    open_notes(page)
    saved=domain(page)
    assert page.locator('.mvpn-card').count() == 12
    page.locator('#mvpNotesSearch').fill('impossivel-sem-correspondencia')
    assert page.locator('.mvpn-card').count() == 0
    expect(page.locator('#mvpNotesList .mvpn-empty')).to_be_visible()
    page.locator('#mvpNotesSearch').fill('sintética 01')
    assert page.locator('.mvpn-card').count() == 1
    page.locator('#mvpNotesSearch').fill('')
    assert page.locator('.mvpn-card').count() == 12
    no_domain_change(page,saved,'search')


def preference_actions(page):
    saved=domain(page);clear_writes(page)
    launcher.mouse_move(page,-110,-90)
    pref=position(page);valid_position(pref)
    attempted=writes(page)
    assert len(attempted)==1 and attempted[0]=={'method':'setItem','area':'local','key':POSITION_KEY}, attempted
    clear_writes(page)
    for cancel in ('escape','cancel','lostcapture'):
        launcher.mouse_move(page,-30,-20,cancel)
        assert position(page)==pref
    assert not writes(page),writes(page)
    page.locator('#headerConfigBtn').click();page.evaluate("settingsNavigateToLeaf('interface')")
    page.locator('#mvpNotesPositionReset').click()
    page.locator('#settingsCloseBtn').click()
    launcher.default_position(page)
    restored=position(page)
    if restored is not None:
        valid_position(restored); assert restored['x']==1 and restored['y']==1
    no_domain_change(page,saved,'preference actions/reset')


# Preference fault fixtures change only the storage/lock boundary in this page.
# Every production read, write, readback, callback and user input still runs.
AUX_PROBE = """() => {
  const key='jpwealth_notes_launcher_position_v1';
  const get=Storage.prototype.getItem,set=Storage.prototype.setItem,remove=Storage.prototype.removeItem;
  const fixture={mode:'normal',unreadable:false,attempts:[],results:[],promises:[],
    raw:()=>get.call(localStorage,key)};
  window.__notesAuxFixture=fixture;
  Storage.prototype.getItem=function(k){
    if(this===localStorage && k===key && fixture.unreadable)throw new DOMException('Synthetic unknown readback','SecurityError');
    return get.call(this,k);
  };
  Storage.prototype.setItem=function(k,value){
    if(this===localStorage && k===key){
      fixture.attempts.push({method:'setItem',value});
      if(fixture.mode==='quota')throw new DOMException('Synthetic refusal','QuotaExceededError');
      if(fixture.mode==='noop')return;
      const result=set.call(this,k,value);
      if(fixture.mode==='unknown')fixture.unreadable=true;
      return result;
    }
    return set.call(this,k,value);
  };
  Storage.prototype.removeItem=function(k){
    if(this===localStorage && k===key)fixture.attempts.push({method:'removeItem'});
    return remove.call(this,k);
  };
  const persist=mvpNotesPersistLauncherPosition;
  mvpNotesPersistLauncherPosition=function(...args){
    const result=persist.apply(this,args);fixture.promises.push(result);
    Promise.resolve(result).then(value=>fixture.results.push(value));return result;
  };
}"""


def aux_reload(page, raw):
    before=domain(page)
    page.evaluate("({key,raw})=>raw===null?localStorage.removeItem(key):localStorage.setItem(key,raw)",
                  {'key':POSITION_KEY,'raw':raw})
    page.reload(wait_until='load');launcher.wait_bootstrap(page)
    page.evaluate('window.__onbShown=true;closeModal();window.confirm=()=>false;window.alert=()=>{};window.prompt=()=>null')
    launcher.settle(page);launcher.instrument(page);page.evaluate(AUX_PROBE)
    return domain_diff(before,domain(page))


def aux_state(page):
    return page.evaluate("""() => {
      const f=window.__notesAuxFixture,s=document.getElementById('mvpNotesPositionStatus');
      return {raw:f.raw(),attempts:f.attempts,results:f.results,
        status:s?{text:s.textContent,error:s.dataset.error}:null,
        position:{...mvpNotesUI.launcherPosition}};
    }""")


def aux_wait(page, previous):
    page.wait_for_function('n=>window.__notesAuxFixture.results.length>n',arg=previous)
    return aux_state(page)


def raw_launcher_drag(page, dx=-50, dy=-35, release=True):
    """Real pointer gesture without the happy-path persistence oracle in helpers."""
    first=launcher.geometry(page);x=first['x']+first['w']/2;y=first['y']+first['h']/2
    page.mouse.move(x,y);page.mouse.down();page.mouse.move(x+dx,y+dy,steps=8)
    if release:page.mouse.up()
    launcher.settle(page)
    return first,launcher.geometry(page)


def aux_error(state):
    assert state['results'] and state['results'][-1] is False,state
    assert state['status'] and state['status']['error']=='true' and state['status']['text'].strip(),state


def preference_invalid(page):
    payloads=['{',json.dumps({'schemaVersion':2,'x':0.2,'y':0.4,'keep':'future'}),
      json.dumps({'schemaVersion':1,'x':'0.2','y':0.4}),
      json.dumps({'schemaVersion':1,'x':-0.1,'y':0.4}),
      json.dumps({'schemaVersion':1,'x':True,'y':0.4}),json.dumps([1,0.2,0.4])]
    facts=[]
    for raw in payloads:
        aux_reload(page,raw);saved=domain(page)
        launcher.default_position(page)
        assert aux_state(page)['raw']==raw,'Invalid envelope was rewritten on load'
        assert not aux_state(page)['attempts'],'Loading invalid preference attempted a write'
        raw_launcher_drag(page)
        rejected=aux_wait(page,0);aux_error(rejected)
        assert rejected['raw']==raw and not rejected['attempts'],rejected
        page.locator('#headerConfigBtn').click();page.evaluate("settingsNavigateToLeaf('interface')")
        expect(page.locator('#mvpNotesPositionStatus')).to_be_visible()
        page.locator('#mvpNotesPositionReset').click()
        reset=aux_wait(page,1)
        assert reset['results'][-1] is True and reset['raw'] is None,reset
        assert reset['attempts']==[{'method':'removeItem'}],reset
        page.locator('#settingsCloseBtn').click();launcher.default_position(page)
        no_domain_change(page,saved,'invalid preference/reset preserves domain')
        facts.append({'input':raw,'rejected':rejected,'reset':reset})
    return facts


def preference_extension(page):
    envelope={'schemaVersion':1,'x':0.65,'y':0.7,'extension':{'label':'preserve me','values':[1,False,None]},'other':17}
    raw=json.dumps(envelope,separators=(',',':'))
    aux_reload(page,raw);saved=domain(page)
    assert aux_state(page)['raw']==raw and not aux_state(page)['attempts']
    raw_launcher_drag(page)
    stored=aux_wait(page,0)
    assert stored['results']==[True] and len(stored['attempts'])==1,stored
    actual=json.loads(stored['raw'])
    assert actual['extension']==envelope['extension'] and actual['other']==17,actual
    assert actual['schemaVersion']==1 and actual['x']==stored['position']['x'] and actual['y']==stored['position']['y'],actual
    assert (actual['x'],actual['y'])!=(envelope['x'],envelope['y']),actual
    no_domain_change(page,saved,'compatible extension preference save')
    return stored


def preference_refusal_retry(page):
    facts=[]
    for mode in ('quota','noop'):
        raw=json.dumps({'schemaVersion':1,'x':0.72,'y':0.74})
        aux_reload(page,raw);saved=domain(page)
        page.evaluate('mode=>window.__notesAuxFixture.mode=mode',mode)
        first,moved=raw_launcher_drag(page)
        rejected=aux_wait(page,0);aux_error(rejected)
        assert rejected['raw']==raw and len(rejected['attempts'])==1,rejected
        assert abs(first['x']-moved['x'])>20 and abs(first['y']-moved['y'])>20,(first,moved)
        assert rejected['position']!={'x':0.72,'y':0.74},rejected
        launcher.contained(page)
        no_domain_change(page,saved,'refused visual preference')
        # Explicit retry calls the same public action; no timer retries are added.
        page.evaluate("window.__notesAuxFixture.mode='normal'")
        result=page.evaluate('mvpNotesPersistLauncherPosition()')
        retried=aux_wait(page,1)
        assert result is True and retried['results']==[False,True],retried
        assert len(retried['attempts'])==2 and retried['status']['error']=='false',retried
        persisted=json.loads(retried['raw'])
        assert persisted['x']==rejected['position']['x'] and persisted['y']==rejected['position']['y'],retried
        no_domain_change(page,saved,'explicit visual retry')
        facts.append({'mode':mode,'rejected':rejected,'retry':retried})
    return facts


def preference_unknown(page):
    raw=json.dumps({'schemaVersion':1,'x':0.72,'y':0.74})
    aux_reload(page,raw);saved=domain(page)
    page.evaluate("window.__notesAuxFixture.mode='unknown'")
    raw_launcher_drag(page)
    uncertain=aux_wait(page,0);aux_error(uncertain)
    assert len(uncertain['attempts'])==1,uncertain
    assert uncertain['raw']!=raw,'Fixture did not establish committed-but-unreadable outcome'
    page.evaluate("window.__notesAuxFixture.mode='normal';window.__notesAuxFixture.unreadable=false")
    result=page.evaluate('mvpNotesPersistLauncherPosition()')
    retry=aux_wait(page,1);aux_error(retry)
    assert result is False and retry['raw']==uncertain['raw'] and retry['attempts']==uncertain['attempts'],retry
    raw_launcher_drag(page,-25,-20)
    gesture=aux_wait(page,2);aux_error(gesture)
    assert gesture['raw']==uncertain['raw'] and gesture['attempts']==uncertain['attempts'],gesture
    no_domain_change(page,saved,'unknown preference blocks blind retry')
    return {'unknown':uncertain,'explicit_retry':retry,'later_gesture':gesture}


def preference_peer_conflict(page):
    raw=json.dumps({'schemaVersion':1,'x':0.72,'y':0.74})
    aux_reload(page,raw)
    peer=page.context.new_page()
    try:
        peer.route('**/dist/assets/**',lambda route:route.continue_(url=route.request.url.replace('/dist/assets/','/assets/')))
        peer.goto(page.url,wait_until='load');launcher.wait_bootstrap(peer)
        peer.evaluate('window.__onbShown=true;closeModal()')
        saved=domain(page)
        page.evaluate("""() => {window.__auxPeerEvent=false;window.addEventListener('storage',e=>{
          if(e.key==='jpwealth_notes_launcher_position_v1')window.__auxPeerEvent=true;
        });}""")
        raw_launcher_drag(page,release=False)
        peer_raw=json.dumps({'schemaVersion':1,'x':0.28,'y':0.34,'peer':'preserved'})
        peer.evaluate('({key,raw})=>localStorage.setItem(key,raw)',{'key':POSITION_KEY,'raw':peer_raw})
        page.wait_for_function('window.__auxPeerEvent===true')
        page.mouse.up();launcher.settle(page)
        conflict=aux_wait(page,0);aux_error(conflict)
        assert conflict['raw']==peer_raw and not conflict['attempts'],conflict
        result=page.evaluate('mvpNotesPersistLauncherPosition()')
        refused=aux_wait(page,1)
        assert result is False and refused['raw']==peer_raw and not refused['attempts'],refused
        no_domain_change(page,saved,'peer position not overwritten')
        return {'conflict':conflict,'later_retry':refused}
    finally:peer.close()


def preference_epoch_callback(page):
    aux_reload(page,None);saved=domain(page)
    page.evaluate("""() => {
      const acquire=sessionAcquireWriteLock;
      window.__auxReleaseLock=null;
      sessionAcquireWriteLock=callback=>new Promise((resolve,reject)=>{
        window.__auxReleaseLock=()=>{
          sessionAcquireWriteLock=acquire;
          Promise.resolve(acquire(callback)).then(resolve,reject);
        };
      });
    }""")
    raw_launcher_drag(page)
    page.wait_for_function("typeof window.__auxReleaseLock==='function'")
    assert not aux_state(page)['attempts'],'Queued writer wrote before receiving the lock'
    # Causal dependency probe: reproduce the finalizer's epoch notification before
    # the pending callback receives its lock. The existing finalization focal owns
    # the complete destructive-session flow; this case owns the stale callback.
    page.evaluate("""() => {
      window.JP_WEALTH_SESSION_WIPE_EPOCH=(Number(window.JP_WEALTH_SESSION_WIPE_EPOCH)||0)+1;
      handleMvpNotesLauncherSessionWipe();
      window.__auxReleaseLock();
    }""")
    late=aux_wait(page,0)
    assert late['results']==[False] and not late['attempts'] and late['raw'] is None,late
    launcher.default_position(page)
    no_domain_change(page,saved,'stale position callback cannot resurrect preference')
    return late


def preference_durable_epoch_race(page):
    setup_reload_diff=aux_reload(page,None)
    saved=domain(page)
    state=page.evaluate("""() => {
      const acquire=sessionAcquireWriteLock;
      window.__auxDurableRace={epochBefore:sessionEpochRead(),
        ramBefore:Number(window.JP_WEALTH_SESSION_WIPE_EPOCH)||0};
      window.__auxReleaseDurableLock=null;
      sessionAcquireWriteLock=callback=>new Promise((resolve,reject)=>{
        window.__auxReleaseDurableLock=()=>{
          sessionAcquireWriteLock=acquire;
          Promise.resolve(acquire(callback)).then(resolve,reject);
        };
      });
      window.__auxRotateDurableFirst=()=>acquire(()=>{
        const next=sessionEpochGenerate();
        if(!next || sessionEpochWriteAndConfirm(next)!==next)throw Error('Synthetic durable epoch rotation failed');
        localStorage.removeItem('jpwealth_notes_launcher_position_v1');
        window.__auxDurableRace.epochAfter=sessionEpochRead();
      });
      return {...window.__auxDurableRace,key:BASE_EPOCH_STORAGE_KEY,serialization:sessionSerializationMode()};
    }""")
    assert state['serialization']=='weblocks',state
    assert isinstance(state['epochBefore'],str) and state['epochBefore'],state
    raw_launcher_drag(page)
    page.wait_for_function("typeof window.__auxReleaseDurableLock==='function'")
    assert not aux_state(page)['attempts'],'Queued preference wrote before callback received lock'
    page.evaluate('window.__auxRotateDurableFirst()')
    rotated=page.evaluate("""() => ({...window.__auxDurableRace,
      ramNow:Number(window.JP_WEALTH_SESSION_WIPE_EPOCH)||0,
      raw:window.__notesAuxFixture.raw(),attempts:window.__notesAuxFixture.attempts})""")
    assert rotated['epochAfter']!=rotated['epochBefore'] and rotated['ramNow']==rotated['ramBefore'],rotated
    assert rotated['raw'] is None,rotated
    # Remove only the fixture's explicit cleanup from the callback-attempt count.
    # Storage remains null; no notice/handleMvpNotesLauncherSessionWipe ran here.
    page.evaluate("window.__notesAuxFixture.attempts=[];window.__auxReleaseDurableLock()")
    late=aux_wait(page,0)
    facts={'setup_reload_diff':setup_reload_diff,'rotation':rotated,'callback':late}
    assert late['results']==[False] and not late['attempts'] and late['raw'] is None,facts
    saved['local'][state['key']]=rotated['epochAfter']
    no_domain_change(page,saved,'durable epoch change blocks callback before RAM notice')
    return facts


def preference_main_document_race(page):
    setup_reload_diff=aux_reload(page,None)
    before=domain(page)
    state=page.evaluate("""() => {
      const acquire=sessionAcquireWriteLock;
      window.__auxMainRace={epochBefore:sessionEpochRead(),
        ramBefore:Number(window.JP_WEALTH_SESSION_WIPE_EPOCH)||0,
        mainBefore:localStorage.getItem(LSKEY)};
      window.__auxReleaseMainLock=null;
      sessionAcquireWriteLock=callback=>new Promise((resolve,reject)=>{
        window.__auxReleaseMainLock=()=>{
          sessionAcquireWriteLock=acquire;
          Promise.resolve(acquire(callback)).then(resolve,reject);
        };
      });
      // A real, established financial-cadastro API changes the main document
      // while the old preference callback is still waiting for its lock.
      window.__auxFinancialWriteFirst=()=>acquire(()=>{
        const result=JPWAlladin.cadastro.addAccount({name:'Conta sintética corrida Notes',
          institution:'Fixture Notes',accountType:'BANK'});
        return {...result,epochAfter:sessionEpochRead(),
          ramAfter:Number(window.JP_WEALTH_SESSION_WIPE_EPOCH)||0,
          mainChanged:localStorage.getItem(LSKEY)!==window.__auxMainRace.mainBefore,
          persistedAccount:JSON.parse(localStorage.getItem(LSKEY)).alladin.accounts
            .some(account=>account.accountId===result.recordId)};
      });
      return {epochBefore:window.__auxMainRace.epochBefore,
        ramBefore:window.__auxMainRace.ramBefore,serialization:sessionSerializationMode()};
    }""")
    assert state['serialization']=='weblocks',state
    raw_launcher_drag(page)
    page.wait_for_function("typeof window.__auxReleaseMainLock==='function'")
    assert not aux_state(page)['attempts'],'Queued preference wrote before receiving its lock'
    financial=page.evaluate('window.__auxFinancialWriteFirst()')
    assert financial['ok'] is True and financial['persistido'] is True and financial['persistedAccount'],financial
    assert financial['mainChanged'] and financial['epochAfter']==state['epochBefore'],financial
    assert financial['ramAfter']==state['ramBefore'],financial
    assert aux_state(page)['raw'] is None and not aux_state(page)['attempts']
    saved=domain(page)
    assert json.loads(saved['state'])['mvpNotes']==json.loads(before['state'])['mvpNotes']
    page.evaluate('window.__auxReleaseMainLock()')
    late=aux_wait(page,0)
    facts={'setup_reload_diff':setup_reload_diff,'initial':state,'financial_write':financial,
      'financial_diff':domain_diff(before,saved),'callback':late}
    assert late['results']==[False] and not late['attempts'] and late['raw'] is None,facts
    no_domain_change(page,saved,'main document changed before notice blocks queued preference')
    return facts


# CHG-UX-NOTES-MENUS-20261102: approved autosave replaces the historical
# initial-modal/manual-save contract. Permanent cases use real UI/storage.
def autosave_direct(page):
    open_notes(page)
    before=page.evaluate('localStorage.getItem(LSKEY)')
    page.locator('#mvpNotesNewBtn').click()
    assert visible(page,'mvpNoteContent') and not visible(page,'mvpNotesNewOverlay'), 'Nova nota must enter the editor directly'
    assert page.evaluate('localStorage.getItem(LSKEY)')==before, 'Opening a blank note must be read-only'
    page.locator('#mvpNoteContent').fill('Primeiro conteúdo sintético')
    assert page.evaluate("JSON.parse(localStorage.getItem(LSKEY)).mvpNotes.items.some(n=>n.content==='Primeiro conteúdo sintético')"), 'First nonempty input must be confirmed immediately'
    identity=page.evaluate('({id:mvpNotesUI.selectedId,ticket:S.mvpNotes.items.find(n=>n.id===mvpNotesUI.selectedId).ticket})')
    assert page.locator('.mvpn-card[data-mvp-note-id="'+identity['id']+'"]').count()==1
    page.locator('#mvpNoteContent').fill('Segundo conteúdo sintético')
    page.locator('#mvpNoteContent').evaluate('e=>{e.setSelectionRange(3,8);e.scrollTop=0}')
    page.wait_for_timeout(650)
    assert page.evaluate("JSON.parse(localStorage.getItem(LSKEY)).mvpNotes.items.find(n=>n.id===mvpNotesUI.selectedId).content")=='Segundo conteúdo sintético'
    assert page.locator('#mvpNoteContent').evaluate('e=>[document.activeElement===e,e.selectionStart,e.selectionEnd]')==[True,3,8]
    assert page.evaluate('S.mvpNotes.items.find(n=>n.id===mvpNotesUI.selectedId).ticket')==identity['ticket']
    for i in range(12):
        page.locator('#mvpNoteContent').fill('Fluxo contínuo '+str(i));page.wait_for_timeout(190)
    assert page.evaluate("JSON.parse(localStorage.getItem(LSKEY)).mvpNotes.items.find(n=>n.id===mvpNotesUI.selectedId).content").startswith('Fluxo contínuo'), 'maxWait must confirm during continuous typing'
    page.locator('#mvpNotesCloseBtn').click()
    assert page.evaluate("JSON.parse(localStorage.getItem(LSKEY)).mvpNotes.items.find(n=>n.id==='"+identity['id']+"').content")=='Fluxo contínuo 11'
    return identity


def autosave_scoped(page):
    open_notes(page);page.evaluate('mvpNotesBeginNewNote()')
    before=page.evaluate('JSON.parse(localStorage.getItem(LSKEY))')
    page.evaluate("S.personalFinance.__syntheticDirtyFinancial='RAM ONLY'; S.__syntheticDirtyOther={value:91}")
    page.locator('#mvpNoteContent').fill('Nota com fronteira financeira')
    after=page.evaluate('JSON.parse(localStorage.getItem(LSKEY))')
    assert any(n['content']=='Nota com fronteira financeira' for n in after['mvpNotes']['items']), 'First input did not save'
    assert {k:v for k,v in after.items() if k!='mvpNotes'}=={k:v for k,v in before.items() if k!='mvpNotes'}, 'Notes must preserve confirmed foreign document fields exactly'
    assert page.evaluate("S.personalFinance.__syntheticDirtyFinancial")=='RAM ONLY'
    assert page.evaluate('S.__syntheticDirtyOther.value')==91
    return {'foreign_document_preserved':True}


def autosave_empty(page):
    open_notes(page);select_first(page)
    ident=page.evaluate('mvpNotesUI.selectedId')
    page.locator('#mvpNoteContent').fill('')
    page.wait_for_timeout(650)
    page.locator('#mvpNotesCloseBtn').click()
    page.reload(wait_until='load');launcher.settle(page)
    assert page.evaluate('(id)=>S.mvpNotes.items.find(n=>n.id===id)?.content',ident)=='', 'A previously saved blank note must survive normalization/reload'
    open_notes(page);page.evaluate('(id)=>mvpNotesSelectNote(id)',ident)
    assert page.locator('#mvpNoteContent').input_value()==''
    assert page.locator('#mvpNotesEditorTitle').text_content()=='Nota sem título'
    # Legacy JSON remains an accepted real import path. Restore the erased note
    # through the application's file input, independently of its normalizer API.
    backup=page.evaluate("({tipo:'jpwealth_full_backup',state:JSON.parse(localStorage.getItem(LSKEY))})")
    page.locator('#mvpNotesCloseBtn').click();page.locator('#headerConfigBtn').click()
    page.evaluate("settingsNavigateToLeaf('backup');S.mvpNotes.items=[];window.confirm=()=>true")
    page.locator('#importFullBackupInput').set_input_files({'name':'synthetic-empty-note.json','mimeType':'application/json','buffer':json.dumps(backup).encode()})
    page.wait_for_function('(id)=>S.mvpNotes.items.some(n=>n.id===id&&n.content==="")',arg=ident)
    assert page.evaluate('(id)=>JSON.parse(localStorage.getItem(LSKEY)).mvpNotes.items.find(n=>n.id===id)?.content',ident)==''
    return {'empty_note_id':ident,'real_legacy_json_import_preserved_blank':True}


def autosave_refused(page):
    open_notes(page);page.evaluate('mvpNotesBeginNewNote()')
    before=page.evaluate('localStorage.getItem(LSKEY)')
    page.evaluate("""() => {window.__notesRealSet=Storage.prototype.setItem;window.__notesAttempts=0;
      Storage.prototype.setItem=function(k,v){if(this===localStorage&&k===LSKEY){window.__notesAttempts++;return;}return window.__notesRealSet.call(this,k,v)};}""")
    page.locator('#mvpNoteContent').fill('Rascunho recusado')
    identity=page.evaluate('mvpNotesAutosave.session.identity')
    assert page.evaluate('localStorage.getItem(LSKEY)')==before
    assert page.evaluate('mvpNotesUI.draftDirty') and page.locator('#mvpNotesSaveStatus').inner_text().startswith('Não foi possível salvar')
    page.locator('#mvpNoteContent').fill('Rascunho recusado preservado');page.wait_for_timeout(2200)
    assert page.evaluate('window.__notesAttempts')==1, 'Refusal must stop automatic retries'
    page.locator('#mvpNotesCloseBtn').click()
    assert visible(page,'mvpNotesOverlay') and page.locator('#mvpNoteContent').input_value()=='Rascunho recusado preservado'
    page.evaluate('()=>{Storage.prototype.setItem=window.__notesRealSet;}')
    page.locator('#mvpNotesSaveBtn').click()
    assert page.evaluate('(id)=>JSON.parse(localStorage.getItem(LSKEY)).mvpNotes.items.filter(n=>n.id===id).length',identity['id'])==1
    assert page.evaluate('mvpNotesUI.selectedId')==identity['id']
    assert page.evaluate('(id)=>S.mvpNotes.items.find(n=>n.id===id).ticket',identity['id'])==identity['ticket']
    assert not page.evaluate('mvpNotesUI.draftDirty')
    return {'refused_preserved':True,'explicit_retry_same_identity':identity}


def autosave_unknown(page):
    open_notes(page);page.evaluate('mvpNotesBeginNewNote()')
    page.evaluate("""() => {window.__notesRealSet=Storage.prototype.setItem;window.__notesRealGet=Storage.prototype.getItem;window.__notesAttempts=0;window.__notesReadPending=false;
      Storage.prototype.setItem=function(k,v){const r=window.__notesRealSet.call(this,k,v);if(this===localStorage&&k===LSKEY){window.__notesAttempts++;window.__notesReadPending=true;}return r;};
      Storage.prototype.getItem=function(k){if(this===localStorage&&k===LSKEY&&window.__notesReadPending){window.__notesReadPending=false;throw Error('synthetic unreadable readback');}return window.__notesRealGet.call(this,k);};}""")
    page.locator('#mvpNoteContent').fill('Resultado desconhecido')
    assert page.evaluate('jpWealthPersistenceOutcomeIsUnknown()')
    assert page.evaluate("mvpNotesUI.draft.content")=='Resultado desconhecido'
    assert page.locator('#mvpNotesSaveBtn').is_disabled()
    assert 'não confirmada' in page.locator('#mvpNotesSaveStatus').inner_text()
    page.locator('#mvpNoteContent').fill('Rascunho após UNKNOWN');page.wait_for_timeout(2200)
    page.evaluate('mvpNotesSaveDraft()')
    assert page.evaluate('window.__notesAttempts')==1, 'UNKNOWN must block every repeat'
    assert page.evaluate('mvpNotesUI.draftDirty')
    return {'unknown_blocked':True}


def autosave_ime_metadata(page):
    open_notes(page);page.evaluate('mvpNotesBeginNewNote()')
    before=page.evaluate('localStorage.getItem(LSKEY)')
    area=page.locator('#mvpNoteContent')
    area.dispatch_event('compositionstart');area.fill('Composição sintética');page.wait_for_timeout(650)
    assert page.evaluate('localStorage.getItem(LSKEY)')==before, 'Composing input must not commit'
    area.dispatch_event('compositionend')
    assert page.evaluate('mvpNotesUI.selectedId')
    original=page.evaluate('mvpNotesUI.draftOriginal')
    page.locator('#mvpNotesInspectorBtn').click()
    page.locator('#mvpNotePolicy').select_option('autonomous_allowed')
    page.locator('#mvpNotePriority').select_option('critical')
    area.fill('Texto salvo sem autorizar IA');page.wait_for_timeout(650)
    saved=page.evaluate('S.mvpNotes.items.find(n=>n.id===mvpNotesUI.selectedId)')
    assert saved['content']=='Texto salvo sem autorizar IA' and saved['aiImplementationPolicy']==original['aiImplementationPolicy'] and saved['priority']==original['priority'], 'Typing must not commit pending metadata/policy'
    assert page.evaluate('mvpNotesUI.draftDirty') and 'detalhes não confirmados' in page.locator('#mvpNotesSaveStatus').inner_text()
    page.evaluate('window.confirm=()=>false');page.locator('#mvpNotesConfirmMetadataBtn').click()
    assert page.evaluate('S.mvpNotes.items.find(n=>n.id===mvpNotesUI.selectedId).aiImplementationPolicy')==original['aiImplementationPolicy']
    page.evaluate('window.__policyConfirmation=null;window.confirm=text=>{window.__policyConfirmation=text;return true;}')
    page.locator('#mvpNotesConfirmMetadataBtn').click()
    assert 'política de IA' in page.evaluate('window.__policyConfirmation')
    saved=page.evaluate('S.mvpNotes.items.find(n=>n.id===mvpNotesUI.selectedId)')
    assert saved['aiImplementationPolicy']=='autonomous_allowed' and saved['priority']=='critical'
    assert not page.evaluate('mvpNotesUI.draftDirty')
    return {'ime_waited':True,'text_did_not_authorize':True,'policy_confirmed_explicitly':True}


def autosave_context(page):
    open_notes(page);select_first(page)
    page.locator('#mvpNoteContent').fill('Callback antigo deve ser inválido')
    before=page.evaluate('localStorage.getItem(LSKEY)')
    page.evaluate('blockJPWealthPersistence();resumeJPWealthPersistence()')
    page.wait_for_timeout(2200)
    assert page.evaluate('localStorage.getItem(LSKEY)')==before
    assert page.evaluate('mvpNotesUI.draft.content')=='Callback antigo deve ser inválido'
    page.evaluate('mvpNotesSaveDraft()')
    assert page.evaluate('localStorage.getItem(LSKEY)')==before
    return {'old_epoch_did_not_write':True}


def autosave_peer(page):
    open_notes(page);select_first(page)
    ident=page.evaluate('mvpNotesUI.selectedId')
    page.locator('#mvpNoteContent').fill('Rascunho local em conflito')
    # Pause composition to keep the draft pending while a real peer writes.
    page.locator('#mvpNoteContent').dispatch_event('compositionstart')
    peer=page.context.new_page();peer.goto(page.url,wait_until='load');launcher.wait_bootstrap(peer)
    peer.evaluate("""id=>{window.__onbShown=true;closeModal();const note=S.mvpNotes.items.find(n=>n.id===id);note.content='Conteúdo confirmado por outra aba';note.title=note.content;if(save()!==true)throw Error('synthetic peer write failed');}""",ident)
    peer_raw=peer.evaluate('localStorage.getItem(LSKEY)')
    page.locator('#mvpNoteContent').dispatch_event('compositionend');page.wait_for_timeout(650)
    assert page.evaluate('localStorage.getItem(LSKEY)')==peer_raw
    assert page.evaluate('mvpNotesUI.draft.content')=='Rascunho local em conflito'
    assert page.evaluate('mvpNotesUI.draftDirty')
    assert 'Não foi possível salvar' in page.locator('#mvpNotesSaveStatus').inner_text()
    peer.close()
    return {'peer_preserved':True,'draft_retained':True}


def autosave_fresh_extensions(page):
    # Reuse this isolated synthetic origin; never inspect a user's profile.
    page.evaluate("""() => {localStorage.removeItem(LSKEY);localStorage.removeItem(BASE_EPOCH_STORAGE_KEY);jpWealthAdoptPersistedRaw(null);S.personalFinance.__freshDirty='RAM ONLY';S.__foreignDirty=99;}""")
    open_notes(page);page.evaluate('mvpNotesBeginNewNote()')
    page.locator('#mvpNoteContent').fill('Primeira nota sem base financeira')
    saved=page.evaluate('JSON.parse(localStorage.getItem(LSKEY))')
    assert isinstance(saved,dict), 'First note must save on a virgin origin without an epoch key'
    assert '__freshDirty' not in saved['personalFinance'] and '__foreignDirty' not in saved
    assert page.evaluate('S.personalFinance.__freshDirty')=='RAM ONLY'
    ident=page.evaluate('mvpNotesUI.selectedId')
    page.evaluate("""id=>{const item=S.mvpNotes.items.find(n=>n.id===id);item.extension={preserve:'synthetic'};S.__confirmedExtension={keep:true};S.accounts=[{id:'synthetic-credential',investorPassword:'SYNTHETIC-SESSION-ONLY'}];if(save()!==true)throw Error('fixture checkpoint failed');mvpNotesCloseEditor();mvpNotesSelectNote(id);}""",ident)
    page.locator('#mvpNoteContent').fill('Extensão permanece na mesma nota');page.wait_for_timeout(650)
    saved=page.evaluate('JSON.parse(localStorage.getItem(LSKEY))')
    assert next(n for n in saved['mvpNotes']['items'] if n['id']==ident)['extension']=={'preserve':'synthetic'}
    assert saved['__confirmedExtension']=={'keep':True} and saved['accounts'][0]['investorPassword']==''
    return {'fresh_does_not_promote_dirty_ram':True,'extension_and_secret_guard':True}


def autosave_filtered_new(page):
    open_notes(page)
    page.evaluate("mvpNotesSwitchFolder('done');mvpNotesUI.query='não corresponde';mvpNotesUI.filterType='bug';mvpNotesUI.filterPriority='critical';renderMvpNotesList()")
    page.locator('#mvpNotesNewBtn').click()
    page.locator('#mvpNoteContent').fill('Nova nota visível sem alterar padrões')
    note=page.evaluate('S.mvpNotes.items.find(n=>n.id===mvpNotesUI.selectedId)')
    assert note['type']=='task' and note['status']=='open' and note['priority']=='medium' and note['folderId'] is None
    assert page.locator('.mvpn-card[data-mvp-note-id="'+note['id']+'"]').is_visible(), 'A newly written note must appear beside the editor even after search/Concluído'
    page.evaluate('(id)=>{mvpNotesSwitchFolder(id);mvpNotesUI.query="outro filtro";renderMvpNotesList()}',page.evaluate('S.mvpNotes.folders[0].id'))
    page.locator('#mvpNotesNewBtn').click();page.locator('#mvpNoteContent').fill('Nova nota na pasta atual')
    note=page.evaluate('S.mvpNotes.items.find(n=>n.id===mvpNotesUI.selectedId)')
    assert note['folderId']==page.evaluate('S.mvpNotes.folders[0].id')
    assert page.locator('.mvpn-card[data-mvp-note-id="'+note['id']+'"]').is_visible()
    return {'new_note_visible_with_safe_defaults':True}


def autosave_divergent_ram(page):
    page.evaluate("S.mvpNotes.items[0].content='RAM de nota ainda não confirmada';S.mvpNotes.items[0].title='RAM de nota ainda não confirmada'")
    open_notes(page);page.evaluate('mvpNotesSelectNote(S.mvpNotes.items[0].id)')
    assert page.locator('#mvpNotesSaveStatus').inner_text()!='Salvo', 'RAM presence alone cannot announce Saved'
    before=page.evaluate('localStorage.getItem(LSKEY)')
    assert page.evaluate('mvpNotesSaveDraft()') is False, 'Retry without a content change must not bless divergent RAM'
    assert page.locator('#mvpNotesSaveStatus').inner_text()!='Salvo', 'No-op retry must verify its confirmed item base'
    assert page.evaluate('localStorage.getItem(LSKEY)')==before
    page.locator('#mvpNoteContent').fill('Texto após RAM divergente');page.wait_for_timeout(650)
    assert page.evaluate('localStorage.getItem(LSKEY)')==before
    assert page.evaluate('mvpNotesUI.draft.content')=='Texto após RAM divergente'
    return {'divergent_ram_never_announced_saved':True}


def autosave_lifecycle(page):
    open_notes(page);page.evaluate('mvpNotesBeginNewNote()')
    page.evaluate("""()=>{window.__notesLifecycle=[];document.addEventListener('jpw-notes-save',event=>{
      window.__notesLifecycle.push({detail:event.detail,dirty:mvpNotesUI.draftDirty,content:mvpNotesUI.draft.content,
        disk:JSON.parse(localStorage.getItem(LSKEY))?.mvpNotes.items.find(n=>n.id===mvpNotesUI.selectedId)?.content||null});
    });}""")
    page.locator('#mvpNoteContent').fill('Primeira edição confiável')
    rows=page.evaluate('window.__notesLifecycle')
    assert len(rows)==2, 'A real edit must emit before and after lifecycle notifications'
    before,after=rows
    assert before['detail']['phase']=='before' and before['dirty'] and before['content']=='Primeira edição confiável'
    assert after['detail']['phase']=='after' and after['detail']['status']=='CONFIRMED' and after['disk']=='Primeira edição confiável'
    assert before['detail']['editToken']==after['detail']['editToken'] and before['detail']['trustedEdit'] is True
    assert set(before['detail'])=={'phase','editToken','trustedEdit','status'}, 'Lifecycle details must not transport note content or identifiers'
    page.locator('#mvpNotesInspectorBtn').click();page.locator('#mvpNotePriority').select_option('critical');page.locator('#mvpNotesConfirmMetadataBtn').click()
    rows=page.evaluate('window.__notesLifecycle')
    assert len(rows)==4 and rows[-1]['detail']['editToken'] is None and rows[-1]['detail']['trustedEdit'] is False, 'Metadata confirmation cannot manufacture a text-edit practice'
    page.locator('#mvpNotesConfirmMetadataBtn').click()
    assert len(page.evaluate('window.__notesLifecycle'))==4, 'An unchanged detail confirmation must not emit save events'
    return {'correlated_confirmed_lifecycle':True}


def autosave_reverted(page):
    open_notes(page);select_first(page)
    area=page.locator('#mvpNoteContent');original=area.input_value()
    raw=page.evaluate('localStorage.getItem(LSKEY)')
    area.fill('Alteração transitória');area.fill(original);page.wait_for_timeout(650)
    assert page.evaluate('localStorage.getItem(LSKEY)')==raw, 'Reverting to the confirmed text must not write'
    assert page.locator('#mvpNotesSaveStatus').inner_text()=='Salvo', 'A reverted draft cannot remain Salvando…'
    assert page.evaluate('mvpNotesAutosave.timer===null&&mvpNotesAutosave.maxTimer===null')
    page.locator('#mvpNotesInspectorBtn').click();page.locator('#mvpNotePriority').select_option('critical')
    area.fill('Outra alteração transitória');area.fill(original);page.wait_for_timeout(650)
    assert page.evaluate('localStorage.getItem(LSKEY)')==raw
    assert page.locator('#mvpNotesSaveStatus').inner_text()=='Texto salvo · detalhes não confirmados'
    return {'reverted_text_no_write_truthful_status':True}


def autosave_metadata_status(page):
    # Exercise the bound inspector select, including a REFUSED draft reverted to
    # equality: a valid base alone must never turn metadata into implicit retry.
    results=[]
    failures=[]
    for scenario in ('confirmed','divergent','refused','unknown','changed-base','global-unknown','recovered'):
        if results:
            page.reload(wait_until='load');launcher.settle(page)
        if scenario=='divergent':
            page.evaluate("S.mvpNotes.items[0].content='Unconfirmed RAM text';S.mvpNotes.items[0].title='Unconfirmed RAM text'")
        open_notes(page);page.evaluate('mvpNotesSelectNote(S.mvpNotes.items[0].id)')
        area=page.locator('#mvpNoteContent');original=area.input_value()
        page.locator('#mvpNotesInspectorBtn').click()
        page.locator('#mvpNoteType').focus()
        page.evaluate("""() => {
          window.__metadataSet=Storage.prototype.setItem;
          window.__metadataGet=Storage.prototype.getItem;
          window.__metadataAttempts=0;window.__metadataMode='count';window.__metadataReadPending=false;
          Storage.prototype.setItem=function(k,v){
            if(this===localStorage&&k===LSKEY){
              window.__metadataAttempts++;
              if(window.__metadataMode==='refused')return;
              const result=window.__metadataSet.call(this,k,v);
              if(window.__metadataMode==='unknown')window.__metadataReadPending=true;
              return result;
            }
            return window.__metadataSet.call(this,k,v);
          };
          Storage.prototype.getItem=function(k){
            if(this===localStorage&&k===LSKEY&&window.__metadataReadPending){
              window.__metadataReadPending=false;throw Error('synthetic unreadable readback');
            }
            return window.__metadataGet.call(this,k);
          };
          S.personalFinance.__metadataDirty='RAM ONLY';
        }""")
        if scenario in ('refused','unknown'):
            page.evaluate('(mode)=>window.__metadataMode=mode',scenario)
            area.fill('Text whose write is '+scenario);page.wait_for_timeout(650)
            assert page.evaluate('mvpNotesAutosave.blocked'),scenario
            # Reverting text is not an explicit retry either.
            area.fill(original)
        elif scenario=='changed-base':
            page.evaluate("""() => {
              const next=JSON.parse(localStorage.getItem(LSKEY));
              next.mvpNotes.items.find(n=>n.id===mvpNotesUI.selectedId).content='Externally changed confirmed text';
              window.__metadataSet.call(localStorage,LSKEY,JSON.stringify(next));
            }""")
        elif scenario=='global-unknown':
            # Another persistence consumer can raise UNKNOWN while Notes still
            # displays its preceding confirmed status and has not blocked yet.
            page.evaluate("markJPWealthPersistenceOutcomeUnknown('READ_AFTER_WRITE')")
            assert not page.evaluate('mvpNotesAutosave.blocked')
            assert page.locator('#mvpNotesSaveStatus').inner_text()=='Salvo'
        elif scenario=='recovered':
            area.fill('Recovered RAM requires confirmation')
            reopened=page.evaluate("""() => {
              const item=jpwWorkspaceDraftProviders.get('notes')(false).find(i=>i.context.kind==='note');
              mvpNotesCloseEditor();return JPWWorkspaceDrafts.reopen(item);
            }""")
            assert reopened['ok']
            assert page.evaluate('mvpNotesAutosave.recovered')
        if not visible(page,'mvpNoteType'):
            page.locator('#mvpNotesInspectorBtn').click()
        select=page.locator('#mvpNoteType')
        assert select.count()==1, {'scenario':scenario,'completed':results,'inspector':page.evaluate('({open:mvpNotesUI.inspectorOpen,draft:!!mvpNotesUI.draft,status:mvpNotesAutosave.status})')}
        select.focus()
        initial=page.evaluate("""() => {
          window.__metadataArea=mvpn('mvpNoteContent');
          return {type:mvpNotesUI.draft.type,status:mvpNotesAutosave.status,
            blocked:mvpNotesAutosave.blocked,identity:{...mvpNotesAutosave.session.identity},
            draft:{...mvpNotesUI.draft},attempts:window.__metadataAttempts};
        }""")
        before=domain(page)
        select.select_option('bug' if initial['type']!='bug' else 'task')
        edited=page.locator('#mvpNotesSaveStatus').inner_text()
        select.select_option(initial['type']);page.wait_for_timeout(2200)
        final=page.evaluate("""() => ({status:mvpNotesAutosave.status,blocked:mvpNotesAutosave.blocked,
          unknown:jpWealthPersistenceOutcomeIsUnknown(),retryDisabled:mvpn('mvpNotesSaveBtn').disabled,
          identity:{...mvpNotesAutosave.session.identity},draft:{...mvpNotesUI.draft},
          attempts:window.__metadataAttempts,focus:document.activeElement===mvpn('mvpNoteType'),
          sameEditor:window.__metadataArea===mvpn('mvpNoteContent'),
          financialRam:S.personalFinance.__metadataDirty})""")
        checks={
          'no_storage_or_domain_change':domain(page)==before,
          'no_automatic_write':final['attempts']==initial['attempts'],
          'draft_and_identity_retained':final['draft']==initial['draft'] and final['identity']==initial['identity'],
          'focus_and_editor_retained':final['focus'] and final['sameEditor'],
          'financial_ram_retained':final['financialRam']=='RAM ONLY',
        }
        if scenario=='confirmed':
            checks.update(confirmed_reversal_saved=final['status']=='Salvo' and not final['blocked'],
              metadata_pending_visible=edited=='Detalhes não confirmados')
        else:
            checks.update(never_saved='salvo' not in edited.lower() and 'salvo' not in final['status'].lower(),
              block_retained=final['blocked'] if scenario!='recovered' else not final['blocked'])
            if scenario not in ('changed-base','global-unknown'):
                checks['failure_guidance_retained']=edited==initial['status']==final['status']
            if scenario in ('unknown','global-unknown'):
                checks['unknown_retry_disabled']=final['unknown'] and final['retryDisabled']
            elif scenario=='refused':
                checks['refused_requires_explicit_retry']=not final['retryDisabled']
        result={'scenario':scenario,'checks':checks,'initial_status':initial['status'],
          'edited_status':edited,'final':final}
        results.append(result)
        failures.extend(scenario+': '+name for name,ok in checks.items() if not ok)
    assert not failures, {'failures':failures,'scenarios':results}
    return {'real_inspector_metadata_status':results}


def autosave_delete_dispose(page):
    open_notes(page);select_first(page)
    ident=page.evaluate('mvpNotesUI.selectedId')
    page.locator('#mvpNoteContent').fill('Texto pendente antes da exclusão')
    page.evaluate('(id)=>{if(!mvpNotesDelete(id))throw Error("synthetic delete refused")}',ident)
    page.wait_for_timeout(2200)
    assert page.evaluate('(id)=>!JSON.parse(localStorage.getItem(LSKEY)).mvpNotes.items.some(n=>n.id===id)',ident), 'Deleting through the original CRUD API must invalidate a pending writer'
    assert page.evaluate('mvpNotesAutosave.timer===null&&mvpNotesAutosave.maxTimer===null&&mvpNotesAutosave.session===null')
    page.evaluate('mvpNotesSelectNote(S.mvpNotes.items[0].id)')
    page.locator('#mvpNoteContent').fill('Texto pendente antes de finalizar')
    raw=page.evaluate('localStorage.getItem(LSKEY)')
    page.evaluate('sessionResetAuxiliarySurfaces()')
    page.wait_for_timeout(2200)
    assert page.evaluate('localStorage.getItem(LSKEY)')==raw, 'Session disposal must invalidate pending Notes timers'
    assert page.evaluate('mvpNotesAutosave.timer===null&&mvpNotesAutosave.maxTimer===null&&mvpNotesAutosave.session===null')
    return {'selected_delete_never_resurrected':True,'session_dispose_did_not_write':True}


def autosave_recovered_draft(page):
    open_notes(page);select_first(page)
    page.locator('#mvpNoteContent').fill('Rascunho recuperado para conferência')
    recovered=page.evaluate("()=>{const item=jpwWorkspaceDraftProviders.get('notes')(false).find(i=>i.context.kind==='note');mvpNotesCloseEditor();return {item,result:JPWWorkspaceDrafts.reopen(item)};}")
    assert recovered['result']['ok']
    raw=page.evaluate('localStorage.getItem(LSKEY)')
    page.locator('#mvpNotesSearch').focus();page.wait_for_timeout(650)
    assert page.evaluate('localStorage.getItem(LSKEY)')==raw, 'Reopening recovered fields and blurring must preserve confirmed facts'
    assert page.evaluate('mvpNotesUI.draftDirty')
    page.locator('#mvpNotesSaveBtn').click()
    assert page.evaluate('S.mvpNotes.items.find(n=>n.id===mvpNotesUI.selectedId).content')=='Rascunho recuperado para conferência'
    page.locator('#mvpNoteContent').fill('Segundo rascunho recuperado')
    page.evaluate("mvpNotesUI.draft.aiImplementationPolicy='autonomous_allowed';mvpNotesRecomputeDirty()")
    recovered=page.evaluate("()=>{const item=jpwWorkspaceDraftProviders.get('notes')(false).find(i=>i.context.kind==='note');mvpNotesCloseEditor();return JPWWorkspaceDrafts.reopen(item);}")
    assert recovered['ok']
    page.locator('#mvpNoteContent').fill('Edição nativa após recuperação');page.wait_for_timeout(650)
    note=page.evaluate('S.mvpNotes.items.find(n=>n.id===mvpNotesUI.selectedId)')
    assert note['content']=='Edição nativa após recuperação' and note['aiImplementationPolicy']=='analysis_only'
    assert page.evaluate('mvpNotesUI.draftDirty')
    return {'reopen_did_not_promote_facts':True,'native_edit_did_not_promote_recovered_policy':True}


def autosave_legacy_erasure(page):
    backup=page.evaluate("()=>{const state=JSON.parse(localStorage.getItem(LSKEY));state.mvpNotes={...state.mvpNotes,schemaVersion:4,items:[{id:'review-v4-empty',title:'Imported legacy title',description:'Original legacy body',type:'task',priority:'medium',status:'open',folderId:null,createdAt:'2025-01-01',updatedAt:'2025-01-01',extension:{keep:true}}]};return {tipo:'jpwealth_full_backup',state};}")
    def import_backup(value):
        page.locator('#headerConfigBtn').click();page.evaluate("settingsNavigateToLeaf('backup');window.confirm=()=>true")
        page.locator('#importFullBackupInput').set_input_files({'name':'synthetic-v4-empty-review.json','mimeType':'application/json','buffer':json.dumps(value).encode()})
        page.wait_for_function("S.mvpNotes.items.some(n=>n.id==='review-v4-empty')")
        page.evaluate('closeSettingsModal()')
    import_backup(backup)
    assert page.evaluate("S.mvpNotes.items[0].content")=='Imported legacy title\nOriginal legacy body'
    open_notes(page);page.evaluate("mvpNotesSelectNote('review-v4-empty')")
    page.locator('#mvpNoteContent').fill('');page.wait_for_timeout(650)
    assert page.evaluate("JSON.parse(localStorage.getItem(LSKEY)).mvpNotes.items[0].content")==''
    page.locator('#mvpNotesCloseBtn').click();page.reload(wait_until='load');launcher.wait_bootstrap(page)
    assert page.evaluate("S.mvpNotes.items.find(n=>n.id==='review-v4-empty').content")=='', 'Erasing an imported v4 note must not replay its legacy description on reload'
    assert page.evaluate("S.mvpNotes.items[0].extension.keep") is True
    empty_backup=page.evaluate("({tipo:'jpwealth_full_backup',state:JSON.parse(localStorage.getItem(LSKEY))})")
    import_backup(empty_backup)
    assert page.evaluate("S.mvpNotes.items.find(n=>n.id==='review-v4-empty').content")=='', 'Reimport must preserve explicit blank content over retained legacy fields'
    return {'v4_erasure_reload_import_preserved':True}


def autosave_legacy_missing_dates(page):
    page.evaluate("()=>{const state=JSON.parse(localStorage.getItem(LSKEY));state.mvpNotes={...state.mvpNotes,schemaVersion:4,folders:[{id:'review-legacy-folder',name:'Legacy folder'}],items:[{id:'review-no-dates',title:'Accepted old note',description:'Original legacy body',folderId:'review-legacy-folder',type:'task',priority:'medium',status:'open',extension:{keep:true}}]};localStorage.setItem(LSKEY,JSON.stringify(state));}")
    page.reload(wait_until='load');launcher.wait_bootstrap(page)
    page.evaluate("()=>{window.__onbShown=true;closeModal();window.__reviewDate=Date;window.__reviewNow=Date.now()+10000;window.Date=class extends window.__reviewDate{constructor(...args){super(...(args.length?args:[window.__reviewNow]));}static now(){return window.__reviewNow;}};}")
    before=page.evaluate('JSON.parse(localStorage.getItem(LSKEY))')
    migrated=page.evaluate('structuredClone(S.mvpNotes)')
    open_notes(page);page.evaluate("mvpNotesSelectNote('review-no-dates')")
    assert page.locator('#mvpNotesSaveStatus').inner_text()=='Salvo', 'Accepted legacy timestamps must stabilize across load and confirmed-base checks'
    page.evaluate("S.personalFinance.__reviewDirty='RAM ONLY';S.__reviewUnconfirmed={value:73}")
    page.locator('#mvpNoteContent').fill('Edited accepted legacy note');page.wait_for_timeout(650)
    after=page.evaluate('JSON.parse(localStorage.getItem(LSKEY))')
    note=next(n for n in after['mvpNotes']['items'] if n['id']=='review-no-dates')
    assert note['content']=='Edited accepted legacy note' and note['extension']=={'keep':True}
    assert note['createdAt']==migrated['items'][0]['createdAt']
    assert {k:v for k,v in after.items() if k!='mvpNotes'}=={k:v for k,v in before.items() if k!='mvpNotes'}, 'Legacy compatibility must not promote adjacent dirty financial RAM'
    assert page.evaluate('S.personalFinance.__reviewDirty')=='RAM ONLY'
    assert after['mvpNotes']['folders']==before['mvpNotes']['folders'], 'Editing the note must preserve untouched legacy folder bytes'
    return {'legacy_missing_dates_scoped_edit':True}


def autosave_legacy_missing_ids_refused(page):
    page.evaluate("()=>{const state=JSON.parse(localStorage.getItem(LSKEY));state.mvpNotes={...state.mvpNotes,schemaVersion:4,folders:[{name:'Accepted unidentified folder'}],items:[{title:'Accepted unidentified note',description:'Legacy text without identity',type:'task',priority:'medium',status:'open',createdAt:'2025-01-01',updatedAt:'2025-01-01'}]};localStorage.setItem(LSKEY,JSON.stringify(state));}")
    page.reload(wait_until='load');launcher.wait_bootstrap(page);page.evaluate('window.__onbShown=true;closeModal()')
    assert page.evaluate('S.mvpNotes.items.length===1&&S.mvpNotes.folders.length===1')
    before=page.evaluate('localStorage.getItem(LSKEY)')
    open_notes(page);page.evaluate('mvpNotesSelectNote(S.mvpNotes.items[0].id)')
    page.locator('#mvpNoteContent').fill('Recoverable draft with unresolved legacy identity')
    assert page.evaluate('mvpNotesSaveDraft()') is False
    assert page.evaluate('localStorage.getItem(LSKEY)')==before
    assert page.locator('#mvpNotesSaveStatus').inner_text()!='Salvo'
    assert page.evaluate('mvpNotesUI.draftDirty')
    assert page.evaluate("mvpNotesRenameFolder(S.mvpNotes.folders[0].id,'Recoverable unidentified folder rename')") is None
    assert page.evaluate('localStorage.getItem(LSKEY)')==before
    assert page.evaluate('mvpNotesUI.draftDirty')
    return {'accepted_missing_identity_safe_refusal':True,'unidentified_folder_rename_refused':True,'automatic_identity_migration_not_claimed':True}


CASES = {
    'autosave-legacy-erasure':autosave_legacy_erasure,'autosave-legacy-missing-dates':autosave_legacy_missing_dates,'autosave-legacy-missing-ids-refused':autosave_legacy_missing_ids_refused,
    'autosave-recovered-draft':autosave_recovered_draft,
    'autosave-delete-dispose':autosave_delete_dispose,
    'autosave-reverted':autosave_reverted,'autosave-metadata-status':autosave_metadata_status,
    'autosave-lifecycle':autosave_lifecycle,
    'autosave-filtered-new':autosave_filtered_new,'autosave-divergent-ram':autosave_divergent_ram,
    'autosave-refused':autosave_refused,'autosave-unknown':autosave_unknown,'autosave-ime-metadata':autosave_ime_metadata,'autosave-context':autosave_context,'autosave-peer':autosave_peer,'autosave-fresh-extensions':autosave_fresh_extensions,
    'autosave-direct':autosave_direct,'autosave-scoped':autosave_scoped,'autosave-empty':autosave_empty,
    'center': center, 'reopen-dirty': reopen_dirty, 'reopen-recovery-focus': reopen_recovery_focus,
    'position-reload': position_reload,
    'responsive': responsive, 'one-note': responsive, 'resize-dirty': resize_dirty, 'focus-settings': focus_settings,
    'icon-labels': icon_labels, 'empty-search': empty_search, 'search': long_search,
    'preference-actions': preference_actions, 'reduced-motion': reduced_motion,
    'preference-invalid': preference_invalid, 'preference-extension': preference_extension,
    'preference-refusal-retry': preference_refusal_retry, 'preference-unknown': preference_unknown,
    'preference-peer-conflict': preference_peer_conflict, 'preference-epoch-callback': preference_epoch_callback,
    'preference-durable-epoch-race': preference_durable_epoch_race,
    'preference-main-document-race': preference_main_document_race,
}


def run(args):
    global launcher
    helper_path=args.root/'tools/notes_launcher_test.py'
    helper_spec=importlib.util.spec_from_file_location('_notes_experience_launcher_target',helper_path)
    launcher=importlib.util.module_from_spec(helper_spec)
    helper_spec.loader.exec_module(launcher)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    if args.output.exists():
        raise FileExistsError('Evidence exists; choose a new --output: '+str(args.output))
    selected=args.cases.split(',') if args.cases else list(CASES)
    unknown=set(selected)-set(CASES)
    if unknown: raise ValueError('Unknown cases: '+','.join(sorted(unknown)))
    report={'started_at':datetime.now(timezone.utc).isoformat(),'root':str(args.root),'baseline':args.baseline,
      'launcher_helper':str(helper_path),'launcher_helper_sha256':hashlib.sha256(helper_path.read_bytes()).hexdigest(),
      'test_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'inputs_before':launcher.hashes(args.root),
      'checks':[],'limits':['Synthetic Chromium only; existing nominal fixtures and blocked service workers.',
      'Position-reload now records a real warmup reload before its full S/local/session checkpoint. Historical experience-v1/v2 PRODUCT_FAIL receipts remain unchanged; their activeOperation-only first-reload differences are TEST_HARNESS setup effects, not position-write evidence.',
      'Reopening is a direct controller contract probe because covered launchers are correctly inert.',
      'Native 200% zoom and pointer/touch cancellation also belong to the separate launcher focal.',
      'Save refusal/retry and persistence-banner keyboard contracts belong to studies_notes_persistence_contract_test.py.',
      'Icon optical quality is reviewed separately; this focal proves shared symbol identity and labels.']}
    server=ThreadingHTTPServer(('127.0.0.1',0),partial(launcher.Quiet,directory=str(args.root)))
    threading.Thread(target=server.serve_forever,daemon=True).start()
    artifacts=['index.html','dist/JP_Wealth_Risk_Terminal_V9.1_PORTABLE.html'] if args.artifact=='both' else [
      'index.html' if args.artifact=='source' else 'dist/JP_Wealth_Risk_Terminal_V9.1_PORTABLE.html']
    try:
        with sync_playwright() as pw:
            browser=pw.chromium.launch(**launcher.launch_options())
            try:
                for artifact in artifacts:
                    for name in selected:
                        configs=[(1440,'light')]
                        if name=='responsive':configs=[(w,t) for w in (1440,1024,390,320) for t in ('light','dark')]
                        elif name in ('center','focus-settings'):configs=[(1440,t) for t in ('light','dark')]
                        for width,theme in configs:
                            label=f'{artifact}/{name}/{width}/{theme}'
                            row={'name':label};context=None;page=None;observed=None
                            try:
                                context=browser.new_context(viewport={'width':width,'height':900},service_workers='block',reduced_motion='reduce')
                                context.set_default_timeout(15000)
                                page,observed=launcher.prepare(context,f'http://127.0.0.1:{server.server_port}/{artifact}',theme)
                                if name!='empty-search':page.evaluate(SEED,1 if name=='one-note' else 12)
                                launcher.settle(page)
                                row['build']=page.evaluate('JP_WEALTH_BUILD_ID')
                                detail=CASES[name](page)
                                if name in ('autosave-unknown','autosave-metadata-status'):
                                    expected='[persistência] DESFECHO INDETERMINADO — novas gravações bloqueadas: READ_AFTER_WRITE'
                                    expected_errors=[expected]*(2 if name=='autosave-metadata-status' else 1)
                                    assert observed['console']==expected_errors, observed
                                    row['expected_console_errors']=observed['console'][:]
                                    observed['console']=[]
                                launcher.assert_clean(context,observed)
                                row.update(result='PASS',detail=detail)
                            except Exception as error:
                                row.update(result=('BASELINE_FAIL' if args.baseline else 'PRODUCT_FAIL') if isinstance(error,AssertionError) or (isinstance(error,PlaywrightTimeout) and 'build' in row) else 'TEST_HARNESS_FAIL',
                                  error_type=type(error).__name__,detail=str(error))
                            finally:
                                if page:
                                    if hasattr(page,'notes_experience_warmup_diff'):
                                        row['warmup_reload_diff']=page.notes_experience_warmup_diff
                                    try:
                                        image=args.output.with_name(args.output.stem+'-'+label.replace('/','-').replace('.html','')+'.png')
                                        page.screenshot(path=str(image));row['screenshot']=str(image)
                                        row['screenshot_sha256']=hashlib.sha256(image.read_bytes()).hexdigest()
                                    except Exception as error:row['capture_error']=str(error)
                                if observed:row['observed_errors']=observed
                                if context:context.close()
                                report['checks'].append(row)
                                print(json.dumps({'name':label,'result':row['result'],'detail':row.get('detail') if row['result']!='PASS' else None},ensure_ascii=False),flush=True)
            finally:browser.close()
    except Exception as error:
        report['checks'].append({'name':'runtime','result':'ENVIRONMENT_ERROR','detail':str(error)})
    finally:
        server.shutdown();server.server_close()
        report['inputs_after']=launcher.hashes(args.root)
        report['launcher_helper_sha256_after']=hashlib.sha256(helper_path.read_bytes()).hexdigest()
        report['source_unchanged']=report['inputs_before']==report['inputs_after'] and report['launcher_helper_sha256']==report['launcher_helper_sha256_after']
        if not report['source_unchanged']:
            report['checks'].append({'name':'candidate stable during execution','result':'TEST_HARNESS_FAIL','detail':'Input hashes changed during focal execution'})
        statuses={r['result'] for r in report['checks']}
        report['result']='PASS' if statuses=={'PASS'} else 'ENVIRONMENT_ERROR' if 'ENVIRONMENT_ERROR' in statuses else 'TEST_HARNESS_FAIL' if 'TEST_HARNESS_FAIL' in statuses else 'BASELINE_FAIL' if args.baseline else 'PRODUCT_FAIL'
        report['finished_at']=datetime.now(timezone.utc).isoformat()
        with args.output.open('x') as out:json.dump(report,out,ensure_ascii=False,indent=2);out.write('\n')
        print(json.dumps({'result':report['result'],'checks':len(report['checks']),'output':str(args.output)},ensure_ascii=False),flush=True)
    return 0 if report['result']=='PASS' else 1


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root',type=Path,default=ROOT)
    parser.add_argument('--output','--out',type=Path,required=True)
    parser.add_argument('--artifact',choices=('source','portable','both'),default='both')
    parser.add_argument('--cases',help='Comma-separated focused cases: '+','.join(CASES))
    parser.add_argument('--baseline',action='store_true')
    raise SystemExit(run(parser.parse_args()))
