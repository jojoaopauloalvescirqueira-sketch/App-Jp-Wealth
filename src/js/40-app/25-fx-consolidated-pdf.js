/* Consolidado FX: local PDF.js text extraction, never a PDF viewer or script host. */
(function(root){
  'use strict';
  const api=root.JPWFXConsolidated=root.JPWFXConsolidated||{};
  const MODULE='src/vendor/pdfjs/pdf.mjs', WORKER='src/vendor/pdfjs/pdf.worker.mjs';
  const scriptBase=typeof document!=='undefined'?document.baseURI:'';
  let generation=0, active=null, localAssets=null;
  const MAX_PAGES=200, MAX_ITEMS=250000, MAX_TEXT=12*1024*1024;
  function error(code,message){ const e=new Error(message);e.code=code;return e; }
  function abortError(){return error('PDF_CANCELLED','Leitura do PDF cancelada.');}
  function norm(s){return String(s).normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLowerCase().replace(/\s+/g,' ').trim();}
  function number(s){
    const v=String(s).replace(/\u2212/g,'-').replace(/[\s\u00a0]/g,'').replace(/%$/,'');
    if(!/^[+-]?(?:\d{1,3}(?:,\d{3})+|\d+)(?:\.\d+)?$/.test(v)) return null;
    const n=Number(v.replace(/,/g,''));return Number.isFinite(n)?n:null;
  }
  async function release(run){
    if(!run||run.released)return;run.released=true;
    if(run.cancel)run.cancel();
    // Cancel is observable even when the browser refuses to start the worker.
    try{if(run.task){const cleanup=run.task.destroy();cleanup.catch(()=>{});}}catch(_){}
    try{if(run.pdfWorker)run.pdfWorker.destroy();}catch(_){}
    if(run.worker)run.worker.terminate();
    run.urls.forEach(url=>URL.revokeObjectURL(url));run.urls.length=0;
    if(active===run)active=null;
  }
  api.disposePDF=function(){generation++;const run=active;active=null;return release(run);};
  function ensureLocalAssets(){
    if(root.JPW_RUNTIME_ASSETS||root.JP_WEALTH_PORTABLE_BUILD||new URL(scriptBase).protocol!=='file:')return Promise.resolve();
    if(!localAssets)localAssets=new Promise((resolve,reject)=>{
      const script=document.createElement('script');
      script.src=new URL('src/vendor/pdfjs/runtime-assets.js',scriptBase).href;
      script.onload=()=>{
        script.remove();
        if(root.JPW_RUNTIME_ASSETS?.[MODULE]&&root.JPW_RUNTIME_ASSETS?.[WORKER])resolve();
        else {localAssets=null;reject(error('PDF_ASSET_MISSING','O leitor PDF local está incompleto. Regenere a versão do aplicativo.'));}
      };
      script.onerror=()=>{script.remove();localAssets=null;reject(error('PDF_ASSET_MISSING','Leitor PDF local ausente. Abra a versão completa do aplicativo ou o portátil atualizado.'));};
      document.head.appendChild(script);
    });
    return localAssets;
  }
  function assetURL(path,run){
    const encoded=root.JPW_RUNTIME_ASSETS&&root.JPW_RUNTIME_ASSETS[path];
    if(encoded){
      // file:// has an opaque origin: Chromium rejects ESM blob:null workers.
      // An embedded data: module worker is supported without fetching any URL.
      if(path===WORKER)return 'data:text/javascript;base64,'+encoded;
      const bytes=Uint8Array.from(atob(encoded),c=>c.charCodeAt(0));
      const url=URL.createObjectURL(new Blob([bytes],{type:'text/javascript'}));run.urls.push(url);return url;
    }
    if(root.JP_WEALTH_PORTABLE_BUILD)throw error('PDF_ASSET_MISSING','O portátil não contém o leitor PDF local.');
    const url=new URL(path,scriptBase);
    if(url.origin!==new URL(scriptBase).origin)throw error('PDF_ASSET_ORIGIN','Recurso PDF fora da origem local.');
    return url.href;
  }
  function linesFromPages(pages){
    const lines=[];
    pages.forEach((items,page)=>{
      const rows=[];
      const ordered=items.filter(item=>item.str&&item.str.trim()).sort((a,b)=>b.transform[5]-a.transform[5]||a.transform[4]-b.transform[4]);
      for(const item of ordered){
        const x=item.transform[4],y=item.transform[5];
        let row=rows.at(-1);if(row&&Math.abs(row.y-y)>=2)row=null;
        if(!row){row={y,page,parts:[]};rows.push(row);}
        row.parts.push({x,width:item.width,text:item.str.trim()});
      }
      rows.sort((a,b)=>b.y-a.y).forEach(r=>{r.parts.sort((a,b)=>a.x-b.x);r.text=r.parts.map(p=>p.text).join(' ');lines.push(r);});
    });return lines;
  }
  function parseSummary(lines,options){
    const aliases={currency:['currency','moeda'],grossProfit:['gross profit','lucro bruto'],grossLoss:['gross loss','perda bruta'],netProfit:['total'],commission:['commissions','comissoes'],swap:['swaps'],balance:['balance','saldo'],equity:['equity','capital liquido'],growthPct:['growth','crescimento'],drawdownPct:['drawdown','rebaixamento'],deposits:['deposits','depositos'],withdrawals:['withdrawals','retiradas'],sharpe:['sharp ratio','sharpe ratio','indice de sharpe'],profitFactor:['profit factor','fator de lucro'],recoveryFactor:['recovery factor','fator de recuperacao']};
    function label(key){
      const found=[];
      for(const row of lines)for(let i=0;i<row.parts.length;i++)for(let len=1;len<=3&&i+len<=row.parts.length;len++){
        const parts=row.parts.slice(i,i+len),text=norm(parts.map(p=>p.text).join(' '));
        if(aliases[key].includes(text))found.push({row,x:parts[0].x,end:parts.at(-1).x+parts.at(-1).width});
      }
      return found;
    }
    const currencyLabel=label('currency')[0], profits=label('grossProfit'),losses=label('grossLoss');
    if(!currencyLabel||profits.length!==1||losses.length!==1||!lines.some(l=>/\bsummary\b|\bresumo\b/i.test(l.text))||!label('balance').length||!label('equity').length)throw error('PDF_PROFILE_UNSUPPORTED','PDF não reconhecido como resumo textual MT5. Exporte o relatório detalhado em HTML.');
    const top=lines.filter(l=>l.page===currencyLabel.row.page&&l.y>currencyLabel.row.y+25);
    const identityRows=top.filter(l=>/\b\d{5,}\b/.test(l.text));
    const identityRow=identityRows.length===1?identityRows[0]:null;
    const kindPresent=identityRow&&top.some(l=>Math.abs(l.y-identityRow.y)<=10&&/\b(?:REAL|DEMO)\b/i.test(l.text));
    const login=kindPresent&&identityRow.text.match(/\b(\d{5,})\b/);
    if(!login)throw error('PDF_ACCOUNT_MISSING','O PDF não identifica inequivocamente o número da conta.');
    const brokerRow=top.find(l=>l.y<identityRow.y-5&&l.y>currencyLabel.row.y+25);
    function near(labelInfo,direction,maxDistance){
      if(!labelInfo)return null;
      const {row,x,end}=labelInfo;
      const candidateRows=lines.filter(r=>r.page===row.page&&(direction==='above'?r.y>row.y&&r.y-row.y<=maxDistance:r.y<row.y&&row.y-r.y<=maxDistance)).sort((a,b)=>Math.abs(a.y-row.y)-Math.abs(b.y-row.y));
      // Numeric labels in adjacent columns can have different baselines. Choose
      // the closest numeric row IN this column, not the closest row on the page.
      for(const candidate of candidateRows){
        const parts=candidate.parts.filter(p=>p.x+p.width>=x-12&&p.x<Math.max(end,x+45));
        const match=parts.map(p=>p.text).join(' ').replace(/\u2212/g,'-').replace(/^([+-])\s+/,'$1').match(/^[+-]?[\d][\d\s,.]*(?:%|\s*\(\d+\))?$/);
        if(match)return match[0].replace(/\s*\(\d+\)$/,'');
      }
      return null;
    }
    const currencyLine=lines.filter(l=>l.page===currencyLabel.row.page&&l.y>currencyLabel.row.y&&l.y-currencyLabel.row.y<23).sort((a,b)=>a.y-b.y)[0];
    const currencyPart=currencyLine&&currencyLine.parts.find(p=>p.x>=currencyLabel.x-3&&p.x<currencyLabel.end+5&&/^[A-Z]{3}$/.test(p.text));
    const currency=currencyPart?currencyPart.text:null;
    if(!currency)throw error('PDF_CURRENCY_MISSING','Moeda ausente no resumo PDF.');
    const summary={};
    const rules={grossProfit:['below',23],grossLoss:['below',23],netProfit:['above',25],commission:['above',23],swap:['above',23],balance:['above',23],equity:['above',23],growthPct:['above',23],drawdownPct:['above',23],deposits:['above',23],withdrawals:['above',23],sharpe:['below',40],profitFactor:['below',40],recoveryFactor:['below',40]};
    const issues=[{code:'PDF_SUMMARY_ONLY',severity:'warning',message:'Resumo importado sem tickets ou série histórica de execuções.'},{code:'SERVER_NOT_REPORTED',severity:'warning',message:'Servidor não informado pelo PDF; origem não autenticada.'}];
    for(const [key,[direction,distance]] of Object.entries(rules)){
      const locations=label(key);
      // Repeated graph labels are not automatically interchangeable with summary totals.
      summary[key]=locations.length===1?near(locations[0],direction,distance):null;
    }
    if(summary.balance===null||summary.equity===null)throw error('PDF_SUMMARY_INCOMPLETE','Saldo/equity não foram extraídos com segurança; use HTML detalhado.');
    const fields=Object.keys(summary),parsed=api.parseReportNumbers?api.parseReportNumbers(fields.map(key=>summary[key]),options):{values:fields.map(key=>summary[key]===null?null:number(summary[key])),issues:[]};
    fields.forEach((key,index)=>{summary[key]=parsed.values[index];});issues.push(...parsed.issues);
    const period=options.period||{from:null,to:null};
    if(!period.from||!period.to)issues.push({code:'PERIOD_NOT_REPORTED',severity:'warning',message:'Período não declarado no PDF; confirme a cobertura antes da importação.'});
    return {format:'mt5-summary-pdf-v1',identity:{login:login[1],broker:brokerRow?brokerRow.text:null,currency,server:null},period:{from:period.from||null,to:period.to||null,declared:!!(period.from&&period.to),timezone:'unknown'},generatedAt:null,orders:[],deals:[],positions:[],summary,issues};
  }
  function parseDetailed(lines,options){
    const clean=s=>norm(s).replace(/[:./_()%–—-]+/g,' ').replace(/\s+/g,' ').trim();
    const sections={orders:'orders',ordens:'orders',deals:'deals',negociacoes:'deals',transacoes:'deals',positions:'positions',posicoes:'positions','open positions':'positions','posicoes abertas':'positions','working orders':'working','ordens ativas':'working',summary:'summary',resumo:'summary',results:'summary',resultados:'summary'};
    const aliases={time:['time','horario','hora','data hora'],openedAt:['open time','horario de abertura'],closedAt:['close time','horario de fechamento'],ticket:['deal','negociacao','transacao','order','ordem','position','posicao','ticket'],order:['order','ordem'],symbol:['symbol','simbolo','ativo'],type:['type','tipo'],direction:['direction','direcao','entrada'],volume:['volume'],price:['price','preco'],sl:['s l','sl'],tp:['t p','tp'],commission:['commission','comissao'],fee:['fee','taxa'],swap:['swap'],profit:['profit','lucro','lucro prejuizo'],balance:['balance','saldo'],state:['state','estado','status'],comment:['comment','comentario'],magic:['magic']};
    const recognized=lines.some(row=>['deals','negociacoes','transacoes'].includes(clean(row.text)));
    if(!recognized)return null;
    if(typeof api.parseHTML!=='function')throw error('PDF_PARSER_MISSING','O leitor de tabelas MT5 não foi carregado.');
    const escape=s=>String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
    const html=[],metadataRows=[],identity=new Map(),facts=new Map();
    let section=null,columns=null,lastPage=-1,recordCount=0;
    const metadata=/\b(Account|Conta|Company|Empresa|Broker|Corretora|Deposit Currency|Currency|Moeda de dep[oó]sito|Moeda|Server|Servidor|Period|Per[ií]odo|Report Date|Date|Data|Total Net Profit|Net Profit|Lucro L[ií]quido Total|Lucro L[ií]quido|Gross Profit|Lucro Bruto|Gross Loss|Perda Bruta|Balance|Saldo|Equity|Capital L[ií]quido|Commission|Commissions|Comiss[aã]o|Comiss[oõ]es|Swap|Swaps|Fee|Fees|Taxas|Deposits|Dep[oó]sitos|Withdrawals|Saques|Profit Factor|Fator de Lucro|Sharpe Ratio|Growth|Crescimento|Total Trades|Total de Negocia[cç][oõ]es|Margin|Margem|Free Margin|Margem Livre):\s*/gi;
    const identityNames={account:'login',conta:'login',company:'broker',empresa:'broker',broker:'broker',corretora:'broker','deposit currency':'currency',currency:'currency',moeda:'currency','moeda de deposito':'currency',server:'server',servidor:'server'};
    for(const row of lines){
      if(row.page!==lastPage){columns=null;lastPage=row.page;}
      const name=clean(row.text);
      if(sections[name]){section=sections[name];columns=null;html.push('<tr><td>'+escape(row.text)+'</td></tr>');continue;}
      const headerKeys=row.parts.map(part=>clean(part.text));
      const isHeader=headerKeys.some(k=>aliases.volume.includes(k))&&headerKeys.some(k=>aliases.type.includes(k));
      if(isHeader){
        if(!section||section==='summary'||headerKeys.some(k=>!Object.values(aliases).some(a=>a.includes(k))))throw error('PDF_TABLE_LAYOUT','Cabeçalho de tabela PDF não reconhecido. Use HTML ou um PDF com colunas completas.');
        if(!headerKeys.some(k=>(section==='deals'?['deal','negociacao','transacao','ticket']:section==='positions'?['position','posicao','ticket']:['order','ordem','ticket']).includes(k)))throw error('PDF_TABLE_LAYOUT','Tabela PDF sem coluna de ticket inequívoca.');
        columns=row.parts;html.push('<tr>'+columns.map(p=>'<th>'+escape(p.text)+'</th>').join('')+'</tr>');continue;
      }
      // Identity and totals are labelled facts. Repeated page headers must agree;
      // never let the last page silently replace the account from the first.
      const matches=Array.from(row.text.matchAll(metadata));
      if(matches.length&&(!columns||section==='summary')){
        const cells=[];
        matches.forEach((match,index)=>{
          const value=row.text.slice(match.index+match[0].length,matches[index+1]?.index??row.text.length).trim();
          const id=identityNames[clean(match[1])];
          if(id){
            const canonical=id==='login'?(value.match(/^(\d+)(?:\s*\(|\s*$)/)||[])[1]:value;
            if(!canonical)throw error('PDF_ACCOUNT_MISSING','Número da conta ausente ou ambíguo no PDF.');
            if(identity.has(id)&&identity.get(id)!==canonical)throw error('PDF_IDENTITY_CONFLICT','As páginas do PDF identificam contas ou moedas diferentes.');
            identity.set(id,canonical);
            if(id==='login'){
              const currencies=value.match(/\b[A-Z]{3}\b/g)||[];
              if(currencies.length>1)throw error('PDF_IDENTITY_CONFLICT','Moeda ambígua na identificação da conta.');
              if(currencies.length){
                if(identity.has('currency')&&identity.get('currency')!==currencies[0])throw error('PDF_IDENTITY_CONFLICT','Moedas divergentes na identificação da conta.');
                identity.set('currency',currencies[0]);
              }
            }
          }
          const factKey=id||clean(match[1]);
          if(!id&&facts.has(factKey)&&facts.get(factKey)!==value)throw error('PDF_FACT_CONFLICT','O PDF apresenta valores divergentes para o mesmo campo. Revise o relatório antes de importar.');
          facts.set(factKey,value);cells.push(match[1]+':',value);
        });
        metadataRows.push('<tr>'+cells.map(s=>'<td>'+escape(s)+'</td>').join('')+'</tr>');continue;
      }
      if(!section||section==='summary')continue;
      if(/^(?:page|pagina)\s+\d+(?:\s+(?:of|de)\s+\d+)?$/i.test(name))continue;
      if(!columns){
        if(/^(?:trade history report|relatorio de historico|metatrader 5)$/.test(name))continue;
        if(/\d/.test(row.text))throw error('PDF_TABLE_HEADER_MISSING','Página com transações sem cabeçalho de colunas. Exporte o PDF com os cabeçalhos repetidos.');
        continue;
      }
      const cells=columns.map(()=>[]);
      for(const part of row.parts){
        // Supported tables have ordered, separate text columns. A cell may have
        // several PDF glyph runs; their original left-to-right text is retained.
        const index=columns.findLastIndex((column,i)=>part.x>=(i===0?column.x-4:(columns[i-1].x+columns[i-1].width+column.x)/2));
        if(index<0)throw error('PDF_TABLE_LAYOUT','Texto fora das colunas reconhecidas do PDF.');
        cells[index].push(part.text);
      }
      const values=cells.map(parts=>parts.join(' '));
      const ticketColumn=columns.findIndex(column=>(section==='deals'?['deal','negociacao','transacao','ticket']:section==='positions'?['position','posicao','ticket']:['order','ordem','ticket']).includes(clean(column.text)));
      if(!/^\d+$/.test(values[ticketColumn]||''))throw error('PDF_TABLE_ROW','Uma linha do PDF não possui ticket legível; nenhum dado foi importado.');
      if(++recordCount>50000)throw error('PDF_ROW_LIMIT','PDF excede o limite de transações.');
      html.push('<tr>'+values.map(s=>'<td>'+escape(s)+'</td>').join('')+'</tr>');
    }
    if(!identity.has('login'))throw error('PDF_ACCOUNT_MISSING','O PDF não identifica inequivocamente o número da conta.');
    if(!identity.has('currency'))throw error('PDF_CURRENCY_MISSING','Moeda ausente no PDF detalhado; use HTML ou informe-a no relatório de origem.');
    const report=api.parseHTML('<table>'+metadataRows.join('')+html.join('')+'</table>',options);
    if(!report.deals.length)throw error('PDF_TABLE_EMPTY','Nenhuma negociação foi extraída com segurança do PDF.');
    // Keep the public v1 PDF envelope. The warning distinguishes textual tables
    // from summaries; the HTML parser is only a shared normalizer, not provenance.
    report.format='mt5-summary-pdf-v1';
    report.coverage={completeHistory:false,timezone:'unknown'};
    report.issues.push({code:'PDF_TEXT_TABLES',severity:'warning',message:'Tabelas textuais do PDF extraídas por coluna. Revise os tickets e os valores; a completude do histórico não é presumida.'});
    return report;
  }
  api.parsePDF=async function(bytes,options){
    options=options||{};
    const token=++generation,previous=active;active=null;
    await release(previous);
    if(token!==generation)throw abortError();
    const run={urls:[],task:null,worker:null,pdfWorker:null,released:false};active=run;
    const stop=new Promise((resolve,reject)=>{run.cancel=()=>reject(abortError());run.fail=reject;});
    stop.catch(()=>{});
    const wait=p=>Promise.race([p,stop]);
    const timeout=setTimeout(()=>run.fail(error('PDF_TIMEOUT','A leitura excedeu 60 segundos e foi interrompida.')),60000);
    const signal=options.signal;
    const cancelled=()=>signal&&signal.aborted||token!==generation||run.released;
    const onAbort=()=>{if(active===run)api.disposePDF();};
    if(signal)signal.addEventListener('abort',onAbort,{once:true});
    try{
      if(cancelled())throw abortError();
      if(!(bytes instanceof ArrayBuffer)&&!ArrayBuffer.isView(bytes))throw error('PDF_INPUT','Escolha um arquivo PDF local.');
      const data=bytes instanceof ArrayBuffer?new Uint8Array(bytes.slice(0)):new Uint8Array(bytes.buffer.slice(bytes.byteOffset,bytes.byteOffset+bytes.byteLength));
      if(data.length>32*1024*1024)throw error('PDF_SIZE_LIMIT','PDF excede 32 MiB; utilize um relatório menor.');
      if(String.fromCharCode(...data.slice(0,5))!=='%PDF-')throw error('PDF_INPUT','Assinatura PDF inválida.');
      await wait(ensureLocalAssets());
      if(cancelled())throw abortError();
      const library=await wait(import(assetURL(MODULE,run)));
      if(cancelled())throw abortError();
      const workerUrl=assetURL(WORKER,run);run.worker=new Worker(workerUrl,{type:'module',name:'JPW MT5 PDF local'});
      run.worker.addEventListener('error',()=>run.fail(error('PDF_WORKER_FAILED','O navegador não iniciou o leitor PDF local.')), {once:true});
      run.pdfWorker=new library.PDFWorker({port:run.worker});
      run.task=library.getDocument({data,worker:run.pdfWorker,isEvalSupported:false,enableXfa:false,useWasm:false,useWorkerFetch:false,useSystemFonts:false,disableFontFace:true,disableAutoFetch:true,disableStream:true,disableRange:true,stopAtErrors:true,verbosity:0});
      run.task.onPassword=()=>{run.task.destroy();};
      const pdf=await wait(run.task.promise);
      if(pdf.numPages>MAX_PAGES)throw error('PDF_PAGE_LIMIT','PDF excede 200 páginas; exporte um período menor.');
      const pages=[];let itemCount=0,textLength=0;
      for(let index=1;index<=pdf.numPages;index++){
        if(cancelled())throw abortError();
        const page=await wait(pdf.getPage(index));const text=await wait(page.getTextContent({disableNormalization:false}));
        if(cancelled())throw abortError();
        itemCount+=text.items.length;textLength+=text.items.reduce((sum,item)=>sum+(item.str?.length||0),0);
        if(itemCount>MAX_ITEMS||textLength>MAX_TEXT)throw error('PDF_TEXT_LIMIT','O texto do PDF excede o limite local; exporte um período menor.');
        if(!text.items.some(x=>x.str&&x.str.trim()))throw error('PDF_NO_TEXT','PDF contém página sem texto extraível; OCR não está disponível.');
        pages.push(text.items);page.cleanup();
      }
      const lines=linesFromPages(pages);
      return parseDetailed(lines,options)||parseSummary(lines,options);
    }catch(e){
      if(cancelled())throw abortError();
      if(e&&e.code)throw e;
      throw error('PDF_READ_FAILED','Não foi possível ler este PDF com segurança. Use o HTML detalhado; PDFs protegidos/digitalizados não são aceitos.');
    }finally{
      clearTimeout(timeout);
      if(signal)signal.removeEventListener('abort',onAbort);
      await release(run);
    }
  };
})(window);
