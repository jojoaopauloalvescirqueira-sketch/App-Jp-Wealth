// ============ GOVERNANÇA DE ARMAZENAMENTO — UI (JPW-HJFGDE) ============
// Camada de apresentação sobre 00-core/06-storage-fs.js e os helpers dg* de
// 04-persistence.js: cartão de status da pasta padrão (Central → Backup e Recuperação),
// diálogo de recuperação da exportação (§7 — nunca fallback silencioso) e aviso de
// backup a cada 30 dias (§10). Nenhuma regra de estado vive aqui — só leitura e gesto.
function dgFmtDateTime(iso){
  if(!iso) return '';
  try{ return new Intl.DateTimeFormat('pt-BR',{dateStyle:'short',timeStyle:'short'}).format(new Date(iso)); }
  catch(e){ return String(iso); }
}
// ---- diálogo de recuperação da exportação (§6.4/§6.5/§7) -------------------------
// Chamado por exportFullBackup() quando a pasta configurada não está acessível.
// Resolve com: 'retry' (acesso possivelmente recuperado — tentar de novo),
// 'downloads' (escolha EXPLÍCITA de exportar excepcionalmente para Downloads) ou
// 'cancelled'. Overlay próprio (não usa #modalOverlay: precisa poder aparecer por cima
// do fluxo de Finalizar Sessão, que já ocupa o overlay genérico).
function dgExportRecoveryDialog(state){
  return new Promise(resolve=>{
    const prev=document.getElementById('dgRecoveryOverlay');
    if(prev) prev.remove();
    const st=(S.dataGovernance&&S.dataGovernance.storage)||{};
    const nome=st.folderDisplayPath||st.folderName||'(pasta não identificada)';
    const missing=state==='missing';
    const titulo=missing?'Pasta da base não localizada neste navegador':'Não foi possível acessar a pasta padrão da base de dados';
    const corpo=missing
      ? 'A base informa a pasta anteriormente configurada, mas este navegador não possui a autorização local para acessá-la — isso é esperado após importar a base em outro dispositivo ou limpar o armazenamento do navegador.'
      : (state==='prompt'
        ? 'A pasta padrão da base está configurada, mas o JP Wealth precisa recuperar autorização para acessá-la.'
        : (state==='denied'
          ? 'O navegador negou o acesso à pasta padrão configurada.'
          : 'A pasta padrão configurada não pôde ser lida ou gravada — ela pode ter sido movida ou removida do disco.'));
    const overlay=document.createElement('div');
    overlay.id='dgRecoveryOverlay';
    overlay.className='dg-overlay';
    overlay.innerHTML=
      '<div class="dg-dialog" role="dialog" aria-modal="true" aria-labelledby="dgRecoveryTitle">'+
      '<h3 id="dgRecoveryTitle">'+esc(titulo)+'</h3>'+
      '<p class="dg-dialog-sub">'+esc(corpo)+'</p>'+
      '<div class="dg-folder-fact"><span>'+(missing?'Pasta anteriormente configurada':'Pasta padrão')+'</span><b>'+esc(nome)+'</b></div>'+
      '<p class="dg-dialog-warn">Nenhum arquivo foi exportado para a pasta configurada.</p>'+
      '<div class="dg-dialog-actions">'+
      (missing
        ? '<button type="button" class="modal-btn confirm" id="dgActLocate">Localizar esta pasta</button>'
        : '<button type="button" class="modal-btn confirm" id="dgActReauth">Reautorizar pasta</button>'+
          '<button type="button" class="modal-btn cancel" id="dgActRepick">Escolher outra pasta</button>')+
      '<button type="button" class="modal-btn cancel" id="dgActDownloads">Exportar excepcionalmente para Downloads</button>'+
      '<button type="button" class="modal-btn cancel" id="dgActCancel">Cancelar</button>'+
      '</div><p class="dg-dialog-note" id="dgActNote" role="status" aria-live="polite"></p></div>';
    document.body.appendChild(overlay);
    const note=overlay.querySelector('#dgActNote');
    function done(result){
      document.removeEventListener('keydown',onKey,true);
      overlay.remove();
      resolve(result);
    }
    function onKey(e){
      if(e.key==='Escape'){ e.stopPropagation(); e.preventDefault(); done('cancelled'); return; }
      if(e.key==='Tab'){
        // ciclo de foco mínimo dentro do diálogo — nada atrás dele é operável
        const focusables=[...overlay.querySelectorAll('button')];
        if(!focusables.length) return;
        const first=focusables[0], last=focusables[focusables.length-1];
        if(e.shiftKey && document.activeElement===first){ e.preventDefault(); last.focus(); }
        else if(!e.shiftKey && document.activeElement===last){ e.preventDefault(); first.focus(); }
      }
    }
    document.addEventListener('keydown',onKey,true);
    const reauth=overlay.querySelector('#dgActReauth');
    if(reauth) reauth.addEventListener('click',async()=>{
      const handle=await dgFsLoadHandle();
      if(!handle){ note.textContent='A autorização local não existe mais neste navegador — escolha a pasta novamente.'; return; }
      const perm=await dgFsRequestPermission(handle);
      if(perm==='granted'){ done('retry'); return; }
      note.textContent='A autorização não foi concedida. Tente novamente, escolha outra pasta ou exporte para Downloads.';
    });
    const pick=async()=>{
      const r=await dgFsPickFolder();
      if(r.ok){ done('retry'); return; }
      if(r.reason==='cancelled'){ note.textContent='Seleção de pasta cancelada — nada foi alterado.'; return; }
      note.textContent=r.message||'Não foi possível configurar a pasta.';
    };
    const repick=overlay.querySelector('#dgActRepick');
    if(repick) repick.addEventListener('click',pick);
    const locate=overlay.querySelector('#dgActLocate');
    if(locate) locate.addEventListener('click',pick);
    overlay.querySelector('#dgActDownloads').addEventListener('click',()=>done('downloads'));
    overlay.querySelector('#dgActCancel').addEventListener('click',()=>done('cancelled'));
    overlay.addEventListener('mousedown',e=>{ if(e.target===overlay) done('cancelled'); });
    const firstBtn=overlay.querySelector('.dg-dialog-actions button');
    if(firstBtn) firstBtn.focus();
  });
}
// ---- cartão de status na Central (§6/§18) ----------------------------------------
function dgChangesBreakdown(changes){
  const ENT={ledger:'fechamento(s) diário(s)',operation:'operação(ões)',quarantine:'quarentena',
    database:'base de dados',storage:'pasta de armazenamento',backup:'backup',
    onboarding:'configuração do período',config:'configuração(ões)'};
  // Toda ação emitida por dgLogChange() precisa de entrada aqui: o fallback `ACT[act]||act`
  // existe para não quebrar, mas exibir o slug cru ('responsibility_accepted') vaza
  // vocabulário interno para o operador. Ao criar uma ação nova, mapeie-a junto.
  const ACT={created:'registrado(s)',updated:'atualizado(s)',deleted:'removido(s)',
    imported:'importada',exported:'exportada',confirmed:'confirmado',archived:'arquivada(s)',
    configured:'configurada',completed:'concluída',
    responsibility_accepted:'— termo de responsabilidade aceito'};
  const counts=new Map();
  changes.forEach(e=>{
    const k=e.entity+'|'+e.action;
    counts.set(k,(counts.get(k)||0)+1);
  });
  return [...counts.entries()].map(([k,n])=>{
    const [ent,act]=k.split('|');
    return n+' × '+(ENT[ent]||ent)+' '+(ACT[act]||act);
  });
}
async function renderDgStorageCard(){
  const box=document.getElementById('dgStorageCard'); if(!box) return;
  const dg=S.dataGovernance||{};
  const supported=typeof dgFsSupported==='function' && dgFsSupported();
  const {state}=supported?await dgFsStatus():{state:'unsupported'};
  const st=dg.storage||{};
  let statusHtml='';
  if(state==='unsupported'){
    statusHtml='<p class="dg-status-note">Armazenamento em pasta personalizada não é suportado neste navegador.</p>'+
      '<p class="dg-status-note">As exportações utilizarão o mecanismo padrão de download, mantendo a nomenclatura progressiva e o controle de backup.</p>'+
      (st.configured?'<div class="dg-folder-fact"><span>Pasta configurada em outro navegador</span><b>'+esc(st.folderDisplayPath||st.folderName)+'</b></div>':'');
  }else if(state==='unconfigured'){
    statusHtml='<p class="dg-status-note">Escolha a pasta padrão onde as exportações da base de dados JP Wealth serão armazenadas.</p>'+
      '<div class="dg-actions"><button type="button" class="reset-btn" id="dgCardPick">Selecionar pasta</button></div>';
  }else if(state==='authorized'){
    statusHtml='<div class="dg-folder-fact"><span>Pasta padrão</span><b>'+esc(st.folderDisplayPath||st.folderName)+'</b></div>'+
      '<p class="dg-status-line dg-status-ok">Status: Acesso autorizado</p>'+
      '<div class="dg-actions"><button type="button" class="reset-btn" id="dgCardPick">Alterar pasta</button>'+
      '<button type="button" class="reset-btn" id="dgCardVerify">Verificar acesso</button></div>';
  }else if(state==='missing'){
    statusHtml='<div class="dg-folder-fact"><span>Pasta anteriormente configurada</span><b>'+esc(st.folderDisplayPath||st.folderName)+'</b></div>'+
      '<p class="dg-status-line dg-status-warn">Status: Autorização necessária — este navegador não possui a autorização local desta pasta (base importada de outro dispositivo, ou armazenamento local limpo).</p>'+
      '<div class="dg-actions"><button type="button" class="reset-btn" id="dgCardPick">Localizar esta pasta</button></div>';
  }else{ // prompt | denied
    statusHtml='<div class="dg-folder-fact"><span>Pasta padrão</span><b>'+esc(st.folderDisplayPath||st.folderName)+'</b></div>'+
      '<p class="dg-status-line dg-status-warn">Status: Autorização necessária — o JP Wealth precisa recuperar autorização para acessar a pasta.</p>'+
      '<div class="dg-actions"><button type="button" class="reset-btn" id="dgCardReauth">Reautorizar pasta</button>'+
      '<button type="button" class="reset-btn" id="dgCardPick">Escolher outra pasta</button></div>';
  }
  const exp=dg.export||{};
  const bk=dg.backup||{};
  const changes=typeof dgChangesSinceLastBackup==='function'?dgChangesSinceLastBackup():[];
  const age=typeof dgBackupAgeDays==='function'?dgBackupAgeDays():null;
  const breakdown=dgChangesBreakdown(changes);
  const detalhe=changes.slice(-30).reverse().map(e=>'<li><span>'+esc(dgFmtDateTime(e.ts))+'</span> — '+esc(e.label||e.entity+' '+e.action)+'</li>').join('');
  box.innerHTML=
    '<h4>Local de armazenamento da base</h4>'+statusHtml+
    '<h4>Exportação e backup</h4>'+
    '<dl class="dg-facts">'+
    '<dt>Última exportação</dt><dd>'+(exp.lastExportFile?'<code>'+esc(exp.lastExportFile)+'</code> — '+esc(dgFmtDateTime(exp.lastExportAt)):'nenhuma exportação registrada')+'</dd>'+
    '<dt>Próxima sequência</dt><dd>'+String((exp.lastSequence||0)+1).padStart(6,'0')+'</dd>'+
    '<dt>Último backup confirmado</dt><dd>'+(bk.lastConfirmedAt?esc(dgFmtDateTime(bk.lastConfirmedAt))+' ('+age+' dia'+(age===1?'':'s')+' atrás)':'nunca confirmado')+'</dd>'+
    '<dt>Alterações desde o último backup</dt><dd>'+(changes.length
      ? changes.length+' alteração(ões) registrada(s)'+(breakdown.length?'<ul class="dg-breakdown"><li>'+breakdown.map(esc).join('</li><li>')+'</li></ul>':'')+
        '<details class="dg-detail"><summary>Detalhamento cronológico (últimas '+Math.min(changes.length,30)+')</summary><ul class="dg-chrono">'+detalhe+'</ul></details>'
      : 'nenhuma alteração registrada')+'</dd>'+
    '</dl>'+
    '<p class="dg-status-note">Exportar gera uma cópia da base; <b>backup confirmado</b> é a sua declaração de que uma cópia adequada está guardada — são eventos distintos.</p>'+
    '<div class="dg-actions"><button type="button" class="reset-btn" id="dgCardConfirmBackup">Confirmar que possuo backup atualizado</button></div>';
  const pickBtn=box.querySelector('#dgCardPick');
  if(pickBtn) pickBtn.addEventListener('click',async()=>{
    const r=await dgFsPickFolder();
    if(!r.ok && r.reason==='error') alert(r.message||'Não foi possível configurar a pasta.');
    renderDgStorageCard();
  });
  const reauthBtn=box.querySelector('#dgCardReauth');
  if(reauthBtn) reauthBtn.addEventListener('click',async()=>{
    const handle=await dgFsLoadHandle();
    if(handle){ await dgFsRequestPermission(handle); }
    renderDgStorageCard();
  });
  const verifyBtn=box.querySelector('#dgCardVerify');
  if(verifyBtn) verifyBtn.addEventListener('click',async()=>{
    const r=await dgFsVerifyAccess();
    alert(r.ok?'Acesso à pasta padrão verificado com sucesso — leitura confirmada.':'A verificação falhou ('+esc(r.state)+'): '+(r.message||'a pasta não está acessível. Reautorize ou escolha outra pasta.'));
    renderDgStorageCard();
  });
  const confirmBtn=box.querySelector('#dgCardConfirmBackup');
  if(confirmBtn) confirmBtn.addEventListener('click',()=>{
    // §10: a confirmação de backup exige gesto explícito e consciente — nunca automática.
    if(!confirm('Confirmar que você possui um backup ATUALIZADO e acessível da base JP Wealth?\n\nIsto registra a data de hoje como último backup confirmado e zera a contagem de 30 dias. Confirme apenas se a cópia realmente existe fora deste navegador.')) return;
    dgConfirmBackup();
    renderDgStorageCard();
    renderDgBackupBanner();
  });
}
// ---- painel de pasta reutilizável (etapa Base de Dados do onboarding, §6) --------
// Versão compacta do bloco de status do cartão: mesmo vocabulário de estados, ações
// auto-religadas no próprio container. A pasta é OPCIONAL no onboarding — configurar
// aqui só antecipa o que o cartão da Central faz.
async function renderDgFolderPanel(box){
  if(!box) return;
  const supported=typeof dgFsSupported==='function' && dgFsSupported();
  const {state}=supported?await dgFsStatus():{state:'unsupported'};
  const st=(S.dataGovernance&&S.dataGovernance.storage)||{};
  let html='';
  if(state==='unsupported'){
    html='<p>Armazenamento em pasta personalizada não é suportado neste navegador.</p>'+
      '<p>As exportações utilizarão o mecanismo padrão de download, mantendo a nomenclatura progressiva e o controle de backup. Você pode configurar uma pasta padrão mais tarde, num navegador compatível (Chrome/Edge desktop), em Configurações → Dados e Segurança.</p>';
  }else if(state==='unconfigured'){
    html='<p>Escolha a pasta padrão onde as exportações da base de dados JP Wealth serão armazenadas. Você também pode fazer isso depois, em Configurações → Dados e Segurança.</p>'+
      '<div class="dg-actions"><button type="button" class="reset-btn" data-dg-act="pick">Selecionar pasta</button></div>';
  }else if(state==='authorized'){
    html='<div class="dg-folder-fact"><span>Pasta configurada</span><b>'+esc(st.folderDisplayPath||st.folderName)+'</b></div>'+
      '<p class="dg-status-line dg-status-ok">Status: Acesso autorizado</p>'+
      '<div class="dg-actions"><button type="button" class="reset-btn" data-dg-act="pick">Alterar pasta</button>'+
      '<button type="button" class="reset-btn" data-dg-act="verify">Verificar acesso</button></div>';
  }else if(state==='missing'){
    html='<div class="dg-folder-fact"><span>Pasta anteriormente configurada</span><b>'+esc(st.folderDisplayPath||st.folderName)+'</b></div>'+
      '<p class="dg-status-line dg-status-warn">Este navegador não possui a autorização local desta pasta.</p>'+
      '<div class="dg-actions"><button type="button" class="reset-btn" data-dg-act="pick">Localizar esta pasta</button></div>';
  }else{
    html='<div class="dg-folder-fact"><span>Pasta configurada</span><b>'+esc(st.folderDisplayPath||st.folderName)+'</b></div>'+
      '<p class="dg-status-line dg-status-warn">Status: Autorização necessária.</p>'+
      '<div class="dg-actions"><button type="button" class="reset-btn" data-dg-act="reauth">Reautorizar pasta</button>'+
      '<button type="button" class="reset-btn" data-dg-act="pick">Escolher outra pasta</button></div>';
  }
  box.innerHTML=html;
  box.querySelectorAll('[data-dg-act]').forEach(btn=>btn.addEventListener('click',async()=>{
    const act=btn.dataset.dgAct;
    if(act==='pick'){
      const r=await dgFsPickFolder();
      if(!r.ok && r.reason==='error') alert(r.message||'Não foi possível configurar a pasta.');
    }else if(act==='reauth'){
      const handle=await dgFsLoadHandle();
      if(handle) await dgFsRequestPermission(handle);
    }else if(act==='verify'){
      const r=await dgFsVerifyAccess();
      alert(r.ok?'Acesso à pasta verificado com sucesso.':'A verificação falhou: '+(r.message||'a pasta não está acessível.'));
    }
    renderDgFolderPanel(box);
    if(typeof renderDgStorageCard==='function') renderDgStorageCard();
  }));
}
// ---- aviso de backup 30 dias (§10) -----------------------------------------------
// Barra discreta fixa no rodapé; some na sessão ao dispensar e reaparece na próxima
// abertura se continuar devida. Não bloqueia nada — governança sem intrusão (§18).
function renderDgBackupBanner(){
  let el=document.getElementById('dgBackupBanner');
  const due=typeof dgBackupDue==='function' && dgBackupDue();
  if(!due || window.__dgBannerDismissed){ if(el) el.remove(); return; }
  const age=dgBackupAgeDays();
  const changes=dgChangesSinceLastBackup().length;
  if(!el){
    el=document.createElement('div');
    el.id='dgBackupBanner';
    el.className='dg-backup-banner';
    document.body.appendChild(el);
  }
  el.innerHTML='<b>Backup recomendado</b><span>'+
    (age===null?'Nenhum backup confirmado até agora':age+' dia'+(age===1?'':'s')+' desde o último backup confirmado')+
    (changes?' — '+changes+' alteração(ões) acumulada(s) desde então':'')+'.</span>'+
    '<button type="button" class="reset-btn" id="dgBannerExport">Exportar backup agora</button>'+
    '<button type="button" class="reset-btn" id="dgBannerHave">Já possuo um backup atualizado</button>'+
    '<button type="button" class="dg-banner-close" id="dgBannerClose" aria-label="Dispensar aviso de backup">✕</button>';
  el.querySelector('#dgBannerExport').addEventListener('click',async()=>{
    await exportFullBackup();
    renderDgStorageCard();
    renderDgBackupBanner();
  });
  el.querySelector('#dgBannerHave').addEventListener('click',()=>{
    if(!confirm('Confirmar que você possui um backup ATUALIZADO e acessível da base JP Wealth?\n\nConfirme apenas se a cópia realmente existe fora deste navegador.')) return;
    dgConfirmBackup();
    renderDgStorageCard();
    renderDgBackupBanner();
  });
  el.querySelector('#dgBannerClose').addEventListener('click',()=>{
    window.__dgBannerDismissed=true;
    renderDgBackupBanner();
  });
}
// primeira renderização — boots seguintes (import, wipe, finalize) re-renderizam via
// os guards em 06-boot.js, no mesmo padrão de renderMvpNotesHeader()
renderDgStorageCard();
renderDgBackupBanner();
