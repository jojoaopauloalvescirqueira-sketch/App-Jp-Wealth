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
