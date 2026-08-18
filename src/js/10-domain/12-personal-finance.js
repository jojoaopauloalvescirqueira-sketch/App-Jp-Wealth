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
