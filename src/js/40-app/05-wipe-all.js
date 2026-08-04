// ============ LIMPEZA TOTAL — dupla confirmação digitando APAGAR (SET 6) ============
function wipeAllData(){
  const p1=prompt('⚠️ Isto apaga TODOS os dados (ordens, fases, fechamentos, auditoria, configurações).\n\nDigite APAGAR para continuar:');
  if(p1===null) return;
  if(p1.trim()!=='APAGAR'){ alert('Texto diferente de APAGAR — nada foi apagado.'); return; }
  const p2=prompt('Última confirmação. Digite APAGAR novamente:');
  if(p2===null) return;
  if(p2.trim()!=='APAGAR'){ alert('Texto diferente de APAGAR — nada foi apagado.'); return; }
  const cleared=clearJPWealthLocalData({removeAuxiliary:false,removeCorrupted:false});
  if(!cleared.ok){ alert('Não foi possível limpar a chave principal: '+cleared.failures.join(', ')); return; }
  S=structuredClone(DEFAULTS);
  window.__onbShown=false; // painel voltou ao início → questionário de início deve reaparecer
  boot();
  alert('Dados apagados. O painel voltou ao estado inicial.');
}
function bindConfig(){
  document.querySelectorAll('#themeSeg button').forEach(b=>b.addEventListener('click',()=>{
    S.theme=b.dataset.themeVal; applyTheme(); renderThemeSeg(); save();
  }));
  bindFsSeg(); bindExplSeg();
  const eb=$('exportFullBackupBtn');
  if(eb) eb.addEventListener('click', exportFullBackup);
  const ib=$('importFullBackupBtn'), ii=$('importFullBackupInput');
  if(ib && ii){
    ib.addEventListener('click',()=>ii.click());
    ii.addEventListener('change',()=>{
      importFullBackupFile(ii.files&&ii.files[0]);
      ii.value='';
    });
  }
  const wb=$('wipeAllBtn');
  if(wb) wb.addEventListener('click', wipeAllData);
  const qc=$('quarantineConfirmBtn');
  if(qc) qc.addEventListener('click',()=>{
    if(!confirm(`Formalizar o Encerramento Compulsório e iniciar a Quarentena de 90 dias (Art. 3.10)? Faça isto apenas se o drawdown de ${fmtPct(activeMDDLimit())} for real.`)) return;
    const hoje=todayISO(), fim=addDaysISO(90);
    S.quarantine={inicio:hoje,fim};
    S.transitionLog.push({fase:'quarentena', ts:new Date().toISOString(), resumo:{motivo:'Encerramento compulsório formalizado', inicio:hoje, fim}});
    save(); render(); renderPhases(); renderConfigQuarantine();
  });
}
