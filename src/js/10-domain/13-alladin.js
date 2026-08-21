// ============ ALLADIN · ALD-01 C1 — FOUNDATION INFRASTRUCTURE ===============
// Sistema Patrimonial e Consolidador de Investimentos do JP Wealth.
// Contrato: JPW-ALLADIN-SPEC V1.2.1 + ALD-01 Proposal Rev.2 (aprovado 2026-08-20).
//
// Duas camadas, ambas cadastrais:
//   C1 — INFRAESTRUTURA: dinheiro, moedas, identidade, write gate, validações
//        base, fail-closed de schema.
//   C2 — MODELO CADASTRAL: Instrument, Asset, Account, CashAccount — identidade
//        e ciclo cadastral. UI fica no C3.
// NENHUM ato econômico: sem transação, valuation, preço, holding, posição,
// cost basis, performance; nenhuma integração com Trading, Finanças Pessoais ou
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
const ALD_SUPPORTED_SCHEMA_VERSION = 2;

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
  const logAntes = (S.dataGovernance && Array.isArray(S.dataGovernance.changeLog)) ? S.dataGovernance.changeLog.length : null;
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
    if(logAntes!==null && S.dataGovernance.changeLog.length>logAntes) S.dataGovernance.changeLog.length = logAntes;
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
  };
}
