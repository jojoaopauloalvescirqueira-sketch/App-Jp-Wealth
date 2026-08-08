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
      const dataRemovida=S.ledger[i].data;
      S.ledger.splice(i,1); syncSaldoAtuFromLedger();
      if(typeof dgLogChange==='function') dgLogChange('ledger','deleted',dataRemovida,'Fechamento diário removido ('+dataRemovida+')');
      save(); renderLedger(); renderDash(); renderParams(); render();
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
// ---- Exportação da base (JPW-HJFGDE) ---------------------------------------------
// Política de senhas de investidor: perguntada UMA vez por exportação, antes de resolver
// o destino. Separada da montagem do arquivo porque o nome definitivo só é conhecido
// depois da sondagem de colisão — e o operador não deve ser perguntado duas vezes.
function dgAskIncludeSecrets(){
  return confirm('Incluir as SENHAS DE INVESTIDOR das contas neste backup?\n\nOK = inclui (arquivo com segredos em texto puro — guarde offline).\nCancelar = exporta sem senhas (mais seguro).');
}
// Monta o arquivo do backup completo. O ENVELOPE é formato normativo e não muda aqui:
// {tipo, versao, localStorageKey, exportadoEm, dataLocal, segredosIncluidos, state}.
//
// AUTOIDENTIFICAÇÃO (FAIL-04): o snapshot gravado declara a PRÓPRIA exportação. Antes,
// o payload era uma fotografia do estado ANTERIOR ao incremento — o arquivo 000010
// carregava por dentro lastSequence=9, e restaurá-lo fazia a base reemitir o 000010.
// A colisão física só mascarava isso quando o arquivo original estivesse na mesma pasta;
// em máquina nova, pasta vazia ou no fallback Downloads não há sondagem, e o número
// saía duplicado. A sondagem é defesa adicional, nunca o mecanismo de continuidade.
//
// A identidade é escrita numa CÓPIA (structuredClone), nunca no objeto vivo: se a
// gravação falhar, não há o que reverter — o estado em memória jamais foi tocado.
function dgBuildBackupBlob(incluirSegredos, seq, filename, exportadoEm){
  const stateExport=structuredClone(S);
  if(!incluirSegredos){
    if(Array.isArray(stateExport.accounts)) stateExport.accounts.forEach(a=>{ a.investorPassword=''; });
    if(stateExport.onboarding) stateExport.onboarding.investorPassword=''; // senha de investidor do onboarding também é segredo
  }
  if(stateExport.dataGovernance && stateExport.dataGovernance.export){
    stateExport.dataGovernance.export.lastSequence=seq;
    stateExport.dataGovernance.export.lastExportFile=filename;
    stateExport.dataGovernance.export.lastExportAt=exportadoEm;
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
  return new Blob([JSON.stringify(payload,null,2)],{type:'application/json'});
}
// Download tradicional (fallback §15 e escolha excepcional §7). Padrão endurecido:
// âncora no DOM e revogação adiada — revogar de forma síncrona após click() corta o
// download em alguns navegadores.
function dgDownloadViaAnchor(filename,blob){
  const a=document.createElement('a');
  a.href=URL.createObjectURL(blob);
  a.download=filename;
  document.body.appendChild(a);
  a.click();
  setTimeout(()=>{ URL.revokeObjectURL(a.href); if(a.parentNode) a.remove(); },0);
}
// Sucesso confirmado → e SÓ então o estado avança (§8.2): sequência, carimbo, arquivo,
// changeLog e gravação. Uma exportação que falhou não deixa rastro de sucesso.
function dgRegisterExportSuccess(seq,filename,exportadoEm,destino){
  S.dataGovernance.export.lastSequence=seq;
  S.dataGovernance.export.lastExportAt=exportadoEm;
  S.dataGovernance.export.lastExportFile=filename;
  if(typeof dgLogChange==='function') dgLogChange('database','exported',filename,
    destino==='folder'?'Base exportada para a pasta padrão':'Base exportada via download do navegador');
  save();
  // mantém o cartão da Central em dia (guardas: a UI carrega depois deste script)
  if(typeof renderDgStorageCard==='function') renderDgStorageCard();
}
// Exportação completa da base — agora async e orquestrada (JPW-HJFGDE §14).
// Retorna meta {filename, exportedAt, segredosIncluidos, destination} em sucesso;
// null quando nada foi exportado (cancelamento ou falha já explicada ao operador).
// NUNCA lança e NUNCA faz fallback silencioso para Downloads (§7): se a pasta
// configurada está inacessível, o operador decide — reautorizar, trocar de pasta ou
// exportar excepcionalmente para Downloads, por escolha explícita.
// opts.quiet: suprime o alert de sucesso (o fluxo chamador mostra a própria confirmação).
// GUARDA DE REENTRÂNCIA (caça a bugs 2026-08-08): duas execuções simultâneas (duplo
// clique) liam a MESMA lastSequence antes de qualquer registro e, no caminho pasta —
// onde há awaits reais entre a sondagem de colisão e a gravação —, produziam o mesmo
// nome de arquivo: a segunda gravação sobrescrevia a primeira, violando o §8.3.
// Serializar por recusa é a correção honesta: a segunda tentativa não exporta nada,
// diz o porquê, e nenhum estado é tocado.
let dgExportEmAndamento=false;
async function exportFullBackup(opts){
  const quiet=!!(opts&&opts.quiet);
  if(dgExportEmAndamento){
    alert('Já existe uma exportação da base em andamento — aguarde ela terminar antes de iniciar outra.');
    return null;
  }
  dgExportEmAndamento=true;
  try{
    return await dgExportFullBackupInner(quiet);
  }finally{
    dgExportEmAndamento=false;
  }
}
async function dgExportFullBackupInner(quiet){
  try{
    // A pergunta sobre segredos vem primeiro e vale para toda a operação; o ARQUIVO só
    // é montado quando sequência e nome forem definitivos (autoidentificação, FAIL-04).
    const segredosIncluidos=dgAskIncludeSecrets();
    const exportadoEm=new Date().toISOString();
    const baseSeq=(S.dataGovernance&&S.dataGovernance.export&&S.dataGovernance.export.lastSequence)||0;
    const supported=typeof dgFsSupported==='function' && dgFsSupported();
    const configured=!!(S.dataGovernance&&S.dataGovernance.storage&&S.dataGovernance.storage.configured);
    // Caminho tradicional: navegador sem suporte, ou pasta nunca configurada. Não é o
    // fallback do §7 (não há pasta prometida sendo ignorada) — é o único caminho que
    // existe, com a nomenclatura progressiva preservada. O navegador ainda pode sufixar
    // " (1)" em colisão dentro de Downloads; nunca sobrescreve (comportamento nativo).
    if(!supported || !configured){
      const seq=baseSeq+1;
      const filename=dgExportFileName(seq,new Date());
      dgDownloadViaAnchor(filename,dgBuildBackupBlob(segredosIncluidos,seq,filename,exportadoEm));
      dgRegisterExportSuccess(seq,filename,exportadoEm,'downloads');
      if(!quiet) alert('Base exportada via download do navegador:\n\n'+filename+(supported?'':'\n\nEste navegador não suporta pasta persistente (File System Access API) — as exportações usam o mecanismo padrão de download.'));
      return {filename,sequence:seq,exportedAt:exportadoEm,segredosIncluidos,destination:'downloads'};
    }
    // Pasta configurada: resolver acesso. Enquanto o operador não resolver (ou optar por
    // Downloads explicitamente), NENHUM arquivo é gerado.
    let {state,handle}=await dgFsStatus();
    for(;;){
      if(state==='authorized'){
        // nome progressivo com proteção física de colisão (§8.3): nunca sobrescrever;
        // em colisão a sequência avança até nome livre (teto de 1000 é rede de segurança)
        let seq=baseSeq+1, filename=dgExportFileName(seq,new Date());
        try{
          let guard=0;
          while(await dgFsFileExists(handle,filename)){
            seq++; filename=dgExportFileName(seq,new Date());
            if(++guard>1000) throw new Error('Não foi possível encontrar um nome de arquivo livre na pasta.');
          }
          // nome definitivo (pós-colisão) → só AGORA o arquivo é montado, já se
          // autoidentificando com esta sequência e este nome
          await dgFsWriteFile(handle,filename,dgBuildBackupBlob(segredosIncluidos,seq,filename,exportadoEm));
          dgRegisterExportSuccess(seq,filename,exportadoEm,'folder');
          if(!quiet) alert('Base exportada para a pasta padrão "'+(S.dataGovernance.storage.folderDisplayPath||handle.name)+'":\n\n'+filename);
          return {filename,sequence:seq,exportedAt:exportadoEm,segredosIncluidos,destination:'folder'};
        }catch(e){
          state='invalid'; // pasta removida/ilegível no meio do caminho — cai no diálogo abaixo
        }
        continue;
      }
      // prompt | denied | missing | invalid → decisão explícita do operador (§7).
      // O diálogo vive em 40-app/16-storage-governance.js; sem ele (geometria degenerada
      // de carregamento) não há como decidir — e decidir por Downloads em silêncio é
      // exatamente o que o ticket proíbe.
      if(typeof dgExportRecoveryDialog!=='function'){
        alert('Não foi possível acessar a pasta padrão da base de dados.\n\nNenhum arquivo foi exportado. Abra Configurações → Dados e Segurança → Backup e Recuperação para reautorizar ou trocar a pasta.');
        return null;
      }
      const decision=await dgExportRecoveryDialog(state);
      if(decision==='downloads'){
        const seq=baseSeq+1;
        const filename=dgExportFileName(seq,new Date());
        dgDownloadViaAnchor(filename,dgBuildBackupBlob(segredosIncluidos,seq,filename,exportadoEm));
        dgRegisterExportSuccess(seq,filename,exportadoEm,'downloads');
        if(!quiet) alert('Base exportada excepcionalmente via download do navegador:\n\n'+filename+'\n\nA pasta padrão continua configurada e precisando de atenção.');
        return {filename,sequence:seq,exportedAt:exportadoEm,segredosIncluidos,destination:'downloads-exception'};
      }
      if(decision==='retry'){ ({state,handle}=await dgFsStatus()); continue; }
      return null; // cancelado — nada foi exportado e nada mudou
    }
  }catch(e){
    alert('A exportação não foi concluída: '+(e&&e.message?e.message:'erro inesperado.')+'\n\nNenhum estado de exportação foi alterado.');
    return null;
  }
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
    // Auditoria resumida (JPW-HJFGDE §11): a importação entra no changeLog DA BASE
    // IMPORTADA — é nela que o evento aconteceu e é ela que o próximo backup protege.
    if(typeof dgLogChange==='function') dgLogChange('database','imported',file.name||'','Importação de backup realizada');
    // Integração A-005: uma importação VALIDADA é decisão legítima de sair do modo de
    // recuperação — mas o desbloqueio só se consolida após gravação comprovada; se a
    // escrita falhar, o modo de recuperação continua e a chave principal fica intacta.
    const gravou=(typeof jpWealthResolveRecoveryAndSave==='function')?jpWealthResolveRecoveryAndSave():save();
    if(typeof markSessionCheckpoint==='function') markSessionCheckpoint();
    boot();
    alert(gravou?'Backup importado com sucesso.':'O backup foi lido e aplicado em memória, mas a gravação no armazenamento local falhou — exporte um backup e verifique o navegador antes de continuar.');
  };
  reader.onerror=()=>alert('Não foi possível ler o arquivo de backup.');
  reader.readAsText(file);
}
