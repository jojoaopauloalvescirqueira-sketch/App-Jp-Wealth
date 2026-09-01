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
  ['cashAccounts','alladinCash'],
  // ALD-05 S1 — destinos ECONÔMICOS, read-only. Os quatro acima continuam
  // cadastrais e sem conteúdo econômico; a fronteira é visível na navegação.
  ['ledger','alladinLedger'],
  ['balances','alladinBalances'],
  ['positions','alladinPositions']
];
const ALLADIN_EMPTY={
  instruments:'Nenhum instrumento cadastrado.',
  assets:'Nenhum bem cadastrado.',
  accounts:'Nenhuma conta cadastrada.',
  cashAccounts:'Nenhuma conta de caixa cadastrada.',
  // Empty ECONÔMICO só existe sob qualidade válida — ver alladinIndisponivel().
  ledger:'Nenhum lançamento registrado.',
  balances:'Nenhuma conta de caixa cadastrada.',
  positions:'Nenhuma posição em aberto.'
};
// Rótulos de status legíveis; valor fora do vocabulário deste build (schema
// futuro) é exibido como veio — projetar não é normalizar.
const ALLADIN_STATUS_LABEL={ACTIVE:'Ativo',INACTIVE:'Inativo'};
// C3-S2-C · F-1: as chaves são EXATAMENTE o catálogo fechado do domínio
// (ALD_LIFECYCLE_STATUS). Rótulo inventado seria vocabulário que o domínio não
// tem, e ausência faria um estado real aparecer como código cru sem necessidade.
// Um assert estrutural da suíte compara este mapa com o catálogo a cada rodada.
const ALLADIN_LIFECYCLE_LABEL={ACTIVE:'Em uso',SOLD:'Vendido',DISPOSED:'Descartado',
  DONATED:'Doado',LOST:'Perdido',WRITTEN_OFF:'Baixado'};

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
  if(!lista.length){ el.innerHTML='<h2>Instrumentos</h2>'+alladinBotaoNovo('instruments')+alladinVazio('instruments'); return; }
  el.innerHTML='<h2>Instrumentos</h2>'+alladinBotaoNovo('instruments')+alladinTabela(
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
  if(!lista.length){ el.innerHTML='<h2>Bens</h2>'+alladinBotaoNovo('assets')+alladinVazio('assets'); return; }
  el.innerHTML='<h2>Bens</h2>'+alladinBotaoNovo('assets')+alladinTabela(
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
// ============ ALLADIN · ALD-05 S1 — PROJEÇÃO ECONÔMICA (READ-ONLY) ==========
// A primeira superfície econômica VISÍVEL do Alladin. Ela PROJETA read-models
// já publicados — não cria regra, não soma, não ordena, não formata dinheiro e
// não deriva direção. Todo número exibido chega pronto; a única lógica nova é
// escolher rótulo e distinguir OK / BLOCKING / EMPTY.
//
// INVARIANTE CENTRAL: read-model indisponível JAMAIS pode virar zero, lista
// vazia, "sem dados" ou tela de aparência normal. Um saldo que some errado é
// pior do que um saldo ausente — o domínio já fecha essa porta na leitura
// (ALD_CASH_DELTA_AUSENTE, integridade estrutural), e a UI seria o último lugar
// onde a mesma falha poderia renascer, agora como pixel.
const ALLADIN_EVENTO_LABEL={
  DEPOSIT:'Aporte', WITHDRAWAL:'Retirada', TRANSFER:'Transferência',
  BUY:'Compra', SELL:'Venda', FEE:'Taxa', TAX:'Imposto',
  ADJUSTMENT_CREDIT:'Ajuste (crédito)', ADJUSTMENT_DEBIT:'Ajuste (débito)'
};
const ALLADIN_TX_STATUS_LABEL={POSTED:'Efetivado', REVERSED:'Estornado'};

// Aviso de indisponibilidade. Reusa .session-warning (mesmo componente do banner
// de schema futuro) — sem CSS novo. É TEXTO, nunca só cor: quem não distingue
// cor precisa ler a mesma informação.
function alladinIndisponivel(titulo, issues){
  const lista=(issues&&issues.length)
    ? '<ul class="alladin-issues">'+issues.map(i=>'<li>'+esc(String(i))+'</li>').join('')+'</ul>'
    : '<p>Nenhum diagnóstico específico foi devolvido pelo domínio.</p>';
  return '<div class="session-warning" role="status"><strong>'+esc(titulo)+'</strong>'+lista+'</div>';
}
// Sentinela de integridade para os Lançamentos (MD-2/A).
// `leitura.transactions()` NÃO tem envelope de qualidade: ele filtra registros
// ilegíveis EM SILÊNCIO e não checa integridade estrutural nem schema futuro.
// Projetar essa lista direto exibiria um ledger silenciosamente filtrado como
// se fosse normal — exatamente o que o invariante proíbe. Enquanto o envelope
// próprio não existe (dívida registrada, slice futura), a confiabilidade vem de
// `posicoes()`, que é global e fail-closed pelos MESMOS motivos (integridade
// estrutural, registro ilegível, cadastro órfão, moeda divergente, schema
// futuro), somada a `compat()`.
//
// Isto é guarda de APRESENTAÇÃO, não regra econômica: a UI não interpreta o
// veredito, apenas se recusa a desenhar quando o domínio não garante o dado.
// Conservador de propósito — bloquear a mais é seguro, a menos não é.
function alladinSentinelaLedger(){
  const compat=JPWAlladin.compat();
  if(compat && compat.readOnly){
    return { ok:false, issues:[compat.reason||'READ_ONLY_FUTURE_SCHEMA'] };
  }
  const pos=JPWAlladin.leitura.posicoes();
  if(!pos.available) return { ok:false, issues:(pos.issues||[]).slice() };
  return { ok:true, issues:[] };
}
// Rótulos cadastrais resolvidos DENTRO dos snapshots de leitura — nunca no
// agregado vivo, como já faz o painel de Caixa.
function alladinCatalogoLabels(){
  const contas={}, caixas={}, instrumentos={};
  JPWAlladin.leitura.accounts().forEach(a=>{ if(a.accountId) contas[a.accountId]=a.name; });
  JPWAlladin.leitura.instruments().forEach(i=>{ if(i.instrumentId) instrumentos[i.instrumentId]=i.symbol||i.name; });
  // CashAccount não tem nome próprio no cadastro: o rótulo legível é
  // moeda + conta-mãe. Duas caixas da MESMA moeda sob a MESMA conta colidem —
  // e duas linhas idênticas com saldos diferentes, ou uma transferência que se
  // lê "BRL · XP → BRL · XP", descrevem um fato falso. Onde o rótulo colide, o
  // identificador canônico entra para desambiguar; onde não colide, o rótulo
  // fica limpo. Isto é resolução de LABEL, não regra econômica.
  const legivel={}, quantos={};
  JPWAlladin.leitura.cashAccounts().forEach(c=>{
    if(!c.cashAccountId) return;
    const mae=contas[c.accountId]||c.accountId;
    const rotulo=(c.currency?c.currency+' · ':'')+alladinTexto(mae);
    legivel[c.cashAccountId]=rotulo;
    quantos[rotulo]=(quantos[rotulo]||0)+1;
  });
  Object.keys(legivel).forEach(id=>{
    const rotulo=legivel[id];
    caixas[id]=quantos[rotulo]>1 ? rotulo+' · '+id : rotulo;
  });
  return { contas, caixas, instrumentos };
}
function alladinCaixaLabel(cat,id){ return id ? (cat.caixas[id]||String(id)) : '—'; }
// Rótulo de evento: tipo fora do vocabulário DESTE build aparece CRU. Traduzir
// o desconhecido seria inventar interpretação; omitir seria esconder um fato.
function alladinEventoLabel(tipo){
  if(tipo===undefined||tipo===null||tipo==='') return '—';
  return ALLADIN_EVENTO_LABEL[tipo] || String(tipo);
}
function alladinEventoCelula(tx){
  if(tx.eventType==='REVERSAL'){
    const orig=tx.reversedEventType;
    const rotulo=ALLADIN_EVENTO_LABEL[orig]||(orig===undefined||orig===null?'—':String(orig));
    return esc('Estorno de '+rotulo);
  }
  return esc(alladinEventoLabel(tx.eventType));
}
// Detalhe por família. NENHUMA direção é calculada aqui: `amount` é magnitude e
// a direção mora no eventType, que já está na coluna Evento. Derivar sinal por
// linha seria reimplementar ALD_CASH_DELTA na UI — e sairia ERRADO no TRANSFER
// (∓ conforme a conta observada) e enganoso em BUY/SELL (o efeito líquido
// embute fees/taxes). O efeito em caixa pertence a saldoDeCaixa, e é a tela
// Saldos que o mostra.
function alladinTxDetalhe(tx,cat){
  const partes=[];
  if(tx.eventType==='TRANSFER'){
    partes.push(esc(alladinCaixaLabel(cat,tx.sourceCashAccountId))+' &rarr; '+
                esc(alladinCaixaLabel(cat,tx.destinationCashAccountId)));
  }
  if(tx.eventType==='BUY'||tx.eventType==='SELL'){
    const papel=[tx.quantity,cat.instrumentos[tx.instrumentId]||tx.instrumentId]
      .filter(v=>v!==undefined&&v!==null&&v!=='').map(String).join(' ');
    if(papel) partes.push(esc(papel));
    // fees/taxes seguem EMBUTIDOS no trade — exibidos como detalhe, jamais
    // recombinados num líquido calculado pela UI.
    const custos=[];
    if(tx.fees!==undefined) custos.push('taxas '+JPWAlladin.money.format({amount:tx.fees,currency:tx.currency}));
    if(tx.taxes!==undefined) custos.push('impostos '+JPWAlladin.money.format({amount:tx.taxes,currency:tx.currency}));
    if(custos.length) partes.push(esc(custos.join(' · ')));
  }
  // O reason é o que torna o ajuste AUDITÁVEL: ele é o único evento cujo valor
  // não pode ser conferido contra nada. Escondê-lo esvaziaria a decisão do S4.
  if(tx.reason!==undefined&&tx.reason!==null&&tx.reason!=='') partes.push(esc(String(tx.reason)));
  if(tx.eventType==='REVERSAL'&&tx.reversalOf) partes.push(esc(String(tx.reversalOf)));
  if(tx.flowScope!==undefined&&tx.flowScope!==null&&tx.flowScope!=='') partes.push(esc(String(tx.flowScope)));
  if(tx.note!==undefined&&tx.note!==null&&tx.note!=='') partes.push(esc(String(tx.note)));
  return partes.length?partes.join('<br>'):'&mdash;';
}
// effectiveAt é o fato ECONÔMICO (e a chave de ordenação); recordedAt é o fato
// de AUDITORIA. Divergir é informação, não ruído — por isso os dois ficam
// sempre visíveis, e recordedAt nunca vai para title/tooltip: informação de
// auditoria não pode depender de mouse nem sumir para quem usa teclado.
function alladinDataCelula(tx){
  return esc(alladinTexto(tx.effectiveAt))+
    '<br><span class="alladin-sub">registrado em '+esc(alladinTexto(tx.recordedAt))+'</span>';
}
function alladinRenderLedger(el){
  const cab='<h2>Lançamentos</h2>';
  const sentinela=alladinSentinelaLedger();
  if(!sentinela.ok){
    // Sob BLOCKING: nenhuma tabela, nenhum número, nenhum texto de empty — e
    // NENHUM convite à escrita (ALD-05 S2): o CTA não é renderizado. Escrever
    // sobre agregado que a leitura recusa só produziria a recusa estrutural do
    // domínio; a UX não convida, mas a autoridade continua sendo aldMutate —
    // se o estado mudar entre render e submit, é o domínio que decide.
    el.innerHTML=cab+alladinIndisponivel(
      'Lançamentos indisponíveis — o agregado não passou na verificação de integridade.',
      sentinela.issues);
    return;
  }
  const cta=alladinTxBotaoNovo();
  const lista=JPWAlladin.leitura.transactions();
  if(!lista.length){ el.innerHTML=cab+cta+alladinVazio('ledger'); return; }
  const cat=alladinCatalogoLabels();
  // ORDEM: exatamente a entregue pelo read-model (ordem econômica
  // effectiveAt, recordedAt, transactionId). A UI não reordena — reordenar
  // seria a UI decidindo o que é ordem econômica.
  el.innerHTML=cab+cta+alladinTabela(
    ['Efetivação','Evento','Detalhe','Valor','Conta / Caixa','Status'],
    lista.map(tx=>[
      alladinDataCelula(tx),
      alladinEventoCelula(tx),
      alladinTxDetalhe(tx,cat),
      esc(JPWAlladin.money.format({amount:tx.amount,currency:tx.currency})),
      esc(alladinCaixaLabel(cat,tx.cashAccountId||tx.sourceCashAccountId)),
      esc(alladinStatus(tx.status,ALLADIN_TX_STATUS_LABEL))
    ]));
}
function alladinRenderBalances(el){
  const cab='<h2>Saldos</h2>';
  const contas=JPWAlladin.leitura.cashAccounts();
  // Empty CADASTRAL — ausência de conta não é saldo zero, e os dois não podem
  // compartilhar a mesma tela.
  if(!contas.length){ el.innerHTML=cab+alladinVazio('balances'); return; }
  const cat=alladinCatalogoLabels();
  el.innerHTML=cab+alladinTabela(
    ['Conta de caixa','Saldo','Lançamentos considerados','Qualidade'],
    contas.map(c=>{
      // UM saldoDeCaixa por conta. A UI não soma transação nenhuma.
      const s=JPWAlladin.leitura.saldoDeCaixa(c.cashAccountId);
      const nome=esc(alladinCaixaLabel(cat,c.cashAccountId));
      if(!s.available){
        // BLOCKING por linha: jamais R$ 0,00 por fallback, jamais célula vazia.
        return [nome,'<strong>Indisponível</strong>','&mdash;',
                esc((s.issues||[]).join(' · ')||'BLOCKING')];
      }
      return [nome,
        esc(JPWAlladin.money.format({amount:s.amount,currency:s.currency})),
        esc(String(s.consideradas)),
        esc(alladinTexto(s.quality))];
    }));
}
function alladinRenderPositions(el){
  const cab='<h2>Posições</h2>';
  const p=JPWAlladin.leitura.posicoes();
  if(!p.available){
    // positions:[] sob BLOCKING NUNCA pode virar "Nenhuma posição".
    el.innerHTML=cab+alladinIndisponivel(
      'Posições indisponíveis — o agregado não passou na verificação de integridade.',
      (p.issues||[]).slice());
    return;
  }
  if(!p.positions.length){ el.innerHTML=cab+alladinVazio('positions'); return; }
  const cat=alladinCatalogoLabels();
  el.innerHTML=cab+alladinTabela(
    ['Instrumento','Conta','Quantidade','Lançamentos considerados'],
    p.positions.map(pos=>[
      esc(alladinTexto(cat.instrumentos[pos.instrumentId]||pos.instrumentId)),
      esc(alladinTexto(cat.contas[pos.accountId]||pos.accountId)),
      // VERBATIM: a string canônica do read-model, apenas escapada. Sem
      // Number(), parseFloat, toFixed, separador de milhar ou truncamento.
      // Negativa aparece fiel — sem rótulo de short, sem cor de alerta: o
      // domínio é explícito em que negativo NÃO tem semântica de short. Valor
      // longo rola dentro da célula; cortar seria inventar outro número.
      esc(String(pos.quantity)),
      esc(String(pos.consideradas))
    ]));
}
const ALLADIN_RENDERERS={
  instruments:alladinRenderInstruments,
  assets:alladinRenderAssets,
  accounts:alladinRenderAccounts,
  cashAccounts:alladinRenderCash,
  ledger:alladinRenderLedger,
  balances:alladinRenderBalances,
  positions:alladinRenderPositions
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
    // A view inativa não RETÉM DOM: um painel renderizado antes de o write gate
    // fechar guardaria botões de mutação sem `disabled` — controles obsoletos
    // que o `inert` esconde mas não corrige. Só a view ativa existe no DOM, e
    // ela sempre vem da leitura canônica desta renderização.
    if(active && ALLADIN_RENDERERS[key]) ALLADIN_RENDERERS[key](el);
    else if(!active) el.innerHTML='';
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

// ============ ALLADIN · MANUTENÇÃO CADASTRAL (C3-S2-A + C3-S2-B · N1) ========
// Escrita cadastral via UI das QUATRO entidades: Account/CashAccount (S2-A) e
// Instrument/Asset (S2-B) — Create/Edit + recordStatus.
// Toda mutação passa por JPWAlladin.cadastro / setRecordStatus — a UI
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
let alladinForm={estado:'IDLE', tipo:null, modo:null, alvoId:null, recordId:null, foco:null, avisos:[], snapshot:null};

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
  alladinForm={estado:'IDLE', tipo:null, modo:null, alvoId:null, recordId:null, foco:null, avisos:[], snapshot:null};
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

// ---- formulários (Account / CashAccount) -----------------------------------
function alladinFormAccountHTML(reg){
  const tipos=JPWAlladin.catalogos().starter.accountType;
  const dl=document.getElementById('alladinAccountTypes');
  if(dl) dl.innerHTML=tipos.map(t=>'<option value="'+esc(t)+'"></option>').join('');
  return '<h3 id="alladinModalTitle">'+(reg?'Editar conta':'Nova conta')+'</h3>'+
    '<p class="modal-sub">Cadastro de conta de custódia ou instituição — dinheiro e movimentos não pertencem a este ciclo.</p>'+
    alladinCampo('alladinFldName','Nome',reg&&reg.name)+
    alladinCampo('alladinFldInstitution','Instituição',reg&&reg.institution)+
    alladinCampo('alladinFldAccountType','Tipo',reg&&reg.accountType,'list="alladinAccountTypes"')+
    '<div class="modal-actions"><button type="button" class="modal-btn cancel" data-ald-act="cancelar">Cancelar</button>'+
    '<button type="button" class="modal-btn confirm" data-ald-act="salvar">Salvar</button></div>';
}
function alladinFormCashHTML(reg){
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
    '<label class="field"><span>Conta-mãe</span><select id="alladinFldAccountId">'+atualInativa+opts+'</select></label>'+
    alladinCampo('alladinFldCurrency','Moeda (código de 3 letras)',reg&&reg.currency,'maxlength="3" autocapitalize="characters"')+
    '<div class="modal-actions"><button type="button" class="modal-btn cancel" data-ald-act="cancelar">Cancelar</button>'+
    '<button type="button" class="modal-btn confirm" data-ald-act="salvar">Salvar</button></div>';
}

// ---- formulários ricos (Instrument / Asset — C3-S2-B) -----------------------
// Conversão %↔bp por aritmética de STRING/INTEIRO (padrão aldParseMoney): duas
// casas decimais = representação EXATA de 1bp; float jamais entra no caminho.
function alladinPctParaBp(txt){
  const m=/^(\d{1,3})(?:[.,](\d{1,2}))?$/.exec(String(txt||'').trim());
  if(!m) return null;
  const bp=parseInt(m[1],10)*100+parseInt(((m[2]||'')+'00').slice(0,2),10);
  return bp>10000?null:bp;   // espelho de UX do teto por owner; o domínio decide
}
function alladinBpParaPct(bp){
  const s=String(bp);
  const inteiro=s.length>2?s.slice(0,-2):'0';
  const frac=s.padStart(3,'0').slice(-2).replace(/0+$/,'');
  return inteiro+(frac?','+frac:'');
}
// Mapa código→texto humano dos avisos REAIS do domínio. O código permanece
// visível entre parênteses: humanizar jamais perde a identidade do aviso, e
// código desconhecido é exibido cru (projeção honesta, nunca descartado).
const ALLADIN_AVISO_TEXTO={
  MOEDA_FORA_DO_SUPORTE_DE_RUNTIME:'A moeda é válida e ficou gravada, mas está fora do suporte deste build',
  OWNERSHIP_PARCIAL_NAO_ATRIBUIDA:'A participação informada não soma o total — a parcela restante fica não atribuída',
  OWNER_NOME_DUPLICADO:'Há proprietários com o mesmo nome',
  DUPLICADO_SYMBOL_EXCHANGE_CURRENCY:'Já existe instrumento com o mesmo símbolo, bolsa e moeda',
  DUPLICADO_MOEDA_NA_CONTA:'Já existe conta de caixa desta moeda na mesma conta',
};
function alladinAvisoTexto(code){
  const c=String(code);
  if(ALLADIN_AVISO_TEXTO[c]) return ALLADIN_AVISO_TEXTO[c]+' ('+c+')';
  if(c.indexOf('DUPLICADO_IDENTIFICADOR_EXTERNO:')===0)
    return 'Já existe instrumento com o mesmo identificador externo ('+c+')';
  return c;
}
function alladinAvisosResumo(avisos){
  return 'Aviso: '+avisos.map(alladinAvisoTexto).join(' · ')+'.';
}
// Erro nos formulários ricos: injetado IN-PLACE — o formulário não é
// re-renderizado, logo o rascunho do operador fica intacto por construção.
function alladinErroInline(msg){
  const box=document.getElementById('alladinModalBox');
  if(!box) return;
  let err=box.querySelector('.session-error');
  if(!err){
    const sub=box.querySelector('.modal-sub');
    if(sub){ sub.insertAdjacentHTML('afterend','<div class="session-error" role="alert"></div>'); err=box.querySelector('.session-error'); }
  }
  if(err) err.textContent=msg;
}
function alladinDatalist(id,valores){
  const dl=document.getElementById(id);
  if(dl) dl.innerHTML=valores.map(v=>'<option value="'+esc(v)+'"></option>').join('');
}
function alladinExtRowHTML(k,v){
  return '<div class="field" data-ald-ext-row><span>Identificador</span>'+
    '<input type="text" data-ald-ext-k list="alladinIdKeys" placeholder="chave (ex.: isin)" value="'+esc(k==null?'':k)+'" autocomplete="off">'+
    '<input type="text" data-ald-ext-v placeholder="conteúdo do identificador" value="'+esc(v==null?'':v)+'" autocomplete="off">'+
    '<button type="button" class="modal-btn cancel" data-ald-act="ext-del">Remover linha</button></div>';
}
function alladinOwnerRowHTML(o){
  o=o||{};
  return '<div data-ald-owner-row>'+
    '<label class="field"><span>Nome do proprietário</span>'+
    '<input type="text" data-ald-owner-nome value="'+esc(o.name==null?'':o.name)+'" autocomplete="off"></label>'+
    '<label class="field"><span>Participação (%)</span>'+
    '<input type="text" data-ald-owner-pct inputmode="decimal" value="'+(o.shareBp==null?'':esc(alladinBpParaPct(o.shareBp)))+'" autocomplete="off"></label>'+
    '<p><label><input type="checkbox" data-ald-owner-self'+(o.isSelf===true?' checked':'')+'> Sou eu</label> '+
    '<button type="button" class="modal-btn cancel" data-ald-act="owner-del">Remover</button></p></div>';
}
function alladinOwnersAtualizarTotal(){
  const box=document.getElementById('alladinModalBox');
  const tot=box&&box.querySelector('[data-ald-owner-total]');
  if(!tot) return;
  const rows=[...box.querySelectorAll('[data-ald-owner-row]')];
  let bp=0, invalido=false;
  for(const row of rows){
    const t=row.querySelector('[data-ald-owner-pct]').value.trim();
    if(!t) continue;
    const v=alladinPctParaBp(t);
    if(v===null){ invalido=true; break; }
    bp+=v;
  }
  tot.hidden=!rows.length;
  tot.textContent='Participação atribuída: '+(invalido?'—':alladinBpParaPct(bp)+'%');
}
// DC-5 na tela: o histórico vem EXCLUSIVAMENTE da leitura canônica — a UI não
// escreve, não reconstrói e não interpreta o algoritmo; entrada de forma
// desconhecida é omitida da linha (projetar não é normalizar).
function alladinHistoricoHTML(reg){
  const h=reg&&reg.symbolHistory;
  if(!Array.isArray(h)||!h.length) return '';
  const itens=h.map(e=>{
    if(!e||typeof e!=='object'||typeof e.symbol!=='string') return null;
    const d=(typeof e.to==='string'&&/^\d{4}-\d{2}-\d{2}/.test(e.to))
      ?' (até '+e.to.slice(8,10)+'/'+e.to.slice(5,7)+'/'+e.to.slice(0,4)+')':'';
    return esc(e.symbol+d);
  }).filter(Boolean);
  return itens.length?'<p class="modal-sub" data-ald-symbol-history>Símbolos anteriores: '+itens.join(' · ')+'</p>':'';
}
// C3-S2-C · B-2: valor de vocabulário fechado que ESTE build não conhece ganha
// opção própria, selecionada e rotulada com honestidade. Sem ela o navegador
// escolheria a primeira opção e o patch-diff reescreveria, em silêncio, um valor
// que o operador nunca tocou — exatamente o que o read-model promete não fazer
// ("projetar não é normalizar"). Preservar não é legitimar: o domínio segue
// recusando o ato, e a saída é o operador escolher deliberadamente um valor vivo.
function alladinValorForaDoVocabulario(reg,valor,catalogo){
  return !!reg && !!valor && catalogo.indexOf(valor)<0;
}
function alladinOpcaoDesconhecida(reg,valor,catalogo){
  if(!alladinValorForaDoVocabulario(reg,valor,catalogo)) return '';
  return '<option value="'+esc(valor)+'" selected>'+esc(valor)+' — valor não reconhecido por esta versão</option>';
}
function alladinFormInstrumentHTML(reg){
  const cat=JPWAlladin.catalogos();
  alladinDatalist('alladinAssetClasses',cat.starter.assetClass);
  const fam=(reg&&reg.instrumentFamily)||'';
  const famOpts=(reg?'':'<option value="" selected disabled>Selecione…</option>')+
    alladinOpcaoDesconhecida(reg,fam,cat.fechados.instrumentFamily)+
    cat.fechados.instrumentFamily.map(f=>'<option value="'+esc(f)+'"'+(f===fam?' selected':'')+'>'+esc(f)+'</option>').join('');
  const ext=(reg&&reg.externalIdentifiers&&typeof reg.externalIdentifiers==='object'&&!Array.isArray(reg.externalIdentifiers))?reg.externalIdentifiers:{};
  const cripto=fam==='CRYPTO';
  // DH-S2B-1 (opção C) + DH-S2C-1: `network` tem campo explícito e é a ÚNICA
  // fonte da chave — nunca vira linha genérica. O campo PERMANECE visível fora
  // de CRYPTO enquanto tiver valor: sair de cripto preserva a rede, e removê-la
  // exige o gesto explícito de limpar o campo (C3-S2-C · B-1).
  const network=(typeof ext.network==='string')?ext.network:'';
  const mostrarRede=cripto||!!network;
  const genericas=Object.keys(ext).filter(k=>k!=='network');
  const moeda=reg
    ?'<label class="field"><span>Moeda</span><input type="text" id="alladinFldCurrency" value="'+esc(reg.currency||'')+'" disabled>'+
     '<span class="note">A moeda é definida na criação e não pode ser alterada neste cadastro.</span></label>'
    :alladinCampo('alladinFldCurrency','Moeda (código de 3 letras)','','maxlength="3" autocapitalize="characters"');
  return '<h3 id="alladinModalTitle">'+(reg?'Editar instrumento':'Novo instrumento')+'</h3>'+
    '<p class="modal-sub">Cadastro de identidade do instrumento — dinheiro e movimentos não pertencem a este ciclo.</p>'+
    alladinCampo('alladinFldName','Nome',reg&&reg.name)+
    alladinCampo('alladinFldSymbol','Símbolo',reg&&reg.symbol,'maxlength="32"')+
    '<label class="field"><span>Família</span><select id="alladinFldFamily">'+famOpts+'</select></label>'+
    '<div id="alladinFldNetworkWrap"'+(mostrarRede?'':' hidden')+'>'+
      '<label class="field"><span>Rede (network)</span>'+
      '<input type="text" id="alladinFldNetwork" value="'+esc(network)+'" autocomplete="off">'+
      '<span class="note">Obrigatória para cripto. Se preenchida, é preservada mesmo fora de cripto — limpe o campo para removê-la.</span></label></div>'+
    alladinCampo('alladinFldAssetClass','Classe',reg&&reg.assetClass,'list="alladinAssetClasses"')+
    moeda+
    alladinCampo('alladinFldExchange','Bolsa / mercado (opcional)',reg&&reg.exchange)+
    alladinCampo('alladinFldCountry','País (opcional)',reg&&reg.country)+
    '<p class="modal-sub">Identificadores externos (opcional)</p>'+
    '<div data-ald-ext-lista>'+genericas.map(k=>alladinExtRowHTML(k,ext[k])).join('')+'</div>'+
    '<p><button type="button" class="modal-btn cancel" data-ald-act="ext-add">+ Adicionar identificador</button></p>'+
    alladinHistoricoHTML(reg)+
    '<div class="modal-actions"><button type="button" class="modal-btn cancel" data-ald-act="cancelar">Cancelar</button>'+
    '<button type="button" class="modal-btn confirm" data-ald-act="salvar">Salvar</button></div>';
}
function alladinFormAssetHTML(reg){
  const cat=JPWAlladin.catalogos();
  alladinDatalist('alladinNatures',cat.starter.nature);
  alladinDatalist('alladinPurposes',cat.starter.strategicPurpose);
  const rm=(reg&&reg.recordMode)||'';
  const modos=(reg?'':'<option value="" selected disabled>Selecione…</option>')+
    alladinOpcaoDesconhecida(reg,rm,cat.fechados.recordMode)+
    [['INDIVIDUAL','Individual'],['GROUPED','Agrupado']]
      .map(([v,l])=>'<option value="'+v+'"'+(v===rm?' selected':'')+'>'+l+'</option>').join('');
  const owners=(reg&&Array.isArray(reg.owners))?reg.owners:[];
  const tags=(reg&&Array.isArray(reg.tags))?reg.tags.join(', '):'';
  // lifecycleStatus: NUNCA input, NUNCA hidden field, NUNCA patch — texto puro.
  const lifecycle=(reg&&reg.lifecycleStatus)
    ?'<p class="modal-sub" data-ald-lifecycle>Estado patrimonial: '+esc(alladinStatus(reg.lifecycleStatus,ALLADIN_LIFECYCLE_LABEL))+
     ' — o estado patrimonial é controlado pelas movimentações patrimoniais e não pode ser alterado neste cadastro.</p>':'';
  let totalTxt='0';
  if(owners.length){
    let bp=0; for(const o of owners){ if(o&&typeof o.shareBp==='number') bp+=o.shareBp; }
    totalTxt=alladinBpParaPct(bp);
  }
  return '<h3 id="alladinModalTitle">'+(reg?'Editar bem':'Novo bem')+'</h3>'+
    '<p class="modal-sub">Cadastro de identidade do bem — dinheiro e movimentos não pertencem a este ciclo.</p>'+
    alladinCampo('alladinFldName','Nome',reg&&reg.name)+
    alladinCampo('alladinFldNature','Natureza',reg&&reg.nature,'list="alladinNatures"')+
    '<label class="field"><span>Modo de registro</span><select id="alladinFldRecordMode">'+modos+'</select></label>'+
    alladinCampo('alladinFldCategory','Categoria (opcional)',reg&&reg.category)+
    alladinCampo('alladinFldSubcategory','Subcategoria (opcional)',reg&&reg.subcategory)+
    alladinCampo('alladinFldPurpose','Finalidade estratégica (opcional)',reg&&reg.strategicPurpose,'list="alladinPurposes"')+
    alladinCampo('alladinFldGroup','Grupo estratégico (opcional)',reg&&reg.strategicGroup)+
    alladinCampo('alladinFldLocation','Localização (opcional)',reg&&reg.location)+
    '<label class="field"><span>Data de aquisição (opcional)</span>'+
    '<input type="date" id="alladinFldAcqDate" value="'+esc((reg&&reg.acquisitionDate)||'')+'"></label>'+
    alladinCampo('alladinFldTags','Tags (separadas por vírgula, opcional)',tags)+
    '<p class="modal-sub">Proprietários (opcional)</p>'+
    '<div data-ald-owner-lista>'+owners.map(alladinOwnerRowHTML).join('')+'</div>'+
    '<p class="modal-sub" data-ald-owner-total'+(owners.length?'':' hidden')+'>Participação atribuída: '+totalTxt+'%</p>'+
    '<p><button type="button" class="modal-btn cancel" data-ald-act="owner-add">+ Adicionar proprietário</button></p>'+
    lifecycle+
    '<div class="modal-actions"><button type="button" class="modal-btn cancel" data-ald-act="cancelar">Cancelar</button>'+
    '<button type="button" class="modal-btn confirm" data-ald-act="salvar">Salvar</button></div>';
}
// Leitura dos formulários ricos. Devolve {dados} ou {erro} (erro de UX vai
// in-place e NADA é submetido). Linhas totalmente vazias são omitidas — o
// domínio recusa valor vazio, e omitir é a única leitura honesta da linha em
// branco; linha meio-preenchida é ambiguidade e recusa local.
function alladinLerFormRico(tipo){
  const box=document.getElementById('alladinModalBox');
  const v=(id)=>{ const el=document.getElementById(id); return el?el.value.trim():''; };
  if(tipo==='instrument'){
    const fam=v('alladinFldFamily');
    const dados={ name:v('alladinFldName'), symbol:v('alladinFldSymbol'), instrumentFamily:fam,
      assetClass:v('alladinFldAssetClass'), exchange:v('alladinFldExchange'), country:v('alladinFldCountry') };
    if(alladinForm.modo!=='edit') dados.currency=v('alladinFldCurrency').toUpperCase();
    if(!dados.name||!dados.symbol||!fam||!dados.assetClass||(alladinForm.modo!=='edit'&&!dados.currency))
      return { erro:'Preencha os campos obrigatórios antes de salvar.' };
    const ext={};
    for(const row of box.querySelectorAll('[data-ald-ext-row]')){
      const k=row.querySelector('[data-ald-ext-k]').value.trim();
      const val=row.querySelector('[data-ald-ext-v]').value.trim();
      if(!k&&!val) continue;
      if(!k||!val) return { erro:'Preencha chave e conteúdo do identificador (ou remova a linha).' };
      if(k==='__proto__'||k==='constructor'||k==='prototype') return { erro:'Esta chave de identificador é reservada e não pode ser usada.' };
      if(k==='network') return { erro:'A rede é informada no campo Rede deste formulário.' };
      if(Object.prototype.hasOwnProperty.call(ext,k)) return { erro:'Há identificadores com a mesma chave.' };
      ext[k]=val;
    }
    // B-1: a rede é lida SEMPRE, não só sob CRYPTO. Sair de cripto preserva o
    // que já existia; esvaziar o campo é o gesto explícito de remoção. Em CRYPTO
    // ela continua obrigatória — quem esvazia recebe a recusa, nada some.
    const net=v('alladinFldNetwork');
    if(fam==='CRYPTO'&&!net) return { erro:'Informe a rede (network) da cripto antes de salvar.' };
    if(net) ext.network=net;
    dados.externalIdentifiers=ext;
    return { dados };
  }
  const dados={ name:v('alladinFldName'), nature:v('alladinFldNature'), recordMode:v('alladinFldRecordMode'),
    category:v('alladinFldCategory'), subcategory:v('alladinFldSubcategory'),
    strategicPurpose:v('alladinFldPurpose'), strategicGroup:v('alladinFldGroup'),
    location:v('alladinFldLocation'), acquisitionDate:v('alladinFldAcqDate') };
  if(!dados.name||!dados.nature||!dados.recordMode) return { erro:'Preencha os campos obrigatórios antes de salvar.' };
  const listaTags=[];
  for(const t of v('alladinFldTags').split(',')){ const tt=t.trim(); if(tt&&listaTags.indexOf(tt)<0) listaTags.push(tt); }
  dados.tags=listaTags;
  const owners=[];
  for(const row of box.querySelectorAll('[data-ald-owner-row]')){
    const nome=row.querySelector('[data-ald-owner-nome]').value.trim();
    const pct=row.querySelector('[data-ald-owner-pct]').value.trim();
    const self=row.querySelector('[data-ald-owner-self]').checked;
    if(!nome&&!pct&&!self) continue;
    if(!nome||!pct) return { erro:'Preencha nome e participação de cada proprietário (ou remova a linha).' };
    const bp=alladinPctParaBp(pct);
    if(bp===null) return { erro:'Participação inválida: use até duas casas decimais, entre 0 e 100.' };
    const o={name:nome, shareBp:bp};
    if(self===true) o.isSelf=true;   // isSelf:false é omitido — espelho do que o domínio persiste
    owners.push(o);
  }
  dados.owners=owners;
  return { dados };
}
// Patch-diff do edit: compara com o snapshot de ABERTURA e envia SÓ o que
// mudou. Campo não tocado nem viaja — a fusão no domínio usa o registro ATUAL,
// então edição concorrente de outro campo sobrevive (contrato stale-modal).
// A comparação normaliza o snapshot pela MESMA higiene da leitura do form
// (trim, dedup de tags, isSelf só-true), senão fixture com espaço viraria
// "mudança" fantasma num edit de outro campo.
function alladinPatch(tipo,dados){
  const snap=alladinForm.snapshot||{};
  const canonExt=(o)=>{ const s={}; Object.keys(o||{}).sort().forEach(k=>{ s[String(k).trim()]=String(o[k]==null?'':o[k]).trim(); }); return JSON.stringify(s); };
  const canonTags=(l)=>{ const out=[]; for(const t of (Array.isArray(l)?l:[])){ const tt=String(t==null?'':t).trim(); if(tt&&out.indexOf(tt)<0) out.push(tt); } return JSON.stringify(out); };
  const canonOwners=(l)=>JSON.stringify((Array.isArray(l)?l:[]).map(o=>{ const r={name:String(o&&o.name==null?'':o.name).trim(), shareBp:o?o.shareBp:null}; if(o&&o.isSelf===true) r.isSelf=true; return r; }));
  const patch={};
  for(const k of Object.keys(dados)){
    const novo=dados[k], velho=snap[k];
    let mudou;
    if(k==='externalIdentifiers') mudou=canonExt(novo)!==canonExt(velho);
    else if(k==='tags') mudou=canonTags(novo)!==canonTags(velho);
    else if(k==='owners') mudou=canonOwners(novo)!==canonOwners(velho);
    else {
      const a=(novo===null||novo===undefined)?'':String(novo);
      const b=(velho===null||velho===undefined)?'':String(velho);
      mudou=a!==b;
    }
    if(mudou) patch[k]=novo;
  }
  return patch;
}
const ALLADIN_FORM_META={
  account:     { lista:()=>JPWAlladin.leitura.accounts(),     campoId:'accountId',     html:(r)=>alladinFormAccountHTML(r) },
  cashaccount: { lista:()=>JPWAlladin.leitura.cashAccounts(), campoId:'cashAccountId', html:(r)=>alladinFormCashHTML(r) },
  instrument:  { lista:()=>JPWAlladin.leitura.instruments(),  campoId:'instrumentId',  html:(r)=>alladinFormInstrumentHTML(r) },
  asset:       { lista:()=>JPWAlladin.leitura.assets(),       campoId:'assetId',       html:(r)=>alladinFormAssetHTML(r) },
};
function alladinAbrirForm(tipo,modo,alvoId){
  const meta=ALLADIN_FORM_META[tipo];
  if(!meta) return;
  alladinForm.estado='EDITING'; alladinForm.tipo=tipo; alladinForm.modo=modo; alladinForm.alvoId=alvoId||null;
  alladinForm.snapshot=null;
  let reg=null;
  if(modo==='edit'){
    reg=meta.lista().find(r=>r[meta.campoId]===alvoId)||null;
    if(!reg){ alladinModalClose(); return; }
    // Snapshot de abertura (DTO congelado da leitura): base do patch-diff do
    // edit — só campos efetivamente alterados viajam ao domínio.
    alladinForm.snapshot=reg;
  }
  const html=meta.html(reg);
  if(alladinModalAberto()){ document.getElementById('alladinModalBox').innerHTML=html; const f=alladinFocusables(); if(f.length) f[0].focus(); }
  else alladinModalOpen(html);
}

// ---- submissão --------------------------------------------------------------
function alladinLerFormulario(tipo){
  const v=(id)=>{ const el=document.getElementById(id); return el?el.value.trim():''; };
  if(tipo==='account') return { name:v('alladinFldName'), institution:v('alladinFldInstitution'), accountType:v('alladinFldAccountType') };
  return { accountId:v('alladinFldAccountId'), currency:v('alladinFldCurrency').toUpperCase() };
}
const ALLADIN_ATOS={
  account:     { add:(d)=>JPWAlladin.cadastro.addAccount(d),     edit:(i,d)=>JPWAlladin.cadastro.editAccount(i,d) },
  cashaccount: { add:(d)=>JPWAlladin.cadastro.addCashAccount(d), edit:(i,d)=>JPWAlladin.cadastro.editCashAccount(i,d) },
  instrument:  { add:(d)=>JPWAlladin.cadastro.addInstrument(d),  edit:(i,d)=>JPWAlladin.cadastro.editInstrument(i,d) },
  asset:       { add:(d)=>JPWAlladin.cadastro.addAsset(d),       edit:(i,d)=>JPWAlladin.cadastro.editAsset(i,d) },
};
// B-2: a recusa por vocabulário fechado desconhecido ganha texto humano. NÃO
// afirma que o dado está corrompido — ele é legítimo, apenas mais novo que este
// build — e NÃO altera coisa alguma: a saída é o operador escolher, ele mesmo,
// um valor que esta versão suporte.
const ALLADIN_ERRO_VOCABULARIO=['ALD_INSTRUMENT_FAMILY_INVALIDA','ALD_RECORD_MODE_INVALIDO'];
function alladinTextoDeRecusa(codigo){
  if(alladinForm.modo==='edit' && ALLADIN_ERRO_VOCABULARIO.indexOf(String(codigo))>=0){
    return 'Este cadastro utiliza um valor que esta versão do Alladin não reconhece. '+
           'Para salvar alterações, selecione um valor atualmente suportado. Nada foi gravado.';
  }
  return 'O cadastro foi recusado: '+codigo+'. Nada foi gravado.';
}
function alladinSubmit(){
  if(alladinForm.estado!=='EDITING') return;      // SUBMITTING/COMMITTED: nunca resubmete
  // ALD-05 S2: o modal de lançamento reusa a MESMA máquina de estados e os
  // mesmos atos 'salvar'/'cancelar' — só o leitor/ator muda de rota aqui.
  if(alladinForm.tipo==='transaction'){ alladinTxSubmit(); return; }
  const {tipo,modo,alvoId}=alladinForm;
  const rico=(tipo==='instrument'||tipo==='asset');
  let dados;
  if(rico){
    const lido=alladinLerFormRico(tipo);
    // Erro de UX é injetado IN-PLACE: o formulário rico não é re-renderizado,
    // então o rascunho (linhas de owners/identificadores) sobrevive intacto.
    if(lido.erro){ alladinErroInline(lido.erro); return; }
    dados=lido.dados;
  }else{
    dados=alladinLerFormulario(tipo);
    for(const k of Object.keys(dados)){
      if(dados[k]===''){ alladinErroInline('Preencha todos os campos antes de salvar.'); return; }
    }
  }
  if(modo==='edit'){
    const patch=alladinPatch(tipo,dados);
    if(!Object.keys(patch).length){ alladinModalClose(); showSessionNotice('Nenhuma alteração a salvar.'); return; }
    dados=patch;
  }
  alladinForm.estado='SUBMITTING';
  const ato=ALLADIN_ATOS[tipo];
  const r=(modo==='edit')?ato.edit(alvoId,dados):ato.add(dados);
  if(!r || r.ok!==true){
    // B-3: o erro é SEMPRE injetado in-place, nas quatro entidades. Re-renderizar
    // o formulário apagaria o que o operador digitou — perder o trabalho dele numa
    // recusa é a segunda punição por um erro que muitas vezes nem foi dele.
    alladinForm.estado='EDITING';
    alladinErroInline(alladinTextoDeRecusa((r&&r.erro)||'erro não identificado'));
    return;
  }
  // persistido:true daqui em diante — o registro EXISTE no disco.
  const avisos=r.avisos||[];
  const dups=avisos.filter(a=>String(a).indexOf('DUPLICADO')===0);
  if(dups.length){
    alladinForm.estado='COMMITTED_WARNING';
    alladinForm.recordId=r.recordId;
    alladinForm.avisos=avisos;
    // DH-S2B-2: a cópia distingue CRIADO de ALTERADO ("foi criado" era falso na
    // edição), e TODOS os avisos do ato permanecem visíveis — os informativos
    // vão em bloco próprio, para que nenhum deles pareça a razão da inativação.
    const outros=avisos.filter(a=>String(a).indexOf('DUPLICADO')!==0);
    const abertura=(modo==='edit')
      ?'A alteração foi salva. O aviso abaixo indica que o registro editado pode duplicar um cadastro existente — decida o que fazer com ele.'
      :'O registro foi criado e já está salvo. O aviso abaixo indica que ele pode duplicar um cadastro existente — decida o que fazer com ele.';
    document.getElementById('alladinModalBox').innerHTML=
      '<h3 id="alladinModalTitle">Possível duplicidade</h3>'+
      '<p class="modal-sub">'+esc(abertura)+'</p>'+
      '<div class="session-warning" role="alert">'+esc(dups.map(alladinAvisoTexto).join(' · '))+'</div>'+
      (outros.length?'<p class="modal-sub" data-ald-outros-avisos>Outros avisos deste registro, que não pedem decisão: '+
        esc(outros.map(alladinAvisoTexto).join(' · '))+'</p>':'')+
      '<div class="modal-actions"><button type="button" class="modal-btn cancel" data-ald-act="manter">Manter registro</button>'+
      '<button type="button" class="modal-btn confirm" data-ald-act="inativar-novo">Inativar este registro</button></div>';
    // Foco no TÍTULO, deliberadamente: um Enter residual do gesto de salvar não
    // pode ativar "Manter" sem leitura — a decisão exige Tab/clique deliberado.
    const titulo=document.getElementById('alladinModalTitle');
    if(titulo){ titulo.setAttribute('tabindex','-1'); titulo.focus(); }
    alladinRender();
    return;
  }
  const extras=avisos.length?' '+alladinAvisosResumo(avisos):'';
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
  const editBtn='<button type="button" class="modal-btn cancel" data-ald-edit="'+esc(tipo)+'" data-ald-id="'+esc(id)+'"'+dis+'>Editar</button> ';
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
  if(view==='instruments'){
    return '<p><button type="button" class="modal-btn confirm" data-ald-new="instrument"'+(bloqueado?' disabled':'')+'>Novo instrumento</button></p>';
  }
  if(view==='assets'){
    return '<p><button type="button" class="modal-btn confirm" data-ald-new="asset"'+(bloqueado?' disabled':'')+'>Novo bem</button></p>';
  }
  if(view==='cashAccounts'){
    const temAtiva=JPWAlladin.leitura.accounts().some(c=>c.recordStatus==='ACTIVE');
    if(!temAtiva) return '<p class="alladin-empty">Cadastre ou reative uma conta antes de criar uma conta de caixa.</p>';
    return '<p><button type="button" class="modal-btn confirm" data-ald-new="cashaccount"'+(bloqueado?' disabled':'')+'>Novo caixa</button></p>';
  }
  return '';
}
// ============ ALLADIN · ALD-05 S2 — CRIAÇÃO DE LANÇAMENTO PELA UI ===========
// A UI coleta campos, resolve rótulos cadastrais e faz UMA chamada a
// JPWAlladin.ledger.addTransaction por submit. Toda validação, derivação
// (moeda, flowScope, defaults de fees/taxes) e recusa é do domínio — a UI não
// tem aritmética financeira, não determina flowScope, não cria unitPrice e não
// normaliza quantity. dedupeKey não é exposta nesta slice (decisão do gate:
// double-submit já é bloqueado pela máquina de estados, e dois fatos idênticos
// sem dedupe são legítimos por contrato). REVERSAL fica fora — slice própria.
const ALLADIN_TX_TIPOS=['DEPOSIT','WITHDRAWAL','TRANSFER','BUY','SELL',
                        'FEE','TAX','ADJUSTMENT_CREDIT','ADJUSTMENT_DEBIT'];
// Texto humano para as recusas do addTransaction. Código desconhecido aparece
// CRU (padrão da casa) — e recusa jamais vira sucesso.
const ALLADIN_TX_ERRO_TEXTO={
  ALD_AMOUNT_INVALIDO:'Valor inválido. Informe um valor monetário positivo, ex.: 1.234,56.',
  ALD_EFFECTIVE_AT_INVALIDA:'Data inválida. Use o formato AAAA-MM-DD.',
  ALD_REASON_OBRIGATORIO:'O ajuste exige uma justificativa (motivo) não vazia.',
  ALD_TRANSFER_MESMA_CONTA:'Origem e destino são a mesma conta de caixa.',
  ALD_TRANSFER_MOEDAS_DIFERENTES:'Origem e destino têm moedas diferentes — não há câmbio implícito.',
  ALD_CASHACCOUNT_NAO_ENCONTRADA:'Conta de caixa não encontrada.',
  ALD_CASHACCOUNT_INATIVA:'A conta de caixa está inativa — lançamento novo exige cadastro ativo.',
  ALD_INSTRUMENT_NAO_ENCONTRADO:'Instrumento não encontrado.',
  ALD_INSTRUMENT_INATIVO:'O instrumento está inativo — lançamento novo exige cadastro ativo.',
  ALD_INSTRUMENT_MOEDA_DIVERGE_DA_CONTA:'A moeda do instrumento difere da moeda da conta — não há câmbio implícito.',
  ALD_QUANTITY_INVALIDA:'Quantidade inválida. Use decimal com ponto, sem sinal, sem zeros à esquerda e sem zeros finais na fração (ex.: 1.5, não 1.50).',
  ALD_FEES_INVALIDAS:'Taxas inválidas. Informe um valor monetário não negativo.',
  ALD_TAXES_INVALIDOS:'Impostos inválidos. Informe um valor monetário não negativo.',
  ALD_EFEITO_MONETARIO_FORA_DO_INTEIRO_SEGURO:'O efeito monetário combinado excede o limite representável.',
  ALD_NOTE_INVALIDA:'Nota inválida (máximo 240 caracteres).',
  ALD_DEDUPE_KEY_DUPLICADA:'Já existe um lançamento com esta chave de deduplicação.',
  ALD_CURRENCY_DIVERGE_DA_CONTA:'A moeda informada diverge da moeda da conta.',
  ALD_EVENT_TYPE_INVALIDO:'Tipo de lançamento não suportado por este build.',
  ALD_COLECAO_ILEGIVEL:'O ledger persistido está ilegível — nada foi gravado.',
  READ_ONLY_FUTURE_SCHEMA:'Este agregado foi gravado por uma versão mais nova do JP Wealth. Escrita bloqueada; nada foi gravado.'
};
function alladinTxTextoDeRecusa(codigo){
  const c=String(codigo||'erro não identificado');
  if(ALLADIN_TX_ERRO_TEXTO[c]) return ALLADIN_TX_ERRO_TEXTO[c]+' Nada foi gravado.';
  if(c.indexOf('ALD_INTEGRIDADE_ESTRUTURAL:')===0)
    return 'O agregado não passou na verificação de integridade ('+c+'). Nada foi gravado.';
  if(c.indexOf('ALD_REFERENCIA_AUSENTE:')===0)
    return 'Referência obrigatória ausente ('+c.slice('ALD_REFERENCIA_AUSENTE:'.length)+'). Nada foi gravado.';
  return 'O lançamento foi recusado: '+c+'. Nada foi gravado.';
}
function alladinTxBotaoNovo(){
  const bloqueado=!!alladinWriteBloqueado();
  return '<p><button type="button" class="modal-btn confirm" data-ald-tx-new="1"'+
         (bloqueado?' disabled':'')+'>Novo lançamento</button></p>';
}
// Snapshots cadastrais para os seletores — SÓ registros ACTIVE: filtro
// cadastral de UX (lançamento novo exige cadastro vivo), nunca autoridade.
// Corrida entre render e submit é decidida pelo domínio.
function alladinTxOpcoesConta(){
  const cat=alladinCatalogoLabels();
  return JPWAlladin.leitura.cashAccounts()
    .filter(c=>c.recordStatus==='ACTIVE')
    .map(c=>({id:c.cashAccountId, rotulo:cat.caixas[c.cashAccountId]||c.cashAccountId,
              currency:c.currency}));
}
function alladinTxOpcoesInstrumento(){
  return JPWAlladin.leitura.instruments()
    .filter(i=>i.recordStatus==='ACTIVE')
    .map(i=>({id:i.instrumentId, rotulo:(i.symbol?i.symbol+' · ':'')+(i.name||i.instrumentId)}));
}
function alladinTxSelect(id,rotulo,opcoes,valor){
  return '<label class="field"><span>'+esc(rotulo)+'</span>'+
    '<select id="'+id+'"><option value="">—</option>'+
    opcoes.map(o=>'<option value="'+esc(o.id)+'"'+(o.id===valor?' selected':'')+'>'+esc(o.rotulo)+'</option>').join('')+
    '</select></label>';
}
function alladinTxTipoAtual(){
  const el=document.getElementById('alladinTxTipo');
  return el?el.value:'DEPOSIT';
}
// Campos ESPECÍFICOS do evento — re-renderizados na troca de tipo. Os comuns
// (valor, data, nota) vivem fora deste bloco e o rascunho deles sobrevive.
function alladinTxCamposHTML(tipo){
  const contas=alladinTxOpcoesConta();
  if(tipo==='TRANSFER'){
    return alladinTxSelect('alladinTxOrigem','Conta de origem',contas,'')+
           alladinTxSelect('alladinTxDestino','Conta de destino',contas,'');
  }
  let html=alladinTxSelect('alladinTxConta','Conta de caixa',contas,'');
  if(tipo==='BUY'||tipo==='SELL'){
    html+=alladinTxSelect('alladinTxInstrumento','Instrumento',alladinTxOpcoesInstrumento(),'')+
      alladinCampo('alladinTxQuantidade','Quantidade (decimal, ex.: 1.5)','')+
      alladinCampo('alladinTxFees','Taxas (opcional)','')+
      alladinCampo('alladinTxTaxes','Impostos (opcional)','');
  }
  if(tipo==='ADJUSTMENT_CREDIT'||tipo==='ADJUSTMENT_DEBIT'){
    // reason é campo PRÓPRIO e obrigatório do ajuste — visível só aqui.
    html+=alladinCampo('alladinTxReason','Motivo (obrigatório)','');
  }
  return html;
}
function alladinTxRenderCampos(){
  const wrap=document.getElementById('alladinTxCampos');
  if(wrap){ wrap.innerHTML=alladinTxCamposHTML(alladinTxTipoAtual()); alladinTxAtualizarMoeda(); }
}
// Moeda DERIVADA da conta selecionada — informação read-only; jamais enviada.
// No TRANSFER a referência primária é a origem (aldTxRefsDoEvento).
function alladinTxContaSelecionada(){
  const el=document.getElementById('alladinTxConta')||document.getElementById('alladinTxOrigem');
  return el?el.value:'';
}
function alladinTxMoedaDerivada(){
  const id=alladinTxContaSelecionada();
  if(!id) return null;
  const c=JPWAlladin.leitura.cashAccounts().find(x=>x.cashAccountId===id);
  return c?c.currency:null;
}
function alladinTxAtualizarMoeda(){
  const span=document.getElementById('alladinTxMoeda');
  if(span) span.textContent=alladinTxMoedaDerivada()||'—';
}
function alladinTxAbrirForm(){
  // Write gate na ABERTURA (padrão W-series) — e de novo no domínio, no submit.
  const bloqueio=alladinWriteBloqueado();
  if(bloqueio){ showSessionNotice('Escrita indisponível: '+bloqueio); return; }
  alladinForm.estado='EDITING'; alladinForm.tipo='transaction'; alladinForm.modo='create';
  alladinForm.alvoId=null; alladinForm.recordId=null; alladinForm.avisos=[]; alladinForm.snapshot=null;
  const opcoesTipo=ALLADIN_TX_TIPOS
    .map(tp=>'<option value="'+tp+'">'+esc(ALLADIN_EVENTO_LABEL[tp]||tp)+'</option>').join('');
  alladinModalOpen(
    '<h3 id="alladinModalTitle">Novo lançamento</h3>'+
    '<p class="modal-sub">O lançamento é validado e gravado pelo domínio — a moeda é derivada da conta.</p>'+
    '<label class="field"><span>Tipo</span><select id="alladinTxTipo">'+opcoesTipo+'</select></label>'+
    '<div id="alladinTxCampos">'+alladinTxCamposHTML('DEPOSIT')+'</div>'+
    '<label class="field"><span>Valor (<span id="alladinTxMoeda">—</span>)</span>'+
      '<input type="text" id="alladinTxValor" value="" autocomplete="off" inputmode="decimal"></label>'+
    alladinCampo('alladinTxData','Data de efetivação (AAAA-MM-DD)','')+
    alladinCampo('alladinTxNota','Nota (opcional)','')+
    '<div class="modal-actions"><button type="button" class="modal-btn cancel" data-ald-act="cancelar">Cancelar</button>'+
    '<button type="button" class="modal-btn confirm" data-ald-act="salvar">Registrar</button></div>');
}
// Leitura do formulário → payload. NUNCA enviados: transactionId, recordedAt,
// status, currency, flowScope, unitPrice, dedupeKey. amount/fees/taxes passam
// EXCLUSIVAMENTE por money.parse (minor units); quantity vai VERBATIM.
// money.parse devolve {amount, currency} para texto válido, NaN para inválido
// e null para vazio. O payload do domínio quer o INTEIRO em unidade mínima —
// extraí-lo de um objeto não é aritmética, é desembrulho. Entrada inválida
// segue como veio (NaN): quem a recusa, com o SEU código, é o domínio.
function alladinTxMinor(txt,moeda){
  const par=JPWAlladin.money.parse(txt,moeda);
  return (par && typeof par==='object') ? par.amount : par;
}
function alladinTxLerFormulario(){
  const v=(id)=>{ const el=document.getElementById(id); return el?el.value:''; };
  const tipo=alladinTxTipoAtual();
  const moeda=alladinTxMoedaDerivada();
  const obrigatorios=[];
  const d={ eventType:tipo, effectiveAt:v('alladinTxData').trim() };
  if(tipo==='TRANSFER'){
    d.sourceCashAccountId=v('alladinTxOrigem');
    d.destinationCashAccountId=v('alladinTxDestino');
    obrigatorios.push(d.sourceCashAccountId,d.destinationCashAccountId);
  }else{
    d.cashAccountId=v('alladinTxConta');
    obrigatorios.push(d.cashAccountId);
  }
  const valorTxt=v('alladinTxValor').trim();
  obrigatorios.push(valorTxt,d.effectiveAt);
  if(tipo==='BUY'||tipo==='SELL'){
    d.instrumentId=v('alladinTxInstrumento');
    d.quantity=v('alladinTxQuantidade');           // VERBATIM — sem trim, sem correção
    obrigatorios.push(d.instrumentId,d.quantity);
    const fees=v('alladinTxFees').trim(), taxes=v('alladinTxTaxes').trim();
    if(fees!=='') d.fees=alladinTxMinor(fees,moeda);
    if(taxes!=='') d.taxes=alladinTxMinor(taxes,moeda);
  }
  if(tipo==='ADJUSTMENT_CREDIT'||tipo==='ADJUSTMENT_DEBIT'){
    d.reason=v('alladinTxReason');                 // o domínio julga vazio/espaços
    obrigatorios.push(d.reason);
  }
  const nota=v('alladinTxNota').trim();
  if(nota!=='') d.note=nota;
  if(obrigatorios.some(x=>x==='' || x===null || x===undefined))
    return { erro:'Preencha todos os campos obrigatórios antes de registrar.' };
  // Sem moeda derivável não há como interpretar o texto do valor — e a UI não
  // adivinha moeda: é recusa de UX, antes de inventar um número.
  if(!moeda) return { erro:'Selecione uma conta de caixa para derivar a moeda do valor.' };
  d.amount=alladinTxMinor(valorTxt,moeda);
  return { dados:d };
}
function alladinTxSubmit(){
  if(alladinForm.estado!=='EDITING') return;
  const lido=alladinTxLerFormulario();
  if(lido.erro){ alladinErroInline(lido.erro); return; }
  alladinForm.estado='SUBMITTING';
  // UMA chamada por submit; o retorno do domínio é o único veredito.
  const r=JPWAlladin.ledger.addTransaction(lido.dados);
  if(!r || r.ok!==true){
    // Recusa: o rascunho sobrevive (erro in-place, sem re-render) e
    // persistido:false continua VISUALMENTE erro — jamais falso sucesso.
    alladinForm.estado='EDITING';
    alladinErroInline(alladinTxTextoDeRecusa(r&&r.erro));
    return;
  }
  alladinModalClose();
  showSessionNotice('Lançamento registrado.');
}

function initAlladinCrud(){
  const ov=document.getElementById('alladinModalOverlay');
  const box=document.getElementById('alladinModalBox');
  const section=document.getElementById('alladin');
  if(!ov||!box||!section) return;
  // Delegação: UM listener por superfície — nenhum bind por abertura.
  section.addEventListener('click',e=>{
    const txn=e.target.closest('button[data-ald-tx-new]');
    if(txn && !txn.disabled){ alladinTxAbrirForm(); return; }
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
    // Editores de lista: alteram SÓ o DOM do rascunho — nenhum autosave, nada
    // persiste antes do submit principal.
    else if(act==='ext-add'){
      const lista=box.querySelector('[data-ald-ext-lista]');
      if(lista){ lista.insertAdjacentHTML('beforeend',alladinExtRowHTML('','')); const i=lista.querySelectorAll('[data-ald-ext-k]'); i[i.length-1].focus(); }
    }
    else if(act==='ext-del'){
      const row=b.closest('[data-ald-ext-row]');
      if(row){ row.remove(); const add=box.querySelector('button[data-ald-act=ext-add]'); if(add) add.focus(); }
    }
    else if(act==='owner-add'){
      const lista=box.querySelector('[data-ald-owner-lista]');
      if(lista){ lista.insertAdjacentHTML('beforeend',alladinOwnerRowHTML(null)); const i=lista.querySelectorAll('[data-ald-owner-nome]'); i[i.length-1].focus(); alladinOwnersAtualizarTotal(); }
    }
    else if(act==='owner-del'){
      const row=b.closest('[data-ald-owner-row]');
      if(row){ row.remove(); alladinOwnersAtualizarTotal(); const add=box.querySelector('button[data-ald-act=owner-add]'); if(add) add.focus(); }
    }
  });
  // Total cadastral de participação, ao vivo (owners/shareBp — jamais valor).
  box.addEventListener('input',e=>{ if(e.target.matches('[data-ald-owner-pct]')) alladinOwnersAtualizarTotal(); });
  // Família CRYPTO revela o campo Rede: a chave `network` tem fonte única.
  box.addEventListener('change',e=>{
    // ALD-05 S2: trocar o TIPO re-renderiza só o bloco de campos específicos —
    // os campos comuns (valor, data, nota) vivem fora dele e o rascunho
    // sobrevive. Trocar a CONTA atualiza a moeda derivada exibida.
    if(e.target.id==='alladinTxTipo'){ alladinTxRenderCampos(); return; }
    if(e.target.id==='alladinTxConta'||e.target.id==='alladinTxOrigem'){ alladinTxAtualizarMoeda(); return; }
    if(e.target.id!=='alladinFldFamily') return;
    const wrap=document.getElementById('alladinFldNetworkWrap');
    const campo=document.getElementById('alladinFldNetwork');
    // Sair de CRYPTO não esconde uma rede preenchida: escondê-la seria removê-la
    // sem que o operador visse o que perdeu.
    if(wrap) wrap.hidden=(e.target.value!=='CRYPTO' && !(campo&&campo.value.trim()));
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
