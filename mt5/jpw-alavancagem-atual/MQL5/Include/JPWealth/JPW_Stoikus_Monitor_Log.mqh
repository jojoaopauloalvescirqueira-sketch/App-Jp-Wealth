#ifndef JPW_STOIKUS_MONITOR_LOG_MQH
#define JPW_STOIKUS_MONITOR_LOG_MQH
// Ephemeral log state only. It cannot grant ownership or financial freshness.
enum JPWMonitorLogStage
  { JPW_MONITOR_LOG_IDENTITY=0,JPW_MONITOR_LOG_OWNERSHIP=1,
    JPW_MONITOR_LOG_ACTIVE=2,JPW_MONITOR_LOG_DEGRADED=3,
    JPW_MONITOR_LOG_LEASE_LOST=4,JPW_MONITOR_LOG_CONTEXT=5 };
struct JPWMonitorLogState
  {
   bool reported;
   int stage;
   string context,reason;
  };
void JPWMonitorLogReset(JPWMonitorLogState &state)
  { state.reported=false; state.stage=-1; state.context=""; state.reason=""; }
string JPWMonitorLogTransition(JPWMonitorLogState &state,const int stage,
                               const string context,const string reason)
  {
   if(state.reported && state.stage==stage && state.context==context && state.reason==reason)
      return("");
   const bool context_changed=state.reported && state.context!=context;
   const bool recovered=state.reported && state.stage!=JPW_MONITOR_LOG_ACTIVE &&
                        stage==JPW_MONITOR_LOG_ACTIVE;
   state.reported=true; state.stage=stage; state.context=context; state.reason=reason;
   string message="Stoikus · Monitor: ";
   if(stage==JPW_MONITOR_LOG_IDENTITY)
      message+="aguardando identidade da conta/instalação; nova tentativa a cada 1 s";
   else if(stage==JPW_MONITOR_LOG_OWNERSHIP)
      message+="aguardando titularidade; nova tentativa a cada 1 s";
   else if(stage==JPW_MONITOR_LOG_ACTIVE)
      message+="produtor ativo"+(recovered ? "; recuperado" : "")+
               ". Capturas e cobertura continuam com validação própria";
   else if(stage==JPW_MONITOR_LOG_DEGRADED)
      message+="estado degradado; confira os módulos afetados";
   else if(stage==JPW_MONITOR_LOG_LEASE_LOST)
      message+="lease perdida; produtor suspenso, aguardando nova titularidade";
   else
      message+="revalidando contexto da conta/instalação; publicação anterior suspensa";
   if(context_changed) message+=". Novo contexto da conta/instalação";
   if(reason!="") message+=". Motivo: "+reason;
   return(message+". Confira Conta → Sistema e mantenha o gráfico de apoio aberto.");
  }
#endif
