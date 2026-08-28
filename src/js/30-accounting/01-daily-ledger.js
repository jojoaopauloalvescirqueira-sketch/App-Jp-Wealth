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
    items.push(`<b style="color:var(--ink)">[${esc(quando)}]</b> ${esc(String(t.fase))} — ${esc(JSON.stringify(t.resumo))}`);
  });
  if(S.quarantine) items.push(`<b style="color:var(--danger)">QUARENTENA</b> de ${esc(S.quarantine.inicio)} até ${esc(S.quarantine.fim)}${quarantineActive()?' (ATIVA)':' (encerrada)'}`);
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
// POLÍTICA DE SEGREDO: o backup NUNCA carrega senha de investidor — a antiga pergunta
// "incluir senhas?" foi removida junto com a opção que ela oferecia. O envelope mantém
// o campo segredosIncluidos (formato normativo) sempre em false.
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
// `estadoFonte` (opcional) — ALD-C3-PRE-PERSISTENCE: o backup oferecido como rede de
// segurança de um ato destrutivo deve representar o DOCUMENTO AUTORITATIVO persistido,
// não o S potencialmente obsoleto desta aba. O fluxo Finalizar Sessão passa o documento
// lido do disco na abertura; todos os outros usos mantêm o comportamento de sempre (S).
function dgBuildBackupBlob(seq, filename, exportadoEm, estadoFonte){
  const stateExport=structuredClone(estadoFonte||S);
  // Incondicional (política de segredo): não existe mais variante de backup com senha.
  if(Array.isArray(stateExport.accounts)) stateExport.accounts.forEach(a=>{ a.investorPassword=''; });
  if(stateExport.onboarding) stateExport.onboarding.investorPassword='';
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
    segredosIncluidos:false, // política de segredo: sempre sem senha
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
  const estadoFonte=(opts&&opts.estadoFonte)||null;
  if(dgExportEmAndamento){
    alert('Já existe uma exportação da base em andamento — aguarde ela terminar antes de iniciar outra.');
    return null;
  }
  dgExportEmAndamento=true;
  try{
    return await dgExportFullBackupInner(quiet,estadoFonte);
  }finally{
    dgExportEmAndamento=false;
  }
}
async function dgExportFullBackupInner(quiet,estadoFonte){
  try{
    // A pergunta sobre segredos vem primeiro e vale para toda a operação; o ARQUIVO só
    // é montado quando sequência e nome forem definitivos (autoidentificação, FAIL-04).
    const segredosIncluidos=false; // política de segredo: sem pergunta, sem variante com senha
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
      dgDownloadViaAnchor(filename,dgBuildBackupBlob(seq,filename,exportadoEm,estadoFonte));
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
          await dgFsWriteFile(handle,filename,dgBuildBackupBlob(seq,filename,exportadoEm,estadoFonte));
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
        dgDownloadViaAnchor(filename,dgBuildBackupBlob(seq,filename,exportadoEm,estadoFonte));
        dgRegisterExportSuccess(seq,filename,exportadoEm,'downloads');
        if(!quiet) alert('Base exportada excepcionalmente via download do navegador:\n\n'+filename+'\n\nA pasta padrão continua configurada e precisando de atenção.');
        return {filename,sequence:seq,exportedAt:exportadoEm,segredosIncluidos,destination:'downloads-exception'};
      }
      if(decision==='retry'){ ({state,handle}=await dgFsStatus()); continue; }
      return null; // cancelado — nada foi exportado e nada mudou
    }
  }catch(e){
    alert('A exportação não foi concluída: '+(e&&e.message?e.message:'erro inesperado.')+'\n\nNenhum estado de exportação foi alterado. Antes de fechar a página, anote manualmente os registros mais recentes (ordens, fechamentos e notas).');
    return null;
  }
}
function normalizeImportedState(raw){
  if(!raw || typeof raw!=='object' || Array.isArray(raw)) throw new Error('JSON inválido: raiz precisa ser um objeto.');
  const candidate = raw.state && typeof raw.state==='object' ? raw.state : raw;
  if(!candidate || typeof candidate!=='object' || Array.isArray(candidate)) throw new Error('Backup sem objeto de estado.');
  if(!candidate.params || typeof candidate.params!=='object' || Array.isArray(candidate.params)) throw new Error('Backup com params inválido.');
  if(candidate.ledger && !Array.isArray(candidate.ledger)) throw new Error('Backup com ledger inválido.');
  if(candidate.ledgerArchive && !Array.isArray(candidate.ledgerArchive)) throw new Error('Backup com ledgerArchive inválido.');
  if(candidate.phases && !Array.isArray(candidate.phases)) throw new Error('Backup com phases inválido.');
  // Agregados que os renderizadores percorrem com .map/.forEach SEM guarda de
  // forma em migrate(). Sem esta recusa, um backup com `checklist:{}` atravessava
  // validação e migração inteiras sem lançar, e a exceção só estourava em boot() —
  // DEPOIS de S=imported e da gravação no localStorage. A ordem era fatal: quando
  // o erro aparecia a base original já não existia, e como migrate() não lançara,
  // o modo de recuperação A-005 não entrava (sem cópia _corrompido_, sem bloqueio
  // de gravação, sem faixa de aviso) — o operador ficava com a tela em branco.
  // Recusar ANTES de tocar em qualquer coisa é o mesmo contrato transacional que
  // as quatro linhas acima já expressavam.
  for(const chave of ['checklist','accounts','instruments','profiles','ledgerArchive','transitionLog']){
    if(chave in candidate && candidate[chave]!=null && !Array.isArray(candidate[chave]))
      throw new Error('Backup com '+chave+' inválido: esperava lista.');
  }
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
  // TRANSACIONAL: nenhum portão muda antes de o candidato estar lido, validado,
  // normalizado E confirmado. A versão anterior chamava resumeJPWealthPersistence()
  // já na entrada — antes do FileReader — e um arquivo inválido deixava o portão
  // genérico reaberto mesmo com o modo de recuperação ainda ativo. O epoch capturado
  // aqui congela a legitimidade do pedido: se o operador resolver a recuperação (ou
  // outro fluxo mexer nos portões) entre escolher o arquivo e a leitura terminar,
  // este import deixa de representar uma decisão sobre o estado vigente e é abortado.
  const requestEpoch=jpWealthPersistenceEpoch();
  const reader=new FileReader();
  reader.onload=()=>{
    if(requestEpoch!==jpWealthPersistenceEpoch()) return;
    let imported;
    try{
      imported=normalizeImportedState(JSON.parse(String(reader.result||'')));
    }catch(e){
      // Falha ANTES da aplicação: estado, portões e modo de recuperação intactos.
      alert('Backup inválido: '+(e&&e.message?e.message:'não foi possível ler o JSON.')+'\n\nNada foi alterado: o estado atual e as proteções de gravação permanecem exatamente como estavam.');
      return;
    }
    if(!confirm('Importar backup completo e sobrescrever o estado atual deste navegador?')) return;
    if(requestEpoch!==jpWealthPersistenceEpoch()) return;
    // ALD-C3-PRE-PERSISTENCE: a substituição da base inteira roda dentro do writer
    // lock cross-tab (mesma serialização da finalização e do wipe). O corpo nunca
    // rejeita: falhas viram alert e a Promise resolve — nenhum fire-and-forget
    // destrutivo. Em modo degraded (sem Web Locks) roda direto, best-effort (DP-3).
    const aplicar=async ()=>{
    if(requestEpoch!==jpWealthPersistenceEpoch()) return;
    // ALD-C3-PRE-EPOCH: o backup já foi lido e validado integralmente acima. A nova
    // geração é firmada AQUI, antes de a base ser substituída — nunca depois, porque
    // uma base nova sob geração antiga deixaria uma finalização pendente atuar sobre
    // ela. Falhando a rotação, a importação é abortada e a base atual fica intacta.
    const novaEpoch=(typeof sessionEpochRotate==='function')?sessionEpochRotate():null;
    if(!novaEpoch){
      alert('Não foi possível estabelecer uma nova geração da base neste navegador. O backup NÃO foi aplicado — recarregue a página e tente novamente.');
      return;
    }
    // Só a partir daqui a operação se aplica — candidato validado e confirmado.
    S=imported;
    // Auditoria resumida (JPW-HJFGDE §11): a importação entra no changeLog DA BASE
    // IMPORTADA — é nela que o evento aconteceu e é ela que o próximo backup protege.
    if(typeof dgLogChange==='function') dgLogChange('database','imported',file.name||'','Importação de backup realizada');
    // Integração A-005: uma importação VALIDADA é decisão legítima de sair do modo de
    // recuperação — o portão genérico só reabre AGORA, com candidato aplicado, e o
    // desbloqueio do recovery só se consolida após gravação comprovada; se a escrita
    // falhar, jpWealthResolveRecoveryAndSave() restaura a flag de recuperação e a
    // chave principal fica intacta.
    if(jpWealthPersistenceIsBlocked()) resumeJPWealthPersistence();
    const gravou=(typeof jpWealthResolveRecoveryAndSave==='function')?jpWealthResolveRecoveryAndSave():save();
    if(typeof markSessionCheckpoint==='function') markSessionCheckpoint();
    // A base foi SUBSTITUÍDA — atravessa as abas pelo mesmo canal da Zona de
    // Perigo e da Finalização. Sem isto, outra aba mantinha o S anterior em
    // memória e a primeira gravação dela ressuscitava o documento antigo por
    // cima do backup recém-restaurado, sem aviso nenhum nas duas telas. Só
    // difunde depois da gravação comprovada: avisar sobre uma base que não
    // chegou ao disco faria as outras abas recarregarem o estado errado.
    if(gravou && typeof sessionNotifyBaseImported==='function') sessionNotifyBaseImported(novaEpoch);
    boot();
    alert(gravou?'Backup importado com sucesso.':'O backup foi lido e aplicado em memória, mas a gravação no armazenamento local falhou — exporte um backup e verifique o navegador antes de continuar.');
    };
    if(typeof sessionAcquireWriteLock==='function'){ sessionAcquireWriteLock(aplicar); }
    else{ aplicar(); }
  };
  reader.onerror=()=>alert('Não foi possível ler o arquivo de backup.');
  reader.readAsText(file);
}
