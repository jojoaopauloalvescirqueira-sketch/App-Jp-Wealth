/* Approved monthly-inline contract, 2026-10-21: result points/USD are previewed
 * through the confirmed-domain rules without writing. Synthetic fixtures only. */
'use strict';
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const vm=require('node:vm');
const {randomUUID}=require('node:crypto');
const root=path.resolve(__dirname,'..');
const moduleFile=process.env.JPW_PLANNING_STATE_SOURCE||path.join(root,'src/js/30-accounting/06-planning/02-state.js');
const engineFile=path.join(root,'src/js/30-accounting/06-planning/01-engine.js');
const plain=value=>JSON.parse(JSON.stringify(value));
function harness(initial={}){
  const control={calls:[],mode:'CONFIRMED',network:0,storage:0};
  class Clock extends Date{constructor(...args){super(...(args.length?args:['2026-10-20T12:00:00.000Z']));}static now(){return new Date('2026-10-20T12:00:00.000Z').getTime();}}
  const forbiddenStorage=()=>{control.storage++;throw new Error('Preview accessed storage');};
  const context=vm.createContext({console,structuredClone,crypto:{randomUUID},Date:Clock,initial:plain(initial),
    getCurrentUsdBrlQuote:()=>null,jpWealthPersistenceEpoch:()=>0,jpWealthPersistenceOutcomeIsUnknown:()=>false,
    localStorage:{getItem:forbiddenStorage,setItem:forbiddenStorage,removeItem:forbiddenStorage},
    fetch:()=>{control.network++;throw new Error('Preview accessed network');},
    jpWealthPersistDocument:(candidate,options)=>{control.calls.push({candidate:plain(candidate),options});
      return control.mode==='REFUSED'?{status:'REFUSED',reason:'SYNTHETIC_REFUSAL'}:{status:'CONFIRMED',payload:JSON.stringify(candidate)};}});
  vm.runInContext('let S=initial; window=globalThis;',context);
  vm.runInContext(fs.readFileSync(engineFile,'utf8'),context,{filename:engineFile});
  vm.runInContext(fs.readFileSync(moduleFile,'utf8'),context,{filename:moduleFile});
  return {api:context.JPWPlanning,control,state:()=>plain(vm.runInContext('S',context)),
    setState:value=>{context.next=plain(value);vm.runInContext('S=next',context);}};
}
function execute(h,type,payload){return h.api.commands.execute(type,payload,h.api.queries.token(payload?.accountId));}
function confirmed(h,type,payload){const r=execute(h,type,payload);assert.equal(r.status,'CONFIRMED',JSON.stringify(r));return r;}
function create(h,changes={}){return confirmed(h,'createAccount',{name:'Synthetic result preview',broker:'Demo',login:'100',server:'Demo',
  startMonth:'2026-01',initialUsd:1000,profileId:'base',monthlyContributionUsd:0,
  goals:{adequate:null,ideal:{value:5000,currency:'USD'}},...changes}).accountId;}
function preview(h,input){assert.equal(typeof h.api.queries.previewResultInput,'function','queries.previewResultInput must be available');return h.api.queries.previewResultInput(input);}
function valid(result){assert.equal(result.ok,true,JSON.stringify(result));assert.equal(result.status,'PREVIEW');assert.deepEqual(plain(result.errors),[]);return result;}
function invalid(result){assert.equal(result.ok,false,JSON.stringify(result));assert.equal(result.status,'INVALID');assert.ok(result.errors.length>0);assert.ok(result.errors.every(error=>typeof error==='string'&&error.trim()));return result;}
const tests=[];const test=(name,run)=>tests.push({name,run});
test('PLRESULT-01 1000 USD at 3 percentage points previews 30 USD with the existing flow shape',()=>{
  const h=harness(),id=create(h),r=valid(preview(h,{accountId:id,month:'2026-01',unit:'PERCENT',value:3}));
  assert.equal(r.openUsd,1000);assert.equal(r.monthTotalUsd,30);assert.equal(r.row.resultUsd,30);assert.equal(r.rate,.03);
  assert.equal(r.inputUnit,'PERCENT');assert.equal(r.inputValue,3);
  const {openUsd,inputUnit,inputValue,...flow}=r;
  assert.deepEqual(plain(flow),plain(h.api.queries.previewFlow({accountId:id,month:'2026-01',kind:'result',usd:30})));
});
test('PLRESULT-02 percent converts 112.55 USD at 3 points to 3.38 USD and returns a fractional rate',()=>{
  const h=harness(),id=create(h,{initialUsd:112.55}),r=valid(preview(h,{accountId:id,month:'2026-01',unit:'PERCENT',value:3}));
  assert.equal(r.openUsd,112.55);assert.equal(r.monthTotalUsd,3.38);assert.equal(r.row.resultUsd,3.38);assert.equal(r.rate,3.38/112.55);
});
test('PLRESULT-03 percentage losses and explicit zero remain valid while motor balance limits apply',()=>{
  const h=harness(),id=create(h);
  assert.equal(valid(preview(h,{accountId:id,month:'2026-01',unit:'PERCENT',value:-3})).monthTotalUsd,-30);
  assert.equal(valid(preview(h,{accountId:id,month:'2026-01',unit:'PERCENT',value:0})).monthTotalUsd,0);
  assert.equal(valid(preview(h,{accountId:id,month:'2026-01',unit:'PERCENT',value:-100})).row.closeUsd,0);
  invalid(preview(h,{accountId:id,month:'2026-01',unit:'PERCENT',value:-100.01}));
});
test('PLRESULT-04 USD zero and signed cents pass unchanged while fractional cents are refused',()=>{
  const h=harness(),id=create(h);
  for(const value of [0,12.34,-12.34]){const r=valid(preview(h,{accountId:id,month:'2026-01',unit:'USD',value}));
    assert.equal(r.monthTotalUsd,value);assert.equal(r.inputUnit,'USD');assert.equal(r.inputValue,value);assert.equal(r.openUsd,1000);}
  for(const value of [.001,-.001,1000.001,Number.MAX_VALUE])invalid(preview(h,{accountId:id,month:'2026-01',unit:'USD',value}));
});
test('PLRESULT-05 percent requires positive opening capital while USD zero retains the existing rule',()=>{
  const h=harness(),id=create(h,{initialUsd:0});
  for(const value of [0,3,-3])assert.match(invalid(preview(h,{accountId:id,month:'2026-01',unit:'PERCENT',value})).errors.join(' '),/saldo.*abertura.*positivo/i);
  const r=valid(preview(h,{accountId:id,month:'2026-01',unit:'USD',value:0}));assert.equal(r.openUsd,0);assert.equal(r.rate,0);
  invalid(preview(h,{accountId:id,month:'2026-01',unit:'USD',value:1}));
});
test('PLRESULT-06 missing or inactive account is refused without creating an aggregate',()=>{
  const empty=harness({other:{preserve:true}}),before=empty.state();
  invalid(preview(empty,{accountId:'missing',month:'2026-01',unit:'PERCENT',value:3}));
  assert.deepEqual(empty.state(),before);assert.equal(empty.control.calls.length,0);
  const h=harness(),id=create(h),document=h.state();document.patrimonialPlanning.accounts[0].active=false;h.setState(document);
  invalid(preview(h,{accountId:id,month:'2026-01',unit:'USD',value:0}));
});
test('PLRESULT-07 current month is available but future facts and invalid horizons are refused',()=>{
  const h=harness(),id=create(h);
  valid(preview(h,{accountId:id,month:'2026-10',unit:'USD',value:0}));
  for(const month of ['2026-11','2025-12','2036-01','2026-13','',null])for(const unit of ['PERCENT','USD'])
    invalid(preview(h,{accountId:id,month,unit,value:3}));
});
test('PLRESULT-08 incompatible envelopes preserve their original data and refuse preview',()=>{
  for(const patrimonialPlanning of [{schemaVersion:99,opaque:'future'},{schemaVersion:1,accounts:'broken'}]){
    const h=harness({patrimonialPlanning}),before=h.state();
    invalid(preview(h,{accountId:'missing',month:'2026-01',unit:'PERCENT',value:3}));
    assert.deepEqual(h.state(),before);assert.equal(h.control.calls.length,0);
  }
});
test('PLRESULT-09 numeric inputs reject blank null strings nonfinite and other types distinctly from zero',()=>{
  const h=harness(),id=create(h);
  for(const unit of ['PERCENT','USD'])for(const value of [undefined,null,'',' ','3',true,false,{},[],NaN,Infinity,-Infinity])
    invalid(preview(h,{accountId:id,month:'2026-01',unit,value}));
  for(const unit of [undefined,null,'','percent','BRL',3])invalid(preview(h,{accountId:id,month:'2026-01',unit,value:3}));
  for(const input of [undefined,null,[],3])invalid(preview(h,input));
});
test('PLRESULT-10 repeated preview does not mutate facts history tokens storage or network',()=>{
  const h=harness({other:{preserve:['extension']}}),id=create(h),before=h.state(),token=plain(h.api.queries.token(id)),calls=h.control.calls.length;
  const input={accountId:id,month:'2026-01',unit:'PERCENT',value:3},copy=plain(input),first=valid(preview(h,input));
  for(let i=0;i<3;i++)assert.deepEqual(plain(valid(preview(h,input))),plain(first));
  first.row.closeUsd=999999;
  assert.equal(valid(preview(h,input)).row.closeUsd,1030);assert.deepEqual(input,copy);
  assert.deepEqual(h.state(),before);assert.deepEqual(plain(h.api.queries.token(id)),token);
  assert.equal(h.control.calls.length,calls);assert.equal(h.control.storage,0);assert.equal(h.control.network,0);
});
test('PLRESULT-11 percent reads fresh opening capital after configuration changes',()=>{
  const h=harness(),id=create(h),input={accountId:id,month:'2026-01',unit:'PERCENT',value:3};
  assert.equal(valid(preview(h,input)).monthTotalUsd,30);
  confirmed(h,'updateAccount',{accountId:id,config:{initialUsd:2000}});
  const r=valid(preview(h,input));assert.equal(r.openUsd,2000);assert.equal(r.monthTotalUsd,60);
});
test('PLRESULT-12 earlier confirmed result changes the next opening and percentage preview',()=>{
  const h=harness(),id=create(h),input={accountId:id,month:'2026-02',unit:'PERCENT',value:3};
  const before=valid(preview(h,input));assert.equal(before.openUsd,1030);assert.equal(before.monthTotalUsd,30.9);
  confirmed(h,'recordResult',{accountId:id,month:'2026-01',usd:100});
  const after=valid(preview(h,input));assert.equal(after.openUsd,1100);assert.equal(after.monthTotalUsd,33);
});
test('PLRESULT-13 preview succeeds without writer use and a later writer refusal preserves facts',()=>{
  const h=harness(),id=create(h),input={accountId:id,month:'2026-01',unit:'PERCENT',value:3},before=h.state(),calls=h.control.calls.length;
  h.control.mode='REFUSED';const r=valid(preview(h,input));assert.equal(h.control.calls.length,calls);
  assert.equal(execute(h,'recordResult',{accountId:id,month:input.month,usd:r.monthTotalUsd}).status,'REFUSED');
  assert.deepEqual(h.state(),before);assert.equal(h.control.calls.length,calls+1);
  valid(preview(h,input));assert.equal(h.control.calls.length,calls+1);assert.equal(h.control.network,0);assert.equal(h.control.storage,0);
});
test('PLRESULT-14 unavailable opening is refused instead of becoming a zero percentage result',()=>{
  const h=harness(),id=create(h),document=h.state();
  document.patrimonialPlanning.accounts[0].plan.results['2026-01']={usd:-2000,revision:1};h.setState(document);
  const before=h.state(),calls=h.control.calls.length;
  assert.equal(h.api.queries.view({accountId:id}).rows[1].openUsd,null);
  assert.match(invalid(preview(h,{accountId:id,month:'2026-02',unit:'PERCENT',value:0})).errors.join(' '),/saldo.*abertura.*positivo/i);
  assert.deepEqual(h.state(),before);assert.equal(h.control.calls.length,calls);
});
module.exports={tests};
if(require.main===module){
  let failed=0;
  for(const t of tests){try{t.run();console.log('PASS '+t.name);}catch(error){failed++;console.error('FAIL '+t.name+'\n'+error.stack);}}
  console.log(JSON.stringify({suite:'planning_monthly_result_input',tests:tests.length,passed:tests.length-failed,failed}));
  process.exitCode=failed?1:0;
}
