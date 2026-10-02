#ifndef JPW_NOCUDA_TERMINAL_MQH
#define JPW_NOCUDA_TERMINAL_MQH

// MT5 boundary for source-candle identity. Never infer candle counts from hours.
bool JPWNoCudaSnapCloseAtTime(const string symbol,
                             const ENUM_TIMEFRAMES source_tf,
                             const datetime click_time,datetime &bar_open,
                             double &bar_close,datetime &known_after,
                             string &reason)
  {
   const int shift=iBarShift(symbol,source_tf,click_time,false);
   if(shift<1)
     { reason="Selecione uma barra-fonte já encerrada."; return(false); }
   const datetime opened=iTime(symbol,source_tf,shift);
   const datetime next_open=iTime(symbol,source_tf,shift-1);
   const int period_seconds=PeriodSeconds(source_tf);
   if(opened<=0 || next_open<=opened || period_seconds<=0 ||
      click_time<opened || click_time>=opened+period_seconds)
     { reason="Clique em um candle-fonte existente, fora das lacunas."; return(false); }
   const double closed=iClose(symbol,source_tf,shift);
   if(!MathIsValidNumber(closed) || closed<=0.0)
     { reason="Fechamento do candle-fonte indisponível."; return(false); }
   bar_open=opened;
   bar_close=closed;
   known_after=next_open; // Conservative evidence: the following bar exists.
   reason="";
   return(true);
  }

bool JPWNoCudaClickedClose(const string symbol,const ENUM_TIMEFRAMES source_tf,
                          const int x,const int y,datetime &bar_open,
                          double &bar_close,datetime &known_after,string &reason)
  {
   int subwindow=-1;
   datetime click_time=0;
   double unused_price=0.0;
   if(!ChartXYToTimePrice(0,x,y,subwindow,click_time,unused_price) || subwindow!=0)
     { reason="Clique no gráfico principal."; return(false); }
   return(JPWNoCudaSnapCloseAtTime(symbol,source_tf,click_time,
                                  bar_open,bar_close,known_after,reason));
  }

bool JPWNoCudaExactBar(const string symbol,const ENUM_TIMEFRAMES source_tf,
                       const datetime opened,int &shift,double &closed,
                       datetime &known_after)
  {
   shift=iBarShift(symbol,source_tf,opened,true);
   if(shift<1 || iTime(symbol,source_tf,shift)!=opened) return(false);
   closed=iClose(symbol,source_tf,shift);
   known_after=iTime(symbol,source_tf,shift-1);
   return(MathIsValidNumber(closed) && closed>0.0 && known_after>opened);
  }

// The signature covers every observed source-bar opening/close in the anchor span.
// Added/removed bars or corrected closes require an explicit revision.
bool JPWNoCudaSourceSignature(const string symbol,const ENUM_TIMEFRAMES source_tf,
                              const datetime a,const datetime b,const datetime c,
                              datetime &range_first,datetime &range_last,
                              int &bar_count,string &signature,string &reason)
  {
   range_first=MathMin(a,MathMin(b,c));
   range_last=MathMax(a,MathMax(b,c));
   MqlRates bars[];
   const int copied=CopyRates(symbol,source_tf,range_first,range_last,bars);
   if(copied<=0 || copied!=ArraySize(bars) || bars[0].time!=range_first ||
      bars[copied-1].time!=range_last)
     { reason="Histórico-fonte insuficiente para validar as âncoras."; return(false); }
   string canonical="";
   for(int i=0;i<copied;i++)
     {
      if(i>0 && bars[i].time<=bars[i-1].time)
        { reason="Ordem de candles inconsistente."; return(false); }
      if(!MathIsValidNumber(bars[i].close) || bars[i].close<=0.0)
        { reason="Fechamento-fonte inválido."; return(false); }
      canonical+=StringFormat("%I64d|%.17g;",(long)bars[i].time,bars[i].close);
     }
   bar_count=copied;
   uchar source[]; uchar key[]; uchar digest[];
   const int copied_chars=StringToCharArray(canonical,source,0,WHOLE_ARRAY,CP_UTF8);
   if(copied_chars<=0 || ArrayResize(source,copied_chars-1)!=copied_chars-1 ||
      CryptEncode(CRYPT_HASH_SHA256,source,key,digest)!=32)
     { reason="Assinatura do histórico-fonte indisponível."; return(false); }
   signature="";
   for(int i=0;i<32;i++) signature+=StringFormat("%02x",(int)digest[i]);
   reason="";
   return(true);
  }

// Loaded candles from the visible source span, oldest first, including the
// current already-open bar only as a projection vertex (never selectable).
bool JPWNoCudaVisibleBars(const string symbol,const ENUM_TIMEFRAMES source_tf,
                          MqlRates &bars[],int &first_shift,string &reason)
  {
   const int width=(int)ChartGetInteger(0,CHART_WIDTH_IN_PIXELS);
   const int height=(int)ChartGetInteger(0,CHART_HEIGHT_IN_PIXELS);
   if(width<20 || height<20)
     { reason="Gráfico pequeno demais."; return(false); }
   int left_sub=-1,right_sub=-1;
   datetime left_time=0,right_time=0;
   double unused=0.0;
   if(!ChartXYToTimePrice(0,0,height/2,left_sub,left_time,unused) ||
      !ChartXYToTimePrice(0,width-1,height/2,right_sub,right_time,unused) ||
      left_sub!=0 || right_sub!=0)
     { reason="Escala do gráfico indisponível."; return(false); }
   int left_shift=iBarShift(symbol,source_tf,left_time,false);
   int right_shift=iBarShift(symbol,source_tf,right_time,false);
   if(left_shift<0 && right_shift<0)
     { reason="Candles-fonte ainda não carregados."; return(false); }
   const int available=Bars(symbol,source_tf);
   if(available<2)
     { reason="Histórico-fonte insuficiente."; return(false); }
   // Clip a viewport edge outside the loaded history instead of hiding all
   // visible source bars. Missing history is never synthesized as candles.
   if(left_shift<0) left_shift=available-1;
   if(right_shift<0) right_shift=0;
   first_shift=MathMin(available-1,MathMax(left_shift,right_shift)+1);
   const int newest=MathMax(0,MathMin(left_shift,right_shift)-1);
   const int count=first_shift-newest+1;
   if(count<=0 || CopyRates(symbol,source_tf,newest,count,bars)!=count)
     { reason="Falha ao ler a faixa de candles-fonte."; return(false); }
   reason="";
   return(true);
  }

#endif
