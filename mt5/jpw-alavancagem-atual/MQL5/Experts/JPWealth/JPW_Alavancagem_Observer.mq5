#property copyright "JP Wealth"
#include <JPWealth/JPW_Alavancagem_Version.mqh>
#property version JPW_PRODUCT_MQL_VERSION
#property description "JPW GENETRIX · Observador legado compativel; nao negocia."
#include <JPWealth/JPW_Genetrix_Observer_Runtime.mqh>
int OnInit()
  {
   if(!JPWObserverRuntimeAttach() || !EventSetTimer(1))
     { JPWObserverRuntimeDetach(REASON_INITFAILED); return(INIT_FAILED); }
   return(INIT_SUCCEEDED);
  }
void OnDeinit(const int reason)
  { EventKillTimer(); JPWObserverRuntimeDetach(reason); }
void OnTradeTransaction(const MqlTradeTransaction &trans,const MqlTradeRequest &request,const MqlTradeResult &result)
  { JPWObserverRuntimeTransaction(trans,request,result); }
void OnTimer() { JPWObserverRuntimeLegacyTick(); }
