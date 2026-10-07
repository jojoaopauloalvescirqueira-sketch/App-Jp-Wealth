#ifndef JPW_GENETRIX_MONITOR_CORE_MQH
#define JPW_GENETRIX_MONITOR_CORE_MQH
// Pure scheduling: caller supplies the monotonic clock and due-work mask.
// No terminal, trading, history-selection, file or database API is used here.
#define JPW_MONITOR_MODULE_COUNT 4
#define JPW_MONITOR_BUDGET_MS 500
#define JPW_MONITOR_LEDGER_SLICE_MS 100
#define JPW_MONITOR_FAIR_PROMOTION 3
struct JPWMonitorScheduler
  {
   ulong last_service_ms[4];
   int skipped[4];
   int cursor;
   long cycles,overruns,deferred_cycles;
   ulong last_elapsed_ms;
  };
void JPWMonitorSchedulerReset(JPWMonitorScheduler &state)
  {
   state.cursor=2; state.cycles=0; state.overruns=0;
   state.deferred_cycles=0; state.last_elapsed_ms=0;
   for(int i=0;i<4;i++) { state.last_service_ms[i]=0; state.skipped[i]=0; }
  }
void JPWMonitorSchedulerBegin(JPWMonitorScheduler &state,const int due_mask)
  {
   state.cycles++;
   for(int i=0;i<4;i++)
      if((due_mask&(1<<i))!=0 && state.skipped[i]<1000000) state.skipped[i]++;
  }
int JPWMonitorSchedulerNext(JPWMonitorScheduler &state,const ulong started,
                           const ulong now,const int due_mask,const int done_mask)
  {
   if(now<started || now-started>=JPW_MONITOR_BUDGET_MS) return(-1);
   int best=-1;
   // Overdue promotion prevents an indivisible recurring priority call from
   // permanently starving accounting or reconstruction. Normal priority is
   // StopRisk, Personal History, then rotating ledger/RaizN work.
   for(int offset=0;offset<4;offset++)
     {
      const int i=(state.cursor+offset)%4;
      if((due_mask&(1<<i))==0 || (done_mask&(1<<i))!=0 ||
         state.skipped[i]<JPW_MONITOR_FAIR_PROMOTION) continue;
      if(best<0 || state.skipped[i]>state.skipped[best]) best=i;
     }
   if(best>=0) return(best);
   for(int i=0;i<2;i++)
      if((due_mask&(1<<i))!=0 && (done_mask&(1<<i))==0) return(i);
   for(int offset=0;offset<4;offset++)
     {
      const int i=(state.cursor+offset)%4;
      if(i>=2 && (due_mask&(1<<i))!=0 && (done_mask&(1<<i))==0) return(i);
     }
   return(-1);
  }
void JPWMonitorSchedulerServiced(JPWMonitorScheduler &state,const int module,
                               const ulong now)
  {
   if(module<0 || module>=4) return;
   state.last_service_ms[module]=now; state.skipped[module]=0;
   state.cursor=(module+1)%4;
  }
void JPWMonitorSchedulerFinish(JPWMonitorScheduler &state,const ulong started,
                              const ulong now,const int due_mask,const int done_mask)
  {
   state.last_elapsed_ms=(now>=started ? now-started : 0);
   if(now<started || state.last_elapsed_ms>=JPW_MONITOR_BUDGET_MS) state.overruns++;
   if((due_mask&done_mask)!=due_mask) state.deferred_cycles++;
  }
#endif
