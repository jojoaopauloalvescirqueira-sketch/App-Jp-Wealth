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
    ['Nome','Símbolo','Família / Classe','Moeda','Status'],
    lista.map(r=>[
      esc(alladinTexto(r.name)),
      esc(alladinTexto(r.symbol)),
      esc([r.instrumentFamily,r.assetClass].filter(Boolean).join(' · ')||'—'),
      esc(alladinTexto(r.currency)),
      esc(alladinStatus(r.recordStatus,ALLADIN_STATUS_LABEL))
    ]));
}
function alladinRenderAssets(el){
  const lista=JPWAlladin.leitura.assets();
  if(!lista.length){ el.innerHTML='<h2>Bens</h2>'+alladinVazio('assets'); return; }
  el.innerHTML='<h2>Bens</h2>'+alladinTabela(
    ['Nome','Natureza / Categoria','Finalidade','Status'],
    lista.map(r=>[
      esc(alladinTexto(r.name)),
      esc([r.nature,r.category].filter(Boolean).join(' · ')||'—'),
      esc(alladinTexto(r.strategicPurpose)),
      // Dois eixos do C2: recordStatus (registro) × lifecycleStatus (vida do bem).
      esc(alladinStatus(r.recordStatus,ALLADIN_STATUS_LABEL))+
        (r.lifecycleStatus?' · '+esc(alladinStatus(r.lifecycleStatus,ALLADIN_LIFECYCLE_LABEL)):'')
    ]));
}
function alladinRenderAccounts(el){
  const lista=JPWAlladin.leitura.accounts();
  if(!lista.length){ el.innerHTML='<h2>Contas</h2>'+alladinVazio('accounts'); return; }
  el.innerHTML='<h2>Contas</h2>'+alladinTabela(
    ['Nome','Instituição','Tipo','Status'],
    lista.map(r=>[
      esc(alladinTexto(r.name)),
      esc(alladinTexto(r.institution)),
      esc(alladinTexto(r.accountType)),
      esc(alladinStatus(r.recordStatus,ALLADIN_STATUS_LABEL))
    ]));
}
function alladinRenderCash(el){
  const lista=JPWAlladin.leitura.cashAccounts();
  if(!lista.length){ el.innerHTML='<h2>Caixa</h2>'+alladinVazio('cashAccounts'); return; }
  // Conta-mãe resolvida DENTRO do snapshot de leitura — nunca no agregado vivo.
  const contas={};
  JPWAlladin.leitura.accounts().forEach(a=>{ if(a.accountId) contas[a.accountId]=a.name; });
  el.innerHTML='<h2>Caixa</h2>'+
    '<p class="expl">Cadastro das contas de caixa por moeda — dinheiro disponível não pertence a este ciclo.</p>'+
    alladinTabela(
    ['Moeda','Conta-mãe','Status'],
    lista.map(r=>[
      esc(alladinTexto(r.currency)),
      esc(alladinTexto(contas[r.accountId]||r.accountId)),
      esc(alladinStatus(r.recordStatus,ALLADIN_STATUS_LABEL))
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
