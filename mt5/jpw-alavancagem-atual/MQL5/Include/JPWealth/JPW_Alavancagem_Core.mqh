#ifndef JPW_ALAVANCAGEM_CORE_MQH
#define JPW_ALAVANCAGEM_CORE_MQH

// JPW Alavancagem Atual v1.2.0. Funcoes puras: nenhum acesso a conta, rede ou grafico.
// Cada valor monetario calculado fica na moeda indicada; so a exibicao arredonda.

enum JPW_RESULT
  {
   JPW_OK=0,
   JPW_BAD_EQUITY,
   JPW_UNSUPPORTED_CONTRACT,
   JPW_NO_CONVERSION,
   JPW_BAD_QUOTE,
   JPW_CALC_ERROR,
   JPW_UNVERIFIED_UNITS
  };

enum JPW_MODEL
  {
   JPW_MODEL_NONE=0,
   JPW_MODEL_FIAT_FOREX,
   JPW_MODEL_LINEAR
  };

struct JPWAccount
  {
   long login;
   string server;
   string currency;
  };

struct JPWPosition
  {
   ulong ticket;
   long identifier;
   string symbol;
   long direction;
   double volume;
  };

struct JPWInstrument
  {
   string symbol;
   int calc_mode;
   string base;
   string profit;
   double contract_size;
   bool underlying_verified; // CFD: SYMBOL_BASIS ou SYMBOL_ISIN presente.
  };

struct JPWQuote
  {
   string symbol;
   string base;
   string profit;
   double bid;
   double ask;
   long time_msc;
   bool conversion_pair; // Apenas modo FOREX fiduciario, nunca CFD da posicao.
  };

struct JPWRoute
  {
   bool valid;
   string source;
   string target;
   string intermediate;
   string first_symbol;
   string second_symbol;
   int first_direction;  // +1 base -> profit; -1 profit -> base.
   int second_direction;
  };

struct JPWClock
  {
   bool anchored;
   ulong started_mono_ms;
   ulong last_mono_ms;
   long last_current_sec;
   long anchor_server_ms;
   ulong anchor_mono_ms;
  };

bool JPWFinitePositive(const double value)
  {
   return(MathIsValidNumber(value) && value>0.0);
  }

bool JPWIsFiat(const string currency)
  {
   // Lista explicita de codigos fiduciarios ISO 4217. Nao inclui metais,
   // criptoativos nem unidades de conta em centavos como USC.
   if(StringLen(currency)!=3) return(false);
   const string codes=",AED,AFN,ALL,AMD,ANG,AOA,ARS,AWG,AZN,BAM,BBD,BDT,BGN,BHD,BIF,BMD,BND,BOB,BRL,BSD,BTN,BWP,BYN,BZD,CAD,CDF,CHF,CLP,CNY,COP,CRC,CUP,CVE,CZK,DJF,DKK,DOP,DZD,EGP,ERN,ETB,EUR,FJD,FKP,GBP,GEL,GHS,GIP,GMD,GNF,GTQ,GYD,HKD,HNL,HTG,HUF,IDR,ILS,INR,IQD,IRR,ISK,JMD,JOD,JPY,KES,KGS,KHR,KMF,KPW,KRW,KWD,KYD,KZT,LAK,LBP,LKR,LRD,LSL,LYD,MAD,MDL,MGA,MKD,MMK,MNT,MOP,MRU,MUR,MVR,MWK,MXN,MYR,MZN,NAD,NGN,NIO,NOK,NPR,NZD,OMR,PAB,PEN,PGK,PHP,PKR,PLN,PYG,QAR,RON,RSD,RUB,RWF,SAR,SBD,SCR,SDG,SEK,SGD,SHP,SLE,SOS,SRD,SSP,STN,SYP,SZL,THB,TJS,TMT,TND,TOP,TRY,TTD,TWD,TZS,UAH,UGX,USD,UYU,UZS,VES,VND,VUV,WST,XAF,XCD,XOF,XPF,YER,ZAR,ZMW,ZWG,";
   return(StringFind(codes,","+currency+",")>=0);
  }

// O codigo USC informa a unidade contabil, nao a unidade do contrato.
string JPWNormalizeCurrency(const string raw)
  {
   string currency=raw;
   StringTrimLeft(currency);
   StringTrimRight(currency);
   StringToUpper(currency);
   return(currency);
  }

bool JPWAccountUnits(const string raw,string &currency,double &divisor)
  {
   currency=JPWNormalizeCurrency(raw);
   divisor=0.0;
   if(currency=="USC")
     {
      currency="USD";
      divisor=100.0;
      return(true);
     }
   if(!JPWIsFiat(currency)) return(false);
   divisor=1.0;
   return(true);
  }

bool JPWContractScaleValid(const double scale)
  {
   return(MathIsValidNumber(scale) && (scale==1.0 || scale==0.01));
  }

// Entrada: lucro hipotetico na moeda da conta para escala contratual 1,
// comparado com quatro resultados nativos: +d, -d, +D, -D (D>d).
// A funcao nao chama OrderCalcProfit; so o script pode realizar essa coleta.
bool JPWVerifyScale(double &scale_one_profit[],double &native_profit[],
                    const double money_quantum,double &scale)
  {
   scale=0.0;
   if(ArraySize(scale_one_profit)!=4 || ArraySize(native_profit)!=4 ||
      !JPWFinitePositive(money_quantum)) return(false);
   for(int i=0;i<4;i++)
     {
      if(!MathIsValidNumber(scale_one_profit[i]) ||
         !MathIsValidNumber(native_profit[i]) ||
         MathAbs(native_profit[i])<100.0*money_quantum) return(false);
      if((i%2==0 && (scale_one_profit[i]<=0.0 || native_profit[i]<=0.0)) ||
         (i%2==1 && (scale_one_profit[i]>=0.0 || native_profit[i]>=0.0)))
         return(false);
     }
   if(MathAbs(scale_one_profit[2])<=MathAbs(scale_one_profit[0]) ||
      MathAbs(scale_one_profit[3])<=MathAbs(scale_one_profit[1]) ||
      MathAbs(native_profit[2])<=MathAbs(native_profit[0]) ||
      MathAbs(native_profit[3])<=MathAbs(native_profit[1])) return(false);
   int matches=0;
   double matched=0.0;
   for(int candidate=0;candidate<2;candidate++)
     {
      const double factor=(candidate==0 ? 1.0 : 0.01);
      bool agrees=true;
      for(int i=0;i<4;i++)
        {
         const double expected=scale_one_profit[i]*factor;
         if(!MathIsValidNumber(expected) ||
            MathAbs(expected)<100.0*money_quantum ||
            MathAbs(native_profit[i]-expected)>MathAbs(expected)*0.01)
            agrees=false;
        }
      if(agrees) { matches++; matched=factor; }
     }
   if(matches!=1) return(false);
   scale=matched;
   return(true);
  }

JPW_RESULT JPWClassify(JPWInstrument &instrument,JPW_MODEL &model)
  {
   model=JPW_MODEL_NONE;
   if(!JPWFinitePositive(instrument.contract_size) || instrument.symbol=="" ||
      !JPWIsFiat(instrument.profit)) return(JPW_UNSUPPORTED_CONTRACT);
   const bool forex=(instrument.calc_mode==SYMBOL_CALC_MODE_FOREX ||
                     instrument.calc_mode==SYMBOL_CALC_MODE_FOREX_NO_LEVERAGE);
   const bool cfd=(instrument.calc_mode==SYMBOL_CALC_MODE_CFD ||
                   instrument.calc_mode==SYMBOL_CALC_MODE_CFDLEVERAGE);
   if(forex && JPWIsFiat(instrument.base) &&
      instrument.base!=instrument.profit)
     {
      model=JPW_MODEL_FIAT_FOREX;
      return(JPW_OK);
     }
   if(instrument.base=="XAU" && (forex || cfd))
     {
      model=JPW_MODEL_LINEAR;
      return(JPW_OK);
     }
   // O modo CFD fornece a formula linear e o tamanho contratual, mas a
   // identidade do subjacente precisa constar de metadado explicito.
   if(cfd && instrument.base!="" && instrument.underlying_verified)
     {
      model=JPW_MODEL_LINEAR;
      return(JPW_OK);
     }
   return(JPW_UNSUPPORTED_CONTRACT);
  }

bool JPWAccountsEqual(JPWAccount &a,JPWAccount &b)
  {
   return(a.login==b.login && a.server==b.server && a.currency==b.currency);
  }

bool JPWPositionsEqual(JPWPosition &a[],JPWPosition &b[])
  {
   const int n=ArraySize(a);
   if(n!=ArraySize(b)) return(false);
   bool used[];
   if(ArrayResize(used,n)!=n) return(false);
   for(int k=0;k<n;k++) used[k]=false;
   for(int i=0;i<n;i++)
     {
      bool found=false;
      for(int j=0;j<n;j++)
        {
         if(used[j]) continue;
         if(a[i].ticket!=b[j].ticket || a[i].identifier!=b[j].identifier ||
            a[i].symbol!=b[j].symbol || a[i].direction!=b[j].direction ||
            a[i].volume!=b[j].volume) continue;
         used[j]=true;
         found=true;
         break;
        }
      if(!found) return(false);
     }
   return(true);
  }

void JPWClockReset(JPWClock &clock,const long initial_current_sec,const ulong mono_ms)
  {
   clock.anchored=false;
   clock.started_mono_ms=mono_ms;
   clock.last_mono_ms=mono_ms;
   clock.last_current_sec=initial_current_sec;
   clock.anchor_server_ms=0;
   clock.anchor_mono_ms=0;
  }

// TimeCurrent so testemunha uma nova cotacao depois de Reset. TimeTradeServer
// e estimativa dependente do relogio local: serve para cotejar, nunca como
// prova isolada. A projecao usa tempo monotono, inclusive se TimeCurrent parar.
bool JPWClockObserve(JPWClock &clock,const long current_sec,
                     const long estimated_server_sec,const ulong mono_ms,
                     const int max_age_sec,long &now_ms)
  {
   now_ms=0;
   if(max_age_sec<=0 || mono_ms<clock.last_mono_ms ||
      current_sec<=0 || estimated_server_sec<=0 ||
      current_sec<clock.last_current_sec)
     {
      clock.anchored=false;
      return(false);
     }
   const long estimate_ms=estimated_server_sec*1000;
   if(current_sec>clock.last_current_sec)
     {
      const long witness_ms=current_sec*1000;
      const long gap=estimate_ms-witness_ms;
      if(gap< -2000 || gap>(long)max_age_sec*1000)
        {
         clock.anchored=false;
         clock.last_current_sec=current_sec;
         clock.last_mono_ms=mono_ms;
         return(false);
        }
      clock.anchored=true;
      clock.anchor_server_ms=witness_ms;
      clock.anchor_mono_ms=mono_ms;
     }
   clock.last_current_sec=current_sec;
   clock.last_mono_ms=mono_ms;
   if(!clock.anchored || mono_ms<clock.anchor_mono_ms) return(false);
   now_ms=clock.anchor_server_ms+(long)(mono_ms-clock.anchor_mono_ms);
   const long drift=estimate_ms-now_ms;
   if(drift< -3000 || drift>3000)
     {
      clock.anchored=false;
      now_ms=0;
      return(false);
     }
   return(true);
  }

// Validade estrutural nao implica atualidade. O timestamp original e preservado.
bool JPWQuoteStoredMid(JPWQuote &quote,double &mid)
  {
   mid=0.0;
   if(quote.time_msc<=0 || !JPWFinitePositive(quote.bid) ||
      !JPWFinitePositive(quote.ask) || quote.ask<quote.bid) return(false);
   mid=quote.bid+(quote.ask-quote.bid)/2.0;
   return(JPWFinitePositive(mid));
  }

bool JPWQuoteMid(JPWQuote &quote,const long now_ms,const int max_age_sec,double &mid)
  {
   mid=0.0;
   if(now_ms<=0 || max_age_sec<=0 || quote.time_msc<=0 ||
      !JPWFinitePositive(quote.bid) || !JPWFinitePositive(quote.ask) ||
      quote.ask<quote.bid) return(false);
   const long age=now_ms-quote.time_msc;
   if(age< -2000 || age>(long)max_age_sec*1000) return(false);
   mid=quote.bid+(quote.ask-quote.bid)/2.0;
   return(JPWFinitePositive(mid));
  }

int JPWQuoteIndex(JPWQuote &quotes[],const string symbol)
  {
   for(int i=0;i<ArraySize(quotes);i++)
      if(quotes[i].symbol==symbol) return(i);
   return(-1);
  }

bool JPWLegRate(JPWQuote &quote,const string source,const string target,
                const long now_ms,const int max_age_sec,int &direction,double &rate,
                const bool stored=false)
  {
   direction=0;
   rate=0.0;
   if(!quote.conversion_pair || !JPWIsFiat(source) ||
      !JPWIsFiat(target) || source==target ||
      !JPWIsFiat(quote.base) || !JPWIsFiat(quote.profit) ||
      quote.base==quote.profit) return(false);
   double mid=0.0;
   if(stored)
     {
      if(!JPWQuoteStoredMid(quote,mid) ||
         (now_ms>0 && quote.time_msc>now_ms+2000)) return(false);
     }
   else if(!JPWQuoteMid(quote,now_ms,max_age_sec,mid)) return(false);
   if(quote.base==source && quote.profit==target)
     {
      direction=1;
      rate=mid;
      return(true);
     }
   if(quote.profit==source && quote.base==target)
     {
      direction=-1;
      rate=1.0/mid;
      return(JPWFinitePositive(rate));
     }
   return(false);
  }

bool JPWRouteRate(JPWRoute &route,JPWQuote &quotes[],const long now_ms,
                  const int max_age_sec,double &rate,const bool stored=false)
  {
   rate=0.0;
   if(!route.valid || !JPWIsFiat(route.source) || !JPWIsFiat(route.target))
      return(false);
   if(route.source==route.target && route.first_symbol=="" &&
      route.second_symbol=="")
     {
      rate=1.0;
      return(true);
     }
   int index=JPWQuoteIndex(quotes,route.first_symbol);
   if(index<0) return(false);
   const string first_target=(route.second_symbol=="" ? route.target : route.intermediate);
   int direction=0;
   double first=0.0;
   if(!JPWLegRate(quotes[index],route.source,first_target,now_ms,
                  max_age_sec,direction,first,stored) || direction!=route.first_direction)
      return(false);
   if(route.second_symbol=="")
     {
      rate=first;
      return(true);
     }
   if(route.intermediate==route.source || route.intermediate==route.target ||
      route.first_symbol==route.second_symbol) return(false);
   index=JPWQuoteIndex(quotes,route.second_symbol);
   if(index<0) return(false);
   double second=0.0;
   if(!JPWLegRate(quotes[index],route.intermediate,route.target,now_ms,
                  max_age_sec,direction,second,stored) || direction!=route.second_direction)
      return(false);
   rate=first*second;
   return(JPWFinitePositive(rate));
  }

// Mantem a rota anterior enquanto valida. Nova escolha: direta, inversa,
// duas etapas; dentro de cada classe, chave lexical (intermediaria/simbolos).
bool JPWFindRoute(const string source,const string target,JPWQuote &quotes[],
                  const long now_ms,const int max_age_sec,JPWRoute &previous,
                  JPWRoute &chosen,double &rate,const bool stored=false)
  {
   chosen.valid=false;
   rate=0.0;
   if(!JPWIsFiat(source) || !JPWIsFiat(target)) return(false);
   if(source==target)
     {
      chosen.valid=true;
      chosen.source=source;
      chosen.target=target;
      chosen.intermediate="";
      chosen.first_symbol="";
      chosen.second_symbol="";
      chosen.first_direction=0;
      chosen.second_direction=0;
      rate=1.0;
      return(true);
     }
   if(previous.valid && previous.source==source && previous.target==target &&
      JPWRouteRate(previous,quotes,now_ms,max_age_sec,rate,stored))
     {
      chosen=previous;
      return(true);
     }
   for(int preference=1;preference>=-1;preference-=2)
     {
      string best="";
      JPWRoute candidate;
      double best_rate=0.0;
      for(int i=0;i<ArraySize(quotes);i++)
        {
         int direction=0;
         double leg=0.0;
         if(!JPWLegRate(quotes[i],source,target,now_ms,max_age_sec,direction,leg,stored) ||
            direction!=preference) continue;
         if(best!="" && StringCompare(quotes[i].symbol,best)>=0) continue;
         best=quotes[i].symbol;
         best_rate=leg;
         candidate.valid=true;
         candidate.source=source;
         candidate.target=target;
         candidate.intermediate="";
         candidate.first_symbol=best;
         candidate.second_symbol="";
         candidate.first_direction=direction;
         candidate.second_direction=0;
        }
      if(best!="")
        {
         chosen=candidate;
         rate=best_rate;
         return(true);
        }
     }
   string best_key="";
   JPWRoute candidate;
   double best_rate=0.0;
   string intermediates[];
   for(int i=0;i<ArraySize(quotes);i++)
     {
      string intermediate="";
      if(quotes[i].base==source) intermediate=quotes[i].profit;
      else if(quotes[i].profit==source) intermediate=quotes[i].base;
      if(!JPWIsFiat(intermediate) || intermediate==source || intermediate==target)
         continue;
      bool known=false;
      for(int k=0;k<ArraySize(intermediates);k++)
         if(intermediates[k]==intermediate) known=true;
      if(known) continue;
      const int n=ArraySize(intermediates);
      if(ArrayResize(intermediates,n+1)!=n+1) return(false);
      intermediates[n]=intermediate;
     }
   for(int k=0;k<ArraySize(intermediates);k++)
     {
      const string intermediate=intermediates[k];
      string first_symbol="";
      string second_symbol="";
      int first_direction=0;
      int second_direction=0;
      double first_rate=0.0;
      double second_rate=0.0;
      for(int i=0;i<ArraySize(quotes);i++)
        {
         int direction=0;
         double leg=0.0;
         if(JPWLegRate(quotes[i],source,intermediate,now_ms,max_age_sec,
                       direction,leg,stored) &&
            (first_symbol=="" || StringCompare(quotes[i].symbol,first_symbol)<0))
           {
            first_symbol=quotes[i].symbol;
            first_direction=direction;
            first_rate=leg;
           }
         if(JPWLegRate(quotes[i],intermediate,target,now_ms,max_age_sec,
                       direction,leg,stored) &&
            (second_symbol=="" || StringCompare(quotes[i].symbol,second_symbol)<0))
           {
            second_symbol=quotes[i].symbol;
            second_direction=direction;
            second_rate=leg;
           }
        }
      if(first_symbol=="" || second_symbol=="" || first_symbol==second_symbol)
         continue;
      const double combined=first_rate*second_rate;
      if(!JPWFinitePositive(combined)) continue;
      const string key=intermediate+"/"+first_symbol+"/"+second_symbol;
      if(best_key!="" && StringCompare(key,best_key)>=0) continue;
      best_key=key;
      best_rate=combined;
      candidate.valid=true;
      candidate.source=source;
      candidate.target=target;
      candidate.intermediate=intermediate;
      candidate.first_symbol=first_symbol;
      candidate.second_symbol=second_symbol;
      candidate.first_direction=first_direction;
      candidate.second_direction=second_direction;
     }
   if(best_key=="") return(false);
   chosen=candidate;
   rate=best_rate;
   return(true);
  }

JPW_RESULT JPWGross(JPWPosition &positions[],JPWInstrument &instruments[],
                     JPWQuote &quotes[],const string account_currency,
                     const long now_ms,const int max_age_sec,
                     JPWRoute &routes[],double &gross)
  {
   gross=0.0;
   if(!JPWIsFiat(account_currency) || ArraySize(positions)!=ArraySize(instruments))
      return(JPW_CALC_ERROR);
   for(int i=0;i<ArraySize(positions);i++)
     {
      if(!JPWFinitePositive(positions[i].volume) ||
         positions[i].symbol!=instruments[i].symbol) return(JPW_CALC_ERROR);
      JPW_MODEL model=JPW_MODEL_NONE;
      JPW_RESULT classified=JPWClassify(instruments[i],model);
      if(classified!=JPW_OK) return(classified);
      const int own_index=JPWQuoteIndex(quotes,positions[i].symbol);
      if(own_index<0) return(JPW_BAD_QUOTE);
      double mid=0.0;
      if(!JPWQuoteMid(quotes[own_index],now_ms,max_age_sec,mid))
         return(JPW_BAD_QUOTE);
      const string source=(model==JPW_MODEL_FIAT_FOREX ?
                           instruments[i].base : instruments[i].profit);
      double rate=1.0;
      if(source!=account_currency)
        {
         int route_index=-1;
         for(int j=0;j<ArraySize(routes);j++)
            if(routes[j].source==source && routes[j].target==account_currency)
              {
               route_index=j;
               break;
              }
         JPWRoute previous;
         previous.valid=false;
         if(route_index>=0) previous=routes[route_index];
         JPWRoute chosen;
         if(!JPWFindRoute(source,account_currency,quotes,now_ms,max_age_sec,
                          previous,chosen,rate)) return(JPW_NO_CONVERSION);
         if(route_index<0)
           {
            route_index=ArraySize(routes);
            if(ArrayResize(routes,route_index+1)!=route_index+1) return(JPW_CALC_ERROR);
           }
         routes[route_index]=chosen;
        }
      double notional=positions[i].volume*instruments[i].contract_size;
      if(!JPWFinitePositive(notional)) return(JPW_CALC_ERROR);
      if(model==JPW_MODEL_LINEAR) notional*=mid;
      if(!JPWFinitePositive(notional)) return(JPW_CALC_ERROR);
      notional*=rate;
      if(!JPWFinitePositive(notional)) return(JPW_CALC_ERROR);
      gross+=MathAbs(notional); // Cada ticket contribui em bruto, sem compensacao.
      if(!MathIsValidNumber(gross) || gross<0.0) return(JPW_CALC_ERROR);
     }
   return(JPW_OK);
  }

// Escolha em duas passagens: todas as rotas atuais, depois ultimas cotacoes.
// Uma rota antiga nunca impede o uso de uma rota recente disponivel.
bool JPWFindRouteReading(const string source,const string target,
                          JPWQuote &quotes[],const long now_ms,
                          const int max_age_sec,const bool clock_valid,
                          const bool connected,JPWRoute &previous,
                          JPWRoute &chosen,double &rate,bool &estimated,
                          long &oldest)
  {
   estimated=false;
   oldest=0;
   const bool current_context=(clock_valid && connected && now_ms>0);
   bool found=false;
   if(current_context)
      found=JPWFindRoute(source,target,quotes,now_ms,max_age_sec,
                        previous,chosen,rate);
   if(!found)
     {
      estimated=true;
      found=JPWFindRoute(source,target,quotes,(clock_valid ? now_ms : 0),
                        max_age_sec,previous,chosen,rate,true);
     }
   if(!found) return(false);
   if(chosen.first_symbol!="")
     {
      const int index=JPWQuoteIndex(quotes,chosen.first_symbol);
      if(index<0) return(false);
      oldest=quotes[index].time_msc;
     }
   if(chosen.second_symbol!="")
     {
      const int index=JPWQuoteIndex(quotes,chosen.second_symbol);
      if(index<0) return(false);
      if(oldest==0 || quotes[index].time_msc<oldest)
         oldest=quotes[index].time_msc;
     }
   return(true);
  }

// target e equity ja devem estar na unidade fiduciaria normalizada pelo
// adapter. Cada escala e uma confirmacao independente para aquele instrumento.
// Falha de uma unica posicao recusa o agregado inteiro: nao devolve subtotal.
JPW_RESULT JPWGrossReading(JPWPosition &positions[],JPWInstrument &instruments[],
                           JPWQuote &quotes[],const string target,
                           const long now_ms,const int max_age_sec,
                           const bool clock_valid,const bool connected,
                           double &scales[],JPWRoute &routes[],double &gross,
                           bool &estimated,long &oldest)
  {
   gross=0.0;
   oldest=0;
   estimated=(!clock_valid || !connected || now_ms<=0);
   const int n=ArraySize(positions);
   if(!JPWIsFiat(target) || n!=ArraySize(instruments) || max_age_sec<=0)
      return(JPW_CALC_ERROR);
   if(n!=ArraySize(scales)) return(JPW_UNVERIFIED_UNITS);
   double complete=0.0;
   long oldest_used=0;
   for(int i=0;i<n;i++)
     {
      if(!JPWContractScaleValid(scales[i])) return(JPW_UNVERIFIED_UNITS);
      if(positions[i].ticket==0 || !JPWFinitePositive(positions[i].volume) ||
         positions[i].symbol!=instruments[i].symbol ||
         (positions[i].direction!=POSITION_TYPE_BUY &&
          positions[i].direction!=POSITION_TYPE_SELL)) return(JPW_CALC_ERROR);
      for(int j=0;j<i;j++)
         if(positions[j].ticket==positions[i].ticket) return(JPW_CALC_ERROR);
      JPW_MODEL model=JPW_MODEL_NONE;
      const JPW_RESULT classified=JPWClassify(instruments[i],model);
      if(classified!=JPW_OK) return(classified);
      const int own_index=JPWQuoteIndex(quotes,positions[i].symbol);
      if(own_index<0) return(JPW_BAD_QUOTE);
      double mid=0.0;
      if(quotes[own_index].base!=instruments[i].base ||
         quotes[own_index].profit!=instruments[i].profit ||
         !JPWQuoteStoredMid(quotes[own_index],mid) ||
         (clock_valid && now_ms>0 && quotes[own_index].time_msc>now_ms+2000))
         return(JPW_BAD_QUOTE);
      double checked_mid=0.0;
      if(!clock_valid || !connected ||
         !JPWQuoteMid(quotes[own_index],now_ms,max_age_sec,checked_mid))
         estimated=true;
      if(oldest_used==0 || quotes[own_index].time_msc<oldest_used)
         oldest_used=quotes[own_index].time_msc;
      const string source=(model==JPW_MODEL_FIAT_FOREX ?
                           instruments[i].base : instruments[i].profit);
      double rate=1.0;
      if(source!=target)
        {
         int route_index=-1;
         for(int j=0;j<ArraySize(routes);j++)
            if(routes[j].source==source && routes[j].target==target)
              { route_index=j; break; }
         JPWRoute previous;
         previous.valid=false;
         if(route_index>=0) previous=routes[route_index];
         JPWRoute chosen;
         bool route_estimated=false;
         long route_oldest=0;
         if(!JPWFindRouteReading(source,target,quotes,now_ms,max_age_sec,
                                 clock_valid,connected,previous,chosen,rate,
                                 route_estimated,route_oldest))
            return(JPW_NO_CONVERSION);
         if(route_estimated) estimated=true;
         if(route_oldest>0 && (oldest_used==0 || route_oldest<oldest_used))
            oldest_used=route_oldest;
         if(route_index<0)
           {
            route_index=ArraySize(routes);
            if(ArrayResize(routes,route_index+1)!=route_index+1)
               return(JPW_CALC_ERROR);
           }
         routes[route_index]=chosen;
        }
      double notional=positions[i].volume*instruments[i].contract_size*scales[i];
      if(!JPWFinitePositive(notional)) return(JPW_CALC_ERROR);
      if(model==JPW_MODEL_LINEAR) notional*=mid;
      if(!JPWFinitePositive(notional)) return(JPW_CALC_ERROR);
      notional*=rate;
      if(!JPWFinitePositive(notional)) return(JPW_CALC_ERROR);
      complete+=MathAbs(notional);
      if(!MathIsValidNumber(complete) || complete<0.0) return(JPW_CALC_ERROR);
     }
   gross=complete;
   oldest=oldest_used;
   return(JPW_OK);
  }

JPW_RESULT JPWLeverage(const double gross,const double equity,double &leverage)
  {
   leverage=0.0;
   if(!JPWFinitePositive(equity)) return(JPW_BAD_EQUITY);
   if(!MathIsValidNumber(gross) || gross<0.0) return(JPW_CALC_ERROR);
   leverage=gross/equity;
   if(!MathIsValidNumber(leverage) || leverage<0.0 || (gross>0.0 && leverage==0.0)) return(JPW_CALC_ERROR);
   return(JPW_OK);
  }

string JPWFormatLeverage(const double leverage)
  {
   if(!MathIsValidNumber(leverage) || leverage<0.0) return("N/D");
   if(leverage>0.0 && leverage<0.01) return("<0,01x");
   string result=StringFormat("%.2f",leverage);
   StringReplace(result,".",",");
   return(result+"x");
  }

// B e P permanecem nas unidades originais da conta: em USC, a escala cancela.
// O resultado e independente da conversao do nocional e do equity.
bool JPWFloatingPercent(const double balance,const double profit,double &percent)
  {
   percent=0.0;
   if(!JPWFinitePositive(balance) || !MathIsValidNumber(profit)) return(false);
   if(profit==0.0) return(true);
   double result=100.0*(profit/balance);
   if(result==0.0)
     {
      // Recupera um quociente subnormal, se o resultado final for representavel.
      const double scaled=100.0*profit;
      if(MathIsValidNumber(scaled)) result=scaled/balance;
     }
   if(!MathIsValidNumber(result) || result==0.0) return(false);
   percent=result;
   return(true);
  }

// Deficit do equity informado pelo terminal em relacao ao saldo corrente.
// ACCOUNT_CREDIT nao e subtraido nem adicionado a esta formula.
bool JPWBalanceDDPercent(const double balance,const double equity,double &percent)
  {
   percent=0.0;
   if(!JPWFinitePositive(balance) || !MathIsValidNumber(equity)) return(false);
   if(equity>=balance) return(true);
   const double deficit=balance-equity;
   if(!JPWFinitePositive(deficit)) return(false);
   double result=100.0*(deficit/balance);
   if(result==0.0)
     {
      const double scaled=100.0*deficit;
      if(MathIsValidNumber(scaled)) result=scaled/balance;
     }
   if(!JPWFinitePositive(result)) return(false);
   percent=result;
   return(true);
  }

string JPWFormatPercent(const double value,const bool signed_value)
  {
   if(!MathIsValidNumber(value)) return("N/D");
   if(value==0.0) return("0,00%");
   const string prefix=(value<0.0 ? "-" : (signed_value ? "+" : ""));
   const double magnitude=MathAbs(value);
   if(magnitude<0.01) return(prefix+"<0,01%");
   string result=StringFormat("%.2f",magnitude);
   StringReplace(result,".",",");
   return(prefix+result+"%");
  }

#endif
