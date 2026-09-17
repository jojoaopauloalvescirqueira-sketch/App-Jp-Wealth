// Ferramentas: UI efêmera. Nenhum escritor financeiro ou armazenamento.
(function(){
  'use strict';
  const el=id=>document.getElementById(id);
  let view='calendar',valid=null,lastCanonical=null,revision=0;
  function selectView(next){
    if(!['calendar','nocuda'].includes(next))return;
    view=next;
    document.querySelectorAll('#tools [data-tools-view]').forEach(node=>{
      node.hidden=node.dataset.toolsView!==next;node.inert=node.hidden;
    });
    if(next==='calendar'&&window.JPWEcalUI)window.JPWEcalUI.render();
  }
  function status(message,bad){el('nocudaStatus').textContent=message;el('nocudaStatus').dataset.state=bad?'error':'ok';}
  function invalidate(){revision++;valid=null;['nocudaCopy','nocudaSave','nocudaEditable'].forEach(id=>el(id).disabled=true);el('nocudaRestore').hidden=!lastCanonical;}
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
  function pineSource(){
    const encoded=window.JPW_NOCUDA_PINE;
    if(!encoded)throw new Error('O modelo Pine não está disponível neste build. Reabra uma versão completa do aplicativo.');
    return new TextDecoder().decode(Uint8Array.from(atob(encoded),c=>c.charCodeAt(0)));
  }
  function generateEditable(value,canonical){
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
    const source=pineSource().split('\n').map(line=>{
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
  el('nocudaEditable').addEventListener('click',()=>{if(!valid)return;try{download(generateEditable(valid.value,valid.canonical),'Nocuda_Tool_Editavel.pine');status('Pine editável gerado. Abra no Pine Editor, salve e adicione ao gráfico compatível.');}catch(error){status(error.message,true);}});
  // Local-file links are not downloadable in every browser. Use the exact
  // build-pinned bytes already embedded by the official generator.
  if(location.protocol==='file:')document.querySelectorAll('[data-nocuda-file]').forEach(link=>{const data=window.JPW_NOCUDA_FILES&&window.JPW_NOCUDA_FILES[link.dataset.nocudaFile];if(data)link.href='data:'+data.mime+';base64,'+data.base64;});
  window.JPWTools=Object.freeze({ui:Object.freeze({selectView,getView:()=>view}),generateEditable});selectView(view);
})();
