#!/usr/bin/env node
// Local, synthetic contract test. Requires the existing Codex Node Playwright
// runtime; it adds no product dependency and never fetches economic data.
const assert=require('assert');
const path=require('path');
const {pathToFileURL}=require('url');
const runtime=process.env.JPW_NODE_MODULES||'/Users/joaopauloalves/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules';
const {chromium}=require(path.join(runtime,'playwright'));
const root=path.resolve(__dirname,'..');
const cases=[];
function check(name,actual,expected){assert.deepStrictEqual(actual,expected,name);cases.push(name);}
(async()=>{
  const browser=await chromium.launch({headless:true,executablePath:'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'});
  try{
    const context=await browser.newContext({serviceWorkers:'block'}),page=await context.newPage(),errors=[];
    page.on('pageerror',error=>errors.push(error.stack));
    await page.goto(pathToFileURL(path.join(root,'index.html')).href,{waitUntil:'domcontentloaded'});
    await page.waitForTimeout(500);
    check('cold boot has no page errors',errors,[]);
    const seed=await page.evaluate(()=>{
      window.__onbShown=true;closeModal();
      S=structuredClone(DEFAULTS);migrate();S.onboarding.done=true;
      S.accounts=[
        {forexAccountId:'SYNTH_A',nome:'Mestre sintética',tipo:'MESTRE',platform:'MT5',platformLogin:'10001',platformCurrency:'USD'},
        {forexAccountId:'SYNTH_B',nome:'Conta B sintética',tipo:'PRÓPRIA',platform:'MT5',platformLogin:'20002',platformCurrency:'USD'}];
      S.forex=JPWForex.state.empty();S.operationHistory={schemaVersion:2,records:[]};
      if(save()!==true)throw Error('Synthetic seed was not durably recorded');
      const record=(accountId,si)=>JPWForex.state.recordAccountPeriod({accountId,startedAt:'2026-09-01',currency:'USD',si,
        openingBook:si,source:'synthetic fixture',activateCurrentPeriod:true},{reason:'synthetic context',expectedEpoch:jpWealthPersistenceEpoch()});
      const a=record('SYNTH_A',10000),b=record('SYNTH_B',5000);
      if(!a.ok||!b.ok)throw Error(JSON.stringify({a,b}));
      const periods=S.forex.accountContexts.accounts;
      return {a:periods.SYNTH_A.currentPeriodId,b:periods.SYNTH_B.currentPeriodId};
    });
    check('unique Mestre selected initially',await page.evaluate(()=>JPWForex.state.operationalSelection().accountId),'SYNTH_A');
    const state=await page.evaluate(({a,b})=>{
      const x=JPWForex.state;
      const post=(accountId,periodId,result,opening)=>{
        x.selectOperationalAccount(accountId);x.selectOperationalPeriod(accountId,periodId);
        const context=x.accountContext({accountId,periodId});
        return x.recordAccountLedger({action:'RECORDED',accountId,periodId,data:'2026-09-02',resultado:result,saldo:null,
          nota:'synthetic close'},{reason:'synthetic close',expectedRevision:context.revision,expectedEpoch:jpWealthPersistenceEpoch()});
      };
      const ra=post('SYNTH_A',a,100,10000),rb=post('SYNTH_B',b,-50,5000);
      if(!ra.ok||!rb.ok)throw Error(JSON.stringify({ra,rb}));
      const ca=x.accountContext({accountId:'SYNTH_A',periodId:a}).value;
      const cb=x.accountContext({accountId:'SYNTH_B',periodId:b}).value;
      return {a:ca.ledger.map(r=>[r.accountId,r.saldo]),b:cb.ledger.map(r=>[r.accountId,r.saldo]),
        global:S.ledger.length,selected:x.operationalSelection().accountId};
    },seed);
    check('A close uses only A book',state.a,[['SYNTH_A',10100]]);
    check('B close uses only B book',state.b,[['SYNTH_B',4950]]);
    check('new records do not enter legacy ledger',state.global,0);
    check('explicit selection is B',state.selected,'SYNTH_B');
    const corrections=await page.evaluate(({a,b})=>{
      const x=JPWForex.state,ca=x.accountContext({accountId:'SYNTH_A',periodId:a});
      x.selectOperationalAccount('SYNTH_A');x.selectOperationalPeriod('SYNTH_A',a);
      const first=ca.value.ledger[0];
      const corrected=x.recordAccountLedger({action:'CORRECTED',id:first.id,accountId:'SYNTH_A',periodId:a,
        data:first.data,resultado:200,saldo:null,nota:'synthetic correction'},
        {reason:'synthetic retroactive correction',expectedRevision:ca.revision,expectedEpoch:jpWealthPersistenceEpoch()});
      if(!corrected.ok)throw Error(JSON.stringify(corrected));
      const after=x.accountContext({accountId:'SYNTH_A',periodId:a}).value;
      const other=x.accountContext({accountId:'SYNTH_B',periodId:b}).value;
      return {a:after.ledger[0].saldo,b:other.ledger[0].saldo,events:after.ledgerEvents.length};
    },seed);
    check('correction remains in A',corrections.a,10200);
    check('correction leaves B intact',corrections.b,4950);
    check('correction retained audit event',corrections.events,2);
    const orders=await page.evaluate(({a,b})=>{
      const x=JPWForex.state;
      const saveOrder=(accountId,periodId,id,result)=>{
        x.selectOperationalAccount(accountId);x.selectOperationalPeriod(accountId,periodId);
        const c=x.accountContext({accountId,periodId});
        return x.recordAccountOrders([{pi:0,oi:0,changes:{id,par:'EURUSD',tipo:'BUY',role:'GENESIS',
          lote:.01,entry:1.1,sl:1,tp:1.2,status:'Fechada',result,costs:0,
          costBasis:'INCLUDED_IN_RESULT',stopValidated:true}}],
          {accountId,periodId,reason:'synthetic recorded fact',expectedRevision:c.revision,
            expectedEpoch:jpWealthPersistenceEpoch()});
      };
      const ra=saveOrder('SYNTH_A',a,'A-ORDER',40),rb=saveOrder('SYNTH_B',b,'B-ORDER',-20);
      if(!ra.ok||!rb.ok)throw Error(JSON.stringify({ra,rb}));
      const ca=x.accountContext({accountId:'SYNTH_A',periodId:a}).value;
      const cb=x.accountContext({accountId:'SYNTH_B',periodId:b}).value;
      return {a:ca.activeOperation?.operationId,b:cb.activeOperation?.operationId,
        aRow:ca.phases[0].orders[0].accountId,bRow:cb.phases[0].orders[0].accountId,
        global:S.activeOperation};
    },seed);
    assert(orders.a&&orders.b&&orders.a!==orders.b,'independent operation identities');cases.push('two accounts own independent operations');
    check('A order stays in A',orders.aRow,'SYNTH_A');
    check('B order stays in B',orders.bRow,'SYNTH_B');
    check('no global active operation created',orders.global,null);
    const forged=await page.evaluate(({b})=>{
      const x=JPWForex.state,p=x.accountContext({accountId:'SYNTH_B',periodId:b});
      const op=p.value.activeOperation,row=p.value.phases[0].orders[0],before=JSON.stringify(S.operationHistory.records);
      const receipt={operationId:op.operationId,accountId:'SYNTH_B',periodId:b,currency:'USD',netResult:-20,
        ordersSnapshot:[{orderId:row.orderId,par:'GBPUSD'}],closedAt:new Date().toISOString(),
        closedAtSource:'formal_confirmation',policySnapshot:structuredClone(op.policySnapshot),
        recordContext:structuredClone(op.recordContext)};
      const result=x.finalizeAccountOperation(receipt,{accountId:'SYNTH_B',periodId:b,
        expectedRevision:p.revision,expectedEpoch:jpWealthPersistenceEpoch()});
      return {accepted:result.ok,historyUnchanged:before===JSON.stringify(S.operationHistory.records),
        stillActive:!!x.accountContext({accountId:'SYNTH_B',periodId:b}).value.activeOperation};
    },seed);
    check('forged receipt with matching ID and net is refused',forged.accepted,false);
    check('forged receipt does not append history',forged.historyUnchanged,true);
    check('forged receipt does not close operation',forged.stillActive,true);
    const review=await page.evaluate(()=>{JPWOperation.openReview();return {
      confirm:!!document.getElementById('modalConfirm'),defenses:!!document.getElementById('finalDefenses'),
      message:document.getElementById('modalBox').textContent.slice(0,500)};});
    assert(review.confirm&&review.defenses,'account-scoped finalization review must reach confirmation: '+JSON.stringify(review));
    cases.push('finalization review shows selected operation');
    await page.waitForTimeout(100);
    const postReview=await page.evaluate(()=>({defenses:!!document.getElementById('finalDefenses'),
      message:document.getElementById('modalBox').textContent.slice(0,250),open:document.getElementById('modalOverlay').className}));
    assert(postReview.defenses,'review changed before editing: '+JSON.stringify(postReview));
    await page.locator('#finalDefenses').fill('0');
    await page.locator('#finalConfirm').fill('FECHADO');
    await page.locator('#modalConfirm').click();
    const closed=await page.evaluate(({a,b})=>{
      const x=JPWForex.state;
      return {a:!!x.accountContext({accountId:'SYNTH_A',periodId:a}).value.activeOperation,
        b:!!x.accountContext({accountId:'SYNTH_B',periodId:b}).value.activeOperation,
        records:S.operationHistory.records.map(r=>[r.accountId,r.periodId,r.netResult]),
        errors:document.getElementById('finalFail')?.textContent||''};
    },seed);
    check('finalizing B preserves A active operation',closed.a,true);
    check('finalizing B closes only B',closed.b,false);
    check('historical record carries B identity and result',closed.records,[['SYNTH_B',seed.b,-20]]);
    const costs=await page.evaluate(({a})=>{
      const x=JPWForex.state;x.selectOperationalAccount('SYNTH_A');x.selectOperationalPeriod('SYNTH_A',a);
      const c=x.accountContext({accountId:'SYNTH_A',periodId:a});
      const result=x.recordAccountOrders([{pi:0,oi:0,orderId:c.value.phases[0].orders[0].orderId,
        expectedVersion:c.value.phases[0].orders[0].recordVersion,
        changes:{costBasis:'SEPARATE_FROM_RESULT',costs:-3}}],
        {accountId:'SYNTH_A',periodId:a,reason:'Synthetic separate cost correction',
          expectedEpoch:jpWealthPersistenceEpoch(),expectedRevision:c.revision});
      if(!result.ok)throw Error(JSON.stringify(result));
      return {net:netOpAtual(),history:S.operationHistory.records.map(r=>r.netResult)};
    },seed);
    check('separate signed costs enter scoped realized net once',costs.net,37);
    check('cost correction in A leaves closed B history intact',costs.history,[-20]);
    const factors=await page.evaluate(({a,b})=>{
      const x=JPWForex.state,scopeA={accountId:'SYNTH_A',periodId:a},scopeB={accountId:'SYNTH_B',periodId:b};
      const atr=x.recordInstrumentContext({...scopeA,instrumentId:'EURUSD',expectedRevision:0,
        componentChanges:{atr:{short:1,long:2,timeframe:'H4',unit:'PRICE',observedAt:'2026-09-01T12:00:00Z',source:'synthetic manual'}}},
        {reason:'synthetic ATR for new contextual period',expectedEpoch:jpWealthPersistenceEpoch()});
      const h4A=x.recordH4({ddPercent:1,closedAt:'2026-09-01T16:00:00Z',source:'synthetic H4'},
        {target:scopeA,reason:'synthetic H4 A',expectedRevision:x.accountContext(scopeA).revision,expectedEpoch:jpWealthPersistenceEpoch()});
      const h4B=x.recordH4({ddPercent:2,closedAt:'2026-09-01T16:00:00Z',source:'synthetic H4'},
        {target:scopeB,reason:'synthetic H4 B',expectedRevision:x.accountContext(scopeB).revision,expectedEpoch:jpWealthPersistenceEpoch()});
      const opId=x.accountContext(scopeA).value.activeOperation.operationId;
      const grid=x.recordGrid(2,{target:{...scopeA,operationId:opId},reason:'synthetic contextual grid',
        expectedRevision:x.accountContext(scopeA).revision,expectedEpoch:jpWealthPersistenceEpoch()});
      const reserve=(scope,amount)=>x.recordReserves({capitalNominal:10000,fcrConstituted:amount,feoConstituted:10,
        source:'synthetic constitution'},{target:scope,reason:'synthetic scoped reserve',
        expectedRevision:x.accountContext(scope).revision,expectedEpoch:jpWealthPersistenceEpoch()});
      const ra=reserve(scopeA,100),rb=reserve(scopeB,200);
      const budget=x.recordOperationBudget({...scopeA,operationId:opId,currency:'USD',amount:500,
        declaredBy:'synthetic operator',declaredAt:'2026-09-01T10:00:00Z',source:'synthetic declaration'},
        {reason:'synthetic contextual budget'});
      const modelA=JPWForex.readModel(scopeA),modelB=JPWForex.readModel(scopeB);
      return {atr:atr.ok,atrBound:x.instrumentContext({...scopeA,instrumentId:'EURUSD'}).value?.periodId,
        h4A:h4A.ok,h4B:h4B.ok,h4Scopes:S.forex.h4Closes.map(c=>[c.accountId,c.periodId,c.ddPercent]),
        grid:grid.ok,gridA:x.accountContext(scopeA).value.grid?.operationId,gridB:x.accountContext(scopeB).value.grid,
        reserves:[ra.ok,rb.ok],reserveA:modelA.reserves.observations.fcrConstituted,
        reserveB:modelB.reserves.observations.fcrConstituted,global:S.forex.reserves,
        budget:budget.ok,budgetBound:modelA.metrics.operationBudget.declaration?.operationId};
    },seed);
    check('new contextual period accepts instrument ATR without old global observation',factors.atr,true);
    check('instrument ATR remains bound to A period',factors.atrBound,seed.a);
    check('H4 records both scoped accounts without global account selection',[factors.h4A,factors.h4B],[true,true]);
    check('H4 scopes retain separate identities',factors.h4Scopes,[['SYNTH_A',seed.a,1],['SYNTH_B',seed.b,2]]);
    check('contextual grid records A active operation',factors.grid,true);
    check('contextual grid leaves B empty',factors.gridB,null);
    check('contextual grid binds A operation',factors.gridA,orders.a);
    check('both reserve observations persist independently',factors.reserves,[true,true]);
    check('A reserve remains visible after B records its reserve',factors.reserveA,100);
    check('B reserve has its own value',factors.reserveB,200);
    check('contextual reserves do not overwrite legacy global snapshot',factors.global,null);
    check('active contextual operation accepts explicit budget',factors.budget,true);
    check('budget remains bound to A operation',factors.budgetBound,orders.a);
    const staleFactorDraft=await page.evaluate(({a,b})=>{
      const x=JPWForex.state;x.selectOperationalAccount('SYNTH_A');x.selectOperationalPeriod('SYNTH_A',a);render();
      const form=document.getElementById('fxH4Facts');form.elements.namedItem('source').value='draft for A';
      form.elements.namedItem('source').dispatchEvent(new Event('input',{bubbles:true}));
      x.selectOperationalAccount('SYNTH_B');x.selectOperationalPeriod('SYNTH_B',b);render();
      const before=S.forex.h4Closes.length;
      form.dispatchEvent(new Event('submit',{bubbles:true,cancelable:true}));
      return {before,after:S.forex.h4Closes.length,response:form.querySelector('.fx-engine-response').textContent,
        bound:form.dataset.fxScopeAccount,selected:x.operationalSelection().accountId};
    },seed);
    check('account change cannot redirect an H4 draft to B',staleFactorDraft.after,staleFactorDraft.before);
    check('H4 draft remains bound to A until explicit review',staleFactorDraft.bound,'SYNTH_A');
    assert(staleFactorDraft.response.includes('Conta ou período mudou'),'stale factor draft explains refusal');
    cases.push('stale factor draft explains refusal');
    const backup=await page.evaluate(async()=>{
      S.forex.accountContexts.extension={opaque:['synthetic extension']};
      const source=structuredClone(S),blob=dgBuildBackupBlob(1,'synthetic.json',new Date().toISOString(),source);
      const envelope=JSON.parse(await blob.text()),restored=normalizeImportedState(envelope);
      const malformed=structuredClone(envelope);malformed.state.forex.accountContexts.schemaVersion=99;
      let rejected=false;try{normalizeImportedState(malformed);}catch(error){rejected=true;}
      const crossed=structuredClone(envelope),a=crossed.state.forex.accountContexts.accounts.SYNTH_A;
      a.periods[a.currentPeriodId].phases[0].orders[0].accountId='SYNTH_B';
      let crossRejected=false;try{normalizeImportedState(crossed);}catch(error){crossRejected=true;}
      return {coverage:envelope.cobertura.sections.includes('forex'),
        accounts:Object.keys(restored.forex.accountContexts.accounts).sort(),
        extension:restored.forex.accountContexts.extension,
        history:restored.operationHistory.records.map(r=>r.accountId),
        rejected,crossRejected,unchanged:JSON.stringify(S)===JSON.stringify(source)};
    });
    check('full backup includes Forex context',backup.coverage,true);
    check('restore keeps both account contexts',backup.accounts,['SYNTH_A','SYNTH_B']);
    check('restore preserves unknown extensions',backup.extension,{opaque:['synthetic extension']});
    check('restore keeps scoped history',backup.history,['SYNTH_B']);
    check('incompatible context backup is refused',backup.rejected,true);
    check('backup with an order assigned to another account is refused',backup.crossRejected,true);
    check('backup preview leaves current state untouched',backup.unchanged,true);
    const preservation=await page.evaluate(()=>{
      const preserved=sessionPreserveLongitudinal({ausenteAborta:true});
      if(!preserved.ok)throw Error(String(preserved.erro));
      const finalState=emptyJPWealthState(preserved.valor);
      return {accounts:finalState.accounts.length,contexts:Object.keys(finalState.forex.accountContexts.accounts),
        operations:Object.values(finalState.forex.accountContexts.accounts).map(a=>!!a.periods[a.currentPeriodId].activeOperation),
        history:finalState.operationHistory.records.length,riskPin:finalState.riskPinHash};
    });
    check('session preserves both registrations',preservation.accounts,2);
    check('session preserves both contexts',preservation.contexts.sort(),['SYNTH_A','SYNTH_B']);
    check('session preserves A operation and B historical closure',preservation.operations,[true,false]);
    check('session clears local risk unlock',preservation.riskPin,null);
    const archive=await page.evaluate(({a,b})=>{
      const x=JPWForex.state;
      const active=x.archiveRegisteredAccount('SYNTH_A',{reason:'Synthetic active account archive refused'});
      const historical=x.archiveRegisteredAccount('SYNTH_B',{reason:'Synthetic historical account archived'});
      return {active:active.ok,historical:historical.ok,registered:S.accounts.map(v=>v.forexAccountId),
        archived:!!S.forex.accountContexts.archivedAccounts.SYNTH_B,
        context:!!x.accountContext({accountId:'SYNTH_B',periodId:b}).value,
        history:S.operationHistory.records.map(v=>v.accountId),selected:x.operationalSelection().accountId,
        reselect:x.selectOperationalAccount('SYNTH_B').ok};
    },seed);
    check('active operation prevents account archive',archive.active,false);
    check('historical account may be archived explicitly',archive.historical,true);
    check('archive preserves historical account context',archive.context,true);
    check('archive preserves scoped finalized history',archive.history,['SYNTH_B']);
    check('archived account is not operationally selectable',archive.reselect,false);
    check('unique remaining Mestre remains default',archive.selected,'SYNTH_A');
    const archivedHistory=await page.evaluate(({b})=>{
      histState.archiveScope='SYNTH_B|'+b;renderOperationHistory();
      const rows=histRecords(),picker=document.getElementById('histArchiveScope');
      const heading=document.querySelector('#execHistory h2')?.textContent||'';
      histState.archiveScope='';
      return {rows:rows.map(r=>r.accountId),picker:picker?.value,heading,
        operational:JPWForex.state.operationalSelection().accountId};
    },seed);
    check('archived historical operation can be consulted read-only',archivedHistory.rows,['SYNTH_B']);
    check('archived history picker identifies the archived period',archivedHistory.picker,'SYNTH_B|'+seed.b);
    assert(archivedHistory.heading.includes('SYNTH_B'),'archived history heading');cases.push('archived history heading identifies B');
    check('historical consultation leaves operational selection unchanged',archivedHistory.operational,'SYNTH_A');
    const legacy=await page.evaluate(({a})=>{
      const x=JPWForex.state,before=x.accountContext({accountId:'SYNTH_A',periodId:a}).value.ledger.length;
      S.ledger=[{id:'LEGACY-A',accountId:'SYNTH_A',periodId:a,currency:'USD',data:'2026-09-02',resultado:1,saldo:1},
        {id:'LEGACY-UNKNOWN',accountId:'SYNTH_A',data:'2026-09-03',resultado:2,saldo:3}];
      S.phases[0].orders[0]={id:'LEGACY-ORDER',accountId:'SYNTH_A',periodId:a,currency:'USD',
        status:'Fechada',result:1};
      if(save()!==true)throw Error('Synthetic legacy seed refused');
      const preview=x.legacyAccountPreview();
      const confirmed=x.confirmLegacyAccountSnapshot({reason:'Synthetic proof of legacy associations',
        expectedEpoch:jpWealthPersistenceEpoch()});
      return {confirmed:confirmed.ok,associations:preview.associations.map(v=>[v.kind,v.status]),
        stored:S.forex.accountContexts.legacy.associations.map(v=>[v.kind,v.status]),
        contextualCount:x.accountContext({accountId:'SYNTH_A',periodId:a}).value.ledger.length,
        before,legacyCount:S.ledger.length};
    },seed);
    check('explicit snapshot confirmation preserves legacy',legacy.confirmed,true);
    check('proven legacy identifiers are linked only as references',legacy.associations,
      [['ORDER','PROVEN'],['LEDGER','PROVEN'],['LEDGER','UNRECONCILED']]);
    check('legacy association proof survives persistence',legacy.stored,legacy.associations);
    check('legacy references do not inflate scoped ledger totals',legacy.contextualCount,legacy.before);
    check('original legacy rows remain intact',legacy.legacyCount,2);
    const linkageValidation=await page.evaluate(()=>{
      const x=JPWForex.state,valid=x.supported(S.forex),forged=structuredClone(S.forex);
      forged.accountContexts.legacy.associations.find(v=>v.status==='PROVEN').currency='EUR';
      return {valid,forged:x.supported(forged)};
    });
    check('valid legacy reference envelope stays readable',linkageValidation.valid,true);
    check('forged proven legacy currency is rejected',linkageValidation.forged,false);
    const failures=await page.evaluate(({a})=>{
      const x=JPWForex.state;x.selectOperationalAccount('SYNTH_A');x.selectOperationalPeriod('SYNTH_A',a);
      const before=JSON.stringify(S.forex.accountContexts),normal=save;
      save=()=>false;
      const refused=x.recordAccountLedger({action:'RECORDED',accountId:'SYNTH_A',periodId:a,
        data:'2026-09-03',resultado:0,saldo:null,nota:'synthetic refusal'},
        {reason:'synthetic refusal',expectedEpoch:jpWealthPersistenceEpoch()});
      const rolledBack=JSON.stringify(S.forex.accountContexts)===before;
      save=()=>undefined;
      const unknown=x.recordAccountLedger({action:'RECORDED',accountId:'SYNTH_A',periodId:a,
        data:'2026-09-03',resultado:0,saldo:null,nota:'synthetic unknown'},
        {reason:'synthetic unknown',expectedEpoch:jpWealthPersistenceEpoch()});
      const blocked=x.recordAccountLedger({action:'RECORDED',accountId:'SYNTH_A',periodId:a,
        data:'2026-09-04',resultado:0,saldo:null,nota:'must not retry'},
        {reason:'must not retry',expectedEpoch:jpWealthPersistenceEpoch()});
      save=normal;
      return {refused:refused.persistido,rolledBack,unknown:unknown.persistido,
        barrier:jpWealthPersistenceOutcomeIsUnknown(),blocked:blocked.ok};
    },seed);
    check('refused write has proved non-persistence',failures.refused,false);
    check('refused write restores account context',failures.rolledBack,true);
    check('unknown write reports no success',failures.unknown,null);
    check('unknown outcome erects writer barrier',failures.barrier,true);
    check('blind retry is blocked',failures.blocked,false);
    check('synthetic browser flow has no page errors',errors,[]);
    const second=await context.newPage(),secondErrors=[];second.on('pageerror',e=>secondErrors.push(e.message));
    await second.goto(pathToFileURL(path.join(root,'index.html')).href,{waitUntil:'domcontentloaded'});
    const selectionProof=await second.evaluate(()=>{
      window.__onbShown=true;closeModal();S=structuredClone(DEFAULTS);migrate();S.onboarding.done=true;
      S.forex=JPWForex.state.empty();
      S.accounts=[{forexAccountId:'BRL_ONE',nome:'Conta BRL',tipo:'PRÓPRIA',platformCurrency:'BRL'}];
      save();const none=JPWForex.state.operationalSelection().accountId;
      S.accounts.push({forexAccountId:'USD_MASTER',nome:'Mestre USD',tipo:'MESTRE',platformCurrency:'USD'});
      const unique=JPWForex.state.operationalSelection().accountId;
      S.accounts.push({forexAccountId:'OTHER_MASTER',nome:'Outra Mestre',tipo:'MESTRE',platformCurrency:'USD'});
      const ambiguous=JPWForex.state.operationalSelection().accountId;
      S.accounts.pop();save();
      const mismatch=JPWForex.state.recordAccountPeriod({accountId:'BRL_ONE',startedAt:'2026-09-01',currency:'USD',si:2000,
        openingBook:2000,source:'synthetic mismatch',activateCurrentPeriod:true},{reason:'synthetic mismatch'});
      const brl=JPWForex.state.recordAccountPeriod({accountId:'BRL_ONE',startedAt:'2026-09-01',currency:'BRL',si:2000,
        openingBook:2000,source:'synthetic BRL period',activateCurrentPeriod:true},{reason:'synthetic BRL period'});
      const usd=JPWForex.state.recordAccountPeriod({accountId:'USD_MASTER',startedAt:'2026-09-01',currency:'USD',si:1000,
        openingBook:1000,source:'synthetic USD period',activateCurrentPeriod:true},{reason:'synthetic USD period'});
      if(!brl.ok||!usd.ok)throw Error(JSON.stringify({brl,usd}));
      const eb=S.forex.accountContexts.accounts,brlId=eb.BRL_ONE.currentPeriodId,usdId=eb.USD_MASTER.currentPeriodId;
      JPWForex.state.recordAccountLedger({accountId:'BRL_ONE',periodId:brlId,action:'RECORDED',data:'2026-09-02',resultado:50,saldo:null},
        {reason:'synthetic BRL close'});
      JPWForex.state.recordAccountLedger({accountId:'USD_MASTER',periodId:usdId,action:'RECORDED',data:'2026-09-02',resultado:-10,saldo:null},
        {reason:'synthetic USD close'});
      JPWForex.state.selectOperationalAccount('USD_MASTER');
      JPWForex.state.selectOperationalPeriod('USD_MASTER',usdId);JPWForex.ui.render();
      const budgetForm=document.getElementById('fxOperationBudget');
      for(const [name,value] of Object.entries({amount:'100',declaredBy:'Synthetic owner',
        declaredAt:'2026-09-01T10:00',source:'synthetic declaration',reason:'synthetic prospective budget'}))
        budgetForm.elements.namedItem(name).value=value;
      budgetForm.dispatchEvent(new Event('submit',{bubbles:true,cancelable:true}));
      const prospect=JPWForex.state.budgetSnapshot({accountId:'USD_MASTER',periodId:usdId,operationId:null});
      const uiBudget={confirmed:prospect.status==='OK',currency:prospect.currency,
        message:budgetForm.querySelector('.fx-engine-response').textContent};
      const firstOp=JPWForex.state.recordAccountOrders([{pi:0,oi:0,changes:{id:'FIRST-OP',par:'EURUSD',tipo:'BUY',role:'GENESIS',lote:.01,
        entry:1.1,sl:1,tp:1.2,status:'Aberta',result:null,costs:0,costBasis:'INCLUDED_IN_RESULT'}}],
        {accountId:'USD_MASTER',periodId:usdId,reason:'synthetic first operation'});
      if(!firstOp.ok)throw Error(JSON.stringify(firstOp));
      const opId=eb.USD_MASTER.periods[usdId].activeOperation.operationId;
      const attached=JPWForex.state.budgetSnapshot({accountId:'USD_MASTER',periodId:usdId,operationId:opId});
      const other=JPWForex.state.recordAccountPeriod({accountId:'USD_MASTER',startedAt:'2026-10-01',currency:'USD',si:900,
        openingBook:900,source:'synthetic later period',activateCurrentPeriod:false},{reason:'synthetic later period'});
      if(!other.ok)throw Error(JSON.stringify(other));
      const laterId=Object.keys(eb.USD_MASTER.periods).find(x=>x!==usdId),later=eb.USD_MASTER.periods[laterId];
      const secondOp=JPWForex.state.recordAccountOrders([{pi:0,oi:0,changes:{id:'SECOND-OP',par:'EURUSD',tipo:'BUY',role:'GENESIS',lote:.01,
        entry:1.1,sl:1,tp:1.2,status:'Aberta',result:null,costs:0,costBasis:'INCLUDED_IN_RESULT'}}],
        {accountId:'USD_MASTER',periodId:laterId,reason:'synthetic concurrent operation'});
      const activate=JPWForex.state.recordAccountPeriod({accountId:'USD_MASTER',startedAt:'2026-11-01',currency:'USD',si:800,
        openingBook:800,source:'synthetic blocked period',activateCurrentPeriod:true},{reason:'synthetic blocked activation'});
      return {none,unique,ambiguous,mismatch:mismatch.ok,brl:eb.BRL_ONE.periods[brlId].ledger[0].saldo,
        usd:eb.USD_MASTER.periods[usdId].ledger[0].saldo,
        brlCurrency:eb.BRL_ONE.periods[brlId].currency,usdCurrency:eb.USD_MASTER.periods[usdId].currency,
        uiBudget,attached:{status:attached.status,id:attached.declaration?.operationId,
          source:attached.declaration?.association?.source},opId,
        secondOp:secondOp.ok,activate:activate.ok,firstAlive:!!eb.USD_MASTER.periods[usdId].activeOperation,
        laterAlive:!!later.activeOperation};
    });
    check('no Mestre requires explicit operational selection',selectionProof.none,null);
    check('unique Mestre is the initial operational account',selectionProof.unique,'USD_MASTER');
    check('ambiguous Mestre requires explicit selection',selectionProof.ambiguous,null);
    check('registration currency mismatch blocks a period',selectionProof.mismatch,false);
    check('BRL ledger remains in BRL account',selectionProof.brl,2050);
    check('USD ledger remains in USD account',selectionProof.usd,990);
    check('two account contexts retain independent currencies',[selectionProof.brlCurrency,selectionProof.usdCurrency],['BRL','USD']);
    check('budget form registers prospect on new contextual period',selectionProof.uiBudget.confirmed,true);
    check('budget form uses the confirmed period currency',selectionProof.uiBudget.currency,'USD');
    check('first contextual order associates prior budget',selectionProof.attached.status,'OK');
    check('prospective budget binds only the new operation',selectionProof.attached.id,selectionProof.opId);
    check('budget association records the first software fact',selectionProof.attached.source,'FIRST_SOFTWARE_FACT_RECORD');
    check('same account cannot open a second active operation in another period',selectionProof.secondOp,false);
    check('active operation blocks activating a new current period',selectionProof.activate,false);
    check('original operation remains confirmed after blocked attempts',[selectionProof.firstAlive,selectionProof.laterAlive],[true,false]);
    check('second synthetic page has no page errors',secondErrors,[]);
    const third=await context.newPage(),thirdErrors=[];third.on('pageerror',e=>thirdErrors.push(e.message));
    await third.goto(pathToFileURL(path.join(root,'index.html')).href,{waitUntil:'domcontentloaded'});
    const budgetRollback=await third.evaluate(()=>{
      window.__onbShown=true;closeModal();S=structuredClone(DEFAULTS);migrate();S.onboarding.done=true;
      S.accounts=[{forexAccountId:'ROLLBACK_M',nome:'Mestre rollback',tipo:'MESTRE',platformCurrency:'USD'}];
      S.forex=JPWForex.state.empty();if(save()!==true)throw Error('rollback seed refused');
      const x=JPWForex.state,p=x.recordAccountPeriod({accountId:'ROLLBACK_M',startedAt:'2026-09-01',currency:'USD',
        si:1000,openingBook:1000,source:'synthetic rollback',activateCurrentPeriod:true},{reason:'synthetic rollback period'});
      if(!p.ok)throw Error(p.error);
      const periodId=S.forex.accountContexts.accounts.ROLLBACK_M.currentPeriodId;
      const declared=x.recordOperationBudget({accountId:'ROLLBACK_M',periodId,operationId:null,currency:'USD',
        amount:100,declaredBy:'synthetic',declaredAt:'2026-09-01T10:00:00Z',source:'synthetic'},
        {reason:'synthetic budget rollback'});
      if(!declared.ok)throw Error(declared.error);
      const before=JSON.stringify(S.forex),normal=save;
      const order=()=>x.recordAccountOrders([{pi:0,oi:0,changes:{id:'ROLLBACK-ORDER',par:'EURUSD',tipo:'BUY',
        role:'GENESIS',lote:.01,entry:1.1,sl:1,tp:1.2,status:'Aberta',result:null,costs:0,
        costBasis:'INCLUDED_IN_RESULT'}}],{accountId:'ROLLBACK_M',periodId,reason:'synthetic first fact'});
      save=()=>false;const refused=order();save=normal;
      const unchanged=before===JSON.stringify(S.forex);
      const prospect=x.budgetSnapshot({accountId:'ROLLBACK_M',periodId,operationId:null});
      const retry=order(),opId=S.forex.accountContexts.accounts.ROLLBACK_M.periods[periodId].activeOperation?.operationId;
      const attached=x.budgetSnapshot({accountId:'ROLLBACK_M',periodId,operationId:opId});
      return {refused:refused.persistido,unchanged,prospect:prospect.status,
        retry:retry.ok,attached:attached.status};
    });
    check('refused first-order write rolls back budget association',budgetRollback.unchanged,true);
    check('refused first-order write reports no persistence',budgetRollback.refused,false);
    check('prospective budget remains available after refusal',budgetRollback.prospect,'OK');
    check('explicit retry records first order and association',budgetRollback.retry,true);
    check('retried operation reads associated budget',budgetRollback.attached,'OK');
    check('third synthetic page has no page errors',thirdErrors,[]);
    console.log('PASS '+cases.length+'/'+cases.length+' synthetic account-context browser contracts');
  }finally{await browser.close();}
})().catch(error=>{console.error(error.stack||String(error));process.exitCode=1});
