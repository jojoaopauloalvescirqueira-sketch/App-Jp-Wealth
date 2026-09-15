#!/usr/bin/env python3
"""Forex V11 commands: synthetic Chromium, existing storage/backup and bootstrap.

No economic service is contacted. Failure injection is session-local. Tests
assert actual return values, memory, persisted state, audit and reload behavior;
local editor friction is never treated as approver authentication.
"""
import argparse
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import hashlib
import json
from pathlib import Path
import sys
import threading
import traceback

from playwright.sync_api import sync_playwright
from browser_bootstrap_fixture import install_bootstrap, wait_bootstrap, assert_fixture_requests

ROOT = Path(__file__).resolve().parents[1]
SOURCES = [
    'src/js/00-core/00-forex-policy.js', 'src/js/10-domain/00-forex-engine.js',
    'src/js/10-domain/00-forex-state.js', 'src/js/10-domain/02-risk-calculations.js',
    'src/js/00-core/04-persistence.js', 'src/js/30-accounting/01-daily-ledger.js',
    'build-id.js',
]
SEED = r"""() => {
  window.__onbShown=true;closeModal();window.alert=()=>{};window.confirm=()=>true;
  const instruments=structuredClone(S.instruments);
  S=structuredClone(DEFAULTS);migrate();S.instruments=instruments;
  delete S.forex;
  S.accounts=[{broker:'Sintético',tipo:'MESTRE',perfil:'Base',apelido:'Conta A'},
              {broker:'Sintético',tipo:'SATELITE',perfil:'Base',apelido:'Conta B'}];
  S.params.saldoIni=10000;S.params.saldoAtu=10000;
  S.personalFinance.syntheticUnrelated={value:'initial'};
  S.onboarding.done=true;
  S.phases=[0,1,2,3].map((index)=>({title:'LEGACY '+index,cls:'legacy'+index,faseNome:'LEGACY '+index,
    ddtxt:'historical',alavtxt:'historical',orders:[{id:'L'+index,par:'EURUSD',tipo:'BUY',
      lote:.01,entry:1.1,sl:1,status:'Fechada',result:index+1}]}));
  S.matrix=[{nome:'LEGACY 1',ddmin:0,ddmax:.03,alav:4},{nome:'LEGACY 2',ddmin:.03,ddmax:.07,alav:2},
            {nome:'LEGACY 3',ddmin:.07,ddmax:.12,alav:1},{nome:'LEGACY 4',ddmin:.12,ddmax:.15,alav:.4}];
  S.profiles=[{name:'LEGACY',fator:.66}];
  S.activeOperation={operationId:'synthetic-operation',openedAt:null,maxAccountPhaseReached:null};
  S.operationHistory={schemaVersion:1,records:[{operationId:'archived-synthetic',custom:{keep:true}}]};
  S.transitionLog=[];S.dataGovernance.changeLog=[];
  if(save()!==true)throw Error('Synthetic baseline could not be saved');
  window.__fxSave=save;window.__fxApi=JPWForex.state;
  window.__fxFacts=(index=0,extra={})=>({accountIndex:index,si:10000,equity:9300,currency:'USD',
    netCashflow:0,cashflowAdjustmentRecorded:true,capitalNominal:12000,
    source:'synthetic fixture',observedAt:'2026-01-01T00:00:00Z',...extra});
  window.__fxWrite=(index=0,extra={})=>__fxApi.recordAccountFacts(__fxFacts(index,extra),{reason:'synthetic observation'});
  window.__fxSnapshot=()=>({forex:S.forex===undefined?null:structuredClone(S.forex),
    accounts:structuredClone(S.accounts),phases:structuredClone(S.phases),matrix:structuredClone(S.matrix),
    profiles:structuredClone(S.profiles),activeOperation:structuredClone(S.activeOperation),
    history:structuredClone(S.operationHistory),transitionLog:structuredClone(S.transitionLog),
    log:structuredClone(S.dataGovernance.changeLog),unrelated:structuredClone(S.personalFinance.syntheticUnrelated),
    raw:localStorage.getItem(LSKEY),unknown:jpWealthPersistenceOutcomeIsUnknown()});
  return {build:JP_WEALTH_BUILD_ID,phaseCount:S.phases.length};
}"""


class Quiet(SimpleHTTPRequestHandler):
    def log_message(self, *_):
        pass


def digest_sources(root):
    manifest = json.loads((root/'src/js/manifest.json').read_text())
    paths = sorted(set(SOURCES + ['src/js/manifest.json', 'index.html'] + [row['path'] for row in manifest['files']]))
    return {name: hashlib.sha256((root/name).read_bytes()).hexdigest() for name in paths}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--root', type=Path, default=ROOT)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--case', default='')
    args = parser.parse_args()
    if args.out.exists():
        parser.error('Evidence exists: use a new output path')
    root = args.root.resolve()
    result = {'root': str(root), 'environment': 'Chromium isolated contexts; existing bootstrap fixtures; loopback only',
              'sources_before': digest_sources(root), 'test_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(), 'cases': []}
    server = ThreadingHTTPServer(('127.0.0.1', 0), partial(Quiet, directory=str(root)))
    threading.Thread(target=server.serve_forever, daemon=True).start()
    url = f'http://127.0.0.1:{server.server_port}/index.html'

    def fresh(browser, record):
        context = browser.new_context(viewport={'width': 1440, 'height': 1000}, service_workers='block')
        install_bootstrap(context)
        context.add_init_script('window.__onbShown=true;')
        page = context.new_page()
        page.on('pageerror', lambda error: record['pageerrors'].append(str(error)))
        page.on('console', lambda message: record['console'].append({'type': message.type, 'text': message.text}))
        page.goto(url)
        wait_bootstrap(page)
        page.evaluate('() => {window.alert=()=>{};window.confirm=()=>true;closeModal();}')
        return context, page

    def case(browser, name, callback):
        if args.case and args.case not in name:
            return
        record = {'name': name, 'observations': {}, 'pageerrors': [], 'console': []}
        context = None
        try:
            context, page = fresh(browser, record)
            record['seed'] = page.evaluate(SEED)
            callback(page, record['observations'], browser, record)
            assert_fixture_requests(context)
            assert not record['pageerrors'], record['pageerrors']
            expected = []
            if name.startswith('unknown-no-blind-retry-') or name.startswith('budget-unknown-'):
                expected.append('[persistência] DESFECHO INDETERMINADO')
            if name == 'refusal-retry-quota':
                expected.append('JP Wealth: falha ao gravar o estado no armazenamento local.')
            unexpected = [m for m in record['console'] if m['type']=='error' and not any(prefix in m['text'] for prefix in expected)]
            assert not unexpected, unexpected
            record['expected_console_error_prefixes'] = expected
            record['status'] = 'PASS'
        except Exception as error:
            record.update(status='FAIL', error=str(error), trace=traceback.format_exc())
        finally:
            if context:
                context.close()
            result['cases'].append(record)
            print(name, record['status'], record.get('error', '')[:250], flush=True)

    def reading(page, observations, *_):
        before = page.evaluate('__fxSnapshot()')
        facts = page.evaluate("() => {const a=__fxApi.read(),b=__fxApi.context(),c=__fxApi.editorStatus();render();return {mode:a.metricsStatus,context:b,editor:c};}")
        after = page.evaluate('__fxSnapshot()')
        observations.update(before=before, after=after, facts=facts)
        assert before == after
        assert after['forex'] is None and facts['mode'] == 'NOT_COMPUTABLE'
        assert facts['context']['provenance'] == 'LEGACY_UNRESOLVED'

    def migration(page, observations, *_):
        before = page.evaluate('__fxSnapshot()')
        outcome = page.evaluate("__fxApi.migrateLegacy({reason:'synthetic explicit migration'})")
        after = page.evaluate('__fxSnapshot()')
        observations.update(outcome=outcome, before=before, after=after)
        assert outcome['ok'] is True and outcome['persistido'] is True
        assert len(after['phases']) == 4
        for key in ['history', 'matrix', 'profiles', 'unrelated']:
            assert before[key] == after[key], key
        assert after['forex']['migration']['sourcePhases'] == before['phases']
        assert after['forex']['migration']['sourceParams']['saldoIni'] == 10000
        assert all(p['policyVersion'] == 'LEGACY_UNRESOLVED' for p in after['phases'])
        for previous, current in zip(before['phases'], after['phases']):
            for key, value in previous.items():
                if key != 'orders':
                    assert current[key] == value
            for key, value in previous['orders'][0].items():
                assert current['orders'][0][key] == value
        second = page.evaluate("__fxApi.migrateLegacy({reason:'do not duplicate'})")
        assert second['alreadyMigrated'] is True and second['persistido'] is False
        assert page.evaluate('__fxSnapshot()') == after

    def periods(page, observations, *_):
        assert page.evaluate('__fxWrite()')['ok'] is True
        first = page.evaluate('__fxSnapshot()')
        refusal = page.evaluate('__fxWrite(0,{si:11000,equity:11000})')
        assert refusal['ok'] is False and page.evaluate('__fxSnapshot()') == first
        accepted = page.evaluate('__fxWrite(0,{si:11000,equity:11000,newPeriod:true})')
        after = page.evaluate('__fxSnapshot()')
        key = first['forex']['activeAccountId']
        previous, current = first['forex']['accounts'][key], after['forex']['accounts'][key]
        assert accepted['ok'] is True and previous['periodId'] != current['periodId']
        assert current['previous'] == previous and current['phaseState']['phase'] == 1
        observations.update(refused=refusal, accepted=accepted, previous=previous, current=current)

    def h4_accounts(page, observations, *_):
        got = page.evaluate("""() => {
          const first=__fxWrite(0);const a=S.forex.activeAccountId;
          const second=__fxWrite(1);const b=S.forex.activeAccountId;
          const otherH4=__fxApi.recordH4({ddPercent:5.5,closedAt:'2026-01-01T04:00:00Z',source:'synthetic B'},{reason:'synthetic B close'});
          const back=__fxWrite(0,{equity:9450,observedAt:'2026-01-01T08:00:00Z'});
          const held=structuredClone(S.forex.accounts[a].phaseState);
          const ownH4=__fxApi.recordH4({ddPercent:5.5,closedAt:'2026-01-01T04:00:00Z',source:'synthetic A'},{reason:'synthetic A close'});
          const next=__fxWrite(0,{equity:9450,observedAt:'2026-01-01T12:00:00Z'});
          const confirmed=structuredClone(S.forex.accounts[a].phaseState);
          const duplicate=__fxApi.recordH4({ddPercent:5.5,closedAt:'2026-01-01T04:00:00Z',source:'synthetic A'},{reason:'duplicate'});
          return {first,second,otherH4,back,held,ownH4,next,confirmed,duplicate,a,b,closes:S.forex.h4Closes};
        }""")
        observations.update(got)
        for key in ['first', 'second', 'otherH4', 'back', 'ownH4', 'next']:
            assert got[key]['ok'] is True, (key, got[key])
        assert got['held']['phase'] == 3 and got['confirmed']['phase'] == 2
        assert got['a'] != got['b'] and len(got['closes']) == 2 and got['duplicate']['ok'] is False

    def h4_missing(page, observations, *_):
        before = page.evaluate('__fxSnapshot()')
        outcome = page.evaluate("__fxApi.recordH4({ddPercent:1,closedAt:'2026-01-01T04:00:00Z',source:'synthetic'},{reason:'no account'})")
        observations['outcome'] = outcome
        assert outcome['ok'] is False and page.evaluate('__fxSnapshot()') == before

    def refused(kind):
        def run(page, observations, *_):
            before = page.evaluate('__fxSnapshot()')
            page.evaluate("""kind => {
              window.__fxSaveCalls=0;
              if(kind==='quota'){window.__fxNativeSet=Storage.prototype.setItem;Storage.prototype.setItem=function(key,value){if(key===LSKEY)throw new DOMException('synthetic quota','QuotaExceededError');return __fxNativeSet.call(this,key,value);};}
              if(kind==='blocked')blockJPWealthPersistence();
              if(kind==='recovery')jpWealthLoadRecovery.active=true;
              save=function(){__fxSaveCalls++;if(kind==='false'){S.personalFinance.syntheticUnrelated={value:'legitimate unrelated change'};return false;}return __fxSave();};
            }""", kind)
            outcome = page.evaluate('__fxWrite()')
            after = page.evaluate('__fxSnapshot()')
            assert outcome['ok'] is False and outcome['persistido'] is False
            for key in ['forex', 'accounts', 'phases', 'matrix', 'profiles', 'history', 'log', 'raw']:
                assert after[key] == before[key], key
            if kind == 'false':
                assert after['unrelated']['value'] == 'legitimate unrelated change'
            page.evaluate("""() => {
              if(window.__fxNativeSet)Storage.prototype.setItem=__fxNativeSet;
              save=__fxSave;if(jpWealthLoadRecovery.active)jpWealthLoadRecovery.active=false;
              if(jpWealthPersistenceIsBlocked())resumeJPWealthPersistence();
              S.personalFinance.syntheticUnrelated.savedAfterRefusal=true;
              if(save()!==true)throw Error('unrelated write refused');
            }""")
            independent = page.evaluate('JSON.parse(localStorage.getItem(LSKEY))')
            assert 'forex' not in independent
            retry = page.evaluate('__fxWrite()')
            committed = page.evaluate('__fxSnapshot()')
            assert retry['ok'] is True and len(committed['forex']['accounts']) == 1
            assert len(committed['forex']['auditLog']) == 1
            observations.update(refused=outcome, retry=retry, before=before, after=after, committed=committed)
            page.reload();wait_bootstrap(page)
            reloaded = page.evaluate('structuredClone(S.forex)')
            assert reloaded == committed['forex']
            observations['reloaded'] = reloaded
        return run

    def uncertain(kind):
        def run(page, observations, *_):
            page.evaluate("""kind => {window.__fxSaveCalls=0;save=function(){__fxSaveCalls++;
              if(kind==='throw-before')throw Error('synthetic before save');
              if(kind==='throw-after'){__fxSave();throw Error('synthetic after save');}
              return undefined;
            };}""", kind)
            outcome = page.evaluate('__fxWrite()')
            after = page.evaluate('__fxSnapshot()')
            retry = page.evaluate('__fxWrite()')
            assert outcome['ok'] is False and outcome['persistido'] is None and after['unknown'] is True
            assert retry['ok'] is False and retry['persistido'] is None
            assert page.evaluate('__fxSaveCalls') == 1
            assert len(after['forex']['auditLog']) == 1
            assert page.evaluate('__fxSnapshot()') == after
            observations.update(outcome=outcome, after=after, refusedRetry=retry, saveCalls=1,
                                note='Attempted in-memory candidate preserved under existing UNKNOWN barrier; not a confirmed action')
        return run

    def grid_market(page, observations, *_):
        assert page.evaluate('__fxWrite()')['ok'] is True
        got = page.evaluate("""() => {
          const market=__fxApi.recordMarket({atrShort:0,atrLong:1,source:'synthetic',observedAt:'2026-01-01T04:00:00Z'},{reason:'synthetic market'});
          const grid=__fxApi.recordGrid(2,{reason:'declared synthetic grid'});
          const before=JSON.stringify(S.forex);
          const invalid=__fxApi.recordGrid(7,{reason:'invalid'});
          return {market,grid,invalid,unchanged:before===JSON.stringify(S.forex),model:__fxApi.read(),transitionLog:S.transitionLog};
        }""")
        observations.update(got)
        assert got['market']['ok'] is True and got['grid']['ok'] is True and got['invalid']['ok'] is False
        assert got['unchanged'] is True and got['model']['activeGridPhase']['value'] == 2
        assert got['model']['accountPhase']['value'] == 3
        assert got['model']['metrics']['vrm']['value'] == 0
        assert got['model']['executionEligibility']['status'] == 'BLOCKED'
        assert len(got['transitionLog']) == 1

    def backup(page, observations, browser, record):
        assert page.evaluate("__fxApi.migrateLegacy({reason:'synthetic migration'})")['ok'] is True
        assert page.evaluate('__fxWrite()')['ok'] is True
        assert page.evaluate("__fxApi.recordReserves({sixMonthExpenseAmount:600,determinationRecorded:true,expensesApproved:true,expensePeriod:'next six months',determinationReference:'synthetic determination',source:'synthetic source',fcrConstituted:2640,feoConstituted:600},{reason:'synthetic reserves'})")['ok'] is True
        expected = page.evaluate('structuredClone(S.forex)')
        account = expected['accounts'][expected['activeAccountId']]
        assert expected['reserves']['periodId'] == account['periodId']
        assert expected['reserves']['currency'] == account['currency']
        payload_text = page.evaluate("async()=>await dgBuildBackupBlob(7,'synthetic-v11.json','2026-01-01T12:00:00Z').text()")
        payload = json.loads(payload_text)
        assert payload['tipo'] == 'jpwealth_full_backup' and payload['state']['forex'] == expected
        target, restored = fresh(browser, record)
        try:
            assert restored.evaluate("!S.forex || !S.forex.activeAccountId")
            restored.evaluate("text=>importFullBackupFile(new File([text],'synthetic-v11.json',{type:'application/json'}))", payload_text)
            restored.wait_for_function('id=>S.forex&&S.forex.activeAccountId===id', arg=expected['activeAccountId'])
            assert restored.evaluate('structuredClone(S.forex)') == expected
            persisted = restored.evaluate('JSON.parse(localStorage.getItem(LSKEY)).forex')
            assert persisted == expected
            restored.reload();wait_bootstrap(restored)
            assert restored.evaluate('structuredClone(S.forex)') == expected
            assert_fixture_requests(target)
            observations.update(envelope={key:value for key,value in payload.items() if key != 'state'},
                                exported_sha256=hashlib.sha256(payload_text.encode()).hexdigest(),
                                forex=expected, persisted=persisted, actualImportAndReload=True)
        finally:
            target.close()

    def editor(page, observations, *_):
        before = page.evaluate('__fxSnapshot()')
        got = page.evaluate("""async()=>{
          const phrase='synthetic-local-editor-fixture';
          const configured=await __fxApi.configureEditor(phrase);
          const wrong=await __fxApi.unlockEditor('synthetic-wrong-fixture','Synthetic editor');
          const correct=await __fxApi.unlockEditor(phrase,'Synthetic editor');
          const unlocked=__fxApi.editorStatus();const realNow=Date.now;
          let expired;try{Date.now=()=>unlocked.expiresAt+1;expired=__fxApi.editorStatus();}finally{Date.now=realNow;}
          return {configured,wrong,correct,unlocked,expired};
        }""")
        observations.update(got)
        assert got['configured']['ok'] and not got['wrong']['ok'] and got['correct']['ok']
        assert got['unlocked']['unlocked'] and not got['expired']['unlocked']
        assert got['unlocked']['activationAvailable'] is False
        assert page.evaluate('__fxSnapshot()') == before
        page.reload();wait_bootstrap(page)
        assert page.evaluate('JPWForex.state.editorStatus().configured') is False

    def editor_race(kind):
        def run(page, observations, *_):
            got = page.evaluate("""async(kind)=>{
              const phrase='synthetic-local-editor-fixture';
              if(kind!=='configure-clear')await __fxApi.configureEditor(phrase);
              const real=crypto.subtle.deriveBits.bind(crypto.subtle);
              let entered,release;const started=new Promise(resolve=>entered=resolve),gate=new Promise(resolve=>release=resolve);
              crypto.subtle.deriveBits=function(...args){const computation=real(...args);entered();return Promise.all([computation,gate]).then(result=>result[0]);};
              let outcome;
              try{
                const operation=kind==='configure-clear'?__fxApi.configureEditor(phrase):__fxApi.unlockEditor(phrase,'Synthetic editor');
                await started;if(kind==='unlock-lock')__fxApi.lockEditor();else __fxApi.clearEditor();
                release();outcome=await operation;
              }finally{release();crypto.subtle.deriveBits=real;}
              return {outcome,status:__fxApi.editorStatus()};
            }""", kind)
            observations.update(got)
            assert got['outcome']['ok'] is False and got['status']['unlocked'] is False
            if kind != 'unlock-lock':
                assert got['status']['configured'] is False
        return run

    def proposal(page, observations, *_):
        got = page.evaluate("""async()=>{
          const version=JPWForex.policy.version,old=JPWForex.policy.get('P-03').value;
          const input={id:'P-03',value:24,reason:'Synthetic scenario only',source:'synthetic decision'};
          const locked=__fxApi.proposeParameterChange(input);
          await __fxApi.configureEditor('synthetic-local-editor-fixture');
          await __fxApi.unlockEditor('synthetic-local-editor-fixture','Synthetic editor');
          const proposed=__fxApi.proposeParameterChange(input);
          const before=__fxSnapshot();const activation=__fxApi.activateProposal();const after=__fxSnapshot();
          return {locked,proposed,before,activation,after,version,newVersion:JPWForex.policy.version,old,current:JPWForex.policy.get('P-03').value};
        }""")
        observations.update(got)
        assert got['locked']['ok'] is False and got['proposed']['ok'] is True
        assert got['activation']['status'] == 'BLOCKED' and got['activation']['persistido'] is False
        assert got['before'] == got['after'] and got['version'] == got['newVersion'] and got['old'] == got['current'] == 22
        assert len(got['after']['forex']['proposals']) == 1 and got['after']['forex']['proposals'][0]['active'] is False
        assert 'synthetic-local-editor-fixture' not in got['after']['raw']

    # Focal counterexamples found after the original 19 cases. These oracles
    # are fixed before the state boundary correction and preserved afterward.
    def incompatible(kind):
        def run(page, observations, *_):
            got = page.evaluate("""kind=>{
              __fxWrite();
              if(kind==='h4-shape')S.forex.h4Closes={};
              if(kind==='policy-version')S.forex.policyVersion='SYNTHETIC-FUTURE-POLICY';
              if(kind==='schema-version')S.forex.schemaVersion=999;
              const before=JSON.stringify(S);let read,exception=null;
              try{read=__fxApi.read();}catch(error){exception=String(error);}
              const context=__fxApi.recordContext();
              const supported=__fxApi.supported();const mutation=__fxWrite();
              return {supported,exception,context,canRecord:read&&read.canRecord,mutation,unchanged:before===JSON.stringify(S)};
            }""", kind)
            observations.update(got)
            assert got['supported'] is False
            assert got['exception'] is None and got['canRecord'] is False
            assert got['context']['status'] == 'NOT_COMPUTABLE'
            assert got['context']['provenance'] != 'RECORDED'
            assert got['context']['policyVersion'] is None
            assert got['context']['accountInputs'] is None
            assert got['mutation']['ok'] is False and got['unchanged'] is True
        return run

    def currency_period(page, observations, *_):
        got = page.evaluate("""()=>{
          __fxWrite();__fxApi.recordReserves({fcrConstituted:2640,source:'synthetic reserve'},{reason:'initial reserve currency'});
          const initial=__fxSnapshot();
          const refused=__fxWrite(0,{currency:'EUR',usdToAccountRate:.9});
          const afterRefusal=__fxSnapshot();
          const explicit=__fxWrite(0,{currency:'EUR',usdToAccountRate:.9,newPeriod:true});
          return {initial,refused,afterRefusal,explicit,after:__fxSnapshot()};
        }""")
        observations.update(got)
        assert got['refused']['ok'] is False and got['initial'] == got['afterRefusal']
        assert got['explicit']['ok'] is True
        key = got['initial']['forex']['activeAccountId']
        previous = got['initial']['forex']['accounts'][key]
        current = got['after']['forex']['accounts'][key]
        assert current['periodId'] != previous['periodId'] and current['previous'] == previous
        assert current['currency'] == 'EUR' and previous['currency'] == 'USD'
        assert got['after']['phases'] == got['initial']['phases']
        assert got['after']['forex']['reserves'] == got['initial']['forex']['reserves']
        assert got['after']['forex']['reserves']['currency'] == previous['currency']
        assert got['after']['forex']['reserves']['periodId'] == previous['periodId']

    def retroactive(page, observations, *_):
        got = page.evaluate("""()=>{
          __fxWrite(0,{observedAt:'2026-01-01T08:00:00Z'});
          __fxApi.recordH4({ddPercent:5.5,closedAt:'2026-01-01T12:00:00Z',source:'synthetic'},{reason:'actual close after observation'});
          const before=__fxSnapshot();
          const result=__fxWrite(0,{equity:9450,observedAt:'2026-01-01T04:00:00Z'});
          return {before,result,after:__fxSnapshot()};
        }""")
        observations.update(got)
        assert got['result']['ok'] is False and got['result']['persistido'] is False
        assert got['before'] == got['after']

    def h4_observation_bound(page, observations, *_):
        got = page.evaluate("""()=>{
          __fxWrite(0,{observedAt:'2026-01-01T00:00:00Z'});
          __fxApi.recordH4({ddPercent:5.5,closedAt:'2026-01-01T08:00:00Z',source:'synthetic'},{reason:'actual close'});
          __fxWrite(0,{equity:9450,observedAt:'2026-01-01T04:00:00Z'});
          const key=S.forex.activeAccountId;
          return {fact:S.forex.accounts[key],read:__fxApi.read().accountPhase,closes:S.forex.h4Closes};
        }""")
        observations.update(got)
        assert got['fact']['phaseState']['phase'] == 3
        assert got['read']['value'] == 3

    def h4_period_bound(page, observations, *_):
        got = page.evaluate("""()=>{
          __fxWrite(0,{observedAt:'2026-01-01T00:00:00Z'});const key=S.forex.activeAccountId,firstPeriod=S.forex.accounts[key].periodId;
          __fxApi.recordH4({ddPercent:5.5,closedAt:'2026-01-01T04:00:00Z',source:'synthetic'},{reason:'period A close'});
          __fxWrite(0,{newPeriod:true,observedAt:'2026-01-01T08:00:00Z'});
          const newStart=structuredClone(S.forex.accounts[key]);
          __fxWrite(0,{equity:9450,observedAt:'2026-01-01T12:00:00Z'});
          const beforeLegacy=__fxApi.read().accountPhase;
          S.forex.h4Closes.push({accountId:key,timeframe:'H4',ddPercent:5.5,closedAt:'2026-01-01T12:00:00Z',source:'legacy without period'});
          return {firstPeriod,newStart,fact:S.forex.accounts[key],beforeLegacy,afterLegacy:__fxApi.read().accountPhase,closes:S.forex.h4Closes};
        }""")
        observations.update(got)
        assert got['closes'][0]['periodId'] == got['firstPeriod']
        assert got['newStart']['periodId'] != got['firstPeriod']
        assert got['newStart']['phaseState']['since'] == got['newStart']['observedAt']
        assert got['fact']['phaseState']['phase'] == 3 and got['beforeLegacy']['value'] == 3
        assert got['afterLegacy']['value'] == 3

    def explicit_context(page, observations, *_):
        got = page.evaluate("""()=>{
          __fxWrite();const a=S.forex.activeAccountId,periodA=S.forex.accounts[a].periodId;
          const original=structuredClone(S.forex.accounts[a]);
          __fxWrite(0,{newPeriod:true,si:12000,equity:12000,observedAt:'2026-01-02T00:00:00Z'});
          __fxWrite(1,{si:2000,equity:2000});const b=S.forex.activeAccountId;
          const before=JSON.stringify(S);
          const target=__fxApi.recordContext({accountId:a,periodId:periodA});
          const unknown=__fxApi.recordContext({accountId:'unknown',periodId:'unknown'});
          const missing=__fxApi.recordContext({accountId:undefined,periodId:undefined});
          const current=__fxApi.recordContext();
          return {a,b,periodA,original,target,unknown,missing,current,unchanged:before===JSON.stringify(S)};
        }""")
        observations.update(got)
        assert got['target']['accountId'] == got['a'] and got['target']['periodId'] == got['periodA']
        assert got['target']['accountInputs'] == got['original']
        assert got['current']['accountId'] == got['b'] and got['unchanged'] is True
        for name in ['unknown', 'missing']:
            assert got[name]['status'] == 'NOT_COMPUTABLE' and got[name]['accountInputs'] is None

    def budget_seed(page, existing=False):
        page.evaluate("""existing=>{
          __fxWrite();const c=__fxApi.recordContext();
          S.phases=__fxApi.newOperationPhases();S.activeOperation=existing?{operationId:'budget-op',recordContext:structuredClone(c)}:null;
          window.__budgetScope={accountId:c.accountId,periodId:c.periodId,currency:c.accountInputs.currency,operationId:existing?'budget-op':null};
          window.__budgetInput=extra=>({...__budgetScope,amount:100,source:'synthetic budget source',declaredBy:'Synthetic operator',declaredAt:'2026-01-01T01:00:00Z',...extra});
          window.__budgetRecord=extra=>__fxApi.recordOperationBudget(__budgetInput(extra||{}),{reason:'synthetic budget declaration'});
          if(save()!==true)throw Error('Budget fixture could not be saved');
        }""", existing)

    def budget_read(page, observations, *_):
        budget_seed(page)
        got = page.evaluate("""()=>{const before=__fxSnapshot();const a=__fxApi.budgetSnapshot(__budgetScope);
          const b=__fxApi.budgetSnapshot({});return {before,after:__fxSnapshot(),a,b};}""")
        assert got['before'] == got['after']
        assert got['a']['status'] == 'NOT_COMPUTABLE' and got['a']['value'] is None
        assert got['b']['status'] == 'NOT_COMPUTABLE'
        assert 'operationBudgets' not in got['after']['forex']
        observations.update(got)

    def budget_declaration(page, observations, *_):
        budget_seed(page)
        got = page.evaluate("""()=>{const first=__budgetRecord({amount:0});const snap=__fxApi.budgetSnapshot(__budgetScope);
          const before=__fxSnapshot();const duplicate=__budgetRecord({amount:99});return {first,snap,duplicate,unchanged:JSON.stringify(before)===JSON.stringify(__fxSnapshot()),raw:S.forex.operationBudgets};}""")
        assert got['first']['ok'] is True and got['snap']['value'] == 0
        assert got['snap']['status'] == 'OK' and got['snap']['executionEligibility'] == 'BLOCKED'
        assert got['snap']['declaration']['operationId'] is None
        v = got['snap']['declaration']['versions'][-1]
        assert v['recordingTiming'] == 'BEFORE_FIRST_SOFTWARE_RECORD' and v['doesNotProveExternalPreExecution'] is True
        assert v['declaredBy'] == 'Synthetic operator' and v['source'] == 'synthetic budget source'
        assert v['policySnapshot']['version'] == v['policyVersion']
        assert got['duplicate']['ok'] is False and got['unchanged'] is True and len(got['raw']) == 1
        observations.update(got)

    def budget_association(page, observations, *_):
        budget_seed(page)
        got = page.evaluate("""()=>{__budgetRecord();const prior=__fxApi.budgetSnapshot(__budgetScope);let attached;
          const first=__fxApi.mutate('synthetic-first-fact','synthetic association',['activeOperation'],f=>{
            S.activeOperation={operationId:'new-op',recordContext:__fxApi.recordContext()};
            attached=__fxApi.attachOperationBudget(f,{...__budgetScope,operationId:'new-op',firstRecordedAt:new Date().toISOString()});
          });
          const scoped=__fxApi.budgetSnapshot({...__budgetScope,operationId:'new-op'});const frozen=JSON.stringify(scoped);
          __fxWrite(1);const historical=__fxApi.budgetSnapshot({...__budgetScope,operationId:'new-op'});
          const before=JSON.stringify(S.forex);const other=__fxApi.attachOperationBudget(S.forex,{...__budgetScope,operationId:'other-op',firstRecordedAt:new Date().toISOString()});
          return {prior,first,attached,scoped,historical,other,same:frozen===JSON.stringify(historical),unchanged:before===JSON.stringify(S.forex)};
        }""")
        assert got['first']['ok'] is True and got['attached']['status'] == 'OK'
        assert got['scoped']['declaration']['operationId'] == 'new-op'
        assert got['scoped']['declaration']['association']['doesNotProveExternalPreExecution'] is True
        assert got['same'] is True and got['other']['status'] == 'NOT_COMPUTABLE' and got['unchanged'] is True
        assert got['prior']['declaration']['operationId'] is None
        observations.update(got)

    def budget_retroactive(page, observations, *_):
        budget_seed(page, existing=True)
        got = page.evaluate("""()=>{const a=__budgetRecord();const snap=__fxApi.budgetSnapshot(__budgetScope);
          const before=__fxSnapshot();const invalid=__budgetRecord({accountId:'unknown',periodId:'unknown',operationId:'other'});
          return {a,snap,invalid,unchanged:JSON.stringify(before)===JSON.stringify(__fxSnapshot())};}""")
        assert got['a']['ok'] is True
        assert got['snap']['declaration']['versions'][0]['recordingTiming'] == 'RETROSPECTIVE_DECLARATION'
        assert got['invalid']['ok'] is False and got['unchanged'] is True
        observations.update(got)

    def budget_reduction(page, observations, *_):
        budget_seed(page, existing=True)
        got = page.evaluate("""()=>{
          S.phases[0].orders=[{orderId:'budget-loss',operationId:'budget-op',...__budgetScope,status:'Fechada',result:-20,costs:-5,costBasis:'SEPARATE_FROM_RESULT'}];save();
          __budgetRecord();const original=__fxApi.budgetSnapshot(__budgetScope);const budgetId=original.declaration.id;
          const increase=__budgetRecord({budgetId,amount:101});
          const decrease=__budgetRecord({budgetId,amount:25,committedRisk:0});const after=__fxApi.budgetSnapshot(__budgetScope);
          const before=__fxSnapshot();const under=__budgetRecord({budgetId,amount:24,committedRisk:0});const reexpand=__budgetRecord({budgetId,amount:50});
          return {original,increase,decrease,after,under,reexpand,unchanged:JSON.stringify(before)===JSON.stringify(__fxSnapshot())};
        }""")
        assert got['increase']['ok'] is False and got['decrease']['ok'] is True
        assert got['after']['value'] == 25 and len(got['after']['declaration']['versions']) == 2
        assert got['after']['declaration']['versions'][1]['committedRiskAtReduction']['value'] == 25
        assert got['after']['declaration']['versions'][0] == got['original']['declaration']['versions'][0]
        assert got['under']['ok'] is False and got['reexpand']['ok'] is False and got['unchanged'] is True
        observations.update(got)

    def budget_missing_rc(page, observations, *_):
        budget_seed(page, existing=True)
        got = page.evaluate("""()=>{S.phases[0].orders=[{orderId:'budget-cost-unknown',operationId:'budget-op',...__budgetScope,status:'Fechada',result:-20}];save();
          __budgetRecord();const budgetId=__fxApi.budgetSnapshot(__budgetScope).declaration.id;const before=__fxSnapshot();
          const r=__budgetRecord({budgetId,amount:25,committedRisk:{status:'OK',value:0}});
          return {r,unchanged:JSON.stringify(before)===JSON.stringify(__fxSnapshot())};}""")
        assert got['r']['ok'] is False and got['unchanged'] is True
        assert 'comprometido' in got['r']['error'].lower()
        observations.update(got)

    def budget_refusal(page, observations, *_):
        budget_seed(page)
        got = page.evaluate("""()=>{const before=__fxSnapshot();save=()=>{S.personalFinance.syntheticUnrelated.value='legitimate-other-flow';return false;};
          const refused=__budgetRecord();const after=__fxSnapshot();save=__fxSave;const retry=__budgetRecord();return {before,refused,after,retry,final:__fxSnapshot()};}""")
        assert got['refused']['ok'] is False and got['refused']['persistido'] is False
        assert got['before']['forex'] == got['after']['forex'] and got['before']['log'] == got['after']['log']
        assert got['after']['unrelated']['value'] == 'legitimate-other-flow'
        assert got['retry']['ok'] is True and len(got['final']['forex']['operationBudgets']) == 1
        page.reload();wait_bootstrap(page)
        assert page.evaluate('structuredClone(S.forex)') == got['final']['forex']
        observations.update(got)

    def budget_unknown(mode):
        def run(page, observations, *_):
            budget_seed(page)
            got = page.evaluate("""mode=>{let calls=0;save=()=>{calls++;if(mode==='throw-before')throw Error('synthetic budget failure');if(mode==='throw-after'){__fxSave();throw Error('synthetic budget acknowledgement failure');}return undefined;};
              const r=__budgetRecord(),first=__fxSnapshot(),retry=__budgetRecord();return {r,first,retry,calls,after:__fxSnapshot()};}""", mode)
            assert got['r']['persistido'] is None and got['r']['ok'] is False
            assert got['retry']['persistido'] is None and got['calls'] == 1
            assert got['first'] == got['after'] and got['after']['unknown'] is True
            observations.update(got)
        return run

    def budget_invalid(page, observations, *_):
        budget_seed(page)
        got = page.evaluate("""()=>{const before=__fxSnapshot();const rows=[{amount:-1},{amount:NaN},{amount:'100'},{source:''},{declaredBy:''},{declaredAt:'invalid'},{currency:'EUR'},{operationId:'not-existing'},{accountId:null},{periodId:null}].map(v=>__budgetRecord(v));
          return {rows,unchanged:JSON.stringify(before)===JSON.stringify(__fxSnapshot())};}""")
        assert all(r['ok'] is False for r in got['rows']) and got['unchanged'] is True
        observations.update(got)

    def budget_malformed(page, observations, *_):
        budget_seed(page)
        got = page.evaluate("""()=>{S.forex.operationBudgets={};const before=JSON.stringify(S);
          return {supported:__fxApi.supported(),snap:__fxApi.budgetSnapshot(__budgetScope),record:__budgetRecord(),unchanged:before===JSON.stringify(S)};}""")
        assert got['supported'] is False and got['snap']['status'] == 'NOT_COMPUTABLE'
        assert got['record']['ok'] is False and got['unchanged'] is True
        observations.update(got)

    def budget_backup(page, observations, browser, record):
        budget_seed(page)
        assert page.evaluate('__budgetRecord()')['ok'] is True
        expected = page.evaluate('structuredClone(S.forex)')
        payload = page.evaluate("async()=>await dgBuildBackupBlob(7,'synthetic-budget.json','2026-01-01T12:00:00Z').text()")
        target, restored = fresh(browser, record)
        try:
            restored.evaluate("text=>importFullBackupFile(new File([text],'synthetic-budget.json',{type:'application/json'}))", payload)
            restored.wait_for_function('id=>S.forex&&S.forex.activeAccountId===id', arg=expected['activeAccountId'])
            assert restored.evaluate('structuredClone(S.forex)') == expected
            restored.reload();wait_bootstrap(restored)
            assert restored.evaluate('structuredClone(S.forex)') == expected
            assert_fixture_requests(target)
            observations.update(expected=expected, payload_sha256=hashlib.sha256(payload.encode()).hexdigest(), actualImportAndReload=True)
        finally:
            target.close()

    def budget_imported_mismatch(page, observations, *_):
        budget_seed(page, existing=True)
        got = page.evaluate("""()=>{__budgetRecord();const row=S.forex.operationBudgets[0];row.currency='EUR';const before=JSON.stringify(S);
          const currency=__budgetRecord({budgetId:row.id,amount:50});const currencyPreserved=before===JSON.stringify(S);
          S.forex.operationBudgets[0].currency='USD';const v=structuredClone(S.forex.operationBudgets[0].versions[0]);v.version=2;v.amount=200;S.forex.operationBudgets[0].versions.push(v);
          const malformedBefore=JSON.stringify(S);const supported=__fxApi.supported(),snapshot=__fxApi.budgetSnapshot(__budgetScope);
          return {currency,currencyPreserved,supported,snapshot,malformedPreserved:malformedBefore===JSON.stringify(S)};
        }""")
        assert got['currency']['ok'] is False and got['currencyPreserved'] is True
        assert got['supported'] is False and got['snapshot']['status'] == 'NOT_COMPUTABLE' and got['malformedPreserved'] is True
        observations.update(got)

    try:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch()
            case(browser, 'read-render-no-implicit-write', reading)
            case(browser, 'explicit-legacy-migration-preserves-four-phases-history', migration)
            case(browser, 'new-SI-requires-explicit-period', periods)
            case(browser, 'H4-account-isolation-and-actual-close', h4_accounts)
            case(browser, 'H4-rejects-missing-account', h4_missing)
            for mode in ['false', 'quota', 'blocked', 'recovery']:
                case(browser, 'refusal-retry-'+mode, refused(mode))
            for mode in ['undefined', 'throw-before', 'throw-after']:
                case(browser, 'unknown-no-blind-retry-'+mode, uncertain(mode))
            case(browser, 'grid-market-separate-from-account-phase', grid_market)
            case(browser, 'full-backup-import-fresh-context-reload', backup)
            case(browser, 'editor-RAM-wrong-phrase-expiry-reload', editor)
            for mode in ['configure-clear', 'unlock-clear', 'unlock-lock']:
                case(browser, 'editor-race-'+mode, editor_race(mode))
            case(browser, 'proposal-cannot-activate-normative-policy', proposal)
            for mode in ['h4-shape', 'policy-version', 'schema-version']:
                case(browser, 'revision2-incompatible-'+mode, incompatible(mode))
            case(browser, 'revision2-currency-requires-explicit-period', currency_period)
            case(browser, 'revision2-retroactive-observation-refused', retroactive)
            case(browser, 'revision2-H4-bounded-by-observation', h4_observation_bound)
            case(browser, 'revision2-H4-bounded-by-period', h4_period_bound)
            case(browser, 'revision2-explicit-context-no-selected-fallback', explicit_context)
            case(browser, 'budget-read-no-write', budget_read)
            case(browser, 'budget-declaration-zero-and-duplicate', budget_declaration)
            case(browser, 'budget-association-once-and-scoped-snapshot', budget_association)
            case(browser, 'budget-retrospective-not-external-preexecution', budget_retroactive)
            case(browser, 'budget-reduction-RC-known-and-no-increase', budget_reduction)
            case(browser, 'budget-reduction-RC-unknown-no-zero', budget_missing_rc)
            case(browser, 'budget-refusal-own-rollback-and-explicit-retry', budget_refusal)
            for mode in ['undefined', 'throw-before', 'throw-after']:
                case(browser, 'budget-unknown-'+mode, budget_unknown(mode))
            case(browser, 'budget-invalid-inputs-no-write', budget_invalid)
            case(browser, 'budget-malformed-extension-preserved', budget_malformed)
            case(browser, 'budget-backup-import-reload', budget_backup)
            case(browser, 'budget-imported-currency-or-version-drift', budget_imported_mismatch)
            browser.close()
    except Exception as error:
        result['environment_error'] = str(error)
        result['trace'] = traceback.format_exc()
    finally:
        server.shutdown();server.server_close()
        result['sources_after'] = digest_sources(root)
        result['source_unchanged'] = result['sources_before'] == result['sources_after']
        result['counts'] = {'total': len(result['cases']), 'passed': sum(r['status']=='PASS' for r in result['cases']),
                            'failed': sum(r['status']!='PASS' for r in result['cases'])}
        result['result'] = 'PASS' if result['cases'] and not result['counts']['failed'] and result['source_unchanged'] and not result.get('environment_error') else 'FAIL'
        with args.out.open('x') as output:
            output.write(json.dumps(result, ensure_ascii=False, indent=2)+'\n')
        print(json.dumps({'result':result['result'],'counts':result['counts'],'source_unchanged':result['source_unchanged']},ensure_ascii=False))
    return 0 if result['result']=='PASS' else 1


if __name__ == '__main__':
    sys.exit(main())
