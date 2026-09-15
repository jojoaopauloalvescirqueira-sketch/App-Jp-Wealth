// JP Wealth V11 documentary policy. Values are not evidence of homologation.
// No state/storage/network; amendments create a separately identified policy.
(function(root){
  'use strict';
  const namespace=root.JPWForex||(root.JPWForex={});
  const sources={
    statute:{path:'docs/normative/Estatuto_JP_WEALTH_UNIFICADO.pdf',version:'V11',sha256:'2dab6166bb8513cd9beb7fe39c574971af086ebae66683d99c0e6fac69eb6769'},
    annex:{path:'docs/normative/ANEXO_PARAMETRICO_CANONICO.md',version:'JPW-ANNEX-T03',effectiveFrom:'2026-09-03',sha256:'6240b6330a35fd488f16d4191129eeb01aff8f7a4707158c043afb37d91cdc23'},
    constitution:{articles:['I.6','I.7'],hashes:['fa4ab196db192ffa4cd8e97e26749ebd44d2282db92a358e0cd7ac7f02f25669','dbdd690bf55dc06abae38f5a6b61364a336671ccf9dd29d4d2298dabb8ef664f']}
  };
  const phases=[
    {id:1,name:'Gênese',lower:0,upper:2,maxLeverage:1,amplification:'FORBIDDEN',defense:'FORBIDDEN'},
    {id:2,name:'Ataque',lower:2,upper:6,maxLeverage:4,amplification:'DECLARED_ZONES_ONLY',defense:'CONDITIONAL'},
    {id:3,name:'Intermédio',lower:6,upper:10,maxLeverage:2.4,amplification:'RESTRICTED',defense:'FORBIDDEN'},
    {id:4,name:'Defesa',lower:10,upper:14,maxLeverage:1.4,amplification:'FORBIDDEN',defense:'FORBIDDEN'},
    {id:5,name:'Cuidado',lower:14,upper:18,maxLeverage:.8,amplification:'FORBIDDEN',defense:'FORBIDDEN',emergency:true},
    {id:6,name:'Preparação',lower:18,upperParameter:'P-03',maxLeverage:.4,amplification:'FORBIDDEN',defense:'FORBIDDEN',emergency:true}
  ];
  const rows=[];
  function item(id,name,value,unit,authority,host,extra){
    const pending=authority==='PENDING_N3';
    const delegated=authority==='DELEGATED_N3'||pending;
    rows.push(Object.assign({id,name,category:'FOREX',description:name,value,unit,
      normativeLevel:delegated?'N3':(authority==='MIRROR_N2'?'N2':'NON_N3'),
      authorityMode:authority,status:pending?'PENDING':(value===null?'INDETERMINATE':'VIGENTE'),
      hostNorm:host,canonicalSource:delegated?sources.annex.path:sources.statute.path,
      homologationStatus:delegated?'NOT_HOMOLOGATED':'NOT_APPLICABLE',
      mathematicalValidationStatus:'NOT_VALIDATED',empiricalValidationStatus:'NOT_VALIDATED',
      operationalEffect:pending?'DEPENDENT_CONDUCT_BLOCKED':'CUMULATIVE_LIMIT',
      dependencies:[],editableMode:delegated?'PROPOSAL_ONLY':'NORMATIVE_AMENDMENT_PROPOSAL',
      effectiveFrom:delegated?sources.annex.effectiveFrom:null,version:sources.annex.version,
      formulaReference:host,notes:[],historicalValues:[]},extra||{}));
  }
  const D='DELEGATED_N3',P='PENDING_N3',M='MIRROR_N2';
  item('P-01','Faixas das seis fases',phases.map(p=>({phase:p.id,lower:p.lower,upper:p.upper===undefined?null:p.upper,upperParameter:p.upperParameter||null})),'DD_PERCENT',M,'PDF p51 Art6.1 §1');
  item('P-02','Tetos de alavancagem por fase',phases.map(p=>p.maxLeverage),'MULTIPLE',M,'PDF p51 Art6.1 §1');
  item('P-03','Limite máximo de drawdown',22,'DD_PERCENT',D,'PDF p51 Art6.1; Constituição I.6 §2',{mathematicalValidationStatus:'PARTIAL',operationalEffect:'COMPULSORY_CLOSE',notes:['Calibração candidata em vigência expressa; não empiricamente validada.']});
  item('P-04a','Margem de histerese',.5,'PERCENTAGE_POINT',D,'PDF p32 Art4.1 §§5/10');
  item('P-04b','Fechamentos de confirmação da histerese',1,'H4_CLOSE',D,'PDF p32 Art4.1 §§5/10');
  item('P-05','Prazo de posição zerada sem confirmação',null,'TIME',P,'PDF p35 Art4.4 §3',{operationalEffect:'OPERATION_CONTINUES_EXCLUSIVITY_RETAINED'});
  item('P-06','Critério de tendência persistente',null,'METRIC',P,'L1 Art3.13 §5',{operationalEffect:'PERSISTENT_REGIME_PRESUMED_DEFENSE_FORBIDDEN'});
  item('P-07','Número máximo de defesas',null,'COUNT',P,'L1 Art3.13 §9',{dependencies:['P-06']});
  item('P-08','Teto acumulado de margem operacional reposta',null,'SI_PERCENT',P,'L1 Art3.16 §2',{operationalEffect:'MOR_NOT_EXECUTABLE'});
  item('P-09','Amostra para revisão de MOR',null,'COUNT',P,'L1 Art3.16 §§13/14',{operationalEffect:'AUTOMATIC_REVOCATION_WITHOUT_DELIBERATION'});
  item('P-10','Segregação da Catraca',null,'RESULT_PERCENT',P,'L1 Art3.19 §5',{operationalEffect:'BEFORE_NEXT_CYCLE_REFERENCE',notes:['Decisão prudencial, não dado ausente. Sem incorporação integral automática ao novo SI.']});
  item('P-11','Períodos VRM',{short:55,long:660,timeframe:'H4'},'PERIOD',D,'PDF p44 Art4.10 §1',{mathematicalValidationStatus:'PARTIAL'});
  item('P-12a','Limiares VRM',{normalBelow:1.2,highAbove:1.5},'RATIO',D,'PDF p69 tabela VRM',{homologationStatus:'RATIFIED_MINUTES_PENDING'});
  item('P-12b','Alavancagem por regime VRM',{normal:.5,transition:.25,high:.25},'MULTIPLE_PER_ORDER',M,'PDF p69 tabela VRM',{notes:['Conduta N2; a delegação do Art4.10 não inclui alavancagem.']});
  item('P-13','Periodicidade de recálculo VRM',null,'TIME',P,'PDF p44 Art4.10 §1',{operationalEffect:'NO_AUTONOMOUS_EFFECT',notes:['Proposta semanal não vigente, sem fallback.']});
  item('P-14','Risco máximo da Gênese',null,'SI_PERCENT',P,'PDF p64 Art8.1 I',{operationalEffect:'GENESIS_BLOCKED',dependencies:['P-18'],historicalValues:[{value:1,status:'LEGACY_NOT_CURRENT'}]});
  item('P-15','Teto estrutural da Gênese',1,'MULTIPLE',M,'PDF pp51/64 Art6.1 e8.1 II',{dependencies:['P-02','P-12b'],notes:['Teto, não dimensionamento; VRM e riscos cumulativos.']});
  item('P-16','Período ATR do stop',55,'H4_PERIOD',D,'PDF p78 Art9.5 §1',{notes:['Parâmetro distinto do período curto do VRM.']});
  item('P-17','Teto de Risco Agregado por fase',null,'SI_PERCENT',P,'PDF p71 Art8.4 §13',{operationalEffect:'PRO_FORMA_AGGREGATE_BLOCKED',notes:['TRA F1=F2; demais não crescentes.']});
  item('P-18','Risco de Admissão por fase',null,'SI_PERCENT',P,'PDF p71 Art8.4 §13',{operationalEffect:'GENESIS_BLOCKED',dependencies:['P-14','P-17']});
  item('P-19','Degraus e distribuição de volume',null,'DECLARED_STRUCTURE',P,'L3 Art9.2 §4',{operationalEffect:'UNDECLARED_STEP_FORBIDDEN',notes:['Estrutura declarada por operação; teto derivado não preenche o parâmetro.']});
  item('P-20','Múltiplo mínimo do stop',3.5,'ATR_MULTIPLE',D,'PDF pp79/80 Art9.5 §§4/7',{homologationStatus:'RATIFIED_MINUTES_PENDING',mathematicalValidationStatus:'PARTIAL',historicalValues:[{value:2,status:'LEGACY_NOT_CURRENT'}]});
  item('P-21','Fator de segurança Raiz-N',null,'FACTOR',P,'L3 Raiz-N; L9 AnexoC',{operationalEffect:'DIAGNOSTIC_ONLY_NO_VETO'});
  item('P-22','N do modelo Raiz-N',null,'H4_CANDLES','INDETERMINATE_NON_N3','L3 Raiz-N',{operationalEffect:'DIAGNOSTIC_ONLY_NO_VETO',editableMode:'DIAGNOSTIC_INPUT'});
  item('P-23','Buffer de descontinuidade',null,'SI_PERCENT',P,'PDF p71 Art8.4 §13-A',{operationalEffect:'UNCOVERED_RESIDUAL_RISK',notes:['Ausência quantitativa expressa; não equivale a buffer zero ou veto autônomo.']});
  item('P-24','Duração mínima da quarentena',null,'TIME',P,'PDF p57 Art6.5 §4',{operationalEffect:'RETURN_BLOCKED',historicalValues:[{value:90,unit:'DAYS',status:'LEGACY_NOT_CURRENT'}]});
  item('P-25','Prazo por movimento corretivo',null,'TIME',P,'L2 Art7.2 §2',{operationalEffect:'IMMEDIATE_PRUNING'});
  item('P-26','Gatilho compulsório por avanço',null,'PHASE_WIDTH_FRACTION',P,'L2 Art7.2 §3',{operationalEffect:'IMMEDIATE_PRUNING'});
  item('P-27','Liquidez FCR',{minimumDays:0,maximumDays:1},'BUSINESS_DAY',D,'PDF p86 Art13.2 §7');
  item('P-28','Liquidez FEO',{maximumDays:2},'BUSINESS_DAY',D,'PDF p88 Art13.3 §11');
  item('P-29','Percentual equivalente do FEO',null,'SI_PERCENT','DERIVED_NON_N3','PDF pp87/88 Art13.3; Anexo P29',{status:'DERIVED',operationalEffect:'REPRESENTATION_ONLY',editableMode:'READ_ONLY',notes:['Despesas → montante → percentual; nunca o inverso. Conflito de homologação nominal permanece explícito.'],historicalValues:[{value:21,status:'LEGACY_NOT_CURRENT'}]});
  item('P-30','Fatores de perfis satélites',null,'FACTOR',P,'PDF p56 Art6.4 §1',{operationalEffect:'REPLICATION_BLOCKED',dependencies:['P-03','MAX_LOSS','SAFETY_MARGIN'],historicalValues:[{value:[66,50,33],status:'REVOKED'},{value:[53,40,27],status:'REVOKED'}]});
  item('FCR_BASE','Base de cálculo FCR','MASTER_NOMINAL_CAPITAL','BASE',M,'PDF p86 Art13.2 §1',{notes:['Prevalência do PDF fornecido. Anexo X-FCR/M02/K01 usa SI; divergência preservada.']});
  item('FEO_COVERAGE','Cobertura FEO',6,'MONTH',M,'PDF pp87/88 Art13.3',{notes:['Despesas reais apuradas; não rentabilidade nem percentual fixo de capital.']});
  item('DECISION_TIMEFRAME','Horizonte decisório','H4','TIMEFRAME',M,'L1 Art3.18 §6');
  item('PLANNING_MONTHLY','Referência mensal de planejamento',.035,'RETURN_RATIO',M,'PDF p117 Título32',{operationalEffect:'PLANNING_ONLY_NOT_EXPECTATION'});
  item('PLANNING_ANNUAL','Referência anual de planejamento',[.35,.40],'RETURN_RATIO',M,'PDF p117 Título32',{operationalEffect:'PLANNING_ONLY_NOT_COMPOUNDED_MONTHLY'});
  function freeze(value){
    if(value&&typeof value==='object'&&!Object.isFrozen(value)){Object.keys(value).forEach(k=>freeze(value[k]));Object.freeze(value);}
    return value;
  }
  const byId=Object.create(null);rows.forEach(r=>{byId[r.id]=freeze(r);});
  phases.forEach(p=>{p.number=p.id;p.ddMinPercent=p.lower;p.ddMaxPercent=p.upper===undefined?byId['P-03'].value:p.upper;});
  const policy={version:'JPW-FOREX-V11-T03-1',policyVersion:'JPW-FOREX-V11-T03-1',statuteVersion:'V11',parametricAnnexVersion:'JPW-ANNEX-T03',
    effectiveDate:'2026-09-03',calculationMode:'CURRENT_DOCUMENTARY',operability:'BLOCKED',sources,phases,
    delegatedCount:rows.filter(r=>r.authorityMode===D||r.authorityMode===P).length,
    planning:{referenceMonthlyReturn:byId.PLANNING_MONTHLY.value,annualReferenceRange:byId.PLANNING_ANNUAL.value},
    conflicts:[
      {id:'FCR_BASE_CONFLICT',source:'PDF p86 / Anexo K01',resolution:'STATUTE_PRECEDENCE_NOMINAL_CAPITAL',closed:false},
      {id:'FEO_HOMOLOGATION_CONFLICT',source:'PDF pp87/88 / Anexo P29',resolution:'EXPENSE_AMOUNT_AND_GOVERNANCE_REPORTED_SEPARATELY',closed:false},
      {id:'ANNEX_AGGREGATE_OMISSION',source:'PDF p70 Art8.4 §9 / Anexo D11',resolution:'INCLUDE_AMPLIFYING_PENDING_ORDERS',closed:false},
      {id:'HOMOLOGATION_NOT_CANONICITY',source:'Constituição I.6 X / Anexo A5',resolution:'NO_OPERATIONAL_APPROVAL_INFERRED',closed:false}
    ],
    get:function(id){return Object.prototype.hasOwnProperty.call(byId,id)?byId[id]:null;},
    list:function(){return rows.slice();},
    snapshot:function(){return JSON.parse(JSON.stringify({version:this.version,statuteVersion:this.statuteVersion,parametricAnnexVersion:this.parametricAnnexVersion,effectiveDate:this.effectiveDate,operability:this.operability,sources:this.sources,items:rows,conflicts:this.conflicts}));}
  };
  freeze(rows);freeze(policy);namespace.policy=policy;
})(typeof globalThis!=='undefined'?globalThis:window);
