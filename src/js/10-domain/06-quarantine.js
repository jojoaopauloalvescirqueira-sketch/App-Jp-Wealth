// ============ Configurações · quarentena reversível (SET 5a) ============
function renderConfigQuarantine(){
  const el=$('configQuarantine'); if(!el) return;
  if(S.quarantine){
    const ativa=quarantineActive();
    el.innerHTML=`<p style="font-size:calc(13px * var(--fs-scale));color:var(--ink-dim);line-height:1.6;margin-bottom:12px">
      Quarentena ${ativa?'<b style="color:var(--danger)">ativa</b>':'expirada'} — início ${S.quarantine.inicio}, fim ${S.quarantine.fim}.</p>
      <button class="reset-btn" id="clearQuarantineBtn">Limpar quarentena / aviso</button>`;
    $('clearQuarantineBtn').addEventListener('click',()=>{
      if(confirm('Limpar o registro de quarentena? Use isto se o aviso surgiu de erro de preenchimento, não de um encerramento real.')){
        S.quarantine=null; save(); render(); renderPhases(); renderConfigQuarantine();
      }
    });
  } else {
    el.innerHTML=`<p style="font-size:calc(13px * var(--fs-scale));color:var(--ink-dim);line-height:1.6">Nenhuma quarentena registrada. O aviso de guilhotina só aparece enquanto o drawdown real estiver ≥ ${fmtPct(activeMDDLimit())} — e some sozinho se corrigido. A quarentena de 90 dias só é gravada quando você a formaliza deliberadamente.</p>`;
  }
}
