/* Original V11 documentary reader. Session UI only; no account/consent writer. */
(function(root){
  'use strict';
  const META=Object.freeze({id:'estatuto-v11',version:'V11.0',title:'Estatuto JP Wealth V11.0',path:'docs/normative/Estatuto_JP_WEALTH_UNIFICADO.pdf',filename:'Estatuto_JP_Wealth_V11.pdf',bytes:1499074,pages:125,sha256:'2dab6166bb8513cd9beb7fe39c574971af086ebae66683d99c0e6fac69eb6769'});
  const MODULE='src/vendor/pdfjs/pdf.mjs',WORKER='src/vendor/pdfjs/pdf.worker.mjs';
  const base=document.baseURI,byId=id=>document.getElementById(id);
  const panel=byId('jpwNormativePage');
  if(!panel)return;
  const ui={};
  ['Status','Integrity','Viewport','PageHost','Page','PageTotal','ZoomLabel','Prev','Next','ZoomOut','ZoomIn','Fit','Rotate','Search','Find','SearchPrev','SearchNext','SearchStatus','Thumbnails','ThumbList','ThumbToggle','Copy','Download','Original','Fullscreen','Retry'].forEach(key=>ui[key]=byId('nr'+key));
  if(Object.values(ui).some(node=>!node))return;
  let current=null,epoch=0,scriptLoads=new Map(),resizeTimer=null,expanded=false,expandFocus=null;
  const session={page:1,zoom:'fit',scale:1,rotation:0,thumbs:false};
  const norm=value=>String(value).normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLocaleLowerCase('pt-BR').replace(/\s+/g,' ');
  const fault=(code,message)=>Object.assign(new Error(message),{code});
  const alive=run=>current===run&&!run.released&&run.epoch===epoch;
  function status(message,error=false){ui.Status.textContent=message;ui.Status.dataset.state=error?'error':'ok';}
  function controls(){
    const ready=!!(current&&current.pdf&&current.verified&&!current.released);
    const originalReady=!!(current&&current.verified&&current.originalURL&&!current.released);
    ['Prev','Next','ZoomOut','ZoomIn','Fit','Rotate','Find','SearchPrev','SearchNext','ThumbToggle','Copy','Download','Fullscreen'].forEach(key=>ui[key].disabled=!ready);
    ui.Page.disabled=!ready;ui.Search.disabled=!ready;
    ui.Prev.disabled=!ready||session.page<=1;ui.Next.disabled=!ready||session.page>=META.pages;
    ui.SearchPrev.disabled=!ready||!current.matches.length;ui.SearchNext.disabled=ui.SearchPrev.disabled;
    ui.Download.disabled=!originalReady;
    ui.Original.setAttribute('aria-disabled',String(!originalReady));
    if(!originalReady)ui.Original.removeAttribute('href');
  }
  function busy(value){panel.setAttribute('aria-busy',String(value));}
  function loadClassic(path,present){
    if(present())return Promise.resolve();
    if(root.JP_WEALTH_PORTABLE_BUILD)return Promise.reject(fault('LOCAL_ASSET_MISSING','Esta cópia portátil não contém todos os recursos de leitura.'));
    if(!scriptLoads.has(path))scriptLoads.set(path,new Promise((resolve,reject)=>{
      const script=document.createElement('script');let timer;
      const finish=error=>{clearTimeout(timer);script.remove();if(error){scriptLoads.delete(path);reject(error);}else resolve();};
      script.src=new URL(path,base).href;
      script.onload=()=>finish(present()?null:fault('LOCAL_ASSET_MISSING','O recurso local de leitura está incompleto.'));
      script.onerror=()=>finish(fault('LOCAL_ASSET_MISSING','Recurso local ausente. Reabra uma versão completa do aplicativo.'));
      timer=setTimeout(()=>finish(fault('LOCAL_ASSET_TIMEOUT','O recurso local não respondeu. Tente novamente.')),15000);
      document.head.appendChild(script);
    }));
    return scriptLoads.get(path);
  }
  async function documentBytes(run){
    if(location.protocol==='file:'||root.JP_WEALTH_PORTABLE_BUILD){
      await loadClassic('src/vendor/normative/statute-payload.js',()=>!!root.JPW_NORMATIVE_STATUTE);
      if(!alive(run))throw fault('CANCELLED','Leitura cancelada.');
      const value=root.JPW_NORMATIVE_STATUTE;
      if(!value||value.id!==META.id||value.version!==META.version||value.path!==META.path||value.mime!=='application/pdf'||value.bytes!==META.bytes||value.sha256!==META.sha256||typeof value.base64!=='string'||value.base64.length>2100000)
        throw fault('DOCUMENT_IDENTITY','O documento incorporado não corresponde ao Estatuto V11 desta versão.');
      try{return Uint8Array.from(atob(value.base64),char=>char.charCodeAt(0));}
      catch(_error){throw fault('DOCUMENT_ENCODING','O documento incorporado está incompleto.');}
    }
    const response=await fetch(new URL(META.path,base),{signal:run.abort.signal,credentials:'same-origin'});
    if(!response.ok)throw fault('DOCUMENT_MISSING','O PDF original não está disponível nesta cópia.');
    return new Uint8Array(await response.arrayBuffer());
  }
  async function verify(bytes){
    if(bytes.length!==META.bytes||String.fromCharCode(...bytes.slice(0,5))!=='%PDF-')throw fault('DOCUMENT_SIZE','O tamanho ou o formato do documento difere do Estatuto V11 original.');
    if(!root.crypto||!root.crypto.subtle)throw fault('CRYPTO_UNAVAILABLE','Este navegador não permite confirmar a integridade do documento. Abra o aplicativo no endereço local seguro.');
    const digest=Array.from(new Uint8Array(await root.crypto.subtle.digest('SHA-256',bytes)),value=>value.toString(16).padStart(2,'0')).join('');
    if(digest!==META.sha256)throw fault('DOCUMENT_HASH','A integridade do documento não foi confirmada. A leitura foi bloqueada.');
  }
  function assetURL(path,run){
    const encoded=root.JPW_RUNTIME_ASSETS&&root.JPW_RUNTIME_ASSETS[path];
    if(encoded){
      if(path===WORKER)return 'data:text/javascript;base64,'+encoded;
      const url=URL.createObjectURL(new Blob([Uint8Array.from(atob(encoded),char=>char.charCodeAt(0))],{type:'text/javascript'}));run.urls.push(url);return url;
    }
    if(root.JP_WEALTH_PORTABLE_BUILD||location.protocol==='file:')throw fault('LOCAL_ASSET_MISSING','O leitor PDF local está incompleto nesta cópia.');
    return new URL(path,base).href;
  }
  function release(run){
    if(!run||run.released)return;run.released=true;run.searchEpoch++;run.renderEpoch++;
    run.abort.abort();run.cancel&&run.cancel();clearTimeout(run.timeout);run.observer&&run.observer.disconnect();
    try{run.renderTask&&run.renderTask.cancel();}catch(_error){}
    try{run.textLayer&&run.textLayer.cancel();}catch(_error){}
    try{run.task&&run.task.destroy().catch(()=>{});}catch(_error){}
    try{run.pdfWorker&&run.pdfWorker.destroy();}catch(_error){}
    run.worker&&run.worker.terminate();
    run.urls.forEach(url=>URL.revokeObjectURL(url));run.urls.length=0;run.texts.clear();
  }
  function fail(run,error){
    if(!alive(run)||error.code==='CANCELLED'||error.name==='AbortError')return;
    release(run);current=null;busy(false);ui.PageHost.replaceChildren();ui.ThumbList.replaceChildren();
    if(run.verified&&run.bytes){
      const url=URL.createObjectURL(new Blob([run.bytes],{type:'application/pdf'}));
      current={epoch,verified:true,bytes:run.bytes,originalURL:url,urls:[url],released:false,pdf:null,abort:new AbortController(),texts:new Map(),matches:[],matchIndex:-1,searchEpoch:0,renderEpoch:0};
      ui.Original.href=url;ui.Original.removeAttribute('download');
      ui.Integrity.textContent='Original V11 verificado · leitor indisponível';ui.Integrity.dataset.state='verified';
    }else {ui.Integrity.textContent='Integridade não confirmada';ui.Integrity.dataset.state='error';}
    status(typeof error.code==='string'?error.message:'O leitor local não pôde ser iniciado. Abra o original ou tente novamente.',true);controls();
  }
  async function textFor(run,page){
    if(!run.texts.has(page))run.texts.set(page,(async()=>{
      const pdfPage=await run.pdf.getPage(page),content=await pdfPage.getTextContent({includeMarkedContent:true});
      const strings=content.items.filter(item=>typeof item.str==='string').map(item=>item.str);
      const tokens=[];let offset=0;
      strings.forEach(value=>{const normalized=norm(value);tokens.push({start:offset,end:offset+normalized.length});offset+=normalized.length+1;});
      return {plain:strings.join(' '),normalized:strings.map(norm).join(' '),tokens};
    })());
    return run.texts.get(page);
  }
  function applyHighlights(run){
    if(!alive(run)||!run.textLayer)return;
    const match=run.matches[run.matchIndex],divs=run.textLayer.textDivs||[];
    divs.forEach(node=>node.classList.remove('nr-found'));
    if(!match||match.page!==session.page)return;
    match.items.forEach(index=>{if(divs[index])divs[index].classList.add('nr-found');});
    const first=divs[match.items[0]];
    if(first)first.scrollIntoView({block:'center',inline:'nearest',behavior:'instant'});
  }
  async function renderPage(run){
    if(!alive(run)||!run.pdf)return;
    const token=++run.renderEpoch,pageNumber=session.page;
    try{run.renderTask&&run.renderTask.cancel();}catch(_error){}
    try{run.textLayer&&run.textLayer.cancel();}catch(_error){}
    run.textLayer=null;busy(true);status('Carregando página '+pageNumber+' de '+META.pages+'…');
    ui.Page.value=String(pageNumber);ui.PageTotal.textContent=String(META.pages);controls();
    try{
      const page=await run.pdf.getPage(pageNumber);
      if(!alive(run)||token!==run.renderEpoch)return;
      const unscaled=page.getViewport({scale:1,rotation:session.rotation});
      const available=Math.max(120,ui.Viewport.clientWidth-32);
      const scale=session.zoom==='fit'?available/unscaled.width:session.scale;
      const viewport=page.getViewport({scale,rotation:session.rotation});
      // Bound the bitmap separately from CSS zoom, including HiDPI mobiles.
      const pixelLimit=ui.Viewport.clientWidth<600?4000000:8000000;
      const dpr=Math.min(root.devicePixelRatio||1,2,Math.sqrt(pixelLimit/(viewport.width*viewport.height)));
      const wrapper=document.createElement('div'),canvas=document.createElement('canvas'),layer=document.createElement('div');
      wrapper.className='nr-page';wrapper.setAttribute('aria-label','Página '+pageNumber);wrapper.style.width=viewport.width+'px';wrapper.style.height=viewport.height+'px';
      wrapper.style.setProperty('--scale-factor',String(scale));wrapper.style.setProperty('--total-scale-factor',String(scale));
      canvas.width=Math.max(1,Math.floor(viewport.width*dpr));canvas.height=Math.max(1,Math.floor(viewport.height*dpr));canvas.style.width=viewport.width+'px';canvas.style.height=viewport.height+'px';canvas.setAttribute('aria-hidden','true');
      layer.className='textLayer';wrapper.append(canvas,layer);ui.PageHost.replaceChildren(wrapper);ui.Viewport.scrollTop=0;
      const context=canvas.getContext('2d',{alpha:false});
      if(!context)throw fault('CANVAS_UNAVAILABLE','Este navegador não conseguiu desenhar a página.');
      run.renderTask=page.render({canvas,canvasContext:context,viewport,transform:dpr===1?undefined:[dpr,0,0,dpr,0,0],annotationMode:run.library.AnnotationMode.DISABLE});
      await run.renderTask.promise;
      if(!alive(run)||token!==run.renderEpoch)return;
      run.textLayer=new run.library.TextLayer({textContentSource:page.streamTextContent({includeMarkedContent:true}),container:layer,viewport});
      await run.textLayer.render();
      if(!alive(run)||token!==run.renderEpoch)return;
      run.renderTask=null;run.scale=scale;run.pageRendered=pageNumber;
      ui.ZoomLabel.textContent=Math.round(scale*100)+'%';busy(false);status('Página '+pageNumber+' de '+META.pages+' · original V11 verificado');
      ui.ThumbList.querySelectorAll('button').forEach(node=>node.setAttribute('aria-current',node.dataset.page===String(pageNumber)?'page':'false'));
      applyHighlights(run);
      // Only neighbouring page proxies are warmed; no 125 full-size canvases.
      [pageNumber-1,pageNumber+1].filter(value=>value>=1&&value<=META.pages).forEach(value=>run.pdf.getPage(value).catch(()=>{}));
    }catch(error){
      if(!alive(run)||token!==run.renderEpoch||error.name==='RenderingCancelledException')return;
      busy(false);ui.PageHost.replaceChildren();status('Não foi possível renderizar a página '+pageNumber+'. Tente novamente ou abra o original.',true);
    }
  }
  function goToPage(value){
    const page=Number(value);
    if(!Number.isInteger(page)||page<1||page>META.pages){ui.Page.value=String(session.page);status('Informe uma página entre 1 e '+META.pages+'.',true);return false;}
    session.page=page;if(current&&current.pdf)renderPage(current);return true;
  }
  function zoom(factor){if(!current||!current.pdf)return;session.zoom='custom';session.scale=Math.max(.25,Math.min(4,(current.scale||session.scale)*factor));renderPage(current);}
  async function runSearch(){
    const run=current;if(!run||!run.pdf)return;
    const query=norm(ui.Search.value.trim()),token=++run.searchEpoch;run.query=query;run.matches=[];run.matchIndex=-1;controls();applyHighlights(run);
    if(!query){ui.SearchStatus.textContent='Digite uma palavra ou expressão.';return;}
    let limited=false;
    try{
      for(let page=1;page<=META.pages;page++){
        if(!alive(run)||token!==run.searchEpoch)return;
        ui.SearchStatus.textContent='Buscando na página '+page+' de '+META.pages+'…';
        const text=await textFor(run,page);
        if(!alive(run)||token!==run.searchEpoch)return;
        let offset=text.normalized.indexOf(query);
        while(offset!==-1){
          const items=text.tokens.map((item,index)=>item.end>offset&&item.start<offset+query.length?index:-1).filter(index=>index>=0);
          run.matches.push({page,offset,items});
          if(run.matches.length>=1000){limited=true;break;}
          offset=text.normalized.indexOf(query,offset+query.length);
        }
        if(limited)break;
      }
      if(!alive(run)||token!==run.searchEpoch)return;
      run.matchIndex=run.matches.length?0:-1;run.limited=limited;controls();
      if(run.matches.length)showMatch(0);
      else ui.SearchStatus.textContent='Nenhum resultado no texto do documento.';
    }catch(error){if(alive(run)&&token===run.searchEpoch)ui.SearchStatus.textContent='A busca não pôde ser concluída. Tente novamente.';}
  }
  function showMatch(delta){
    const run=current;if(!run||!run.matches.length)return;
    run.matchIndex=(run.matchIndex+delta+run.matches.length)%run.matches.length;
    const match=run.matches[run.matchIndex];ui.SearchStatus.textContent='Resultado '+(run.matchIndex+1)+' de '+run.matches.length+(run.limited?' · limite de 1.000 resultados':'')+' · página '+match.page;
    if(session.page!==match.page)goToPage(match.page);else applyHighlights(run);
  }
  async function copyText(){
    const run=current;if(!run||!run.pdf)return;
    try{
      const selection=root.getSelection(),selected=selection&&selection.toString().trim()&&ui.PageHost.contains(selection.anchorNode)&&ui.PageHost.contains(selection.focusNode)?selection.toString():'';
      const text=selected||(await textFor(run,session.page)).plain;
      if(!alive(run))return;
      if(!text.trim())throw fault('TEXT_EMPTY','Esta página não contém texto selecionável.');
      if(!navigator.clipboard||!navigator.clipboard.writeText)throw fault('CLIPBOARD_UNAVAILABLE','Cópia automática indisponível.');
      await navigator.clipboard.writeText(text);if(alive(run))status(selected?'Trecho selecionado copiado.':'Texto da página '+session.page+' copiado.');
    }catch(error){
      if(!alive(run))return;
      const layer=ui.PageHost.querySelector('.textLayer');
      if(layer){const range=document.createRange();range.selectNodeContents(layer);const selection=root.getSelection();selection.removeAllRanges();selection.addRange(range);status('Texto selecionado. Use ⌘C ou Ctrl+C para copiar.');}
      else status(error.message||'Não foi possível copiar o texto.',true);
    }
  }
  function thumbnails(run){
    if(!alive(run)||!run.pdf)return;
    ui.Thumbnails.hidden=!session.thumbs;ui.Thumbnails.inert=!session.thumbs;ui.ThumbToggle.setAttribute('aria-expanded',String(session.thumbs));
    if(!session.thumbs){run.observer&&run.observer.disconnect();return;}
    if(!ui.ThumbList.children.length){
      const nodes=[];for(let page=1;page<=META.pages;page++){const button=document.createElement('button'),label=document.createElement('span');button.type='button';button.dataset.page=String(page);button.setAttribute('aria-label','Ir para página '+page);label.textContent=String(page);button.append(label);button.addEventListener('click',()=>goToPage(page));nodes.push(button);}ui.ThumbList.replaceChildren(...nodes);
    }
    const queue=[];let running=0;
    const pump=()=>{
      if(!alive(run)||!session.thumbs)return;
      while(running<2&&queue.length){
        const node=queue.shift();running++;
        (async()=>{
          try{
            const page=await run.pdf.getPage(Number(node.dataset.page));if(!alive(run))return;
            const baseView=page.getViewport({scale:1}),viewport=page.getViewport({scale:90/baseView.width});const canvas=document.createElement('canvas');canvas.width=Math.ceil(viewport.width);canvas.height=Math.ceil(viewport.height);canvas.setAttribute('aria-hidden','true');
            await page.render({canvas,canvasContext:canvas.getContext('2d'),viewport,annotationMode:run.library.AnnotationMode.DISABLE}).promise;
            if(alive(run)){node.prepend(canvas);node.dataset.rendered='true';}
          }catch(error){if(alive(run)){node.dataset.rendered='error';node.title='Miniatura indisponível; a página continua acessível.';}}
          finally{running--;pump();}
        })();
      }
    };
    if(!run.observer){run.thumbPump=pump;run.observer=new IntersectionObserver(entries=>entries.forEach(entry=>{
      if(!entry.isIntersecting||entry.target.dataset.queued||entry.target.dataset.rendered)return;
      entry.target.dataset.queued='true';queue.push(entry.target);pump();
    }),{root:ui.Thumbnails,rootMargin:'120px'});}
    ui.ThumbList.querySelectorAll('button').forEach(node=>{node.setAttribute('aria-current',node.dataset.page===String(session.page)?'page':'false');run.observer.observe(node);});
    run.thumbPump();
  }
  async function setExpanded(value){
    if(value===expanded)return;expanded=value;panel.classList.toggle('nr-expanded',value);ui.Fullscreen.setAttribute('aria-pressed',String(value));ui.Fullscreen.textContent=value?'Sair da tela cheia':'Tela cheia';
    if(value){expandFocus=document.activeElement;try{if(panel.requestFullscreen)await panel.requestFullscreen();}catch(_error){/* The bounded panel expansion remains available. */}ui.Viewport.focus({preventScroll:true});}
    else {try{if(document.fullscreenElement===panel)await document.exitFullscreen();}catch(_error){}if(expandFocus&&panel.contains(expandFocus)&&!panel.hidden)expandFocus.focus({preventScroll:true});}
    if(current&&session.zoom==='fit')renderPage(current);
  }
  function leave(){epoch++;const run=current;current=null;release(run);clearTimeout(resizeTimer);busy(false);if(expanded)setExpanded(false);ui.PageHost.replaceChildren();ui.ThumbList.replaceChildren();ui.SearchStatus.textContent='';controls();}
  async function enter(){
    if(panel.hidden)return;
    if(current&&!current.released)return;
    const run={epoch:++epoch,abort:new AbortController(),urls:[],texts:new Map(),verified:false,pdf:null,released:false,searchEpoch:0,renderEpoch:0,matches:[],matchIndex:-1,scale:1};current=run;
    run.cancelled=new Promise((_resolve,reject)=>run.cancel=()=>reject(fault('CANCELLED','Leitura cancelada.')));run.cancelled.catch(()=>{});
    const wait=promise=>Promise.race([promise,run.cancelled]);
    busy(true);ui.Integrity.textContent='Confirmando o original V11…';ui.Integrity.dataset.state='pending';status('Abrindo o Estatuto JP Wealth V11.0…');controls();
    run.timeout=setTimeout(()=>fail(run,fault('DOCUMENT_TIMEOUT','A abertura excedeu 45 segundos. Tente novamente.')),45000);
    try{
      const bytes=await wait(documentBytes(run));await wait(verify(bytes));if(!alive(run))return;
      run.bytes=bytes;run.verified=true;
      if(location.protocol==='file:'&&!root.JPW_RUNTIME_ASSETS)await wait(loadClassic('src/vendor/pdfjs/runtime-assets.js',()=>!!(root.JPW_RUNTIME_ASSETS&&root.JPW_RUNTIME_ASSETS[MODULE]&&root.JPW_RUNTIME_ASSETS[WORKER])));
      if(!alive(run))return;
      const library=await wait(import(assetURL(MODULE,run)));if(!alive(run))return;run.library=library;
      run.worker=new Worker(assetURL(WORKER,run),{type:'module',name:'JPW Estatuto V11 local'});
      run.worker.addEventListener('error',()=>fail(run,fault('WORKER_FAILED','O navegador não iniciou o leitor PDF local. Tente novamente.')),{once:true});
      run.pdfWorker=new library.PDFWorker({port:run.worker});
      run.task=library.getDocument({data:bytes.slice(),worker:run.pdfWorker,isEvalSupported:false,enableXfa:false,useWasm:false,useWorkerFetch:false,useSystemFonts:false,disableFontFace:false,disableAutoFetch:true,disableRange:true,disableStream:true,stopAtErrors:true,verbosity:0});
      run.task.onPassword=()=>fail(run,fault('DOCUMENT_PASSWORD','O documento desta cópia está protegido e não corresponde ao original esperado.'));
      run.pdf=await wait(run.task.promise);if(!alive(run))return;
      if(run.pdf.numPages!==META.pages)throw fault('DOCUMENT_PAGES','A quantidade de páginas difere do Estatuto V11 original.');
      clearTimeout(run.timeout);
      const original=URL.createObjectURL(new Blob([bytes],{type:'application/pdf'}));run.urls.push(original);run.originalURL=original;ui.Original.href=original;ui.Original.removeAttribute('download');
      ui.Integrity.textContent='Original V11 verificado · 125 páginas';ui.Integrity.dataset.state='verified';ui.Integrity.title='SHA-256: '+META.sha256;
      controls();thumbnails(run);await renderPage(run);
    }catch(error){fail(run,error);}
  }
  ui.Prev.addEventListener('click',()=>goToPage(session.page-1));ui.Next.addEventListener('click',()=>goToPage(session.page+1));
  ui.Page.addEventListener('keydown',event=>{if(event.key==='Enter'){event.preventDefault();goToPage(ui.Page.value);}});
  ui.Page.addEventListener('change',()=>goToPage(ui.Page.value));
  ui.ZoomOut.addEventListener('click',()=>zoom(1/1.2));ui.ZoomIn.addEventListener('click',()=>zoom(1.2));
  ui.Fit.addEventListener('click',()=>{session.zoom='fit';if(current)renderPage(current);});ui.Rotate.addEventListener('click',()=>{session.rotation=(session.rotation+90)%360;if(current)renderPage(current);});
  ui.Find.addEventListener('click',runSearch);ui.SearchPrev.addEventListener('click',()=>showMatch(-1));ui.SearchNext.addEventListener('click',()=>showMatch(1));
  ui.Search.addEventListener('keydown',event=>{
    if(event.key==='Enter'){event.preventDefault();if(current&&current.query===norm(ui.Search.value.trim())&&current.matches.length)showMatch(event.shiftKey?-1:1);else {if(current)current.query=norm(ui.Search.value.trim());runSearch();}}
    if(event.key==='Escape'){event.preventDefault();event.stopPropagation();if(current){current.searchEpoch++;current.matches=[];current.matchIndex=-1;applyHighlights(current);}ui.SearchStatus.textContent='Busca cancelada.';controls();}
  });
  ui.ThumbToggle.addEventListener('click',()=>{session.thumbs=!session.thumbs;if(current)thumbnails(current);if(current&&session.zoom==='fit')renderPage(current);});
  ui.Copy.addEventListener('click',copyText);
  ui.Download.addEventListener('click',()=>{if(!current||!current.verified||!current.originalURL)return;const link=document.createElement('a');link.href=current.originalURL;link.download=META.filename;document.body.appendChild(link);link.click();link.remove();status('Original V11 verificado preparado para download.');});
  ui.Original.addEventListener('click',event=>{if(!current||!current.verified||!current.originalURL){event.preventDefault();status('Confirme a integridade do original antes de abri-lo.',true);}});
  ui.Fullscreen.addEventListener('click',()=>setExpanded(!expanded));ui.Retry.addEventListener('click',()=>{if(current&&current.pdf)renderPage(current);else {leave();enter();}});
  panel.addEventListener('keydown',event=>{
    if(event.key==='Escape'&&expanded){event.preventDefault();setExpanded(false);return;}
    if(event.key==='Tab'&&expanded){
      const nodes=Array.from(panel.querySelectorAll('button:not(:disabled),input:not(:disabled),a[href],[tabindex="0"]')).filter(node=>!node.closest('[hidden]'));
      const first=nodes[0],last=nodes[nodes.length-1];if(event.shiftKey&&document.activeElement===first){event.preventDefault();last.focus();}else if(!event.shiftKey&&document.activeElement===last){event.preventDefault();first.focus();}return;
    }
    if((event.ctrlKey||event.metaKey)&&event.key.toLowerCase()==='f'){event.preventDefault();ui.Search.focus();ui.Search.select();return;}
    if(event.target.matches('input,textarea,select')||!ui.Viewport.contains(event.target))return;
    if(event.ctrlKey||event.metaKey){if(['+','='].includes(event.key)){event.preventDefault();zoom(1.2);}else if(event.key==='-'){event.preventDefault();zoom(1/1.2);}return;}
    const next=event.key==='PageDown'?session.page+1:event.key==='PageUp'?session.page-1:event.key==='Home'?1:event.key==='End'?META.pages:null;
    if(next!==null){event.preventDefault();goToPage(Math.max(1,Math.min(META.pages,next)));}
  });
  document.addEventListener('fullscreenchange',()=>{if(expanded&&document.fullscreenElement!==panel)setExpanded(false);});
  const resize=new ResizeObserver(()=>{if(!current||!current.pdf||session.zoom!=='fit')return;clearTimeout(resizeTimer);resizeTimer=setTimeout(()=>{if(current&&!panel.hidden)renderPage(current);},150);});resize.observe(ui.Viewport);
  // Hiding the outer Tools module bypasses local selectView in some routes.
  // Observe both ancestors so every navigation exit releases the worker.
  const hiddenObserver=new MutationObserver(()=>{if(panel.hidden||panel.closest('[hidden]')||(byId('tools')&&getComputedStyle(byId('tools')).display==='none'))leave();});
  hiddenObserver.observe(panel,{attributes:true,attributeFilter:['hidden']});const tools=byId('tools');if(tools)hiddenObserver.observe(tools,{attributes:true,attributeFilter:['hidden','style','class']});
  root.JPWNormativeReader=Object.freeze({enter,leave,refreshLayout:()=>{if(current)renderPage(current);},snapshot:()=>Object.freeze({documentId:META.id,version:META.version,verified:!!(current&&current.verified&&!current.released),page:session.page,rotation:session.rotation,renderedPage:current&&current.pageRendered||null,matches:current?current.matches.length:0,active:!!current})});
  controls();
  if(root.JPWTools&&root.JPWTools.ui.getView()==='normative')enter();
})(window);
