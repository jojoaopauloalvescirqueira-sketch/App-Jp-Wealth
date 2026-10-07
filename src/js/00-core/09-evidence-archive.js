// Local original evidence archive. Financial facts remain in S/localStorage.
// IndexedDB owns bytes; only explicit import confirmation or reassociation writes.
// ZIP SHA-256 verifies integrity, not authorship or statutory compliance.
(function(root){
  'use strict';
  const DB='jpwealth_evidence_v1', STORE='originals', VERSION=1;
  const LIMITS=Object.freeze({file:32*1024*1024,zip:144*1024*1024,total:128*1024*1024,entries:201,manifest:2*1024*1024});
  const HASH=/^[a-f0-9]{64}$/, object=v=>v!==null&&typeof v==='object'&&!Array.isArray(v);
  let last={status:'ABSENT',reason:'Nenhum arquivo de evidências conferido nesta sessão.',at:null}, busy=false;
  const result=(status,reason,extra={})=>Object.assign({ok:status==='CONFIRMED',status,reason,at:new Date().toISOString()},extra);
  function publish(value){
    last={...value};
    try{root.dispatchEvent(new CustomEvent('jpw-evidence-status',{detail:{...last}}));}catch(error){}
    return value;
  }
  const refusal=(reason,extra)=>publish(result('REFUSED',reason,extra));
  async function digest(bytes){
    if(!root.crypto?.subtle)throw Error('SHA-256 local indisponível. Use um endereço seguro ou navegador compatível.');
    return Array.from(new Uint8Array(await root.crypto.subtle.digest('SHA-256',bytes)),v=>v.toString(16).padStart(2,'0')).join('');
  }
  function name(value){
    if(typeof value!=='string'||!value.trim()||value.length>255||/[\u0000-\u001f\u007f/\\]/.test(value))throw Error('Nome de original inválido.');
    return value;
  }
  function kind(fileName,bytes){
    const ext=fileName.split('.').pop().toLowerCase();
    if(ext==='pdf'&&String.fromCharCode(...bytes.subarray(0,5))==='%PDF-')return 'pdf';
    if((ext==='html'||ext==='htm')&&bytes.length){
      const prefix=new TextDecoder((bytes[0]===255&&bytes[1]===254)?'utf-16le':(bytes[0]===254&&bytes[1]===255)?'utf-16be':'utf-8').decode(bytes.subarray(0,8192));
      if(/<(?:!doctype\s+html|html|head|body|table)\b/i.test(prefix))return 'html';
    }
    throw Error('Somente PDF ou HTML original identificado é aceito. O conteúdo não será executado.');
  }
  async function readOriginal(file,expectedHash){
    if(!file||typeof file.arrayBuffer!=='function'||!Number.isSafeInteger(file.size)||file.size<=0||file.size>LIMITS.file)throw Error('Original vazio ou acima de 32 MiB.');
    const fileName=name(file.name), bytes=new Uint8Array(await file.arrayBuffer());
    if(bytes.length!==file.size)throw Error('O tamanho do original mudou durante a leitura.');
    const fileHash=await digest(bytes);
    if(expectedHash&&(!HASH.test(expectedHash)||expectedHash!==fileHash))throw Error('SHA-256 divergente. Este arquivo não corresponde ao comprovante.');
    return {fileHash,fileName,kind:kind(fileName,bytes),size:bytes.length,bytes};
  }
  function open(){
    return new Promise((resolve,reject)=>{
      if(!root.indexedDB)return reject(Error('IndexedDB indisponível; original não preservado.'));
      let req,settled=false;
      try{req=root.indexedDB.open(DB,VERSION);}catch(error){return reject(error);}
      req.onupgradeneeded=()=>{
        const db=req.result;if(!db.objectStoreNames.contains(STORE))db.createObjectStore(STORE,{keyPath:'fileHash'});
      };
      req.onblocked=()=>{settled=true;reject(Error('Arquivo de evidências ocupado por outra versão. Feche a outra aba.'));};
      req.onerror=()=>{settled=true;reject(req.error||Error('Não foi possível abrir o arquivo de evidências.'));};
      req.onsuccess=()=>{
        const db=req.result;if(settled){db.close();return;}settled=true;
        if(!db.objectStoreNames.contains(STORE)){db.close();reject(Error('Arquivo de evidências incompatível; nenhuma reinicialização foi realizada.'));return;}
        db.onversionchange=()=>db.close();resolve(db);
      };
    });
  }
  async function records(){
    const db=await open();
    return new Promise((resolve,reject)=>{
      let tx,rows=[];try{tx=db.transaction(STORE,'readonly');}catch(error){db.close();reject(error);return;}
      const req=tx.objectStore(STORE).openCursor();
      req.onsuccess=()=>{const c=req.result;if(c){rows.push(c.value);c.continue();}};
      tx.oncomplete=()=>{db.close();resolve(rows);};
      tx.onabort=()=>{db.close();reject(tx.error||Error('Leitura das evidências interrompida.'));};
      tx.onerror=()=>{};
    });
  }
  function metadata(row){
    if(!object(row)||!HASH.test(row.fileHash)||!['pdf','html'].includes(row.kind)||!Number.isSafeInteger(row.size)||row.size<=0||row.size>LIMITS.file||
      !Array.isArray(row.receiptIds)||row.receiptIds.length>2000||row.receiptIds.some(v=>typeof v!=='string'||!v||v.length>255)||
      !row.blob||row.blob.size!==row.size||typeof row.blob.arrayBuffer!=='function')throw Error('Original armazenado incompatível ou corrompido. Nenhum dado foi redefinido.');
    name(row.fileName);if(typeof row.storedAt!=='string'||!Number.isFinite(Date.parse(row.storedAt)))throw Error('Instante do original armazenado inválido.');
    return {fileHash:row.fileHash,fileName:row.fileName,kind:row.kind,size:row.size,receiptIds:[...row.receiptIds],storedAt:row.storedAt};
  }
  async function writeBatch(input){
    const db=await open();
    return new Promise((resolve,reject)=>{
      let tx;try{tx=db.transaction(STORE,'readwrite');}catch(error){db.close();reject(error);return;}
      const store=tx.objectStore(STORE);let failure='';
      // The quota bound is checked within this same transaction, so two tabs
      // cannot independently accept conflicting totals.
      const scan=store.getAll();
      scan.onsuccess=()=>{
        try{
          const current=new Map(scan.result.map(r=>{metadata(r);return [r.fileHash,r];}));
          for(const item of input){
            const prior=current.get(item.fileHash);
            if(prior&&(prior.size!==item.size||prior.kind!==item.kind))throw Error('Metadados existentes divergem do original. Preserve o arquivo.');
            const receiptIds=[...new Set([...(prior?.receiptIds||[]),...item.receiptIds])];
            if(receiptIds.length>2000)throw Error('Limite de vínculos por original excedido.');
            current.set(item.fileHash,{...item,receiptIds,storedAt:prior?.storedAt||item.storedAt});
          }
          if(current.size>200||[...current.values()].reduce((n,r)=>n+r.size,0)>LIMITS.total)throw Error('Limite local de 200 originais / 128 MiB atingido. Exporte as evidências antes de incluir outras.');
          for(const item of input)store.put(current.get(item.fileHash));
        }catch(error){failure=error.message;try{tx.abort();}catch(ignored){}}
      };
      tx.oncomplete=()=>{db.close();resolve(result('CONFIRMED','Original preservado após conclusão da transação.',{count:input.length}));};
      tx.onabort=()=>{db.close();reject(Error(failure||tx.error?.message||'Gravação de evidências recusada. Nenhuma transação foi confirmada.'));};
      tx.onerror=()=>{};
    });
  }
  async function putOriginal(file,link={}){
    try{
      const expected=typeof link.fileHash==='string'?link.fileHash.toLowerCase():'';
      if(!HASH.test(expected)||typeof link.receiptId!=='string'||!link.receiptId||link.receiptId.length>255)throw Error('Comprovante e SHA-256 são necessários para vincular o original.');
      const read=await readOriginal(file,expected);
      const row={...read,bytes:undefined,blob:new Blob([read.bytes],{type:read.kind==='pdf'?'application/pdf':'text/html'}),
        receiptIds:[link.receiptId],storedAt:new Date().toISOString()};
      delete row.bytes;
      const saved=await writeBatch([row]);return publish({...saved,fileHash:read.fileHash});
    }catch(error){return refusal(error.message||'Original não preservado. Guarde uma cópia externa.');}
  }
  async function summary(){
    try{
      const rows=await records(),items=rows.map(metadata);
      return {status:'CONFIRMED',verification:'METADATA_ONLY',count:items.length,bytes:items.reduce((n,r)=>n+r.size,0),items,last:{...last},limits:LIMITS};
    }catch(error){return {status:'REFUSED',reason:error.message,count:null,bytes:null,items:[],last:{...last},limits:LIMITS};}
  }
  async function status(fileHash){
    if(!HASH.test(fileHash||''))return {status:'ABSENT',reason:'Original indisponível: comprovante sem SHA-256.'};
    try{
      const rows=await records(),row=rows.find(r=>r.fileHash===fileHash);
      if(!row)return {status:'ABSENT',reason:'Original indisponível neste navegador. Reassocie somente o arquivo com o mesmo SHA-256.'};
      const found=metadata(row),bytes=new Uint8Array(await row.blob.arrayBuffer());
      if(await digest(bytes)!==fileHash||kind(found.fileName,bytes)!==found.kind)throw Error('Original armazenado corrompido. Reassocie o arquivo com o mesmo SHA-256 antes de utilizá-lo.');
      return {status:'CONFIRMED',verification:'SHA256_AND_TYPE',reason:'Original preservado; SHA-256 e tipo conferidos nesta leitura.',...found};
    }catch(error){return {status:'REFUSED',reason:error.message};}
  }
  const encode=v=>new TextEncoder().encode(JSON.stringify(v));
  function download(bytes,filename,type){
    const url=URL.createObjectURL(new Blob([bytes],{type})),a=document.createElement('a');
    a.href=url;a.download=filename;a.hidden=true;document.body.appendChild(a);a.click();a.remove();setTimeout(()=>URL.revokeObjectURL(url),60000);
  }
  async function exportArchive(){
    if(busy)return refusal('Outra operação de evidências está em andamento.');
    busy=true;
    try{
      if(!root.fflate?.zipSync)throw Error('Biblioteca ZIP local indisponível. Nenhum arquivo foi gerado.');
      const rows=await records(),files=Object.create(null),entries=[];
      for(const row of rows){
        const meta=metadata(row),bytes=new Uint8Array(await row.blob.arrayBuffer());
        if(await digest(bytes)!==meta.fileHash)throw Error('Original armazenado corrompido. A exportação não foi concluída.');
        if(kind(meta.fileName,bytes)!==meta.kind)throw Error('Tipo do original divergente.');
        const path='originals/'+meta.fileHash+'.'+meta.kind;
        entries.push({...meta,path});files[path]=[bytes,{level:0}];
      }
      const body={format:'jpwealth_original_evidence',formatVersion:1,createdAt:new Date().toISOString(),coverage:'original-pdf-html-only',entries};
      const manifest={...body,checksum:{algorithm:'SHA-256',value:await digest(encode(body))}};
      files['manifest.json']=[encode(manifest),{level:0}];
      const zip=root.fflate.zipSync(files,{level:0}),filename='JP_WEALTH_EVIDENCES_'+new Date().toISOString().replace(/[:.]/g,'-')+'_'+crypto.randomUUID()+'.zip';
      if(zip.length>LIMITS.zip)throw Error('Arquivo ZIP excedeu o limite de 144 MiB.');
      download(zip,filename,'application/zip');
      return publish(result('DOWNLOAD_REQUESTED','ZIP gerado e download solicitado. Confira o arquivo fora do navegador.',{filename,count:entries.length,bytes:zip.length}));
    }catch(error){return refusal(error.message||'Exportação de evidências não concluída.');}
    finally{busy=false;}
  }
  // Validate the central directory before decompression: bounds, duplicate
  // names, unsupported ZIP64/encryption/compression, paths and expanded size.
  // Version 1 emits STORE entries only. Refusing deflate avoids allocating or
  // processing an untrusted expansion before its actual size can be verified.
  function inspectZip(bytes){
    const view=new DataView(bytes.buffer,bytes.byteOffset,bytes.byteLength),length=bytes.length;
    let end=-1;
    for(let i=length-22;i>=Math.max(0,length-65557);i--)if(view.getUint32(i,true)===0x06054b50&&i+22+view.getUint16(i+20,true)===length){end=i;break;}
    if(end<0)throw Error('ZIP inválido ou incompleto.');
    const count=view.getUint16(end+10,true),size=view.getUint32(end+12,true),offset=view.getUint32(end+16,true);
    if(view.getUint16(end+4,true)||view.getUint16(end+6,true)||view.getUint16(end+8,true)!==count||!count||count>LIMITS.entries||
      count===65535||size===4294967295||offset===4294967295||offset+size!==end)throw Error('Estrutura ZIP não suportada ou acima dos limites.');
    const names=new Set(),expected=new Map();let pos=offset,total=0;
    for(let n=0;n<count;n++){
      if(pos+46>end||view.getUint32(pos,true)!==0x02014b50)throw Error('Diretório ZIP inválido.');
      const flags=view.getUint16(pos+8,true),method=view.getUint16(pos+10,true),packed=view.getUint32(pos+20,true),expanded=view.getUint32(pos+24,true),
        nl=view.getUint16(pos+28,true),el=view.getUint16(pos+30,true),cl=view.getUint16(pos+32,true),local=view.getUint32(pos+42,true);
      if(pos+46+nl+el+cl>end)throw Error('Nome ZIP fora dos limites.');
      const path=new TextDecoder('utf-8',{fatal:true}).decode(bytes.subarray(pos+46,pos+46+nl));
      if(names.has(path)||!(path==='manifest.json'||/^originals\/[a-f0-9]{64}\.(pdf|html)$/.test(path))||
        flags&1||method!==0||packed!==expanded||view.getUint16(pos+34,true)||packed===4294967295||expanded===4294967295||
        expanded>(path==='manifest.json'?LIMITS.manifest:LIMITS.file)||local+30>offset||view.getUint32(local,true)!==0x04034b50)throw Error('Entrada ZIP recusada: caminho, tamanho, compressão não suportada, criptografia ou duplicação.');
      const lnl=view.getUint16(local+26,true),lel=view.getUint16(local+28,true),start=local+30+lnl+lel;
      if(start+packed>offset||view.getUint16(local+6,true)!==flags||view.getUint16(local+8,true)!==method||
        (!(flags&8)&&(view.getUint32(local+18,true)!==packed||view.getUint32(local+22,true)!==expanded))||
        new TextDecoder('utf-8',{fatal:true}).decode(bytes.subarray(local+30,local+30+lnl))!==path)throw Error('Cabeçalho local ZIP divergente.');
      total+=expanded;if(total>LIMITS.total+LIMITS.manifest)throw Error('ZIP expandido acima de 130 MiB.');
      names.add(path);expected.set(path,expanded);pos+=46+nl+el+cl;
    }
    if(pos!==end||!names.has('manifest.json'))throw Error('Manifesto ZIP ausente ou diretório divergente.');
    return expected;
  }
  async function restoreArchive(file){
    if(busy)return refusal('Outra operação de evidências está em andamento.');
    busy=true;
    try{
      if(!file||!Number.isSafeInteger(file.size)||file.size<=0||file.size>LIMITS.zip)throw Error('ZIP vazio ou acima de 144 MiB.');
      if(!root.fflate?.unzipSync)throw Error('Biblioteca ZIP local indisponível.');
      const bytes=new Uint8Array(await file.arrayBuffer()),expected=inspectZip(bytes);
      const entries=root.fflate.unzipSync(bytes,{filter:entry=>expected.has(entry.name)&&entry.originalSize===expected.get(entry.name)});
      if(Object.keys(entries).length!==expected.size||Object.entries(entries).some(([p,b])=>b.length!==expected.get(p)))throw Error('Conteúdo ZIP divergente do diretório.');
      const manifest=JSON.parse(new TextDecoder('utf-8',{fatal:true}).decode(entries['manifest.json']));
      if(!object(manifest)||manifest.format!=='jpwealth_original_evidence'||manifest.formatVersion!==1||manifest.coverage!=='original-pdf-html-only'||
        !Array.isArray(manifest.entries)||manifest.entries.length>200||manifest.entries.length+1!==expected.size||
        !object(manifest.checksum)||manifest.checksum.algorithm!=='SHA-256'||!HASH.test(manifest.checksum.value||''))throw Error('Formato ou cobertura do manifesto incompatível.');
      const {checksum,...body}=manifest;if(await digest(encode(body))!==checksum.value)throw Error('Checksum do manifesto divergente.');
      const rows=[],seen=new Set();
      for(const item of manifest.entries){
        if(!object(item)||!HASH.test(item.fileHash||'')||seen.has(item.fileHash)||item.path!=='originals/'+item.fileHash+'.'+item.kind||
          !Number.isSafeInteger(item.size)||item.size<=0||item.size>LIMITS.file||!['pdf','html'].includes(item.kind)||
          !Array.isArray(item.receiptIds)||item.receiptIds.length>2000||item.receiptIds.some(id=>typeof id!=='string'||!id||id.length>255)||
          typeof item.storedAt!=='string'||!Number.isFinite(Date.parse(item.storedAt)))throw Error('Metadados do original incompatíveis.');
        name(item.fileName);
        const data=entries[item.path];
        if(!data||data.length!==item.size||await digest(data)!==item.fileHash||kind(item.fileName,data)!==item.kind)throw Error('Original não corresponde ao hash/tamanho/tipo do manifesto.');
        seen.add(item.fileHash);rows.push({...item,path:undefined,blob:new Blob([data],{type:item.kind==='pdf'?'application/pdf':'text/html'})});
      }
      // No writes occurred before every entry and checksum passed.
      const saved=await writeBatch(rows);
      return publish({...saved,reason:'ZIP conferido; originais restaurados. A base financeira e os rascunhos não foram alterados.'});
    }catch(error){return refusal(error.message||'Restauração das evidências recusada.');}
    finally{busy=false;}
  }
  async function reassociate(file,receipt){
    if(!object(receipt)||!HASH.test(receipt.fileHash||'')||typeof receipt.id!=='string')return refusal('Comprovante original sem hash válido.');
    return putOriginal(file,{fileHash:receipt.fileHash,receiptId:receipt.id});
  }
  root.JPWEvidence=Object.freeze({formatVersion:VERSION,limits:LIMITS,digest,putOriginal,summary,status,exportArchive,restoreArchive,reassociate,lastResult:()=>({...last})});
})(window);
