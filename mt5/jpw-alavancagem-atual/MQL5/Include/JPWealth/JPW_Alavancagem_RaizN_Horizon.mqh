#ifndef JPW_ALAVANCAGEM_RAIZN_HORIZON_MQH
#define JPW_ALAVANCAGEM_RAIZN_HORIZON_MQH

// 1W/2W are rolling server-civil 7/14-day diagnostic horizons. N counts
// expected H4 bar closes for the exact symbol, not 30/60 or 42/84 by fiat.
// A weekly session template is only an estimate: it cannot certify holidays,
// future broker session changes or daylight-saving exceptions.
enum JPW_HORIZON_STATUS
  {
   JPW_HORIZON_UNAVAILABLE=0,
   JPW_HORIZON_ESTIMATED=1,
   JPW_HORIZON_EXACT=2
  };

struct JPWHorizonResult
  {
   datetime reference_time;
   datetime end_1w;
   datetime end_2w;
   int n_1w;
   int n_2w;
   JPW_HORIZON_STATUS status_1w;
   JPW_HORIZON_STATUS status_2w;
   string reason_1w;
   string reason_2w;
   string source;
   string source_sha256;
  };

struct JPWHorizonSession
  {
   datetime from_time;
   datetime to_time;
  };

// SymbolInfoSessionQuote may encode a session ending on the next server day
// as an offset above 86400. Some terminals instead return a wrapped clock
// time. Preserve either representation without counting a second day twice.
bool JPWHorizonNormalizeSessionOffsets(const long from_offset,const long to_offset,
                                       long &normalized_to)
  {
   normalized_to=0;
   if(from_offset<0 || from_offset>=86400 || to_offset<0 || to_offset>2*86400)
      return(false);
   normalized_to=to_offset;
   if(normalized_to<=from_offset) normalized_to+=86400;
   return(normalized_to>from_offset && normalized_to<=2*86400);
  }

void JPWHorizonClear(JPWHorizonResult &out)
  {
   out.reference_time=0; out.end_1w=0; out.end_2w=0;
   out.n_1w=0; out.n_2w=0;
   out.status_1w=JPW_HORIZON_UNAVAILABLE;
   out.status_2w=JPW_HORIZON_UNAVAILABLE;
   out.reason_1w="Horizonte indisponivel";
   out.reason_2w="Horizonte indisponivel";
   out.source=""; out.source_sha256="";
  }

bool JPWHorizonEnds(const datetime reference,datetime &one,datetime &two)
  {
   one=0; two=0;
   if(reference<=0) return(false);
   // MQL datetime uses the server's civil representation here. A later
   // calendar approval is required to make future DST/holiday dates exact.
   one=(datetime)((long)reference+7*86400);
   two=(datetime)((long)reference+14*86400);
   return(one>reference && two>one);
  }

int JPWHorizonCountSessions(const datetime reference,const datetime end_time,
                           JPWHorizonSession &sessions[])
  {
   if(reference<=0 || end_time<=reference) return(0);
   int count=0;
   const long step=4*60*60;
   const long first=((long)reference/step+1)*step;
   for(long close_time=first;close_time<=(long)end_time;close_time+=step)
     {
      const long open_time=close_time-step;
      for(int i=0;i<ArraySize(sessions);i++)
        {
         if((long)sessions[i].from_time<close_time &&
            (long)sessions[i].to_time>open_time)
           { count++; break; }
        }
     }
   return(count);
  }

// Pure cross-check used by the terminal adapter and synthetic fixtures. A
// shifted session or a missing observed bar invalidates the weekly projection;
// it must not silently become an exact calendar.
bool JPWHorizonBarsMatchSessions(const datetime reference,
                                 const datetime &bar_opens[],
                                 JPWHorizonSession &sessions[],string &reason)
  {
   reason="Barras H4 observadas divergem da grade semanal";
   if(reference<=7*86400 || ArraySize(bar_opens)<2 || ArraySize(sessions)<1)
      return(false);
   int actual=0;
   datetime previous=0;
   for(int i=0;i<ArraySize(bar_opens);i++)
     {
      const datetime open_time=bar_opens[i];
      if(open_time<=previous || ((long)open_time%(4*3600))!=0)
         return(false);
      previous=open_time;
      const datetime close_time=(datetime)((long)open_time+4*3600);
      if(close_time<=reference && close_time>reference-7*86400)
        {
         bool covered=false;
         for(int j=0;j<ArraySize(sessions);j++)
            if(sessions[j].from_time<close_time && sessions[j].to_time>open_time)
              { covered=true; break; }
         if(!covered) return(false);
         actual++;
        }
     }
   const int projected=JPWHorizonCountSessions((datetime)((long)reference-7*86400),
                                               reference,sessions);
   if(actual<1 || actual!=projected) return(false);
   reason="";
   return(true);
  }

bool JPWHorizonParseDate(const string value,datetime &result)
  {
   result=0;
   if(StringLen(value)!=19) return(false);
   result=StringToTime(value);
   return(result>0 && TimeToString(result,TIME_DATE|TIME_SECONDS)==value);
  }

// A dated calendar's text is data, not proof of approval. The caller must
// independently verify its raw SHA-256 against an authority-provisioned hash
// BEFORE invoking this parser. This release ships no approved-hash allowlist.
bool JPWHorizonParseApprovedCalendar(const string text,const string symbol,
                                     const datetime reference,
                                     const string verified_sha256,
                                     JPWHorizonResult &out,string &reason)
  {
   JPWHorizonClear(out);
   reason="Calendario datado invalido";
   if(symbol=="" || verified_sha256=="" || StringLen(verified_sha256)!=64 || reference<=0)
     { reason="Hash aprovado ausente ou contexto invalido"; return(false); }
   datetime end1=0,end2=0;
   if(!JPWHorizonEnds(reference,end1,end2)) return(false);
   string lines[];
   const int line_count=StringSplit(text,'\n',lines);
   if(line_count<7) return(false);
   string header=lines[0];
   if(StringLen(header)>0 && StringGetCharacter(header,StringLen(header)-1)==13)
      header=StringSubstr(header,0,StringLen(header)-1);
   if(header!="JPW_H4_CALENDAR_V1") return(false);
   string file_symbol="",version="",authority="",approval_ref="";
   datetime coverage_start=0,coverage_end=0,previous=0,first_close=0;
   int count1=0,count2=0,closures=0;
   for(int i=1;i<line_count;i++)
     {
      string row=lines[i];
      if(StringLen(row)>0 && StringGetCharacter(row,StringLen(row)-1)==13)
         row=StringSubstr(row,0,StringLen(row)-1);
      if(row=="") continue;
      if(StringFind(row,"symbol=")==0)
        { if(file_symbol!="") return(false); file_symbol=StringSubstr(row,7); }
      else if(StringFind(row,"version=")==0)
        { if(version!="") return(false); version=StringSubstr(row,8); }
      else if(StringFind(row,"authority=")==0)
        { if(authority!="") return(false); authority=StringSubstr(row,10); }
      else if(StringFind(row,"approval_ref=")==0)
        { if(approval_ref!="") return(false); approval_ref=StringSubstr(row,13); }
      else if(StringFind(row,"coverage_start=")==0)
        { if(coverage_start!=0 || !JPWHorizonParseDate(StringSubstr(row,15),coverage_start)) return(false); }
      else if(StringFind(row,"coverage_end=")==0)
        { if(coverage_end!=0 || !JPWHorizonParseDate(StringSubstr(row,13),coverage_end)) return(false); }
      else if(StringFind(row,"close=")==0)
        {
         datetime close_time=0;
         if(!JPWHorizonParseDate(StringSubstr(row,6),close_time) ||
            ((long)close_time%(4*60*60))!=0 ||
            (previous!=0 && close_time<=previous)) return(false);
         if(first_close==0) first_close=close_time;
         previous=close_time; closures++;
         if(close_time>reference && close_time<=end1) count1++;
         if(close_time>reference && close_time<=end2) count2++;
        }
      else return(false);
     }
   if(file_symbol!=symbol || version=="" || authority=="" || approval_ref=="" ||
      coverage_start>reference || coverage_end<end2 ||
      coverage_start<=0 || coverage_end<=coverage_start ||
      closures<1 || count1<1 || count2<count1 ||
      first_close<coverage_start || previous>coverage_end)
     { reason="Cobertura, simbolo ou contagens nao comprovados"; return(false); }
   out.reference_time=reference; out.end_1w=end1; out.end_2w=end2;
   out.n_1w=count1; out.n_2w=count2;
   out.status_1w=JPW_HORIZON_EXACT; out.status_2w=JPW_HORIZON_EXACT;
   out.reason_1w="Calendario datado coberto e hash aprovado conferido";
   out.reason_2w=out.reason_1w;
   out.source="Calendario H4 datado "+version+"; "+authority+"; "+approval_ref;
   out.source_sha256=verified_sha256;
   reason="";
   return(true);
  }

#ifndef JPW_RAIZN_HORIZON_SYNTHETIC_ONLY
// The approved digest is supplied by a separate governance authority. A
// self-declared flag or hash INSIDE the calendar file is never accepted.
bool JPWHorizonLoadApprovedCalendar(const string file_name,
                                    const string authority_sha256,
                                    const string symbol,const datetime reference,
                                    JPWHorizonResult &out,string &reason)
  {
   reason="Hash aprovado nao provisionado";
   if(authority_sha256=="" || StringLen(authority_sha256)!=64) return(false);
   uchar bytes[];
   const long size=FileLoad(file_name,bytes);
   if(size<1 || size>262144) { reason="Calendario ausente ou grande demais"; return(false); }
   for(int i=0;i<(int)size;i++)
      if(bytes[i]==0 || bytes[i]>127)
        { reason="Calendario deve ser texto ASCII sem NUL"; return(false); }
   uchar key[],digest[];
   if(CryptEncode(CRYPT_HASH_SHA256,bytes,key,digest)!=32)
     { reason="Hash do calendario indisponivel"; return(false); }
   string actual="";
   for(int i=0;i<32;i++) actual+=StringFormat("%02X",(int)digest[i]);
   string expected=authority_sha256;
   StringToUpper(expected);
   if(actual!=expected) { reason="Hash do calendario nao aprovado"; return(false); }
   return(JPWHorizonParseApprovedCalendar(CharArrayToString(bytes,0,(int)size,CP_UTF8),
                                          symbol,reference,actual,out,reason));
  }

bool JPWHorizonProjectNativeSessions(const string symbol,
                                     const datetime reference,
                                     const datetime end_time,
                                     JPWHorizonSession &sessions[],string &reason)
  {
   ArrayResize(sessions,0);
   reason="Grade semanal de cotacoes indisponivel";
   if(symbol=="" || reference<=0 || end_time<=reference) return(false);
   // Cover the past seven days used for observed-bar consistency as well as
   // the future horizon; one extra day catches overnight quote sessions.
   const long first_day=((long)reference/86400-8)*86400;
   const long last_day=((long)end_time/86400)*86400;
   for(long day=first_day;day<=last_day;day+=86400)
     {
      MqlDateTime civil;
      if(!TimeToStruct((datetime)day,civil)) return(false);
      for(uint index=0;index<32;index++)
        {
         datetime from=0,to=0;
         if(!SymbolInfoSessionQuote(symbol,(ENUM_DAY_OF_WEEK)civil.day_of_week,
                                    index,from,to)) break;
         const long open_offset=(long)from;
         long close_offset=0;
         if(!JPWHorizonNormalizeSessionOffsets(open_offset,(long)to,close_offset))
            { reason="Horario semanal de cotacao invalido"; return(false); }
         const int count=ArraySize(sessions);
         if(ArrayResize(sessions,count+1)!=count+1) return(false);
         sessions[count].from_time=(datetime)(day+open_offset);
         sessions[count].to_time=(datetime)(day+close_offset);
         if(index==31)
           { reason="Grade semanal excedeu o limite de sessoes"; return(false); }
        }
     }
   if(ArraySize(sessions)<1) return(false);
   reason="";
   return(true);
  }

bool JPWHorizonPastBarsConsistent(const string symbol,const datetime reference,
                                  JPWHorizonSession &sessions[],string &reason)
  {
   long sync=0;
   reason="Serie H4 nao sincronizada para conferir a grade semanal";
   if(!SeriesInfoInteger(symbol,PERIOD_H4,SERIES_SYNCHRONIZED,sync) || sync==0)
      return(false);
   datetime opens[];
   const datetime history_start=(datetime)((long)reference-7*86400-4*3600);
   const int bars=CopyTime(symbol,PERIOD_H4,history_start,reference,opens);
   if(bars<2) { reason="Barras H4 observadas insuficientes"; return(false); }
   return(JPWHorizonBarsMatchSessions(reference,opens,sessions,reason));
  }

bool JPWHorizonResolveWithApprovedCalendar(const string symbol,
                                           const datetime reference_server_time,
                                           const string approved_sha256,
                                           const string calendar_file,
                                           JPWHorizonResult &out)
  {
   JPWHorizonClear(out);
   datetime end1=0,end2=0;
   if(symbol=="" || !JPWHorizonEnds(reference_server_time,end1,end2)) return(false);
   out.reference_time=reference_server_time;
   out.end_1w=end1; out.end_2w=end2;
   string reason="";
   if(approved_sha256!="")
     {
      if(JPWHorizonLoadApprovedCalendar(calendar_file,approved_sha256,symbol,
                                        reference_server_time,out,reason)) return(true);
      out.reason_1w=reason; out.reason_2w=reason;
      return(false); // Never silently downgrade a failed approved-calendar check.
     }
   JPWHorizonSession sessions[];
   if(!JPWHorizonProjectNativeSessions(symbol,reference_server_time,end2,sessions,reason) ||
      !JPWHorizonPastBarsConsistent(symbol,reference_server_time,sessions,reason))
     { out.reason_1w=reason; out.reason_2w=reason; return(false); }
   const int n1=JPWHorizonCountSessions(reference_server_time,end1,sessions);
   const int n2=JPWHorizonCountSessions(reference_server_time,end2,sessions);
   if(n1<1 || n2<n1)
     { out.reason_1w="Grade semanal sem fechamentos H4"; out.reason_2w=out.reason_1w; return(false); }
   out.n_1w=n1; out.n_2w=n2;
   out.status_1w=JPW_HORIZON_ESTIMATED;
   out.status_2w=JPW_HORIZON_ESTIMATED;
   out.reason_1w="Grade semanal recorrente; feriados e excecoes futuros nao confirmados";
   out.reason_2w=out.reason_1w;
   out.source="SymbolInfoSessionQuote / grade semanal do terminal";
   out.source_sha256="";
   return(true);
  }

// No approved calendar hash is provisioned in 1.6.0. This public resolver
// therefore cannot emit EXACT; the optional API above is for a later,
// separately authorized calendar policy.
bool JPWHorizonResolve(const string symbol,const datetime reference_server_time,
                       JPWHorizonResult &out)
  {
   return(JPWHorizonResolveWithApprovedCalendar(symbol,reference_server_time,
                                                 "","",out));
  }
#endif

#endif
