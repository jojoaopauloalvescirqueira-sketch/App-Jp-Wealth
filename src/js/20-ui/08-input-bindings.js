// Legacy controls remain discoverable, but the current engine only accepts
// explicit observations/proposals through its command boundary.
function bindParams(){
  for(const id of ['pSaldoIni','pSaldoAtu','pInicio','pMDD','pAlarm','pGenLev','pGenRisk','pFW','pVrmN','pVrmHV','pRefM','pRefA','iAtr55','iAtr660']){
    const input=$(id);if(!input)continue;input.readOnly=true;
    input.title='Registro explícito em Configurações → Operação → Parâmetros. Não altera norma a cada tecla.';
  }
  $('mExpAlvo').addEventListener('input',e=>{S.expAlvo=parseFloat(e.target.value)||0;save();renderMotor();});
  $('cLoteMaster').addEventListener('input',e=>{S.loteMaster=parseFloat(e.target.value)||0;save();renderAplicacao();});
  $('addAccountBtn').addEventListener('click',()=>{
    const result=JPWForex.state.mutate('account-create','Criação explícita de cadastro de conta',['accounts'],()=>{
      S.accounts.push({nome:'Nova Conta',tipo:'SATÉLITE',broker:'',platform:'',platformLogin:'',investorPassword:'',perfil:'',perfilLocked:false,sini:0,satu:0});
    });
    if(!result.ok){alert(result.error);return;}
    if(typeof accountEditorsOpen!=='undefined')accountEditorsOpen.add(S.accounts.length-1);
    renderContas();const input=document.querySelector(`#contasBody .account-detail-row[data-idx="${S.accounts.length-1}"] input[data-f="nome"]`);if(input)input.focus();
  });
}
