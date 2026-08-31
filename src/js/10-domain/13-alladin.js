// ============ ALLADIN · ALD-01 C1 — FOUNDATION INFRASTRUCTURE ===============
// Sistema Patrimonial e Consolidador de Investimentos do JP Wealth.
// Contrato: JPW-ALLADIN-SPEC V1.2.1 + ALD-01 Proposal Rev.2 (aprovado 2026-08-20).
//
// Camadas deste módulo:
//   C1 — INFRAESTRUTURA: dinheiro, moedas, identidade, write gate, validações
//        base, fail-closed de schema.
//   C2 — MODELO CADASTRAL: Instrument, Asset, Account, CashAccount — identidade
//        e ciclo cadastral. UI cadastral no C3.
//   ALD-03 — LEDGER ECONÔMICO: DEPOSIT/WITHDRAWAL/TRANSFER (S1) e BUY/SELL
//        (S2), com REVERSAL e saldo de caixa derivado fail-closed.
//   ALD-04 S1 — POSITION QUANTITY ENGINE: posição por quantidade DERIVADA do
//        ledger (nunca persistida), aritmética decimal exata em BigInt.
// AINDA NÃO EXISTEM: cost basis, valuation, preço, patrimônio monetário, P&L,
// performance, benchmark; nenhuma integração com Trading, Finanças Pessoais ou
// Planejamento FX (fronteiras HD-1/HD-2/HD-3 pendentes de decisão humana).
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
const ALD_SUPPORTED_SCHEMA_VERSION = 4;

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
  // SNAPSHOT antes de fn (correção da auditoria C2). Sem ele, `persistido:false`
  // conviveria com o registro VIVO em memória: em modo de recuperação A-005, sob
  // quota estourada ou com o portão de persistência fechado, save() devolve
  // false — e o próximo save() de QUALQUER origem gravaria o registro fantasma
  // que o sistema declarou não ter criado. O snapshot é a serialização do
  // agregado, que é exatamente o que seria persistido.
  const snapshot = JSON.stringify(S.alladin);
  // SEQUENCIA anterior, nao comprimento (ALD-03-H0 · D-1): dgLogChange REATRIBUI
  // o array ao podar no teto DG_CHANGELOG_MAX, e nesse caso 401→slice→400 devolve
  // o mesmo comprimento de antes. Restaurar por comprimento seria, exatamente no
  // teto, uma restauracao que nao restaura: a entrada do ato recusado sobreviveria
  // e a mais antiga legitima seria evicta. Um ledger vive NO teto — la o ramo
  // defeituoso seria o unico.
  const logAntes = (S.dataGovernance && Array.isArray(S.dataGovernance.changeLog)) ? S.dataGovernance.changeLog.slice() : null;
  const r = fn(S.alladin) || {};
  if(r.ok===false){
    // Recusa por validação: por contrato fn não mutou. Restaurar aqui é cinto
    // de segurança — não licença para fn sujar o agregado.
    if(JSON.stringify(S.alladin)!==snapshot) S.alladin = JSON.parse(snapshot);
    return { ok:false, persistido:false, erro:r.erro||'ato recusado' };
  }
  dgLogChange('alladin', String(acao||'ato'), String(r.recordId||''), String((meta&&meta.label)||acao||''));
  const gravou = save();
  if(gravou!==true){
    S.alladin = JSON.parse(snapshot);
    if(logAntes!==null){
      // Restauracao IN-PLACE: preserva a identidade do array, que a poda troca.
      const log = S.dataGovernance.changeLog;
      if(Array.isArray(log)){ log.length = 0; for(const e of logAntes) log.push(e); }
      else S.dataGovernance.changeLog = logAntes;
    }
    return { ...r, ok:false, persistido:false, erro:'persistencia recusada' };
  }
  // Extras de fn ANTES, veredito DEPOIS: fn jamais sobrescreve ok/persistido/erro.
  return { ...r, ok:true, persistido:true, erro:undefined };
}

// ============ ALLADIN · ALD-02 C2 — MODELO CADASTRAL =========================
// Identidade das quatro entidades sobre a infraestrutura do C1. NENHUM fato
// econômico: sem transação, sem valuation, sem preço, sem posição, sem custo.
// Contrato: ALD-02 Change Proposal Rev.2 (decisões DC-1..DC-6, OP-1..OP-4).
//
// TRÊS REGIMES DE CLASSIFICAÇÃO, deliberados (OP-2):
//   FECHADO — mandato normativo ou função estrutural; valor fora RECUSA o ato.
//   STARTER — valores canônicos SEMEADOS e oferecidos; valor novo é ACEITO com
//             validação de forma. Starter NÃO é enum: taxonomia patrimonial é
//             evolutiva, e fechá-la por inferência seria decisão que a spec não
//             tomou.
//   LIVRE   — texto do operador (category, subcategory, strategicGroup, tags).

const ALD_INSTRUMENT_FAMILIES = ['EQUITY_LIKE','FUND_LIKE','FIXED_INCOME','CRYPTO','COMMODITY','CASH','DERIVATIVE','ALTERNATIVE']; // FECHADO (spec §39; sem PHYSICAL_ASSET)
const ALD_RECORD_MODES        = ['INDIVIDUAL','GROUPED'];  // FECHADO (spec §14)
const ALD_RECORD_STATUS       = ['ACTIVE','INACTIVE'];     // FECHADO (eixo técnico/cadastral)
const ALD_LIFECYCLE_STATUS    = ['ACTIVE','SOLD','DISPOSED','DONATED','LOST','WRITTEN_OFF']; // FECHADO (spec §10.8)

// STARTER — sementes, não fronteiras.
const ALD_STARTER_ACCOUNT_TYPES = ['BANK','BROKERAGE','EXCHANGE','WALLET','COLD_WALLET','OTHER'];
// DC-3: NENHUM valor de nature representa caixa. Dinheiro líquido é sempre
// Account+CashAccount, inclusive espécie — Carteira e Cofre nascem como Account
// 'OTHER'. Numerário de coleção (moeda rara) é COLECAO: é bem, não caixa.
// Duas representações do mesmo real seriam duplicação semântica antes de ser
// duplicação de valor.
const ALD_STARTER_NATURES       = ['BEM_PESSOAL','BEM_DURAVEL','BEM_PRODUTIVO','IMOVEL','DIREITO','COLECAO','OUTRO'];
// DC-3 como INVARIANTE, não como convenção de catálogo (achado da auditoria C2):
// o regime STARTER aceita valor novo, então sem esta guarda o operador digitaria
// nature:'CAIXA_FISICO' e criaria a segunda representação do mesmo real. Custo
// aceito: uma natureza legítima que contenha a palavra (ex.: "caixa de
// ferramentas") precisa de outro nome. `assetClass:'CAIXA'` continua legítimo —
// é classe de INSTRUMENTO financeiro (equivalente de caixa), outro eixo.
const ALD_NATURE_DE_CAIXA_RE = /(caixa|cash|dinheiro|esp[eé]cie|numer[aá]rio)/i;
const ALD_STARTER_PURPOSES      = ['AUTOIMAGEM','MORADIA','PRODUTIVIDADE','TRABALHO','CAPITAL_INTELECTUAL','INVESTIMENTO','RESERVA','MOBILIDADE','COLECAO','LAZER','OUTRO'];
const ALD_STARTER_ASSET_CLASSES = ['RENDA_VARIAVEL','IMOBILIARIO_FINANCEIRO','RENDA_FIXA','FUNDO','CRIPTO','COMMODITY','CAIXA','ALTERNATIVO'];

const ALD_CURRENCY_RE = /^[A-Z]{3}$/; // forma ISO 4217 — schema aberto (o runtime é que é limitado)
const ALD_DATE_RE     = /^\d{4}-\d{2}-\d{2}$/;

const ALD_COLECOES = {
  instrument:  { colecao:'instruments',  campoId:'instrumentId'  },
  asset:       { colecao:'assets',       campoId:'assetId'       },
  account:     { colecao:'accounts',     campoId:'accountId'     },
  cashaccount: { colecao:'cashAccounts', campoId:'cashAccountId' },
};

function aldNowISO(){ return new Date().toISOString(); }
// Campos que a edição NÃO altera. Recusar é melhor que descartar em silêncio: o
// chamador que tenta trocar identidade ou carimbo precisa saber que não trocou
// (achado da auditoria C2 — política era inconsistente entre os atos).
function aldCamposProtegidosViolados(mudancas, lista){
  const m = mudancas || {}, achados=[];
  for(const k of lista){ if(Object.prototype.hasOwnProperty.call(m,k)) achados.push(k); }
  return achados;
}
function aldInEnum(v, lista){ return typeof v==='string' && lista.indexOf(v)>=0; }
function aldRegistroLegivel(r){ return !!r && typeof r==='object' && !Array.isArray(r); }
function aldFindIn(a, colecao, campoId, id){
  const lista = (a && Array.isArray(a[colecao])) ? a[colecao] : [];
  for(const r of lista){ if(aldRegistroLegivel(r) && r[campoId]===id) return r; }
  return null;
}
// Campo opcional de texto: '' , null e undefined significam "não informado"
// (null canônico); qualquer outro valor precisa passar na validação de forma.
function aldOptionalText(v, max){
  if(v===null || v===undefined || v==='') return { ok:true, valor:null };
  if(!aldTextInDomain(v, {max:max||120})) return { ok:false };
  return { ok:true, valor:String(v) };
}
function aldValidateTags(tags){
  if(tags===null || tags===undefined) return { ok:true, valor:[] };
  if(!Array.isArray(tags)) return { ok:false };
  const out=[];
  for(const t of tags){ if(!aldTextInDomain(t,{max:40})) return { ok:false }; out.push(String(t)); }
  return { ok:true, valor:out };
}
function aldValidateExternalIds(ext){
  if(ext===null || ext===undefined) return { ok:true, valor:{} };
  if(typeof ext!=='object' || Array.isArray(ext)) return { ok:false };
  const out={};
  for(const k of Object.keys(ext)){
    if(!aldTextInDomain(k,{max:40})) return { ok:false };
    // Chave reservada seria aceita e depois PERDIDA em silêncio (o setter de
    // Object.prototype ignora atribuição de string) — recusar é honesto.
    if(k==='__proto__' || k==='constructor' || k==='prototype') return { ok:false };
    if(!aldTextInDomain(ext[k],{max:120})) return { ok:false };
    out[k]=String(ext[k]);
  }
  return { ok:true, valor:out };
}

// ---- owners[] com isSelf (DC-2 + OP-1) --------------------------------------
// A spec define Ownership Share como "percentual econômico pertencente ao
// USUÁRIO" (§10.2). Numa lista de nomes é preciso saber qual entrada é o
// operador — sem isso, nenhum valor proporcional é computável sem inferência.
// Decisão humana de 2026-08-20: marcador isSelf, no máximo um.
//   soma > 10000  ⇒ RECUSA (economicamente impossível)
//   soma < 10000  ⇒ legítimo COM AVISO (parcela não atribuída) — jamais
//                   normalizar em silêncio: fabricar dado é proibido
//   lista vazia   ⇒ legítima ("não informado" ≠ zero)
function aldValidateOwners(owners){
  if(owners===null || owners===undefined) return { ok:true, valor:[], avisos:[] };
  if(!Array.isArray(owners)) return { ok:false, erro:'ALD_OWNERS_NAO_E_LISTA' };
  const avisos=[], vistos=new Set(), limpos=[];
  let soma=0, selfs=0;
  for(const o of owners){
    if(!aldRegistroLegivel(o)) return { ok:false, erro:'ALD_OWNER_INVALIDO' };
    if(!aldTextInDomain(o.name)) return { ok:false, erro:'ALD_OWNER_NOME_INVALIDO' };
    if(!aldBpInDomain(o.shareBp)) return { ok:false, erro:'ALD_OWNER_SHAREBP_INVALIDO' };
    soma += o.shareBp;
    // isSelf é booleano estrito: `1`/'sim'/'true' seriam descartados em
    // silêncio, e o operador acreditaria ter marcado a si mesmo (auditoria C2).
    if('isSelf' in o && o.isSelf!==true && o.isSelf!==false) return { ok:false, erro:'ALD_ISSELF_NAO_BOOLEANO' };
    const rec = { name:String(o.name), shareBp:o.shareBp };
    if(o.isSelf===true){ selfs++; rec.isSelf=true; }
    const chave = rec.name.trim().toLowerCase();
    if(vistos.has(chave)) avisos.push('OWNER_NOME_DUPLICADO'); else vistos.add(chave);
    limpos.push(rec);
  }
  // Dois "eu" é impossível, não é ambiguidade tolerável: RECUSA, não aviso.
  if(selfs>1) return { ok:false, erro:'ALD_MULTIPLOS_ISSELF' };
  if(soma>10000) return { ok:false, erro:'ALD_OWNERSHIP_ACIMA_DE_100' };
  if(limpos.length && soma<10000) avisos.push('OWNERSHIP_PARCIAL_NAO_ATRIBUIDA');
  return { ok:true, valor:limpos, avisos };
}

// ---- normalizadores de campo (validam ANTES de qualquer mutação) ------------
// Contrato de falha parcial: nenhum ato toca o agregado antes de a validação
// inteira passar. Ato recusado deixa S.alladin byte-idêntico.
function aldNormalizeInstrumentFields(d){
  d = d || {};
  if(!aldTextInDomain(d.name)) return { ok:false, erro:'ALD_NOME_INVALIDO' };
  if(!aldTextInDomain(d.symbol,{max:32})) return { ok:false, erro:'ALD_SYMBOL_INVALIDO' };
  if(typeof d.currency!=='string' || !ALD_CURRENCY_RE.test(d.currency)) return { ok:false, erro:'ALD_CURRENCY_INVALIDA' };
  if(!aldInEnum(d.instrumentFamily, ALD_INSTRUMENT_FAMILIES)) return { ok:false, erro:'ALD_INSTRUMENT_FAMILY_INVALIDA' };
  if(!aldTextInDomain(d.assetClass,{max:40})) return { ok:false, erro:'ALD_ASSET_CLASS_INVALIDA' }; // STARTER: só forma
  const ex = aldOptionalText(d.exchange,40); if(!ex.ok) return { ok:false, erro:'ALD_EXCHANGE_INVALIDA' };
  const co = aldOptionalText(d.country,40);  if(!co.ok) return { ok:false, erro:'ALD_COUNTRY_INVALIDO' };
  const ids = aldValidateExternalIds(d.externalIdentifiers); if(!ids.ok) return { ok:false, erro:'ALD_EXTERNAL_IDENTIFIERS_INVALIDOS' };
  // DC-4: cripto exige network — o mesmo symbol em redes distintas é OUTRO ativo
  // (USDT Ethereum ≠ USDT Tron). Aqui é RECUSA, não aviso: sem a rede a
  // identidade não fecha.
  if(d.instrumentFamily==='CRYPTO' && !aldTextInDomain(ids.valor.network,{max:40})) return { ok:false, erro:'ALD_CRYPTO_SEM_NETWORK' };
  const avisos = aldCurrencySupported(d.currency) ? [] : ['MOEDA_FORA_DO_SUPORTE_DE_RUNTIME'];
  return { ok:true, avisos, valor:{
    name:String(d.name), symbol:String(d.symbol),
    exchange:ex.valor, country:co.valor, currency:d.currency,
    assetClass:String(d.assetClass), instrumentFamily:d.instrumentFamily,
    externalIdentifiers:ids.valor,
  }};
}
function aldNormalizeAssetFields(d){
  d = d || {};
  if(!aldTextInDomain(d.name)) return { ok:false, erro:'ALD_NOME_INVALIDO' };
  if(!aldTextInDomain(d.nature,{max:40})) return { ok:false, erro:'ALD_NATURE_INVALIDA' }; // STARTER: só forma
  if(ALD_NATURE_DE_CAIXA_RE.test(d.nature)) return { ok:false, erro:'ALD_NATURE_DE_CAIXA_PROIBIDA' }; // DC-3
  if(!aldInEnum(d.recordMode, ALD_RECORD_MODES)) return { ok:false, erro:'ALD_RECORD_MODE_INVALIDO' };
  const cat=aldOptionalText(d.category,80), sub=aldOptionalText(d.subcategory,80),
        pur=aldOptionalText(d.strategicPurpose,40), grp=aldOptionalText(d.strategicGroup,80),
        loc=aldOptionalText(d.location,120);
  if(!cat.ok||!sub.ok||!pur.ok||!grp.ok||!loc.ok) return { ok:false, erro:'ALD_CAMPO_TEXTO_INVALIDO' };
  const tags = aldValidateTags(d.tags); if(!tags.ok) return { ok:false, erro:'ALD_TAGS_INVALIDAS' };
  const own  = aldValidateOwners(d.owners); if(!own.ok) return { ok:false, erro:own.erro };
  const aq = d.acquisitionDate;
  const aqOk = (aq===null || aq===undefined || aq==='') || (typeof aq==='string' && ALD_DATE_RE.test(aq));
  if(!aqOk) return { ok:false, erro:'ALD_ACQUISITION_DATE_INVALIDA' };
  return { ok:true, avisos:own.avisos, valor:{
    name:String(d.name), nature:String(d.nature),
    category:cat.valor, subcategory:sub.valor,
    strategicPurpose:pur.valor, strategicGroup:grp.valor, tags:tags.valor,
    recordMode:d.recordMode, owners:own.valor, location:loc.valor,
    acquisitionDate:(aq===null||aq===undefined||aq==='')?null:aq,
  }};
}
function aldNormalizeAccountFields(d){
  d = d || {};
  if(!aldTextInDomain(d.name)) return { ok:false, erro:'ALD_NOME_INVALIDO' };
  if(!aldTextInDomain(d.institution)) return { ok:false, erro:'ALD_INSTITUTION_INVALIDA' };
  // DC-1: Account É a custódia financeira; accountType a tipifica. STARTER
  // (OP-2): valor novo é aceito — não transformar a lista em enum rígido.
  if(!aldTextInDomain(d.accountType,{max:40})) return { ok:false, erro:'ALD_ACCOUNT_TYPE_INVALIDO' };
  return { ok:true, avisos:[], valor:{ name:String(d.name), institution:String(d.institution), accountType:String(d.accountType) }};
}

// ---- avisos de duplicidade (DC-4: AVISA, jamais bloqueia) -------------------
// Duas carteiras com BTC são legítimas; dois PETR4 pedem análise humana. O
// sistema alerta e o registro nasce.
// `network` QUALIFICA a identidade de cripto (USDT Ethereum ≠ USDT Tron), mas não
// a identifica sozinho: dois tokens distintos na mesma rede compartilham o valor.
// Por isso ele entra na CHAVE de cripto e sai da varredura de identificadores.
const ALD_QUALIFICADORES_NAO_IDENTIDADE = ['network'];
function aldInstrumentAvisosDuplicidade(a, cand, ignorarId){
  const avisos=[];
  const chave = (r)=>{
    const partes=[String(r.symbol||'').trim().toLowerCase(), String(r.exchange||'').trim().toLowerCase(), String(r.currency||'')];
    if(r.instrumentFamily==='CRYPTO'){
      const ext = aldRegistroLegivel(r.externalIdentifiers) ? r.externalIdentifiers : {};
      partes.push(String(ext.network||'').trim().toLowerCase()); // DC-4: a rede é parte da identidade
    }
    return partes.join('|');
  };
  const alvo = chave(cand);
  let dupChave=false, dupExt=null;
  for(const r of (Array.isArray(a.instruments)?a.instruments:[])){
    if(!aldRegistroLegivel(r)) continue;
    if(ignorarId && r.instrumentId===ignorarId) continue;
    if(chave(r)===alvo) dupChave=true;
    const ext = aldRegistroLegivel(r.externalIdentifiers) ? r.externalIdentifiers : {};
    for(const k of Object.keys(cand.externalIdentifiers||{})){
      if(ALD_QUALIFICADORES_NAO_IDENTIDADE.indexOf(k)>=0) continue;
      if(!Object.prototype.hasOwnProperty.call(ext,k)) continue;
      // Mesma normalização da chave (trim+caixa): o mesmo par de duplicatas não
      // pode ser detectado ou não conforme o campo por onde se manifesta.
      const norm=(v)=>String(v==null?'':v).trim().toLowerCase();
      if(norm(ext[k])===norm(cand.externalIdentifiers[k])){ dupExt=k; break; }
    }
  }
  if(dupChave) avisos.push('DUPLICADO_SYMBOL_EXCHANGE_CURRENCY');
  if(dupExt) avisos.push('DUPLICADO_IDENTIFICADOR_EXTERNO:'+dupExt);
  return avisos;
}

// ---- atos cadastrais --------------------------------------------------------
// Todos passam por aldMutate: fail-closed de módulo e sentinela por registro
// vêm do C1. Nenhum ato de EXCLUSÃO no C2 — registro cadastral poderá ser
// referenciado por transações futuras (padrão pfActDeleteDebt); a política de
// exclusão nasce com o ledger.
function aldActAddInstrument(dados){
  return aldMutate('instrument_add', (a)=>{
    const r = aldNormalizeInstrumentFields(dados);
    if(!r.ok) return { ok:false, erro:r.erro };
    const rec = { instrumentId:aldId('aldi'), ...r.valor, symbolHistory:[], recordStatus:'ACTIVE', createdAt:aldNowISO() };
    const avisos = r.avisos.concat(aldInstrumentAvisosDuplicidade(a, rec, null));
    if(!Array.isArray(a.instruments)) return { ok:false, erro:'ALD_COLECAO_ILEGIVEL' };
    a.instruments.push(rec);
    return { recordId:rec.instrumentId, avisos };
  }, { label:'instrument_add' });
}
function aldActEditInstrument(instrumentId, mudancas){
  return aldMutate('instrument_edit', (a)=>{
    const alvo = aldFindIn(a,'instruments','instrumentId',instrumentId);
    if(!alvo) return { ok:false, erro:'ALD_REGISTRO_NAO_ENCONTRADO' };
    const m = mudancas || {};
    const prot = aldCamposProtegidosViolados(m, ['instrumentId','createdAt','recordStatus','symbolHistory']);
    if(prot.length) return { ok:false, erro:'ALD_CAMPO_PROTEGIDO:'+prot[0] };
    // Moeda é identidade econômica do instrumento: trocá-la reinterpretaria todo
    // montante futuro. Correção exige novo cadastro, não edição silenciosa.
    if('currency' in m && m.currency!==alvo.currency) return { ok:false, erro:'ALD_CURRENCY_IMUTAVEL' };
    // ALD-03 S2: a família congela na primeira referência econômica. Trocar
    // CRYPTO→EQUITY_LIKE com trades registrados reinterpretaria a semântica da
    // quantidade de TODOS eles. Antes do primeiro trade, curadoria é livre —
    // depois, correção exige novo cadastro. (currency já é imutável sempre;
    // symbol continua editável, com symbolHistory preservando o passado.)
    if('instrumentFamily' in m && m.instrumentFamily!==alvo.instrumentFamily){
      for(const tx of (Array.isArray(a.transactions)?a.transactions:[])){
        if(aldRegistroLegivel(tx) && tx.instrumentId===instrumentId)
          return { ok:false, erro:'ALD_INSTRUMENT_COM_LANCAMENTOS' };
      }
    }
    const cand = { ...alvo, ...m, currency:alvo.currency };
    const r = aldNormalizeInstrumentFields(cand);
    if(!r.ok) return { ok:false, erro:r.erro };
    const avisos = r.avisos.concat(aldInstrumentAvisosDuplicidade(a, { ...r.valor, currency:alvo.currency }, instrumentId));
    // DC-5: symbolHistory append-only. O símbolo anterior é EMPURRADO, nunca
    // perdido. `from:null` = início de uso não registrado (o C2 não o conhece);
    // `to` = instante da aposentadoria. Semântica de corporate action é de fase
    // própria (§36 da spec) — aqui só não se perde o passado.
    // symbolHistory ilegível NÃO é reescrito: apagar a história na primeira
    // edição de nome violaria a lei do conteúdo justamente no campo cuja razão
    // de existir é não perder o passado (DC-5).
    if(alvo.symbolHistory!==undefined && !Array.isArray(alvo.symbolHistory)) return { ok:false, erro:'ALD_SYMBOL_HISTORY_ILEGIVEL' };
    const hist = Array.isArray(alvo.symbolHistory) ? alvo.symbolHistory.slice() : [];
    if(r.valor.symbol!==String(alvo.symbol)){
      hist.push({ symbol:String(alvo.symbol), exchange:(alvo.exchange===undefined?null:alvo.exchange), from:null, to:aldNowISO() });
    }
    alvo.name=r.valor.name; alvo.symbol=r.valor.symbol; alvo.exchange=r.valor.exchange;
    alvo.country=r.valor.country; alvo.assetClass=r.valor.assetClass;
    alvo.instrumentFamily=r.valor.instrumentFamily; alvo.externalIdentifiers=r.valor.externalIdentifiers;
    alvo.symbolHistory=hist;
    return { recordId:instrumentId, avisos };
  }, { label:'instrument_edit' });
}
function aldActAddAsset(dados){
  return aldMutate('asset_add', (a)=>{
    const r = aldNormalizeAssetFields(dados);
    if(!r.ok) return { ok:false, erro:r.erro };
    // lifecycleStatus nasce ACTIVE e NÃO é editável no C2: transição patrimonial
    // (SOLD/DISPOSED/…) é evento econômico do ledger físico, não ato cadastral.
    const rec = { assetId:aldId('alda'), ...r.valor, recordStatus:'ACTIVE', lifecycleStatus:'ACTIVE', createdAt:aldNowISO() };
    if(!Array.isArray(a.assets)) return { ok:false, erro:'ALD_COLECAO_ILEGIVEL' };
    a.assets.push(rec);
    return { recordId:rec.assetId, avisos:r.avisos };
  }, { label:'asset_add' });
}
function aldActEditAsset(assetId, mudancas){
  return aldMutate('asset_edit', (a)=>{
    const alvo = aldFindIn(a,'assets','assetId',assetId);
    if(!alvo) return { ok:false, erro:'ALD_REGISTRO_NAO_ENCONTRADO' };
    const m = mudancas || {};
    if('lifecycleStatus' in m && m.lifecycleStatus!==alvo.lifecycleStatus) return { ok:false, erro:'ALD_LIFECYCLE_NAO_EDITAVEL_NO_C2' };
    const protA = aldCamposProtegidosViolados(m, ['assetId','createdAt','recordStatus']);
    if(protA.length) return { ok:false, erro:'ALD_CAMPO_PROTEGIDO:'+protA[0] };
    const r = aldNormalizeAssetFields({ ...alvo, ...m });
    if(!r.ok) return { ok:false, erro:r.erro };
    for(const k of Object.keys(r.valor)) alvo[k]=r.valor[k];
    return { recordId:assetId, avisos:r.avisos };
  }, { label:'asset_edit' });
}
function aldActAddAccount(dados){
  return aldMutate('account_add', (a)=>{
    const r = aldNormalizeAccountFields(dados);
    if(!r.ok) return { ok:false, erro:r.erro };
    const rec = { accountId:aldId('aldacc'), ...r.valor, recordStatus:'ACTIVE', createdAt:aldNowISO() };
    if(!Array.isArray(a.accounts)) return { ok:false, erro:'ALD_COLECAO_ILEGIVEL' };
    a.accounts.push(rec);
    return { recordId:rec.accountId, avisos:r.avisos };
  }, { label:'account_add' });
}
function aldActEditAccount(accountId, mudancas){
  return aldMutate('account_edit', (a)=>{
    const alvo = aldFindIn(a,'accounts','accountId',accountId);
    if(!alvo) return { ok:false, erro:'ALD_REGISTRO_NAO_ENCONTRADO' };
    const protAc = aldCamposProtegidosViolados(mudancas, ['accountId','createdAt','recordStatus']);
    if(protAc.length) return { ok:false, erro:'ALD_CAMPO_PROTEGIDO:'+protAc[0] };
    const r = aldNormalizeAccountFields({ ...alvo, ...(mudancas||{}) });
    if(!r.ok) return { ok:false, erro:r.erro };
    for(const k of Object.keys(r.valor)) alvo[k]=r.valor[k];
    return { recordId:accountId, avisos:r.avisos };
  }, { label:'account_edit' });
}
function aldActAddCashAccount(dados){
  return aldMutate('cashaccount_add', (a)=>{
    const d = dados || {};
    const conta = aldFindIn(a,'accounts','accountId',d.accountId);
    if(!conta) return { ok:false, erro:'ALD_ACCOUNT_NAO_ENCONTRADA' };
    if(conta.recordStatus!=='ACTIVE') return { ok:false, erro:'ALD_ACCOUNT_INATIVA' };
    if(typeof d.currency!=='string' || !ALD_CURRENCY_RE.test(d.currency)) return { ok:false, erro:'ALD_CURRENCY_INVALIDA' };
    const avisos = aldCurrencySupported(d.currency) ? [] : ['MOEDA_FORA_DO_SUPORTE_DE_RUNTIME'];
    for(const c of (Array.isArray(a.cashAccounts)?a.cashAccounts:[])){
      if(aldRegistroLegivel(c) && c.accountId===d.accountId && c.currency===d.currency){ avisos.push('DUPLICADO_MOEDA_NA_CONTA'); break; }
    }
    const rec = { cashAccountId:aldId('aldc'), accountId:d.accountId, currency:d.currency, recordStatus:'ACTIVE', createdAt:aldNowISO() };
    if(!Array.isArray(a.cashAccounts)) return { ok:false, erro:'ALD_COLECAO_ILEGIVEL' };
    a.cashAccounts.push(rec);
    return { recordId:rec.cashAccountId, avisos };
  }, { label:'cashaccount_add' });
}
// Correção de erro cadastral da cash account. accountId e currency SÃO
// editáveis aqui porque, no C2, nada depende deles: não existe lançamento. Com o
// ledger (ALD-03) a regra muda — cash account com movimento não pode trocar de
// moeda nem de conta, e a restrição precisa nascer junto com o ledger.
function aldActEditCashAccount(cashAccountId, mudancas){
  return aldMutate('cashaccount_edit', (a)=>{
    const alvo = aldFindIn(a,'cashAccounts','cashAccountId',cashAccountId);
    if(!alvo) return { ok:false, erro:'ALD_REGISTRO_NAO_ENCONTRADO' };
    const prot = aldCamposProtegidosViolados(mudancas, ['cashAccountId','createdAt','recordStatus']);
    if(prot.length) return { ok:false, erro:'ALD_CAMPO_PROTEGIDO:'+prot[0] };
    const m = mudancas || {};
    const novoAccountId = ('accountId' in m) ? m.accountId : alvo.accountId;
    const novaMoeda = ('currency' in m) ? m.currency : alvo.currency;
    // ALD-03 S1: uma vez que a conta tenha sido referenciada por um lançamento,
    // `currency` e `accountId` viram imutáveis. Não é rigor formal — trocar a
    // moeda REINTERPRETA todo o passado: os lançamentos continuam na moeda
    // antiga e o saldo inteiro passa a MOEDA_DIVERGENTE, isto é, história
    // ilegível. Corrigir um erro de cadastro depois de haver movimento exige
    // outra conta, não a reescrita do significado da que existe.
    if(('currency' in m && novaMoeda!==alvo.currency) ||
       ('accountId' in m && novoAccountId!==alvo.accountId)){
      for(const t of (Array.isArray(a.transactions)?a.transactions:[])){
        if(!aldRegistroLegivel(t)) continue;
        if(t.cashAccountId===cashAccountId || t.sourceCashAccountId===cashAccountId
           || t.destinationCashAccountId===cashAccountId)
          return { ok:false, erro:'ALD_CASHACCOUNT_COM_LANCAMENTOS' };
      }
    }
    const conta = aldFindIn(a,'accounts','accountId',novoAccountId);
    if(!conta) return { ok:false, erro:'ALD_ACCOUNT_NAO_ENCONTRADA' };
    if(conta.recordStatus!=='ACTIVE') return { ok:false, erro:'ALD_ACCOUNT_INATIVA' };
    if(typeof novaMoeda!=='string' || !ALD_CURRENCY_RE.test(novaMoeda)) return { ok:false, erro:'ALD_CURRENCY_INVALIDA' };
    const avisos = aldCurrencySupported(novaMoeda) ? [] : ['MOEDA_FORA_DO_SUPORTE_DE_RUNTIME'];
    for(const c of (Array.isArray(a.cashAccounts)?a.cashAccounts:[])){
      if(aldRegistroLegivel(c) && c.cashAccountId!==cashAccountId && c.accountId===novoAccountId && c.currency===novaMoeda){
        avisos.push('DUPLICADO_MOEDA_NA_CONTA'); break;
      }
    }
    alvo.accountId=novoAccountId; alvo.currency=novaMoeda;
    return { recordId:cashAccountId, avisos };
  }, { label:'cashaccount_edit' });
}
// Ciclo cadastral ACTIVE↔INACTIVE. Inativar NUNCA apaga nem oculta do histórico
// — é o eixo técnico, distinto do lifecycleStatus patrimonial do Asset.
function aldActSetRecordStatus(tipo, id, status){
  return aldMutate(String(tipo)+'_set_record_status', (a)=>{
    const meta = ALD_COLECOES[tipo];
    if(!meta) return { ok:false, erro:'ALD_TIPO_DESCONHECIDO' };
    if(!aldInEnum(status, ALD_RECORD_STATUS)) return { ok:false, erro:'ALD_RECORD_STATUS_INVALIDO' };
    const alvo = aldFindIn(a, meta.colecao, meta.campoId, id);
    if(!alvo) return { ok:false, erro:'ALD_REGISTRO_NAO_ENCONTRADO' };
    // Integridade referencial, NAS DUAS DIREÇÕES (a segunda foi achado da
    // auditoria C2): reativar cash account exige conta pai ATIVA, senão o par
    // (conta INACTIVE, cash ACTIVE) nasceria pela porta dos fundos.
    if(tipo==='cashaccount' && status==='ACTIVE'){
      const pai = aldFindIn(a,'accounts','accountId',alvo.accountId);
      if(!pai) return { ok:false, erro:'ALD_ACCOUNT_NAO_ENCONTRADA' };
      if(pai.recordStatus!=='ACTIVE') return { ok:false, erro:'ALD_ACCOUNT_INATIVA' };
    }
    if(tipo==='account' && status==='INACTIVE'){
      for(const c of (Array.isArray(a.cashAccounts)?a.cashAccounts:[])){
        if(aldRegistroLegivel(c) && c.accountId===id && c.recordStatus==='ACTIVE') return { ok:false, erro:'ALD_ACCOUNT_COM_CASHACCOUNT_ATIVA' };
      }
    }
    alvo.recordStatus=status;
    return { recordId:id };
  }, { label:String(tipo)+'_set_record_status' });
}
// ============ ALLADIN · ALD-03 S1 — CASH LEDGER ==============================
// O primeiro fato ECONÔMICO do Alladin. O cadastro responde "o que existe"; a
// partir daqui o domínio começa a responder "o que aconteceu" — e só isso: nada
// de posição, custo, valuation, performance ou câmbio, que pertencem a fases
// próprias. Saldo NUNCA é campo: é sempre derivado dos eventos (ALD-I27).
//
// Um fato econômico, múltiplos efeitos (decisão DH-03-2): a transferência é UM
// registro com origem e destino, não dois lançamentos correlacionados. Assim o
// cenário "debitou a origem e o destino não recebeu" não é evitado por controle
// de fluxo — ele é IRREPRESENTÁVEL no schema.
const ALD_EVENT_TYPES  = ['DEPOSIT','WITHDRAWAL','TRANSFER','BUY','SELL','REVERSAL']; // FECHADO
const ALD_TX_STATUS    = ['POSTED','REVERSED'];                          // FECHADO (DRAFT: fase própria)
const ALD_FLOW_SCOPES  = ['INTERNAL','EXTERNAL'];                        // FECHADO
// flowScope é RELAÇÃO COM O PERÍMETRO, não direção (DH-03-1): EXTERNAL cruza a
// fronteira do patrimônio consolidado, INTERNAL move entre custódias que já são
// nossas. Por isso a transferência não é aporte — e é persistido, não inferido:
// registro que divergir desta tabela é DADO INVÁLIDO, jamais corrigido em silêncio.
//
// BUY/SELL NÃO estão na tabela de propósito (DH-S2-9): trocar caixa por papel é
// mudança de COMPOSIÇÃO dentro da mesma custódia, não fluxo de capital pelo
// perímetro. Um trade não possui flowScope — a AUSÊNCIA é contratual, e um
// trade carimbado de fluxo é dado adulterado, tão ilegível quanto um TRANSFER
// dizendo EXTERNAL.
const ALD_FLOW_POR_EVENTO = { DEPOSIT:'EXTERNAL', WITHDRAWAL:'EXTERNAL', TRANSFER:'INTERNAL' };
// Delta de caixa por evento, na perspectiva de cada conta referenciada.
// ALD-03 S2: deixou de ser multiplicador ±1 porque o delta de um trade é
// COMPOSTO — BUY drena amount+fees+taxes; SELL entrega amount−fees−taxes, que
// pode legitimamente ser zero ou negativo (venda pequena com custo maior que o
// produto). Recusar isso seria recusar um fato real por ser incomum.
const ALD_CASH_DELTA = {
  DEPOSIT:    (tx, id) => (tx.cashAccountId===id ? +tx.amount : 0),
  WITHDRAWAL: (tx, id) => (tx.cashAccountId===id ? -tx.amount : 0),
  TRANSFER:   (tx, id) => (tx.sourceCashAccountId===id ? -tx.amount : (tx.destinationCashAccountId===id ? +tx.amount : 0)),
  BUY:        (tx, id) => (tx.cashAccountId===id ? -(tx.amount+tx.fees+tx.taxes) : 0),
  SELL:       (tx, id) => (tx.cashAccountId===id ? +(tx.amount-tx.fees-tx.taxes) : 0),
};
// A perna de papel de BUY/SELL (+quantity/−quantity) NÃO tem engine neste
// ciclo: quantity é fato persistido e verificável, e quem o agregará é o
// Position Engine (ALD-04). Somar aqui exigiria aritmética decimal que este
// slice deliberadamente não tem.

// Forma canônica de quantity: string decimal positiva, uma grafia por valor —
// sem sinal, expoente, zeros à esquerda ou zeros finais na fração. A igualdade
// de VALOR vira igualdade de STRING, e é disso que a consistência do reversal
// depende sem precisar de aritmética. O teto de 64 chars é proteção TÉCNICA de
// representação, não política econômica de precisão (rounding por classe é
// decisão pendente da spec §29).
const ALD_QUANTITY_RE = /^(0|[1-9][0-9]*)(\.[0-9]*[1-9])?$/;
function aldQuantityValida(q){
  return typeof q==='string' && q!=='0' && q.length<=64 && ALD_QUANTITY_RE.test(q);
}

function aldTxRefsDoEvento(tipo){
  return tipo==='TRANSFER' ? ['sourceCashAccountId','destinationCashAccountId'] : ['cashAccountId'];
}
// Forma de UM registro do ledger, sem olhar o resto do agregado. Devolve o
// diagnóstico em vez de lançar: quem calcula saldo precisa distinguir "não é
// desta conta" de "não dá para saber de quem é".
function aldTxLegivel(tx){
  if(!aldRegistroLegivel(tx)) return false;
  if(!aldInEnum(tx.eventType, ALD_EVENT_TYPES)) return false;
  if(!aldInEnum(tx.status, ALD_TX_STATUS)) return false;
  if(typeof tx.amount!=='number' || !Number.isSafeInteger(tx.amount) || tx.amount<=0) return false;
  if(typeof tx.currency!=='string' || !ALD_CURRENCY_RE.test(tx.currency)) return false;
  if(typeof tx.effectiveAt!=='string' || !ALD_DATE_RE.test(tx.effectiveAt)) return false;
  if(typeof tx.transactionId!=='string' || !tx.transactionId) return false;
  if(tx.eventType==='REVERSAL'){
    if(typeof tx.reversalOf!=='string' || !tx.reversalOf) return false;
    // reversedEventType é obrigatório e nunca aponta para outro REVERSAL: sem
    // ele não há como saber qual contrato de flowScope o espelho deve seguir.
    if(!aldInEnum(tx.reversedEventType, ALD_EVENT_TYPES) || tx.reversedEventType==='REVERSAL') return false;
  }else if(tx.reversalOf!==undefined) return false;
  // flowScope é condicional por FAMÍLIA (DH-S2-9): evento de fluxo exige o
  // valor exato da tabela; trade exige AUSÊNCIA — presença é adulteração. O
  // reversal segue o contrato do tipo que reverte.
  const tipoBase = tx.eventType==='REVERSAL' ? tx.reversedEventType : tx.eventType;
  const fsEsperado = ALD_FLOW_POR_EVENTO[tipoBase];
  if(fsEsperado!==undefined){
    if(tx.flowScope!==fsEsperado) return false;
  }else if(Object.prototype.hasOwnProperty.call(tx,'flowScope')) return false;
  if((tipoBase==='BUY'||tipoBase==='SELL') && tx.eventType!=='REVERSAL'){
    if(typeof tx.instrumentId!=='string' || !tx.instrumentId) return false;
    if(!aldQuantityValida(tx.quantity)) return false;
    if(!Number.isSafeInteger(tx.fees) || tx.fees<0) return false;
    if(!Number.isSafeInteger(tx.taxes) || tx.taxes<0) return false;
    // MC-S2-2 vale também na LEITURA: componentes individualmente válidos podem
    // compor um delta fora do inteiro seguro — registro assim é ilegível, nunca
    // um número plausível.
    const delta = tipoBase==='BUY' ? tx.amount+tx.fees+tx.taxes : tx.amount-tx.fees-tx.taxes;
    if(!Number.isSafeInteger(delta)) return false;
  }
  // Os campos econômicos de um REVERSAL (inclusive os de trade) são julgados
  // pela consistência cruzada com o original (aldReversalConsistente): a
  // legibilidade de UM registro não enxerga o par.
  if(tx.eventType!=='REVERSAL'){
    for(const r of aldTxRefsDoEvento(tx.eventType)){ if(typeof tx[r]!=='string' || !tx[r]) return false; }
    if(tx.eventType==='TRANSFER' && tx.sourceCashAccountId===tx.destinationCashAccountId) return false;
  }
  return true;
}
// Efeito de um registro sobre UMA conta. O REVERSAL espelha as referências do
// original e inverte o sinal — o original permanece contando, e a soma dos dois
// dá zero. "REVERSED" diz que o fato foi revertido depois, não que ele nunca
// aconteceu: apagar o passado seria reescrever a história, não corrigi-la.
// MC-S2-1 — consistência cruzada do par original ↔ reversal, na INTERPRETAÇÃO
// do agregado. A porta de escrita constrói o reversal correto, mas escrita
// correta não prova leitura íntegra: um reversal adulterado depois de persistido
// (amount 10000→9000) continuaria formalmente legível e o saldo sairia errado
// com cara de válido. Aqui, qualquer divergência econômica entre o par torna o
// saldo INDISPONÍVEL — nunca corrigido em silêncio.
// Próprios do reversal, fora da igualdade: transactionId, effectiveAt,
// recordedAt, dedupeKey, note, status.
function aldReversalConsistente(rev, orig){
  if(rev.reversedEventType!==orig.eventType) return false;
  if(rev.amount!==orig.amount) return false;
  if(rev.currency!==orig.currency) return false;
  for(const r of ['cashAccountId','sourceCashAccountId','destinationCashAccountId']){
    const temRev = Object.prototype.hasOwnProperty.call(rev, r);
    if(temRev!==Object.prototype.hasOwnProperty.call(orig, r)) return false;
    if(temRev && rev[r]!==orig[r]) return false;
  }
  if(orig.eventType==='BUY'||orig.eventType==='SELL'){
    if(rev.instrumentId!==orig.instrumentId) return false;
    if(rev.quantity!==orig.quantity) return false;   // igualdade de STRING (forma canônica)
    if(rev.fees!==orig.fees) return false;
    if(rev.taxes!==orig.taxes) return false;
  }
  const fsRev = Object.prototype.hasOwnProperty.call(rev,'flowScope');
  if(fsRev!==Object.prototype.hasOwnProperty.call(orig,'flowScope')) return false;
  if(fsRev && rev.flowScope!==orig.flowScope) return false;
  return true;
}
// Delta de caixa de um registro sobre UMA conta. Para o REVERSAL, o delta é o
// NEGATIVO do delta do original — depois que a consistência do par foi provada,
// o original é a única fonte necessária, e divergência já virou BLOCKING antes
// de chegar aqui.
function aldTxEfeito(tx, cashAccountId, porId){
  if(tx.eventType!=='REVERSAL'){
    const f = ALD_CASH_DELTA[tx.eventType];
    return f ? f(tx, cashAccountId) : 0;
  }
  const orig = porId[tx.reversalOf];
  if(!orig) return null;                       // reversal órfão: não classificável
  const f = ALD_CASH_DELTA[orig.eventType];
  if(!f) return null;
  return -f(orig, cashAccountId);
}
function aldTxOrdenar(lista){
  return lista.slice().sort((a,b)=>
    (a.effectiveAt<b.effectiveAt?-1:a.effectiveAt>b.effectiveAt?1:
    (a.recordedAt<b.recordedAt?-1:a.recordedAt>b.recordedAt?1:
    (a.transactionId<b.transactionId?-1:a.transactionId>b.transactionId?1:0))));
}
function aldTxDedupeExiste(a, chave, ignorarId){
  for(const t of (Array.isArray(a.transactions)?a.transactions:[])){
    if(!aldRegistroLegivel(t)) continue;
    if(ignorarId && t.transactionId===ignorarId) continue;
    if(typeof t.dedupeKey==='string' && t.dedupeKey===chave) return true;
  }
  return false;
}
// Conta de caixa apta a RECEBER lançamento novo: existe e está ativa. Fato já
// registrado nunca deixa de valer porque a conta foi encerrada depois — o
// passado não depende do status presente.
function aldCashAptaParaLancamento(a, id){
  const c = aldFindIn(a,'cashAccounts','cashAccountId',id);
  if(!c) return { ok:false, erro:'ALD_CASHACCOUNT_NAO_ENCONTRADA' };
  if(c.recordStatus!=='ACTIVE') return { ok:false, erro:'ALD_CASHACCOUNT_INATIVA' };
  return { ok:true, valor:c };
}
function aldNormalizeTransactionFields(a, d){
  d = d || {};
  if(!aldInEnum(d.eventType, ['DEPOSIT','WITHDRAWAL','TRANSFER','BUY','SELL'])) return { ok:false, erro:'ALD_EVENT_TYPE_INVALIDO' };
  // Trade nao possui flowScope valido NENHUM — o chamador que o declara esta
  // afirmando uma semantica economica impossivel, e apagar a declaracao em
  // silencio mascararia o erro do produtor. Nos eventos de fluxo o dominio tem
  // resposta propria e sempre deriva; aqui nao ha o que derivar: RECUSA. A
  // regra e de PRESENCA ({flowScope: undefined} tambem recusa).
  if((d.eventType==='BUY'||d.eventType==='SELL') &&
     Object.prototype.hasOwnProperty.call(d,'flowScope'))
    return { ok:false, erro:'ALD_FLOW_SCOPE_NAO_PERMITIDO_EM_TRADE' };
  if(typeof d.amount!=='number' || !Number.isSafeInteger(d.amount) || d.amount<=0) return { ok:false, erro:'ALD_AMOUNT_INVALIDO' };
  if(typeof d.effectiveAt!=='string' || !ALD_DATE_RE.test(d.effectiveAt)) return { ok:false, erro:'ALD_EFFECTIVE_AT_INVALIDA' };
  const nota = aldOptionalText(d.note, 240); if(!nota.ok) return { ok:false, erro:'ALD_NOTE_INVALIDA' };
  let dedupe = null;
  if(d.dedupeKey!==undefined && d.dedupeKey!==null && d.dedupeKey!==''){
    if(!aldTextInDomain(d.dedupeKey,{max:120})) return { ok:false, erro:'ALD_DEDUPE_KEY_INVALIDA' };
    dedupe = String(d.dedupeKey).trim();
    // Duplicidade de CADASTRO avisa; duplicidade de LANÇAMENTO fabrica dinheiro.
    // Por isso aqui é recusa, não aviso — a única divergência deliberada do DC-4.
    if(aldTxDedupeExiste(a, dedupe, null)) return { ok:false, erro:'ALD_DEDUPE_KEY_DUPLICADA' };
  }
  const refs = aldTxRefsDoEvento(d.eventType);
  const contas = {};
  for(const r of refs){
    if(typeof d[r]!=='string' || !d[r]) return { ok:false, erro:'ALD_REFERENCIA_AUSENTE:'+r };
    const apta = aldCashAptaParaLancamento(a, d[r]);
    if(!apta.ok) return { ok:false, erro:apta.erro };
    contas[r] = apta.valor;
  }
  if(d.eventType==='TRANSFER'){
    if(d.sourceCashAccountId===d.destinationCashAccountId) return { ok:false, erro:'ALD_TRANSFER_MESMA_CONTA' };
    // Sem câmbio neste ciclo: converter exigiria taxa, e taxa é fato econômico
    // que ninguém registrou. Transferir entre moedas distintas é RECUSA, não
    // conversão implícita.
    if(contas.sourceCashAccountId.currency!==contas.destinationCashAccountId.currency)
      return { ok:false, erro:'ALD_TRANSFER_MOEDAS_DIFERENTES' };
  }
  const moeda = contas[refs[0]].currency;
  if(d.currency!==undefined && d.currency!==moeda) return { ok:false, erro:'ALD_CURRENCY_DIVERGE_DA_CONTA' };
  const valor = { eventType:d.eventType, status:'POSTED',
    amount:d.amount, currency:moeda, effectiveAt:d.effectiveAt };
  // flowScope só existe para evento de FLUXO (DH-S2-9): a tabela não conhece
  // BUY/SELL e a propriedade nem sequer é criada — presença/ausência é contrato.
  const fs = ALD_FLOW_POR_EVENTO[d.eventType];
  if(fs!==undefined) valor.flowScope = fs;
  if(d.eventType==='BUY'||d.eventType==='SELL'){
    // A dupla atômica papel↔caixa: UM registro, duas pernas. O instrumento
    // precisa existir e estar apto — fato antigo nunca depende do status
    // presente, mas lançamento NOVO exige cadastro vivo (espelho da regra de
    // CashAccount do S1).
    if(typeof d.instrumentId!=='string' || !d.instrumentId) return { ok:false, erro:'ALD_REFERENCIA_AUSENTE:instrumentId' };
    const inst = aldFindIn(a,'instruments','instrumentId',d.instrumentId);
    if(!inst) return { ok:false, erro:'ALD_INSTRUMENT_NAO_ENCONTRADO' };
    if(inst.recordStatus!=='ACTIVE') return { ok:false, erro:'ALD_INSTRUMENT_INATIVO' };
    // Sem câmbio implícito: liquidar um instrumento numa conta de outra moeda
    // exigiria taxa que ninguém registrou — RECUSA, como no TRANSFER do S1.
    if(inst.currency!==moeda) return { ok:false, erro:'ALD_INSTRUMENT_MOEDA_DIVERGE_DA_CONTA' };
    if(!aldQuantityValida(d.quantity)) return { ok:false, erro:'ALD_QUANTITY_INVALIDA' };
    // fees/taxes: opcionais na ENTRADA, obrigatórios na forma PERSISTIDA
    // (DH-S2-10) — uma única grafia, sem que consumidor futuro distinga
    // "sem taxa" de "taxa zero".
    let fees = 0, taxes = 0;
    if(d.fees!==undefined){
      if(typeof d.fees!=='number' || !Number.isSafeInteger(d.fees) || d.fees<0) return { ok:false, erro:'ALD_FEES_INVALIDAS' };
      fees = d.fees;
    }
    if(d.taxes!==undefined){
      if(typeof d.taxes!=='number' || !Number.isSafeInteger(d.taxes) || d.taxes<0) return { ok:false, erro:'ALD_TAXES_INVALIDOS' };
      taxes = d.taxes;
    }
    // MC-S2-2: componentes individualmente válidos podem compor delta fora do
    // inteiro seguro (amount=1, fees=MAX) — recusa na porta, nos DOIS sentidos.
    const delta = d.eventType==='BUY' ? d.amount+fees+taxes : d.amount-fees-taxes;
    if(!Number.isSafeInteger(delta)) return { ok:false, erro:'ALD_EFEITO_MONETARIO_FORA_DO_INTEIRO_SEGURO' };
    valor.instrumentId = d.instrumentId;
    valor.quantity = d.quantity;
    valor.fees = fees;
    valor.taxes = taxes;
  }
  for(const r of refs) valor[r]=d[r];
  if(dedupe) valor.dedupeKey=dedupe;
  if(nota.valor) valor.note=nota.valor;
  return { ok:true, valor };
}
function aldActAddTransaction(dados){
  return aldMutate('transaction_add', (a)=>{
    if(!Array.isArray(a.transactions)) return { ok:false, erro:'ALD_COLECAO_ILEGIVEL' };
    const r = aldNormalizeTransactionFields(a, dados);
    if(!r.ok) return { ok:false, erro:r.erro };
    const rec = { transactionId:aldId('aldtx'), ...r.valor, recordedAt:aldNowISO() };
    a.transactions.push(rec);
    return { recordId:rec.transactionId, avisos:[] };
  }, { label:'transaction_add' });
}
// A reversão é um fato econômico NOVO, com data própria: `effectiveAt` é do
// chamador. Tudo o que é econômico — valor, moeda, escopo e as referências —
// é COPIADO do original, de modo que divergir seja impossível.
function aldActReverseTransaction(originalId, dados){
  return aldMutate('transaction_reverse', (a)=>{
    if(!Array.isArray(a.transactions)) return { ok:false, erro:'ALD_COLECAO_ILEGIVEL' };
    const orig = aldFindIn(a,'transactions','transactionId',originalId);
    if(!orig) return { ok:false, erro:'ALD_REGISTRO_NAO_ENCONTRADO' };
    if(!aldTxLegivel(orig)) return { ok:false, erro:'ALD_TRANSACAO_ILEGIVEL' };
    if(orig.eventType==='REVERSAL') return { ok:false, erro:'ALD_REVERSAL_DE_REVERSAL' };
    // A busca pelo reversal existente vem ANTES da checagem de status: reverter
    // duas vezes falha pelas duas razões, e a mais informativa é a que diz o que
    // de fato aconteceu — "já existe uma reversão", não "não está POSTED".
    for(const t of a.transactions){
      if(aldRegistroLegivel(t) && t.eventType==='REVERSAL' && t.reversalOf===originalId)
        return { ok:false, erro:'ALD_REVERSAL_JA_EXISTE' };
    }
    if(orig.status!=='POSTED') return { ok:false, erro:'ALD_TRANSACAO_NAO_ESTA_POSTED' };
    const d = dados || {};
    if(typeof d.effectiveAt!=='string' || !ALD_DATE_RE.test(d.effectiveAt)) return { ok:false, erro:'ALD_EFFECTIVE_AT_INVALIDA' };
    const nota = aldOptionalText(d.note, 240); if(!nota.ok) return { ok:false, erro:'ALD_NOTE_INVALIDA' };
    let dedupe = null;
    if(d.dedupeKey!==undefined && d.dedupeKey!==null && d.dedupeKey!==''){
      if(!aldTextInDomain(d.dedupeKey,{max:120})) return { ok:false, erro:'ALD_DEDUPE_KEY_INVALIDA' };
      dedupe = String(d.dedupeKey).trim();
      if(aldTxDedupeExiste(a, dedupe, null)) return { ok:false, erro:'ALD_DEDUPE_KEY_DUPLICADA' };
    }
    for(const k of ['amount','currency','flowScope','eventType','cashAccountId',
                    'sourceCashAccountId','destinationCashAccountId',
                    'instrumentId','quantity','fees','taxes']){
      if(Object.prototype.hasOwnProperty.call(d,k)) return { ok:false, erro:'ALD_CAMPO_ECONOMICO_NAO_INFORMAVEL:'+k };
    }
    const rec = { transactionId:aldId('aldtx'), eventType:'REVERSAL', status:'POSTED',
      amount:orig.amount, currency:orig.currency,
      effectiveAt:d.effectiveAt, recordedAt:aldNowISO(), reversalOf:originalId,
      reversedEventType:orig.eventType };
    // flowScope espelha PRESENÇA, não só valor (DH-S2-9): original de fluxo →
    // copia; original de trade → a propriedade nem é criada. `{flowScope:
    // orig.flowScope}` com original sem o campo fabricaria uma propriedade
    // presente com undefined — presença/ausência é contrato, não detalhe.
    if(Object.prototype.hasOwnProperty.call(orig,'flowScope')) rec.flowScope = orig.flowScope;
    if(orig.eventType==='BUY'||orig.eventType==='SELL'){
      rec.instrumentId = orig.instrumentId;
      rec.quantity = orig.quantity;       // string copiada byte-idêntica
      rec.fees = orig.fees;
      rec.taxes = orig.taxes;
    }
    for(const r of aldTxRefsDoEvento(orig.eventType)) rec[r]=orig[r];
    if(dedupe) rec.dedupeKey=dedupe;
    if(nota.valor) rec.note=nota.valor;
    a.transactions.push(rec);
    orig.status='REVERSED';   // lifecycle do original; campos econômicos intactos
    return { recordId:rec.transactionId, avisos:[] };
  }, { label:'transaction_reverse' });
}
function aldCatalogos(){
  return {
    fechados:{ instrumentFamily:ALD_INSTRUMENT_FAMILIES.slice(), recordMode:ALD_RECORD_MODES.slice(),
               recordStatus:ALD_RECORD_STATUS.slice(), lifecycleStatus:ALD_LIFECYCLE_STATUS.slice() },
    starter:{ accountType:ALD_STARTER_ACCOUNT_TYPES.slice(), nature:ALD_STARTER_NATURES.slice(),
              strategicPurpose:ALD_STARTER_PURPOSES.slice(), assetClass:ALD_STARTER_ASSET_CLASSES.slice() },
  };
}

// ---- superfície pública -----------------------------------------------------
// Leitura e utilitários apenas — não é UI (HD-7: UI só no C3). aldCompat() é a
// exposição explícita do estado de incompatibilidade exigida pelo fail-closed;
// o aviso visual chega com a UI do C3.
if(typeof window!=='undefined'){
// ---- C3-S1 · read-model cadastral (fronteira de LEITURA da UI) ----------------
// A UI não recebe referência viva de S.alladin: cada chamada devolve um snapshot
// PROFUNDAMENTE desacoplado (clone por JSON + congelamento recursivo) contendo
// APENAS os campos cadastrais que ESTE build conhece — um agregado em schema
// futuro é projetado, nunca normalizado, e campos desconhecidos são ignorados
// (o agregado original permanece byte-idêntico). NADA aqui materializa estado:
// S.alladin ausente ou ilegível devolve coleção vazia sem criar coisa alguma.
// Nenhum campo econômico existe neste contrato — saldo, quantidade, preço,
// valuation e afins só nascerão com ALD-03/ALD-04, em superfícies próprias.
const ALD_LEITURA_CAMPOS = Object.freeze({
  instruments: Object.freeze(['instrumentId','name','symbol','instrumentFamily','assetClass',
    'currency','exchange','country','externalIdentifiers','symbolHistory','recordStatus','createdAt']),
  assets: Object.freeze(['assetId','name','nature','category','subcategory','strategicPurpose',
    'strategicGroup','tags','recordMode','owners','location','acquisitionDate',
    'recordStatus','lifecycleStatus','createdAt']),
  accounts: Object.freeze(['accountId','name','institution','accountType','recordStatus','createdAt']),
  cashAccounts: Object.freeze(['cashAccountId','accountId','currency','recordStatus','createdAt']),
  transactions: Object.freeze(['transactionId','eventType','status','flowScope','amount','currency',
    'effectiveAt','recordedAt','cashAccountId','sourceCashAccountId','destinationCashAccountId',
    'instrumentId','quantity','fees','taxes',
    'reversalOf','reversedEventType','dedupeKey','note']),
});
function aldFreezeDeep(v){
  if(v && typeof v==='object'){
    Object.keys(v).forEach(k=>aldFreezeDeep(v[k]));
    Object.freeze(v);
  }
  return v;
}
function aldVistaCadastral(colecao){
  const campos=ALD_LEITURA_CAMPOS[colecao];
  if(!campos) return Object.freeze([]);
  const a=(typeof S==='object' && S) ? S.alladin : undefined;   // leitura pura
  const lista=(a && Array.isArray(a[colecao])) ? a[colecao] : [];
  const out=lista.filter(aldRegistroLegivel).map(function(r){
    const dto={};
    campos.forEach(function(k){
      if(!Object.prototype.hasOwnProperty.call(r,k)) return;
      try{ dto[k]=JSON.parse(JSON.stringify(r[k])); }catch(e){ /* campo não-serializável: omitido */ }
    });
    return aldFreezeDeep(dto);
  });
  return Object.freeze(out);
}

// ---- saldo de caixa: DERIVADO, e fail-closed por qualidade de dado ----------
// Nunca existe `CashAccount.balance`. O saldo é a soma dos efeitos econômicos, e
// participam TODOS os registros efetivos: o original REVERSED continua contando
// e o REVERSAL contra-lança, somando zero. Filtrar o revertido apagaria metade
// do par e devolveria um número errado com cara de certo.
//
// Qualidade BLOQUEANTE não vira saldo parcial: um único registro que este build
// não consiga classificar com segurança torna a métrica INDISPONÍVEL — porque
// não há como afirmar que ele não pertencia a esta conta. Meio saldo apresentado
// como saldo é pior que a ausência dele.
function aldSaldoDeCaixa(cashAccountId){
  const a = (typeof S==='object' && S) ? S.alladin : undefined;
  const conta = a ? aldFindIn(a,'cashAccounts','cashAccountId',cashAccountId) : null;
  const issues = [];
  if(!conta) return Object.freeze({ available:false, amount:null, currency:null,
    quality:'BLOCKING', issues:Object.freeze(['ALD_CASHACCOUNT_NAO_ENCONTRADA']), consideradas:0 });
  const lista = Array.isArray(a.transactions) ? a.transactions : [];
  const porId = {};
  for(const t of lista){ if(aldRegistroLegivel(t) && typeof t.transactionId==='string') porId[t.transactionId]=t; }
  let total = 0, consideradas = 0;
  for(const t of lista){
    if(!aldTxLegivel(t)){ issues.push('ALD_TRANSACAO_ILEGIVEL'); continue; }
    // MC-S2-1: a consistência do par vem ANTES do efeito. A escrita constrói o
    // reversal correto, mas o saldo é calculado sobre o que está PERSISTIDO —
    // e um par divergente é mentira no ledger, jamais um número.
    if(t.eventType==='REVERSAL'){
      const orig = porId[t.reversalOf];
      if(orig && !aldReversalConsistente(t, orig)){
        issues.push('ALD_REVERSAL_INCONSISTENTE:'+t.transactionId); continue;
      }
    }
    const efeito = aldTxEfeito(t, cashAccountId, porId);
    if(efeito===null){ issues.push('ALD_REVERSAL_ORFAO:'+t.transactionId); continue; }
    if(efeito===0) continue;
    if(t.currency!==conta.currency){ issues.push('ALD_MOEDA_DIVERGENTE:'+t.transactionId); continue; }
    // MC-S2-2: a guarda é POR PASSO. Um acumulador que atravessa 2^53 já perdeu
    // precisão, e um total que "volta" à faixa segura é número corrompido com
    // cara de são — a checagem só no fim aprovaria exatamente esse caso.
    const proximo = total + efeito;
    if(!Number.isSafeInteger(proximo)){ issues.push('ALD_SOMA_FORA_DO_INTEIRO_SEGURO'); continue; }
    total = proximo; consideradas++;
  }
  if(issues.length) return Object.freeze({ available:false, amount:null, currency:conta.currency,
    quality:'BLOCKING', issues:Object.freeze(issues.slice(0,20)), consideradas:0 });
  return Object.freeze({ available:true, amount:total, currency:conta.currency,
    quality:'OK', issues:Object.freeze([]), consideradas });
}

// ============ ALLADIN · ALD-04 S1 — POSITION QUANTITY ENGINE =================
// Posição por QUANTIDADE, derivada do ledger a cada leitura — nunca persistida
// (ALD-I27). Identidade: instrumentId + accountId (DH-04-1); a custódia vem
// EXCLUSIVAMENTE de cashAccount.accountId — o papel vive na corretora, não na
// conta de caixa, e duas cash accounts do mesmo Account somam UMA posição.
//
// Aritmética decimal EXATA por inteiro escalado em BigInt: adição/subtração
// decimal é fechada — não existe arredondamento possível, então nenhuma
// política de rounding é criada aqui (spec §29 segue pendente). Number/float
// jamais tocam valor econômico. BigInt nunca sai destas funções: o DTO carrega
// apenas a string canônica.
function aldDecParse(q){
  const ponto = q.indexOf('.');
  if(ponto < 0) return { v: BigInt(q), e: 0 };
  const frac = q.slice(ponto + 1);
  return { v: BigInt(q.slice(0, ponto) + frac), e: frac.length };
}
function aldDecSoma(a, b){
  const e = a.e > b.e ? a.e : b.e;
  const va = a.v * (10n ** BigInt(e - a.e));
  const vb = b.v * (10n ** BigInt(e - b.e));
  return { v: va + vb, e };
}
function aldDecNeg(a){ return { v: -a.v, e: a.e }; }
function aldDecZero(a){ return a.v === 0n; }
// Render canônico ASSINADO: fração sem zeros finais, inteiro sem zeros à
// esquerda (BigInt garante), '-' só quando o valor é negativo. O derivado pode
// exceder os 64 chars do teto de ENTRADA — o teto é de payload de input, não
// de verdade econômica: truncar aqui seria inventar um número.
function aldDecRender(a){
  let v = a.v;
  const neg = v < 0n;
  if(neg) v = -v;
  let s = v.toString();
  if(a.e > 0){
    if(s.length <= a.e) s = '0'.repeat(a.e - s.length + 1) + s;
    const int = s.slice(0, s.length - a.e);
    const frac = s.slice(s.length - a.e).replace(/0+$/, '');
    s = frac ? int + '.' + frac : int;
  }
  return (neg && s !== '0') ? '-' + s : s;
}

// Direção da perna de papel por evento. Eventos só-caixa não estão na tabela.
const ALD_PAPEL_DELTA = { BUY: 1, SELL: -1 };

function aldPosicoes(){
  const a = (typeof S==='object' && S) ? S.alladin : undefined;
  const issues = [];
  const bloqueado = (iss) => Object.freeze({ available:false, quality:'BLOCKING',
    issues:Object.freeze(iss.slice(0,20)), positions:Object.freeze([]) });
  // FUTURE SCHEMA primeiro, mesmo que todos os registros presentes sejam de
  // tipos conhecidos: um agregado de versão futura pode carregar semântica que
  // este build ignora, e afirmar posição sobre ele seria afirmar o que não se
  // pode provar.
  if(aldCompat().readOnly) return bloqueado([ALD_READ_ONLY_FUTURE_SCHEMA]);
  const lista = (a && Array.isArray(a.transactions)) ? a.transactions : [];
  const porId = {};
  for(const t of lista){ if(aldRegistroLegivel(t) && typeof t.transactionId==='string') porId[t.transactionId]=t; }
  // Map aninhado como identidade — nunca concatenação de IDs, que colide.
  const porInstrumento = new Map();
  // A custódia do trade: cashAccountId → CashAccount → accountId → Account.
  // Cadastro ausente ou moeda divergente entre trade/caixa/instrumento é
  // classificação insegura ⇒ fail-closed GLOBAL, nunca posição parcial.
  const custodiaDoTrade = (tx) => {
    const caixa = aldFindIn(a,'cashAccounts','cashAccountId',tx.cashAccountId);
    if(!caixa){ issues.push('ALD_CASHACCOUNT_NAO_ENCONTRADA:'+tx.transactionId); return null; }
    const conta = aldFindIn(a,'accounts','accountId',caixa.accountId);
    if(!conta){ issues.push('ALD_ACCOUNT_NAO_ENCONTRADA:'+tx.transactionId); return null; }
    const inst = aldFindIn(a,'instruments','instrumentId',tx.instrumentId);
    if(!inst){ issues.push('ALD_INSTRUMENT_NAO_ENCONTRADO:'+tx.transactionId); return null; }
    if(tx.currency!==caixa.currency || inst.currency!==caixa.currency){
      issues.push('ALD_MOEDA_DIVERGENTE:'+tx.transactionId); return null;
    }
    return caixa.accountId;
  };
  for(const t of lista){
    if(!aldTxLegivel(t)){ issues.push('ALD_TRANSACAO_ILEGIVEL'); continue; }
    let alvo = null, sinal = 0;
    if(t.eventType==='REVERSAL'){
      const orig = porId[t.reversalOf];
      if(!orig || !aldTxLegivel(orig)){ issues.push('ALD_REVERSAL_ORFAO:'+t.transactionId); continue; }
      // MC-S2-1 antes de qualquer efeito — par divergente é mentira no ledger.
      if(!aldReversalConsistente(t, orig)){ issues.push('ALD_REVERSAL_INCONSISTENTE:'+t.transactionId); continue; }
      const d = ALD_PAPEL_DELTA[orig.eventType];
      if(d===undefined) continue;          // reversal de evento só-caixa: papel zero
      alvo = orig; sinal = -d;             // neutralização EXATA: quantity byte-igual + soma exata
    }else{
      const d = ALD_PAPEL_DELTA[t.eventType];
      if(d===undefined) continue;          // evento só-caixa: papel zero
      alvo = t; sinal = d;
    }
    const accountId = custodiaDoTrade(alvo);
    if(accountId===null) continue;         // issue registrada — bloqueio no fim
    let porConta = porInstrumento.get(alvo.instrumentId);
    if(!porConta){ porConta = new Map(); porInstrumento.set(alvo.instrumentId, porConta); }
    let pos = porConta.get(accountId);
    if(!pos){ pos = { acc:{ v:0n, e:0 }, consideradas:0 }; porConta.set(accountId, pos); }
    const q = aldDecParse(alvo.quantity);
    pos.acc = aldDecSoma(pos.acc, sinal < 0 ? aldDecNeg(q) : q);
    pos.consideradas++;
  }
  if(issues.length) return bloqueado(issues);
  // Ordem DETERMINÍSTICA — instrumentId ASC, depois accountId ASC. A ordem
  // física do array é acidente de inserção e não pode vazar para o resultado.
  const positions = [];
  for(const iid of [...porInstrumento.keys()].sort()){
    const porConta = porInstrumento.get(iid);
    for(const aid of [...porConta.keys()].sort()){
      const pos = porConta.get(aid);
      if(aldDecZero(pos.acc)) continue;    // DH-04-2: posição zerada sai da coleção
      positions.push(Object.freeze({ instrumentId:iid, accountId:aid,
        quantity: aldDecRender(pos.acc), consideradas: pos.consideradas }));
    }
  }
  return Object.freeze({ available:true, quality:'OK', issues:Object.freeze([]),
    positions:Object.freeze(positions) });
}

  window.JPWAlladin = {
    compat: aldCompat,
    // Leitura cadastral para a UI (C3-S1): snapshots desacoplados e congelados.
    leitura: Object.freeze({
      instruments: function(){ return aldVistaCadastral('instruments'); },
      assets: function(){ return aldVistaCadastral('assets'); },
      accounts: function(){ return aldVistaCadastral('accounts'); },
      cashAccounts: function(){ return aldVistaCadastral('cashAccounts'); },
      // Ledger em ordem ECONÔMICA — (effectiveAt, recordedAt, transactionId) —
      // nunca a ordem do array, que é acidente de inserção e não fato temporal.
      transactions: function(){ return Object.freeze(aldTxOrdenar(aldVistaCadastral('transactions'))); },
      saldoDeCaixa: aldSaldoDeCaixa,
      // ALD-04 S1 — posição por quantidade, derivada e fail-closed (DH-04-5:
      // única API nova do slice; posicaoDe() não existe neste ciclo).
      posicoes: aldPosicoes,
    }),
    writeBlockReason: aldWriteBlockReason,
    money: {
      parse: aldParseMoney,
      format: aldFormatMoney,
      supported: aldCurrencySupported,
      runtimeCurrencies: function(){ return Object.keys(ALD_RUNTIME_CURRENCIES); },
    },
    id: aldId,
    catalogos: aldCatalogos,
    // Atos cadastrais (C2). Não é UI (HD-7: UI só no C3) — é a superfície pela
    // qual os testes e a Human Acceptance por console exercitam o domínio.
    cadastro: {
      addInstrument: aldActAddInstrument,   editInstrument: aldActEditInstrument,
      addAsset: aldActAddAsset,             editAsset: aldActEditAsset,
      addAccount: aldActAddAccount,         editAccount: aldActEditAccount,
      addCashAccount: aldActAddCashAccount, editCashAccount: aldActEditCashAccount,
      setRecordStatus: aldActSetRecordStatus,
    },
    // ALD-03 S1 — superfície econômica, separada do cadastro de propósito: o
    // Alladin passa a responder duas perguntas distintas, e a fronteira entre
    // elas é visível também na API.
    ledger: {
      addTransaction: aldActAddTransaction,
      reverseTransaction: aldActReverseTransaction,
    },
  };
}
