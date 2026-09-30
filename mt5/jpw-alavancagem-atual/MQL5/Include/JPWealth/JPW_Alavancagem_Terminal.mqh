#ifndef JPW_ALAVANCAGEM_TERMINAL_MQH
#define JPW_ALAVANCAGEM_TERMINAL_MQH
#include <JPWealth/JPW_Alavancagem_Core.mqh>
#include <JPWealth/JPW_Alavancagem_Genesis_Core.mqh>
// Shared read-only MT5 adapter. Selecting conversion symbols may add Market Watch entries.

struct JPWCatalogEntry
  {
   string symbol;
   string base;
   string profit;
  };

JPWCatalogEntry g_catalog[];
int g_scan_index=0;
int g_scan_total=0;
bool g_catalog_ready=false;
JPWRoute g_routes[];
JPWClock g_clock;
JPWAccount g_account;
bool g_account_known=false;
bool g_connected=false;
bool g_quotes_pending=false;
bool g_budget_exceeded=false;
string g_unsynchronized_symbols[];

void JPWResetData()
  {
   ArrayResize(g_catalog,0);
   ArrayResize(g_routes,0);
   g_scan_index=0;
   g_scan_total=0;
   g_catalog_ready=false;
   JPWClockReset(g_clock,(long)TimeCurrent(),GetTickCount64());
  }

bool JPWReadAccount(JPWAccount &account)
  {
   account.login=AccountInfoInteger(ACCOUNT_LOGIN);
   account.server=AccountInfoString(ACCOUNT_SERVER);
   account.currency=JPWNormalizeCurrency(AccountInfoString(ACCOUNT_CURRENCY));
   return(account.login>0 && account.server!="" && account.currency!="");
  }

bool JPWReadSnapshot(JPWPosition &positions[])
  {
   const int count=PositionsTotal();
   if(count<0 || ArrayResize(positions,count)!=count) return(false);
   for(int i=0;i<count;i++)
     {
      const ulong ticket=PositionGetTicket(i);
      if(ticket==0 || !PositionSelectByTicket(ticket)) return(false);
      long identifier=0;
      long direction=-1;
      string symbol="";
      double volume=0.0;
      if(!PositionGetInteger(POSITION_IDENTIFIER,identifier) ||
         !PositionGetInteger(POSITION_TYPE,direction) ||
         !PositionGetString(POSITION_SYMBOL,symbol) ||
         !PositionGetDouble(POSITION_VOLUME,volume) ||
         identifier<=0 || symbol=="" || !JPWFinitePositive(volume) ||
         (direction!=POSITION_TYPE_BUY && direction!=POSITION_TYPE_SELL))
         return(false);
      positions[i].ticket=ticket;
      positions[i].identifier=identifier;
      positions[i].symbol=symbol;
      positions[i].direction=direction;
      positions[i].volume=volume;
     }
   return(true);
  }

// Separate, complete snapshot for the SL reference. A failed property read
// invalidates this metric only; the existing notional snapshot is unchanged.
bool JPWReadGenesisSnapshot(JPWGenesisPosition &positions[])
  {
   const int count=PositionsTotal();
   if(count<0 || ArrayResize(positions,count)!=count) return(false);
   for(int i=0;i<count;i++)
     {
      const ulong ticket=PositionGetTicket(i);
      if(ticket==0 || !PositionSelectByTicket(ticket)) return(false);
      long identifier=0,direction=-1,opened=0,updated=0;
      string symbol="";
      double sl=0.0,volume=0.0;
      if(!PositionGetInteger(POSITION_IDENTIFIER,identifier) ||
         !PositionGetInteger(POSITION_TYPE,direction) ||
         !PositionGetInteger(POSITION_TIME_MSC,opened) ||
         !PositionGetInteger(POSITION_TIME_UPDATE_MSC,updated) ||
         !PositionGetString(POSITION_SYMBOL,symbol) ||
         !PositionGetDouble(POSITION_SL,sl) ||
         !PositionGetDouble(POSITION_VOLUME,volume) ||
         identifier<=0 || opened<=0 || symbol=="" || !JPWFinitePositive(volume) ||
         !MathIsValidNumber(sl) || sl<0.0 ||
         (direction!=POSITION_TYPE_BUY && direction!=POSITION_TYPE_SELL))
         return(false);
      positions[i].ticket=ticket;
      positions[i].identifier=identifier;
      positions[i].symbol=symbol;
      positions[i].direction=direction;
      positions[i].opened_msc=opened;
      positions[i].updated_msc=updated;
      positions[i].sl=sl;
      positions[i].volume=volume;
      // Duplicate identities make absence ambiguous. Never tombstone a saved
      // reference from a snapshot that cannot distinguish its position.
      for(int j=0;j<i;j++)
         if(positions[j].ticket==ticket || positions[j].identifier==identifier)
            return(false);
     }
   return(true);
  }

bool JPWGenesisSnapshotsEqual(JPWGenesisPosition &a[],JPWGenesisPosition &b[])
  {
   const int count=ArraySize(a);
   if(count!=ArraySize(b)) return(false);
   bool used[];
   if(ArrayResize(used,count)!=count) return(false);
   for(int i=0;i<count;i++) used[i]=false;
   for(int i=0;i<count;i++)
     {
      bool found=false;
      for(int j=0;j<count;j++)
        {
         if(used[j] || a[i].ticket!=b[j].ticket ||
            a[i].identifier!=b[j].identifier || a[i].symbol!=b[j].symbol ||
            a[i].direction!=b[j].direction || a[i].opened_msc!=b[j].opened_msc ||
            a[i].updated_msc!=b[j].updated_msc || a[i].sl!=b[j].sl ||
            a[i].volume!=b[j].volume) continue;
         used[j]=true;
         found=true;
         break;
        }
      if(!found) return(false);
     }
   return(true);
  }

bool JPWReadSpecification(const string symbol,JPWInstrument &instrument)
  {
   long mode=0;
   string base="";
   string profit="";
   double size=0.0;
   if(!SymbolInfoInteger(symbol,SYMBOL_TRADE_CALC_MODE,mode) ||
      !SymbolInfoDouble(symbol,SYMBOL_TRADE_CONTRACT_SIZE,size) ||
      !SymbolInfoString(symbol,SYMBOL_CURRENCY_BASE,base) ||
      !SymbolInfoString(symbol,SYMBOL_CURRENCY_PROFIT,profit)) return(false);
   string basis="";
   string isin="";
   SymbolInfoString(symbol,SYMBOL_BASIS,basis);
   SymbolInfoString(symbol,SYMBOL_ISIN,isin);
   instrument.symbol=symbol;
   instrument.calc_mode=(int)mode;
   instrument.base=JPWNormalizeCurrency(base);
   instrument.profit=JPWNormalizeCurrency(profit);
   instrument.contract_size=size;
   instrument.underlying_verified=(basis!="" || isin!="");
   return(true);
  }

bool JPWPrepareCatalog()
  {
   const int total=SymbolsTotal(false);
   if(total<=0) return(false);
   if(g_scan_total!=total)
     {
      ArrayResize(g_catalog,0);
      g_scan_total=total;
      g_scan_index=0;
      g_catalog_ready=false;
     }
   if(g_catalog_ready) return(true);
   const ulong started=GetTickCount64();
   int handled=0;
   while(g_scan_index<g_scan_total && handled<100)
     {
      if(GetTickCount64()-started>=50) break;
      const string symbol=SymbolName(g_scan_index,false);
      g_scan_index++;
      handled++;
      if(symbol=="") continue;
      long mode=0;
      long custom=0;
      string base="";
      string profit="";
      // Pares criados localmente podem ter ticks arbitrários; conversão
      // da conta deve usar apenas instrumentos publicados pelo servidor.
      if(!SymbolInfoInteger(symbol,SYMBOL_CUSTOM,custom) || custom!=0 ||
         !SymbolInfoInteger(symbol,SYMBOL_TRADE_CALC_MODE,mode) ||
         !SymbolInfoString(symbol,SYMBOL_CURRENCY_BASE,base) ||
         !SymbolInfoString(symbol,SYMBOL_CURRENCY_PROFIT,profit)) continue;
      if(mode!=SYMBOL_CALC_MODE_FOREX && mode!=SYMBOL_CALC_MODE_FOREX_NO_LEVERAGE)
         continue;
      base=JPWNormalizeCurrency(base);
      profit=JPWNormalizeCurrency(profit);
      if(!JPWIsFiat(base) || !JPWIsFiat(profit) || base==profit) continue;
      const int n=ArraySize(g_catalog);
      if(ArrayResize(g_catalog,n+1)!=n+1) return(false);
      g_catalog[n].symbol=symbol;
      g_catalog[n].base=base;
      g_catalog[n].profit=profit;
     }
   g_catalog_ready=(g_scan_index>=g_scan_total);
   return(g_catalog_ready);
  }

bool JPWPrimePositionSymbols()
  {
   // Preparacao limitada: permite que um simbolo de posicao fora do Market
   // Watch produza a observacao temporal necessaria apos a inicializacao.
   const int count=PositionsTotal();
   const ulong started=GetTickCount64();
   for(int i=0;i<count;i++)
     {
      if(GetTickCount64()<started || GetTickCount64()-started>=100)
         return(false);
      const ulong ticket=PositionGetTicket(i);
      if(ticket==0 || !PositionSelectByTicket(ticket)) return(false);
      string symbol="";
      long selected=0;
      if(!PositionGetString(POSITION_SYMBOL,symbol) || symbol=="")
         return(false);
      if(!SymbolInfoInteger(symbol,SYMBOL_SELECT,selected) || selected==0)
         if(!SymbolSelect(symbol,true)) return(false);
     }
   return(true);
  }

bool JPWWithinBudget(const ulong started)
  {
   if(GetTickCount64()<started || GetTickCount64()-started>500)
     {
      g_budget_exceeded=true;
      return(false);
     }
   return(true);
  }

bool JPWConversionMetadata(const string symbol,const string base,const string profit)
  {
   long mode=0,custom=0;
   string current_base="",current_profit="";
   return(SymbolInfoInteger(symbol,SYMBOL_CUSTOM,custom) && custom==0 &&
          SymbolInfoInteger(symbol,SYMBOL_TRADE_CALC_MODE,mode) &&
          (mode==SYMBOL_CALC_MODE_FOREX || mode==SYMBOL_CALC_MODE_FOREX_NO_LEVERAGE) &&
          SymbolInfoString(symbol,SYMBOL_CURRENCY_BASE,current_base) &&
          SymbolInfoString(symbol,SYMBOL_CURRENCY_PROFIT,current_profit) &&
          JPWNormalizeCurrency(current_base)==base && JPWNormalizeCurrency(current_profit)==profit &&
          JPWIsFiat(base) && JPWIsFiat(profit) && base!=profit);
  }

bool JPWWasUnsynchronized(const string symbol)
  {
   for(int i=0;i<ArraySize(g_unsynchronized_symbols);i++)
      if(g_unsynchronized_symbols[i]==symbol) return(true);
   return(false);
  }

// Uma chamada SymbolInfoTick por simbolo em cada tentativa. Erros ficam no
// cache somente da tentativa; no proximo timer sera feita nova leitura.
bool JPWCaptureQuote(const string symbol,const string base,const string profit,
                     JPWQuote &quotes[],const bool conversion_pair)
  {
   const int existing=JPWQuoteIndex(quotes,symbol);
   if(conversion_pair && !JPWConversionMetadata(symbol,base,profit))
     {
      if(existing>=0) quotes[existing].conversion_pair=false;
      // Invalidate the catalogue even if its symbol count did not change.
      g_catalog_ready=false; g_scan_total=0;
      return(false);
     }
   if(existing>=0)
     {
      if(quotes[existing].base!=base || quotes[existing].profit!=profit) return(false);
      if(conversion_pair) quotes[existing].conversion_pair=true;
      return(quotes[existing].time_msc>0);
     }
   const int n=ArraySize(quotes);
   if(ArrayResize(quotes,n+1)!=n+1) return(false);
   quotes[n].symbol=symbol;
   quotes[n].base=base;
   quotes[n].profit=profit;
   quotes[n].bid=0.0;
   quotes[n].ask=0.0;
   quotes[n].time_msc=0;
   quotes[n].conversion_pair=conversion_pair;
   long selected=0;
   if(!SymbolInfoInteger(symbol,SYMBOL_SELECT,selected) || selected==0)
     {
      if(!SymbolSelect(symbol,true)) return(false);
      g_quotes_pending=true;
     }
   // A stored quote can still support an explicitly labelled estimate.
   if(!SymbolIsSynchronized(symbol))
     {
      g_quotes_pending=true;
      if(!JPWWasUnsynchronized(symbol))
        {
         const int k=ArraySize(g_unsynchronized_symbols);
         if(ArrayResize(g_unsynchronized_symbols,k+1)!=k+1) return(false);
         g_unsynchronized_symbols[k]=symbol;
        }
     }
   MqlTick tick={};
   if(!SymbolInfoTick(symbol,tick))
     {
      g_quotes_pending=true;
      return(false);
     }
   if(tick.time<=0 || (tick.time_msc>0 &&
      MathAbs((double)(tick.time_msc-(long)tick.time*1000))>1000.0))
      return(false);
   quotes[n].bid=tick.bid;
   quotes[n].ask=tick.ask;
   quotes[n].time_msc=(tick.time_msc>0 ? tick.time_msc : (long)tick.time*1000);
   return(quotes[n].time_msc>0);
  }

bool JPWTouches(const JPWCatalogEntry &entry,const string first,const string second)
  {
   return((entry.base==first && entry.profit==second) ||
          (entry.profit==first && entry.base==second));
  }

// Prefer routes whose actual captured symbols are synchronized. Preserve the
// selected route for the pure calculation; stale alternatives remain available
// for the second, explicitly estimated pass.
bool JPWPreparedCurrentRoute(const string source,const string target,JPWQuote &quotes[],
                             const long now_ms,const int max_age_sec,JPWRoute &previous)
  {
   JPWQuote current[];
   for(int i=0;i<ArraySize(quotes);i++)
     {
      if(JPWWasUnsynchronized(quotes[i].symbol)) continue;
      const int n=ArraySize(current);
      if(ArrayResize(current,n+1)!=n+1) return(false);
      current[n]=quotes[i];
     }
   JPWRoute chosen;
   double rate=0.0;
   if(!JPWFindRoute(source,target,current,now_ms,max_age_sec,previous,chosen,rate)) return(false);
   int index=-1;
   for(int i=0;i<ArraySize(g_routes);i++)
      if(g_routes[i].source==source && g_routes[i].target==target) { index=i; break; }
   if(index<0)
     {
      index=ArraySize(g_routes);
      if(ArrayResize(g_routes,index+1)!=index+1) return(false);
     }
   g_routes[index]=chosen;
   return(true);
  }

bool JPWPreparedRoute(const string source,const string target,JPWQuote &quotes[],
                      const long now_ms,const ulong started,
                      const bool clock_valid,const bool connected,
                      const int max_age_sec=30)
  {
   if(source==target) return(true);
   JPWRoute previous;
   previous.valid=false;
   for(int i=0;i<ArraySize(g_routes);i++)
      if(g_routes[i].source==source && g_routes[i].target==target)
        {
         previous=g_routes[i];
         break;
        }
   if(previous.valid)
     {
      for(int i=0;i<ArraySize(g_catalog);i++)
        {
         if(g_catalog[i].symbol==previous.first_symbol ||
            g_catalog[i].symbol==previous.second_symbol)
            JPWCaptureQuote(g_catalog[i].symbol,g_catalog[i].base,
                            g_catalog[i].profit,quotes,true);
        }
      double rate=0.0;
      if(clock_valid && connected && !JPWWasUnsynchronized(previous.first_symbol) &&
         !JPWWasUnsynchronized(previous.second_symbol) &&
         JPWRouteRate(previous,quotes,now_ms,max_age_sec,rate))
         return(true);
     }
   for(int i=0;i<ArraySize(g_catalog);i++)
     {
      if(!JPWWithinBudget(started)) return(false);
      if(JPWTouches(g_catalog[i],source,target))
         JPWCaptureQuote(g_catalog[i].symbol,g_catalog[i].base,
                         g_catalog[i].profit,quotes,true);
     }
   JPWRoute chosen;
   double rate=0.0;
   if(clock_valid && connected &&
      JPWPreparedCurrentRoute(source,target,quotes,now_ms,max_age_sec,previous)) return(true);
   // A busca de duas etapas so ocorre se nenhuma cotacao direta/inversa
   // valida existe. Tres passagens lineares pelo catalogo identificam as
   // moedas intermediarias e as pernas, sem recomecar uma busca N x N.
   string target_neighbors=",";
   for(int i=0;i<ArraySize(g_catalog);i++)
     {
      if(!JPWWithinBudget(started)) return(false);
      string neighbor="";
      if(g_catalog[i].base==target) neighbor=g_catalog[i].profit;
      else if(g_catalog[i].profit==target) neighbor=g_catalog[i].base;
      if(JPWIsFiat(neighbor) && neighbor!=source && neighbor!=target &&
         StringFind(target_neighbors,","+neighbor+",")<0)
         target_neighbors+=neighbor+",";
     }
   string intermediates=",";
   for(int i=0;i<ArraySize(g_catalog);i++)
     {
      if(!JPWWithinBudget(started)) return(false);
      string neighbor="";
      if(g_catalog[i].base==source) neighbor=g_catalog[i].profit;
      else if(g_catalog[i].profit==source) neighbor=g_catalog[i].base;
      if(JPWIsFiat(neighbor) && neighbor!=source && neighbor!=target &&
         StringFind(target_neighbors,","+neighbor+",")>=0 &&
         StringFind(intermediates,","+neighbor+",")<0)
         intermediates+=neighbor+",";
     }
   for(int i=0;i<ArraySize(g_catalog);i++)
     {
      if(!JPWWithinBudget(started)) return(false);
      string source_neighbor="";
      string target_neighbor="";
      if(g_catalog[i].base==source) source_neighbor=g_catalog[i].profit;
      else if(g_catalog[i].profit==source) source_neighbor=g_catalog[i].base;
      if(g_catalog[i].base==target) target_neighbor=g_catalog[i].profit;
      else if(g_catalog[i].profit==target) target_neighbor=g_catalog[i].base;
      if(StringFind(intermediates,","+source_neighbor+",")>=0 ||
         StringFind(intermediates,","+target_neighbor+",")>=0)
         JPWCaptureQuote(g_catalog[i].symbol,g_catalog[i].base,
                         g_catalog[i].profit,quotes,true);
     }
   if(clock_valid && connected &&
      JPWPreparedCurrentRoute(source,target,quotes,now_ms,max_age_sec,previous)) return(true);
   bool estimated=false;
   long oldest=0;
   return(JPWFindRouteReading(source,target,quotes,now_ms,max_age_sec,
                              clock_valid,connected,previous,chosen,rate,estimated,oldest));
  }


#endif
