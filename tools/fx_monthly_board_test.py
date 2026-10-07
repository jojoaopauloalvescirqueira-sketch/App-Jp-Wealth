#!/usr/bin/env python3
"""Monthly planning contracts against the real application in disposable profiles.

The app, financial core, commands, persistence, backup and monthly board are not
stubbed. The existing bounded bootstrap fixture replaces public news/FX feeds.
Failure probes replace only the physical storage adapter or its return receipt.
All accounts, plans, deposits and operations below are synthetic.

Run --baseline against the preserved source directory before implementation to
record the old behaviour without modifying old fixtures, gates or judges.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
from http.server import SimpleHTTPRequestHandler
import threading
import time
import traceback

from playwright.sync_api import sync_playwright
from browser_fixture_server import BrowserFixtureServer
from browser_bootstrap_fixture import install_bootstrap, wait_bootstrap, assert_fixture_requests


SOURCE_PATHS = [
    'src/js/30-accounting/05-fx-planning/01-fx-model.js',
    'src/js/30-accounting/05-fx-planning/02-fx-engine.js',
    'src/js/30-accounting/05-fx-planning/03-fx-state.js',
    'src/js/30-accounting/05-fx-planning/04-fx-charts.js',
    'src/js/30-accounting/05-fx-planning/05-fx-ui.js',
    'src/js/00-core/04-persistence.js',
    'src/js/30-accounting/01-daily-ledger.js',
    'src/js/40-app/01-navigation.js',
    'src/styles/app.css',
]


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, *_args):
        pass


SETUP = r"""() => {
  window.__testPrimaryWrites=0;
  const original=Storage.prototype.setItem;
  Storage.prototype.setItem=function(key,value){
    if(key==='jpwealth_v9_state')window.__testPrimaryWrites++;
    return original.call(this,key,value);
  };
  window.__monthlyTest={
    seed(overrides={}){
      S.fxPlanning={schemaVersion:1,plan:null,auditLog:[]};
      const created=JPWFx.state.fxPlanCreate({name:'Synthetic monthly plan',assumptions:{
        startMonth:'2026-01',horizonMonths:6,initialBalanceUsd:1000,
        defaultMonthlyReturn:.01,projectedFxRate:5,
        recurringContributions:{personalUsd:10,propUsd:5},...overrides
      }});
      if(!created.ok)throw Error(JSON.stringify(created));
      return created;
    },
    near(a,b,label='value'){
      if(typeof a!=='number'||!Number.isFinite(a)||Math.abs(a-b)>1e-8)
        throw Error(label+': '+JSON.stringify(a)+' != '+b);
    },
    yes(value,label='assertion'){if(!value)throw Error(label);},
    same(a,b,label='identity'){
      if(JSON.stringify(a)!==JSON.stringify(b))throw Error(label+' differs');
    },
    rows(){return JPWFx.engine.fxMonthlyTimeline(JPWFx.state.fxActivePlan());},
    finalize(month,input={inputType:'rate',returnRate:.01}){
      const r=JPWFx.state.fxPlanFinalizeMonth(month,{...input,contributionsConfirmed:true});
      this.yes(r.ok,JSON.stringify(r));return r;
    }
  };
}"""


def open_page(browser, url, *, seed=None, width=1440, context=None):
    created_context = context is None
    if context is None:
        context = browser.new_context(viewport={'width': width, 'height': 960}, service_workers='block')
        context.add_init_script("window.__onbShown=true;")
        context.add_init_script("localStorage.setItem('jpw_module_availability_v1',JSON.stringify({schemaVersion:1,modules:{alladin:'active'}}));")
        if seed is not None:
            context.add_init_script("localStorage.setItem('jpwealth_v9_state'," + json.dumps(seed) + ");")
        install_bootstrap(context)
    page = context.new_page()
    errors = []
    page.on('pageerror', lambda error: errors.append(str(error)))
    page.on('dialog', lambda dialog: dialog.accept('Synthetic review reason') if dialog.type == 'prompt' else dialog.accept())
    page.goto(url, wait_until='load')
    wait_bootstrap(page)
    page.wait_for_function('() => window.JPWFx && JPWFx.state && window.JPWNavigation')
    page.evaluate(SETUP)
    return context, page, errors, created_context


BASELINE_CASES = {
    'null override coerced to explicit zero': r"""() => {
      const p=JPWFx.model.fxCreatePlan({name:'Baseline',assumptions:{startMonth:'2026-01',horizonMonths:2,
        initialBalanceUsd:1000,defaultMonthlyReturn:.01,monthOverrides:{'2026-01':null}}});
      return {rate:JPWFx.model.fxResolveRate(p.current,'2026-01'),monthlyBoard:typeof JPWFx.engine.fxMonthlyTimeline};
    }""",
    'recorded actual editable without reopening': r"""() => {
      const t=__monthlyTest;t.seed();
      const first=JPWFx.state.fxPlanRecordActual('2026-01',{inputType:'usd',profitUsd:10});
      const second=JPWFx.state.fxPlanRecordActual('2026-01',{inputType:'usd',profitUsd:20});
      return {first,second,profit:S.fxPlanning.plan.actuals['2026-01'].profitUsd};
    }""",
    'deposit added after recorded actual': r"""() => {
      const t=__monthlyTest;t.seed();
      JPWFx.state.fxPlanRecordActual('2026-01',{inputType:'usd',profitUsd:10});
      const first=JPWFx.engine.fxActualTimeline(JPWFx.state.fxActivePlan())[0].close;
      const result=JPWFx.state.fxPlanAddContribution({month:'2026-01',source:'personal',originalCurrency:'USD',originalAmount:100});
      const second=JPWFx.engine.fxActualTimeline(JPWFx.state.fxActivePlan())[0].close;
      return {first,second,result};
    }""",
    'monthly absence and closure APIs absent': r"""() => ({
      clear:typeof JPWFx.state.fxPlanClearMonth,
      finalize:typeof JPWFx.state.fxPlanFinalizeMonth,
      reopen:typeof JPWFx.state.fxPlanReopenMonth,
      timeline:typeof JPWFx.engine.fxMonthlyTimeline
    })""",
}


DOMAIN_CASES = {
    'malformed monthly values remain unavailable instead of numeric coercion': r"""() => {
      const t=__monthlyTest;
      for(const value of [null,'',' ',true,false,[],{},'2xyz']){
        t.seed();const a={...S.fxPlanning.plan.current,monthOverrides:{'2026-02':value}};
        t.yes(JPWFx.model.fxResolveRate(a,'2026-02')===null,'malformed rate became number');
        const normalized=JPWFx.model.fxNormalizeAssumptions(a);
        t.yes(normalized.monthOverrides['2026-02']===null);
        t.yes(JPWFx.model.fxValidateAssumptions(normalized).length>0);
        const before=JSON.stringify(S.fxPlanning),writes=__testPrimaryWrites;
        t.yes(!JPWFx.state.fxPlanReviseFromMonth('2026-02',{rate:value},'Invalid').ok);
        t.yes(JSON.stringify(S.fxPlanning)===before&&__testPrimaryWrites===writes);
      }
      t.seed();const valid={...S.fxPlanning.plan.current,monthOverrides:{'2026-02':0}};
      t.yes(JPWFx.model.fxResolveRate(valid,'2026-02')===0);return {malformedRefused:8,zeroPreserved:true};
    }""",
    'full arithmetic, recurring deposits and explicit zero exceptions': r"""() => {
      const t=__monthlyTest;t.seed();const a=t.rows();
      t.near(a[0].profit,10);t.near(a[0].close,1025);t.near(a[1].open,1025);
      t.yes(JPWFx.state.fxPlanReviseFromMonth('2026-02',{rate:0,personalUsd:0,propUsd:0},'Zero month').ok);
      const b=t.rows();t.near(b[1].profit,0);t.near(b[1].close,1025);
      t.near(b[2].personalUsd,10);t.near(b[2].propUsd,5);
      t.yes(S.fxPlanning.plan.current.plannedContributions['2026-02'].personalUsd===0);
      return b.slice(0,3);
    }""",
    'clear month distinguishes absence from zero and blocks dependent values': r"""() => {
      const t=__monthlyTest;t.seed();const before=t.rows(),baseline=structuredClone(S.fxPlanning.plan.baseline);
      t.yes(JPWFx.state.fxPlanReviseFromMonth('2026-04',{rate:.04,personalUsd:40,propUsd:8},'Future exception').ok);
      t.yes(JPWFx.state.fxPlanClearMonth('2026-02','Remove February').ok);
      const a=t.rows();t.same(a[0],before[0]);t.yes(a[1].status==='ABSENT');
      for(const r of a.slice(1)){t.yes(r.close===null&&r.profit===null,'gap manufactured number');}
      t.yes(a[2].blockedBy==='2026-02');t.near(a[3].rate,.04);
      t.same(S.fxPlanning.plan.baseline,baseline);
      t.yes(JPWFx.state.fxPlanReviseFromMonth('2026-02',{rate:0},'Incomplete restore').ok===false);
      t.yes(JPWFx.state.fxPlanReviseFromMonth('2026-02',{rate:0,personalUsd:0,propUsd:0},'Refill zero').ok);
      const b=t.rows();t.near(b[1].close,b[0].close);t.near(b[3].rate,.04);
      return {gap:a.slice(0,4),restored:b.slice(0,4)};
    }""",
    'gaps at first last and all months remain absent through summaries': r"""() => {
      const t=__monthlyTest;const out=[];
      for(const month of ['2026-01','2026-06']){
        t.seed();t.yes(JPWFx.state.fxPlanClearMonth(month,'Boundary absent').ok);
        const p=JPWFx.state.fxActivePlan(),rows=t.rows(),annual=JPWFx.engine.fxAnnualSummary(rows);
        t.yes(rows.find(r=>r.month===month).close===null);
        t.yes(annual[0].close===null&&annual[0].profitUsd===null,'partial total masquerades as complete');
        t.yes(JPWFx.engine.fxVarianceRows(rows,JPWFx.engine.fxPlannedTimeline(p.baseline)).every(r=>r.diffUsd===null||typeof r.diffUsd==='number'));
        out.push({month,annual});
      }
      t.seed();for(let i=0;i<6;i++)t.yes(JPWFx.state.fxPlanClearMonth(JPWFx.model.fxAddMonths('2026-01',i),'All absent').ok);
      t.yes(t.rows().every(r=>r.close===null));return out;
    }""",
    'general assumptions preserve monthly exceptions and removed forecasts': r"""() => {
      const t=__monthlyTest;t.seed();
      t.yes(JPWFx.state.fxPlanReviseFromMonth('2026-02',{rate:0,personalUsd:0,propUsd:0},'Monthly exception').ok);
      t.yes(JPWFx.state.fxPlanClearMonth('2026-04','No estimate').ok);
      const baseline=structuredClone(S.fxPlanning.plan.baseline);
      t.yes(JPWFx.state.fxPlanReviseAssumptions({...S.fxPlanning.plan.current,defaultMonthlyReturn:.02,
        recurringContributions:{personalUsd:20,propUsd:10}},'General premise').ok);
      const rows=t.rows();t.near(rows[0].rate,.02);t.near(rows[0].personalUsd,20);
      t.near(rows[1].rate,0);t.near(rows[1].personalUsd,0);t.yes(rows[3].status==='ABSENT');
      t.same(S.fxPlanning.plan.baseline,baseline);
      t.yes(JPWFx.state.fxPlanRestoreMonth('2026-02','Use general premises').ok);
      const restored=t.rows()[1];t.near(restored.rate,.02);t.near(restored.personalUsd,20);return restored;
    }""",
    'finalization requires explicit deposit check including zero': r"""() => {
      const t=__monthlyTest;t.seed();const before=JSON.stringify(S.fxPlanning),writes=__testPrimaryWrites;
      for(const value of [null,'',' ',true,false,[],{}]){
        const r=JPWFx.state.fxPlanFinalizeMonth('2026-01',{inputType:'rate',returnRate:value,contributionsConfirmed:true});
        t.yes(!r.ok,'invalid original accepted');
      }
      t.yes(!JPWFx.state.fxPlanFinalizeMonth('2026-01',{inputType:'usd',profitUsd:0}).ok);
      t.yes(JSON.stringify(S.fxPlanning)===before&&__testPrimaryWrites===writes,'refusal wrote');
      t.finalize('2026-01',{inputType:'usd',profitUsd:0});const r=t.rows()[0];
      t.yes(r.status==='FINALIZED');t.near(r.close,1000);t.near(r.contributionUsd,0);
      t.yes(S.fxPlanning.plan.actuals['2026-01'].returnRate===null,'two original inputs persisted');
      t.yes(S.fxPlanning.plan.planningRevision===3);return r;
    }""",
    'finalized month guards record, deposit addition/removal, preview clear and import': r"""() => {
      const t=__monthlyTest;t.seed();
      const c=JPWFx.state.fxPlanAddContribution({month:'2026-01',source:'personal',originalCurrency:'BRL',originalAmount:500,acquisitionFxRate:5});
      t.yes(c.ok);t.finalize('2026-01');const before=JSON.stringify(S.fxPlanning),writes=__testPrimaryWrites;
      const results=[
        JPWFx.state.fxPlanRecordActual('2026-01',{inputType:'rate',returnRate:.2,contributionsConfirmed:true}),
        JPWFx.state.fxPlanFinalizeMonth('2026-01',{inputType:'rate',returnRate:.2,contributionsConfirmed:true}),
        JPWFx.state.fxPlanAddContribution({month:'2026-01',source:'prop',originalCurrency:'USD',originalAmount:200}),
        JPWFx.state.fxPlanRemoveContribution(c.contribution.id),
        JPWFx.state.fxPlanClearMonth('2026-01','Remove closed forecast'),
        JPWFx.state.fxPlanReviseFromMonth('2026-01',{rate:.2},'Try forecast edit'),
        JPWFx.state.fxPlanImportLedgerActual('2026-01',{complete:true,replace:true,sourceVersion:'synthetic'})
      ];
      t.yes(results.every(r=>!r.ok),'closed path accepted edit');
      t.yes(JSON.stringify(S.fxPlanning)===before&&__testPrimaryWrites===writes,'guard mutated');return results;
    }""",
    'reopen old actual preserves downstream inputs and requires chronological reconciliation': r"""() => {
      const t=__monthlyTest;t.seed();
      t.finalize('2026-01',{inputType:'rate',returnRate:.1});
      t.finalize('2026-02',{inputType:'rate',returnRate:.1});
      t.finalize('2026-03',{inputType:'usd',profitUsd:100,source:{system:'SYNTHETIC_IMPORT',version:'one'}});
      const baseline=structuredClone(S.fxPlanning.plan.baseline),old=structuredClone(S.fxPlanning.plan.actuals);
      t.yes(!JPWFx.state.fxPlanReopenMonth('2026-01','').ok);
      t.yes(JPWFx.state.fxPlanReopenMonth('2026-01','Correct opening result').ok);
      const a=t.rows();t.yes(a[0].status==='REOPENED'&&a[1].status==='REVIEW_REQUIRED'&&a[2].status==='REVIEW_REQUIRED');
      t.yes(a.slice(0,3).every(r=>r.close===null),'reopened stale result displayed active');
      t.yes(S.fxPlanning.plan.actuals['2026-02'].returnRate===old['2026-02'].returnRate);
      t.yes(S.fxPlanning.plan.actuals['2026-03'].profitUsd===100);
      t.same(S.fxPlanning.plan.actuals['2026-03'].source,old['2026-03'].source);
      t.yes(!JPWFx.state.fxPlanFinalizeMonth('2026-03',{inputType:'usd',profitUsd:100,contributionsConfirmed:true}).ok);
      t.finalize('2026-01',{inputType:'rate',returnRate:.2});
      t.yes(t.rows()[1].status==='REVIEW_REQUIRED');
      t.finalize('2026-02',{inputType:'rate',returnRate:.1});
      t.finalize('2026-03',{inputType:'usd',profitUsd:100,source:old['2026-03'].source});
      const b=t.rows();t.near(b[0].close,1200);t.near(b[1].close,1320);t.near(b[2].close,1420);t.near(b[3].open,1420);
      t.same(S.fxPlanning.plan.baseline,baseline);
      t.yes(S.fxPlanning.plan.actualHistory.some(r=>r.month==='2026-01'&&r.before),'history lost prior input');
      return {before:old,review:a,reconciled:b.slice(0,4),history:S.fxPlanning.plan.actualHistory};
    }""",
    'cleared forecast can be replaced with actual and actual deposits remain single source': r"""() => {
      const t=__monthlyTest;t.seed();t.yes(JPWFx.state.fxPlanClearMonth('2026-01','No projection').ok);
      t.yes(JPWFx.state.fxPlanAddContribution({month:'2026-01',source:'personal',originalCurrency:'BRL',originalAmount:500,acquisitionFxRate:5}).ok);
      t.yes(JPWFx.state.fxPlanAddContribution({month:'2026-01',source:'prop',originalCurrency:'USD',originalAmount:25}).ok);
      t.finalize('2026-01',{inputType:'usd',profitUsd:-10,valuationFxRate:5.4});
      const rows=t.rows();t.near(rows[0].profit,-10);t.near(rows[0].contributionUsd,125);t.near(rows[0].close,1115);
      t.near(rows[1].open,1115);t.near(JPWFx.engine.fxCostBasis(S.fxPlanning.plan.contributions).weightedAverageFx,5);
      t.near(fxChartConvert(rows[0],'brl',{presentMonth:'2026-01',currentRate:99,projectedRate:88}),1115*5.4);
      return rows.slice(0,2);
    }""",
    'gap chart conversions do not fabricate values or join segments': r"""() => {
      const t=__monthlyTest;t.seed();t.yes(JPWFx.state.fxPlanClearMonth('2026-03','Chart gap').ok);
      const rows=t.rows(),p=JPWFx.state.fxActivePlan();
      t.yes(fxChartConvert(rows[2],'usd',{})===null);t.yes(fxChartConvert(rows[2],'brl',{projectedRate:5})===null);
      const segments=fxChartSegments([{i:0,y:100},{i:1,y:null},{i:2,y:0},{i:3,y:110}]);
      t.same(segments.map(s=>s.map(p=>p.i)),[[0],[2,3]]);
      const host=document.createElement('div');host.style.width='900px';document.body.append(host);
      fxDrawMainChart(host,p,JPWFx.engine.fxOverview(p),'usd');
      t.yes(host.querySelector('svg'),'chart missing');t.yes(!/NaN|Infinity/.test(host.innerHTML),'invalid SVG');
      const text=fxMainChartSummaryText(p,JPWFx.engine.fxOverview(p),'usd');
      host.remove();return {segments,text};
    }""",
    'reads projections and redraw do not save or normalize the document': r"""() => {
      const t=__monthlyTest;t.seed();S.fxPlanning.plan.extension={opaque:[1,2]};
      const before=JSON.stringify(S.fxPlanning),writes=__testPrimaryWrites;
      JPWFx.state.fxActivePlan();JPWFx.state.fxOverviewLive();t.rows();
      JPWFx.engine.fxAnnualSummary(t.rows());JPWFx.engine.fxForecastAtRevision(JPWFx.state.fxActivePlan(),0);
      renderFxPlanning();renderFxPlanning();
      t.yes(JSON.stringify(S.fxPlanning)===before);t.yes(__testPrimaryWrites===writes);return {writes};
    }""",
    'legacy revision two reads finalized and preserves extension through explicit revision': r"""() => {
      const t=__monthlyTest;t.seed();const raw=S.fxPlanning.plan;
      raw.planningRevision=2;raw.extension={opaque:[1,2]};
      raw.actuals['2026-01']={inputType:'usd',profitUsd:10,closedAt:'2026-02-01T00:00:00Z',updatedAt:'2026-02-01T00:00:00Z',extension:'keep'};
      delete raw.current.absentMonths;delete raw.current.recurringContributions;
      const before=JSON.stringify(raw),writes=__testPrimaryWrites;
      const r=t.rows()[0];t.yes(r.status==='FINALIZED');t.near(r.close,1010);
      t.yes(JSON.stringify(raw)===before&&__testPrimaryWrites===writes,'read migration persisted');
      t.yes(JPWFx.state.fxPlanReviseFromMonth('2026-03',{rate:.02},'Legacy forecast update').ok);
      t.same(S.fxPlanning.plan.extension,{opaque:[1,2]});t.yes(S.fxPlanning.plan.actuals['2026-01'].extension==='keep');
      t.yes(S.fxPlanning.plan.planningRevision===3);return t.rows().slice(0,3);
    }""",
    'future incompatible revision and corrupt gap state refuse without writing': r"""() => {
      const t=__monthlyTest;t.seed();S.fxPlanning.plan.planningRevision=99;
      let before=JSON.stringify(S.fxPlanning),writes=__testPrimaryWrites;
      t.yes(JPWFx.state.fxEnvelopeIssue());t.yes(JPWFx.state.fxActivePlan()===null);
      t.yes(!JPWFx.state.fxPlanClearMonth('2026-01','incompatible').ok);
      t.yes(JSON.stringify(S.fxPlanning)===before&&__testPrimaryWrites===writes);
      t.seed();S.fxPlanning.plan.current.absentMonths=[];
      before=JSON.stringify(S.fxPlanning);writes=__testPrimaryWrites;
      t.yes(JPWFx.state.fxEnvelopeIssue());t.yes(!JPWFx.state.fxPlanRestoreMonth('2026-01','corrupt').ok);
      t.yes(JSON.stringify(S.fxPlanning)===before&&__testPrimaryWrites===writes);return {writes};
    }""",
    'physical storage refusal rolls back financial audit and keeps persisted state': r"""() => {
      const t=__monthlyTest;t.seed();const before=JSON.stringify(S.fxPlanning),dg=JSON.stringify(S.dataGovernance.changeLog),disk=localStorage.getItem('jpwealth_v9_state');
      const original=Storage.prototype.setItem;
      Storage.prototype.setItem=function(k,v){if(k==='jpwealth_v9_state')throw new DOMException('Synthetic quota','QuotaExceededError');return original.call(this,k,v);};
      let result;try{result=JPWFx.state.fxPlanClearMonth('2026-02','Storage refusal');}finally{Storage.prototype.setItem=original;}
      t.yes(result.ok===false&&result.persistido===false);t.yes(JSON.stringify(S.fxPlanning)===before);
      t.yes(JSON.stringify(S.dataGovernance.changeLog)===dg);t.yes(localStorage.getItem('jpwealth_v9_state')===disk);
      t.yes(!document.querySelector('#savedTag')?.classList.contains('show'));return result;
    }""",
    'unknown receipt blocks replay without claiming success': r"""() => {
      const t=__monthlyTest;t.seed();const original=save;
      save=function(){original();return undefined;};
      let result;try{result=JPWFx.state.fxPlanClearMonth('2026-02','Unknown receipt');}finally{save=original;}
      t.yes(result.ok===false&&result.persistido===null);t.yes(jpWealthPersistenceOutcomeIsUnknown());
      const writes=__testPrimaryWrites;
      const retry=JPWFx.state.fxPlanClearMonth('2026-02','Do not replay');t.yes(!retry.ok&&retry.persistido===null);
      t.yes(__testPrimaryWrites===writes);t.yes(!document.querySelector('#savedTag')?.classList.contains('show'));return {result,retry,writes};
    }""",
}


def run_js_case(browser, url, expression):
    context, page, errors, _ = open_page(browser, url)
    try:
        result = page.evaluate(expression)
        assert not errors, errors
        assert_fixture_requests(context)
        return result
    finally:
        context.close()


def reload_backup_case(browser, url):
    context, page, errors, _ = open_page(browser, url)
    try:
        before = page.evaluate(r"""async () => {
          const t=__monthlyTest;t.seed();
          t.yes(JPWFx.state.fxPlanClearMonth('2026-04','Saved absence').ok);
          t.finalize('2026-01',{inputType:'usd',profitUsd:7});
          S.fxPlanning.plan.extension={opaque:'roundtrip'};save();
          const backup=JSON.parse(await dgBuildBackupBlob(1,'synthetic.json','2026-02-01T00:00:00Z').text());
          return {planning:structuredClone(S.fxPlanning),backup};
        }""")
        page.reload(wait_until='load')
        wait_bootstrap(page)
        restored = page.evaluate('() => structuredClone(S.fxPlanning)')
        assert restored == before['planning'], 'reload changed monthly state/history'
        assert before['backup']['state']['fxPlanning'] == restored, 'canonical backup lost monthly state'
        payload = json.dumps(before['backup'], ensure_ascii=False)
        page.evaluate(r"""text => {
          window.__monthlyImportAlerts=[];
          window.alert=m=>__monthlyImportAlerts.push(String(m));
          window.confirm=()=>true;
          S.fxPlanning.plan.extension={opaque:'overwritten only in disposable profile'};
          save();
          importFullBackupFile(new File([text],'synthetic-monthly.json',{type:'application/json'}));
        }""", payload)
        page.wait_for_function("() => S.fxPlanning.plan?.extension?.opaque==='roundtrip'")
        assert page.evaluate('() => structuredClone(S.fxPlanning)') == restored, 'real import changed financial plan'
        assert not page.evaluate('() => __monthlyImportAlerts.filter(s=>/inválido|não.*aplic|recusad/i.test(s))'), 'backup import failed'
        assert not errors, errors
        return {'reload': True, 'canonicalBackup': True, 'realFileImport': True, 'revision': restored['plan']['planningRevision']}
    finally:
        context.close()


def two_tabs_case(browser, url):
    context, first, errors, _ = open_page(browser, url)
    second = None
    try:
        first.evaluate('() => __monthlyTest.seed()')
        _, second, errors2, _ = open_page(browser, url, context=context)
        before = second.evaluate('() => JSON.stringify(S.fxPlanning)')
        saved = first.evaluate("() => JPWFx.state.fxPlanReviseFromMonth('2026-02',{rate:.03},'First tab')")
        assert saved['ok'], saved
        refused = second.evaluate("() => JPWFx.state.fxPlanClearMonth('2026-03','Stale second tab')")
        assert refused['ok'] is False and refused['persistido'] is False, refused
        assert second.evaluate('() => JSON.stringify(S.fxPlanning)') == before, 'stale tab contaminated memory'
        assert first.evaluate("() => JSON.parse(localStorage.getItem('jpwealth_v9_state')).fxPlanning.plan.current.monthOverrides['2026-02']") == .03
        assert first.evaluate("() => JSON.parse(localStorage.getItem('jpwealth_v9_state')).fxPlanning.plan.current.absentMonths?.['2026-03'] || null") is None
        assert not errors + errors2, errors + errors2
        return {'firstSaved': saved, 'staleTabRefused': refused}
    finally:
        context.close()


def ui_case(browser, url, artifacts):
    context, page, errors, _ = open_page(browser, url)
    page.set_default_timeout(8000)
    try:
        assert page.evaluate("() => {__monthlyTest.seed();return JPWNavigation.navigate('forex-planning');}")
        assert page.evaluate('JPWFx.ui.getView()') == 'table', 'canonical planning entry is not the monthly board'
        page.wait_for_selector('.fxp-month-table')
        field = lambda month, key: page.locator(f'[data-fxp-month="{month}"][data-fxp-field="{key}"]')
        action = lambda month, key: page.locator(f'[data-fxp-month="{month}"][data-fxp-month-action="{key}"]')
        row = lambda month: page.locator(f'[data-fxp-month-row="{month}"]')
        def click_action(month, key):
            button = action(month, key)
            if not button.is_visible():
                action(month, 'details').click()
            button.click()
        assert row('2026-02').locator('td').count() == 8, 'monthly fields are not in separate columns'
        assert action('2026-02', 'save').is_disabled()
        disk = page.evaluate("() => localStorage.getItem('jpwealth_v9_state')")
        writes = page.evaluate('() => __testPrimaryWrites')
        feb_rate = field('2026-02', 'rate')
        feb_rate.focus()
        page.evaluate("window.__originalMonthInput=document.querySelector('#fxpMonth-2026-02-rate')")
        feb_rate.fill('3')
        feb_rate.press('Escape')
        assert feb_rate.input_value() == '1'
        assert action('2026-02', 'save').is_disabled(), 'cell cancellation left a false dirty month'
        assert row('2026-02').locator('[data-fxp-dirty]').inner_text() == ''
        feb_rate.focus()
        feb_rate.fill('2')
        assert feb_rate.evaluate('el => el===window.__originalMonthInput'), 'typing replaced the active field'
        assert '1.060,50' in row('2026-02').inner_text(), 'dependent preview is not immediate'
        assert row('2026-02').locator('[data-fxp-dirty]').inner_text() == 'Não salvo'
        assert page.evaluate("() => localStorage.getItem('jpwealth_v9_state')") == disk
        feb_rate.press('Enter')
        assert page.evaluate('() => __testPrimaryWrites') == writes, 'Enter saved a financial fact'
        feb_rate.focus()
        feb_rate.fill('3')
        feb_rate.press('Escape')
        assert feb_rate.input_value() == '2', 'Escape did not cancel the current cell change'
        feb_rate.focus()
        feb_rate.evaluate('el=>el.setSelectionRange(0,1)')
        page.set_viewport_size({'width': 1024, 'height': 960})
        page.wait_for_timeout(120)
        assert page.evaluate("document.activeElement.id") == 'fxpMonth-2026-02-rate'
        assert feb_rate.input_value() == '2'
        page.evaluate('renderFxPlanning()')
        assert page.evaluate("document.activeElement.id") == 'fxpMonth-2026-02-rate'
        assert feb_rate.evaluate('el=>[el.selectionStart,el.selectionEnd]') == [0, 1]
        action('2026-02', 'cancel').click()
        assert float(field('2026-02', 'rate').input_value().replace(',', '.')) == 1
        assert action('2026-02', 'save').is_disabled()
        field('2026-02', 'rate').fill('2')
        field('2026-02', 'personalUsd').fill('0')
        field('2026-02', 'propUsd').fill('0')
        assert page.evaluate("() => localStorage.getItem('jpwealth_v9_state')") == disk
        action('2026-02', 'save').click()
        assert page.evaluate("S.fxPlanning.plan.current.monthOverrides['2026-02']") == .02
        assert page.evaluate('() => __testPrimaryWrites') == writes + 1, 'Save month dispatched more than one write'
        assert action('2026-02', 'save').is_disabled()
        click_action('2026-03', 'clear')
        assert row('2026-03').get_attribute('data-fxp-month-state') == 'ABSENT'
        assert row('2026-04').locator('[data-fxp-value="close"]').inner_text() == '—'
        for key in ('rate', 'personalUsd', 'propUsd'):
            field('2026-03', key).fill('0')
        action('2026-03', 'save').click()
        assert row('2026-03').get_attribute('data-fxp-month-state') == 'PROJECTED'
        assert row('2026-04').locator('[data-fxp-value="close"]').inner_text() != '—'

        # The new actual form starts blank; planned deposits never become actual.
        click_action('2026-01', 'actual')
        assert field('2026-01', 'rate').input_value() == '', 'planned return promoted to actual'
        field('2026-01', 'rate').fill('0')
        before = page.evaluate('() => __testPrimaryWrites')
        action('2026-01', 'finalize').click()
        assert page.evaluate('() => __testPrimaryWrites') == before, 'unchecked deposits finalized'
        assert 'depósito' in row('2026-01').locator('[data-fxp-error]').inner_text().lower()
        field('2026-01', 'contributionsConfirmed').check()
        action('2026-01', 'finalize').click()
        assert row('2026-01').get_attribute('data-fxp-month-state') == 'FINALIZED'
        assert row('2026-01').evaluate("el=>el.classList.contains('fxp-month-finalized')")
        assert field('2026-01', 'rate').count() == 0, 'finalized result remains editable'
        assert page.evaluate("JPWFx.engine.fxActualTimeline(JPWFx.state.fxActivePlan())[0].close") == 1000
        if not page.locator('#fxpReopenNote-2026-01').is_visible():
            action('2026-01', 'details').click()
        page.locator('#fxpReopenNote-2026-01').fill('Correct synthetic zero result')
        action('2026-01', 'reopen').click()
        assert row('2026-01').get_attribute('data-fxp-month-state') == 'REOPENED'
        click_action('2026-01', 'actual')
        field('2026-01', 'rate').fill('1')
        field('2026-01', 'contributionsConfirmed').check()
        action('2026-01', 'finalize').click()
        assert row('2026-01').get_attribute('data-fxp-month-state') == 'FINALIZED'
        assert page.evaluate("JPWFx.engine.fxActualTimeline(JPWFx.state.fxActivePlan())[0].close") == 1010

        # A surviving draft is exercised while all four layouts and five widths
        # change. This is a CSS/reflow matrix, not a claim of native zoom proof.
        field('2026-05', 'rate').fill('2,5')
        field('2026-05', 'rate').focus()
        page.evaluate("() => document.querySelectorAll('.fxp-month-detail').forEach(detail=>detail.open=false)")
        before = page.evaluate("() => ({financial:JSON.stringify(S.fxPlanning),writes:__testPrimaryWrites})")
        measurements = []
        for layout in ('sidebar', 'topbar', 'submenu', 'glass'):
            page.evaluate('layout=>mountNavigationLayout(layout)', layout)
            for width in (320, 390, 768, 1024, 1440):
                page.set_viewport_size({'width': width, 'height': 900})
                for theme in ('light', 'dark'):
                    page.evaluate("theme=>{document.documentElement.dataset.theme=theme;document.body.dataset.theme=theme}", theme)
                    page.wait_for_timeout(60)
                    values = page.evaluate(r"""() => {
                      const input=document.querySelector('#fxpMonth-2026-05-rate');
                      const row=document.querySelector('[data-fxp-month-row="2026-01"]');
                      const scroll=document.querySelector('.fxp-month-scroll');
                      const visible=element=>!!element&&element.getBoundingClientRect().width>0;
                      const controls=[...document.querySelectorAll('.fxp-month-row button,.fxp-month-row input')].filter(visible);
                      return {globalWidth:document.documentElement.scrollWidth,viewport:innerWidth,
                        boardWidth:scroll.clientWidth,boardScroll:scroll.scrollWidth,
                        rowDisplay:getComputedStyle(row).display,blue:getComputedStyle(row.querySelector('td')).backgroundColor,
                        commonHeight:document.querySelector('[data-fxp-month-row="2026-02"]').getBoundingClientRect().height,
                        draft:input.value,minHeight:Math.min(...controls.map(el=>el.getBoundingClientRect().height)),
                        active:document.activeElement.id,svg:!!document.querySelector('#fxpMainChart svg')};
                    }""")
                    assert values['globalWidth'] <= width + 2, (layout, width, theme, values)
                    assert values['draft'] == '2,5', 'resize or layout lost monthly draft'
                    assert values['active'] == 'fxpMonth-2026-05-rate', 'layout changed editing focus'
                    assert values['minHeight'] >= 43.5, 'monthly control is not accessible'
                    assert values['svg'], 'chart lost during resize'
                    if values['rowDisplay'] == 'table-row':
                        assert values['commonHeight'] <= 80, 'desktop row is no longer a compact monthly sheet'
                    if width < 768:
                        assert values['rowDisplay'] == 'grid', (layout, width, values)
                        assert values['boardScroll'] <= values['boardWidth'] + 2, 'mobile board globally scrolls'
                    measurements.append({'layout': layout, 'width': width, 'theme': theme, **values})
                    if layout == 'sidebar' and width in (390, 1440):
                        page.locator('.fxp-month-board').screenshot(path=str(artifacts / f'monthly-{width}-{theme}.png'))
        assert page.evaluate("() => ({financial:JSON.stringify(S.fxPlanning),writes:__testPrimaryWrites})") == before
        assert not errors, errors
        return {'directEdit': True, 'enterDoesNotSave': True, 'escapeCellCancel': True,
                'sameEditorWhileTyping': True, 'cancelRestoresSaved': True,
                'explicitZeroActual': True, 'blueFinalizedProtected': True, 'reopenAndRefinalize': True,
                'matrix': measurements, 'nativeBrowserZoom200': 'NOT_RUN'}
    except Exception:
        page.screenshot(path=str(artifacts / 'monthly-ui-failure.png'), full_page=True)
        failure = page.evaluate("""() => ({view:JPWFx.ui.getView(),active:document.activeElement.id,
          details:[...document.querySelectorAll('.fxp-month-detail')].map(e=>({id:e.id,open:e.open})),
          months:[...document.querySelectorAll('[data-fxp-month-row]')].map(e=>({month:e.dataset.fxpMonthRow,state:e.dataset.fxpMonthState,text:e.innerText})),
          errors:[...document.querySelectorAll('.fxp-month-error')].map(e=>e.innerText),financial:JSON.stringify(S.fxPlanning)})""")
        (artifacts / 'monthly-ui-failure.json').write_text(json.dumps(failure, ensure_ascii=False, indent=2))
        raise
    finally:
        context.close()


def old_forms_ui_case(browser, url):
    context, page, errors, _ = open_page(browser, url)
    page.set_default_timeout(8000)
    try:
        page.evaluate("() => {__monthlyTest.seed();JPWNavigation.navigate('forex-planning');JPWFx.ui.selectView('table');}")
        month = '2026-02'
        rate = page.locator(f'[data-fxp-month="{month}"][data-fxp-field="rate"]')
        rate.fill('2xyz')
        assert page.locator(f'[data-fxp-month-row="{month}"] [data-fxp-value="close"]').inner_text() == '—', 'invalid suffix used parseFloat'
        disk = page.evaluate("localStorage.getItem('jpwealth_v9_state')")
        writes = page.evaluate('__testPrimaryWrites')
        page.locator(f'[data-fxp-month="{month}"][data-fxp-month-action="save"]').click()
        assert page.evaluate("localStorage.getItem('jpwealth_v9_state')") == disk
        assert page.evaluate('__testPrimaryWrites') == writes
        assert rate.input_value() == '2xyz', 'rejected save lost draft'
        page.locator(f'[data-fxp-month="{month}"][data-fxp-month-action="cancel"]').click()
        page.evaluate("() => {__monthlyTest.finalize('2026-01');JPWFx.ui.selectView('actuals');}")
        page.locator('#fxpActMonth').select_option('2026-01')
        assert page.locator('#fxpActValue').is_disabled(), 'legacy result form bypasses protection'
        assert page.locator('#fxpActBtn').is_disabled()
        assert page.locator('#fxpActConfirmed').is_disabled()
        page.locator('#fxpCMonth').fill('2026-01')
        assert page.locator('#fxpCBtn').is_disabled(), 'legacy deposit form bypasses protection'
        page.locator('#fxpActMonth').select_option('2026-02')
        assert page.locator('#fxpActValue').is_enabled()
        page.locator('#fxpActValue').fill('0')
        before = page.evaluate('__testPrimaryWrites')
        page.locator('#fxpActBtn').click()
        assert page.evaluate('__testPrimaryWrites') == before, 'legacy finalize omitted deposit check'
        assert 'depósito' in page.locator('#fxpActErr').inner_text().lower()
        page.locator('#fxpActConfirmed').check()
        page.locator('#fxpActBtn').click()
        assert page.evaluate("S.fxPlanning.plan.actuals['2026-02'].closureStatus") == 'FINALIZED'
        assert not errors, errors
        return {'strictSuffix': True, 'rejectedDraftPreserved': True, 'legacyFinalProtected': True,
                'legacyDepositProtected': True, 'legacyExplicitCheckRequired': True}
    finally:
        context.close()


def large_text_ui_case(browser, url, artifacts):
    context, page, errors, _ = open_page(browser, url)
    try:
        page.evaluate("""() => {
          __monthlyTest.seed({initialBalanceUsd:1234567890.125,defaultMonthlyReturn:-.025,
            recurringContributions:{personalUsd:1234567.89,propUsd:0}});
          JPWNavigation.navigate('forex-planning');JPWFx.ui.selectView('table');
        }""")
        before = page.evaluate("() => ({financial:JSON.stringify(S.fxPlanning),writes:__testPrimaryWrites})")
        values = []
        for width in (320, 390, 1440):
            page.set_viewport_size({'width': width, 'height': 900})
            for scale in (1, 2):
                page.evaluate("scale=>document.documentElement.style.setProperty('--fs-scale',String(scale))", scale)
                page.wait_for_timeout(100)
                measurements = page.evaluate("""() => ({globalWidth:document.documentElement.scrollWidth,
                  width:innerWidth,values:[...document.querySelector('[data-fxp-month-row="2026-01"]').querySelectorAll('[data-fxp-value]')].map(el=>({text:el.innerText,
                    width:el.clientWidth,scroll:el.scrollWidth,overflow:getComputedStyle(el).textOverflow,font:getComputedStyle(el).fontSize}))})""")
                assert measurements['globalWidth'] <= width + 2, (width, scale, measurements)
                assert all(v['overflow'] != 'ellipsis' for v in measurements['values']), 'financial value ellipsis'
                assert all(v['scroll'] <= v['width'] + 1 for v in measurements['values']), 'financial span clipped'
                values.append({'width': width, 'scale': scale, **measurements})
        assert page.evaluate("() => ({financial:JSON.stringify(S.fxPlanning),writes:__testPrimaryWrites})") == before
        assert not errors, errors
        return {'cssTextAmplification': values, 'nativeBrowserZoom': 'NOT_RUN'}
    finally:
        context.close()



def precise_editable_rates_ui_case(browser, url):
    """Editing another field must not re-parse untouched rates into rounded doubles."""
    context, page, errors, _ = open_page(browser, url)
    page.set_default_timeout(8000)
    evidence = []
    try:
        variants = ('hidden monthly overrides', 'FX only', 'recurring deposit only',
                    'note only', 'one monthly override')
        for variant in variants:
            page.evaluate("""() => {
              __monthlyTest.seed();__monthlyTest.finalize('2026-01');
              __monthlyTest.yes(JPWFx.state.fxPlanReviseFromMonth('2026-02',
                {rate:.12345678901234567,personalUsd:11.11,propUsd:5.55},'Precise synthetic February').ok);
              __monthlyTest.yes(JPWFx.state.fxPlanReviseFromMonth('2026-03',
                {rate:.023456789012345,personalUsd:10,propUsd:5},'Precise synthetic March').ok);
              __monthlyTest.yes(JPWFx.state.fxPlanClearMonth('2026-04','Synthetic gap').ok);
              __monthlyTest.yes(JPWFx.state.fxPlanReviseAssumptions({...S.fxPlanning.plan.current,
                defaultMonthlyReturn:.12345678901234567,yearOverrides:{'2026':.12345678901234567}},
                'Precise synthetic defaults').ok);
              JPWNavigation.navigate('forex-planning');JPWFx.ui.selectView('table');
              window.__precisionBefore=structuredClone(S.fxPlanning.plan);
              if(!window.__precisionOriginalForecast){
                window.__precisionOriginalForecast=JPWFx.engine.fxForecastTimeline;
                JPWFx.engine.fxForecastTimeline=function(...args){
                  const rows=window.__precisionOriginalForecast.apply(this,args);
                  if(args[1]?.assumptions)window.__precisionPreview={assumptions:structuredClone(args[1].assumptions),rows:structuredClone(rows)};
                  return rows;
                };
              }
              window.__precisionPreview=null;renderFxPlanning();
            }""")
            page.locator('#fxpGeneralAssumptions').evaluate('el=>el.open=true')
            writes = page.evaluate('__testPrimaryWrites')
            if variant == 'hidden monthly overrides':
                page.locator('#fxpEditRate').fill('2')
                page.locator('#fxpEditMonthOvr').evaluate("el=>{el.value='';el.dispatchEvent(new Event('input',{bubbles:true}))}")
            elif variant == 'FX only':
                page.locator('#fxpEditProjFx').fill('5.5')
            elif variant == 'recurring deposit only':
                page.locator('#fxpEditRecPersonal').fill('20.5')
            elif variant == 'note only':
                page.locator('#fxpEditNote').fill('Synthetic note only')
            else:
                page.locator('#fxpEditMonthOvr').evaluate("""el=>{
                  el.value=el.value.split(';').map(v=>v.trim().startsWith('2026-02=')?'2026-02=2.5%':v).join(';');
                  el.dispatchEvent(new Event('input',{bubbles:true}));
                }""")
            assert page.evaluate('__testPrimaryWrites') == writes, 'premise preview wrote financial state'
            assert page.evaluate('!!window.__precisionPreview'), 'real forecast did not receive premise preview'
            page.locator('#fxpReviseBtn').click()
            result = page.evaluate("""variant=>{
              const before=__precisionBefore,after=S.fxPlanning.plan,t=__monthlyTest;
              const b=before.current,a=after.current,p=__precisionPreview;
              t.yes(__testPrimaryWrites>=1);
              t.same(before.actuals,after.actuals,'actuals');t.same(before.baseline,after.baseline,'baseline');
              t.same(b.absentMonths,a.absentMonths,'absence');
              t.same(b.plannedContributions,a.plannedContributions,'monthly deposits');
              const premiseKeys=['defaultMonthlyReturn','yearOverrides','monthOverrides','recurringContributions','projectedFxRate','absentMonths','plannedContributions'];
              for(const key of premiseKeys)t.same(p.assumptions[key],a[key],'preview/writer assumptions '+key);
              t.same(p.rows,JPWFx.engine.fxForecastTimeline(JPWFx.state.fxActivePlan()),'preview/writer rows');
              for(const key of Object.keys(b.yearOverrides))t.yes(Object.is(b.yearOverrides[key],a.yearOverrides[key]),'year precision lost');
              for(const key of Object.keys(b.monthOverrides)){
                const expected=variant==='one monthly override'&&key==='2026-02'?.025:b.monthOverrides[key];
                t.yes(Object.is(expected,a.monthOverrides[key]),'month precision lost: '+key);
              }
              t.yes(Object.is(variant==='hidden monthly overrides'?.02:b.defaultMonthlyReturn,a.defaultMonthlyReturn),'default precision lost');
              if(variant==='FX only')t.yes(a.projectedFxRate===5.5,'FX change not saved');
              if(variant==='recurring deposit only')t.yes(a.recurringContributions.personalUsd===20.5,'deposit change not saved');
              if(variant==='note only')t.yes(after.revisions[after.revisions.length-1].note==='Synthetic note only','note change not saved');
              return {variant,exactRateIdentity:true,previewWriterParity:true,original:b,current:a,writes:__testPrimaryWrites};
            }""", variant)
            assert result['writes'] == writes + 1, 'general premise save did not write exactly once'
            evidence.append(result)

        for mode in ('monthly board', 'advanced monthly form'):
            page.evaluate("""() => {
              __monthlyTest.seed();
              __monthlyTest.yes(JPWFx.state.fxPlanReviseFromMonth('2026-02',
                {rate:.12345678901234567,personalUsd:10,propUsd:5},'Precise synthetic monthly rate').ok);
              JPWFx.ui.selectView('table');renderFxPlanning();
              window.__precisionOriginalMonthly=S.fxPlanning.plan.current.monthOverrides['2026-02'];
            }""")
            writes = page.evaluate('__testPrimaryWrites')
            if mode == 'monthly board':
                page.locator('#fxpMonth-2026-02-personalUsd').fill('21')
                page.locator('[data-fxp-month="2026-02"][data-fxp-month-action="save"]').click()
            else:
                page.locator('#fxpTimelineDisclosure').evaluate('el=>el.open=true')
                page.locator('#fxpRowMonth').select_option('2026-02')
                page.locator('#fxpRowPersonal').fill('21')
                page.locator('#fxpRowNote').fill('Synthetic deposit-only correction')
                page.locator('#fxpRowSave').click()
            result = page.evaluate("""() => ({
              rate:S.fxPlanning.plan.current.monthOverrides['2026-02'],
              exact:Object.is(__precisionOriginalMonthly,S.fxPlanning.plan.current.monthOverrides['2026-02']),
              personalUsd:S.fxPlanning.plan.current.plannedContributions['2026-02'].personalUsd,
              writes:__testPrimaryWrites})""")
            assert result['exact'], 'deposit-only edit changed the untouched monthly rate'
            assert result['personalUsd'] == 21 and result['writes'] == writes + 1, (mode,result,writes,page.locator('#fxpTimelineErr').inner_text())
            evidence.append({'variant': mode, **result})

        for mode in ('monthly actual note', 'legacy actual note'):
            page.evaluate("""() => {
              __monthlyTest.seed();
              __monthlyTest.finalize('2026-01',{inputType:'rate',returnRate:.12345678901234567});
              __monthlyTest.yes(JPWFx.state.fxPlanReopenMonth('2026-01','Synthetic note correction').ok);
              window.__precisionOriginalActual=S.fxPlanning.plan.actuals['2026-01'].returnRate;
              JPWFx.ui.selectView('table');renderFxPlanning();
            }""")
            writes = page.evaluate('__testPrimaryWrites')
            if mode == 'monthly actual note':
                page.locator('[data-fxp-month="2026-01"][data-fxp-month-action="actual"]').click()
                page.locator('#fxpMonth-2026-01-note').fill('Synthetic actual note only')
                page.locator('#fxpMonth-2026-01-contributionsConfirmed').check()
                page.locator('[data-fxp-month="2026-01"][data-fxp-month-action="finalize"]').click()
            else:
                page.evaluate("JPWFx.ui.selectView('actuals')")
                page.locator('#fxpActMonth').select_option('2026-01')
                page.locator('#fxpActNotes').fill('Synthetic actual note only')
                page.locator('#fxpActConfirmed').check()
                page.locator('#fxpActBtn').click()
            result = page.evaluate("""() => ({
              exact:Object.is(__precisionOriginalActual,S.fxPlanning.plan.actuals['2026-01'].returnRate),
              rate:S.fxPlanning.plan.actuals['2026-01'].returnRate,
              notes:S.fxPlanning.plan.actuals['2026-01'].notes,
              closureStatus:S.fxPlanning.plan.actuals['2026-01'].closureStatus,writes:__testPrimaryWrites})""")
            assert result['exact'], 'actual-note edit changed the original rate'
            assert result['notes'] == 'Synthetic actual note only' and result['closureStatus'] == 'FINALIZED'
            assert result['writes'] == writes + 1, 'actual note reconfirmation did not write exactly once'
            evidence.append({'variant': mode, **result})
        assert not errors, errors
        assert_fixture_requests(context)
        return {'strictDoubleIdentity': True, 'realEnginePreviewAndWriterParity': True, 'variants': evidence}
    finally:
        context.close()


def unknown_finalization_repaint_ui_case(browser, url, artifacts):
    """A real write with an unknown receipt must never appear confirmed after repaint."""
    context, page, errors, _ = open_page(browser, url)
    page.set_default_timeout(8000)
    try:
        page.evaluate("() => {__monthlyTest.seed();JPWNavigation.navigate('forex-planning');JPWFx.ui.selectView('table');}")
        page.locator('[data-fxp-month="2026-01"][data-fxp-month-action="details"]').click()
        page.locator('[data-fxp-month="2026-01"][data-fxp-month-action="actual"]').click()
        page.locator('#fxpMonth-2026-01-rate').fill('0')
        page.locator('#fxpMonth-2026-01-contributionsConfirmed').check()
        page.evaluate("""() => {
          window.__unknownBefore=structuredClone(S.fxPlanning.plan);
          window.__unknownBeforeRows=JPWFx.engine.fxMonthlyTimeline(JPWFx.state.fxActivePlan());
          window.__unknownSaveCalls=0;window.__unknownFinalizeCalls=0;window.__unknownCharts=[];
          const realSave=window.save,realFinalize=JPWFx.state.fxPlanFinalizeMonth;
          window.save=function(...args){__unknownSaveCalls++;window.__unknownPhysicalReceipt=realSave.apply(this,args);return undefined;};
          JPWFx.state.fxPlanFinalizeMonth=function(...args){__unknownFinalizeCalls++;window.__unknownCommandReceipt=realFinalize.apply(this,args);return __unknownCommandReceipt;};
          const realChart=JPWFx.charts.fxDrawMainChart;
          JPWFx.charts.fxDrawMainChart=function(...args){
            __unknownCharts.push({actuals:structuredClone(args[1].actuals),rows:JPWFx.engine.fxMonthlyTimeline(args[1])});
            return realChart.apply(this,args);
          };
        }""")
        writes = page.evaluate('__testPrimaryWrites')
        page.locator('[data-fxp-month="2026-01"][data-fxp-month-action="finalize"]').click()

        def reading(stage):
            result = page.evaluate("""stage=>{
              const row=document.querySelector('[data-fxp-month-row="2026-01"]'),root=document.getElementById('fxPlanningRoot');
              const disk=JSON.parse(localStorage.getItem('jpwealth_v9_state'));
              const notice=row.closest('.fxp-month-board').querySelector('.fxp-read-warning');
              return {stage,receipt:__unknownCommandReceipt,physicalReceipt:__unknownPhysicalReceipt,
                globalUnknown:jpWealthPersistenceOutcomeIsUnknown(),reading:root.dataset.fxpReading,
                state:row.dataset.fxpMonthState,classes:row.className,
                status:row.querySelector('[data-fxp-status]').innerText,dirty:row.querySelector('[data-fxp-dirty]').innerText,
                error:row.querySelector('[data-fxp-error]').innerText,
                rate:document.getElementById('fxpMonth-2026-01-rate').value,
                checked:document.getElementById('fxpMonth-2026-01-contributionsConfirmed').checked,
                finalizeDisabled:row.querySelector('[data-fxp-month-action="finalize"]').disabled,
                localNotice:notice?.innerText,localNoticeVisible:!!notice?.getClientRects().length,
                unqualifiedConfirmed:root.innerText.includes('Realizado confirmado'),
                attemptedMemoryStatus:S.fxPlanning.plan.actuals['2026-01']?.closureStatus,
                attemptedDiskStatus:disk.fxPlanning.plan.actuals['2026-01']?.closureStatus,
                writes:__testPrimaryWrites,saveCalls:__unknownSaveCalls,finalizeCalls:__unknownFinalizeCalls,
                charts:structuredClone(__unknownCharts)};
            }""", stage)
            assert result['receipt']['ok'] is False and result['receipt']['persistido'] is None
            assert result['globalUnknown'] and result['reading'] == 'unknown', 'unknown receipt was silently resolved'
            assert result['state'] == 'UNKNOWN' and 'fxp-month-finalized' not in result['classes'], 'unknown attempt presented as blue confirmed actual'
            assert result['status'] == 'Gravação indeterminada' and result['dirty'] == 'Não salvo'
            assert 'indeterminada' in result['error'].lower(), 'local failure message disappeared'
            assert result['rate'] == '0' and result['checked'], 'unknown receipt lost the editing draft'
            assert result['finalizeDisabled'], 'unknown receipt left repeat finalization enabled'
            assert result['localNoticeVisible'] and 'indeterminad' in result['localNotice'].lower(), 'reading qualified only by an off-screen global banner'
            assert not result['unqualifiedConfirmed'], 'reading claims confirmed actual after unknown receipt'
            assert result['attemptedMemoryStatus'] == result['attemptedDiskStatus'] == 'FINALIZED', 'failure adapter did not delegate the physical write'
            assert result['writes'] == writes + 1 and result['saveCalls'] == result['finalizeCalls'] == 1, 'presentation retried the write'
            assert result['charts'], 'unknown presentation was not checked against the real chart producer'
            for chart in result['charts']:
                assert chart['actuals'] == {}, 'tentative actual entered confirmed chart data'
                assert chart['rows'] == page.evaluate('window.__unknownBeforeRows'), 'unknown repaint changed confirmed chart values'
            return result

        stages = [reading('immediate rejected receipt')]
        page.evaluate('renderFxPlanning()')
        stages.append(reading('explicit read-only repaint'))
        for view in ('overview', 'actuals', 'planning'):
            page.evaluate('view=>JPWFx.ui.selectView(view)', view)
            assert page.evaluate('jpWealthPersistenceOutcomeIsUnknown()'), 'view consultation acknowledged unknown receipt'
            assert page.evaluate('__testPrimaryWrites') == writes + 1
            assert not page.evaluate("document.getElementById('fxPlanningRoot').innerText.includes('Realizado confirmado')")
        page.evaluate("JPWFx.ui.selectView('table')")
        stages.append(reading('table return after other planning views'))
        page.evaluate("document.querySelector('[data-fxp-month=\"2026-01\"][data-fxp-month-action=\"finalize\"]').click()")
        stages.append(reading('disabled repeat action does not dispatch'))
        page.locator('.fxp-month-board').screenshot(path=str(artifacts / 'unknown-finalization-after-repaint.png'))
        assert not errors, errors
        assert_fixture_requests(context)
        return {'adapter': 'real physical writer delegates, unknown return receipt',
                'unexpectedRepeatWrites': 0, 'confirmedChartsUsePreviousReading': True, 'stages': stages}
    finally:
        context.close()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument('--artifacts', type=Path, default=Path(__file__).resolve().parent / '.artifacts' / 'fx-monthly-board')
    parser.add_argument('--baseline', action='store_true')
    parser.add_argument('--skip-ui', action='store_true')
    parser.add_argument('--only', help='Run cases whose name contains this string')
    args = parser.parse_args()
    args.root = args.root.resolve()
    args.artifacts = args.artifacts.resolve()
    os.chdir(args.root)
    args.artifacts.mkdir(parents=True, exist_ok=True)
    hashes = {path: hashlib.sha256((args.root / path).read_bytes()).hexdigest() for path in SOURCE_PATHS}
    report = {'mode': 'BASELINE_CHARACTERIZATION' if args.baseline else 'CANDIDATE_CONTRACT',
              'data': 'SYNTHETIC_ONLY', 'sourcesBefore': hashes, 'cases': [], 'nativeExcel': 'NOT_RUN'}
    server = BrowserFixtureServer(('127.0.0.1', 0), QuietHandler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    url = f'http://127.0.0.1:{server.server_port}/index.html'
    def case(name, fn):
        if args.only and args.only not in name:
            return
        started = time.monotonic()
        try:
            evidence = fn()
            item = {'name': name, 'status': 'OBSERVED' if args.baseline else 'PASS', 'evidence': evidence}
        except Exception as error:
            item = {'name': name, 'status': 'PRODUCT_FAIL', 'error': str(error), 'traceback': traceback.format_exc()}
        item['seconds'] = round(time.monotonic() - started, 3)
        report['cases'].append(item)
        print(f"[{item['status']}] {name}", flush=True)
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch()
            report['browser'] = browser.version
            for name, expression in (BASELINE_CASES if args.baseline else DOMAIN_CASES).items():
                case(name, lambda expression=expression: run_js_case(browser, url, expression))
            if not args.baseline:
                case('reload canonical backup and actual FileReader import', lambda: reload_backup_case(browser, url))
                case('two disposable tabs reject stale writer without overwriting', lambda: two_tabs_case(browser, url))
                if not args.skip_ui:
                    case('monthly board interaction keyboard and responsive layout', lambda: ui_case(browser, url, args.artifacts))
                    case('strict monthly parser and old actual/deposit forms guards', lambda: old_forms_ui_case(browser, url))
                    case('large values and text scale at narrow widths', lambda: large_text_ui_case(browser, url, args.artifacts))
                    case('editable rates retain full original precision and preview writer parity', lambda: precise_editable_rates_ui_case(browser, url))
                    case('unknown finalization retains draft and qualifies read-only repaint', lambda: unknown_finalization_repaint_ui_case(browser, url, args.artifacts))
            browser.close()
    finally:
        server.shutdown()
    report['sourcesAfter'] = {path: hashlib.sha256((args.root / path).read_bytes()).hexdigest() for path in SOURCE_PATHS}
    report['sourcesUnchanged'] = report['sourcesBefore'] == report['sourcesAfter']
    failures = [case for case in report['cases'] if case['status'] == 'PRODUCT_FAIL']
    report['status'] = 'PRODUCT_FAIL' if failures or not report['sourcesUnchanged'] else 'OBSERVED' if args.baseline else 'PASS'
    target = args.artifacts / ('baseline-monthly.json' if args.baseline else 'candidate-monthly.json')
    target.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f"{report['status']}: {len(report['cases'])-len(failures)}/{len(report['cases'])}; receipt={target}")
    raise SystemExit(1 if report['status'] == 'PRODUCT_FAIL' else 0)


if __name__ == '__main__':
    main()
