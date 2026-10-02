#ifndef JPW_SIGNAL_COPY_CORE_MQH
#define JPW_SIGNAL_COPY_CORE_MQH
#include <JPWealth/JPW_SignalCopy_Types.mqh>
#include <JPWealth/JPW_Alavancagem_RaizN_Core.mqh>

// Pure transient composition. No terminal, chart, file, clock or trade calls.
// This is a manually reviewed message, not a trade request or thesis record.
string JPWSignalQualityText(const int quality)
  {
   if(quality==2) return("Current");
   if(quality==1) return("Estimated");
   return("N/A");
  }

string JPWSignalOrderTypeText(JPWSignalRow &row)
  {
   if(row.kind==JPW_SIGNAL_POSITION)
     {
      if(row.side==POSITION_TYPE_BUY) return("BUY");
      if(row.side==POSITION_TYPE_SELL) return("SELL");
      return("N/A");
     }
   if(row.order_type==ORDER_TYPE_BUY_LIMIT) return("BUY LIMIT");
   if(row.order_type==ORDER_TYPE_SELL_LIMIT) return("SELL LIMIT");
   if(row.order_type==ORDER_TYPE_BUY_STOP) return("BUY STOP");
   if(row.order_type==ORDER_TYPE_SELL_STOP) return("SELL STOP");
   if(row.order_type==ORDER_TYPE_BUY_STOP_LIMIT) return("BUY STOP LIMIT");
   if(row.order_type==ORDER_TYPE_SELL_STOP_LIMIT) return("SELL STOP LIMIT");
   return("N/A");
  }

string JPWSignalRoleText(JPWSignalMember &member,const bool netting)
  {
   if(netting) return("Posição agregada — netting");
   string role="Papel não definido";
   if(member.role==1) role="Gênese";
   else if(member.role>=2) role="Defesa "+IntegerToString(member.role-1);
   if(member.origin==JPW_SIGNAL_CONFIRMED) return(role+" · conferida pelo usuário");
   if(member.origin==JPW_SIGNAL_REFERENCE) return(role+" · referência acompanhada");
   return(role+" · inferida");
  }

bool JPWSignalRowValid(JPWSignalRow &row,const bool require_stop,string &reason)
  {
   reason="";
   if((row.kind!=JPW_SIGNAL_POSITION && row.kind!=JPW_SIGNAL_PENDING) ||
      row.ticket==0 || row.symbol=="" ||
      (row.side!=POSITION_TYPE_BUY && row.side!=POSITION_TYPE_SELL) ||
      !JPWFinitePositive(row.volume) || !JPWFinitePositive(row.entry) ||
      row.digits<0 || row.digits>16 || row.volume_digits<0 || row.volume_digits>8)
     { reason="Identidade ou valores do item inválidos"; return(false); }
   if(row.kind==JPW_SIGNAL_POSITION && row.identifier<=0)
     { reason="Identificador da posição indisponível"; return(false); }
   if(!MathIsValidNumber(row.sl) || row.sl<0.0 ||
      !MathIsValidNumber(row.tp) || row.tp<0.0)
     { reason="SL ou TP inválido"; return(false); }
   if(require_stop && row.sl<=0.0)
     { reason="SL obrigatório ausente"; return(false); }
   if(row.kind==JPW_SIGNAL_PENDING)
     {
      const bool buy=(row.order_type==ORDER_TYPE_BUY_LIMIT ||
                      row.order_type==ORDER_TYPE_BUY_STOP);
      const bool sell=(row.order_type==ORDER_TYPE_SELL_LIMIT ||
                       row.order_type==ORDER_TYPE_SELL_STOP);
      if((!buy && !sell) || (buy && row.side!=POSITION_TYPE_BUY) ||
         (sell && row.side!=POSITION_TYPE_SELL))
        { reason="Tipo da pendente não suportado para este cenário"; return(false); }
      if(!JPWFinitePositive(row.initial_volume) || row.volume>row.initial_volume)
        { reason="Volume remanescente da pendente inconsistente"; return(false); }
     }
   return(true);
  }

bool JPWSignalDistancePercent(JPWSignalRow &row,JPWSignalMetrics &metrics,
                               const bool from_entry,double &raw,double &percent)
  {
   raw=0.0; percent=0.0;
   const double price=(from_entry ? row.entry :
                       (row.side==POSITION_TYPE_BUY ? metrics.bid : metrics.ask));
   if(!JPWFinitePositive(price) || !JPWFinitePositive(row.sl) ||
      !JPWFinitePositive(metrics.tick_size) ||
      (row.side!=POSITION_TYPE_BUY && row.side!=POSITION_TYPE_SELL)) return(false);
   const double distance=(row.side==POSITION_TYPE_BUY ? price-row.sl : row.sl-price);
   if(!MathIsValidNumber(distance)) return(false);
   const double tolerance=metrics.tick_size*1e-8;
   if(!JPWFinitePositive(tolerance)) return(false);
   if(MathAbs(distance)<=tolerance) return(true);
   double result=100.0*(MathAbs(distance)/price);
   if(result==0.0)
     {
      const double scaled=100.0*MathAbs(distance);
      if(MathIsValidNumber(scaled)) result=scaled/price;
     }
   if(!JPWFinitePositive(result)) return(false);
   raw=distance; percent=result;
   return(true);
  }

// Current whole-account portfolio, with only the selected pending applied.
// A selected live position is already present and must never be added twice.
bool JPWSignalVirtualPositions(JPWSignalRow &rows[],const int selected,
                               const long margin_mode,JPWPosition &positions[],
                               string &reason)
  {
   ArrayResize(positions,0); reason="";
   const int count=ArraySize(rows);
   if(count<=0 || count>JPW_SIGNAL_MAX_ROWS || selected<0 || selected>=count)
     { reason="Item selecionado indisponível"; return(false); }
   if(margin_mode!=ACCOUNT_MARGIN_MODE_RETAIL_HEDGING &&
      margin_mode!=ACCOUNT_MARGIN_MODE_RETAIL_NETTING &&
      margin_mode!=ACCOUNT_MARGIN_MODE_EXCHANGE)
     { reason="Modo da conta indisponível"; return(false); }
   string validation="";
   if(!JPWSignalRowValid(rows[selected],false,validation))
     { reason=validation; return(false); }
   for(int i=0;i<count;i++)
     {
      for(int j=0;j<i;j++)
         if(rows[i].kind==rows[j].kind && rows[i].ticket==rows[j].ticket)
           { reason="Item duplicado no catálogo"; ArrayResize(positions,0); return(false); }
      if(rows[i].kind!=JPW_SIGNAL_POSITION) continue;
      if(!JPWSignalRowValid(rows[i],false,validation))
        { reason=validation; ArrayResize(positions,0); return(false); }
      const int next=ArraySize(positions);
      for(int j=0;j<next;j++)
        {
         if(positions[j].identifier==rows[i].identifier ||
            (margin_mode!=ACCOUNT_MARGIN_MODE_RETAIL_HEDGING &&
             positions[j].symbol==rows[i].symbol))
           { reason="Composição de posições inconsistente"; ArrayResize(positions,0); return(false); }
        }
      if(ArrayResize(positions,next+1)!=next+1)
        { reason="Memória insuficiente"; ArrayResize(positions,0); return(false); }
      positions[next].ticket=rows[i].ticket;
      positions[next].identifier=rows[i].identifier;
      positions[next].symbol=rows[i].symbol;
      positions[next].direction=rows[i].side;
      positions[next].volume=rows[i].volume;
     }
   if(rows[selected].kind==JPW_SIGNAL_POSITION) return(true);
   if(margin_mode==ACCOUNT_MARGIN_MODE_EXCHANGE)
     { reason="Cenário de pendente em bolsa não suportado"; ArrayResize(positions,0); return(false); }
   JPWSignalRow pending=rows[selected];
   int target=-1;
   if(margin_mode==ACCOUNT_MARGIN_MODE_RETAIL_NETTING)
      for(int i=0;i<ArraySize(positions);i++)
         if(positions[i].symbol==pending.symbol) target=i;
   if(target<0)
     {
      const int next=ArraySize(positions);
      // A partially executed order can share its ticket with the open
      // position. This entry is synthetic, not that native order identity.
      // At most `next` positive candidates are occupied: next+1 is sufficient.
      ulong synthetic_ticket=1;
      for(int candidate=0;candidate<=next;candidate++)
        {
         bool used=false;
         for(int i=0;i<next;i++)
            if(positions[i].ticket==synthetic_ticket) { used=true; break; }
         if(!used) break;
         synthetic_ticket++;
        }
      if(ArrayResize(positions,next+1)!=next+1)
        { reason="Memória insuficiente"; ArrayResize(positions,0); return(false); }
      positions[next].ticket=synthetic_ticket;
      positions[next].identifier=0; // Synthetic exposure, never a position identity.
      positions[next].symbol=pending.symbol;
      positions[next].direction=pending.side;
      positions[next].volume=pending.volume;
      return(true);
     }
   const double old_signed=(positions[target].direction==POSITION_TYPE_BUY ?
                            positions[target].volume : -positions[target].volume);
   const double delta=(pending.side==POSITION_TYPE_BUY ? pending.volume : -pending.volume);
   const double resulting=old_signed+delta;
   if(!MathIsValidNumber(resulting))
     { reason="Volume condicional inválido"; ArrayResize(positions,0); return(false); }
   const double tolerance=1e-12*MathMax(1.0,MathAbs(old_signed)+MathAbs(delta));
   if(MathAbs(resulting)<=tolerance)
     {
      const int size=ArraySize(positions);
      for(int i=target;i<size-1;i++) positions[i]=positions[i+1];
      ArrayResize(positions,size-1);
     }
   else
     {
      positions[target].direction=(resulting>0.0 ? POSITION_TYPE_BUY : POSITION_TYPE_SELL);
      positions[target].volume=MathAbs(resulting);
     }
   return(true);
  }

// Antiguidade only suggests message roles; it does not certify a thesis.
// A saved reference is stable. Closed/absent reference, missing dates or a tie
// leave roles unspecified, so the user must confer them explicitly.
bool JPWSignalSuggestMembers(JPWSignalRow &rows[],const int selected,
                              const long reference_identifier,
                              const bool reference_closed,
                              JPWSignalMember &members[],string &reason)
  {
   ArrayResize(members,0); reason="";
   if(selected<0 || selected>=ArraySize(rows))
     { reason="Item selecionado indisponível"; return(false); }
   const string symbol=rows[selected].symbol;
   const int side=rows[selected].side;
   if(symbol=="" || (side!=POSITION_TYPE_BUY && side!=POSITION_TYPE_SELL))
     { reason="Grupo selecionado indisponível"; return(false); }
   for(int i=0;i<ArraySize(rows);i++)
     {
      if(rows[i].symbol!=symbol || rows[i].side!=side) continue;
      const int next=ArraySize(members);
      if(ArrayResize(members,next+1)!=next+1)
        { ArrayResize(members,0); reason="Memória insuficiente"; return(false); }
      members[next].row=i;
      members[next].included=(rows[i].kind==JPW_SIGNAL_POSITION || i==selected);
      members[next].role=0;
      members[next].origin=JPW_SIGNAL_INFERRED;
     }
   // Stable chronology for presentation only. Ticket breaks display ties but
   // never authorizes a Genesis/Defense inference.
   for(int i=1;i<ArraySize(members);i++)
     {
      JPWSignalMember value=members[i]; int j=i-1;
      while(j>=0 && (rows[members[j].row].opened_msc>rows[value.row].opened_msc ||
            (rows[members[j].row].opened_msc==rows[value.row].opened_msc &&
             rows[members[j].row].ticket>rows[value.row].ticket)))
        { members[j+1]=members[j]; j--; }
      members[j+1]=value;
     }
   if(reference_closed)
     { reason="Referência encerrada; confira uma nova estrutura de mensagem"; return(true); }
   if(reference_identifier<0)
     { reason="Referência indisponível; confira os papéis manualmente"; return(true); }
   int reference=-1; bool ambiguous=false;
   for(int i=0;i<ArraySize(members);i++)
     {
      const int row=members[i].row;
      if(!members[i].included) continue;
      if(rows[row].opened_msc<=0) ambiguous=true;
      if(reference_identifier>0 && rows[row].kind==JPW_SIGNAL_POSITION &&
         rows[row].identifier==reference_identifier)
        { if(reference>=0) ambiguous=true; reference=i; }
      for(int j=0;j<i;j++)
         if(members[j].included && rows[members[j].row].opened_msc==rows[row].opened_msc)
            ambiguous=true;
     }
   if(reference_identifier>0 && reference<0)
     { reason="Referência não presente no grupo; confira os papéis"; return(true); }
   if(ambiguous)
     { reason="Horário ausente ou empate; confira os papéis"; return(true); }
   if(reference<0)
     {
      // A pending-only group has no executed Genesis yet.
      for(int i=0;i<ArraySize(members);i++)
         if(members[i].included && rows[members[i].row].kind==JPW_SIGNAL_POSITION)
           { reference=i; break; }
      if(reference<0)
        { reason="Sem Gênese executada; confira o papel planejado"; return(true); }
     }
   members[reference].role=1;
   members[reference].origin=(reference_identifier>0 ? JPW_SIGNAL_REFERENCE : JPW_SIGNAL_INFERRED);
   int defense=2;
   for(int i=0;i<ArraySize(members);i++)
      if(members[i].included && i!=reference)
         members[i].role=defense++;
   reason="Sugestão por símbolo e direção; tese não certificada";
   return(true);
  }

bool JPWSignalCanPrepare(JPWSignalCapture &capture,JPWSignalRow &rows[],
                         const int selected,JPWSignalMember &members[],
                         JPWSignalMetrics &metrics,string &reason)
  {
   reason="";
   if(capture.context=="" || capture.digest=="" || capture.account.login<=0 ||
      capture.account.server=="" || capture.account.currency=="" ||
      capture.observed_utc<=0 || capture.accepted_ms==0 ||
      !JPWFinitePositive(capture.balance) || !JPWFinitePositive(capture.equity) ||
      !MathIsValidNumber(capture.profit) || !MathIsValidNumber(capture.credit))
     { reason="Amostra da conta indisponível ou inconsistente"; return(false); }
   if(selected<0 || selected>=ArraySize(rows) || ArraySize(rows)>JPW_SIGNAL_MAX_ROWS)
     { reason="Item selecionado indisponível"; return(false); }
   if(!JPWSignalRowValid(rows[selected],true,reason)) return(false);
   if(!metrics.leverage_valid || !MathIsValidNumber(metrics.leverage) || metrics.leverage<0.0 ||
      metrics.leverage_quality<1 || metrics.leverage_quality>2)
     { reason="Alavancagem obrigatória indisponível"; return(false); }
   if(rows[selected].kind==JPW_SIGNAL_PENDING &&
      (!metrics.scenario_valid || !MathIsValidNumber(metrics.scenario_leverage) ||
       metrics.scenario_leverage<0.0))
     { reason="Cenário condicional da pendente indisponível"; return(false); }
   if(!metrics.floating_valid || !MathIsValidNumber(metrics.floating_percent) ||
      metrics.floating_quality<1 || metrics.floating_quality>2)
     { reason="Flutuante obrigatório indisponível"; return(false); }
   if(!metrics.root_valid || !JPWFinitePositive(metrics.root_1w) ||
      !JPWFinitePositive(metrics.root_2w) ||
      (metrics.factor!=1.5 && metrics.factor!=1.8) ||
      metrics.n_1w<=0 || metrics.n_2w<=0 || !JPWFinitePositive(metrics.atr) ||
      metrics.atr_bar_time<=0 || metrics.root_quality<1 || metrics.root_quality>2)
     { reason="Raiz N 1W/2W obrigatória indisponível"; return(false); }
   if(!metrics.stop_valid || !JPWFinitePositive(metrics.bid) ||
      !JPWFinitePositive(metrics.ask) || metrics.bid>metrics.ask ||
      !JPWFinitePositive(metrics.point) || !JPWFinitePositive(metrics.tick_size) ||
      metrics.quote_time_msc<=0 || metrics.quote_quality<1 || metrics.quote_quality>2)
     { reason="Distância ao SL obrigatória indisponível"; return(false); }
   double raw_distance=0.0,stop_percent=0.0;
   if(!JPWSignalDistancePercent(rows[selected],metrics,true,raw_distance,stop_percent) ||
      !JPWSignalDistancePercent(rows[selected],metrics,false,raw_distance,stop_percent))
     { reason="Distância ao SL não representável"; return(false); }
   double expected_floating=0.0,price_distance=0.0,expected_1w=0.0,expected_2w=0.0;
   const double midpoint=metrics.bid+(metrics.ask-metrics.bid)/2.0;
   if(!JPWFloatingPercent(capture.balance,capture.profit,expected_floating) ||
      MathAbs(expected_floating-metrics.floating_percent)>
         1e-10*MathMax(1.0,MathAbs(expected_floating)) ||
      JPWRaizNCalculate(midpoint,metrics.atr,metrics.n_1w,metrics.factor,
                        price_distance,expected_1w)!=JPW_RAIZN_OK ||
      JPWRaizNCalculate(midpoint,metrics.atr,metrics.n_2w,metrics.factor,
                        price_distance,expected_2w)!=JPW_RAIZN_OK ||
      MathAbs(expected_1w-metrics.root_1w)>1e-10*MathMax(1.0,expected_1w) ||
      MathAbs(expected_2w-metrics.root_2w)>1e-10*MathMax(1.0,expected_2w))
     { reason="Métricas não correspondem à mesma amostra"; return(false); }
   bool selected_included=false; int genesis_count=0, included_count=0;
   const bool netting=(capture.margin_mode!=ACCOUNT_MARGIN_MODE_RETAIL_HEDGING);
   for(int i=0;i<ArraySize(members);i++)
     {
      const int row=members[i].row;
      if(row<0 || row>=ArraySize(rows))
        { reason="Composição da mensagem inválida"; return(false); }
      for(int j=0;j<i;j++)
         if(members[j].row==row)
           { reason="Item repetido na estrutura"; return(false); }
      if(!members[i].included) continue;
      included_count++;
      if(row==selected) selected_included=true;
      if(rows[row].symbol!=rows[selected].symbol || rows[row].side!=rows[selected].side)
        { reason="Estrutura inclui outro símbolo ou direção"; return(false); }
      if(members[i].origin!=JPW_SIGNAL_CONFIRMED)
        { reason="Confira explicitamente os membros da mensagem"; return(false); }
      if(!netting)
        {
         if(members[i].role<=0)
           { reason="Confira o papel de cada membro"; return(false); }
         if(members[i].role==1) genesis_count++;
         for(int j=0;j<i;j++)
            if(members[j].included && members[j].role==members[i].role)
              { reason="Papéis duplicados na estrutura"; return(false); }
        }
     }
   if(!selected_included || included_count<=0)
     { reason="O item selecionado deve integrar a mensagem"; return(false); }
   if(!netting && genesis_count>1)
     { reason="Confira no máximo uma Gênese para esta mensagem"; return(false); }
   JPWPosition virtual_positions[];
   if(!JPWSignalVirtualPositions(rows,selected,capture.margin_mode,virtual_positions,reason))
      return(false);
   return(true);
  }

string JPWSignalPercent(const double value,const bool signed_value=false)
  {
   if(value!=0.0 && MathAbs(value)<0.01)
     {
      const string sign=(value<0.0 ? "−" : (signed_value ? "+" : ""));
      return(sign+"<0.01%");
     }
   return((signed_value && value>0.0 ? "+" : "")+DoubleToString(value,2)+"%");
  }

string JPWSignalTimestamp(const long seconds)
  {
   if(seconds<=0) return("N/A");
   return(TimeToString((datetime)seconds,TIME_DATE|TIME_SECONDS));
  }

string JPWSignalStopDistance(JPWSignalRow &row,JPWSignalMetrics &metrics,
                             const bool from_entry)
  {
   double raw=0.0,percent=0.0;
   if(!JPWSignalDistancePercent(row,metrics,from_entry,raw,percent)) return("N/A");
   if(raw==0.0)
     {
      const string status=(from_entry ? "SL na entrada" : "SL reached");
      return("0.00% · "+status);
     }
   if(from_entry && raw<0.0)
      return(JPWSignalPercent(percent)+" · SL protege resultado");
   if(!from_entry && raw<0.0)
      return(JPWSignalPercent(-percent)+" · SL passed");
   return(JPWSignalPercent(percent)+" · SL à frente");
  }

// Formatting consumes the accepted capture; no hidden collection or mutation.
bool JPWSignalMessage(JPWSignalCapture &capture,JPWSignalRow &rows[],
                      const int selected,JPWSignalMember &members[],
                      JPWSignalMetrics &metrics,string &message,string &reason)
  {
   message="";
   if(!JPWSignalCanPrepare(capture,rows,selected,members,metrics,reason)) return(false);
   JPWSignalRow row=rows[selected];
   const bool pending=(row.kind==JPW_SIGNAL_PENDING);
   const bool netting=(capture.margin_mode!=ACCOUNT_MARGIN_MODE_RETAIL_HEDGING);
   const string quote_name=(row.side==POSITION_TYPE_BUY ? "Bid" : "Ask");
   const string direction=(row.side==POSITION_TYPE_BUY ? "Buy" : "Sell");
   string role="";
   double open_volume=0.0;
   for(int i=0;i<ArraySize(members);i++)
     {
      if(!members[i].included) continue;
      if(members[i].row==selected) role=JPWSignalRoleText(members[i],netting);
      if(rows[members[i].row].kind==JPW_SIGNAL_POSITION)
         open_volume+=rows[members[i].row].volume;
     }
   if(!MathIsValidNumber(open_volume))
     { reason="Exposição aberta não representável"; return(false); }
   if(pending && netting) role="Ordem pendente — netting · conferida pelo usuário";
   message=(pending ? "Pending Order | JP Wealth Model\n" : "New Order | JP Wealth Model\n");
   message+=(pending ? "Status: Ordem pendente\n" : "Status: Posição aberta\n");
   message+="Ordem: "+role+"\n";
   message+=(pending ? "Ticket da ordem: " : "Ticket da posição: ")+StringFormat("%I64u",row.ticket)+"\n";
   message+="Ativo: "+row.symbol+"\n";
   message+="Tipo: "+(pending ? JPWSignalOrderTypeText(row) : "Posição aberta · "+direction)+"\n";
   message+="Volume remanescente: "+DoubleToString(row.volume,row.volume_digits)+" lote\n";
   message+=(pending ? "Entrada planejada: " : "Entrada: ")+DoubleToString(row.entry,row.digits)+"\n";
   message+="Stop Loss: "+DoubleToString(row.sl,row.digits)+"\n";
   message+="Take Profit: "+(row.tp>0.0 ? DoubleToString(row.tp,row.digits) : "Sem TP")+"\n";
   message+="\n---\nEstrutura da operação — "+row.symbol+" · "+direction+"\n";
   for(int i=0;i<ArraySize(members);i++)
     {
      if(!members[i].included) continue;
      JPWSignalRow item=rows[members[i].row];
      if(item.kind!=JPW_SIGNAL_POSITION) continue;
      string item_role="Posição agregada — netting";
      if(!netting) item_role=(members[i].role==1 ? "Gênese" :
                             "Defesa "+IntegerToString(members[i].role-1));
      message+="🔹 "+item_role+": "+DoubleToString(item.volume,item.volume_digits)+
               " lote · "+StringFormat("%I64u",item.ticket)+" · Ativa\n";
     }
   bool pending_header=false;
   for(int i=0;i<ArraySize(members);i++)
     {
      if(!members[i].included) continue;
      JPWSignalRow item=rows[members[i].row];
      if(item.kind!=JPW_SIGNAL_PENDING) continue;
      if(!pending_header) { message+="\nPendentes incluídas:\n"; pending_header=true; }
      string item_role="Ordem pendente — netting";
      if(!netting) item_role=(members[i].role==1 ? "Gênese" :
                             "Defesa "+IntegerToString(members[i].role-1));
      message+="🔹 "+item_role+": "+DoubleToString(item.volume,item.volume_digits)+
               " lote · "+StringFormat("%I64u",item.ticket)+" · Pendente planejada\n";
     }
   message+="\nExposição aberta da operação: "+DoubleToString(open_volume,row.volume_digits)+" lote\n";
   message+="Alavancagem atual da conta: "+DoubleToString(metrics.leverage,2)+"x · "+
            JPWSignalQualityText(metrics.leverage_quality)+"\n";
   if(pending)
     {
      double conditional_volume=0.0;
      string conditional_direction=direction;
      if(netting)
        {
         JPWPosition projected[];
         if(!JPWSignalVirtualPositions(rows,selected,capture.margin_mode,projected,reason))
           { message=""; return(false); }
         for(int i=0;i<ArraySize(projected);i++)
            if(projected[i].symbol==row.symbol)
              {
               conditional_volume+=projected[i].volume;
               conditional_direction=(projected[i].direction==POSITION_TYPE_BUY ? "Buy" : "Sell");
              }
         if(conditional_volume==0.0) conditional_direction="posição zerada";
        }
      else conditional_volume=open_volume+row.volume;
      if(!MathIsValidNumber(conditional_volume))
        { message=""; reason="Exposição condicional não representável"; return(false); }
      message+="Exposição hipotética após somente esta pendente: "+
               DoubleToString(conditional_volume,row.volume_digits)+" lote · "+conditional_direction+"\n";
      message+="Alavancagem projetada após somente esta pendente: "+
               DoubleToString(metrics.scenario_leverage,2)+"x · "+JPWSignalQualityText(metrics.leverage_quality)+"\n";
     }
   message+="\n---\nRisk Management\n";
   message+="Entrada → SL: "+JPWSignalStopDistance(row,metrics,true)+"\n";
   message+="Mercado → SL: "+JPWSignalStopDistance(row,metrics,false)+" · "+
            JPWSignalQualityText(metrics.quote_quality)+"\n";
   message+="Raiz N 1W: "+JPWSignalPercent(metrics.root_1w)+" · F "+
            DoubleToString(metrics.factor,1)+" · "+JPWSignalQualityText(metrics.root_quality)+"\n";
   message+="Raiz N 2W: "+JPWSignalPercent(metrics.root_2w)+" · F "+
            DoubleToString(metrics.factor,1)+" · "+JPWSignalQualityText(metrics.root_quality)+"\n";
   message+="Flutuante da conta / saldo: "+JPWSignalPercent(metrics.floating_percent,true)+" · "+
            JPWSignalQualityText(metrics.floating_quality)+"\n";
   message+="\nLeitura: "+JPWSignalTimestamp(capture.observed_utc)+" UTC (relógio do computador)\n";
   message+="Cotação: "+JPWSignalTimestamp(metrics.quote_time_msc/1000)+" (servidor MT5; "+quote_name+" para distância ao SL)\n";
   message+="Barra ATR(55,H4): "+JPWSignalTimestamp(metrics.atr_bar_time)+" (servidor MT5)\n";
   message+="Abertura do item: "+JPWSignalTimestamp(row.opened_msc/1000)+" (servidor MT5)\n";
   if(!pending) message+="Identificador da posição: "+IntegerToString(row.identifier)+"\n";
   message+="N 1W/2W: "+IntegerToString(metrics.n_1w)+" / "+IntegerToString(metrics.n_2w)+"\n";
   message+="Moeda da conta: "+capture.account.currency+" (percentuais na mesma unidade; USC não escala preços)\n";
   if(pending)
     {
      const string scenario_basis=(netting ? "redução/zeragem/reversão por exposição líquida no ativo." :
                                   "a alavancagem usa a exposição bruta de toda a conta após somente esta pendente; lotes referem-se aos itens incluídos da operação.");
      message+="Cenário hipotético: apenas o volume remanescente selecionado; preços e equity congelados; "+
               scenario_basis+"\n";
     }
   if(capture.reference_closed)
      message+="Gênese registrada encerrada; nenhuma sucessora foi promovida.\n";
   else if(capture.reference_identifier<0)
      message+="Referência registrada indisponível; papéis conferidos somente para esta mensagem.\n";
   else if(capture.reference_identifier>0)
     {
      bool reference_included=false;
      for(int i=0;i<ArraySize(members);i++)
         if(members[i].included && rows[members[i].row].kind==JPW_SIGNAL_POSITION &&
            rows[members[i].row].identifier==capture.reference_identifier)
            reference_included=true;
      if(!reference_included)
         message+="Gênese registrada fora dos itens incluídos; nenhuma sucessora foi promovida.\n";
     }
   if(metrics.leverage_reason!="") message+="Estado alavancagem: "+metrics.leverage_reason+"\n";
   if(metrics.root_reason!="") message+="Estado Raiz N: "+metrics.root_reason+"\n";
   if(metrics.stop_reason!="") message+="Estado SL: "+metrics.stop_reason+"\n";
   if(metrics.floating_reason!="") message+="Estado flutuante: "+metrics.floating_reason+"\n";
   message+="Conferência transitória; não certifica tese, Gênese ou Defesas no Estatuto.\n";
   message+="Raiz N é diagnóstico do mercado atual; não é probabilidade remanescente do SL nem autorização de entrada.\n";
   message+="SL reached/passed indica nível geométrico, não execução. Não há envio ou negociação automática.";
   return(true);
  }
#endif
