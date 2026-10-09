#property copyright "JP Wealth"
#property version "1.60"
#property description "Testes sinteticos do coletor corrente Raiz N, sem dados de conta."

#include <JPWealth/JPW_Alavancagem_RaizN_Live.mqh>

// O provedor abaixo fornece todos os dados. OnStart nao instancia o provedor
// nativo nem le conta, posicao, grafico, cotacao, arquivo ou historico real.
class JPWRaizNLiveFake : public JPWRaizNLiveProvider
  {
public:
   string symbol;
   JPWRaizNLiveSeries before;
   JPWRaizNLiveSeries after;
   double bid;
   double ask;
   double atr;
   long quote_time;
   long now;
   bool connected;
   bool clock_valid;
   bool quote_ok;
   bool series_ok;
   bool atr_ok;
   int series_reads;
   int atr_reads;
   int quote_reads;
   void Reset()
     {
      symbol="SYNTHETIC.EXACT";
      before.current_open=(datetime)172800;
      before.closed_open=(datetime)158400;
      before.bars=100;
      before.calculated=100;
      before.synchronized=true;
      after=before;
      bid=99.0;
      ask=101.0;
      atr=0.4;
      quote_time=172900000;
      now=172901000;
      connected=true;
      clock_valid=true;
      quote_ok=true;
      series_ok=true;
      atr_ok=true;
      series_reads=0;
      atr_reads=0;
      quote_reads=0;
     }
   virtual string ExactSymbol() { return(symbol); }
   virtual bool Connected() { return(connected); }
   virtual bool ClockValid() { return(clock_valid); }
   virtual long NowMilliseconds() { return(now); }
   virtual long MaxQuoteAgeMilliseconds() { return(30000); }
   virtual bool ReadQuote(double &out_bid,double &out_ask,long &out_time)
     {
      quote_reads++;
      out_bid=bid;
      out_ask=ask;
      out_time=quote_time;
      return(quote_ok);
     }
   virtual bool ReadSeries(JPWRaizNLiveSeries &out_series)
     {
      if(series_reads%2==0) out_series=before;
      else out_series=after;
      series_reads++;
      return(series_ok);
     }
   virtual bool ReadClosedATR(double &out_atr)
     { atr_reads++; out_atr=atr; return(atr_ok); }
  };

int g_raiz_live_passes=0;
int g_raiz_live_failures=0;

void JPWRaizLiveAssert(const bool condition,const string label)
  {
   if(condition) g_raiz_live_passes++;
   else { g_raiz_live_failures++; Print("FAIL: ",label); }
  }

bool JPWRaizLiveNear(const double actual,const double expected)
  {
   return(MathIsValidNumber(actual) && MathAbs(actual-expected)<1e-9);
  }

void JPWRaizLiveTestSharedHorizonSample()
  {
   JPWRaizNLiveFake fake;
   fake.Reset();
   JPWRaizNLiveCache cache;
   JPWRaizNLiveResetCache(cache);
   JPWRaizNLiveSample sample;
   double price1=0.0,pct1=0.0,price2=0.0,pct2=0.0;
   JPWRaizLiveAssert(JPWRaizNReadLiveBase(fake,cache,"synthetic-account",sample),
                    "shared current base sample succeeds without N or F");
   JPWRaizLiveAssert(JPWRaizNTimeScale(sample.p0,sample.atr,30,price1,pct1)==JPW_RAIZN_OK &&
                    JPWRaizNTimeScale(sample.p0,sample.atr,60,price2,pct2)==JPW_RAIZN_OK,
                    "both horizons derive from one quote and one ATR sample");
   JPWRaizLiveAssert(fake.quote_reads==1 && fake.atr_reads==1 &&
                    JPWRaizLiveNear(pct2/pct1,MathSqrt(2.0)),
                    "two horizons do not trigger a second quote or ATR read");
  }

void JPWRaizLiveTestCalculationAndCache()
  {
   JPWRaizNLiveFake fake;
   fake.Reset();
   JPWRaizNLiveCache cache;
   JPWRaizNLiveResetCache(cache);
   JPWRaizNLiveSample sample;
   JPWRaizLiveAssert(JPWRaizNReadLive(fake,cache,"synthetic-account-A",30,1.25,sample),
                    "complete quote and closed H4 calculate without positions or Genesis");
   JPWRaizLiveAssert(JPWRaizLiveNear(sample.p0,100.0),"P0 is current midpoint");
   JPWRaizLiveAssert(JPWRaizLiveNear(sample.percent,2.738612787525831),"known percent example");
   JPWRaizLiveAssert(JPWRaizLiveNear(sample.distance,2.738612787525831),"known price-distance example");
   JPWRaizLiveAssert(sample.current && sample.bar_time==158400 &&
                    sample.current_bar_time==172800,"last completed H4 selected");
   JPWRaizLiveAssert(fake.atr_reads==1,"first collection reads ATR");
   fake.bid=199.0;
   fake.ask=201.0;
   JPWRaizLiveAssert(JPWRaizNReadLive(fake,cache,"synthetic-account-A",30,1.25,sample),
                    "new quote recalculates within same H4");
   JPWRaizLiveAssert(JPWRaizLiveNear(sample.percent,1.3693063937629155) &&
                    JPWRaizLiveNear(sample.distance,2.738612787525831),
                    "price changes percentage, not ATR distance");
   JPWRaizLiveAssert(fake.atr_reads==2,"each capture rereads closed ATR, including unchanged H4");
   fake.before.closed_open=fake.before.current_open;
   fake.before.current_open+=14400;
   fake.before.bars++;
   fake.before.calculated++;
   fake.after=fake.before;
   fake.quote_time=(long)fake.before.current_open*1000+1000;
   fake.now=fake.quote_time+1000;
   fake.atr=0.8;
   JPWRaizLiveAssert(JPWRaizNReadLive(fake,cache,"synthetic-account-A",30,1.25,sample) &&
                    sample.current && sample.bar_time==172800 && fake.atr_reads==3,
                    "new H4 refreshes ATR at newly closed bar");
   JPWRaizLiveAssert(JPWRaizLiveNear(sample.percent,2.738612787525831),"new H4 ATR used");

   fake.Reset();
   JPWRaizLiveAssert(JPWRaizNReadLive(fake,cache,"synthetic-USD",30,1.25,sample),"USD context");
   const double usd=sample.percent;
   JPWRaizLiveAssert(JPWRaizNReadLive(fake,cache,"synthetic-USC",30,1.25,sample) &&
                    JPWRaizLiveNear(sample.percent,usd) && fake.atr_reads==2,
                    "USC does not scale prices; context change invalidates cache");
   fake.symbol="SYNTHETIC.OTHER";
   JPWRaizLiveAssert(JPWRaizNReadLive(fake,cache,"synthetic-USC",30,1.25,sample) &&
                    fake.atr_reads==3,"exact symbol change invalidates cache");
  }

void JPWRaizLiveTestQuality()
  {
   JPWRaizNLiveFake fake;
   fake.Reset();
   JPWRaizNLiveCache cache;
   JPWRaizNLiveResetCache(cache);
   JPWRaizNLiveSample sample;
   fake.clock_valid=false;
   JPWRaizLiveAssert(JPWRaizNReadLive(fake,cache,"synthetic",30,1.25,sample) && !sample.current,
                    "initialization without clock anchor is Estimated");
   fake.clock_valid=true;
   fake.connected=false;
   JPWRaizLiveAssert(JPWRaizNReadLive(fake,cache,"synthetic",30,1.25,sample) && !sample.current &&
                    sample.reason=="Sem conexao","disconnected complete data are Estimated");
   fake.connected=true;
   fake.now=fake.quote_time+30001;
   JPWRaizLiveAssert(JPWRaizNReadLive(fake,cache,"synthetic",30,1.25,sample) && !sample.current,
                    "old quote is Estimated, not unavailable");
   fake.now=fake.quote_time+1000;
   JPWRaizLiveAssert(JPWRaizNReadLive(fake,cache,"synthetic",30,1.25,sample) && sample.current,
                    "recent quote after reconnect returns to Current");
   fake.before.synchronized=false;
   fake.after=fake.before;
   JPWRaizLiveAssert(JPWRaizNReadLive(fake,cache,"synthetic",30,1.25,sample) && !sample.current,
                    "complete but unconfirmed history is Estimated");
   fake.before.synchronized=true;
   fake.after=fake.before;
   const int reads=fake.atr_reads;
   JPWRaizLiveAssert(JPWRaizNReadLive(fake,cache,"synthetic",30,1.25,sample) && sample.current &&
                    fake.atr_reads==reads+1,"resynchronization refreshes ATR before Current");
   fake.now=(long)(fake.before.current_open+3*24*60*60)*1000;
   JPWRaizLiveAssert(JPWRaizNReadLive(fake,cache,"synthetic",30,1.25,sample) && !sample.current,
                    "weekend stale feed is Estimated");
   fake.quote_time=fake.now;
   JPWRaizLiveAssert(JPWRaizNReadLive(fake,cache,"synthetic",30,1.25,sample) && !sample.current,
                    "new quote alone cannot certify a stale H4 series");
  }

void JPWRaizLiveTestInvalid()
  {
   JPWRaizNLiveFake fake;
   JPWRaizNLiveCache cache;
   JPWRaizNLiveSample sample;
   JPWRaizNLiveResetCache(cache);
   fake.Reset();
   JPWRaizLiveAssert(!JPWRaizNReadLive(fake,cache,"synthetic",0,1.25,sample),"missing N has no default");
   JPWRaizLiveAssert(!JPWRaizNReadLive(fake,cache,"synthetic",30,0.0,sample),"missing F has no default");
   JPWRaizLiveAssert(!JPWRaizNReadLive(fake,cache,"",30,1.25,sample),"account context missing");
   fake.before.bars=55;
   fake.after=fake.before;
   JPWRaizLiveAssert(!JPWRaizNReadLive(fake,cache,"synthetic",30,1.25,sample),"insufficient true-range history");
   fake.Reset();
   fake.before.calculated=55;
   fake.after=fake.before;
   JPWRaizLiveAssert(!JPWRaizNReadLive(fake,cache,"synthetic",30,1.25,sample),"ATR buffer not ready");
   fake.Reset();
   fake.before.closed_open=fake.before.current_open;
   fake.after=fake.before;
   JPWRaizLiveAssert(!JPWRaizNReadLive(fake,cache,"synthetic",30,1.25,sample),"open candle never used as closed");
   fake.Reset();
   fake.atr=EMPTY_VALUE;
   JPWRaizLiveAssert(!JPWRaizNReadLive(fake,cache,"synthetic",30,1.25,sample),"EMPTY_VALUE not a valid ATR");
   fake.Reset();
   fake.atr=MathSqrt(-1.0);
   JPWRaizLiveAssert(!JPWRaizNReadLive(fake,cache,"synthetic",30,1.25,sample),"non-finite ATR rejected");
   fake.Reset();
   fake.atr_ok=false;
   JPWRaizLiveAssert(!JPWRaizNReadLive(fake,cache,"synthetic",30,1.25,sample),"CopyBuffer failure not hidden");
   fake.Reset();
   fake.bid=0.0;
   JPWRaizLiveAssert(!JPWRaizNReadLive(fake,cache,"synthetic",30,1.25,sample),"missing price not artificial zero");
   fake.Reset();
   fake.ask=fake.bid-0.1;
   JPWRaizLiveAssert(!JPWRaizNReadLive(fake,cache,"synthetic",30,1.25,sample),"inverted spread rejected");
   fake.Reset();
   fake.quote_time=fake.now+2001;
   JPWRaizLiveAssert(!JPWRaizNReadLive(fake,cache,"synthetic",30,1.25,sample),"future tick rejected");
   fake.Reset();
   fake.quote_time=(long)fake.before.current_open*1000-1;
   JPWRaizLiveAssert(!JPWRaizNReadLive(fake,cache,"synthetic",30,1.25,sample),"quote predating bar rejected");
   fake.Reset();
   fake.after.current_open+=14400;
   fake.after.closed_open=fake.before.current_open;
   fake.after.bars++;
   fake.after.calculated++;
   JPWRaizLiveAssert(!JPWRaizNReadLive(fake,cache,"synthetic",30,1.25,sample) && !cache.valid &&
                    sample.percent==0.0,"bar rollover during collection discards result and cache");
   fake.Reset();
   fake.after.synchronized=false;
   JPWRaizLiveAssert(!JPWRaizNReadLive(fake,cache,"synthetic",30,1.25,sample),"series synchronization change rejected");
   fake.Reset();
   fake.series_ok=false;
   JPWRaizLiveAssert(!JPWRaizNReadLive(fake,cache,"synthetic",30,1.25,sample),"history unavailable rejected");
   JPWRaizLiveAssert(sample.p0==0.0 && sample.percent==0.0 && !sample.current,
                    "failed collection carries no prior value as valid");
  }

// Juiz candidato1.21.2: referências independentes previamente congeladas.
// ATR0.4/0.8 * sqrt(30) *1.25, P0=100; mesmo metadata/tick entre capturas.
// O provedor sintético não lê o terminal. Falha deve invalidar resultado/cache.
void JPWRaizLiveTestATRContentCorrection()
  {
   JPWRaizNLiveFake fake;
   fake.Reset();
   JPWRaizNLiveCache cache;
   JPWRaizNLiveResetCache(cache);
   JPWRaizNLiveSample sample;
   const datetime current_open=fake.before.current_open;
   const datetime closed_open=fake.before.closed_open;
   const int bars=fake.before.bars;
   const int calculated=fake.before.calculated;
   const long quote=fake.quote_time,now=fake.now;
   JPWRaizLiveAssert(JPWRaizNReadLive(fake,cache,"synthetic-ATR-content",30,1.25,sample) &&
                    sample.current && fake.atr_reads==1 &&
                    JPWRaizLiveNear(sample.distance,2.738612787525830567284848914004) &&
                    JPWRaizLiveNear(sample.percent,2.738612787525830567284848914004),
                    "independent initial ATR content reference");
   fake.atr=0.8;
   JPWRaizLiveAssert(JPWRaizNReadLive(fake,cache,"synthetic-ATR-content",30,1.25,sample) &&
                    sample.current && fake.atr_reads==2 && JPWRaizLiveNear(sample.atr,0.8) &&
                    JPWRaizLiveNear(sample.distance,5.477225575051661134569697828008) &&
                    JPWRaizLiveNear(sample.percent,5.477225575051661134569697828008),
                    "corrected ATR content with unchanged metadata is used");
   JPWRaizLiveAssert(fake.before.current_open==current_open && fake.before.closed_open==closed_open &&
                    fake.before.bars==bars && fake.before.calculated==calculated &&
                    fake.quote_time==quote && fake.now==now && fake.bid==99.0 && fake.ask==101.0,
                    "ATR correction changes only ATR content");
   fake.atr_ok=false;
   JPWRaizLiveAssert(!JPWRaizNReadLive(fake,cache,"synthetic-ATR-content",30,1.25,sample) &&
                    !cache.valid && !sample.current && fake.atr_reads==3 &&
                    sample.p0==0.0 && sample.atr==0.0 && sample.distance==0.0 && sample.percent==0.0,
                    "unavailable corrected ATR leaves no Current or stale numeric result");
  }

void OnStart()
  {
   JPWRaizLiveTestCalculationAndCache();
   JPWRaizLiveTestSharedHorizonSample();
   JPWRaizLiveTestQuality();
   JPWRaizLiveTestInvalid();
   JPWRaizLiveTestATRContentCorrection();
   if(g_raiz_live_failures==0)
      Print("JPW_Alavancagem_RaizN_Live_Tests PASS: ",g_raiz_live_passes," asserts");
   else Print("JPW_Alavancagem_RaizN_Live_Tests FAIL: ",g_raiz_live_failures,
              " failures / ",g_raiz_live_passes," passes");
  }
