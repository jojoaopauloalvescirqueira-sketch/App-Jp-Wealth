#!/usr/bin/env python3
"""Forex: contrato de confirmação, recusa e desfecho desconhecido.

Oráculos fixados antes do patch (CHG-FUNCTIONAL-RELIABILITY-20260911).
App real servido da --root, Chromium isolado e fixtures nominais existentes.
Não corrige nem classifica reservas como regra aprovada: caracteriza a discrepância.
"""
import argparse
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import hashlib
import json
from pathlib import Path
import threading
import traceback
from playwright.sync_api import sync_playwright
from browser_bootstrap_fixture import install_bootstrap, wait_bootstrap, assert_fixture_requests

SOURCE_PATHS = [
    'src/js/30-accounting/01-daily-ledger.js',
    'src/js/30-accounting/04-patrimonial-simulation.js',
    'src/js/30-accounting/05-fx-planning/03-fx-state.js',
    'src/js/30-accounting/05-fx-planning/05-fx-ui.js',
    'src/js/00-core/04-persistence.js',
]

SEED = """() => {
  window.__onbShown=true; closeModal();
  window.__alerts=[]; window.alert=t=>window.__alerts.push(String(t));
  window.confirm=()=>true;
  // Mantém os instrumentos da fixture econômica já concluída; o reset de
  // domínio não deve ressuscitar preços default anteriores ao bootstrap.
  const bootInstruments=structuredClone(S.instruments);
  S=structuredClone(DEFAULTS); migrate(); S.instruments=bootInstruments;
  S.onboarding.done=true;
  S.params.saldoIni=10000; S.params.saldoAtu=10000;
  S.ledger=[];
  S.fxPlanning.plan=fxCreatePlan({name:'Plano sintético', now:'2026-01-01T12:00:00Z', assumptions:{
    startMonth:'2026-01',horizonMonths:12,initialBalanceUsd:1000,
    defaultMonthlyReturn:0.01,projectedFxRate:5}});
  S.fxPlanning.plan.extensaoSintetica={preservar:true};
  S.fxPlanning.auditLog=Array.from({length:400},(_,i)=>({id:'fx-old-'+i,ts:'2025-01-01T00:00:00Z',type:'HISTORICAL',month:null,detail:''}));
  S.dataGovernance.changeLog=Array.from({length:400},(_,i)=>({id:'dg-old-'+i,ts:'2025-01-01T00:00:00Z',entity:'synthetic',action:'historical',recordId:'',label:''}));
  if(save()!==true) throw new Error('seed não gravou');
  window.__saveReal=save;
  window.__snap=()=>({fx:JSON.stringify(S.fxPlanning),ledger:JSON.stringify(S.ledger),
    saldo:S.params.saldoAtu,log:JSON.stringify(S.dataGovernance.changeLog),raw:localStorage.getItem(LSKEY),
    unknown:jpWealthPersistenceOutcomeIsUnknown(),recovered:document.getElementById('persistenceAlert')?.classList.contains('is-recovered'),saved:document.getElementById('savedTag').classList.contains('show')});
  window.__act=(name)=>{
    const api=JPWFx.state;
    if(name==='create') return api.fxPlanCreate({name:'Novo sintético',assumptions:{startMonth:'2026-01',horizonMonths:12,initialBalanceUsd:1000,defaultMonthlyReturn:0.01,projectedFxRate:5}});
    if(name==='delete') return api.fxPlanDelete();
    if(name==='revise') return api.fxPlanReviseAssumptions({...S.fxPlanning.plan.current,defaultMonthlyReturn:0.02},'revisão sintética');
    if(name==='actual'||name==='edit') return api.fxPlanRecordActual('2026-01',{inputType:'usd',profitUsd:10,valuationFxRate:5,notes:'sintético'});
    if(name==='add') return api.fxPlanAddContribution({month:'2026-01',source:'personal',originalCurrency:'USD',originalAmount:25,acquisitionFxRate:null});
    if(name==='remove') return api.fxPlanRemoveContribution(S.fxPlanning.plan.contributions[0].id);
    throw new Error('ato desconhecido');
  };
  window.__prepare=(name)=>{
    if(name==='create') S.fxPlanning.plan=null;
    if(name==='edit') S.fxPlanning.plan.actuals['2026-01']={inputType:'usd',profitUsd:5,returnRate:null,valuationFxRate:5,notes:'anterior',closedAt:'2026-02-01T00:00:00Z',updatedAt:'2026-02-01T00:00:00Z'};
    if(name==='remove') S.fxPlanning.plan.contributions.push(fxNormalizeContribution({id:'fxc-existing',month:'2026-01',source:'personal',originalCurrency:'USD',originalAmount:25,createdAt:'2026-01-01T00:00:00Z'}));
    if(save()!==true) throw new Error('preparo não gravou');
  };
  window.__installFailure=(kind)=>{
    window.__saveCalls=0;
    if(kind==='quota'){
      window.__setReal=Storage.prototype.setItem;
      Storage.prototype.setItem=function(k,v){if(k===LSKEY)throw new DOMException('Quota sintética','QuotaExceededError');return window.__setReal.call(this,k,v);};
    }
    save=function(){window.__saveCalls++;
      if(kind==='false')return false;
      if(kind==='throw-before')throw new Error('exceção antes da escrita');
      if(kind==='throw-after'){window.__saveReal();throw new Error('exceção depois da escrita');}
      if(kind==='undefined')return undefined;
      return window.__saveReal();
    };
    if(kind==='blocked')blockJPWealthPersistence();
    if(kind==='recovery')jpWealthLoadRecovery.active=true;
  };
  window.__restoreFailure=()=>{
    if(window.__setReal){Storage.prototype.setItem=window.__setReal;window.__setReal=null;}
    save=window.__saveReal;
    if(jpWealthLoadRecovery.active)jpWealthLoadRecovery.active=false;
    if(jpWealthPersistenceIsBlocked())resumeJPWealthPersistence();
  };
  return __snap();
}"""


class Quiet(SimpleHTTPRequestHandler):
    def log_message(self, *_):
        pass


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[1])
    ap.add_argument('--artifact',type=Path,required=True)
    ap.add_argument('--case',default='')
    args=ap.parse_args(); root=args.root.resolve()
    test_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    artifact={'root':str(root),'test_sha256':test_sha256,'sources':{p:hashlib.sha256((root/p).read_bytes()).hexdigest() for p in SOURCE_PATHS},'cases':[]}
    server=ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=str(root)))
    threading.Thread(target=server.serve_forever,daemon=True).start()
    url=f'http://127.0.0.1:{server.server_port}/index.html'
    def case(name, callback):
        if args.case and args.case not in name:return
        record={'name':name,'observations':{},'console':[],'pageerror':[]}
        context=browser.new_context(viewport={'width':1440,'height':1000},service_workers='block')
        install_bootstrap(context)
        context.add_init_script('window.__onbShown=true;')
        page=context.new_page()
        page.on('console',lambda m:record['console'].append({'type':m.type,'text':m.text}))
        page.on('pageerror',lambda e:record['pageerror'].append(str(e)))
        try:
            page.goto(url);wait_bootstrap(page);page.evaluate(SEED)
            callback(page,record['observations'])
            assert_fixture_requests(context)
            assert not record['pageerror'],record['pageerror']
            record['status']='PASS'
        except Exception as e:
            record['status']='FAIL';record['error']=str(e);record['trace']=traceback.format_exc()
        finally:
            context.close();artifact['cases'].append(record)
            print(name,record['status'],record.get('error','')[:300],flush=True)
    def rejection(action,mode):
        def run(p,o):
            p.evaluate('__prepare',action);before=p.evaluate('__snap()');o['before']=before
            p.evaluate('__installFailure',mode)
            try:result=p.evaluate('__act',action)
            except Exception as e:result={'exception':str(e)}
            after=p.evaluate('__snap()');o.update(result=result,after=after)
            assert result.get('ok') is False,result
            for key in ['fx','ledger','saldo','log','raw']:assert after[key]==before[key],key
            p.evaluate('__restoreFailure()')
            # Another real, unrelated input path cannot include the refused act.
            p.evaluate("() => {S.atr55=7;if(save()!==true)throw new Error('save independente');}")
            unrelated=p.evaluate("() => ({fx:JSON.stringify(JSON.parse(localStorage.getItem(LSKEY)).fxPlanning),ledger:JSON.stringify(JSON.parse(localStorage.getItem(LSKEY)).ledger)})")
            assert unrelated['fx']==before['fx'] and unrelated['ledger']==before['ledger'],unrelated
            retry=p.evaluate('__act',action);o['retry']=retry;assert retry['ok'] is True,retry
            committed=p.evaluate('__snap()');o['committed']=committed
            assert len(json.loads(committed['fx'])['auditLog'])==400
            assert len(json.loads(committed['log']))==400
            assert json.loads(committed['log'])[-2]['id']=='dg-old-399'
            assert json.loads(committed['fx'])['auditLog'][-2]['id']=='fx-old-399'
            if action=='add':assert len(json.loads(committed['fx'])['plan']['contributions'])==1
            if action=='edit':assert json.loads(committed['fx'])['plan']['actuals']['2026-01']['closedAt']=='2026-02-01T00:00:00Z'
            if action not in ('create','delete'):assert json.loads(committed['fx'])['plan']['extensaoSintetica']=={'preservar':True}
            p.reload();wait_bootstrap(p)
            reloaded=p.evaluate("() => ({fx:JSON.stringify(S.fxPlanning),log:JSON.stringify(S.dataGovernance.changeLog)})")
            o['reloaded']=reloaded;assert reloaded['fx']==committed['fx'] and reloaded['log']==committed['log']
        return run
    def uncertain(action,mode):
        def run(p,o):
            before=p.evaluate('__snap()');p.evaluate('__installFailure',mode)
            try:result=p.evaluate('__act',action)
            except Exception as e:result={'exception':str(e)}
            after=p.evaluate('__snap()');o.update(before=before,result=result,after=after)
            assert result.get('ok') is False and result.get('persistido') is None,result
            assert after['unknown'] and not after['saved'],after
            assert after['fx']!=before['fx'],'tentativa não preservada'
            if mode=='throw-after':assert after['raw']!=before['raw']
            else:assert after['raw']==before['raw']
            calls=p.evaluate('__saveCalls');retry=p.evaluate('__act',action);o['retry']=retry
            assert retry.get('ok') is False and p.evaluate('__saveCalls')==calls,retry
            assert p.evaluate('__snap().fx')==after['fx']
            p.evaluate('__restoreFailure()');assert p.evaluate('save()') is False
            p.evaluate('resumeJPWealthPersistence()');assert p.evaluate('save()') is False
            p.reload();wait_bootstrap(p)
            persisted=p.evaluate("() => Object.keys(S.fxPlanning.plan.actuals)")
            assert persisted==(['2026-01'] if mode=='throw-after' else []),persisted
        return run
    def daily(mode,delete=False,update=False):
        def run(p,o):
            p.evaluate("() => {JPWNavigation.navigate('forex-reconciliation');}")
            if delete or update:
                p.evaluate("() => {S.ledger=[{data:'2026-01-02',resultado:5,saldo:10005,nota:'anterior'}];syncSaldoAtuFromLedger();save();renderLedger();}")
            before=p.evaluate('__snap()');o['before']=before
            if not delete:
                p.locator('#ldDate').fill('2026-01-02');p.locator('#ldResult').fill('-100');p.locator('#ldNota').fill('rascunho sintético')
            p.evaluate('__installFailure',mode)
            p.locator('[data-ldel]' if delete else '#ldAddBtn').click()
            after=p.evaluate('__snap()');o['after']=after;o['status']=p.locator('#ldStatus').inner_text()
            assert '✓' not in o['status'] and o['status'],o
            if mode in ('throw-before','throw-after','undefined'):
                assert after['unknown'] and not after['saved'],after
                assert after['ledger']!=before['ledger']
                if mode=='throw-after':assert after['raw']!=before['raw']
                else:assert after['raw']==before['raw']
                calls=p.evaluate('__saveCalls');p.locator('[data-ldel]' if delete else '#ldAddBtn').click()
                assert p.evaluate('__saveCalls')==calls
                p.evaluate('__restoreFailure()');assert p.evaluate('save()') is False
            else:
                for key in ['fx','ledger','saldo','log','raw']:assert after[key]==before[key],key
                if not delete:assert p.locator('#ldResult').input_value()=='-100' and p.locator('#ldNota').input_value()=='rascunho sintético'
                p.evaluate('__restoreFailure()')
                p.evaluate("() => {S.atr55=7;save();}")
                assert p.evaluate("JSON.stringify(JSON.parse(localStorage.getItem(LSKEY)).ledger)")==before['ledger']
                p.locator('[data-ldel]' if delete else '#ldAddBtn').click()
                committed=p.evaluate('__snap()');o['committed']=committed
                assert len(json.loads(committed['ledger']))==(0 if delete else 1)
                assert committed['saldo']==(10000 if delete else 9900)
                assert len(json.loads(committed['log']))==400
                assert json.loads(committed['log'])[-2]['id']=='dg-old-399'
                if not delete:assert p.locator('#ldResult').input_value()==''
                p.reload();wait_bootstrap(p)
                assert p.evaluate('JSON.stringify(S.ledger)')==committed['ledger']
        return run
    def ui_actual(p,o):
        p.evaluate("() => {JPWNavigation.navigate('forex-planning');JPWFx.ui.selectView('actuals');}")
        p.locator('#fxpActType').select_option('usd');p.locator('#fxpActValue').fill('10');p.locator('#fxpActNotes').fill('mensal sintético')
        before=p.evaluate('__snap()');p.evaluate("__installFailure('quota')")
        p.locator('#fxpActBtn').click();o['error']=p.locator('#fxpActErr').inner_text();o['after']=p.evaluate('__snap()')
        assert o['error'] and p.locator('#fxpActValue').input_value()=='10'
        assert p.locator('#fxpActMonth').input_value()=='2026-01'
        assert o['after']['fx']==before['fx']
        p.evaluate('__restoreFailure()');p.locator('#fxpActBtn').click()
        assert p.locator('#fxpActMonth').input_value()=='2026-02'
        assert p.evaluate('S.fxPlanning.plan.actuals["2026-01"].profitUsd')==10
        p.reload();wait_bootstrap(p);assert p.evaluate('S.fxPlanning.plan.actuals["2026-01"].profitUsd')==10
    def rejected_draft_navigation(p,o):
        p.evaluate("() => {JPWNavigation.navigate('forex-planning');JPWFx.ui.selectView('actuals');}")
        p.locator('#fxpActType').select_option('usd');p.locator('#fxpActValue').fill('10');p.locator('#fxpActNotes').fill('rascunho recusado')
        p.evaluate("__installFailure('quota')");p.locator('#fxpActBtn').click()
        p.evaluate("() => {JPWNavigation.navigate('dashboard');JPWNavigation.navigate('forex-planning');JPWFx.ui.selectView('actuals');}")
        o['after']={'value':p.locator('#fxpActValue').input_value(),'notes':p.locator('#fxpActNotes').input_value()}
        assert o['after']=={'value':'10','notes':'rascunho recusado'},o
    def unknown_after_recovery(p,o):
        p.evaluate("__installFailure('quota')");r=p.evaluate("__act('actual')");assert r['ok'] is False
        p.evaluate('__restoreFailure()');p.evaluate("__installFailure('throw-after')")
        r=p.evaluate("__act('actual')");o.update(result=r,after=p.evaluate('__snap()'))
        assert r['ok'] is False and o['after']['unknown']
        assert not o['after']['saved'] and not o['after']['recovered'],o
    def invalid_and_normal(p,o):
        before=p.evaluate('__snap()')
        invalid=p.evaluate("() => [JPWFx.state.fxPlanRecordActual('2026-03',{inputType:'usd',profitUsd:1}),JPWFx.state.fxPlanAddContribution({month:'invalid',source:'personal',originalCurrency:'USD',originalAmount:25})]")
        after=p.evaluate('__snap()');o.update(invalid=invalid,before=before,after=after)
        assert all(r['ok'] is False for r in invalid)
        for key in ['fx','ledger','saldo','log','raw']:assert before[key]==after[key]
        result=p.evaluate("() => JPWFx.state.fxPlanRecordActual('2026-01',{inputType:'usd',profitUsd:0,notes:'zero explícito'})")
        assert result['ok'] is True
        assert p.evaluate('S.fxPlanning.plan.actuals["2026-01"].profitUsd')==0
        assert p.evaluate('fxOverviewLive().currentBalanceUsd')==1000
    def prepare_exception(p,o):
        before=p.evaluate('__snap()')
        p.evaluate("() => {window.__auditReal=fxAudit;fxAudit=()=>{throw new Error('audit sintético antes de save')};}")
        try:result=p.evaluate("__act('actual')")
        except Exception as e:result={'exception':str(e)}
        after=p.evaluate('__snap()');o.update(result=result,before=before,after=after)
        assert result.get('ok') is False and result.get('persistido') is False,result
        for key in ['fx','ledger','saldo','log','raw']:assert after[key]==before[key],key
    def preserve_other_mutation(p,o):
        before=p.evaluate('__snap()')
        p.evaluate("() => {save=()=>{S.atr55=27;return false;};}")
        result=p.evaluate("__act('actual')");after=p.evaluate('__snap()');o.update(result=result,after=after)
        assert result.get('ok') is False and p.evaluate('S.atr55')==27,result
        for key in ['fx','ledger','saldo','log','raw']:assert after[key]==before[key],key
    def mobile_feedback(p,o):
        p.set_viewport_size({'width':390,'height':844})
        p.evaluate("() => {JPWNavigation.navigate('forex-planning');JPWFx.ui.selectView('actuals');}")
        p.locator('#fxpActType').select_option('usd');p.locator('#fxpActValue').fill('10')
        p.evaluate("__installFailure('quota')");p.locator('#fxpActBtn').click()
        assert p.locator('#fxpActErr [role=alert]').is_visible()
        assert p.evaluate('document.activeElement.id')=='fxpActBtn'
        assert p.evaluate('document.documentElement.scrollWidth<=window.innerWidth'), 'overflow global'
        for theme in ['light','dark']:
            p.evaluate("theme=>document.documentElement.setAttribute('data-theme',theme)",theme)
            p.locator('#fxpActErr').scroll_into_view_if_needed()
            path=args.artifact.parent/(args.artifact.stem+'-mobile-'+theme+'.png')
            p.screenshot(path=str(path));o[theme]=str(path)
        p.evaluate("() => {JPWNavigation.navigate('forex-reconciliation');}")
        p.locator('#ldDate').fill('2026-01-02');p.locator('#ldResult').fill('-100');p.locator('#ldAddBtn').click()
        assert p.locator('#ldStatus').is_visible() and '✓' not in p.locator('#ldStatus').inner_text()
        assert p.evaluate('document.activeElement.id')=='ldAddBtn'
        assert p.evaluate('document.documentElement.scrollWidth<=window.innerWidth')
        p.screenshot(path=str(args.artifact.parent/(args.artifact.stem+'-mobile-daily.png')))
    def ui_form(group):
        def run(p,o):
            if group=='create':p.evaluate("() => {S.fxPlanning.plan=null;save();}")
            if group=='removal':p.evaluate("__prepare('remove')")
            p.evaluate("() => JPWNavigation.navigate('forex-planning')")
            if group in ('planning','deletion'):p.evaluate("() => JPWFx.ui.selectView('planning')")
            if group in ('contribution','removal'):p.evaluate("() => JPWFx.ui.selectView('actuals')")
            controls={
                'create':{'fxpName':'Plano de rascunho','fxpStart':'2026-01','fxpInitial':'1000','fxpDefaultRate':'1','fxpHorizon':'12'},
                'planning':{'fxpEditRate':'2','fxpEditNote':'revisão recusada'},
                'deletion':{'fxpDeleteConfirm':'EXCLUIR'},
                'contribution':{'fxpCMonth':'2026-01','fxpCAmount':'25'},
                'removal':{}}[group]
            button={'create':'#fxpCreateBtn','planning':'#fxpReviseBtn','deletion':'#fxpDeleteBtn','contribution':'#fxpCBtn','removal':'[data-fxp-del]'}[group]
            error={'create':'#fxpCreateErr','planning':'#fxpPlanningErr','deletion':'#fxpDeleteErr','contribution':'#fxpCErr','removal':'#fxpCErr'}[group]
            if group=='contribution':p.locator('#fxpCCurrency').select_option('USD')
            for id,value in controls.items():p.locator('#'+id).fill(value)
            before=p.evaluate('__snap()');p.evaluate("__installFailure('quota')");p.locator(button).click()
            after=p.evaluate('__snap()');o.update(before=before,after=after)
            assert p.locator(error).count(),'formulário de erro desapareceu após recusa'
            o['error']=p.locator(error).inner_text()
            assert o['error'] and after['fx']==before['fx']
            p.evaluate("() => {JPWNavigation.navigate('dashboard');JPWNavigation.navigate('forex-planning');}")
            if group in ('planning','deletion'):p.evaluate("() => JPWFx.ui.selectView('planning')")
            if group in ('contribution','removal'):p.evaluate("() => JPWFx.ui.selectView('actuals')")
            for id,value in controls.items():assert p.locator('#'+id).input_value()==value,(id,p.locator('#'+id).input_value())
            assert p.locator(error).inner_text()
            if group=='planning':
                p.locator(error).scroll_into_view_if_needed()
                for theme in ['light','dark']:
                    p.evaluate("theme=>document.documentElement.setAttribute('data-theme',theme)",theme)
                    path=args.artifact.parent/(args.artifact.stem+'-desktop-'+theme+'.png');p.screenshot(path=str(path));o[theme]=str(path)
            p.evaluate('__restoreFailure()');p.locator(button).click()
            state=p.evaluate('S.fxPlanning.plan');o['committed']=state
            if group=='deletion':assert state is None
            elif group=='create':assert state['name']=='Plano de rascunho'
            elif group=='planning':assert state['current']['defaultMonthlyReturn']==0.02 and state['baseline']['defaultMonthlyReturn']==0.01
            elif group=='contribution':assert len(state['contributions'])==1 and state['contributions'][0]['usdAmount']==25
            elif group=='removal':assert state['contributions']==[]
        return run
    def one_write_normal(p,o):
        p.evaluate("() => {window.__physicalWrites=0;window.__setReal=Storage.prototype.setItem;Storage.prototype.setItem=function(k,v){if(k===LSKEY)window.__physicalWrites++;return window.__setReal.call(this,k,v);};}")
        result=p.evaluate("__act('actual')");o.update(result=result,writes=p.evaluate('__physicalWrites'),after=p.evaluate('__snap()'))
        assert result.get('ok') is True and o['writes']==1,o
        assert len(json.loads(o['after']['fx'])['plan']['actuals'])==1
        assert json.loads(o['after']['log'])[-1]['action']=='FX_MONTH_ACTUAL_RECORDED'
    def refused_reload(p,o):
        p.evaluate("() => {JPWNavigation.navigate('forex-planning');JPWFx.ui.selectView('actuals');}")
        p.locator('#fxpActType').select_option('usd');p.locator('#fxpActValue').fill('10')
        before=p.evaluate('__snap()');p.evaluate("__installFailure('quota')")
        p.locator('#fxpActBtn').focus();p.keyboard.press('Enter')
        assert p.locator('#fxpActErr').inner_text()
        assert p.evaluate('document.activeElement.id')=='fxpActBtn'
        p.reload();wait_bootstrap(p)
        after=p.evaluate("() => ({fx:JSON.stringify(S.fxPlanning),log:JSON.stringify(S.dataGovernance.changeLog),raw:localStorage.getItem(LSKEY)})")
        o.update(before=before,after=after)
        for key in ['fx','log','raw']:assert after[key]==before[key],key
    def cancellation(p,o):
        p.evaluate("() => {S.ledger=[{data:'2026-01-02',resultado:5,saldo:10005,nota:'anterior'}];syncSaldoAtuFromLedger();save();JPWNavigation.navigate('forex-reconciliation');renderLedger();window.confirm=()=>false;}")
        before=p.evaluate('__snap()');p.locator('#ldDate').fill('2026-01-02');p.locator('#ldResult').fill('12');p.locator('#ldAddBtn').click()
        p.locator('[data-ldel]').click();after=p.evaluate('__snap()');o.update(before=before,after=after)
        for key in ['fx','ledger','saldo','log','raw']:assert after[key]==before[key]
        p.locator('#ldDate').fill('2026-01-01');p.locator('#ldAddBtn').click()
        assert p.evaluate('__snap().ledger')==before['ledger'],'cancelar backdate alterou ledger'
    def two_tabs(p,o):
        second=p.context.new_page();second.goto(url);wait_bootstrap(second)
        # B commits through the actual save implementation. No storage listener
        # is replaced: the observations prove whether A refuses its stale state.
        second.evaluate("() => {S.atr55=13;if(save()!==true)throw new Error('B não gravou');}")
        p.wait_for_timeout(100)
        before=p.evaluate('__snap()');result=p.evaluate("__act('actual')");after=p.evaluate('__snap()')
        o.update(before=before,result=result,after=after)
        assert result.get('ok') is False,result
        assert after['fx']==before['fx'] and after['log']==before['log']
        assert json.loads(after['raw'])['atr55']==13
        second.close()
    def reserves(p,o):
        p.evaluate("""() => {S.params.saldoIni=10000;S.params.saldoAtu=10000;
          S.onboarding={...S.onboarding,done:true,reserveMasterCapital:'10000',reserveFcrCurrent:'1500',reserveFcrStatus:'Regular',reserveFcrCoveragePct:'100',reserveMonthlyExpenses:'100',reserveFeoCurrent:'600',reserveFeoStatus:'Regular',reserveFeoMonthsCovered:'6',centralCashStatus:'Sim.',epStatus:'Sim, vou utilizar.'};save();openSettingsModal('parameters');}""")
        # Actual compute is observed; no expected financial clearance invented.
        o['before']=p.evaluate("() => ({clearance:getOperationalClearance(),panel:fxReservePanelData()})")
        if not p.locator('#pSaldoIni').is_visible():
            p.evaluate("() => {settingsNavigate('parameters');}")
        p.locator('#pSaldoIni').fill('20000')
        o['after']=p.evaluate("() => ({clearance:getOperationalClearance(),panel:fxReservePanelData(),snapshot:S.onboarding.reserveFcrStatus,stored:JSON.parse(localStorage.getItem(LSKEY)).params.saldoIni})")
        assert o['after']['stored']==20000
        assert o['after']['panel']['fcrStatus']=='Insuficiente' and o['after']['snapshot']=='Regular'
        assert not any('Reservas segregadas' in r for r in o['after']['clearance']['reasons'])
        o['classification']='NEEDS_HUMAN_RULE — inconsistência caracterizada, sem aprovação normativa'
    try:
        with sync_playwright() as pw:
            browser=pw.chromium.launch(headless=True)
            for action in ['create','delete','revise','actual','edit','add','remove']:
                case('fx-'+action+'-quota-retry-reload',rejection(action,'quota'))
            for mode in ['false','blocked','recovery']:
                case('fx-actual-'+mode,rejection('actual',mode))
            for mode in ['throw-before','throw-after','undefined']:
                case('fx-actual-'+mode,uncertain('actual',mode))
            for mode in ['quota','false','blocked','recovery','throw-before','throw-after','undefined']:
                case('daily-create-'+mode,daily(mode))
            case('daily-update-quota',daily('quota',update=True))
            case('daily-delete-quota',daily('quota',delete=True))
            for mode in ['throw-before','throw-after','undefined']:
                case('daily-delete-'+mode,daily(mode,delete=True))
            case('daily-cancel',cancellation)
            case('fx-month-ui-quota',ui_actual)
            case('two-tabs-refusal',two_tabs)
            case('reserves-characterization',reserves)
            case('fx-draft-navigation',rejected_draft_navigation)
            case('fx-unknown-after-recovery',unknown_after_recovery)
            case('fx-invalid-normal',invalid_and_normal)
            case('fx-exception-before-save',prepare_exception)
            case('fx-preserve-other-mutation',preserve_other_mutation)
            case('mobile-feedback',mobile_feedback)
            case('fx-one-physical-write',one_write_normal)
            case('fx-refused-reload-keyboard',refused_reload)
            for group in ['create','planning','deletion','contribution','removal']:
                case('ui-form-'+group,ui_form(group))
            browser.close()
    finally:
        server.shutdown();server.server_close()
        artifact['sources_after']={p:hashlib.sha256((root/p).read_bytes()).hexdigest() for p in SOURCE_PATHS}
        assert artifact['sources_after']==artifact['sources'],'fontes mudaram durante os focais'
        assert hashlib.sha256(Path(__file__).read_bytes()).hexdigest()==test_sha256,'teste mudou durante a execução'
        artifact['summary']={'total':len(artifact['cases']),'passed':sum(c['status']=='PASS' for c in artifact['cases']),'failed':sum(c['status']=='FAIL' for c in artifact['cases'])}
        args.artifact.parent.mkdir(parents=True,exist_ok=True)
        args.artifact.write_text(json.dumps(artifact,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(artifact['summary']),flush=True)
    return 1 if artifact['summary']['failed'] else 0


if __name__=='__main__':
    raise SystemExit(main())
