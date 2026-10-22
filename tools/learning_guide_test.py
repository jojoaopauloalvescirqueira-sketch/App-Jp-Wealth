#!/usr/bin/env python3
"""Native guide regression: original UI/writers, disposable Chromium profiles.

Only nominal public-feed fixtures and explicitly named Storage faults are used.
No replacement guide, router, save, observer or persistence implementation.
Run the identical first-entry oracle on --root source-baseline to obtain RED.
"""
import argparse
from datetime import datetime, timezone
from functools import partial
import hashlib
import json
import math
import os
from pathlib import Path
import shutil
import tempfile
import threading
import time
import traceback

from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
from browser_bootstrap_fixture import install_bootstrap, wait_bootstrap, assert_fixture_requests
from browser_fixture_server import BrowserFixtureServer
from notes_launcher_test import Quiet, launch_options

ROOT = Path(__file__).resolve().parents[1]
BASELINE_ROOT = ROOT.parent/'source-baseline'
GUIDE_KEY = 'jpwealth_learning_guide_v1'
MAIN_KEY = 'jpwealth_v9_state'
PORTABLE = 'dist/JP_Wealth_Risk_Terminal_V9.1_PORTABLE.html'
MODULES = ['src/js/40-app/26-learning-catalog.js', 'src/js/00-core/09-learning-progress.js',
           'src/js/40-app/27-learning-view.js', 'src/js/40-app/28-learning-guide.js']
PLANNING_MODULES = [f'src/js/30-accounting/06-planning/{name}.js' for name in ('01-engine','02-state','03-ui')]
RETIRED_PLANNING_MODULES = [f'src/js/30-accounting/05-fx-planning/{name}.js' for name in ('01-fx-model','02-fx-engine','03-fx-state','04-fx-charts','05-fx-ui')]
SOURCES = MODULES + PLANNING_MODULES + ['src/styles/app.css', 'src/js/40-app/01-navigation.js',
    'src/js/40-app/06-boot.js', 'src/js/40-app/07-finalize-session.js',
    'src/js/40-app/09-settings-modal.js', 'src/js/00-core/04-persistence.js',
    'src/js/00-core/07-workspace-backup.js', 'src/js/20-ui/18-finpes-budget.js',
    'src/js/40-app/14-mvp-notes.js', 'src/js/manifest.json', 'index.html',
    'sw.js', 'build-id.js', PORTABLE]

def hashes(root):
    return {name: hashlib.sha256((root/name).read_bytes()).hexdigest()
            if (root/name).is_file() else None for name in SOURCES}

def settle(page):
    page.evaluate('() => new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)))')

def snap(page):
    return page.evaluate('JPWLearningGuide.snapshot()')

def financial(page):
    return page.evaluate("""() => ({state:JSON.stringify(S),raw:window.__lgStorage?
      __lgStorage.get.call(localStorage,'jpwealth_v9_state'):localStorage.getItem('jpwealth_v9_state'),
      writes:window.__lgStorage?.writes.filter(x=>x.key==='jpwealth_v9_state')||[]})""")

def invariant(page, before):
    after = financial(page)
    assert after == before, {'financialChanged':[k for k in before if before[k]!=after[k]], 'after':after}

def instrument(page):
    page.evaluate("""() => {
      if(window.__lgStorage)return;
      const get=Storage.prototype.getItem,set=Storage.prototype.setItem,remove=Storage.prototype.removeItem;
      window.__lgStorage={get,set,remove,writes:[],mode:'normal',key:null,post:false};
      Storage.prototype.setItem=function(key,value){
        const t=__lgStorage;
        if(this===localStorage){t.writes.push({key,kind:'attempt'});
          if(key===t.key&&t.mode==='refused')throw new DOMException('Named guide test quota','QuotaExceededError');
        }
        const out=set.call(this,key,value);
        if(this===localStorage){t.writes.push({key,kind:'committed'});if(key===t.key&&t.mode==='unknown')t.post=true;}
        return out;
      };
      Storage.prototype.getItem=function(key){const t=__lgStorage;
        if(this===localStorage&&key===t.key&&(t.mode==='read-refused'||t.mode==='unknown'&&t.post))
          throw new DOMException('Named guide test read interruption','SecurityError');
        return get.call(this,key);
      };
    }""")

def fault(page, mode, key):
    instrument(page)
    page.evaluate('([mode,key])=>Object.assign(__lgStorage,{mode,key,post:false})',[mode,key])

def receipt(page):
    return page.evaluate('jpWealthPersistenceLastResult()')

def record(page, step):
    return snap(page)['progress']['steps'].get(step)

def seen(page, step, practice=None):
    page.wait_for_function("([id,p])=>JPWLearningGuide.snapshot().progress.steps[id]?.orientation==='seen'&&JPWLearningGuide.snapshot().progress.steps[id]?.practice===p",arg=[step,practice])

def click(page, selector):
    target=page.locator(selector).filter(visible=True).first
    target.click()
    settle(page)

def keyboard_click(page, selector):
    target=page.locator(selector).filter(visible=True).first
    target.focus();page.keyboard.press('Enter');settle(page)

def pointer_uncovered(page, selector):
    target=page.locator(selector).filter(visible=True).first
    target.scroll_into_view_if_needed();settle(page)
    measurement=target.evaluate("""e=>{const r=e.getBoundingClientRect(),x=r.x+r.width/2,y=r.y+r.height/2,
      hit=document.elementFromPoint(x,y);return {x,y,width:r.width,height:r.height,
      uncovered:hit===e||e.contains(hit),hit:hit?.id||hit?.tagName};}""")
    assert measurement['uncovered'], {'selector':selector,**measurement}
    return measurement

def central(page):
    assert page.evaluate('JPWLearningGuide.open()') is True
    page.locator('#jpwLearningCenter').wait_for(state='visible')
    assert page.locator('#jpwLearningCenter').count()==1

def start(page, track):
    central(page);click(page,f'[data-learning-track="{track}"]')
    page.locator('#jpwLearningCoach').wait_for(state='visible')

def recover_owned_transition(page):
    """Close only an owned native surface after the coach explicitly suspends."""
    if not snap(page)['paused']:
        return
    for selector in ['#mvpNotesNewCancelBtn','#mvpNotesCloseBtn','#forexChecklistClose','#settingsCloseBtn']:
        if page.locator(selector).is_visible():
            keyboard_click(page,selector)
            break
    if page.locator('#jpwLearningGo').is_visible():
        click(page,'#jpwLearningGo')
    else:
        central(page);click(page,'#jpwLearningResume')
    assert not snap(page)['paused'], snap(page)

def reach(page, track, step):
    start(page,track)
    for _ in range(60):
        recover_owned_transition(page)
        if snap(page)['stepId']==step:
            return
        if snap(page)['stepId']=='general-notes':
            complete_action(page,{'id':'general-notes','action':'notes'});click(page,'#jpwLearningNext')
            continue
        click(page,'#jpwLearningSkip')
    raise AssertionError('Target lesson not reached: '+step)

def complete_action(page, step):
    action=step.get('action')
    if action=='menu':
        selector='[data-shell-menu-toggle]' if page.locator('[data-shell-menu-toggle]').is_visible() else '[data-route="dashboard"]'
        pointer_uncovered(page,selector);keyboard_click(page,selector);seen(page,step['id'])
        if page.evaluate("typeof shellUI!=='undefined'&&shellUI.open"):
            page.keyboard.press('Escape');settle(page)
    elif action=='help':
        help_button=page.locator('.note-i').filter(visible=True).first
        if not help_button.count():
            assert step.get('allowRead'),'Native action has no approved reading fallback'
            click(page,'#jpwLearningUnderstand');seen(page,step['id'])
            return 'declared-read-fallback'
        help_button.focus();page.keyboard.press('Enter');seen(page,step['id'])
        if help_button.get_attribute('aria-expanded')=='true':
            help_button.focus();page.keyboard.press('Enter');settle(page)
    elif action=='notes':
        pointer_uncovered(page,'#headerNotesBtn');keyboard_click(page,'#headerNotesBtn')
        page.locator('#mvpNotesOverlay').wait_for(state='visible');seen(page,step['id'])
    elif action=='session':
        pointer_uncovered(page,'#finalizeSessionBtn');keyboard_click(page,'#finalizeSessionBtn')
        page.locator('#sessionCancel').wait_for(state='visible')
        assert record(page,step['id']) is None,'Opening session alone completed the lesson'
        keyboard_click(page,'#sessionCancel');seen(page,step['id'])
    else:
        raise AssertionError('Unhandled native action '+str(action))
    return 'observed'

def welcome(page, row):
    page.locator('#jpwWelcomeExplore').wait_for(state='visible')
    instrument(page);before=financial(page)
    click(page,'#jpwWelcomeExplore')
    # This is intentionally the first oracle: absent guide fails frozen baseline.
    page.locator('#jpwLearningCenter').wait_for(state='visible')
    assert page.evaluate("JPWNavigation.current().canonical==='dashboard'")
    assert not page.locator('#jpwWelcome').is_visible()
    assert page.locator('[data-learning-track]').count()==7
    assert page.locator('#jpwLearningCenter').count()==1
    invariant(page,before)
    click(page,'#settingsCloseBtn')
    keyboard_click(page,'#headerConfigBtn')
    assert page.evaluate("settingsNavigateToLeaf('learning-guide',{focus:false})") is not False
    page.locator('#jpwLearningCenter').wait_for(state='visible')
    assert page.locator('[data-settings-panel="learning-guide"] #jpwLearningCenter').count()==1
    assert page.evaluate("SETTINGS_NAV.some(x=>x.id==='knowledge')") if page.evaluate("typeof SETTINGS_NAV!=='undefined'") else True
    row['trackCount']=7

def readonly(page, row):
    instrument(page);before=financial(page)
    tracks=page.evaluate('JPWLearningCatalog.tracks')
    assert len(tracks)==7 and sum(len(t['steps']) for t in tracks)==57
    actions=[];completed=[];fallbacks=[]
    for track in tracks:
        start(page,track['id'])
        for step in track['steps']:
            recover_owned_transition(page)
            assert snap(page)['stepId']==step['id'],snap(page)
            page.locator('#jpwLearningCoach').wait_for(state='visible')
            assert page.locator('#jpwLearningCoach').get_attribute('data-learning-step')==step['id']
            if step.get('kind')=='action':
                outcome=complete_action(page,step)
                if outcome=='observed':actions.append(step['action'])
                else:fallbacks.append({'step':step['id'],'reason':'No native i at declared destination; approved Entendi reading fallback'})
            else:
                click(page,'#jpwLearningUnderstand');seen(page,step['id'])
            assert record(page,step['id'])=={'orientation':'seen','practice':None}
            completed.append(step['id']);invariant(page,before)
            click(page,'#jpwLearningNext')
    records=snap(page)['progress']['steps']
    assert len(records)==57 and all(r=={'orientation':'seen','practice':None} for r in records.values())
    assert actions in [['menu','help','notes','session'],['menu','notes','session']],actions
    invariant(page,before)
    row.update(completedLessonIds=completed,seenCount=57,skippedCount=0,confirmedPracticeCount=0,observedNativeActions=actions,declaredReadFallbacks=fallbacks,mainWrites=0)

def progress_lifecycle(page,row):
    instrument(page);before=financial(page);start(page,'basics')
    click(page,'#jpwLearningUnderstand');seen(page,'basics-home')
    click(page,'#jpwLearningNext');click(page,'#jpwLearningSkip')
    assert record(page,'basics-menu')=={'orientation':'skipped','practice':None}
    step=snap(page)['stepId'];click(page,'#jpwLearningPause')
    raw=page.evaluate('localStorage.getItem('+json.dumps(GUIDE_KEY)+')')
    page.reload();wait_bootstrap(page);settle(page)
    assert snap(page)['stepId']==step and snap(page)['paused']
    assert page.evaluate('localStorage.getItem('+json.dumps(GUIDE_KEY)+')')==raw
    central(page);click(page,'#jpwLearningResume');assert not snap(page)['paused']
    click(page,'#jpwLearningBack');assert record(page,'basics-menu')['orientation']=='skipped'
    central(page);click(page,'#jpwLearningRestart')
    assert snap(page)['progress']['steps']=={} and snap(page)['trackId'] is None
    assert page.evaluate('localStorage.getItem('+json.dumps(GUIDE_KEY)+')') is None
    after=financial(page);assert after['state']==before['state'] and after['raw']==before['raw']
    row.update(skipDistinct=True,reloadCursor=step,resetOnlyGuide=True)

def invalid_progress(page,row):
    raw='{"schemaVersion":99,"catalogVersion":99,"private":"must survive"}'
    page.evaluate('([k,v])=>localStorage.setItem(k,v)',[GUIDE_KEY,raw]);page.reload();wait_bootstrap(page)
    before=financial(page);central(page)
    assert snap(page)['storage']=='blocked'
    click(page,'[data-learning-track="basics"]')
    assert page.evaluate('(k)=>localStorage.getItem(k)',GUIDE_KEY)==raw
    click(page,'#jpwLearningRestart')
    assert page.evaluate('(k)=>localStorage.getItem(k)',GUIDE_KEY) is None
    invariant(page,before);row['incompatibleRawPreservedUntilRestart']=True

def guide_storage(page,row,mode):
    before=financial(page);fault(page,mode,GUIDE_KEY)
    if mode=='read-refused':
        page.evaluate("JPWLearningGuide.revalidate('import')")
    start(page,'basics');click(page,'#jpwLearningUnderstand')
    assert record(page,'basics-home')=={'orientation':'seen','practice':None}
    assert snap(page)['storage']=='memory' and 'sessão' in snap(page)['notice']
    invariant(page,before);row.update(fault=mode,storage=snap(page)['storage'])

def cross_tab(page,row):
    start(page,'basics');before=financial(page)
    other=page.context.new_page();other.goto(page.url);wait_bootstrap(other);settle(other)
    central(other);click(other,'[data-learning-track="personal-finance"]')
    competing=other.evaluate('(k)=>localStorage.getItem(k)',GUIDE_KEY)
    # Storage notification may already have paused the first tab; its next command
    # still must retain the other tab's exact receipt rather than claiming home.
    if page.locator('#jpwLearningUnderstand').is_visible() and page.locator('#jpwLearningUnderstand').is_enabled():
        click(page,'#jpwLearningUnderstand')
    else:
        assert snap(page)['paused'],'Concurrent storage notification must pause before another action'
    assert page.evaluate('(k)=>localStorage.getItem(k)',GUIDE_KEY)==competing
    assert snap(page)['paused'] and record(page,'basics-home') is None
    invariant(page,before);other.close();row['competingRawPreserved']=True

def suspension(page,row,kind):
    before=financial(page)
    if kind in {'frozen-alladin','frozen-personal-finance'}:
        module = 'alladin' if kind=='frozen-alladin' else 'personal-finance'
        first_step = 'alladin-start' if module=='alladin' else 'personal-finance-overview'
        availability=page.evaluate("localStorage.getItem('jpw_module_availability_v1')")
        assert page.evaluate("id=>!JPWModuleAvailability.canAccess(id)",module)
        central(page);click(page,'[data-learning-track="'+module+'"]');assert snap(page)['paused']
        assert 'congelado' in snap(page)['notice'].lower(),snap(page)
        assert page.evaluate("localStorage.getItem('jpw_module_availability_v1')")==availability
        assert record(page,first_step) is None
    elif kind=='missing-anchor':
        start(page,'basics');page.locator('#dash').evaluate('e=>e.hidden=true');settle(page)
        assert snap(page)['paused'] and record(page,'basics-home') is None
    elif kind=='off-route':
        start(page,'basics');assert page.evaluate("JPWNavigation.navigate('personal-finance')")
        settle(page);assert snap(page)['paused'] and record(page,'basics-home') is None
    else:
        start(page,'basics');keyboard_click(page,'#finalizeSessionBtn')
        page.locator('#sessionCancel').wait_for(state='visible');settle(page)
        assert snap(page)['paused'];dialog=page.locator('#modalBox').inner_text()
        assert page.evaluate("JPWLearningGuide.start('personal-finance')") is False
        assert page.locator('#modalBox').inner_text()==dialog
        keyboard_click(page,'#sessionCancel')
    invariant(page,before);row['suspension']=kind

def geometry(page,row):
    instrument(page);before=financial(page);start(page,'basics')
    metrics=page.locator('#jpwLearningCoach').evaluate("""e=>{const r=e.getBoundingClientRect(),v=visualViewport;
      return {x:r.x,y:r.y,right:r.right,bottom:r.bottom,width:r.width,height:r.height,
      viewport:{width:v.width,height:v.height,left:v.offsetLeft,top:v.offsetTop},
      docWidth:document.documentElement.scrollWidth,innerWidth};}""")
    v=metrics['viewport'];assert metrics['x']>=v['left']-1 and metrics['right']<=v['left']+v['width']+1,metrics
    assert metrics['y']>=v['top']-1 and metrics['bottom']<=v['top']+v['height']+1,metrics
    assert metrics['docWidth']<=metrics['innerWidth']+1,metrics
    page.locator('#jpwLearningUnderstand').focus();page.keyboard.press('Enter');seen(page,'basics-home')
    page.locator('#jpwLearningNext').focus();page.keyboard.press('Enter');settle(page)
    assert page.evaluate("document.activeElement?.closest('#jpwLearningCoach')!==null"),'Guide transition lost keyboard focus'
    pointer_uncovered(page,'[data-shell-menu-toggle]' if page.locator('[data-shell-menu-toggle]').is_visible() else '[data-route="dashboard"]')
    invariant(page,before);row['geometry']=metrics

def cleanup(page,row):
    instrument(page);before=financial(page);start(page,'basics');click(page,'#jpwLearningUnderstand')
    assert page.evaluate('(k)=>localStorage.getItem(k)',GUIDE_KEY)
    click(page,'#jpwLearningNext')
    selector='[data-shell-menu-toggle]' if page.locator('[data-shell-menu-toggle]').is_visible() else '[data-route="dashboard"]'
    page.evaluate("""selector=>{window.__lgCleanupResult=null;
      document.addEventListener('click',event=>{if(!event.isTrusted||!event.target.closest?.(selector))return;
        // This fixture hook runs after the original trusted action, before its
        // pending observer/subscription animation frame can write completion.
        sessionResetAuxiliarySurfaces();window.__lgCleanupResult=clearJPWealthLocalData({removeAuxiliary:true,removeCorrupted:false,preserveMain:true});
      },{once:true});}""",selector)
    keyboard_click(page,selector);result=page.evaluate('__lgCleanupResult')
    assert result.get('ok') is True,result
    assert GUIDE_KEY in result['removedKeys'],result
    assert page.evaluate('(k)=>localStorage.getItem(k)',GUIDE_KEY) is None
    assert snap(page)['paused'] and not snap(page)['active']
    assert not page.locator('#jpwLearningCoach').is_visible()
    page.evaluate("""() => {window.dispatchEvent(new StorageEvent('storage',{key:'jpwealth_learning_guide_v1',newValue:null}));}""")
    settle(page);assert page.evaluate('(k)=>localStorage.getItem(k)',GUIDE_KEY) is None
    assert page.evaluate("JPWLearningGuide.start('basics')") is False
    page.evaluate('boot()')
    assert page.evaluate('(k)=>localStorage.getItem(k)',GUIDE_KEY) is None
    start(page,'basics');assert not snap(page)['paused']
    invariant(page,before);row['removedKeys']=result['removedKeys'];row['staleCallbacksNoResurrection']=True

def pf_fixture(page):
    page.evaluate("""() => {S.personalFinance=structuredClone(DEFAULTS.personalFinance);
      S.personalFinance.months[pfCurrentMonthKey()]={createdAt:new Date().toISOString(),
        incomes:[{id:'pfi_guide_fixture',name:'Synthetic guide income',projectedAmount:10000,
          receivedAmount:null,status:'PROJETADA',ruleId:null}],expenses:[],debtSnapshots:[],allocations:[],notes:''};
      if(save()!==true)throw Error('HARNESS_SETUP: PF fixture refused');}""")
    page.reload();wait_bootstrap(page);settle(page)

def private_free_progress(page):
    progress=snap(page)['progress']
    assert set(progress)=={'schemaVersion','catalogVersion','trackId','stepId','paused','steps'}
    known=page.evaluate('JPWLearningCatalog.tracks.flatMap(t=>t.steps.map(s=>s.id))')
    for key,value in progress['steps'].items():
        assert key in known and set(value)=={'orientation','practice'}
        assert value['orientation'] in ['seen','skipped'] and value['practice'] in [None,'confirmed']
    text=json.dumps(progress)
    assert all(word not in text for word in ['pfi_guide_fixture','Synthetic guide income','12345','Synthetic native note'])

def visible_practice_instruction(page,row):
    """Original save semantics must be readable before the user arms practice."""
    information=page.evaluate("""() => {const cursor=JPWLearningGuide.snapshot(),step=JPWLearningCatalog.tracks.flatMap(t=>t.steps).find(s=>s.id===cursor.stepId);
      return {stepId:cursor.stepId,instruction:step?.practiceInstruction,layout:document.getElementById('jpwLearningCoach')?.dataset.learningLayout||null};}""")
    assert information['instruction'],'Current optional practice has no catalog save-semantics instruction'
    matches=page.locator('#jpwLearningCoach').get_by_text(information['instruction'],exact=True)
    visible=matches.filter(visible=True)
    evidence={**information,'matchingCopies':matches.count(),'visibleCopies':visible.count()}
    row.setdefault('practiceNoticeEvidence',[]).append(evidence)
    assert visible.count()>0,{'failure':'Original save-semantics notice is hidden before enabled Practice Start','evidence':evidence}
    notice=visible.first
    assert notice.inner_text()==information['instruction']
    evidence['paragraphId']=notice.get_attribute('id')
    evidence['insideClosedDetails']=notice.evaluate("e=>!!e.closest('details:not([open])')")
    if information['layout']=='flow':
        assert not evidence['insideClosedDetails'],'Compact guide hides original save semantics in a collapsed disclosure'
    notice.scroll_into_view_if_needed();settle(page)
    assert notice.is_visible()
    evidence['practiceStartPointer']=pointer_uncovered(page,'#jpwLearningPracticeStart')
    assert page.locator('#jpwLearningPracticeStart').is_enabled()

def pf_practice(page,row,kind):
    pf_fixture(page);reach(page,'personal-finance','personal-finance-budget')
    field=page.locator('#finpesBudgetRoot [data-fi-campo="projectedAmount"][data-fi-id="pfi_guide_fixture"]')
    assert field.is_visible() and field.is_enabled()
    instrument(page)
    row['nativeBackupReminderDismissedByUser']=False
    if page.locator('#dgBannerClose').is_visible():
        dismissal_before=financial(page)
        writes_before=page.evaluate('__lgStorage.writes.length')
        assert page.locator('#dgBackupBanner').is_visible()
        close_pointer=pointer_uncovered(page,'#dgBannerClose')
        click(page,'#dgBannerClose')
        assert page.locator('#dgBackupBanner').count()==0,'Original backup reminder was not removed by its native X'
        invariant(page,dismissal_before)
        writes_after=page.evaluate('__lgStorage.writes.length')
        assert writes_after==writes_before,'Dismissing original reminder wrote browser storage'
        row['nativeBackupReminderDismissedByUser']=True
        row['nativeBackupReminderDismissal']={'visibleBefore':True,'closeButtonPointer':close_pointer,
          'removedAfterTrustedClick':True,'financialUnchanged':True,'storageWritesBefore':writes_before,'storageWritesAfter':writes_after}
    row['practiceBannerState']='dismissed-by-native-X' if row['nativeBackupReminderDismissedByUser'] else 'absent-before-practice'
    before=financial(page);prior=receipt(page)
    visible_practice_instruction(page,row)
    click(page,'#jpwLearningPracticeStart')
    assert record(page,'personal-finance-budget') is None
    row['nativeFieldPointer']=pointer_uncovered(page,'#finpesBudgetRoot [data-fi-campo="projectedAmount"][data-fi-id="pfi_guide_fixture"]')
    if kind=='escape':
        field.fill('987,65');assert page.evaluate('fbPendingFields.size')>0
        invariant(page,before);field.press('Escape');field.press('Tab');settle(page)
        assert page.evaluate('fbPendingFields.size')==0
        invariant(page,before);assert record(page,'personal-finance-budget') is None
        assert not snap(page)['paused'],'Input Escape was stolen by guide'
    else:
        if kind in ['refused','unknown']:fault(page,kind,MAIN_KEY)
        field.fill('123,45');field.press('Tab');settle(page)
        got=receipt(page);raw=financial(page)['raw']
        durable=json.loads(raw)['personalFinance']['months']
        month=page.evaluate('fbCurrentKey()')
        amount=next(x for x in durable[month]['incomes'] if x['id']=='pfi_guide_fixture')['projectedAmount']
        if kind=='confirmed':
            assert got['status']=='CONFIRMED' and got['reason']=='READBACK_MATCH' and got!=prior,got
            assert got['context']==prior['context'] and got['epoch']==prior['epoch'] and amount==12345
            seen(page,'personal-finance-budget','confirmed')
            page.reload();wait_bootstrap(page);settle(page)
            assert page.evaluate("S.personalFinance.months[pfCurrentMonthKey()].incomes.find(x=>x.id==='pfi_guide_fixture').projectedAmount")==12345
        elif kind=='refused':
            assert got['status']=='REFUSED' and got['reason'] in ['WRITE_REFUSED','WRITE_NOT_APPLIED'],got
            assert raw==before['raw'] and page.evaluate('JSON.stringify(S)')==before['state']
            assert record(page,'personal-finance-budget') is None
            assert field.input_value()=='123,45','Refused original input draft was discarded'
            fault(page,'normal',None);field.focus();field.fill('234,56');field.press('Tab');settle(page)
            assert receipt(page)['status']=='CONFIRMED';seen(page,'personal-finance-budget','confirmed')
        else:
            assert got['status']=='UNKNOWN' and got['reason']=='READ_AFTER_WRITE',got
            assert page.evaluate('jpWealthPersistenceOutcomeIsUnknown()')
            assert record(page,'personal-finance-budget') is None
            attempts=page.evaluate("__lgStorage.writes.filter(x=>x.key===LSKEY&&x.kind==='attempt').length")
            field.fill('345,67');field.press('Tab');settle(page)
            assert page.evaluate("__lgStorage.writes.filter(x=>x.key===LSKEY&&x.kind==='attempt').length")==attempts
        row.update(receipt=got,durableAmount=amount,priorReceipt=prior)
    private_free_progress(page);row['nativePF']=kind

def notes_new(page):
    keyboard_click(page,'#mvpNotesNewBtn');page.locator('#mvpNotesNewBox').wait_for(state='visible')
    defaults=page.evaluate("[mvpNotesNewType.value,mvpNotesNewPriority.value,mvpNotesNewStatus.value,mvpNotesNewFolder.value,mvpNotesNewPolicy.value]")
    assert defaults==['task','medium','open','','analysis_only'],defaults
    for selector,value in [('#mvpNotesNewType','bug'),('#mvpNotesNewPriority','critical'),('#mvpNotesNewStatus','in_progress'),('#mvpNotesNewFolder',''),('#mvpNotesNewPolicy','blocked')]:
        page.locator(selector).select_option(value)
    keyboard_click(page,'#mvpNotesNewConfirmBtn');page.locator('#mvpNoteContent').wait_for(state='visible')

def notes_practice(page,row,kind):
    reach(page,'general','general-notes-save')
    instrument(page);before=financial(page);click(page,'#jpwLearningPracticeStart')
    notes_new(page);invariant(page,before)
    metadata=page.evaluate('structuredClone(mvpNotesUI.draft)')
    assert metadata=={'content':'','type':'bug','priority':'critical','status':'in_progress','folderId':None,'aiImplementationPolicy':'blocked'},metadata
    assert page.evaluate('S.mvpNotes.items.length')==0
    page.locator('#mvpNoteContent').fill('Synthetic native note\nSecond fixture line')
    assert page.evaluate('mvpNotesUI.draftDirty')
    if kind=='dirty-refusal':
        dialogs=[]
        def dismiss(dialog):dialogs.append(dialog.message);dialog.dismiss()
        page.on('dialog',dismiss);draft=page.evaluate('structuredClone(mvpNotesUI.draft)')
        keyboard_click(page,'#mvpNotesCloseBtn')
        assert dialogs and page.evaluate('mvpNotesUI.open&&mvpNotesUI.draftDirty')
        assert page.evaluate('structuredClone(mvpNotesUI.draft)')==draft
        invariant(page,before);assert record(page,'general-notes-save') is None
        page.locator('#mvpNoteContent').press('Escape');settle(page)
        assert page.evaluate('mvpNotesUI.draftDirty') and page.locator('#mvpNotesOverlay').is_visible()
        invariant(page,before);row['nativeDiscardDialogs']=dialogs
    else:
        if kind in ['refused','unknown']:fault(page,kind,MAIN_KEY)
        prior=receipt(page);draft=page.evaluate('structuredClone(mvpNotesUI.draft)')
        keyboard_click(page,'#mvpNotesSaveBtn');got=receipt(page)
        if kind=='confirmed':
            assert got['status']=='CONFIRMED' and got['reason']=='READBACK_MATCH' and got!=prior,got
            assert got['context']==prior['context'] and got['epoch']==prior['epoch']
            item=page.evaluate('S.mvpNotes.items.find(x=>x.id===mvpNotesUI.selectedId)')
            assert item and all(item.get(k)==v for k,v in draft.items()) and item['title']=='Synthetic native note',item
            assert not page.evaluate('mvpNotesUI.draftDirty');seen(page,'general-notes-save','confirmed')
            page.reload();wait_bootstrap(page);settle(page)
            assert page.evaluate('(id)=>S.mvpNotes.items.find(x=>x.id===id)',item['id'])==item
            row['durableNote']=item
        elif kind=='refused':
            assert got['status']=='REFUSED',got
            assert financial(page)['raw']==before['raw'] and page.evaluate('S.mvpNotes.items.length')==0
            assert page.evaluate('mvpNotesUI.draftDirty') and page.evaluate('structuredClone(mvpNotesUI.draft)')==draft
            assert record(page,'general-notes-save') is None
            fault(page,'normal',None);keyboard_click(page,'#mvpNotesSaveBtn');seen(page,'general-notes-save','confirmed')
        else:
            assert got['status']=='UNKNOWN' and got['reason']=='READ_AFTER_WRITE',got
            assert record(page,'general-notes-save') is None and page.evaluate('jpWealthPersistenceOutcomeIsUnknown()')
        row.update(receipt=got,priorReceipt=prior)
    private_free_progress(page);row['nativeNotes']=kind

def notes_cancel(page,row,kind):
    reach(page,'general','general-notes-save');instrument(page);before=financial(page)
    click(page,'#jpwLearningPracticeStart');keyboard_click(page,'#mvpNotesNewBtn')
    page.locator('#mvpNotesNewBox').wait_for(state='visible')
    for _ in range(9):
        page.keyboard.press('Tab')
        assert page.evaluate("document.activeElement?.closest('#mvpNotesNewBox')!==null"),'Tab escaped original metadata focus host'
    page.keyboard.press('Shift+Tab')
    assert page.evaluate("document.activeElement?.closest('#mvpNotesNewBox')!==null")
    if kind=='escape':page.keyboard.press('Escape')
    elif kind=='backdrop':
        page.locator('#mvpNotesNewOverlay').click(position={'x':2,'y':2})
    else:click(page,'#mvpNotesNewCancelBtn')
    settle(page);assert not page.locator('#mvpNotesNewBox').is_visible()
    assert page.locator('#mvpNotesOverlay').is_visible() and page.evaluate('S.mvpNotes.items.length')==0
    row['focusAfterDismissal']=page.evaluate("({id:document.activeElement?.id,tag:document.activeElement?.tagName,insideCoach:!!document.activeElement?.closest('#jpwLearningCoach')})")
    if kind!='backdrop':
        assert page.evaluate("document.activeElement===document.getElementById('mvpNotesNewBtn')"),row['focusAfterDismissal']
    else:
        row['baselineFocus']=native_backdrop_focus(page)
        assert row['focusAfterDismissal']==row['baselineFocus'],'Guide changed original backdrop focus ownership'
    assert record(page,'general-notes-save') is None
    invariant(page,before);row['metadataCancelledBy']=kind

def native_backdrop_focus(page):
    """Same original dismissal on frozen original source, with no guide injected."""
    if not (BASELINE_ROOT/'index.html').is_file():
        raise RuntimeError('HARNESS_BASELINE: --baseline-root must contain frozen index.html for backdrop ownership comparison')
    server=BrowserFixtureServer(('127.0.0.1',0),partial(Quiet,directory=str(BASELINE_ROOT)))
    threading.Thread(target=server.serve_forever,daemon=True).start()
    context=page.context.browser.new_context(viewport={'width':1440,'height':1000},service_workers='block')
    try:
        install_bootstrap(context);context.add_init_script('window.__onbShown=true;')
        original=context.new_page();original.set_default_timeout(7000)
        original.goto(f'http://127.0.0.1:{server.server_port}/index.html');wait_bootstrap(original)
        original.evaluate('S.mvpNotes.showHeaderIcon=true;renderMvpNotesHeader()')
        keyboard_click(original,'#headerNotesBtn');keyboard_click(original,'#mvpNotesNewBtn')
        for _ in range(9):original.keyboard.press('Tab')
        original.keyboard.press('Shift+Tab')
        original.locator('#mvpNotesNewOverlay').click(position={'x':2,'y':2});settle(original)
        assert not original.locator('#mvpNotesNewBox').is_visible() and original.locator('#mvpNotesOverlay').is_visible()
        assert_fixture_requests(context)
        return original.evaluate("({id:document.activeElement?.id,tag:document.activeElement?.tagName,insideCoach:!!document.activeElement?.closest('#jpwLearningCoach')})")
    finally:
        context.close();server.shutdown();server.server_close()

def backup(page,row):
    start(page,'basics');click(page,'#jpwLearningUnderstand');central(page)
    assert page.evaluate("settingsNavigateToLeaf('backup',{focus:false})") is not False
    page.locator('#exportFullBackupBtn').wait_for(state='visible')
    guide_raw=page.evaluate('(k)=>localStorage.getItem(k)',GUIDE_KEY)
    with page.expect_download() as download:
        keyboard_click(page,'#exportFullBackupBtn')
    artifact=download.value;path=artifact.path();assert path and artifact.failure() is None
    payload=json.loads(Path(path).read_text())
    inspected=page.evaluate('async value=>await JPWBackup.inspect(value)',payload)
    assert inspected.get('kind')=='FULL_V2' and inspected.get('legacy') is False and inspected.get('missing')==[],inspected
    assert payload['formatVersion']==2
    assert GUIDE_KEY not in payload['workspace']['preferences']
    assert GUIDE_KEY not in page.evaluate('JPW_WORKSPACE_KEYS')
    text=json.dumps(payload);assert GUIDE_KEY not in text and 'basics-home' not in text
    assert page.evaluate('(k)=>localStorage.getItem(k)',GUIDE_KEY)==guide_raw
    row.update(actualDownload=artifact.suggested_filename,backupInspection=inspected)

def import_revalidation(page,row):
    pf_fixture(page)
    exported=page.evaluate("async()=>await dgBuildBackupBlob(1,'synthetic-guide-import.json',new Date().toISOString()).text()")
    payload=json.loads(exported)
    assert payload['formatVersion']==2 and GUIDE_KEY not in exported
    page.evaluate("""() => {S.personalFinance.months[pfCurrentMonthKey()].incomes[0].projectedAmount=20000;
      if(save()!==true)throw Error('HARNESS_SETUP: synthetic alternate base refused');}""")
    reach(page,'personal-finance','personal-finance-budget');click(page,'#jpwLearningPracticeStart')
    field=page.locator('#finpesBudgetRoot [data-fi-campo="projectedAmount"][data-fi-id="pfi_guide_fixture"]')
    field.fill('987,65');assert page.evaluate('fbPendingFields.size')>0
    old_receipt=receipt(page);old_base_epoch=page.evaluate("localStorage.getItem('jpwealth_base_epoch_v1')")
    old_raw=page.evaluate('(k)=>localStorage.getItem(k)',GUIDE_KEY)
    dialogs=[]
    def decide(dialog):
        dialogs.append({'type':dialog.type,'message':dialog.message});dialog.accept()
    page.on('dialog',decide)
    # Native FileReader/importer, native validation, confirmation and writer.
    # No substituted save/import/progress function or forged receipt.
    page.evaluate('(text)=>importFullBackupFile(new File([text],"synthetic-guide-import.json",{type:"application/json"}))',exported)
    page.wait_for_function("S.personalFinance.months[pfCurrentMonthKey()].incomes.find(x=>x.id==='pfi_guide_fixture').projectedAmount===10000")
    settle(page);assert any(d['type']=='confirm' for d in dialogs) and any('sucesso' in d['message'].lower() for d in dialogs),dialogs
    row['postImportReceipt']=receipt(page)
    row['postImportBaseEpoch']=page.evaluate("localStorage.getItem('jpwealth_base_epoch_v1')")
    assert row['postImportReceipt']['status']=='CONFIRMED' and row['postImportReceipt']['reason']=='READBACK_MATCH' and row['postImportReceipt']!=old_receipt,row['postImportReceipt']
    # Persistence receipt epoch is a separate guard counter; healthy import
    # rotates the durable session base generation through its native protocol.
    assert row['postImportBaseEpoch'] and row['postImportBaseEpoch']!=old_base_epoch
    assert snap(page)['paused'] and record(page,'personal-finance-budget') is None
    assert page.evaluate('(k)=>localStorage.getItem(k)',GUIDE_KEY)==old_raw
    assert not page.locator('#jpwLearningCoach').is_visible()
    page.evaluate("window.dispatchEvent(new StorageEvent('storage',{key:'jpwealth_v9_state',newValue:localStorage.getItem('jpwealth_v9_state')}))")
    settle(page);assert record(page,'personal-finance-budget') is None
    row.update(nativeImportDialogs=dialogs,preImportReceipt=old_receipt,preImportBaseEpoch=old_base_epoch,guideRawPreserved=True)
    page.reload();wait_bootstrap(page);settle(page)
    assert snap(page)['paused'] and record(page,'personal-finance-budget') is None
    assert page.evaluate('(k)=>localStorage.getItem(k)',GUIDE_KEY)==old_raw

def account_guard(page,row):
    # Original fixture declaration only; strip its storage instrumentation and
    # confirm substitutes by using its materialized account shape through save.
    page.evaluate("""() => {S.accounts=[{forexAccountId:'fx_guide_guard',nome:'Synthetic guard account',
      tipo:'MESTRE',broker:'Synthetic Broker',platform:'MetaTrader 5',platformCurrency:'USD'}];
      const r=JPWForex.state.recordAccountPeriod({accountId:'fx_guide_guard',startedAt:'2026-09-01',
        currency:'USD',si:10000,openingBook:10000,source:'Synthetic guard fixture',activateCurrentPeriod:true},
        {reason:'Synthetic guard fixture'});if(!r.ok)throw Error('HARNESS_SETUP: '+JSON.stringify(r));
      if(save()!==true)throw Error('HARNESS_SETUP: account fixture save');render();}""")
    reach(page,'forex','forex-accounts')
    keyboard_click(page,'#fxAccountsRows [data-fx-examine="fx_guide_guard"]')
    summary=page.locator('details',has=page.locator('#fxAccountFacts')).locator('summary').first
    if not page.locator('#fxAccountFacts input[name="source"]').is_visible():summary.click()
    field=page.locator('#fxAccountFacts input[name="source"]');field.fill('Synthetic pending source')
    assert page.evaluate('JPWForex.accountsUI.hasDrafts()')
    assert page.locator('#fxAccountFacts').get_attribute('data-fx-touched')=='true'
    instrument(page);before=financial(page)
    page.evaluate("() => {window.__lgNav=[];window.__lgUnsub=JPWNavigation.subscribe(e=>window.__lgNav.push(e));}")
    current=page.evaluate('JPWNavigation.current()')
    assert page.evaluate("JPWNavigation.navigate('dashboard')") is False
    page.locator('#fxAccountsLeaveDialog[open]').wait_for(state='visible')
    keyboard_click(page,'#fxAccountsStay')
    assert page.evaluate('JPWNavigation.current()')==current and page.evaluate('__lgNav.length')==0
    assert field.input_value()=='Synthetic pending source'
    assert record(page,'forex-accounts') is None
    assert page.evaluate("JPWNavigation.navigate('dashboard')") is False
    page.locator('#fxAccountsLeaveDialog[open]').wait_for(state='visible')
    page.keyboard.press('Escape');settle(page)
    assert page.evaluate('JPWNavigation.current()')==current and page.evaluate('__lgNav.length')==0
    assert page.evaluate("JPWNavigation.navigate('dashboard')") is False
    keyboard_click(page,'#fxAccountsDiscard')
    page.wait_for_function("JPWNavigation.current().canonical==='dashboard'")
    row['guardDiagnostic']=page.evaluate('({events:__lgNav,drafts:JPWForex.accountsUI.hasDrafts(),current:JPWNavigation.current(),touched:document.getElementById("fxAccountFacts").dataset.fxTouched})')
    assert page.evaluate('__lgNav.length')==1 and not page.evaluate('JPWForex.accountsUI.hasDrafts()'),row['guardDiagnostic']
    assert snap(page)['paused'] and record(page,'forex-accounts') is None
    invariant(page,before);row['acceptedPublications']=page.evaluate('__lgNav');page.evaluate('__lgUnsub()')

def research_drafts(page,row):
    reach(page,'research','research-forex');page.locator('#ncPrice1').fill('1.23412')
    assert page.evaluate('JPWNocodaUI.hasDrafts()')
    draft=page.evaluate('JPWNocodaUI.backupDraft()');instrument(page);before=financial(page)
    page.evaluate("() => {window.__lgNav=[];window.__lgUnsub=JPWNavigation.subscribe(e=>window.__lgNav.push(e));}")
    assert page.evaluate("JPWNavigation.navigate('dashboard')")
    settle(page);assert snap(page)['paused']
    assert page.evaluate("JPWNavigation.navigate('research-forex')")
    assert page.evaluate('JPWNocodaUI.backupDraft()')==draft
    assert page.evaluate('__lgNav.length')==2,page.evaluate('__lgNav')
    old=page.locator('#ncInstrument').input_value()
    alternate=page.locator('#ncInstrument option').evaluate_all('(items)=>items.map(x=>x.value).find(x=>x&&x!==document.querySelector("#ncInstrument").value)')
    assert alternate,'Native research fixture has no second canonical instrument'
    publications=page.evaluate('__lgNav.length');dialogs=[]
    def reject(dialog):dialogs.append(dialog.message);dialog.dismiss()
    page.on('dialog',reject);page.locator('#ncInstrument').select_option(alternate);settle(page)
    assert dialogs and page.locator('#ncInstrument').input_value()==old
    assert page.evaluate('JPWNocodaUI.backupDraft()')==draft and page.evaluate('__lgNav.length')==publications
    assert page.evaluate("JPWNavigation.navigateLocal('research','pivots')")
    keyboard_click(page,'#pvNewStudyBtn');page.locator('#pvPeriodStart').fill('2026-08-01');page.locator('#pvPeriodEnd').fill('2026-08-31')
    assert page.evaluate('JPWPivotsUI.hasDrafts()');pivots=page.evaluate('JPWPivotsUI.backupDraft()')
    assert page.evaluate("JPWNavigation.navigate('dashboard')")
    assert page.evaluate("JPWNavigation.navigate('research-forex')")
    assert page.evaluate("JPWNavigation.navigateLocal('research','pivots')")
    assert page.evaluate('JPWPivotsUI.backupDraft()')==pivots
    assert page.evaluate('__lgNav.length')==6,page.evaluate('__lgNav')
    invariant(page,before);row['localRefusalDialogs']=dialogs;row['canonicalDraftNavigationAccepted']=True
    row['acceptedPublications']=page.evaluate('__lgNav')
    page.evaluate('__lgUnsub()')

# The original106 classic-script path identities and order in base0037bd3.
# A single planned download loader may precede its tools-services consumer.
ORIGINAL_SCRIPT_PATHS_SHA256 = '40a619eac3b449f7e0704d8aa2be46f38280902d0340f961e898057d22b36c82'
DOWNLOAD_LOADER = 'src/js/00-core/10-download-assets.js'
DOWNLOAD_CONSUMER = 'src/js/20-ui/31-tools-services.js'
TIME_TWINS_MODULES = [f'src/js/40-app/29-time-twins/{name}.js' for name in
    ('01-simulation','02-missions','03-progress','04-view','05-controller')]

CAPITAL_CURRENTS_MODULES = [f'src/js/40-app/30-capital-currents/{name}.js' for name in
    ('01-engine','02-scenarios','03-progress','04-field-renderer','04-view','05-controller')]

MARKET_HOURS_MODULES = [f'src/js/40-app/31-market-hours/{name}.js' for name in
    ('01-sessions','02-assets','03-view','04-controller')]

def assert_startup_scripts(root,scripts,expected):
    assert scripts==expected,{'scripts':scripts,'manifest':expected}
    planning_present=any(path in expected for path in PLANNING_MODULES)
    if planning_present:
        assert expected[-3:]==PLANNING_MODULES and all(expected.count(path)==1 for path in PLANNING_MODULES),'Planning must be one ordered block after the guide'
        assert not any(path in expected for path in RETIRED_PLANNING_MODULES),'Retired planning scripts must not be loaded'
        expected=expected[:-3]
    assert expected[-4:]==MODULES,'The four guide scripts must preserve their order'
    if any(path in expected for path in MARKET_HOURS_MODULES):
        assert all(expected.count(path)==1 for path in MARKET_HOURS_MODULES),expected
        assert DOWNLOAD_LOADER in expected,'Market hours must follow the download loader'
        market_start=expected.index(DOWNLOAD_LOADER)+1
        assert expected[market_start:market_start+4]==MARKET_HOURS_MODULES,'Market hours must form one ordered block immediately after the download loader'
        # Validate the approved block before applying the unchanged legacy oracles.
        expected=expected[:market_start]+expected[market_start+4:]
    twins_present=any(path in expected for path in TIME_TWINS_MODULES)
    capital_present=any(path in expected for path in CAPITAL_CURRENTS_MODULES)
    if capital_present:
        assert twins_present, 'The third game must preserve Time Twins'
        assert all(expected.count(path)==1 for path in CAPITAL_CURRENTS_MODULES),expected
        capital_start=expected.index(CAPITAL_CURRENTS_MODULES[0])
        assert expected[capital_start:capital_start+6]==CAPITAL_CURRENTS_MODULES,expected
        assert capital_start+6==expected.index(DOWNLOAD_LOADER),'Capital Currents must immediately precede the download loader'
    if twins_present:
        assert all(expected.count(path)==1 for path in TIME_TWINS_MODULES),expected
        start=expected.index(TIME_TWINS_MODULES[0])
        assert expected[start:start+5]==TIME_TWINS_MODULES,expected
        assert start+5==expected.index(CAPITAL_CURRENTS_MODULES[0] if capital_present else DOWNLOAD_LOADER),'Time Twins must precede the next isolated game or the download loader'
    original=[path for path in expected if path!=DOWNLOAD_LOADER and path not in TIME_TWINS_MODULES and path not in CAPITAL_CURRENTS_MODULES]
    if planning_present:
        # Only the five explicitly retired identities are replaced. Reconstruct
        # their original slot for the unchanged106-path hash: every other legacy
        # identity and relative position remains protected by the same oracle.
        assert len(original)==101,original
        old_slot=original.index('src/js/10-domain/08-usd-brl-quote.js')+1
        original=original[:old_slot]+RETIRED_PLANNING_MODULES+original[old_slot:]
    assert len(original)==106 and hashlib.sha256('\n'.join(original).encode()).hexdigest()==ORIGINAL_SCRIPT_PATHS_SHA256,{'original':original}
    if DOWNLOAD_LOADER in expected:
        assert len(expected)==(118 if capital_present else 112 if twins_present else 107)-(5 if planning_present else 0) and expected.count(DOWNLOAD_LOADER)==1 and expected.count(DOWNLOAD_CONSUMER)==1,expected
        assert (Path(root)/DOWNLOAD_LOADER).is_file(),'Declared download loader source is missing'
        assert expected.index(DOWNLOAD_LOADER)+1==expected.index(DOWNLOAD_CONSUMER),'Download loader must immediately precede tools-services'
    else:
        assert not twins_present and len(expected)==106-(5 if planning_present else 0),expected

def startup_surface(page,row):
    assert page.evaluate("!!(JPWLearningGuide&&JPWLearningProgress&&JPWLearningCatalog&&JPWLearningView)")
    start(page,'basics');click(page,'#jpwLearningUnderstand');seen(page,'basics-home')
    assert len(page.evaluate('JPWLearningCatalog.tracks'))==7
    assert page.evaluate('JPWLearningCatalog.version')==1
    if page.locator('#minigamesTimeTwinsCard').count():
        entry=page.evaluate("JPWLearningCatalog.tracks.flatMap(t=>t.steps).find(s=>s.id==='general-settings-probability-lab')")
        assert 'Gêmeos do Tempo' in entry['instruction'] and 'Galton Board' in entry['instruction']
        assert ('três cartões' if page.locator('#minigamesCapitalCurrentsCard').count() else 'dois cartões') in entry['expected']
        if page.locator('#minigamesCapitalCurrentsCard').count():
            assert 'Correntes de Capital' in entry['instruction'] and 'Correntes de Capital' in entry['expected']
    if not row['config'].get('surface'):
        scripts=page.evaluate('[...document.scripts].map(x=>x.getAttribute("src")).filter(x=>x&&x!=="build-id.js")')
        expected=[item['path'] for item in json.loads((Path(row['root'])/'src/js/manifest.json').read_text())['files']]
        assert_startup_scripts(row['root'],scripts,expected)
        row['classicScriptCount']=len(scripts);row['sourceJSCount']=sum(x.startswith('src/js/') for x in scripts)
    row['startupFacade']=True

def offline(page,row):
    page.wait_for_function('navigator.serviceWorker.controller!==null',timeout=20000)
    paths=page.evaluate("""async()=>{const names=await caches.keys(),all=[];
      for(const n of names){const c=await caches.open(n);all.push(...(await c.keys()).map(r=>new URL(r.url).pathname));}return all;}""")
    assert all('/'+asset in paths for asset in MODULES),paths
    if page.evaluate('!!window.JPWPlanning'):
        assert all('/'+asset in paths for asset in PLANNING_MODULES),'The independent Planning scripts must also be precached'
    page.context.set_offline(True);page.reload();page.wait_for_function('window.JPWLearningGuide && window.JPWLearningCatalog')
    startup_surface(page,row);row['actualPrecachedGuideModules']=MODULES

def viewport_events(page,row,kind):
    start(page,'general' if kind=='nested-scroll' else 'basics');instrument(page);before=financial(page)
    if kind=='nested-scroll':
        page.set_viewport_size({'width':1440,'height':600})
        reach(page,'general','general-settings-parameters')
        coach=page.locator('#jpwLearningCoach');target=page.locator('[data-settings-panel="parameters"]')
        row['scrollFixture']=page.locator('#settingsContent').evaluate('e=>({clientHeight:e.clientHeight,scrollHeight:e.scrollHeight})')
        assert row['scrollFixture']['scrollHeight']>row['scrollFixture']['clientHeight'],'HARNESS_SCROLL: original Parameters page has no overflow'
        before_y=target.bounding_box()['y'];page.locator('#settingsContent').evaluate('e=>e.scrollTop=100')
        settle(page);after_y=target.bounding_box()['y']
        assert after_y!=before_y,'HARNESS_SCROLL: nested scroll fixture did not establish overflow'
        box=coach.bounding_box();assert box and box['x']>=0 and box['y']>=0,box
        row['nestedScrollTargetY']=[before_y,after_y]
    else:
        cdp=page.context.new_cdp_session(page)
        if kind=='visualViewport-shrink':
            cdp.send('Emulation.setPageScaleFactor',{'pageScaleFactor':1.4})
            settle(page);assert page.evaluate('visualViewport.width<innerWidth')
            row['pageScale']=page.evaluate('visualViewport.scale')
        else:
            page.set_viewport_size({'width':720,'height':600});settle(page)
            row['reflowViewport']={'width':720,'height':600}
        box=page.locator('#jpwLearningCoach').bounding_box();v=page.evaluate('({width:visualViewport.width,height:visualViewport.height,x:visualViewport.offsetLeft,y:visualViewport.offsetTop})')
        assert box['x']>=v['x']-1 and box['y']>=v['y']-1 and box['x']+box['width']<=v['x']+v['width']+1 and box['y']+box['height']<=v['y']+v['height']+1,(box,v)
    invariant(page,before)

def contextual_help(page,row):
    reach(page,'research','research-stocks-br')
    assert snap(page)['stepId']=='research-stocks-br'
    instrument(page);before=financial(page)
    target=page.locator('#researchStocksBr .note-i').filter(visible=True).first
    target.wait_for(state='visible')
    target.focus();page.keyboard.press('Enter');settle(page)
    assert target.get_attribute('aria-expanded')=='true'
    target.focus();page.keyboard.press('Enter');settle(page)
    assert target.get_attribute('aria-expanded')=='false'
    assert record(page,'research-stocks-br') is None,'Unrelated help must not manufacture lesson acknowledgment'
    invariant(page,before);row['nativeHelpOpenedAndClosed']=True

def metadata_guide_keyboard(page,row):
    reach(page,'general','general-notes-save');click(page,'#jpwLearningPracticeStart')
    keyboard_click(page,'#mvpNotesNewBtn');page.locator('#mvpNotesNewBox').wait_for(state='visible')
    assert page.locator('#mvpNotesNewBox #jpwLearningCoach').is_visible()
    before=financial(page);draft=page.evaluate('mvpNotesUI.draft?structuredClone(mvpNotesUI.draft):null')
    page.locator('#mvpNotesNewBox #jpwLearningPause').focus();page.keyboard.press('Enter');settle(page)
    row['afterKeyboard']=page.evaluate("({metadataOpen:mvpNotesUI.newNoteOpen,stage:mvpNotesUI.stage,focus:document.activeElement?.id,draft:mvpNotesUI.draft?structuredClone(mvpNotesUI.draft):null})")
    assert row['afterKeyboard']['metadataOpen'],'Guide Pause Enter bubbled to the original metadata Confirm handler'
    assert row['afterKeyboard']['draft']==draft and snap(page)['paused']
    invariant(page,before)

def native_metadata_geometry(page,row):
    """Original form usability with an active, real guide in its native host."""
    reach(page,'general','general-notes-save');visible_practice_instruction(page,row)
    click(page,'#jpwLearningPracticeStart')
    keyboard_click(page,'#mvpNotesNewBtn');page.locator('#mvpNotesNewBox').wait_for(state='visible')
    page.locator('#mvpNotesNewBox #jpwLearningCoach').wait_for(state='visible')
    instrument(page);before=financial(page)
    native_ids=['mvpNotesNewType','mvpNotesNewPriority','mvpNotesNewStatus','mvpNotesNewFolder',
      'mvpNotesNewPolicy','mvpNotesNewConfirmBtn','mvpNotesNewCancelBtn']
    original=page.evaluate("({draft:mvpNotesUI.draft?structuredClone(mvpNotesUI.draft):null,options:[mvpNotesNewType.value,mvpNotesNewPriority.value,mvpNotesNewStatus.value,mvpNotesNewFolder.value,mvpNotesNewPolicy.value]})")
    row['nativeControls']={}
    for target in native_ids:
        row['nativeControls'][target]=pointer_uncovered(page,'#'+target)

    # Keyboard must visit all seven original controls and every currently
    # visible enabled guide control through the original host's own Tab trap.
    required_guide=page.locator('#jpwLearningCoach button:enabled').filter(visible=True).evaluate_all('(items)=>items.filter(x=>!x.hidden).map(x=>x.id)')
    assert {'jpwLearningUnderstand','jpwLearningBack','jpwLearningSkip','jpwLearningPause'}<=set(required_guide),required_guide
    if page.locator('#jpwLearningDetailsSummary').is_visible():required_guide.append('jpwLearningDetailsSummary')
    required=set(native_ids+required_guide);visited=set();row['trustedTabFocus']=[]
    # Start from the original first select; opening New already selected it.
    # Pointer geometry checks above do not focus or activate any control.
    for _ in range(2*(len(required)+3)):
        page.keyboard.press('Tab');settle(page)
        state=page.evaluate("({id:document.activeElement?.id,owned:!!document.activeElement?.closest('#mvpNotesNewBox')})")
        assert state['owned'],'Native Tab left the actual metadata/guide focus host'
        visited.add(state['id']);row['trustedTabFocus'].append(state['id'])
        samples=page.evaluate("""async()=>{const take=()=>{const e=document.getElementById('mvpNotesNewCancelBtn'),r=e.getBoundingClientRect();return {x:r.x,y:r.y,width:r.width,height:r.height};};
          const rows=[];for(let n=0;n<12;n++){await new Promise(requestAnimationFrame);rows.push(take());}return rows;}""")
        for axis in ['x','y','width','height']:
            delta=max(s[axis] for s in samples)-min(s[axis] for s in samples)
            assert delta<=0.5,{'failure':'Native Cancel moves after trusted Tab','axis':axis,'delta':delta,'samples':samples,'focus':state}
        row.setdefault('stableFrameRanges',[]).append({axis:max(s[axis] for s in samples)-min(s[axis] for s in samples) for axis in ['x','y','width','height']})
        if required<=visited:break
    assert required<=visited,{'missing':sorted(required-visited),'visited':sorted(visited)}
    page.keyboard.press('Shift+Tab');settle(page)
    assert page.evaluate("!!document.activeElement?.closest('#mvpNotesNewBox')")

    # The adaptive presentation keeps full local instructional copy available.
    # Expand/collapse the real native disclosure using Enter; no teacher DOM is
    # created or bypassed by the harness, and original metadata stays untouched.
    disclosure=page.locator('#jpwLearningDetails')
    if disclosure.count():
        assert not disclosure.evaluate('e=>e.open'),'Constrained guide must initially leave the native form usable'
        summary=page.locator('#jpwLearningDetailsSummary');pointer_uncovered(page,'#jpwLearningDetailsSummary')
        summary.focus();page.keyboard.press('Enter');settle(page)
        assert disclosure.evaluate('e=>e.open') and page.evaluate('mvpNotesUI.newNoteOpen')
        body=page.locator('#jpwLearningBody');body.wait_for(state='visible')
        instruction=page.evaluate("JPWLearningCatalog.tracks.find(t=>t.id==='general').steps.find(s=>s.id==='general-notes-save').instruction")
        assert body.inner_text()==instruction
        assert page.locator('#jpwLearningExpected').is_visible()
        summary.focus();page.keyboard.press('Enter');settle(page)
        assert not disclosure.evaluate('e=>e.open') and page.evaluate('mvpNotesUI.newNoteOpen')
        row['instructionDisclosure']={'initiallyCollapsed':True,'nativeEnterExpandedAndCollapsed':True,'fullCatalogCopy':True}
    else:
        assert page.locator('#jpwLearningBody').is_visible(),'Full guide instruction is inaccessible'
        row['instructionDisclosure']={'fullCopyVisibleWithoutDisclosure':True}
    assert page.evaluate("({draft:mvpNotesUI.draft?structuredClone(mvpNotesUI.draft):null,options:[mvpNotesNewType.value,mvpNotesNewPriority.value,mvpNotesNewStatus.value,mvpNotesNewFolder.value,mvpNotesNewPolicy.value]})")==original
    assert record(page,'general-notes-save') is None and page.evaluate('S.mvpNotes.items.length')==0
    row['cancelAfterKeyboard']=pointer_uncovered(page,'#mvpNotesNewCancelBtn')
    click(page,'#mvpNotesNewCancelBtn')
    assert not page.locator('#mvpNotesNewBox').is_visible() and page.locator('#mvpNotesOverlay').is_visible()
    assert page.evaluate("document.activeElement===document.getElementById('mvpNotesNewBtn')")
    assert record(page,'general-notes-save') is None
    invariant(page,before);row['mainWrites']=0;row['nativeFormPreserved']=True

def prepare(context,url,row,welcome_case=False):
    install_bootstrap(context)
    if not welcome_case:context.add_init_script('window.__onbShown=true;')
    page=context.new_page();page.set_default_timeout(7000)
    errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
    row['pageErrors']=errors
    if '/dist/' in url:
        page.route('**/dist/assets/**',lambda route:route.continue_(url=route.request.url.replace('/dist/assets/','/assets/')))
    page.goto(url,wait_until='load');wait_bootstrap(page);settle(page);row['knownBoot']=True
    row['build']=page.evaluate("typeof JP_WEALTH_BUILD_ID!=='undefined'?JP_WEALTH_BUILD_ID:null")
    if not welcome_case:
        page.wait_for_function('window.JPWLearningGuide && window.JPWLearningCatalog')
        # Establish the native document/receipt and causal epoch before the
        # behavioral checkpoint, then let native reload normalization settle.
        page.evaluate("""() => {S.onboarding.done=true;S.mvpNotes.showHeaderIcon=true;
          if(save()!==true)throw Error('HARNESS_SETUP: native checkpoint refused');
          sessionEpochCurrent();markSessionCheckpoint();}""")
        page.reload();wait_bootstrap(page);settle(page)
    return page

def case_list():
    cases=[('welcome-permanent-entry',welcome,{}),('readonly-all-57-native-actions',readonly,{'active_alladin':True,'active_pf':True}),
      ('progress-skip-pause-reload-resume-restart',progress_lifecycle,{}),('invalid-version-raw-preserved',invalid_progress,{}),
      ('guide-storage-read-refused',lambda p,r:guide_storage(p,r,'read-refused'),{}),
      ('guide-storage-write-refused',lambda p,r:guide_storage(p,r,'refused'),{}),
      ('cross-tabs-conflict-before-receipt',cross_tab,{'active_pf':True}),('cleanup-dispose-clear-stale-boot',cleanup,{})]
    cases += [(kind,lambda p,r,k=kind:suspension(p,r,k),{'active_pf':True} if kind in {'off-route','foreign-dialog'} else {}) for kind in ['frozen-alladin','frozen-personal-finance','missing-anchor','off-route','foreign-dialog']]
    cases += [(f'layout/{layout}/{width}/{theme}',geometry,{'layout':layout,'width':width,'theme':theme})
      for layout in ['sidebar','topbar','glass','submenu'] for width,theme in [(1440,'dark'),(390,'light')]]
    cases += [(f'native-pf/{kind}',lambda p,r,k=kind:pf_practice(p,r,k),{'active_pf':True})
      for kind in ['confirmed','refused','unknown','escape']]
    cases += [(f'native-notes/{kind}',lambda p,r,k=kind:notes_practice(p,r,k),{})
      for kind in ['confirmed','refused','unknown','dirty-refusal']]
    cases += [(f'native-notes-metadata-cancel/{kind}',lambda p,r,k=kind:notes_cancel(p,r,k),{})
      for kind in ['button','escape','backdrop']]
    cases += [('native-contextual-help',contextual_help,{}),('native-pending-account-guard',account_guard,{}),
      ('native-research-draft-preservation-local-refusal',research_drafts,{}),('actual-backup-excludes-guide',backup,{}),
      ('actual-backup-import-pauses-invalidates-practice',import_revalidation,{'active_pf':True}),
      ('startup-source-manifest',startup_surface,{}),('startup-portable-http',startup_surface,{'surface':'portable-http'}),
      ('startup-portable-file',startup_surface,{'surface':'portable-file'}),('offline-sw-four-guide-modules',offline,{'service_workers':'allow'})]
    cases += [(kind,lambda p,r,k=kind:viewport_events(p,r,k),{})
      for kind in ['nested-scroll','reflow-200-equivalent','visualViewport-shrink']]
    cases += [('native-browser-zoom-200',geometry,{'nativeZoom':True,'theme':'dark'}),
      ('guide-controls-in-metadata-own-enter',metadata_guide_keyboard,{})]
    cases += [(f'native-metadata-geometry/{width}x{height}',native_metadata_geometry,{'width':width,'height':height})
      for width,height in [(1440,900),(390,844),(320,640)]]
    cases += [(f'readonly-all-57-native-actions/mobile-{width}x{height}',readonly,
      {'width':width,'height':height,'active_alladin':True,'active_pf':True}) for width,height in [(390,844),(320,700)]]
    cases += [('native-pf/confirmed/mobile-390x844',lambda p,r:pf_practice(p,r,'confirmed'),{'width':390,'height':844,'active_pf':True})]
    return cases

def main():
    global BASELINE_ROOT
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root',type=Path,default=ROOT);parser.add_argument('--out',type=Path,required=True)
    parser.add_argument('--case',default='',help='Substring filter; no selected cases is an error')
    parser.add_argument('--browser',choices=['system'],default='system')
    parser.add_argument('--baseline-root',type=Path,help='Frozen original app for native backdrop focus comparison')
    args=parser.parse_args();root=args.root.resolve();out=args.out.resolve();out.parent.mkdir(parents=True,exist_ok=True)
    BASELINE_ROOT=(args.baseline_root or root.parent/'source-baseline').resolve()
    started=time.monotonic();report={'root':str(root),'startedUTC':datetime.now(timezone.utc).isoformat(),
      'inputs_before':hashes(root),'test_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
      'cases':[],'registeredCaseCount':len(case_list()),'baselineFocusRoot':str(BASELINE_ROOT),'limits':['Disposable synthetic contexts only; no operator profile or production account.',
       'Headless viewport/reflow and CDP page scale are measured separately from native browser zoom.',
       'Physical touch, screen reader and real mobile keyboard NOT_RUN.']}
    server=None
    try:
        cases=[x for x in case_list() if args.case in x[0]]
        if not cases:raise ValueError('No cases match --case '+repr(args.case))
        server=BrowserFixtureServer(('127.0.0.1',0),partial(Quiet,directory=str(root)))
        threading.Thread(target=server.serve_forever,daemon=True).start()
        prefix=f'http://127.0.0.1:{server.server_port}/'
        with sync_playwright() as pw:
            options=launch_options();report['runtime']={'launch':options,'python':os.sys.executable}
            browser=pw.chromium.launch(**options);report['runtime']['browserVersion']=browser.version
            for name,fn,config in cases:
                row={'name':name,'result':'NOT_RUN','config':config,'root':str(root)};context=None;page=None;profile=None
                try:
                    if config.get('nativeZoom'):
                        profile=Path(tempfile.mkdtemp(prefix='learning-native-zoom-',dir=out.parent))
                        (profile/'Default').mkdir()
                        (profile/'Default/Preferences').write_text(json.dumps({'partition':{'default_zoom_level':{'x':math.log(2)/math.log(1.2)}}}))
                        native=dict(options);native.update(headless=False,no_viewport=True,args=['--window-size=1440,1000'],service_workers='block',reduced_motion='reduce',accept_downloads=True)
                        context=pw.chromium.launch_persistent_context(str(profile),**native)
                    else:
                        context=browser.new_context(viewport={'width':config.get('width',1440),'height':config.get('height',1000)},
                            service_workers=config.get('service_workers','block'),reduced_motion='reduce',accept_downloads=True)
                    context.add_init_script('localStorage.setItem("jpw_nav_layout",'+json.dumps(config.get('layout','sidebar'))+');')
                    surface=config.get('surface');url=(root/PORTABLE).as_uri() if surface=='portable-file' else prefix+(PORTABLE if surface=='portable-http' else 'index.html')
                    page=prepare(context,url,row,name=='welcome-permanent-entry')
                    # Ativação nominal única, preservando outros overrides e futuros reloads/imports.
                    for module, enabled in [('alladin',config.get('active_alladin')),('personal-finance',config.get('active_pf'))]:
                        if enabled:
                            assert page.evaluate("id=>JPWModuleAvailability.setState(id,'active').ok",module), module
                    if config.get('nativeZoom'):
                        row['nativeZoomMeasurement']=page.evaluate('({ratio:outerWidth/innerWidth,cssZoom:getComputedStyle(document.documentElement).zoom})')
                        assert page.evaluate('Math.abs(outerWidth/innerWidth-2)<0.02 && getComputedStyle(document.documentElement).zoom==="1"'), 'HARNESS_NATIVE_ZOOM: Chromium native 200% was not established'
                    if config.get('theme'):
                        page.evaluate('(theme)=>{S.theme=theme;applyTheme();renderThemeSeg();}',config['theme'])
                    fn(page,row);assert_fixture_requests(context);assert not row['pageErrors'],row['pageErrors']
                    row['result']='PASS'
                except Exception as error:
                    product=(isinstance(error,AssertionError) or isinstance(error,PlaywrightTimeout) and row.get('knownBoot')) and not str(error).startswith('HARNESS_')
                    row.update(result='PRODUCT_FAIL' if product else 'TEST_HARNESS_FAIL',detail=str(error),traceback=traceback.format_exc())
                    if page:
                        try:row['lastSnapshot']=page.evaluate('window.JPWLearningGuide?.snapshot()||null')
                        except Exception:pass
                        try:page.screenshot(path=str(out.parent/(out.stem+'-'+name.replace('/','-')+'.png')),full_page=True)
                        except Exception:pass
                finally:
                    report['cases'].append(row);print(json.dumps(row,ensure_ascii=False),flush=True)
                    if context:context.close()
                    if profile:shutil.rmtree(profile)
            browser.close()
    except Exception as error:
        report['harnessError']={'detail':str(error),'traceback':traceback.format_exc()}
    finally:
        if server:server.shutdown();server.server_close()
        report['inputs_after']=hashes(root);report['source_unchanged']=report['inputs_before']==report['inputs_after']
        report['durationSeconds']=time.monotonic()-started
        report['counts']={status:sum(c['result']==status for c in report['cases']) for status in ['PASS','PRODUCT_FAIL','TEST_HARNESS_FAIL','NOT_RUN']}
        out.write_text(json.dumps(report,ensure_ascii=False,indent=2))
    return 0 if report['cases'] and report['source_unchanged'] and not report.get('harnessError') and all(c['result']=='PASS' for c in report['cases']) else 1

if __name__=='__main__':raise SystemExit(main())
