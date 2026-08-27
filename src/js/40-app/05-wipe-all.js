// ============ LIMPEZA TOTAL — dupla confirmação digitando APAGAR (SET 6) ============
function wipeAllData(){
  // Guarda de entrada A-005: em modo de recuperação, a limpeza total é interrompida antes
  // do primeiro prompt — "Começar com base vazia" (no aviso do topo) é o equivalente
  // legítimo desta ação enquanto o banco original estiver protegido.
  if(typeof jpWealthLoadRecoveryActive==='function' && jpWealthLoadRecoveryActive()){
    alert('O banco de dados está em modo de recuperação e as gravações estão bloqueadas.\n\nUse o aviso no topo da tela: baixe a cópia de recuperação, restaure um backup válido ou escolha "Começar com base vazia" — esta última equivale à limpeza total.');
    return;
  }
  // A-004: os textos declaram exatamente o que esta função faz — apaga a base inteira do
  // JP Wealth (removeAuxiliary:false preserva as preferências locais de interface;
  // removeCorrupted:false preserva cópias de recuperação existentes). Texto e
  // comportamento precisam coincidir numa ação irreversível.
  const p1=prompt('⚠️ Isto apaga TODA a base do JP Wealth deste navegador: ordens, fases, fechamentos, auditoria, configurações e tickets. A ação é irreversível.\n\nPreferências locais de interface (escala da fonte, estado da navegação, ícone do app) são preservadas, e cópias de recuperação existentes não são apagadas.\n\nDigite APAGAR para continuar:');
  if(p1===null) return;
  if(p1.trim()!=='APAGAR'){ alert('Texto diferente de APAGAR — nada foi apagado.'); return; }
  const p2=prompt('Última confirmação. Digite APAGAR novamente:');
  if(p2===null) return;
  if(p2.trim()!=='APAGAR'){ alert('Texto diferente de APAGAR — nada foi apagado.'); return; }
  // JPW-FX-WIPE-RACE: invalida a GERAÇÃO da persistência antes de destruir a base.
  // Operações assíncronas iniciadas antes daqui já capturam jpWealthPersistenceEpoch()
  // e o conferem depois do await (updateFxRates é o caso real) — mas a Zona de Perigo
  // era o único fluxo destrutivo que não incrementava o epoch, então o guard comparava
  // a MESMA geração, passava, e a continuação regravava a chave recém-apagada.
  // Finalizar Sessão (local e vinda de outra aba) já fazia isto; aqui só se equipara.
  // ALD-C3-PRE-EPOCH: a nova geração é firmada ANTES de qualquer mutação destrutiva.
  // Se rotacionar e a limpeza falhar depois, fica uma geração nova sobre a base antiga
  // — invalida mensagens pendentes e não destrói nada. O inverso seria inaceitável:
  // base nova protegida pela geração antiga deixaria uma finalização pendente atuar
  // sobre ela. Falhando a rotação, NADA é apagado.
  const novaEpoch=(typeof sessionEpochRotate==='function')?sessionEpochRotate():null;
  if(!novaEpoch){
    alert('Não foi possível estabelecer uma nova geração da base neste navegador. Nada foi apagado — recarregue a página e tente novamente.');
    return;
  }
  blockJPWealthPersistence();
  const cleared=clearJPWealthLocalData({removeAuxiliary:false,removeCorrupted:false});
  if(!cleared.ok){
    // Nada foi apagado: devolve a persistência ao operador exatamente como estava.
    resumeJPWealthPersistence();
    alert('Não foi possível limpar a chave principal: '+cleared.failures.join(', '));
    return;
  }
  S=structuredClone(DEFAULTS);
  // Geração nova: o que for iniciado a partir daqui pode gravar normalmente. O par
  // block+resume deixa o epoch duas casas à frente, então nenhuma continuação da
  // geração anterior volta a casar.
  resumeJPWealthPersistence();
  // O epoch só protege ESTA aba. Outra aba aberta mantém o S completo em memória e
  // ressuscitaria a base inteira na primeira gravação — a exclusão precisa atravessar
  // as abas para ser exclusão. Mesmo canal da Finalização de Sessão, com semântica
  // própria (auxiliares e cópias de recuperação preservadas).
  if(typeof sessionNotifyBaseWiped==='function') sessionNotifyBaseWiped(novaEpoch);
  // JPW-HJFGDE §17: a base morreu — a autorização local da pasta de exportação morre
  // junto. Fire-and-forget: sem metadados o handle já seria inerte; limpar evita órfão.
  if(typeof dgFsClearHandle==='function') dgFsClearHandle();
  window.__onbShown=false; // painel voltou ao início → questionário de início deve reaparecer
  boot();
  // §12: base excluída → tela inicial canônica (DEFAULT_START_ROUTE), nunca a tela em
  // que o operador por acaso estava quando confirmou a limpeza.
  if(typeof navigateToScreen==='function' && typeof DEFAULT_START_ROUTE!=='undefined') navigateToScreen(DEFAULT_START_ROUTE);
  alert('A base do JP Wealth foi apagada e o painel voltou ao estado inicial. Preferências locais de interface e cópias de recuperação existentes foram preservadas.');
}
function bindConfig(){
  document.querySelectorAll('#themeSeg button').forEach(b=>b.addEventListener('click',()=>{
    S.theme=b.dataset.themeVal; applyTheme(); renderThemeSeg(); save();
  }));
  bindFsSeg(); bindExplSeg(); bindNavStyleSeg();
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
    // auditoria resumida da base (JPW-HJFGDE §11) — o transitionLog acima segue sendo o
    // registro normativo; esta linha só alimenta "alterações desde o último backup".
    if(typeof dgLogChange==='function') dgLogChange('quarantine','created','','Quarentena operacional formalizada ('+hoje+' → '+fim+')');
    save(); render(); renderPhases(); renderConfigQuarantine();
  });
}
