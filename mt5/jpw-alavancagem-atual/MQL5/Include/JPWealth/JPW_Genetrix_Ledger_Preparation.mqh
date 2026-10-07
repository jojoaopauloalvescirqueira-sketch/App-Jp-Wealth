#ifndef JPW_GENETRIX_LEDGER_PREPARATION_MQH
#define JPW_GENETRIX_LEDGER_PREPARATION_MQH
#include <JPWealth/JPW_Genetrix_Ledger_Terminal.mqh>
// Private ephemeral indexes/replay for the unified monitor. The legacy pure
// builder remains the compatibility oracle; no codec, formula or schema changes.
class CJPWLedgerLongIndex
  {
private:
   long keys[];
   int values[],stamps[];
   int capacity,epoch;
public:
   bool Init(const int wanted=131072)
     {
      capacity=wanted; epoch=1;
      if(capacity<2 || ArrayResize(keys,capacity)!=capacity || ArrayResize(values,capacity)!=capacity ||
         ArrayResize(stamps,capacity)!=capacity) return(false);
      ArrayInitialize(stamps,0); return(true);
     }
   void Clear()
     { if(epoch>=2147483646) { ArrayInitialize(stamps,0); epoch=1; } else epoch++; }
   int Get(const long key)
     {
      if(key<=0 || capacity<2) return(-1);
      int slot=(int)((ulong)key%(ulong)capacity);
      for(int n=0;n<capacity;n++)
        { if(stamps[slot]!=epoch) return(-1); if(keys[slot]==key) return(values[slot]); slot=(slot+1)%capacity; }
      return(-1);
     }
   bool Put(const long key,const int value)
     {
      if(key<=0 || capacity<2) return(false);
      int slot=(int)((ulong)key%(ulong)capacity);
      for(int n=0;n<capacity;n++)
        { if(stamps[slot]!=epoch || keys[slot]==key)
           { keys[slot]=key; values[slot]=value; stamps[slot]=epoch; return(true); }
          slot=(slot+1)%capacity; }
      return(false);
     }
  };
class CJPWLedgerGroupIndex
  {
private:
   string keys[];
   int values[],used[];
   int Slot(const string key)
     { uint hash=2166136261; for(int i=0;i<StringLen(key);i++) hash=(hash^(uint)StringGetCharacter(key,i))*16777619;
       return((int)(hash%8192)); }
public:
   bool Init()
     { if(ArrayResize(keys,8192)!=8192 || ArrayResize(values,8192)!=8192 || ArrayResize(used,8192)!=8192) return(false);
       ArrayInitialize(used,0); return(true); }
   int Get(const string key)
     { int slot=Slot(key); for(int n=0;n<8192;n++)
         { if(used[slot]==0) return(-1); if(keys[slot]==key) return(values[slot]); slot=(slot+1)%8192; } return(-1); }
   bool Put(const string key,const int value)
     { int slot=Slot(key); for(int n=0;n<8192;n++)
         { if(used[slot]==0 || keys[slot]==key) { keys[slot]=key; values[slot]=value; used[slot]=1; return(true); }
           slot=(slot+1)%8192; } return(false); }
  };

class CJPWLedgerReplay
  {
public:
   JPWLedgerCycle cycles[];
   JPWLedgerMember members[];
   string reason;
   int stage,cursor,processed;
private:
   JPWLedgerEvent heap[],batch[];
   CJPWLedgerLongIndex deal_index,order_index,member_index,live_index,future_index;
   CJPWLedgerGroupIndex groups;
   int order_cycle[],order_active[],execution_seen[],linked[],next_future[];
   double executed_volume[];
   int heads[],next_member[],previous_group[],opens[],pendings[],rollovers[],touched[],touch_queue[];
   int safe_epoch[],safe_count[],csv_length[],csv_offset[],csv_cursor[];
   uchar csv[];
   int batch_epoch,batch_cursor,touch_cursor;
   bool unassigned_cost,canceled_unresolved;

   bool Push(JPWLedgerEvent &e)
     {
      int n=ArraySize(heap);
#ifdef __MQL5__
      if(ArrayResize(heap,n+1,4096)!=n+1) return(false);
#else
      if(ArrayResize(heap,n+1)!=n+1) return(false);
#endif
      int i=n; while(i>0)
        { int parent=(i-1)/2; if(JPWLedgerCompareEvent(heap[parent],e)<=0) break;
          heap[i]=heap[parent]; i=parent; } heap[i]=e; return(true);
     }
   bool Pop(JPWLedgerEvent &e)
     {
      int n=ArraySize(heap); if(n<1) return(false); e=heap[0]; JPWLedgerEvent tail=heap[n-1];
      if(ArrayResize(heap,n-1)!=n-1) return(false);
      int i=0; while(i*2+1<n-1)
        { int child=i*2+1; if(child+1<n-1 && JPWLedgerCompareEvent(heap[child+1],heap[child])<0) child++;
          if(JPWLedgerCompareEvent(tail,heap[child])<=0) break; heap[i]=heap[child]; i=child; }
      if(n>1) heap[i]=tail; return(true);
     }
   string GroupKey(const string symbol,const int side) { return(symbol+"|"+IntegerToString(side)); }
   int Active(const string symbol,const int side)
     { int c=groups.Get(GroupKey(symbol,side));
       while(c>=0 && cycles[c].state==3) c=previous_group[c]; return(c); }
   void Touch(const int c)
     { if(c<0 || touched[c]!=0) return; touched[c]=1; int n=ArraySize(touch_queue);
       if(ArrayResize(touch_queue,n+1)==n+1) touch_queue[n]=c; else reason="Fila de ciclos sem memória"; }
   int NewCycle(const string symbol,const int side,const long seed,const long when,const string prefix)
     { int c=JPWLedgerNewCycle(cycles,symbol,side,seed,when,prefix); if(c<0) return(-1);
       previous_group[c]=groups.Get(GroupKey(symbol,side));
       if(!groups.Put(GroupKey(symbol,side),c)) return(-1); heads[c]=-1; Touch(c); return(c); }
   int Safe(const int c)
     { if(safe_epoch[c]!=batch_epoch) { safe_epoch[c]=batch_epoch; safe_count[c]=opens[c]; } return(safe_count[c]); }
   void SetMember(const int m,const double volume,const bool wait)
     {
      int c=members[m].cycle; bool before=members[m].volume>JPW_LEDGER_EPS,after=volume>JPW_LEDGER_EPS;
      Safe(c);
      if(before!=after) opens[c]+=(after ? 1 : -1);
      if(members[m].rollover_wait!=wait) rollovers[c]+=(wait ? 1 : -1);
      if(future_index.Get(members[m].identifier)<0)
        { Safe(c); if(before!=after) safe_count[c]+=(after ? 1 : -1); }
      members[m].volume=volume; members[m].rollover_wait=wait; Touch(c);
     }
   bool AmbiguousFlat(const int c,const int e,JPWLedgerDeal &deals[])
     {
      if(pendings[c]>0 || rollovers[c]>0 || Safe(c)>0) return(false);
      for(int m=heads[c];m>=0;m=next_member[m])
        {
         double remaining=members[m].volume;
         int f=future_index.Get(members[m].identifier);
         while(f>=0)
           { if(f>e) { JPWLedgerDeal d=deals[batch[f].index]; remaining-=d.volume; if(d.reason==1) return(false); }
             f=next_future[f]; }
         if(remaining>JPW_LEDGER_EPS) return(false);
        }
      return(true);
     }
   bool ReplayEvent(const int e,JPWLedgerDeal &deals[],JPWLedgerOrder &orders[])
     {
      JPWLedgerEvent event=batch[e];
      if(event.kind==0)
        {
         JPWLedgerOrder order=orders[event.index]; int c=Active(order.symbol,order.side);
         if(c<0) c=NewCycle(order.symbol,order.side,order.ticket,event.time_msc,"O"); if(c<0) return(false);
         order_cycle[event.index]=c; order_active[event.index]=1; pendings[c]++; Touch(c);
         if(order.state==4) { cycles[c].history_complete=false; cycles[c].reason="Estado de pendente não reconciliado"; }
        }
      else if(event.kind==2)
        {
         int c=order_cycle[event.index]; if(c<0) { reason="Pendente sem início"; return(false); }
         if(orders[event.index].state==3 && (execution_seen[event.index]==0 ||
            !JPWLedgerNear(executed_volume[event.index],orders[event.index].volume)))
           { cycles[c].history_complete=false; cycles[c].reason="Execução da pendente ainda não reconciliada"; }
         else { if(order_active[event.index]!=0) pendings[c]--; order_active[event.index]=0; Touch(c); }
        }
      else
        {
         JPWLedgerDeal deal=deals[event.index]; int m=member_index.Get(deal.position_id),c=(m>=0 ? members[m].cycle : -1);
         if(deal.kind==4)
           { if(deal.commission!=0 || deal.fee!=0 || deal.swap!=0) unassigned_cost=true; return(true); }
         if((deal.kind==1 || deal.kind==5) && deal.entry==0)
           {
            if(m<0)
              {
               int o=order_index.Get(deal.order_ticket); if(o>=0) c=order_cycle[o];
               if(c<0) c=Active(deal.symbol,deal.side);
               if(c>=0 && cycles[c].genesis_inferred && cycles[c].started_msc<deal.time_msc && AmbiguousFlat(c,e,deals))
                 { cycles[c].history_complete=false; cycles[c].genesis_ambiguous=true;
                   cycles[c].reason="Zeragem e nova entrada no mesmo milissegundo sem ordenação comprovada"; }
               if(c<0) c=NewCycle(deal.symbol,deal.side,deal.ticket,event.time_msc,"D"); if(c<0) return(false);
               m=ArraySize(members);
#ifdef __MQL5__
               if(ArrayResize(members,m+1,4096)!=m+1) return(false);
#else
               if(ArrayResize(members,m+1)!=m+1) return(false);
#endif
               if(!member_index.Put(deal.position_id,m)) return(false);
               members[m].identifier=deal.position_id; members[m].symbol=deal.symbol; members[m].side=deal.side;
               members[m].cycle=c; members[m].volume=0; members[m].rollover_wait=false;
               next_member[m]=heads[c]; heads[c]=m;
               if(deal.order_ticket!=deal.position_id)
                 { cycles[c].history_complete=false; cycles[c].reason="Ordem original de abertura ausente"; }
               if(cycles[c].genesis_deal==0)
                 { cycles[c].genesis_identifier=deal.position_id; cycles[c].genesis_deal=deal.ticket;
                   cycles[c].genesis_inferred=true; cycles[c].started_msc=deal.time_msc; }
               else if(cycles[c].started_msc==deal.time_msc && cycles[c].genesis_identifier!=deal.position_id)
                  cycles[c].genesis_ambiguous=true;
              }
            if(members[m].symbol!=deal.symbol || members[m].side!=deal.side)
              { cycles[c].history_complete=false; cycles[c].reason="Identificador reutilizado em outro grupo"; }
            SetMember(m,members[m].volume+deal.volume,false);
           }
         else if(deal.kind==1 || deal.kind==5)
           {
            if(m<0)
              { c=Active(deal.symbol,-deal.side); if(c<0) c=NewCycle(deal.symbol,-deal.side,deal.ticket,event.time_msc,"X");
                if(c<0) return(false); cycles[c].history_complete=false; cycles[c].reason="Saída sem abertura comprovada"; }
            else if(deal.entry==2 || members[m].side==deal.side || deal.volume>members[m].volume+JPW_LEDGER_EPS)
              { cycles[c].history_complete=false; cycles[c].reason="Volume/direção de saída não reconciliados"; }
            else
              { double volume=MathMax(0.0,members[m].volume-deal.volume);
                SetMember(m,volume,members[m].rollover_wait || (deal.reason==1 && volume<=JPW_LEDGER_EPS)); }
           }
         if(deal.kind==5 && linked[event.index]==0) canceled_unresolved=true;
         if(c>=0)
           { cycles[c].realized_price+=deal.profit; cycles[c].realized_swap+=deal.swap;
             cycles[c].commissions+=deal.commission; cycles[c].fees+=deal.fee; }
         else if(deal.kind==2 || deal.commission!=0 || deal.fee!=0 || deal.swap!=0) unassigned_cost=true;
        }
      return(reason=="");
     }
   void RecountOne(const int c,const long when)
     { cycles[c].open_positions=opens[c]; cycles[c].pending_orders=pendings[c];
       if(opens[c]>0) { cycles[c].state=1; cycles[c].ended_msc=0; }
       else if(pendings[c]>0) { cycles[c].state=2; cycles[c].ended_msc=0; }
       else if(rollovers[c]>0) { cycles[c].state=4; cycles[c].ended_msc=0; }
       else if(cycles[c].state!=3) { cycles[c].state=3; cycles[c].ended_msc=when; } touched[c]=0; }
public:
   bool Begin(JPWLedgerDeal &deals[],JPWLedgerOrder &orders[])
     {
      reason=""; stage=1; cursor=0; processed=0; batch_epoch=1; batch_cursor=0; touch_cursor=0;
      unassigned_cost=false; canceled_unresolved=false;
      ArrayResize(cycles,0); ArrayResize(members,0); ArrayResize(heap,0); ArrayResize(batch,0); ArrayResize(touch_queue,0);
      int nd=ArraySize(deals),no=ArraySize(orders);
      if(nd>JPW_LEDGER_MAX_RECORDS || no>JPW_LEDGER_MAX_RECORDS) { reason="Limite de histórico"; return(false); }
      if(!deal_index.Init() || !order_index.Init() || !member_index.Init() || !live_index.Init(2048) ||
         !future_index.Init() || !groups.Init()) return(false);
      if(ArrayResize(order_cycle,no)!=no || ArrayResize(order_active,no)!=no || ArrayResize(execution_seen,no)!=no ||
         ArrayResize(executed_volume,no)!=no || ArrayResize(linked,nd)!=nd || ArrayResize(next_member,nd)!=nd) return(false);
      ArrayInitialize(order_cycle,-1); ArrayInitialize(order_active,0); ArrayInitialize(execution_seen,0);
      ArrayInitialize(executed_volume,0); ArrayInitialize(linked,0);
      if(ArrayResize(heads,JPW_LEDGER_MAX_CYCLES)!=JPW_LEDGER_MAX_CYCLES ||
         ArrayResize(previous_group,JPW_LEDGER_MAX_CYCLES)!=JPW_LEDGER_MAX_CYCLES ||
         ArrayResize(opens,JPW_LEDGER_MAX_CYCLES)!=JPW_LEDGER_MAX_CYCLES || ArrayResize(pendings,JPW_LEDGER_MAX_CYCLES)!=JPW_LEDGER_MAX_CYCLES ||
         ArrayResize(rollovers,JPW_LEDGER_MAX_CYCLES)!=JPW_LEDGER_MAX_CYCLES || ArrayResize(touched,JPW_LEDGER_MAX_CYCLES)!=JPW_LEDGER_MAX_CYCLES ||
         ArrayResize(safe_epoch,JPW_LEDGER_MAX_CYCLES)!=JPW_LEDGER_MAX_CYCLES || ArrayResize(safe_count,JPW_LEDGER_MAX_CYCLES)!=JPW_LEDGER_MAX_CYCLES ||
         ArrayResize(csv_length,JPW_LEDGER_MAX_CYCLES)!=JPW_LEDGER_MAX_CYCLES || ArrayResize(csv_offset,JPW_LEDGER_MAX_CYCLES)!=JPW_LEDGER_MAX_CYCLES ||
         ArrayResize(csv_cursor,JPW_LEDGER_MAX_CYCLES)!=JPW_LEDGER_MAX_CYCLES) return(false);
      ArrayInitialize(heads,-1); ArrayInitialize(opens,0); ArrayInitialize(pendings,0); ArrayInitialize(rollovers,0);
      ArrayInitialize(touched,0); ArrayInitialize(safe_epoch,0); ArrayInitialize(safe_count,0);
      ArrayInitialize(csv_length,0); ArrayInitialize(csv_cursor,0); return(true);
     }
   // One input record/event is the cooperative unit. Native calls are measured
   // by the caller; deadline does not preempt a terminal/SQLite/builtin call.
   bool Step(JPWLedgerDeal &deals[],JPWLedgerOrder &orders[],const ulong deadline,bool &ready)
     {
      ready=false;
      while(GetTickCount64()<deadline)
        {
         if(stage==1)
           {
            if(cursor>=ArraySize(orders)) { stage=2; cursor=0; continue; }
            JPWLedgerOrder o=orders[cursor];
            if(o.ticket<=0 || o.setup_msc<=0 || o.symbol=="" || (o.side!=1 && o.side!=-1) || o.state<1 || o.state>4 ||
               !JPWLedgerFinite(o.volume) || o.volume<0 || order_index.Get(o.ticket)>=0 || !order_index.Put(o.ticket,cursor))
              { reason="Pendente inválida/duplicada"; return(false); }
            JPWLedgerEvent e; e.time_msc=o.setup_msc; e.ticket=o.ticket; e.kind=0; e.index=cursor;
            if(!Push(e)) return(false);
            if(o.state==2 || o.state==3) { if(o.done_msc<o.setup_msc) return(false); e.time_msc=o.done_msc; e.kind=2; if(!Push(e)) return(false); }
            cursor++; processed++; continue;
           }
         if(stage==2)
           {
            if(cursor>=ArraySize(deals)) { stage=3; cursor=0; continue; }
            JPWLedgerDeal d=deals[cursor];
            if(!JPWLedgerDealValid(d) || deal_index.Get(d.ticket)>=0 || !deal_index.Put(d.ticket,cursor))
              { reason="Deal inválido/duplicado"; return(false); }
            if(!d.deleted) { JPWLedgerEvent e; e.time_msc=d.time_msc; e.ticket=d.ticket; e.kind=1; e.index=cursor; if(!Push(e)) return(false); }
            cursor++; processed++; continue;
           }
         if(stage==3)
           {
            if(cursor>=ArraySize(deals)) { stage=4; cursor=0; continue; }
            JPWLedgerDeal d=deals[cursor]; int o=order_index.Get(d.order_ticket);
            // Same ticket-ordered summation as the compatibility builder.
            if(!d.deleted && d.kind==1 && o>=0 && d.time_msc<=orders[o].done_msc)
              { execution_seen[o]=1; executed_volume[o]+=d.volume; }
            int a=deal_index.Get(d.adjustment_of);
            if(!d.deleted && (d.kind==2 || d.kind==3) && a>=0 && d.position_id>0 &&
               d.position_id==deals[a].position_id && d.time_msc>=deals[a].time_msc) linked[a]=1;
            cursor++; processed++; continue;
           }
         if(stage==4)
           {
            if(ArraySize(heap)==0) { stage=8; ready=true; return(true); }
            if(ArraySize(batch)==0) { future_index.Clear(); batch_epoch++; batch_cursor=0; }
            JPWLedgerEvent e;
            if(ArraySize(batch)>0 && heap[0].time_msc!=batch[0].time_msc)
              { if(ArrayResize(next_future,ArraySize(batch))!=ArraySize(batch)) return(false);
                ArrayInitialize(next_future,-1); stage=5; cursor=ArraySize(batch)-1; continue; }
            if(!Pop(e)) return(false); int n=ArraySize(batch);
#ifdef __MQL5__
            if(ArrayResize(batch,n+1,2048)!=n+1) return(false);
#else
            if(ArrayResize(batch,n+1)!=n+1) return(false);
#endif
            batch[n]=e;
            if(ArraySize(heap)==0) { if(ArrayResize(next_future,ArraySize(batch))!=ArraySize(batch)) return(false);
              ArrayInitialize(next_future,-1); stage=5; cursor=ArraySize(batch)-1; } continue;
           }
         if(stage==5)
           {
            if(cursor<0) { stage=6; batch_cursor=0; continue; }
            JPWLedgerEvent e=batch[cursor];
            if(e.kind==1) { JPWLedgerDeal d=deals[e.index]; if((d.kind==1 || d.kind==5) && d.entry!=0)
              { int prior=future_index.Get(d.position_id); next_future[cursor]=prior;
                if(prior<0) { int m=member_index.Get(d.position_id); if(m>=0 && members[m].volume>JPW_LEDGER_EPS)
                    { int c=members[m].cycle; Safe(c); safe_count[c]--; } }
                if(!future_index.Put(d.position_id,cursor)) return(false); } }
            cursor--; continue;
           }
         if(stage==6)
           { if(batch_cursor>=ArraySize(batch)) { stage=7; touch_cursor=0; continue; }
             if(!ReplayEvent(batch_cursor,deals,orders)) return(false); batch_cursor++; processed++; continue; }
         if(stage==7)
           { if(touch_cursor>=ArraySize(touch_queue)) { ArrayResize(touch_queue,0); ArrayResize(batch,0); stage=4; continue; }
             RecountOne(touch_queue[touch_cursor++],batch[0].time_msc); continue; }
         if(stage==8) { ready=true; return(true); }
         reason="Etapa de replay inválida"; return(false);
        }
      return(true);
     }
   bool BeginLive(JPWLedgerPosition &live[])
     {
      if(!live_index.Init(2048)) return(false);
      for(int p=0;p<ArraySize(live);p++)
        { if(live[p].identifier<=0 || live[p].ticket<=0 || live[p].opened_msc<=0 || live[p].symbol=="" ||
             (live[p].side!=1 && live[p].side!=-1) || !JPWLedgerFinite(live[p].volume) || live[p].volume<=0 ||
             !JPWLedgerFinite(live[p].profit) || !JPWLedgerFinite(live[p].swap) || live_index.Get(live[p].identifier)>=0 ||
             !live_index.Put(live[p].identifier,p)) { reason="Identificador/P&L vivo inválido ou duplicado"; return(false); } }
      for(int c=0;c<ArraySize(cycles);c++) { cycles[c].unrealized_price=0; cycles[c].unrealized_swap=0; }
      stage=9; cursor=0; return(true);
     }
   bool LiveStep(JPWLedgerPosition &live[],JPWLedgerView &view,const ulong deadline,bool &ready)
     {
      ready=false;
      if(view.margin_mode!=JPW_LEDGER_HEDGING) { reason="Hedging requerido; netting/exchange N/A"; return(false); }
      while(GetTickCount64()<deadline)
        {
         if(stage==9)
           {
            if(cursor>=ArraySize(members)) { stage=10; cursor=0; continue; }
            int m=cursor++,c=members[m].cycle,found=live_index.Get(members[m].identifier);
            if(members[m].rollover_wait || (found<0 && members[m].volume>JPW_LEDGER_EPS) ||
               (found>=0 && (live[found].symbol!=members[m].symbol || live[found].side!=members[m].side ||
                            !JPWLedgerNear(live[found].volume,members[m].volume))))
              { cycles[c].history_complete=false; cycles[c].reason="Volume vivo/histórico não reconciliado"; }
            if(found>=0) { cycles[c].unrealized_price+=live[found].profit; cycles[c].unrealized_swap+=live[found].swap; }
            csv_length[c]+=StringLen(IntegerToString(members[m].identifier))+1;
            JPWLedgerEvent e; e.time_msc=members[m].identifier; e.ticket=members[m].identifier; e.kind=0; e.index=m;
            if(!Push(e)) return(false); continue;
           }
         if(stage==10)
           { if(cursor>=ArraySize(live)) { stage=11; cursor=0; continue; }
             if(member_index.Get(live[cursor++].identifier)<0) { reason="Posição viva sem origem no histórico"; return(false); } continue; }
         if(stage==11)
           {
            if(cursor>=ArraySize(cycles)) { int total=(ArraySize(cycles)>0 ? csv_offset[cursor-1]+csv_length[cursor-1] : 0);
              if(ArrayResize(csv,total)!=total) return(false); stage=12; continue; }
            if(csv_length[cursor]>0) csv_length[cursor]--; // no trailing comma
            csv_offset[cursor]=(cursor==0 ? 0 : csv_offset[cursor-1]+csv_length[cursor-1]); cursor++; continue;
           }
         if(stage==12)
           {
            if(ArraySize(heap)==0) { stage=13; cursor=0; continue; }
            JPWLedgerEvent e; if(!Pop(e)) return(false); int c=members[e.index].cycle;
            string id=IntegerToString(members[e.index].identifier);
            if(csv_cursor[c]>0) csv[csv_offset[c]+csv_cursor[c]++]=44;
            for(int j=0;j<StringLen(id);j++) csv[csv_offset[c]+csv_cursor[c]++]=(uchar)StringGetCharacter(id,j);
            continue;
           }
         if(stage==13)
           {
            if(cursor>=ArraySize(cycles)) { view.costs_complete=view.costs_complete && !unassigned_cost && !canceled_unresolved;
              stage=14; ready=true; return(true); }
            int c=cursor++;
            if(csv_cursor[c]!=csv_length[c]) { reason="Projeção de membros inconsistente"; return(false); }
            cycles[c].members_available=true;
            cycles[c].member_identifiers=(csv_length[c]>0 ? CharArrayToString(csv,csv_offset[c],csv_length[c],CP_UTF8) : "");
            cycles[c].history_complete=cycles[c].history_complete && view.history_complete;
            cycles[c].costs_complete=view.costs_complete && !unassigned_cost && !canceled_unresolved;
            cycles[c].partial=!cycles[c].costs_complete || !cycles[c].history_complete;
            cycles[c].compensated=cycles[c].realized_price+cycles[c].realized_swap+
               cycles[c].commissions+cycles[c].fees+cycles[c].unrealized_price+cycles[c].unrealized_swap;
            cycles[c].amount_valid=cycles[c].genesis_inferred && cycles[c].history_complete && JPWLedgerFinite(cycles[c].compensated);
            cycles[c].percent_valid=cycles[c].amount_valid && JPWLedgerFinite(view.balance) && view.balance>0;
            if(cycles[c].percent_valid) cycles[c].percent=100.0*(cycles[c].compensated/view.balance);
            if(!JPWLedgerFinite(cycles[c].percent)) { cycles[c].percent=0; cycles[c].percent_valid=false; }
            if(!cycles[c].costs_complete && cycles[c].reason=="") cycles[c].reason="Custos/ajustes não integralmente atribuídos; subtotal parcial";
            if(!cycles[c].history_complete && view.reason!="" && cycles[c].reason=="") cycles[c].reason=view.reason;
            if(!cycles[c].history_complete && cycles[c].state==3) cycles[c].state=4;
            if(!cycles[c].genesis_inferred)
              { cycles[c].state=4; cycles[c].amount_valid=false; cycles[c].percent_valid=false;
                cycles[c].reason="Pendente antes da primeira execução; ciclo contábil não iniciado"; }
            if(cycles[c].genesis_ambiguous)
              { cycles[c].genesis_identifier=0; cycles[c].genesis_deal=0;
                if(cycles[c].reason=="") cycles[c].reason="Primeira execução no mesmo milissegundo ambígua"; }
            if(!JPWLedgerMemberListValid(cycles[c])) { reason="Estado final de membros inconsistente"; return(false); }
            continue;
           }
         if(stage==14) { ready=true; return(true); }
         reason="Etapa viva inválida"; return(false);
        }
      return(true);
     }
  };
// Resumable reconciliation: no main cursor or transaction survives Step().
// Every historic slice reacquires its exact selection. Three content passes use
// canonical payloads and rolling digests, not merely counts or maximum ticket.
class CJPWLedgerPreparation
  {
public:
   CJPWLedgerReplay replay;
   JPWLedgerView view;
   JPWLedgerDeal deals[];
   JPWLedgerOrder orders[];
   JPWLedgerPosition live[];
   string reason,composition;
   int stage,progress;
private:
   int db,cursor,old_projection_count,old_projection_cursor,source_deal_count,source_order_count;
   long row_cursor,base_generation;
   string key,token,declared_account,evidence,base_payload,base_digest,first_composition,history_hash,verified_hash;
   bool history_confirmed,costs_confirmed,queue_loss,first_fresh;
   datetime history_end;
   long deletes[],source_deal_ids[],source_order_ids[];
   JPWLedgerOrder active[];
   CJPWLedgerLongIndex previous_members;
   CJPWLedgerGroupIndex previous_cycles;

   bool Identity()
     { string actual="",currency="";
       if(!JPWLedgerIdentity(actual,currency) || actual!=key || currency!=view.currency)
         { reason="Conta mudou/indisponível; rascunho descartado"; return(false); } return(true); }
   bool HashRecord(string &hash,const string raw)
     { string next=""; if(!JPWRaizNHash(hash+"|"+JPWRaizNFrame(raw),next)) return(false); hash=next; return(true); }
   bool SelectSource()
     {
      if(!Identity() || history_end<=0 || !HistorySelect(0,history_end)) { if(reason=="") reason="Seleção compartilhada indisponível"; return(false); }
      if(HistoryDealsTotal()!=source_deal_count || HistoryOrdersTotal()!=source_order_count)
        { reason="Conjunto histórico mudou entre fatias; tentativa invalidada"; return(false); }
      return(true);
     }
   bool Base()
     {
      if(!JPWLedgerPreparationTables(db,reason)) return(false);
      int q=DatabasePrepare(db,"PRAGMA quick_check"); string status="";
      bool ok=q!=INVALID_HANDLE && DatabaseRead(q) && DatabaseColumnText(q,0,status) && status=="ok";
      if(q!=INVALID_HANDLE) DatabaseFinalize(q); if(!ok) { reason="Integridade SQLite recusada; nenhum reset"; return(false); }
      q=DatabasePrepare(db,"SELECT generation,payload,digest FROM main.ledger_meta WHERE id=1 AND account_key=?1");
      ok=q!=INVALID_HANDLE && DatabaseBind(q,0,key) && DatabaseRead(q) && DatabaseColumnLong(q,0,base_generation) &&
         DatabaseColumnText(q,1,base_payload) && DatabaseColumnText(q,2,base_digest) && base_generation>=0 && base_generation<LONG_MAX-1;
      if(q!=INVALID_HANDLE) DatabaseFinalize(q); if(!ok) return(false);
      old_projection_count=0; old_projection_cursor=0;
      if(base_generation>0)
        { JPWLedgerView old; string digest="",old_composition="";
          if(!JPWRaizNHash(base_payload,digest) || digest!=base_digest ||
             !JPWLedgerDecodeView(base_payload,old,old_projection_count,old_composition) || old.generation!=base_generation || old.account_key!=key)
            { reason="Projeção anterior corrompida; nenhuma substituição"; return(false); } }
      if(!previous_members.Init() || !previous_cycles.Init()) return(false);
      row_cursor=0; stage=1; return(true);
     }
   bool OldRows(const int table,const ulong deadline,bool &done)
     {
      done=false; string sql="SELECT ticket,revision,payload,digest,observed FROM ";
      sql+=(table==0 ? "main.ledger_deals" : "main.ledger_orders"); sql+=" WHERE ticket>?1 ORDER BY ticket LIMIT 64";
      int q=DatabasePrepare(db,sql);
      if(q==INVALID_HANDLE || !DatabaseBind(q,0,row_cursor)) { if(q!=INVALID_HANDLE) DatabaseFinalize(q); return(false); }
      int read=0; bool ok=true; ResetLastError();
      while(GetTickCount64()<deadline && DatabaseRead(q))
        {
         long ticket=0,revision=0,observed=0; string raw="",digest="";
         ok=DatabaseColumnLong(q,0,ticket) && DatabaseColumnLong(q,1,revision) && DatabaseColumnText(q,2,raw) &&
            DatabaseColumnText(q,3,digest) && DatabaseColumnLong(q,4,observed);
         if(ok && table==0) { JPWLedgerDeal d; ok=JPWLedgerDecodeDeal(raw,d) && d.ticket==ticket; }
         if(ok && table==1) { JPWLedgerOrder o; ok=JPWLedgerDecodeOrder(raw,o) && o.ticket==ticket; }
         if(ok) ok=JPWLedgerStageOld(db,table,ticket,revision,raw,digest,observed);
         if(!ok) break; row_cursor=ticket; read++; cursor++;
         if(cursor>JPW_LEDGER_MAX_RECORDS) { ok=false; reason="Histórico local excessivo"; break; }
         ResetLastError();
        }
      if(ok && GetLastError()==ERR_DATABASE_NO_MORE_DATA) done=true;
      else if(ok && GetLastError()!=0) ok=false;
      DatabaseFinalize(q);
      if(!ok && reason=="") reason="Histórico local corrompido/ocupado; nenhuma alteração";
      return(ok);
     }
   bool OldProjection(const ulong deadline,bool &done)
     {
      done=false; if(base_generation==0) { done=true; return(true); }
      int q=DatabasePrepare(db,"SELECT rowno,payload,digest FROM main.ledger_projection WHERE generation=?1 AND rowno>=?2 ORDER BY rowno LIMIT 16");
      bool ok=q!=INVALID_HANDLE && DatabaseBind(q,0,base_generation) && DatabaseBind(q,1,old_projection_cursor);
      if(!ok) { if(q!=INVALID_HANDLE) DatabaseFinalize(q); return(false); }
      ResetLastError();
      while(GetTickCount64()<deadline && DatabaseRead(q))
        {
         int row=0; string raw="",digest="",actual=""; JPWLedgerCycle c;
         ok=DatabaseColumnInteger(q,0,row) && row==old_projection_cursor && row<old_projection_count &&
            DatabaseColumnText(q,1,raw) && DatabaseColumnText(q,2,digest) && JPWRaizNHash(raw,actual) && actual==digest && JPWLedgerDecodeCycle(raw,c);
         if(ok) ok=previous_cycles.Get(c.cycle_id)<0 && previous_cycles.Put(c.cycle_id,row);
         if(ok)
           { JPWLedgerView old; string old_comp=""; int ignored=0;
             ok=JPWLedgerDecodeView(base_payload,old,ignored,old_comp) && (!c.percent_valid ||
                (c.amount_valid && old.balance>0 && JPWLedgerNear(c.percent,100.0*(c.compensated/old.balance)))); }
         if(ok && c.member_identifiers!="")
           { string ids[]; int n=StringSplit(c.member_identifiers,',',ids);
             for(int i=0;ok && i<n;i++) { long id=StringToInteger(ids[i]); ok=previous_members.Get(id)<0 && previous_members.Put(id,row); } }
         if(ok) ok=JPWLedgerStageProjection(db,row,raw,true);
         if(!ok) break; old_projection_cursor++; ResetLastError();
        }
      if(ok && GetLastError()==ERR_DATABASE_NO_MORE_DATA)
        { done=true; ok=(old_projection_cursor==old_projection_count); }
      else if(ok && GetLastError()!=0) ok=false;
      DatabaseFinalize(q); if(!ok) reason="Geração anterior incompleta/corrompida; preservada"; return(ok);
     }
   bool SourceBegin()
     {
      if(!Identity() || !JPWLedgerAccountDouble(ACCOUNT_BALANCE,view.balance)) return(false);
      view.margin_mode=AccountInfoInteger(ACCOUNT_MARGIN_MODE);
      if(view.margin_mode!=ACCOUNT_MARGIN_MODE_RETAIL_HEDGING) { reason="Ledger v1 requer hedging; demais módulos independentes"; return(false); }
      if(!JPWLedgerReadLive(live,active,first_fresh,reason) ||
         !JPWLedgerComposition(live,active,key,view.balance,view.margin_mode,first_composition)) return(false);
      history_end=TimeTradeServer(); if(history_end<=0) history_end=TimeCurrent();
      if(history_end<=0 || !HistorySelect(0,history_end)) { reason="Histórico indisponível"; return(false); }
      source_deal_count=HistoryDealsTotal(); source_order_count=HistoryOrdersTotal();
      if(source_deal_count<0 || source_deal_count>JPW_LEDGER_MAX_RECORDS || source_order_count<0 || source_order_count>JPW_LEDGER_MAX_RECORDS)
        { reason="Histórico fora do limite explícito"; return(false); }
      if(ArrayResize(source_deal_ids,source_deal_count)!=source_deal_count || ArrayResize(source_order_ids,source_order_count)!=source_order_count) return(false);
      if(!JPWRaizNHash("H|"+key+"|"+IntegerToString((long)history_end),history_hash)) return(false);
      verified_hash=history_hash; cursor=0; stage=5; return(true);
     }
   bool NativeOne(const int table,const bool verify)
     {
      ulong ticket=(table==0 ? HistoryDealGetTicket(cursor) : HistoryOrderGetTicket(cursor));
      if(ticket==0 || ticket>(ulong)LONG_MAX) { reason="Identidade histórica inválida"; return(false); }
      string raw=""; bool relevant=true;
      if(table==0) { JPWLedgerDeal d; if(!JPWLedgerReadDeal(ticket,d)) return(false); raw=JPWLedgerEncodeDeal(d); }
      else { JPWLedgerOrder o; if(!JPWLedgerReadOrder(ticket,true,o,relevant)) return(false);
         raw=(relevant ? JPWLedgerEncodeOrder(o) : "NON_PENDING|"+IntegerToString((long)ticket)); }
      if(verify)
        {
         long expected=(table==0 ? source_deal_ids[cursor] : source_order_ids[cursor]);
         if(expected!=(long)ticket) { reason="Seleção/conjunto histórico mudou; tentativa invalidada"; return(false); }
         if(relevant && !JPWLedgerStageWitness(db,table,(long)ticket,raw,reason)) return(false);
         if(!HashRecord(verified_hash,raw)) return(false);
        }
      else
        {
         if(table==0) source_deal_ids[cursor]=(long)ticket; else source_order_ids[cursor]=(long)ticket;
         if(relevant && !JPWLedgerStageRaw(db,table,(long)ticket,raw,1,reason)) return(false);
         if(!HashRecord(history_hash,raw)) return(false);
        }
      cursor++; return(true);
     }
   bool Missing(const int table,const ulong deadline,bool &done)
     {
      done=false; string sql="SELECT ticket,payload FROM "; sql+=JPWLedgerPreparationTable(table,false);
      sql+=" WHERE seen=0 AND ticket>?1 ORDER BY ticket LIMIT 64";
      int q=DatabasePrepare(db,sql); bool ok=q!=INVALID_HANDLE && DatabaseBind(q,0,row_cursor);
      if(!ok) { if(q!=INVALID_HANDLE) DatabaseFinalize(q); return(false); }
      ResetLastError();
      while(GetTickCount64()<deadline && DatabaseRead(q))
        {
         long ticket=0; string raw="";
         ok=DatabaseColumnLong(q,0,ticket) && DatabaseColumnText(q,1,raw);
         if(ok && table==0) { JPWLedgerDeal d; ok=JPWLedgerDecodeDeal(raw,d); if(ok && !d.deleted) view.history_complete=false; }
         if(ok && table==1) { JPWLedgerOrder o; ok=JPWLedgerDecodeOrder(raw,o);
           if(ok && (o.state==1 || o.state==4)) { o.state=4; o.done_msc=0; view.history_complete=false;
             ok=JPWLedgerStageRaw(db,1,ticket,JPWLedgerEncodeOrder(o),0,reason); } }
         if(!ok) break; row_cursor=ticket; ResetLastError();
        }
      if(ok && GetLastError()==ERR_DATABASE_NO_MORE_DATA) done=true;
      else if(ok && GetLastError()!=0) ok=false;
      DatabaseFinalize(q); return(ok);
     }
   bool MergedRows(const int table,const ulong deadline,bool &done)
     {
      done=false; string sql="SELECT ticket,payload,digest FROM "; sql+=JPWLedgerPreparationTable(table,false);
      sql+=" WHERE ticket>?1 ORDER BY ticket LIMIT 64";
      int q=DatabasePrepare(db,sql); bool ok=q!=INVALID_HANDLE && DatabaseBind(q,0,row_cursor);
      if(!ok) { if(q!=INVALID_HANDLE) DatabaseFinalize(q); return(false); }
      ResetLastError();
      while(GetTickCount64()<deadline && DatabaseRead(q))
        {
         long ticket=0; string raw="",digest="",actual="";
         ok=DatabaseColumnLong(q,0,ticket) && DatabaseColumnText(q,1,raw) && DatabaseColumnText(q,2,digest) &&
            JPWRaizNHash(raw,actual) && digest==actual;
         if(ok && table==0)
           { JPWLedgerDeal d; int n=ArraySize(deals); ok=n<JPW_LEDGER_MAX_RECORDS && JPWLedgerDecodeDeal(raw,d) && d.ticket==ticket;
#ifdef __MQL5__
             if(ok) ok=ArrayResize(deals,n+1,4096)==n+1;
#else
             if(ok) ok=ArrayResize(deals,n+1)==n+1;
#endif
             if(ok) deals[n]=d; }
         if(ok && table==1)
           { JPWLedgerOrder o; int n=ArraySize(orders); ok=n<JPW_LEDGER_MAX_RECORDS && JPWLedgerDecodeOrder(raw,o) && o.ticket==ticket;
#ifdef __MQL5__
             if(ok) ok=ArrayResize(orders,n+1,4096)==n+1;
#else
             if(ok) ok=ArrayResize(orders,n+1)==n+1;
#endif
             if(ok) orders[n]=o; }
         if(!ok) break; row_cursor=ticket; ResetLastError();
        }
      if(ok && GetLastError()==ERR_DATABASE_NO_MORE_DATA) done=true;
      else if(ok && GetLastError()!=0) ok=false;
      DatabaseFinalize(q); if(!ok && reason=="") reason="Conjunto bruto excessivo/inválido"; return(ok);
     }
   bool CaptureLive()
     {
      JPWLedgerOrder pending[]; JPWLedgerPosition positions[]; bool fresh=false; double balance=0;
      if(!Identity() || !JPWLedgerAccountDouble(ACCOUNT_BALANCE,balance) || balance!=view.balance ||
         AccountInfoInteger(ACCOUNT_MARGIN_MODE)!=view.margin_mode || !JPWLedgerReadLive(positions,pending,fresh,reason) ||
         !JPWLedgerComposition(positions,pending,key,balance,view.margin_mode,composition) || composition!=first_composition)
        { if(reason=="") reason="Conta/composição mudou durante preparação"; return(false); }
      if(ArrayResize(live,ArraySize(positions))!=ArraySize(positions)) return(false);
      for(int i=0;i<ArraySize(positions);i++) live[i]=positions[i];
      view.observed_utc=(long)TimeGMT(); view.observed_mono_ms=(long)GetTickCount64();
      view.quality=(TerminalInfoInteger(TERMINAL_CONNECTED)!=0 && first_fresh && fresh &&
         MathAbs((double)((long)TimeTradeServer()-(long)TimeCurrent()))<=30 ? 1 : 2);
      view.healthy=true;
      // Coverage was declared before absence/fault reconciliation. Keep its
      // lowered flags; only refresh the diagnostic observation instant.
      if(view.observed_utc<=0 || view.observed_mono_ms<=0) return(false);
      return(replay.BeginLive(live));
     }
public:
   void Abort()
     { stage=-1; progress=0; ArrayResize(deals,0); ArrayResize(orders,0); ArrayResize(live,0);
       ArrayResize(source_deal_ids,0); ArrayResize(source_order_ids,0); }
   bool Begin(const int handle,const string account,const string publisher,const string declaration_account,
              const bool history,const bool costs,const string reference,long &known_deletes[],const bool lost)
     {
      Abort(); db=handle; key=account; token=publisher; declared_account=declaration_account;
      history_confirmed=history; costs_confirmed=costs; evidence=reference; queue_loss=lost;
      JPWLedgerClearView(view); view.account_key=key; view.publisher_token=token;
      string actual="";
      if(!JPWLedgerIdentity(actual,view.currency) || actual!=key || db==INVALID_HANDLE) { reason="Contexto contábil indisponível"; return(false); }
      if(ArrayResize(deletes,ArraySize(known_deletes))!=ArraySize(known_deletes)) return(false);
      for(int i=0;i<ArraySize(known_deletes);i++) deletes[i]=known_deletes[i];
      reason=""; stage=0; progress=0; cursor=0; row_cursor=0; return(true);
     }
   bool Step(const ulong deadline,bool &ready)
     {
      ready=false; if(stage<0 || !Identity()) return(false); bool selected=false;
      while(GetTickCount64()<deadline)
        {
         bool done=false;
         if(stage==0) { if(!Base()) return(false); cursor=0; continue; }
         if(stage==1 || stage==2)
           { if(!OldRows(stage-1,deadline,done)) return(false);
             if(done) { stage++; row_cursor=0; cursor=0; } continue; }
         if(stage==3) { if(!OldProjection(deadline,done)) return(false); if(done) stage=4; continue; }
         if(stage==4) { if(!SourceBegin()) return(false); selected=true; continue; }
         if(stage==5 || stage==6 || stage==14 || stage==15 || stage==20 || stage==21)
           {
            if(!selected) { if(!SelectSource()) return(false); selected=true; }
            bool verify=stage>=14; int table=(stage==5 || stage==14 || stage==20 ? 0 : 1);
            int total=(table==0 ? source_deal_count : source_order_count);
            if(cursor>=total)
              { cursor=0; stage++;
                if(stage==7) { view.observed_utc=(long)TimeGMT();
                  JPWLedgerApplyDeclaredCoverage(view,history_confirmed,costs_confirmed,evidence,declared_account); }
                if((stage==16 || stage==22) && verified_hash!=history_hash) { reason="Hash histórico divergente; tentativa invalidada"; return(false); }
                continue; }
            if(!NativeOne(table,verify)) { if(reason=="") reason="Campos históricos incompletos"; return(false); } continue;
           }
         if(stage==7)
           { if(cursor>=ArraySize(active)) { stage=8; cursor=0; continue; }
             if(!JPWLedgerStageRaw(db,1,active[cursor].ticket,JPWLedgerEncodeOrder(active[cursor]),2,reason)) return(false);
             cursor++; continue; }
         if(stage==8)
           { if(cursor>=ArraySize(deletes)) { if(queue_loss && !JPWLedgerSQL(db,"INSERT OR IGNORE INTO temp.jpw_faults VALUES(0,'DELETE_ORIGIN_UNKNOWN')")) return(false);
               stage=9; cursor=0; row_cursor=0; continue; }
             if(!JPWLedgerStageDelete(db,deletes[cursor++],reason)) return(false); continue; }
         if(stage==9)
           { if(!Missing(cursor,deadline,done)) return(false);
             if(done) { cursor++; row_cursor=0; if(cursor==2) { stage=10; cursor=0; } } continue; }
         if(stage==10 || stage==11)
           { if(!MergedRows(stage-10,deadline,done)) return(false);
             if(done) { stage++; row_cursor=0; } continue; }
         if(stage==12)
           { long faults=0; if(!JPWLedgerStageScalar(db,"SELECT COUNT(*) FROM temp.jpw_faults",faults)) return(false);
             if(faults>0) view.history_complete=false;
             if(!replay.Begin(deals,orders)) { reason=replay.reason; return(false); } stage=13; continue; }
         if(stage==13)
           { if(!replay.Step(deals,orders,deadline,done)) { reason=replay.reason; return(false); }
             if(done) { stage=14; cursor=0; selected=false; } continue; }
         if(stage==16) { if(!CaptureLive()) return(false); stage=17; continue; }
         if(stage==17)
           { if(!replay.LiveStep(live,view,deadline,done)) { reason=replay.reason; return(false); }
             if(done) { stage=18; cursor=0; } continue; }
         if(stage==18)
           { if(cursor>=ArraySize(replay.cycles))
               { // Recheck costs/corrections after live projection and encoding.
                 // Native transaction epoch also invalidates any later change.
                 stage=20; cursor=0; selected=false;
                 if(!JPWRaizNHash("H|"+key+"|"+IntegerToString((long)history_end),verified_hash)) return(false);
                 continue; }
             if(!JPWLedgerStageProjection(db,cursor,JPWLedgerEncodeCycle(replay.cycles[cursor]),false)) return(false);
             cursor++; continue; }
         if(stage==22) { ready=true; progress=100; return(true); }
         reason="Etapa de preparação inválida"; return(false);
        }
      // Progress is preparation, never historical coverage/completeness.
      progress=(int)MathMin(99,MathMax(0,stage*4)); return(true);
     }
   bool RevalidateLive()
     {
      JPWLedgerPosition positions[]; JPWLedgerOrder pending[]; bool fresh=false; string current=""; double balance=0;
      if(!Identity() || !JPWLedgerAccountDouble(ACCOUNT_BALANCE,balance) || balance!=view.balance ||
         AccountInfoInteger(ACCOUNT_MARGIN_MODE)!=view.margin_mode ||
         !JPWLedgerReadLive(positions,pending,fresh,reason) ||
         !JPWLedgerComposition(positions,pending,key,balance,view.margin_mode,current) || current!=composition)
        { if(reason=="") reason="Composição/contexto mudou antes da publicação"; return(false); }
      if(!fresh || TerminalInfoInteger(TERMINAL_CONNECTED)==0 || GetTickCount64()<(ulong)view.observed_mono_ms ||
         GetTickCount64()-(ulong)view.observed_mono_ms>JPW_LEDGER_MAX_AGE_MS) view.quality=2;
      return(true);
     }
   bool Publish()
     { if(stage!=22 || !SelectSource() || !RevalidateLive()) return(false);
       return(JPWLedgerPublishPrepared(db,view,composition,ArraySize(replay.cycles),base_generation,base_payload,base_digest,reason)); }
  };
#endif
