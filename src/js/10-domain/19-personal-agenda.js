// Personal agenda: civil dates, explicit commands and the confirmed document writer.
// Read models never create/migrate the optional aggregate. Persistence uses the
// existing best-effort revision guard; it is not an atomic compare-and-swap.
(function(root){
  'use strict';
  const own=(value,key)=>Object.prototype.hasOwnProperty.call(value,key);
  const object=value=>!!value&&typeof value==='object'&&!Array.isArray(value);
  const clone=value=>structuredClone(value);
  const id=prefix=>prefix+'_'+(root.crypto?.randomUUID?.()||Date.now().toString(36)+'_'+Math.random().toString(36).slice(2));
  const session=id('agenda_session');
  const empty=()=>({schemaVersion:1,revision:0,items:[]});
  const error=(field,code,message)=>({field,code,message});
  const iso=value=>typeof value==='string'&&/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z$/.test(value)&&Number.isFinite(Date.parse(value))&&new Date(value).toISOString()===value;
  const integer=value=>Number.isSafeInteger(value)&&value>=0;
  const current=()=>typeof S!=='undefined'&&object(S)?S:null;
  const epoch=()=>typeof jpWealthPersistenceEpoch==='function'?jpWealthPersistenceEpoch():null;
  const globallyUnknown=()=>typeof jpWealthPersistenceOutcomeIsUnknown==='function'&&jpWealthPersistenceOutcomeIsUnknown();
  const canonical=value=>stable(JSON.parse(JSON.stringify(value,(key,item)=>key==='investorPassword'?'':item)));
  let generation=0,trackedRoot=null,trackedAggregate=null,unknown=false;
  let baseline=current()?clone(current()):null,contextEpoch=epoch();
  const formatters=new Map();
  function stable(value){
    if(Array.isArray(value))return '['+value.map(stable).join(',')+']';
    if(object(value))return '{'+Object.keys(value).sort().map(key=>JSON.stringify(key)+':'+stable(value[key])).join(',')+'}';
    return JSON.stringify(value);
  }
  function utcStamp(year,month,day,hour=0,minute=0){
    const value=new Date(0);value.setUTCFullYear(year,month-1,day);value.setUTCHours(hour,minute,0,0);return value.getTime();
  }
  function civil(value){
    if(typeof value!=='string'||!/^\d{4}-\d{2}-\d{2}$/.test(value))return false;
    const [year,month,day]=value.split('-').map(Number),d=new Date(utcStamp(year,month,day));
    return year>0&&d.getUTCFullYear()===year&&d.getUTCMonth()+1===month&&d.getUTCDate()===day;
  }
  function clock(value){return typeof value==='string'&&/^(?:[01]\d|2[0-3]):[0-5]\d$/.test(value);}
  function formatter(zone){
    if(typeof zone!=='string'||!zone.trim()||zone.length>100||/^[+−-]/.test(zone))return null;
    if(formatters.has(zone))return formatters.get(zone);
    try{
      const intl=typeof Intl!=='undefined'?Intl:null;
      if(!intl||typeof intl.DateTimeFormat!=='function')return zone==='UTC'?{utc:true}:null;
      const value=new intl.DateTimeFormat('en-CA-u-ca-gregory-nu-latn',{timeZone:zone,year:'numeric',month:'2-digit',day:'2-digit',hour:'2-digit',minute:'2-digit',second:'2-digit',hourCycle:'h23'});
      value.format(new Date(0));formatters.set(zone,value);return value;
    }catch(_error){return null;}
  }
  function parts(at,zone){
    const f=formatter(zone);if(!f)return null;
    if(f.utc){const d=new Date(at);return {year:d.getUTCFullYear(),month:d.getUTCMonth()+1,day:d.getUTCDate(),hour:d.getUTCHours(),minute:d.getUTCMinutes(),second:d.getUTCSeconds()};}
    const value={};for(const p of f.formatToParts(new Date(at)))if(['year','month','day','hour','minute','second'].includes(p.type))value[p.type]=Number(p.value);
    return value;
  }
  function dateAt(at,zone){
    const p=parts(at,zone);return p?String(p.year).padStart(4,'0')+'-'+String(p.month).padStart(2,'0')+'-'+String(p.day).padStart(2,'0'):null;
  }
  function viewingZone(){try{return (typeof Intl!=='undefined'&&Intl.DateTimeFormat().resolvedOptions().timeZone)||'UTC';}catch(_error){return 'UTC';}}
  function offsetAt(at,zone){const p=parts(at,zone);return utcStamp(p.year,p.month,p.day,p.hour,p.minute)+p.second*1000-Math.floor(at/1000)*1000;}
  function possibleInstants(date,time,zone){
    const [year,month,day]=date.split('-').map(Number),[hour,minute]=time.split(':').map(Number),wall=utcStamp(year,month,day,hour,minute),offsets=new Set();
    // Sample both sides of transitions, including non-hour changes such as
    // Lord Howe. Each candidate must then round-trip to the exact wall minute.
    for(let hours=-36;hours<=36;hours+=3)offsets.add(offsetAt(wall+hours*3600000,zone));
    const found=[];
    for(const offset of offsets){
      const at=wall-offset,p=parts(at,zone);
      if(p.year===year&&p.month===month&&p.day===day&&p.hour===hour&&p.minute===minute&&p.second===0)found.push(new Date(at).toISOString());
    }
    return Array.from(new Set(found)).sort();
  }
  function offsetLabel(value,zone){
    const offset=offsetAt(Date.parse(value),zone)/60000,absolute=Math.abs(offset),hours=Math.floor(absolute/60),minutes=absolute%60;
    return 'UTC'+(offset>=0?'+':'−')+String(hours).padStart(2,'0')+':'+String(minutes).padStart(2,'0')+' · '+value;
  }
  function safeTree(value,seen=new Set()){
    if(value===null||typeof value!=='object')return value===undefined||['string','boolean'].includes(typeof value)||typeof value==='number'&&Number.isFinite(value);
    if(seen.has(value))return false;seen.add(value);
    for(const key of Object.keys(value))if(['__proto__','prototype','constructor'].includes(key)||/password|passwd|senha|secret|token|credential|authorization|api[-_]?key|private[-_]?key/i.test(key)||!safeTree(value[key],seen))return false;
    seen.delete(value);return true;
  }
  function previewEntry(input){
    const errors=[],ambiguities=[];
    const reject=(field,code,message)=>errors.push(error(field,code,message));
    try{
      const allowed=['kind','title','notes','date','allDay','startTime','endDate','endTime','timeZone','startAtChoice','endAtChoice'];
      if(!object(input)||!safeTree(input)||Object.keys(input).some(key=>!allowed.includes(key))){reject('form','INVALID_INPUT','O preenchimento contém campos não permitidos.');return {ok:false,entry:null,errors,ambiguities};}
      if(!['task','appointment'].includes(input.kind))reject('kind','INVALID_KIND','Escolha tarefa ou compromisso.');
      const title=typeof input.title==='string'?input.title.trim():'';
      if(!title||title.length>200||/[\u0000-\u001f\u007f]/.test(title))reject('title','INVALID_TITLE','Informe um título com até 200 caracteres, sem controles.');
      const notes=input.notes==null?'':input.notes;
      if(typeof notes!=='string'||notes.length>10000||/[\u0000-\u0008\u000b\u000c\u000e-\u001f\u007f]/.test(notes))reject('notes','INVALID_NOTES','As observações devem ter até 10.000 caracteres, sem controles.');
      if(!civil(input.date))reject('date','INVALID_DATE','Informe uma data civil válida.');
      if(typeof input.allDay!=='boolean'||input.kind==='task'&&input.allDay!==true)reject('allDay','INVALID_ALL_DAY','Tarefas usam uma data, sem horário.');
      const entry={kind:input.kind,title,notes,date:input.date,allDay:input.allDay,startAt:null,endAt:null,timeZone:null};
      if(input.kind==='appointment'&&input.allDay===false){
        if(!clock(input.startTime))reject('startTime','INVALID_TIME','Informe o horário inicial em HH:mm.');
        if(!civil(input.endDate))reject('endDate','INVALID_DATE','Informe uma data final válida.');
        if(!clock(input.endTime))reject('endTime','INVALID_TIME','Informe o horário final em HH:mm.');
        if(!formatter(input.timeZone))reject('timeZone','INVALID_TIME_ZONE','Escolha um fuso IANA válido.');
        if(!errors.length){
          const resolve=(date,time,choice,field)=>{
            const options=possibleInstants(date,time,input.timeZone);
            if(!options.length){reject(field,'NONEXISTENT_TIME','Este horário não existe nesse fuso devido à mudança de relógio. Escolha outro horário.');return null;}
            if(options.length>1){
              if(!options.includes(input[choice])){
                ambiguities.push({field:choice,options:options.map(value=>({value,label:offsetLabel(value,input.timeZone)}))});
                reject(choice,'AMBIGUOUS_TIME','Este horário ocorre duas vezes. Escolha explicitamente o instante desejado.');return null;
              }
              return input[choice];
            }
            if(input[choice]!=null&&input[choice]!==''&&input[choice]!==options[0]){reject(choice,'INVALID_CHOICE','A escolha não corresponde ao horário e fuso atuais. Confira novamente.');return null;}
            return options[0];
          };
          entry.startAt=resolve(input.date,input.startTime,'startAtChoice','startTime');
          entry.endAt=resolve(input.endDate,input.endTime,'endAtChoice','endTime');entry.timeZone=input.timeZone;
          if(entry.startAt&&entry.endAt&&Date.parse(entry.endAt)<=Date.parse(entry.startAt))reject('endTime','INVALID_INTERVAL','O fim deve ocorrer depois do início.');
        }
      }
      return {ok:errors.length===0,entry:errors.length?null:entry,errors,ambiguities};
    }catch(_error){return {ok:false,entry:null,errors:[error('form','INVALID_INPUT','Não foi possível conferir este preenchimento.')],ambiguities};}
  }
  function aggregateIssues(value){
    const invalid=()=>[error('agenda','INCOMPATIBLE','A agenda é incompatível. Preserve a base para recuperação; seus registros não foram alterados.')];
    if(!object(value)||value.schemaVersion!==1||!integer(value.revision)||!Array.isArray(value.items))return invalid();
    const ids=new Set();
    for(const item of value.items){
      if(!object(item)||typeof item.id!=='string'||!item.id||ids.has(item.id)||!integer(item.revision)||item.revision<1||item.revision>value.revision||
        !['task','appointment'].includes(item.kind)||typeof item.title!=='string'||!item.title.trim()||item.title.length>200||/[\u0000-\u001f\u007f]/.test(item.title)||
        typeof item.notes!=='string'||item.notes.length>10000||/[\u0000-\u0008\u000b\u000c\u000e-\u001f\u007f]/.test(item.notes)||!civil(item.date)||typeof item.allDay!=='boolean'||
        !iso(item.createdAt)||!iso(item.updatedAt)||Date.parse(item.updatedAt)<Date.parse(item.createdAt)||!(item.completedAt===null||iso(item.completedAt)))return invalid();
      ids.add(item.id);
      if(item.kind==='task'&&!item.allDay||item.kind==='appointment'&&item.completedAt!==null)return invalid();
      if(item.allDay){if(item.startAt!==null||item.endAt!==null||item.timeZone!==null)return invalid();}
      else if(!iso(item.startAt)||!iso(item.endAt)||Date.parse(item.endAt)<=Date.parse(item.startAt)||!formatter(item.timeZone)||dateAt(Date.parse(item.startAt),item.timeZone)!==item.date)return invalid();
    }
    return [];
  }
  function sync(){
    const document=current(),aggregate=document?.personalAgenda;
    if(trackedRoot!==null&&(trackedRoot!==document||trackedAggregate!==aggregate))generation++;
    trackedRoot=document;trackedAggregate=aggregate;return document;
  }
  function envelope(){const document=sync();return document&&own(document,'personalAgenda')?document.personalAgenda:empty();}
  function snapshot(){
    const value=envelope(),issues=aggregateIssues(value);
    return issues.length?{status:'INCOMPATIBLE',revision:null,items:[],errors:issues}:{status:'OK',revision:value.revision,items:clone(value.items)};
  }
  function range(options={}){
    const source=snapshot();if(source.status!=='OK')return {status:source.status,items:[],errors:source.errors};
    if(!object(options))return {status:'INVALID',items:[],errors:[error('range','INVALID_RANGE','Informe um intervalo de datas e o fuso de visualização.')]};
    const zone=options.timeZone||viewingZone();
    if(!civil(options.from)||!civil(options.to)||options.from>options.to||!formatter(zone))return {status:'INVALID',items:[],errors:[error('range','INVALID_RANGE','Confira o intervalo de datas e o fuso de visualização.')]};
    const items=source.items.filter(item=>{
      if(item.allDay)return item.date>=options.from&&item.date<=options.to;
      // End is exclusive: an event finishing at midnight does not occupy the
      // following civil day. Viewing zone is independent of the item's IANA.
      return dateAt(Date.parse(item.startAt),zone)<=options.to&&dateAt(Date.parse(item.endAt)-1,zone)>=options.from;
    });
    return {status:'OK',items};
  }
  function token(value,item){return {session,generation,epoch:epoch(),revision:value.revision,itemId:item?.id||null,itemRevision:item?.revision??null};}
  function prepare({id:itemId=null}={}){
    const value=envelope(),issues=aggregateIssues(value),item=Array.isArray(value?.items)?value.items.find(item=>item.id===itemId):null;
    if(issues.length||!current())return {ok:false,token:null,item:null,errors:issues.length?issues:[error('agenda','NO_DOCUMENT','Documento principal indisponível.')]};
    if(itemId!==null&&!item)return {ok:false,token:null,item:null,errors:[error('id','NOT_FOUND','O registro não existe mais.')]};
    return {ok:true,token:token(value,item),item:item?clone(item):null,errors:[]};
  }
  function matches(t,value,itemId){
    const item=value.items.find(item=>item.id===itemId);
    return object(t)&&t.session===session&&t.generation===generation&&t.epoch===epoch()&&t.revision===value.revision&&
      t.itemId===itemId&&t.itemRevision===(item?.revision??null);
  }
  const outcome=(status,idValue=null,errors=[])=>({ok:status==='CONFIRMED',status,id:idValue,errors});
  function resetContext(){
    const document=current(),confirmed=typeof jpWealthConfirmedStateSnapshot==='function'?jpWealthConfirmedStateSnapshot():null;
    if(!document||globallyUnknown())return false;
    try{
      if(confirmed&&canonical(document)!==canonical(confirmed))return false;
      if(!confirmed&&canonical(document)!==canonical(baseline)){
        const defaults=typeof DEFAULTS!=='undefined'?DEFAULTS:null;if(!defaults||canonical(document)!==canonical(defaults))return false;
      }
    }catch(_error){return false;}
    const changed=trackedRoot!==null&&(trackedRoot!==document||trackedAggregate!==document.personalAgenda)||contextEpoch!==epoch();
    if(changed)generation++;
    trackedRoot=document;trackedAggregate=document.personalAgenda;contextEpoch=epoch();baseline=clone(document);if(confirmed)unknown=false;return changed;
  }
  function disposeForSession(){generation++;}
  function execute(type,options){
    const document=sync(),value=envelope(),t=options?.token,itemId=type==='save'?(t?.itemId??null):options?.id;
    if(unknown||globallyUnknown())return outcome('UNKNOWN',null,[error('agenda','PERSISTENCE_UNKNOWN','Resultado da gravação desconhecido. Preserve o rascunho e confira a recuperação antes de tentar novamente.')]);
    const issues=aggregateIssues(value);
    if(!document||issues.length)return outcome('INCOMPATIBLE',null,issues.length?issues:[error('agenda','NO_DOCUMENT','Documento principal indisponível.')]);
    if(!matches(t,value,itemId))return outcome('CONFLICT',itemId,[error('agenda','CONTEXT_CHANGED','A base ou o registro mudou. Confira o rascunho novamente antes de salvar.')]);
    try{
      const confirmed=typeof jpWealthConfirmedStateSnapshot==='function'?jpWealthConfirmedStateSnapshot():null;
      if(canonical(document)!==canonical(confirmed||baseline))return outcome('CONFLICT',itemId,[error('agenda','UNCONFIRMED_DOCUMENT','Há alterações não confirmadas em outra área. Preserve o rascunho e resolva a gravação antes de confirmar a agenda.')]);
      const candidate=clone(document),next=clone(value),index=next.items.findIndex(item=>item.id===itemId),previous=index>=0?next.items[index]:null;
      const at=new Date().toISOString();let affected=itemId,changed=true;
      if(type==='save'){
        const preview=previewEntry(options.input);if(!preview.ok)return outcome('INVALID',itemId,preview.errors);
        if(itemId!==null&&!previous)return outcome('INVALID',itemId,[error('id','NOT_FOUND','O registro não existe mais.')]);
        affected=previous?.id||id('agenda');
        const entry={...(previous||{}),...preview.entry,id:affected,revision:(previous?.revision||0)+1,
          completedAt:preview.entry.kind==='task'&&previous?.kind==='task'?previous.completedAt:null,createdAt:previous?.createdAt||at,updatedAt:at};
        if(index<0)next.items.push(entry);else next.items[index]=entry;
      }else{
        if(!previous)return outcome('INVALID',itemId,[error('id','NOT_FOUND','O registro não existe mais.')]);
        if(type==='remove')next.items.splice(index,1);
        else if(type==='setCompleted'){
          if(previous.kind!=='task'||typeof options.completed!=='boolean')return outcome('INVALID',itemId,[error('completed','INVALID_COMPLETION','Somente tarefas podem ser concluídas ou reabertas explicitamente.')]);
          changed=(previous.completedAt!==null)!==options.completed;
          if(changed)next.items[index]={...previous,completedAt:options.completed?at:null,revision:previous.revision+1,updatedAt:at};
        }else return outcome('INVALID',itemId,[error('form','INVALID_COMMAND','Ação de agenda inválida.')]);
      }
      if(changed)next.revision++;
      const invalid=aggregateIssues(next);if(invalid.length)return outcome('INVALID',itemId,invalid);
      candidate.personalAgenda=next;
      if(changed&&typeof dgLogChange==='function')dgLogChange('personalAgenda',type,affected,'Agenda: '+type,candidate);
      if(typeof jpWealthPersistDocument!=='function'||epoch()===null)return outcome('REFUSED',itemId,[error('agenda','WRITER_UNAVAILABLE','O escritor confirmado está indisponível. Preserve o rascunho.')]);
      let written;
      try{written=jpWealthPersistDocument(candidate,{expectedEpoch:t.epoch,component:'personalAgenda'});}
      catch(_error){written={status:'UNKNOWN'};}
      if(written?.status==='CONFIRMED'){
        S=candidate;trackedRoot=candidate;trackedAggregate=candidate.personalAgenda;baseline=clone(candidate);contextEpoch=epoch();
        // Observers only refresh projections. An unavailable or failing observer
        // cannot turn an already confirmed document into a refused command.
        try{if(typeof root.dispatchEvent==='function'&&typeof root.CustomEvent==='function')root.dispatchEvent(new root.CustomEvent('jpw-agenda-changed'));}catch(_error){}
        return outcome('CONFIRMED',affected);
      }
      generation++;
      if(written?.status==='REFUSED')return outcome(written.reason==='CONFLICT'?'CONFLICT':'REFUSED',itemId,[error('agenda',written.reason||'WRITE_REFUSED','A gravação foi recusada. Preserve e confira o rascunho.')]);
      unknown=true;if(!globallyUnknown()&&typeof markJPWealthPersistenceOutcomeUnknown==='function')markJPWealthPersistenceOutcomeUnknown('Agenda: confirmação indisponível.');
      return outcome('UNKNOWN',itemId,[error('agenda','PERSISTENCE_UNKNOWN','Resultado da gravação desconhecido. Preserve o rascunho e confira a recuperação.')]);
    }catch(_error){return outcome('INVALID',itemId,[error('form','INVALID_INPUT','Não foi possível preparar esta alteração com segurança.')]);}
  }
  const commands=Object.freeze({save:options=>execute('save',options),setCompleted:options=>execute('setCompleted',options),remove:options=>execute('remove',options),resetContext,disposeForSession});
  root.JPWAgenda=Object.freeze({queries:Object.freeze({snapshot,range,prepare,previewEntry}),commands,resetContext,disposeForSession});
})(window);
