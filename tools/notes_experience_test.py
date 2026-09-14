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
    page.locator('#headerNotesBtn').click()
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
    page.locator('#mvpNotesCloseBtn').click()
    expect(page.locator('#mvpNotesOverlay')).to_be_visible()
    assert_draft(page, before)
    page.locator('#mvpNotesSaveBtn').click()
    assert not page.evaluate('mvpNotesUI.draftDirty')
    assert page.locator('#mvpNoteContent').input_value() == LONG_BODY
    page.locator('#mvpNotesCloseBtn').click()
    expect(page.locator('#headerNotesBtn')).to_be_focused()


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
        page.locator('#mvpNotesBackBtn').click()
        assert_draft(page, before)
        assert visible_panes(page) == [PANES[2]]
    elif width <= 1100:
        assert visible_panes(page) == [PANES[1], PANES[2]], geometry(page)
        assert geometry(page)['panes'][2]['width'] >= 320
    else:
        assert visible_panes(page) == list(PANES)
    page.locator('#mvpNotesSaveBtn').click()
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


CASES = {
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
