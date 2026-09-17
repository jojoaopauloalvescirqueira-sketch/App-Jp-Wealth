/* Consolidado FX: local descriptive projections, not the normative Forex engine.
 * Classic scripts share a namespace, never financial globals. Imported HTML is
 * parsed inside an inert template and only allowlisted text facts leave it.
 * Reports: metatrader5.com/en/terminal/help/trading_advanced/history_report
 * Deals: mql5.com/en/docs/constants/tradingconstants/dealproperties
 */
(function (root) {
  'use strict';
  const api = root.JPWFXConsolidated = root.JPWFXConsolidated || {};
  const VERSION = 1, MAX_ROWS = 50000, MAX_TEXT = 12 * 1024 * 1024;
  const METRICS = ['netProfit','grossProfit','grossLoss','commission','swap','fee','tradeCount','wins','losses','neutral','bestTrade','worstTrade','averageWin','averageLoss','maxWinStreak','maxLossStreak','initialBalance','deposits','withdrawals','winRate','profitFactor','expectedPayoff','balance','equity','growthPct','drawdownPct','drawdownAmount','sharpe','recoveryFactor','tradingActivityPct','maxDepositLoadPct','mfe','mae'];
  const SUMMARY = [...METRICS,'deposits','withdrawals','margin','freeMargin','credit'];
  const IDENTITY = ['login','broker','currency','server'];
  const FIELDS = ['ticket','orderTicket','positionId','time','openedAt','closedAt','symbol','type','entry','volume','remainingVolume','price','sl','tp','commission','fee','swap','profit','netResult','balance','state','orderScope','comment','magic'];
  const NUMBERS = new Set(['volume','remainingVolume','price','sl','tp','commission','fee','swap','profit','netResult','balance']);
  const CASH_TYPES = new Set(['commission','commission_daily','commission_monthly','commission_agent_daily','commission_agent_monthly','charge','interest','dividend','dividend_franked','tax']);
  const DEAL_TYPES = new Set(['buy','sell','balance','credit','correction','bonus','buy_canceled','sell_canceled',...CASH_TYPES]);
  const clone = value => JSON.parse(JSON.stringify(value));
  const plain = value => value !== null && typeof value === 'object' && !Array.isArray(value) && (Object.getPrototypeOf(value) === Object.prototype || Object.getPrototypeOf(value) === null);
  const text = value => typeof value === 'string' ? value.replace(/[\u0000-\u0008\u000b\u000c\u000e-\u001f]/g,'').trim().slice(0,512) : null;
  const key = value => String(value || '').normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLowerCase().replace(/[\s:./_%()–—-]+/g,' ').trim();
  const identityKey = value => String(value || '').normalize('NFC').trim().toLowerCase();
  const issue = (code,message,severity) => ({code,message,severity:severity || 'warning'});
  const finite = value => typeof value === 'number' && Number.isFinite(value) && Math.abs(value) <= 1e15;
  const numeric = value => finite(value) ? value : null;
  const fingerprint = value => JSON.stringify(value); // Collision-free equality guard, never persisted.
  function shortHash(value) {
    let n = 2166136261;
    for (let i = 0; i < value.length; i++) n = Math.imul(n ^ value.charCodeAt(i),16777619);
    return (n >>> 0).toString(16).padStart(8,'0'); // Readable receipt suffix, not identity/security.
  }
  // Decimal addition avoids binary summation drift; source precision is retained
  // up to eight decimals. Ratios remain unrounded; UI owns display rounding.
  function sum(values) {
    if (values.some(value => !finite(value))) return null;
    const parts = values.map(value => value.toFixed(8).replace(/\.?0+$/,''));
    const scale = parts.reduce((max,value)=>Math.max(max,(value.split('.')[1]||'').length),0);
    const total=parts.reduce((n,value)=>n+BigInt((value.includes('.')?value:value+'.').padEnd(value.split('.')[0].length+1+scale,'0').replace('.','')||'0'),0n);
    if(total>BigInt(Number.MAX_SAFE_INTEGER)||total<BigInt(-Number.MAX_SAFE_INTEGER)) return null;
    return Number(total) / Math.pow(10,scale);
  }
  function numberText(value) {
    let s = String(value ?? '').trim().replace(/\u2212/g,'-');
    if (!s || /^[-–—]$/.test(s)) return null;
    if (s.startsWith('(') && s.endsWith(')')) s = '-' + s.slice(1,-1);
    s = s.replace(/%$/,'').trim();
    // Whitespace/apostrophes may group thousands, but arbitrary gaps are not digits.
    if (/[\s\u00a0\u202f']/.test(s)) {
      if (!/^[+-]?[1-9]\d{0,2}(?:[\s\u00a0\u202f']\d{3})+(?:[.,]\d{1,8})?$/.test(s)) return '';
      s = s.replace(/[\s\u00a0\u202f']/g,'');
    }
    return s;
  }
  function parseNumber(value,format) {
    let s = numberText(value);
    if (!s) return null;
    const comma=format==='decimal-comma';
    const valid=comma?/^[+-]?(?:\d+(?:,\d{1,8})?|[1-9]\d{0,2}(?:\.\d{3})+(?:,\d{1,8})?)$/:/^[+-]?(?:\d+(?:\.\d{1,8})?|[1-9]\d{0,2}(?:,\d{3})+(?:\.\d{1,8})?)$/;
    if(!valid.test(s)) return null;
    s=comma?s.replace(/\./g,'').replace(',','.'):s.replace(/,/g,'');
    if (!/^[+-]?\d+(?:\.\d{1,8})?$/.test(s)) return null;
    const n = Number(s);
    return finite(n) && Number.isSafeInteger(Math.round(n * Math.pow(10,(s.split('.')[1]||'').length))) ? n : null;
  }
  function parseReportNumbers(values,options={}) {
    const result={values:[],format:null,issues:[]},requested=options.numberFormat||'auto';
    if(!['auto','decimal-dot','decimal-comma'].includes(requested)) {
      result.values=values.map(()=>null);result.issues.push(issue('number_format_invalid','Formato numérico não reconhecido.','error'));return result;
    }
    const candidates=values.map(value=>({value,dot:parseNumber(value,'decimal-dot'),comma:parseNumber(value,'decimal-comma')}));
    const evidence=new Set(candidates.filter(c=>(c.dot===null)!==(c.comma===null)).map(c=>c.dot===null?'decimal-comma':'decimal-dot'));
    result.format=requested!=='auto'?requested:evidence.size===1?[...evidence][0]:null;
    if(requested==='auto'&&evidence.size>1) result.issues.push(issue('number_format_conflict','O arquivo mistura separadores numéricos incompatíveis. Confira os valores e o formato de exportação.','error'));
    const ambiguous=[],invalid=[],review=[];
    candidates.forEach(c=>{
      let n=result.format==='decimal-dot'?c.dot:result.format==='decimal-comma'?c.comma:c.dot===c.comma?c.dot:null;
      if(numberText(c.value)!==null) {
        if(c.dot===null&&c.comma===null || result.format&&n===null) invalid.push(String(c.value).slice(0,80));
        else if(n===null) ambiguous.push(c);
        if(requested!=='auto'&&n!==null&&/[.,]/.test(String(c.value))) review.push({label:String(c.value).slice(0,80)+' → '+n,ambiguous:c.dot!==null&&c.comma!==null&&c.dot!==c.comma});
      }
      result.values.push(n);
    });
    if(invalid.length) result.issues.push(issue('number_invalid','Valores numéricos inválidos para o formato: '+[...new Set(invalid)].slice(0,3).join('; ')+'.','error'));
    if(ambiguous.length) result.issues.push(issue('number_format_ambiguous','Confirme o separador decimal. Exemplos: '+ambiguous.slice(0,3).map(c=>String(c.value).slice(0,80)+' → '+c.dot+' (ponto) ou '+c.comma+' (vírgula)').join('; ')+'.','error'));
    if(requested!=='auto') result.issues.push(issue('number_format_confirmed','Formato escolhido: decimal com '+(requested==='decimal-dot'?'ponto':'vírgula')+'. Revise: '+[...new Set(review.sort((a,b)=>Number(b.ambiguous)-Number(a.ambiguous)).map(c=>c.label))].slice(0,3).join('; ')+'.'));
    return result;
  }
  function date(value,order) {
    const s = text(value);
    if (!s) return null;
    let m = s.match(/^(\d{4})[.\/-](\d{2})[.\/-](\d{2})(?:[ T](\d{2}):(\d{2})(?::(\d{2})(\.\d{1,3})?)?)?(Z|[+-]\d{2}:\d{2})?$/);
    if(!m) {
      const local=s.match(/^(\d{2})[.\/-](\d{2})[.\/-](\d{4})((?:[ T]\d{2}:\d{2}(?::\d{2}(?:\.\d{1,3})?)?)?(?:Z|[+-]\d{2}:\d{2})?)$/);
      if(!local) return null;
      const resolved=order||(+local[1]>12?'dmy':+local[2]>12?'mdy':local[1]===local[2]?'dmy':null);
      if(!resolved) return null;
      return date(local[3]+'-'+local[resolved==='dmy'?2:1]+'-'+local[resolved==='dmy'?1:2]+local[4]);
    }
    if (!m) return null;
    const y=+m[1],mo=+m[2],d=+m[3],h=+(m[4]||0),mi=+(m[5]||0),se=+(m[6]||0);
    const probe = new Date(Date.UTC(y,mo-1,d));
    if (y<1970||y>2200||probe.getUTCMonth()!==mo-1||probe.getUTCDate()!==d||h>23||mi>59||se>59) return null;
    if (m[8] && m[8]!=='Z' && (+m[8].slice(1,3)>23 || +m[8].slice(4)>59)) return null;
    return m[1]+'-'+m[2]+'-'+m[3]+(m[4]?'T'+m[4]+':'+m[5]+':'+(m[6]||'00')+(m[7]||''):'')+(m[8]||'');
  }
  const endOfDeclaredDate = value => value&&value.length===10?value+'T23:59:59.999':value;
  function reportCoverage(report) {
    const times=report.deals.map(r=>date(r.time)).filter(Boolean).sort();
    return {completeHistory:report.coverage?.completeHistory===true,timezone:text(report.coverage?.timezone)||'unknown',
      from:times[0]||null,through:endOfDeclaredDate(date(report.period.to)||date(report.generatedAt)||times[times.length-1]||null)};
  }
  function balanceReconciliation(report) {
    const unavailable={status:'unavailable',declaredBalance:numeric(report.summary.balance),ledgerBalance:null,difference:null};
    if(!report.coverage.completeHistory||unavailable.declaredBalance===null) return unavailable;
    const rows=[...new Map(report.deals.map(r=>[r.ticket,r])).values()].sort((a,b)=>(a.time||'').localeCompare(b.time||'')||String(a.ticket).localeCompare(String(b.ticket),undefined,{numeric:true}));
    if(!rows.length||rows[0].type!=='balance'||!(rows[0].profit>0)||!rows.every(r=>r.time&&r.time>=report.coverage.from&&r.time<=report.coverage.through&&r.netResult!==null&&(r.type==='buy'||r.type==='sell'||r.type==='balance'||CASH_TYPES.has(r.type)))) return unavailable;
    const ledgerBalance=sum(rows.map(r=>r.netResult));
    if(ledgerBalance===null) return unavailable;
    const difference=sum([unavailable.declaredBalance,-ledgerBalance]);
    return {status:difference===0?'matched':'mismatch',declaredBalance:unavailable.declaredBalance,ledgerBalance,difference};
  }
  function reconciliationIssue(reconciliation) {
    return issue('balance_reconciliation_mismatch','DIVERGÊNCIA DE SALDO: relatório declara '+reconciliation.declaredBalance+'; histórico comprovado calcula '+reconciliation.ledgerBalance+'. Diferença '+reconciliation.difference+'. Ambos os valores foram preservados; a importação não comprova conciliação.');
  }
  function completeSnapshotCoversLedger(snapshot,rows) {
    if(snapshot.coverage?.completeHistory!==true||!rows.length||typeof snapshot.reportSignature!=='string') return false;
    // The retained signature contains normalized facts, not executable source.
    // Bounds alone do not cover backdated additions or revised old events.
    try {
      const proof=JSON.parse(snapshot.reportSignature);
      if(reportValidation(proof).length||proof.coverage?.completeHistory!==true||proof.format!=='mt5-classic-html-v1') return false;
      const coverage=reportCoverage(proof),facts=new Map(proof.deals.map(r=>[r.ticket,fingerprint(normalizedRow(r))]));
      return facts.size===rows.length&&!!coverage.from&&!!coverage.through&&rows.every(r=>r.time&&r.time>=coverage.from&&r.time<=coverage.through&&facts.get(r.ticket)===fingerprint(normalizedRow(r)));
    } catch (_error) {return false;}
  }
  function emptyState() { return {schemaVersion:VERSION,accounts:[],receipts:[],revisions:[],defaultAccountId:null}; }
  function validateState(value) {
    const errors=[];
    if (!plain(value) || value.schemaVersion!==VERSION) return {ok:false,errors:['schema_version_unsupported']};
    if (!Array.isArray(value.accounts)||!Array.isArray(value.receipts)||!Array.isArray(value.revisions)) return {ok:false,errors:['state_collections_invalid']};
    if (value.defaultAccountId!==null && typeof value.defaultAccountId!=='string') errors.push('default_account_invalid');
    const ids=new Set();
    value.accounts.forEach(a=>{
      if (!plain(a)||typeof a.id!=='string'||!a.id||ids.has(a.id)) { errors.push('account_identity_invalid');return; }
      ids.add(a.id);
      IDENTITY.forEach(k=>{if(a[k]!==null && a[k]!==undefined && typeof a[k]!=='string') errors.push('account_'+k+'_invalid');});
      ['orders','deals','positions','summaries'].forEach(k=>{
        if(!Array.isArray(a[k])||a[k].length>MAX_ROWS) errors.push('account_'+k+'_invalid');
        else if(k!=='summaries') {
          const tickets=new Set();
          a[k].forEach(r=>{
            if(!plain(r)||typeof r.ticket!=='string'||!r.ticket||tickets.has(r.ticket)) errors.push('record_identity_invalid');
            else tickets.add(r.ticket);
            if(plain(r)) {
              NUMBERS.forEach(n=>{if(r[n]!==undefined&&r[n]!==null&&!finite(r[n])) errors.push('record_number_invalid');});
              if(k==='deals'&&!DEAL_TYPES.has(r.type)) errors.push('deal_type_invalid');
            }
          });
        } else a.summaries.forEach(s=>{
          if(!plain(s)||!plain(s.values)||!plain(s.period)||typeof s.receiptId!=='string') {errors.push('summary_invalid');return;}
          SUMMARY.forEach(n=>{if(s.values[n]!=null&&!finite(s.values[n])) errors.push('summary_number_invalid');});
          if(s.values.monthly!=null&&(!Array.isArray(s.values.monthly)||s.values.monthly.some(m=>!plain(m)||!/^\d{4}-\d{2}$/.test(m.month)||['netProfit','growthPct','tradeCount'].some(n=>m[n]!=null&&!finite(m[n]))))) errors.push('summary_monthly_invalid');
        });
      });
    });
    function inspect(v,depth) {
      if(depth>20) {errors.push('state_depth_invalid');return;}
      if(typeof v==='number'&&!finite(v)) errors.push('state_number_invalid');
      if(v&&typeof v==='object') Object.keys(v).forEach(k=>{
        if(['__proto__','constructor','prototype','investorPassword','password','rawHTML','originalBytes'].includes(k)) errors.push('state_field_forbidden');
        else inspect(v[k],depth+1);
      });
    }
    inspect(value,0);
    return {ok:errors.length===0,errors:[...new Set(errors)]};
  }
  const columnAliases = {
    time:['time','horario','hora','data hora'],openedAt:['open time','horario de abertura','hora de abertura'],closedAt:['close time','horario de fechamento'],
    ticket:['deal','negociacao','transacao','order','ordem','position','posicao','ticket'],orderTicket:['order','ordem'],positionId:['position id','id da posicao'],
    symbol:['symbol','simbolo','ativo'],type:['type','tipo'],entry:['direction','direcao','entrada'],volume:['volume'],price:['price','preco'],
    sl:['s l','sl'],tp:['t p','tp'],commission:['commission','comissao'],fee:['fee','taxa'],swap:['swap'],profit:['profit','lucro','lucro prejuizo'],balance:['balance','saldo'],state:['state','estado','status'],comment:['comment','comentario'],magic:['magic']
  };
  const labels = {
    login:['account','conta'],broker:['company','broker','empresa','corretora'],currency:['currency','deposit currency','moeda','moeda de deposito'],server:['server','servidor'],
    period:['period','periodo'],generatedAt:['date','data','report date'],netProfit:['total net profit','net profit','lucro liquido total','lucro liquido'],grossProfit:['gross profit','lucro bruto'],grossLoss:['gross loss','perda bruta','prejuizo bruto'],
    balance:['balance','saldo'],equity:['equity','patrimonio','capital liquido'],commission:['commission','commissions','comissao','comissoes'],swap:['swap','swaps'],fee:['fee','fees','taxas'],deposits:['deposits','depositos'],withdrawals:['withdrawals','saques'],
    profitFactor:['profit factor','fator de lucro'],sharpe:['sharpe ratio','indice de sharpe'],growthPct:['growth','crescimento'],tradeCount:['total trades','total de negociacoes'],margin:['margin','margem'],freeMargin:['free margin','margem livre']
  };
  function entry(value) {
    return ({'in':'in','entrada':'in','out':'out','saida':'out','in out':'inout','inout':'inout','reversao':'inout','out by':'out_by','out_by':'out_by','saida por':'out_by'})[key(value)] || text(value);
  }
  function type(value) {
    const k=key(value), map={'compra':'buy','venda':'sell','saldo':'balance','deposito':'balance','saque':'balance','credito':'credit','comissao':'commission','comissao diaria':'commission_daily','comissao mensal':'commission_monthly','juros':'interest','dividendo':'dividend','imposto':'tax','correcao':'correction','bonus':'bonus','buy canceled':'buy_canceled','sell canceled':'sell_canceled'};
    return map[k] || k.replace(/ /g,'_') || null;
  }
  function normalizedRow(row) {
    const out={};
    FIELDS.forEach(k=>{out[k]=NUMBERS.has(k)?numeric(row[k]):text(row[k]);});
    out.type=type(out.type);out.entry=entry(out.entry);
    // Signed amounts are preserved. Missing cost is not a zero charge.
    out.netResult=sum([out.profit,out.commission,out.fee,out.swap]);
    return out;
  }
  function parseHTML(input,options={}) {
    const report={format:'unknown',identity:{login:null,broker:null,currency:null,server:null},period:{from:null,to:null,declared:false,timezone:'unknown'},generatedAt:null,orders:[],deals:[],positions:[],summary:{},issues:[],coverage:{completeHistory:false,timezone:'unknown'}};
    if(typeof input!=='string'||input.length>MAX_TEXT) {report.issues.push(issue('html_size','Arquivo HTML ausente ou acima do limite local.','error'));return report;}
    const template=root.document.createElement('template');
    template.innerHTML=input; // Inert: never attached, and no URL-bearing node is copied.
    const dom=template.content;
    dom.querySelectorAll('script,style,iframe,object,embed,link,img,video,audio,source,svg,math,template').forEach(n=>n.remove());
    const numbers=[],dates=[];
    const numberCell=(target,field,value)=>{target[field]=null;numbers.push({target,field,value});};
    const dateCell=(target,field,value)=>{target[field]=null;if(value) dates.push({target,field,value});};
    let section=null,headers=null,signature=false,rows=0;
    dom.querySelectorAll('tr').forEach(tr=>{
      if(++rows>MAX_ROWS) return;
      const cells=Array.from(tr.children).filter(n=>n.tagName==='TD'||n.tagName==='TH').map(n=>n.textContent.trim());
      if(!cells.length) return;
      const nonempty=cells.filter(Boolean),first=key(nonempty[0]);
      const sections={'orders':'orders','ordens':'orders','deals':'deals','negociacoes':'deals','transacoes':'deals','positions':'positions','posicoes':'positions','open positions':'positions','posicoes abertas':'positions','working orders':'working','ordens ativas':'working','summary':'summary','resumo':'summary','details':'summary','detalhes':'summary','results':'summary','resultados':'summary'};
      if(nonempty.length===1&&sections[first]) {section=sections[first];headers=null;if(['orders','deals'].includes(section)) signature=true;return;}
      const keys=cells.map(key);
      if(['orders','deals','positions','working'].includes(section)&&keys.some(k=>columnAliases.volume.includes(k))&&keys.some(k=>columnAliases.type.includes(k))) {headers=keys;return;}
      if(headers&&['orders','deals','positions','working'].includes(section)) {
        const raw={};
        FIELDS.forEach(field=>{
          const aliases=columnAliases[field]||[];
          let index=headers.findIndex(k=>aliases.includes(k));
          if(field==='ticket') index=headers.findIndex(k=>(section==='deals'?['deal','negociacao','transacao','ticket']:['orders','working'].includes(section)?['order','ordem','ticket']:['position','posicao','ticket']).includes(k));
          if(field==='orderTicket'&&section!=='deals') index=-1;
          const cell=index<0?null:cells[index];
          if(NUMBERS.has(field)) {
            numberCell(raw,field,field==='volume'&&cell?cell.split('/')[0].trim():cell);
          } else if(['time','openedAt','closedAt'].includes(field)) {
            dateCell(raw,field,cell);
          } else raw[field]=text(cell);
        });
        if(!raw.ticket) {if(cells.some(c=>/(?:\d{4}[.\/-]\d{2}[.\/-]\d{2}|\d{2}[.\/-]\d{2}[.\/-]\d{4})/.test(c))) report.issues.push(issue('ticket_missing','Linha transacional sem ticket.','error'));return;}
        const vi=headers.indexOf('volume'),volume=vi<0?null:cells[vi];
        if(volume&&volume.split('/').length>2) report.issues.push(issue('number_invalid','Volume dividido em mais de dois valores na linha '+rows+'.','error'));
        if(volume&&volume.includes('/')) numberCell(raw,'remainingVolume',volume.split('/')[1].trim());
        if(['orders','working'].includes(section)) raw.orderScope=section==='working'?'active':'historical';
        report[section==='working'?'orders':section].push(raw);return;
      }
      for(let i=0;i<cells.length-1;i++) {
        const name=Object.keys(labels).find(k=>labels[k].includes(key(cells[i])));
        if(!name||!cells[i+1]) continue;
        const value=cells[i+1];
        if(IDENTITY.includes(name)) {
          if(name==='login') {
            const match=value.match(/^([0-9]+)(?:\s*\((.*?)\))?/);
            report.identity.login=match?match[1]:text(value);
            const cur=match&&match[2]&&match[2].match(/\b[A-Z]{3}\b/);if(cur) report.identity.currency=cur[0];
          } else report.identity[name]=text(value);
        } else if(name==='period') {
          report.period.declared=true;
          if(/^(all history|todo o historico|historico completo|todo historico)$/i.test(key(value))) report.coverage.completeHistory=true;
          else {
            const matches=value.match(/(?:\d{4}[.\/-]\d{2}[.\/-]\d{2}|\d{2}[.\/-]\d{2}[.\/-]\d{4})(?:[ T]\d{2}:\d{2}(?::\d{2})?)?/g)||[];
            if(matches.length!==2) report.issues.push(issue('date_invalid','Período do relatório não reconhecido.','error'));
            dateCell(report.period,'from',matches[0]);dateCell(report.period,'to',matches[1]);
          }
        } else if(name==='generatedAt') dateCell(report,'generatedAt',value);
        else numberCell(report.summary,name,value);
        i++;
      }
    });
    const parsedNumbers=parseReportNumbers(numbers.map(c=>c.value),options);
    numbers.forEach((c,i)=>{c.target[c.field]=parsedNumbers.values[i];});
    report.issues.push(...parsedNumbers.issues);
    const requestedOrder=options.dateOrder||'auto',dateEvidence=new Set();
    dates.forEach(c=>{
      const m=c.value.match(/^(\d{2})[.\/-](\d{2})[.\/-]\d{4}/);
      if(m&&+m[1]>12&&+m[2]<=12) dateEvidence.add('dmy');
      if(m&&+m[2]>12&&+m[1]<=12) dateEvidence.add('mdy');
    });
    const dateOrder=requestedOrder==='auto'?(dateEvidence.size===1?[...dateEvidence][0]:null):requestedOrder;
    if(!['auto','dmy','mdy'].includes(requestedOrder)) report.issues.push(issue('date_order_invalid','Ordem de datas não reconhecida.','error'));
    if(requestedOrder==='auto'&&dateEvidence.size>1) report.issues.push(issue('date_order_conflict','O arquivo mistura datas dia/mês e mês/dia. Confira o formato de exportação.','error'));
    const badDates=[],ambiguousDates=[];
    dates.forEach(c=>{
      c.target[c.field]=date(c.value,dateOrder);
      if(c.target[c.field]===null) {
        if(!dateOrder&&date(c.value,'dmy')&&date(c.value,'mdy')) ambiguousDates.push(c.value);
        else badDates.push(c.value);
      }
    });
    if(ambiguousDates.length) report.issues.push(issue('date_order_ambiguous','Confirme dia/mês ou mês/dia: '+[...new Set(ambiguousDates)].slice(0,3).join('; ')+'.','error'));
    if(badDates.length) report.issues.push(issue('date_invalid','Datas inválidas: '+[...new Set(badDates)].slice(0,3).join('; ')+'.','error'));
    if(['dmy','mdy'].includes(requestedOrder)) report.issues.push(issue('date_order_confirmed','Ordem escolhida: '+(requestedOrder==='dmy'?'dia/mês/ano':'mês/dia/ano')+'. Revise: '+dates.filter(c=>c.target[c.field]!==null).slice(0,3).map(c=>c.value+' → '+c.target[c.field]).join('; ')+'.'));
    ['orders','deals','positions'].forEach(k=>{report[k]=report[k].map(normalizedRow);});
    if(rows>MAX_ROWS) report.issues.push(issue('row_limit','Relatório excede o limite de linhas.','error'));
    if(signature&&report.deals.length) report.format='mt5-classic-html-v1';
    else report.issues.push(issue('format_unknown','Não foi reconhecido um extrato MT5 detalhado com negociações.','error'));
    report.issues.push(issue('timezone_unknown','Horários do servidor preservados; fuso não informado pelo arquivo.'));
    if(!report.coverage.completeHistory) report.issues.push(issue('history_partial','Completude do histórico não comprovada; saldo inicial e crescimento não serão inferidos.'));
    return report;
  }
  function reportValidation(report) {
    const errors=[];
    if(!plain(report)||!['mt5-classic-html-v1','mt5-summary-pdf-v1'].includes(report.format)) return ['format_unsupported'];
    if(!plain(report.identity)||!plain(report.period)||!plain(report.summary)||!Array.isArray(report.issues)) return ['report_envelope_invalid'];
    if(!text(report.identity.login)) return ['account_number_required'];
    IDENTITY.forEach(k=>{if(report.identity[k]!=null&&typeof report.identity[k]!=='string') errors.push('identity_invalid');});
    report.issues.forEach(x=>{if(x&&x.severity==='error') errors.push(text(x.code)||'report_error');});
    ['orders','deals','positions'].forEach(k=>{
      if(!Array.isArray(report[k])||report[k].length>MAX_ROWS) {errors.push('report_rows_invalid');return;}
      const seen=new Map();
      report[k].forEach(row=>{
        if(!plain(row)||typeof row.ticket!=='string'||!row.ticket) {errors.push('ticket_missing');return;}
        if(seen.has(row.ticket)&&seen.get(row.ticket)!==fingerprint(row)) errors.push('duplicate_ticket_conflict');
        seen.set(row.ticket,fingerprint(row));
        NUMBERS.forEach(n=>{if(row[n]!=null&&!finite(row[n])) errors.push('report_number_invalid');});
        if(k==='deals'&&!DEAL_TYPES.has(type(row.type))) errors.push('deal_type_unsupported');
        ['time','openedAt','closedAt'].forEach(d=>{if(row[d]!=null&&!date(row[d])) errors.push('report_date_invalid');});
      });
    });
    SUMMARY.forEach(k=>{if(report.summary[k]!=null&&!finite(report.summary[k])) errors.push('summary_number_invalid');});
    ['from','to'].forEach(k=>{if(report.period[k]!=null&&!date(report.period[k])) errors.push('period_invalid');});
    if(report.period.from&&report.period.to&&date(report.period.from)>date(report.period.to)) errors.push('period_reversed');
    return [...new Set(errors)];
  }
  function cleanReport(report) {
    const identity={};IDENTITY.forEach(k=>{identity[k]=text(report.identity[k]);});
    const summary={};SUMMARY.forEach(k=>{if(k in report.summary) summary[k]=numeric(report.summary[k]);});
    if(Array.isArray(report.summary.monthly)) summary.monthly=report.summary.monthly.filter(r=>plain(r)&&/^\d{4}-\d{2}$/.test(r.month)).map(r=>({month:r.month,netProfit:numeric(r.netProfit),growthPct:numeric(r.growthPct),tradeCount:numeric(r.tradeCount)}));
    return {format:report.format,identity,period:{from:date(report.period.from),to:date(report.period.to),declared:report.period.declared===true,timezone:text(report.period.timezone)||'unknown'},generatedAt:date(report.generatedAt),
      orders:report.orders.map(normalizedRow),deals:report.deals.map(normalizedRow),positions:report.positions.map(normalizedRow),summary,
      issues:report.issues.filter(plain).map(x=>issue(text(x.code)||'report_note',text(x.message)||'',x.severity==='error'?'error':'warning')),
      coverage:reportCoverage(report)};
  }
  function accountDescriptor(account) {
    const out={id:text(account.id),name:text(account.name),type:text(account.type)};
    IDENTITY.forEach(k=>{out[k]=text(account[k]??account.identity?.[k]);});return out;
  }
  function previewImport(state,account,report,meta) {
    const result={ok:false,error:null,baseFingerprint:null,account:null,report:null,meta:null,counts:{newOrders:0,newDeals:0,newPositions:0,duplicates:0,conflicts:0},conflicts:[],issues:[],requiresIdentityConfirmation:false,duplicate:false};
    const check=validateState(state);
    if(!check.ok) {result.error=check.errors.join(', ');return result;}
    const reportErrors=reportValidation(report);
    if(reportErrors.length) {result.error=reportErrors.join(', ');return result;}
    if(!plain(account)||typeof account.id!=='string'||!account.id) {result.error='account_required';return result;}
    result.account=accountDescriptor(account);result.report=cleanReport(report);result.baseFingerprint=fingerprint(state);
    result.meta={fileHash:text(meta?.fileHash)||text(meta?.reportHash),fileName:text(meta?.fileName),importedAt:date(meta?.importedAt),coverage:plain(meta?.coverage)?{completeHistory:meta.coverage.completeHistory===true}:null};
    const existing=state.accounts.find(a=>a.id===account.id);
    if(result.report.identity.login&&result.report.identity.server&&state.accounts.some(a=>a.id!==account.id&&identityKey(a.login)===identityKey(result.report.identity.login)&&identityKey(a.server)===identityKey(result.report.identity.server))) {result.error='identity_already_linked';return result;}
    for(const k of IDENTITY) {
      const declared=result.account[k],stored=existing?.[k],incoming=result.report.identity[k];
      if((declared&&incoming&&identityKey(declared)!==identityKey(incoming))||(stored&&incoming&&identityKey(stored)!==identityKey(incoming))||(stored&&declared&&identityKey(stored)!==identityKey(declared))) {result.error='identity_mismatch_'+k;return result;}
      if(!incoming || !(declared||stored)) result.requiresIdentityConfirmation=true;
    }
    result.issues=clone(result.report.issues);
    result.reconciliation=balanceReconciliation(result.report);
    if(result.reconciliation.status==='mismatch') result.issues.push(reconciliationIssue(result.reconciliation));
    ['orders','deals','positions'].forEach(collection=>{
      const old=new Map((existing?.[collection]||[]).map(r=>[r.ticket,r])),seen=new Set();
      result.report[collection].forEach(row=>{
        if(seen.has(row.ticket)) {result.counts.duplicates++;return;}
        seen.add(row.ticket);
        if(!old.has(row.ticket)) result.counts['new'+collection[0].toUpperCase()+collection.slice(1)]++;
        else if(fingerprint(old.get(row.ticket))===fingerprint(row)) result.counts.duplicates++;
        else result.conflicts.push({collection,ticket:row.ticket,before:clone(old.get(row.ticket)),after:clone(row)});
      });
    });
    const sameSnapshot=existing?.summaries.slice().reverse().find(s=>s.format===result.report.format&&fingerprint(s.period)===fingerprint(result.report.period)&&(result.report.period.from&&result.report.period.to||result.report.generatedAt&&s.generatedAt===result.report.generatedAt));
    if(sameSnapshot&&fingerprint(sameSnapshot.values)!==fingerprint(result.report.summary)) result.conflicts.push({collection:'summaries',ticket:sameSnapshot.receiptId,before:clone(sameSnapshot.values),after:clone(result.report.summary)});
    result.counts.conflicts=result.conflicts.length;
    // Canonical report equality is authoritative. File hash alone cannot hide a
    // changed report and is retained solely as user-visible provenance.
    const signature=fingerprint(result.report);
    result.duplicate=result.conflicts.length===0&&result.counts.newOrders===0&&result.counts.newDeals===0&&result.counts.newPositions===0&&!!existing?.summaries.some(s=>s.reportSignature===signature);
    result.ok=true;return result;
  }
  function applyImport(state,preview,options) {
    const fail=error=>({ok:false,state:null,receipt:null,error});
    if(!preview?.ok||preview.baseFingerprint!==fingerprint(state)) return fail('preview_stale_or_invalid');
    const fresh=previewImport(state,preview.account,preview.report,preview.meta);
    if(!fresh.ok) return fail(fresh.error);
    if(fresh.requiresIdentityConfirmation&&options?.confirmIdentity!==true) return fail('identity_confirmation_required');
    if(fresh.conflicts.length&&options?.acceptRevision!==true) return fail('revision_confirmation_required');
    if(fresh.duplicate) return {ok:true,state:clone(state),receipt:null,error:null,duplicate:true};
    const next=clone(state);let account=next.accounts.find(a=>a.id===fresh.account.id);
    if(!account) {account={...fresh.account,orders:[],deals:[],positions:[],summaries:[]};next.accounts.push(account);}
    IDENTITY.forEach(k=>{if(!account[k]) account[k]=fresh.report.identity[k]||fresh.account[k]||null;});
    const id='fx-import-'+(next.receipts.length+1)+'-'+shortHash(fingerprint(fresh.report));
    const receipt={id,accountId:account.id,format:fresh.report.format,importedAt:fresh.meta.importedAt,fileHash:fresh.meta.fileHash,fileName:fresh.meta.fileName,period:clone(fresh.report.period),counts:clone(fresh.counts),issues:clone(fresh.issues),reconciliation:clone(fresh.reconciliation)};
    ['orders','deals','positions'].forEach(collection=>{
      const indexes=new Map(account[collection].map((r,i)=>[r.ticket,i]));
      fresh.report[collection].forEach(row=>{
        if(!indexes.has(row.ticket)) {indexes.set(row.ticket,account[collection].length);account[collection].push(clone(row));}
        else {
          const i=indexes.get(row.ticket);
          if(fingerprint(account[collection][i])!==fingerprint(row)) {
            next.revisions.push({receiptId:id,accountId:account.id,collection,ticket:row.ticket,before:clone(account[collection][i]),after:clone(row)});
            account[collection][i]=clone(row);
          }
        }
      });
    });
    fresh.conflicts.filter(c=>c.collection==='summaries').forEach(c=>next.revisions.push({receiptId:id,accountId:account.id,...clone(c)}));
    // Only normalized facts/signature, never original HTML/PDF bytes.
    account.summaries.push({receiptId:id,format:fresh.report.format,period:clone(fresh.report.period),generatedAt:fresh.report.generatedAt,importedAt:fresh.meta.importedAt,values:clone(fresh.report.summary),coverage:clone(fresh.report.coverage),reconciliation:clone(fresh.reconciliation),reportSignature:fingerprint(fresh.report)});
    next.receipts.push(receipt);
    const checked=validateState(next);if(!checked.ok) return fail(checked.errors.join(', '));
    return {ok:true,state:next,receipt,error:null,duplicate:false};
  }
  function metric(value,availability,unit,reason) {
    return {value:finite(value)?value:null,availability:finite(value)?availability:'unavailable',unit:unit||null,reason:finite(value)?(reason||null):(reason||'Dados suficientes não foram observados.')};
  }
  const trade = row => row.type==='buy'||row.type==='sell';
  const closes = row => trade(row)&&['out','inout','out_by'].includes(row.entry);
  function metricUnit(k,currency) {
    if(['tradeCount','wins','losses','neutral','maxWinStreak','maxLossStreak'].includes(k)) return 'count';
    if(['growthPct','winRate','drawdownPct','tradingActivityPct','maxDepositLoadPct'].includes(k)) return '%';
    if(['profitFactor','sharpe','recoveryFactor'].includes(k)) return 'ratio';
    return currency||null;
  }
  function manualFacts(record) {
    const facts={};
    ['operationId','accountId','periodId','currency','instrument','direction','openedAt','openedAtSource','closedAt','closedAtSource','referenceBalanceType','referenceBalanceProvenance','maxAccountPhaseIntegrity','resultConsolidation'].forEach(k=>{facts[k]=text(record[k]);});
    ['referenceBalance','netResult','defenseCount','maxAccountPhaseReached','maxGridPhaseReached'].forEach(k=>{facts[k]=numeric(record[k]);});
    facts.policyVersion=text(record.policySnapshot?.policyVersion);
    return facts;
  }
  function inPeriod(row,query) {
    const t=row.time||row.closedAt;
    if(!query.from&&!query.to) return true;
    if(!t) return false;
    return (!query.from||t.slice(0,10)>=query.from.slice(0,10))&&(!query.to||t.slice(0,10)<=query.to.slice(0,10));
  }
  function breakdown(rows,field) {
    const groups=new Map();rows.forEach(r=>{const k=r[field]||'unknown';if(!groups.has(k)) groups.set(k,[]);groups.get(k).push(r);});
    return [...groups.entries()].map(([k,list])=>({[field]:k,netProfit:sum(list.map(r=>r.netResult)),tradeCount:list.filter(r=>r.isClose).length,winRate:list.filter(r=>r.isClose).length&&list.filter(r=>r.isClose).every(r=>r.netResult!==null)?100*list.filter(r=>r.isClose&&r.netResult>0).length/list.filter(r=>r.isClose).length:null}));
  }
  function project(state,manualRecords,query) {
    query=query||{};
    const out={source:query.source||'mt5',methodologyVersion:'fx-descriptive-v1',period:{from:date(query.from),to:date(query.to)},account:null,accounts:[],records:[],metrics:{},series:{balance:[],growth:[],drawdown:[],equity:[],load:[],realized:[]},breakdowns:{monthly:[],years:[],symbols:[],directions:[]},issues:[],coverage:{kind:'empty',from:null,to:null,timezone:'unknown',completeHistory:false,partial:false}};
    METRICS.forEach(k=>{out.metrics[k]=metric(null,'unavailable',null);});
    if(!['mt5','manual'].includes(out.source)) {out.issues.push(issue('source_invalid','Selecione uma origem separada.','error'));return out;}
    const validation=validateState(state);
    if(!validation.ok) {out.issues.push(issue('state_invalid',validation.errors.join(', '),'error'));return out;}
    const selected=state.accounts.find(a=>a.id===query.accountId);
    out.account=selected?accountDescriptor(selected):(query.account&&query.account.id===query.accountId?accountDescriptor(query.account):null);
    out.accounts=state.accounts.map(accountDescriptor);
    if(typeof query.accountId!=='string'||!query.accountId.trim()) {out.issues.push(issue('account_required','Selecione uma conta; não há agregação automática entre contas.','error'));return out;}
    let allRows=[],snapshots=[];
    if(out.source==='manual') {
      const originals=Array.isArray(manualRecords)?manualRecords:(Array.isArray(manualRecords?.records)?manualRecords.records:[]);
      allRows=originals.filter(plain).filter(r=>!query.accountId||(query.accountId==='unassigned'?!r.accountId:r.accountId===query.accountId)).map(r=>({id:text(r.operationId),ticket:text(r.operationId),time:date(r.closedAt),openedAt:date(r.openedAt),closedAt:date(r.closedAt),symbol:text(r.instrument),direction:text(r.direction),type:null,entry:'out',volume:null,profit:null,commission:null,swap:null,fee:null,netResult:numeric(r.netResult),currency:text(r.currency),accountId:text(r.accountId),source:'manual',isClose:true,facts:manualFacts(r)}));
      out.coverage.kind=allRows.length?'manual':'empty';
      out.issues.push(issue('manual_context','Somente fatos capturados no fechamento; sem recompor saldo, equity ou contexto pelo cadastro atual.'));
    } else {
      const accounts=query.accountId?(selected?[selected]:[]):state.accounts;
      allRows=accounts.flatMap(a=>a.deals.map(r=>({...clone(r),id:a.id+':'+r.ticket,source:'mt5',currency:a.currency,accountId:a.id,direction:trade(r)?(closes(r)?(r.type==='buy'?'SELL':'BUY'):r.type.toUpperCase()):null,executionDirection:trade(r)?r.type.toUpperCase():null,isClose:closes(r)})));
      snapshots=accounts.flatMap(a=>a.summaries.map(s=>({...s,accountId:a.id,currency:a.currency}))).sort((a,b)=>(b.period.to||b.generatedAt||b.importedAt||'').localeCompare(a.period.to||a.generatedAt||a.importedAt||'')||(b.generatedAt||'').localeCompare(a.generatedAt||'')||(b.importedAt||'').localeCompare(a.importedAt||'')||String(b.receiptId).localeCompare(String(a.receiptId),undefined,{numeric:true}));
      out.coverage.kind=allRows.length?'ledger':snapshots.length?'summary':'empty';
      // A past declaration covers its own bounded interval, never later
      // partial imports. Import time is not evidence of historical coverage.
      out.coverage.completeHistory=accounts.length===1&&snapshots.some(s=>completeSnapshotCoversLedger(s,allRows));
      out.coverage.partial=allRows.length>0&&!out.coverage.completeHistory;
    }
    allRows.sort((a,b)=>(a.time||'').localeCompare(b.time||'')||String(a.ticket).localeCompare(String(b.ticket),undefined,{numeric:true}));
    const rows=allRows.filter(r=>inPeriod(r,query));out.records=rows;
    out.coverage.from=rows.find(r=>r.time)?.time||snapshots[0]?.period.from||null;
    out.coverage.to=[...rows].reverse().find(r=>r.time)?.time||snapshots[0]?.period.to||null;
    const currencies=new Set(rows.map(r=>r.currency));
    const knownIdentity=out.source!=='manual'||rows.every(r=>!!r.accountId);
    const knownCurrency=rows.length>0&&knownIdentity&&currencies.size===1&&!currencies.has(null)&&!currencies.has(undefined);
    const unit=knownCurrency?[...currencies][0]:null;
    const set=(k,v,reason)=>{out.metrics[k]=metric(v,'calculated',metricUnit(k,unit),reason);};
    if(rows.length) {
      const results=rows.filter(r=>out.source==='manual'||trade(r)||CASH_TYPES.has(r.type));
      const closing=rows.filter(r=>r.isClose);
      set('tradeCount',closing.length);
      set('winRate',closing.length&&closing.every(r=>r.netResult!==null)?100*closing.filter(r=>r.netResult>0).length/closing.length:null,out.source==='manual'?'Operações manuais positivas divididas pelas operações manuais com resultado registrado, em %.':'Resultado por deal de saída, parcial, reversão ou Close By; não agrupa uma posição.');
      if(closing.every(r=>r.netResult!==null)) {
        set('wins',closing.filter(r=>r.netResult>0).length);set('losses',closing.filter(r=>r.netResult<0).length);set('neutral',closing.filter(r=>r.netResult===0).length);
        let wins=0,losses=0,maxWins=0,maxLosses=0;
        closing.forEach(r=>{wins=r.netResult>0?wins+1:0;losses=r.netResult<0?losses+1:0;maxWins=Math.max(maxWins,wins);maxLosses=Math.max(maxLosses,losses);});
        set('maxWinStreak',maxWins);set('maxLossStreak',maxLosses);
      }
      if(knownCurrency) {
        set('netProfit',results.length?sum(results.map(r=>r.netResult)):null);
        if(out.source==='mt5') {
          const traded=rows.filter(trade);
          set('grossProfit',traded.length&&traded.every(r=>r.profit!==null)?sum(traded.filter(r=>r.profit>0).map(r=>r.profit)):null);
          set('grossLoss',traded.length&&traded.every(r=>r.profit!==null)?sum(traded.filter(r=>r.profit<0).map(r=>r.profit)):null);
          set('commission',sum(rows.filter(r=>r.type!=='balance').map(r=>CASH_TYPES.has(r.type)&&r.type.startsWith('commission')?sum([r.commission,r.profit]):r.commission)));
          set('swap',sum(rows.filter(r=>r.type!=='balance').map(r=>r.swap)));set('fee',sum(rows.filter(r=>r.type!=='balance').map(r=>r.fee)));
          const flows=rows.filter(r=>r.type==='balance');
          if(flows.every(r=>r.profit!==null)) {set('deposits',sum(flows.filter(r=>r.profit>0).map(r=>r.profit)));set('withdrawals',sum(flows.filter(r=>r.profit<0).map(r=>-r.profit)));}
        } else {
          set('grossProfit',results.every(r=>r.netResult!==null)?sum(results.filter(r=>r.netResult>0).map(r=>r.netResult)):null,'Soma dos resultados líquidos positivos capturados.');
          set('grossLoss',results.every(r=>r.netResult!==null)?sum(results.filter(r=>r.netResult<0).map(r=>r.netResult)):null,'Soma dos resultados líquidos negativos capturados.');
        }
        const gp=out.metrics.grossProfit.value,gl=out.metrics.grossLoss.value,np=out.metrics.netProfit.value;
        if(closing.length&&closing.every(r=>r.netResult!==null)) {
          const values=closing.map(r=>r.netResult),wins=values.filter(n=>n>0),losses=values.filter(n=>n<0);
          set('bestTrade',values.reduce((a,b)=>Math.max(a,b)));set('worstTrade',values.reduce((a,b)=>Math.min(a,b)));set('averageWin',wins.length?sum(wins)/wins.length:null);set('averageLoss',losses.length?sum(losses)/losses.length:null);
        }
        const factorAvailable=gp!==null&&gl!==null&&gl<0;
        set('profitFactor',factorAvailable?gp/Math.abs(gl):null,factorAvailable?(out.source==='mt5'?'Lucro bruto positivo dividido pelo módulo do prejuízo bruto, antes de comissões, taxas e swaps.':'Resultados líquidos positivos divididos pelo módulo dos resultados líquidos negativos das operações manuais.'):(gl===0?'Sem perdas observadas, a razão não possui denominador.':'Lucro e prejuízo não foram integralmente observados.'));
        set('expectedPayoff',np!==null&&closing.length?np/closing.length:null);
        out.breakdowns.symbols=breakdown(results,'symbol');out.breakdowns.directions=breakdown(results,'direction');
        if(out.source==='manual'&&rows.every(r=>r.time&&r.netResult!==null)) {
          let realized=0;out.series.realized=rows.map(r=>({time:r.time,value:(realized=sum([realized,r.netResult])),ticket:r.ticket}));
        }
      } else out.issues.push(knownIdentity?issue('currency_unknown_or_mixed','Moedas ausentes ou diferentes: nenhum total monetário foi calculado.'):issue('identity_unassigned','Registros não conciliados: consulta dos fatos sem agregados monetários ou curvas de conta.'));
      const months=new Map();rows.forEach(r=>{if(!r.time) return;const month=r.time.slice(0,7);if(!months.has(month)) months.set(month,[]);months.get(month).push(r);});
      out.breakdowns.monthly=[...months.entries()].map(([month,list])=>({month,netProfit:knownCurrency?sum(list.filter(r=>out.source==='manual'||trade(r)||CASH_TYPES.has(r.type)).map(r=>r.netResult)):null,growthPct:null,tradeCount:list.filter(r=>r.isClose).length}));
    }
    // A ledger balance path is only derived with explicit complete-history
    // evidence, first funding, one account and every signed component known.
    if(out.source==='mt5'&&out.coverage.completeHistory&&knownCurrency&&new Set(allRows.map(r=>r.accountId)).size===1&&allRows.length&&allRows[0].type==='balance'&&allRows[0].profit>0&&allRows.every(r=>r.time&&r.netResult!==null&&(trade(r)||r.type==='balance'||CASH_TYPES.has(r.type)))) {
      let balance=0,peak=0,growth=1,validGrowth=true,maxDD=0,maxPct=0;const monthFactors=new Map();
      allRows.forEach(r=>{
        const before=balance;balance=sum([balance,r.netResult]);
        const month=r.time.slice(0,7);if(!monthFactors.has(month)) monthFactors.set(month,1);
        if(r.type!=='balance') {
          if(before>0&&balance>0) {const factor=balance/before;growth*=factor;monthFactors.set(month,monthFactors.get(month)*factor);}
          else validGrowth=false;
        }
        peak=Math.max(peak,balance);const dd=peak-balance,pct=peak>0?100*dd/peak:null;
        if(inPeriod(r,query)) {
          out.series.balance.push({time:r.time,value:balance,ticket:r.ticket});
          out.series.drawdown.push({time:r.time,value:pct,ticket:r.ticket});
          if(validGrowth) out.series.growth.push({time:r.time,value:100*(growth-1),ticket:r.ticket});
          maxDD=Math.max(maxDD,dd);maxPct=Math.max(maxPct,pct||0);
        }
      });
      const last=out.series.balance[out.series.balance.length-1];set('balance',last?.value??null);
      set('initialBalance',allRows[0].profit);
      set('drawdownAmount',last?maxDD:null,'Queda observada de balance; inclui lançamentos de caixa, não é drawdown de equity.');set('drawdownPct',last?maxPct:null,'Drawdown de balance desde o pico histórico observado.');
      if(validGrowth) {
        const periods=out.breakdowns.monthly.map(m=>monthFactors.get(m.month));
        // Sub-month filters cannot use a whole-month return.
        let selectedFactor=1,selectedValid=true,current=0;
        allRows.forEach(r=>{const before=current;current=sum([current,r.netResult]);if(inPeriod(r,query)&&r.type!=='balance') {if(before>0&&current>0) selectedFactor*=current/before;else selectedValid=false;}});
        set('growthPct',last&&selectedValid?100*(selectedFactor-1):null,'Crescimento do balance ajustado a depósitos/saques, composto entre fluxos.');
        out.breakdowns.monthly.forEach((m,i)=>{m.growthPct=(!query.from||query.from.slice(0,7)!==m.month||query.from.slice(8,10)==='01')&&(!query.to||query.to.slice(0,7)!==m.month)?100*(periods[i]-1):null;});
        if(!query.from&&!query.to) out.breakdowns.monthly.forEach(m=>{m.growthPct=100*(monthFactors.get(m.month)-1);});
      } else {out.series.growth=[];out.issues.push(issue('growth_nonpositive','Saldo não positivo impede o cálculo da razão de crescimento.'));}
    }
    const matchingSnapshot=snapshots.find(s=>(!query.from||s.period.from===query.from)&&(!query.to||s.period.to===query.to));
    if(matchingSnapshot?.reconciliation?.status==='mismatch') out.issues.push(reconciliationIssue(matchingSnapshot.reconciliation));
    const snapshotCoversLedger=matchingSnapshot&&((matchingSnapshot.period.from&&matchingSnapshot.period.to&&matchingSnapshot.period.from.slice(0,10)<=out.coverage.from?.slice(0,10)&&matchingSnapshot.period.to.slice(0,10)>=out.coverage.to?.slice(0,10))||matchingSnapshot.coverage?.completeHistory&&matchingSnapshot.generatedAt>=out.coverage.to);
    if(matchingSnapshot&&new Set(snapshots.map(s=>s.accountId)).size===1&&(!rows.length||new Set(allRows.map(r=>r.accountId)).size<=1&&snapshotCoversLedger)) {
      // Snapshot indicators are facts for their stated period. They never add
      // trades, fill a price trajectory or override a calculated ledger value.
      METRICS.forEach(k=>{if(out.metrics[k].value===null&&finite(matchingSnapshot.values[k])) out.metrics[k]={...metric(matchingSnapshot.values[k],'imported',metricUnit(k,matchingSnapshot.currency),'Informado no relatório para o período declarado; não recalculado.'),period:clone(matchingSnapshot.period)};});
      if(!rows.length&&Array.isArray(matchingSnapshot.values.monthly)) out.breakdowns.monthly=clone(matchingSnapshot.values.monthly);
    }
    const years=new Map();out.breakdowns.monthly.forEach(m=>{const y=m.month.slice(0,4);if(!years.has(y)) years.set(y,[]);years.get(y).push(m);});
    out.breakdowns.years=[...years.entries()].map(([year,list])=>({year,netProfit:sum(list.map(m=>m.netProfit)),growthPct:list.every(m=>m.growthPct!==null)?100*(list.reduce((n,m)=>n*(1+m.growthPct/100),1)-1):null,tradeCount:sum(list.map(m=>m.tradeCount))}));
    if(out.coverage.partial) out.issues.push(issue('history_partial','Histórico sem cobertura integral comprovada até o último evento: curvas patrimoniais indisponíveis.'));
    out.period={from:date(query.from)||out.coverage.from,to:date(query.to)||out.coverage.to,timezone:out.coverage.timezone};
    out.coverage.lastReceiptId=snapshots[0]?.receiptId||null;
    return out;
  }
  Object.assign(api,{emptyState,validateState,validateReport:reportValidation,parseHTML,parseReportNumbers,previewImport,applyImport,project});
})(window);
