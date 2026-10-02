#ifndef JPW_GENETRIX_UI_MQH
#define JPW_GENETRIX_UI_MQH
#include <JPWealth/JPW_Genetrix_Ledger_Bridge.mqh>
#include <JPWealth/JPW_Genetrix_Risk_Store.mqh>

// Read-model presentation only. Selection is instance RAM, never a chart
// preference, an account switch, a thesis declaration or a trading command.
JPWLedgerCycle g_genetrix_cycles[];
JPWLedgerView g_genetrix_view;
string g_genetrix_selected_cycle="";
string g_genetrix_ledger_reason="Aguardando ledger desta instalação";
bool g_genetrix_ledger_available=false;
string g_genetrix_cycle_button_id[16];
int g_genetrix_cycle_button_count=0;
JPWRiskView g_genetrix_risk_view;
bool g_genetrix_risk_available=false;
string g_genetrix_risk_reason="Registro do supervisor ainda não consultado";

int JPWGenetrixFindCycle(JPWLedgerCycle &cycles[],const string cycle_id)
  {
   if(cycle_id=="") return(-1);
   for(int i=0;i<ArraySize(cycles);i++)
      if(cycles[i].cycle_id==cycle_id) return(i);
   return(-1);
  }

string JPWGenetrixSignedNumber(const double value)
  {
   if(!MathIsValidNumber(value)) return("N/A");
   string shown=DoubleToString(value,2);
   StringReplace(shown,".",",");
   return(shown);
  }

string JPWGenetrixMoney(const double value,const string currency)
  { return(currency+" "+JPWGenetrixSignedNumber(value)); }

string JPWGenetrixCycleScope(JPWLedgerCycle &cycle)
  { return(cycle.symbol+" "+(cycle.side==1 ? "BUY" : (cycle.side==-1 ? "SELL" : "direção N/A"))); }

string JPWGenetrixCycleState(JPWLedgerCycle &cycle)
  {
   if(cycle.state==1) return("Posições abertas");
   if(cycle.state==2) return("Sem posições · pendentes ativas");
   if(cycle.state==3) return("Encerrado · histórico");
   if(cycle.state==4) return("Provisório · origem não confirmada");
   return("Estado indisponível");
  }

string JPWGenetrixGenesisLabel(JPWLedgerCycle &cycle)
  {
   if(cycle.genesis_ambiguous) return("AMBÍGUA");
   return(cycle.genesis_inferred ? "INFERIDA" : "não identificada");
  }

// A ledger projection, never a census reconstructed from live positions.
// Old envelopes lack this list; absence must not become a zero-member claim.
bool JPWGenetrixMemberIdentifiers(JPWLedgerCycle &cycle,string &identifiers[])
  {
   ArrayResize(identifiers,0);
   if(!cycle.members_available) return(false);
   if(cycle.member_identifiers=="") return(cycle.state==4 && !cycle.genesis_inferred);
   const int count=StringSplit(cycle.member_identifiers,',',identifiers);
   if(count<1) return(false);
   for(int i=0;i<count;i++)
     {
      if(StringLen(identifiers[i])<1 || StringGetCharacter(identifiers[i],0)<'1' ||
         StringGetCharacter(identifiers[i],0)>'9')
        { ArrayResize(identifiers,0); return(false); }
      for(int j=1;j<StringLen(identifiers[i]);j++)
         if(StringGetCharacter(identifiers[i],j)<'0' || StringGetCharacter(identifiers[i],j)>'9')
           { ArrayResize(identifiers,0); return(false); }
     }
   return(true);
  }

bool JPWGenetrixRecent(JPWLedgerView &view,const ulong now_ms)
  {
   return(view.quality==1 && view.observed_mono_ms>0 &&
      now_ms>=(ulong)view.observed_mono_ms &&
      now_ms-(ulong)view.observed_mono_ms<=30000);
  }

string JPWGenetrixCycleQuality(JPWLedgerView &view,JPWLedgerCycle &cycle,
                             const ulong now_ms)
  {
   if(cycle.cycle_id=="" || cycle.symbol=="" || (cycle.side!=1 && cycle.side!=-1) ||
      cycle.state<1 || cycle.state>3 || view.quality==0) return("N/A");
   if(cycle.state==3 || view.quality==2) return("Historical");
   if(cycle.partial || !cycle.history_complete || !cycle.costs_complete ||
      !view.history_complete || !view.costs_complete) return("Partial");
   if(JPWGenetrixRecent(view,now_ms) && cycle.amount_valid &&
      MathIsValidNumber(cycle.compensated)) return("Current");
   return("N/A");
  }

// Flags come from the ledger. This formatter never recomputes compensated
// result, percentages, completeness, allocation or financial capacity.
string JPWGenetrixCycleValue(JPWLedgerView &view,JPWLedgerCycle &cycle,
                           const ulong now_ms)
  {
   const string quality=JPWGenetrixCycleQuality(view,cycle,now_ms);
   if(quality!="Current") return(quality=="N/A" ? "N/A" : "N/A · "+quality);
   return(JPWGenetrixMoney(cycle.compensated,view.currency)+" · "+
      (cycle.percent_valid && MathIsValidNumber(cycle.percent) ?
       JPWGenetrixSignedNumber(cycle.percent)+"% saldo" : "N/A % saldo"));
  }

void JPWGenetrixInvalidate(const string reason,const bool clear_selection=true)
  {
   ArrayResize(g_genetrix_cycles,0);
   ZeroMemory(g_genetrix_view);
   if(clear_selection) g_genetrix_selected_cycle="";
   g_genetrix_ledger_available=false;
   g_genetrix_ledger_reason=reason;
   g_genetrix_cycle_button_count=0;
   ZeroMemory(g_genetrix_risk_view);
   g_genetrix_risk_available=false;
   g_genetrix_risk_reason=reason;
  }

bool JPWGenetrixSelectCycle(const int index)
  {
   if(!g_genetrix_ledger_available || index<0 || index>=ArraySize(g_genetrix_cycles)) return(false);
   g_genetrix_selected_cycle=g_genetrix_cycles[index].cycle_id;
   return(g_genetrix_selected_cycle!="");
  }

int JPWGenetrixSelectedIndex()
  { return(JPWGenetrixFindCycle(g_genetrix_cycles,g_genetrix_selected_cycle)); }

string JPWGenetrixMetricQuality(const int index,const JPW_VIEW_QUALITY quality)
  {
   if(index!=6) return(JPWCockpitQualityText(quality));
   const int selected=JPWGenetrixSelectedIndex();
   if(!g_genetrix_ledger_available || selected<0) return("N/A");
   const string state=JPWGenetrixCycleQuality(g_genetrix_view,g_genetrix_cycles[selected],GetTickCount64());
   return(state=="Current" && quality!=JPW_VIEW_CURRENT ? "N/A" : state);
  }

string JPWGenetrixLedgerHealth()
  {
   if(!g_genetrix_ledger_available) return("Ledger: indisponível · "+g_genetrix_ledger_reason);
   return("Ledger: "+(g_genetrix_view.healthy ? "leitura íntegra" : "atenção")+
      "; histórico "+(g_genetrix_view.history_complete ? "completo declarado" : "incompleto")+
      "; custos "+(g_genetrix_view.costs_complete ? "completos declarados" : "incompletos")+
      ". "+g_genetrix_view.reason+". Saúde técnica não homologa a métrica nem o Estatuto.");
  }

string JPWGenetrixRiskSummary()
  {
   if(!g_genetrix_risk_available) return("Supervisor 7x: N/A · "+g_genetrix_risk_reason);
   JPWRiskView view=g_genetrix_risk_view;
   const long now=(long)TimeGMT();
   const bool current=(view.quality=="Current" && view.observed_utc>0 &&
      now>=view.observed_utc && now-view.observed_utc<=30);
   return("Supervisor 7x: "+(current ? "Current" : "N/A · última leitura")+" · "+view.state+
      (current && MathIsValidNumber(view.leverage) ? "; leverage "+DoubleToString(view.leverage,4)+"x" : "")+
      "; proteção "+(view.protection_incomplete ? "incompleta" : "estado registrado")+
      "; demo "+(view.demo_armed ? "armada no registro" : "desarmada no registro")+
      "; observado "+TimeToString((datetime)view.observed_utc,TIME_DATE|TIME_SECONDS)+
      " UTC. "+view.reason+". Registro não confirma atividade contínua. UI não arma nem negocia; 7x não substitui V11.");
  }

void JPWGenetrixPresentMetric()
  {
   const int index=6;
   g_cockpit_snapshot.metric[index].sample=g_metric_samples[index];
   g_cockpit_snapshot.metric[index].title="Flutuante compensado";
   g_cockpit_snapshot.metric[index].quality=JPW_VIEW_NA;
   g_cockpit_snapshot.metric[index].value="N/A";
   g_cockpit_snapshot.metric[index].reason=g_genetrix_ledger_reason;
   g_cockpit_snapshot.metric[index].detail="Ciclo contábil inferido; não certifica Operação formal V11. Resultado não libera RC.";
   if(!g_genetrix_ledger_available) return;
   const int selected=JPWGenetrixSelectedIndex();
   if(selected<0)
     {
      g_cockpit_snapshot.metric[index].reason=(ArraySize(g_genetrix_cycles)==0 ?
         "Nenhum ciclo identificado nesta leitura" :
         "Selecione um ciclo · "+IntegerToString(ArraySize(g_genetrix_cycles))+" disponível(is)");
      return;
     }
   JPWLedgerCycle cycle=g_genetrix_cycles[selected];
   const string state=JPWGenetrixCycleQuality(g_genetrix_view,cycle,GetTickCount64());
   const bool current=(state=="Current" && JPWSampleDisplayValid(g_metric_samples[index],g_sample_context,GetTickCount64()));
   g_cockpit_snapshot.metric[index].value=(current ? JPWGenetrixCycleValue(g_genetrix_view,cycle,GetTickCount64()) :
      (state=="Current" || state=="N/A" ? "N/A" : "N/A · "+state));
   g_cockpit_snapshot.metric[index].quality=(current ? JPW_VIEW_CURRENT : JPW_VIEW_NA);
   g_cockpit_snapshot.metric[index].reason=JPWGenetrixCycleScope(cycle)+" · "+JPWGenetrixCycleState(cycle)+
      "; histórico "+(cycle.history_complete ? "completo declarado" : "incompleto")+
      "; custos "+(cycle.costs_complete ? "completos declarados" : "incompletos")+". "+cycle.reason;
   g_cockpit_snapshot.metric[index].detail="Ciclo "+StringSubstr(cycle.cycle_id,0,16)+
      "; símbolo exato/direção: "+JPWGenetrixCycleScope(cycle)+
      "; leitura em "+TimeToString((datetime)g_genetrix_view.observed_utc,TIME_DATE|TIME_SECONDS)+
      " UTC; percentual usa saldo desta amostra. Gênese contábil "+
      JPWGenetrixGenesisLabel(cycle)+
      ". Não certifica tese, flag ou encerramento formal V11; não restaura RC.";
  }

#endif
