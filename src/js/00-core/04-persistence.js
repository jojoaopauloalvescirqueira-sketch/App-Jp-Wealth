// ============ PERSISTÊNCIA (localStorage) ============
const LSKEY='jpwealth_v9_state';
let S;
let jpWealthPersistenceBlocked=false;
let jpWealthSessionEpoch=0;
function jpWealthPersistenceIsBlocked(){ return jpWealthPersistenceBlocked; }
function jpWealthPersistenceEpoch(){ return jpWealthSessionEpoch; }
function blockJPWealthPersistence(){
  jpWealthPersistenceBlocked=true;
  jpWealthSessionEpoch++;
}
function resumeJPWealthPersistence(){
  jpWealthPersistenceBlocked=false;
  jpWealthSessionEpoch++;
}
function load(){
  let raw=null;
  try{ raw=localStorage.getItem(LSKEY); }catch(e){}
  if(raw){
    let parsed=null;
    try{ parsed=JSON.parse(raw); }catch(e){ parsed=null; }
    if(parsed){
      try{ S=parsed; migrate(); return; }
      catch(e){
        try{ localStorage.setItem(LSKEY+'_corrompido_'+Date.now(), raw); }catch(_){}
        setTimeout(()=>alert('Não foi possível migrar o estado salvo ('+(e&&e.message?e.message:'erro')+'). Uma cópia bruta foi guardada e o painel abriu no estado inicial. Seus dados continuam no navegador — use exportar/importar backup para recuperar.'),400);
      }
    }
  }
  S=structuredClone(DEFAULTS);
}
// ---- Notas do MVP: enums fixos e normalização (14-mvp-notes.js consome os mesmos
// arrays). Definidos aqui — script cedo — porque migrate() roda em load() (06-boot.js)
// antes de 14-mvp-notes.js sequer carregar; a UI só lê estes valores depois. ----
const MVP_NOTES_TYPES=['task','bug','feature','improvement'];
const MVP_NOTES_STATUSES=['open','in_progress','done','discarded'];
const MVP_NOTES_PRIORITIES=['low','medium','high','critical'];
function mvpNotesId(){ return 'mvpn_'+Date.now().toString(36)+'_'+Math.random().toString(36).slice(2,8); }
function mvpNotesFolderId(){ return 'mvpnf_'+Date.now().toString(36)+'_'+Math.random().toString(36).slice(2,8); }
// ---- pastas (schemaVersion 2) — normalizadas ANTES dos itens: mvpNotesNormalizeItem()
// precisa do conjunto de IDs válidos/ambíguos resultante para reconciliar item.folderId. ----
function mvpNotesNormalizeFolders(rawList){
  const seenIds=new Set();
  const ambiguousIds=new Set(); // ID original que apareceu mais de uma vez no backup — uma
  // nota que referenciava esse ID não tem como saber qual das duas pastas era a pretendida.
  const folders=[];
  (Array.isArray(rawList)?rawList:[]).forEach(raw=>{
    if(!raw || typeof raw!=='object') return;
    const name=String(raw.name||'').trim();
    if(!name) return; // pasta sem nome não é preservada — não existe "pasta vazia de nome"
    let id=String(raw.id||'').trim();
    if(!id){ id=mvpNotesFolderId(); }
    else if(seenIds.has(id)){
      ambiguousIds.add(id); // preserva o primeiro ID válido; a duplicata recebe ID novo
      id=mvpNotesFolderId();
    }
    seenIds.add(id);
    const createdAt=(typeof raw.createdAt==='string'&&raw.createdAt)?raw.createdAt:new Date().toISOString();
    const updatedAt=(typeof raw.updatedAt==='string'&&raw.updatedAt)?raw.updatedAt:createdAt;
    folders.push({id, name:name.slice(0,80), createdAt, updatedAt});
  });
  return {folders, validIds:seenIds, ambiguousIds};
}
function mvpNotesResolveFolderId(rawFolderId,validIds,ambiguousIds){
  const id=String(rawFolderId||'').trim();
  if(!id) return null; // ausente = Sem pasta
  if(ambiguousIds.has(id)) return null; // referência ambígua = Sem pasta, nunca inventa vínculo
  if(!validIds.has(id)) return null; // pasta inexistente = Sem pasta
  return id;
}
function mvpNotesNormalizeItem(raw,seenIds,validFolderIds,ambiguousFolderIds){
  if(!raw || typeof raw!=='object') return null;
  const title=String(raw.title||'').trim();
  if(!title) return null; // título obrigatório — sem ele o item é descartado, não o backup inteiro
  let id=String(raw.id||'').trim();
  if(!id || seenIds.has(id)) id=mvpNotesId(); // impede ID ausente/duplicado
  seenIds.add(id);
  const createdAt=(typeof raw.createdAt==='string'&&raw.createdAt)?raw.createdAt:new Date().toISOString();
  return {
    id,
    type:MVP_NOTES_TYPES.includes(raw.type)?raw.type:'task',
    title:title.slice(0,120),
    description:String(raw.description||'').slice(0,5000),
    priority:MVP_NOTES_PRIORITIES.includes(raw.priority)?raw.priority:'medium',
    status:MVP_NOTES_STATUSES.includes(raw.status)?raw.status:'open',
    folderId:mvpNotesResolveFolderId(raw.folderId,validFolderIds,ambiguousFolderIds),
    screenId:String(raw.screenId||''),
    buildId:String(raw.buildId||''),
    createdAt,
    updatedAt:(typeof raw.updatedAt==='string'&&raw.updatedAt)?raw.updatedAt:createdAt
  };
}
function mvpNotesNormalizeState(){
  if(!S.mvpNotes || typeof S.mvpNotes!=='object') S.mvpNotes=structuredClone(DEFAULTS.mvpNotes);
  S.mvpNotes.schemaVersion=2;
  S.mvpNotes.showHeaderIcon=S.mvpNotes.showHeaderIcon!==false; // padrão true; só desliga com false explícito
  // Estado v1 (sem folders) chega aqui com S.mvpNotes.folders===undefined — normaliza para []
  // e cada nota, sem folderId prévio, resolve para null (Sem pasta) abaixo. Sem tela de
  // migração: o operador só vê o resultado (tudo em "Sem pasta") ao abrir o painel.
  const {folders,validIds,ambiguousIds}=mvpNotesNormalizeFolders(S.mvpNotes.folders);
  S.mvpNotes.folders=folders;
  const seenIds=new Set();
  S.mvpNotes.items=(Array.isArray(S.mvpNotes.items)?S.mvpNotes.items:[])
    .map(item=>mvpNotesNormalizeItem(item,seenIds,validIds,ambiguousIds))
    .filter(Boolean);
}
function migrate(){ // garante chaves novas se schema evoluir
  for(const k in DEFAULTS){ if(!(k in S)) S[k]=structuredClone(DEFAULTS[k]); }
  mvpNotesNormalizeState(); // legado sem mvpNotes já recebeu DEFAULTS.mvpNotes acima; aqui valida a forma
  // migração por-instrumento: estados salvos antes desta versão não têm 'updated'/'banned'.
  // Sem isso, bloqueios normativos como XAUUSD e US500 seriam perdidos silenciosamente em contas já em uso.
  if(Array.isArray(S.instruments)){
    const us500Ref=DEFAULTS.instruments.find(d=>d.name==='US500');
    if(us500Ref && !S.instruments.some(ins=>ins.name==='US500')) S.instruments.push(structuredClone(us500Ref));
    S.instruments.forEach(ins=>{
      const ref=DEFAULTS.instruments.find(d=>d.name===ins.name);
      if(!('updated' in ins)) ins.updated = '2000-01-01'; // desconhecido = tratar como não confiável
      if(ref && ref.banned && (ins.name==='US500' || !('banned' in ins))){
        ins.banned=true; ins.banReason=ref.banReason; // reaplica o bloqueio, não assume liberação
      }
      // sessões antigas podem não ter cpl/teto/preco — sem isso o renderMotor quebra o boot inteiro
      if(ref){
        if(!(typeof ins.cpl==='number' && ins.cpl>0)) ins.cpl=ref.cpl;
        if(typeof ins.teto!=='number') ins.teto=ref.teto;
        if(!(typeof ins.preco==='number' && ins.preco>0)) ins.preco=ref.preco;
      }
      // estados salvos pela versão anterior gravaram preco=1.00 nos pares de base USD
      // (semântica antiga de "nocional"); o nocional agora é derivado, então 1.00 é só
      // uma cotação obviamente errada — restaura a referência até o próximo fetch.
      if(ref && ['USDJPY','USDCHF','USDCAD'].includes(ins.name) && ins.preco===1) ins.preco=ref.preco;
    });
  }
  if(Array.isArray(S.accounts)){
    S.accounts.forEach(a=>{
      // conta salva antes desta versão já tinha perfil escolhido -> trava por padrão,
      // não deixa a mudança de schema abrir uma exceção que ninguém pediu.
      if(!('perfilLocked' in a)) a.perfilLocked = !!a.perfil;
      if(a.perfil) a.perfil=normalizeRiskProfileName(a.perfil);
      if(!('platform' in a)) a.platform='';
      if(!('platformLogin' in a)) a.platformLogin='';
      if(!('investorPassword' in a)) a.investorPassword='';
      a.platform=normalizePlatformName(a.platform);
      a.platformLogin=String(a.platformLogin||'');
      a.investorPassword=String(a.investorPassword||'');
      const br=brokerFor(a.broker);
      if(br) a.broker=br.name;
    });
  }
  // matriz de fases: compute() e phaseTetoRisco() assumem 4 linhas com ddmin/ddmax/alav numéricos.
  // O loop genérico acima só recria a matriz se ela estiver AUSENTE — um backup corrompido/truncado
  // (ex.: matrix:[] ou linha sem ddmax) passaria e derrubaria o boot em m[2].ddmax. Restaura o que faltar.
  if(!Array.isArray(S.matrix) || S.matrix.length!==DEFAULTS.matrix.length){
    S.matrix=structuredClone(DEFAULTS.matrix);
  } else {
    S.matrix.forEach((row,i)=>{
      const ref=DEFAULTS.matrix[i];
      if(!row || typeof row!=='object'
        || typeof row.ddmin!=='number' || typeof row.ddmax!=='number' || typeof row.alav!=='number'){
        S.matrix[i]=structuredClone(ref);
      } else if(typeof row.nome!=='string'){ row.nome=ref.nome; }
    });
  }
  if(!('riskPinHash' in S)) S.riskPinHash=null;
  if(!Array.isArray(S.phaseUnlocked)) S.phaseUnlocked=[true,false,false,false];
  if(!Array.isArray(S.transitionLog)) S.transitionLog=[];
  if(typeof S.protocolBreaches!=='number') S.protocolBreaches=0;
  if(typeof S.cycleRealizado!=='number') S.cycleRealizado=0;
  if(!('quarantine' in S)) S.quarantine=null;
  if(!Array.isArray(S.ledger)) S.ledger=[];
  if(!Array.isArray(S.ledgerArchive)) S.ledgerArchive=[];
  if(!S.period || typeof S.period!=='object') S.period={nome:'',profile:'base'};
  S.period.profile=normalizeRiskProfileKey(S.period.profile||'base');
  S.profiles=riskProfilesForState();
  const activeProfile=getActiveRiskProfile(S.period.profile);
  S.params.refM=activeProfile.mensal; S.params.refA=activeProfile.anual;
  S.params.fw=1; // V10: remove multiplicador fixo; aplica saldo normalizado × fator de perfil
  if(S.theme!=='dark' && S.theme!=='light') S.theme='dark'; // Mission Control: escuro é a experiência principal; escolha salva do usuário é respeitada
  if(!S.acct || typeof S.acct!=='object') S.acct={diasSemana:4.5, mesesAno:10.5};
  if(typeof S.acct.diasSemana!=='number') S.acct.diasSemana=4.5;
  if(typeof S.acct.mesesAno!=='number') S.acct.mesesAno=10.5;
  // MEI-JP: migração defensiva para backups anteriores, sem tocar nas estruturas existentes.
  if(!S.mei || typeof S.mei!=='object') S.mei=structuredClone(DEFAULTS.mei);
  else {
    for(const k in DEFAULTS.mei){ if(!(k in S.mei)) S.mei[k]=structuredClone(DEFAULTS.mei[k]); }
    S.mei.version='1.0';
    S.mei.enabled=S.mei.enabled!==false;
    S.mei.sourceMode='auto';
    S.mei.simulationCount=[1000,2000,5000,10000].includes(+S.mei.simulationCount)?+S.mei.simulationCount:5000;
    S.mei.horizonMonths=[12,24,60,120].includes(+S.mei.horizonMonths)?+S.mei.horizonMonths:60;
    S.mei.confidenceLevel=Math.max(.5,Math.min(.99,+S.mei.confidenceLevel||.90));
    S.mei.seedMode=S.mei.seedMode==='fixed'?'fixed':'random';
    S.mei.fixedSeed=String(S.mei.fixedSeed||'');
    // Revisão metodológica v1.0: predominância empírica exige ≥36 retornos válidos.
    // Estados antigos (24) são elevados para 36 — é revisão de política institucional,
    // não preferência do usuário; 24 observações voltam a ser estágio híbrido avançado.
    S.mei.minimumHistoricalMonths=Math.max(36,Math.round(+S.mei.minimumHistoricalMonths||36));
    S.mei.hybridStartMonths=Math.max(2,Math.round(+S.mei.hybridStartMonths||6));
    S.mei.empiricalStartMonths=Math.max(36,Math.max(S.mei.hybridStartMonths+1,Math.round(+S.mei.empiricalStartMonths||36)));
    if(!S.mei.cid || typeof S.mei.cid!=='object') S.mei.cid=structuredClone(DEFAULTS.mei.cid);
    RISK_PROFILES.forEach(p=>{
      const v=S.mei.cid[p.key];
      const n=typeof v==='string' ? Number(v.replace(',','.')) : +v;
      S.mei.cid[p.key]=(v===''||v==null||!Number.isFinite(n))?'':Math.max(0,Math.min(1,n));
    });
    // Preserva registros legados, mesmo se incompletos: o operador deve poder corrigi-los na interface.
    // A camada de cálculo filtra somente as observações válidas, sem apagar dados do backup.
    // Correção 5 (fluxos externos): registros antigos migram com aportes=0, retiradas=0
    // (fluxo líquido 0) e equity inicial informativa vazia — nenhum registro é perdido.
    S.mei.history=Array.isArray(S.mei.history)?S.mei.history.filter(r=>r&&typeof r==='object').map((r,i)=>({
      id:String(r.id||('mei_legacy_'+i+'_'+Date.now())), date:String(r.date||''),
      startingEquity:(r.startingEquity===''||r.startingEquity==null||!Number.isFinite(+r.startingEquity))?'':Number(r.startingEquity),
      endingEquity:Number(r.endingEquity),
      contributions:Number.isFinite(+r.contributions)?Math.max(0,+r.contributions):0,
      withdrawals:Number.isFinite(+r.withdrawals)?Math.max(0,+r.withdrawals):0,
      notes:String(r.notes||'')
    })):[];
    S.mei.lastCalibrationAt=String(S.mei.lastCalibrationAt||'');
    S.mei.notes=String(S.mei.notes||'');
  }
  if(!(typeof S.stopF==='number' && S.stopF>0)) S.stopF=1.8;
  if(typeof S.atrPctManual!=='number') S.atrPctManual=0;
  if(!S.onboarding || typeof S.onboarding!=='object') S.onboarding=structuredClone(DEFAULTS.onboarding);
  else {
    const br=brokerFor(S.onboarding.corretora);
    if(br) S.onboarding.corretora=br.name;
    for(const k in DEFAULTS.onboarding){ if(!(k in S.onboarding)) S.onboarding[k]=DEFAULTS.onboarding[k]; }
    S.onboarding.brokerLogin=String(S.onboarding.brokerLogin||'');
    S.onboarding.investorPassword=String(S.onboarding.investorPassword||'');
    S.onboarding.brokerServer=String(S.onboarding.brokerServer||'');
    S.onboarding.moedaBase=normalizeAccountCurrency(S.onboarding.moedaBase);
    S.onboarding.propDailyDrawdown=String(S.onboarding.propDailyDrawdown||'');
    S.onboarding.propMaxDrawdown=String(S.onboarding.propMaxDrawdown||'');
    S.onboarding.propTrailingRule=String(S.onboarding.propTrailingRule||'');
    S.onboarding.propTrailingDescription=String(S.onboarding.propTrailingDescription||'');
    S.onboarding.propProfitTarget=String(S.onboarding.propProfitTarget||'');
    S.onboarding.propMinTradingDays=String(S.onboarding.propMinTradingDays||'');
    S.onboarding.propAbsenceRules=String(S.onboarding.propAbsenceRules||'');
    S.onboarding.restrictiveRuleAccepted=Boolean(S.onboarding.restrictiveRuleAccepted);
    // Capital nominal da Conta Mestre não tem mais entrada própria: o Saldo de Início do
    // Período (S.params.saldoIni) é a fonte única. Reconcilia aqui para que backups/estados
    // legados com valor divergente nunca sobrevivam a um load — o campo persiste só por
    // compatibilidade de formato do backup, nunca é lido como fonte de verdade em runtime.
    S.onboarding.reserveMasterCapital=String(S.params.saldoIni||0);
    S.onboarding.reserveFcrRequired=String(S.onboarding.reserveFcrRequired||'');
    S.onboarding.reserveFcrCurrent=String(S.onboarding.reserveFcrCurrent||'');
    S.onboarding.reserveFcrStatus=String(S.onboarding.reserveFcrStatus||'');
    S.onboarding.reserveMonthlyExpenses=String(S.onboarding.reserveMonthlyExpenses||'');
    S.onboarding.reserveFeoRequired=String(S.onboarding.reserveFeoRequired||'');
    S.onboarding.reserveFeoCurrent=String(S.onboarding.reserveFeoCurrent||'');
    S.onboarding.reserveFeoStatus=String(S.onboarding.reserveFeoStatus||'');
    S.onboarding.reserveFcrCoveragePct=String(S.onboarding.reserveFcrCoveragePct||'');
    S.onboarding.reserveFeoCoveragePct=String(S.onboarding.reserveFeoCoveragePct||'');
    S.onboarding.reserveFeoMonthsCovered=String(S.onboarding.reserveFeoMonthsCovered||'');
    S.onboarding.reserveSegregationAccepted=Boolean(S.onboarding.reserveSegregationAccepted);
    S.onboarding.reserveDeficitAccepted=Boolean(S.onboarding.reserveDeficitAccepted);
    S.onboarding.reserveNotes=String(S.onboarding.reserveNotes||'');
    S.onboarding.centralCashStatus=String(S.onboarding.centralCashStatus||'');
    S.onboarding.centralCashCustody=String(S.onboarding.centralCashCustody||'');
    S.onboarding.centralCashCustodyOther=String(S.onboarding.centralCashCustodyOther||'');
    S.onboarding.centralCashMainPct=String(S.onboarding.centralCashMainPct||'');
    S.onboarding.centralCashAgilePct=String(S.onboarding.centralCashAgilePct||'');
    S.onboarding.centralCashLiquidityPct=String(S.onboarding.centralCashLiquidityPct||'');
    S.onboarding.centralCashExternalPct=String(S.onboarding.centralCashExternalPct||'');
    S.onboarding.centralCashOtherPct=String(S.onboarding.centralCashOtherPct||'');
    S.onboarding.centralCashCompositionMode=String(S.onboarding.centralCashCompositionMode||'percentual');
    S.onboarding.centralCashCompositionTotal=String(S.onboarding.centralCashCompositionTotal||'');
    S.onboarding.centralCashTraceabilityScore=String(S.onboarding.centralCashTraceabilityScore||'');
    S.onboarding.fcrLiquidity=String(S.onboarding.fcrLiquidity||'');
    S.onboarding.feoLiquidity=String(S.onboarding.feoLiquidity||'');
    S.onboarding.cashLedgerStatus=String(S.onboarding.cashLedgerStatus||'');
    S.onboarding.centralCashPolicyAccepted=Boolean(S.onboarding.centralCashPolicyAccepted);
    S.onboarding.centralCashNoAccepted=Boolean(S.onboarding.centralCashNoAccepted);
    S.onboarding.centralCashNotes=String(S.onboarding.centralCashNotes||'');
    S.onboarding.epStatus=String(S.onboarding.epStatus||'');
    S.onboarding.epPlatform=String(S.onboarding.epPlatform||'');
    S.onboarding.epPlatformOther=String(S.onboarding.epPlatformOther||'');
    S.onboarding.epReference=String(S.onboarding.epReference||'');
    S.onboarding.epDailyLimit=String(S.onboarding.epDailyLimit||'');
    S.onboarding.epMaxDrawdown=String(S.onboarding.epMaxDrawdown||'');
    S.onboarding.epStatuteMatch=String(S.onboarding.epStatuteMatch||'');
    S.onboarding.epRestrictiveAccepted=Boolean(S.onboarding.epRestrictiveAccepted);
    S.onboarding.epPropDailyEnabled=String(S.onboarding.epPropDailyEnabled||'');
    S.onboarding.epPropDailyBase=String(S.onboarding.epPropDailyBase||'');
    S.onboarding.epPropDailyNotes=String(S.onboarding.epPropDailyNotes||'');
    S.onboarding.epTestStatus=String(S.onboarding.epTestStatus||'');
    S.onboarding.epNoConfigAccepted=Boolean(S.onboarding.epNoConfigAccepted);
    S.onboarding.epNotes=String(S.onboarding.epNotes||'');
    S.onboarding.summaryAccepted=Boolean(S.onboarding.summaryAccepted);
  }
  // estado antigo COM atividade (ordens/fechamentos/log) = período já em andamento:
  // não abrir o questionário de início por cima — confirmar sobrescreveria saldoIni/inicio.
  if(!S.onboarding.done){
    const temAtividade=(Array.isArray(S.transitionLog)&&S.transitionLog.length>0)
      ||(Array.isArray(S.ledger)&&S.ledger.length>0)
      ||(Array.isArray(S.phases)&&S.phases.some(ph=>Array.isArray(ph.orders)&&ph.orders.some(o=>o&&o.status)));
    if(temAtividade) S.onboarding.done=true;
  }
  // migração de ordens: versões anteriores usavam 'Active' ou inferiam status pela presença
  // de lote/entry/sl. Agora o status é explícito (Aberta/Fechada) e passou a ser o único
  // critério para contar risco — sem isso, ordens já preenchidas silenciosamente sumiriam do cálculo.
  if(Array.isArray(S.phases)){
    S.phases.forEach(ph=>{
      if(!Array.isArray(ph.orders)) return;
      ph.orders.forEach(o=>{
        if(o.status==='Active') o.status='Aberta';
        else if(!o.status && o.lote>0 && o.entry>0 && o.sl>0) o.status='Aberta'; // dado preenchido = presumir aberta
      });
    });
  }
}
let saveTimer;
function save(){
  if(jpWealthPersistenceBlocked) return false;
  try{localStorage.setItem(LSKEY,JSON.stringify(S));
    const t=document.getElementById('savedTag'); t.classList.add('show');
    clearTimeout(saveTimer); saveTimer=setTimeout(()=>t.classList.remove('show'),1200);
    return true;
  }catch(e){ return false; }
}
