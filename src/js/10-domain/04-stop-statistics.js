// ============ STOP ESTATÍSTICO §9 — Múltiplo de ATR estratificado + Raiz-N por horizonte ============
// Tudo em PERCENTUAL (§9.2): ATR% = ATR55/preço × 100. Comparação AO VIVO: usa o preço
// atual do ativo da Gênese (cotações do Motor de Lote), não a entrada.
function genesisOrder(){
  const g=S.phases[0].orders[0];
  if(g && (g.par||g.sl>0)) return g;
  for(const ph of S.phases){ const o=ph.orders.find(x=>x.status==='Aberta'&&x.par); if(o) return o; }
  return g||null;
}
function atrPctCalc(price){ // ATR(55) H4 em % — valor manual prevalece; senão deriva do ATR absoluto ÷ preço ao vivo
  if(S.atrPctManual>0) return S.atrPctManual;
  const atr=+S.atr55||0;
  return (price>0&&atr>0)? atr/price*100 : 0;
}
function atrStrat(m){ // §9.2.1 — Sistema de Interpretação Estratificada do Múltiplo de ATR
  if(!(m>0)) return null;
  if(m<1)   return {t:'FRÁGIL', d:'altamente exposto ao ruído', c:'var(--f4)'};
  if(m<2)   return {t:'LEVEMENTE FRÁGIL', d:'não recomendável p/ maturação longa', c:'var(--f3)'};
  if(m<3.5) return {t:'MÍNIMO REALISTA', d:'não recomendável p/ maturação longa', c:'var(--f2)'};
  if(m<5)   return {t:'NÍVEL NORMAL', d:'mínimo aceitável', c:'var(--f1)'};
  if(m<7)   return {t:'CONSERVADOR', d:'longa duração — exige alvo proporcional', c:'var(--f1)'};
  return {t:'ZONA SEGURA', d:'exige alvo proporcional', c:'var(--f1)'};
}
function riskIndicatorsHTML(active){
  const gen=genesisOrder();
  const ins=gen?instFor(gen.par):null;
  const priceLive=(ins&&ins.preco>0)?ins.preco:0;
  const F=S.stopF||1.8;
  const atrPct=atrPctCalc(priceLive);
  // Stop Técnico Quantitativo da Gênese em % AO VIVO: distância do preço atual até o SL mãe (§9 + pedido 3)
  const stopPct=(priceLive>0&&gen&&gen.sl>0)? Math.abs(priceLive-gen.sl)/priceLive*100 : 0;
  const mult=(atrPct>0&&stopPct>0)? stopPct/atrPct : 0;
  const strat=atrStrat(mult);
  const rz1=atrPct*Math.sqrt(30)*F;  // √30 ≈ 1 semana de candles H4 (§9.3)
  const rz2=atrPct*Math.sqrt(55)*F;  // √55 ≈ 2 semanas (§9.3.1)
  const pc=v=>v>0?v.toFixed(2).replace('.',',')+'%':'—';
  const verd=(rz)=> stopPct<=0||rz<=0 ? {t:'—',c:'var(--ink-faint)',d:''}
    : stopPct>=rz ? {t:'RESISTE',c:'var(--f1)',d:'stop ≥ mínimo estatístico'}
    : {t:'ZONA DE RUÍDO',c:'var(--f3)',d:'abaixo do mínimo — consciência exigida (§9.5)'};
  const v1=verd(rz1), v2=verd(rz2);
  const chip=(k,v,sub,col)=>`<div class="metric"><div class="k">${k}</div><div class="v sm" style="${col?'color:'+col:''}">${v}</div>${sub?`<div class="sub">${sub}</div>`:''}</div>`;
  return `<div class="card" style="margin-bottom:14px">
    <h2>Stop Loss Mínimo · Validação Estatística <span class="art">§9 · ao vivo: ${gen&&gen.par?esc(gen.par)+' @ '+(priceLive||'—'):'defina a gênese'} · SL mãe ${gen&&gen.sl>0?gen.sl:'—'}</span></h2>
    <!-- Fase 2C: o MÉTODO desce para disclosure, como no protótipo ("método ▾").
         Os campos continuam editáveis e no mesmo lugar do DOM — só deixam de
         disputar a leitura primária com os vereditos, que ficam à vista logo
         abaixo. O card do Stop deixa de ocupar o dobro da altura da Grade. -->
    <details class="jp-p3">
      <summary>método</summary>
    <div style="display:flex; gap:14px; flex-wrap:wrap; align-items:flex-end; margin-bottom:12px">
      <div class="field" style="margin-bottom:0; max-width:170px">
        <label>ATR(55) H4 em % <span class="art">§9.2</span></label>
        <input type="number" step="0.001" id="iAtrPct" value="${atrPct>0?+atrPct.toFixed(3):''}" placeholder="auto">
        <span class="note note-live">${S.atrPctManual>0?'manual — apague p/ voltar ao automático':'auto: ATR55 ÷ preço ao vivo'}</span>
      </div>
      <div class="field" style="margin-bottom:0; max-width:250px">
        <label>Fator F <span class="art">§9.3.2 · cauda estatística</span></label>
        <select id="iStopF">
          ${[1.25,1.5,1.8,2].includes(F)?'':`<option value="${F}" selected>${String(F).replace('.',',')} — personalizado</option>`}
          <option value="1.25" ${F===1.25?'selected':''}>1,25 — V10 proposto · cobre menos cauda</option>
          <option value="1.5" ${F===1.5?'selected':''}>1,50 — ~86,6% de confiança (1,5σ)</option>
          <option value="1.8" ${F===1.8?'selected':''}>1,80 — padrão JP Wealth · ~90%+</option>
          <option value="2" ${F===2?'selected':''}>2,00 — ~95,4% (2σ) · máx. conservador</option>
        </select>
        <span class="note">F maior → stop mínimo mais distante: resiste mais ao ruído natural, mas exige mais espaço e alvo proporcional. F menor → mínimo mais curto, maior chance de stop por respiração do ativo.</span>
      </div>
      <div class="field" style="margin-bottom:0; max-width:190px">
        <label>Stop Técnico Quantitativo da Gênese <span class="art">ao vivo</span></label>
        <input type="text" disabled value="${pc(stopPct)}">
        <span class="note">|preço atual − SL mãe| ÷ preço</span>
      </div>
    </div>
    </details>
    <div class="risk-primary-indicators">
      ${chip('Stop da Gênese · Múltiplo de ATR', `${pc(stopPct)} · ${mult>0?mult.toFixed(1).replace('.',',')+'x':'—'}`, strat?`<span style="color:${strat.c};font-weight:700">${strat.t}</span> · ${strat.d}`:'distância ao SL mãe ÷ ATR%')}
      ${chip('Raiz-N · resistência estatística', `√30 ${pc(rz1)} · √55 ${pc(rz2)}`,
        `1 sem <span style="color:${v1.c};font-weight:700">${v1.t}</span> · 2 sem <span style="color:${v2.c};font-weight:700">${v2.t}</span> · síntese <span style="color:${(stopPct>0&&atrPct>0)?(stopPct>=rz1?'var(--f1)':'var(--f3)'):'var(--ink-faint)'};font-weight:700">${(stopPct>0&&atrPct>0)?(stopPct>=rz2?'COERENTE 2 SEM':(stopPct>=rz1?'COERENTE 1 SEM':'VULNERÁVEL')):'—'}</span>`)}
    </div>
  </div>`;
}
// Classe CSS da fase: whitelist semântica, não escaping. Atributo `class` não deve
// aceitar valor arbitrário nem escapado — só os identificadores do catálogo oficial.
function phaseCssClass(ph){
  const permitido=DEFAULTS.phases.map(p=>p.cls);
  return (ph && permitido.includes(ph.cls)) ? ph.cls : '';
}
function renderPhases(){
  healSupersededPhases(); // corrige órfãos antes de desenhar qualquer coisa
  const qAct=quarantineActive(); // Art. 3.10: quarentena trava edição, permite apenas fechar
  const active=getMaxUnlockedIdx(); // grade ativa = fase mais avançada já liberada
  const cont=$('phaseContainer');
  const ph=S.phases[active];
  let html=riskIndicatorsHTML(active);
  if(noExternalProtectionActive()){
    html+=`<div class="risk-note" style="margin:0 0 14px; color:var(--f4); border-color:var(--f4)">${noExternalProtectionWarning()}</div>`;
  }
  // grade ATIVA — a única editável e sempre visível
  html+=`<div class="phase ${phaseCssClass(ph)}" data-phase="${active}">
    <div class="phase-head" style="cursor:default">
      <span class="badge">${esc(String(ph.faseNome||'').replace('FASE ','F'))}</span>
      <span>${esc(ph.title)}</span>
      <span class="here" style="margin-left:auto">◄ GRADE ATIVA</span>
    </div>
    <div class="phase-body">${phaseBodyHTML(active, qAct)}</div>
  </div>`;
  // botão de MIGRAR para a próxima fase (única forma de progredir — Art. 3.8)
  if(active<3){
    if(qAct){
      html+=`<div class="phase-meta" style="padding:12px 4px 2px">⛔ Migração de fase suspensa durante a quarentena (Art. 3.10).</div>`;
    } else {
      html+=`<button class="unlock-phase-btn" data-migrate="${active}" style="margin-top:8px; width:100%">⏭ Migrar para ${esc(S.phases[active+1].faseNome)} — responder questionário de transição</button>`;
    }
  } else {
    html+=`<div class="phase-meta" style="padding:12px 4px 2px">A Fase 4 é o limite absoluto ativo do perfil (${fmtPct(activeMDDLimit())}) — não há próxima fase. A única ação permitida é reduzir exposição (Art. 3.7).</div>`;
  }
  // FASES ANTERIORES — escondidas por padrão (estética limpa), read-only ao expandir
  if(active>0){
    let hist='';
    for(let pi=0; pi<active; pi++){
      hist+=`<div class="phase ${phaseCssClass(S.phases[pi])} collapsed" data-phase="${pi}" style="margin-top:10px">
        <div class="phase-head" data-toggle="${pi}">
          <span class="badge">${esc(String(S.phases[pi].faseNome||'').replace('FASE ','F'))}</span>
          <span>${esc(S.phases[pi].title)}</span>
          <span style="margin-left:auto; font-size:calc(10px * var(--fs-scale)); color:var(--ink-faint)">🔒 histórico</span>
          <span class="chev">▾</span>
        </div>
        <div class="phase-body">${phaseBodyHTML(pi, qAct)}</div>
      </div>`;
    }
    html+=`<button class="reset-btn" id="histToggle" style="margin-top:14px">▸ Ver fases anteriores (${active})</button>
      <div id="histWrap" style="display:none; margin-top:6px">${hist}</div>`;
  }
  cont.innerHTML=html;
  // bind toggles das fases de histórico
  cont.querySelectorAll('.phase-head[data-toggle]').forEach(h=>h.addEventListener('click',e=>{
    if(e.target.closest('input,select'))return;
    h.parentElement.classList.toggle('collapsed');
  }));
  // bind MIGRAR — sequencial (Art. 3.8), suspenso em quarentena
  cont.querySelectorAll('[data-migrate]').forEach(btn=>{
    btn.addEventListener('click',e=>{
      e.stopPropagation();
      const from=+btn.dataset.migrate, fn=from+2; // faseNum 1-based da próxima fase
      if(quarantineActive()){ alert('⛔ Quarentena ativa até '+S.quarantine.fim+' — transições de fase suspensas (Art. 3.10).'); return; }
      if(!S.phaseUnlocked[fn-2]){ alert('🚫 Transição sequencial obrigatória (Art. 3.8).'); return; }
      openTransitionModal(fn);
    });
  });
  // bind histórico toggle
  const ht=$('histToggle');
  if(ht) ht.addEventListener('click',()=>{
    const w=$('histWrap'); const open=w.style.display!=='none';
    w.style.display=open?'none':'block';
    ht.textContent=(open?'▸':'▾')+' Ver fases anteriores ('+active+')';
  });
  // bind ATR% / Fator F do painel de Stop Estatístico (§9)
  const ap=$('iAtrPct');
  if(ap) ap.addEventListener('change',()=>{
    S.atrPctManual=parseFloat(ap.value)||0; // vazio/0 = volta ao automático
    save(); renderPhases();
  });
  const sfEl=$('iStopF');
  if(sfEl) sfEl.addEventListener('change',()=>{
    const v=parseFloat(sfEl.value);
    S.stopF=(v>=1&&v<=2.5)?v:1.8;
    save(); renderPhases();
  });
  // bind adicionar ordem (sem teto artificial — o risco/alavancagem já é fiscalizado pelo semáforo e LIFO)
  cont.querySelectorAll('[data-addorder]').forEach(btn=>{
    btn.addEventListener('click',e=>{
      e.stopPropagation();
      const pi=+btn.dataset.addorder;
      S.phases[pi].orders.push({id:'',par:'',tipo:'BUY',lote:0,entry:0,sl:0,tp:0,result:0,status:''});
      save(); renderPhases();
      // foca no ID da nova linha
      const rows=document.querySelectorAll(`.phase[data-phase="${pi}"] tbody tr`);
      const last=rows[rows.length-1];
      if(last){
        last.classList.add('is-new-order');
        last.querySelector('input[data-f="id"]')?.focus();
      }
    });
  });
  // bind remover ordem — sem fricção se vazia, confirma se tiver dado real
  cont.querySelectorAll('[data-delorder]').forEach(btn=>{
    btn.addEventListener('click',e=>{
      e.stopPropagation();
      const [pi,oi]=btn.dataset.delorder.split(':').map(Number);
      const o=S.phases[pi].orders[oi];
      const temDado = !!(o.id||o.par||o.lote||o.entry||o.sl||o.tp||o.status||o.result);
      if(temDado && !confirm('Esta linha tem dados registrados. Remover mesmo assim?')) return;
      const eraOperacional = typeof operationOrderIsLive==='function' && operationOrderIsLive(o);
      S.phases[pi].orders.splice(oi,1);
      // ABANDONO ADMINISTRATIVO. Excluir a ULTIMA ordem operacional apaga a
      // evidencia que constituia a Operacao Unica; a entidade nao pode
      // sobreviver a isso. Se ela sobrevivesse, a guarda de nascimento
      // (`!S.activeOperation`) falharia na proxima Genese e a nova tese herdaria
      // identidade, abertura e proveniencia da anterior — medido: um registro
      // GBPUSD gravado como aberto em outra data, com openedAtSource
      // 'genesis_transition', sob o operationId da operacao anterior.
      //
      // Nao e finalizacao e nao finge ser: NENHUM registro no Historico, NENHUMA
      // consolidacao em cycleRealizado, NENHUM reset de fases. E o mesmo
      // tratamento do reinicio administrativo de periodo.
      //
      // A limpeza acontece no ATO EXPLICITO, e nao por heuristica de "grades
      // vazias": uma operacao cujas ordens estao todas FECHADAS continua viva e
      // suas linhas continuam na grade — e disso depende a exclusividade da tese.
      if(eraOperacional && S.activeOperation && typeof operationLiveOrders==='function'
         && operationLiveOrders().length===0){
        if(typeof dgLogChange==='function'){
          dgLogChange('operation','abandoned', S.activeOperation.operationId,
            'Operação Única abandonada: última ordem operacional excluída pelo operador');
        }
        S.activeOperation=null;
      }
      save(); renderPhases();
    });
  });
  // bind order inputs — texto/número: atualização leve (preserva foco). selects: reconstrução completa (evento discreto).
  cont.querySelectorAll('input').forEach(inp=>{
    inp.addEventListener('focus',()=>{
      inp.dataset.prevval=inp.value; // snapshot para poder reverter se estourar o teto da fase
    });
    inp.addEventListener('input',()=>{
      const pi=+inp.dataset.p, oi=+inp.dataset.o, f=inp.dataset.f;
      // autofill/edição programática não dispara 'focus' — semeia o snapshot com o valor do modelo
      if(inp.dataset.prevval===undefined) inp.dataset.prevval=String(S.phases[pi].orders[oi][f]??'');
      let val=inp.value;
      if(['lote','entry','sl','tp','result'].includes(f)) val=parseFloat(val)||0;
      S.phases[pi].orders[oi][f]=val;
      // NÃO há gancho de status aqui: este laço é querySelectorAll('input') e o
      // campo Status é um <select>. A chamada que existia neste ponto era
      // inalcançável — a Operação Única nunca nascia pelo grid. O gancho vive no
      // laço de <select>, depois das guardas de abertura.
      if((f==='sl'||f==='tp') && S.phases[pi].orders[oi].needsReview){
        S.phases[pi].orders[oi].needsReview=false; // tocou no stop -> considera revisado
      }
      save(); render(); renderPhasesLite(pi);
    });
    inp.addEventListener('change',()=>{
      const pi=+inp.dataset.p, oi=+inp.dataset.o, f=inp.dataset.f;
      const o=S.phases[pi].orders[oi];
      // Resultado informado e ato confirmado, e e o que mais move o drawdown.
      if(f==='result'){
        if(typeof operationTouchAccountPhase==='function') operationTouchAccountPhase();
        save(); checkDivergence(pi,oi); return;
      }
      const revert=()=>{
        const raw=inp.dataset.prevval??'';
        const val=['lote','entry','sl','tp'].includes(f)?(parseFloat(raw)||0):raw;
        S.phases[pi].orders[oi][f]=val;
        inp.value=val||'';
        save(); render(); renderPhasesLite(pi);
      };
      if(o.status==='Aberta'){
        if(f==='sl' && !(o.sl>0)){
          alert('🚫 Ordem aberta não pode ficar sem stop — o SL é obrigatório em toda ordem (Função de Auditoria / Estatuto). Feche a posição se a intenção era removê-la.');
          revert(); return;
        }
        if(f==='par'||f==='lote'){
          const msg=orderGateMsg(pi,oi);
          if(msg){ alert(msg); revert(); return; }
        }
      }
      if(f==='lote'||f==='entry'||f==='sl'){
        const check=checkPhaseCap(pi,oi);
        if(check.excede){
          if(f==='sl'){
            handleStopLimitBreach(pi,oi,check);
            return;
          }
          alert('🚫 TETO DE RISCO — '+phaseCapBreachMessage(pi,check));
          revert(); return;
        } else if(f==='sl' && o.stopPhaseWarning){
          delete o.stopPhaseWarning;
          save(); render(); renderPhases();
        }
      }
      if(f==='par'){ renderPhases(); } // par novo muda risco/nocional — redesenha
      // EDICAO COMPROMETIDA: chegar aqui significa que o valor sobreviveu a
      // todas as guardas e a todas as reversoes — os caminhos de recusa saem por
      // `return` antes. So agora o estado e uma afirmacao do operador, e so agora
      // a Fase da Conta pode virar evidencia historica.
      if(typeof operationTouchAccountPhase==='function') operationTouchAccountPhase();
      save();
    });
  });
  cont.querySelectorAll('select').forEach(sel=>{
    sel.addEventListener('change',()=>{
      const pi=+sel.dataset.p, oi=+sel.dataset.o, f=sel.dataset.f;
      const o=S.phases[pi].orders[oi];
      if(f==='status' && sel.value==='Aberta'){
        const prevStatus=o.status;
        o.status='Aberta'; // aplica temporariamente para as guardas considerarem esta ordem

        // ---- GUARDAS PURAMENTE REJEITADORAS ----------------------------------
        // Todas antes do nascimento: uma ordem RECUSADA jamais pode criar
        // entidade. Nenhuma delas produz efeito colateral — só decidem se o ato
        // acontece.
        let msg=null;
        if(!o.par) msg='🚫 Defina o PAR antes de marcar a ordem como Aberta — sem par o risco e o nocional ficam indefinidos.';
        if(!msg && !(o.sl>0) && o.lote>0) msg='🚫 Não é permitido abrir ordem sem stop — registre o SL antes de marcar como Aberta (Função de Auditoria / Estatuto).';
        if(!msg) msg=orderGateMsg(pi,oi);
        if(msg){
          o.status=prevStatus; // reverte
          sel.value=prevStatus||'';
          alert(msg);
          return;
        }
        // Última rejeição possível. Ela ficava DEPOIS de handleStopLimitBreach,
        // e foi trazida para cá porque um "não" do operador aqui reverteria uma
        // abertura que já tinha destravado fase e carimbado evento — efeito
        // colateral sobrevivendo a um ato recusado.
        if(shouldWarnManualRiskConfirmation()){
          const ok=confirm('Você está prestes a registrar uma operação sem Equity Protector ativo. Confirme que o risco, o drawdown e a exposição foram verificados manualmente.');
          if(!ok){
            o.status=prevStatus;
            sel.value=prevStatus||'';
            return;
          }
        }

        // ---- ABERTURA ACEITA: A OPERAÇÃO NASCE AQUI --------------------------
        // Depois da última guarda que pode rejeitar, e ANTES do primeiro efeito
        // colateral que pertence à operação aceita.
        //
        // O nascimento vive neste laço de <select> — e não no de <input> — porque
        // o campo Status é um <select>: o gancho que existia lá era código morto e
        // a entidade jamais nascia pelo grid.
        //
        // A ORDEM IMPORTA. handleStopLimitBreach destrava fase e carimba o evento
        // via operationStampTransition, que lê S.activeOperation. Com o nascimento
        // depois dele, o destravamento provocado pela PRÓPRIA Gênese da operação
        // era carimbado com operationId:null, operationResolveGridPhaseMax o
        // descartava, e o registro imutável afirmava "Fase máxima da Grade: FASE 1"
        // para uma operação que viveu inteira na FASE 2 — a fase que essa mesma
        // ordem forçou. Não se reconstrói isso por cronologia: o vínculo tem de
        // existir no instante do carimbo.
        if(typeof operationOnOrderStatus==='function') operationOnOrderStatus(o,'Aberta',pi,oi);

        // ---- EFEITOS COLATERAIS DA OPERAÇÃO ACEITA ---------------------------
        // Já existe identidade viva: o evento de destravamento nasce vinculado.
        const check=checkPhaseCap(pi,oi);
        if(check.excede) handleStopLimitBreach(pi,oi,check);
      } else if(f==='status' && sel.value==='Fechada'){
        const prevStatus=o.status;
        sel.value=prevStatus||''; // reverte visualmente até confirmar no modal
        openCloseOrderModal(pi,oi);
        return;
      } else if(f==='tipo'){
        const prevTipo=o.tipo;
        o.tipo=sel.value;
        if(o.status==='Aberta'){
          const msg=orderGateMsg(pi,oi);
          if(msg){ o.tipo=prevTipo; sel.value=prevTipo; alert(msg); return; }
        }
      } else if(f==='par'){
        const prevPar=o.par;
        o.par=sel.value;
        if(o.status==='Aberta'){
          const msg=orderGateMsg(pi,oi);
          if(msg){ o.par=prevPar; sel.value=prevPar||''; alert(msg); return; }
          // TETO DE RISCO DA FASE: trocar o instrumento muda o risco em USD da
          // ordem tanto quanto mudar o lote, porque orderRisk() depende de cpl e
          // da conversão da moeda de cotação — de JPY para USD o fator chega a
          // duas ordens de grandeza. O ramo de <input> já barrava lote/entry/sl
          // com esta mesma guarda; a troca de par escapava dela e ultrapassava o
          // teto consolidado da grade sem alerta, sem reversão e sem o
          // questionário de transição.
          //
          // NENHUM PARÂMETRO NORMATIVO MUDA: aplica-se a checagem que já existe,
          // com os mesmos limites, a um caminho que estava sem ela. É restauração
          // de aderência ao Estatuto, não alteração dele.
          const check=checkPhaseCap(pi,oi);
          if(check.excede){
            o.par=prevPar; sel.value=prevPar||'';
            alert('🚫 TETO DE RISCO — '+phaseCapBreachMessage(pi,check));
            save(); render(); renderPhases();
            return;
          }
        }
      } else {
        S.phases[pi].orders[oi][f]=sel.value;
      }
      save(); render();
      renderPhases(); // status/tipo mudam estrutura visual da linha — rebuild completo é seguro aqui
    });
  });
}
// re-render só os campos calculados de uma fase (evita perder foco)
function renderPhasesLite(pi){
  // recalcula R:R e risco$ inline sem reconstruir inputs
  const phaseEl=document.querySelector(`.phase[data-phase="${pi}"]`);
  if(!phaseEl)return;
  const ph=S.phases[pi];
  const rows=phaseEl.querySelectorAll('tbody tr');
  let lsum=0,rsum=0,ltsum=0;
  ph.orders.forEach((o,oi)=>{
    const rr=(o.entry>0&&o.sl>0&&o.tp>0)?(Math.abs(o.tp-o.entry)/Math.abs(o.entry-o.sl)):0;
    const risco=o.status==='Aberta'?orderRisk(o):0;
    const cells=rows[oi].querySelectorAll('.calc');
    if(cells[0])cells[0].textContent=rr>0?rr.toFixed(2):'—';
    if(cells[1]){cells[1].textContent=risco>0?fmtMoney(risco):'—'; cells[1].className='calc '+(risco>0?'neg':'');}
    lsum+=(+o.lote||0); rsum+=risco;
    if(o.status==='Fechada') ltsum+=Math.max(0,(+o.result||0));
  });
  const loteSum=phaseEl.querySelector('tfoot .lote-sum');
  const riskSum=phaseEl.querySelector('tfoot .risk-sum');
  const lucroSum=phaseEl.querySelector('tfoot .lucro-sum');
  if(loteSum) loteSum.textContent=lsum.toFixed(2);
  if(riskSum) riskSum.textContent=rsum>0?fmtMoney(rsum):'—';
  if(lucroSum) lucroSum.textContent=ltsum>0?fmtMoney(ltsum):'—';
}

// ---- Params screen ----
function renderParams(){
  const p=S.params;
  const pr=getActiveRiskProfile();
  const matrixActive=activeRiskMatrix();
  const setTxt=(id,v)=>{ const el=$(id); if(el) el.textContent=v; };
  setTxt('rpSaldoIni',fmtMoney2(p.saldoIni||0));
  setTxt('rpSaldoAtu',fmtMoney2(p.saldoAtu||0));
  setTxt('rpInicio',p.inicio||'—');
  setTxt('rpMDD',fmtPct(activeMDDLimit()));
  setTxt('rpAlarm',fmtPct(activeAlarmLimit()));
  setTxt('rpGenLev',fmtX(pr.lev||p.genLev||0));
  setTxt('rpGenRisk',fmtPct(activeGenesisRiskLimit()));
  setTxt('rpFW',fmtPct(activeProfileFator()));
  setTxt('rpVrmN',(p.vrmN||0).toLocaleString('pt-BR',{minimumFractionDigits:2,maximumFractionDigits:2}));
  setTxt('rpVrmHV',(p.vrmHV||0).toLocaleString('pt-BR',{minimumFractionDigits:2,maximumFractionDigits:2}));
  setTxt('rpRefM',pctView(p.refM));
  setTxt('rpRefA',pctView(p.refA));
  const map={pSaldoIni:'saldoIni',pSaldoAtu:'saldoAtu',pInicio:'inicio',pMDD:'mdd',pAlarm:'alarm',
    pGenLev:'genLev',pGenRisk:'genRisk',pFW:'fw',pVrmN:'vrmN',pVrmHV:'vrmHV',pRefM:'refM',pRefA:'refA'};
  const pctInputs=new Set(['pMDD','pAlarm','pGenRisk','pFW','pRefM','pRefA']);
  for(const id in map){
    const el=$(id); if(!el) continue;
    const key=map[id];
    el.value=pctInputs.has(id)?decimalToPercentInput(p[key]):p[key];
  }
  // matrix
  const mb=$('matrixBody');
  mb.innerHTML=matrixActive.map((m,i)=>`<tr>
      <td class="hl">${esc(m.nome)}</td>
      <td>${fmtPct(m.ddmin)}</td>
      <td>${fmtPct(m.ddmax)}</td>
      <td>${fmtPct(m.baseDdmin)}–${fmtPct(m.baseDdmax)}</td>
      <td>${fmtX(m.alav)}</td>
      <td>${esc(pr.name)} · ${Math.round(activeProfileFator()*100)}%</td>
    </tr>`).join('');
  $('iAtr55').value=S.atr55; $('iAtr660').value=S.atr660;
}

// ---- Atualização automática de câmbio (Frankfurter, ECB, sem chave) ----
// Só cobre os 8 pares de câmbio. US500 permanece suspenso pelo Estatuto V10.0.
// XAUUSD nem entra aqui — banido, sem motivo para infraestrutura.
const FX_MAP = {
  EURUSD:{base:'EUR',quote:'USD'}, GBPUSD:{base:'GBP',quote:'USD'},
  AUDUSD:{base:'AUD',quote:'USD'}, NZDUSD:{base:'NZD',quote:'USD'},
  USDJPY:{base:'USD',quote:'JPY'}, USDCHF:{base:'USD',quote:'CHF'},
  USDCAD:{base:'USD',quote:'CAD'}, AUDCAD:{base:'AUD',quote:'CAD'},
};
let fxAutoFetchedThisSession=false;
async function fetchOneRate(base,quote){
  const ctrl=new AbortController();
  const timer=setTimeout(()=>ctrl.abort(),6000); // nunca trava esperando para sempre
  try{
    const res=await fetch(`https://api.frankfurter.dev/v2/rate/${base}/${quote}`,{signal:ctrl.signal});
    clearTimeout(timer);
    if(!res.ok) throw new Error('http '+res.status);
    const data=await res.json();
    if(typeof data.rate!=='number' || !isFinite(data.rate)) throw new Error('resposta sem rate válido');
    return data.rate;
  }catch(e){ clearTimeout(timer); throw e; }
}
async function updateFxRates(){
  const operationEpoch=jpWealthPersistenceEpoch();
  const statusEl=$('fxFetchStatus');
  const btn=$('fxUpdateBtn');
  if(btn) btn.disabled=true;
  if(statusEl){ statusEl.textContent='🔄 Atualizando cotações FX…'; statusEl.className='fx-status busy'; }
  const names=Object.keys(FX_MAP);
  const results=await Promise.allSettled(names.map(n=>fetchOneRate(FX_MAP[n].base,FX_MAP[n].quote)));
  if(jpWealthPersistenceIsBlocked() || operationEpoch!==jpWealthPersistenceEpoch()) return;
  let ok=0, fail=0;
  results.forEach((r,i)=>{
    const name=names[i];
    const ins=S.instruments.find(x=>x.name===name);
    if(!ins) return;
    if(r.status==='fulfilled'){ ins.preco=r.value; ins.updated=todayISO(); ok++; }
    else fail++;
  });
  if(ok>0) save();
  renderMotor();
  render(); renderPhases(); // preços novos mudam risco/nocional/ATR% e o stop vivo do §9
  if(statusEl){
    if(fail===0){ statusEl.textContent='✅ '+ok+'/'+names.length+' pares atualizados agora (taxa ECB via Frankfurter)'; statusEl.className='fx-status ok'; }
    else if(ok===0){ statusEl.textContent='⚠️ Sem conexão ou serviço indisponível — mantendo últimos preços salvos'; statusEl.className='fx-status err'; }
    else { statusEl.textContent='⚠️ '+ok+'/'+names.length+' atualizados, '+fail+' falharam — revise manualmente os que faltaram'; statusEl.className='fx-status warn'; }
  }
  if(btn) btn.disabled=false;
}


function daysStale(dateStr){
  if(!dateStr) return 999;
  const then=new Date(dateStr+'T00:00:00');
  const now=new Date(); now.setHours(0,0,0,0);
  return Math.round((now-then)/86400000);
}
function staleInfo(dateStr){
  const d=daysStale(dateStr);
  if(d<=3) return {cls:'fresh', label:d<=0?'hoje':d+' dia'+(d>1?'s':'')+' atrás'};
  if(d<=20) return {cls:'warn', label:d+' dias atrás'};
  return {cls:'danger', label:d+' dias — não confiável'};
}
function dateISO(d){
  const x=d instanceof Date ? d : new Date(d);
  const y=x.getFullYear();
  const m=String(x.getMonth()+1).padStart(2,'0');
  const day=String(x.getDate()).padStart(2,'0');
  return `${y}-${m}-${day}`;
}
function todayISO(){ return dateISO(new Date()); }
function localDateTimeISO(d=new Date()){
  const x=d instanceof Date ? d : new Date(d);
  const hh=String(x.getHours()).padStart(2,'0');
  const mm=String(x.getMinutes()).padStart(2,'0');
  const ss=String(x.getSeconds()).padStart(2,'0');
  return `${dateISO(x)}T${hh}:${mm}:${ss}`;
}
function addDaysISO(days){ const d=new Date(); d.setDate(d.getDate()+days); return dateISO(d); }

function renderMotor(){
  $('mExpAlvo').value=S.expAlvo;
  const mb=$('motorBody'); mb.innerHTML='';
  S.instruments.forEach((ins,i)=>{
    const valorLote=usdPerBase(ins)*ins.cpl; // nocional USD real (base USD = $100k fixo; AUDCAD via AUDUSD)
    const exp=S.expAlvo*S.params.saldoIni; // Art. 3.4§2: sizing sempre sobre saldo inicial
    const lotePad=valorLote>0?exp/valorLote:0;
    const loteHV=lotePad*0.5;
    const st=staleInfo(ins.updated);
    const tr=document.createElement('tr');
    tr.dataset.idx=i;

    if(ins.banned && !ins.unlocked){
      const blockLabel=ins.name==='US500'?'SUSPENSO':'BANIDO';
      const unlockLabel=ins.name==='US500'?'Registrar deliberação':'Desbloquear (exceção)';
      tr.className='row-banned';
      tr.innerHTML=`
        <td class="hl">${esc(ins.name)}</td>
        <td>${esc(ins.preco)}</td>
        <td colspan="2"><span class="ban-label">🔒 ${blockLabel}</span></td>
        <td>${fmtMoney(valorLote)}</td>
        <td>—</td><td>—</td><td>${(+ins.teto||0).toFixed(2)}</td>
        <td><button class="unlock-btn" data-unlock="${i}">${unlockLabel}</button></td>
      `;
      mb.appendChild(tr);
      return;
    }

    tr.innerHTML=`
      <td class="hl">${esc(ins.name)}${ins.banned?' <span title="'+esc(ins.banReason)+'" style="cursor:help">⚠️</span>':''}</td>
      <td class="editable"><input type="number" step="0.00001" data-f="preco" value="${esc(ins.preco)}"></td>
      <td><span class="stale-pill ${st.cls}">${st.label}</span></td>
      <td class="editable"><input type="number" step="1" data-f="cpl" value="${esc(ins.cpl)}"></td>
      <td class="calc-valorlote">${fmtMoney(valorLote)}</td>
      <td class="hl calc-lotepad">${lotePad.toFixed(2)}</td>
      <td class="calc-lotehv">${loteHV.toFixed(2)}</td>
      <td class="editable"><input type="number" step="0.01" data-f="teto" value="${esc(ins.teto)}"></td>
      <td>${ins.banned?'<button class="unlock-btn" data-relock="'+i+'" style="color:var(--f1);border-color:var(--f1)">Travar</button>':''}</td>
    `;
    mb.appendChild(tr);
  });

  // bind price/cpl/teto edits
  mb.querySelectorAll('input').forEach(inp=>{
    inp.addEventListener('input',()=>{
      const tr=inp.closest('tr'); const i=+tr.dataset.idx; const f=inp.dataset.f;
      const val=parseFloat(inp.value)||0;
      S.instruments[i][f]=val;
      if(f==='preco') S.instruments[i].updated=todayISO(); // editar preço = confirmar que está atual
      save();
      recomputeMotorRow(i);
    });
  });
  // bind unlock/relock
  mb.querySelectorAll('[data-unlock]').forEach(btn=>{
    btn.addEventListener('click',()=>{
      const i=+btn.dataset.unlock;
      const ins=S.instruments[i];
      const msg=ins.name==='US500'
        ? `"${ins.name}" está suspenso pelo Estatuto JP Wealth V10.0: ${ins.banReason}\n\nSó registre liberação se houver deliberação formal.`
        : `"${ins.name}" está bloqueado por decreto pessoal: ${ins.banReason}\n\nDesbloquear mesmo assim? Isso é uma exceção deliberada ao seu próprio Estatuto.`;
      if(confirm(msg)){
        ins.unlocked=true; save(); renderMotor();
      }
    });
  });
  mb.querySelectorAll('[data-relock]').forEach(btn=>{
    btn.addEventListener('click',()=>{
      const i=+btn.dataset.relock;
      S.instruments[i].unlocked=false; save(); renderMotor();
    });
  });

  const pb=$('profileBody');
  pb.innerHTML=RISK_PROFILES.map(pr=>`<tr>
      <td class="hl">${esc(pr.name)}</td>
      <td>${pr.fator.toFixed(2)}</td>
      <td>${fmtPct(pr.ddrTarget)}</td>
      <td>${fmtPct(pr.scenarioDD15)}</td>
      <td>${fmtX(pr.orderLeverage)}</td>
      <td>${esc(pr.limit)}</td>
    </tr>`).join('');
}
// recalcula só as células derivadas de uma linha (preserva foco)
function recomputeMotorRow(i){
  const tr=document.querySelector(`#motorBody tr[data-idx="${i}"]`);
  if(!tr || tr.classList.contains('row-banned')) return;
  const ins=S.instruments[i];
  const valorLote=usdPerBase(ins)*ins.cpl; // nocional USD real
  const exp=S.expAlvo*S.params.saldoIni; // Art. 3.4§2: sizing sempre sobre saldo inicial
  const lotePad=valorLote>0?exp/valorLote:0;
  const loteHV=lotePad*0.5;
  tr.querySelector('.calc-valorlote').textContent=fmtMoney(valorLote);
  tr.querySelector('.calc-lotepad').textContent=lotePad.toFixed(2);
  tr.querySelector('.calc-lotehv').textContent=loteHV.toFixed(2);
  const st=staleInfo(ins.updated);
  const pill=tr.querySelector('.stale-pill');
  pill.className='stale-pill '+st.cls; pill.textContent=st.label;
}


// ---- Contas screen ----
function getMaster(){ return S.accounts.find(a=>a.tipo==='MESTRE')||S.accounts[0]; }
function profileFactor(perfilName){
  return riskProfileByAny(perfilName).fator;
}
function contaCalc(a){
  const master=getMaster();
  const lucro=a.sini>0?(a.satu-a.sini)/a.sini:0;
  const corr=(master&&master.sini>0)?a.sini/master.sini:0;
  const fw=1; // V10: sem multiplicador fixo; Art. 10.1 usa normalização por saldo × fator de perfil
  const pf=profileFactor(a.perfil);
  const loteVs=corr*fw*pf;
  return {lucro,corr,fw,pf,loteVs};
}
// ---- PIN de alteração de perfil (fricção deliberada, NÃO é criptografia real —
//      qualquer um com DevTools pode editar o localStorage e contornar isso.
//      O objetivo é impedir o clique impulsivo, não resistir a um invasor.) ----
async function sha256Hex(text){
  const enc=new TextEncoder().encode(text);
  const buf=await crypto.subtle.digest('SHA-256',enc);
  return Array.from(new Uint8Array(buf)).map(b=>b.toString(16).padStart(2,'0')).join('');
}
async function requestPinUnlock(operationEpoch=jpWealthPersistenceEpoch()){
  if(!S.riskPinHash){
    const p1=prompt('Nenhuma senha definida ainda.\nCrie uma senha para futuras alterações de perfil de risco:');
    if(p1===null || p1.trim()==='') return false;
    const p2=prompt('Confirme a senha:');
    if(p2!==p1){ alert('As senhas não coincidem. Nada foi alterado.'); return false; }
    const hash=await sha256Hex(p1);
    if(jpWealthPersistenceIsBlocked() || operationEpoch!==jpWealthPersistenceEpoch()) return false;
    S.riskPinHash=hash;
    save();
    alert('Senha definida. Esta alteração de perfil está liberada — as próximas exigirão a senha.');
    return true;
  }
  const p=prompt('Digite a senha para alterar o perfil de risco desta conta:');
  if(p===null) return false;
  const h=await sha256Hex(p);
  if(jpWealthPersistenceIsBlocked() || operationEpoch!==jpWealthPersistenceEpoch()) return false;
  if(h!==S.riskPinHash){ alert('Senha incorreta. Perfil permanece travado.'); return false; }
  return true;
}
const accountEditorsOpen=new Set();
function accountCredentialState(a){
  const missing=[!a.platform?'plataforma':null,!a.platformLogin?'login':null,!a.investorPassword?'senha do investidor':null].filter(Boolean);
  return {
    missing,
    label:missing.length?missing.length+' pendente'+(missing.length>1?'s':''):'completas',
    detail:missing.length?'Falta preencher: '+missing.join(', '):normalizePlatformName(a.platform)+' · Login '+a.platformLogin+' · senha cadastrada'
  };
}
function updateAccountCredentialMeta(row,a){
  const i=+row.dataset.idx;
  const summary=document.querySelector(`#contasBody .account-summary-row[data-idx="${i}"]`);
  const chip=summary&&summary.querySelector('.account-cred');
  const state=accountCredentialState(a);
  if(chip){
    chip.textContent=state.label;
    chip.title=state.detail;
    chip.classList.toggle('ok',!state.missing.length);
  }
}
function renderContas(){
  const cb=$('contasBody'); cb.innerHTML='';
  S.accounts.forEach((a,i)=>{
    const {lucro,corr,fw,pf,loteVs}=contaCalc(a);
    const cred=accountCredentialState(a), open=accountEditorsOpen.has(i);
    const perfilCell = a.perfilLocked
      ? `<div style="display:flex; align-items:center; gap:6px">
           <span class="hl">🔒 ${esc(a.perfil)}</span>
           <button class="unlock-btn" data-perfilkey="${i}" title="Exige senha">alterar</button>
         </div>`
      : `<select data-f="perfil">
           <option value="" ${!a.perfil?'selected':''} disabled>escolher…</option>
           ${RISK_PROFILES.map(p=>`<option value="${esc(p.name)}" ${a.perfil&&riskProfileByAny(a.perfil).key===p.key?'selected':''}>${esc(p.name)}</option>`).join('')}
         </select>`;
    const brokerAtual=brokerFor(a.broker);
    const brokerEditor=`<div class="broker-field">
        ${brokerMiniHTML(a.broker)}
        <select data-f="broker">
          ${!brokerAtual&&a.broker?`<option value="${esc(a.broker)}" selected>${esc(a.broker)} · a preencher</option>`:''}
          <option value="" ${!a.broker?'selected':''}>a preencher</option>
          ${BROKER_PARTNERS.map(b=>`<option value="${esc(b.name)}" ${brokerAtual&&brokerAtual.key===b.key?'selected':''}>${esc(b.name)}</option>`).join('')}
        </select>
      </div>`;
    const typeClass=a.tipo==='MESTRE'?'master':(a.tipo==='PRÓPRIA'?'own':'satellite');
    const summary=document.createElement('tr');
    summary.className='account-summary-row'; summary.dataset.idx=i;
    summary.innerHTML=`
      <td class="account-name-cell"><button type="button" class="account-editor-toggle" data-account-toggle="${i}" aria-expanded="${open}" aria-controls="account-detail-${i}">${esc(a.nome||'Conta sem nome')}<span aria-hidden="true">${open?'▾':'▸'}</span></button></td>
      <td><span class="account-type ${typeClass}">${esc(a.tipo)}</span></td>
      <td class="account-broker-read">${esc(brokerAtual?brokerAtual.name:(a.broker||'a preencher'))}</td>
      <td class="account-profile-read">${a.perfilLocked?'🔒 ':''}${esc(a.perfil||'a preencher')}</td>
      <td class="account-sini-read">${fmtMoney2(+a.sini||0)}</td>
      <td class="account-satu-read">${fmtMoney2(+a.satu||0)}</td>
      <td class="calc-lucro ${lucro>=0?'pos':'neg'}">${fmtPct(lucro)}</td>
      <td class="calc-lotevs hl">${loteVs.toFixed(3)}×</td>
      <td><button type="button" class="account-chip account-cred ${cred.missing.length?'':'ok'}" data-account-toggle="${i}" aria-expanded="${open}" aria-controls="account-detail-${i}" title="${esc(cred.detail)}">${esc(cred.label)}</button></td>
      <td><button class="row-del" title="Excluir conta" aria-label="Excluir ${esc(a.nome)}" data-del="${i}">✕</button></td>`;
    const detail=document.createElement('tr');
    detail.className='account-detail-row'; detail.dataset.idx=i; detail.id='account-detail-'+i; detail.hidden=!open;
    detail.innerHTML=`<td colspan="10"><div class="account-editor-grid">
      <label class="field"><span>Nome da conta</span><input data-f="nome" value="${esc(a.nome)}" placeholder="Nome da conta"></label>
      <label class="field"><span>Tipo</span><select data-f="tipo"><option ${a.tipo==='MESTRE'?'selected':''}>MESTRE</option><option ${a.tipo==='PRÓPRIA'?'selected':''}>PRÓPRIA</option><option ${a.tipo==='SATÉLITE'?'selected':''}>SATÉLITE</option></select></label>
      <div class="field"><span class="account-editor-label">Broker</span>${brokerEditor}</div>
      <div class="field"><span class="account-editor-label">Perfil</span>${perfilCell}</div>
      <label class="field"><span>Saldo inicial</span><input type="number" step="0.01" data-f="sini" value="${esc(a.sini)}"></label>
      <label class="field"><span>Saldo atual</span><input type="number" step="0.01" data-f="satu" value="${esc(a.satu)}"></label>
      <label class="field"><span>Plataforma</span><select data-f="platform">${platformOptions(a.platform)}</select></label>
      <label class="field"><span>Login da plataforma</span><input data-f="platformLogin" value="${esc(a.platformLogin)}" placeholder="Login da plataforma"></label>
      <div class="field account-password-field"><span class="account-editor-label">Senha do investidor / somente leitura</span><div class="investor-pass-row"><input type="password" data-f="investorPassword" value="${esc(a.investorPassword)}" placeholder="Válida só nesta sessão — não é armazenada" autocomplete="off"><button type="button" class="pass-toggle" data-pass-toggle="${i}" aria-pressed="false">revelar</button></div></div>
      <details class="account-calc-detail"><summary>Memória de Lote vs Mestre</summary><dl><dt>Correção</dt><dd class="calc-corr">${corr.toFixed(3)}</dd><dt>Normalização V10</dt><dd class="calc-fw">${fw.toFixed(3)}</dd><dt>Fator de Perfil</dt><dd class="calc-pf">${pf.toFixed(3)}</dd><dt>Lote vs Mestre</dt><dd>${loteVs.toFixed(3)}×</dd></dl></details>
    </div></td>`;
    cb.append(summary,detail);
  });

  cb.querySelectorAll('[data-account-toggle]').forEach(btn=>btn.addEventListener('click',()=>{
    const i=+btn.dataset.accountToggle;
    if(accountEditorsOpen.has(i)) accountEditorsOpen.delete(i); else accountEditorsOpen.add(i);
    renderContas();
    const next=document.querySelector(`#contasBody [data-account-toggle="${i}"]`); if(next) next.focus();
  }));

  // bind edits
  cb.querySelectorAll('input,select').forEach(inp=>{
    const evt = inp.tagName==='SELECT' ? 'change' : 'input';
    inp.addEventListener(evt,()=>{
      const tr=inp.closest('tr'); const i=+tr.dataset.idx; const f=inp.dataset.f;
      let val=inp.value;
      if(f==='sini'||f==='satu') val=parseFloat(val)||0;
      if(f==='perfil') val=normalizeRiskProfileName(val);
      if(f==='platform') val=normalizePlatformName(val);
      S.accounts[i][f]=val;
      if(f==='tipo'){
        inp.style.borderColor = val==='MESTRE'?'var(--violet)':(val==='SATÉLITE'?'var(--f3)':'var(--f1)');
        save(); renderContas(); return;
      }
      if(f==='perfil' && val){
        // primeira escolha trava sozinha — "só possa ser escolhido uma vez"
        S.accounts[i].perfilLocked=true;
        save(); renderContas(); return;
      }
      if(f==='broker'){
        const br=brokerFor(val);
        if(br) S.accounts[i].broker=br.name;
        save(); renderContas(); return;
      }
      if(f==='platform'){
        save(); renderContas(); return;
      }
      save();
      if(f==='nome'){
        const label=document.querySelector(`#contasBody .account-summary-row[data-idx="${i}"] .account-editor-toggle`);
        if(label && label.firstChild) label.firstChild.nodeValue=val||'Conta sem nome';
      }
      if(f==='platformLogin'||f==='investorPassword') updateAccountCredentialMeta(tr,S.accounts[i]);
      recomputeContasCalc();
    });
  });
  // revelar/ocultar senha do investidor apenas por ação explícita
  cb.querySelectorAll('[data-pass-toggle]').forEach(btn=>{
    btn.addEventListener('click',()=>{
      const row=btn.closest('tr');
      const input=row&&row.querySelector('input[data-f="investorPassword"]');
      if(!input) return;
      const show=input.type==='password';
      input.type=show?'text':'password';
      btn.textContent=show?'ocultar':'revelar';
      btn.setAttribute('aria-pressed', show?'true':'false');
    });
  });
  // bind "alterar" (exige senha) nas contas travadas
  cb.querySelectorAll('[data-perfilkey]').forEach(btn=>{
    btn.addEventListener('click', async ()=>{
      const i=+btn.dataset.perfilkey;
      const operationEpoch=jpWealthPersistenceEpoch();
      const ok = await requestPinUnlock(operationEpoch);
      if(ok && !jpWealthPersistenceIsBlocked() && operationEpoch===jpWealthPersistenceEpoch()){
        S.accounts[i].perfilLocked=false; save(); renderContas();
      }
    });
  });
  // bind delete
  cb.querySelectorAll('.row-del').forEach(btn=>{
    btn.addEventListener('click',()=>{
      const i=+btn.dataset.del;
      if(S.accounts[i].tipo==='MESTRE' && S.accounts.filter(a=>a.tipo==='MESTRE').length===1){
        alert('Mantenha ao menos uma conta MESTRE — ela é a referência de correção de lote das demais.');
        return;
      }
      if(confirm(`Excluir a conta "${S.accounts[i].nome}"?`)){
        S.accounts.splice(i,1); accountEditorsOpen.clear(); save(); renderContas();
      }
    });
  });

  renderAplicacao();
}
// recalcula só as células derivadas, sem reconstruir inputs (preserva foco/cursor)
function recomputeContasCalc(){
  document.querySelectorAll('#contasBody .account-summary-row').forEach(tr=>{
    const i=+tr.dataset.idx; const a=S.accounts[i];
    const {lucro,loteVs}=contaCalc(a);
    const lc=tr.querySelector('.calc-lucro'); lc.textContent=fmtPct(lucro); lc.className='calc-lucro '+(lucro>=0?'pos':'neg');
    tr.querySelector('.account-sini-read').textContent=fmtMoney2(+a.sini||0);
    tr.querySelector('.account-satu-read').textContent=fmtMoney2(+a.satu||0);
    tr.querySelector('.calc-lotevs').textContent=loteVs.toFixed(3)+'×';
  });
  renderAplicacao();
}
function renderAplicacao(){
  $('cLoteMaster').value=S.loteMaster;
  const ab=$('aplicBody');
  ab.innerHTML=S.accounts.map(a=>{
    const {loteVs}=contaCalc(a);
    return `<tr><td class="hl">${esc(a.nome)}</td><td>${loteVs.toFixed(3)}</td><td class="hl">${(S.loteMaster*loteVs).toFixed(3)}</td></tr>`;
  }).join('');
}

// ---- Dashboard — Acompanhamento Mensal estilo MQL5 Signals ----
// Linhas = anos, colunas = Jan..Dez (% do mês) + total composto do ano.
function renderDash(){
  const box=$('mqlMonthly'); if(!box) return;
  const MESES=['Jan','Fev','Mar','Abr','Mai','Jun','Jul','Ago','Set','Out','Nov','Dez'];
  const led=[...S.ledger].sort((a,b)=>a.data<b.data?-1:1);
  const pivot={}; // {ano:{mes: retorno}}
  let retAcum=0, ddMax=0;
  if(led.length){
    const fimDoMes={}; // último saldo de cada YYYY-MM
    led.forEach(e=>{
      fimDoMes[e.data.slice(0,7)]=e.saldo;
      ddMax=Math.max(ddMax, S.params.saldoIni>0?Math.max(0,(S.params.saldoIni-e.saldo)/S.params.saldoIni):0);
    });
    let prev=S.params.saldoIni;
    Object.keys(fimDoMes).sort().forEach(k=>{
      const [y,m]=k.split('-');
      (pivot[y]=pivot[y]||{})[+m]=prev>0?fimDoMes[k]/prev-1:0;
      prev=fimDoMes[k];
    });
    retAcum=S.params.saldoIni>0?led[led.length-1].saldo/S.params.saldoIni-1:0;
  }
  const anos=Object.keys(pivot).sort();
  const noEpBanner=noExternalProtectionActive()?`<div class="risk-note" style="margin:0 0 12px; color:var(--f4); border-color:var(--f4)">${noExternalProtectionWarning()}</div>`:'';
  if(!anos.length){
    box.innerHTML=noEpBanner+'<p class="muted" style="font-size:calc(12px * var(--fs-scale))">Sem dados ainda — registre fechamentos diários na aba 07 Contabilidade.</p>';
  } else {
    let html=`<table class="dtable" style="font-size:calc(11px * var(--fs-scale)); min-width:780px">
      <thead><tr><th>Ano</th>${MESES.map(m=>`<th style="text-align:right">${m}</th>`).join('')}<th style="text-align:right; border-left:1px solid var(--line)">Ano</th></tr></thead><tbody>`;
    anos.forEach(y=>{
      let f=1; html+=`<tr><td class="hl">${y}</td>`;
      for(let m=1;m<=12;m++){
        const r=pivot[y][m];
        if(r!=null){ f*=1+r; html+=`<td style="text-align:right"><span class="${r>0?'pos':(r<0?'neg':'muted')}">${(r*100).toFixed(2).replace('.',',')}</span></td>`; }
        else html+='<td style="text-align:right" class="muted">—</td>';
      }
      html+=`<td style="text-align:right; border-left:1px solid var(--line)"><span class="${f-1>=0?'pos':'neg'}" style="font-weight:700">${((f-1)*100).toFixed(2).replace('.',',')}%</span></td></tr>`;
    });
    html+=`</tbody></table><p style="font-size:calc(10px * var(--fs-scale)); color:var(--ink-faint); margin-top:8px">Valores em % ao mês (composto no total do ano) — mesmo formato do acompanhamento MQL5 Signals. Derivado do fechamento diário.</p>`;
    box.innerHTML=noEpBanner+html;
  }
  $('dRetAcum').textContent=led.length?(retAcum*100).toFixed(1)+'%':'—';
  $('dDDmax').textContent=led.length?(ddMax*100).toFixed(1)+'%':'—';
  $('dMar').textContent=led.length&&ddMax>0?(retAcum/ddMax).toFixed(2):'—';
  $('dMeta').textContent=(S.params.refM*100).toFixed(1)+'%';
  renderDashCharts();
}

// ---- Dashboard — Gráficos de acompanhamento (evolução patrimonial, drawdown, expectativa vs real) ----
// Reutiliza o ledger (fechamento diário) e a projeção da meta do perfil ativo. NÃO substitui a
// tabela MQL5 acima — complementa. Sem dependência externa; SVG inline; cores por var(--*) => tema claro/escuro.
// Seguro com ledger vazio: a linha de expectativa aparece sempre; a curva real só a partir do 1º fechamento.
