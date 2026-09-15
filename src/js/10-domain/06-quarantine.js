// Quarantine remains a factual restriction. P-24 does not supply a release date.
function renderConfigQuarantine(){
  const el=$('configQuarantine');if(!el)return;
  if(S.quarantine){
    el.innerHTML='<p>Quarentena registrada: '+esc(S.quarantine.inicio||'data não informada')+'. Prazo e liberação dependem da autoridade normativa; uma data antiga não autoriza retorno.</p><p>Correções do registro exigem preservar sua trilha. O registro de fatos continua disponível.</p>';
  }else{
    el.innerHTML='<p>Nenhuma quarentena registrada. Atingir DD_MAX produz a indicação de encerramento compulsório no motor. P-24 permanece pendente, sem prazo automático.</p>';
  }
}
