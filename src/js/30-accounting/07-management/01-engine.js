// Annual management read model. Worksheet arithmetic is descriptive; this
// module neither authorizes trading nor reads/writes app state, DOM or storage.
(function(root){
  'use strict';
  const object=v=>v!==null&&typeof v==='object'&&!Array.isArray(v);
  const finite=v=>typeof v==='number'&&Number.isFinite(v);
  const text=v=>typeof v==='string'&&v.trim().length>0;
  const clone=v=>JSON.parse(JSON.stringify(v));
  const DAY=86400000;
  function utcDate(key){const d=new Date(0);d.setUTCFullYear(Number(key.slice(0,4)),Number(key.slice(5,7))-1,Number(key.slice(8,10)));d.setUTCHours(12,0,0,0);return d;}
  function dateKey(value){
    if(Object.prototype.toString.call(value)==='[object Date]'){
      if(!Number.isFinite(value.getTime()))return '';
      value=String(value.getFullYear()).padStart(4,'0')+'-'+String(value.getMonth()+1).padStart(2,'0')+'-'+String(value.getDate()).padStart(2,'0');
    }
    if(typeof value!=='string'||!/^\d{4}-(0[1-9]|1[0-2])-(0[1-9]|[12]\d|3[01])$/.test(value)||Number(value.slice(0,4))<1)return '';
    const d=utcDate(value);return Number.isFinite(+d)&&d.toISOString().slice(0,10)===value?value:'';
  }
  const endOfYear=c=>String(c.year).padStart(4,'0')+'-12-31';
  const beginningOfYear=c=>String(c.year).padStart(4,'0')+'-01-01';
  function dayDifference(date,from){const toKey=dateKey(date),fromKey=dateKey(from);return toKey&&fromKey?Math.round((+utcDate(toKey)-+utcDate(fromKey))/DAY):null;}
  function validateConfig(c){
    if(!object(c))return ['Configuração anual ausente.'];
    const errors=[];
    if(!text(c.accountId)||!text(c.periodId))errors.push('Identifique a conta e o período confirmados.');
    if(!Number.isInteger(c.year)||c.year<1||c.year>9999)errors.push('Ano civil inválido.');
    if(!dateKey(c.startDate)||Number(c.startDate.slice(0,4))!==c.year)errors.push('A data inicial deve pertencer ao ano do plano.');
    if(!finite(c.initialBalance)||c.initialBalance<=0)errors.push('Confirme um saldo inicial positivo.');
    if(typeof c.currency!=='string'||!/^[A-Z]{3}$/.test(c.currency))errors.push('Moeda confirmada inválida.');
    if(!finite(c.annualTarget)||c.annualTarget<=-1)errors.push('O objetivo anual deve ser finito e maior que -100%.');
    if(!finite(c.daysPerWeek)||c.daysPerWeek<=0||c.daysPerWeek>7)errors.push('Dias por semana deve ser maior que zero e até sete.');
    if(!finite(c.monthsPerYear)||c.monthsPerYear<=0||c.monthsPerYear>12)errors.push('Meses por ano deve ser maior que zero e até doze.');
    if(c.referenceYears!==undefined&&(!finite(c.referenceYears)||c.referenceYears<=0))errors.push('Anos da referência deve ser positivo.');
    if(c.referenceDays!==undefined&&(!finite(c.referenceDays)||c.referenceDays<=0))errors.push('Dias da referência deve ser positivo.');
    if(!Array.isArray(c.excludedDates)||c.excludedDates.some(d=>!dateKey(d)||Number(d.slice(0,4))!==c.year))errors.push('Exclusões devem ser datas válidas do ano do plano.');
    else if(new Set(c.excludedDates).size!==c.excludedDates.length)errors.push('Cada data excluída deve ser informada uma única vez.');
    return errors;
  }
  function eligibleDates(c,start){
    const dates=[],excluded=new Set(c.excludedDates),end=+utcDate(endOfYear(c));
    for(let d=utcDate(start);+d<=end;d=new Date(+d+DAY)){
      const key=d.toISOString().slice(0,10),weekday=d.getUTCDay();
      if(weekday!==0&&weekday!==6&&!excluded.has(key))dates.push(key);
    }
    return dates;
  }
  function calendar(c){return validateConfig(c).length?[]:eligibleDates(c,c.startDate);}
  function weekKey(date){const d=utcDate(date);d.setUTCDate(d.getUTCDate()-((d.getUTCDay()+6)%7));return d.toISOString().slice(0,10);}
  const inactive=r=>r&&(['VOIDED','voided','CANCELLED'].includes(r.status)||['VOIDED','voided'].includes(r.recordStatus)||r.voided===true);
  const sameScope=(r,c)=>(r.accountId===undefined||r.accountId===c.accountId)&&(r.periodId===undefined||r.periodId===c.periodId)&&(r.currency===undefined||r.currency===c.currency);
  function stable(v){
    if(Array.isArray(v))return v.map(stable);
    if(object(v)){const o={};for(const k of Object.keys(v).sort())if(v[k]!==undefined)o[k]=stable(v[k]);return o;}
    return v;
  }
  function dependencies(c,{ledger=[],declarations=[],openingSource=null}={}){
    const end=endOfYear(c),recordDate=r=>r.data||r.date||'';
    const facts=ledger.filter(r=>object(r)&&sameScope(r,c)&&recordDate(r)<=end&&!inactive(r)).map(r=>clone(r));
    facts.sort((a,b)=>recordDate(a).localeCompare(recordDate(b))||String(a.id||'').localeCompare(String(b.id||'')));
    const declared=declarations.filter(r=>object(r)&&sameScope(r,c)).map(r=>clone(r)).sort((a,b)=>String(a.date).localeCompare(String(b.date))||String(a.id||'').localeCompare(String(b.id||'')));
    const config=clone(c);if(Array.isArray(config.excludedDates))config.excludedDates=[...new Set(config.excludedDates)].sort();
    return JSON.stringify(stable({config,ledger:facts,declarations:declared,openingSource}));
  }
  function unavailable(reason){return {ok:false,equivalentDate:null,days:null,color:null,direction:null,reason};}
  function fail(config,errors){return {ok:false,errors,config:object(config)?clone(config):null,rows:[],summary:null,referenceDate:null,readyForAnnualClose:false};}
  function build(config,options={}){
    const errors=validateConfig(config);if(errors.length)return fail(config,errors);
    const c=clone(config),today=dateKey(options.today===undefined?new Date():options.today),ledger=options.ledger===undefined?[]:options.ledger,declarations=options.declarations===undefined?[]:options.declarations;
    const actualInitial=options.actualOpeningBalance===undefined?c.initialBalance:options.actualOpeningBalance;
    if(!today)errors.push('Data de referência inválida.');
    if(options.periodStart!==undefined&&options.periodStart!==null&&(!dateKey(options.periodStart)||options.periodStart>c.startDate))errors.push('O plano não pode começar antes do período confirmado.');
    if(actualInitial!==null&&!finite(actualInitial))errors.push('Abertura real inválida.');
    if(!Array.isArray(ledger)||!Array.isArray(declarations))errors.push('Fontes de realizados inválidas.');
    if(errors.length)return fail(c,errors);
    const end=endOfYear(c),eligible=calendar(c),full=eligibleDates(c,beginningOfYear(c));
    if(!eligible.length||!full.length)return fail(c,['Não há dias elegíveis na programação deste plano.']);
    const referenceDate=Number(today.slice(0,4))<c.year?null:(today>end?end:today),eligibleSet=new Set(eligible),records=new Map(),declared=new Map();
    for(const r of ledger){
      if(!object(r)){errors.push('Lançamento realizado inválido.');continue;}
      if(inactive(r))continue;
      if(r.accountId!==c.accountId||r.periodId!==c.periodId||r.currency!==c.currency||!dateKey(r.data)||!finite(r.resultado)||!finite(r.saldo)){errors.push('Lançamento com identidade, moeda, data ou valores incompatíveis.');continue;}
      if(r.data<c.startDate||r.data>end)continue;
      if(records.has(r.data)){errors.push('Há mais de um fechamento realizado na mesma data.');continue;}
      records.set(r.data,clone(r));
    }
    for(const d of declarations){
      if(!object(d)||!sameScope(d,c)||!dateKey(d.date)||d.kind!=='NO_RESULT'||!text(d.reason)){errors.push('A declaração exige data, ausência explícita de resultado e motivo.');continue;}
      if(d.date<c.startDate||d.date>end)continue;
      if(declared.has(d.date)||records.has(d.date)){errors.push('A declaração não pode duplicar ou contradizer um fechamento.');continue;}
      declared.set(d.date,clone(d));
    }
    if(errors.length)return fail(c,errors);
    const fraction=eligible.length/full.length,programmedDays=c.daysPerWeek*52*c.monthsPerYear/12,partialProgrammedDays=programmedDays*fraction,partialMonths=c.monthsPerYear*fraction;
    // Applying the same fraction to target and time cancels algebraically.
    // Direct roots avoid cancellation when a short plan has a tiny target.
    const partialTarget=Math.expm1(Math.log1p(c.annualTarget)*fraction),dailyTarget=Math.expm1(Math.log1p(c.annualTarget)/programmedDays),monthlyTarget=Math.expm1(Math.log1p(c.annualTarget)/c.monthsPerYear);
    const dates=[...new Set([...eligible,...records.keys(),...declared.keys()])].sort(),rows=[];
    let plannedBalance=c.initialBalance,actualBalance=actualInitial,latestBalance=actualInitial,balanceDate=null,index=0,recordedDays=0,declaredDays=0,recordedResult=0,mismatches=0;
    const pendingDates=[];
    for(const date of dates){
      const isEligible=eligibleSet.has(date),due=referenceDate!==null&&date<=referenceDate,record=records.get(date)||null,declaration=declared.get(date)||null;
      const result=isEligible?plannedBalance*dailyTarget:0,closing=plannedBalance+result;
      if(!finite(result)||!finite(closing))return fail(c,['A projeção excede o domínio numérico; revise as premissas.']);
      const planned={opening:plannedBalance,result,closing,cumulative:closing/c.initialBalance-1};
      plannedBalance=closing;if(isEligible)index++;
      const actual={opening:due?actualBalance:null,result:null,closing:null,cumulative:null,record,id:record?record.id||null:null,version:record?record.version??0:null,status:due?'PENDING':'FUTURE',observedClosing:record?record.balanceInput==='OBSERVED':false,mismatch:false,declaration};
      if(record){
        actual.status='RECORDED';actual.result=record.resultado;actual.closing=record.saldo;
        if(due){
          actual.mismatch=finite(actualBalance)&&Math.abs(actualBalance+record.resultado-record.saldo)>Math.max(1e-8,Math.abs(record.saldo)*1e-12);
          if(actual.mismatch)mismatches++;
          actualBalance=record.saldo;latestBalance=record.saldo;balanceDate=date;recordedDays++;recordedResult+=record.resultado;
        }
      }else if(due&&declaration){
        actual.status='NO_RESULT';actual.closing=actualBalance;declaredDays++;
      }else if(due&&isEligible){pendingDates.push(date);actualBalance=null;}
      if(finite(actual.closing)&&finite(actualInitial)&&actualInitial!==0)actual.cumulative=actual.closing/actualInitial-1;
      rows.push({date,weekKey:weekKey(date),index:isEligible?index:null,eligible:isEligible,planned,actual});
    }
    const elapsedDays=referenceDate===null?0:eligible.filter(d=>d<=referenceDate).length;
    const started=referenceDate!==null&&referenceDate>=c.startDate,completeActual=started&&elapsedDays>0&&pendingDates.length===0&&mismatches===0&&finite(actualInitial);
    let realDailyRate=null,projectedMonth=null,projectedYear=null;
    if(completeActual&&actualInitial>0&&latestBalance>0){
      const rate=Math.expm1(Math.log(latestBalance/actualInitial)/elapsedDays);
      if(finite(rate)){realDailyRate=rate;const month=Math.expm1(Math.log1p(rate)*c.daysPerWeek*4),year=Math.expm1(Math.log1p(rate)*240);projectedMonth=finite(month)?month:null;projectedYear=finite(year)?year:null;}
    }
    const plannedRows=rows.filter(r=>r.eligible),monotonic=dailyTarget>0&&plannedRows.every((r,i)=>!i||r.planned.opening>plannedRows[i-1].planned.opening);
    const targetMatch=monotonic?plannedRows.filter(r=>r.planned.cumulative<=partialTarget).at(-1):null;
    let thermometer=unavailable(!started?'O plano ainda não começou.':!completeActual?'Há dias pendentes, abertura ausente ou saldos a reconciliar.':!monotonic?'O alvo não produz uma sequência crescente válida para esta comparação.':'Saldo fora do domínio da comparação.');
    if(completeActual&&monotonic&&latestBalance>0){
      const equivalent=plannedRows.filter(r=>r.planned.opening<=latestBalance).at(-1);
      if(equivalent){const days=Math.round((+utcDate(equivalent.date)-+utcDate(referenceDate))/DAY);thermometer={ok:true,equivalentDate:equivalent.date,days,color:days<14?'green':days<=29?'amber':'red',direction:days>0?'AHEAD':days<0?'BEHIND':'ON_PLAN',reason:null};}
    }
    const referenceDays=c.referenceDays===undefined?364:c.referenceDays;
    const reference={years:c.referenceYears===undefined?1:c.referenceYears,days:referenceDays,daysPerMonth30:referenceDays/30,calendarMonthDays:referenceDays/12,weeks:referenceDays/7,daysPerWeek:7};
    const summary={status:!started?'NOT_STARTED':completeActual?'COMPLETE':'INCOMPLETE',referenceDate,reference,initialBalance:c.initialBalance,actualInitialBalance:actualInitial,currentBalance:started?latestBalance:null,balanceDate,
      accumulatedResult:started&&finite(latestBalance)&&finite(actualInitial)?latestBalance-actualInitial:null,recordedResult,realCumulative:started&&finite(latestBalance)&&finite(actualInitial)&&actualInitial!==0?latestBalance/actualInitial-1:null,
      annualEligibleDays:full.length,eligibleDays:eligible.length,elapsedDays,recordedDays,declaredDays,pendingDays:pendingDates.length,pendingDates,mismatches,completeActual,
      fraction,programmedDays,partialProgrammedDays,partialMonths,annualTarget:c.annualTarget,annualTargetAmount:c.initialBalance*c.annualTarget,partialTarget,partialTargetAmount:c.initialBalance*partialTarget,
      desiredBalance:c.initialBalance*(1+partialTarget),projectedClosing:plannedBalance,dailyTarget,monthlyTarget,realDailyRate,projectedMonth,projectedYear,targetDate:targetMatch?targetMatch.date:null,thermometer};
    if(Object.values(summary).some(v=>typeof v==='number'&&!finite(v)))return fail(c,['Os resultados excedem o domínio numérico; revise as premissas.']);
    return {ok:true,errors:[],config:c,rows,summary,referenceDate,readyForAnnualClose:today>end&&completeActual};
  }
  const api=Object.freeze({dateKey,dayDifference,validateConfig,calendar,build,dependencies});
  root.JPWAnnualEngine=api;
  if(typeof module==='object'&&module.exports)module.exports=api;
})(typeof window!=='undefined'?window:globalThis);
