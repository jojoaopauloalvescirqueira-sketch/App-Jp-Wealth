// ============ 07 CONTABILIDADE — fechamento diário, Real vs Projetado, log de auditoria ============
function ledgerSorted(){ return [...S.ledger].sort((a,b)=>a.data<b.data?-1:1); }
function archiveCurrentLedgerForNewPeriod(nextPeriodMeta){
  const led=ledgerSorted();
  if(!led.length) return null;
  if(!Array.isArray(S.ledgerArchive)) S.ledgerArchive=[];
  const snapshot={
    archivedAt:new Date().toISOString(),
    previousInicio:S.params&&S.params.inicio||'',
    previousSaldoIni:S.params&&S.params.saldoIni||0,
    previousSaldoAtu:S.params&&S.params.saldoAtu||0,
    previousProfile:S.period&&S.period.profile||'base',
    count:led.length,
    firstDay:led[0].data||'',
    lastDay:led[led.length-1].data||'',
    nextPeriodMeta:structuredClone(nextPeriodMeta||{}),
    ledger:structuredClone(led)
  };
  S.ledgerArchive.push(snapshot);
  S.ledger=[];
  S.transitionLog.push({fase:'arquivamento de ledger', ts:snapshot.archivedAt,
    resumo:{motivo:'reinício de período', previousInicio:snapshot.previousInicio,
      previousSaldoIni:snapshot.previousSaldoIni, previousSaldoAtu:snapshot.previousSaldoAtu,
      previousProfile:snapshot.previousProfile, count:snapshot.count,
      firstDay:snapshot.firstDay, lastDay:snapshot.lastDay,
      nextInicio:snapshot.nextPeriodMeta.inicio||'', nextSaldoIni:snapshot.nextPeriodMeta.saldoIni||0,
      nextProfile:snapshot.nextPeriodMeta.profile||''}});
  return snapshot;
}
function syncSaldoAtuFromLedger(){
  const led=ledgerSorted();
  S.params.saldoAtu = led.length ? (+led[led.length-1].saldo||0) : (+S.params.saldoIni||0);
  return S.params.saldoAtu;
}
function renderLedger(){
  const dEl=$('ldDate'); if(dEl && !dEl.value) dEl.value=todayISO();
  const tb=$('ledgerBody'); if(!tb) return;
  const led=ledgerSorted();
  tb.innerHTML=[...led].reverse().map(e=>{
    const i=S.ledger.indexOf(e);
    const dd=S.params.saldoIni>0?Math.max(0,(S.params.saldoIni-e.saldo)/S.params.saldoIni):0;
    return `<tr>
      <td class="hl">${esc(e.data)}</td>
      <td class="${e.resultado>=0?'pos':'neg'}">${fmtMoney2(e.resultado)}</td>
      <td>${fmtMoney2(e.saldo)}</td>
      <td class="${dd>0?'neg':'muted'}">${dd>0?fmtPct(dd):'—'}</td>
      <td class="muted">${esc(e.nota||'')}</td>
      <td><button class="row-del" data-ldel="${i}" title="Remover lançamento">✕</button></td>
    </tr>`;
  }).join('');
  tb.querySelectorAll('[data-ldel]').forEach(b=>b.addEventListener('click',()=>{
    const i=+b.dataset.ldel;
    if(confirm('Remover o lançamento de '+S.ledger[i].data+'?')){
      S.ledger.splice(i,1); syncSaldoAtuFromLedger(); save(); renderLedger(); renderDash(); renderParams(); render();
    }
  }));
  renderAcct();
  renderAuditLog();
}
function renderAuditLog(){
  const box=$('auditLogBox'); if(!box) return;
  const items=[];
  S.transitionLog.forEach(t=>{
    const quando=String(t.ts||'').replace('T',' ').slice(0,16);
    items.push(`<b style="color:var(--ink)">[${quando}]</b> ${esc(String(t.fase))} — ${esc(JSON.stringify(t.resumo))}`);
  });
  if(S.quarantine) items.push(`<b style="color:var(--danger)">QUARENTENA</b> de ${S.quarantine.inicio} até ${S.quarantine.fim}${quarantineActive()?' (ATIVA)':' (encerrada)'}`);
  if(S.protocolBreaches>0) items.push(`<b style="color:var(--danger)">${S.protocolBreaches} rompimento(s) de protocolo</b> registrados no ciclo`);
  S.phases.forEach(ph=>ph.orders.forEach(o=>{
    if(o.divergenceReason) items.push(`Divergência <b>${esc(o.id||'?')}</b>: ${esc(o.divergenceReason)}`);
  }));
  box.innerHTML=items.length?items.map(i=>`<div>· ${i}</div>`).join(''):'<span class="muted">Nenhum evento registrado neste ciclo.</span>';
}
function exportAudit(){
  const contasSemSegredo=S.accounts.map(a=>({...a, investorPassword: a.investorPassword?'••• (removida da exportação)':''}));
  const payload={
    exportadoEm:new Date().toISOString(), versao:'V9.1',
    params:S.params, cycleRealizado:S.cycleRealizado, quarantine:S.quarantine,
    protocolBreaches:S.protocolBreaches, transitionLog:S.transitionLog,
    ledger:ledgerSorted(), fases:S.phases, contas:contasSemSegredo,
  };
  const blob=new Blob([JSON.stringify(payload,null,2)],{type:'application/json'});
  const a=document.createElement('a');
  a.href=URL.createObjectURL(blob);
  a.download='jpwealth_auditoria_'+todayISO()+'.json';
  a.click();
  URL.revokeObjectURL(a.href);
}
function exportFullBackup(){
  const incluirSegredos=confirm('Incluir as SENHAS DE INVESTIDOR das contas neste backup?\n\nOK = inclui (arquivo com segredos em texto puro — guarde offline).\nCancelar = exporta sem senhas (mais seguro).');
  const exportadoEm=new Date().toISOString();
  let stateExport=S;
  if(!incluirSegredos){
    stateExport=structuredClone(S);
    if(Array.isArray(stateExport.accounts)) stateExport.accounts.forEach(a=>{ a.investorPassword=''; });
    if(stateExport.onboarding) stateExport.onboarding.investorPassword=''; // senha de investidor do onboarding também é segredo
  }
  const payload={
    tipo:'jpwealth_full_backup',
    versao:'V9.1',
    localStorageKey:LSKEY,
    exportadoEm,
    dataLocal:todayISO(),
    segredosIncluidos:incluirSegredos,
    state:stateExport,
  };
  const blob=new Blob([JSON.stringify(payload,null,2)],{type:'application/json'});
  const a=document.createElement('a');
  a.href=URL.createObjectURL(blob);
  a.download='jpwealth_backup_completo_'+todayISO()+'.json';
  a.click();
  URL.revokeObjectURL(a.href);
  return {filename:a.download,exportedAt:exportadoEm,segredosIncluidos:incluirSegredos};
}
function normalizeImportedState(raw){
  if(!raw || typeof raw!=='object' || Array.isArray(raw)) throw new Error('JSON inválido: raiz precisa ser um objeto.');
  const candidate = raw.state && typeof raw.state==='object' ? raw.state : raw;
  if(!candidate || typeof candidate!=='object' || Array.isArray(candidate)) throw new Error('Backup sem objeto de estado.');
  if(!candidate.params || typeof candidate.params!=='object') throw new Error('Backup sem params.');
  if(candidate.ledger && !Array.isArray(candidate.ledger)) throw new Error('Backup com ledger inválido.');
  if(candidate.ledgerArchive && !Array.isArray(candidate.ledgerArchive)) throw new Error('Backup com ledgerArchive inválido.');
  if(candidate.phases && !Array.isArray(candidate.phases)) throw new Error('Backup com phases inválido.');
  const current=S;
  let imported;
  try{
    S=structuredClone(candidate);
    migrate();
    syncSaldoAtuFromLedger();
    imported=structuredClone(S);
  }finally{
    S=current;
  }
  return imported;
}
function importFullBackupFile(file){
  if(!file) return;
  if(jpWealthPersistenceIsBlocked()) resumeJPWealthPersistence();
  const requestEpoch=jpWealthPersistenceEpoch();
  const reader=new FileReader();
  reader.onload=()=>{
    if(jpWealthPersistenceIsBlocked() || requestEpoch!==jpWealthPersistenceEpoch()) return;
    let imported;
    try{
      imported=normalizeImportedState(JSON.parse(String(reader.result||'')));
    }catch(e){
      alert('Backup inválido: '+(e&&e.message?e.message:'não foi possível ler o JSON.'));
      return;
    }
    if(!confirm('Importar backup completo e sobrescrever o estado atual deste navegador?')) return;
    if(jpWealthPersistenceIsBlocked() || requestEpoch!==jpWealthPersistenceEpoch()) return;
    S=imported;
    save();
    if(typeof markSessionCheckpoint==='function') markSessionCheckpoint();
    boot();
    alert('Backup importado com sucesso.');
  };
  reader.onerror=()=>alert('Não foi possível ler o arquivo de backup.');
  reader.readAsText(file);
}
