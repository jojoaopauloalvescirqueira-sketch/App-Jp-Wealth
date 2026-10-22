// Ferramentas: UI efêmera. Nenhum escritor financeiro ou armazenamento.
(function(){
  'use strict';
  const el=id=>document.getElementById(id);
  let view='calendar',valid=null,lastCanonical=null,revision=0,downloadGeneration=0;
  const downloadControllers=new Set();
  const epoch=()=>typeof sessionEpochRead==='function'?sessionEpochRead():null;
  function cancelDownloads(){downloadGeneration++;downloadControllers.forEach(c=>c.abort());downloadControllers.clear();}
  window.JPWNavigation?.subscribe(cancelDownloads);window.addEventListener('pagehide',cancelDownloads);
  function downloadAction(){const controller=new AbortController(),generation=downloadGeneration,base=epoch();downloadControllers.add(controller);
    return {signal:controller.signal,current:()=>!controller.signal.aborted&&generation===downloadGeneration&&base===epoch(),done:()=>downloadControllers.delete(controller)};}

  jpwWorkspaceDraftProviders.set('nocuda-transfer',(reset=false)=>{
    if(reset){invalidate();lastCanonical=null;valid=null;el('nocudaPayload').value='';return [];}
    const text=el('nocudaPayload').value;
    return text?[{label:'NoCuda — parâmetros em conferência',provider:'nocuda-transfer',version:1,context:{route:'tools-nocuda'},baseReference:null,text}]:[];
  });
  window.JPWWorkspaceDrafts.registerRestorer('nocuda-transfer',{
    inspect(item){return {compatible:typeof item.text==='string'&&item.text.length<=16384&&!el('nocudaPayload').value,reason:'Não pode existir outro desenho aberto; código recuperado precisa de nova validação.'};},
    reopen(item){if(typeof closeSettingsModal==='function')closeSettingsModal();if(window.JPWNavigation?.navigate('tools-nocuda')===false)throw new Error('Navegação recusada.');
      el('nocudaPayload').value=item.text;invalidate();status('Parâmetros recuperados, ainda não validados. Confira e valide antes de gerar.');el('nocudaPayload').focus();}
  });
  // The Tools workspace owns visibility; the existing Galton controller owns
  // physics, preferences and session epochs. Never rebuild a mounted board.
  const dialogSelector='dialog[open],[role="dialog"],[aria-modal="true"]';
  const overlaySelector='#settingsOverlay,#modalOverlay,#mvpNotesOverlay,#ecalOverlay,#alladinModalOverlay';
  const isVisible=node=>!node.closest('[hidden],[inert],[aria-hidden="true"]')&&node.getClientRects().length>0&&getComputedStyle(node).visibility!=='hidden';
  function openDialog(){
    return [...document.querySelectorAll(dialogSelector)].find(isVisible)||
      [...document.querySelectorAll(overlaySelector.split(',').map(selector=>selector+'.show').join(','))].find(isVisible)||null;
  }
  function canNavigateToGame(){
    const dialog=openDialog();if(!dialog)return true;
    let notice=dialog.querySelector('[data-minigames-navigation-status]');
    if(!notice){notice=document.createElement('p');notice.dataset.minigamesNavigationStatus='';notice.className='minigames-navigation-status';notice.setAttribute('role','status');dialog.append(notice);}
    notice.textContent='Feche a janela atual antes de abrir um jogo em MiniGames';
    return false;
  }
  let marketEntryPending=false;
  function syncMarketHours(allowMount=false){
    const slot=el('toolsMarketHoursSlot');if(!slot)return;
    if(allowMount)marketEntryPending=true;
    if(view!=='market-hours'||!el('tools').classList.contains('active'))marketEntryPending=false;
    const visible=view==='market-hours'&&el('tools').classList.contains('active')&&!openDialog()&&!document.hidden&&isVisible(slot);
    if(!visible){window.JPWMarketHours?.deactivate();return;}
    // Only accepted navigation may mount. Visibility observers cannot recreate
    // a finalized controller, and async completion must recheck the real host.
    if(marketEntryPending){marketEntryPending=false;window.JPWMarketHours?.mount(slot).then(()=>syncMarketHours()).catch(()=>{});}
    window.JPWMarketHours?.activate();
  }
  function syncMiniGames(allowMount=false){
    const capitalSlot=el('toolsCapitalCurrentsSlot');
    if(capitalSlot){
      const capitalVisible=view==='capital-currents'&&el('tools').classList.contains('active')&&!openDialog()&&!document.hidden&&!capitalSlot.closest('[hidden],[inert]')&&capitalSlot.getClientRects().length>0;
      let capital=capitalSlot.__capitalCurrentsController;
      if(capital?.snapshot().destroyed)capital=null;
      if(capitalVisible&&allowMount&&!capital)capital=window.JPWCapitalCurrents?.mount(capitalSlot);
      if(capitalVisible&&capital&&!capital.snapshot().active)capital.activate();
      else if(!capitalVisible&&capital?.snapshot().active)capital.deactivate();
    }
    const twinsSlot=el('toolsTimeTwinsSlot');
    if(twinsSlot){
      const twinsVisible=view==='time-twins'&&el('tools').classList.contains('active')&&!openDialog()&&!document.hidden&&!twinsSlot.closest('[hidden],[inert]')&&twinsSlot.getClientRects().length>0;
      let twins=twinsSlot.__timeTwinsController;
      if(twins?.snapshot().destroyed)twins=null;
      // Only a newly accepted entry may create an instance. Dialog/visibility
      // observers can reactivate a live instance, never resurrect a disposed one.
      if(twinsVisible&&allowMount&&!twins)twins=window.JPWTimeTwins?.mount(twinsSlot);
      if(twinsVisible&&twins&&!twins.snapshot().active)twins.activate();
      else if(!twinsVisible&&twins?.snapshot().active)twins.deactivate();
    }
    const slot=el('toolsGaltonSlot');if(!slot)return;
    const visible=view==='galton'&&el('tools').classList.contains('active')&&!openDialog()&&!slot.closest('[hidden],[inert]')&&slot.getClientRects().length>0;
    if(visible&&!slot.querySelector('[data-galton-root]')){
      slot.innerHTML=typeof galtonBoardPanelHTML==='function'?galtonBoardPanelHTML():'<p role="alert">Galton Board não pôde ser carregado.</p>';
    }
    const controller=slot.querySelector('[data-galton-root]')?.__galtonController;
    // Browser visibility remains with onVisibility; UI departure always requires
    // explicit Continuar, including when a dialog closes over the same route.
    if(visible&&!document.hidden&&!controller?.active)window.activateGaltonBoard?.();
    else if(!visible&&controller?.active)window.deactivateGaltonBoard?.({resume:false});
  }
  window.JPWNavigation?.subscribe(({current})=>{
    syncMarketHours(current.primary==='tools'&&current.localView?.view==='market-hours');
    syncMiniGames(current.primary==='tools'&&['time-twins','capital-currents'].includes(current.localView?.view));
    if(current.primary!=='tools'||openDialog())return;
    if(current.localView?.view==='market-hours')el('marketHoursTitle').focus({preventScroll:true});
    if(current.localView?.view==='galton')el('minigamesGaltonTitle').focus({preventScroll:true});
    if(current.localView?.view==='time-twins')el('minigamesTimeTwinsTitle').focus({preventScroll:true});
    if(current.localView?.view==='capital-currents')el('minigamesCapitalCurrentsTitle').focus({preventScroll:true});
  });
  function initMiniGames(){
    el('minigamesOpenCapitalCurrents').addEventListener('click',()=>window.JPWNavigation?.navigateLocal('tools','capital-currents'));
    el('minigamesCapitalCurrentsBack').addEventListener('click',()=>{
      if(window.JPWNavigation?.navigate('tools-minigames'))el('minigamesOpenCapitalCurrents').focus({preventScroll:true});
    });
    el('minigamesOpenTimeTwins').addEventListener('click',()=>window.JPWNavigation?.navigateLocal('tools','time-twins'));
    el('minigamesTimeTwinsBack').addEventListener('click',()=>{
      if(window.JPWNavigation?.navigate('tools-minigames'))el('minigamesOpenTimeTwins').focus({preventScroll:true});
    });
    el('minigamesOpenGalton').addEventListener('click',()=>window.JPWNavigation?.navigateLocal('tools','galton'));
    el('minigamesBack').addEventListener('click',()=>{
      if(window.JPWNavigation?.navigate('tools-minigames'))el('minigamesOpenGalton').focus({preventScroll:true});
    });
    // Listen only for dialog/ancestor visibility changes. Galton histogram and
    // canvas updates cannot trigger navigation or repeated activation.
    const containsDialog=node=>node instanceof Element&&(node.matches('dialog,[role="dialog"],[aria-modal="true"],'+overlaySelector)||!!node.querySelector('dialog,[role="dialog"],[aria-modal="true"],'+overlaySelector));
    const observer=new MutationObserver(records=>{
      if(records.some(record=>record.type==='attributes'?containsDialog(record.target):[...record.addedNodes,...record.removedNodes].some(containsDialog))){syncMiniGames();syncMarketHours();}
    });
    document.addEventListener('visibilitychange',()=>{syncMiniGames();syncMarketHours();});
    observer.observe(document.body,{subtree:true,childList:true,attributes:true,attributeFilter:['class','hidden','inert','open','aria-hidden','role','aria-modal','style']});
  }
  function selectView(next){
    if(!['calendar','market-hours','nocuda','leverage','normative','minigames','galton','time-twins','capital-currents'].includes(next))return;
    if(view==='market-hours'&&next!=='market-hours')window.JPWMarketHours?.deactivate();
    if(view==='capital-currents'&&next!=='capital-currents')window.JPWCapitalCurrents?.deactivate(el('toolsCapitalCurrentsSlot'));
    if(view==='time-twins'&&next!=='time-twins')window.JPWTimeTwins?.deactivate(el('toolsTimeTwinsSlot'));
    if(view==='galton'&&next!=='galton')window.deactivateGaltonBoard?.({resume:false});
    if(view==='normative'&&next!=='normative'&&window.JPWNormativeReader)window.JPWNormativeReader.leave();
    view=next;
    document.querySelectorAll('#tools [data-tools-view]').forEach(node=>{
      node.hidden=node.dataset.toolsView!==next;node.inert=node.hidden;
    });
    if(next==='calendar'&&window.JPWEcalUI)window.JPWEcalUI.render();
    if(next==='normative'&&window.JPWNormativeReader)window.JPWNormativeReader.enter();
  }
  function status(message,bad){el('nocudaStatus').textContent=message;el('nocudaStatus').dataset.state=bad?'error':'ok';}
  function invalidate(){cancelDownloads();revision++;valid=null;['nocudaCopy','nocudaSave','nocudaEditable'].forEach(id=>el(id).disabled=true);el('nocudaRestore').hidden=!lastCanonical;}
  function summary(value){
    const items=[['Instrumento',value.symbol],['Período',value.tf%3600===0?(value.tf/3600)+' h':value.tf%60===0?(value.tf/60)+' min':value.tf+' s'],['Origem',value.src+' · '+value.feed],['Linhas',(17+value.before+value.after).toString()],['Passo','0,125'],['Largura assinada',value.d]];
    const nodes=[];items.forEach(([name,text])=>{const box=document.createElement('div'),dt=document.createElement('dt'),dd=document.createElement('dd');dt.textContent=name;dd.textContent=text;box.append(dt,dd);nodes.push(box);});el('nocudaSummary').replaceChildren(...nodes);
    el('nocudaAnchors').replaceChildren(...['a','b','c'].map(key=>{const point=value[key],row=document.createElement('tr');const offset=point.offset,sign=offset<0?'−':'+';[key.toUpperCase()+' · linha '+(key==='c'?'9':'17'),new Date(point.time).toISOString().replace('T',' ').replace('.000Z',''),point.price,'UTC'+sign+String(Math.floor(Math.abs(offset)/60)).padStart(2,'0')+':'+String(Math.abs(offset)%60).padStart(2,'0')].forEach(text=>{const cell=document.createElement('td');cell.textContent=text;row.append(cell);});return row;}));
  }
  function preview(value){
    const svg=el('nocudaPreview'),geo=window.JPWNocudaTransfer.geometry(value),ns='http://www.w3.org/2000/svg';
    const lines=geo.lines.filter(line=>line.visible),prices=lines.flatMap(line=>[line.fromPrice,line.toPrice]);
    if(!prices.length){svg.replaceChildren();return;}
    const lo=Math.min(...prices),hi=Math.max(...prices),range=hi-lo||1,y=price=>238-(price-lo)/range*218;
    const nodes=[];
    lines.forEach(item=>{
      const line=document.createElementNS(ns,'line'),style=item.style;
      line.setAttribute('x1','25');line.setAttribute('x2','805');line.setAttribute('y1',y(item.fromPrice));line.setAttribute('y2',y(item.toPrice));line.setAttribute('stroke',`rgb(${style.r},${style.g},${style.b})`);line.setAttribute('stroke-opacity',1-style.alpha/100);line.setAttribute('stroke-width',style.width);
      if(style.style!=='S')line.setAttribute('stroke-dasharray',style.style==='D'?'7 5':'2 4');nodes.push(line);
      if(item.label){const text=document.createElementNS(ns,'text');text.setAttribute('x','820');text.setAttribute('y',y(item.toPrice)+4);text.textContent=item.label;text.setAttribute('fill','currentColor');text.setAttribute('font-size','11');nodes.push(text);}
    });svg.replaceChildren(...nodes);
  }
  function validate(){
    invalidate();const result=window.JPWNocudaTransfer.parse(el('nocudaPayload').value);
    if(!result.ok){status(result.error.message+(result.error.field?' Campo: '+result.error.field+'.':'')+(lastCanonical?' A prévia abaixo mantém o último código válido.':''),true);return false;}
    valid=result;lastCanonical=result.canonical;el('nocudaRestore').hidden=true;['nocudaCopy','nocudaSave','nocudaEditable'].forEach(id=>el(id).disabled=false);el('nocudaCanonical').value=result.canonical;summary(result.value);preview(result.value);el('nocudaResult').hidden=false;
    status('Código válido. Confira instrumento, período e provedor na plataforma de destino.');return true;
  }
  function download(text,name,type){
    const blob=new Blob([text],{type:type||'text/plain;charset=utf-8'}),url=URL.createObjectURL(blob),link=document.createElement('a');link.href=url;link.download=name;document.body.append(link);link.click();link.remove();setTimeout(()=>URL.revokeObjectURL(url),30000);
  }
  async function generateEditable(value,canonical,options){
    // Always validate at the boundary, including callers of the public helper.
    const checked=window.JPWNocudaTransfer.parse(canonical);
    if(!checked.ok)throw new Error('Parâmetros inválidos.');value=checked.value;
    const values={modeInput:'Manual',generatedSeed:canonical,importText:'',drawingId:value.id,symbolIdentity:'',confirmDifferentFeed:false,exportEnabled:false,beforeSteps:value.before,afterSteps:value.after,extendInput:({N:'Nenhum',R:'Direita',L:'Esquerda',B:'Ambos'})[value.ext]};
    const raw={};['A','B','C'].forEach(key=>{const point=value[key.toLowerCase()];values['time'+key]=point.time;raw['price'+key]=point.price;});
    const hex=(r,g,b)=>'#'+[r,g,b].map(c=>c.toString(16).padStart(2,'0')).join('').toUpperCase();
    const styles={S:'Contínua',D:'Tracejada',P:'Pontilhada'};
    Object.entries({s1:'1',s3:'3',s5:'5',s9:'9',s17:'17',si:'Inner',sx:'Outer'}).forEach(([key,suffix])=>{
      const s=value.styles[key];values['show'+suffix]=!!s.on;values['custom'+suffix]=true;raw['color'+suffix]=hex(s.r,s.g,s.b);values['alpha'+suffix]=s.alpha;values['width'+suffix]=s.width;values['style'+suffix]=styles[s.style];
    });
    const l=value.labels;
    Object.assign(values,{labelMode:({M:'Marcos',A:'Todas as linhas',N:'Nenhum'})[l.mode],labelSize:l.size,labelTransparency:l.alpha,labelPosition:({L:'Início',C:'Centro',R:'Fim',T:'Último candle'})[l.pos],labelVertical:({U:'Acima',O:'Sobre a linha',D:'Abaixo'})[l.vert],labelGap:l.gapPercent,labelOffset:l.offsetBars,showLevel:!!l.showLevel,showPrice:!!l.showPrice,showMax:!!l.showMax,labelUseLineColor:!!l.useLineColor});raw.labelColor=hex(l.r,l.g,l.b);
    const expected=new Set([...Object.keys(values),...Object.keys(raw)]),found=new Set();
    const source=(await window.JPWDownloadAssets.getText('nocuda/Nocuda_Tool.pine',options)).split('\n').map(line=>{
      const match=line.match(/\/\/ NOCUDA_DEFAULT:([A-Za-z0-9_]+)\s*$/);if(!match||!expected.has(match[1]))return line;
      const key=match[1];if(found.has(key))throw new Error('Modelo Pine com marcador duplicado.');
      const literal=Object.hasOwn(raw,key)?raw[key]:JSON.stringify(values[key]);
      const updated=line.replace(/(input\.(?:int|float|price|time|bool|string|text_area|color)\()\s*(?:"(?:[^"\\]|\\.)*"|#[A-Fa-f0-9]{6,8}|true|false|-?\d+(?:\.\d+)?|timestamp\("(?:[^"\\]|\\.)*"\))(?=\s*,)/,(_all,start)=>start+literal);
      if(updated===line&&!line.includes('('+literal+','))throw new Error('Modelo Pine incompatível: '+key);found.add(key);return updated;
    }).join('\n');
    if(found.size!==expected.size||!source.includes('const bool PRECONFIGURED = false // NOCUDA_PRECONFIGURED'))throw new Error('Modelo Pine incompleto. Atualize o aplicativo.');return source.replace('const bool PRECONFIGURED = false // NOCUDA_PRECONFIGURED','const bool PRECONFIGURED = true // NOCUDA_PRECONFIGURED');
  }
  el('nocudaValidate').addEventListener('click',validate);
  el('nocudaPayload').addEventListener('input',()=>{invalidate();status('Rascunho alterado. Valide antes de copiar ou gerar. A prévia mantém o último código válido.');});
  el('nocudaClear').addEventListener('click',()=>{lastCanonical=null;invalidate();el('nocudaResult').hidden=true;el('nocudaCanonical').value='';el('nocudaPayload').value='';el('nocudaFile').value='';status('O desenho fica apenas nesta página durante a sessão.');el('nocudaPayload').focus();});
  el('nocudaRestore').addEventListener('click',()=>{if(lastCanonical){el('nocudaPayload').value=lastCanonical;validate();}});
  el('nocudaExample').addEventListener('click',()=>{el('nocudaPayload').value=window.JPWNocudaTransfer.example();validate();status('Exemplo fictício carregado para demonstração.');});
  el('nocudaFile').addEventListener('change',async event=>{
    invalidate();const token=revision,file=event.target.files[0];if(!file)return;
    if(file.size>16384){status('Arquivo maior que 16 KiB. Abra somente parâmetros Nocuda.',true);event.target.value='';return;}
    try{const text=await file.text();if(token!==revision)return;el('nocudaPayload').value=text;validate();}catch(_error){if(token===revision)status('Não foi possível abrir o arquivo.',true);}finally{event.target.value='';}
  });
  el('nocudaCopy').addEventListener('click',async()=>{
    if(!valid)return;const token=revision;
    try{await navigator.clipboard.writeText(valid.canonical);if(token===revision)status('Parâmetros copiados. Cole no campo de importação do indicador.');}
    catch(_error){if(token!==revision)return;el('nocudaCanonical').focus();el('nocudaCanonical').select();status('Selecione e copie o código validado abaixo com ⌘C ou Ctrl+C.');}
  });
  el('nocudaSave').addEventListener('click',()=>{if(valid)download(valid.canonical,'Nocuda_Parametros.txt');});
  el('nocudaEditable').addEventListener('click',async()=>{if(!valid)return;const token=revision,action=downloadAction(),value=valid;
    try{const source=await generateEditable(value.value,value.canonical,{signal:action.signal});if(!action.current()||token!==revision)return;
      download(source,'Nocuda_Tool_Editavel.pine');status('Pine editável gerado. Abra no Pine Editor, salve e adicione ao gráfico compatível.');
    }catch(error){if(action.current()&&token===revision)status(error.message,true);}finally{action.done();}});
  document.querySelectorAll('[data-nocuda-file]').forEach(link=>link.addEventListener('click',async event=>{
    if(event.button>0||event.ctrlKey||event.metaKey||event.shiftKey||event.altKey)return;
    event.preventDefault();const action=downloadAction(),name=link.dataset.nocudaFile;
    try{const bytes=await window.JPWDownloadAssets.getBytes('nocuda/'+name,{signal:action.signal});if(!action.current())return;
      const descriptor=window.JPW_DOWNLOAD_MANIFEST.resources['nocuda/'+name];download(bytes,descriptor.filename,descriptor.mime);
    }catch(error){if(action.current())status('Download não iniciado: '+error.message,true);}finally{action.done();}
  }));
  function initLeverageDownloads(){
    // Public release metadata and embedded bytes are generated from the same
    // manifest by the official build. The page never reads account data.
    const manifest=window.JPW_LEVERAGE_MANIFEST;

    const set=(name,value)=>document.querySelectorAll('[data-jpw-leverage-meta="'+name+'"]')
      .forEach(node=>{node.textContent=value;});
    const notice=(message,error)=>{const node=el('jpwLeverageDownloadStatus');node.textContent=message;node.dataset.state=error?'error':'ok';};
    const artifactCatalog={C5:{
      nativeKit:{filename:'Kit_Windows_Stoikus_Painel_C5_D1.zip',mime:'application/zip'},
      nativePin:{filename:'root-pin-Painel-C5-D1.json',mime:'application/json'},
      preview:{filename:'Previa_Stoikus_Painel_C5.html',mime:'text/html'}
    },R5:{
      nativeKit:{filename:'Kit_Windows_Stoikus_Janelas_R5.zip',mime:'application/zip'},
      nativePin:{filename:'root-pin-R5.json',mime:'application/json'},
      preview:{filename:'Previa_Stoikus_Janelas_R5.html',mime:'text/html'}
    },R4:{
      nativeKit:{filename:'Kit_Windows_Stoikus_Assinatura_R4.zip',mime:'application/zip'},
      nativePin:{filename:'root-pin-R4.json',mime:'application/json'},
      preview:{filename:'Previa_Stoikus_Interface_R4.html',mime:'text/html'}
    }};
    const artifactTypes=artifactCatalog[manifest?.interfaceRelease?.revision]||artifactCatalog.R5;
    const kinds=['dailySource','source','compiled',...Object.keys(artifactTypes),'installer'];
    const release=manifest&&manifest.interfaceRelease;
    const validRelease=release&&((release.revision==='R4'&&release.candidate==='1.22.3-interface'&&release.archiveVariant==='interface'&&manifest.version==='1.22.3')||
      (release.revision==='C5'&&release.candidate==='1.23.0-interface'&&release.archiveVariant==='painel-C5'&&manifest.version==='1.23.0')||
      (release.revision==='R5'&&release.candidate==='1.23.0-interface'&&release.archiveVariant===''&&manifest.version==='1.23.0'))&&release.state==='SOURCE_ONLY_NATIVE_PENDING'&&
      manifest.downloads?.compiled?.available===false&&
      ['nativeCompilation','nativeRuntime','humanAcceptance','windowsX64'].every(key=>release[key]==='NOT_RUN')&&release.artifacts&&
      Object.keys(release.artifacts).length===3&&Object.keys(artifactTypes).every(key=>Object.hasOwn(release.artifacts,key));
    const validEntry=(entry,kind)=>entry&&entry.available===true&&
      typeof entry.path==='string'&&
      (Object.hasOwn(artifactTypes,kind)?!!validRelease&&entry.path==='downloads/jpw-alavancagem-atual/'+artifactTypes[kind].filename:
        /^downloads\/jpw-alavancagem-atual\/[A-Za-z0-9._-]+\.zip$/.test(entry.path))&&
      entry.filename===entry.path.split('/').pop()&&/^[a-f0-9]{64}$/.test(entry.sha256)&&
      Number.isSafeInteger(entry.bytes)&&entry.bytes>0;
    const installerFilename='Stoikus_Setup_1.0.0-beta.1_win-x64.exe';
    const releasePrefix='https://github.com/jojoaopauloalvescirqueira-sketch/App-Jp-Wealth/releases/download/';
    const validInstaller=entry=>entry&&entry.available===true&&entry.installerVersion==='1.0.0-beta.1'&&
      entry.productVersion===manifest?.version&&entry.platform==='win-x64'&&entry.unsigned===true&&
      entry.filename===installerFilename&&entry.path==='downloads/jpw-alavancagem-atual/'+installerFilename&&
      /^[a-f0-9]{64}$/.test(entry.sha256)&&Number.isSafeInteger(entry.bytes)&&entry.bytes>0&&
      typeof entry.releaseUrl==='string'&&entry.releaseUrl.startsWith(releasePrefix)&&
      /^[A-Za-z0-9._-]+\/Stoikus_Setup_1\.0\.0-beta\.1_win-x64\.exe$/.test(entry.releaseUrl.slice(releasePrefix.length))&&
      ['windowsX64','parallelsArm','browser'].every(stage=>entry.nativeTests?.[stage]==='PASS'&&
        /^docs\/validation\/[A-Za-z0-9_./-]+\.json$/.test(entry.nativeEvidence?.[stage]?.path||'')&&
        !entry.nativeEvidence[stage].path.split('/').some(part=>part==='..'||part==='.')&&
        /^[a-f0-9]{64}$/.test(entry.nativeEvidence[stage].sha256));
    const validManifest=manifest&&manifest.schemaVersion===1&&
      typeof manifest.version==='string'&&/^[0-9]+\.[0-9]+\.[0-9]+$/.test(manifest.version)&&
      manifest.downloads&&manifest.validation;
    if(!validManifest){
      for(const kind of kinds){
        document.querySelectorAll('[data-jpw-leverage-download="'+kind+'"]')
          .forEach(button=>{button.disabled=true;});
      }
      set('source-availability','Fontes não confirmadas');
      set('dailySource-availability','Pacote de uso não confirmado');
      set('native-summary','Validação nativa não informada');
      set('dailySource-status','Metadados de distribuição indisponíveis nesta cópia.');
      set('source-status','Metadados de distribuição indisponíveis nesta cópia.');
      set('compiled-status','Metadados de distribuição indisponíveis nesta cópia.');
      notice('Não foi possível confirmar os arquivos desta versão.',true);
      return;
    }
    set('version',manifest.version);
    set('interface-release',validRelease?'Interface '+release.revision+' · '+release.candidate+' · SOURCE_ONLY · validação nativa pendente':'Interface não confirmada nesta cópia');
    set('source-availability',validEntry(manifest.downloads.source)?'Fontes disponíveis':'Fontes indisponíveis');
    set('dailySource-availability',validEntry(manifest.downloads.dailySource)?'Pacote de uso disponível':'Pacote de uso indisponível nesta cópia');
    const nativeStages=['compilation','terminal'].map(stage=>manifest.validation[stage]?.status);
    set('native-summary',nativeStages.every(state=>state==='passed')?'Evidências nativas registradas':
      manifest.validation.compilation?.status==='passed'&&manifest.validation.terminal?.status==='pending'?'Compilado · execução MT5 pendente':
      nativeStages.some(state=>state==='pending')?'Validação nativa pendente':'Validação nativa não informada');
    set('coverage',typeof manifest.coverage==='string'&&manifest.coverage?manifest.coverage:'Cobertura não informada.');
    for(const stage of ['mathematics','compilation','terminal','clipboard']){
      const item=manifest.validation[stage];
      const state=item&&item.status==='passed'?'Executada':item&&item.status==='pending'?'Pendente':'Não informada';
      const detail=item&&typeof item.detail==='string'&&item.detail?item.detail:'';
      set(stage,state+(detail?' · '+detail:''));
    }
    for(const kind of kinds){
      const isInstaller=kind==='installer',type=isInstaller?{mime:'application/vnd.microsoft.portable-executable'}:artifactTypes[kind]||{mime:'application/zip'};
      const entry=Object.hasOwn(artifactTypes,kind)?(validRelease?release.artifacts[kind]:null):manifest.downloads[kind],buttons=document.querySelectorAll('[data-jpw-leverage-download="'+kind+'"]');
      const disable=value=>buttons.forEach(button=>{button.disabled=value;});
      const resource=window.JPW_DOWNLOAD_MANIFEST?.resources?.['leverage/'+kind];
      const ready=isInstaller?location.protocol!=='file:'&&validInstaller(entry):validEntry(entry,kind)&&!!resource&&resource.mime===type.mime&&
        ['path','filename','sha256','bytes'].every(key=>resource[key]===entry[key]);
      disable(!ready);
      if(isInstaller)buttons.forEach(button=>{button.textContent=ready?'Baixar instalador .exe':'Instalador .exe · indisponível';});
      set(kind+'-sha',ready?entry.sha256:'—');
      if(ready) set(kind+'-status','Disponível · '+entry.filename+' · '+entry.bytes.toLocaleString('pt-BR')+' bytes');
      else if(entry&&entry.available===false&&typeof entry.reason==='string'&&entry.reason)
        set(kind+'-status','Indisponível · '+entry.reason);
      else set(kind+'-status','Arquivo indisponível ou sem integridade confirmada nesta cópia.');
      buttons.forEach(button=>button.addEventListener('click',async()=>{
        if(!ready||button.disabled)return;
        const action=downloadAction();disable(true);notice('Verificando o arquivo antes do download…');
        try{
          let bytes;
          if(isInstaller){
            const response=await fetch(entry.releaseUrl,{signal:action.signal,credentials:'omit',cache:'no-store'});
            if(!response.ok)throw new Error('Arquivo não encontrado neste endereço.');
            const mime=(response.headers?.get('content-type')||'').split(';')[0].trim().toLowerCase();
            if(!['application/octet-stream','application/x-msdownload','application/vnd.microsoft.portable-executable'].includes(mime))
              throw new Error('Tipo de arquivo diferente do esperado.');
            bytes=new Uint8Array(await response.arrayBuffer());
            if(bytes.length!==entry.bytes)throw new Error('Tamanho do pacote diferente do manifesto.');
            if(!crypto.subtle)throw new Error('Verificação criptográfica indisponível neste navegador.');
            const digest=Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256',bytes)),n=>n.toString(16).padStart(2,'0')).join('');
            if(digest!==entry.sha256)throw new Error('Hash do pacote diferente do manifesto.');
          }else bytes=await window.JPWDownloadAssets.getBytes('leverage/'+kind,{signal:action.signal});
          if(!action.current())return;
          const url=URL.createObjectURL(new Blob([bytes],{type:type.mime}));
          const link=document.createElement('a');link.href=url;link.download=entry.filename;document.body.append(link);link.click();link.remove();
          setTimeout(()=>URL.revokeObjectURL(url),30000);
          notice('Arquivo '+entry.filename+' verificado e preparado para download.');
        }catch(error){if(action.current())notice('Download não iniciado: '+error.message,true);}
        finally{action.done();disable(false);}
      }));
    }
  }
  function initGenetrixUI(){
    const region=el('jpwLeveragePage');
    const areas=['overview','install','resources','validation','help'];
    const panels=new Map(areas.map(area=>[area,region.querySelector('[data-genetrix-panel="'+area+'"]')]));
    const tabs=new Map(areas.map(area=>[area,region.querySelector('[data-genetrix-tab="'+area+'"]')]));
    // Exact DOM identities form the allowlist. A URL fragment never becomes
    // a selector, HTML, an external route or a persistent preference.
    const targets=new Map([region,...region.querySelectorAll('[id]')].map(node=>[node.id,node]));
    let active='overview',hashFrame=null,lastResolvedHash=null;
    const complete=areas.every(area=>panels.get(area)&&tabs.get(area));
    function select(area){
      if(!complete||!panels.has(area))return false;
      active=area;
      areas.forEach(key=>{
        const selected=key===area,panel=panels.get(key),tab=tabs.get(key);
        panel.hidden=!selected;panel.inert=!selected;
        tab.setAttribute('aria-selected',String(selected));
        tab.tabIndex=selected?0:-1;
      });
      return true;
    }
    function ensureRoute(){
      const nav=window.JPWNavigation;
      if(!nav||typeof nav.navigate!=='function')return false;
      return nav.current().canonical==='tools-leverage'||nav.navigate('tools-leverage');
    }
    function findTarget(hash){
      if(typeof hash!=='string'||!/^#[A-Za-z][A-Za-z0-9_-]{0,95}$/.test(hash))return null;
      return targets.get(hash.slice(1))||null;
    }
    function reveal(target,{record=false,focus=true,scroll=true}={}){
      if(!complete||!target||!ensureRoute())return false;
      const parent=target.closest('[data-genetrix-panel]');
      const area=parent?parent.dataset.genetrixPanel:target.dataset.genetrixTab||'overview';
      if(!select(area))return false;
      for(let node=target;node&&node!==region;node=node.parentElement){
        if(node.tagName==='DETAILS')node.open=true;
      }
      if(record&&location.hash!=='#'+target.id)history.pushState(null,'','#'+target.id);
      if(focus){
        const focusTarget=target.hasAttribute('data-genetrix-panel')?
          target.querySelector('[data-genetrix-panel-focus],h2,h1')||target:target;
        if(!focusTarget.hasAttribute('tabindex')&&!focusTarget.matches('a[href],button,input,select,textarea,summary'))focusTarget.tabIndex=-1;
        focusTarget.focus({preventScroll:true});
      }
      if(scroll)target.scrollIntoView({block:'start',behavior:'instant'});
      return true;
    }
    function open(area){
      const panel=panels.get(area);
      if(!panel)return false;
      return reveal(panel,{record:true});
    }
    function fromHash(){
      const target=findTarget(location.hash);
      const inGenetrix=window.JPWNavigation?.current().canonical==='tools-leverage';
      if(target){
        const area=target.closest('[data-genetrix-panel]')?.dataset.genetrixPanel||'overview';
        // popstate and hashchange may describe the same transition. Resolving
        // it twice must not steal focus from a control the user just opened.
        if(lastResolvedHash===location.hash&&inGenetrix&&active===area)return;
        if(reveal(target))lastResolvedHash=location.hash;
      }
      // Back can return to the original unfragmented Genetrix overview.
      // An empty fragment elsewhere must never activate Tools on its own.
      else if(!location.hash&&inGenetrix){
        if(lastResolvedHash!==''||active!=='overview')reveal(panels.get('overview'));
        lastResolvedHash='';
      }else lastResolvedHash=null;
    }
    function scheduleHash(){
      if(hashFrame!==null)cancelAnimationFrame(hashFrame);
      hashFrame=requestAnimationFrame(()=>{hashFrame=null;fromHash();});
    }
    if(complete){
      select(active);
      region.addEventListener('click',event=>{
        if(event.button!==0||event.metaKey||event.ctrlKey||event.shiftKey||event.altKey)return;
        const tab=event.target.closest('[data-genetrix-tab]');
        if(tab&&region.contains(tab)){
          const area=tab.dataset.genetrixTab;
          if(select(area)){
            event.preventDefault();
            const hash='#'+panels.get(area).id;
            if(location.hash!==hash)history.pushState(null,'',hash);
          }
          return;
        }
        const action=event.target.closest('[data-genetrix-open]');
        if(action&&region.contains(action)&&panels.has(action.dataset.genetrixOpen)){
          event.preventDefault();open(action.dataset.genetrixOpen);return;
        }
        const link=event.target.closest('a[href^="#"]');
        const target=link&&region.contains(link)?findTarget(link.getAttribute('href')):null;
        if(target){event.preventDefault();reveal(target,{record:true});}
      });
      region.addEventListener('keydown',event=>{
        const tab=event.target.closest('[data-genetrix-tab]');
        if(!tab||!region.contains(tab)||event.altKey||event.ctrlKey||event.metaKey)return;
        const index=areas.indexOf(tab.dataset.genetrixTab);
        const next=event.key==='Home'?0:event.key==='End'?areas.length-1:
          ['ArrowRight','ArrowDown'].includes(event.key)?(index+1)%areas.length:
          ['ArrowLeft','ArrowUp'].includes(event.key)?(index+areas.length-1)%areas.length:null;
        if(next===null)return;
        event.preventDefault();
        tabs.get(areas[next]).click();tabs.get(areas[next]).focus({preventScroll:true});
        tabs.get(areas[next]).scrollIntoView({block:'nearest',inline:'nearest',behavior:'instant'});
      });
      window.addEventListener('hashchange',scheduleHash);
      window.addEventListener('popstate',scheduleHash);
      if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',fromHash,{once:true});
      else scheduleHash();
    }
    return Object.freeze({getView:()=>active,open});
  }
  initMiniGames();
  initLeverageDownloads();
  // Publish the existing Tools facade before resolving an initial deep link.
  // JPWNavigation needs that facade to reveal its outer Tools view.
  const genetrix=initGenetrixUI();
  window.JPWTools=Object.freeze({ui:Object.freeze({selectView,getView:()=>view}),generateEditable,genetrix,minigames:Object.freeze({canNavigate:canNavigateToGame})});selectView(view);
})();
