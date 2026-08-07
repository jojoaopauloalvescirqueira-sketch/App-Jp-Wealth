// ============ ESTADO INICIAL (espelha a planilha) ============
const DEFAULTS = {
  params:{ saldoIni:10000, saldoAtu:10240, inicio:'2026-05-25',
    mdd:0.15, alarm:0.13, genLev:0.4, genRisk:0.01, fw:1,
    vrmN:1.20, vrmHV:1.50, refM:BASE_TARGET_MONTHLY, refA:BASE_TARGET_ANNUAL },
  matrix:[
    {nome:'FASE 1',ddmin:0,ddmax:0.04,alav:4.0},
    {nome:'FASE 2',ddmin:0.0401,ddmax:0.08,alav:2.0},
    {nome:'FASE 3',ddmin:0.0801,ddmax:0.12,alav:1.0},
    {nome:'FASE 4',ddmin:0.1201,ddmax:0.15,alav:0.4},
  ],
  atr55:0.00335, atr660:0.00426, expAlvo:0.4,
  // 'preco' = cotação de mercado do par. O nocional USD é derivado por usdPerBase():
  // pares de base USD (USDJPY/CHF/CAD) têm nocional fixo de $100k; AUDCAD usa AUDUSD.
  instruments:[
    {name:'EURUSD',preco:1.1413,cpl:100000,teto:0.05,updated:'2026-07-02'},
    {name:'GBPUSD',preco:1.3303,cpl:100000,teto:0.04,updated:'2026-07-02'},
    {name:'AUDUSD',preco:0.6893,cpl:100000,teto:0.09,updated:'2026-07-02'},
    {name:'NZDUSD',preco:0.5681,cpl:100000,teto:0.09,updated:'2026-07-02'},
    {name:'USDJPY',preco:161.93,cpl:100000,teto:0.05,updated:'2026-07-02'},
    {name:'USDCHF',preco:0.8069,cpl:100000,teto:0.05,updated:'2026-07-02'},
    {name:'USDCAD',preco:1.4213,cpl:100000,teto:0.05,updated:'2026-07-02'},
    {name:'AUDCAD',preco:0.9796,cpl:100000,teto:0.11,updated:'2026-07-02'},
    {name:'US500',preco:7000,cpl:1,teto:0.88,updated:'2026-06-25',
     banned:true,banReason:'Suspenso pelo Estatuto JP Wealth V10.0 — pendente de deliberação sobre exclusão definitiva ou reativação futura.'},
    {name:'XAUUSD',preco:4200,cpl:100,teto:0.02,updated:'2026-05-01',
     banned:true,banReason:'Decreto pessoal — proibição de operar metais (comportamento destrutivo recorrente).'},
  ],
  profiles:riskProfilesForState(),
  accounts:[
    {nome:'Jp Wealth MAM',tipo:'MESTRE',broker:'Hantec Markets',platform:'',platformLogin:'',investorPassword:'',perfil:'Base',sini:10000,satu:10240,perfilLocked:true},
    {nome:'Swissquote I',tipo:'PRÓPRIA',broker:'Swissquote',platform:'',platformLogin:'',investorPassword:'',perfil:'Base',sini:5000,satu:5100,perfilLocked:true},
    {nome:'TTP 10K I',tipo:'SATÉLITE',broker:'The Trading Pit',platform:'',platformLogin:'',investorPassword:'',perfil:'Longevity',sini:10000,satu:10000,perfilLocked:true},
    {nome:'FTMO 100k',tipo:'SATÉLITE',broker:'FTMO',platform:'',platformLogin:'',investorPassword:'',perfil:'High Longevity Plus',sini:100000,satu:100000,perfilLocked:true},
  ],
  riskPinHash:null, // hash SHA-256 da senha de alteração de perfil (fricção, não criptografia militar)
  phaseUnlocked:[true,false,false,false], // Fase 1 sempre liberada; 2/3/4 exigem questionário de transição
  transitionLog:[], // auditoria: {fase, ts, resumo}
  protocolBreaches:0, // contador de fechamentos marcados como rompimento de protocolo sem justificativa
  loteMaster:0.04,
  cycleRealizado:0, // resultado líquido acumulado de operações ARQUIVADAS no ciclo (perda mantém DD; lucro não amplia limites — Art. 4.3)
  quarantine:null, // {inicio,fim} quando a guilhotina de 15% dispara (Art. 3.10 §2 — 90 dias)
  ledger:[], // fechamento diário: {data,resultado,saldo,nota}
  ledgerArchive:[], // períodos encerrados: snapshots do ledger antigo ao reiniciar período
  period:{nome:'',profile:'base'}, // período contábil: identificação + perfil de risco escolhido
  theme:'dark', // aparência: 'dark' (padrão Mission Control) | 'light' (SET 4)
  acct:{diasSemana:4.5, mesesAno:10.5}, // programação da contabilidade → dias líquidos/ano
  // MEI-JP: somente parâmetros e observações históricas persistem. Resultados de Monte Carlo
  // são sempre recalculados, evitando salvar trajetórias pesadas no navegador.
  mei:{
    version:'1.0', enabled:true, sourceMode:'auto', simulationCount:5000,
    horizonMonths:60, confidenceLevel:0.90, seedMode:'random', fixedSeed:'',
    // Revisão metodológica v1.0: predominância empírica só a partir de 36 retornos válidos
    // (antes 24). Amostra patrimonial curta é vulnerável a regime, concentração temporal e
    // contaminação por fluxos — 24 observações permanecem em estágio híbrido avançado.
    minimumHistoricalMonths:36, hybridStartMonths:6, empiricalStartMonths:36,
    cid:{base:'',longevity:'',high_longevity:'',high_longevity_plus:''},
    // history: [{id, date:'AAAA-MM-01', startingEquity:''|num (informativo), endingEquity:num,
    //            contributions:num, withdrawals:num, notes:''}] — fluxo líquido F = aportes − retiradas
    history:[], lastCalibrationAt:'', notes:''
  },
  stopF:1.8, // fator F do Stop Estatístico Raiz-N (§9.3.2 — 1,5 a 2,0)
  atrPctManual:0, // ATR(55) H4 em % — 0 = derivar do ATR absoluto ÷ preço ao vivo; >0 = valor manual
  onboarding:{done:false, operador:'', supervisor:'', corretora:'', plataforma:'', alavCorretora:'', moedaBase:'USD',
    brokerLogin:'', investorPassword:'', brokerServer:'',
    propDailyDrawdown:'', propMaxDrawdown:'', propTrailingRule:'', propTrailingDescription:'',
    propProfitTarget:'', propMinTradingDays:'', propAbsenceRules:'', restrictiveRuleAccepted:false,
    reserveMasterCapital:'', reserveFcrRequired:'', reserveFcrCurrent:'', reserveFcrStatus:'',
    reserveMonthlyExpenses:'', reserveFeoRequired:'', reserveFeoCurrent:'', reserveFeoStatus:'',
    reserveFcrCoveragePct:'', reserveFeoCoveragePct:'', reserveFeoMonthsCovered:'',
    reserveSegregationAccepted:false, reserveDeficitAccepted:false, reserveNotes:'',
    centralCashStatus:'', centralCashCustody:'', centralCashCustodyOther:'',
    centralCashMainPct:'', centralCashAgilePct:'', centralCashLiquidityPct:'', centralCashExternalPct:'', centralCashOtherPct:'',
    centralCashCompositionMode:'percentual', centralCashCompositionTotal:'', centralCashTraceabilityScore:'',
    fcrLiquidity:'', feoLiquidity:'', cashLedgerStatus:'', centralCashPolicyAccepted:false, centralCashNoAccepted:false, centralCashNotes:'',
    epStatus:'', epPlatform:'', epPlatformOther:'', epReference:'',
    epDailyLimit:'', epMaxDrawdown:'', epStatuteMatch:'', epRestrictiveAccepted:false,
    epPropDailyEnabled:'', epPropDailyBase:'', epPropDailyNotes:'',
    epTestStatus:'', epNoConfigAccepted:false, epNotes:'',
    summaryAccepted:false,
    consentAccepted:false, consentVersion:'', consentDocument:'', consentAcceptedAt:'', consentOperator:''}, // questionário de início de período (SET 5b)
  // grades por fase: cada ordem {id,par,tipo,lote,entry,sl,tp,result,status}
  // Gênese de exemplo com risco ≤ 1% do saldo inicial (Art. 8.6): 0.04 × 100k × 0.02432 = $97,28
  phases:[
    {title:'FASE 1 — O ATAQUE',cls:'p1',faseNome:'FASE 1',ddtxt:'0–4%',alavtxt:'4,0x',
     orders:[
       {id:'248.1',par:'GBPUSD',tipo:'BUY',lote:0.04,entry:1.35032,sl:1.32600,tp:1.38060,result:0,status:'Aberta'},
       {id:'248.2',par:'GBPUSD',tipo:'BUY',lote:0.04,entry:1.34485,sl:1.31552,tp:1.35337,result:0,status:'Aberta'},
       {id:'248.3',par:'GBPUSD',tipo:'BUY',lote:0.04,entry:1.34087,sl:1.31448,tp:1.34883,result:0,status:'Aberta'},
       {id:'',par:'',tipo:'BUY',lote:0,entry:0,sl:0,tp:0,result:0,status:''},
       {id:'',par:'',tipo:'BUY',lote:0,entry:0,sl:0,tp:0,result:0,status:''},
     ]},
    {title:'FASE 2 — DESACELERAÇÃO',cls:'p2',faseNome:'FASE 2',ddtxt:'4–8%',alavtxt:'2,0x',orders:emptyOrders(4)},
    {title:'FASE 3 — SOBREVIVÊNCIA',cls:'p3',faseNome:'FASE 3',ddtxt:'8–12%',alavtxt:'1,0x',orders:emptyOrders(3)},
    {title:'FASE 4 — O ABISMO',cls:'p4',faseNome:'FASE 4',ddtxt:'12–15%',alavtxt:'0,4x',orders:emptyOrders(2)},
  ],
  perf:[
    {mes:'Jan',ret:0.012,dd:0.01},{mes:'Fev',ret:0.019,dd:0.008},{mes:'Mar',ret:0.031,dd:0.012},
    {mes:'Abr',ret:-0.021,dd:0.021},{mes:'Mai',ret:0.028,dd:0.015},{mes:'Jun',ret:0.015,dd:0.009},
    {mes:'Jul',ret:0,dd:0},{mes:'Ago',ret:0,dd:0},{mes:'Set',ret:0,dd:0},
    {mes:'Out',ret:0,dd:0},{mes:'Nov',ret:0,dd:0},{mes:'Dez',ret:0,dd:0},
  ],
  checklist:[
    {group:'Contexto — o mercado permite operar?',items:[
      {label:'Calendário econômico verificado',v:1},{label:'Juros / Dólar / COT alinhados',v:1}]},
    {group:'Regime de mercado',items:[
      {label:'Tendência limpa / impulsos consistentes',v:2},{label:'Não está em expansão sem pullback',v:1}]},
    {group:'Lógica operacional',items:[
      {label:'Tendência dominante (D1)',v:2},{label:'Tendência primária/secundária (H4/H1)',v:1}]},
    {group:'Zonas de liquidez',items:[
      {label:'Suportes/resistências e LTA/LTB',v:2},{label:'Linhas Nocuda revalidadas',v:1},{label:'Pivots D1 e H1/H4',v:2}]},
    {group:'Gatilho válido',items:[
      {label:'Toque na linha Nocuda a favor da tendência',v:2},{label:'Nocuda + Confluência',v:2}]},
    {group:'Bússola Estratégica (Art. 1.3)',items:[
      {label:'Padrão',v:1},{label:'Tendência',v:2},{label:'Amplitude',v:1},{label:'Confluência',v:2}]},
  ],
  // Backlog interno do período de MVP (14-mvp-notes.js) — tarefas/bugs/funcionalidades/
  // melhorias registradas pelo operador durante testes. Não é log de auditoria financeira,
  // não é notificação, não guarda dado de trading. items: ver mvpNotesNormalizeItem().
  // Evolução do schema (migração idempotente em mvpNotesNormalizeState, 04-persistence.js):
  //   v1 = notas sem pastas (items[] apenas);
  //   v2 = folders[] + item.folderId;
  //   v3 = item.completedAt (carimbo de conclusão, só enquanto status==='done') +
  //        ui{} (preferências persistidas do painel: drawerWidth) + visão virtual
  //        "Concluído", derivada de status e nunca gravada como pasta.
  mvpNotes:{schemaVersion:3, showHeaderIcon:true, folders:[], items:[], ui:{drawerWidth:460}},
};
function emptyOrders(n){return Array.from({length:n},()=>({id:'',par:'',tipo:'BUY',lote:0,entry:0,sl:0,tp:0,result:0,status:''}));}
