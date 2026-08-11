// ============ PLANEJAMENTO FX · MODELO DE DOMÍNIO ============
// Motor de planejamento patrimonial temporal para Forex (Contabilidade/Patrimônio).
// Deriva conceitualmente da planilha histórica "Planejamento FX.xlsx" SEM reproduzir
// suas inconsistências (colunas de reserva 10%/FIIS, coluna de aporte instável,
// datas hardcoded, taxa única de dólar). Três classes de informação NUNCA se
// misturam: PLANEJADO (premissa do usuário), REALIZADO (histórico contábil) e
// NORMATIVO (Estatuto — consumido via reserveRequirementsCalc, nunca duplicado).
//
// Três séries temporais distintas (decisão do gestor, 2026-08-11):
//   BASELINE  → premissas congeladas na aprovação do plano; imutável.
//   FORECAST  → recalculado do último fechamento realizado + premissas vigentes.
//   REALIZADO → fechamentos mensais efetivos; imutável a mudanças de premissa.
//
// CONVENÇÃO DE PROJEÇÃO (documentada e testada): a rentabilidade do mês incide
// sobre o SALDO DE ABERTURA; aportes entram DEPOIS do resultado:
//   close[t] = open[t] + open[t]*rate[t] + aportes[t];  open[t+1] = close[t]
// REALIZADO usa a mesma álgebra do MEI-JP (03-mei-jp.js, Correções 4/5):
//   R_aj = (V_t − V_{t−1} − F_t) / V_{t−1}  ⇔  profit = close − open − aportes
// — nenhuma métrica nova de rentabilidade com fluxo intra-mês foi inventada.
//
// Este módulo é PURO: nenhuma leitura de S, DOM, storage ou rede. A ponte com o
// estado vive em 03-fx-state.js; interface em 04/05. Rentabilidade planejada é
// premissa do usuário — NUNCA deriva de perfis de risco (V10 removeu projeções
// por perfil por ausência de memória de cálculo; ADR-0010 pendente).

const FX_MONTH_RE=/^\d{4}-(0[1-9]|1[0-2])$/;
const FX_HORIZON_MIN=1, FX_HORIZON_MAX=600; // horizonte livre; 600 = teto sanitário (50 anos)

function fxMonthKey(value){
  const key=String(value||'').slice(0,7);
  return FX_MONTH_RE.test(key)?key:'';
}
function fxMonthIndex(value){ // meses desde o ano 0 — mesmo esquema de meiMonthIndex
  const key=fxMonthKey(value); if(!key) return null;
  const [y,m]=key.split('-').map(Number);
  return y*12+m-1;
}
function fxMonthFromIndex(idx){
  const y=Math.floor(idx/12), m=idx-y*12+1;
  return String(y).padStart(4,'0')+'-'+String(m).padStart(2,'0');
}
function fxAddMonths(month,n){
  const idx=fxMonthIndex(month);
  return idx==null?'':fxMonthFromIndex(idx+n);
}
function fxYearOf(month){ return fxMonthKey(month)?month.slice(0,4):''; }

function fxNum(v,fallback=0){ return Number.isFinite(+v)?+v:fallback; }
function fxId(prefix){ return prefix+'_'+Date.now().toString(36)+'_'+Math.random().toString(36).slice(2,8); }

// ---- Premissas (assumptions) ----------------------------------------------
// Estrutura única usada por baseline, current e revisions[].snapshot:
// { startMonth, horizonMonths, initialBalanceUsd, defaultMonthlyReturn,
//   yearOverrides:{'2028':r}, monthOverrides:{'2028-03':r},
//   plannedContributions:{'YYYY-MM':{personalUsd,propUsd}}, projectedFxRate }
// initialBalanceUsd é PARÂMETRO DO PLANEJAMENTO (decisão 3) — não é fonte
// canônica da Conta Mestre nem do patrimônio institucional.
// startMonth/horizonMonths/initialBalanceUsd são estruturais: congelados com o
// baseline; `current` só revisa premissas de futuro (taxas, aportes, câmbio).

// Precedência de rentabilidade: mês > ano > padrão (seção 7 da especificação).
function fxResolveRate(assumptions,month){
  const mo=assumptions.monthOverrides||{};
  if(Object.prototype.hasOwnProperty.call(mo,month)&&Number.isFinite(+mo[month])) return +mo[month];
  const yo=assumptions.yearOverrides||{}, year=fxYearOf(month);
  if(Object.prototype.hasOwnProperty.call(yo,year)&&Number.isFinite(+yo[year])) return +yo[year];
  return fxNum(assumptions.defaultMonthlyReturn,0);
}
function fxPlannedContribution(assumptions,month){
  const rec=(assumptions.plannedContributions||{})[month]||{};
  const personal=Math.max(0,fxNum(rec.personalUsd)), prop=Math.max(0,fxNum(rec.propUsd));
  return {personalUsd:personal, propUsd:prop, totalUsd:personal+prop};
}
function fxNormalizeAssumptions(raw){
  const src=raw&&typeof raw==='object'?raw:{};
  const startMonth=fxMonthKey(src.startMonth);
  const horizon=Math.round(fxNum(src.horizonMonths));
  const out={
    startMonth,
    horizonMonths:Math.max(FX_HORIZON_MIN,Math.min(FX_HORIZON_MAX,horizon||0)),
    initialBalanceUsd:Math.max(0,fxNum(src.initialBalanceUsd)),
    defaultMonthlyReturn:fxNum(src.defaultMonthlyReturn),
    yearOverrides:{}, monthOverrides:{}, plannedContributions:{},
    projectedFxRate:fxNum(src.projectedFxRate,null)>0?+src.projectedFxRate:null
  };
  Object.entries(src.yearOverrides||{}).forEach(([y,r])=>{
    if(/^\d{4}$/.test(y)&&Number.isFinite(+r)&&+r>-1) out.yearOverrides[y]=+r;
  });
  Object.entries(src.monthOverrides||{}).forEach(([m,r])=>{
    if(fxMonthKey(m)&&Number.isFinite(+r)&&+r>-1) out.monthOverrides[m]=+r;
  });
  Object.entries(src.plannedContributions||{}).forEach(([m,rec])=>{
    const key=fxMonthKey(m); if(!key||!rec||typeof rec!=='object') return;
    const personal=Math.max(0,fxNum(rec.personalUsd)), prop=Math.max(0,fxNum(rec.propUsd));
    if(personal>0||prop>0) out.plannedContributions[key]={personalUsd:personal,propUsd:prop};
  });
  return out;
}
function fxValidateAssumptions(a){
  const errors=[];
  if(!fxMonthKey(a.startMonth)) errors.push('Mês inicial inválido (use AAAA-MM).');
  const h=Math.round(fxNum(a.horizonMonths));
  if(!(h>=FX_HORIZON_MIN&&h<=FX_HORIZON_MAX)) errors.push(`Horizonte deve estar entre ${FX_HORIZON_MIN} e ${FX_HORIZON_MAX} meses.`);
  if(!(fxNum(a.initialBalanceUsd)>0)) errors.push('Saldo inicial do planejamento deve ser maior que zero.');
  if(!Number.isFinite(+a.defaultMonthlyReturn)||+a.defaultMonthlyReturn<=-1) errors.push('Rentabilidade padrão inválida (deve ser fração > −100%).');
  return errors;
}

// ---- Realizado -------------------------------------------------------------
// actuals: {'YYYY-MM':{inputType:'rate'|'usd', returnRate, profitUsd,
//   valuationFxRate, notes, closedAt, updatedAt}}
// Os APORTES REALIZADOS não vivem aqui: a fonte única é o ledger contributions[]
// (evita a dupla escrituração que a planilha tinha na coluna K). inputType marca
// qual campo foi a ENTRADA ORIGINAL; o outro é DERIVADO pelo motor.
function fxNormalizeActual(raw){
  const src=raw&&typeof raw==='object'?raw:{};
  const inputType=src.inputType==='usd'?'usd':'rate';
  const rate=Number.isFinite(+src.returnRate)?+src.returnRate:null;
  const usd=Number.isFinite(+src.profitUsd)?+src.profitUsd:null;
  return {
    inputType,
    returnRate:inputType==='rate'?rate:null,   // só a entrada original persiste;
    profitUsd:inputType==='usd'?usd:null,      // o derivado é recalculado sempre
    valuationFxRate:fxNum(src.valuationFxRate,null)>0?+src.valuationFxRate:null,
    notes:String(src.notes||''),
    closedAt:String(src.closedAt||''),
    updatedAt:String(src.updatedAt||'')
  };
}
function fxValidateActualInput(rec){
  const errors=[];
  if(rec.inputType==='rate'){
    if(!Number.isFinite(+rec.returnRate)||+rec.returnRate<=-1) errors.push('Rentabilidade realizada inválida (fração > −100%).');
  } else if(rec.inputType==='usd'){
    if(!Number.isFinite(+rec.profitUsd)) errors.push('Resultado realizado em USD inválido.');
  } else errors.push('Tipo de entrada do realizado deve ser taxa ou USD.');
  return errors;
}

// ---- Ledger cambial de aportes ---------------------------------------------
// contributions[]: {id, month, source:'personal'|'prop', originalCurrency:'BRL'|'USD',
//   originalAmount, usdAmount, acquisitionFxRate, affectsFxCostBasis, notes, createdAt}
// Três conceitos de câmbio NUNCA se confundem (seção 10 da especificação):
//   acquisitionFxRate → taxa efetivamente paga na aquisição (histórico contábil);
//   valuationFxRate   → taxa de conversão do patrimônio na data (realizado mensal);
//   projectedFxRate   → premissa de projeção (assumptions).
// Só transações affectsFxCostBasis:true alimentam o custo médio; entradas
// USD-nativas (ex.: crédito de Prop Firm) nascem com false.
function fxNormalizeContribution(raw){
  const src=raw&&typeof raw==='object'?raw:{};
  const month=fxMonthKey(src.month);
  const currency=src.originalCurrency==='BRL'?'BRL':'USD';
  const rate=fxNum(src.acquisitionFxRate,null)>0?+src.acquisitionFxRate:null;
  const original=Math.max(0,fxNum(src.originalAmount));
  let usd=Math.max(0,fxNum(src.usdAmount));
  if(currency==='BRL'&&rate&&original>0&&!(usd>0)) usd=original/rate; // derivação canônica
  if(currency==='USD'&&!(usd>0)) usd=original;
  return {
    id:String(src.id||'')||fxId('fxc'),
    month,
    source:src.source==='prop'?'prop':'personal',
    originalCurrency:currency,
    originalAmount:original,
    usdAmount:usd,
    acquisitionFxRate:currency==='BRL'?rate:null,
    affectsFxCostBasis:currency==='BRL'?src.affectsFxCostBasis!==false:false,
    notes:String(src.notes||''),
    createdAt:String(src.createdAt||'')
  };
}
function fxValidateContribution(c){
  const errors=[];
  if(!fxMonthKey(c.month)) errors.push('Mês do aporte inválido (use AAAA-MM).');
  if(!(fxNum(c.usdAmount)>0)) errors.push('Valor do aporte em USD deve ser maior que zero.');
  if(c.originalCurrency==='BRL'){
    if(!(fxNum(c.acquisitionFxRate)>0)) errors.push('Aporte em BRL exige a taxa USD/BRL efetivamente paga.');
    else if(fxNum(c.originalAmount)>0){
      const implied=c.originalAmount/c.acquisitionFxRate;
      if(Math.abs(implied-c.usdAmount)>Math.max(0.01,implied*1e-6)) errors.push('Valor USD inconsistente com BRL ÷ taxa de aquisição.');
    }
  }
  return errors;
}

// ---- Plano -----------------------------------------------------------------
function fxCreatePlan({name,assumptions,now}){
  const ts=String(now||new Date().toISOString());
  const base=fxNormalizeAssumptions(assumptions);
  return {
    id:fxId('fxp'),
    name:String(name||'').trim()||'Planejamento FX',
    createdAt:ts, updatedAt:ts,
    baseline:{...base, frozenAt:ts},        // congelado — nunca editado depois
    current:{...base, revisedAt:ts},        // premissas vigentes do forecast
    revisions:[],                           // snapshots leves de premissas anteriores
    actuals:{},                             // 'YYYY-MM' → fechamento realizado
    contributions:[]                        // ledger cambial (fonte única de aportes realizados)
  };
}
// Revisão de premissas: o snapshot ANTERIOR de `current` é preservado em
// revisions[] antes da troca — o baseline jamais é tocado (requisito adicional).
function fxReviseAssumptions(plan,nextAssumptions,{now,note}={}){
  const ts=String(now||new Date().toISOString());
  const prev={...plan.current};
  const structural={startMonth:plan.baseline.startMonth,
    horizonMonths:plan.baseline.horizonMonths,
    initialBalanceUsd:plan.baseline.initialBalanceUsd}; // estruturais não mudam pós-criação
  const next={...fxNormalizeAssumptions({...nextAssumptions,...structural}),revisedAt:ts};
  return {...plan, updatedAt:ts, current:next,
    revisions:[...(plan.revisions||[]),{revisedAt:prev.revisedAt||plan.createdAt,supersededAt:ts,note:String(note||''),snapshot:prev}]};
}
