// Historical profile records remain identifiable; current factors come only from policy.
const LEGACY_RISK_PROFILES=[
  {key:'base', name:'Base', fator:1.00, pct:1.00, monthlyTarget:0.0275, ddrTarget:0.15, scenarioDD15:0.15, orderLeverage:0.40, limit:'Conta mestre/base', desc:'Perfil base da arquitetura JP Wealth · mensal 2,75% · drawdown maximo 15,00% · alavancagem por ordem 0,40x.', aliases:['Base','Mestre','Master']},
  {key:'longevity', name:'Longevity', fator:0.66, pct:0.66, monthlyTarget:0.0181, ddrTarget:0.099, scenarioDD15:0.099, orderLeverage:0.26, limit:'≤ 1/3 das contas satélites', desc:'Perfil Longevity · mensal 1,81% · drawdown maximo 9,90% · alavancagem por ordem 0,26x.', aliases:['Longevity']},
  {key:'high_longevity', name:'High Longevity', fator:0.50, pct:0.50, monthlyTarget:0.0137, ddrTarget:0.075, scenarioDD15:0.075, orderLeverage:0.20, limit:'≤ 1/2 das contas satélites', desc:'Perfil High Longevity · mensal 1,37% · drawdown maximo 7,50% · alavancagem por ordem 0,20x.', aliases:['High Longevity']},
  {key:'high_longevity_plus', name:'High Longevity Plus', fator:0.33, pct:0.33, monthlyTarget:0.0090, ddrTarget:0.0495, scenarioDD15:0.0495, orderLeverage:0.13, limit:'Sem teto', desc:'Perfil High Longevity Plus · mensal 0,90% · drawdown maximo 4,95% · alavancagem por ordem 0,13x.', aliases:['High Longevity Plus','High Plus','HL Plus','High Longevity+']},
];
const BASE_TARGET_MONTHLY=JPWForex.policy.planning.referenceMonthlyReturn;
const BASE_TARGET_ANNUAL=null; // the annual normative reference is a range, not monthly compounding
const RISK_PROFILES=LEGACY_RISK_PROFILES.map(old=>Object.freeze({key:old.key,name:old.name,aliases:old.aliases,
  fator:old.key==='base'?1:null,pct:old.key==='base'?1:null,
  monthlyTarget:old.key==='base'?BASE_TARGET_MONTHLY:null,ddrTarget:JPWForex.policy.get('P-03').value/100,
  orderLeverage:null,annualReferenceRange:JPWForex.policy.planning.annualReferenceRange,
  status:old.key==='base'?'DOCUMENTARY_CURRENT':'PENDING',
  limit:'Execução normativa BLOCKED',desc:old.key==='base'?'V11 · referências de planejamento, sem promessa de retorno.':'Fator de replicação P-30 PENDING; cadastro não autoriza replicar.'}));
const ACCT_PROFILES=RISK_PROFILES;
function profileNorm(v){return String(v||'').toLowerCase().replace(/[^a-z0-9]/g,'');}
function riskProfileByAny(v){
  if(v&&typeof v==='object')v=v.key||v.name;
  const n=profileNorm(v);
  return RISK_PROFILES.find(p=>profileNorm(p.key)===n||profileNorm(p.name)===n||(p.aliases||[]).some(a=>profileNorm(a)===n))||
    {key:n||'unassigned',name:String(v||'Não definido'),fator:null,pct:null,monthlyTarget:null,ddrTarget:null,orderLeverage:null,status:'PENDING',aliases:[],desc:'Perfil sem equivalência vigente demonstrada.'};
}
function normalizeRiskProfileName(v){return riskProfileByAny(v).name;}
function normalizeRiskProfileKey(v){return riskProfileByAny(v).key;}
function riskProfilesForState(){return RISK_PROFILES.map(p=>({name:p.name,key:p.key,fator:p.fator,status:p.status,desc:p.desc}));}
function riskProfileMonthlyTarget(p){return riskProfileByAny(p).monthlyTarget;}
function riskProfileAnnualTarget(){return null;}
function riskProfileForAcct(p){const pr=riskProfileByAny(p);return {...pr,mensal:pr.monthlyTarget,anual:null,mdd:pr.ddrTarget,lev:pr.orderLeverage};}
function acctProfiles(){return RISK_PROFILES.map(p=>riskProfileForAcct(p.key));}
function riskProfileOperationalLabel(p){return riskProfileByAny(p).desc;}
function riskProfileUXSummary(p){return riskProfileByAny(p).desc;}
function riskProfileIconText(p){return ({base:'B',longevity:'L',high_longevity:'HL',high_longevity_plus:'H+'})[riskProfileByAny(p).key]||'?';}
function getActiveRiskProfile(profileKey){return riskProfileForAcct(profileKey??(S.period&&S.period.profile)??'base');}
// Explicit documentary reader; legacy/global consumers keep their existing contract.
function getAccountRiskProfileContext(target){return globalThis.JPWForex?.state?.accountProfileContext(target)??null;}
function activeProfileFator(){return getActiveRiskProfile().fator;}
function activeRiskMatrix(){return JPWForex.policy.phases.map(row=>({nome:'FASE '+row.id,
  title:row.name,ddmin:row.lower/100,ddmax:(row.upper===undefined?JPWForex.policy.get(row.upperParameter).value:row.upper)/100,
  baseDdmin:row.lower/100,baseDdmax:(row.upper===undefined?JPWForex.policy.get(row.upperParameter).value:row.upper)/100,alav:row.maxLeverage,fator:null}));}
function activeMDDLimit(){return JPWForex.policy.get('P-03').value/100;}
function activeAlarmLimit(){return null;} // no fabricated V11 alarm threshold
function activeGenesisRiskLimit(){const item=JPWForex.policy.get('P-14');return item.status==='PENDING'?null:item.value/100;}
function forexNewOperationPhases(){return JPWForex.policy.phases.map(row=>({
  title:'FASE '+row.id+' — '+row.name.toUpperCase(),cls:'p'+row.id,faseNome:'FASE '+row.id,
  ddtxt:(row.id===1?'0':'>'+row.lower)+'–'+(row.upper===undefined?JPWForex.policy.get(row.upperParameter).value:row.upper)+'%',
  alavtxt:row.maxLeverage+'x',policyVersion:JPWForex.policy.version,orders:emptyOrders(1)}));}

const jpwAccountProfileObject=value=>!!value&&typeof value==='object'&&!Array.isArray(value);
const jpwAccountProfileString=value=>typeof value==='string'?value.trim():'';
const jpwAccountProfileInstant=value=>!!jpwAccountProfileString(value)&&Number.isFinite(Date.parse(value));
// Documentary account metadata is validated before load/migrate as well as import.
// Pure shape validation only; this never assigns policy or writes state.
const jpwAccountProfileKeys=RISK_PROFILES.map(profile=>profile.key);
const jpwAccountProfileText=value=>typeof value==='string'&&!!value.trim()&&value.length<=500&&!/[\u0000-\u001f\u007f]/.test(value);
function jpwValidAccountProfileAssignment(value,accountId){
  if(value==null)return true; // Older documents have no assignment.
  const seen=new Set();let current=value,lastRevision=null;
  while(current!=null){
    if(!jpwAccountProfileObject(current)||seen.has(current)||current.schemaVersion!==1||!jpwAccountProfileString(current.accountId)||
      (accountId&&current.accountId!==accountId)||current.accountId!==value.accountId||
      !jpwAccountProfileKeys.includes(current.profileKey)||!Number.isSafeInteger(current.revision)||current.revision<1||
      !jpwAccountProfileInstant(current.assignedAt)||!['source','declaredBy','reason'].every(k=>jpwAccountProfileText(current[k]))||
      (lastRevision!==null&&current.revision!==lastRevision-1))return false;
    seen.add(current);lastRevision=current.revision;current=current.previous;
  }
  return lastRevision===1;
}
function jpwValidAccountProfileSnapshot(value,accountId,periodId){
  return value==null||jpwAccountProfileObject(value)&&value.schemaVersion===1&&value.status==='DOCUMENTARY_ONLY'&&
    jpwAccountProfileString(value.accountId)&&jpwAccountProfileString(value.periodId)&&(!accountId||value.accountId===accountId)&&(!periodId||value.periodId===periodId)&&
    jpwAccountProfileKeys.includes(value.profileKey)&&jpwAccountProfileText(value.profileName)&&
    Number.isSafeInteger(value.assignmentRevision)&&value.assignmentRevision>0&&
    jpwAccountProfileInstant(value.assignedAt)&&jpwAccountProfileInstant(value.capturedAt)&&jpwAccountProfileText(value.source)&&jpwAccountProfileText(value.declaredBy)&&jpwAccountProfileString(value.policyVersion);
}
function jpwValidateAccountProfileExtensions(document){
  const accounts=rows=>!Array.isArray(rows)||rows.every(a=>jpwAccountProfileObject(a)&&
    (a.accountEnvironment==null||['','unknown','real','demo'].includes(a.accountEnvironment))&&
    jpwValidAccountProfileAssignment(a.riskProfileAssignment,a.forexAccountId)&&
    (a.riskProfileAssignment==null||a.riskProfileAssignment.accountId===a.forexAccountId));
  const context=c=>c==null||jpwValidAccountProfileSnapshot(c.riskProfileSnapshot,c.accountId,c.periodId);
  if(!accounts(document?.accounts)||!context(document?.activeOperation?.recordContext))return false;
  const envelope=document?.forex?.accountContexts;
  if(jpwAccountProfileObject(envelope)){
    for(const [accountId,archive] of Object.entries(envelope.archivedAccounts||{})){
      const seen=new Set();let entry=archive;
      while(entry!=null){
        if(!jpwAccountProfileObject(entry)||seen.has(entry)||!accounts([entry.record])||entry.record.forexAccountId!==accountId)return false;
        seen.add(entry);entry=entry.previous;
      }
    }
    for(const a of Object.values(envelope.accounts||{}))for(const p of Object.values(a?.periods||{})){
      if(!jpwValidAccountProfileSnapshot(p?.riskProfileSnapshot,p?.accountId,p?.periodId)||!context(p?.activeOperation?.recordContext))return false;
    }
  }
  return !Array.isArray(document?.operationHistory?.records)||document.operationHistory.records.every(r=>
    context(r?.recordContext)&&context(r?.finalizationContext)&&context(r?.entryContext)&&context(r?.operationSnapshot?.recordContext));
}
