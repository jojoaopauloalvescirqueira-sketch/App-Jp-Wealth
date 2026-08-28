// ============ ALLADIN · SUPERFÍCIE CADASTRAL READ-ONLY (C3-S1 · N1) ============
// Primeira superfície funcional do Alladin: apresenta o cadastro C2 REAL, e só
// ele. A UI é OBSERVADORA — invariante de segurança do slice:
//   abrir · trocar view · renderizar · refresh · READ_ONLY · empty state
//   ⇒ zero save(), zero aldMutate, zero cadastro.*, zero materialização de
//     S.alladin, zero chave de storage, S e disco byte-idênticos.
// A leitura passa EXCLUSIVAMENTE por JPWAlladin.leitura (snapshots profundos e
// congelados) — esta superfície nunca toca S.alladin, nem para checar ausência.
// PROIBIÇÃO ECONÔMICA (UI-A/UI-B do gate C3): nenhum saldo, quantidade, preço,
// valor, custo, patrimônio, P&L, rentabilidade ou performance — nem como zero.
// "Caixa" é o CADASTRO de CashAccount (DC-3), jamais dinheiro disponível.
// A seleção de view é EFÊMERA (padrão Research/NAV-03): não toca S nem storage.

const ALLADIN_VIEWS=[
  ['instruments','alladinInstruments'],
  ['assets','alladinAssets'],
  ['accounts','alladinAccounts'],
  ['cashAccounts','alladinCash']
];
const ALLADIN_EMPTY={
  instruments:'Nenhum instrumento cadastrado.',
  assets:'Nenhum bem cadastrado.',
  accounts:'Nenhuma conta cadastrada.',
  cashAccounts:'Nenhuma conta de caixa cadastrada.'
};
// Rótulos de status legíveis; valor fora do vocabulário deste build (schema
// futuro) é exibido como veio — projetar não é normalizar.
const ALLADIN_STATUS_LABEL={ACTIVE:'Ativo',INACTIVE:'Inativo'};
const ALLADIN_LIFECYCLE_LABEL={ACTIVE:'Em uso',SOLD:'Vendido',DISPOSED:'Baixado',TRANSFERRED:'Transferido'};

let alladinView='instruments';

function alladinStatus(v,mapa){
  if(v===undefined||v===null||v==='') return '—';
  return (mapa && mapa[v]) || String(v);
}
function alladinTexto(v){
  return (v===undefined||v===null||v==='') ? '—' : String(v);
}
function alladinTabela(colunas,linhas){
  const head='<tr>'+colunas.map(c=>'<th>'+esc(c)+'</th>').join('')+'</tr>';
  const corpo=linhas.map(cels=>'<tr>'+cels.map(c=>'<td>'+c+'</td>').join('')+'</tr>').join('');
  return '<div class="jp-table-scroll"><table class="dtable">'+head+corpo+'</table></div>';
}
function alladinVazio(view){
  // NÃO usar class="expl": essa classe pertence ao sistema global de Explicações,
  // que a colapsa atrás do botão "i". Empty state é informação primária e fica
  // sempre visível.
  return '<p class="alladin-empty">'+esc(ALLADIN_EMPTY[view])+'</p>';
}
// Apresentação congelada no gate (teto = read-model; tabela = colunas abaixo):
//   Instrumentos  Nome | Símbolo | Família/Classe | Moeda | Status
//   Bens          Nome | Natureza/Categoria | Finalidade | Status
//   Contas        Nome | Instituição | Tipo | Status
//   Caixa         Moeda | Conta-mãe | Status
function alladinRenderInstruments(el){
  const lista=JPWAlladin.leitura.instruments();
  if(!lista.length){ el.innerHTML='<h2>Instrumentos</h2>'+alladinVazio('instruments'); return; }
  el.innerHTML='<h2>Instrumentos</h2>'+alladinTabela(
    ['Nome','Símbolo','Família / Classe','Moeda','Status','Ações'],
    lista.map(r=>[
      esc(alladinTexto(r.name)),
      esc(alladinTexto(r.symbol)),
      esc([r.instrumentFamily,r.assetClass].filter(Boolean).join(' · ')||'—'),
      esc(alladinTexto(r.currency)),
      esc(alladinStatus(r.recordStatus,ALLADIN_STATUS_LABEL)),
      alladinAcaoDeLinha('instrument',r)
    ]));
}
function alladinRenderAssets(el){
  const lista=JPWAlladin.leitura.assets();
  if(!lista.length){ el.innerHTML='<h2>Bens</h2>'+alladinVazio('assets'); return; }
  el.innerHTML='<h2>Bens</h2>'+alladinTabela(
    ['Nome','Natureza / Categoria','Finalidade','Status','Ações'],
    lista.map(r=>[
      esc(alladinTexto(r.name)),
      esc([r.nature,r.category].filter(Boolean).join(' · ')||'—'),
      esc(alladinTexto(r.strategicPurpose)),
      // Dois eixos do C2: recordStatus (registro) × lifecycleStatus (vida do bem).
      esc(alladinStatus(r.recordStatus,ALLADIN_STATUS_LABEL))+
        (r.lifecycleStatus?' · '+esc(alladinStatus(r.lifecycleStatus,ALLADIN_LIFECYCLE_LABEL)):''),
      alladinAcaoDeLinha('asset',r)
    ]));
}
function alladinRenderAccounts(el){
  const lista=JPWAlladin.leitura.accounts();
  if(!lista.length){ el.innerHTML='<h2>Contas</h2>'+alladinBotaoNovo('accounts')+alladinVazio('accounts'); return; }
  el.innerHTML='<h2>Contas</h2>'+alladinBotaoNovo('accounts')+alladinTabela(
    ['Nome','Instituição','Tipo','Status','Ações'],
    lista.map(r=>[
      esc(alladinTexto(r.name)),
      esc(alladinTexto(r.institution)),
      esc(alladinTexto(r.accountType)),
      esc(alladinStatus(r.recordStatus,ALLADIN_STATUS_LABEL)),
      alladinAcaoDeLinha('account',r)
    ]));
}
function alladinRenderCash(el){
  const lista=JPWAlladin.leitura.cashAccounts();
  if(!lista.length){ el.innerHTML='<h2>Caixa</h2>'+alladinBotaoNovo('cashAccounts')+alladinVazio('cashAccounts'); return; }
  // Conta-mãe resolvida DENTRO do snapshot de leitura — nunca no agregado vivo.
  const contas={};
  JPWAlladin.leitura.accounts().forEach(a=>{ if(a.accountId) contas[a.accountId]=a.name; });
  el.innerHTML='<h2>Caixa</h2>'+
    '<p class="expl">Cadastro das contas de caixa por moeda — dinheiro disponível não pertence a este ciclo.</p>'+
    alladinBotaoNovo('cashAccounts')+
    alladinTabela(
    ['Moeda','Conta-mãe','Status','Ações'],
    lista.map(r=>[
      esc(alladinTexto(r.currency)),
      esc(alladinTexto(contas[r.accountId]||r.accountId)),
      esc(alladinStatus(r.recordStatus,ALLADIN_STATUS_LABEL)),
      alladinAcaoDeLinha('cashaccount',r)
    ]));
}
const ALLADIN_RENDERERS={
  instruments:alladinRenderInstruments,
  assets:alladinRenderAssets,
  accounts:alladinRenderAccounts,
  cashAccounts:alladinRenderCash
};

function alladinRenderBanner(){
  const banner=document.getElementById('alladinReadOnlyBanner');
  if(!banner) return;
  const compat=JPWAlladin.compat();
  if(compat.readOnly){
    banner.hidden=false;
    banner.textContent='Cadastro em modo somente-leitura. Este agregado foi gravado por uma versão mais nova do JP Wealth. Os dados compatíveis podem ser consultados, mas não alterados neste build.';
  }else{
    banner.hidden=true;
    banner.textContent='';
  }
}
function alladinApplyView(view){
  ALLADIN_VIEWS.forEach(([key,id])=>{
    const el=document.getElementById(id);
    if(!el) return;
    const active=key===view;
    el.hidden=!active;
    el.inert=!active;
    if(active && ALLADIN_RENDERERS[key]) ALLADIN_RENDERERS[key](el);
  });
  const tabs=document.getElementById('alladinTabs');
  if(tabs) tabs.querySelectorAll('button[data-alladin-view]').forEach(b=>{
    const on=b.dataset.alladinView===view;
    b.classList.toggle('on',on);
    b.setAttribute('aria-pressed',on?'true':'false');
  });
}
function alladinRender(){
  alladinRenderBanner();
  alladinApplyView(alladinView);
}
function alladinSelectView(view){
  if(!ALLADIN_RENDERERS[view]) return;
  alladinView=view;              // efêmero: nunca persiste
  alladinRender();
}
function initAlladinViews(){
  const section=document.getElementById('alladin');
  const tabs=document.getElementById('alladinTabs');
  if(!section||!tabs) return;
  // Delegação: UM listener para as quatro tabs — trocar view jamais acumula nós
  // nem listeners (as tabelas são substituídas por innerHTML no mesmo container).
  tabs.addEventListener('click',e=>{
    const btn=e.target.closest('button[data-alladin-view]');
    if(btn) alladinSelectView(btn.dataset.alladinView);
  });
  // Render ao ENTRAR na tela: observa a própria section (hook local; a navegação
  // global não é tocada — os quatro destinos são estado efêmero do Alladin).
  new MutationObserver(()=>{
    if(section.classList.contains('active')) alladinRender();
  }).observe(section,{attributes:true,attributeFilter:['class']});
  alladinRender();
}
window.JPWAlladinUI=Object.freeze({render:alladinRender,selectView:alladinSelectView});
initAlladinViews();

// ============ ALLADIN · MANUTENÇÃO CADASTRAL (C3-S2-A · N1) ==================
// Primeira ESCRITA cadastral via UI: Account e CashAccount (Create/Edit) +
// recordStatus das QUATRO entidades. Instrument/Asset ganham formulários no
// S2-B. Toda mutação passa por JPWAlladin.cadastro / setRecordStatus — a UI
// JAMAIS escreve em S, jamais muta snapshots de leitura, jamais decide regra
// estrutural (o domínio é a autoridade; validação de UX é só "obrigatório
// preenchido"). Nenhum campo econômico: currency é cadastro, montante não existe.
//
// MÁQUINA DE ESTADOS do modal (contrato do gate):
//   IDLE → EDITING → SUBMITTING → { ERROR→EDITING · SUCCESS→CLOSED ·
//   COMMITTED_WARNING → { KEEP→CLOSED · DEACTIVATE→(SUCCESS→CLOSED |
//   ERROR→COMMITTED_WARNING) } }  — e CONFIRM_STATUS para Inativar/Reativar.
// Em SUBMITTING nenhuma segunda submissão. Em COMMITTED_WARNING o registro JÁ
// nasceu e JÁ está persistido (contrato DC-4 do C2: "o registro nasce e o
// operador decide"): Salvar deixa de existir, Enter não recria, Escape e
// backdrop ficam SUSPENSOS até o gesto explícito Manter/Inativar.
const ALLADIN_TIPO_LABEL={instrument:'instrumento', asset:'bem', account:'conta', cashaccount:'conta de caixa'};
let alladinForm={estado:'IDLE', tipo:null, modo:null, alvoId:null, recordId:null, foco:null, avisos:[]};

function alladinFocusables(){
  const box=document.getElementById('alladinModalBox');
  return box?[...box.querySelectorAll('button:not([disabled]),input:not([disabled]),select:not([disabled]),[tabindex]:not([tabindex="-1"])')]:[];
}
function alladinModalAberto(){
  const ov=document.getElementById('alladinModalOverlay');
  return !!(ov && ov.classList.contains('show'));
}
// O rerender substitui os nós da lista por innerHTML: guardar o ELEMENTO de
// origem não basta — ele morre com o render. Guarda-se um seletor re-resolvível.
function alladinSeletorDeFoco(el){
  if(!el||!el.dataset) return null;
  if(el.dataset.aldNew) return 'button[data-ald-new="'+el.dataset.aldNew+'"]';
  if(el.dataset.aldEdit) return 'button[data-ald-edit="'+el.dataset.aldEdit+'"][data-ald-id="'+el.dataset.aldId+'"]';
  if(el.dataset.aldStatus) return 'button[data-ald-tipo="'+el.dataset.aldTipo+'"][data-ald-id="'+el.dataset.aldId+'"]';
  return null;
}
function alladinModalOpen(html, foco){
  const ov=document.getElementById('alladinModalOverlay');
  const box=document.getElementById('alladinModalBox');
  if(!ov||!box) return;
  const origem=foco||document.activeElement;
  alladinForm.foco=alladinSeletorDeFoco(origem)||origem;
  box.innerHTML=html;
  ov.classList.add('show');
  const f=alladinFocusables(); if(f.length) f[0].focus();
}
function alladinModalClose(){
  const ov=document.getElementById('alladinModalOverlay');
  if(ov) ov.classList.remove('show');
  const foco=alladinForm.foco;
  alladinForm={estado:'IDLE', tipo:null, modo:null, alvoId:null, recordId:null, foco:null, avisos:[]};
  alladinRender();
  const alvo=(typeof foco==='string')?document.querySelector(foco):foco;
  if(alvo && typeof alvo.focus==='function') alvo.focus();
}
// Escape/backdrop: cancelam SOMENTE fora dos estados protegidos. Em
// COMMITTED_WARNING e SUBMITTING a saída silenciosa é proibida por contrato.
function alladinModalDismiss(){
  if(alladinForm.estado==='COMMITTED_WARNING'||alladinForm.estado==='SUBMITTING') return;
  alladinModalClose();
}

function alladinWriteBloqueado(){
  try{ return JPWAlladin.writeBlockReason(); }catch(e){ return 'ALD_INDISPONIVEL'; }
}
function alladinCampo(id,rotulo,valor,extra){
  return '<label class="field"><span>'+esc(rotulo)+'</span>'+
    '<input type="text" id="'+id+'" value="'+esc(valor==null?'':valor)+'" autocomplete="off" '+(extra||'')+'></label>';
}
function alladinErroBox(msg){
  return msg?'<div class="session-error" role="alert">'+esc(msg)+'</div>':'';
}

// ---- formulários (Account / CashAccount) -----------------------------------
function alladinFormAccountHTML(reg,erro){
  const tipos=JPWAlladin.catalogos().starter.accountType;
  const dl=document.getElementById('alladinAccountTypes');
  if(dl) dl.innerHTML=tipos.map(t=>'<option value="'+esc(t)+'"></option>').join('');
  return '<h3 id="alladinModalTitle">'+(reg?'Editar conta':'Nova conta')+'</h3>'+
    '<p class="modal-sub">Cadastro de conta de custódia ou instituição — dinheiro e movimentos não pertencem a este ciclo.</p>'+
    alladinErroBox(erro)+
    alladinCampo('alladinFldName','Nome',reg&&reg.name)+
    alladinCampo('alladinFldInstitution','Instituição',reg&&reg.institution)+
    alladinCampo('alladinFldAccountType','Tipo',reg&&reg.accountType,'list="alladinAccountTypes"')+
    '<div class="modal-actions"><button type="button" class="modal-btn cancel" data-ald-act="cancelar">Cancelar</button>'+
    '<button type="button" class="modal-btn confirm" data-ald-act="salvar">Salvar</button></div>';
}
function alladinFormCashHTML(reg,erro){
  const contas=JPWAlladin.leitura.accounts();
  const ativas=contas.filter(c=>c.recordStatus==='ACTIVE');
  let atualInativa='';
  // Referência atual HONESTA: se o registro aponta para conta hoje inativa, a
  // opção aparece rotulada como tal, selecionada e inalterada — a UI nunca troca
  // accountId em silêncio; o domínio decide no submit.
  if(reg){
    const atual=contas.find(c=>c.accountId===reg.accountId);
    if(atual && atual.recordStatus!=='ACTIVE'){
      atualInativa='<option value="'+esc(atual.accountId)+'" selected>'+esc(atual.name)+' — INATIVA</option>';
    }else if(!atual && reg.accountId){
      atualInativa='<option value="'+esc(reg.accountId)+'" selected>'+esc(reg.accountId)+' — AUSENTE</option>';
    }
  }
  const opts=ativas.map(c=>'<option value="'+esc(c.accountId)+'"'+(reg&&reg.accountId===c.accountId?' selected':'')+'>'+esc(c.name)+'</option>').join('');
  return '<h3 id="alladinModalTitle">'+(reg?'Editar conta de caixa':'Nova conta de caixa')+'</h3>'+
    '<p class="modal-sub">Cadastro da conta de caixa por moeda — dinheiro disponível não pertence a este ciclo.</p>'+
    alladinErroBox(erro)+
    '<label class="field"><span>Conta-mãe</span><select id="alladinFldAccountId">'+atualInativa+opts+'</select></label>'+
    alladinCampo('alladinFldCurrency','Moeda (código de 3 letras)',reg&&reg.currency,'maxlength="3" autocapitalize="characters"')+
    '<div class="modal-actions"><button type="button" class="modal-btn cancel" data-ald-act="cancelar">Cancelar</button>'+
    '<button type="button" class="modal-btn confirm" data-ald-act="salvar">Salvar</button></div>';
}
function alladinAbrirForm(tipo,modo,alvoId,erro){
  alladinForm.estado='EDITING'; alladinForm.tipo=tipo; alladinForm.modo=modo; alladinForm.alvoId=alvoId||null;
  let reg=null;
  if(modo==='edit'){
    const lista=(tipo==='account')?JPWAlladin.leitura.accounts():JPWAlladin.leitura.cashAccounts();
    reg=lista.find(r=>(tipo==='account'?r.accountId:r.cashAccountId)===alvoId)||null;
    if(!reg){ alladinModalClose(); return; }
  }
  const html=(tipo==='account')?alladinFormAccountHTML(reg,erro):alladinFormCashHTML(reg,erro);
  if(alladinModalAberto()){ document.getElementById('alladinModalBox').innerHTML=html; const f=alladinFocusables(); if(f.length) f[0].focus(); }
  else alladinModalOpen(html);
}

// ---- submissão --------------------------------------------------------------
function alladinLerFormulario(tipo){
  const v=(id)=>{ const el=document.getElementById(id); return el?el.value.trim():''; };
  if(tipo==='account') return { name:v('alladinFldName'), institution:v('alladinFldInstitution'), accountType:v('alladinFldAccountType') };
  return { accountId:v('alladinFldAccountId'), currency:v('alladinFldCurrency').toUpperCase() };
}
function alladinSubmit(){
  if(alladinForm.estado!=='EDITING') return;      // SUBMITTING/COMMITTED: nunca resubmete
  const {tipo,modo,alvoId}=alladinForm;
  const dados=alladinLerFormulario(tipo);
  for(const k of Object.keys(dados)){
    if(dados[k]===''){ alladinAbrirForm(tipo,modo,alvoId,'Preencha todos os campos antes de salvar.'); return; }
  }
  alladinForm.estado='SUBMITTING';
  let r;
  if(tipo==='account') r=(modo==='edit')?JPWAlladin.cadastro.editAccount(alvoId,dados):JPWAlladin.cadastro.addAccount(dados);
  else r=(modo==='edit')?JPWAlladin.cadastro.editCashAccount(alvoId,dados):JPWAlladin.cadastro.addCashAccount(dados);
  if(!r || r.ok!==true){
    alladinForm.estado='EDITING';
    alladinAbrirForm(tipo,modo,alvoId,'O cadastro foi recusado: '+esc((r&&r.erro)||'erro não identificado')+'. Nada foi gravado.');
    return;
  }
  // persistido:true daqui em diante — o registro EXISTE no disco.
  const dups=(r.avisos||[]).filter(a=>String(a).indexOf('DUPLICADO')===0);
  if(dups.length){
    alladinForm.estado='COMMITTED_WARNING';
    alladinForm.recordId=r.recordId;
    alladinForm.avisos=r.avisos||[];
    document.getElementById('alladinModalBox').innerHTML=
      '<h3 id="alladinModalTitle">Possível duplicidade</h3>'+
      '<p class="modal-sub">O registro foi criado e já está salvo. O aviso abaixo indica que ele pode duplicar um cadastro existente — decida o que fazer com ele.</p>'+
      '<div class="session-warning" role="alert">'+esc(dups.join(' · '))+'</div>'+
      '<div class="modal-actions"><button type="button" class="modal-btn cancel" data-ald-act="manter">Manter registro</button>'+
      '<button type="button" class="modal-btn confirm" data-ald-act="inativar-novo">Inativar este registro</button></div>';
    // Foco no TÍTULO, deliberadamente: um Enter residual do gesto de salvar não
    // pode ativar "Manter" sem leitura — a decisão exige Tab/clique deliberado.
    const titulo=document.getElementById('alladinModalTitle');
    if(titulo){ titulo.setAttribute('tabindex','-1'); titulo.focus(); }
    alladinRender();
    return;
  }
  const extras=(r.avisos||[]).length?' Aviso: '+r.avisos.join(' · ')+'.':'';
  alladinModalClose();
  showSessionNotice('Cadastro salvo.'+extras);
}
function alladinResolverWarning(acao){
  if(alladinForm.estado!=='COMMITTED_WARNING') return;
  if(acao==='manter'){ alladinModalClose(); showSessionNotice('Registro mantido.'); return; }
  // Segundo gesto explícito e segunda mutação legítima: setRecordStatus.
  const {tipo,recordId}=alladinForm;
  const r=JPWAlladin.cadastro.setRecordStatus(tipo,recordId,'INACTIVE');
  if(!r || r.ok!==true){
    // O registro permanece exatamente como o domínio o deixou; a decisão continua visível.
    const caixa=document.getElementById('alladinModalBox');
    const err=caixa.querySelector('.session-error');
    const msg='Não foi possível inativar: '+((r&&r.erro)||'erro não identificado')+'. O registro criado permanece ativo.';
    if(err) err.textContent=msg;
    else caixa.querySelector('.session-warning').insertAdjacentHTML('afterend','<div class="session-error" role="alert">'+esc(msg)+'</div>');
    return;
  }
  alladinModalClose();
  showSessionNotice('Registro criado e inativado.');
}

// ---- recordStatus ×4 (ação separada, com confirmação explícita) -------------
function alladinConfirmarStatus(tipo,id,novo){
  alladinForm.estado='CONFIRM_STATUS'; alladinForm.tipo=tipo; alladinForm.alvoId=id; alladinForm.modo=novo;
  const verbo=(novo==='INACTIVE')?'Inativar':'Reativar';
  alladinModalOpen('<h3 id="alladinModalTitle">'+verbo+' '+esc(ALLADIN_TIPO_LABEL[tipo]||tipo)+'</h3>'+
    '<p class="modal-sub">O registro não é apagado: inativar apenas o marca como fora de uso, e ele pode ser reativado depois.</p>'+
    '<div class="modal-actions"><button type="button" class="modal-btn cancel" data-ald-act="cancelar">Cancelar</button>'+
    '<button type="button" class="modal-btn confirm" data-ald-act="status-confirmado">'+verbo+'</button></div>');
}
function alladinExecutarStatus(){
  if(alladinForm.estado!=='CONFIRM_STATUS') return;
  const {tipo,alvoId,modo}=alladinForm;
  const r=JPWAlladin.cadastro.setRecordStatus(tipo,alvoId,modo);
  if(!r || r.ok!==true){
    const caixa=document.getElementById('alladinModalBox');
    caixa.querySelector('.modal-sub').insertAdjacentHTML('afterend',
      '<div class="session-error" role="alert">'+esc('Recusado: '+((r&&r.erro)||'erro não identificado'))+'</div>');
    return;   // status visual NÃO muda: nada foi relido, nada re-renderizado
  }
  alladinModalClose();
  showSessionNotice('Status atualizado.');
}

// ---- fiação -----------------------------------------------------------------
function alladinAcaoDeLinha(tipo,reg){
  const bloqueado=!!alladinWriteBloqueado();
  const id=(tipo==='instrument')?reg.instrumentId:(tipo==='asset')?reg.assetId:(tipo==='account')?reg.accountId:reg.cashAccountId;
  const dis=bloqueado?' disabled':'';
  const editBtn=(tipo==='account'||tipo==='cashaccount')
    ?'<button type="button" class="modal-btn cancel" data-ald-edit="'+esc(tipo)+'" data-ald-id="'+esc(id)+'"'+dis+'>Editar</button> '
    :'';
  const statusBtn=(reg.recordStatus==='ACTIVE')
    ?'<button type="button" class="modal-btn cancel" data-ald-status="INACTIVE" data-ald-tipo="'+esc(tipo)+'" data-ald-id="'+esc(id)+'"'+dis+'>Inativar</button>'
    :'<button type="button" class="modal-btn cancel" data-ald-status="ACTIVE" data-ald-tipo="'+esc(tipo)+'" data-ald-id="'+esc(id)+'"'+dis+'>Reativar</button>';
  return editBtn+statusBtn;
}
function alladinBotaoNovo(view){
  const bloqueado=!!alladinWriteBloqueado();
  if(view==='accounts'){
    return '<p><button type="button" class="modal-btn confirm" data-ald-new="account"'+(bloqueado?' disabled':'')+'>Nova conta</button></p>';
  }
  if(view==='cashAccounts'){
    const temAtiva=JPWAlladin.leitura.accounts().some(c=>c.recordStatus==='ACTIVE');
    if(!temAtiva) return '<p class="alladin-empty">Cadastre ou reative uma conta antes de criar uma conta de caixa.</p>';
    return '<p><button type="button" class="modal-btn confirm" data-ald-new="cashaccount"'+(bloqueado?' disabled':'')+'>Novo caixa</button></p>';
  }
  return '';
}
function initAlladinCrud(){
  const ov=document.getElementById('alladinModalOverlay');
  const box=document.getElementById('alladinModalBox');
  const section=document.getElementById('alladin');
  if(!ov||!box||!section) return;
  // Delegação: UM listener por superfície — nenhum bind por abertura.
  section.addEventListener('click',e=>{
    const novo=e.target.closest('button[data-ald-new]');
    if(novo && !novo.disabled){ alladinAbrirForm(novo.dataset.aldNew,'create',null); return; }
    const ed=e.target.closest('button[data-ald-edit]');
    if(ed && !ed.disabled){ alladinAbrirForm(ed.dataset.aldEdit,'edit',ed.dataset.aldId); return; }
    const st=e.target.closest('button[data-ald-status]');
    if(st && !st.disabled){ alladinConfirmarStatus(st.dataset.aldTipo,st.dataset.aldId,st.dataset.aldStatus); }
  });
  box.addEventListener('click',e=>{
    const b=e.target.closest('button[data-ald-act]');
    if(!b) return;
    const act=b.dataset.aldAct;
    if(act==='cancelar') alladinModalDismiss();
    else if(act==='salvar') alladinSubmit();
    else if(act==='manter') alladinResolverWarning('manter');
    else if(act==='inativar-novo') alladinResolverWarning('inativar');
    else if(act==='status-confirmado') alladinExecutarStatus();
  });
  ov.addEventListener('click',e=>{ if(e.target===ov) alladinModalDismiss(); });
  box.addEventListener('keydown',e=>{
    if(e.key==='Enter' && e.target.tagName==='INPUT'){
      e.preventDefault();
      if(alladinForm.estado==='EDITING') alladinSubmit();   // COMMITTED/SUBMITTING: Enter inerte
    }
    if(e.key==='Tab'){
      const f=alladinFocusables(); if(!f.length) return;
      const first=f[0], last=f[f.length-1];
      if(e.shiftKey && document.activeElement===first){ e.preventDefault(); last.focus(); }
      else if(!e.shiftKey && document.activeElement===last){ e.preventDefault(); first.focus(); }
    }
  });
  document.addEventListener('keydown',e=>{
    if(e.key==='Escape' && alladinModalAberto()) alladinModalDismiss();
  });
}
initAlladinCrud();
