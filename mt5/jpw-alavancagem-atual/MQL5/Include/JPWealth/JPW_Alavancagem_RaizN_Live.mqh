#ifndef JPW_ALAVANCAGEM_RAIZN_LIVE_MQH
#define JPW_ALAVANCAGEM_RAIZN_LIVE_MQH

#include "JPW_Alavancagem_RaizN_Core.mqh"

// Coletor unico para o diagnostico corrente 1.6.0. O provedor nativo abaixo
// e substituido por um provedor sintetico nos testes do MESMO coletor.
// Nao seleciona posicoes, nao acessa Genesis, conta, USC ou persistencia.
struct JPWRaizNLiveSeries
  {
   datetime current_open;
   datetime closed_open;
   int bars;
   int calculated;
   bool synchronized;
  };

struct JPWRaizNLiveSample
  {
   double p0;
   double atr;
   double distance;
   double percent;
   datetime bar_time;
   datetime current_bar_time;
   long quote_time_msc;
   bool current;
   string reason;
  };

struct JPWRaizNLiveCache
  {
   string context_key;
   string symbol;
   datetime current_open;
   datetime closed_open;
   int bars;
   int calculated;
   double atr;
   bool valid;
   bool synchronized;
  };

void JPWRaizNLiveResetCache(JPWRaizNLiveCache &cache)
  {
   cache.context_key="";
   cache.symbol="";
   cache.current_open=0;
   cache.closed_open=0;
   cache.bars=0;
   cache.calculated=0;
   cache.atr=0.0;
   cache.valid=false;
   cache.synchronized=false;
  }

// Apenas esta pequena fronteira conhece a API do terminal. H4 e fixo no
// provedor nativo; o timeframe do grafico nao e uma entrada do coletor.
class JPWRaizNLiveProvider
  {
public:
   virtual string ExactSymbol() { return(""); }
   virtual bool ReadQuote(double &bid,double &ask,long &time_msc) { return(false); }
   virtual bool ReadSeries(JPWRaizNLiveSeries &series) { return(false); }
   virtual bool ReadClosedATR(double &atr) { return(false); }
   virtual bool Connected() { return(false); }
   virtual bool ClockValid() { return(false); }
   virtual long NowMilliseconds() { return(0); }
   virtual long MaxQuoteAgeMilliseconds() { return(0); }
  };

#ifndef JPW_RAIZN_LIVE_SYNTHETIC_ONLY
class JPWRaizNLiveNativeProvider : public JPWRaizNLiveProvider
  {
private:
   string m_symbol;
   int m_handle;
   bool m_connected;
   bool m_clock_valid;
   long m_now;
   long m_max_age;
public:
   void Configure(const string symbol,const int handle,const bool connected,
                  const bool clock_valid,const long now_ms,const long max_age_ms)
     {
      m_symbol=symbol;
      m_handle=handle;
      m_connected=connected;
      m_clock_valid=clock_valid;
      m_now=now_ms;
      m_max_age=max_age_ms;
     }
   virtual string ExactSymbol() { return(m_symbol); }
   virtual bool Connected() { return(m_connected); }
   virtual bool ClockValid() { return(m_clock_valid); }
   virtual long NowMilliseconds() { return(m_now); }
   virtual long MaxQuoteAgeMilliseconds() { return(m_max_age); }
   virtual bool ReadQuote(double &bid,double &ask,long &time_msc)
     {
      MqlTick tick;
      if(m_symbol=="" || !SymbolInfoTick(m_symbol,tick)) return(false);
      bid=tick.bid;
      ask=tick.ask;
      time_msc=tick.time_msc;
      return(true);
     }
   virtual bool ReadSeries(JPWRaizNLiveSeries &series)
     {
      if(m_symbol=="" || m_handle==INVALID_HANDLE) return(false);
      long synchronized=0;
      if(!SeriesInfoInteger(m_symbol,PERIOD_H4,SERIES_SYNCHRONIZED,synchronized))
         return(false);
      series.synchronized=(synchronized!=0);
      series.bars=Bars(m_symbol,PERIOD_H4);
      series.calculated=BarsCalculated(m_handle);
      datetime opened[1],closed[1];
      if(CopyTime(m_symbol,PERIOD_H4,0,1,opened)!=1 ||
         CopyTime(m_symbol,PERIOD_H4,1,1,closed)!=1) return(false);
      series.current_open=opened[0];
      series.closed_open=closed[0];
      return(true);
     }
   virtual bool ReadClosedATR(double &atr)
     {
      if(m_handle==INVALID_HANDLE) return(false);
      double value[1];
      // Shift 1 e exclusivamente a ultima barra concluida da serie H4.
      if(CopyBuffer(m_handle,0,1,1,value)!=1) return(false);
      atr=value[0];
      return(true);
     }
  };
#endif

bool JPWRaizNLiveSeriesValid(JPWRaizNLiveSeries &series)
  {
   // ATR(55) precisa de historico para os 55 true ranges e fechamento anterior.
   return(series.bars>=56 && series.calculated>=56 &&
          series.current_open>0 && series.closed_open>0 &&
          JPWRaizNBarClosedBy(series.closed_open,series.current_open));
  }

bool JPWRaizNLiveSeriesSame(JPWRaizNLiveSeries &a,JPWRaizNLiveSeries &b)
  {
   return(a.current_open==b.current_open && a.closed_open==b.closed_open &&
          a.bars==b.bars && a.calculated==b.calculated &&
          a.synchronized==b.synchronized);
  }

// One verified Bid/Ask tick and one completed ATR bar feed both standardized
// horizons. This function has no N/F input and makes no calibration claim.
bool JPWRaizNReadLiveBase(JPWRaizNLiveProvider &provider,
                          JPWRaizNLiveCache &cache,const string context_key,
                          JPWRaizNLiveSample &sample)
  {
   sample.p0=0.0;
   sample.atr=0.0;
   sample.distance=0.0;
   sample.percent=0.0;
   sample.bar_time=0;
   sample.current_bar_time=0;
   sample.quote_time_msc=0;
   sample.current=false;
   sample.reason="Dados indisponiveis";
   const string symbol=provider.ExactSymbol();
   if(cache.context_key!=context_key || cache.symbol!=symbol)
      JPWRaizNLiveResetCache(cache);
   if(context_key=="" || symbol=="")
     { sample.reason="Contexto indisponivel"; return(false); }
   JPWRaizNLiveSeries before,after;
   if(!provider.ReadSeries(before) || !JPWRaizNLiveSeriesValid(before))
     {
      cache.valid=false;
      sample.reason="Historico H4 insuficiente";
      return(false);
     }
   double bid=0.0,ask=0.0;
   long quote_time=0;
   if(!provider.ReadQuote(bid,ask,quote_time) ||
      !MathIsValidNumber(bid) || !MathIsValidNumber(ask) ||
      bid<=0.0 || ask<=0.0 || ask<bid || quote_time<=0)
     { sample.reason="Sem cotacao valida"; return(false); }
   const long now_ms=provider.NowMilliseconds();
   const bool clock_valid=(provider.ClockValid() && now_ms>0);
   // Mesma tolerancia de 2 s da coleta cambial; fora disso o futuro nao e
   // tratado como cotacao antiga utilizavel nem como sincronizacao provada.
   if(clock_valid && quote_time>now_ms+2000)
     { sample.reason="Horario da cotacao inconsistente"; return(false); }
   if(quote_time/1000<(long)before.current_open)
     { sample.reason="Cotacao anterior a serie H4"; return(false); }

   double atr=0.0;
   const bool cached=(cache.valid && cache.context_key==context_key &&
      cache.symbol==symbol && cache.current_open==before.current_open &&
      cache.closed_open==before.closed_open && cache.bars==before.bars &&
      cache.calculated==before.calculated && cache.synchronized &&
      before.synchronized);
   if(cached) atr=cache.atr;
   else if(!provider.ReadClosedATR(atr))
     { cache.valid=false; sample.reason="ATR H4 indisponivel"; return(false); }
   if(atr==EMPTY_VALUE || !MathIsValidNumber(atr) || atr<=0.0)
     { cache.valid=false; sample.reason="ATR H4 invalido"; return(false); }
   if(!provider.ReadSeries(after) || !JPWRaizNLiveSeriesValid(after) ||
      !JPWRaizNLiveSeriesSame(before,after) || symbol!=provider.ExactSymbol())
     {
      cache.valid=false;
      sample.reason="Serie H4 mudou durante a leitura";
      return(false);
     }
   // Forma que evita overflow intermediario em bid+ask.
   const double p0=bid*0.5+ask*0.5;
   cache.context_key=context_key;
   cache.symbol=symbol;
   cache.current_open=after.current_open;
   cache.closed_open=after.closed_open;
   cache.bars=after.bars;
   cache.calculated=after.calculated;
   cache.atr=atr;
   cache.synchronized=after.synchronized;
   cache.valid=true;
   sample.p0=p0;
   sample.atr=atr;
   sample.bar_time=after.closed_open;
   sample.current_bar_time=after.current_open;
   sample.quote_time_msc=quote_time;

   const long age=now_ms-quote_time;
   const bool recent=(clock_valid && provider.MaxQuoteAgeMilliseconds()>0 &&
                      age>=-2000 && age<=provider.MaxQuoteAgeMilliseconds());
   // Serie sincronizada nao basta para Current: a barra mais recente deve
   // conter tanto a cotacao quanto o relogio servidor comprovado. No fim de
   // semana ou feed parado, os ultimos dados completos sao Estimated.
   const long bar_end=((long)after.current_open+4*60*60)*1000;
   const bool current_history=(after.synchronized && clock_valid &&
      now_ms>=(long)after.current_open*1000 && now_ms<bar_end &&
      quote_time<bar_end);
   sample.current=(provider.Connected() && recent && current_history);
   if(sample.current) sample.reason="Current";
   else if(!provider.Connected()) sample.reason="Sem conexao";
   else if(!clock_valid) sample.reason="Referencia temporal nao confirmada";
   else if(!recent) sample.reason="Cotacao sem atualizacao comprovada";
   else sample.reason="Historico H4 nao confirmado como atual";
   return(true);
  }

// Retained unchanged at the public boundary for legacy manually declared N/F
// diagnostics and their historical tests. The automatic scale does not call it.
bool JPWRaizNReadLive(JPWRaizNLiveProvider &provider,
                      JPWRaizNLiveCache &cache,const string context_key,
                      const int n,const double f,JPWRaizNLiveSample &sample)
  {
   if(n<=0 || !MathIsValidNumber(f) || f<=0.0)
     {
      sample.p0=0.0; sample.atr=0.0; sample.distance=0.0;
      sample.percent=0.0; sample.bar_time=0; sample.current_bar_time=0;
      sample.quote_time_msc=0; sample.current=false;
      sample.reason="Configure N/F";
      return(false);
     }
   if(!JPWRaizNReadLiveBase(provider,cache,context_key,sample)) return(false);
   if(JPWRaizNCalculate(sample.p0,sample.atr,n,f,
                        sample.distance,sample.percent)!=JPW_RAIZN_OK)
     { sample.reason="Calculo Raiz N invalido"; return(false); }
   return(true);
  }

#endif
