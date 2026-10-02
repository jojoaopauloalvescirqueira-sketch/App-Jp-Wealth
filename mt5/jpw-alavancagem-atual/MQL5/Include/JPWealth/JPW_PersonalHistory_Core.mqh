#ifndef JPW_PERSONAL_HISTORY_CORE_MQH
#define JPW_PERSONAL_HISTORY_CORE_MQH
// Pure observational contract. No terminal, file, trade or notification calls.
#define JPW_PERSONAL_REPEAT_MS 60000
#define JPW_PERSONAL_MAX_SUBJECTS 20000
enum JPWPersonalQuality { JPW_PERSONAL_UNAVAILABLE=0, JPW_PERSONAL_CURRENT=1, JPW_PERSONAL_ESTIMATED=2 };
enum JPWPersonalKind { JPW_PERSONAL_POSITION=1, JPW_PERSONAL_PENDING=2 };
enum JPWPersonalEpisodeState { JPW_PERSONAL_ACTIVE=1, JPW_PERSONAL_SL_PRESENT=2, JPW_PERSONAL_NO_LONGER_PRESENT=3 };
struct JPWPersonalSubject
  {
   int kind; string id; string ticket; string symbol; int side; int order_type;
   double volume; double price; double sl; double tp; bool sl_readable;
   string link_id; string terminal_reason;
  };
struct JPWPersonalCapture
  {
   string account_key; string source; string product_version;
   long started_msc; long finished_msc; long wall_seconds; ulong mono_ms;
   bool stable; bool connected; bool inventory_valid; int quality;
   double balance; double equity; double credit; double profit;
   double margin; double free_margin; double margin_level; double gross;
   bool leverage_valid; string units; string details;
  };
struct JPWPersonalEpisode
  {
   string episode_id; string account_key; JPWPersonalSubject subject;
   int state; long first_wall; long last_wall; long resolved_wall;
   long last_requested_wall; long next_wall; ulong next_mono;
   bool mono_ready; int requested_count; string resolution;
  };
struct JPWPersonalEvent
  { string type; string episode_id; long wall; string payload; };
struct JPWPersonalPeak
  {
   bool valid; int quality; double leverage; long wall; long started_msc; long finished_msc;
   string account_key; string snapshot;
  };
bool JPWPersonalFinite(const double value) { return(MathIsValidNumber(value)); }
bool JPWPersonalDigits(const string value)
  {
   if(value=="" || StringLen(value)>32) return(false);
   for(int i=0;i<StringLen(value);i++)
     { ushort c=StringGetCharacter(value,i); if(c<'0' || c>'9') return(false); }
   return(true);
  }
string JPWPersonalInt(const long value) { return(IntegerToString(value)); }
string JPWPersonalNum(const double value) { return(StringFormat("%.17g",value)); }
string JPWPersonalJSON(const string value)
  {
   string output="\"";
   for(int i=0;i<StringLen(value);i++)
     {
      ushort c=StringGetCharacter(value,i);
      if(c=='"') output+="\\\"";
      else if(c=='\\') output+="\\\\";
      else if(c<32) output+=StringFormat("\\u%04x",(int)c);
      else output+=StringSubstr(value,i,1);
     }
   return(output+"\"");
  }
string JPWPersonalHex(const string value)
  {
   if(value=="") return("-");
   uchar bytes[]; int size=StringToCharArray(value,bytes,0,WHOLE_ARRAY,CP_UTF8)-1;
   if(size<1) return(""); string output="";
   for(int i=0;i<size;i++) output+=StringFormat("%02x",(int)bytes[i]);
   return(output);
  }
int JPWPersonalHexDigit(const ushort c)
  { if(c>='0' && c<='9') return((int)(c-'0')); if(c>='a' && c<='f') return((int)(c-'a')+10); return(-1); }
bool JPWPersonalUnhex(const string value,string &output)
  {
   output=""; if(value=="-") return(true);
   int count=StringLen(value); if(count<2 || count%2!=0) return(false);
   uchar bytes[]; if(ArrayResize(bytes,count/2)!=count/2) return(false);
   for(int i=0;i<count/2;i++)
     { int a=JPWPersonalHexDigit(StringGetCharacter(value,2*i)),b=JPWPersonalHexDigit(StringGetCharacter(value,2*i+1));
       if(a<0 || b<0) return(false); bytes[i]=(uchar)(a*16+b); }
   output=CharArrayToString(bytes,0,count/2,CP_UTF8);
   return(JPWPersonalHex(output)==value);
  }
bool JPWPersonalSubjectValid(JPWPersonalSubject &subject)
  {
   return((subject.kind==JPW_PERSONAL_POSITION || subject.kind==JPW_PERSONAL_PENDING) &&
      JPWPersonalDigits(subject.id) && JPWPersonalDigits(subject.ticket) && subject.symbol!="" &&
      (subject.side==1 || subject.side==-1) && JPWPersonalFinite(subject.volume) && subject.volume>0 &&
      JPWPersonalFinite(subject.price) && subject.price>=0 &&
      JPWPersonalFinite(subject.sl) && subject.sl>=0);
  }
string JPWPersonalSubjectKey(JPWPersonalSubject &subject)
  { return(JPWPersonalInt(subject.kind)+":"+subject.id); }
void JPWPersonalEventAdd(JPWPersonalEvent &events[],const string type,const string id,const long wall,const string payload)
  { int size=ArraySize(events); if(ArrayResize(events,size+1)==size+1)
     { events[size].type=type; events[size].episode_id=id; events[size].wall=wall; events[size].payload=payload; } }
bool JPWPersonalCaptureInventoryValid(JPWPersonalCapture &capture,JPWPersonalSubject &subjects[])
  {
   if(!capture.connected || !capture.stable || !capture.inventory_valid || capture.account_key=="" ||
      capture.wall_seconds<=0 || capture.finished_msc<capture.started_msc || ArraySize(subjects)>JPW_PERSONAL_MAX_SUBJECTS) return(false);
   for(int i=0;i<ArraySize(subjects);i++)
     {
      if(!JPWPersonalSubjectValid(subjects[i])) return(false);
      for(int j=0;j<i;j++) if(JPWPersonalSubjectKey(subjects[i])==JPWPersonalSubjectKey(subjects[j])) return(false);
     }
   return(true);
  }
bool JPWPersonalIsDue(JPWPersonalCapture &capture,JPWPersonalEpisode &episode,bool &clock_inconsistent)
  {
   clock_inconsistent=false;
   if(episode.requested_count==0) return(true);
   if(episode.mono_ready)
     { clock_inconsistent=capture.wall_seconds<episode.last_requested_wall;
       return(capture.mono_ms>=episode.next_mono); }
   // Restored state cannot retain a boot-relative clock. Bound recovery to one
   // notification after live revalidation; never replay elapsed intervals.
   if(capture.wall_seconds<episode.last_requested_wall || episode.next_wall<episode.last_requested_wall ||
      episode.next_wall-episode.last_requested_wall!=60)
     { clock_inconsistent=true; return(true); }
   if(capture.wall_seconds>=episode.next_wall) return(true);
   episode.next_mono=capture.mono_ms+(ulong)(episode.next_wall-capture.wall_seconds)*1000;
   episode.mono_ready=true; return(false);
  }
// due[] contains indexes, not tickets. Caller marks requests AFTER fresh
// reconciliation, independently of whether a persistence write succeeds.
bool JPWPersonalReconcile(JPWPersonalCapture &capture,JPWPersonalSubject &subjects[],
                           JPWPersonalEpisode &episodes[],JPWPersonalEvent &events[],int &due[])
  {
   ArrayResize(events,0); ArrayResize(due,0);
   if(!JPWPersonalCaptureInventoryValid(capture,subjects)) return(false);
   for(int i=0;i<ArraySize(episodes);i++)
     {
      if(episodes[i].state!=JPW_PERSONAL_ACTIVE) continue;
      if(episodes[i].account_key!=capture.account_key) return(false);
      int found=-1;
      for(int j=0;j<ArraySize(subjects);j++)
         if(JPWPersonalSubjectKey(episodes[i].subject)==JPWPersonalSubjectKey(subjects[j])) { found=j; break; }
      if(found<0)
        {
         episodes[i].state=JPW_PERSONAL_NO_LONGER_PRESENT; episodes[i].resolved_wall=capture.wall_seconds;
         if(capture.wall_seconds>episodes[i].last_wall) episodes[i].last_wall=capture.wall_seconds;
         episodes[i].resolution="NO_LONGER_PRESENT";
         JPWPersonalEventAdd(events,"NO_LONGER_PRESENT",episodes[i].episode_id,capture.wall_seconds,""); continue;
        }
      bool changed=(episodes[i].subject.ticket!=subjects[found].ticket || episodes[i].subject.volume!=subjects[found].volume ||
         episodes[i].subject.sl!=subjects[found].sl || episodes[i].subject.tp!=subjects[found].tp ||
         episodes[i].subject.sl_readable!=subjects[found].sl_readable || episodes[i].subject.link_id!=subjects[found].link_id ||
         episodes[i].subject.terminal_reason!=subjects[found].terminal_reason);
      episodes[i].subject=subjects[found]; if(changed && capture.wall_seconds>episodes[i].last_wall) episodes[i].last_wall=capture.wall_seconds;
      if(!subjects[found].sl_readable) continue; // unknown SL never resolves or notifies
      if(subjects[found].sl>0)
        {
         episodes[i].state=JPW_PERSONAL_SL_PRESENT; episodes[i].resolved_wall=capture.wall_seconds;
         episodes[i].resolution="RESOLVED_SL_PRESENT";
         JPWPersonalEventAdd(events,"RESOLVED_SL_PRESENT",episodes[i].episode_id,capture.wall_seconds,"");
        }
     }
   for(int i=0;i<ArraySize(subjects);i++)
     {
      if(!subjects[i].sl_readable || subjects[i].sl!=0) continue;
      int found=-1;
      for(int j=0;j<ArraySize(episodes);j++) if(episodes[j].state==JPW_PERSONAL_ACTIVE &&
         JPWPersonalSubjectKey(episodes[j].subject)==JPWPersonalSubjectKey(subjects[i])) { found=j; break; }
      if(found<0)
        {
         found=ArraySize(episodes); if(ArrayResize(episodes,found+1)!=found+1) return(false);
         JPWPersonalEpisode item;
         item.episode_id=JPWPersonalSubjectKey(subjects[i])+":"+JPWPersonalInt(capture.wall_seconds)+":"+
            JPWPersonalInt((long)capture.mono_ms)+":"+JPWPersonalInt(found);
         item.account_key=capture.account_key; item.subject=subjects[i]; item.state=JPW_PERSONAL_ACTIVE;
         item.first_wall=capture.wall_seconds; item.last_wall=capture.wall_seconds; item.resolved_wall=0;
         item.last_requested_wall=0; item.next_wall=0; item.next_mono=0; item.mono_ready=false;
         item.requested_count=0; item.resolution=""; episodes[found]=item;
         JPWPersonalEventAdd(events,"NO_SL_DETECTED",item.episode_id,capture.wall_seconds,subjects[i].link_id);
        }
      bool inconsistent=false;
      if(JPWPersonalIsDue(capture,episodes[found],inconsistent))
        { int count=ArraySize(due); if(ArrayResize(due,count+1)!=count+1) return(false); due[count]=found; }
      if(inconsistent) JPWPersonalEventAdd(events,"CLOCK_INCONSISTENT",episodes[found].episode_id,capture.wall_seconds,"");
     }
   return(true);
  }
void JPWPersonalMarkRequested(JPWPersonalCapture &capture,JPWPersonalEpisode &episode)
  {
   episode.last_requested_wall=capture.wall_seconds; episode.next_wall=capture.wall_seconds+60;
   episode.next_mono=capture.mono_ms+JPW_PERSONAL_REPEAT_MS; episode.mono_ready=true; episode.requested_count++;
   if(capture.wall_seconds>episode.last_wall) episode.last_wall=capture.wall_seconds;
  }
bool JPWPersonalPeakAccept(JPWPersonalCapture &capture,const string snapshot,
                           JPWPersonalPeak &current,JPWPersonalPeak &estimated,int &changed)
  {
   changed=0;
   if(!capture.stable || !capture.connected || !capture.inventory_valid || !capture.leverage_valid ||
      (capture.quality!=JPW_PERSONAL_CURRENT && capture.quality!=JPW_PERSONAL_ESTIMATED) ||
      !JPWPersonalFinite(capture.equity) || capture.equity<=0 || !JPWPersonalFinite(capture.gross) || capture.gross<0 ||
      capture.account_key=="" || capture.wall_seconds<=0 || capture.started_msc<0 ||
      capture.finished_msc<capture.started_msc || snapshot=="") return(false);
   double value=capture.gross/capture.equity;
   if(!JPWPersonalFinite(value) || value<0) return(false);
   JPWPersonalPeak next;
   next.valid=true; next.quality=capture.quality; next.leverage=value; next.wall=capture.wall_seconds;
   next.started_msc=capture.started_msc; next.finished_msc=capture.finished_msc;
   next.account_key=capture.account_key; next.snapshot=snapshot;
   if(capture.quality==JPW_PERSONAL_CURRENT)
     { if(current.valid && current.account_key!=capture.account_key) return(false);
       if(!current.valid || value>current.leverage) { current=next; changed=JPW_PERSONAL_CURRENT; } }
   else
     { if(estimated.valid && estimated.account_key!=capture.account_key) return(false);
       if(!estimated.valid || value>estimated.leverage) { estimated=next; changed=JPW_PERSONAL_ESTIMATED; } }
   return(true);
  }
string JPWPersonalEncodeSubject(JPWPersonalSubject &s)
  { return(JPWPersonalInt(s.kind)+"|"+s.id+"|"+s.ticket+"|"+JPWPersonalHex(s.symbol)+"|"+JPWPersonalInt(s.side)+"|"+
     JPWPersonalInt(s.order_type)+"|"+JPWPersonalNum(s.volume)+"|"+JPWPersonalNum(s.price)+"|"+JPWPersonalNum(s.sl)+"|"+
     JPWPersonalNum(s.tp)+"|"+JPWPersonalInt(s.sl_readable)+"|"+JPWPersonalHex(s.link_id)+"|"+JPWPersonalHex(s.terminal_reason)); }
bool JPWPersonalDecodeSubject(const string raw,JPWPersonalSubject &s)
  {
   string p[]; if(StringSplit(raw,'|',p)!=13) return(false);
   s.kind=(int)StringToInteger(p[0]); s.id=p[1]; s.ticket=p[2]; s.side=(int)StringToInteger(p[4]);
   s.order_type=(int)StringToInteger(p[5]); s.volume=StringToDouble(p[6]); s.price=StringToDouble(p[7]);
   s.sl=StringToDouble(p[8]); s.tp=StringToDouble(p[9]); s.sl_readable=(bool)StringToInteger(p[10]);
   return(JPWPersonalUnhex(p[3],s.symbol) && JPWPersonalUnhex(p[11],s.link_id) &&
      JPWPersonalUnhex(p[12],s.terminal_reason) && JPWPersonalSubjectValid(s) && JPWPersonalEncodeSubject(s)==raw);
  }
string JPWPersonalEncodeEpisode(JPWPersonalEpisode &e)
  { return("1|"+JPWPersonalHex(e.episode_id)+"|"+JPWPersonalHex(e.account_key)+"|"+JPWPersonalHex(JPWPersonalEncodeSubject(e.subject))+"|"+
     JPWPersonalInt(e.state)+"|"+JPWPersonalInt(e.first_wall)+"|"+JPWPersonalInt(e.last_wall)+"|"+JPWPersonalInt(e.resolved_wall)+"|"+
     JPWPersonalInt(e.last_requested_wall)+"|"+JPWPersonalInt(e.next_wall)+"|"+JPWPersonalInt(e.requested_count)+"|"+JPWPersonalHex(e.resolution)); }
bool JPWPersonalDecodeEpisode(const string raw,JPWPersonalEpisode &e)
  {
   string p[],subject; if(StringSplit(raw,'|',p)!=12 || p[0]!="1") return(false);
   if(!JPWPersonalUnhex(p[1],e.episode_id) || !JPWPersonalUnhex(p[2],e.account_key) || !JPWPersonalUnhex(p[3],subject) ||
      !JPWPersonalDecodeSubject(subject,e.subject) || !JPWPersonalUnhex(p[11],e.resolution)) return(false);
   e.state=(int)StringToInteger(p[4]); e.first_wall=StringToInteger(p[5]); e.last_wall=StringToInteger(p[6]);
   e.resolved_wall=StringToInteger(p[7]); e.last_requested_wall=StringToInteger(p[8]); e.next_wall=StringToInteger(p[9]);
   e.requested_count=(int)StringToInteger(p[10]); e.next_mono=0; e.mono_ready=false;
   return(e.episode_id!="" && e.account_key!="" && e.state>=1 && e.state<=3 && e.first_wall>0 &&
      e.last_wall>=e.first_wall && e.requested_count>=0 && JPWPersonalEncodeEpisode(e)==raw);
  }
string JPWPersonalEncodePeak(JPWPersonalPeak &peak)
  { return("1|"+JPWPersonalInt(peak.quality)+"|"+JPWPersonalNum(peak.leverage)+"|"+JPWPersonalInt(peak.wall)+"|"+
      JPWPersonalInt(peak.started_msc)+"|"+JPWPersonalInt(peak.finished_msc)+"|"+JPWPersonalHex(peak.account_key)+"|"+JPWPersonalHex(peak.snapshot)); }
bool JPWPersonalDecodePeak(const string raw,JPWPersonalPeak &peak)
  {
   string p[]; if(StringSplit(raw,'|',p)!=8 || p[0]!="1") return(false);
   peak.quality=(int)StringToInteger(p[1]); peak.leverage=StringToDouble(p[2]); peak.wall=StringToInteger(p[3]);
   peak.started_msc=StringToInteger(p[4]); peak.finished_msc=StringToInteger(p[5]);
   if(!JPWPersonalUnhex(p[6],peak.account_key) || !JPWPersonalUnhex(p[7],peak.snapshot)) return(false);
   peak.valid=true;
   return(peak.quality>=1 && peak.quality<=2 && JPWPersonalFinite(peak.leverage) && peak.leverage>=0 &&
      peak.wall>0 && peak.finished_msc>=peak.started_msc && peak.account_key!="" && peak.snapshot!="" && JPWPersonalEncodePeak(peak)==raw);
  }
#endif
