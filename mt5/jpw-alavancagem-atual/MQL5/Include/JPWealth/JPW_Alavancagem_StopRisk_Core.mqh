#ifndef JPW_ALAVANCAGEM_STOP_RISK_CORE_MQH
#define JPW_ALAVANCAGEM_STOP_RISK_CORE_MQH

#include <JPWealth/JPW_Alavancagem_Core.mqh>

// Informative execution-to-current-SL risk. Money and balance are always in
// ACCOUNT_CURRENCY, including USC; neither side is divided by 100 alone.
#define JPW_STOP_RISK_POSITION 1
#define JPW_STOP_RISK_PENDING 2
#define JPW_STOP_RISK_MAX_ROWS 512

struct JPWStopRiskRow
  {
   int kind;
   long ticket;
   long identifier;
   long opened_msc;
   string symbol;
   int side;                 // +1 buy, -1 sell; 0 means unsupported direction.
   int order_type;           // MT5 pending type, or -1 for a live position.
   int valid;                // 1 only when execution/planned-entry to SL is known.
   double volume;
   double entry;
   double sl;
   double risk_money;
   double additional_money; // Market Bid/Ask to SL, positions only.
   string reason;
   int additional_valid;
   string additional_reason;
  };

struct JPWStopRiskSample
  {
   string account_key;
   long generation;
   long observed_utc;       // Local computer observation, not server execution.
   long observed_mono_ms;   // Milliseconds since OS boot; session lease detects MT5 restart.
   string currency;
   double balance;
   long margin_mode;
   string composition_digest;
   int row_count;
   string publisher_token;
   string checksum;
  };

void JPWStopRiskClearSample(JPWStopRiskSample &s)
  {
   s.account_key=""; s.generation=0; s.observed_utc=0;
   s.observed_mono_ms=0; s.currency=""; s.balance=0.0;
   s.margin_mode=-1; s.composition_digest=""; s.row_count=0;
   s.publisher_token=""; s.checksum="";
  }

void JPWStopRiskClearRow(JPWStopRiskRow &r)
  {
   r.kind=0; r.ticket=0; r.identifier=0; r.opened_msc=0;
   r.symbol=""; r.side=0; r.order_type=-1; r.valid=0;
   r.volume=0.0; r.entry=0.0; r.sl=0.0; r.risk_money=0.0;
   r.additional_money=0.0; r.reason="";
   r.additional_valid=0; r.additional_reason="";
  }

// OrderCalcProfit returns signed P/L in deposit currency. A protective SL
// cannot create a negative risk. It does not include slippage, costs or gaps.
bool JPWStopRiskLossFromProfit(const double signed_profit,double &money)
  {
   money=0.0;
   if(!MathIsValidNumber(signed_profit)) return(false);
   money=MathMax(0.0,-signed_profit);
   return(MathIsValidNumber(money) && money>=0.0);
  }

bool JPWStopRiskRowValid(JPWStopRiskRow &r)
  {
   if((r.kind!=JPW_STOP_RISK_POSITION && r.kind!=JPW_STOP_RISK_PENDING) ||
      r.ticket<=0 || r.symbol=="" || r.opened_msc<=0 ||
      !JPWFinitePositive(r.volume) ||
      !MathIsValidNumber(r.entry) || r.entry<0.0 ||
      !MathIsValidNumber(r.sl) || r.sl<0.0 ||
      !MathIsValidNumber(r.risk_money) || r.risk_money<0.0 ||
      !MathIsValidNumber(r.additional_money) || r.additional_money<0.0 ||
      (r.valid!=0 && r.valid!=1) ||
      (r.additional_valid!=0 && r.additional_valid!=1)) return(false);
   if(r.kind==JPW_STOP_RISK_POSITION &&
      (r.identifier<=0 || r.order_type!=-1 ||
       (r.side!=1 && r.side!=-1))) return(false);
   if(r.kind==JPW_STOP_RISK_PENDING && r.identifier!=0) return(false);
   if(r.valid==1 &&
      ((r.side!=1 && r.side!=-1) || !JPWFinitePositive(r.entry) ||
       !JPWFinitePositive(r.sl) || r.reason!="")) return(false);
   if(r.valid==0 && r.reason=="") return(false);
   if(r.kind==JPW_STOP_RISK_PENDING && r.additional_valid!=0) return(false);
   if(r.additional_valid==1 &&
      (r.kind!=JPW_STOP_RISK_POSITION || r.valid!=1 ||
       r.additional_reason!="")) return(false);
   return(true);
  }

// Caller must establish symbol/direction via saved Genesis or an unambiguous
// inferred group. No account-wide sum is silently called one operation.
bool JPWStopRiskAggregate(JPWStopRiskSample &sample,JPWStopRiskRow &rows[],
                          const string symbol,const int side,
                          double &total,double &percent_balance,
                          double &positions_money,double &pending_money,
                          double &additional_money,string &reason)
  {
   total=0.0; percent_balance=0.0; positions_money=0.0;
   pending_money=0.0; additional_money=0.0; reason="";
   if(sample.row_count!=ArraySize(rows) || symbol=="" ||
      (side!=1 && side!=-1) || !JPWFinitePositive(sample.balance))
     { reason="Amostra, grupo ou saldo invalido"; return(false); }
   if(sample.margin_mode!=ACCOUNT_MARGIN_MODE_RETAIL_HEDGING)
     { reason="Netting/exchange: ordens de origem nao separaveis";
       return(false); }
   bool additional_complete=true;
   for(int i=0;i<ArraySize(rows);i++)
     {
      JPWStopRiskRow row=rows[i];
      if(!JPWStopRiskRowValid(row))
        { reason="Linha local invalida"; return(false); }
      if(row.symbol!=symbol) continue;
      if(row.side==0)
        { reason="Ordem pendente de direcao nao suportada"; return(false); }
      if(row.side!=side) continue;
      if(row.valid!=1)
        { reason=(row.reason=="" ? "Stop nao calculavel" : row.reason);
          return(false); }
      if(row.kind==JPW_STOP_RISK_POSITION)
        {
         positions_money+=row.risk_money;
         if(row.additional_valid==1) additional_money+=row.additional_money;
         else additional_complete=false;
        }
      else pending_money+=row.risk_money;
      if(!MathIsValidNumber(positions_money) ||
         !MathIsValidNumber(pending_money) ||
         !MathIsValidNumber(additional_money))
        { reason="Soma monetaria invalida"; return(false); }
     }
   total=positions_money+pending_money;
   // Keep the usual evaluation (including tiny ratios). If scaling the total
   // overflows, divide first; a representable percentage must not become N/A
   // solely because of an intermediate product.
   const double scaled_total=100.0*total;
   percent_balance=(MathIsValidNumber(scaled_total) ? scaled_total/sample.balance :
                    (total/sample.balance)*100.0);
   if(!MathIsValidNumber(total) || total<0.0 ||
      !MathIsValidNumber(percent_balance) || percent_balance<0.0)
     { reason="Risco ou percentual invalido"; return(false); }
   if(!additional_complete) additional_money=-1.0; // Explicit N/A sentinel.
   return(true);
  }

#endif
