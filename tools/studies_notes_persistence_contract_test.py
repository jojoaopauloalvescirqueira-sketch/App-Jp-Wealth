#!/usr/bin/env python3
"""OPEN-02/03/04: storage refusal contracts, with real UI and synthetic state.

The oracle predates the fixes: proven refusal restores only the affected
aggregate, retains the draft, and cannot leak into a later successful save.
Exceptions from save are UNKNOWN, even when the fixture knows the write point.
Uses the existing nominal bootstrap fixture; no economic API is contacted.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import sys
import threading
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

from playwright.sync_api import sync_playwright

sys.path.insert(0, str(Path(__file__).resolve().parent))
from browser_bootstrap_fixture import install_bootstrap, wait_bootstrap, assert_fixture_requests

NC = {'anchor1': {'datetime': '2021-01-04T11:00:00', 'price': 1.23412},
      'anchor2': {'datetime': '2021-06-08T04:00:00', 'price': 1.22513},
      'anchor3': {'datetime': '2021-03-16T08:00:00', 'price': 1.17156}}
PV = {'id': 'pivot-existing', 'timeframe': 'H4', 'startDatetime': '2025-02-12T08:00:00',
      'startPrice': 1.08, 'endDatetime': '2025-03-04T16:00:00', 'endPrice': 1.14934,
      'maxCorrectionPct': 47.2, 'notes': 'original', 'createdAt': '2025-01-01', 'updatedAt': '2025-01-01'}

PREPARE = r"""({caseName,nc,pv}) => {
  closeModal(); window.alert=m=>window.__alerts.push(String(m)); window.__alerts=[];
  window.__confirm=true; window.confirm=()=>window.__confirm;
  S.nocoda={schemaVersion:1,studies:{}};
  S.pivotStudies={schemaVersion:1,studies:[]};
  S.mvpNotes=structuredClone(DEFAULTS.mvpNotes);
  const instrument=instrumentCatalog()[0].id;
  const study={id:'study-existing',instrumentId:instrument,periodStart:'2025-01-01',periodEnd:'2025-12-31',createdAt:'2025-01-01',updatedAt:'2025-01-01',pivots:[pv]};
  const folder={id:'folder-existing',name:'Original',position:0,createdAt:'2025-01-01',updatedAt:'2025-01-01'};
  const note={id:'note-existing',ticket:'JPW-ABCDEF',content:'Original\nBody',title:'Original',type:'task',priority:'medium',status:'open',folderId:folder.id,
    aiImplementationPolicy:'analysis_only',screenId:'dash',buildId:'synthetic',sourceRevision:null,createdAt:'2025-01-01',updatedAt:'2025-01-01',completedAt:null};
  if(caseName.startsWith('nc-')){
    if(caseName==='nc-edit') S.nocoda.studies[instrument]={...structuredClone(nc),updatedAt:'2025-01-01',extension:'preserved'};
    ncSelectedId=instrument; ncDraft=JSON.parse(JSON.stringify(nc));ncDraft.anchor1.price='1.23512';ncDirty=true;
    JPWNavigation.navigate('nocoda');
  }else if(caseName.startsWith('pv-')){
    if(caseName==='pv-create') study.pivots=[];
    S.pivotStudies.studies=[study];pvInstrumentId=instrument;pvStudyId=study.id;
    pvDraft={...pv,startPrice:'1.09'};pvEditingId=caseName==='pv-edit'?pv.id:null;pvFormOpen=true;pvDirty=true;
    pvNewStudyOpen=true;pvNewStudyDraft={periodStart:'2024-01-01',periodEnd:'2024-12-31'};
    JPWNavigation.navigate('pivots');
  }else{
    S.mvpNotes.folders=[folder,{...folder,id:'folder-second',name:'Second',position:1}];
    S.mvpNotes.items=caseName==='note-create'?[]:[note];
    openMvpNotesDrawer();
    if(caseName==='note-create') mvpNotesBeginNewNote();
    else mvpNotesSelectNote(note.id);
    mvpNotesUI.draft.content='Modified\nRecoverable draft';mvpNotesUI.draftDirty=true;
    renderMvpNotesEditor();
  }
  if(save()!==true) throw Error('Synthetic checkpoint failed');
  window.__realSave=save;window.__realSet=Storage.prototype.setItem;window.__saveCalls=[];
  window.__operation=caseName;window.__mode='normal';
  Storage.prototype.setItem=function(k,v){if(k===LSKEY&&window.__mode==='quota')throw new DOMException('synthetic quota','QuotaExceededError');return window.__realSet.call(this,k,v);};
  save=function(){
    if(window.__mode==='false'){window.__saveCalls.push(false);return false;}
    if(window.__mode==='throw-before')throw Error('synthetic exception before write');
    const r=window.__realSave();window.__saveCalls.push(r);
    if(window.__mode==='throw-after')throw Error('synthetic exception after confirmed native write');
    if(window.__mode==='unexpected')return undefined;
    return r;
  };
}"""
SNAPSHOT = r"""() => {
  const c=window.__operation;
  return {aggregate:structuredClone(c.startsWith('nc-')?S.nocoda:c.startsWith('pv-')?S.pivotStudies:S.mvpNotes),
    raw:localStorage.getItem(LSKEY),log:JSON.stringify(S.dataGovernance.changeLog),
    other:JSON.stringify(S.personalFinance),unknown:jpWealthPersistenceOutcomeIsUnknown(),calls:window.__saveCalls.slice(),
    failure:jpWealthPersistenceFailure.kind,alerts:window.__alerts.slice(),
    banner:document.getElementById('persistenceAlert')?.className,
    savedTag:document.getElementById('savedTag')?.classList.contains('show'),
    ui:c.startsWith('nc-')?{dirty:ncDirty,draft:ncDraft,status:document.getElementById('ncStatus')?.textContent}:
      c.startsWith('pv-')?{dirty:pvDirty,draft:pvDraft,formOpen:pvFormOpen,newStudyOpen:pvNewStudyOpen,newStudyDraft:pvNewStudyDraft,study:pvStudyId}:
      {dirty:mvpNotesUI.draftDirty,draft:mvpNotesUI.draft,selected:mvpNotesUI.selectedId,live:document.getElementById('mvpNotesCopyLive')?.textContent}}
}"""
OPERATE = r"""() => {
  switch(window.__operation){
    case 'nc-create':case 'nc-edit':return ncSaveStudy();
    case 'pv-create':case 'pv-edit':return pvSavePivot();
    case 'pv-delete':return pvDeletePivot('pivot-existing');
    case 'pv-study-create':return pvCreateStudy();
    case 'pv-study-delete':return pvDeleteStudy();
    case 'note-create':case 'note-edit':return mvpNotesSaveDraft();
    case 'note-delete':return mvpNotesDelete('note-existing');
    case 'folder-create':return mvpNotesCreateFolder('New folder');
    case 'folder-rename':return mvpNotesRenameFolder('folder-existing','Renamed');
    case 'folder-delete':return mvpNotesDeleteFolder('folder-existing');
    case 'folder-move':return mvpNotesMoveFolder('folder-existing',1);
  }
}"""
DRAFT_CASES={'nc-create','nc-edit','pv-create','pv-edit','note-create','note-edit'}
CASES=['nc-create','nc-edit','pv-create','pv-edit','pv-delete','pv-study-create','pv-study-delete',
       'note-create','note-edit','note-delete','folder-create','folder-rename','folder-delete','folder-move']

def check(condition, message, failures):
    if not condition:
        failures.append(message)


def run_case(browser, url, case, mode):
    context=browser.new_context(viewport={'width':1440,'height':1000},service_workers='block')
    install_bootstrap(context)
    page=context.new_page()
    page.add_init_script('window.__onbShown=true;')
    page.goto(url,wait_until='load');wait_bootstrap(page)
    page.evaluate(PREPARE,{'caseName':case,'nc':NC,'pv':PV})
    before=page.evaluate(SNAPSHOT)
    page.evaluate('(m)=>window.__mode=m',mode)
    if mode=='recovered-unknown':
        page.evaluate('window.__mode="quota"');page.evaluate(OPERATE)
        page.evaluate('window.__mode="throw-after"')
    if mode=='unknown':page.evaluate("markJPWealthPersistenceOutcomeUnknown('synthetic existing unknown')")
    if mode=='recovery':page.evaluate('jpWealthLoadRecovery.active=true')
    if mode=='conflict':
        peer=context.new_page();peer.goto(url,wait_until='load');wait_bootstrap(peer)
        peer.evaluate("() => { S.mvpNotes.showHeaderIcon=false; if(save()!==true)throw Error('peer save'); }")
        # Production storage listener may reload S; restore only the stale synthetic
        # snapshot deliberately so this attempts the same stale tab write guarded by save.
        page.evaluate('(raw)=>{S=JSON.parse(raw);jpWealthLastPersistedRaw=raw;}',before['raw'])
    disk_before=page.evaluate('localStorage.getItem(LSKEY)')
    errors=[]
    try: result=page.evaluate(OPERATE)
    except Exception as error: result=None;errors.append(str(error))
    after=page.evaluate(SNAPSHOT)
    failures=[]
    unknown=mode in ('unknown','throw-before','throw-after','unexpected','recovered-unknown')
    if mode=='normal':
        check(after['aggregate']!=before['aggregate'],'normal action did not mutate expected aggregate',failures)
        check(after['calls']==[True],'normal action did not save exactly once',failures)
        check_committed(case,after['aggregate'],failures)
    elif unknown:
        check(after['unknown'],'ambiguous outcome not blocked as UNKNOWN',failures)
        check(not after['savedTag'] and 'is-recovered' not in (after['banner'] or ''),'UNKNOWN retained global success feedback',failures)
        if mode=='unknown':check(after['aggregate']==before['aggregate'],'preexisting UNKNOWN mutated aggregate',failures)
        if mode in ('throw-before','unknown'):check(after['raw']==before['raw'],'unexpected physical write before UNKNOWN',failures)
        else:
            key='nocoda' if case.startswith('nc-') else 'pivotStudies' if case.startswith('pv-') else 'mvpNotes'
            check(json.loads(after['raw'])[key]==after['aggregate'],'ambiguous physical write was rolled back in memory',failures)
        if case in DRAFT_CASES:check(after['ui']['dirty'] and after['ui']['draft']==before['ui']['draft'],'UNKNOWN discarded recoverable draft',failures)
        message=after['ui'].get('status') or after['ui'].get('live') or ' '.join(after['alerts'])
        check('não repita' in message.lower(),'UNKNOWN did not explain retry prohibition',failures)
        if case.startswith('nc-'):
            page.evaluate("JPWNavigation.navigate('dash');JPWNavigation.navigate('nocoda')")
            check('gravação não confirmada' in page.locator('#ncStatus').inner_text(),'NoCoda reentry announced saved UNKNOWN study',failures)
        checkpoint=page.evaluate(SNAPSHOT)
        page.evaluate('window.__mode="normal"')
        try:page.evaluate(OPERATE)
        except Exception as error:errors.append(str(error))
        retry=page.evaluate(SNAPSHOT)
        check(retry['aggregate']==checkpoint['aggregate'] and retry['calls']==checkpoint['calls'],'UNKNOWN allowed blind retry',failures)
        key='nocoda' if case.startswith('nc-') else 'pivotStudies' if case.startswith('pv-') else 'mvpNotes'
        expected_disk=json.loads(after['raw'])[key]
        page.reload(wait_until='load');wait_bootstrap(page)
        check(page.evaluate('(k)=>S[k]',key)==expected_disk,'reload differs from actual UNKNOWN disk outcome',failures)
    else:
        check(after['aggregate']==before['aggregate'],'proven refusal retained mutation in aggregate',failures)
        check(after['raw']==disk_before,'proven refusal changed storage',failures)
        check(after['log']==before['log'],'proven refusal changed history',failures)
        if case in DRAFT_CASES:
            check(after['ui']['dirty'] and after['ui']['draft']==before['ui']['draft'],'refusal lost recoverable draft/dirty',failures)
        if case.startswith('nc-'):check(after['ui']['status']!='parâmetros salvos','false local success',failures)
        if case in ('pv-create','pv-edit'):check(after['ui']['formOpen'],'refusal closed pivot form',failures)
        if case=='pv-study-create':check(after['ui']['newStudyOpen'] and after['ui']['newStudyDraft']==before['ui']['newStudyDraft'],'refusal lost new study form',failures)
        if mode in ('quota','false'):
            page.evaluate("() => { window.__mode='normal'; S.mvpNotes.showHeaderIcon=!S.mvpNotes.showHeaderIcon; if(save()!==true)throw Error('later save'); }")
            disk=json.loads(page.evaluate('localStorage.getItem(LSKEY)'))
            key='nocoda' if case.startswith('nc-') else 'pivotStudies' if case.startswith('pv-') else 'mvpNotes'
            expected=dict(before['aggregate'])
            if key=='mvpNotes':expected['showHeaderIcon']=not expected['showHeaderIcon']
            check(disk[key]==expected,'later unrelated save incorporated refused action',failures)
            try:page.evaluate(OPERATE)
            except Exception as error:errors.append(str(error))
            retried=page.evaluate(SNAPSHOT)
            check(retried['aggregate']!=after['aggregate'],'explicit retry failed to apply action',failures)
            check_committed(case,retried['aggregate'],failures)
            if case=='pv-create':check(len(retried['aggregate']['studies'][0]['pivots'])==1,'retry duplicated pivot',failures)
            if case=='note-create':check(len(retried['aggregate']['items'])==1,'retry duplicated note',failures)
            page.reload(wait_until='load');wait_bootstrap(page)
            loaded=page.evaluate('(k)=>S[k]',key)
            check(loaded==retried['aggregate'],'reload differs from confirmed retry',failures)
    check(after['other']==before['other'],'unrelated financial aggregate changed',failures)
    check(not errors,'uncaught action exception',failures)
    assert_fixture_requests(context)
    context.close()
    return {'case':case,'mode':mode,'classification':'PRODUCT_FAIL' if failures else 'PASS','violations':failures,
            'action_return':result,'errors':errors,'before':before,'after':after}


def check_committed(case,aggregate,failures):
    """Expected input effects fixed independently of the mutation implementation."""
    if case.startswith('nc-'):
        studies=list(aggregate['studies'].values())
        check(len(studies)==1 and studies[0]['anchor1']['price']==1.23512,'saved anchor value/count differs from input',failures)
        check(studies[0]['anchor2']==NC['anchor2'] and studies[0]['anchor3']==NC['anchor3'],'unchanged anchors changed',failures)
        if case=='nc-edit':check(studies[0].get('extension')=='preserved','unknown study field lost',failures)
    elif case.startswith('pv-'):
        studies=aggregate['studies']
        if case=='pv-study-create':check(len(studies)==2 and studies[1]['periodStart']=='2024-01-01' and studies[1]['pivots']==[],'new study mismatch',failures)
        elif case=='pv-study-delete':check(studies==[],'deleted study retained',failures)
        elif case=='pv-delete':check(studies[0]['pivots']==[],'deleted pivot retained',failures)
        else:
            pivots=studies[0]['pivots']
            check(len(pivots)==1 and pivots[0]['startPrice']==1.09 and pivots[0]['endPrice']==1.14934,'pivot values/count differ',failures)
            if case=='pv-edit':check(pivots[0]['id']=='pivot-existing','edit changed pivot identity',failures)
    elif case.startswith('note-'):
        items=aggregate['items']
        if case=='note-delete':check(items==[],'deleted note retained',failures)
        else:
            check(len(items)==1 and items[0]['content']=='Modified\nRecoverable draft' and items[0]['title']=='Modified','note content/count differs',failures)
            if case=='note-edit':check(items[0]['id']=='note-existing','edit changed note identity',failures)
    elif case=='folder-create':check(len(aggregate['folders'])==3 and aggregate['folders'][2]['name']=='New folder','created folder mismatch',failures)
    elif case=='folder-rename':check(aggregate['folders'][0]['id']=='folder-existing' and aggregate['folders'][0]['name']=='Renamed','renamed folder mismatch',failures)
    elif case=='folder-delete':check([f['id'] for f in aggregate['folders']]==['folder-second'] and aggregate['items'][0]['folderId'] is None,'folder references not updated together',failures)
    elif case=='folder-move':check([f['id'] for f in aggregate['folders']]==['folder-second','folder-existing'] and [f['position'] for f in aggregate['folders']]==[0,1],'folder ordering mismatch',failures)


def run_ui(browser,url,case,width,artifact):
    context=browser.new_context(viewport={'width':width,'height':1000},color_scheme='dark' if width==1440 else 'light',service_workers='block')
    install_bootstrap(context)
    page=context.new_page();page.add_init_script('window.__onbShown=true;')
    page.goto(url,wait_until='load');wait_bootstrap(page)
    page.evaluate(PREPARE,{'caseName':case,'nc':NC,'pv':PV})
    page.evaluate('(theme)=>{S.theme=theme;applyTheme();}', 'dark' if width==1440 else 'light')
    field,button=('#ncPrice1','#ncSaveBtn') if case.startswith('nc-') else ('#pv_startPrice','#pvSavePivotBtn') if case.startswith('pv-') else ('#mvpNoteContent','#mvpNotesSaveBtn')
    value='1.23512' if case.startswith('nc-') else '1.09' if case.startswith('pv-') else 'Modified\nRecoverable draft'
    page.locator(field).fill(value)
    before=page.evaluate(SNAPSHOT)
    page.evaluate('window.__mode="quota"')
    page.locator(button).click()
    refused=page.evaluate(SNAPSHOT);failures=[]
    check(refused['aggregate']==before['aggregate'] and refused['raw']==before['raw'],'button refusal changed confirmed state',failures)
    check(refused['ui']['dirty'] and refused['ui']['draft']==before['ui']['draft'],'button refusal lost draft',failures)
    check(page.locator('#persistenceAlert').is_visible(),'global failure banner absent',failures)
    check(not page.locator('#savedTag').evaluate("e=>e.classList.contains('show')"),'stale success tag remained visible',failures)
    page.evaluate('window.__confirm=false')
    if case.startswith('nc-'):
        current=page.locator('#ncInstrument').input_value()
        next_id=page.locator('#ncInstrument option').nth(1).get_attribute('value')
        page.locator('#ncInstrument').select_option(next_id)
        check(page.locator('#ncInstrument').input_value()==current,'cancel failed to retain NoCoda instrument',failures)
        page.evaluate("JPWNavigation.navigate('dash');JPWNavigation.navigate('nocoda')")
    elif case.startswith('pv-'):
        page.locator('#pvCancelPivotBtn').click()
        page.evaluate("JPWNavigation.navigate('dash');JPWNavigation.navigate('pivots')")
    else:
        page.locator('#mvpNotesCloseBtn').click()
        check(page.locator('#mvpNotesOverlay').is_visible(),'cancel closed dirty notes drawer',failures)
    check(page.locator(field).input_value()==value,'cancel/navigation lost input',failures)
    check(page.evaluate('document.documentElement.scrollWidth<=innerWidth+1'),'page horizontal overflow',failures)
    image=artifact.parent/(artifact.stem+'-'+case+'-'+str(width)+'.png')
    page.screenshot(path=str(image),full_page=True)
    page.evaluate('window.__mode="normal"')
    page.locator(button).focus();page.keyboard.press('Enter')
    retried=page.evaluate(SNAPSHOT)
    check_committed(case,retried['aggregate'],failures)
    check(not retried['ui']['dirty'],'successful button retry remained dirty',failures)
    check(retried['calls']==[False,True],'UI retry did not call save once per attempt',failures)
    # A new context on the same synthetic origin reads physical storage after reload.
    key='nocoda' if case.startswith('nc-') else 'pivotStudies' if case.startswith('pv-') else 'mvpNotes'
    page.reload(wait_until='load');wait_bootstrap(page)
    check(page.evaluate('(k)=>S[k]',key)==retried['aggregate'],'UI confirmed state not recovered on reload',failures)
    assert_fixture_requests(context);context.close()
    return {'case':case,'mode':'ui-'+str(width),'classification':'PRODUCT_FAIL' if failures else 'PASS','violations':failures,'screenshot':str(image),'before':before,'refused':refused,'retried':retried}


def run_folder_prompt(browser,url,rename=False):
    context=browser.new_context(viewport={'width':1440,'height':1000},service_workers='block');install_bootstrap(context)
    page=context.new_page();page.add_init_script('window.__onbShown=true;')
    page.goto(url,wait_until='load');wait_bootstrap(page)
    case='folder-rename' if rename else 'folder-create'
    page.evaluate(PREPARE,{'caseName':case,'nc':NC,'pv':PV})
    page.evaluate('mvpNotesUI.draftDirty=false;window.__mode="quota"')
    prompts=[]
    def dialog(d):
        prompts.append({'type':d.type,'default':d.default_value,'message':d.message})
        if len(prompts)==1:d.accept('Recoverable folder')
        else:d.dismiss()
    page.on('dialog',dialog)
    def click():
        if rename:
            page.locator('[data-mvp-folder-row="folder-existing"] summary').focus()
            page.keyboard.press('Enter')
            page.locator('[data-mvp-folder-rename="folder-existing"]').click()
        else:page.locator('#mvpNotesNewFolderBtn').click()
    before=page.evaluate(SNAPSHOT);click();after=page.evaluate(SNAPSHOT);click()
    failures=[]
    check(after['aggregate']==before['aggregate'] and after['raw']==before['raw'],'folder prompt refusal changed confirmed state',failures)
    check(len(prompts)==2 and prompts[1]['default']=='Recoverable folder','refused folder name not recoverable in explicit retry',failures)
    context.close()
    return {'case':case,'mode':'native-prompt','classification':'PRODUCT_FAIL' if failures else 'PASS','violations':failures,'prompts':prompts}


def run_missing_note(browser,url):
    context=browser.new_context(service_workers='block');install_bootstrap(context)
    page=context.new_page();page.add_init_script('window.__onbShown=true;')
    page.goto(url,wait_until='load');wait_bootstrap(page)
    page.evaluate(PREPARE,{'caseName':'note-edit','nc':NC,'pv':PV})
    page.evaluate('S.mvpNotes.items=[]')
    before=page.evaluate(SNAPSHOT);page.evaluate(OPERATE);after=page.evaluate(SNAPSHOT)
    failures=[]
    check(after['ui']['dirty'] and after['ui']['draft']==before['ui']['draft'],'missing target discarded draft',failures)
    check(after['calls']==[] and after['raw']==before['raw'],'missing target wrote storage',failures)
    check('não existe' in (after['ui']['live'] or ''),'missing target lacks explanation',failures)
    context.close()
    return {'case':'note-missing','mode':'api','classification':'PRODUCT_FAIL' if failures else 'PASS','violations':failures,'before':before,'after':after}


def run_folder_reference(browser,url,mode):
    """Deleting a folder must not let the still-open draft resurrect its ID."""
    context=browser.new_context(service_workers='block');install_bootstrap(context)
    page=context.new_page();page.add_init_script('window.__onbShown=true;')
    page.goto(url,wait_until='load');wait_bootstrap(page)
    page.evaluate(PREPARE,{'caseName':'note-edit','nc':NC,'pv':PV})
    if mode=='normal':
        page.evaluate('mvpNotesUI.draft=mvpNotesDraftFromItem(S.mvpNotes.items[0]);mvpNotesUI.draftOriginal={...mvpNotesUI.draft};mvpNotesUI.draftDirty=false;renderMvpNotesEditor()')
    if mode=='other-folder':page.evaluate('mvpNotesUI.draft.folderId="folder-second"')
    if mode=='quota':page.evaluate('window.__mode="quota"')
    before=page.evaluate(SNAPSHOT)
    page.evaluate('mvpNotesDeleteFolder("folder-existing")')
    after=page.evaluate(SNAPSHOT);failures=[]
    if mode=='quota':
        check(after['aggregate']==before['aggregate'] and all(after['ui'][key]==before['ui'][key] for key in ('dirty','draft','selected')),'refused folder deletion changed draft/reference',failures)
    else:
        expected='folder-second' if mode=='other-folder' else None
        check(after['aggregate']['items'][0]['folderId'] is None,'confirmed deletion did not unfile note',failures)
        check(after['ui']['draft']['folderId']==expected,'open draft retained deleted folder reference',failures)
        check(after['ui']['draft']['content']==before['ui']['draft']['content'],'reference alignment overwrote draft text',failures)
        check(after['ui']['dirty']==before['ui']['dirty'],'reference alignment changed unrelated dirty state',failures)
        page.locator('#mvpNoteContent').fill('Reference contract\nLater saved body')
        page.locator('#mvpNotesSaveBtn').click()
        saved=page.evaluate('({item:S.mvpNotes.items[0],disk:JSON.parse(localStorage.getItem(LSKEY)).mvpNotes.items[0]})')
        check(saved['item']['folderId']==expected and saved['disk']['folderId']==expected,'later note save resurrected deleted folder',failures)
        page.reload(wait_until='load');wait_bootstrap(page)
        check(page.evaluate('S.mvpNotes.items[0].folderId')==expected,'reload changed supposedly confirmed folder reference',failures)
    context.close()
    return {'case':'folder-reference','mode':mode,'classification':'PRODUCT_FAIL' if failures else 'PASS','violations':failures,'before':before,'after':after}


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[1])
    parser.add_argument('--artifact',type=Path,required=True)
    parser.add_argument('--mode',choices=['baseline','full'],default='full')
    parser.add_argument('--only',choices=['conflict','ui','missing','folders','recovered-unknown','folder-reference'])
    args=parser.parse_args();root=args.root.resolve();os.chdir(root)
    class Quiet(SimpleHTTPRequestHandler):
        def log_message(self,*args):pass
    server=ThreadingHTTPServer(('127.0.0.1',0),Quiet)
    threading.Thread(target=server.serve_forever,daemon=True).start()
    results=[]
    tasks=[(case,'quota') for case in CASES]
    if args.mode=='full':
        tasks += [(case,mode) for case in ('nc-edit','pv-create','note-create','note-edit')
                  for mode in ('normal','false','throw-before','throw-after','unexpected','unknown','recovery','conflict','recovered-unknown')]
    if args.only:tasks=[t for t in tasks if t[1]==args.only]
    try:
        with sync_playwright() as pw:
            browser=pw.chromium.launch()
            for case,mode in tasks:
                try:record=run_case(browser,f'http://127.0.0.1:{server.server_port}/index.html',case,mode)
                except Exception as error:record={'case':case,'mode':mode,'classification':'TEST_HARNESS_FAIL','error':str(error)}
                results.append(record)
                args.artifact.write_text(json.dumps({'root':str(root),'suite_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'results':results},ensure_ascii=False,indent=2))
                print(json.dumps({k:v for k,v in record.items() if k not in ('before','after','action_return')},ensure_ascii=False),flush=True)
            if args.mode=='full' and args.only in (None,'ui'):
                for case in ('nc-edit','pv-create','note-create','note-edit'):
                    for width in (1440,390):
                        try:record=run_ui(browser,f'http://127.0.0.1:{server.server_port}/index.html',case,width,args.artifact)
                        except Exception as error:record={'case':case,'mode':'ui-'+str(width),'classification':'TEST_HARNESS_FAIL','error':str(error)}
                        results.append(record)
                        print(json.dumps({k:v for k,v in record.items() if k not in ('before','refused','retried')},ensure_ascii=False),flush=True)
            if args.mode=='full' and args.only in (None,'missing'):
                results.append(run_missing_note(browser,f'http://127.0.0.1:{server.server_port}/index.html'))
            if args.mode=='full' and args.only in (None,'folders'):
                for rename in (False,True):
                    try:record=run_folder_prompt(browser,f'http://127.0.0.1:{server.server_port}/index.html',rename)
                    except Exception as error:record={'case':'folder-rename' if rename else 'folder-create','mode':'native-prompt','classification':'TEST_HARNESS_FAIL','error':str(error)}
                    results.append(record);print(json.dumps(record,ensure_ascii=False),flush=True)
            if args.mode=='full' and args.only in (None,'folder-reference'):
                for mode in ('normal','dirty','other-folder','quota'):
                    try:record=run_folder_reference(browser,f'http://127.0.0.1:{server.server_port}/index.html',mode)
                    except Exception as error:record={'case':'folder-reference','mode':mode,'classification':'TEST_HARNESS_FAIL','error':str(error)}
                    results.append(record)
                    print(json.dumps({k:v for k,v in record.items() if k not in ('before','after')},ensure_ascii=False),flush=True)
            args.artifact.write_text(json.dumps({'root':str(root),'suite_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'results':results},ensure_ascii=False,indent=2))
            browser.close()
    finally:server.shutdown()
    return 0 if all(r['classification']=='PASS' for r in results) else 1

if __name__=='__main__':sys.exit(main())
