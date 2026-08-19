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

// ============ PF-02 · BLOCO B — RECEITAS E RECORRÊNCIA ======================
// Atos do domínio. Todos passam por pfMutate; todos validam ANTES de tocar o
// estado (o gate não desfaz o que fn fizer). Campos monetários chegam aqui já
// em centavos (ou null) — o parse é da UI, a guarda de domínio é daqui.

function pfFindIncome(pf, monthKey, incomeId){
  const m = pf.months[monthKey];
  if(!m || !Array.isArray(m.incomes)) return null;
  return m.incomes.find(i=>i && i.id===incomeId) || null;
}

function pfActAddIncome(monthKey, dados){
  if(!pfMonthKeyValid(monthKey)) return { ok:false, erro:'competência inválida' };
  const nome = String((dados&&dados.name)||'').trim();
  if(!nome) return { ok:false, erro:'descrição obrigatória' };
  const proj = (dados&&dados.projectedAmount!==undefined) ? dados.projectedAmount : null;
  if(!pfAmountInDomain(proj,{allowNull:true})) return { ok:false, erro:'valor projetado fora do domínio (≥ 0 ou vazio)' };
  return pfMutate('income_add', pf => {
    const m = pfMaterializeMonth(pf, monthKey);
    const rec = { id: pfId('pfi'), name: nome, projectedAmount: proj,
                  receivedAmount: null, status:'PROJETADA', ruleId: null };
    m.incomes.push(rec);
    return { recordId: rec.id };
  });
}

// Edição por campo (name | projectedAmount | receivedAmount). Um campo por ato:
// a edição inline da linha é discreta por natureza (change), não um formulário
// atômico — cada commit de campo é o ato inteiro.
function pfActUpdateIncomeField(monthKey, incomeId, campo, valor){
  const pf0 = S.personalFinance;
  const alvo = pfFindIncome(pf0, monthKey, incomeId);
  if(!alvo) return { ok:false, erro:'receita inexistente' };
  if(campo==='name'){
    const nome = String(valor||'').trim();
    if(!nome) return { ok:false, erro:'descrição obrigatória' };
    return pfMutate('income_update', pf => { pfFindIncome(pf,monthKey,incomeId).name = nome; return { recordId: incomeId }; });
  }
  if(campo==='projectedAmount' || campo==='receivedAmount'){
    if(!pfAmountInDomain(valor,{allowNull:true})) return { ok:false, erro:'valor fora do domínio (≥ 0 ou vazio)' };
    if(campo==='receivedAmount' && valor===null && alvo.status==='RECEBIDA')
      return { ok:false, erro:'RECEBIDA exige recebido explícito — mude o status antes de limpar o valor' };
    return pfMutate('income_update', pf => { pfFindIncome(pf,monthKey,incomeId)[campo] = valor; return { recordId: incomeId }; });
  }
  return { ok:false, erro:'campo desconhecido' };
}

function pfActSetIncomeStatus(monthKey, incomeId, status){
  if(!['PROJETADA','RECEBIDA','CANCELADA'].includes(status)) return { ok:false, erro:'status desconhecido' };
  const alvo = pfFindIncome(S.personalFinance, monthKey, incomeId);
  if(!alvo) return { ok:false, erro:'receita inexistente' };
  // Guarda do congelamento: RECEBIDA exige receivedAmount explícito (0 vale).
  if(status==='RECEBIDA' && alvo.receivedAmount===null)
    return { ok:false, erro:'RECEBIDA exige o valor recebido explícito — informe 0 se nada entrou' };
  return pfMutate('income_status', pf => { pfFindIncome(pf,monthKey,incomeId).status = status; return { recordId: incomeId }; });
}

function pfActDeleteIncome(monthKey, incomeId){
  const alvo = pfFindIncome(S.personalFinance, monthKey, incomeId);
  if(!alvo) return { ok:false, erro:'receita inexistente' };
  return pfMutate('income_delete', pf => {
    const m = pf.months[monthKey];
    m.incomes = m.incomes.filter(i=>i.id!==incomeId);
    return { recordId: incomeId };
  });
}

// Editar um FANTASMA (projeção de regra em mês virtual) é um ato real: o mês
// materializa (estampando TODAS as regras vigentes) e a edição cai na estampa
// da própria regra.
function pfActEditGhost(monthKey, ruleId, campo, valor){
  if(!pfMonthKeyValid(monthKey)) return { ok:false, erro:'competência inválida' };
  if(pfIsMaterialized(monthKey)) return { ok:false, erro:'mês já registrado' };
  if((campo==='projectedAmount'||campo==='receivedAmount') && !pfAmountInDomain(valor,{allowNull:true}))
    return { ok:false, erro:'valor fora do domínio (≥ 0 ou vazio)' };
  return pfMutate('month_materialize_edit', pf => {
    const m = pfMaterializeMonth(pf, monthKey);
    const alvo = m.incomes.find(i=>i.ruleId===ruleId);
    if(!alvo) return { ok:false, erro:'projeção não encontrada na estampa' };
    if(campo==='name') alvo.name = String(valor||'').trim() || alvo.name;
    else alvo[campo] = valor;
    return { recordId: alvo.id };
  });
}

// ---- recorrência ------------------------------------------------------------
// Formulário ATÔMICO (modal): tudo validado, aplicado num ato só. Ligar cria a
// regra e vincula ruleId; desligar desativa a regra (active:false) e NUNCA
// apaga receitas históricas já estampadas. Editar regra vigente muda apenas
// meses ainda virtuais — por construção: regra só é lida por pfVirtualIncomes
// e pfMaterializeMonth.
function pfActConfigureRecurrence(monthKey, incomeId, cfg){
  const alvo = pfFindIncome(S.personalFinance, monthKey, incomeId);
  if(!alvo) return { ok:false, erro:'receita inexistente' };
  const ligar = !!(cfg && cfg.recorrente);
  if(!ligar){
    if(!alvo.ruleId) return { ok:true, persistido:true, recordId:incomeId }; // nada a fazer
    return pfMutate('recurrence_off', pf => {
      const r = pf.recurringIncome.find(x=>x.id===alvo.ruleId);
      if(r) r.active = false;
      return { recordId: alvo.ruleId };
    });
  }
  const amount = cfg.amount;
  if(!(typeof amount==='number' && Number.isSafeInteger(amount) && amount>=0))
    return { ok:false, erro:'regra recorrente exige valor (≥ 0) em centavos' };
  const inicio = cfg.startMonth;
  if(!pfMonthKeyValid(inicio)) return { ok:false, erro:'início da recorrência inválido (YYYY-MM)' };
  const fim = (cfg.endMonth===null || cfg.endMonth===undefined || cfg.endMonth==='') ? null : cfg.endMonth;
  if(fim!==null && (!pfMonthKeyValid(fim) || fim < inicio)) return { ok:false, erro:'fim da recorrência inválido (vazio ou ≥ início)' };
  return pfMutate('recurrence_on', pf => {
    const receita = pfFindIncome(pf, monthKey, incomeId);
    let r = receita.ruleId ? pf.recurringIncome.find(x=>x.id===receita.ruleId) : null;
    if(!r){
      r = { id: pfId('pfr'), name: receita.name, amount, periodicity:'MENSAL',
            startMonth: inicio, endMonth: fim, active: true };
      pf.recurringIncome.push(r);
      receita.ruleId = r.id;
    } else {
      r.name = receita.name; r.amount = amount; r.startMonth = inicio; r.endMonth = fim; r.active = true;
    }
    return { recordId: r.id };
  });
}

// ---- calculadores (derivados; consumidos pelo Resumo no Bloco D) ------------
function pfProjectedIncome(m){
  if(!m || !Array.isArray(m.incomes)) return 0;
  return m.incomes.reduce((acc,i)=> acc + ((i && i.status!=='CANCELADA' && typeof i.projectedAmount==='number') ? i.projectedAmount : 0), 0);
}
function pfKnownReceivedIncome(m){
  if(!m || !Array.isArray(m.incomes)) return 0;
  // TODO valor informado soma, INDEPENDENTE do status — dinheiro que entrou, entrou.
  return m.incomes.reduce((acc,i)=> acc + ((i && typeof i.receivedAmount==='number') ? i.receivedAmount : 0), 0);
}
function pfIncomeCoverage(m){
  const linhas = (m && Array.isArray(m.incomes)) ? m.incomes.filter(Boolean) : [];
  const conhecidas = linhas.filter(i=>i.receivedAmount!==null && i.receivedAmount!==undefined).length;
  return { conhecidas, total: linhas.length, completa: conhecidas===linhas.length };
}

// ============ PF-02 · BLOCO C — DESPESAS ====================================
// Meta ≠ Previsto ≠ Executado. O executado tem DOIS canais (fora do cartão e
// cartão) e o total é SEMPRE derivado — persistir executedTotal seria a
// segunda fonte de verdade que o contrato proíbe. Na V1 o canal cartão é
// informado manualmente; quando o subsistema de Cartão existir (PF-FUTURE),
// este campo torna-se derivado e o input congela.

function pfFindExpense(pf, monthKey, expenseId){
  const m = pf.months[monthKey];
  if(!m || !Array.isArray(m.expenses)) return null;
  return m.expenses.find(e=>e && e.id===expenseId) || null;
}

function pfActAddExpense(monthKey, dados){
  if(!pfMonthKeyValid(monthKey)) return { ok:false, erro:'competência inválida' };
  const nome = String((dados&&dados.name)||'').trim();
  if(!nome) return { ok:false, erro:'nome da despesa obrigatório' };
  return pfMutate('expense_add', pf => {
    const m = pfMaterializeMonth(pf, monthKey);
    const rec = { id: pfId('pfe'), name: nome, installments: null,
                  targetAmount: null, expectedAmount: null,
                  executedCash: null, executedCard: null, status:'PENDENTE' };
    m.expenses.push(rec);
    return { recordId: rec.id };
  });
}

const PF_EXPENSE_MONEY_FIELDS = ['targetAmount','expectedAmount','executedCash','executedCard'];
function pfActUpdateExpenseField(monthKey, expenseId, campo, valor){
  const alvo = pfFindExpense(S.personalFinance, monthKey, expenseId);
  if(!alvo) return { ok:false, erro:'despesa inexistente' };
  if(campo==='name'){
    const nome = String(valor||'').trim();
    if(!nome) return { ok:false, erro:'nome da despesa obrigatório' };
    return pfMutate('expense_update', pf => { pfFindExpense(pf,monthKey,expenseId).name = nome; return { recordId: expenseId }; });
  }
  if(PF_EXPENSE_MONEY_FIELDS.includes(campo)){
    if(!pfAmountInDomain(valor,{allowNull:true})) return { ok:false, erro:'valor fora do domínio (≥ 0 ou vazio)' };
    if((campo==='executedCash'||campo==='executedCard') && valor===null && alvo.status==='PAGO')
      return { ok:false, erro:'PAGO exige os dois canais explícitos — mude o status antes de limpar um canal' };
    return pfMutate('expense_update', pf => { pfFindExpense(pf,monthKey,expenseId)[campo] = valor; return { recordId: expenseId }; });
  }
  return { ok:false, erro:'campo desconhecido' };
}

function pfActSetExpenseStatus(monthKey, expenseId, status){
  if(!['PENDENTE','PAGO','CANCELADO'].includes(status)) return { ok:false, erro:'status desconhecido' };
  const alvo = pfFindExpense(S.personalFinance, monthKey, expenseId);
  if(!alvo) return { ok:false, erro:'despesa inexistente' };
  // Guarda do congelamento: PAGO exige os DOIS canais explícitos (0 vale em
  // qualquer um). Um canal desconhecido torna o total da linha indemonstrável.
  if(status==='PAGO' && (alvo.executedCash===null || alvo.executedCard===null))
    return { ok:false, erro:'PAGO exige executado explícito nos dois canais — informe 0 no canal que não foi usado' };
  return pfMutate('expense_status', pf => { pfFindExpense(pf,monthKey,expenseId).status = status; return { recordId: expenseId }; });
}

// Parcelamento: {total, paid} com 0 <= paid <= total e total >= 1; null limpa.
// `remaining` é DERIVADO — jamais persiste (o defeito da FALTA negativa da
// planilha nasceu exatamente de parcelas incoerentes persistidas).
function pfActSetExpenseInstallments(monthKey, expenseId, parc){
  const alvo = pfFindExpense(S.personalFinance, monthKey, expenseId);
  if(!alvo) return { ok:false, erro:'despesa inexistente' };
  if(parc!==null){
    const total = parc && parc.total, paid = parc && parc.paid;
    if(!(Number.isInteger(total) && total>=1)) return { ok:false, erro:'total de parcelas deve ser inteiro ≥ 1' };
    if(!(Number.isInteger(paid) && paid>=0)) return { ok:false, erro:'parcelas pagas deve ser inteiro ≥ 0' };
    if(paid>total) return { ok:false, erro:'parcelas pagas não podem exceder o total (paid ≤ total)' };
  }
  return pfMutate('expense_installments', pf => {
    pfFindExpense(pf,monthKey,expenseId).installments = parc===null ? null : { total: parc.total, paid: parc.paid };
    return { recordId: expenseId };
  });
}

function pfActDeleteExpense(monthKey, expenseId){
  const alvo = pfFindExpense(S.personalFinance, monthKey, expenseId);
  if(!alvo) return { ok:false, erro:'despesa inexistente' };
  return pfMutate('expense_delete', pf => {
    const m = pf.months[monthKey];
    m.expenses = m.expenses.filter(e=>e.id!==expenseId);
    return { recordId: expenseId };
  });
}

// ---- calculadores derivados -------------------------------------------------
function pfExpenseExecutedKnown(e){
  // total conhecido da LINHA: soma dos canais informados (para exibição e
  // agregados "conhecidos"); a COMPLETUDE exige os dois explícitos.
  const a = (typeof e.executedCash==='number') ? e.executedCash : 0;
  const b = (typeof e.executedCard==='number') ? e.executedCard : 0;
  return a + b;
}
function pfPlannedExpenses(m){
  if(!m || !Array.isArray(m.expenses)) return 0;
  return m.expenses.reduce((acc,e)=> acc + ((e && e.status!=='CANCELADO' && typeof e.expectedAmount==='number') ? e.expectedAmount : 0), 0);
}
function pfKnownExecutedExpenses(m){
  if(!m || !Array.isArray(m.expenses)) return 0;
  // TODO executado informado soma, INDEPENDENTE do status — dinheiro gasto, gasto.
  return m.expenses.reduce((acc,e)=> acc + (e ? pfExpenseExecutedKnown(e) : 0), 0);
}
function pfExpenseCoverage(m){
  const linhas = (m && Array.isArray(m.expenses)) ? m.expenses.filter(Boolean) : [];
  const conhecidas = linhas.filter(e=>e.executedCash!==null && e.executedCash!==undefined
                                   && e.executedCard!==null && e.executedCard!==undefined).length;
  return { conhecidas, total: linhas.length, completa: conhecidas===linhas.length };
}

// ============ PF-02 · BLOCO D — RESUMO DO MÊS ===============================
// Consolidador derivado. A lei central: SOMA PARCIAL NUNCA SE APRESENTA COMO
// TOTAL. realizedSurplus e incomeExpenseRatio SÓ existem com cobertura
// completa dos dois lados; o que existe antes disso é "saldo conhecido",
// rotulado como tal. Nada daqui persiste.
function pfMonthSummary(m){
  const projectedIncome      = pfProjectedIncome(m);
  const plannedExpenses      = pfPlannedExpenses(m);
  const knownReceivedIncome  = pfKnownReceivedIncome(m);
  const knownExecutedExpenses= pfKnownExecutedExpenses(m);
  const incomeCoverage       = pfIncomeCoverage(m);
  const expenseCoverage      = pfExpenseCoverage(m);
  const completo             = incomeCoverage.completa && expenseCoverage.completa;
  const realizedSurplus      = completo ? (knownReceivedIncome - knownExecutedExpenses) : null;
  // ratio = executado/recebido: exige completude E receita > 0 (jamais dividir
  // por zero; receita zero completa é "N/A", não infinito nem 0 fictício).
  const incomeExpenseRatio   = (completo && knownReceivedIncome>0)
    ? (knownExecutedExpenses / knownReceivedIncome) : null;
  return {
    projectedIncome, plannedExpenses,
    projectedSurplus: projectedIncome - plannedExpenses,
    knownReceivedIncome, knownExecutedExpenses,
    knownBalance: knownReceivedIncome - knownExecutedExpenses, // auxiliar; NUNCA rotular como sobra
    incomeCoverage, expenseCoverage, completo,
    realizedSurplus, incomeExpenseRatio,
  };
}

// ============ PF-02 · BLOCO E — DESTINO DO EXCEDENTE ========================
// A sobra é insumo: pode ser destinada. allocation.amount é OBRIGATÓRIO e ≥ 0
// (linha sem valor não se cria — não existe destinação "não informada").
// Sem inventoryAssetRef: adiado para PF-08 por decisão do congelamento.

function pfFindAllocation(pf, monthKey, allocId){
  const m = pf.months[monthKey];
  if(!m || !Array.isArray(m.allocations)) return null;
  return m.allocations.find(a=>a && a.id===allocId) || null;
}
function pfActAddAllocation(monthKey, dados){
  if(!pfMonthKeyValid(monthKey)) return { ok:false, erro:'competência inválida' };
  const label = String((dados&&dados.label)||'').trim();
  if(!label) return { ok:false, erro:'destino obrigatório' };
  const amount = dados && dados.amount;
  if(!(typeof amount==='number' && Number.isSafeInteger(amount) && amount>=0))
    return { ok:false, erro:'destinação exige valor ≥ 0 — linha sem valor não se cria' };
  return pfMutate('allocation_add', pf => {
    const m = pfMaterializeMonth(pf, monthKey);
    const rec = { id: pfId('pfa'), label, amount };
    m.allocations.push(rec);
    return { recordId: rec.id };
  });
}
function pfActUpdateAllocationField(monthKey, allocId, campo, valor){
  const alvo = pfFindAllocation(S.personalFinance, monthKey, allocId);
  if(!alvo) return { ok:false, erro:'destinação inexistente' };
  if(campo==='label'){
    const label = String(valor||'').trim();
    if(!label) return { ok:false, erro:'destino obrigatório' };
    return pfMutate('allocation_update', pf => { pfFindAllocation(pf,monthKey,allocId).label = label; return { recordId: allocId }; });
  }
  if(campo==='amount'){
    if(!(typeof valor==='number' && Number.isSafeInteger(valor) && valor>=0))
      return { ok:false, erro:'destinação exige valor ≥ 0 (vazio não vale)' };
    return pfMutate('allocation_update', pf => { pfFindAllocation(pf,monthKey,allocId).amount = valor; return { recordId: allocId }; });
  }
  return { ok:false, erro:'campo desconhecido' };
}
function pfActDeleteAllocation(monthKey, allocId){
  const alvo = pfFindAllocation(S.personalFinance, monthKey, allocId);
  if(!alvo) return { ok:false, erro:'destinação inexistente' };
  return pfMutate('allocation_delete', pf => {
    const m = pf.months[monthKey];
    m.allocations = m.allocations.filter(a=>a.id!==allocId);
    return { recordId: allocId };
  });
}
function pfTotalAllocated(m){
  if(!m || !Array.isArray(m.allocations)) return 0;
  return m.allocations.reduce((acc,a)=> acc + ((a && typeof a.amount==='number') ? a.amount : 0), 0);
}
// unallocatedSurplus SÓ existe quando realizedSurplus existe. Com realizado
// incompleto, destinar continua permitido — mas nenhum "saldo restante
// realizado" é fabricado. Excedente negativo é legítimo (dinheiro de saldo
// anterior): alerta, jamais clamp ou bloqueio.
function pfUnallocatedSurplus(m){
  const r = pfMonthSummary(m);
  if(r.realizedSurplus===null) return null;
  return r.realizedSurplus - pfTotalAllocated(m);
}

// ============ PF-02 · BLOCO F — INFORMAÇÕES IMPORTANTES =====================
// Texto + status, nada mais: sem prioridade, tags, responsável, workflow ou
// automação — por decisão expressa do contrato.
function pfFindNote(pf, monthKey, noteId){
  const m = pf.months[monthKey];
  if(!m || !Array.isArray(m.notes)) return null;
  return m.notes.find(n=>n && n.id===noteId) || null;
}
function pfActAddNote(monthKey, texto){
  if(!pfMonthKeyValid(monthKey)) return { ok:false, erro:'competência inválida' };
  const text = String(texto||'').trim();
  if(!text) return { ok:false, erro:'texto obrigatório' };
  return pfMutate('note_add', pf => {
    const m = pfMaterializeMonth(pf, monthKey);
    const rec = { id: pfId('pfn'), text, status:'PENDENTE', createdAt: new Date().toISOString() };
    m.notes.push(rec);
    return { recordId: rec.id };
  });
}
function pfActToggleNoteStatus(monthKey, noteId){
  const alvo = pfFindNote(S.personalFinance, monthKey, noteId);
  if(!alvo) return { ok:false, erro:'nota inexistente' };
  return pfMutate('note_status', pf => {
    const n = pfFindNote(pf, monthKey, noteId);
    n.status = (n.status==='PENDENTE') ? 'RESOLVIDO' : 'PENDENTE';
    return { recordId: noteId };
  });
}
function pfActDeleteNote(monthKey, noteId){
  const alvo = pfFindNote(S.personalFinance, monthKey, noteId);
  if(!alvo) return { ok:false, erro:'nota inexistente' };
  return pfMutate('note_delete', pf => {
    const m = pf.months[monthKey];
    m.notes = m.notes.filter(n=>n.id!==noteId);
    return { recordId: noteId };
  });
}
