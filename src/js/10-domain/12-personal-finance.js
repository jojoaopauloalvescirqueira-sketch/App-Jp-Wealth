// ============ FINANÇAS PESSOAIS · núcleo do domínio (PF-01) ============
// Contrato normativo: docs/architecture/PERSONAL-FINANCE.md. Schema v1 CONGELADO.
//
// Este arquivo é a ÚNICA fonte da política monetária do módulo. Não existe um
// segundo parser nem um segundo formatador: espalhar parsers pela UI foi
// declarado defeito de revisão no congelamento do schema. Todo ponto de
// entrada e saída de dinheiro de Finanças Pessoais passa por aqui.
//
// A unidade do agregado é BRL_CENTS: inteiros em centavos de real.
// R$ 1.420,50 → 142050. null = não informado; 0 = zero explicitamente
// declarado. A distinção é normativa (ausência ≠ zero) e o parser a preserva:
// devolve null para vazio, inteiro para valor válido e NaN para inválido —
// três estados que jamais se confundem.

const PF_MONEY_UNIT = 'BRL_CENTS';
// Competência mensal: 'YYYY-MM'. Mesma forma do FX_MONTH_RE do Planejamento FX,
// duplicada de propósito: reutilizar a constante de outro domínio acoplaria
// Finanças Pessoais ao FX — exatamente a fronteira que o contrato proíbe cruzar.
const PF_MONTH_RE = /^\d{4}-(0[1-9]|1[0-2])$/;

// Identidade permanente: gerada uma vez, persistida, jamais recalculada.
// Mesmo padrão canônico de dgId/pivotStudyId/operationRecordId — a replicação
// por módulo É o padrão do projeto (não há helper compartilhado).
function pfId(prefix){
  return String(prefix||'pf')+'_'+Date.now().toString(36)+'_'+Math.random().toString(36).slice(2,8);
}

function pfMonthKeyValid(m){
  return typeof m==='string' && PF_MONTH_RE.test(m);
}

// ---- parseBRLCents: string → centavos, SEM ponto flutuante no caminho ------
// O número nunca visita parseFloat: os dígitos são extraídos por forma
// reconhecida e o valor é montado por aritmética inteira. Formas aceitas:
//   "1420"      → 142000     (inteiro em reais)
//   "1420,50"   → 142050     (vírgula decimal, 1–2 casas)
//   "1420.50"   → 142050     (ponto decimal, 1–2 casas)
//   "1.420,50"  → 142050     (milhar BR com decimal)
//   "1.420"     → 142000     (milhar BR sem decimal — grupos de 3 exatos)
// Rejeitadas (NaN): letras, parcial numérico, mais de 2 casas decimais,
// mistura ambígua de separadores ("1,420.50"), grupos de milhar quebrados,
// espaços internos, e inteiros com mais de 13 dígitos (overflow além de
// Number.MAX_SAFE_INTEGER em centavos).
// Vazio (após trim) → null: "não informado" é estado real, não erro.
//
// O sinal negativo é RECONHECIDO sintaticamente (útil para a UI detectar e
// explicar), mas parser ≠ guarda semântica: os atos do domínio recusam
// negativo nos campos cujo contrato exige ≥ 0 (pfAmountInDomain abaixo).
function parseBRLCents(txt){
  const t = String(txt==null?'':txt).trim();
  if(!t) return null;
  let s=t, neg=false;
  if(s[0]==='-' || s[0]==='−'){ neg=true; s=s.slice(1); }
  let m, intDigits, decDigits;
  if((m=/^(\d{1,3}(?:\.\d{3})+),(\d{1,2})$/.exec(s))){ intDigits=m[1].replace(/\./g,''); decDigits=m[2]; }
  else if((m=/^(\d{1,3}(?:\.\d{3})+)$/.exec(s)))     { intDigits=m[1].replace(/\./g,''); decDigits=''; }
  else if((m=/^(\d+)[.,](\d{1,2})$/.exec(s)))        { intDigits=m[1]; decDigits=m[2]; }
  else if((m=/^(\d+)$/.exec(s)))                     { intDigits=m[1]; decDigits=''; }
  else return NaN;
  if(intDigits.length>13) return NaN; // overflow: 10^13 reais já excede o domínio seguro em centavos
  const cents = Number(intDigits)*100 + Number((decDigits+'00').slice(0,2));
  if(!Number.isSafeInteger(cents)) return NaN;
  return neg ? -cents : cents;
}

// ---- formatBRLCents: centavos → "R$ 1.420,50", por aritmética de STRING ----
// Sem divisão por 100 em float: o inteiro é fatiado em texto. Exato para
// qualquer centavo seguro, inclusive derivados negativos ("-R$ 1.879,00").
// null/undefined → '—' (não informado). Qualquer coisa que não seja inteiro
// seguro → '—': este formatador não legitima valor que o domínio não aceita.
function formatBRLCents(cents){
  if(cents===null || cents===undefined) return '—';
  if(typeof cents!=='number' || !Number.isSafeInteger(cents)) return '—';
  const neg = cents<0;
  const s = String(Math.abs(cents)).padStart(3,'0');
  const inteiro = s.slice(0,-2).replace(/\B(?=(\d{3})+(?!\d))/g,'.');
  return (neg?'-R$ ':'R$ ')+inteiro+','+s.slice(-2);
}

// ---- guarda semântica de domínio -------------------------------------------
// Campos de ENTRADA do agregado são ≥ 0 (a direção é do campo, não do sinal).
// allowNull decide se "não informado" é aceitável naquele ato.
function pfAmountInDomain(cents, opts){
  const allowNull = !!(opts && opts.allowNull);
  if(cents===null) return allowNull;
  return typeof cents==='number' && Number.isSafeInteger(cents) && cents>=0;
}

// ---- sentinela de unidade monetária (Bloco C) ------------------------------
// moneyUnit é INVARIANTE. Unidade que não seja BRL_CENTS jamais é convertida,
// reinterpretada ou sobrescrita: o agregado fica intacto e o MÓDULO entra em
// modo leitura. O bloqueio é do módulo, nunca do JP Wealth inteiro.
const PF_READ_ONLY_UNSUPPORTED_MONEY_UNIT = 'READ_ONLY_UNSUPPORTED_MONEY_UNIT';
function pfMoneyUnitSupported(){
  return !!(S && S.personalFinance && S.personalFinance.moneyUnit===PF_MONEY_UNIT);
}
// Toda ação MUTÁVEL de Finanças Pessoais consulta esta guarda antes de tocar
// no estado. Retorna null quando a escrita está liberada, ou o código do
// bloqueio. PF-01 não tem ato de escrita ainda; a guarda nasce agora para que
// PF-02+ não tenha como esquecê-la (e para o teste provar o bloqueio).
function pfWriteBlockReason(){
  if(!pfMoneyUnitSupported()) return PF_READ_ONLY_UNSUPPORTED_MONEY_UNIT;
  return null;
}

// ============ PF-02 · TEMPO, WRITE GATE E MATERIALIZAÇÃO ====================

// ---- write gate canônico ----------------------------------------------------
// Invariante normativo do PF-02: TODO ato mutável de Finanças Pessoais passa
// por aqui. Nenhum botão, modal ou fluxo decide "opcionalmente" se consulta a
// sentinela — a fronteira de escrita é uma só.
//
// fn recebe S.personalFinance e aplica a mudança COERENTE do ato (o ato inteiro,
// nunca campo a campo de um formulário atômico). Pode devolver {ok:false, erro}
// para recusar por validação — nesse caso NADA foi mutado por contrato do
// chamador (valide antes de tocar; o gate não tem como desfazer o que fn fizer).
// Retorno: {ok, persistido, erro?, ...extras de fn}. save()===false é prova de
// não-escrita (portões retornam antes do storage) — o chamador decide como
// avisar; o padrão de falha de persistência da casa segue valendo.
function pfMutate(acao, fn, meta){
  const bloqueio = pfWriteBlockReason();
  if(bloqueio) return { ok:false, persistido:false, erro:bloqueio };
  const r = fn(S.personalFinance) || {};
  if(r.ok===false) return { ok:false, persistido:false, erro:r.erro||'ato recusado' };
  // Rótulo GENÉRICO por contrato de privacidade: ação + recordId, nunca nome
  // ou valor financeiro — o changeLog persiste e viaja no backup.
  dgLogChange('personalFinance', String(acao||'ato'), String(r.recordId||''), String((meta&&meta.label)||acao||''));
  const gravou = save();
  return { ok: gravou===true, persistido: gravou===true, erro: gravou===true?undefined:'persistencia recusada', ...r };
}

// ---- competência mensal -----------------------------------------------------
function pfCurrentMonthKey(){
  // dateISO/todayISO (10-domain/04-stop-statistics.js) são locais — nunca o
  // fuso UTC do toISOString, que viraria o mês na noite errada.
  return todayISO().slice(0,7);
}
function pfMonthAdd(key, delta){
  const [y,m] = key.split('-').map(Number);
  const idx = y*12 + (m-1) + delta;
  const ny = Math.floor(idx/12), nm = (idx%12)+1;
  return String(ny).padStart(4,'0')+'-'+String(nm).padStart(2,'0');
}
const PF_MONTH_NAMES = ['JANEIRO','FEVEREIRO','MARÇO','ABRIL','MAIO','JUNHO',
  'JULHO','AGOSTO','SETEMBRO','OUTUBRO','NOVEMBRO','DEZEMBRO'];
function pfMonthLabel(key){
  // Nome é APRESENTAÇÃO; a identidade é sempre a chave YYYY-MM.
  if(!pfMonthKeyValid(key)) return key;
  const [y,m] = key.split('-').map(Number);
  return PF_MONTH_NAMES[m-1]+' '+y;
}

// ---- mês virtual × materializado -------------------------------------------
function pfIsMaterialized(key){
  const pf=S.personalFinance;
  return !!(pf && pf.months && Object.prototype.hasOwnProperty.call(pf.months,key)
    && pf.months[key] && typeof pf.months[key]==='object');
}
function pfRuleAppliesTo(rule, key){
  if(!rule || rule.active===false) return false;
  if(!pfMonthKeyValid(rule.startMonth)) return false;
  if(rule.startMonth > key) return false;
  if(rule.endMonth!=null && pfMonthKeyValid(rule.endMonth) && key > rule.endMonth) return false;
  return true;
}
// Projeções de um mês VIRTUAL: derivadas das regras VIGENTES, a cada render.
// Não são história — mudar a regra muda esta lista, e isso é legítimo porque
// o mês nunca foi registro.
function pfVirtualIncomes(key){
  const pf=S.personalFinance;
  if(!pf || !Array.isArray(pf.recurringIncome)) return [];
  return pf.recurringIncome.filter(r=>pfRuleAppliesTo(r,key)).map(r=>({
    ruleId:r.id, name:String(r.name||''), projectedAmount:(typeof r.amount==='number')?r.amount:null,
  }));
}
// Materialização — SÓ dentro de um ato (via pfMutate). Estampa as projeções
// das regras vigentes NAQUELE INSTANTE, com ruleId preservado; a partir daqui
// o mês é independente e nenhuma automação o reescreve.
function pfMaterializeMonth(pf, key){
  if(!pfMonthKeyValid(key)) return null;
  if(pf.months[key] && typeof pf.months[key]==='object') return pf.months[key];
  pf.months[key] = {
    createdAt: new Date().toISOString(), // carimbo real do ATO (nunca de render)
    incomes: (pf.recurringIncome||[]).filter(r=>pfRuleAppliesTo(r,key)).map(r=>({
      id: pfId('pfi'), name:String(r.name||''),
      projectedAmount:(typeof r.amount==='number')?r.amount:null,
      receivedAmount:null, status:'PROJETADA', ruleId:r.id,
    })),
    expenses: [], debtSnapshots: [], allocations: [], notes: [],
  };
  return pf.months[key];
}

// ---- pendências de meses anteriores ----------------------------------------
// Pendência é EXCLUSIVAMENTE status PENDENTE em despesa ou nota de mês
// MATERIALIZADO anterior ao corrente. Nada é inferido de null, texto livre,
// cobertura incompleta ou ausência de dado.
function pfPendingBefore(currentKey){
  const pf=S.personalFinance;
  if(!pf || !pf.months) return [];
  const out=[];
  for(const key of Object.keys(pf.months).sort()){
    if(!pfMonthKeyValid(key) || key>=currentKey) continue;
    const m=pf.months[key];
    if(!m || typeof m!=='object') continue;
    const despesas = Array.isArray(m.expenses) ? m.expenses.filter(e=>e && e.status==='PENDENTE').length : 0;
    const notas    = Array.isArray(m.notes)    ? m.notes.filter(n=>n && n.status==='PENDENTE').length : 0;
    if(despesas>0 || notas>0) out.push({ key, despesas, notas });
  }
  return out;
}
