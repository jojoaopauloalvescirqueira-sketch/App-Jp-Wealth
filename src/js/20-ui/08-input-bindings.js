// Legacy controls remain discoverable, but the current engine only accepts
// explicit observations/proposals through its command boundary.
function bindParams(){
  for(const id of ['pSaldoIni','pSaldoAtu','pInicio','pMDD','pAlarm','pGenLev','pGenRisk','pFW','pVrmN','pVrmHV','pRefM','pRefA','iAtr55','iAtr660']){
    const input=$(id);if(!input)continue;input.readOnly=true;
    input.title='Registro explícito em Configurações → Operação → Parâmetros. Não altera norma a cada tecla.';
  }
  $('mExpAlvo').addEventListener('input',e=>{S.expAlvo=parseFloat(e.target.value)||0;save();renderMotor();});
  $('cLoteMaster').addEventListener('input',e=>{S.loteMaster=parseFloat(e.target.value)||0;save();renderAplicacao();});
  $('addAccountBtn')?.addEventListener('click',()=>{
    JPWFXConsolidated.openAccountRegistration({trigger:$('addAccountBtn')});
  });
}
