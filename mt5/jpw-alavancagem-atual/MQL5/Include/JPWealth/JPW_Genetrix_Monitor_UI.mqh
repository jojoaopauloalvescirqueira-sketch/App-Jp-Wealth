#ifndef JPW_GENETRIX_MONITOR_UI_MQH
#define JPW_GENETRIX_MONITOR_UI_MQH
#include <JPWealth/JPW_Genetrix_Monitor_Status.mqh>
// Read-only presentation cache, separate from accepted financial samples.
// Only Coordinator collects diagnostics. Drawing never reads a file, renews a
// lease, starts a producer or changes a financial coverage declaration.
JPWMonitorSnapshot g_monitor_ui;
bool g_monitor_ui_available=false;
string g_monitor_ui_context="",g_monitor_ui_reason="Diagnóstico ainda não consultado nesta conta.";
ulong g_monitor_ui_next_ms=0;

void JPWMonitorUIInvalidate(const string reason)
  {
   ZeroMemory(g_monitor_ui);
   g_monitor_ui_available=false; g_monitor_ui_context="";
   g_monitor_ui_reason=reason; g_monitor_ui_next_ms=0;
  }

bool JPWMonitorUICaptureRecent(JPWMonitorModuleStatus &module,const ulong now_ms)
  {
   return(module.observed_mono_ms>0 && now_ms>=(ulong)module.observed_mono_ms &&
          now_ms-(ulong)module.observed_mono_ms<=JPW_MONITOR_STATUS_MAX_AGE_MS);
  }

string JPWMonitorUIStage(JPWMonitorModuleStatus &module,const bool present,const ulong now_ms)
  {
   // State identifiers belong to the public diagnostics contract.
   // Preserve quality literally, and never turn missing evidence into zero.
   if(module.state==JPW_MONITOR_CONFLICT) return("Conflito de produtor");
   if(module.state==JPW_MONITOR_FAILED) return("Falha · consulte o motivo");
   if(module.state==JPW_MONITOR_DETACHED) return("Não anexado ou indisponível");
   if(!present) return("Antigo · presença atual não confirmada");
   if(module.state==JPW_MONITOR_PREPARING) return("Preparando");
   if(module.state==JPW_MONITOR_PARTIAL) return(JPWMonitorUICaptureRecent(module,now_ms) ?
      "Cobertura incompleta" : "Cobertura incompleta · captura antiga/ausente");
   if(module.state==JPW_MONITOR_HISTORICAL || !JPWMonitorUICaptureRecent(module,now_ms))
      return("Antigo · última captura não confirma o presente");
   if(module.state==JPW_MONITOR_CURRENT) return("Captura Current declarada pelo módulo");
   return("Indisponível · estado não confirmado");
  }

string JPWMonitorUITime(const long wall,const long mono,const ulong now_ms)
  {
   if(wall<=0 || mono<=0) return("não confirmada");
   const string stamp=TimeToString((datetime)wall,TIME_DATE|TIME_SECONDS)+" UTC";
   if(now_ms<(ulong)mono) return(stamp+" · relógio monotônico incompatível");
   return(stamp+" · idade "+IntegerToString((long)((now_ms-(ulong)mono)/1000))+" s");
  }

string JPWMonitorUIGuidance(JPWMonitorModuleStatus &module,const bool present,const bool accounting=false)
  {
   if(module.state==JPW_MONITOR_CONFLICT) return("Confira os EAs em todos os gráficos. Retire produtores legados normalmente; não apague locks ou bancos.");
   if(module.state==JPW_MONITOR_FAILED) return("Confira o motivo e a aba Experts. Preserve os registros; falha deste módulo não aprova ou reprova o outro.");
   if(!present || module.state==JPW_MONITOR_DETACHED || module.state==JPW_MONITOR_HISTORICAL)
      return("Confira o núcleo no gráfico de apoio, a conexão e a aba Experts; aguarde revalidação da captura.");
   if(module.state==JPW_MONITOR_PREPARING) return("Aguarde a reconciliação e confira o progresso. Percentual de preparação não é cobertura histórica.");
   if(module.state==JPW_MONITOR_PARTIAL) return(accounting ?
      "Confira origem, período e custos. Não confirme cobertura sem evidência para liberar um número." :
      "Confira o motivo e as lacunas de cobertura. Preserve os registros; não declare completude sem evidência.");
   return("Consulte também a qualidade e o escopo da métrica; presença e saúde técnica não homologam o modelo.");
  }

#endif
