#ifndef JPW_PERSONAL_HISTORY_CONTROLLER_MQH
#define JPW_PERSONAL_HISTORY_CONTROLLER_MQH
#include <JPWealth/JPW_PersonalHistory_Terminal.mqh>
#include <JPWealth/JPW_PersonalHistory_Store.mqh>
// One observational producer; chart windows are only consumers. No trade calls.
JPWPersonalStoreContext g_ph_store;
JPWPersonalEpisode g_ph_episodes[];
JPWPersonalEvent g_ph_unwritten[];
JPWPersonalPeak g_ph_current,g_ph_estimated_peak;
string g_ph_context="",g_ph_token="",g_ph_last_problem="";
bool g_ph_loaded=false,g_ph_incomplete=false,g_ph_gap=false,g_ph_dirty=true;
bool g_ph_pending_current=false,g_ph_pending_estimated=false,g_ph_notification_error=false;
ulong g_ph_next_open=0,g_ph_last_cycle=0,g_ph_last_accepted=0;
long g_ph_last_wall=0;
int g_ph_live_count=-1,g_ph_exclusive_file=INVALID_HANDLE;
bool g_ph_memory_state=false,g_ph_restored_once=false,g_ph_gap_noted=false,g_ph_persist_error_cycle=false,g_ph_owner_conflict=false;
#define JPW_PERSONAL_UNWRITTEN_LIMIT 4096
string JPWPersonalControllerMarker(const string prefix)
  { return(prefix+StringSubstr(g_ph_context,0,24)+"_"+StringSubstr(g_ph_token,0,24)); }
void JPWPersonalControllerBridge(const int state)
  {
   if(!JPWPersonalHashValid(g_ph_context) || !JPWPersonalHashValid(g_ph_token)) return;
   const string name=JPWPersonalControllerMarker("JPWPH_"),count=JPWPersonalControllerMarker("JPWPC_");
   if(!GlobalVariableCheck(name)) GlobalVariableTemp(name);
   if(!GlobalVariableCheck(count)) GlobalVariableTemp(count);
   // Technical freshness/state only; not a financial sample or continuous-cover proof.
   if(GlobalVariableCheck(name)) GlobalVariableSet(name,(double)((long)TimeGMT()*16+state));
   if(GlobalVariableCheck(count)) GlobalVariableSet(count,(double)g_ph_live_count);
  }
void JPWPersonalControllerProblem(const string reason,const bool storage)
  {
   if(reason!=g_ph_last_problem) Print("JPW Histórico Pessoal: ",reason);
   g_ph_last_problem=reason; if(storage) { g_ph_incomplete=true; g_ph_gap=true; g_ph_persist_error_cycle=true; }
   JPWPersonalControllerBridge(storage ? 3 : 2);
  }
void JPWPersonalControllerQueue(JPWPersonalEvent &events[])
  {
   for(int i=0;i<ArraySize(events);i++)
     {
      int n=ArraySize(g_ph_unwritten);
      if(n>=JPW_PERSONAL_UNWRITTEN_LIMIT || ArrayResize(g_ph_unwritten,n+1)!=n+1)
        { g_ph_incomplete=true; g_ph_gap=true;
          JPWPersonalControllerProblem("Fila do Histórico Pessoal incompleta; evento não confirmado",true); return; }
      g_ph_unwritten[n]=events[i];
     }
  }
void JPWPersonalControllerCompact()
  {
   int kept=0;
   for(int i=0;i<ArraySize(g_ph_episodes);i++) if(g_ph_episodes[i].state==JPW_PERSONAL_ACTIVE)
      g_ph_episodes[kept++]=g_ph_episodes[i];
   ArrayResize(g_ph_episodes,kept); // Only memory; immutable financial history remains in SQLite.
  }
bool JPWPersonalControllerExclusive()
  {
   if(g_ph_exclusive_file!=INVALID_HANDLE) return(true);
   FolderCreate("JPWealth"); FolderCreate("JPWealth\\Genetrix"); FolderCreate("JPWealth\\Genetrix\\PersonalHistory");
   // No FILE_SHARE_READ/WRITE: a retained OS handle is the local producer fence.
   // This technical lock is never a financial record and is never deleted.
   g_ph_exclusive_file=FileOpen(JPW_PERSONAL_FOLDER+"writer_"+g_ph_context+".lock",FILE_READ|FILE_WRITE|FILE_BIN);
   if(g_ph_exclusive_file==INVALID_HANDLE)
     { g_ph_live_count=-1; JPWPersonalControllerBridge(4); return(false); }
   return(true);
  }
void JPWPersonalControllerMarkDirty() { g_ph_dirty=true; }
void JPWPersonalControllerDeferred()
  {
   g_ph_gap=true; g_ph_live_count=-1;
   JPWPersonalControllerBridge(g_ph_incomplete ? 3 : 2);
  }
void JPWPersonalControllerDetach(const string why)
  {
   if(g_ph_store.db!=INVALID_HANDLE && g_ph_store.writer)
     {
      const long wall=(long)TimeGMT(); const ulong mono=GetTickCount64();
      if(ArraySize(g_ph_unwritten)>0 || g_ph_pending_current || g_ph_pending_estimated || g_ph_gap)
         JPWPersonalCoverage(g_ph_store,"GAP",wall,mono,"Encerramento com trabalho/histórico não confirmado: "+why);
      JPWPersonalCoverage(g_ph_store,"SESSION_END",wall,mono,why);
     }
   JPWPersonalClose(g_ph_store,(long)TimeGMT(),GetTickCount64());
   if(g_ph_exclusive_file!=INVALID_HANDLE) FileClose(g_ph_exclusive_file);
   g_ph_exclusive_file=INVALID_HANDLE;
   if(g_ph_context!="" && g_ph_token!="")
     { GlobalVariableDel(JPWPersonalControllerMarker("JPWPH_")); GlobalVariableDel(JPWPersonalControllerMarker("JPWPC_")); }
   JPWPersonalTerminalReset(); ArrayResize(g_ph_episodes,0); ArrayResize(g_ph_unwritten,0);
   g_ph_context=""; g_ph_token=""; g_ph_loaded=false; g_ph_memory_state=false; g_ph_live_count=-1;
  }
bool JPWPersonalControllerAttach(const string key,const string token_seed)
  {
   g_ph_store.db=INVALID_HANDLE; g_ph_store.writer=false; g_ph_exclusive_file=INVALID_HANDLE; g_ph_memory_state=false; g_ph_restored_once=false; g_ph_gap_noted=false; g_ph_persist_error_cycle=false; g_ph_owner_conflict=false;
   g_ph_context=key; g_ph_token=""; g_ph_loaded=false; g_ph_incomplete=false; g_ph_gap=false; g_ph_dirty=true;
   g_ph_pending_current=false; g_ph_pending_estimated=false; g_ph_notification_error=false;
   g_ph_current.valid=false; g_ph_estimated_peak.valid=false; g_ph_next_open=0;
   g_ph_last_cycle=0; g_ph_last_accepted=0; g_ph_last_wall=0; g_ph_last_problem=""; g_ph_live_count=-1;
   JPWResetData(); JPWPersonalTerminalReset(); ArrayResize(g_ph_episodes,0); ArrayResize(g_ph_unwritten,0);
   string seed=token_seed;
   if(seed=="") seed=JPWPersonalInt(ChartID())+"|"+JPWPersonalInt((long)TimeGMT())+"|"+JPWPersonalInt((long)GetMicrosecondCount());
   if(!JPWPersonalHashValid(key) ||
      !JPWPersonalHash(key+"|personal_writer_v1|"+seed+"|"+JPWPersonalInt((long)GetMicrosecondCount()),g_ph_token))
     { JPWPersonalControllerProblem("Identidade do produtor indisponível; monitoramento não habilitado",true); return(false); }
   JPWPersonalControllerBridge(0); return(true);
  }
void JPWPersonalControllerMergeRestored(JPWPersonalEpisode &restored[])
  {
   // Do not erase requests made in observation while persistence was unavailable.
   for(int i=0;i<ArraySize(restored);i++)
     {
      int found=-1;
      for(int j=0;j<ArraySize(g_ph_episodes);j++)
         if(JPWPersonalSubjectKey(restored[i].subject)==JPWPersonalSubjectKey(g_ph_episodes[j].subject)) { found=j; break; }
      if(found>=0)
        {
         if(g_ph_episodes[found].first_wall<restored[i].first_wall) restored[i].first_wall=g_ph_episodes[found].first_wall;
         if(g_ph_episodes[found].last_wall>=restored[i].last_wall)
           {
            restored[i].subject=g_ph_episodes[found].subject; restored[i].state=g_ph_episodes[found].state;
            restored[i].last_wall=g_ph_episodes[found].last_wall; restored[i].resolved_wall=g_ph_episodes[found].resolved_wall;
            restored[i].resolution=g_ph_episodes[found].resolution;
           }
         if(g_ph_episodes[found].last_requested_wall>=restored[i].last_requested_wall)
           {
            restored[i].last_requested_wall=g_ph_episodes[found].last_requested_wall;
            restored[i].next_wall=g_ph_episodes[found].next_wall; restored[i].next_mono=g_ph_episodes[found].next_mono;
            restored[i].mono_ready=g_ph_episodes[found].mono_ready;
            restored[i].requested_count=(int)MathMax(restored[i].requested_count,g_ph_episodes[found].requested_count);
           }
         // Earlier failed events retain their local IDs; this explicit bridge
         // relates them to the durable episode rather than rewriting history.
         if(restored[i].episode_id!=g_ph_episodes[found].episode_id)
           {
            JPWPersonalEvent links[];
            JPWPersonalEventAdd(links,"RECOVERY_EPISODE_LINK",restored[i].episode_id,(long)TimeGMT(),g_ph_episodes[found].episode_id);
            JPWPersonalControllerQueue(links);
           }
         g_ph_episodes[found]=restored[i];
        }
      else
        { int n=ArraySize(g_ph_episodes); if(ArrayResize(g_ph_episodes,n+1)==n+1) g_ph_episodes[n]=restored[i];
          else JPWPersonalControllerProblem("Recuperação de episódios incompleta",true); }
     }
  }
bool JPWPersonalControllerEnsureStore(const ulong timer_started)
  {
   const ulong mono=GetTickCount64(); const long wall=(long)TimeGMT();
   if(g_ph_owner_conflict) { JPWPersonalControllerBridge(4); return(false); }
   if(g_ph_loaded && g_ph_store.writer)
     {
      if(JPWPersonalKeepAlive(g_ph_store,wall,mono)) return(true);
      if(!g_ph_store.writer)
        { g_ph_loaded=false; g_ph_owner_conflict=true; JPWPersonalTerminalReset(); g_ph_live_count=-1;
          JPWPersonalControllerProblem("Titularidade SQL mudou apesar do lock local; avisos e escrita suspensos até nova ativação",true);
          JPWPersonalControllerBridge(4); }
      else JPWPersonalControllerProblem(g_ph_store.reason,true);
      return(false);
     }
   if(mono<g_ph_next_open || mono-timer_started>=500) return(false);
   if(g_ph_store.db!=INVALID_HANDLE) JPWPersonalClose(g_ph_store,wall,mono);
   if(!JPWPersonalOpen(g_ph_context,true,g_ph_token,wall,mono,g_ph_store))
     {
      g_ph_next_open=mono+5000;
      // A surviving database lease may delay takeover after a crash. The
      // exclusive handle still permits read-only recovery of its cooldown.
      if(!g_ph_restored_once)
        {
         JPWPersonalStoreContext reader; JPWPersonalEpisode saved[]; JPWPersonalPeak current,estimated;
         if(JPWPersonalOpen(g_ph_context,false,"",0,0,reader))
           {
            if(JPWPersonalLoad(reader,saved,current,estimated))
              {
               JPWPersonalControllerMergeRestored(saved);
               if(current.valid && (!g_ph_current.valid || current.leverage>=g_ph_current.leverage))
                  { g_ph_current=current; g_ph_pending_current=false; }
               if(estimated.valid && (!g_ph_estimated_peak.valid || estimated.leverage>=g_ph_estimated_peak.leverage))
                  { g_ph_estimated_peak=estimated; g_ph_pending_estimated=false; }
               g_ph_restored_once=true;
              }
            JPWPersonalClose(reader,0,0);
           }
        }
      if(g_ph_store.result==JPW_STORE_BUSY) { g_ph_live_count=-1; JPWPersonalControllerBridge(4); }
      else JPWPersonalControllerProblem(g_ph_store.reason,true);
      return(false);
     }
   JPWPersonalEpisode restored[]; JPWPersonalPeak restored_current,restored_estimated;
   if(!JPWPersonalLoad(g_ph_store,restored,restored_current,restored_estimated))
     { JPWPersonalControllerProblem(g_ph_store.reason,true); JPWPersonalClose(g_ph_store,wall,mono);
       g_ph_next_open=mono+30000; return(false); }
   JPWPersonalControllerMergeRestored(restored);
   if(restored_current.valid && (!g_ph_current.valid || restored_current.leverage>=g_ph_current.leverage))
      { g_ph_current=restored_current; g_ph_pending_current=false; }
   if(restored_estimated.valid && (!g_ph_estimated_peak.valid || restored_estimated.leverage>=g_ph_estimated_peak.leverage))
      { g_ph_estimated_peak=restored_estimated; g_ph_pending_estimated=false; }
   g_ph_loaded=true; g_ph_restored_once=true;
   if(!JPWPersonalCoverage(g_ph_store,"SESSION_START",wall,mono,
      "Monitoramento a partir desta ativação; períodos anteriores/entre sessões não são cobertura comprovada"))
      JPWPersonalControllerProblem(g_ph_store.reason,true);
   // Explicit unknown interval on restart when previous financial state exists.
   if(ArraySize(g_ph_episodes)>0 || g_ph_current.valid || g_ph_estimated_peak.valid)
     { g_ph_gap=true;
       if(!JPWPersonalCoverage(g_ph_store,"GAP",wall,mono,"Reinício/tomada de titularidade; continuidade anterior não demonstrada"))
         JPWPersonalControllerProblem(g_ph_store.reason,true); }
   return(true);
  }
void JPWPersonalControllerCompletionEvidence(JPWPersonalEvent &events[],const ulong started)
  {
   for(int i=0;i<ArraySize(events);i++)
     {
      if(events[i].type!="NO_LONGER_PRESENT" || GetTickCount64()-started>=500) continue;
      for(int j=0;j<ArraySize(g_ph_episodes);j++) if(g_ph_episodes[j].episode_id==events[i].episode_id)
        {
         string reason="",link="";
         if(JPWPersonalTerminalCompletionProof(g_ph_episodes[j].subject,reason,link))
           { g_ph_episodes[j].subject.terminal_reason=reason; g_ph_episodes[j].subject.link_id=link;
             g_ph_episodes[j].resolution=reason;
             events[i].payload="{\"reason\":"+JPWPersonalJSON(reason)+",\"link_id\":"+JPWPersonalJSON(link)+
               ",\"evidence\":\"MT5_HISTORY_CONFIRMED\"}"; }
         else events[i].payload="{\"reason\":\"NO_LONGER_PRESENT_REASON_UNAVAILABLE\"}";
         break;
        }
     }
  }
bool JPWPersonalControllerPersist(JPWPersonalCapture &capture)
  {
   const int changed=(g_ph_pending_current ? 1 : (g_ph_pending_estimated ? 2 : 0));
   if(!JPWPersonalCommit(g_ph_store,capture,g_ph_episodes,g_ph_unwritten,g_ph_current,g_ph_estimated_peak,changed))
     { JPWPersonalControllerProblem(g_ph_store.reason,true); return(false); }
   if(changed==1) g_ph_pending_current=false; if(changed==2) g_ph_pending_estimated=false;
   ArrayResize(g_ph_unwritten,0); JPWPersonalControllerCompact();
   return(true);
  }
void JPWPersonalControllerNotifyDue(JPWPersonalCapture &capture,int &due[],const ulong started)
  {
   if(ArraySize(due)==0 || g_ph_owner_conflict) return;
   // Reconcile indices refer to the un-compacted projection. Called before a
   // successful persistence compacts memory. No index is used after compaction.
   int verified[]; string payload="[",message="GENETRIX — sem SL registrado na corretora";
   for(int i=0;i<ArraySize(due);i++)
     {
      if(GetTickCount64()-started>=500) { g_ph_gap=true; break; }
      const int index=due[i];
      if(index<0 || index>=ArraySize(g_ph_episodes) || g_ph_episodes[index].state!=JPW_PERSONAL_ACTIVE ||
         !JPWPersonalTerminalNoSLNow(g_ph_context,g_ph_episodes[index].subject)) continue;
      int n=ArraySize(verified); if(ArrayResize(verified,n+1)!=n+1) { g_ph_incomplete=true; break; }
      verified[n]=index;
      if(n>0) payload+=",";
      payload+="{\"episode_id\":"+JPWPersonalJSON(g_ph_episodes[index].episode_id)+",\"kind\":"+
        JPWPersonalInt(g_ph_episodes[index].subject.kind)+",\"ticket\":"+JPWPersonalJSON(g_ph_episodes[index].subject.ticket)+"}";
      if(StringLen(message)<1400) message+="\n"+g_ph_episodes[index].subject.symbol+" · "+
         (g_ph_episodes[index].subject.kind==JPW_PERSONAL_POSITION ? "posição " : "pendente ")+g_ph_episodes[index].subject.ticket;
     }
   if(ArraySize(verified)==0) return;
   // Capture monetary values remain frozen; the notification schedule uses the
   // actual request instant and fresh exact-ticket SL readings above.
   capture.wall_seconds=(long)TimeGMT(); capture.mono_ms=GetTickCount64();
   for(int i=0;i<ArraySize(verified);i++) JPWPersonalMarkRequested(capture,g_ph_episodes[verified[i]]);
   payload+="]"; message+="\nOcorrências: "+JPWPersonalInt(ArraySize(verified))+". Reaviso em 60s após nova verificação.";
   string group=""; JPWPersonalHash(g_ph_context+"|"+g_ph_token+"|"+JPWPersonalInt((long)capture.mono_ms)+"|"+payload,group);
   bool intent=g_ph_loaded && g_ph_store.writer && JPWPersonalNotify(g_ph_store,group,"INTENT",capture.wall_seconds,capture.mono_ms,payload,g_ph_episodes);
   if(!intent)
     {
      JPWPersonalControllerProblem("Histórico incompleto — intenção do aviso não persistida: "+g_ph_store.reason,true);
      // The retained exclusive handle still proves the local producer fence.
      // Explicit SQL-owner conflict overrides it and suspends all channels.
      if(g_ph_loaded && !g_ph_store.writer) { g_ph_owner_conflict=true; return; }
      if(g_ph_exclusive_file==INVALID_HANDLE) return;
      message+="\nHistórico incompleto — gravação não confirmada.";
     }
   string key="",currency="";
   if(!JPWPersonalTerminalIdentity(key,currency) || key!=g_ph_context || !TerminalInfoInteger(TERMINAL_CONNECTED))
     { g_ph_gap=true; return; }
   bool channel_error=false;
   const string result=JPWPersonalTerminalNotify(message,channel_error);
   // Alert() has no acknowledgement. CALLED records the function request only.
   if(intent)
     {
      if(result!="TESTER_CHANNELS_UNAVAILABLE_NOT_CALLED" &&
         !JPWPersonalNotify(g_ph_store,group,"CALLED",(long)TimeGMT(),GetTickCount64(),"Popup e som solicitados; visto/ouvido indisponível",g_ph_episodes))
         JPWPersonalControllerProblem(g_ph_store.reason,true);
      if(!JPWPersonalNotify(g_ph_store,group,"RESULT",(long)TimeGMT(),GetTickCount64(),result,g_ph_episodes))
         JPWPersonalControllerProblem(g_ph_store.reason,true);
     }
   else g_ph_gap=true; // Unrecorded request remains explicitly incomplete, never a fake durable receipt.
   if(channel_error)
     {
      JPWPersonalEvent errors[];
      JPWPersonalEventAdd(errors,"NOTIFICATION_CHANNEL_ERROR",group,(long)TimeGMT(),result);
      JPWPersonalControllerQueue(errors);
     }
   g_ph_notification_error=channel_error;
  }
void JPWPersonalControllerTick(const ulong started)
  {
   if(g_ph_context=="" || g_ph_token=="") return;
   g_ph_persist_error_cycle=false;
   if(GetTickCount64()-started>=500) { JPWPersonalControllerDeferred(); return; }
   const ulong now=GetTickCount64(); const long wall=(long)TimeGMT();
   if(g_ph_last_cycle>0 && (now<g_ph_last_cycle || now-g_ph_last_cycle>5000)) g_ph_gap=true;
   if(g_ph_last_wall>0 && wall<g_ph_last_wall) g_ph_gap=true;
   g_ph_last_cycle=now; g_ph_last_wall=wall;
   if(!JPWPersonalControllerExclusive()) return;
   if(g_ph_dirty) { JPWPersonalTerminalReset(); g_ph_dirty=false; }
   bool writer=JPWPersonalControllerEnsureStore(started);
   // Read-only observation remains possible without storage. Notifications
   // require the exclusive local producer handle to prevent competing instances.
   JPWPersonalCapture capture; JPWPersonalSubject subjects[]; bool ready=false; string reason="";
   if(!JPWPersonalTerminalCaptureStep(g_ph_context,started,capture,subjects,ready,reason))
     {
      g_ph_gap=true; g_ph_live_count=-1; JPWPersonalControllerProblem(reason,false);
      if(!g_ph_gap_noted && writer && GetTickCount64()-started<500 &&
         JPWPersonalCoverage(g_ph_store,"GAP",(long)TimeGMT(),GetTickCount64(),reason)) g_ph_gap_noted=true;
      return;
     }
   if(!ready)
     { JPWPersonalControllerBridge(g_ph_incomplete ? 3 : (writer ? 0 : 4)); return; }
   g_ph_dirty=false; g_ph_last_accepted=now;
   if(!writer || !g_ph_loaded) g_ph_incomplete=true;
   g_ph_memory_state=true;
   JPWPersonalEvent events[]; int due[];
   if(!JPWPersonalReconcile(capture,subjects,g_ph_episodes,events,due))
     { g_ph_gap=true; g_ph_live_count=-1; JPWPersonalControllerProblem("Inventário não reconciliado; nenhum alerta ou máximo novo",false); return; }
   JPWPersonalControllerCompletionEvidence(events,started);
   string context_id=""; bool context_needed=false;
   JPWPersonalHash(capture.details,context_id);
   for(int i=0;i<ArraySize(events);i++) if(events[i].type=="NO_SL_DETECTED")
     {
      context_needed=true;
      events[i].payload="{\"link_id\":"+JPWPersonalJSON(events[i].payload)+",\"observation_id\":"+JPWPersonalJSON(context_id)+"}";
     }
   // A shared immutable witness avoids repeating an entire account photograph
   // for every subject that is detected in the same accepted observation.
   if(context_needed) JPWPersonalEventAdd(events,"INVENTORY_CONTEXT",context_id,capture.wall_seconds,capture.details);
   JPWPersonalControllerQueue(events);
   int changed=0;
   JPWPersonalPeakAccept(capture,capture.details,g_ph_current,g_ph_estimated_peak,changed);
   if(changed==1) g_ph_pending_current=true; if(changed==2) g_ph_pending_estimated=true;
   g_ph_live_count=0;
   for(int i=0;i<ArraySize(subjects);i++)
     {
      if(!subjects[i].sl_readable) { g_ph_live_count=-1; break; }
      if(subjects[i].sl==0) g_ph_live_count++;
     }
   if(g_ph_live_count<0) g_ph_gap=true;
   // Persist transitions before external notification, but defer compaction
   // until due indices have been consumed.
   const int pending=(g_ph_pending_current ? 1 : (g_ph_pending_estimated ? 2 : 0));
   bool stored=writer && g_ph_loaded && JPWPersonalCommit(g_ph_store,capture,g_ph_episodes,g_ph_unwritten,g_ph_current,g_ph_estimated_peak,pending);
   if(stored)
     { ArrayResize(g_ph_unwritten,0); if(pending==1) g_ph_pending_current=false; if(pending==2) g_ph_pending_estimated=false; }
   else
     { JPWPersonalControllerProblem(g_ph_store.reason,true);
       if(g_ph_loaded && !g_ph_store.writer) g_ph_owner_conflict=true; }
   JPWPersonalControllerNotifyDue(capture,due,started);
   if(stored) JPWPersonalControllerCompact();
   if(g_ph_gap && GetTickCount64()-started<500 && g_ph_store.writer)
     {
      if(!g_ph_gap_noted)
        {
         if(JPWPersonalCoverage(g_ph_store,"GAP",(long)TimeGMT(),GetTickCount64(),
            "Intervalo com monitoramento, captura ou escrita incompleta; detalhes nos registros e Journal")) g_ph_gap_noted=true;
         else JPWPersonalControllerProblem(g_ph_store.reason,true);
        }
      if(g_ph_gap_noted && stored && !g_ph_persist_error_cycle && g_ph_live_count>=0 &&
         ArraySize(g_ph_unwritten)==0 && !g_ph_pending_current && !g_ph_pending_estimated)
        {
         if(JPWPersonalCoverage(g_ph_store,"RESUMED",(long)TimeGMT(),GetTickCount64(),"Inventário revalidado; não prova completude anterior"))
            { g_ph_gap=false; g_ph_gap_noted=false; }
         else JPWPersonalControllerProblem(g_ph_store.reason,true);
        }
     }
   if(stored && !g_ph_persist_error_cycle && !g_ph_gap && ArraySize(g_ph_unwritten)==0 && !g_ph_pending_current && !g_ph_pending_estimated)
     { g_ph_incomplete=false; g_ph_last_problem=""; }
   JPWPersonalControllerBridge(g_ph_owner_conflict ? 4 : (g_ph_incomplete ? 3 : (g_ph_gap ? 2 : (g_ph_notification_error ? 5 : 1))));
  }
#endif
