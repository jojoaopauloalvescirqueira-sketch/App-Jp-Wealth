// ============ ALLADIN · ALD-01 C1 — FOUNDATION INFRASTRUCTURE ===============
// Sistema Patrimonial e Consolidador de Investimentos do JP Wealth.
// Contrato: JPW-ALLADIN-SPEC V1.2.1 + ALD-01 Proposal Rev.2 (aprovado 2026-08-20).
//
// Este arquivo é INFRAESTRUTURA do domínio, não o domínio completo: dinheiro,
// moedas, identidade, write gate e validações base. Entidades cadastrais
// (Instrument, Asset, Account, CashAccount) chegam no C2; UI no C3. Nenhum
// ato econômico, nenhum cálculo patrimonial, nenhuma integração com Trading,
// Finanças Pessoais ou Planejamento FX (fronteiras HD-1/HD-2/HD-3 pendentes).
//
// DOM-free por contrato (HD-5): este módulo não toca document/window além da
// superfície declarada ao final, e todos os efeitos (S, save, dgLogChange)
// são globais injetáveis — o harness unitário roda este arquivo sozinho em
// página em branco com stubs.

// ---- versão suportada -------------------------------------------------------
// Deliberadamente DUPLICADA de ALLADIN_SCHEMA_VERSION (00-core/04-persistence.js),
// como PF_MONTH_RE duplica o FX: o módulo de domínio precisa funcionar isolado
// no harness unitário. As duas constantes DEVEM permanecer iguais — o teste de
// integração prova o comportamento conjunto (fail-closed).
const ALD_SUPPORTED_SCHEMA_VERSION = 1;

// ---- moedas: schema extensível ≠ runtime universal --------------------------
// O SCHEMA aceita qualquer código ISO 4217 (nenhuma lista de moedas é contrato
// estrutural — adicionar moeda futura jamais exige migration). O que é limitado
// é o SUPORTE DE RUNTIME: parse/format/interpretação do expoente da unidade
// mínima. Estender = adicionar entrada aqui (mudança de dado/configuração).
// Moeda fora do suporte deixa o registro VÁLIDO e intacto; apenas ilegível
// ("—") até o suporte chegar — nunca reinterpretada (padrão da sentinela de
// unidade do PF, generalizado).
const ALD_RUNTIME_CURRENCIES = {
  BRL: { exp: 2, symbol: 'R$' },
  USD: { exp: 2, symbol: 'US$' },
};
function aldCurrencySupported(code){
  return typeof code==='string' && Object.prototype.hasOwnProperty.call(ALD_RUNTIME_CURRENCIES, code);
}

// ---- identidade permanente --------------------------------------------------
// Mesmo padrão canônico de pfId/dgId/operationRecordId — replicação por módulo
// É o padrão do projeto. Prefixos do domínio: aldi_ (instrument), alda_ (asset),
// aldacc_ (account), aldc_ (cash account) — catálogo fixado no Proposal §3.
// ID é canônico, imutável e sem semântica (ALD-I09/I10: ticker e provider-id
// jamais são chave).
function aldId(prefix){
  return String(prefix||'ald')+'_'+Date.now().toString(36)+'_'+Math.random().toString(36).slice(2,8);
}

// ---- aldParseMoney: string → {amount,currency}, SEM float no caminho -------
// Generalização de parseBRLCents (10-domain/12-personal-finance.js) para o
// expoente da moeda: dígitos extraídos por forma reconhecida (convenção pt-BR),
// valor montado por aritmética inteira. Para exp=2 aceita exatamente as mesmas
// formas do PF ("1420", "1420,50", "1.420,50", "1.420", "1420.50").
// Vazio → null ("não informado" é estado real, não erro).
// Moeda sem suporte de runtime → NaN sentinelado: sem o expoente não há como
// interpretar os dígitos — inventar interpretação seria pior que recusar.
// Sinal negativo reconhecido sintaticamente; a guarda semântica dos atos (C2)
// decide onde ≥ 0 é contrato.
function aldParseMoney(txt, currency){
  if(!aldCurrencySupported(currency)) return NaN;
  const exp = ALD_RUNTIME_CURRENCIES[currency].exp;
  const t = String(txt==null?'':txt).trim();
  if(!t) return null;
  let s=t, neg=false;
  if(s[0]==='-' || s[0]==='−'){ neg=true; s=s.slice(1); }
  let m, intDigits, decDigits;
  const dec = '(\\d{1,'+exp+'})';
  if((m=new RegExp('^(\\d{1,3}(?:\\.\\d{3})+),'+dec+'$').exec(s))){ intDigits=m[1].replace(/\./g,''); decDigits=m[2]; }
  else if((m=/^(\d{1,3}(?:\.\d{3})+)$/.exec(s)))                  { intDigits=m[1].replace(/\./g,''); decDigits=''; }
  else if((m=new RegExp('^(\\d+)[.,]'+dec+'$').exec(s)))          { intDigits=m[1]; decDigits=m[2]; }
  else if((m=/^(\d+)$/.exec(s)))                                  { intDigits=m[1]; decDigits=''; }
  else return NaN;
  if(intDigits.length>13) return NaN; // overflow além do inteiro seguro na unidade mínima
  const minor = Number(intDigits)*Math.pow(10,exp) + Number((decDigits+'0'.repeat(exp)).slice(0,exp)||'0');
  if(!Number.isSafeInteger(minor)) return NaN;
  // "-0" normaliza para 0: zero não tem sinal no domínio (Object.is(-0,0) é
  // false e JSON serializa -0 como 0 — identidade dupla seria bug latente).
  return { amount: (neg && minor!==0) ? -minor : minor, currency };
}

// ---- aldFormatMoney: {amount,currency} → texto, por aritmética de STRING ---
// Sem divisão em float: o inteiro é fatiado em texto (padrão formatBRLCents).
// null/undefined → '—'. Forma inválida, amount não-inteiro-seguro ou moeda fora
// do suporte de runtime → '—': este formatador não legitima o que o domínio não
// interpreta (sentinela de leitura, ALD-I30 por analogia).
function aldFormatMoney(money){
  if(money===null || money===undefined) return '—';
  if(typeof money!=='object' || Array.isArray(money)) return '—';
  const { amount, currency } = money;
  if(!aldCurrencySupported(currency)) return '—';
  if(typeof amount!=='number' || !Number.isSafeInteger(amount)) return '—';
  const { exp, symbol } = ALD_RUNTIME_CURRENCIES[currency];
  const neg = amount<0;
  const s = String(Math.abs(amount)).padStart(exp+1,'0');
  const inteiro = (exp>0 ? s.slice(0,-exp) : s).replace(/\B(?=(\d{3})+(?!\d))/g,'.');
  const frac = exp>0 ? ','+s.slice(-exp) : '';
  return (neg?'-':'')+symbol+' '+inteiro+frac;
}

// ---- validações base (forma, não semântica econômica) ----------------------
function aldMoneyInDomain(money, opts){
  const allowNull = !!(opts && opts.allowNull);
  if(money===null || money===undefined) return allowNull;
  if(typeof money!=='object' || Array.isArray(money)) return false;
  if(typeof money.currency!=='string' || !money.currency) return false; // ALD-I16: não existe amount sem currency
  if(typeof money.amount!=='number' || !Number.isSafeInteger(money.amount)) return false;
  if(opts && opts.nonNegative && money.amount<0) return false;
  return true;
}
// Proporções em pontos-base: inteiro 0..10000 (5000 = 50%). Nunca float.
function aldBpInDomain(bp){
  return typeof bp==='number' && Number.isSafeInteger(bp) && bp>=0 && bp<=10000;
}
// Texto de cadastro: string não vazia após trim, teto de tamanho (default 120,
// mesmo teto de títulos do mvpNotes). Validação de FORMA — starter values e
// classificações extensíveis (Proposal §4.2) aceitam valor novo que passe aqui.
function aldTextInDomain(txt, opts){
  const max = (opts && opts.max) || 120;
  return typeof txt==='string' && txt.trim().length>0 && txt.length<=max;
}

// ---- fail-closed / compatibilidade -----------------------------------------
// Espelho de leitura do fail-closed da migração (alladinNormalizeState):
// versão futura ⇒ domínio inteiro somente-leitura. O bloqueio é do módulo,
// nunca do JP Wealth inteiro.
const ALD_READ_ONLY_FUTURE_SCHEMA = 'READ_ONLY_FUTURE_SCHEMA';
// Versão LEGÍVEL = inteiro OU string só de dígitos (a forma mais provável num
// backup editado à mão). Demais formas (float, Infinity, lixo) são envelope
// corrompido de versão desconhecida — coerção documentada, não futuro.
// DEVE espelhar aldSchemaVersionLegivel de 00-core/04-persistence.js.
function aldSchemaVersionLegivel(v){
  if(Number.isInteger(v)) return v;
  if(typeof v==='string' && /^[0-9]+$/.test(v.trim())) return parseInt(v.trim(),10);
  return null;
}
function aldCompat(){
  const a = (typeof S==='object' && S) ? S.alladin : null;
  const stored = (a && typeof a==='object') ? aldSchemaVersionLegivel(a.schemaVersion) : null;
  const readOnly = stored!==null && stored>ALD_SUPPORTED_SCHEMA_VERSION;
  return {
    supportedSchemaVersion: ALD_SUPPORTED_SCHEMA_VERSION,
    storedSchemaVersion: stored,
    readOnly,
    reason: readOnly ? ALD_READ_ONLY_FUTURE_SCHEMA : null,
  };
}
function aldWriteBlockReason(){
  return aldCompat().reason;
}

// ---- write gate canônico ----------------------------------------------------
// TODO ato mutável do Alladin passa por aqui (invariante herdado do pfMutate,
// 12-personal-finance.js:120). fn recebe S.alladin e aplica o ato COERENTE;
// pode devolver {ok:false, erro} para recusar por validação — nesse caso NADA
// foi mutado por contrato do chamador. save()===false é prova de não-escrita.
//
// HD-6 (decisão humana de 2026-08-20): dgLogChange é LOG OPERACIONAL
// NÃO-CANÔNICO — não é o Audit Trail do Alladin e NÃO satisfaz ALD-I26
// (deferred to ALD-07). Rótulo genérico por contrato de privacidade: ação +
// recordId, nunca nome ou valor — o changeLog persiste e viaja no backup.
function aldMutate(acao, fn, meta){
  const bloqueio = aldWriteBlockReason();
  if(bloqueio) return { ok:false, persistido:false, erro:bloqueio };
  const r = fn(S.alladin) || {};
  if(r.ok===false) return { ok:false, persistido:false, erro:r.erro||'ato recusado' };
  dgLogChange('alladin', String(acao||'ato'), String(r.recordId||''), String((meta&&meta.label)||acao||''));
  const gravou = save();
  // Extras de fn ANTES, veredito DEPOIS: fn jamais sobrescreve ok/persistido/erro.
  // (Correção da auditoria C1 sobre o precedente pfMutate, onde o spread final
  // permitia a um fn {ok:true} mascarar save()===false como sucesso.)
  return { ...r, ok: gravou===true, persistido: gravou===true, erro: gravou===true?undefined:'persistencia recusada' };
}

// ---- superfície pública -----------------------------------------------------
// Leitura e utilitários apenas — não é UI (HD-7: UI só no C3). aldCompat() é a
// exposição explícita do estado de incompatibilidade exigida pelo fail-closed;
// o aviso visual chega com a UI do C3.
if(typeof window!=='undefined'){
  window.JPWAlladin = {
    compat: aldCompat,
    writeBlockReason: aldWriteBlockReason,
    money: {
      parse: aldParseMoney,
      format: aldFormatMoney,
      supported: aldCurrencySupported,
      runtimeCurrencies: function(){ return Object.keys(ALD_RUNTIME_CURRENCIES); },
    },
    id: aldId,
  };
}
