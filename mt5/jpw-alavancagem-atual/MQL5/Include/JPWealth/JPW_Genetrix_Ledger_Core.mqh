#ifndef JPW_GENETRIX_LEDGER_CORE_MQH
#define JPW_GENETRIX_LEDGER_CORE_MQH
// Pure chronological accounting. No terminal, files, orders or UI effects.
// Signed money stays in ACCOUNT_CURRENCY. Costs are booked at their deal,
// including the entire entry commission; no second partial-volume allocation.
#define JPW_LEDGER_MAX_RECORDS 50000
#define JPW_LEDGER_MAX_CYCLES 4096
#define JPW_LEDGER_HEDGING 2
#define JPW_LEDGER_EPS 0.00000001

struct JPWLedgerDeal
  {
   long ticket,order_ticket,position_id,time_msc,adjustment_of;
   string symbol;
   int kind; // 1 trade, 2 account cost/correction, 3 balance, 4 credit, 5 canceled trade
   int side,entry,reason; // normalized side +/-1; native entry; 1 means rollover
   double volume,profit,swap,commission,fee;
   int deleted; // only an explicitly witnessed delete; never inferred from absence
   // adjustment_of is an explicitly evidenced cancellation correction link;
   // same position_id alone does not establish which deal was corrected.
  };
struct JPWLedgerOrder
  {
   long ticket,setup_msc,done_msc;
   string symbol;
   int side,state; // 1 active, 2 canceled/expired/rejected, 3 filled, 4 unresolved
   double volume;
  };
struct JPWLedgerPosition
  {
   long identifier,ticket,opened_msc;
   string symbol;
   int side;
   double volume,profit,swap;
  };
struct JPWLedgerCycle
  {
   string cycle_id,symbol;
   int side;
   long genesis_identifier,genesis_deal,started_msc,ended_msc;
   int state; // 1 positions, 2 only pendings, 3 accounting closed, 4 unconfirmed
   bool genesis_inferred,genesis_ambiguous;
   double realized_price,realized_swap,commissions,fees;
   double unrealized_price,unrealized_swap,compensated,percent;
   bool amount_valid,percent_valid,partial,history_complete,costs_complete;
   int open_positions,pending_orders;
   string reason;
   string member_identifiers; // all observed members, numeric ascending CSV of POSITION_IDENTIFIER, never tickets
   bool members_available; // projection available; historical completeness remains an independent flag
  };
struct JPWLedgerView
  {
   string account_key,currency,publisher_token,reason;
   long generation,observed_utc,observed_mono_ms,margin_mode;
   double balance;
   int quality; // 0 N/A, 1 Current, 2 historical observation (not live)
   bool history_complete,costs_complete,healthy;
  };
struct JPWLedgerMember
  {
   long identifier;
   string symbol;
   int side,cycle;
   double volume;
   bool rollover_wait;
  };
struct JPWLedgerEvent
  {
   long time_msc,ticket;
   int kind,index; // 0 pending setup, 1 deal, 2 pending resolution
  };

void JPWLedgerClearView(JPWLedgerView &v)
  {
   v.account_key=""; v.currency=""; v.publisher_token=""; v.reason="";
   v.generation=0; v.observed_utc=0; v.observed_mono_ms=0;
   v.margin_mode=-1; v.balance=0; v.quality=0;
   v.history_complete=false; v.costs_complete=false; v.healthy=false;
  }
void JPWLedgerClearCycle(JPWLedgerCycle &c)
  {
   c.cycle_id=""; c.symbol=""; c.side=0;
   c.genesis_identifier=0; c.genesis_deal=0; c.started_msc=0; c.ended_msc=0;
   c.state=4; c.genesis_inferred=false; c.genesis_ambiguous=false;
   c.realized_price=0; c.realized_swap=0; c.commissions=0; c.fees=0;
   c.unrealized_price=0; c.unrealized_swap=0; c.compensated=0; c.percent=0;
   c.amount_valid=false; c.percent_valid=false; c.partial=false;
   c.history_complete=true; c.costs_complete=true;
   c.open_positions=0; c.pending_orders=0; c.reason="";
   c.member_identifiers=""; c.members_available=false;
  }
bool JPWLedgerFinite(const double x) { return(MathIsValidNumber(x)); }
bool JPWLedgerTickFresh(const long server_msc,const long tick_msc)
  {
   // TimeTradeServer supplies whole seconds, while MqlTick has milliseconds.
   // Match the base clock convention: at most 2s future skew, 30s old.
   return(server_msc>0 && tick_msc>0 && tick_msc-server_msc<=2000 && server_msc-tick_msc<=30000);
  }
bool JPWLedgerCountsStable(const int before_positions,const int before_orders,
   const int after_positions,const int after_orders)
  {
   return(before_positions>=0 && before_positions<=512 && before_orders>=0 && before_orders<=512 &&
      before_positions==after_positions && before_orders==after_orders);
  }
// Explicit operator coverage declaration, not a broker completeness validator
// or a normative approval. The declaration is bound to the account captured at
// initialization; an account switch cannot reuse it without reinitialization.
bool JPWLedgerApplyDeclaredCoverage(JPWLedgerView &view,const bool history_confirmed,
   const bool costs_confirmed,const string evidence,const string declared_account)
  {
   view.history_complete=false; view.costs_complete=false;
   bool substantive=false;
   for(int i=0;i<StringLen(evidence);i++) if(StringGetCharacter(evidence,i)>32) { substantive=true; break; }
   if(!substantive || StringLen(evidence)>1024 || view.account_key=="" || declared_account!=view.account_key)
     { view.reason="Cobertura sem referência vinculada à conta/período; N/A"; return(false); }
   view.history_complete=history_confirmed; view.costs_complete=costs_confirmed;
   view.reason="Cobertura DECLARADA por operador, condicionada a evidência; não verificada automaticamente; conta="+
      view.account_key+"; histórico solicitado desde origem até UTC="+IntegerToString(view.observed_utc)+"; ref="+evidence;
   return(history_confirmed || costs_confirmed);
  }
bool JPWLedgerNear(const double a,const double b)
  { return(JPWLedgerFinite(a) && JPWLedgerFinite(b) && MathAbs(a-b)<=JPW_LEDGER_EPS); }
bool JPWLedgerDealValid(JPWLedgerDeal &d)
  {
   if(d.ticket<=0 || d.time_msc<=0 || d.order_ticket<0 || d.position_id<0 || d.adjustment_of<0 ||
      d.kind<1 || d.kind>5 || (d.deleted!=0 && d.deleted!=1) ||
      !JPWLedgerFinite(d.profit) || !JPWLedgerFinite(d.swap) ||
      !JPWLedgerFinite(d.commission) || !JPWLedgerFinite(d.fee) ||
      !JPWLedgerFinite(d.volume) || d.volume<0) return(false);
   return((d.kind!=1 && d.kind!=5) || (d.position_id>0 && d.order_ticket>0 && d.symbol!="" &&
          (d.side==1 || d.side==-1) && d.volume>0 && d.entry>=0 && d.entry<=3));
  }
bool JPWLedgerSameDeal(JPWLedgerDeal &a,JPWLedgerDeal &b)
  {
   return(a.ticket==b.ticket && a.order_ticket==b.order_ticket &&
      a.position_id==b.position_id && a.time_msc==b.time_msc && a.symbol==b.symbol &&
      a.kind==b.kind && a.side==b.side && a.entry==b.entry && a.reason==b.reason &&
      a.volume==b.volume && a.profit==b.profit && a.swap==b.swap &&
      a.commission==b.commission && a.fee==b.fee && a.deleted==b.deleted && a.adjustment_of==b.adjustment_of);
  }
bool JPWLedgerUniqueRaw(JPWLedgerDeal &deals[],JPWLedgerOrder &orders[],string &reason)
  {
   long tickets[]; int count=ArraySize(deals);
   if(count>JPW_LEDGER_MAX_RECORDS || ArraySize(orders)>JPW_LEDGER_MAX_RECORDS) return(false);
   if(ArrayResize(tickets,count)!=count) return(false);
   for(int i=0;i<count;i++) tickets[i]=deals[i].ticket;
   if(count>1) ArraySort(tickets);
   for(int i=1;i<count;i++) if(tickets[i]==tickets[i-1])
     { reason="Projeção contém deal duplicado"; return(false); }
   count=ArraySize(orders); if(ArrayResize(tickets,count)!=count) return(false);
   for(int i=0;i<count;i++) tickets[i]=orders[i].ticket;
   if(count>1) ArraySort(tickets);
   for(int i=1;i<count;i++) if(tickets[i]==tickets[i-1])
     { reason="Projeção contém pendente duplicada"; return(false); }
   return(true);
  }
// Structural validation is used while Build has not finalized provisional
// states yet. Published/decoded projections use the stricter final validator.
bool JPWLedgerMemberListStructureValid(JPWLedgerCycle &cycle)
  {
   if(!cycle.members_available) return(cycle.member_identifiers=="");
   if(cycle.genesis_inferred && cycle.genesis_identifier<=0 && !cycle.genesis_ambiguous) return(false);
   if(StringLen(cycle.member_identifiers)>JPW_LEDGER_MAX_RECORDS*21) return(false);
   if(cycle.member_identifiers=="") return(!cycle.genesis_inferred);
   string ids[]; int count=StringSplit(cycle.member_identifiers,',',ids);
   if(count<1 || count>JPW_LEDGER_MAX_RECORDS) return(false);
   long previous=0; bool genesis_found=(cycle.genesis_identifier==0); string canonical="";
   for(int i=0;i<count;i++)
     {
      long id=StringToInteger(ids[i]);
      if(id<=previous || IntegerToString(id)!=ids[i]) return(false);
      previous=id; if(id==cycle.genesis_identifier) genesis_found=true;
      canonical+=(i>0 ? "," : "")+IntegerToString(id);
     }
   return(canonical==cycle.member_identifiers && (!cycle.genesis_inferred || genesis_found));
  }
bool JPWLedgerMemberListValid(JPWLedgerCycle &cycle)
  {
   if(!JPWLedgerMemberListStructureValid(cycle)) return(false);
   if(!cycle.members_available || cycle.member_identifiers!="") return(true);
   return(cycle.state==4 && !cycle.genesis_inferred && !cycle.genesis_ambiguous &&
      cycle.genesis_identifier==0 && cycle.genesis_deal==0 && cycle.open_positions==0 &&
      !cycle.amount_valid && !cycle.percent_valid);
  }
bool JPWLedgerMembershipStructureValid(JPWLedgerCycle &cycles[])
  {
   long all[];
   for(int c=0;c<ArraySize(cycles);c++)
     {
      for(int previous=0;previous<c;previous++) if(cycles[previous].cycle_id==cycles[c].cycle_id) return(false);
      if(!JPWLedgerMemberListStructureValid(cycles[c])) return(false);
      if(!cycles[c].members_available || cycles[c].member_identifiers=="") continue;
      string ids[]; int count=StringSplit(cycles[c].member_identifiers,',',ids);
      int offset=ArraySize(all);
      if(offset+count>JPW_LEDGER_MAX_RECORDS || ArrayResize(all,offset+count)!=offset+count) return(false);
      for(int i=0;i<count;i++) all[offset+i]=StringToInteger(ids[i]);
     }
   if(ArraySize(all)>1) ArraySort(all);
   for(int i=1;i<ArraySize(all);i++) if(all[i]==all[i-1]) return(false);
   return(true);
  }
bool JPWLedgerMembershipProjectionValid(JPWLedgerCycle &cycles[])
  {
   if(!JPWLedgerMembershipStructureValid(cycles)) return(false);
   for(int c=0;c<ArraySize(cycles);c++) if(!JPWLedgerMemberListValid(cycles[c])) return(false);
   return(true);
  }
bool JPWLedgerProjectMembers(JPWLedgerCycle &cycles[],JPWLedgerMember &members[])
  {
   for(int c=0;c<ArraySize(cycles);c++)
     {
      long ids[];
      for(int m=0;m<ArraySize(members);m++) if(members[m].cycle==c)
        { int n=ArraySize(ids); if(ArrayResize(ids,n+1)!=n+1) return(false); ids[n]=members[m].identifier; }
      if(ArraySize(ids)>1) ArraySort(ids);
      cycles[c].member_identifiers=""; cycles[c].members_available=true;
      for(int i=0;i<ArraySize(ids);i++) cycles[c].member_identifiers+=(i>0 ? "," : "")+IntegerToString(ids[i]);
     }
   return(JPWLedgerMembershipStructureValid(cycles));
  }
int JPWLedgerMemberIndex(JPWLedgerMember &members[],const long id)
  { for(int i=0;i<ArraySize(members);i++) if(members[i].identifier==id) return(i); return(-1); }
int JPWLedgerCompareEvent(JPWLedgerEvent &a,JPWLedgerEvent &b)
  {
   if(a.time_msc!=b.time_msc) return(a.time_msc<b.time_msc ? -1 : 1);
   if(a.kind!=b.kind) return(a.kind<b.kind ? -1 : 1);
   if(a.ticket!=b.ticket) return(a.ticket<b.ticket ? -1 : 1);
   return(0);
  }
void JPWLedgerSortEvents(JPWLedgerEvent &e[],const int left,const int right)
  {
   int i=left,j=right; JPWLedgerEvent pivot=e[(left+right)/2];
   while(i<=j)
     {
      while(JPWLedgerCompareEvent(e[i],pivot)<0) i++;
      while(JPWLedgerCompareEvent(e[j],pivot)>0) j--;
      if(i<=j) { JPWLedgerEvent temp=e[i]; e[i]=e[j]; e[j]=temp; i++; j--; }
     }
   if(left<j) JPWLedgerSortEvents(e,left,j);
   if(i<right) JPWLedgerSortEvents(e,i,right);
  }
bool JPWLedgerAddEvent(JPWLedgerEvent &e[],const long time,const long ticket,
                       const int kind,const int index)
  {
   int n=ArraySize(e); if(n>=3*JPW_LEDGER_MAX_RECORDS || ArrayResize(e,n+1)!=n+1) return(false);
   e[n].time_msc=time; e[n].ticket=ticket; e[n].kind=kind; e[n].index=index; return(true);
  }
int JPWLedgerActiveGroup(JPWLedgerCycle &cycles[],const string symbol,const int side)
  {
   for(int i=ArraySize(cycles)-1;i>=0;i--)
      if(cycles[i].symbol==symbol && cycles[i].side==side && cycles[i].state!=3) return(i);
   return(-1);
  }
int JPWLedgerNewCycle(JPWLedgerCycle &cycles[],const string symbol,const int side,
                      const long seed,const long time,const string prefix)
  {
   int n=ArraySize(cycles);
   if(n>=JPW_LEDGER_MAX_CYCLES || ArrayResize(cycles,n+1)!=n+1) return(-1);
   JPWLedgerClearCycle(cycles[n]);
   cycles[n].cycle_id=prefix+IntegerToString(seed);
   cycles[n].symbol=symbol; cycles[n].side=side; cycles[n].started_msc=time;
   return(n);
  }
void JPWLedgerRecount(JPWLedgerCycle &cycles[],JPWLedgerMember &members[],
                     int &order_cycle[],bool &order_active[],const long time)
  {
   for(int c=0;c<ArraySize(cycles);c++)
     {
      int positions=0,pendings=0; bool rollover=false;
      for(int m=0;m<ArraySize(members);m++) if(members[m].cycle==c)
        { if(members[m].volume>JPW_LEDGER_EPS) positions++;
          if(members[m].rollover_wait) rollover=true; }
      for(int o=0;o<ArraySize(order_cycle);o++) if(order_cycle[o]==c && order_active[o]) pendings++;
      cycles[c].open_positions=positions; cycles[c].pending_orders=pendings;
      if(positions>0) { cycles[c].state=1; cycles[c].ended_msc=0; }
      else if(pendings>0) { cycles[c].state=2; cycles[c].ended_msc=0; }
      else if(rollover) { cycles[c].state=4; cycles[c].ended_msc=0; }
      else if(cycles[c].state!=3) { cycles[c].state=3; cycles[c].ended_msc=time; }
     }
  }

// Latest raw projection is supplied by the transactional store, not event order.
// Deals on an existing identifier retain their original cycle, including late
// charges and technical reopening. Symbol/side are inferred grouping, not V11 thesis.
bool JPWLedgerBuild(JPWLedgerDeal &deals[],JPWLedgerOrder &orders[],
                    JPWLedgerPosition &live[],JPWLedgerView &view,
                    JPWLedgerCycle &cycles[],string &reason)
  {
   ArrayResize(cycles,0); reason="";
   if(view.margin_mode!=JPW_LEDGER_HEDGING)
     { reason="Hedging requerido; netting/exchange N/A"; return(false); }
   if(ArraySize(deals)>JPW_LEDGER_MAX_RECORDS || ArraySize(orders)>JPW_LEDGER_MAX_RECORDS)
     { reason="Limite de histórico"; return(false); }
   if(!JPWLedgerUniqueRaw(deals,orders,reason)) return(false);
   for(int p=0;p<ArraySize(live);p++)
      if(live[p].identifier<=0 || live[p].ticket<=0 || live[p].symbol=="" ||
         (live[p].side!=1 && live[p].side!=-1) || !JPWLedgerFinite(live[p].volume) || live[p].volume<=0 ||
         !JPWLedgerFinite(live[p].profit) || !JPWLedgerFinite(live[p].swap))
        { reason="Posição viva inválida"; return(false); }
   JPWLedgerEvent events[]; JPWLedgerMember members[];
   int order_cycle[]; bool order_active[];
   ArrayResize(order_cycle,ArraySize(orders)); ArrayResize(order_active,ArraySize(orders));
   for(int o=0;o<ArraySize(orders);o++)
     {
      order_cycle[o]=-1; order_active[o]=false;
      if(orders[o].ticket<=0 || orders[o].symbol=="" || orders[o].setup_msc<=0 ||
         (orders[o].side!=1 && orders[o].side!=-1) || orders[o].state<1 || orders[o].state>4 ||
         !JPWLedgerFinite(orders[o].volume) || orders[o].volume<0)
        { reason="Pendente inválida"; return(false); }
      if(!JPWLedgerAddEvent(events,orders[o].setup_msc,orders[o].ticket,0,o)) return(false);
      if(orders[o].state==2 || orders[o].state==3)
        {
         if(orders[o].done_msc<orders[o].setup_msc ||
            !JPWLedgerAddEvent(events,orders[o].done_msc,orders[o].ticket,2,o))
           { reason="Fim de pendente não confirmado"; return(false); }
        }
     }
   for(int d=0;d<ArraySize(deals);d++)
     {
      if(!JPWLedgerDealValid(deals[d])) { reason="Deal inválido"; return(false); }
      if(!deals[d].deleted && !JPWLedgerAddEvent(events,deals[d].time_msc,deals[d].ticket,1,d)) return(false);
     }
   if(ArraySize(events)>1) JPWLedgerSortEvents(events,0,ArraySize(events)-1);
   bool unassigned_cost=false,canceled_unresolved=false;
   for(int e=0;e<ArraySize(events);e++)
     {
      JPWLedgerEvent event=events[e];
      if(event.kind==0)
        {
         JPWLedgerOrder order=orders[event.index];
         int c=JPWLedgerActiveGroup(cycles,order.symbol,order.side);
         if(c<0) c=JPWLedgerNewCycle(cycles,order.symbol,order.side,order.ticket,event.time_msc,"O");
         if(c<0) return(false);
         order_cycle[event.index]=c; order_active[event.index]=true;
         if(order.state==4) { cycles[c].history_complete=false; cycles[c].reason="Estado de pendente não reconciliado"; }
        }
      else if(event.kind==2)
        {
         int c=order_cycle[event.index];
         if(c<0) { reason="Pendente sem início"; return(false); }
         bool execution=false; double executed_volume=0;
         for(int d=0;d<ArraySize(deals);d++)
            if(!deals[d].deleted && deals[d].kind==1 && deals[d].order_ticket==event.ticket &&
               deals[d].time_msc<=event.time_msc)
               { execution=true; executed_volume+=deals[d].volume; }
         if(orders[event.index].state==3 && (!execution ||
            !JPWLedgerNear(executed_volume,orders[event.index].volume)))
           { cycles[c].history_complete=false; cycles[c].reason="Execução da pendente ainda não reconciliada";
             order_active[event.index]=true; } // no verified flat transition
         else order_active[event.index]=false;
        }
      else
        {
         JPWLedgerDeal deal=deals[event.index];
         int m=JPWLedgerMemberIndex(members,deal.position_id),c=(m>=0 ? members[m].cycle : -1);
         if(deal.kind==4)
           {
            if(deal.commission!=0 || deal.fee!=0 || deal.swap!=0) unassigned_cost=true;
            if(e+1==ArraySize(events) || events[e+1].time_msc!=event.time_msc)
               JPWLedgerRecount(cycles,members,order_cycle,order_active,event.time_msc);
            continue; // credit is never Operation performance
           }
         if((deal.kind==1 || deal.kind==5) && deal.entry==0)
           {
            if(m<0)
              {
               for(int o=0;o<ArraySize(orders);o++) if(orders[o].ticket==deal.order_ticket) { c=order_cycle[o]; break; }
               if(c<0) c=JPWLedgerActiveGroup(cycles,deal.symbol,deal.side);
               if(c>=0 && cycles[c].genesis_inferred && cycles[c].started_msc<deal.time_msc)
                 {
                  bool exposure=false,pending=false,rollover=false;
                  for(int k=0;k<ArraySize(members);k++) if(members[k].cycle==c)
                    {
                     double remaining=members[k].volume;
                     if(members[k].rollover_wait) rollover=true;
                     // Ticket ordering within a server millisecond is not
                     // proof of the true flat/open boundary. Include exits
                     // still to replay in the current timestamp batch.
                     for(int f=e+1;f<ArraySize(events) && events[f].time_msc==event.time_msc;f++)
                        if(events[f].kind==1)
                          { JPWLedgerDeal future=deals[events[f].index];
                            if((future.kind==1 || future.kind==5) && future.entry!=0 &&
                               future.position_id==members[k].identifier)
                              { remaining-=future.volume; if(future.reason==1) rollover=true; } }
                     if(remaining>JPW_LEDGER_EPS) exposure=true;
                    }
                  for(int k=0;k<ArraySize(order_cycle);k++) if(order_cycle[k]==c && order_active[k]) pending=true;
                  if(!exposure && !pending && !rollover)
                    { cycles[c].history_complete=false; cycles[c].genesis_ambiguous=true;
                      cycles[c].reason="Zeragem e nova entrada no mesmo milissegundo sem ordenação comprovada"; }
                 }
               if(c<0) c=JPWLedgerNewCycle(cycles,deal.symbol,deal.side,deal.ticket,deal.time_msc,"D");
               if(c<0) return(false);
               m=ArraySize(members); if(ArrayResize(members,m+1)!=m+1) return(false);
               members[m].identifier=deal.position_id; members[m].symbol=deal.symbol;
               members[m].side=deal.side; members[m].cycle=c; members[m].volume=0; members[m].rollover_wait=false;
               if(deal.order_ticket!=deal.position_id)
                 { cycles[c].history_complete=false; cycles[c].reason="Ordem original de abertura ausente"; }
               if(cycles[c].genesis_deal==0)
                 {
                  cycles[c].genesis_identifier=deal.position_id; cycles[c].genesis_deal=deal.ticket;
                  cycles[c].genesis_inferred=true; cycles[c].started_msc=deal.time_msc;
                 }
               else if(cycles[c].started_msc==deal.time_msc && cycles[c].genesis_identifier!=deal.position_id)
                 { cycles[c].genesis_ambiguous=true; }
              }
            if(members[m].symbol!=deal.symbol || members[m].side!=deal.side)
              { cycles[c].history_complete=false; cycles[c].reason="Identificador reutilizado em outro grupo"; }
            members[m].volume+=deal.volume; members[m].rollover_wait=false;
           }
         else if(deal.kind==1 || deal.kind==5)
           {
            if(m<0)
              {
               c=JPWLedgerActiveGroup(cycles,deal.symbol,-deal.side);
               if(c<0) c=JPWLedgerNewCycle(cycles,deal.symbol,-deal.side,deal.ticket,deal.time_msc,"X");
               if(c<0) return(false);
               cycles[c].history_complete=false; cycles[c].reason="Saída sem abertura comprovada";
              }
            else if(deal.entry==2 || members[m].side==deal.side ||
                    deal.volume>members[m].volume+JPW_LEDGER_EPS)
              { cycles[c].history_complete=false; cycles[c].reason="Volume/direção de saída não reconciliados"; }
            else
              { members[m].volume=MathMax(0.0,members[m].volume-deal.volume);
                if(deal.reason==1 && members[m].volume<=JPW_LEDGER_EPS) members[m].rollover_wait=true; }
           }
         if(deal.kind==5)
           {
            bool linked_adjustment=false;
            for(int k=0;k<ArraySize(deals);k++)
               if(!deals[k].deleted && (deals[k].kind==2 || deals[k].kind==3) &&
                  deals[k].position_id==deal.position_id && deal.position_id>0 &&
                  deals[k].adjustment_of==deal.ticket && deals[k].time_msc>=deal.time_msc)
                  { linked_adjustment=true; break; }
            if(!linked_adjustment) canceled_unresolved=true;
           }
         if(c>=0)
           {
            cycles[c].realized_price+=deal.profit; cycles[c].realized_swap+=deal.swap;
            cycles[c].commissions+=deal.commission; cycles[c].fees+=deal.fee;
           }
         else if(deal.kind==2 || deal.commission!=0 || deal.fee!=0 || deal.swap!=0)
            unassigned_cost=true;
        }
      // Resolve the entire server-millisecond batch before a zero transition.
      if(e+1==ArraySize(events) || events[e+1].time_msc!=event.time_msc)
         JPWLedgerRecount(cycles,members,order_cycle,order_active,event.time_msc);
     }
   for(int m=0;m<ArraySize(members);m++)
     {
      int c=members[m].cycle,found=-1;
      for(int p=0;p<ArraySize(live);p++) if(live[p].identifier==members[m].identifier)
        { if(found>=0) { reason="Identificador vivo duplicado"; return(false); } found=p; }
      if(members[m].rollover_wait || (found<0 && members[m].volume>JPW_LEDGER_EPS) ||
         (found>=0 && (live[found].symbol!=members[m].symbol || live[found].side!=members[m].side ||
                      !JPWLedgerNear(live[found].volume,members[m].volume))))
        { cycles[c].history_complete=false; cycles[c].reason="Volume vivo/histórico não reconciliado"; }
      if(found>=0)
        {
         if(!JPWLedgerFinite(live[found].profit) || !JPWLedgerFinite(live[found].swap))
           { reason="P/L vivo inválido"; return(false); }
         cycles[c].unrealized_price+=live[found].profit; cycles[c].unrealized_swap+=live[found].swap;
        }
     }
   for(int p=0;p<ArraySize(live);p++) if(JPWLedgerMemberIndex(members,live[p].identifier)<0)
     { reason="Posição viva sem origem no histórico"; return(false); }
   if(!JPWLedgerProjectMembers(cycles,members))
     { reason="Projeção de membros inconsistente"; return(false); }
   for(int c=0;c<ArraySize(cycles);c++)
     {
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
     }
   if(!JPWLedgerMembershipProjectionValid(cycles))
     { reason="Estado final da projeção de membros inconsistente"; return(false); }
   view.costs_complete=view.costs_complete && !unassigned_cost && !canceled_unresolved;
   return(true);
  }
#endif
