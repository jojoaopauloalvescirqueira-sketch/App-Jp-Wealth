#ifndef JPW_ALAVANCAGEM_STOP_RISK_TERMINAL_MQH
#define JPW_ALAVANCAGEM_STOP_RISK_TERMINAL_MQH

#include <JPWealth/JPW_Alavancagem_StopRisk_Core.mqh>
#include <JPWealth/JPW_Alavancagem_RaizN_Observer.mqh>

// Read-only terminal adapter, safe to include from an indicator. In
// particular, OrderCalcProfit is deliberately absent from this file.
bool JPWStopRiskIdentity(string &key,string &currency,double &balance,
                         long &margin_mode,string &reason)
  {
   key=""; currency=""; balance=0.0; margin_mode=-1; reason="";
   const long login=AccountInfoInteger(ACCOUNT_LOGIN);
   const string server=AccountInfoString(ACCOUNT_SERVER);
   currency=JPWNormalizeCurrency(AccountInfoString(ACCOUNT_CURRENCY));
   const string installation=TerminalInfoString(TERMINAL_DATA_PATH);
   ResetLastError();
   balance=AccountInfoDouble(ACCOUNT_BALANCE);
   const int balance_error=GetLastError();
   ResetLastError();
   margin_mode=AccountInfoInteger(ACCOUNT_MARGIN_MODE);
   const int mode_error=GetLastError();
   if(balance_error!=0 || mode_error!=0 || !JPWFinitePositive(balance) ||
      !JPWObserverAccountKey(server,login,currency,installation,key) ||
      (margin_mode!=ACCOUNT_MARGIN_MODE_RETAIL_HEDGING &&
       margin_mode!=ACCOUNT_MARGIN_MODE_RETAIL_NETTING &&
       margin_mode!=ACCOUNT_MARGIN_MODE_EXCHANGE))
     { reason="Identidade, saldo ou modo de conta indisponivel"; return(false); }
   return(true);
  }

int JPWStopRiskPendingSide(const int order_type)
  {
   if(order_type==ORDER_TYPE_BUY_LIMIT || order_type==ORDER_TYPE_BUY_STOP ||
      order_type==ORDER_TYPE_BUY_STOP_LIMIT) return(1);
   if(order_type==ORDER_TYPE_SELL_LIMIT || order_type==ORDER_TYPE_SELL_STOP ||
      order_type==ORDER_TYPE_SELL_STOP_LIMIT) return(-1);
   return(0);
  }

bool JPWStopRiskPendingSupported(const int order_type)
  {
   return(order_type==ORDER_TYPE_BUY_LIMIT ||
          order_type==ORDER_TYPE_BUY_STOP ||
          order_type==ORDER_TYPE_SELL_LIMIT ||
          order_type==ORDER_TYPE_SELL_STOP);
  }

int JPWStopRiskCompareRows(JPWStopRiskRow &a,JPWStopRiskRow &b)
  {
   if(a.kind<b.kind) return(-1);
   if(a.kind>b.kind) return(1);
   if(a.ticket<b.ticket) return(-1);
   if(a.ticket>b.ticket) return(1);
   return(0);
  }

void JPWStopRiskSortRows(JPWStopRiskRow &rows[],const int left,
                         const int right)
  {
   int i=left,j=right;
   JPWStopRiskRow pivot=rows[(left+right)/2];
   while(i<=j)
     {
      while(JPWStopRiskCompareRows(rows[i],pivot)<0) i++;
      while(JPWStopRiskCompareRows(rows[j],pivot)>0) j--;
      if(i<=j)
        { JPWStopRiskRow tmp=rows[i]; rows[i]=rows[j]; rows[j]=tmp;
          i++; j--; }
     }
   if(left<j) JPWStopRiskSortRows(rows,left,j);
   if(i<right) JPWStopRiskSortRows(rows,i,right);
  }

bool JPWStopRiskRawDigest(JPWStopRiskSample &sample,
                          JPWStopRiskRow &rows[],string &digest)
  {
   digest="";
   if(!JPWRaizNIsHash(sample.account_key) ||
      sample.currency=="" || !JPWFinitePositive(sample.balance) ||
      sample.row_count!=ArraySize(rows) ||
      sample.row_count>JPW_STOP_RISK_MAX_ROWS) return(false);
   string body=JPWRaizNFrame(sample.account_key)+
      JPWRaizNFrame(sample.currency)+
      JPWRaizNFrame(DoubleToString(sample.balance,-16))+
      JPWRaizNFrame(IntegerToString(sample.margin_mode))+
      JPWRaizNFrame(IntegerToString(sample.row_count));
   for(int i=0;i<ArraySize(rows);i++)
     {
      JPWStopRiskRow row=rows[i];
      if((row.kind!=JPW_STOP_RISK_POSITION &&
          row.kind!=JPW_STOP_RISK_PENDING) || row.ticket<=0 ||
         row.symbol=="" || !JPWFinitePositive(row.volume) ||
         !JPWFinitePositive(row.entry) || !MathIsValidNumber(row.sl) ||
         row.sl<0.0 || row.opened_msc<=0) return(false);
      body+=JPWRaizNFrame(IntegerToString(row.kind))+
            JPWRaizNFrame(IntegerToString(row.ticket))+
            JPWRaizNFrame(IntegerToString(row.identifier))+
            JPWRaizNFrame(IntegerToString(row.opened_msc))+
            JPWRaizNFrame(row.symbol)+
            JPWRaizNFrame(IntegerToString(row.side))+
            JPWRaizNFrame(IntegerToString(row.order_type))+
            JPWRaizNFrame(DoubleToString(row.volume,-16))+
            JPWRaizNFrame(DoubleToString(row.entry,-16))+
            JPWRaizNFrame(DoubleToString(row.sl,-16));
     }
   return(JPWRaizNHash(body,digest));
  }

// Complete account-wide collection: no symbol is dropped merely because it
// differs from the chart or Genesis group. The indicator later chooses one
// exact (symbol, side) group from this coherent account snapshot.
bool JPWStopRiskCollectRaw(const string expected_account_key,
                           JPWStopRiskSample &sample,
                           JPWStopRiskRow &rows[],string &reason)
  {
   JPWStopRiskClearSample(sample); ArrayResize(rows,0); reason="";
   if(!JPWStopRiskIdentity(sample.account_key,sample.currency,
                           sample.balance,sample.margin_mode,reason) ||
      sample.account_key!=expected_account_key)
     { reason="Conta mudou durante coleta de stops"; return(false); }
   const int positions=PositionsTotal();
   const int orders=OrdersTotal();
   if(positions<0 || orders<0 ||
      positions+orders>JPW_STOP_RISK_MAX_ROWS ||
      ArrayResize(rows,positions+orders)!=positions+orders)
     { reason="Numero de posicoes ou pendentes indisponivel"; return(false); }
   for(int i=0;i<positions;i++)
     {
      const ulong ticket=PositionGetTicket(i);
      JPWStopRiskRow row; JPWStopRiskClearRow(row);
      long type=-1,identifier=0,opened=0;
      if(ticket==0 || ticket>(ulong)LONG_MAX ||
         !PositionSelectByTicket(ticket) ||
         !PositionGetInteger(POSITION_TYPE,type) ||
         !PositionGetInteger(POSITION_IDENTIFIER,identifier) ||
         !PositionGetInteger(POSITION_TIME_MSC,opened) ||
         !PositionGetString(POSITION_SYMBOL,row.symbol) ||
         !PositionGetDouble(POSITION_VOLUME,row.volume) ||
         !PositionGetDouble(POSITION_PRICE_OPEN,row.entry) ||
         !PositionGetDouble(POSITION_SL,row.sl) ||
         identifier<=0 || opened<=0 || row.symbol=="" ||
         !JPWFinitePositive(row.volume) || !JPWFinitePositive(row.entry) ||
         !MathIsValidNumber(row.sl) || row.sl<0.0 ||
         (type!=POSITION_TYPE_BUY && type!=POSITION_TYPE_SELL))
        { reason="Posicao aberta incompleta"; return(false); }
      row.kind=JPW_STOP_RISK_POSITION;
      row.ticket=(long)ticket; row.identifier=identifier;
      row.opened_msc=opened;
      row.side=(type==POSITION_TYPE_BUY ? 1 : -1);
      row.reason="Risco ainda nao calculado";
      row.additional_reason="Cotacao ainda nao calculada";
      rows[i]=row;
     }
   for(int i=0;i<orders;i++)
     {
      const ulong ticket=OrderGetTicket(i);
      JPWStopRiskRow row; JPWStopRiskClearRow(row);
      long type=-1,opened=0;
      if(ticket==0 || ticket>(ulong)LONG_MAX ||
         !OrderSelect(ticket) ||
         !OrderGetInteger(ORDER_TYPE,type) ||
         !OrderGetInteger(ORDER_TIME_SETUP_MSC,opened) ||
         !OrderGetString(ORDER_SYMBOL,row.symbol) ||
         !OrderGetDouble(ORDER_VOLUME_CURRENT,row.volume) ||
         !OrderGetDouble(ORDER_PRICE_OPEN,row.entry) ||
         !OrderGetDouble(ORDER_SL,row.sl) ||
         opened<=0 || row.symbol=="" || !JPWFinitePositive(row.volume) ||
         !JPWFinitePositive(row.entry) ||
         !MathIsValidNumber(row.sl) || row.sl<0.0)
        { reason="Ordem pendente incompleta"; return(false); }
      row.kind=JPW_STOP_RISK_PENDING;
      row.ticket=(long)ticket; row.identifier=0; row.opened_msc=opened;
      row.order_type=(int)type;
      row.side=JPWStopRiskPendingSide((int)type);
      row.reason=(JPWStopRiskPendingSupported((int)type) ?
                  "Reserva ainda nao calculada" :
                  "Tipo de ordem pendente nao suportado");
      row.additional_reason="Nao se aplica a pendentes";
      rows[positions+i]=row;
     }
   if(ArraySize(rows)>1)
      JPWStopRiskSortRows(rows,0,ArraySize(rows)-1);
   for(int i=1;i<ArraySize(rows);i++)
      if(rows[i].kind==rows[i-1].kind && rows[i].ticket==rows[i-1].ticket)
        { reason="Tickets duplicados na coleta"; return(false); }
   string after_key="",after_currency="",identity_reason="";
   double after_balance=0.0;
   long after_mode=-1;
   if(PositionsTotal()!=positions || OrdersTotal()!=orders ||
      !JPWStopRiskIdentity(after_key,after_currency,after_balance,
                           after_mode,identity_reason) ||
      after_key!=sample.account_key ||
      after_currency!=sample.currency ||
      after_balance!=sample.balance ||
      after_mode!=sample.margin_mode)
     { reason="Conta ou composicao mudou durante coleta"; return(false); }
   sample.row_count=ArraySize(rows);
   if(!JPWStopRiskRawDigest(sample,rows,sample.composition_digest))
     { reason="Digest da composicao indisponivel"; return(false); }
   return(true);
  }

bool JPWStopRiskLiveDigest(const string account_key,string &digest,
                           string &reason)
  {
   digest="";
   JPWStopRiskSample sample;
   JPWStopRiskRow rows[];
   if(!JPWStopRiskCollectRaw(account_key,sample,rows,reason)) return(false);
   digest=sample.composition_digest;
   return(true);
  }

#endif
