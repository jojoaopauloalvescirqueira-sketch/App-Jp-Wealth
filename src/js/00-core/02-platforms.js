// ============ PLATAFORMAS (fonte central para contas) ============
const TRADING_PLATFORMS=[
  {key:'mt5', name:'MetaTrader 5', aliases:['MT5','MetaTrader5','Meta Trader 5']},
  {key:'mt4', name:'MetaTrader 4', aliases:['MT4','MetaTrader4','Meta Trader 4']},
  {key:'ninjatrader', name:'NinjaTrader', aliases:['Ninja Trader','NT','NT8']},
];
function platformNorm(v){ return String(v||'').toLowerCase().replace(/[^a-z0-9]/g,''); }
function platformFor(v){
  const n=platformNorm(v);
  if(!n) return null;
  return TRADING_PLATFORMS.find(p=>platformNorm(p.key)===n || platformNorm(p.name)===n || (p.aliases||[]).some(a=>platformNorm(a)===n))||null;
}
function normalizePlatformName(v){
  const p=platformFor(v);
  return p?p.name:String(v||'');
}
const ACCOUNT_CURRENCIES=['USD','EUR','BRL','GBP','CHF'];
function normalizeAccountCurrency(v){
  const n=String(v||'').trim().toUpperCase();
  return ACCOUNT_CURRENCIES.includes(n) ? n : 'USD';
}
function accountCurrencyOptions(current){
  const cur=normalizeAccountCurrency(current);
  return ACCOUNT_CURRENCIES.map(c=>`<option value="${c}" ${cur===c?'selected':''}>${c}</option>`).join('');
}
function platformOptions(current){
  const cur=String(current||'');
  const known=platformFor(cur);
  const legacy=cur && !known ? `<option value="${esc(cur)}" selected>${esc(cur)} · a preencher</option>` : '';
  return `${legacy}<option value="" ${!cur?'selected':''}>a preencher</option>`+
    TRADING_PLATFORMS.map(p=>`<option value="${esc(p.name)}" ${known&&known.key===p.key?'selected':''}>${esc(p.name)}</option>`).join('');
}
