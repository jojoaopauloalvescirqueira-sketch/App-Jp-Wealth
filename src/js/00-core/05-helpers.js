// ============ HELPERS ============
const $=id=>document.getElementById(id);
const fmtMoney=v=>'$'+Math.round(v).toLocaleString('pt-BR');
const fmtMoney2=v=>(v<0?'-$':'$')+Math.abs(v).toLocaleString('pt-BR',{minimumFractionDigits:2,maximumFractionDigits:2});
const fmtPct=v=>(v*100).toLocaleString('pt-BR',{minimumFractionDigits:2,maximumFractionDigits:2})+'%';
const pctText=v=>(Number.isFinite(v)?v:0).toFixed(1).replace('.',',')+'%'; // usado por renderConfigOnboarding (cobertura FCR/FEO) — precisa ser global, não só closure do onboarding
const fmtX=v=>v.toLocaleString('pt-BR',{minimumFractionDigits:1,maximumFractionDigits:2})+'x';
function decimalToPercentInput(v){
  const n=(parseFloat(v)||0)*100;
  return Number(n.toFixed(4)).toString();
}
function percentInputToDecimal(v){
  const n=parseFloat(String(v??'').replace('%','').replace(',','.'));
  return isFinite(n)?n/100:0;
}
function pctView(v){ return decimalToPercentInput(v)+'%'; }
const esc=s=>String(s??'').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;').replace(/'/g,'&#39;');
