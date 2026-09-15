/* Consolidado FX: local PDF.js text extraction, never a PDF viewer or script host. */
(function(root){
  'use strict';
  const api=root.JPWFXConsolidated=root.JPWFXConsolidated||{};
  const MODULE='src/vendor/pdfjs/pdf.mjs', WORKER='src/vendor/pdfjs/pdf.worker.mjs';
  const scriptBase=typeof document!=='undefined'?document.baseURI:'';
  let generation=0, active=null;
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
    pages.forEach(items=>{
      const rows=[];
      for(const item of items){
        if(!item.str||!item.str.trim())continue;
        const x=item.transform[4],y=item.transform[5];
        let row=rows.find(r=>Math.abs(r.y-y)<2);
        if(!row){row={y,parts:[]};rows.push(row);}
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
    const top=lines.filter(l=>l.y>currencyLabel.row.y+25);
    const identityRows=top.filter(l=>/\b\d{5,}\b/.test(l.text));
    const identityRow=identityRows.length===1?identityRows[0]:null;
    const kindPresent=identityRow&&top.some(l=>Math.abs(l.y-identityRow.y)<=10&&/\b(?:REAL|DEMO)\b/i.test(l.text));
    const login=kindPresent&&identityRow.text.match(/\b(\d{5,})\b/);
    if(!login)throw error('PDF_ACCOUNT_MISSING','O PDF não identifica inequivocamente o número da conta.');
    const brokerRow=top.find(l=>l.y<identityRow.y-5&&l.y>currencyLabel.row.y+25);
    function near(labelInfo,direction,maxDistance){
      if(!labelInfo)return null;
      const {row,x,end}=labelInfo;
      const candidateRows=lines.filter(r=>direction==='above'?r.y>row.y&&r.y-row.y<=maxDistance:r.y<row.y&&row.y-r.y<=maxDistance).sort((a,b)=>Math.abs(a.y-row.y)-Math.abs(b.y-row.y));
      // Numeric labels in adjacent columns can have different baselines. Choose
      // the closest numeric row IN this column, not the closest row on the page.
      for(const candidate of candidateRows){
        const parts=candidate.parts.filter(p=>p.x+p.width>=x-12&&p.x<Math.max(end,x+45));
        const match=parts.map(p=>p.text).join(' ').replace(/\u2212/g,'-').replace(/^([+-])\s+/,'$1').match(/^[+-]?[\d][\d\s,.]*(?:%|\s*\(\d+\))?$/);
        if(match)return number(match[0].replace(/\s*\(\d+\)$/,''));
      }
      return null;
    }
    const currencyLine=lines.filter(l=>l.y>currencyLabel.row.y&&l.y-currencyLabel.row.y<23).sort((a,b)=>a.y-b.y)[0];
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
    const period=options.period||{from:null,to:null};
    if(!period.from||!period.to)issues.push({code:'PERIOD_NOT_REPORTED',severity:'warning',message:'Período não declarado no PDF; confirme a cobertura antes da importação.'});
    return {format:'mt5-summary-pdf-v1',identity:{login:login[1],broker:brokerRow?brokerRow.text:null,currency,server:null},period:{from:period.from||null,to:period.to||null,declared:!!(period.from&&period.to),timezone:'unknown'},generatedAt:null,orders:[],deals:[],positions:[],summary,issues};
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
      const library=await wait(import(assetURL(MODULE,run)));
      if(cancelled())throw abortError();
      const workerUrl=assetURL(WORKER,run);run.worker=new Worker(workerUrl,{type:'module',name:'JPW MT5 PDF local'});
      run.worker.addEventListener('error',()=>run.fail(error('PDF_WORKER_FAILED','O navegador não iniciou o leitor PDF local.')), {once:true});
      run.pdfWorker=new library.PDFWorker({port:run.worker});
      run.task=library.getDocument({data,worker:run.pdfWorker,isEvalSupported:false,enableXfa:false,useWasm:false,useWorkerFetch:false,useSystemFonts:false,disableFontFace:true,disableAutoFetch:true,disableStream:true,disableRange:true,stopAtErrors:true,verbosity:0});
      run.task.onPassword=()=>{run.task.destroy();};
      const pdf=await wait(run.task.promise);
      if(pdf.numPages!==1)throw error('PDF_PROFILE_UNSUPPORTED','Esta versão aceita o resumo MT5 de uma página; use HTML para histórico detalhado.');
      if(cancelled())throw abortError();
      const page=await wait(pdf.getPage(1));const text=await wait(page.getTextContent({disableNormalization:false}));
      if(cancelled())throw abortError();
      if(!text.items.some(x=>x.str&&x.str.trim()))throw error('PDF_NO_TEXT','PDF sem texto extraível; OCR não está disponível.');
      return parseSummary(linesFromPages([text.items]),options);
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
