#property copyright "JP Wealth"
#property version   "1.10"
#property script_show_inputs
#property description "JPW GENETRIX · Confirma a escala contratual USC por simbolo sem enviar ordens."

#include <JPWealth/JPW_Alavancagem_Terminal.mqh>
#include <JPWealth/JPW_Alavancagem_Profile.mqh>

#define JPW_USC_MAX_SYMBOLS 256
#define JPW_USC_WAIT_MS 30000

bool JPWUSCAddSymbol(string &symbols[],const string symbol)
  {
   if(symbol=="") return(false);
   for(int i=0;i<ArraySize(symbols);i++)
      if(symbols[i]==symbol) return(true);
   const int n=ArraySize(symbols);
   if(n>=JPW_USC_MAX_SYMBOLS || ArrayResize(symbols,n+1)!=n+1) return(false);
   symbols[n]=symbol;
   return(true);
  }

bool JPWUSCCollectSymbols(JPWPosition &positions[],string &symbols[])
  {
   ArrayResize(symbols,0);
   if(!JPWUSCAddSymbol(symbols,ChartSymbol(0))) return(false);
   for(int i=0;i<ArraySize(positions);i++)
      if(!JPWUSCAddSymbol(symbols,positions[i].symbol)) return(false);
   return(true);
  }

// A prova de unidade pode usar as ultimas cotacoes validas, inclusive sem
// novos ticks. Isto nao confere frescor ao indicador. Ordem hipotetica, tick
// values e quatro comparacoes devem continuar concordando integralmente.
bool JPWUSCPrepareCatalog()
  {
   const ulong started=GetTickCount64();
   while(!IsStopped() && GetTickCount64()>=started &&
         GetTickCount64()-started<JPW_USC_WAIT_MS)
     {
      if(JPWPrepareCatalog()) return(true);
      Sleep(50);
     }
   return(false);
  }

bool JPWUSCMoneyQuantum(long &digits,double &quantum)
  {
   ResetLastError();
   digits=AccountInfoInteger(ACCOUNT_CURRENCY_DIGITS);
   quantum=0.0;
   if(GetLastError()!=0 || digits<0 || digits>8) return(false);
   quantum=MathPow(10.0,-(double)digits);
   return(JPWFinitePositive(quantum));
  }

bool JPWUSCProbeVolume(const string symbol,double &volume)
  {
   volume=0.0;
   double minimum=0.0;
   double maximum=0.0;
   double step=0.0;
   if(!SymbolInfoDouble(symbol,SYMBOL_VOLUME_MIN,minimum) ||
      !SymbolInfoDouble(symbol,SYMBOL_VOLUME_MAX,maximum) ||
      !SymbolInfoDouble(symbol,SYMBOL_VOLUME_STEP,step) ||
      !JPWFinitePositive(minimum) || !JPWFinitePositive(step) ||
      !JPWFinitePositive(maximum) || maximum<minimum) return(false);
   const double target=MathMax(minimum,MathMin(maximum,1.0));
   volume=minimum+MathFloor((target-minimum)/step+1e-8)*step;
   return(JPWFinitePositive(volume) && volume>=minimum-1e-8 &&
          volume<=maximum+1e-8);
  }

bool JPWUSCProbePrices(JPWInstrument &instrument,const double mid,
                       const double volume,const double rate,const double quantum,
                       double &open_price,double &small,double &large)
  {
   open_price=0.0;
   small=0.0;
   large=0.0;
   double tick_size=0.0;
   long digits=0;
   if(!SymbolInfoDouble(instrument.symbol,SYMBOL_TRADE_TICK_SIZE,tick_size) ||
      !SymbolInfoInteger(instrument.symbol,SYMBOL_DIGITS,digits) ||
      !JPWFinitePositive(tick_size) || digits<0 || digits>16 ||
      !JPWFinitePositive(mid) || !JPWFinitePositive(rate)) return(false);
   // A precisao monetaria vem da conta. Mesmo na escala menor, os
   // resultados devem superar 100 quanta; planejar 200 evita a fronteira.
   const double worst_per_tick=tick_size*volume*instrument.contract_size*
                               0.01*rate*100.0;
   if(!JPWFinitePositive(worst_per_tick)) return(false);
   if(!JPWFinitePositive(quantum)) return(false);
   const double min_ticks=MathCeil(200.0*quantum/worst_per_tick);
   const double relative_ticks=MathCeil(mid*0.001/tick_size);
   const double ticks=MathMax(10.0,MathMax(min_ticks,relative_ticks));
   if(!MathIsValidNumber(ticks) || ticks>100000000.0) return(false);
   small=ticks*tick_size;
   large=2.0*small;
   open_price=NormalizeDouble(MathRound(mid/tick_size)*tick_size,(int)digits);
   small=NormalizeDouble(small,(int)digits);
   large=NormalizeDouble(large,(int)digits);
   return(JPWFinitePositive(open_price) && JPWFinitePositive(small) &&
          large>small && open_price-large>0.0 && large<open_price*0.10);
  }

bool JPWUSCVerifyInstrument(JPWInstrument &instrument,JPWAccount &account,
                            JPWQuote &quotes[],const double quantum,double &scale)
  {
   scale=0.0;
   JPW_MODEL model=JPW_MODEL_NONE;
   if(JPWClassify(instrument,model)!=JPW_OK) return(false);
   const int quote_index=JPWQuoteIndex(quotes,instrument.symbol);
   double mid=0.0;
   if(quote_index<0 || !JPWQuoteStoredMid(quotes[quote_index],mid))
      return(false);
   double rate=1.0;
   if(instrument.profit!="USD")
     {
      JPWRoute previous;
      previous.valid=false;
      JPWRoute chosen;
      bool estimated=false;
      long oldest=0;
      if(!JPWFindRouteReading(instrument.profit,"USD",quotes,0,30,
                              false,false,previous,chosen,rate,estimated,oldest)) return(false);
     }
   double volume=0.0;
   double open_price=0.0;
   double small=0.0;
   double large=0.0;
   if(!JPWUSCProbeVolume(instrument.symbol,volume) ||
      !JPWUSCProbePrices(instrument,mid,volume,rate,quantum,open_price,small,large))
      return(false);
   double predicted[];
   double native[];
   if(ArrayResize(predicted,4)!=4 || ArrayResize(native,4)!=4) return(false);
   for(int i=0;i<4;i++)
     {
      const double delta=(i==0 ? small : (i==1 ? -small : (i==2 ? large : -large)));
      const bool buy=(i<2);
      const ENUM_ORDER_TYPE side=(buy ? ORDER_TYPE_BUY : ORDER_TYPE_SELL);
      const double close_price=NormalizeDouble(open_price+
                                 (buy ? delta : -delta),
                                 (int)SymbolInfoInteger(instrument.symbol,SYMBOL_DIGITS));
      if(!JPWFinitePositive(close_price) || close_price==open_price) return(false);
      const double signed_move=(buy ? close_price-open_price : open_price-close_price);
      predicted[i]=signed_move*volume*instrument.contract_size*rate*100.0;
      native[i]=0.0;
      // OrderCalcProfit e apenas uma hipotese local; nunca envia ordem.
      ResetLastError();
      if(!OrderCalcProfit(side,instrument.symbol,volume,open_price,
                          close_price,native[i]))
        { Print("JPW USC: calculo nativo recusado, codigo ",GetLastError(),"; perfil nao alterado."); return(false); }
     }
   if(!JPWVerifyScale(predicted,native,quantum,scale)) return(false);
   return(JPWProfileTickConsistent(instrument,scale,account,quotes,0,
                                   false,false));
  }

bool JPWUSCVerifyAll(const string &symbols[],JPWInstrument &instruments[],
                     JPWAccount &account,const double quantum,
                     JPWProfileEntry &entries[],string &signatures[],
                     JPWQuote &quotes[],const datetime verified_at)
  {
   const int count=ArraySize(symbols);
   if(verified_at<=0 || ArrayResize(instruments,count)!=count ||
      ArrayResize(signatures,count)!=count) return(false);
   ArrayResize(quotes,0);
   ArrayResize(g_unsynchronized_symbols,0);
   const ulong started_all=GetTickCount64();
   for(int i=0;i<count;i++)
     {
      if(!JPWReadSpecification(symbols[i],instruments[i]) ||
         !JPWProfileSignature(instruments[i],signatures[i])) return(false);
      JPW_MODEL model=JPW_MODEL_NONE;
      if(JPWClassify(instruments[i],model)!=JPW_OK) return(false);
      if(!JPWCaptureQuote(symbols[i],instruments[i].base,
                          instruments[i].profit,quotes,false)) return(false);
      double mid=0.0;
      const int index=JPWQuoteIndex(quotes,symbols[i]);
      if(index<0 || !JPWQuoteStoredMid(quotes[index],mid)) return(false);
     }
   for(int i=0;i<count;i++)
     {
      if(instruments[i].profit=="USD") continue;
      const ulong started=GetTickCount64();
      if(!JPWPreparedRoute(instruments[i].profit,"USD",quotes,0,
                            started,false,false,30)) return(false);
     }
   for(int i=0;i<count;i++)
     {
      if(IsStopped() || GetTickCount64()<started_all ||
         GetTickCount64()-started_all>=JPW_USC_WAIT_MS) return(false);
      double scale=0.0;
      if(!JPWUSCVerifyInstrument(instruments[i],account,quotes,quantum,scale))
         return(false);
      string symbol_hash="";
      if(!JPWProfileHash(symbols[i],symbol_hash)) return(false);
      int found=-1;
      for(int j=0;j<ArraySize(entries);j++)
         if(entries[j].symbol_hash==symbol_hash) { found=j; break; }
      if(found<0)
        {
         found=ArraySize(entries);
         if(found>=JPW_PROFILE_MAX_ENTRIES ||
            ArrayResize(entries,found+1)!=found+1) return(false);
        }
      entries[found].symbol_hash=symbol_hash;
      entries[found].spec_hash=signatures[i]; // Captured BEFORE all native probes.
      entries[found].scale=scale;
      entries[found].verified_at=verified_at;
     }
   return(GetTickCount64()>=started_all &&
          GetTickCount64()-started_all<JPW_USC_WAIT_MS);
  }

void OnStart()
  {
   JPWAccount before;
   if(!JPWReadAccount(before) || before.currency!="USC")
     { Print("JPW USC: requer identidade de conta USC; perfil nao alterado."); return; }
   const bool connected_before=(bool)TerminalInfoInteger(TERMINAL_CONNECTED);
   long money_digits=0;
   double quantum=0.0;
   if(!JPWUSCMoneyQuantum(money_digits,quantum))
     { Print("JPW USC: precisao monetaria indisponivel; perfil nao alterado."); return; }
   JPWPosition positions_before[];
   if(!JPWReadSnapshot(positions_before))
     { Print("JPW USC: snapshot indisponivel; perfil nao alterado."); return; }
   const string chart_before=ChartSymbol(0);
   string symbols[];
   if(!JPWUSCCollectSymbols(positions_before,symbols))
     { Print("JPW USC: lista de instrumentos indisponivel; perfil nao alterado."); return; }
   JPWResetData();
   if(!JPWUSCPrepareCatalog())
     { Print("JPW USC: catalogo indisponivel; perfil nao alterado."); return; }
   JPWProfileEntry entries[];
   long generation=0;
   int slot=-1;
   if(JPWProfileLoadState(before,entries,generation,slot)==JPW_PROFILE_INVALID)
     { Print("JPW USC: perfil invalido; preserve os arquivos e solicite recuperacao antes de nova verificacao."); return; }
   JPWInstrument instruments[];
   JPWQuote quotes[];
   string signatures[];
   // Technical verification time uses the computer clock, not an invented tick time.
   const datetime verified_at=TimeLocal();
   if(!JPWUSCVerifyAll(symbols,instruments,before,quantum,entries,signatures,quotes,verified_at))
     { Print("JPW USC: unidade nao confirmada em todos os instrumentos; perfil nao alterado."); return; }
   JPWAccount after;
   JPWPosition positions_after[];
   long after_digits=0;
   double after_quantum=0.0;
   if(!JPWReadAccount(after) || !JPWAccountsEqual(before,after) ||
      !JPWReadSnapshot(positions_after) ||
      !JPWPositionsEqual(positions_before,positions_after) ||
      ChartSymbol(0)!=chart_before ||
      !JPWUSCMoneyQuantum(after_digits,after_quantum) ||
      money_digits!=after_digits || quantum!=after_quantum ||
      connected_before!=(bool)TerminalInfoInteger(TERMINAL_CONNECTED))
     { Print("JPW USC: conta, precisao ou posicoes mudaram; perfil nao alterado."); return; }
   for(int i=0;i<ArraySize(symbols);i++)
     {
      JPWInstrument current;
      string current_signature="";
      if(!JPWReadSpecification(symbols[i],current) ||
         !JPWProfileSignature(current,current_signature) ||
         signatures[i]!=current_signature)
        { Print("JPW USC: especificacao mudou; perfil nao alterado."); return; }
     }
   for(int q=0;q<ArraySize(quotes);q++)
      if(quotes[q].conversion_pair &&
         !JPWConversionMetadata(quotes[q].symbol,quotes[q].base,quotes[q].profit))
        { Print("JPW USC: metadados da conversao mudaram; perfil nao alterado."); return; }
   if(!JPWProfileSave(before,entries))
     { Print("JPW USC: gravacao recusada ou inconclusiva; perfil anterior preservado."); return; }
   Print("JPW USC: verificacao concluida para ",ArraySize(symbols),
         " instrumento(s). Perfil tecnico confirmado por releitura.");
  }
