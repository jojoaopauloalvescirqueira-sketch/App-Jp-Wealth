#ifndef JPW_NOCUDA_PROJECTION_CORE_MQH
#define JPW_NOCUDA_PROJECTION_CORE_MQH

#include <JPWealth/JPW_NoCuda_Core.mqh>

// A consulta e uma observacao geometrica, nao uma revisao nem previsao de mercado.
struct JPWNoCudaTimePoint
  {
   bool valid;
   bool estimated;
   bool outside_session;
   datetime time;
   double ordinal;
   double price;
  };

struct JPWNoCudaDailyResult
  {
   bool valid;
   bool estimated;
   bool no_session;
   datetime day;
   datetime generated;
   double start_price;
   double mid_price;
   double end_price;
   double mean_price;
   double min_price;
   double max_price;
   bool start_outside;
   bool mid_outside;
   bool end_outside;
   string source;
   string source_signature;
   string reason;
  };

struct JPWNoCudaProjectionSession
  {
   datetime from_time;
   datetime to_time;
  };

void JPWNoCudaTimePointClear(JPWNoCudaTimePoint &out)
  {
   out.valid=false; out.estimated=false; out.outside_session=false;
   out.time=0; out.ordinal=0.0; out.price=0.0;
  }

void JPWNoCudaDailyClear(JPWNoCudaDailyResult &out)
  {
   out.valid=false; out.estimated=false; out.no_session=false;
   out.day=0; out.generated=0;
   out.start_price=0.0; out.mid_price=0.0; out.end_price=0.0;
   out.mean_price=0.0; out.min_price=0.0; out.max_price=0.0;
   out.start_outside=false; out.mid_outside=false; out.end_outside=false;
   out.source=""; out.source_signature=""; out.reason="Consulta indisponivel";
  }

bool JPWNoCudaProjectionSessionContains(JPWNoCudaProjectionSession &sessions[],
                                       const datetime at)
  {
   for(int i=0;i<ArraySize(sessions);i++)
      if(sessions[i].from_time<=at && sessions[i].to_time>at) return(true);
   return(false);
  }

bool JPWNoCudaProjectionSessionOverlaps(JPWNoCudaProjectionSession &sessions[],
                                       const datetime start,const datetime end)
  {
   if(start<=0 || end<=start) return(false);
   for(int i=0;i<ArraySize(sessions);i++)
      if(sessions[i].from_time<end && sessions[i].to_time>start) return(true);
   return(false);
  }

// Engineering convention for future NoCuda coordinates, not for Raiz N:
// H1 uses 00/01/.../23 and H4 uses 00/04/08/12/16/20 server-civil bins.
// A partial overlapping session contributes one bin, never H1-count / 4.
// Other periods remain available for observed-history interpolation only.
bool JPWNoCudaProjectionBucketSupported(const int source_seconds)
  {
   return(source_seconds==3600 || source_seconds==14400);
  }

bool JPWNoCudaProjectionExpectedBucket(JPWNoCudaProjectionSession &sessions[],
                                      const datetime opened,const int source_seconds)
  {
   if(!JPWNoCudaProjectionBucketSupported(source_seconds) || opened<=0 ||
      ((long)opened%source_seconds)!=0) return(false);
   return(JPWNoCudaProjectionSessionOverlaps(sessions,opened,
                                     (datetime)((long)opened+source_seconds)));
  }

// A partial session does not imply that its bucket already exists before
// the session's first possible quote. This prevents projecting missing elapsed
// data, while permitting a not-yet-open partial session to remain future.
bool JPWNoCudaProjectionExpectedBucketBy(JPWNoCudaProjectionSession &sessions[],
                                        const datetime opened,const datetime known_at,
                                        const int source_seconds)
  {
   if(!JPWNoCudaProjectionBucketSupported(source_seconds) || opened<=0 ||
      known_at<opened || ((long)opened%source_seconds)!=0) return(false);
   const datetime end=(datetime)((long)opened+source_seconds);
   for(int i=0;i<ArraySize(sessions);i++)
     {
      const datetime first=MathMax(opened,sessions[i].from_time);
      if(first<end && first<sessions[i].to_time &&
         sessions[i].to_time>opened && first<=known_at) return(true);
     }
   return(false);
  }

// Preserve the legacy H1 API while exposing H4 explicitly to callers/tests.
bool JPWNoCudaProjectionExpectedH1(JPWNoCudaProjectionSession &sessions[],
                                 const datetime opened)
  { return(JPWNoCudaProjectionExpectedBucket(sessions,opened,3600)); }

bool JPWNoCudaProjectionExpectedH4(JPWNoCudaProjectionSession &sessions[],
                                 const datetime opened)
  { return(JPWNoCudaProjectionExpectedBucket(sessions,opened,14400)); }

bool JPWNoCudaProjectionExpectedH1By(JPWNoCudaProjectionSession &sessions[],
                                    const datetime opened,const datetime known_at)
  { return(JPWNoCudaProjectionExpectedBucketBy(sessions,opened,known_at,3600)); }

bool JPWNoCudaProjectionExpectedH4By(JPWNoCudaProjectionSession &sessions[],
                                    const datetime opened,const datetime known_at)
  { return(JPWNoCudaProjectionExpectedBucketBy(sessions,opened,known_at,14400)); }

bool JPWNoCudaProjectionValidateOpens(const datetime &opens[],
                                     const int observed_count,string &reason)
  {
   reason="Sequencia de barras indisponivel";
   const int count=ArraySize(opens);
   if(count<1 || observed_count<1 || observed_count>count) return(false);
   for(int i=0;i<count;i++)
      if(opens[i]<=0 || (i>0 && opens[i]<=opens[i-1]))
        { reason="Sequencia de barras incoerente"; return(false); }
   reason="";
   return(true);
  }

// Common exact-opening mapping for observed render vertices and time queries.
// Negative evaluation ordinals are allowed before A; the origin remains the
// immutable ordinal accepted when the geometry was built.
bool JPWNoCudaSourceOpeningOrdinal(const long origin_ordinal,
                                   const int anchor_shift,const int vertex_shift,
                                   double &ordinal)
  {
   ordinal=0.0;
   if(origin_ordinal<0 || origin_ordinal>9007199254740991 ||
      anchor_shift<0 || vertex_shift<0) return(false);
   const double computed=(double)origin_ordinal+(double)anchor_shift-(double)vertex_shift;
   if(!MathIsValidNumber(computed) || MathAbs(computed)>9007199254740991.0)
      return(false);
   ordinal=computed;
   return(true);
  }

// Compare every opening in the closed window, not a count that can hide a
// missing bar plus an extra one. H4 is corroborated against actual H4 opens.
bool JPWNoCudaProjectionCorroborateBuckets(const datetime &opens[],
                                          const datetime start,const datetime end,
                                          JPWNoCudaProjectionSession &sessions[],
                                          const int source_seconds,string &reason)
  {
   reason=(source_seconds==14400 ? "Historico H4 diverge da grade de sessoes" :
                                  "Historico H1 diverge da grade de sessoes");
   if(!JPWNoCudaProjectionBucketSupported(source_seconds) || start<=0 || end<=start ||
      ((long)start%source_seconds)!=0 || ((long)end%source_seconds)!=0 ||
      ArraySize(sessions)<1) return(false);
   int index=0;
   while(index<ArraySize(opens) && opens[index]<start) index++;
   for(long slot=(long)start;slot<(long)end;slot+=source_seconds)
     {
      const bool expected=JPWNoCudaProjectionExpectedBucket(sessions,(datetime)slot,source_seconds);
      const bool observed=index<ArraySize(opens) && opens[index]==(datetime)slot;
      if(expected!=observed) return(false);
      if(observed) index++;
      if(index<ArraySize(opens) && opens[index]<(datetime)(slot+source_seconds)) return(false);
     }
   if(index<ArraySize(opens) && opens[index]<end) return(false);
   reason="";
   return(true);
  }

bool JPWNoCudaProjectionCorroborateH1(const datetime &opens[],
                                     const datetime start,const datetime end,
                                     JPWNoCudaProjectionSession &sessions[],string &reason)
  { return(JPWNoCudaProjectionCorroborateBuckets(opens,start,end,sessions,3600,reason)); }

bool JPWNoCudaProjectionCorroborateH4(const datetime &opens[],
                                     const datetime start,const datetime end,
                                     JPWNoCudaProjectionSession &sessions[],string &reason)
  { return(JPWNoCudaProjectionCorroborateBuckets(opens,start,end,sessions,14400,reason)); }

int JPWNoCudaProjectionFloorOpening(const datetime &opens[],const datetime at)
  {
   int low=0,high=ArraySize(opens)-1,result=-1;
   while(low<=high)
     {
      const int middle=low+(high-low)/2;
      if(opens[middle]<=at) { result=middle; low=middle+1; }
      else high=middle-1;
     }
   return(result);
  }

// Fast evaluator for a sequence already validated by the terminal boundary.
// Binary lookup avoids rescanning a long history for every canvas vertex.
bool JPWNoCudaProjectionResolveValidated(const datetime &opens[],const int observed_count,
                                const datetime anchor_open,
                                const JPWNoCudaGeometry &geometry,const double level,
                                const datetime at,const int source_seconds,
                                JPWNoCudaProjectionSession &sessions[],
                                const bool has_sessions,JPWNoCudaTimePoint &out,
                                string &reason)
  {
   JPWNoCudaTimePointClear(out);
   if(ArraySize(opens)<1 || observed_count<1 || observed_count>ArraySize(opens))
     { reason="Sequencia validada indisponivel"; return(false); }
   if(at<=0 || source_seconds<=0 || !MathIsValidNumber(level))
     { reason="Tempo, periodo ou nivel invalido"; return(false); }
   const int anchor=JPWNoCudaProjectionFloorOpening(opens,anchor_open);
   const int left=JPWNoCudaProjectionFloorOpening(opens,at);
   if(anchor<0 || anchor>=observed_count || opens[anchor]!=anchor_open)
     { reason="Ancora A nao consta na sequencia observada"; return(false); }
   if(left<0)
     { reason="Falta abertura anterior ao instante consultado"; return(false); }
   double ordinal=0.0;
   if(!JPWNoCudaSourceOpeningOrdinal(geometry.origin_ordinal,
       ArraySize(opens)-1-anchor,ArraySize(opens)-1-left,ordinal))
     { reason="Ordinal da fonte invalido"; return(false); }
   bool estimated=(left>=observed_count);
   if(opens[left]!=at)
     {
      if(left+1>=ArraySize(opens))
        { reason="Falta abertura seguinte para interpolar"; return(false); }
      const double fraction=((double)at-(double)opens[left])/
                            ((double)opens[left+1]-(double)opens[left]);
      if(!MathIsValidNumber(fraction) || fraction<0.0 || fraction>=1.0)
        { reason="Intervalo de interpolacao invalido"; return(false); }
      ordinal+=fraction;
      estimated=estimated || left+1>=observed_count;
     }
   double price=0.0;
   if(!JPWNoCudaPriceAt(geometry,level,ordinal,price))
     { reason="Preco geometrico invalido"; return(false); }
   out.valid=true; out.estimated=estimated; out.time=at;
   out.ordinal=ordinal; out.price=price;
   // Outside the nominal source bucket is a known gap. A session template,
   // when available, also identifies partial-hour and overnight boundaries.
   out.outside_session=(has_sessions ?
      !JPWNoCudaProjectionSessionContains(sessions,at) :
      at>=(datetime)((long)opens[left]+source_seconds));
   reason="";
   return(true);
  }

// Public pure boundary validates ordering before the shared fast evaluator.
// No uncovered time is clamped to the last ordinal.
bool JPWNoCudaProjectionResolve(const datetime &opens[],const int observed_count,
                                const datetime anchor_open,
                                const JPWNoCudaGeometry &geometry,const double level,
                                const datetime at,const int source_seconds,
                                JPWNoCudaProjectionSession &sessions[],
                                const bool has_sessions,JPWNoCudaTimePoint &out,
                                string &reason)
  {
   JPWNoCudaTimePointClear(out);
   if(!JPWNoCudaProjectionValidateOpens(opens,observed_count,reason)) return(false);
   return(JPWNoCudaProjectionResolveValidated(opens,observed_count,anchor_open,
      geometry,level,at,source_seconds,sessions,has_sessions,out,reason));
  }

bool JPWNoCudaDailyFromPoints(const datetime day,const datetime generated,
                              const JPWNoCudaTimePoint &start,
                              const JPWNoCudaTimePoint &middle,
                              const JPWNoCudaTimePoint &end,
                              const bool no_session,const string source,
                              JPWNoCudaDailyResult &out)
  {
   JPWNoCudaDailyClear(out);
   out.day=day; out.generated=generated; out.source=source;
   out.no_session=no_session;
   out.estimated=start.estimated || middle.estimated || end.estimated;
   if(no_session)
     { out.reason=(out.estimated ? "Estimated: sem sessao nesse dia; nenhuma faixa exibida" :
                                 "Sem sessao nesse dia; nenhuma faixa exibida");
       return(false); }
   if(day<=0 || ((long)day%86400)!=0 || generated<=0 ||
      !start.valid || !middle.valid || !end.valid ||
      start.time!=day || middle.time!=(datetime)((long)day+43200) ||
      end.time!=(datetime)((long)day+86400) ||
      !MathIsValidNumber(start.price) || !MathIsValidNumber(middle.price) ||
      !MathIsValidNumber(end.price))
     { out.reason="00h, 12h ou 24h indisponivel"; return(false); }
   // Half each operand prevents overflow of a finite same-sign sum.
   const double mean=start.price/2.0+end.price/2.0;
   if(!MathIsValidNumber(mean))
     { out.reason="Media dos extremos invalida"; return(false); }
   out.valid=true;
   out.estimated=start.estimated || middle.estimated || end.estimated;
   out.start_price=start.price; out.mid_price=middle.price; out.end_price=end.price;
   out.mean_price=mean;
   out.min_price=MathMin(start.price,end.price);
   out.max_price=MathMax(start.price,end.price);
   out.start_outside=start.outside_session;
   out.mid_outside=middle.outside_session;
   out.end_outside=end.outside_session;
   out.reason=(out.estimated ?
      "Estimated: grade semanal; feriados e excecoes futuros nao confirmados" :
      "Geometria sobre aberturas observadas do periodo-fonte");
   return(true);
  }

#endif
