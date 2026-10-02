#property copyright "JP Wealth"
#property version   "1.21"

#property description "JPW GENETRIX · Consulta sob demanda do máximo DD/saldo observado."

#include <JPWealth/JPW_Alavancagem_Version.mqh>
#include <JPWealth/JPW_Alavancagem_MDD.mqh>

bool JPWMDDCurrentAccount(JPWAccount &account)
  {
   account.login=AccountInfoInteger(ACCOUNT_LOGIN);
   account.server=AccountInfoString(ACCOUNT_SERVER);
   account.currency=JPWNormalizeCurrency(AccountInfoString(ACCOUNT_CURRENCY));
   string key="";
   string currency="";
   double scale=0.0;
   return(JPWMDDAccountKey(account,key,currency,scale));
  }

string JPWMDDViewText(const JPW_MDD_STATE state,JPWMDDRecord &record)
  {
   if(state==JPW_MDD_VALID)
     {
      return("Máximo observado de DD/saldo: "+
             JPWFormatPercent(record.max_percent,false)+"\n"+
             "Início da observação: "+
             TimeToString(record.observation_started_at,TIME_DATE|TIME_SECONDS)+
             " UTC (relógio do computador)\n"+
             "Amostra vencedora: "+
             TimeToString(record.observed_at_utc,TIME_DATE|TIME_SECONDS)+
             " UTC (relógio do computador)\n"+
             "Saldo na amostra: "+
             DoubleToString(record.balance_at_max,-16)+" "+record.currency+"\n"+
             "Equity na amostra: "+
             DoubleToString(record.equity_at_max,-16)+" "+record.currency+"\n\n"+
             "Somente amostras atuais válidas enquanto o indicador esteve ativo. " +
             "Não é histórico completo, MDD pico-a-vale nem DD operacional do Estatuto.");
     }
   if(state==JPW_MDD_ABSENT)
      return("Nenhum máximo observado de DD/saldo foi registrado para esta " +
             "conta nesta instalação do MT5. O indicador precisa coletar " +
             "uma amostra atual válida.");
   if(state==JPW_MDD_BUSY)
      return("O registro está ocupado ou o lock está indisponível. " +
             "Nenhum valor foi exibido; tente consultar novamente.");
   if(state==JPW_MDD_INVALID)
      return("O registro local de DD/saldo é inválido. " +
             "A consulta foi bloqueada; nenhum valor foi exibido.");
   if(state==JPW_MDD_INCOMPATIBLE)
      return("O registro local de DD/saldo usa uma versão incompatível. " +
             "A consulta foi bloqueada; nenhum valor foi exibido.");
   if(state==JPW_MDD_ACCOUNT_UNAVAILABLE)
      return("A identidade da conta está indisponível ou mudou durante a " +
             "consulta. Nenhum valor foi exibido.");
   return("A leitura do registro local de DD/saldo está indisponível. " +
          "Nenhum valor foi exibido.");
  }

void OnStart()
  {
   JPWAccount before;
   JPWMDDRecord record;
   JPWMDDClear(record);
   JPW_MDD_STATE state=JPW_MDD_ACCOUNT_UNAVAILABLE;
   if(JPWMDDCurrentAccount(before))
      state=JPWMDDReadOnly(before,JPW_MDD_FOLDER,record);
   string message=JPWMDDViewText(state,record);
   // A leitura ja liberou o lock. Confirme a identidade antes de abrir a caixa.
   JPWAccount after;
   if(!JPWMDDCurrentAccount(after))
     {
      JPWMDDClear(record);
      state=JPW_MDD_ACCOUNT_UNAVAILABLE;
     }
   else if(state!=JPW_MDD_ACCOUNT_UNAVAILABLE)
      state=JPWMDDConfirmAccount(before,after,state,record);
   if(state==JPW_MDD_ACCOUNT_UNAVAILABLE)
      message=JPWMDDViewText(state,record);
   MessageBox(message,JPW_PRODUCT_NAME+" · MDD observado sobre saldo",MB_OK);
  }
