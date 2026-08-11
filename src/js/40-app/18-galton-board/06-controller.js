// ============ GALTON BOARD · CONTROLADOR E PERSISTÊNCIA ISOLADA (N1/N2) ============
(function initJPWGaltonController(global){
  'use strict';
  const ns=global.JPWGalton=global.JPWGalton||{};
  const STORAGE_KEY='jpwealth_galton_preferences_v1';
  const SCHEMA_VERSION=1;
  const SPEEDS=[.5,1,2,4];
  const PREFERENCE_FIELDS=['preset','showTheory','speed','releasePoint','tiltDegrees','seed','config'];
  const PERSISTED_CONFIG_FIELDS=['rows','pegSpacing','rowSpacing','pegRadius','ballRadius','ballDensity','ballRestitution','ballFriction','gravity','releaseJitter','pegTolerance','ballCollisions'];
  const DEFAULT_PREFERENCES={schemaVersion:SCHEMA_VERSION,preset:'realistic',showTheory:true,speed:1,releasePoint:0,tiltDegrees:0,seed:18473,config:{}};

  function finite(value,fallback){ return Number.isFinite(Number(value))?Number(value):fallback; }
  function clamp(value,min,max){ return Math.min(max,Math.max(min,finite(value,min))); }
  function clone(value){ return JSON.parse(JSON.stringify(value)); }
  function configDefaults(){ return clone(ns.config&&ns.config.DEFAULTS?ns.config.DEFAULTS:{}); }
  function normalizedConfig(value){
    const candidate={...configDefaults(),...(value&&typeof value==='object'?value:{})};
    if(!ns.config||typeof ns.config.validate!=='function') return candidate;
    const result=ns.config.validate(candidate);
    return result&&result.value?result.value:(result&&result.config?result.config:result);
  }
  function presetConfig(name,current){
    if(ns.config&&typeof ns.config.applyPreset==='function'){
      const result=ns.config.applyPreset(name);
      return normalizedConfig(result&&result.config?result.config:result);
    }
    const preset=ns.config&&ns.config.PRESETS&&ns.config.PRESETS[name];
    return normalizedConfig({...current,...(preset||{})});
  }
  function normalizePreferences(raw){
    const source=raw&&typeof raw==='object'&&!Array.isArray(raw)?raw:{};
    const preferredPreset=['realistic','idealized','high-dissipation','low-dissipation','custom'].includes(source.preset)?source.preset:DEFAULT_PREFERENCES.preset;
    const speed=SPEEDS.includes(Number(source.speed))?Number(source.speed):DEFAULT_PREFERENCES.speed;
    const seed=ns.rng&&typeof ns.rng.normalizeSeed==='function'?ns.rng.normalizeSeed(source.seed):Math.max(1,Math.floor(finite(source.seed,DEFAULT_PREFERENCES.seed)));
    const value={
      schemaVersion:SCHEMA_VERSION,
      preset:preferredPreset,
      showTheory:source.showTheory!==false,
      speed,
      releasePoint:clamp(source.releasePoint,-1,1),
      tiltDegrees:clamp(source.tiltDegrees,-3,3),
      seed,
      config:normalizedConfig(source.config)
    };
    const extensions={};
    Object.keys(source).filter(key=>!['schemaVersion',...PREFERENCE_FIELDS].includes(key)).forEach(key=>{ extensions[key]=clone(source[key]); });
    const configExtensions={};
    const knownConfig=new Set(Object.keys(configDefaults()));
    if(source.config&&typeof source.config==='object') Object.keys(source.config).filter(key=>!knownConfig.has(key)).forEach(key=>{ configExtensions[key]=clone(source.config[key]); });
    return {value,extensions,configExtensions};
  }
  function readPreferences(storage){
    let raw=null;
    try{
      const target=storage===undefined?global.localStorage:storage;
      raw=target.getItem(STORAGE_KEY);
      if(raw===null) return {...normalizePreferences(DEFAULT_PREFERENCES),ok:true,blocked:false,error:null,raw:null};
      const parsed=JSON.parse(raw);
      const validEnvelope=parsed&&typeof parsed==='object'&&!Array.isArray(parsed)&&Number.isInteger(parsed.schemaVersion)&&parsed.schemaVersion===SCHEMA_VERSION;
      if(!validEnvelope) return {...normalizePreferences(parsed),ok:false,blocked:true,error:new Error('Envelope de preferências incompatível com este aplicativo.'),raw};
      return {...normalizePreferences(parsed),ok:true,blocked:false,error:null,raw};
    }catch(error){ return {...normalizePreferences(DEFAULT_PREFERENCES),ok:false,blocked:true,error,raw}; }
  }
  function writePreferences(value,storage,extensions={},configExtensions={}){
    const normalized=normalizePreferences(value).value;
    const safeConfig={}; PERSISTED_CONFIG_FIELDS.forEach(key=>{ safeConfig[key]=normalized.config[key]; });
    const payload={...clone(extensions),...normalized,config:{...clone(configExtensions),...safeConfig}};
    try{
      const target=storage===undefined?global.localStorage:storage;
      target.setItem(STORAGE_KEY,JSON.stringify(payload));
      return {ok:target.getItem(STORAGE_KEY)!==null,value:normalized,error:null};
    }catch(error){ return {ok:false,value:normalized,error}; }
  }

  function panelHTML(){
    return `<div class="galton-board" id="galtonBoardRoot" data-galton-root>
      <p class="galton-kicker">Probabilidade em movimento</p>
      <p class="settings-lead">Experimento interativo de probabilidade com corpos rígidos reais. Observe como trajetórias individuais imprevisíveis formam padrões agregados.</p>
      <p class="galton-disclaimer">O Galton Board demonstra princípios de probabilidade, agregação e distribuição. Ele não representa diretamente a distribuição dos retornos do mercado Forex.</p>
      <div class="galton-metrics" aria-label="Estatísticas da simulação">
        <div><span>Amostra <button type="button" class="galton-info" title="Número de bolas já contabilizadas nos compartimentos." aria-label="Amostra: número de bolas já contabilizadas nos compartimentos">i</button></span><strong data-galton-metric="n">0</strong></div>
        <div><span>Média <button type="button" class="galton-info" title="Posição média ponderada dos compartimentos observados." aria-label="Média: posição média ponderada dos compartimentos observados">i</button></span><strong data-galton-metric="mean">—</strong></div>
        <div><span>Desvio padrão <button type="button" class="galton-info" title="Grau de dispersão das observações em torno da média." aria-label="Desvio padrão: grau de dispersão das observações em torno da média">i</button></span><strong data-galton-metric="stdDev">—</strong></div>
        <div><span>Moda</span><strong data-galton-metric="mode">—</strong></div>
        <div><span>Assimetria <button type="button" class="galton-info" title="Indica o deslocamento da distribuição para um dos lados." aria-label="Assimetria: indica o deslocamento da distribuição para um dos lados">i</button></span><strong data-galton-metric="skewness">—</strong></div>
        <div><span>Curtose</span><strong data-galton-metric="kurtosis">—</strong></div>
      </div>
      <div class="galton-stage">
        <canvas data-galton-canvas role="img" aria-label="Galton Board vazio" aria-describedby="galtonCanvasDescription"></canvas>
        <div class="galton-bin-tooltip" data-galton-tooltip hidden></div>
      </div>
      <p id="galtonCanvasDescription" class="sr-only" data-galton-canvas-description>Tabuleiro vazio, sem bolas contabilizadas.</p>
      <div class="galton-status-row"><p data-galton-convergence role="status" aria-live="polite">Tabuleiro vazio. Adicione bolas à fila para iniciar.</p><span data-galton-live class="sr-only" aria-live="polite"></span></div>
      <p class="galton-storage-status is-error" data-galton-integrity role="status" aria-live="polite" hidden></p>
      <section class="galton-controls" aria-label="Controles do experimento">
        <div class="galton-control-group"><span class="galton-control-label">Adicionar à fila</span><div class="galton-button-row">
          <button type="button" data-galton-add="1">+1</button><button type="button" data-galton-add="10">+10</button><button type="button" data-galton-add="100">+100</button><button type="button" data-galton-add="500">+500</button>
          <button type="button" class="galton-primary" data-galton-action="execute">Executar <span data-galton-staged>0</span></button>
        </div></div>
        <div class="galton-button-row"><button type="button" data-galton-action="pause" aria-pressed="false">Pausar</button><button type="button" data-galton-action="reset">Resetar</button><button type="button" data-galton-action="center">Centralizar</button><button type="button" data-galton-action="restore-defaults">Restaurar padrões</button><button type="button" data-galton-action="new-seed">Nova seed</button><span class="galton-seed">Seed <output data-galton-seed>18473</output></span></div>
        <div class="galton-control-grid">
          <fieldset class="galton-speed"><legend>Velocidade</legend><div class="galton-segmented">${SPEEDS.map(speed=>`<button type="button" data-galton-speed="${speed}" aria-pressed="${speed===1?'true':'false'}">${speed}x</button>`).join('')}</div></fieldset>
          <label>Ponto de lançamento <output data-galton-output="releasePoint">centro</output><input type="range" min="-1" max="1" step="0.05" value="0" data-galton-pref="releasePoint" aria-label="Ponto de lançamento"></label>
          <label>Inclinação <output data-galton-output="tiltDegrees">0.0°</output><input type="range" min="-3" max="3" step="0.1" value="0" data-galton-pref="tiltDegrees" aria-label="Inclinação do tabuleiro"></label>
          <label>Preset <select data-galton-pref="preset"><option value="realistic">Realista</option><option value="idealized">Idealizado</option><option value="high-dissipation">Alta dissipação</option><option value="low-dissipation">Baixa dissipação</option><option value="custom">Personalizado</option></select></label>
          <label class="galton-check"><input type="checkbox" data-galton-pref="showTheory" checked> Mostrar teoria binomial quando elegível</label>
        </div>
        <p class="galton-theory-status"><button type="button" class="galton-info" title="Compara percentuais observados com Binomial(n, 0,5), sem ajustar a física." aria-label="Distribuição teórica: comparação binomial sem ajuste da física">i</button> <span data-galton-theory-status></span></p>
      </section>
      <details class="galton-details" data-galton-advanced><summary>Parâmetros físicos</summary>
        <p>Alterar um parâmetro reinicia o tabuleiro e mantém apenas as preferências.</p>
        <div class="galton-parameter-grid">
          <label>Linhas <input type="number" min="6" max="16" step="1" data-galton-config="rows"></label>
          <label>Espaçamento horizontal <input type="number" min="0.65" max="1.4" step="0.05" data-galton-config="pegSpacing"></label>
          <label>Espaçamento vertical <input type="number" min="0.55" max="1.2" step="0.05" data-galton-config="rowSpacing"></label>
          <label>Raio do pino <input type="number" min="0.05" max="0.16" step="0.01" data-galton-config="pegRadius"></label>
          <label>Raio da bola <input type="number" min="0.08" max="0.25" step="0.01" data-galton-config="ballRadius"></label>
          <label>Densidade da bola <input type="number" min="0.2" max="3" step="0.1" data-galton-config="ballDensity"></label>
          <label>Restituição <input type="number" min="0" max="0.9" step="0.05" data-galton-config="ballRestitution"></label>
          <label>Atrito <input type="number" min="0" max="1" step="0.05" data-galton-config="ballFriction"></label>
          <label>Gravidade <input type="number" min="2" max="20" step="0.5" data-galton-config="gravity"></label>
          <label>Jitter de soltura <input type="number" min="0" max="0.4" step="0.01" data-galton-config="releaseJitter"></label>
          <label>Tolerância dos pinos <input type="number" min="0" max="0.04" step="0.005" data-galton-config="pegTolerance"></label>
          <label class="galton-check"><input type="checkbox" data-galton-config="ballCollisions"> Colisão bola-bola</label>
        </div>
        <p><button type="button" class="reset-btn" data-galton-action="restore-physics">Restaurar valores físicos padrão</button></p>
      </details>
      <details class="galton-details"><summary>O que observar</summary><ol><li>Uma única bola é difícil de prever.</li><li>Muitas observações revelam padrões agregados.</li><li>Pequenas assimetrias podem deslocar toda a distribuição.</li><li>Amostras pequenas apresentam maior ruído estatístico.</li><li>Regularidade estatística não significa previsibilidade individual.</li></ol><p>Esta experiência ilustra princípios gerais de probabilidade e não constitui um modelo dos retornos do Forex.</p></details>
      <details class="galton-details"><summary>Detalhes acessíveis dos compartimentos</summary><div class="galton-table-wrap"><table><caption>Distribuição empírica e referência teórica por compartimento</caption><thead><tr><th scope="col">Bin</th><th scope="col">Quantidade</th><th scope="col">Percentual</th><th scope="col">Teoria esperada</th><th scope="col">Diferença</th></tr></thead><tbody data-galton-bins></tbody></table></div></details>
      <p class="galton-storage-status" data-galton-storage role="status"></p>
    </div>`;
  }

  function describeHistogram(histogram){
    if(ns.statistics&&typeof ns.statistics.describeHistogram==='function') return ns.statistics.describeHistogram(histogram);
    const total=histogram.reduce((sum,value)=>sum+finite(value,0),0);
    if(!total) return {n:0,mean:null,stdDev:null,mode:null,skewness:null,kurtosis:null};
    const mean=histogram.reduce((sum,value,index)=>sum+index*value,0)/total;
    const moments=[2,3,4].map(power=>histogram.reduce((sum,value,index)=>sum+value*Math.pow(index-mean,power),0)/total);
    const stdDev=Math.sqrt(moments[0]);
    const max=Math.max(...histogram), modes=histogram.map((v,i)=>v===max?i:null).filter(v=>v!==null);
    return {n:total,mean,stdDev,mode:modes.join(', '),skewness:stdDev?moments[1]/Math.pow(stdDev,3):0,kurtosis:stdDev?moments[2]/Math.pow(stdDev,4)-3:0};
  }

  class GaltonController{
    constructor(root){
      this.root=root; this.canvas=root.querySelector('[data-galton-canvas]'); this.renderer=new ns.renderer.CanvasRenderer(this.canvas);
      const loaded=readPreferences();
      this.preferences=loaded.value; this.extensions=loaded.extensions; this.configExtensions=loaded.configExtensions;
      this.storageReadError=loaded.error; this.persistenceBlocked=loaded.blocked===true; this.preservedPreferenceRaw=loaded.raw; this.engine=null; this.active=false; this.destroyed=false; this.raf=0; this.lastAt=0; this.lastDomAt=0; this.lastDrawAt=0; this.lastPhysicsMs=0; this.staged=0; this.manualPaused=true; this.resumeAfterLifecycle=false; this.lastHistogramKey='';
      this.sessionWipeEpoch=finite(global.JP_WEALTH_SESSION_WIPE_EPOCH,0);
      this.debug=/^(localhost|127\.0\.0\.1)$/.test(location.hostname)&&new URLSearchParams(location.search).get('galtonDebug')==='1';
      this.reducedMotion=Boolean(global.matchMedia&&global.matchMedia('(prefers-reduced-motion: reduce)').matches);
      this.abortController=new AbortController();
      this.resizeObserver=typeof ResizeObserver==='function'?new ResizeObserver(()=>{ this.renderer.resize(); this.redraw(); }):null;
      this.resizeObserverActive=false;
      if(this.resizeObserver){ this.resizeObserver.observe(this.canvas); this.resizeObserverActive=true; }
      this.bind(); this.syncControls(); this.createEngine(); this.render(true);
      if(this.storageReadError) this.showStorageStatus('Preferências salvas incompatíveis, ilegíveis ou indisponíveis foram preservadas sem sobrescrita. O laboratório usa valores seguros apenas em memória; use Restaurar padrões para substituí-las explicitamente.',true);
      if(this.debug){ global.__galtonDebug=global.__galtonDebug||{mounts:0,destroys:0,activeRaf:0,resizeObservers:0}; global.__galtonDebug.mounts++; if(this.resizeObserverActive) global.__galtonDebug.resizeObservers++; }
    }
    bind(){
      const signal=this.abortController.signal;
      this.root.addEventListener('click',event=>this.onClick(event),{signal});
      this.root.addEventListener('input',event=>this.onInput(event),{signal});
      this.root.addEventListener('change',event=>this.onChange(event),{signal});
      this.canvas.addEventListener('pointermove',event=>this.showBinTooltip(event),{signal});
      this.canvas.addEventListener('pointerleave',()=>this.hideBinTooltip(),{signal});
      this.canvas.addEventListener('click',event=>this.onCanvasClick(event),{signal});
      document.addEventListener('visibilitychange',()=>this.onVisibility(),{signal});
    }
    engineOptions(){
      return {config:{...this.preferences.config,releasePoint:this.preferences.releasePoint,tiltDegrees:this.preferences.tiltDegrees,speed:this.preferences.speed},seed:this.preferences.seed,debug:this.debug};
    }
    createEngine(){
      if(this.engine) this.engine.destroy();
      if(!ns.physics||typeof ns.physics.createEngine!=='function') throw new Error('Motor físico do Galton Board indisponível.');
      this.engine=ns.physics.createEngine(this.engineOptions());
      this.manualPaused=true; this.lastAt=0; this.lastHistogramKey='';
    }
    activate(){
      if(this.destroyed) return;
      this.active=true;
      if(this.resizeObserver&&!this.resizeObserverActive){ this.resizeObserver.observe(this.canvas); this.resizeObserverActive=true; if(this.debug&&global.__galtonDebug) global.__galtonDebug.resizeObservers++; }
      this.renderer.resize(); this.render(true);
      if(this.resumeAfterLifecycle&&!this.manualPaused){ this.engine.resume(); this.ensureFrame(); }
    }
    deactivate(options={}){
      if(this.destroyed) return;
      const snap=this.snapshot(); this.resumeAfterLifecycle=Boolean(snap.running&&!this.manualPaused);
      this.active=false; this.cancelFrame(); if(this.engine) this.engine.pause();
      if(this.resizeObserver&&this.resizeObserverActive){ this.resizeObserver.disconnect(); this.resizeObserverActive=false; if(this.debug&&global.__galtonDebug) global.__galtonDebug.resizeObservers=Math.max(0,global.__galtonDebug.resizeObservers-1); }
      if(options.destroy) this.destroy();
    }
    destroy(){
      if(this.destroyed) return;
      this.destroyed=true; this.active=false; this.cancelFrame(); this.abortController.abort();
      if(this.resizeObserver){ this.resizeObserver.disconnect(); if(this.resizeObserverActive&&this.debug&&global.__galtonDebug) global.__galtonDebug.resizeObservers=Math.max(0,global.__galtonDebug.resizeObservers-1); this.resizeObserverActive=false; }
      if(this.engine) this.engine.destroy(); this.engine=null; this.renderer.destroy();
      this.root.removeAttribute('data-galton-mounted'); this.root.__galtonController=null;
      if(this.debug&&global.__galtonDebug) global.__galtonDebug.destroys++;
    }
    snapshot(){
      const snapshot=this.engine?this.engine.snapshot():{};
      snapshot.showTheory=this.preferences.showTheory;
      const theoryInput={...this.preferences.config,releasePoint:this.preferences.releasePoint,tiltDegrees:this.preferences.tiltDegrees};
      const theoryResult=ns.config&&typeof ns.config.theoryEligibility==='function'?ns.config.theoryEligibility(theoryInput):{eligible:Math.abs(this.preferences.releasePoint)<1e-9&&Math.abs(this.preferences.tiltDegrees)<1e-9,reasons:[]};
      snapshot.theoryEligible=Boolean(theoryResult.eligible);
      snapshot.theoryReasons=Array.isArray(theoryResult.reasons)?theoryResult.reasons.slice():[];
      snapshot.debug=this.debug;
      snapshot.physicsMs=this.lastPhysicsMs;
      return snapshot;
    }
    onClick(event){
      const add=event.target.closest('[data-galton-add]');
      if(add){ this.staged=Math.min(10000,this.staged+Number(add.dataset.galtonAdd)); this.updateStaged(); return; }
      const speed=event.target.closest('[data-galton-speed]');
      if(speed){ this.preferences.speed=Number(speed.dataset.galtonSpeed); this.engine.setSpeed(this.preferences.speed); this.persist(); this.syncSpeed(); this.ensureFrame(); return; }
      const action=event.target.closest('[data-galton-action]'); if(!action) return;
      if(action.dataset.galtonAction==='execute') this.execute();
      if(action.dataset.galtonAction==='pause') this.togglePause();
      if(action.dataset.galtonAction==='reset') this.reset();
      if(action.dataset.galtonAction==='center') this.center();
      if(action.dataset.galtonAction==='restore-defaults') this.restoreDefaults();
      if(action.dataset.galtonAction==='restore-physics') this.restorePhysics();
      if(action.dataset.galtonAction==='new-seed') this.newSeed();
    }
    onInput(event){
      const pref=event.target.dataset.galtonPref;
      if(pref==='releasePoint'){
        this.preferences.releasePoint=clamp(event.target.value,-1,1); this.updateOutputs(); this.reset({announce:false});
      }else if(pref==='tiltDegrees'){
        this.preferences.tiltDegrees=clamp(event.target.value,-3,3); this.updateOutputs(); this.reset({announce:false});
      }
    }
    onChange(event){
      const pref=event.target.dataset.galtonPref;
      if(pref==='preset'){
        this.preferences.preset=event.target.value; if(event.target.value!=='custom') this.preferences.config=presetConfig(event.target.value,this.preferences.config);
        this.syncConfigControls(); this.persist(); this.reset({announce:'Preset aplicado; tabuleiro reiniciado.'}); return;
      }
      if(pref==='showTheory'){ this.preferences.showTheory=event.target.checked; this.persist(); this.render(true); return; }
      if(pref==='releasePoint'||pref==='tiltDegrees'){
        this.persist(); this.reset({announce:`${pref==='releasePoint'?'Ponto de lançamento':'Inclinação'} atualizado; tabuleiro reiniciado para não misturar regimes físicos.`}); return;
      }
      const key=event.target.dataset.galtonConfig;
      if(key){
        const value=event.target.type==='checkbox'?event.target.checked:finite(event.target.value,this.preferences.config[key]);
        this.preferences.config=normalizedConfig({...this.preferences.config,[key]:value}); this.preferences.preset='custom'; this.syncControls(); this.persist(); this.reset({announce:'Parâmetro físico atualizado; tabuleiro reiniciado.'});
      }
    }
    execute(){
      if(this.staged<=0) this.staged=1;
      const requested=this.staged,accepted=this.engine.enqueue(requested); this.staged=0; this.updateStaged();
      if(accepted<=0){ this.announce('A fila atingiu o limite seguro; nenhuma bola foi adicionada.'); this.render(true); return; }
      this.manualPaused=false; if(typeof this.engine.start==='function') this.engine.start(); else this.engine.resume();
      this.announce(`${accepted} ${accepted===1?'bola adicionada':'bolas adicionadas'} ao experimento${accepted<requested?`; ${requested-accepted} excederam o limite da fila`:''}.`); this.updatePause(); this.ensureFrame();
    }
    onCanvasClick(event){
      const rect=this.canvas.getBoundingClientRect();
      if(event.clientY-rect.top>Math.min(96,rect.height*.22)) return;
      const accepted=this.engine.enqueue(1); if(!accepted){ this.announce('A fila atingiu o limite seguro; a bola não foi adicionada.'); return; }
      this.manualPaused=false; this.engine.start(); this.updatePause(); this.announce('Uma bola liberada pelo emissor superior.'); this.ensureFrame();
    }
    togglePause(){
      const snap=this.snapshot();
      if(snap.running&&!this.manualPaused){ this.manualPaused=true; this.engine.pause(); this.cancelFrame(); this.announce('Simulação pausada.'); }
      else{ this.manualPaused=false; this.engine.resume(); this.announce('Simulação retomada.'); this.ensureFrame(); }
      this.updatePause(); this.render(true);
    }
    reset(options={}){
      this.cancelFrame(); this.staged=0; this.updateStaged(); this.createEngine(); this.render(true); if(options.announce!==false) this.announce(options.announce||'Tabuleiro reiniciado e resultados removidos.');
    }
    newSeed(){
      this.preferences.seed=ns.rng&&typeof ns.rng.newSeed==='function'?ns.rng.newSeed():((Date.now()>>>0)||1);
      this.persist(); this.syncControls(); this.reset({announce:`Nova seed ${this.preferences.seed}; tabuleiro reiniciado.`});
    }
    center(){
      this.preferences.releasePoint=0; this.preferences.tiltDegrees=0; this.syncControls(); this.persist(); this.reset({announce:'Ponto de lançamento e inclinação centralizados; tabuleiro reiniciado.'});
    }
    restorePhysics(){
      this.preferences.config=normalizedConfig(configDefaults()); this.preferences.preset='realistic'; this.syncControls(); this.persist(); this.reset({announce:'Valores físicos padrão restaurados; tabuleiro reiniciado.'});
    }
    restoreDefaults(){
      this.preferences=normalizePreferences(DEFAULT_PREFERENCES).value; this.persistenceBlocked=false; this.preservedPreferenceRaw=null; this.storageReadError=null; this.extensions={}; this.configExtensions={}; this.syncControls(); this.persist(); this.reset({announce:'Preferências e valores físicos padrão restaurados; tabuleiro reiniciado.'});
    }
    persist(){
      if(finite(global.JP_WEALTH_SESSION_WIPE_EPOCH,0)!==this.sessionWipeEpoch){
        this.showStorageStatus('Sessão encerrada: esta instância não pode recriar preferências locais antigas.',true);
        return false;
      }
      if(this.persistenceBlocked){
        this.showStorageStatus('Gravação bloqueada para preservar as preferências existentes. Use Restaurar padrões para autorizar sua substituição explícita.',true);
        return false;
      }
      const result=writePreferences(this.preferences,undefined,this.extensions,this.configExtensions);
      this.preferences=result.value;
      this.showStorageStatus(result.ok?'Preferências do laboratório salvas neste navegador.':'Não foi possível salvar as preferências. A simulação continua em memória; nenhum dado financeiro foi alterado.',!result.ok);
      return result.ok;
    }
    showStorageStatus(message,isError=false){
      const el=this.root.querySelector('[data-galton-storage]'); if(!el) return; el.textContent=message; el.classList.toggle('is-error',isError);
    }
    ensureFrame(){
      if(!this.active||this.destroyed||document.hidden||this.raf) return;
      this.raf=requestAnimationFrame(time=>this.frame(time)); if(this.debug&&global.__galtonDebug) global.__galtonDebug.activeRaf=1;
    }
    cancelFrame(){ if(this.raf) cancelAnimationFrame(this.raf); this.raf=0; this.lastAt=0; if(this.debug&&global.__galtonDebug) global.__galtonDebug.activeRaf=0; }
    frame(time){
      this.raf=0; if(!this.active||this.destroyed||document.hidden) return;
      const elapsed=this.lastAt?Math.min(.25,Math.max(0,(time-this.lastAt)/1000)):0; this.lastAt=time;
      if(elapsed&&!this.manualPaused){ const physicsAt=performance.now(); this.engine.step(elapsed); this.lastPhysicsMs=performance.now()-physicsAt; }
      let snapshot=this.snapshot(),becameIdle=false;
      if(snapshot.idle&&snapshot.running&&typeof this.engine.stop==='function'){ this.engine.stop(); snapshot=this.snapshot(); becameIdle=true; }
      const drawInterval=this.reducedMotion?250:0;
      if(becameIdle||!drawInterval||!this.lastDrawAt||time-this.lastDrawAt>=drawInterval){ this.renderer.draw(snapshot); this.lastDrawAt=time; }
      if(becameIdle||!this.lastDomAt||time-this.lastDomAt>=(this.reducedMotion?250:125)){ this.renderDOM(snapshot,becameIdle); this.lastDomAt=time; }
      if(!this.manualPaused&&(snapshot.running||snapshot.activeCount>0||snapshot.queuedCount>0)) this.ensureFrame(); else this.cancelFrame();
    }
    redraw(){ if(!this.destroyed) this.renderer.draw(this.snapshot()); }
    render(force=false){ const snapshot=this.snapshot(); this.renderer.draw(snapshot); if(force) this.renderDOM(snapshot,true); }
    renderDOM(snapshot,force=false){
      const histogram=Array.isArray(snapshot.histogram)?snapshot.histogram:[];
      const stats=describeHistogram(histogram), fmt=value=>Number.isFinite(value)?Number(value).toFixed(2):'—';
      const values={n:stats.n||snapshot.settledCount||0,mean:fmt(stats.mean),stdDev:fmt(stats.stdDev),mode:stats.mode===null||stats.mode===undefined?'—':String(stats.mode),skewness:fmt(stats.skewness),kurtosis:fmt(stats.kurtosis)};
      Object.entries(values).forEach(([key,value])=>{ const el=this.root.querySelector(`[data-galton-metric="${key}"]`); if(el) el.textContent=value; });
      const n=Number(values.n)||0, convergence=this.root.querySelector('[data-galton-convergence]');
      if(convergence){
        const message=n===0?'Tabuleiro vazio. Adicione bolas à fila para iniciar.':n<100?'Amostra pequena: flutuações individuais ainda exercem grande influência.':n<500?'Com mais de 100 observações, padrões agregados começam a ficar mais legíveis.':n<1000?'Com mais de 500 observações, flutuações individuais tendem a exercer menor influência sobre a distribuição agregada.':'Com mais de 1.000 observações, a distribuição empírica tende a ficar mais estável; isso não prevê a próxima bola nem exige normalidade.';
        if(convergence.textContent!==message) convergence.textContent=message;
      }
      const summary=`${n} bolas contabilizadas em ${histogram.length||finite(snapshot.config&&snapshot.config.rows,10)+1} compartimentos; ${snapshot.activeCount||0} corpos ativos; ${snapshot.queuedCount||0} na fila.`;
      this.canvas.setAttribute('aria-label',`Galton Board: ${summary}`); const desc=this.root.querySelector('[data-galton-canvas-description]'); if(desc) desc.textContent=summary;
      const integrity=this.root.querySelector('[data-galton-integrity]');
      if(integrity){
        const expired=Math.max(0,Math.floor(finite(snapshot.expiredCount,0))), reasons=snapshot.expiredByReason||{}, outside=Math.max(0,Math.floor(finite(reasons.outside,0))), maxAge=Math.max(0,Math.floor(finite(reasons.maxAge,0)));
        const hidden=expired===0, message=expired?`Integridade da amostra: ${expired} ${expired===1?'bola não chegou':'bolas não chegaram'} a um compartimento e ${expired===1?'foi removida':'foram removidas'} pelo limite de segurança (${maxAge} por tempo; ${outside} fora do tabuleiro). ${expired===1?'Ela não entra':'Elas não entram'} no histograma.`:'';
        if(integrity.hidden!==hidden) integrity.hidden=hidden;
        if(integrity.textContent!==message) integrity.textContent=message;
      }
      const theoryStatus=this.root.querySelector('[data-galton-theory-status]');
      if(theoryStatus){
        const reasonLabels={'release-not-centered':'ponto de lançamento fora do centro','gravity-not-vertical':'inclinação diferente de zero','peg-tolerance-breaks-symmetry':'tolerância dos pinos quebra a simetria','ball-interactions-break-independence':'colisão bola-bola quebra a independência'};
        theoryStatus.textContent=!this.preferences.showTheory?'Curva teórica desativada.':snapshot.theoryEligible?'Curva azul: referência binomial p = 0,5 no mesmo N e eixo do histograma.':`Curva teórica ocultada: ${snapshot.theoryReasons.map(reason=>reasonLabels[reason]||reason).join('; ')}.`;
      }
      const key=`${histogram.join(',')}|${snapshot.showTheory}|${snapshot.theoryEligible}`; if(force||key!==this.lastHistogramKey){ this.renderBinTable(histogram,n,snapshot); this.lastHistogramKey=key; }
      this.updatePause(snapshot);
    }
    renderBinTable(histogram,total,snapshot){
      const tbody=this.root.querySelector('[data-galton-bins]'); if(!tbody) return;
      const count=histogram.length||Math.max(2,Math.round(finite(this.preferences.config.rows,10))+1);
      const probabilities=snapshot.showTheory&&snapshot.theoryEligible&&ns.statistics?ns.statistics.binomialDistribution(count-1):null;
      const fragment=document.createDocumentFragment();
      for(let i=0;i<count;i++){
        const value=finite(histogram[i],0), percent=total?value/total*100:0, theoryPercent=probabilities?probabilities[i]*100:null, expected=theoryPercent!==null&&total?`${(probabilities[i]*total).toFixed(1)} (${theoryPercent.toFixed(1)}%)`:'—', delta=theoryPercent!==null&&total?`${percent-theoryPercent>=0?'+':''}${(percent-theoryPercent).toFixed(1)} p.p.`:'—', row=document.createElement('tr');
        row.tabIndex=0; row.dataset.galtonBin=String(i); row.innerHTML=`<th scope="row">${i}</th><td>${value}</td><td>${percent.toFixed(1)}%</td><td>${expected}</td><td>${delta}</td>`; fragment.append(row);
      }
      tbody.replaceChildren(fragment);
    }
    syncControls(){
      const p=this.preferences;
      const set=(selector,value)=>{ const el=this.root.querySelector(selector); if(el){ if(el.type==='checkbox') el.checked=Boolean(value); else el.value=String(value); } };
      set('[data-galton-pref="preset"]',p.preset); set('[data-galton-pref="showTheory"]',p.showTheory); set('[data-galton-pref="releasePoint"]',p.releasePoint); set('[data-galton-pref="tiltDegrees"]',p.tiltDegrees);
      this.syncConfigControls(); this.syncSpeed(); this.updateOutputs(); const seed=this.root.querySelector('[data-galton-seed]'); if(seed) seed.textContent=String(p.seed);
    }
    syncConfigControls(){
      this.root.querySelectorAll('[data-galton-config]').forEach(input=>{ const value=this.preferences.config[input.dataset.galtonConfig]; if(input.type==='checkbox') input.checked=Boolean(value); else if(value!==undefined) input.value=String(value); });
    }
    syncSpeed(){ this.root.querySelectorAll('[data-galton-speed]').forEach(button=>button.setAttribute('aria-pressed',Number(button.dataset.galtonSpeed)===this.preferences.speed?'true':'false')); }
    updateOutputs(){
      const release=this.root.querySelector('[data-galton-output="releasePoint"]'); if(release) release.textContent=Math.abs(this.preferences.releasePoint)<.001?'centro':`${this.preferences.releasePoint>0?'+':''}${this.preferences.releasePoint.toFixed(2)}`;
      const tilt=this.root.querySelector('[data-galton-output="tiltDegrees"]'); if(tilt) tilt.textContent=`${this.preferences.tiltDegrees>0?'+':''}${this.preferences.tiltDegrees.toFixed(1)}°`;
    }
    updateStaged(){ const el=this.root.querySelector('[data-galton-staged]'); if(el) el.textContent=String(this.staged); }
    updatePause(snapshot=this.snapshot()){
      const button=this.root.querySelector('[data-galton-action="pause"]'); if(!button) return;
      const paused=this.manualPaused||!snapshot.running; button.textContent=paused?'Continuar':'Pausar'; button.setAttribute('aria-pressed',paused?'true':'false');
    }
    announce(message){ const el=this.root.querySelector('[data-galton-live]'); if(el){ el.textContent=''; requestAnimationFrame(()=>{ el.textContent=message; }); } }
    showBinTooltip(event){
      const index=this.renderer.binAtClientPoint(event.clientX,event.clientY), tooltip=this.root.querySelector('[data-galton-tooltip]'); if(!tooltip||index<0){ this.hideBinTooltip(); return; }
      const snapshot=this.snapshot(),histogram=snapshot.histogram||[], value=finite(histogram[index],0), total=histogram.reduce((a,b)=>a+finite(b,0),0), empirical=total?value/total*100:0, probabilities=snapshot.showTheory&&snapshot.theoryEligible&&ns.statistics?ns.statistics.binomialDistribution(histogram.length-1):null, theory=probabilities?probabilities[index]*100:null, stage=this.root.querySelector('.galton-stage'), rect=stage.getBoundingClientRect(), theoryText=theory===null?'—':`${theory.toFixed(1)}%`, deltaText=theory===null?'—':`${empirical-theory>=0?'+':''}${(empirical-theory).toFixed(1)} p.p.`;
      tooltip.textContent=`Bin ${index} · Observações ${value} · Empírico ${empirical.toFixed(1)}% · Teórico ${theoryText} · Δ ${deltaText}`;
      tooltip.hidden=false; tooltip.style.maxWidth=`${Math.max(0,rect.width-12)}px`; tooltip.style.whiteSpace='normal'; tooltip.style.left='0px'; tooltip.style.top='0px';
      const tooltipRect=tooltip.getBoundingClientRect(), inset=6, desiredLeft=event.clientX-rect.left+10, desiredTop=event.clientY-rect.top-32;
      tooltip.style.left=`${clamp(desiredLeft,inset,Math.max(inset,rect.width-tooltipRect.width-inset))}px`;
      tooltip.style.top=`${clamp(desiredTop,inset,Math.max(inset,rect.height-tooltipRect.height-inset))}px`;
    }
    hideBinTooltip(){ const tooltip=this.root.querySelector('[data-galton-tooltip]'); if(tooltip) tooltip.hidden=true; }
    onVisibility(){
      if(document.hidden){ const snap=this.snapshot(); this.resumeAfterLifecycle=Boolean(snap.running&&!this.manualPaused); if(this.engine) this.engine.pause(); this.cancelFrame(); if(this.resizeObserver&&this.resizeObserverActive){ this.resizeObserver.disconnect(); this.resizeObserverActive=false; if(this.debug&&global.__galtonDebug) global.__galtonDebug.resizeObservers=Math.max(0,global.__galtonDebug.resizeObservers-1); } }
      else if(this.active){ if(this.resizeObserver&&!this.resizeObserverActive){ this.resizeObserver.observe(this.canvas); this.resizeObserverActive=true; if(this.debug&&global.__galtonDebug) global.__galtonDebug.resizeObservers++; } if(this.resumeAfterLifecycle&&!this.manualPaused){ this.engine.resume(); this.ensureFrame(); } }
    }
  }

  function mount(root=document.querySelector('[data-galton-root]')){
    if(!root) return null;
    if(root.__galtonController&&!root.__galtonController.destroyed) return root.__galtonController;
    root.dataset.galtonMounted='true'; root.__galtonController=new GaltonController(root); return root.__galtonController;
  }
  function activate(){ const controller=mount(); if(controller) controller.activate(); return controller; }
  function deactivate(options={}){ const root=document.querySelector('[data-galton-root]'); if(root&&root.__galtonController) root.__galtonController.deactivate(options); }
  function handleSessionWipe(){
    const root=document.querySelector('[data-galton-root]'); if(!root) return null;
    const current=root.__galtonController, remount=Boolean(current&&current.active&&root.isConnected&&root.getClientRects().length);
    if(current) current.destroy();
    if(!remount) return null;
    const controller=mount(root); controller.activate(); return controller;
  }

  ns.persistence={STORAGE_KEY,SCHEMA_VERSION,PERSISTED_CONFIG_FIELDS:PERSISTED_CONFIG_FIELDS.slice(),normalize:normalizePreferences,read:readPreferences,write:writePreferences};
  ns.controller={GaltonController,mount,activate,deactivate,panelHTML};
  global.galtonBoardPanelHTML=panelHTML;
  global.activateGaltonBoard=activate;
  global.deactivateGaltonBoard=deactivate;
  global.handleGaltonSessionWipe=handleSessionWipe;
})(window);
