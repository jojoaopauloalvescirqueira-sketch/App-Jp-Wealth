#!/usr/bin/env python3
"""AUD-03..06: synthetic regression oracles against original source in Node VM.

No browser profile, repository write, network, policy activation or real data.
The save double checks command atomicity in RAM only; it does not prove browser
persistence. Assertions are desired behavior, so unpatched baseline exits1.
"""
import argparse,hashlib,json,os,shutil,subprocess,sys
from pathlib import Path

PATHS=['src/js/00-core/00-forex-policy.js','src/js/10-domain/00-forex-engine.js',
 'src/js/00-core/01-risk-profiles.js','src/js/00-core/03-default-state.js',
 'src/js/00-core/05-helpers.js','src/js/10-domain/00-forex-state.js',
 'src/js/10-domain/02-risk-calculations.js','src/js/10-domain/12-personal-finance.js',
 'src/js/10-domain/07-reserve-requirements.js','src/js/30-accounting/03-mei-jp.js',
 'src/js/30-accounting/05-fx-planning/01-fx-model.js','src/js/30-accounting/05-fx-planning/02-fx-engine.js',
 'src/js/30-accounting/05-fx-planning/03-fx-state.js','src/js/30-accounting/05-fx-planning/05-fx-ui.js']
EXTRA=['src/js/00-core/04-persistence.js','src/js/manifest.json']
NODE=r'''
const fs=require('fs'),vm=require('vm'),assert=require('assert'),crypto=require('crypto');
const input=JSON.parse(fs.readFileSync(0,'utf8')),cases=[];
function harness(){
 let writes=0,disk=null;
 const c={console,Date,Math,JSON,Intl,structuredClone,crypto:crypto.webcrypto,setTimeout,clearTimeout,
  addEventListener(){},document:{getElementById(){return null;},querySelectorAll(){return [];},addEventListener(){}},
  jpwWorkspaceDraftProviders:new Map(),JPWWorkspaceDrafts:{registerRestorer(){}},
  instFor(){return null;},quarantineActive(){return false;},dgLogChange(){},hideStaleSavedTag(){},
  jpWealthPersistenceEpoch(){return 1;},jpWealthPersistenceOutcomeIsUnknown(){return false;},
  markJPWealthPersistenceOutcomeUnknown(){throw Error('Unexpected unknown result in synthetic fixture');},
  save(){writes++;disk=JSON.stringify(c.S);return true;}};
 c.window=c;c.globalThis=c;vm.createContext(c);
 for(const p of input.paths){
  if(p==='src/js/00-core/05-helpers.js')c.S=vm.runInContext('structuredClone(DEFAULTS)',c);
  vm.runInContext(input.sources[p],c,{filename:p});
 }
 const persistence=input.sources['src/js/00-core/04-persistence.js'];
 const from=persistence.indexOf('function personalFinanceIsEmpty(pf){'),to=persistence.indexOf('// ---- Alladin: guarda estrutural de boot');
 if(from<0||to<=from)throw Error('PF normalizer extraction unavailable');
 vm.runInContext(persistence.slice(from,to),c,{filename:'04-persistence.js PF normalizer only'});
 return {c,run:s=>vm.runInContext(s,c),snapshot:()=>({state:JSON.stringify(c.S),writes,disk})};
}
function same(a,b,message){assert.deepStrictEqual(JSON.parse(JSON.stringify(a)),JSON.parse(JSON.stringify(b)),message);}
function setupOk(result,label){if(result?.ok!==true)throw Error(label+': '+JSON.stringify(result));}
function test(name,fn){
 let observed={};
 try{const h=harness();fn(h,observed);cases.push({name,status:'PASS',observed});}
 catch(e){cases.push({name,status:e instanceof assert.AssertionError?'PRODUCT_FAIL':'TEST_HARNESS_FAIL',error:e.message,observed});}
}
function pf(h,value,expense=false){
 const m={createdAt:'2026-10-12T12:00:00Z',incomes:expense?[]:[{id:'SYNTH-INCOME',name:'Synthetic',projectedAmount:null,receivedAmount:value,status:'PROJETADA',ruleId:null}],expenses:expense?[{id:'SYNTH-EXPENSE',name:'Synthetic',targetAmount:null,expectedAmount:null,executedCash:100,executedCard:value,status:'PENDENTE'}]:[],debtSnapshots:[],allocations:[],notes:[]};
 h.c.S.personalFinance.months={'2026-10':m};h.run('personalFinanceNormalizeState()');return m;
}
for(const [label,value] of [['string','invalid'],['decimal',1.5],['unsafe',Number.MAX_SAFE_INTEGER+1],['negative',-1]]){
 test('AUD03 income '+label+' cannot be COMPLETE', (h,o)=>{
  pf(h,value);const before=h.snapshot();o.summary=h.run("pfMonthSummary(S.personalFinance.months['2026-10'])");o.metric=h.run("pfCompMetrics('2026-10').receita");
  o.fact=h.c.S.personalFinance.months['2026-10'].incomes[0].receivedAmount;
  assert.equal(o.summary.incomeCoverage.completa,false);assert.equal(o.summary.realizedSurplus,null);assert.notEqual(o.metric.status,'COMPLETE');
  assert.strictEqual(o.fact,value);same(before,h.snapshot(),'PF read changed fixture');
 });
 test('AUD03 expense '+label+' cannot be COMPLETE', (h,o)=>{
  pf(h,value,true);const before=h.snapshot();o.summary=h.run("pfMonthSummary(S.personalFinance.months['2026-10'])");o.metric=h.run("pfCompMetrics('2026-10').despesa");
  assert.equal(o.summary.expenseCoverage.completa,false);assert.equal(o.summary.realizedSurplus,null);assert.notEqual(o.metric.status,'COMPLETE');
  assert.equal(o.summary.knownExecutedExpenses,100);assert.strictEqual(h.c.S.personalFinance.months['2026-10'].expenses[0].executedCard,value);same(before,h.snapshot(),'PF read changed fixture');
 });
}
for(const [label,value,complete] of [['absent',null,false],['zero',0,true]])test('AUD03 '+label+' remains distinct',(h,o)=>{
 pf(h,value);o.summary=h.run("pfMonthSummary(S.personalFinance.months['2026-10'])");assert.equal(o.summary.incomeCoverage.completa,complete);assert.strictEqual(o.summary.realizedSurplus,complete?0:null);
});
function account(h,{type='MESTRE',currency='USD',startedAt='2026-10-12',observe=true,nominal=10000}={}){
 const id='SYNTH-'+type+'-'+currency;
 h.c.S.accounts=[{forexAccountId:id,nome:'SYNTHETIC '+type,platformCurrency:currency,tipo:type}];
 setupOk(h.c.JPWForex.state.recordAccountPeriod({accountId:id,startedAt,currency,si:10000,openingBook:10000,source:'SYNTHETIC audit',activateCurrentPeriod:true},{reason:'SYNTHETIC period'}),'prepare period');
 const periodId=h.c.S.forex.accountContexts.accounts[id].currentPeriodId;
 setupOk(h.c.JPWForex.state.selectOperationalContext(id,periodId),'select scope');
 const facts={accountIndex:0,periodId,si:10000,equity:10000,currency,usdToAccountRate:currency==='USD'?1:.9,capitalNominal:nominal,netCashflow:0,cashflowAdjustmentRecorded:true,source:'SYNTHETIC broker',observedAt:'2026-10-12T12:00:00Z'};
 if(observe)setupOk(h.c.JPWForex.state.recordAccountFacts(facts,{reason:'SYNTHETIC observation'}),'observe account');
 return {id,periodId,facts};
}
for(const type of ['SATÉLITE','PRÓPRIA','MESTRE'])test('AUD04 '+type+' retains canonical FCR',(h,o)=>{
 account(h,{type});const before=h.snapshot(),model=h.c.JPWForex.state.read(),panel=h.c.JPWFx.state.fxReservePanelData();
 o.canonical=model.metrics.fcrRequirement;o.panel=panel;
 same(panel.requirements.fcr,model.metrics.fcrRequirement,'planning rewrote canonical FCR result');
 assert.strictEqual(panel.fcrReq,model.metrics.fcrRequirement.status==='OK'?model.metrics.fcrRequirement.value:null);
 assert.strictEqual(panel.status,'PENDING_GOVERNANCE');same(before,h.snapshot(),'reserve read changed fixture');
});
test('AUD04 nominal conflict findings retained',(h,o)=>{
 const a=account(h);setupOk(h.c.JPWForex.state.recordReserves({capitalNominal:9000,fcrConstituted:0,feoConstituted:0,sixMonthExpenseAmount:0,source:'SYNTHETIC conflicts'},{target:{accountId:a.id,periodId:a.periodId},reason:'SYNTHETIC reserve conflict'}),'reserve conflict');
 const model=h.c.JPWForex.state.read(),panel=h.c.JPWFx.state.fxReservePanelData();o.canonical=model.metrics.fcrRequirement;o.panel=panel;
 assert.strictEqual(panel.fcrReq,null);same(panel.requirements.fcr,model.metrics.fcrRequirement,'canonical conflict result lost');
 for(const f of model.metrics.fcrRequirement.findings)assert(panel.findings.some(p=>p.code===f.code),'canonical finding lost '+f.code);assert.equal(panel.status,'PENDING_GOVERNANCE');
});
for(const currency of ['USD','EUR','BRL'])test('AUD04 '+currency+' displayed without implied conversion',(h,o)=>{
 account(h,{currency});const panel=h.c.JPWFx.state.fxReservePanelData();h.c.syntheticPanel=panel;
 o.html=h.run('fxpReservesHTML(syntheticPanel)');o.expectedAmount=h.run(`fmtForexMoney(2200,{currency:${JSON.stringify(currency)}})`);o.panelCurrency=panel.currency;
 assert.equal(panel.currency,currency,'planning reserve currency was discarded');assert(o.html.includes(o.expectedAmount),'reserve UI changed currency or value');
 if(currency!=='USD')assert(!o.html.includes('$2.200,00</td>'),'foreign reserve labeled USD');
});
test('AUD04 absent equity keeps factual reserves and currency',(h,o)=>{
 const a=account(h,{currency:'EUR',observe:false});setupOk(h.c.JPWForex.state.recordReserves({capitalNominal:null,fcrConstituted:0,feoConstituted:500,source:'SYNTHETIC factual reserves'},{target:{accountId:a.id,periodId:a.periodId},reason:'SYNTHETIC factual reserve'}),'reserve facts');
 const m=h.c.JPWForex.state.read(),panel=h.c.JPWFx.state.fxReservePanelData();o.canonical=m.metrics.fcrRequirement;o.panel=panel;
 assert.equal(panel.currency,'EUR');assert.strictEqual(panel.fcrCur,0);assert.strictEqual(panel.feoCur,500);same(panel.requirements.fcr,m.metrics.fcrRequirement);assert.equal(panel.status,'PENDING_GOVERNANCE');
});
function mei(h){h.c.S.mei={...h.c.S.mei,enabled:true,history:[],cid:{base:.01,longevity:.01,high_longevity:.01,high_longevity_plus:.01},seedMode:'fixed',fixedSeed:'SYNTHETIC-AUDIT',simulationCount:1000};}
for(const profile of ['longevity','high_longevity','high_longevity_plus'])test('AUD05 '+profile+' null reference cannot simulate',(h,o)=>{
 mei(h);const before=h.snapshot();o.calibration=h.run(`meiCalibration(${JSON.stringify(profile)})`);o.simulation=h.run(`runMEIMonteCarlo({profileKey:${JSON.stringify(profile)},startingEquity:10000,horizonMonths:1,simulationCount:1000})`);
 assert.equal(o.calibration.enabled,false,'UI calibration advertised unavailable reference');assert.equal(o.simulation.enabled,false);assert.equal(o.simulation.medianPath,undefined,'unavailable reference generated trajectory');same(before,h.snapshot(),'MEI changed fixture');
});
test('AUD05 Base finite reference still simulates',(h,o)=>{mei(h);const r=h.run("runMEIMonteCarlo({profileKey:'base',startingEquity:10000,horizonMonths:1,simulationCount:1000})");o.result={enabled:r.enabled,muUsed:r.muUsed,logDrift:r.logDrift};assert.equal(r.enabled,true);assert.equal(r.muUsed,.035);assert.equal(r.medianPath.length,2);});
test('AUD05 explicit zero synthetic boundary differs from null',(h,o)=>{
 mei(h);
 // Isolated reader double only. Active policy/registry/source files untouched.
 const original=h.c.riskProfileByAny;
 h.c.riskProfileByAny=value=>{const p=original(value);return {...p,monthlyTarget:p.key==='base'?0:p.monthlyTarget};};
 const r=h.run("runMEIMonteCarlo({profileKey:'base',startingEquity:10000,horizonMonths:1,simulationCount:1000})");o.result={enabled:r.enabled,muUsed:r.muUsed,logDrift:r.logDrift};o.limit='Synthetic reader double; no policy activation';assert.equal(r.enabled,true);assert.strictEqual(r.muUsed,0);assert.strictEqual(r.logDrift,0);
});
for(const [name,time,allowed] of [
 ['prior UTC day','2026-10-11T23:59:59Z',false],['same UTC midnight','2026-10-12T00:00:00Z',true],
 ['negative offset enters UTC day','2026-10-11T23:30:00-03:00',true],['positive offset remains prior UTC day','2026-10-12T00:30:00+02:00',false],
 ['retroactive valid within declared period','2026-10-12T12:00:00Z',true]])test('AUD06 '+name,(h,o)=>{
 const a=account(h,{observe:false});h.c.syntheticDraft={...a.facts,observedAt:time};
 const before=h.snapshot(),draft=JSON.stringify(h.c.syntheticDraft),r=h.c.JPWForex.state.recordAccountFacts(h.c.syntheticDraft,{reason:'SYNTHETIC first observation'});
 o.result=r;o.observedAt=time;o.normalizedDay=new Date(time).toISOString().slice(0,10);o.allowed=allowed;
 assert.equal(r.ok,allowed,'first observation chronology disagrees with declared UTC period');assert.equal(JSON.stringify(h.c.syntheticDraft),draft,'caller draft changed');
 if(!allowed){assert.equal(r.persistido,false);same(h.snapshot(),before,'rejected observation changed state/save/log');}
});
test('AUD06 chronological current observation cannot be overwritten',(h,o)=>{
 const a=account(h),before=h.snapshot();o.result=h.c.JPWForex.state.recordAccountFacts({...a.facts,observedAt:'2026-10-12T11:00:00Z'},{reason:'SYNTHETIC earlier observation'});assert.equal(o.result.ok,false);same(before,h.snapshot());
});
const failed=cases.filter(c=>c.status!=='PASS'),classification=cases.some(c=>c.status==='TEST_HARNESS_FAIL')?'TEST_HARNESS_FAIL':failed.length?'PRODUCT_FAIL':'PASS';
console.log(JSON.stringify({classification,environment:'Node VM; original sources; synthetic state/save double; no browser persistence claim',cases},null,2));
process.exitCode=failed.length?1:0;
'''

def main():
 p=argparse.ArgumentParser();p.add_argument('--root',type=Path,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--node',default=os.environ.get('JP_WEALTH_NODE',''));a=p.parse_args()
 root=a.root.resolve();a.out.mkdir(parents=True,exist_ok=False)
 sources={name:(root/name).read_text() for name in PATHS+EXTRA}
 hashes={name:hashlib.sha256((root/name).read_bytes()).hexdigest() for name in PATHS+EXTRA}
 node=a.node or shutil.which('node') or '/Users/joaoalvescirqueira/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node'
 cp=subprocess.run([node,'-e',NODE],input=json.dumps({'paths':PATHS,'sources':sources}),text=True,capture_output=True)
 (a.out/'stdout.json').write_text(cp.stdout);(a.out/'stderr.log').write_text(cp.stderr)
 meta={'command':[node,'-e','<embedded NODE>'],'root':str(root),'head':subprocess.check_output(['git','rev-parse','HEAD'],cwd=root,text=True).strip(),'branch':subprocess.check_output(['git','branch','--show-current'],cwd=root,text=True).strip(),'sourceHashesBefore':hashes,'sourceHashesAfter':{name:hashlib.sha256((root/name).read_bytes()).hexdigest() for name in PATHS+EXTRA},'testSha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'nodeVersion':subprocess.check_output([node,'--version'],text=True).strip(),'exitCode':cp.returncode}
 try:result=json.loads(cp.stdout);meta['classification']=result['classification'];meta['pass']=sum(c['status']=='PASS' for c in result['cases']);meta['fail']=sum(c['status']!='PASS' for c in result['cases'])
 except (ValueError,KeyError):meta['classification']='TEST_HARNESS_FAIL'
 if meta['sourceHashesBefore']!=meta['sourceHashesAfter']:meta['classification']='TEST_HARNESS_FAIL';meta['error']='Source changed during execution'
 (a.out/'receipt.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2));print(json.dumps({k:meta.get(k) for k in ['classification','pass','fail','exitCode','root','head','branch']},ensure_ascii=False));return 0 if meta['classification']=='PASS' else 1

if __name__=='__main__':sys.exit(main())
