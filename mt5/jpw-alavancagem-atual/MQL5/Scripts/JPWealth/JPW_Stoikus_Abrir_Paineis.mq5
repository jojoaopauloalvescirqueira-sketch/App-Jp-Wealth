#property copyright "JP Wealth"
#include <JPWealth/JPW_Alavancagem_Version.mqh>
#property version JPW_PRODUCT_MQL_VERSION
#property description "Stoikus · abre Conta e NoCuda no gráfico atual; preserva os componentes já presentes."

// Native indicator handles initialize their programs before ChartIndicatorAdd.
// Always inspect the whole chart first; a second instance could touch retained
// preferences or studies even if its later attachment were rejected.
bool JPWStoikusPanelName(const string name,const bool account)
  {
   if(!account)
      return(name==JPW_NOCUDA_SHORTNAME ||
             name=="JPW GENETRIX · NoCuda Channels" || name=="JPW_NoCuda_Channels");
   if(name=="JPW_Alavancagem_Atual") return(true);
   const string current=JPW_PRODUCT_NAME;
   const string current_prefix=current+" · Cockpit";
   const string legacy_prefix="JPW GENETRIX · Cockpit";
   return(name==current_prefix || StringFind(name,current_prefix+" ")==0 ||
          name==legacy_prefix || StringFind(name,legacy_prefix+" ")==0);
  }

// -1 means that presence could not be established. Fail closed rather than
// create a handle in an uncertain object namespace.
int JPWStoikusPanelCount(const long chart,const bool account,string &listed,bool &legacy)
  {
   listed=""; legacy=false;
   long windows=0;
   ResetLastError();
   if(!ChartGetInteger(chart,CHART_WINDOWS_TOTAL,0,windows) || windows<1)
     { Print("Stoikus · Abrir painéis: não foi possível consultar as janelas do gráfico. Erro ",GetLastError());
       return(-1); }
   int copies=0;
   for(int window=0;window<(int)windows;window++)
     {
      ResetLastError();
      const int total=ChartIndicatorsTotal(chart,window);
      if(total<0 || GetLastError()!=0)
        { Print("Stoikus · Abrir painéis: lista de indicadores indisponível. Erro ",GetLastError());
          return(-1); }
      for(int i=0;i<total;i++)
        {
         ResetLastError();
         const string name=ChartIndicatorName(chart,window,i);
         if(name=="")
           { Print("Stoikus · Abrir painéis: nome de indicador indisponível. Erro ",GetLastError());
             return(-1); }
         if(JPWStoikusPanelName(name,account))
           {
            if(listed!="") listed+="; ";
            listed+=name+" (janela "+IntegerToString(window)+")";
            if(StringFind(name,"JPW GENETRIX")==0 || name=="JPW_Alavancagem_Atual" ||
               name=="JPW_NoCuda_Channels") legacy=true;
            copies++;
           }
        }
     }
   return(copies);
  }

bool JPWStoikusOpenPanel(const long chart,const bool account,string &result)
  {
   const string role=(account ? "Conta" : "NoCuda");
   string listed=""; bool legacy=false;
   const int copies=JPWStoikusPanelCount(chart,account,listed,legacy);
   if(copies<0)
     { result="presença não confirmada; confira a lista em Ctrl+I e tente novamente";
       return(false); }
   if(copies>0)
     {
      result="listado e preservado: "+listed+"; confira versão e dados";
      if(legacy) result+=". Nome legado ou sem versão detectado; confira as versões em Ctrl+I e no Diário";
      if(copies>1) result+=". Há "+IntegerToString(copies)+" cópias; confira Ctrl+I";
      Print("Stoikus · ",role,": ",result);
      return(true);
     }

   ResetLastError();
   // Root at MQL5 so an EX5 in this script's folder cannot shadow Indicators.
   // No explicit parameters: keep each indicator's existing public defaults.
   const int handle=(account ?
      iCustom(ChartSymbol(chart),ChartPeriod(chart),"\\Indicators\\JPWealth\\JPW_Alavancagem_Atual") :
      iCustom(ChartSymbol(chart),ChartPeriod(chart),"\\Indicators\\JPWealth\\JPW_NoCuda_Channels"));
   const int create_error=GetLastError();
   if(handle==INVALID_HANDLE)
     {
      const string filename=(account ? "JPW_Alavancagem_Atual" : "JPW_NoCuda_Channels");
      result="falhou ao carregar (erro "+IntegerToString(create_error)+
         "). Compile "+filename+".mq5 no MetaEditor e confira MQL5\\Indicators\\JPWealth";
      Print("Stoikus · ",role,": ",result);
      return(false);
     }

   ResetLastError();
   const bool attached=ChartIndicatorAdd(chart,0,handle);
   const int attach_error=GetLastError();
   if(attached) ChartRedraw(chart);
   const int confirmed=(attached ? JPWStoikusPanelCount(chart,account,listed,legacy) : 0);
   // The chart owns its attached reference. Release only this script's handle.
   // Never delete by short name: that could also remove dependent indicators.
   string release_notice="";
   ResetLastError();
   if(!IndicatorRelease(handle))
     {
      release_notice=". Aviso: falha na liberação do handle da ferramenta (erro "+IntegerToString(GetLastError())+
         "). Confira o Diário; as instâncias listadas foram preservadas";
      Print("Stoikus · ",role,release_notice);
     }
   if(!attached)
     { result="carregado, mas falhou ao anexar (erro "+IntegerToString(attach_error)+
          "). Confira o Diário e execute a ferramenta novamente"+release_notice;
       Print("Stoikus · ",role,": ",result);
       return(false); }
   if(confirmed<1)
     { result="anexação não confirmada; confira Ctrl+I e o Diário antes de tentar novamente"+release_notice;
       Print("Stoikus · ",role,": ",result);
       return(false); }
   result="carregado, anexado e listado: "+listed+"; confira versão e dados"+release_notice;
   Print("Stoikus · ",role,": ",result);
   return(true);
  }

void OnStart()
  {
   const long chart=ChartID();
   // Preflight both components before initialization can touch chart objects.
   string account_listed="",nocuda_listed="";
   bool account_legacy=false,nocuda_legacy=false;
   const int account_copies=JPWStoikusPanelCount(chart,true,account_listed,account_legacy);
   const int nocuda_copies=JPWStoikusPanelCount(chart,false,nocuda_listed,nocuda_legacy);
   if(account_copies<0 || nocuda_copies<0)
     {
      const string message="Stoikus · Abertura incompleta. Conta e NoCuda: presença não confirmada.\n"
         "Confira a lista de indicadores em Ctrl+I e o Diário; depois tente novamente.\n"
         "Mantenha o Monitor em outro gráfico de apoio, aberto.";
      Print(message); Alert(message);
      return;
     }
   string account_result="",nocuda_result="";
   const bool account_ok=JPWStoikusOpenPanel(chart,true,account_result);
   const bool nocuda_ok=JPWStoikusOpenPanel(chart,false,nocuda_result);
   const string title=(account_ok && nocuda_ok ? "Painéis listados no gráfico" : "Abertura incompleta");
   const string message="Stoikus · "+title+".\nConta: "+account_result+".\nNoCuda: "+nocuda_result+
      ".\nA listagem não confirma funcionamento ou compatibilidade. Confira versões e dados; nenhuma instância existente foi substituída.\n"
      "Mantenha o Monitor em outro gráfico de apoio, aberto. Para ajustar Entradas: Ctrl+I > indicador > Editar.";
   // One visible result per execution. A successful addition stays in place
   // when its companion fails; rerunning opens only the missing component.
   Print(message); Alert(message);
  }
