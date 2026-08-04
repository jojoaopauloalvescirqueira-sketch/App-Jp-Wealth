// ============ INPUT BINDINGS ============
function bindParams(){
  const map={pSaldoIni:'saldoIni',pSaldoAtu:'saldoAtu',pInicio:'inicio',pMDD:'mdd',pAlarm:'alarm',
    pGenLev:'genLev',pGenRisk:'genRisk',pFW:'fw',pVrmN:'vrmN',pVrmHV:'vrmHV',pRefM:'refM',pRefA:'refA'};
  const pctInputs=new Set(['pMDD','pAlarm','pGenRisk','pFW','pRefM','pRefA']);
  const derivados=new Set(['pFW','pRefM','pRefA']); // derivados do perfil ativo — não editáveis à mão
  for(const id in map){
    const el=$(id); if(!el)continue;
    if(derivados.has(id)){ el.disabled=true; el.title='Derivado do perfil ativo — ajuste trocando o perfil em 07 Contabilidade'; continue; }
    el.addEventListener('input',()=>{
      const key=map[id];
      S.params[key] = id==='pInicio'?el.value:(pctInputs.has(id)?percentInputToDecimal(el.value):(parseFloat(el.value)||0));
      save(); render(); renderParams(); renderMotor(); renderContas(); renderDash(); renderPhases(); renderLedger();
    });
  }
  $('iAtr55').addEventListener('input',e=>{S.atr55=parseFloat(e.target.value)||0; save(); render();});
  $('iAtr660').addEventListener('input',e=>{S.atr660=parseFloat(e.target.value)||0; save(); render();});
  $('mExpAlvo').addEventListener('input',e=>{S.expAlvo=parseFloat(e.target.value)||0; save(); renderMotor();});
  $('cLoteMaster').addEventListener('input',e=>{S.loteMaster=parseFloat(e.target.value)||0; save(); renderAplicacao();});
  $('addAccountBtn').addEventListener('click',()=>{
    S.accounts.push({nome:'Nova Conta',tipo:'SATÉLITE',broker:'',platform:'',platformLogin:'',investorPassword:'',perfil:'',perfilLocked:false,sini:0,satu:0});
    save(); renderContas();
    // foca no nome da nova linha
    const rows=document.querySelectorAll('#contasBody tr');
    const last=rows[rows.length-1];
    if(last) last.querySelector('input[data-f="nome"]').focus();
  });
}
