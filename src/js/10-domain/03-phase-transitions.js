// ============ QUESTIONÁRIOS DE TRANSIÇÃO DE FASE ============
// Pesos psicológicos diferentes por fase — Art. 3.7 e doc. de tese quadrifásica.
const TRANSITION_QUESTIONNAIRES = {
  2:{
    title:'Transição para Fase 2 — Desaceleração',
    subtitle:'DD 4,01%–8,00% · Teto de alavancagem cai para 2,0x · Bloqueio de novos lotes agressivos',
    questions:[
      {id:'reconhecimento', type:'bool', label:'Você reconhece formalmente que houve erro de timing na tese da Fase 1?', mustBeYes:true},
      {id:'suspensao', type:'bool', label:'O objetivo migra de lucro para busca de breakeven/lucro reduzido — você concorda em suspender novos lotes agressivos?', mustBeYes:true},
      {id:'stopRecalc', type:'bool', label:'Você recalculou o Stop Estatístico (ATR×√N×F, Art. 9.5) para as condições atuais de volatilidade?', mustBeYes:true},
      {id:'causa', type:'text', label:'Qual foi a causa da deterioração da tese?', placeholder:'estrutura invalidada / notícia inesperada / erro de leitura / outro'},
    ]
  },
  3:{
    title:'Transição para Fase 3 — Sobrevivência',
    subtitle:'DD 8,01%–12,00% · Proibição absoluta de novas adições · Postura puramente passiva',
    questions:[
      {id:'tendenciaConfirmada', type:'bool', label:'A tendência adversa está confirmada pela estrutura de mercado — não é apenas ruído de curto prazo?', mustBeYes:true},
      {id:'semNovosLotes', type:'bool', label:'Reconhece que, a partir daqui, a única ação permitida é REDUZIR exposição em movimentos corretivos — nunca ampliar?', mustBeYes:true},
      {id:'motivoManutencao', type:'text', label:'Descreva objetivamente, sem viés emocional, por que ainda mantém a tese aberta em vez de encerrá-la agora.'},
      {id:'vieses', type:'checklist', label:'Autoconsciência (não bloqueia a liberação) — marque o que estiver presente agora:',
        options:['Recusa da perda planejada','Apego à tese','Teimosia','Esperança de recuperação sem base técnica']},
    ]
  },
  4:{
    title:'Transição para Fase 4 — O Abismo / Fuga',
    subtitle:'DD 12,01%–15,00% · Suspensão integral de atividade discricionária · Freeze',
    questions:[
      {id:'info', type:'info', label:'Esta é a fase final antes do Encerramento Compulsório em 15,00% (Art. 3.10). A partir daqui, a atividade discricionária está suspensa — só resta gerenciar o encerramento residual.'},
      {id:'relatorio', type:'bool', label:'Você já está mentalmente preparado para o Relatório de Incidente obrigatório caso o limite de 15% seja atingido (Art. 3.10 §3)?'},
      {id:'confirmPhrase', type:'confirmText', label:'Digite exatamente a frase abaixo para confirmar que entende que não pode abrir novas posições, apenas gerenciar o encerramento residual:',
        mustMatch:'ACEITO A SALVAGUARDA'},
    ]
  }
};

// Questionário de DOWNGRADE — simétrico ao de transição, mas com registro psicológico oposto:
// o risco aqui não é desespero, é euforia silenciosa. Art. 4.3 (Ilusão do DDC) é o ancoradouro.
const DOWNGRADE_QUESTIONNAIRE={
  title:'Downgrade de Fase — reconhecer a melhora sem tratá-la como licença',
  subtitle:'O drawdown caiu abaixo do mínimo da fase destravada. Isso não autoriza alavancagem maior (Art. 4.3 — Ilusão do DDC).',
  questions:[
    {id:'naoAutoriza', type:'bool', label:'Você reconhece que esta melhora NÃO autoriza aumento de lote ou alavancagem acima do que a fase de destino permite?', mustBeYes:true},
    {id:'melhoraReal', type:'bool', label:'Essa melhora veio de redução de risco/lucro técnico real — não é uma recuperação parcial que ainda pode reverter a qualquer momento?', mustBeYes:true},
    {id:'licao', type:'text', label:'O que você aprendeu com o ciclo que levou ao drawdown anterior, antes de tratar isso como resolvido?'},
  ]
};

function closeModal(){
  if(typeof window.__cleanupOnboardingModalUI === 'function'){
    try{ window.__cleanupOnboardingModalUI(); }catch(e){}
    window.__cleanupOnboardingModalUI=null;
  }
  $('modalOverlay').classList.remove('show');
  $('modalBox').classList.remove('onboarding-modal');
  $('modalBox').innerHTML='';
  renderOnboardingIncompleteBanner();
  renderExecutionOnboardingWarning();
  renderConfigOnboarding();
}
function activePhaseRangeLabel(idx){
  const row=activeRiskMatrix()[idx];
  return row ? `${fmtPct(row.ddmin)}–${fmtPct(row.ddmax)}` : '—';
}
function transitionSubtitleFor(faseNum, fallback){
  const range=activePhaseRangeLabel(faseNum-1);
  if(faseNum===2) return `DD ${range} · Teto de alavancagem cai para 2,0x · Bloqueio de novos lotes agressivos`;
  if(faseNum===3) return `DD ${range} · Proibição absoluta de novas adições · Postura puramente passiva`;
  if(faseNum===4) return `DD ${range} · Suspensão integral de atividade discricionária · Freeze`;
  return fallback;
}
function activeLimitQuestionText(txt){
  return String(txt||'').replace(/15,00%|15%/g,fmtPct(activeMDDLimit()));
}

function openTransitionModal(faseNum){
  const q=TRANSITION_QUESTIONNAIRES[faseNum];
  if(!q) return;
  const answers={};
  const box=$('modalBox');
  $('modalOverlay').classList.add('show');
  let html=`<h3>🔒 ${q.title}</h3><div class="modal-sub">${transitionSubtitleFor(faseNum,q.subtitle)}</div>`;
  q.questions.forEach(item=>{
    const label=activeLimitQuestionText(item.label);
    html+=`<div class="modal-q" data-qid="${item.id}">`;
    if(item.type==='info'){
      html+=`<div class="qinfo">${label}</div>`;
    } else if(item.type==='bool'){
      html+=`<div class="ql">${label}</div>
        <div class="seg" data-qtype="bool">
          <button type="button" data-val="sim">Sim</button>
          <button type="button" data-val="nao">Não</button>
        </div>
        <div class="modal-err">Esta confirmação é obrigatória para prosseguir.</div>`;
    } else if(item.type==='text'){
      html+=`<div class="ql">${label}</div>
        <textarea placeholder="${item.placeholder||''}"></textarea>
        <div class="modal-err">Descreva antes de prosseguir — não deixe em branco.</div>`;
    } else if(item.type==='confirmText'){
      html+=`<div class="ql">${label}</div>
        <input type="text" placeholder="${item.mustMatch}" autocomplete="off">
        <div class="modal-err">O texto precisa ser exatamente igual: "${item.mustMatch}".</div>`;
    } else if(item.type==='checklist'){
      html+=`<div class="ql">${label}</div>`;
      item.options.forEach((opt,oi)=>{
        html+=`<label class="check-row"><input type="checkbox" data-opt="${oi}"> ${opt}</label>`;
      });
    }
    html+=`</div>`;
  });
  html+=`<div class="modal-actions">
    <button class="modal-btn cancel" id="modalCancel">Cancelar</button>
    <button class="modal-btn confirm" id="modalConfirm">Confirmar e liberar Fase ${faseNum}</button>
  </div>`;
  box.innerHTML=html;
  // bind seg (bool) toggles
  box.querySelectorAll('[data-qtype="bool"] button').forEach(b=>{
    b.addEventListener('click',()=>{
      const seg=b.parentElement;
      seg.querySelectorAll('button').forEach(x=>x.classList.remove('on'));
      b.classList.add('on');
      seg.dataset.answer=b.dataset.val;
      seg.parentElement.querySelector('.modal-err')?.classList.remove('show');
    });
  });
  $('modalCancel').addEventListener('click', closeModal);
  $('modalConfirm').addEventListener('click',()=>{
    let ok=true;
    const collected={};
    q.questions.forEach(item=>{
      const qEl=box.querySelector(`[data-qid="${item.id}"]`);
      if(item.type==='bool'){
        const seg=qEl.querySelector('.seg');
        const ans=seg.dataset.answer;
        if(item.mustBeYes && ans!=='sim'){ ok=false; qEl.querySelector('.modal-err').classList.add('show'); }
        else if(!ans){ ok=false; qEl.querySelector('.modal-err').classList.add('show'); }
        collected[item.id]=ans||'';
      } else if(item.type==='text'){
        const val=qEl.querySelector('textarea').value.trim();
        if(val.length<3){ ok=false; qEl.querySelector('.modal-err').classList.add('show'); }
        collected[item.id]=val;
      } else if(item.type==='confirmText'){
        const val=qEl.querySelector('input[type=text]').value.trim();
        if(val!==item.mustMatch){ ok=false; qEl.querySelector('.modal-err').classList.add('show'); }
        collected[item.id]=val;
      } else if(item.type==='checklist'){
        const checked=[...qEl.querySelectorAll('input[type=checkbox]:checked')].map(c=>item.options[+c.dataset.opt]);
        collected[item.id]=checked;
      }
    });
    if(!ok) return;
    // libera a fase
    S.phaseUnlocked[faseNum-1]=true;
    S.transitionLog.push({fase:faseNum, ts:new Date().toISOString(), resumo:collected});
    save();
    closeModal();
    if(faseNum>=2) mirrorPhaseForward(faseNum-2);
    render(); renderPhases();
  });
}

// ---- Detecção de downgrade: DD caiu abaixo do mínimo de uma fase destravada e vazia ----
function getMaxUnlockedIdx(){
  let max=0;
  S.phaseUnlocked.forEach((u,i)=>{ if(u) max=i; });
  return max;
}
function phaseVacated(pi){
  return S.phases[pi].orders.every(o=>o.status!=='Aberta');
}
function checkDowngrade(fi){
  const maxUnlocked=getMaxUnlockedIdx();
  if(maxUnlocked<=fi) return null; // nada destravado acima do que a matemática justifica
  for(let i=fi+1;i<=maxUnlocked;i++){
    if(!phaseVacated(i)) return null; // ainda tem ordem viva lá — não sugere downgrade, só travaria posição aberta
  }
  return {fromIdx:maxUnlocked, toIdx:fi};
}
function openDowngradeModal(fromIdx,toIdx){
  const q=DOWNGRADE_QUESTIONNAIRE;
  const box=$('modalBox');
  $('modalOverlay').classList.add('show');
  let html=`<h3>📉 ${q.title}</h3><div class="modal-sub">${q.subtitle} (de FASE ${fromIdx+1} para FASE ${toIdx+1})</div>`;
  q.questions.forEach(item=>{
    html+=`<div class="modal-q" data-qid="${item.id}">`;
    if(item.type==='bool'){
      html+=`<div class="ql">${item.label}</div>
        <div class="seg" data-qtype="bool">
          <button type="button" data-val="sim">Sim</button>
          <button type="button" data-val="nao">Não</button>
        </div>
        <div class="modal-err">Esta confirmação é obrigatória para prosseguir.</div>`;
    } else if(item.type==='text'){
      html+=`<div class="ql">${item.label}</div>
        <textarea placeholder=""></textarea>
        <div class="modal-err">Descreva antes de prosseguir — não deixe em branco.</div>`;
    }
    html+=`</div>`;
  });
  html+=`<div class="modal-actions">
    <button class="modal-btn cancel" id="modalCancel">Deixar para depois</button>
    <button class="modal-btn confirm" id="modalConfirm">Confirmar downgrade</button>
  </div>`;
  box.innerHTML=html;
  box.querySelectorAll('[data-qtype="bool"] button').forEach(b=>{
    b.addEventListener('click',()=>{
      const seg=b.parentElement;
      seg.querySelectorAll('button').forEach(x=>x.classList.remove('on'));
      b.classList.add('on');
      seg.dataset.answer=b.dataset.val;
      seg.parentElement.querySelector('.modal-err')?.classList.remove('show');
    });
  });
  $('modalCancel').addEventListener('click', closeModal);
  $('modalConfirm').addEventListener('click',()=>{
    let ok=true;
    const collected={};
    q.questions.forEach(item=>{
      const qEl=box.querySelector(`[data-qid="${item.id}"]`);
      if(item.type==='bool'){
        const seg=qEl.querySelector('.seg');
        const ans=seg.dataset.answer;
        if(item.mustBeYes && ans!=='sim'){ ok=false; qEl.querySelector('.modal-err').classList.add('show'); }
        else if(!ans){ ok=false; qEl.querySelector('.modal-err').classList.add('show'); }
        collected[item.id]=ans||'';
      } else if(item.type==='text'){
        const val=qEl.querySelector('textarea').value.trim();
        if(val.length<3){ ok=false; qEl.querySelector('.modal-err').classList.add('show'); }
        collected[item.id]=val;
      }
    });
    if(!ok) return;
    for(let i=toIdx+1;i<=fromIdx;i++){ S.phaseUnlocked[i]=false; }
    S.transitionLog.push({fase:`downgrade ${fromIdx+1}→${toIdx+1}`, ts:new Date().toISOString(), resumo:collected});
    save();
    closeModal();
    render(); renderPhases();
  });
}

// ---- Espelhamento Fase 1 -> Fase 2 (Art. 3.8): mesma tese, novo stop/objetivo obrigatório ----
// ---- Espelhamento genérico: fase fromIdx -> fromIdx+1 (Art. 3.8) ----
// Reaplicável a qualquer momento, não só no instante da transição — é o que permite
// "curar" órfãos: ordens abertas numa fase já superada, que nunca deveriam existir ali.
function mirrorPhaseForward(fromIdx){
  const fFrom=S.phases[fromIdx], fTo=S.phases[fromIdx+1];
  if(!fTo) return false;
  let migrou=false;
  fFrom.orders.forEach(o=>{
    if(o.status!=='Aberta') return;
    let slot=fTo.orders.find(x=>!x.status && !x.lote);
    const mirrored={
      id:(o.id||'').replace(/\s*\(F\d\)$/,'')+` (F${fromIdx+2})`, par:o.par, tipo:o.tipo, lote:o.lote,
      entry:o.entry, sl:o.sl, tp:o.tp, // mantém valores antigos como placeholder — NUNCA zera o risco na transição
      result:0, status:'Aberta', needsReview:true,
    };
    if(slot){ Object.assign(slot, mirrored); }
    else { fTo.orders.push(mirrored); }
    o.status='Migrada'; // sai do risco da fase de origem, fica visível como histórico
    migrou=true;
  });
  return migrou;
}
// uma fase está CONGELADA (histórico puro, zero edição) quando a fase seguinte já foi destravada —
// "superada", nas suas palavras. Não existe mais operação viva dividida entre duas grades.
function phaseFrozen(pi){
  return pi<3 && !!S.phaseUnlocked[pi+1];
}
// roda a cada render: se alguma fase congelada ainda tem ordem 'Aberta' (órfã, criada depois
// da transição), arrasta pra frente automaticamente. Idempotente — sem órfãos, não faz nada.
function healSupersededPhases(){
  let mudou=false;
  for(let pi=0;pi<3;pi++){
    if(phaseFrozen(pi) && S.phases[pi].orders.some(o=>o.status==='Aberta')){
      if(mirrorPhaseForward(pi)) mudou=true;
    }
  }
  if(mudou) save();
  return mudou;
}

// ---- Guarda de teto de risco — a transição de fase é OBRIGATÓRIA, não decorativa.
// O teto agora é CONSOLIDADO (todas as grades + perdas realizadas): o orçamento de DD da
// fase é um só, não um cofre novo por grade. Lucro não amplia orçamento (Cláusula de Integridade). ----
function phaseTetoRisco(pi){
  const row=activeRiskMatrix()[pi];
  return row ? row.ddmax*S.params.saldoIni : 0;
}
function checkPhaseCap(pi, oi){
  const o=S.phases[pi].orders[oi];
  if(o.status!=='Aberta') return {excede:false};
  const estaOrdem=orderRisk(o);
  if(!(estaOrdem>0)) return {excede:false};
  // Art. 8.6 — risco da Ordem Gênese ≤ genRisk (1%) do saldo inicial
  if(pi===0 && oi===0 && estaOrdem > activeGenesisRiskLimit()*S.params.saldoIni){
    return {excede:true, tipo:'genese', total:estaOrdem, teto:activeGenesisRiskLimit()*S.params.saldoIni};
  }
  // Art. 9.3 — defesa final na Fase 4 limitada a 1% do saldo por ordem (escalado pelo perfil — SET 11)
  if(pi===3 && estaOrdem > 0.01*activeProfileFator()*S.params.saldoIni){
    return {excede:true, tipo:'defesaF4', total:estaOrdem, teto:0.01*activeProfileFator()*S.params.saldoIni};
  }
  const total=totalRiscoAbertoExc(pi,oi)+estaOrdem+Math.max(0,-netOpAtual())+perdaCicloArq();
  const teto=phaseTetoRisco(pi);
  return {excede: total>teto, tipo:'fase', total, teto};
}
function phaseCapBreachMessage(pi, check){
  if(check.tipo==='genese'){
    return `O risco da Ordem Gênese seria ${fmtMoney(check.total)}, acima do limite de ${fmtMoney(check.teto)} — 1% do saldo inicial (Art. 8.6). A Gênese não pode concentrar risco prematuro; ela é 25% da capacidade da Fase 1, não a fase inteira.`;
  }
  if(check.tipo==='defesaF4'){
    return `A defesa final da Fase 4 não pode exceder ${fmtMoney(check.teto)} — 1% do saldo (Art. 9.3). Esta ordem sozinha carregaria ${fmtMoney(check.total)} de risco. A Fase 4 existe para gerenciar o encerramento, não para ampliar exposição.`;
  }
  const ph=S.phases[pi];
  if(pi>=3){
    return `Isso levaria o risco consolidado da Operação Única (todas as grades + perdas realizadas) para ${fmtMoney(check.total)}, acima do teto de ${fmtMoney(check.teto)}. A Fase 4 é o limite absoluto ativo do perfil (${fmtPct(activeMDDLimit())}) — não há próxima fase para transicionar. A única ação permitida aqui é reduzir exposição (Art. 3.7), nunca ampliar.`;
  }
  const proximaFase=`FASE ${pi+2}`;
  return `Isso levaria o risco consolidado da Operação Única (todas as grades + perdas realizadas) para ${fmtMoney(check.total)}, acima do teto da ${ph.faseNome} (${fmtMoney(check.teto)}). A estrutura precisa crescer na grade da ${proximaFase} — complete a transição de fase para continuar. Não é permitido exceder o teto sem o questionário formal.`;
}
function phaseSupportForRisk(total){
  for(let i=0;i<S.matrix.length;i++){
    if(total<=phaseTetoRisco(i)) return i;
  }
  return -1;
}
function stopLimitSummary(pi, oi, check){
  const o=S.phases[pi].orders[oi];
  const supported=check.tipo==='fase'?phaseSupportForRisk(check.total):-1;
  const current=S.phases[pi];
  let reason='Stop Técnico Quantitativo acima do limite da fase atual.';
  if(check.tipo==='genese') reason='Stop gera risco acima do limite específico da Ordem Gênese.';
  if(check.tipo==='defesaF4') reason='Stop gera risco acima do limite por defesa final da Fase 4.';
  const supportText=supported>=0?S.phases[supported].faseNome:'nenhuma fase';
  return {
    supported,
    inline:`${reason} Risco calculado: ${fmtMoney(check.total)}. Limite atual: ${fmtMoney(check.teto)}. Fase que suportaria: ${supportText}.`,
    resumo:{
      ordem:o.id||`linha ${oi+1}`,
      par:o.par||'',
      faseAtual:current.faseNome,
      tipo:check.tipo,
      stop:o.sl||0,
      riscoCalculado:+(+check.total||0).toFixed(2),
      limiteAtual:+(+check.teto||0).toFixed(2),
      faseSuportada:supported>=0?S.phases[supported].faseNome:'',
      limiteFaseSuportada:supported>=0?+phaseTetoRisco(supported).toFixed(2):0,
    }
  };
}
function auditStopLimit(kind, resumo){
  S.transitionLog.push({fase:kind, ts:localDateTimeISO(), resumo});
}
function handleStopLimitBreach(pi, oi, check){
  const o=S.phases[pi].orders[oi];
  const info=stopLimitSummary(pi,oi,check);
  o.stopPhaseWarning=info.inline;
  if(check.tipo==='fase' && info.supported>pi){
    const target=S.phases[info.supported].faseNome;
    const phrase=`CONFIRMO ${target}`;
    const ok=prompt(
      `${info.inline}\n\n`+
      `Para aceitar a mudança de fase, digite exatamente:\n${phrase}\n\n`+
      `Sem essa confirmação, o Stop permanece registrado apenas como simulação/alerta de risco.`
    );
    if(ok===phrase){
      for(let i=0;i<=info.supported;i++) S.phaseUnlocked[i]=true;
      auditStopLimit('stop quantitativo - mudança de fase', {...info.resumo, confirmado:true, confirmacao:phrase});
      delete o.stopPhaseWarning;
      save(); render(); renderPhases();
      return true;
    }
    auditStopLimit('stop quantitativo acima da fase', {...info.resumo, confirmado:false});
    alert('Stop mantido para simulação, com risco visível. A fase não foi alterada porque a confirmação formal não foi concluída.');
    save(); render(); renderPhasesLite(pi); renderAuditLog();
    return false;
  }
  const kind=info.supported<0?'stop quantitativo limite absoluto':'stop quantitativo regra específica';
  auditStopLimit(kind, {...info.resumo, confirmado:false});
  alert(info.supported<0
    ? `${info.inline}\n\nNenhuma fase suporta este Stop. Ele viola o limite máximo absoluto e deve ser tratado como simulação de risco, não autorização operacional.`
    : info.inline);
  save(); render(); renderPhasesLite(pi); renderAuditLog();
  return false;
}
// ---- Guardas de instrumento e tese (Art. 3.5/3.6, decreto de banimento, Teto/Op) ----
// retorna null se ok, ou a mensagem de bloqueio
function orderGateMsg(pi, oi){
  const o=S.phases[pi].orders[oi];
  const ins=instFor(o.par);
  if(ins && ins.banned && !ins.unlocked){
    if(ins.name==='US500') return `🚫 ${ins.name} está SUSPENSO pelo Estatuto JP Wealth V10.0: ${ins.banReason} Pode aparecer apenas para referência/histórico; não opere sem deliberação formal.`;
    return `🚫 ${ins.name} está BANIDO por decreto pessoal: ${ins.banReason} Se for uma exceção deliberada, desbloqueie primeiro no Motor de Lote.`;
  }
  if(ins && ins.teto>0 && o.lote>ins.teto){
    return `🚫 Lote ${o.lote} acima do Teto/Op de ${ins.name} (${ins.teto}) — Regra 1 do Controle Objetivo de Risco. Ajuste o lote ou revise o teto no Motor de Lote.`;
  }
  // Operação Única Exclusiva: toda posição aberta pertence à mesma tese (mesmo par, mesma direção)
  let ref=null;
  outer:
  for(let p2=0;p2<S.phases.length;p2++){
    const os=S.phases[p2].orders;
    for(let o2=0;o2<os.length;o2++){
      if(p2===pi&&o2===oi) continue;
      const q=os[o2];
      if(q.status==='Aberta'&&q.par){ ref=q; break outer; }
    }
  }
  if(ref){
    const norm=s=>String(s||'').toUpperCase().replace(/[^A-Z0-9]/g,'');
    if(o.par && norm(o.par)!==norm(ref.par)){
      return `🚫 Operação Única Exclusiva (Art. 3.6): já existe posição aberta em ${ref.par}. Não é permitido abrir ${o.par} enquanto a operação atual não for encerrada.`;
    }
    if(o.tipo && ref.tipo && o.tipo!==ref.tipo){
      return `🚫 Operação Única (Art. 3.5): a tese ativa é ${ref.tipo} em ${ref.par}. Posição na direção contrária não pertence à mesma tese — encerre a operação antes de inverter.`;
    }
  }
  return null;
}


const DIVERGENCE_THRESHOLD=1.20; // 20% acima do risco programado
const DIVERGENCE_REASONS=[
  'Slippage de execução (gap, liquidez, spread)',
  'Erro de programação da ordem (SL mal calculado/registrado)',
  'Rompimento de protocolo — stop foi movido/ignorado sem justificativa',
  'Outro',
];
// ---- Fechamento definitivo de ordem — dupla confirmação, captura o Lucro Técnico no mesmo ato.
// Depois de confirmada, a linha trava por completo: só pode ser apagada, nunca mais editada. ----
function openCloseOrderModal(pi,oi){
  const o=S.phases[pi].orders[oi];
  const box=$('modalBox');
  $('modalOverlay').classList.add('show');
  const projetado=orderRisk(o);
  box.innerHTML=`
    <h3>🔒 Confirmar Fechamento — ${esc(o.id)||'(sem ID)'} ${esc(o.par)}</h3>
    <div class="modal-sub">Depois de confirmado, esta linha NÃO pode mais ser editada — só apagada. ${projetado>0?'Risco programado desta ordem: '+fmtMoney(projetado):''}</div>
    <div class="modal-q" data-qid="resultado">
      <div class="ql">Lucro Técnico / Resultado desta ordem ($) — negativo se foi prejuízo:</div>
      <input type="text" inputmode="decimal" id="closeResultInput" placeholder="0" value="${esc(o.result||'')}">
    </div>
    <div class="modal-q" data-qid="confirmtxt">
      <div class="ql">Digite <b>FECHADO</b> para confirmar:</div>
      <input type="text" id="closeConfirmInput" autocomplete="off">
      <div class="modal-err">Precisa digitar exatamente "FECHADO".</div>
    </div>
    <div class="modal-actions">
      <button class="modal-btn cancel" id="modalCancel">Cancelar</button>
      <button class="modal-btn confirm" id="modalConfirm">Confirmar Fechamento</button>
    </div>`;
  $('modalCancel').addEventListener('click', closeModal);
  $('modalConfirm').addEventListener('click',()=>{
    const resultVal=parseFloat(box.querySelector('#closeResultInput').value)||0;
    const confirmTxt=box.querySelector('#closeConfirmInput').value.trim();
    if(confirmTxt!=='FECHADO'){
      box.querySelector('[data-qid="confirmtxt"] .modal-err').classList.add('show');
      return;
    }
    o.status='Fechada';
    o.result=resultVal;
    save();
    closeModal();
    render(); renderPhases();
    checkDivergence(pi,oi);
  });
}

function checkDivergence(pi,oi){
  const o=S.phases[pi].orders[oi];
  if(o.status!=='Fechada') return;
  const result=+o.result||0;
  if(result>=0) return; // só audita prejuízo
  const projetado=orderRisk(o);
  if(projetado<=0) return;
  const divergencia=Math.abs(result)/projetado;
  if(divergencia<=DIVERGENCE_THRESHOLD) return;
  if(o._divergenceCheckedFor===result) return; // já perguntado para este valor exato
  openDivergenceModal(pi,oi,projetado,result,divergencia);
}
function openDivergenceModal(pi,oi,projetado,result,divergencia){
  const box=$('modalBox');
  const pctTxt=((divergencia-1)*100).toFixed(0);
  let html=`<h3>⚠️ Divergência de fechamento</h3>
    <div class="modal-sub">Prejuízo registrado ${fmtMoney(Math.abs(result))} — ${pctTxt}% acima do risco programado (${fmtMoney(projetado)}). Isso não bloqueia nada; é auditoria, não permissão.</div>
    <div class="modal-q" data-qid="motivo">
      <div class="ql">Qual foi a causa da divergência?</div>`;
  DIVERGENCE_REASONS.forEach((r,i)=>{
    html+=`<label class="check-row"><input type="radio" name="divreason" value="${i}"> ${r}</label>`;
  });
  html+=`<div class="modal-err">Selecione uma causa antes de prosseguir.</div>
    </div>
    <div class="modal-q" data-qid="detalhe" style="display:none">
      <div class="ql">Detalhe (opcional):</div>
      <textarea placeholder="Contexto adicional, se relevante"></textarea>
    </div>
    <div class="modal-actions">
      <button class="modal-btn confirm" id="modalConfirm">Registrar causa</button>
    </div>`;
  box.innerHTML=html;
  $('modalOverlay').classList.add('show');
  box.querySelectorAll('input[name=divreason]').forEach(r=>{
    r.addEventListener('change',()=>{
      box.querySelector('[data-qid="detalhe"]').style.display = r.value==='3'?'block':'none';
      box.querySelector('[data-qid="motivo"] .modal-err').classList.remove('show');
    });
  });
  $('modalConfirm').addEventListener('click',()=>{
    const sel=box.querySelector('input[name=divreason]:checked');
    if(!sel){ box.querySelector('[data-qid="motivo"] .modal-err').classList.add('show'); return; }
    const reasonText=DIVERGENCE_REASONS[+sel.value];
    const detalhe=box.querySelector('[data-qid="detalhe"] textarea')?.value.trim()||'';
    const o=S.phases[pi].orders[oi];
    o.divergenceReason=reasonText+(detalhe?(' — '+detalhe):'');
    o._divergenceCheckedFor=result;
    if(reasonText.startsWith('Rompimento')){
      S.protocolBreaches=(S.protocolBreaches||0)+1;
    }
    save();
    closeModal();
    render();
  });
}


// Constrói o corpo de UMA grade (meta + tabela + botão adicionar). frozen/qAct desabilitam edição.
function phaseBodyHTML(pi, qAct){
  const ph=S.phases[pi], isGen=pi===0, frozen=phaseFrozen(pi);
  const activeRow=activeRiskMatrix()[pi] || S.matrix[pi];
  const faixaDDLabel=`${fmtPct(activeRow.ddmin)}–${fmtPct(activeRow.ddmax)}`;
  let rows='', lsum=0, rsum=0, ltsum=0;
  ph.orders.forEach((o,oi)=>{
    const slot = isGen&&oi===0?'GÊNESE':(isGen?'DEF '+oi:`DEF ${pi+1}.${oi+1}`);
    const rr = (o.entry>0&&o.sl>0&&o.tp>0)?(Math.abs(o.tp-o.entry)/Math.abs(o.entry-o.sl)):0;
    const risco = o.status==='Aberta'?orderRisk(o):0;
    const semStop = o.status==='Aberta' && o.lote>0 && !(o.sl>0);
    const isFechada = o.status==='Fechada';
    const isMigrada = o.status==='Migrada';
    const readOnly = isMigrada || frozen || isFechada;
    const dis = (readOnly||qAct)?'disabled':'';
    const disStatus = (readOnly || (qAct && o.status!=='Aberta'))?'disabled':'';
    const rowCls = (isMigrada||frozen||isFechada)?'row-migrada':(o.stopPhaseWarning?'stop-breach':(o.needsReview?'needs-review':''));
    const slotLabel = isMigrada ? slot+' <span class="review-badge" style="color:var(--ink-faint);background:transparent">→ migrada</span>'
                     : frozen ? slot+' <span class="review-badge" style="color:var(--ink-faint);background:transparent">🔒 histórico</span>'
                     : semStop ? slot+' <span class="review-badge" style="color:var(--danger);background:var(--f4-bg)">✋ SEM STOP</span>'
                     : o.stopPhaseWarning ? slot+' <span class="review-badge" style="color:var(--danger);background:var(--f4-bg)">⚠ stop acima da fase</span>'
                     : o.needsReview ? slot+' <span class="review-badge">⚠ novo stop pendente</span>'
                     : slot;
    rows+=`<tr class="${slot==='GÊNESE'?'slot-gen':''} ${rowCls}">
      <td>${slotLabel}${o.stopPhaseWarning?`<div class="stop-warning">${esc(o.stopPhaseWarning)}</div>`:''}</td>
      <td class="calc">${rr>0?rr.toFixed(2):'—'}</td>
      <td class="calc ${risco>0?'neg':''}">${risco>0?fmtMoney(risco):(semStop?'<span style="color:var(--danger)">?!</span>':'—')}</td>
      <td><input data-p="${pi}" data-o="${oi}" data-f="id" value="${esc(o.id)}" placeholder="—" ${dis}></td>
      <td><select data-p="${pi}" data-o="${oi}" data-f="par" ${dis} style="text-align:center">
        <option value="" ${!o.par?'selected':''}>—</option>
        ${S.instruments.filter(ins=>!(ins.banned&&!ins.unlocked)||ins.name===String(o.par||'').toUpperCase().replace(/[^A-Z0-9]/g,'')).map(ins=>`<option ${String(o.par||'').toUpperCase().replace(/[^A-Z0-9]/g,'')===ins.name?'selected':''}>${ins.name}</option>`).join('')}
      </select></td>
      <td><select data-p="${pi}" data-o="${oi}" data-f="tipo" ${dis}><option ${o.tipo==='BUY'?'selected':''}>BUY</option><option ${o.tipo==='SELL'?'selected':''}>SELL</option></select></td>
      <td><input type="number" step="0.01" data-p="${pi}" data-o="${oi}" data-f="lote" value="${esc(o.lote||'')}" placeholder="0" ${dis}></td>
      <td><input type="number" step="0.00001" data-p="${pi}" data-o="${oi}" data-f="entry" value="${esc(o.entry||'')}" placeholder="0" ${dis}></td>
      <td class="stop-col"><input type="number" step="0.00001" data-p="${pi}" data-o="${oi}" data-f="sl" value="${esc(o.sl||'')}" placeholder="0" ${dis} title="Stop Técnico Quantitativo: pode ser simulado livremente, mas risco acima da fase exige confirmação e auditoria."><span class="stop-note">Stop Técnico Quantitativo</span></td>
      <td><input type="number" step="0.00001" data-p="${pi}" data-o="${oi}" data-f="tp" value="${esc(o.tp||'')}" placeholder="0" ${dis} ${o.needsReview?'style="border-color:var(--f2)"':''}></td>
      <td>
        <select data-p="${pi}" data-o="${oi}" data-f="status" ${disStatus}>
          <option value="" ${!o.status?'selected':''}>—</option>
          <option value="Aberta" ${o.status==='Aberta'?'selected':''}>Aberta</option>
          <option value="Fechada" ${o.status==='Fechada'?'selected':''}>Fechada</option>
          ${isMigrada?'<option value="Migrada" selected>Migrada</option>':''}
        </select>
      </td>
      <td><input type="number" step="0.01" data-p="${pi}" data-o="${oi}" data-f="result" value="${esc(o.result||'')}" placeholder="0"
            style="${isFechada?'':'opacity:.35'}" title="Lucro Técnico — só conta quando Fechada (Art. 9.2)" ${dis}></td>
      <td>${(isMigrada||frozen||qAct)?'':`<button class="row-del" data-delorder="${pi}:${oi}" title="Remover linha">✕</button>`}</td>
    </tr>`;
  });
  ph.orders.forEach(o=>{ lsum+=(+o.lote||0); if(o.status==='Aberta')rsum+=orderRisk(o); if(o.status==='Fechada')ltsum+=Math.max(0,(+o.result||0)); });
  return `
    <div class="phase-meta">
      <span>Faixa DD: <b>${faixaDDLabel}</b></span>
      <span>Teto alav.: <b>${ph.alavtxt}</b></span>
      <span>Teto risco: <b>${fmtMoney(phaseTetoRisco(pi))}</b></span>
      ${ltsum>0?`<span style="color:var(--f1)">Lucro técnico realizado: <b>${fmtMoney(ltsum)}</b></span>`:''}
      ${rsum>phaseTetoRisco(pi)?`<span style="color:var(--danger)">⚠ risco desta grade acima do teto — podar via LIFO</span>`:''}
      ${frozen?`<span style="color:var(--ink-faint)">🔒 Fase superada — somente histórico, sem edição</span>`:''}
    </div>
    <div style="overflow-x:auto">
    <table class="otable">
      <thead><tr><th>Slot</th><th>R:R</th><th>Risco $</th><th>ID</th><th>Par</th><th>Tipo</th><th>Lote</th><th>Entrada</th><th>Stop Técnico Quantitativo</th><th>TP</th><th>Status</th><th>Lucro Técnico $</th><th></th></tr></thead>
      <tbody>${rows}</tbody>
      <tfoot><tr><td>Σ ${ph.faseNome}</td><td></td><td class="calc risk-sum">${rsum>0?fmtMoney(rsum):'—'}</td><td colspan="3"></td><td class="lote-sum">${lsum.toFixed(2)}</td><td colspan="4"></td><td class="calc lucro-sum">${ltsum>0?fmtMoney(ltsum):'—'}</td><td></td></tr></tfoot>
    </table>
    </div>
    ${(frozen||qAct)?'':`<button class="reset-btn" data-addorder="${pi}" style="margin-top:10px; color:var(--violet); border-color:var(--violet)">+ Adicionar ordem à ${ph.faseNome}</button>`}`;
}
