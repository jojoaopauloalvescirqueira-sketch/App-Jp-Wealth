#!/usr/bin/env python3
"""AUD-07..09: original app, DOM journeys, synthetic profiles, no external network.

The recovery envelope/reset are fixtures; the draft is captured by the actual
provider after ordinary view reentry, never filtered to force compatibility.
No source, schema, gate, real profile or operational data is changed by this test.
"""
import argparse
from datetime import datetime, timezone
from functools import partial
import hashlib
from http.server import SimpleHTTPRequestHandler
import json
from pathlib import Path
import sys
import threading
import traceback

sys.dont_write_bytecode = True

SOURCE_FILES = (
    'index.html', 'build-id.js', 'src/js/manifest.json',
    'src/js/20-ui/15-pivot-studies.js', 'src/js/20-ui/33-module-work.js',
    'src/js/40-app/14-mvp-notes.js', 'src/js/00-core/07-workspace-backup.js',
)
CONFIGS = [(1440, 900, 'light'), (820, 900, 'dark'), (390, 844, 'dark')]


def hashes(root):
    return {name: hashlib.sha256((root/name).read_bytes()).hexdigest() for name in SOURCE_FILES}


def settle(page):
    page.evaluate('() => new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)))')


def go_research(page, view='pivots', primary=False):
    if primary:
        toggle=page.locator('[data-shell-menu-toggle]')
        if toggle.is_visible() and toggle.get_attribute('aria-expanded')!='true':
            page.locator('[data-shell-menu-toggle]').click()
            settle(page)
        page.locator('#researchNavTrigger').click()
        settle(page)
    selector='[data-nav-local-surface="research"][data-nav-local-view="'+view+'"]'
    if not page.locator(selector).is_visible():
        toggle=page.locator('[data-shell-menu-toggle]')
        if toggle.is_visible() and toggle.get_attribute('aria-expanded')!='true':
            page.locator('[data-shell-menu-toggle]').click()
            settle(page)
        page.locator('[data-nav-child="research-forex"]:visible').click()
        settle(page)
    page.locator(selector+':visible').click()
    settle(page)


def snapshot(page):
    return page.evaluate("""() => ({state:JSON.stringify(S),
      local:JSON.stringify(Object.fromEntries(Object.keys(localStorage).sort().map(k=>[k,localStorage.getItem(k)]))),
      session:JSON.stringify(Object.fromEntries(Object.keys(sessionStorage).sort().map(k=>[k,sessionStorage.getItem(k)]))),
      writes:window.__auditUIWrites.length})""")


def instrument(page):
    page.evaluate("""() => {window.__auditUIWrites=[];
      for(const method of ['setItem','removeItem','clear']){
        const original=Storage.prototype[method];
        Storage.prototype[method]=function(...args){
          __auditUIWrites.push({method,key:args[0]||null,area:this===localStorage?'local':'session'});
          return original.apply(this,args);
        };
      }}""")


def check(case, label, condition, details=None):
    case['checks'].append({'label':label,'passed':bool(condition),'details':details})


def capture(page, case, out, suffix):
    name=case['name']+'-'+suffix+'.png'
    page.screenshot(path=str(out/name),full_page=True)
    case.setdefault('screenshots',[]).append(name)


def create_study(page):
    page.locator('#pvNewStudyBtn').click()
    page.locator('#pvPeriodStart').fill('2026-09-01')
    page.locator('#pvPeriodEnd').fill('2026-09-30')
    page.locator('#pvCreateStudyBtn').click()


def create_pivot(page, notes='Synthetic observation'):
    page.locator('#pvAddPivotBtn').click()
    page.locator('#pv_timeframe').select_option('H1')
    for key,value in {'startDatetime':'2026-09-10T10:00','startPrice':'1.2000',
        'endDatetime':'2026-09-10T14:00','endPrice':'1.2500',
        'maxCorrectionPct':'30','notes':notes}.items():
        page.locator('#pv_'+key).fill(value)
    page.locator('#pvSavePivotBtn').click()


def pivot_state(page):
    return page.evaluate("""() => ({view:JPWResearch.ui.getView(),formOpen:pvFormOpen,dirty:pvDirty,
      draft:structuredClone(pvDraft),editingId:pvEditingId,newStudyOpen:pvNewStudyOpen,
      newStudy:structuredClone(pvNewStudyDraft),instrumentId:pvInstrumentId,studyId:pvStudyId,
      fieldsVisible:!!document.getElementById('pv_startPrice')?.getClientRects().length,
      newStudyVisible:!!document.getElementById('pvPeriodStart')?.getClientRects().length,
      focused:document.activeElement?.id||document.activeElement?.tagName,
      focusInVisibleWorkspace:!!document.activeElement?.closest('#execPivots')&&!document.activeElement?.closest('[hidden],[inert]')})""")


def recovery_case(page, case, out, decision, kind):
    go_research(page,primary=True)
    if kind != 'new-study':
        create_study(page)
    if kind == 'edit':
        create_pivot(page)
        page.locator('[data-pv-edit]').first.click()
        page.locator('#pv_notes').fill('Synthetic recovered edit')
    elif kind == 'new':
        page.locator('#pvAddPivotBtn').click()
        page.locator('#pv_startPrice').fill('1.23456')
    else:
        page.locator('#pvNewStudyBtn').click()
        page.locator('#pvPeriodStart').fill('2026-08-01')
        page.locator('#pvPeriodEnd').fill('2026-08-31')
    original=pivot_state(page)
    initial_item=page.evaluate('() => jpwWorkspaceDraftProviders.get("module-work")()[0]')
    case['captureBeforeReentryKinds']=[e['kind'] for e in json.loads(initial_item['text'])]
    go_research(page,'nocoda')
    go_research(page,'pivots')
    preparation=page.evaluate("""() => {
      const item=jpwWorkspaceDraftProviders.get('module-work')()[0];
      JPWPivotsUI.resetDraft();JPWPivotsUI.render();
      S.workspaceRecovery={schemaVersion:1,pending:false,drafts:[item]};
      jpwWorkspaceRender();return {item,inspection:JPWWorkspaceDrafts.inspect(item)};
    }""")
    case['preparation']=preparation
    check(case,'Ordinary view reentry produces a compatible item',preparation['inspection']['compatible'])
    if not preparation['inspection']['compatible']:
        return
    boundaries=page.evaluate("""() => {
      const item=S.workspaceRecovery.drafts[0];
      const wrong=structuredClone(item);wrong.baseReference='SYNTHETIC-WRONG-BASE';
      const generic=structuredClone(item);const entries=JSON.parse(generic.text);
      entries.push({kind:'campos não confirmados',fields:[{field:'Synthetic',value:'copy-only'}]});
      generic.text=JSON.stringify(entries);
      return {wrong:JPWWorkspaceDrafts.inspect(wrong),copyOnly:JPWWorkspaceDrafts.inspect(generic)};
    }""")
    check(case,'Incompatible base is refused',not boundaries['wrong']['compatible'],boundaries)
    check(case,'Generic copy-only entries remain refused',not boundaries['copyOnly']['compatible'],boundaries)
    before=snapshot(page)
    decision['accept']=False
    page.locator('#workspaceDraftsButton').click()
    page.locator('#workspaceDraftDialog').get_by_role('button',name='Conferir e reabrir campos',exact=True).click()
    check(case,'Cancel preserves data and storage',snapshot(page)==before)
    check(case,'Cancel leaves conference dialog open',page.locator('#workspaceDraftDialog').evaluate('e=>e.open'))
    check(case,'Cancel does not restore pending fields',not pivot_state(page)['dirty'])
    decision['accept']=True
    page.locator('#workspaceDraftDialog').get_by_role('button',name='Conferir e reabrir campos',exact=True).click()
    settle(page)
    actual=pivot_state(page)
    case['original']=original;case['after']=actual
    check(case,'Accept preserves confirmed data and storage',snapshot(page)==before)
    check(case,'Accept selects Pivots workspace',actual['view']=='pivots',actual)
    check(case,'Accept keeps instrument and study',actual['instrumentId']==original['instrumentId'] and actual['studyId']==original['studyId'])
    if kind == 'new-study':
        check(case,'New-study draft is visible and exact',actual['newStudyVisible'] and actual['newStudy']==original['newStudy'])
    else:
        check(case,'Pivot form is open and visible',actual['formOpen'] and actual['fieldsVisible'])
        check(case,'Recovered pivot draft and target are exact',actual['draft']==original['draft'] and actual['editingId']==original['editingId'])
        check(case,'Recovered form prevents accidental replacement',page.locator('#pvAddPivotBtn').is_disabled())
    capture(page,case,out,'recovered')


def open_notes(page):
    page.locator('#headerNotesBtn').click()
    if not page.locator('#mvpNotesNewBtn').is_visible():
        page.locator('[data-mvp-folder="all"]:visible').click()


def note_state(page):
    return page.evaluate("""() => {const input=document.getElementById('mvpNoteContent');return {
      selected:mvpNotesUI.selectedId,draft:structuredClone(mvpNotesUI.draft),original:structuredClone(mvpNotesUI.draftOriginal),
      dirty:mvpNotesUI.draftDirty,folder:mvpNotesUI.activeFolder,stage:mvpNotesUI.stage,
      value:input.value,start:input.selectionStart,end:input.selectionEnd,
      visible:!!input.getClientRects().length};}""")


def notes_case(page, case, out, decision, kind):
    open_notes(page)
    page.locator('#mvpNotesNewBtn').click()
    page.locator('#mvpNotesNewConfirmBtn').click()
    if kind=='existing':
        page.locator('#mvpNoteContent').fill('Synthetic note\nOriginal saved content')
        page.locator('#mvpNotesSaveBtn').click()
    page.locator('#mvpNoteContent').fill('Synthetic note\nUnsaved content to discard')
    page.locator('#mvpNoteContent').evaluate('e=>e.setSelectionRange(4,9)')
    if not page.locator('[data-mvp-folder="unfiled"]:visible').count():
        requested=page.viewport_size
        if requested['width']<=600:
            page.set_viewport_size({'width':820,'height':requested['height']})
        page.locator('#mvpNotesBackBtn').click()  # tablet shows folders and preserves RAM
        if requested['width']<=600:
            page.set_viewport_size(requested)
    before_state=note_state(page);before=snapshot(page)
    decision['accept']=False
    page.locator('[data-mvp-folder="unfiled"]:visible').click()
    check(case,'Cancel keeps editor, draft and folder',note_state(page)==before_state)
    check(case,'Cancel performs no storage/data write',snapshot(page)==before)
    decision['accept']=True
    page.locator('[data-mvp-folder="unfiled"]:visible').click()
    after=note_state(page);case['before']=before_state;case['after']=after
    check(case,'Accept performs no storage/data write',snapshot(page)==before)
    check(case,'Accept changes the selected folder',after['folder']=='unfiled')
    check(case,'Accept really discards pending RAM',after['draft'] is None and after['selected'] is None and not after['dirty'],after)
    check(case,'Discarded editor is hidden',not after['visible'])
    capture(page,case,out,'discard')


def results_case(page, case, out, decision, _kind):
    go_research(page,primary=True);create_study(page)
    create_pivot(page,'Synthetic first pivot')
    create_pivot(page,'Synthetic second pivot')
    page.locator('#pvAddPivotBtn').click()
    page.locator('#pv_notes').fill('Synthetic pending draft preserved through ordering')
    page.locator('#pv_notes').evaluate('e=>e.setSelectionRange(5,12)')
    before=snapshot(page)
    original=pivot_state(page)
    page.evaluate("""() => {window.__auditOriginal={sort:document.getElementById('pvSort'),
      input:document.getElementById('pv_notes'),filter:document.querySelector('[data-pv-filter="timeframe"][data-pv-value="H4"]')};}""")
    page.locator('#pvSort').focus()
    page.keyboard.press('ArrowDown');settle(page)
    case['nativePopupObservation']=page.evaluate('() => ({value:document.getElementById("pvSort").value,focus:document.activeElement.id})')
    page.keyboard.press('Escape')
    page.locator('#pvSort').select_option('amplitude:asc');settle(page)
    sort=page.evaluate("""() => ({connected:__auditOriginal.sort.isConnected,same:__auditOriginal.sort===document.getElementById('pvSort'),
      focus:document.activeElement.id,inputSame:__auditOriginal.input===document.getElementById('pv_notes'),
      start:document.getElementById('pv_notes').selectionStart,end:document.getElementById('pv_notes').selectionEnd})""")
    case['sort']=sort
    check(case,'Sort keeps original focused selector',sort['connected'] and sort['same'] and sort['focus']=='pvSort',sort)
    check(case,'Sort keeps original draft input and cursor',sort['inputSame'] and (sort['start'],sort['end'])==(5,12),sort)
    page.locator('[data-pv-filter="timeframe"][data-pv-value="H4"]').click();settle(page)
    filtered=page.evaluate("""() => ({same:__auditOriginal.filter===document.querySelector('[data-pv-filter="timeframe"][data-pv-value="H4"]'),
      connected:__auditOriginal.filter.isConnected,focus:document.activeElement===__auditOriginal.filter,
      inputSame:__auditOriginal.input===document.getElementById('pv_notes'),
      pressed:document.querySelector('[data-pv-filter="timeframe"][data-pv-value="H4"]').getAttribute('aria-pressed'),
      rows:document.querySelectorAll('[data-pv-row]').length})""")
    case['filtered']=filtered
    check(case,'Filter keeps original focused button',filtered['same'] and filtered['connected'] and filtered['focus'],filtered)
    check(case,'Filter updates pressed state and visible results',filtered['pressed']=='true' and filtered['rows']==0,filtered)
    check(case,'Filter keeps pending draft input',filtered['inputSame'] and pivot_state(page)['draft']==original['draft'])
    page.locator('[data-pv-filter="timeframe"][data-pv-value="all"]').click()
    page.locator('#pvSort').select_option('duration:desc')
    page.locator('#pvSort').select_option('date:asc');settle(page)
    check(case,'Repeated results changes perform no data/storage writes',snapshot(page)==before)
    check(case,'Repeated updates preserve draft dirty and values',pivot_state(page)['dirty'] and pivot_state(page)['draft']==original['draft'])
    # Only newly-created result controls are rebound; one click emits one confirmation.
    count=len(case['dialogs']);decision['accept']=False
    page.locator('[data-pv-delete]').first.click()
    check(case,'Result delete listener stays singular',len(case['dialogs'])==count+1)
    check(case,'Refused delete preserves state/storage',snapshot(page)==before)
    decision['accept']=True
    capture(page,case,out,'results')


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[1])
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--desktop-only',action='store_true')
    args=parser.parse_args();root=args.root.resolve();out=args.output.resolve();out.mkdir(parents=True,exist_ok=True)
    sys.path.insert(0,str(root/'tools'))
    from browser_fixture_server import BrowserFixtureServer
    from browser_bootstrap_fixture import install_bootstrap,wait_bootstrap,assert_fixture_requests
    from playwright.sync_api import sync_playwright
    class Quiet(SimpleHTTPRequestHandler):
        def log_message(self,*_):pass
    receipt={'root':str(root),'generatedAt':datetime.now(timezone.utc).isoformat(),
      'scope':'AUD-07..09 synthetic DOM regressions; recovery envelope/reset are fixtures; no external network; SW blocked',
      'sourcesBefore':hashes(root),'cases':[]}
    server=BrowserFixtureServer(('127.0.0.1',0),partial(Quiet,directory=str(root)))
    threading.Thread(target=server.serve_forever,daemon=True).start()
    try:
        with sync_playwright() as pw:
            browser=pw.chromium.launch(headless=True);receipt['browserVersion']=browser.version
            tests=[('AUD-07-new',recovery_case,'new'),('AUD-07-edit',recovery_case,'edit'),
                   ('AUD-07-new-study',recovery_case,'new-study'),('AUD-08-existing',notes_case,'existing'),
                   ('AUD-08-new',notes_case,'new'),('AUD-09-results',results_case,None)]
            for width,height,theme in (CONFIGS[:1] if args.desktop_only else CONFIGS):
                for name,fn,kind in tests:
                    case={'name':name+'-'+str(width)+'-'+theme,'checks':[],'dialogs':[],'pageerror':[],'consoleErrors':[],
                          'viewport':{'width':width,'height':height},'theme':theme}
                    context=browser.new_context(viewport=case['viewport'],service_workers='block')
                    install_bootstrap(context)
                    context.add_init_script('window.__onbShown=true;')
                    page=context.new_page();decision={'accept':True}
                    page.on('pageerror',lambda e,c=case:c['pageerror'].append(str(e)))
                    page.on('console',lambda m,c=case:c['consoleErrors'].append(m.text) if m.type=='error' else None)
                    def dialog_handler(dialog,c=case,d=decision):
                        c['dialogs'].append({'type':dialog.type,'message':dialog.message,'accepted':d['accept']})
                        dialog.accept() if d['accept'] else dialog.dismiss()
                    page.on('dialog',dialog_handler)
                    try:
                        page.goto('http://127.0.0.1:'+str(server.server_port)+'/index.html',wait_until='load')
                        wait_bootstrap(page)
                        page.evaluate('() => {closeModal();document.documentElement.setAttribute("data-theme",'+json.dumps(theme)+');}')
                        instrument(page)
                        fn(page,case,out,decision,kind)
                        assert_fixture_requests(context)
                        check(case,'No page errors',not case['pageerror'],case['pageerror'])
                        check(case,'No console errors',not case['consoleErrors'],case['consoleErrors'])
                        case['classification']='PASS' if all(c['passed'] for c in case['checks']) else 'PRODUCT_FAIL'
                    except Exception as error:
                        case['classification']='TEST_HARNESS_FAIL'
                        case['exception']={'message':str(error),'traceback':traceback.format_exc()}
                        capture(page,case,out,'attempt')
                    finally:
                        receipt['cases'].append(case);context.close()
                        print(case['name']+': '+case['classification'],flush=True)
            browser.close()
    finally:
        server.shutdown();server.server_close()
    receipt['sourcesAfter']=hashes(root)
    receipt['sourceStability']='PASS' if receipt['sourcesBefore']==receipt['sourcesAfter'] else 'BASELINE_FAIL'
    receipt['counts']={key:sum(c['classification']==key for c in receipt['cases']) for key in ['PASS','PRODUCT_FAIL','TEST_HARNESS_FAIL']}
    (out/'receipt.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'receipt':str(out/'receipt.json'),'counts':receipt['counts'],'sourceStability':receipt['sourceStability']}),flush=True)
    return 0 if receipt['counts']['PRODUCT_FAIL']==receipt['counts']['TEST_HARNESS_FAIL']==0 and receipt['sourceStability']=='PASS' else 1


if __name__=='__main__':
    raise SystemExit(main())
