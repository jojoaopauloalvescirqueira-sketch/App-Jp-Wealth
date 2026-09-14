#!/usr/bin/env python3
"""Backup reliability: fixed synthetic oracles for baseline and candidate.

Uses storage_governance_test.prepare_page and its nominal economic bootstrap.
Folder writes are File System Access mocks, never claims of a physical file.
No schema field is invented for new descriptive export metadata.
"""
import argparse
from datetime import datetime, timezone
from functools import partial
import hashlib
from http.server import ThreadingHTTPServer
import importlib.util
import json
import os
from pathlib import Path
import sys
import threading
import traceback

from playwright.sync_api import sync_playwright

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
SOURCES = ('index.html', 'build-id.js', 'src/styles/app.css', 'src/js/manifest.json',
    'src/js/00-core/03-default-state.js', 'src/js/00-core/04-persistence.js',
    'src/js/00-core/06-storage-fs.js', 'src/js/30-accounting/01-daily-ledger.js',
    'src/js/40-app/07-finalize-session.js', 'src/js/40-app/09-settings-modal.js',
    'src/js/40-app/12-global-dashboard.js', 'src/js/40-app/16-storage-governance.js',
    'tools/storage_governance_test.py', 'tools/browser_bootstrap_fixture.py',
    'tools/design_experience_test.py', 'tools/studies_notes_persistence_contract_test.py',
    'tools/fixtures/personal_finance_v1.json')
DOMAINS = ('params', 'ledger', 'personalFinance', 'alladin', 'nocoda', 'pivotStudies',
           'mvpNotes', 'fxPlanning', 'operationHistory', 'activeOperation')
AUX = {'jpwealth_local_profile_v1': '{"schemaVersion":1,"displayName":"BR-AUX-PROFILE","avatarDataUrl":null}',
       'jpwealth_notes_launcher_position_v1': '{"schemaVersion":1,"x":0.2,"y":0.6}',
       'jpwealth_galton_preferences_v1': '{"schemaVersion":1,"preset":"realistic"}',
       'jpwealth.ui.widgetLayouts.v6': '{"BR-AUX-WIDGET":true}',
       'jpwealth.ui.ffNews.sourceUrl': 'https://raw.githubusercontent.com/jojoaopauloalvescirqueira-sketch/jp-wealth-news-feed/main/ff-high-impact.json'}


def digest(value):
    raw = value if isinstance(value, str) else json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'))
    return hashlib.sha256(raw.encode()).hexdigest()


def load(root, name):
    spec = importlib.util.spec_from_file_location(name, root / 'tools' / (name + '.py'))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def identity(root):
    return {name: hashlib.sha256((root / name).read_bytes()).hexdigest() for name in SOURCES}


PREPARE = r"""() => {
  closeModal();window.__onbShown=true;
  const nativeGet=Storage.prototype.getItem,nativeSet=Storage.prototype.setItem;
  window.__br={nativeGet,nativeSet,alerts:[],confirmQuestions:[],accept:true,
    writes:[],mode:'normal',confirmFinished:false,confirmResult:null};
  window.alert=message=>__br.alerts.push(String(message));
  window.confirm=message=>{__br.confirmQuestions.push(String(message));return __br.accept;};
  S.onboarding.done=true;
  S.dataGovernance.backup.lastConfirmedAt='';
  S.dataGovernance.backup.lastConfirmedExportSequence=0;
  S.dataGovernance.changeLog=[{id:'br-original',ts:new Date(Date.now()-86400000).toISOString(),
    entity:'config',action:'updated',recordId:'',label:'Synthetic existing change'}];
  if(save()!==true)throw Error('Synthetic checkpoint was refused');
  if(!sessionEpochCurrent())throw Error('Synthetic epoch bootstrap failed');
  const confirmBackup=dgConfirmBackup;
  dgConfirmBackup=function(...args){
    try{
      const result=confirmBackup.apply(this,args);
      if(result && typeof result.then==='function')return result.then(value=>{
        __br.confirmResult=value??null;__br.confirmFinished=true;return value;
      },error=>{__br.confirmFinished=true;throw error;});
      __br.confirmResult=result??null;__br.confirmFinished=true;return result;
    }catch(error){__br.confirmFinished=true;throw error;}
  };
  Storage.prototype.setItem=function(key,value){
    if(this===localStorage && key===LSKEY){
      __br.writes.push({key,value:String(value)});
      if(__br.mode==='quota')throw new DOMException('synthetic quota','QuotaExceededError');
      if(__br.mode==='noop')return;
      const result=nativeSet.call(this,key,value);
      if(__br.mode==='readback')__br.readFault=true;
      if(__br.mode==='divergent')nativeSet.call(this,key,__br.otherRaw);
      return result;
    }
    return nativeSet.call(this,key,value);
  };
  Storage.prototype.getItem=function(key){
    if(this===localStorage && key===LSKEY && __br.readFault)
      throw new DOMException('synthetic readback denied','SecurityError');
    return nativeGet.call(this,key);
  };
  window.__dgBannerDismissed=false;
  renderSystemStatus();renderDgBackupBanner();
}"""

FACTS = r"""() => {
  const node=id=>{const el=document.getElementById(id);return el?{
    exists:true,text:el.textContent,state:el.dataset.state||'',visible:!!el.getClientRects().length}: {exists:false};};
  return {state:JSON.stringify(S),raw:__br.nativeGet.call(localStorage,LSKEY),
    governance:structuredClone(S.dataGovernance),due:dgBackupDue(),age:dgBackupAgeDays(),
    unknown:jpWealthPersistenceOutcomeIsUnknown(),blocked:jpWealthPersistenceIsBlocked(),
    recovery:jpWealthLoadRecoveryActive(),recoveryContext:{active:jpWealthLoadRecovery.active,
      kind:jpWealthLoadRecovery.kind,raw:jpWealthLoadRecovery.raw,recoveryKey:jpWealthLoadRecovery.recoveryKey,
      lastError:String(jpWealthLoadRecovery.lastError||'')},recoveryWarning:node('persistenceRecovery'),
    failure:{active:jpWealthPersistenceFailure.active,
      kind:jpWealthPersistenceFailure.kind,lastError:String(jpWealthPersistenceFailure.lastError||'')},epoch:jpWealthPersistenceEpoch(),
    persist:node('jpwSsPersist'),backup:node('jpwSsBackup'),banner:node('dgBackupBanner'),
    savedTag:document.getElementById('savedTag')?.classList.contains('show')||false,
    alerts:__br.alerts.slice(),writes:__br.writes.length,confirmation:__br.confirmResult,
    aux:Object.fromEntries(Object.keys(localStorage).filter(key=>key!==LSKEY).sort()
      .map(key=>[key,__br.nativeGet.call(localStorage,key)]))};
}"""


def brief(facts):
    return {**{key: value for key, value in facts.items() if key not in ('state', 'raw', 'aux')},
            'state_sha256': digest(facts['state']), 'raw_sha256': digest(facts['raw']),
            'aux_sha256': digest(facts['aux'])}


class Case:
    def __init__(self, name):
        self.name, self.checks, self.observed = name, [], {}

    def check(self, name, passed, detail=None):
        self.checks.append({'name': name, 'result': 'PASS' if passed else 'PRODUCT_FAIL', 'detail': detail})

    def require(self, name, passed, detail=None):
        self.check(name, passed, detail)
        if not passed:
            raise AssertionError(name)


def settle(page):
    page.evaluate('() => new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve)))')


def refresh(page):
    page.evaluate('() => {renderSystemStatus();renderDgBackupBanner();}')
    settle(page)


def prepare(helper, browser, url):
    page = helper.prepare_page(browser, url)
    page.clock.set_fixed_time(datetime(2026, 9, 14, 15, 0, tzinfo=timezone.utc))
    page.evaluate(PREPARE)
    return page


def confirmation(case, page, mode):
    before = page.evaluate(FACTS)
    case.require('existing due banner and confirmation control', before['due'] and before['banner']['exists']
                 and page.locator('#dgBannerHave').count() == 1, brief(before))
    page.evaluate(r"""mode => {
      __br.mode=mode;
      if(mode==='refused')blockJPWealthPersistence();
      if(mode==='unknown')markJPWealthPersistenceOutcomeUnknown('synthetic existing unknown');
      if(mode==='divergent'){
        const other=JSON.parse(__br.nativeGet.call(localStorage,LSKEY));
        other.syntheticOtherWriter='BR-DIVERGENT';__br.otherRaw=JSON.stringify(other);
      }
    }""", mode)
    page.locator('#dgBannerHave').click()
    page.wait_for_function('__br.confirmFinished')
    refresh(page)
    after = page.evaluate(FACTS)
    case.observed.update(before=brief(before), after=brief(after))
    if mode == 'normal':
        disk = json.loads(after['raw'])
        case.check('confirmed date and sequence persisted', bool(disk['dataGovernance']['backup']['lastConfirmedAt'])
                   and disk['dataGovernance']['backup']['lastConfirmedExportSequence'] == disk['dataGovernance']['export']['lastSequence'])
        case.check('confirmation log persisted exactly once', sum(e['entity'] == 'backup' and e['action'] == 'confirmed'
                   for e in disk['dataGovernance']['changeLog']) == 1)
        case.check('RAM governance equals disk', after['governance'] == disk['dataGovernance'])
        case.check('only confirmed backup clears due reminder', not after['due'] and not after['banner']['exists'])
        return
    if mode in ('readback', 'divergent'):
        case.check('indeterminate readback blocks as UNKNOWN', after['unknown'], brief(after))
        case.check('indeterminate outcome has no confirmation success', after['confirmation'] is not True
                   and after['persist']['exists'] and after['persist']['state'] != 'ok'
                   and not after['savedTag'], brief(after))
        checkpoint = after
        page.evaluate("() => {__br.mode='normal';__br.readFault=false;}")
        attempt = page.evaluate('save()')
        after_retry = page.evaluate(FACTS)
        case.check('UNKNOWN prevents blind save and further writes', attempt is False
                   and after_retry['writes'] == checkpoint['writes'] and after_retry['raw'] == checkpoint['raw'])
        return
    case.check('refusal preserves original confirmation and log', after['governance'] == before['governance'])
    case.check('refusal preserves persisted document', after['raw'] == before['raw'])
    case.check('refusal keeps due reminder visible', after['due'] and after['banner']['exists'])
    if mode == 'unknown':
        case.check('preexisting UNKNOWN attempts no write', after['writes'] == before['writes'])
        case.check('UNKNOWN status is present and never saved', after['persist']['exists']
                   and after['persist']['state'] != 'ok' and 'dados salvos' not in after['persist'].get('text', '').lower())
        return
    page.evaluate("() => {__br.mode='normal';__br.readFault=false;resumeJPWealthPersistence();S.theme=S.theme==='dark'?'light':'dark';}")
    later_result = page.evaluate('save()')
    later = page.evaluate(FACTS)
    case.require('unrelated later save actually succeeds', later_result is True and later['raw'] == later['state'])
    disk = json.loads(later['raw'])
    case.check('later save cannot resurrect refused confirmation', disk['dataGovernance'] == before['governance'])
    case.observed['later'] = brief(later)
    page.reload(wait_until='load')
    page.wait_for_function("typeof S==='object' && !!S.dataGovernance")
    case.check('reload cannot resurrect refused confirmation', page.evaluate('S.dataGovernance.backup') == before['governance']['backup'])
    if mode == 'refused' and page.evaluate('S.dataGovernance.backup') == before['governance']['backup']:
        page.evaluate("() => {closeModal();window.confirm=()=>true;renderDgBackupBanner();}")
        case.require('explicit retry control exists after valid reload', page.locator('#dgBannerHave').count() == 1)
        page.locator('#dgBannerHave').click()
        page.wait_for_function("S.dataGovernance.backup.lastConfirmedAt && JSON.parse(localStorage.getItem(LSKEY)).dataGovernance.backup.lastConfirmedAt===S.dataGovernance.backup.lastConfirmedAt")
        case.check('fresh explicit gesture can confirm after refusal and reload', not page.evaluate('dgBackupDue()'))


def freshness(case, page):
    observed = []
    for age in (29, 30, 31):
        page.evaluate('age=>{S.dataGovernance.backup.lastConfirmedAt=new Date(Date.now()-age*86400000).toISOString();}', age)
        before = page.evaluate(FACTS)
        refresh(page)
        after = page.evaluate(FACTS)
        case.require(f'{age}d status row exists', after['backup']['exists'])
        case.check(f'{age}d canonical due boundary', after['due'] == (age >= 30))
        case.check(f'{age}d dashboard agrees with canonical due', (after['backup']['state'] != 'ok') == after['due'], after['backup'])
        case.check(f'{age}d reminder agrees with canonical due', after['banner']['exists'] == after['due'])
        case.check(f'{age}d render preserves historical date and storage', before['state'] == after['state'] and before['raw'] == after['raw'])
        observed.append(brief(after))
    case.observed['ages'] = observed
    # Opening Settings must refresh its projection without a test calling its renderer.
    page.evaluate("() => {S.dataGovernance.backup.lastConfirmedAt=new Date(Date.now()-29*86400000).toISOString();}")
    raw = page.evaluate('localStorage.getItem(LSKEY)')
    page.locator('#headerConfigBtn').click()
    page.evaluate("settingsNavigateToLeaf('backup')")
    page.wait_for_function("document.querySelector('#dgBackupFreshness') && document.querySelector('#dgBackupFreshness').textContent==='Backup confirmado'")
    case.check('opening Backup refreshes current state without waiting for timer', page.locator('#dgBackupFreshness').inner_text() == 'Backup confirmado')
    case.check('opening Backup does not write', page.evaluate('localStorage.getItem(LSKEY)') == raw)


EXPORT_SETUP = r"""mode => {
  __br.exportMode=mode;__br.files=[];__br.fileEvents=[];__br.recoveryDialogs=[];__br.payload=null;
  const originalDownload=dgDownloadViaAnchor;
  dgDownloadViaAnchor=(name,blob)=>{__br.payload=blob;__br.fileEvents.push('download-started');return originalDownload(name,blob);};
  const handle={name:'SYNTHETIC-MOCK-ONLY',async getFileHandle(name){
    __br.fileEvents.push('getFileHandle');
    return {async createWritable(){
      __br.fileEvents.push('createWritable');
      if(mode==='before-write')throw new Error('synthetic before write');
      let pending;
      return {async write(blob){pending=blob;__br.payload=blob;__br.fileEvents.push('write');},
        async close(){__br.files.push({name,blob:pending});__br.fileEvents.push('close-resolved');}};
    }};
  }};
  dgFsSupported=()=>mode!=='download';
  S.dataGovernance.storage={configured:mode!=='download',folderName:handle.name,folderDisplayPath:handle.name,configuredAt:''};
  dgFsStatus=async()=>({state:'authorized',handle});dgFsFileExists=async()=>false;
  const recovery=dgExportRecoveryDialog;
  dgExportRecoveryDialog=state=>{
    const pending=recovery(state);
    const overlay=document.getElementById('dgExportRecoveryOverlay');
    __br.recoveryDialogs.push(overlay?.innerText||document.body.innerText);
    const cancel=document.getElementById('dgActCancel');
    if(!cancel)throw Error('Existing export recovery cancel control missing');
    cancel.click();return pending;
  };
  if(save()!==true)throw Error('Synthetic export checkpoint refused');
  if(mode==='metadata-refused')blockJPWealthPersistence();
  if(mode==='metadata-readback')__br.mode='readback';
  if(mode==='after-close')renderDgStorageCard=()=>{throw Error('synthetic UI error AFTER close');};
}"""


def export_phase(case, page, mode):
    page.evaluate(EXPORT_SETUP, mode)
    before = page.evaluate(FACTS)
    meta = page.evaluate('async()=>await exportFullBackup()')
    after = page.evaluate(FACTS)
    events = page.evaluate('({events:__br.fileEvents,files:__br.files.length,dialogs:__br.recoveryDialogs,alerts:__br.alerts})')
    case.observed.update(before=brief(before), after=brief(after), meta=meta, **events)
    text = '\n'.join(events['alerts'] + events['dialogs']).lower()
    case.check('export never auto-confirms human backup', after['governance']['backup'] == before['governance']['backup'])
    if mode == 'metadata-readback':
        case.check('file mock closed before metadata became unknown', events['files'] == 1 and events['events'].count('close-resolved') == 1)
        case.check('UNKNOWN export cannot return continuation metadata', meta is None and after['unknown'])
        case.check('UNKNOWN after close never claims no file', 'nenhum arquivo' not in text, text)
        return
    if mode == 'before-write':
        case.check('failure before write produces no completed file', events['files'] == 0 and 'close-resolved' not in events['events'])
        case.check('failure before write preserves metadata and disk', after['governance'] == before['governance'] and after['raw'] == before['raw'])
        case.check('cancel produces no successful export result', meta is None)
        return
    case.check('completed export result remains usable', isinstance(meta, dict) and bool(meta.get('filename')), meta)
    if mode == 'download':
        case.check('download initiation is identified without physical-save claim', events['events'] == ['download-started']
                   and 'iniciad' in text and 'arquivo salvo' not in text, text)
    else:
        case.check('folder mock writes and closes exactly once', events['files'] == 1
                   and events['events'].count('write') == 1 and events['events'].count('close-resolved') == 1, events)
        case.check('no false no-file claim after close', 'nenhum arquivo' not in text, text)
    if mode == 'metadata-refused':
        case.check('refused metadata preserves RAM governance and disk', after['governance'] == before['governance'] and after['raw'] == before['raw'])
        case.check('completed file and refused local registration are distinguished',
                   ('metadad' in text or 'registro' in text) and ('não' in text or 'falh' in text), text)
    elif mode != 'after-close':
        case.check('export sequence advances once only after output', after['governance']['export']['lastSequence'] == before['governance']['export']['lastSequence'] + 1)
        case.check('export metadata agrees with disk', json.loads(after['raw'])['dataGovernance'] == after['governance'])


def finalize_export_unknown(case, page):
    page.evaluate(EXPORT_SETUP, 'folder')
    page.evaluate(r"""() => {
      const begin=beginSessionExport;
      __br.sessionExportFinished=false;
      beginSessionExport=async function(...args){try{return await begin.apply(this,args);}
        finally{__br.sessionExportFinished=true;}};
    }""")
    case.require('finalize control exists', page.locator('#finalizeSessionBtn').count() == 1)
    page.locator('#finalizeSessionBtn').click()
    choices = page.locator('#sessionExport, #sessionExportNow')
    case.require('existing export step is available', choices.count() == 1)
    before = page.evaluate(FACTS)
    page.evaluate("__br.mode='readback'")
    choices.click()
    page.wait_for_function('__br.sessionExportFinished')
    after = page.evaluate(FACTS)
    facts = page.evaluate("({meta:sessionFinalizeExportMeta,files:__br.files.length,modal:document.getElementById('modalBox')?.textContent||document.getElementById('modalOverlay').textContent})")
    case.check('mock export completed once before unknown metadata', facts['files'] == 1)
    case.check('unknown result cannot enable session continuation', after['unknown'] and facts['meta'] is None)
    for ident in ('sessionExportAcknowledged', 'sessionExportContinue', 'sessionProceed', 'sessionDeleteConfirm'):
        case.check('destructive continuation absent: ' + ident, page.locator('#' + ident).count() == 0)
    before_state, after_state = json.loads(before['state']), json.loads(after['state'])
    before_state.pop('dataGovernance');after_state.pop('dataGovernance')
    case.check('no destructive data change occurs', before_state == after_state)
    case.check('unknown export failure does not claim no file', 'nenhum arquivo' not in facts['modal'].lower(), facts['modal'])
    case.observed.update(before=brief(before), after=brief(after), **facts)


def import_gate(case, page):
    before = page.evaluate(FACTS)
    result = page.evaluate(r"""() => {
      const rows=[],original=structuredClone(S);
      const attempt=(name,value)=>{try{normalizeImportedState(value);rows.push({name,rejected:false});}
        catch(error){rows.push({name,rejected:true,error:String(error.message)});}};
      attempt('root-array',[]);attempt('params-array',{...original,params:[]});
      attempt('envelope-type',{tipo:'other',state:original});
      attempt('envelope-version',{tipo:'jpwealth_full_backup',versao:'V999',state:original});
      attempt('envelope-version-container',{tipo:'jpwealth_full_backup',versao:{future:true},state:original});
      attempt('envelope-storage-key',{tipo:'jpwealth_full_backup',localStorageKey:'other',state:original});
      attempt('envelope-state-null',{tipo:'jpwealth_full_backup',state:null});
      attempt('envelope-state-array',{tipo:'jpwealth_full_backup',state:[]});
      attempt('envelope-state-scalar',{tipo:'jpwealth_full_backup',state:42});
      for(const name of ['alladin','personalFinance','fxPlanning','nocoda','pivotStudies','mvpNotes']){
        for(const bad of [null,[],42])attempt(name+'-'+(bad===null?'null':Array.isArray(bad)?'array':'scalar'),{...original,[name]:bad});
      }
      const legacy=structuredClone(original);
      for(const key of ['alladin','personalFinance','fxPlanning','nocoda','pivotStudies','mvpNotes','dataGovernance'])delete legacy[key];
      const absent=[legacy,{state:legacy},{tipo:'jpwealth_full_backup',state:legacy}].map((value,index)=>{
        try{return {index,accepted:true,keys:Object.keys(normalizeImportedState(value))};}
        catch(error){return {index,accepted:false,error:String(error.message)};}
      });
      const future=structuredClone(original);future.alladin.schemaVersion=999;
      const futureResult=normalizeImportedState(future);
      return {rows,absent,futureAlladinPreserved:JSON.stringify(futureResult.alladin)===JSON.stringify(future.alladin)};
    }""")
    after = page.evaluate(FACTS)
    case.observed.update(**result, before=brief(before), after=brief(after))
    for row in result['rows']:
        case.check('explicit incompatible container rejected: ' + row['name'], row['rejected'], row)
    case.check('absent legacy aggregates and envelope metadata remain accepted', all(row['accepted'] for row in result['absent']), result['absent'])
    case.check('future Alladin remains preserved for existing fail-closed domain', result['futureAlladinPreserved'])
    case.check('normalization attempts preserve live state disk and gates', before == after)


def import_ui(case, page, kind):
    before = page.evaluate(FACTS)
    page.evaluate("() => {__br.alerts=[];__br.confirmQuestions=[];__br.accept=true;}")
    payload = page.evaluate('S')
    if kind == 'corrupt':
        content = b'{ synthetic invalid JSON'
    else:
        content = json.dumps({'tipo': 'jpwealth_full_backup', 'versao': 'V9.1', 'state': payload}).encode()
        page.evaluate('__br.accept=false')
    case.require('existing import control exists', page.locator('#importFullBackupInput').count() == 1)
    page.locator('#importFullBackupInput').set_input_files({'name': 'synthetic-backup.json', 'mimeType': 'application/json', 'buffer': content})
    page.wait_for_function('__br.alerts.length>0 || __br.confirmQuestions.length>0')
    settle(page)
    after = page.evaluate(FACTS)
    case.check('invalid or cancelled import preserves exact live state and disk', after['state'] == before['state'] and after['raw'] == before['raw'])
    case.check('invalid or cancelled import preserves gates and epoch', all(after[key] == before[key]
               for key in ('unknown', 'blocked', 'recovery', 'epoch')))
    case.observed.update(before=brief(before), after=brief(after))


def import_fault(case, page, mode):
    original = page.evaluate(FACTS)
    payload = page.evaluate("() => ({tipo:'jpwealth_full_backup',versao:'V9.1',state:{...structuredClone(S),syntheticImportedMarker:'BR-IMPORTED-DIFFERENT'}})")
    content = json.dumps(payload).encode()
    page.evaluate(r"""mode => {
      __br.mode=mode==='recovery-noop'?'noop':mode;__br.checkpoints=0;__br.boots=0;
      const checkpoint=markSessionCheckpoint,oldBoot=boot;
      markSessionCheckpoint=function(...args){__br.checkpoints++;return checkpoint.apply(this,args);};
      boot=function(...args){__br.boots++;return oldBoot.apply(this,args);};
      if(mode==='unknown')markJPWealthPersistenceOutcomeUnknown('synthetic existing unknown before import');
      if(mode==='recovery-noop'){
        const raw='{ BR-SYNTHETIC-RECOVERY';
        __br.nativeSet.call(localStorage,LSKEY,raw);jpWealthAdoptPersistedRaw(raw);
        enterLoadRecoveryMode('json-invalido',raw,new Error('synthetic existing recovery'));
      }
      if(mode==='divergent'){
        const other=JSON.parse(__br.nativeGet.call(localStorage,LSKEY));
        other.syntheticOtherWriter='BR-OTHER-IMPORT-WRITER';__br.otherRaw=JSON.stringify(other);
      }
    }""", mode)
    before = page.evaluate(FACTS)
    case.require('existing real import input', page.locator('#importFullBackupInput').count() == 1)
    upload = {'name': 'synthetic-different-state.json', 'mimeType': 'application/json', 'buffer': content}
    page.locator('#importFullBackupInput').set_input_files(upload)
    page.wait_for_function('__br.alerts.length>0')
    refresh(page)
    after = page.evaluate(FACTS)
    calls = page.evaluate('({checkpoints:__br.checkpoints,boots:__br.boots})')
    case.observed.update(original=brief(original), before=brief(before), after=brief(after), calls=calls)
    case.check('failed import cannot publish successful checkpoint', calls['checkpoints'] == 0, calls)
    case.check('failed import does not announce success', not any('importado com sucesso' in text.lower() for text in after['alerts']), after['alerts'])
    if mode == 'unknown':
        case.check('preexisting UNKNOWN preserves RAM and disk without writes', after['state'] == before['state']
                   and after['raw'] == before['raw'] and after['writes'] == before['writes'])
        case.check('preexisting UNKNOWN aborts before epoch rotation', after['epoch'] == before['epoch']
                   and after['aux'].get('jpwealth_base_epoch_v1') == before['aux'].get('jpwealth_base_epoch_v1'))
        case.check('preexisting UNKNOWN remains blocked and no boot', after['unknown'] and calls['boots'] == 0)
    elif mode in ('readback', 'divergent'):
        case.check('indeterminate import enters UNKNOWN without saved status', after['unknown']
                   and after['persist']['exists'] and after['persist']['state'] != 'ok')
        case.check('indeterminate import does not blindly restore previous RAM', after['state'] != before['state']
                   and json.loads(after['state']).get('syntheticImportedMarker') == 'BR-IMPORTED-DIFFERENT')
        page.evaluate("() => {__br.mode='normal';__br.readFault=false;}")
        attempt = page.evaluate('save()')
        retry = page.evaluate(FACTS)
        case.check('UNKNOWN refuses subsequent save without changing disk', attempt is False and retry['raw'] == after['raw']
                   and retry['writes'] == after['writes'])
    else:
        case.check('proven refusal restores entire previous RAM and disk', after['state'] == before['state'] and after['raw'] == before['raw'])
        case.check('proven refusal does not boot imported state', calls['boots'] == 0)
        if mode == 'recovery-noop':
            case.require('recovery warning existed before import', before['recovery'] and before['recoveryWarning']['exists'] and before['recoveryWarning']['visible'])
            case.check('refused recovery import preserves context and warning', after['recoveryContext'] == before['recoveryContext']
                       and after['recoveryWarning']['exists'] and after['recoveryWarning']['visible'])
        page.evaluate("() => {__br.mode='normal';__br.readFault=false;__br.alerts=[];}")
        page.locator('#importFullBackupInput').set_input_files(upload)
        page.wait_for_function('__br.alerts.length>0')
        retry = page.evaluate(FACTS)
        try:
            retry_disk = json.loads(retry['raw'])
        except (TypeError, json.JSONDecodeError):
            retry_disk = {}
        case.check('explicit retry after proven refusal imports the distinct state',
                   retry_disk.get('syntheticImportedMarker') == 'BR-IMPORTED-DIFFERENT'
                   and json.loads(retry['state']).get('syntheticImportedMarker') == 'BR-IMPORTED-DIFFERENT'
                   and any('importado com sucesso' in text.lower() for text in retry['alerts']))
        case.observed['retry'] = brief(retry)


def roundtrip(case, page, helper, browser, url, root, metadata_only=False):
    design, studies = load(root, 'design_experience_test'), load(root, 'studies_notes_persistence_contract_test')
    pf = json.loads((root / 'tools/fixtures/personal_finance_v1.json').read_text())['personalFinance']
    page.evaluate(design.ALLADIN_SEED)
    page.evaluate(r"""({pf,nc,pv,aux}) => {
      S.personalFinance=structuredClone(pf);
      const instrument=instrumentCatalog()[0].id;
      S.nocoda={schemaVersion:1,studies:{[instrument]:{...nc,updatedAt:'2025-01-01',extension:'BR-NC'}}};
      S.pivotStudies={schemaVersion:1,studies:[{id:'br-study',instrumentId:instrument,periodStart:'2025-01-01',periodEnd:'2025-12-31',
        createdAt:'2025-01-01',updatedAt:'2025-01-01',pivots:[pv]}]};
      S.ledger=[{data:'2026-01-03',saldo:10123,resultado:123,nota:'BR-FOREX'},{data:'2026-01-17',saldo:10200,resultado:77,nota:'BR-FOREX'}];
      const folder=mvpNotesCreateFolder('BR-Pasta');
      if(!folder || !mvpNotesCreate({content:'BR-Nota 1\nCorpo preservado',type:'task',priority:'medium',status:'open',folderId:folder.id})
        || !mvpNotesCreate({content:'BR-Nota 2',type:'task',priority:'high',status:'open',folderId:folder.id}))throw Error('Synthetic Notes seed refused');
      S.syntheticBackupExtension={preserved:'BR-UNKNOWN-FIELD'};
      S=normalizeImportedState(S);
      if(save()!==true)throw Error('Synthetic multimodule checkpoint refused');
      Object.entries(aux).forEach(([key,value])=>__br.nativeSet.call(localStorage,key,value));
      S.accounts[0].investorPassword='BR-SYNTHETIC-SECRET';
      S.onboarding.investorPassword='BR-SYNTHETIC-SECRET';
      __br.exportPayload=null;
      const download=dgDownloadViaAnchor;
      dgDownloadViaAnchor=(filename,blob)=>{__br.exportPayload=blob;return download(filename,blob);};
      dgFsSupported=()=>false;
    }""", {'pf': pf, 'nc': studies.NC, 'pv': studies.PV, 'aux': AUX})
    before = page.evaluate(FACTS)
    expected = page.evaluate('(keys)=>Object.fromEntries(keys.map(key=>[key,structuredClone(S[key])]))', list(DOMAINS))
    case.require('multiple domains are materially populated', len(expected['ledger']) == 2
                 and len(expected['alladin']['transactions']) > 0 and len(expected['mvpNotes']['items']) == 2
                 and len(expected['nocoda']['studies']) > 0 and len(expected['pivotStudies']['studies']) > 0
                 and bool(expected['personalFinance']['months']))
    with page.expect_download():
        meta = page.evaluate('async()=>await exportFullBackup({quiet:true})')
    body = page.evaluate('async()=>await __br.exportPayload.text()')
    payload = json.loads(body)
    after = page.evaluate(FACTS)
    case.check('existing envelope retains identity version and timestamp', payload.get('tipo') == 'jpwealth_full_backup'
               and payload.get('versao') == 'V9.1' and payload.get('localStorageKey') == 'jpwealth_v9_state'
               and bool(payload.get('exportadoEm')))
    case.check('secret excluded from serialized artifact', 'BR-SYNTHETIC-SECRET' not in body and payload.get('segredosIncluidos') is False)
    case.check('all populated domains exported semantically intact', all(payload['state'][key] == value for key, value in expected.items()))
    case.check('unknown top-level field preserved', payload['state'].get('syntheticBackupExtension') == {'preserved': 'BR-UNKNOWN-FIELD'})
    case.check('auxiliary preferences neither exported nor modified', all(key not in payload['state'] for key in AUX)
               and all(token not in body for token in ('BR-AUX-PROFILE', 'BR-AUX-WIDGET', 'BR-AUX-SOURCE'))
               and before['aux'] == after['aux'])
    case.observed.update(envelope_without_state={key: value for key, value in payload.items() if key != 'state'},
                        payload_sha256=digest(body), domain_hashes={key: digest(value) for key, value in expected.items()}, meta=meta)
    if metadata_only:
        description = json.dumps({key: value for key, value in payload.items() if key != 'state'}, ensure_ascii=False).lower()
        aliases = [('personalfinance', 'finanças pessoais'), ('alladin',), ('nocoda', 'nocoda'),
                   ('pivotstudies', 'pivots'), ('mvpnotes', 'notas')]
        case.check('metadata identifies actual included sections', all(any(alias in description for alias in group) for group in aliases), description)
        case.check('metadata identifies current build', page.evaluate('JP_WEALTH_BUILD_ID').lower() in description)
        case.check('metadata explains deliberate profile and preference exclusions',
                   ('perfil' in description or 'profile' in description) and ('prefer' in description or 'launcher' in description), description)
        return
    target = prepare(helper, browser, url)
    try:
        target_aux = {**AUX,
            'jpwealth_local_profile_v1': '{"schemaVersion":1,"displayName":"BR-TARGET-PROFILE","avatarDataUrl":null}',
            'jpwealth_notes_launcher_position_v1': '{"schemaVersion":1,"x":0.8,"y":0.3}'}
        target.evaluate('aux=>Object.entries(aux).forEach(([key,value])=>__br.nativeSet.call(localStorage,key,value))', target_aux)
        local_before = target.evaluate(FACTS)['aux']
        case.require('real import control exists in disposable target', target.locator('#importFullBackupInput').count() == 1)
        target.locator('#importFullBackupInput').set_input_files({'name': 'synthetic-multimodule.json', 'mimeType': 'application/json', 'buffer': body.encode()})
        target.wait_for_function("__br.alerts.some(text=>text.toLowerCase().includes('importado com sucesso'))")
        settle(target)
        actual = target.evaluate('(keys)=>Object.fromEntries(keys.map(key=>[key,S[key]]))', list(DOMAINS))
        for key, value in expected.items():
            case.check('round-trip exact semantic domain: ' + key, actual[key] == value,
                       {'before_sha256': digest(value), 'after_sha256': digest(actual[key])})
        final = target.evaluate(FACTS)
        disk = json.loads(final['raw'])
        case.check('round-trip domains actually reached storage', all(disk[key] == value for key, value in expected.items()))
        case.check('unknown extension survives real import', disk.get('syntheticBackupExtension') == {'preserved': 'BR-UNKNOWN-FIELD'})
        case.check('import preserves destination local preferences', all(final['aux'].get(key) == local_before.get(key) for key in AUX))
        helper.assert_fixture_requests(target.context)
        case.check('round-trip has no pageerror', not target.jpwealth_observed['pageerror'], target.jpwealth_observed['pageerror'])
    finally:
        target.context.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=ROOT)
    parser.add_argument('--artifact', required=True, type=Path)
    parser.add_argument('--case', action='append', help='Run only a named case; repeat to select several')
    args = parser.parse_args()
    root, artifact = args.root.resolve(), args.artifact.resolve()
    if artifact.is_relative_to(root):
        parser.error('--artifact must be outside the tested product')
    if artifact.exists():
        parser.error('refusing to replace an existing receipt')
    sys.path.insert(0, str(root / 'tools'))
    helper = load(root, 'storage_governance_test')
    sources_before = identity(root)
    cases = {**{'confirmation-' + mode: ('confirmation', mode) for mode in
              ('normal', 'refused', 'quota', 'unknown', 'noop', 'readback', 'divergent')},
             'backup-freshness': ('freshness', None),
             **{'export-' + mode: ('export', mode) for mode in
                ('download', 'folder', 'before-write', 'after-close', 'metadata-refused', 'metadata-readback')},
             'finalize-export-unknown': ('finalize-export', None),
             'import-containers': ('import-gate', None), 'import-corrupt': ('import-ui', 'corrupt'),
             'import-cancelled': ('import-ui', 'cancelled'),
             **{'import-' + mode: ('import-fault', mode) for mode in ('quota', 'noop', 'unknown', 'readback', 'divergent', 'recovery-noop')},
             'multimodule-roundtrip': ('roundtrip', None), 'coverage-metadata': ('metadata', None)}
    chosen = args.case or list(cases)
    if set(chosen) - set(cases):
        parser.error('unknown case; available: ' + ', '.join(cases))
    result = {'started_at': datetime.now(timezone.utc).isoformat(), 'root': str(root),
        'build': (root / 'build-id.js').read_text().split("'")[1],
        'test_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'sources_before': sources_before, 'cases': [],
        'method': 'Existing storage_governance_test.prepare_page + nominal bootstrap; isolated contexts, synthetic data. Folder API is mocked; no physical file or real profile claim.'}
    server = ThreadingHTTPServer(('127.0.0.1', 0), partial(helper.Quiet, directory=str(root)))
    threading.Thread(target=server.serve_forever, daemon=True).start()
    url = f'http://127.0.0.1:{server.server_port}/'
    try:
        with sync_playwright() as pw:
            options = {'headless': True}
            if os.environ.get('JP_WEALTH_CHROMIUM'):
                options['executable_path'] = os.environ['JP_WEALTH_CHROMIUM']
            browser = pw.chromium.launch(**options)
            try:
                for name in chosen:
                    case, page = Case(name), None
                    try:
                        page = prepare(helper, browser, url)
                        action, mode = cases[name]
                        if action == 'confirmation': confirmation(case, page, mode)
                        elif action == 'freshness': freshness(case, page)
                        elif action == 'export': export_phase(case, page, mode)
                        elif action == 'import-gate': import_gate(case, page)
                        elif action == 'import-ui': import_ui(case, page, mode)
                        elif action == 'import-fault': import_fault(case, page, mode)
                        elif action == 'finalize-export': finalize_export_unknown(case, page)
                        else: roundtrip(case, page, helper, browser, url, root, action == 'metadata')
                        helper.assert_fixture_requests(page.context)
                        case.check('no uncaught pageerror', not page.jpwealth_observed['pageerror'], page.jpwealth_observed['pageerror'])
                    except AssertionError as error:
                        if not any(check['result'] != 'PASS' for check in case.checks):
                            case.check('required fixture or product invariant', False, str(error))
                    except Exception as error:
                        case.checks.append({'name': 'case execution', 'result': 'TEST_HARNESS_FAIL' if page is None else 'PRODUCT_FAIL',
                            'detail': str(error), 'traceback': traceback.format_exc()})
                    finally:
                        if page:
                            case.observed['browser_events'] = page.jpwealth_observed
                            page.context.close()
                    statuses = [check['result'] for check in case.checks]
                    status = 'TEST_HARNESS_FAIL' if 'TEST_HARNESS_FAIL' in statuses else 'PRODUCT_FAIL' if 'PRODUCT_FAIL' in statuses else 'PASS'
                    result['cases'].append({'name': name, 'result': status, 'checks': case.checks, 'observed': case.observed})
                    print(name + ': ' + status, flush=True)
            finally:
                browser.close()
    finally:
        server.shutdown();server.server_close()
        result['sources_after'] = identity(root)
        result['sources_unchanged'] = result['sources_before'] == result['sources_after']
        result['finished_at'] = datetime.now(timezone.utc).isoformat()
        result['summary'] = {status: sum(case['result'] == status for case in result['cases'])
                             for status in ('PASS', 'PRODUCT_FAIL', 'TEST_HARNESS_FAIL')}
        artifact.parent.mkdir(parents=True, exist_ok=True)
        encoded = json.dumps(result, ensure_ascii=False, indent=2)
        with artifact.open('x') as file:
            file.write(encoded + '\n')
    print(json.dumps({'summary': result['summary'], 'sources_unchanged': result['sources_unchanged'], 'artifact': str(artifact)}), flush=True)
    return 0 if result['sources_unchanged'] and len(result['cases']) == len(chosen) and all(case['result'] == 'PASS' for case in result['cases']) else 1


if __name__ == '__main__':
    raise SystemExit(main())
