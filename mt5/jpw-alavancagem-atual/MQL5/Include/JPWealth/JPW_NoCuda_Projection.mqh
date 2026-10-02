#ifndef JPW_NOCUDA_PROJECTION_MQH
#define JPW_NOCUDA_PROJECTION_MQH

#include <JPWealth/JPW_NoCuda_Projection_Core.mqh>

// Local, read-only adapter. It never writes studies or any financial store.
// Future calendar vertices are time/ordinal hypotheses, NOT synthetic candles.
struct JPWNoCudaProjectionTimeline
  {
   datetime opens[];
   JPWNoCudaProjectionSession sessions[];
   int observed_count;
   datetime generated;
   bool has_sessions;
   string source;
  };

// Only the current H1/H4 bucket has a short read cache. Calendar-backed values
// stay Estimated. A five-second reuse never claims a fresh full-history scan.
JPWNoCudaProjectionTimeline g_jpw_nocuda_projection_cache;
string g_jpw_nocuda_projection_cache_symbol="";
string g_jpw_nocuda_projection_cache_feed="";
datetime g_jpw_nocuda_projection_cache_anchor=0;
datetime g_jpw_nocuda_projection_cache_created=0;
datetime g_jpw_nocuda_projection_cache_newest=0;
datetime g_jpw_nocuda_projection_cache_session_first=0;
datetime g_jpw_nocuda_projection_cache_session_last=0;
int g_jpw_nocuda_projection_cache_anchor_shift=-1;
int g_jpw_nocuda_projection_cache_bars=0;
ENUM_TIMEFRAMES g_jpw_nocuda_projection_cache_tf=PERIOD_H1;

bool JPWNoCudaProjectionCopyTimeline(const JPWNoCudaProjectionTimeline &source,
                                    JPWNoCudaProjectionTimeline &destination)
  {
   if(ArrayResize(destination.opens,ArraySize(source.opens))!=ArraySize(source.opens))
      return(false);
   for(int i=0;i<ArraySize(source.opens);i++) destination.opens[i]=source.opens[i];
   if(ArrayResize(destination.sessions,ArraySize(source.sessions))!=ArraySize(source.sessions))
      return(false);
   for(int i=0;i<ArraySize(source.sessions);i++) destination.sessions[i]=source.sessions[i];
   destination.observed_count=source.observed_count;
   destination.generated=source.generated;
   destination.has_sessions=source.has_sessions;
   destination.source=source.source;
   return(true);
  }

bool JPWNoCudaProjectionSessions(const string symbol,const datetime first,
                                const datetime last,
                                JPWNoCudaProjectionSession &sessions[],string &reason)
  {
   ArrayResize(sessions,0);
   reason="Grade semanal de cotacao indisponivel";
   if(symbol=="" || first<=0 || last<first) return(false);
   const long first_day=((long)first/86400-1)*86400;
   const long last_day=((long)last/86400)*86400;
   // A history query may span years; cap work explicitly rather than truncate.
   if(last_day-first_day>3660*86400)
     { reason="Intervalo de sessoes excede o orcamento da consulta"; return(false); }
   for(long day=first_day;day<=last_day;day+=86400)
     {
      MqlDateTime civil;
      if(!TimeToStruct((datetime)day,civil)) return(false);
      for(uint index=0;index<32;index++)
        {
         datetime from=0,to=0;
         if(!SymbolInfoSessionQuote(symbol,(ENUM_DAY_OF_WEEK)civil.day_of_week,
                                    index,from,to)) break;
         const long begin=(long)from;
         long finish=(long)to;
         if(begin<0 || begin>=86400 || finish<0 || finish>172800)
           { reason="Horario semanal de cotacao invalido"; return(false); }
         if(finish<=begin) finish+=86400;
         if(finish<=begin || finish>172800)
           { reason="Sessao semanal invalida"; return(false); }
         const int n=ArraySize(sessions);
         if(n>=32768 || ArrayResize(sessions,n+1)!=n+1)
           { reason="Grade de sessoes excede o orcamento"; return(false); }
         sessions[n].from_time=(datetime)(day+begin);
         sessions[n].to_time=(datetime)(day+finish);
         if(index==31)
           { reason="Grade semanal excedeu 32 sessoes por dia"; return(false); }
        }
     }
   if(ArraySize(sessions)<1) return(false);
   reason="";
   return(true);
  }

bool JPWNoCudaProjectionSameSessions(JPWNoCudaProjectionSession &first[],
                                    JPWNoCudaProjectionSession &second[])
  {
   if(ArraySize(first)!=ArraySize(second)) return(false);
   for(int i=0;i<ArraySize(first);i++)
      if(first[i].from_time!=second[i].from_time ||
         first[i].to_time!=second[i].to_time) return(false);
   return(true);
  }

// Transient query provenance, separate from immutable study checksums/schema.
// Generation time is deliberately excluded: a stable source must hash the same.
bool JPWNoCudaProjectionDigest(const string symbol,const ENUM_TIMEFRAMES tf,
                              const datetime anchor_open,const datetime first,
                              const datetime last,
                              const JPWNoCudaProjectionTimeline &timeline,
                              string &signature)
  {
   signature="";
   string canonical="JPW_NOCUDA_QUERY_V1|"+symbol+"|"+IntegerToString((int)tf)+"|"+
      IntegerToString((long)anchor_open)+"|"+IntegerToString((long)first)+"|"+
      IntegerToString((long)last)+"|"+IntegerToString(timeline.observed_count)+"|";
   for(int i=0;i<timeline.observed_count;i++)
      canonical+=IntegerToString((long)timeline.opens[i])+";";
   canonical+="|sessions|";
   for(int i=0;i<ArraySize(timeline.sessions);i++)
      canonical+=IntegerToString((long)timeline.sessions[i].from_time)+","+
                 IntegerToString((long)timeline.sessions[i].to_time)+";";
   uchar bytes[];
   uchar key[];
   uchar digest[];
   const int copied=StringToCharArray(canonical,bytes,0,WHOLE_ARRAY,CP_UTF8);
   if(copied<2 || ArrayResize(bytes,copied-1)!=copied-1 ||
      CryptEncode(CRYPT_HASH_SHA256,bytes,key,digest)!=32) return(false);
   for(int i=0;i<32;i++) signature+=StringFormat("%02x",(int)digest[i]);
   return(true);
  }

bool JPWNoCudaProjectionLoadTimeline(const string symbol,const ENUM_TIMEFRAMES tf,
                                    const datetime anchor_open,
                                    const datetime query_first,
                                    const datetime query_last,
                                    JPWNoCudaProjectionTimeline &out,string &reason)
  {
   ArrayResize(out.opens,0); ArrayResize(out.sessions,0);
   out.observed_count=0; out.generated=0; out.has_sessions=false; out.source="";
   reason="Historico-fonte indisponivel";
   const int seconds=PeriodSeconds(tf);
   const string period_label=(tf==PERIOD_H4 ? "H4" : "H1");
   long synced=0;
   const datetime now=TimeTradeServer();
   if(symbol=="" || anchor_open<=0 || query_first<=0 || query_last<query_first ||
      seconds<=0 || now<=0 ||
      !SeriesInfoInteger(symbol,tf,SERIES_SYNCHRONIZED,synced) || synced==0)
      return(false);
   const datetime newest=iTime(symbol,tf,0);
   const int anchor_shift=iBarShift(symbol,tf,anchor_open,true);
   if(newest<=0 || anchor_shift<1 || iTime(symbol,tf,anchor_shift)!=anchor_open)
     { reason="Ancora A deve identificar barra-fonte encerrada"; return(false); }
   const bool needs_future=(query_last>newest);
   const long today=((long)now/86400)*86400;
   if(needs_future && tf!=PERIOD_H1 && tf!=PERIOD_H4)
     { reason="Projecao futura disponivel somente para fontes H1 e H4"; return(false); }
   if(needs_future && (long)query_last>today+31*86400)
     { reason="Escolha um dia ate 30 dias civis a frente"; return(false); }
   // The lower bracket is searched only for observed historical times. Future
   // time is never passed to iBarShift(false), which could return the last bar.
   int first_shift=anchor_shift;
   if(query_first<=newest)
     {
      const int left=iBarShift(symbol,tf,query_first,false);
      if(left<0 || iTime(symbol,tf,left)>query_first)
        { reason="Historico nao cobre o inicio da consulta"; return(false); }
      first_shift=MathMax(first_shift,left);
     }
   int last_shift=0;
   if(!needs_future)
     {
      const int left=iBarShift(symbol,tf,query_last,false);
      if(left<0)
        { reason="Historico nao cobre o fim da consulta"; return(false); }
      const datetime left_open=iTime(symbol,tf,left);
      if(left_open>query_last)
        { reason="Abertura historica incoerente"; return(false); }
      const int right=(left_open==query_last ? left : left-1);
      if(right<0)
        { reason="Falta abertura seguinte observada"; return(false); }
      last_shift=MathMin(anchor_shift,right);
     }
   const datetime validation_start=(datetime)(today-14*86400);
   if(needs_future)
     {
      const int validation_shift=iBarShift(symbol,tf,validation_start,false);
      // A partial session can start after midnight on the very first covered
      // day. Load the oldest available opening in that case; the exhaustive
      // expected/observed comparison below still rejects every missing bucket.
      const int oldest=(validation_shift>=0 ? validation_shift : Bars(symbol,tf)-1);
      if(oldest<0)
        { reason="Faltam 14 dias civis encerrados de historico "+period_label; return(false); }
      first_shift=MathMax(first_shift,oldest);
     }
   const int count=first_shift-last_shift+1;
   if(count<1 || count>200000 || CopyTime(symbol,tf,last_shift,count,out.opens)!=count)
     { reason="Sequencia historica incompleta ou excede o orcamento"; return(false); }
   out.observed_count=count;
   if(!JPWNoCudaProjectionValidateOpens(out.opens,count,reason)) return(false);
   if(out.opens[0]!=iTime(symbol,tf,first_shift) ||
      out.opens[count-1]!=iTime(symbol,tf,last_shift))
     { reason="Faixa historica mudou durante a leitura"; return(false); }
   const datetime session_first=validation_start;
   const datetime projected_end=(datetime)((long)query_last+7*86400);
   const datetime session_last=(needs_future ? projected_end : query_last);
   if(needs_future)
     {
      if(!JPWNoCudaProjectionSessions(symbol,session_first,session_last,
                                      out.sessions,reason)) return(false);
      out.has_sessions=true;
      // Only the last 14 CLOSED civil days validate the recurring projection
      // grade. Older holidays remain actual source ordinals, not calendar vetoes.
      // The source timeframe supplies BOTH the observed sequence and the
      // calendar bucket width; H4 is never synthesized from an H1 count.
      if(((long)newest%seconds)!=0 ||
         !JPWNoCudaProjectionExpectedBucket(out.sessions,newest,seconds))
        { reason="Abertura "+period_label+" corrente diverge da grade do servidor"; return(false); }
      if(!JPWNoCudaProjectionCorroborateBuckets(out.opens,validation_start,
                                          (datetime)today,out.sessions,seconds,reason) ||
         (newest>(datetime)today &&
          !JPWNoCudaProjectionCorroborateBuckets(out.opens,(datetime)today,
                                           newest,out.sessions,seconds,reason)))
        {
         if(reason=="") reason="Faltam 14 dias civis encerrados de historico "+period_label;
         return(false);
        }
      for(long slot=(long)newest+seconds;slot<=(long)now;slot+=seconds)
         if(JPWNoCudaProjectionExpectedBucketBy(out.sessions,(datetime)slot,now,seconds))
           {
            reason="Falta barra "+period_label+" ja esperada no dia corrente; atualize o historico";
            return(false);
           }
      int projected=0;
      for(long slot=(long)newest+seconds;slot<=(long)projected_end;slot+=seconds)
        {
         if(!JPWNoCudaProjectionExpectedBucket(out.sessions,(datetime)slot,seconds)) continue;
         const int n=ArraySize(out.opens);
         if(++projected>900 || ArrayResize(out.opens,n+1)!=n+1)
           { reason="Projecao excede o orcamento de aberturas"; return(false); }
         out.opens[n]=(datetime)slot;
         if(slot>(long)query_last) break;
        }
      if(out.opens[ArraySize(out.opens)-1]<query_last)
        { reason="Falta abertura projetada em ate 7 dias para interpolar"; return(false); }
      out.source=period_label+": aberturas observadas + SymbolInfoSessionQuote; grade semanal Estimated";
      JPWNoCudaProjectionSession check_sessions[];
      if(!JPWNoCudaProjectionSessions(symbol,session_first,session_last,check_sessions,reason) ||
         !JPWNoCudaProjectionSameSessions(out.sessions,check_sessions))
        { reason="Grade de sessoes mudou durante a leitura"; return(false); }
     }
   else
     {
      // Preserve the actual observed sequence, including H1 and other periods,
      // across holidays/weekends. There is no fabricated historical calendar
      // and no conversion from elapsed hours to candle counts.
      // Synchronization, exact endpoints, count and full reread below are the
      // evidence for this local sequence; they do not certify a universal feed.
      out.source="Aberturas observadas do periodo-fonte; lacunas reais; sem projecao futura";
     }
   datetime reread[];
   if(CopyTime(symbol,tf,last_shift,count,reread)!=count ||
      iTime(symbol,tf,0)!=newest || iBarShift(symbol,tf,anchor_open,true)!=anchor_shift ||
      !SeriesInfoInteger(symbol,tf,SERIES_SYNCHRONIZED,synced) || synced==0)
     { reason="Historico mudou durante a consulta; tente novamente"; return(false); }
   for(int i=0;i<count;i++)
      if(reread[i]!=out.opens[i])
        { reason="Sequencia historica mudou durante a consulta"; return(false); }
   out.generated=now;
   reason="";
   return(true);
  }

bool JPWNoCudaPriceAtTime(const string symbol,const ENUM_TIMEFRAMES tf,
                         const datetime anchor_open,const JPWNoCudaGeometry &g,
                         const double level,const datetime at,
                         JPWNoCudaTimePoint &out,string &reason)
  {
   JPWNoCudaTimePointClear(out);
   JPWNoCudaProjectionTimeline timeline;
   const datetime now=TimeTradeServer();
   const datetime newest=iTime(symbol,tf,0);
   const int seconds=PeriodSeconds(tf);
   const string feed=AccountInfoString(ACCOUNT_SERVER);
   const bool current_bucket=((tf==PERIOD_H1 || tf==PERIOD_H4) && at>newest &&
                              at<(datetime)((long)newest+seconds));
   bool reused=false;
   long sync=0;
   if(current_bucket && now>=g_jpw_nocuda_projection_cache_created &&
      now-g_jpw_nocuda_projection_cache_created<=5 &&
      symbol==g_jpw_nocuda_projection_cache_symbol &&
      feed==g_jpw_nocuda_projection_cache_feed &&
      tf==g_jpw_nocuda_projection_cache_tf &&
      anchor_open==g_jpw_nocuda_projection_cache_anchor &&
      newest==g_jpw_nocuda_projection_cache_newest &&
      Bars(symbol,tf)==g_jpw_nocuda_projection_cache_bars &&
      iBarShift(symbol,tf,anchor_open,true)==g_jpw_nocuda_projection_cache_anchor_shift &&
      SeriesInfoInteger(symbol,tf,SERIES_SYNCHRONIZED,sync) && sync!=0)
     {
      JPWNoCudaProjectionSession check[];
      if(JPWNoCudaProjectionSessions(symbol,g_jpw_nocuda_projection_cache_session_first,
          g_jpw_nocuda_projection_cache_session_last,check,reason) &&
         JPWNoCudaProjectionSameSessions(g_jpw_nocuda_projection_cache.sessions,check))
        {
         bool elapsed_missing=false;
         for(long slot=(long)newest+seconds;slot<=(long)now;slot+=seconds)
            if(JPWNoCudaProjectionExpectedBucketBy(check,(datetime)slot,now,seconds))
               elapsed_missing=true;
         if(!elapsed_missing)
            reused=JPWNoCudaProjectionCopyTimeline(g_jpw_nocuda_projection_cache,timeline);
        }
     }
   if(!reused)
     {
      if(!JPWNoCudaProjectionLoadTimeline(symbol,tf,anchor_open,at,at,timeline,reason))
         return(false);
      if(current_bucket)
        {
         if(!JPWNoCudaProjectionCopyTimeline(timeline,g_jpw_nocuda_projection_cache))
            g_jpw_nocuda_projection_cache_created=0;
         else
           {
         g_jpw_nocuda_projection_cache_symbol=symbol;
         g_jpw_nocuda_projection_cache_feed=feed;
         g_jpw_nocuda_projection_cache_tf=tf;
         g_jpw_nocuda_projection_cache_anchor=anchor_open;
         g_jpw_nocuda_projection_cache_created=now;
         g_jpw_nocuda_projection_cache_newest=newest;
         g_jpw_nocuda_projection_cache_anchor_shift=iBarShift(symbol,tf,anchor_open,true);
         g_jpw_nocuda_projection_cache_bars=Bars(symbol,tf);
         const datetime validation_start=(datetime)(((long)now/86400-14)*86400);
         g_jpw_nocuda_projection_cache_session_first=validation_start;
         g_jpw_nocuda_projection_cache_session_last=(datetime)((long)at+7*86400);
           }
        }
     }
   return(JPWNoCudaProjectionResolve(timeline.opens,timeline.observed_count,
      anchor_open,g,level,at,PeriodSeconds(tf),timeline.sessions,
      timeline.has_sessions,out,reason));
  }

bool JPWNoCudaProjectDay(const string symbol,const ENUM_TIMEFRAMES tf,
                        const datetime anchor_open,const JPWNoCudaGeometry &g,
                        const double level,const datetime day,
                        JPWNoCudaDailyResult &out)
  {
   JPWNoCudaDailyClear(out);
   if(day<=0)
     { out.reason="Data do servidor invalida"; return(false); }
   const datetime start=(datetime)(((long)day/86400)*86400);
   const datetime middle=(datetime)((long)start+43200);
   const datetime end=(datetime)((long)start+86400);
   out.day=start;
   JPWNoCudaProjectionTimeline timeline;
   string reason="";
   if(!JPWNoCudaProjectionLoadTimeline(symbol,tf,anchor_open,start,end,timeline,reason))
     { out.reason=reason; return(false); }
   string source_signature="";
   if(!JPWNoCudaProjectionDigest(symbol,tf,anchor_open,start,end,timeline,source_signature))
     { out.reason="Assinatura transiente da consulta indisponivel"; return(false); }
   bool no_session=false;
   if(timeline.has_sessions)
      no_session=!JPWNoCudaProjectionSessionOverlaps(timeline.sessions,start,end);
   else if(PeriodSeconds(tf)<86400)
     {
      bool observed=false;
      for(int i=0;i<timeline.observed_count;i++)
         if(timeline.opens[i]>=start && timeline.opens[i]<end) observed=true;
      no_session=!observed;
     }
   if(no_session)
     {
      out.no_session=true; out.generated=timeline.generated; out.source=timeline.source;
      out.source_signature=source_signature;
      out.estimated=end>timeline.opens[timeline.observed_count-1];
      out.reason=(out.estimated ? "Estimated: sem sessao nesse dia; nenhuma faixa exibida" :
                                 "Sem barra-fonte observada nesse dia; nenhuma faixa exibida");
      return(false);
     }
   JPWNoCudaTimePoint a,b,c;
   if(!JPWNoCudaProjectionResolve(timeline.opens,timeline.observed_count,anchor_open,
       g,level,start,PeriodSeconds(tf),timeline.sessions,timeline.has_sessions,a,reason) ||
      !JPWNoCudaProjectionResolve(timeline.opens,timeline.observed_count,anchor_open,
       g,level,middle,PeriodSeconds(tf),timeline.sessions,timeline.has_sessions,b,reason) ||
      !JPWNoCudaProjectionResolve(timeline.opens,timeline.observed_count,anchor_open,
       g,level,end,PeriodSeconds(tf),timeline.sessions,timeline.has_sessions,c,reason))
     { out.reason=reason; return(false); }
   const bool accepted=JPWNoCudaDailyFromPoints(start,timeline.generated,a,b,c,false,
                                               timeline.source,out);
   if(accepted)
     {
      out.source_signature=source_signature;
      if(!timeline.has_sessions && PeriodSeconds(tf)>=86400)
         out.reason+="; sessao diaria nao inferida de aberturas de periodo amplo";
     }
   return(accepted);
  }

#endif
