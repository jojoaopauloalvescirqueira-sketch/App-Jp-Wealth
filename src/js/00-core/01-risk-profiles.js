// ============ PERFIS DE RISCO V10.0 (fonte única) ============
const BASE_TARGET_MONTHLY=0.0275;
const BASE_TARGET_ANNUAL=Math.pow(1+BASE_TARGET_MONTHLY,12)-1;
const RISK_PROFILES=[
  {key:'base', name:'Base', fator:1.00, pct:1.00, monthlyTarget:0.0275, ddrTarget:0.15, scenarioDD15:0.15, orderLeverage:0.40, limit:'Conta mestre/base', desc:'Perfil base da arquitetura JP Wealth · mensal 2,75% · drawdown maximo 15,00% · alavancagem por ordem 0,40x.', aliases:['Base','Mestre','Master']},
  {key:'longevity', name:'Longevity', fator:0.66, pct:0.66, monthlyTarget:0.0181, ddrTarget:0.099, scenarioDD15:0.099, orderLeverage:0.26, limit:'≤ 1/3 das contas satélites', desc:'Perfil Longevity · mensal 1,81% · drawdown maximo 9,90% · alavancagem por ordem 0,26x.', aliases:['Longevity']},
  {key:'high_longevity', name:'High Longevity', fator:0.50, pct:0.50, monthlyTarget:0.0137, ddrTarget:0.075, scenarioDD15:0.075, orderLeverage:0.20, limit:'≤ 1/2 das contas satélites', desc:'Perfil High Longevity · mensal 1,37% · drawdown maximo 7,50% · alavancagem por ordem 0,20x.', aliases:['High Longevity']},
  {key:'high_longevity_plus', name:'High Longevity Plus', fator:0.33, pct:0.33, monthlyTarget:0.0090, ddrTarget:0.0495, scenarioDD15:0.0495, orderLeverage:0.13, limit:'Sem teto', desc:'Perfil High Longevity Plus · mensal 0,90% · drawdown maximo 4,95% · alavancagem por ordem 0,13x.', aliases:['High Longevity Plus','High Plus','HL Plus','High Longevity+']},
];
const ACCT_PROFILES=RISK_PROFILES; // compatibilidade: lista derivada da fonte central, sem valores proprios
function profileNorm(v){ return String(v||'').toLowerCase().replace(/[^a-z0-9]/g,''); }
function riskProfileByAny(v){
  if(v && typeof v==='object'){
    if(v.key || v.name) return riskProfileByAny(v.key||v.name);
  }
  const n=profileNorm(v);
  if(!n) return RISK_PROFILES[0];
  return RISK_PROFILES.find(p=>profileNorm(p.key)===n || profileNorm(p.name)===n || (p.aliases||[]).some(a=>profileNorm(a)===n))||RISK_PROFILES[0];
}
function normalizeRiskProfileName(v){ return riskProfileByAny(v).name; }
function normalizeRiskProfileKey(v){ return riskProfileByAny(v).key; }
function riskProfilesForState(){
  return RISK_PROFILES.map(p=>({name:p.name, fator:p.fator, desc:p.desc, key:p.key}));
}
function riskProfileMonthlyTarget(p){
  const pr=riskProfileByAny(p);
  return typeof pr.monthlyTarget==='number' ? pr.monthlyTarget : BASE_TARGET_MONTHLY;
}
function riskProfileAnnualTarget(p){
  const monthly=riskProfileMonthlyTarget(p);
  return Math.pow(1+monthly,12)-1;
}
function riskProfileForAcct(p){
  const pr=riskProfileByAny(p);
  return {...pr, mensal:riskProfileMonthlyTarget(pr), anual:riskProfileAnnualTarget(pr), mdd:pr.ddrTarget, lev:pr.orderLeverage};
}
function acctProfiles(){ return RISK_PROFILES.map(p=>riskProfileForAcct(p.key)); }
function riskProfileOperationalLabel(p){
  const key=riskProfileByAny(p).key;
  if(key==='base') return 'Perfil base da arquitetura JP Wealth.';
  if(key==='longevity') return 'Perfil voltado para preservacao de capital com continuidade operacional.';
  if(key==='high_longevity') return 'Perfil conservador para desaceleracao estrutural do risco.';
  if(key==='high_longevity_plus') return 'Perfil de preservacao maxima e exposicao bastante reduzida.';
  return 'Perfil operacional da estrutura JP Wealth.';
}
function riskProfileIconText(p){
  const key=riskProfileByAny(p).key;
  if(key==='base') return 'B';
  if(key==='longevity') return 'L';
  if(key==='high_longevity') return 'HL';
  if(key==='high_longevity_plus') return 'H+';
  return 'R';
}
function riskProfileUXSummary(p){
  const key=riskProfileByAny(p).key;
  if(key==='base') return 'Perfil integral da arquitetura JP Wealth. Maior expectativa, maior tolerancia a drawdown e maior exigencia de disciplina operacional.';
  if(key==='longevity') return 'Perfil voltado para longevidade da conta. Reduz exposicao para preservar capital e suavizar drawdown.';
  if(key==='high_longevity') return 'Perfil defensivo, priorizando estabilidade e sobrevivencia estatistica acima de retorno.';
  if(key==='high_longevity_plus') return 'Perfil ultraconservador. Indicado para maxima preservacao, menor oscilacao e menor agressividade operacional.';
  return riskProfileOperationalLabel(p);
}
function getActiveRiskProfile(profileKey){
  return riskProfileForAcct(profileKey ?? (S.period&&S.period.profile) ?? 'base');
}
// SET 11 — escalonamento proporcional real: fator do perfil ativo (Base=1.0 se não houver período).
// Aplicado à Matriz Quadrifásica (ddmax), Gênese (Art. 8.6), Defesa Final F4 e Guilhotina/Alarme,
// para que "grade de operações e margem" realmente sigam o perfil escolhido, não só as metas de retorno.
function activeProfileFator(){
  const p=getActiveRiskProfile();
  return (p && typeof p.fator==='number' && p.fator>0) ? p.fator : 1;
}
function activeRiskMatrix(profileKey){
  const pr = profileKey==null ? getActiveRiskProfile() : getActiveRiskProfile(profileKey);
  const fator=(pr && typeof pr.fator==='number' && pr.fator>0) ? pr.fator : 1;
  const base=(S && Array.isArray(S.matrix) && S.matrix.length) ? S.matrix : DEFAULTS.matrix;
  return base.map((row,i)=>{
    const baseDdmin=i===0 ? 0 : (base[i-1] ? base[i-1].ddmax : row.ddmin);
    return {
      ...row,
      baseDdmin,
      baseDdmax:row.ddmax,
      ddmin:baseDdmin*fator,
      ddmax:row.ddmax*fator,
      fator
    };
  });
}
function activeMDDLimit(){
  const base=(S && S.params && typeof S.params.mdd==='number') ? S.params.mdd : 0.15;
  return base*activeProfileFator();
}
function activeAlarmLimit(){
  const base=(S && S.params && typeof S.params.alarm==='number') ? S.params.alarm : 0.13;
  return base*activeProfileFator();
}
function activeGenesisRiskLimit(){
  const base=(S && S.params && typeof S.params.genRisk==='number') ? S.params.genRisk : 0.01;
  return base*activeProfileFator();
}
