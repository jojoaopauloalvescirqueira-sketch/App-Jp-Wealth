#!/usr/bin/env python3
"""Calendar N2 boundaries with isolated browser storage and synthetic records.

Oracles come from the approved calendar/agenda contract (2026-10-23): explicit
confirmed CRUD, opaque incompatible data, complete backup, separate drafts and
preferences. No personal profile, external live feed or real financial data.
"""
import argparse
from functools import partial
import hashlib
import json
from pathlib import Path
import threading
import traceback

from playwright.sync_api import sync_playwright
from browser_fixture_server import BrowserFixtureServer
from browser_bootstrap_fixture import wait_bootstrap, assert_fixture_requests
from dashboard_macro_test import launch_browser
from notification_center_test import Quiet, prepare

ROOT = Path(__file__).resolve().parents[1]
TASK = {'kind': 'task', 'title': 'SYN agenda task', 'notes': 'Synthetic observation',
        'date': '2026-09-14', 'allDay': True}
PREFS_KEY = 'jpwealth_calendar_view_v1'
PREFS = {'schemaVersion': 1, 'currencies': ['USD', 'GBP', 'JPY', 'NZD', 'CHF'],
         'impacts': ['high'], 'contents': ['economic', 'personal', 'app']}
DEVELOPMENT_CONTROLLER = False


def require_agenda(page):
    assert page.evaluate("typeof window.JPWAgenda?.queries?.prepare === 'function'"), 'Agenda domain must load in the real page'


def seed(page):
    require_agenda(page)
    page.evaluate("""() => {
      closeModal(); S=structuredClone(DEFAULTS); S.onboarding.done=true;
      S.calendarRecoveryProbe='SYN_AGENDA_RECOVERY';
      S.foreignAgendaExtension={opaque:['preserve',7]};
      if(save()!==true)throw Error('Synthetic confirmed base was refused');
      JPWAgenda.commands.resetContext();
    }""")


def core_crud(page, _dialogs):
    seed(page)
    result = page.evaluate("""input => {
      const token=JPWAgenda.queries.prepare({id:null}).token;
      const first=JPWAgenda.commands.save({input,token});
      return {first,memory:JPWAgenda.queries.snapshot(),disk:JSON.parse(localStorage.getItem(LSKEY))};
    }""", TASK)
    assert result['first']['status'] == 'CONFIRMED', result
    item_id = result['first']['id']
    assert result['disk']['personalAgenda']['items'][0]['id'] == item_id
    assert result['disk']['foreignAgendaExtension'] == {'opaque': ['preserve', 7]}
    page.reload(); wait_bootstrap(page)
    assert page.evaluate('JPWAgenda.queries.snapshot().items[0].title') == TASK['title']
    result = page.evaluate("""({id,input}) => {
      const changed=JPWAgenda.commands.save({input:{...input,title:'SYN corrected'},token:JPWAgenda.queries.prepare({id}).token});
      const completed=JPWAgenda.commands.setCompleted({id,completed:true,token:JPWAgenda.queries.prepare({id}).token});
      return {changed,completed,disk:JSON.parse(localStorage.getItem(LSKEY)).personalAgenda};
    }""", {'id': item_id, 'input': TASK})
    assert result['changed']['ok'] and result['completed']['ok'], result
    assert result['disk']['items'][0]['title'] == 'SYN corrected'
    assert result['disk']['items'][0]['completedAt'] == '2026-09-14T12:00:00.000Z'
    page.reload(); wait_bootstrap(page)
    removed = page.evaluate("""id => JPWAgenda.commands.remove({id,token:JPWAgenda.queries.prepare({id}).token})""", item_id)
    assert removed['status'] == 'CONFIRMED', removed
    page.reload(); wait_bootstrap(page)
    assert page.evaluate('JPWAgenda.queries.snapshot().items') == []
    return {'created_updated_completed_removed_reloaded': item_id}


def import_containers(page, _dialogs):
    seed(page)
    result = page.evaluate("""() => {
      const before=JSON.stringify(S),raw=localStorage.getItem(LSKEY),rejected=[];
      for(const value of [null,42,'scalar',[],true]){
        const source=structuredClone(S); source.personalAgenda=value;
        let refused=false;try{normalizeImportedState(source);}catch(error){refused=true;}
        rejected.push(refused);
      }
      const legacy=structuredClone(S);delete legacy.personalAgenda;
      const imported=normalizeImportedState(legacy);
      return {rejected,legacyAbsent:!Object.hasOwn(imported,'personalAgenda'),stateUnchanged:before===JSON.stringify(S),diskUnchanged:raw===localStorage.getItem(LSKEY)};
    }""")
    assert result['rejected'] == [True]*5, 'Present incompatible Agenda containers must refuse before import: '+repr(result)
    assert result['legacyAbsent'] and result['stateUnchanged'] and result['diskUnchanged'], result
    return result


def backup_roundtrip(page, _dialogs):
    seed(page)
    result = page.evaluate("""async ({input,preferences}) => {
      const created=JPWAgenda.commands.save({input,token:JPWAgenda.queries.prepare({id:null}).token});
      if(!created.ok)throw Error(JSON.stringify(created));
      S.personalAgenda.extension={opaque:['aggregate',9]};S.personalAgenda.items[0].extension={opaque:'item'};
      if(save()!==true)throw Error('Synthetic compatible extensions were refused');JPWAgenda.commands.resetContext();
      const key='jpwealth_calendar_view_v1',preferenceRaw=JSON.stringify(preferences);localStorage.setItem(key,preferenceRaw);
      const publicKey='jpwealth.ui.ffNews.v1';localStorage.setItem(publicKey,JSON.stringify({fetchedAt:Date.now(),payload:{version:1,generated_at:new Date().toISOString(),events:[]}}));
      const publicCacheExists=localStorage.getItem(publicKey)!==null;
      const before=JSON.stringify(S.personalAgenda),blob=dgBuildBackupBlob(1,'synthetic-calendar.json',new Date().toISOString());
      const file=new File([blob],'synthetic-calendar.json',{type:'application/json'});
      const parsed=await new Promise((resolve,reject)=>{const reader=new FileReader();reader.onload=()=>resolve(JSON.parse(reader.result));reader.onerror=()=>reject(reader.error);reader.readAsText(file);});
      const oldRoot=S,oldRaw=localStorage.getItem(LSKEY),normalized=normalizeImportedState(parsed);
      return {created,fromFile:parsed.state.personalAgenda,roundtrip:normalized.personalAgenda,exact:JSON.stringify(normalized.personalAgenda)===before,
        preferenceRaw,exportedPreference:parsed.workspace.preferences[key],recoveredPreference:normalized.workspaceRecovery.snapshot.preferences[key],
        publicCacheExists,publicCacheExcluded:!Object.hasOwn(parsed.workspace.preferences,publicKey),
        currentUnchanged:S===oldRoot&&localStorage.getItem(LSKEY)===oldRaw,hasCoverage:parsed.cobertura.sections.includes('personalAgenda')};
    }""", {'input': TASK, 'preferences': {**PREFS, 'currencies': ['USD','EUR','GBP','JPY','CHF','CAD','AUD','NZD','CNY']}})
    assert result['exact'] and result['currentUnchanged'] and result['hasCoverage'], result
    assert result['roundtrip']['items'][0]['date'] == '2026-09-14'
    assert result['roundtrip']['items'][0]['extension'] == {'opaque': 'item'}
    assert result['roundtrip']['extension'] == {'opaque': ['aggregate', 9]}
    assert result['exportedPreference']==result['preferenceRaw']==result['recoveredPreference'],result
    assert result['publicCacheExists'] and result['publicCacheExcluded'],result
    return {'blob_file_reader_normalizer_exact': True, 'nineCurrenciesPreferenceExact':True,'publicCacheExcluded':True,'item_id': result['created']['id']}


def future_opaque(page, _dialogs):
    seed(page)
    future = {'schemaVersion': 99, 'opaque': {'preserve': ['future', 17]}}
    result = page.evaluate("""async future => {
      S.personalAgenda=structuredClone(future);if(save()!==true)throw Error('Synthetic future fixture refused');
      JPWAgenda.commands.resetContext();const before=JSON.stringify(S),raw=localStorage.getItem(LSKEY);
      const snapshot=JPWAgenda.queries.snapshot(),prepared=JPWAgenda.queries.prepare({id:null});
      const refused=JPWAgenda.commands.save({input:{kind:'task',title:'Do not create',notes:'',date:'2026-09-14',allDay:true},token:{}});
      const blob=dgBuildBackupBlob(2,'future-agenda.json',new Date().toISOString());
      const parsed=JSON.parse(await blob.text()),normalized=normalizeImportedState(parsed);
      const preserved=sessionPreserveLongitudinal({}),finalized=emptyJPWealthState(preserved.valor);
      return {snapshot,prepared,refused,exported:parsed.state.personalAgenda,normalized:normalized.personalAgenda,finalized:finalized.personalAgenda,unchanged:JSON.stringify(S)===before&&localStorage.getItem(LSKEY)===raw};
    }""", future)
    assert result['snapshot']['status'] == 'INCOMPATIBLE' and not result['prepared']['ok'] and not result['refused']['ok'], result
    assert result['exported'] == future and result['normalized'] == future and result['finalized'] == future, result
    assert result['unchanged'], result
    return {'opaque_future_export_import_finalization_preserved': True}


def preference_boundary(page, _dialogs):
    seed(page)
    result = page.evaluate("""({key,preferences}) => {
      const validRaw=JSON.stringify(preferences),before=localStorage.getItem(LSKEY),source=JSON.stringify(S);
      const check=value=>{try{jpwWorkspaceValidate({schemaVersion:2,preferences:{[key]:JSON.stringify(value)},drafts:[]});return true;}catch(error){return false;}};
      const valid=check(preferences),expanded=check({...preferences,currencies:['USD','EUR','GBP','JPY','CHF','CAD','AUD','NZD','CNY']}),invalid=[{...preferences,schemaVersion:99},{...preferences,currencies:['XXX']},{...preferences,impacts:['critical']},{...preferences,contents:['forex']},{...preferences,contents:'personal'},[]].map(check);
      let captured=null,captureError=null;localStorage.setItem(key,validRaw);
      try{captured=jpwWorkspaceCapture().preferences[key];}catch(error){captureError=error.message;}
      return {valid,expanded,invalid,captured,captureError,stateUnchanged:source===JSON.stringify(S),diskUnchanged:before===localStorage.getItem(LSKEY)};
    }""", {'key': PREFS_KEY, 'preferences': PREFS})
    assert result['valid'], 'Known Calendar preference must be accepted by the workspace allowlist: '+repr(result)
    assert result['expanded'], 'All nine approved currency filters must be accepted without resetting the old preference: '+repr(result)
    assert result['invalid'] == [False]*6, 'Calendar enum/schema/container validation must reject invalid imported preferences: '+repr(result)
    assert result['captured'] == json.dumps(PREFS, separators=(',', ':')), result
    assert result['stateUnchanged'] and result['diskUnchanged'], result
    return result


def require_ui(page):
    # While the parent assembles manifest/index, load the actual new controller
    # in the browser; once integrated this branch does not run.
    if DEVELOPMENT_CONTROLLER and not page.evaluate("typeof window.JPWCalendar?.open === 'function'"):
        page.add_script_tag(url=page.url.rsplit('/', 1)[0]+'/src/js/40-app/19-calendar-agenda.js')
    assert page.evaluate("typeof window.JPWCalendar?.open === 'function'"), 'Calendar controller is required for draft integration'


def open_draft(page):
    require_ui(page)
    assert page.evaluate('JPWCalendar.open()') is True
    page.locator('#calendarDialog [data-calendar-action="new"]').click()
    page.locator('#calendarDialog .calendar-form [name="title"]').fill('SYN unsaved agenda draft')
    page.locator('#calendarDialog .calendar-form [name="notes"]').fill('SYN draft notes')


def draft_capture(page, _dialogs):
    seed(page); open_draft(page)
    result = page.evaluate("""() => {
      const raw=localStorage.getItem(LSKEY),state=JSON.stringify(S),drafts=jpwWorkspaceDrafts();
      return {drafts,stateUnchanged:state===JSON.stringify(S),diskUnchanged:raw===localStorage.getItem(LSKEY)};
    }""")
    assert len(result['drafts']) == 1, 'Calendar provider must own each draft once; generic input collection must exclude .calendar-form: '+repr(result)
    draft = result['drafts'][0]
    assert draft['provider'] == 'calendar-agenda' and draft['version'] == 1, draft
    assert json.loads(draft['text'])['title'] == 'SYN unsaved agenda draft'
    assert 'token' not in json.loads(draft['text']), draft
    assert result['stateUnchanged'] and result['diskUnchanged'], result
    page.keyboard.press('Escape')
    assert page.evaluate('JPWCalendar.open()') is True
    assert page.locator('#calendarDialog [name="title"]').input_value() == 'SYN unsaved agenda draft'
    assert page.evaluate('jpwWorkspaceDrafts().length') == 1
    return {'single_closed_reopened_draft': draft}


def draft_recovery(page, _dialogs):
    seed(page); open_draft(page)
    result = page.evaluate("""async () => {
      JPWCalendar.close();const drafts=jpwWorkspaceDrafts(),raw=localStorage.getItem(LSKEY),source=JSON.stringify(S);
      const blob=dgBuildBackupBlob(3,'calendar-drafts.json',new Date().toISOString()),parsed=JSON.parse(await blob.text()),normalized=normalizeImportedState(parsed);
      const exported=parsed.workspace.drafts.filter(d=>d.provider==='calendar-agenda');
      JPWCalendar.resetContext();const inspection=JPWWorkspaceDrafts.inspect(exported[0]);
      const reopened=JPWWorkspaceDrafts.reopen(exported[0]);
      const title=document.querySelector('#calendarDialog [name="title"]')?.value;
      const unchanged=raw===localStorage.getItem(LSKEY)&&source===JSON.stringify(S);
      JPWCalendar.resetContext();
      const changed=JPWAgenda.commands.save({input:{kind:'task',title:'SYN changed context',notes:'',date:'2026-09-14',allDay:true},token:JPWAgenda.queries.prepare({id:null}).token});
      const incompatible=JPWWorkspaceDrafts.inspect(exported[0]);
      return {draftCount:drafts.length,exportCount:exported.length,inspection,reopened,title,unchanged,changed,incompatible,
        normalized:normalized.workspaceRecovery.snapshot.drafts.filter(d=>d.provider==='calendar-agenda')};
    }""")
    assert result['draftCount'] == result['exportCount'] == 1, result
    assert result['inspection']['compatible'] and result['reopened']['ok'], result
    assert result['title'] == 'SYN unsaved agenda draft' and result['unchanged'], result
    assert result['changed']['ok'] and not result['incompatible']['compatible'], result
    assert len(result['normalized']) == 1
    assert 'token' not in json.loads(result['normalized'][0]['text'])
    return {'reopened_without_writing': True, 'changed_context_refused': True, 'draft': result['normalized'][0]}


def finalization_preservation(page, _dialogs):
    seed(page)
    created = page.evaluate("""input => JPWAgenda.commands.save({input,token:JPWAgenda.queries.prepare({id:null}).token})""", TASK)
    assert created['ok'], created
    page.evaluate('({key,preferences})=>localStorage.setItem(key,JSON.stringify(preferences))', {'key': PREFS_KEY, 'preferences': PREFS})
    open_draft(page)
    result = page.evaluate("""async key => {
      JPWCalendar.close();const expected=JSON.stringify(S.personalAgenda),pref=localStorage.getItem(key),token=JPWAgenda.queries.prepare({id:S.personalAgenda.items[0].id}).token;
      markSessionCheckpoint();openFinalizeSessionFlow();await finalizeJPWealthSession();
      const disk=JSON.parse(localStorage.getItem(LSKEY)),recovered=disk.workspaceRecovery?.drafts?.filter(d=>d.provider==='calendar-agenda')||[];
      const stale=JPWAgenda.commands.remove({id:token.itemId,token});
      const providers=jpwWorkspaceDrafts().filter(d=>d.provider==='calendar-agenda');
      const reopened=JPWCalendar.open(),hasOldForm=!!document.querySelector('#calendarDialog .calendar-form');
      JPWCalendar.close();
      return {exact:JSON.stringify(disk.personalAgenda)===expected,prefsPreserved:localStorage.getItem(key)===pref,recovered,stale,providers,reopened,hasOldForm,notice:document.getElementById('sessionNotice')?.textContent||'',blocked:jpWealthPersistenceIsBlocked()};
    }""", PREFS_KEY)
    assert result['exact'] and result['prefsPreserved'], result
    assert len(result['recovered']) == 1, result
    # Recovered journal material is intentionally still visible in jpwWorkspaceDrafts;
    # the controller itself must not contribute a second live form after dispose.
    assert len(result['providers']) == 1, result
    assert result['stale']['status'] == 'CONFLICT', result
    # Existing finalization intentionally keeps the ordinary writer blocked on
    # success; only an unsuccessful finalization resumes it in the finally block.
    assert result['reopened'] and not result['hasOldForm'] and result['blocked'], result
    return {'confirmed_agenda_and_preferences_preserved': True, 'draft_count': len(result['recovered']), 'stale_token_status': result['stale']['status'], 'session_writer_blocked': result['blocked']}


CASES = {'core-crud': core_crud, 'import-containers': import_containers,
         'backup-roundtrip': backup_roundtrip, 'future-opaque': future_opaque,
         'preference-boundary': preference_boundary, 'draft-capture': draft_capture,
         'draft-recovery': draft_recovery, 'finalization-preservation': finalization_preservation}


def main():
    global DEVELOPMENT_CONTROLLER
    parser = argparse.ArgumentParser()
    parser.add_argument('--case', action='append', default=[])
    parser.add_argument('--receipt', type=Path)
    parser.add_argument('--development-controller', action='store_true', help='Development only: load the actual UI source before parent manifest integration')
    args = parser.parse_args()
    DEVELOPMENT_CONTROLLER = args.development_controller
    names = args.case or list(CASES)
    assert set(names) <= set(CASES), {'unknown_cases': set(names)-set(CASES)}
    server = BrowserFixtureServer(('127.0.0.1', 0), partial(Quiet, directory=str(ROOT)))
    threading.Thread(target=server.serve_forever, daemon=True).start()
    results = []
    try:
        with sync_playwright() as p:
            browser = launch_browser(p)
            for name in names:
                context = None
                try:
                    context, page, dialogs = prepare(browser, f'http://127.0.0.1:{server.server_port}/index.html', timezone_id='America/Sao_Paulo')
                    page.set_default_timeout(5000)
                    evidence = CASES[name](page, dialogs)
                    assert_fixture_requests(context)
                    assert not page.notification_errors, page.notification_errors
                    result = {'case': name, 'result': 'PASS', 'evidence': evidence}
                except Exception as error:
                    result = {'case': name, 'result': 'PRODUCT_FAIL' if isinstance(error, AssertionError) else 'TEST_HARNESS_FAIL', 'evidence': str(error), 'traceback': traceback.format_exc()}
                finally:
                    if context:
                        context.close()
                results.append(result)
                print(json.dumps(result, ensure_ascii=False), flush=True)
            browser.close()
    finally:
        server.shutdown(); server.server_close()
    paths = ['src/js/10-domain/19-personal-agenda.js', 'src/js/00-core/07-workspace-backup.js', 'src/js/30-accounting/01-daily-ledger.js', 'src/js/40-app/07-finalize-session.js', 'tools/calendar_recovery_test.py']
    receipt = {'development_controller': DEVELOPMENT_CONTROLLER, 'source_sha256': {name: hashlib.sha256((ROOT/name).read_bytes()).hexdigest() for name in paths if (ROOT/name).exists()}, 'results': results}
    if args.receipt:
        args.receipt.parent.mkdir(parents=True, exist_ok=True);args.receipt.write_text(json.dumps(receipt, ensure_ascii=False, indent=2)+'\n')
    print(json.dumps(receipt, ensure_ascii=False, indent=2))
    raise SystemExit(0 if results and all(row['result']=='PASS' for row in results) else 1)


if __name__ == '__main__':
    main()
