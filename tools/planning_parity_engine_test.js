#!/usr/bin/env node
'use strict';
// Oracles: original native Sheet visible layout and Formulario.verified.gs,
// ApresentacaoConsolidado.gs and Prazos.gs snapshots verified 2026-10-19;
// visible native cells/formulas were read again on 2026-10-20.
// All accounts, flows and FX quotes here are synthetic. No network or DOM.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const root = path.resolve(__dirname, '..');
const source = 'src/js/30-accounting/06-planning/01-engine.js';
const context = {window: {}};
vm.createContext(context);
vm.runInContext(fs.readFileSync(path.join(root, source), 'utf8'), context, {filename: source});
const E = context.window.JPWPlanning.engine;
let count = 0;
function test(id, fn) { fn(); count++; console.log('PASS ' + id); }
function near(actual, expected, label = 'amount') {
  assert.equal(typeof actual, 'number', label);
  assert.ok(Math.abs(actual - expected) <= Math.max(1e-8, Math.abs(expected) * 1e-12),
    `${label}: ${actual} != ${expected}`);
}
function config(overrides = {}) {
  return Object.assign({startMonth:'2026-01',initialUsd:1000,profileId:'base',monthlyContributionUsd:100,
    goals:{adequate:{value:50,currency:'USD'},ideal:{value:300,currency:'USD'}}},overrides);
}
function account(id='account-one', changes={}) {
  return {id,name:'Synthetic '+id,broker:'',login:'',server:'',active:true,
    plan:E.createPlan(config(changes),{id:'plan-'+id,now:'2026-01-01T12:00:00Z'})};
}
function envelope(accounts=[account()]) {
  return {schemaVersion:1,revision:0,accounts,archive:[],audit:[],operations:[]};
}
function view(value,options={}) {
  return E.sheetView(value,Object.assign({month:'2026-01',quote:{rate:5,source:'synthetic',referenceDate:'2026-01-15',fetchedAt:'2026-01-15T12:00:00Z'}},options));
}
function fixedBalance(n,initial=1000,contribution=100,rate=.03) {
  return rate===0?initial+n*contribution:initial*(1+rate)**n+contribution*((1+rate)**n-1)/rate;
}
function confirmed(plan,month,usd) {
  plan.results[month]={usd,revision:1,recordedAt:'2026-02-01T12:00:00Z'};
  plan.closures[month]={confirmed:true,confirmFlows:true,revision:1,confirmedAt:'2026-02-01T12:00:00Z'};
}
function plain(value) { return JSON.parse(JSON.stringify(value)); }

test('PLN-PARITY-01 native sheet presentation has a shared DOM-independent read model', () => {
  assert.equal(typeof E.sheetView, 'function');
  assert.equal(typeof E.formView, 'function');
  assert.equal(typeof E.profileView, 'function');
});

test('PLN-PARITY-02 selected projection year reads its own December and is independent of chart period',()=>{
  const value=envelope(),before=JSON.stringify(value);
  const first=view(value,{projectionYear:2026,chartPeriod:'full'}),second=view(value,{projectionYear:2027,chartPeriod:'full'});
  assert.equal(first.sheet.projection.year,2026);assert.equal(first.sheet.projection.month,'2026-12');
  near(first.sheet.projection.closeUsd,fixedBalance(12));near(first.sheet.projection.closeBrl,fixedBalance(12)*5);
  near(second.sheet.projection.closeUsd,fixedBalance(24));assert.equal(second.sheet.chart.rows.length,120);
  const graph=view(value,{projectionYear:2027,chartPeriod:'year:2026'});
  near(graph.sheet.projection.closeUsd,fixedBalance(24));
  assert.equal(graph.sheet.chart.rows.length,12);assert.equal(graph.sheet.chart.rows[0].month,'2026-01');
  assert.equal(graph.sheet.chart.rows[11].month,'2026-12');
  assert.equal(JSON.stringify(value),before,'presentation selectors cannot write financial data');
});

test('PLN-PARITY-03 calendar union uses the terminal month of a partial final year',()=>{
  const value=envelope([account('a',{startMonth:'2026-10'})]);
  const model=view(value,{month:'2026-10',projectionYear:2036});
  assert.equal(model.sheet.projection.month,'2036-09');near(model.sheet.projection.closeUsd,fixedBalance(120));
  assert.deepEqual(plain(model.sheet.projection.years),Array.from({length:11},(_,i)=>2026+i));
});

test('PLN-PARITY-04 annual rate compounds monthly returns and does not treat contributions as return',()=>{
  const m=view(envelope(),{tableMode:'Anual',projectionYear:2026});
  const year=m.sheet.table.annual.find(r=>Number(r.year)===2026);assert.ok(year);
  near(year.contributionUsd,1200);near(year.closeUsd,fixedBalance(12));
  near(year.resultUsd,fixedBalance(12)-1000-1200);near(year.rate,1.03**12-1);
});

test('PLN-PARITY-05 monthly table has months on rows and calendar years on columns',()=>{
  const value=envelope(),m=view(value,{tableMode:'Mensal · Patrimônio',indicator:'Patrimônio'});
  assert.equal(m.sheet.table.monthly.length,12);assert.equal(m.sheet.table.monthly[0].label,'Janeiro');
  const jan=m.sheet.table.monthly[0];
  near(jan.values.find(r=>Number(r.year)===2026).value,1130);
  near(jan.values.find(r=>Number(r.year)===2027).value,fixedBalance(13));
  const profit=view(value,{tableMode:'Mensal · Resultado do mês',indicator:'Resultado do mês'}).sheet.table.monthly[0];
  near(profit.values.find(r=>Number(r.year)===2026).value,30);
  const rate=view(value,{tableMode:'Mensal · Rentabilidade',indicator:'Rentabilidade'}).sheet.table.monthly[0];
  near(rate.values.find(r=>Number(r.year)===2026).value,.03);
});

test('PLN-PARITY-06 only one active account resolves individual income goals in Todas as contas',()=>{
  const value=envelope();const all=view(value),individual=view(value,{accountId:'account-one'});
  assert.ok(all.sheet.goals&&all.sheet.goals.ideal,'single-account All view must expose its own objectives');
  assert.equal(all.sheet.goals.ideal.month,individual.goals.ideal.month);
  value.accounts.push(account('two'));
  const many=view(value);assert.ok(!many.sheet.goals||!many.sheet.goals.ideal,'independent income objectives are not summed');
});

test('PLN-PARITY-07 no closure never presents initial capital as confirmed wealth',()=>{
  const m=view(envelope());assert.equal(m.confirmed.balanceUsd,null);
  near(m.sheet.summary.initialUsd,1000);assert.equal(m.sheet.comparison.through,null);
  for(const row of m.sheet.comparison.rows)assert.equal(row.confirmed,null,'unconfirmed amount remains unavailable');
});

test('PLN-PARITY-08 planned versus actual compares identical confirmed month and excludes later pending facts',()=>{
  const a=account();confirmed(a.plan,'2026-01',50);
  a.plan.results['2026-02']={usd:200,revision:1,recordedAt:'2026-02-01T12:00:00Z'};
  const m=view(envelope([a]),{month:'2026-02'}),comparison=m.sheet.comparison;
  assert.equal(comparison.through,'2026-01');
  const wealth=comparison.rows.find(r=>/patrim[oô]nio/i.test(r.label));assert.ok(wealth);
  near(wealth.planned,1130);near(wealth.confirmed,1050);near(wealth.deviationUsd,-80);near(wealth.deviationRate,-80/1130);
  const contribution=comparison.rows.find(r=>/aporte/i.test(r.label));assert.ok(contribution);
  near(contribution.planned,100);near(contribution.confirmed,0);near(contribution.deviationUsd,-100);
  assert.equal(comparison.rows.length,2,'the live native comparison has wealth and cumulative contributions only');
});

test('PLN-PARITY-09 absent or zero reference base never manufactures a percentage deviation',()=>{
  const a=account('zero',{initialUsd:0,monthlyContributionUsd:0});confirmed(a.plan,'2026-01',0);
  const comparison=view(envelope([a]),{month:'2026-01'}).sheet.comparison;
  const wealth=comparison.rows.find(r=>/patrim[oô]nio/i.test(r.label));assert.ok(wealth);
  near(wealth.planned,0);near(wealth.confirmed,0);assert.equal(wealth.deviationRate,null);
});

test('PLN-PARITY-10 initial reference table has exactly its own 120 months and original premisses',()=>{
  const a=account();a.plan.future['2026-02']={rate:0,contributionUsd:0};
  const r=view(envelope([a]),{accountId:a.id}).sheet.reference;
  assert.equal(r.startMonth,'2026-01');assert.equal(r.endMonth,'2035-12');assert.equal(r.rows.length,120);
  near(r.initialUsd,1000);near(r.monthlyContributionUsd,100);near(r.rows[1].closeUsd,1263.9);
});

test('PLN-PARITY-11 form forecasts use initial fixed premisses even when start is in the past',()=>{
  const m=E.formView(config(),{month:'2026-10'});
  assert.equal(m.model.rows.length,120);near(m.model.rows[0].contributionUsd,100);
  near(m.model.rows[119].closeUsd,fixedBalance(120));near(m.requiredCapitalUsd,10000);
});

test('PLN-PARITY-12 risk comparison shows compound growth and asymmetric recovery independently',()=>{
  for(const [id,rate,loss] of [['high-risk',.06,.4],['base',.03,.2],['conservative',.02,.13],['safety',.015,.1]]){
    const profile=E.profileView(id);near(profile.recoveryRate,loss/(1-loss));
    assert.ok(profile.growth.length>1);
    for(const point of profile.growth)near(point.value,100*(1+rate)**point.month);
    for(const point of profile.recoveryCurve95)near(point.gain,point.loss/(1-point.loss));
  }
});

test('PLN-PARITY-13 monthly FX accounting uses paid BRL for acquisition and separates cash withdrawals',()=>{
  const a=account();a.plan.contributions.push({id:'c1',month:'2026-01',usd:100,brl:500,revision:1});
  a.plan.withdrawals.push({id:'w1',month:'2026-01',usd:25,brl:140,revision:1});
  confirmed(a.plan,'2026-01',50);
  const m=view(envelope([a]),{month:'2026-01',accountId:a.id,quote:{rate:5.5,source:'synthetic',referenceDate:'2026-01-15',fetchedAt:'2026-01-15T12:00:00Z'}});
  const row=m.sheet.monthlyRows[0];near(row.openUsd,1000);near(row.resultUsd,50);near(row.rate,.05);
  near(row.contributionUsd,100);near(row.withdrawalUsd,25);near(row.closeUsd,1125);
  near(row.paidBrl,500);near(row.averageRate,5);near(row.fxVariation,.1);
});

test('PLN-PARITY-14 chart contributions include expected future flows without rewriting realized sums',()=>{
  const value=envelope();const m=view(value,{chartPeriod:'full'}),rows=m.sheet.chart.rows;
  assert.equal(rows.length,120);near(rows[0].cumulativeContributionUsd,100);near(rows[11].cumulativeContributionUsd,1200);
  assert.equal(m.confirmed.contributionsUsd,0);assert.equal(value.accounts[0].plan.contributions.length,0);
});

test('PLN-PARITY-15 blank blue contribution is zero in calculation and stays distinct from explicit zero',()=>{
  const a=account();a.plan.future['2026-02']={rate:.03,contributionUsd:''};
  const input=envelope([a]),before=JSON.stringify(input);assert.deepEqual(plain(E.validateEnvelope(input)),[]);
  let model=view(input,{month:'2026-01',accountId:a.id}),r=model.sheet.monthlyRows[1];
  assert.equal(r.contributionBlank,true);near(r.plannedContributionUsd,0);near(r.contributionUsd,0);near(r.closeUsd,1163.9);
  assert.equal(r.costStatus,'Sem aporte previsto');assert.equal(a.plan.future['2026-02'].contributionUsd,'');
  assert.equal(JSON.stringify(input),before);assert.equal(a.plan.contributions.length,0);
  a.plan.future['2026-02'].contributionUsd=0;r=view(input,{month:'2026-01',accountId:a.id}).sheet.monthlyRows[1];
  assert.equal(r.contributionBlank,false);near(r.contributionUsd,0);near(r.closeUsd,1163.9);
});

test('PLN-PARITY-16 realized chart has four native modes and excludes pending/current forecasts',()=>{
  const a=account();a.plan.contributions.push({id:'c1',month:'2026-01',usd:100,brl:500,revision:1});
  a.plan.withdrawals.push({id:'w1',month:'2026-01',usd:25,revision:1});confirmed(a.plan,'2026-01',50);
  a.plan.results['2026-02']={usd:200,revision:1,recordedAt:'2026-02-01T00:00:00Z'};
  const input=envelope([a]),before=JSON.stringify(input);
  const modes=['Patrimônio e aportes (US$)','Rentabilidade mensal (%)','Aportes do mês (US$)','Saques do mês (US$)'];
  const defaultModel=view(input,{month:'2026-02',chartPeriod:'year:2030'});
  assert.equal(defaultModel.sheet.realChart.mode,'Rentabilidade mensal (%)');
  assert.deepEqual(plain(defaultModel.sheet.realChart.options).map(x=>x.label),modes);
  for(const [mode,amount,secondary] of [[modes[0],1125,100],[modes[1],.05,null],[modes[2],100,null],[modes[3],25,null]]){
    const real=view(input,{month:'2026-02',chartPeriod:'year:2030',realChartMode:mode}).sheet.realChart;
    assert.equal(real.rows.length,1,'pending February must not enter realized chart');assert.equal(real.rows[0].month,'2026-01');
    near(real.rows[0].value,amount);if(secondary===null)assert.equal(real.rows[0].secondaryValue,null);else near(real.rows[0].secondaryValue,secondary);
  }
  assert.equal(JSON.stringify(input),before,'realized chart filters never write financial facts');
});

test('PLN-PARITY-17 twelve-month phase subtotals follow plan anniversaries rather than calendar years',()=>{
  // Live source D17:U17, formula-only read 2026-10-20: first opening,
  // twelve monthly sums, terminal FX/wealth, and year span. G17 is blank.
  const a=account('anniversary',{startMonth:'2026-10'}),input=envelope([a]),before=JSON.stringify(input);
  const totals=view(input,{accountId:a.id,month:'2026-10'}).sheet.phaseTotals;
  assert.equal(totals.length,10);assert.equal(totals[0].label,'2026–2027');assert.equal(totals[0].monthLabel,'12 MESES');
  assert.equal(totals[0].startMonth,'2026-10');assert.equal(totals[0].endMonth,'2027-09');
  near(totals[0].openUsd,1000);near(totals[0].closeUsd,fixedBalance(12));near(totals[0].contributionUsd,1200);
  near(totals[0].resultUsd,fixedBalance(12)-2200);assert.equal(totals[0].situation,'Misto');
  assert.equal(totals[1].label,'2027–2028');near(totals[1].openUsd,fixedBalance(12));near(totals[1].closeUsd,fixedBalance(24));
  near(totals[1].resultUsd,fixedBalance(24)-fixedBalance(12)-1200);assert.equal(totals[1].situation,'Projeção');
  assert.equal(view(envelope(),{month:'2026-01'}).sheet.phaseTotals[0].monthLabel,'FECHAMENTO');
  assert.equal(JSON.stringify(input),before,'phase subtotal preparation performs no financial writes');
  a.plan.future['2026-11']={rate:null,contributionUsd:100};
  assert.equal(view(input,{accountId:a.id,month:'2026-10'}).sheet.phaseTotals[0].situation,'Pendente');
});

if(process.argv.includes('--source-oracle')){
  const directory=process.env.JPW_PLANNING_ORACLE_DIR||'/private/tmp/stoikus-auditoria-entrega-20261019/native';
  const file=path.join(directory,'Prazos.gs');
  const blocked=new Proxy({},{get(){throw Error('Native platform API forbidden in pure source comparison');}});
  const native={SpreadsheetApp:blocked,Utilities:blocked};vm.createContext(native);
  vm.runInContext(fs.readFileSync(file,'utf8'),native,{filename:'Prazos.gs'});
  const statuses={NAO_INFORMADO:'NOT_INFORMED',DADOS_PENDENTES:'PENDING_DATA',NAO_ALCANCADO:'NOT_REACHED',REALIZADO:'ACHIEVED',PROJECAO:'PROJECTED'};
  const variants=[
    ['unconfirmed original',()=>{},'2026-01'],
    ['confirmed original',a=>confirmed(a.plan,'2026-01',400),'2026-01'],
    ['changed income objective',a=>{a.plan.goals.ideal={value:100,currency:'USD',usd:100,quote:null};},'2026-01'],
    ['optional adequate absent',a=>{a.plan.goals.adequate=null;},'2026-01'],
    ['provisional zero and withdrawals',a=>{a.plan.future['2026-02']={rate:null,contributionUsd:0};a.plan.withdrawals.push({id:'w',month:'2026-01',usd:100,revision:1});},'2026-01'],
    ['unreached within horizon',a=>{a.plan.goals.ideal={value:999999999,currency:'USD',usd:999999999,quote:null};},'2026-01'],
    ['past projected goal awaits closure',()=>{},'2028-01']
  ];
  for(const [name,change,month] of variants)test('PLN-PARITY-ORACLE '+name,()=>{
    const a=account();change(a);const before=JSON.stringify(a),m=E.account(a,{month});
    const nativeInput={capital:a.plan.initialUsd,conta:a.id,plano:a.plan.id,
      fechados:m.rows.filter(r=>r.finalized).length,
      metas:{adequada:a.plan.goals.adequate?.usd,ideal:a.plan.goals.ideal?.usd},
      meses:m.rows.map(r=>({mes:r.month,taxa:r.rate,resultado:r.resultUsd,patrimonio:r.closeUsd})),
      base:{plano:a.plan.id,metas:{adequada:a.plan.reference.config.goals.adequate?.usd,ideal:a.plan.reference.config.goals.ideal?.usd},
        trajetoria:m.referenceRows.map(r=>({mes:r.month,resultado:r.resultUsd,patrimonio:r.closeUsd}))}};
    const original=native.calcularComparativoRendaStoikus_(nativeInput);
    for(const [i,key] of [[0,'adequate'],[1,'ideal']]){
      assert.equal(m.goals[key].status,statuses[original[i].estado],key+' state');
      assert.equal(m.goals[key].month,original[i].atual||null,key+' current date');
      if(original[i].estado!=='NAO_INFORMADO'){
        assert.equal(m.goals[key].referenceMonth,original[i].inicial||null,key+' preserved date');
        assert.equal(m.goals[key].goalChanged,original[i].metaAlterada,key+' changed target');
        assert.equal(m.goals[key].deltaMonths,original[i].delta===''?null:original[i].delta,key+' calendar displacement');
      }
    }
    assert.equal(JSON.stringify(a),before,'native comparison is read only');
  });
}

console.log(`PASS ${count} source-grounded Planning parity checks`);
