#ifndef JPW_GENETRIX_RISK_STORE_MQH
#define JPW_GENETRIX_RISK_STORE_MQH
#include <JPWealth/JPW_Genetrix_Risk_Core.mqh>
#include <JPWealth/JPW_Alavancagem_Profile.mqh>

// New isolated local namespace. No legacy financial/profile/observer store mutation.
// Public consumer API is read-only; an observed state is NOT proof of an active executor.
#define JPW_RISK_FOLDER "JPWealth\\GenetrixRiskV1\\"
#define JPW_RISK_MAX_BYTES 65536
struct JPWRiskView
  {
   int schema;
   string account_key;
   long generation;
   long observed_utc;
   string quality;
   string state;
   string reason;
   double gross;
   double equity;
   double leverage;
   double projected_leverage;
   bool pending_projection_valid;
   int pending_count;
   int position_count;
   int action_kind;
   ulong action_ticket;
   long action_identifier;
   double action_volume;
   bool protection_incomplete;
   bool demo_armed;
   string session_challenge;
  };
struct JPWRiskRecord { JPWRiskView view; JPWRiskMachine machine; };

bool JPWRiskAccountKey(JPWAccount &account,string &key)
  {
   string financial="";
   if(!JPWProfileAccountHash(account,financial)) return(false);
   return(JPWProfileHash(JPW_RISK_POLICY+JPWProfileFrame(financial)+
      JPWProfileFrame(TerminalInfoString(TERMINAL_DATA_PATH)),key));
  }
string JPWRiskStorePath(const string key,const int slot)
  { return(JPW_RISK_FOLDER+key+"."+IntegerToString(slot)+".risk"); }
bool JPWRiskFrameRead(const string body,int &offset,string &value)
  {
   value="";
   const int colon=StringFind(body,":",offset);
   if(colon<offset || colon-offset>6) return(false);
   const string digits=StringSubstr(body,offset,colon-offset);
   const int count=(int)StringToInteger(digits);
   if(count<0 || count>JPW_RISK_MAX_BYTES || IntegerToString(count)!=digits ||
      colon+1+count>StringLen(body)) return(false);
   value=StringSubstr(body,colon+1,count); offset=colon+1+count;
   return(true);
  }
string JPWRiskEncode(JPWRiskRecord &record)
  {
   JPWRiskView v=record.view; JPWRiskMachine m=record.machine;
   string b=JPWProfileFrame(JPW_RISK_POLICY);
   b+=JPWProfileFrame(IntegerToString(v.schema))+JPWProfileFrame(v.account_key);
   b+=JPWProfileFrame(IntegerToString(v.generation))+JPWProfileFrame(IntegerToString(v.observed_utc));
   b+=JPWProfileFrame(v.quality)+JPWProfileFrame(v.state)+JPWProfileFrame(v.reason);
   b+=JPWProfileFrame(DoubleToString(v.gross,16))+JPWProfileFrame(DoubleToString(v.equity,16));
   b+=JPWProfileFrame(DoubleToString(v.leverage,16))+JPWProfileFrame(DoubleToString(v.projected_leverage,16));
   b+=JPWProfileFrame(IntegerToString(v.pending_projection_valid))+JPWProfileFrame(IntegerToString(v.pending_count));
   b+=JPWProfileFrame(IntegerToString(v.position_count))+JPWProfileFrame(v.session_challenge);
   b+=JPWProfileFrame(IntegerToString((int)m.phase))+JPWProfileFrame(IntegerToString(m.armed));
   b+=JPWProfileFrame(IntegerToString(m.cancel_refused))+JPWProfileFrame(IntegerToString(m.protection_incomplete));
   b+=JPWProfileFrame(IntegerToString((int)m.active.kind))+JPWProfileFrame(IntegerToString((long)m.active.ticket));
   b+=JPWProfileFrame(IntegerToString(m.active.identifier))+JPWProfileFrame(m.active.symbol);
   b+=JPWProfileFrame(IntegerToString(m.active.direction))+JPWProfileFrame(DoubleToString(m.active.volume,16));
   b+=JPWProfileFrame(IntegerToString((long)m.request_order))+JPWProfileFrame(IntegerToString((long)m.request_deal));
   b+=JPWProfileFrame(IntegerToString(m.request_id))+JPWProfileFrame(IntegerToString(m.retcode));
   b+=JPWProfileFrame(m.nonce)+JPWProfileFrame(IntegerToString(m.submitted_utc));
   b+=JPWProfileFrame(DoubleToString(m.executed_volume,16));
   string hash="";
   if(StringLen(b)>JPW_RISK_MAX_BYTES/2 || StringFind(b,"\n")>=0 ||
      StringFind(b,"\r")>=0 || !JPWProfileHash(b,hash)) return("");
   return("JPW-RISK/1|"+hash+"|"+b);
  }
bool JPWRiskDecode(const string payload,JPWRiskRecord &record)
  {
   if(StringSubstr(payload,0,11)!="JPW-RISK/1|" || StringLen(payload)<76) return(false);
   const string checksum=StringSubstr(payload,11,64);
   if(StringSubstr(payload,75,1)!="|") return(false);
   const string body=StringSubstr(payload,76);
   string computed="";
   if(!JPWProfileHash(body,computed) || checksum!=computed) return(false);
   string values[];
   if(ArrayResize(values,33)!=33) return(false);
   int offset=0;
   for(int i=0;i<33;i++) if(!JPWRiskFrameRead(body,offset,values[i])) return(false);
   if(offset!=StringLen(body) || values[0]!=JPW_RISK_POLICY) return(false);
   JPWRiskRecord candidate;
   candidate.view.schema=(int)StringToInteger(values[1]); candidate.view.account_key=values[2];
   candidate.view.generation=StringToInteger(values[3]); candidate.view.observed_utc=StringToInteger(values[4]);
   candidate.view.quality=values[5]; candidate.view.state=values[6]; candidate.view.reason=values[7];
   candidate.view.gross=StringToDouble(values[8]); candidate.view.equity=StringToDouble(values[9]);
   candidate.view.leverage=StringToDouble(values[10]); candidate.view.projected_leverage=StringToDouble(values[11]);
   candidate.view.pending_projection_valid=(values[12]=="1");
   candidate.view.pending_count=(int)StringToInteger(values[13]);
   candidate.view.position_count=(int)StringToInteger(values[14]); candidate.view.session_challenge=values[15];
   candidate.machine.phase=(JPWRiskPhase)StringToInteger(values[16]); candidate.machine.armed=(values[17]=="1");
   candidate.machine.cancel_refused=(values[18]=="1"); candidate.machine.protection_incomplete=(values[19]=="1");
   candidate.machine.active.kind=(JPWRiskActionKind)StringToInteger(values[20]);
   candidate.machine.active.ticket=(ulong)StringToInteger(values[21]); candidate.machine.active.identifier=StringToInteger(values[22]);
   candidate.machine.active.symbol=values[23]; candidate.machine.active.direction=StringToInteger(values[24]);
   candidate.machine.active.volume=StringToDouble(values[25]); candidate.machine.request_order=(ulong)StringToInteger(values[26]);
   candidate.machine.request_deal=(ulong)StringToInteger(values[27]); candidate.machine.request_id=(uint)StringToInteger(values[28]);
   candidate.machine.retcode=(uint)StringToInteger(values[29]); candidate.machine.nonce=values[30];
   candidate.machine.submitted_utc=StringToInteger(values[31]); candidate.machine.executed_volume=StringToDouble(values[32]);
   if(candidate.view.schema!=JPW_RISK_SCHEMA || !JPWProfileIsHash(candidate.view.account_key) ||
      candidate.view.generation<=0 || candidate.view.observed_utc<=0 ||
      candidate.view.pending_count<0 || candidate.view.position_count<0 ||
      candidate.machine.phase<JPW_RISK_OBSERVE || candidate.machine.phase>JPW_RISK_PAUSED_LIFO ||
      candidate.machine.active.kind<JPW_RISK_NONE || candidate.machine.active.kind>JPW_RISK_CLOSE ||
      (candidate.view.quality!="Current" && candidate.view.quality!="Estimated" && candidate.view.quality!="N/A") ||
      !MathIsValidNumber(candidate.view.gross) || !MathIsValidNumber(candidate.view.equity) ||
      !MathIsValidNumber(candidate.view.leverage) || !MathIsValidNumber(candidate.view.projected_leverage)) return(false);
   if(candidate.machine.phase==JPW_RISK_UNKNOWN || candidate.machine.phase==JPW_RISK_REMAINDER ||
      candidate.machine.phase==JPW_RISK_PAUSED_LIFO)
     {
      if(candidate.machine.active.kind==JPW_RISK_NONE || candidate.machine.active.ticket==0 ||
         candidate.machine.active.symbol=="" || !JPWFinitePositive(candidate.machine.active.volume) ||
         candidate.machine.nonce=="" || candidate.machine.submitted_utc<=0) return(false);
      if(candidate.machine.active.kind==JPW_RISK_CLOSE &&
         (candidate.machine.active.identifier<=0 ||
          (candidate.machine.active.direction!=POSITION_TYPE_BUY && candidate.machine.active.direction!=POSITION_TYPE_SELL))) return(false);
      if((candidate.machine.phase==JPW_RISK_REMAINDER || candidate.machine.phase==JPW_RISK_PAUSED_LIFO) &&
         candidate.machine.active.kind!=JPW_RISK_CLOSE) return(false);
     }
   // Canonical round-trip rejects malformed/overflowed numbers and booleans, not just checksum damage.
   if(JPWRiskEncode(candidate)!=payload) return(false);
   candidate.view.action_kind=(int)candidate.machine.active.kind;
   candidate.view.action_ticket=candidate.machine.active.ticket;
   candidate.view.action_identifier=candidate.machine.active.identifier;
   candidate.view.action_volume=candidate.machine.active.volume;
   candidate.view.protection_incomplete=candidate.machine.protection_incomplete;
   candidate.view.demo_armed=candidate.machine.armed;
   record=candidate; return(true);
  }
bool JPWRiskReadPayload(const string path,string &payload)
  {
   payload="";
   const int handle=FileOpen(path,FILE_READ|FILE_TXT|FILE_ANSI|FILE_COMMON|FILE_SHARE_READ|FILE_SHARE_WRITE,0,CP_UTF8);
   if(handle==INVALID_HANDLE) return(false);
   if(FileSize(handle)<=0 || FileSize(handle)>JPW_RISK_MAX_BYTES) { FileClose(handle); return(false); }
   payload=FileReadString(handle); const bool complete=FileIsEnding(handle);
   FileClose(handle); return(complete && payload!="");
  }
bool JPWRiskLoadRecord(const string key,JPWRiskRecord &record,string &reason)
  {
   if(!JPWProfileIsHash(key)) { reason="INVALID_ACCOUNT_KEY"; return(false); }
   bool found=false;
   for(int slot=0;slot<2;slot++)
     {
      const string path=JPWRiskStorePath(key,slot);
      // An interrupted latest intent must never be hidden by fallback to an older clean slot.
      if(FileIsExist(path+".tmp",FILE_COMMON)) { reason="INTERRUPTED_WRITE_REVIEW_REQUIRED"; return(false); }
      if(!FileIsExist(path,FILE_COMMON)) continue;
      string payload=""; JPWRiskRecord candidate;
      if(!JPWRiskReadPayload(path,payload) || !JPWRiskDecode(payload,candidate) || candidate.view.account_key!=key)
         { reason="STORE_CORRUPT_OR_UNREADABLE"; return(false); }
      if(!found || candidate.view.generation>record.view.generation) { record=candidate; found=true; }
      else if(candidate.view.generation==record.view.generation)
         { reason="STORE_GENERATION_COLLISION"; return(false); }
     }
   reason=(found ? "READ_CONFIRMED" : "ABSENT"); return(found);
  }
bool JPWRiskSaveRecord(JPWRiskRecord &record,string &reason)
  {
   const long old=record.view.generation;
   if(old<0 || old==LONG_MAX) { reason="INVALID_GENERATION"; return(false); }
   record.view.generation=old+1;
   const string payload=JPWRiskEncode(record);
   const string path=JPWRiskStorePath(record.view.account_key,(int)(record.view.generation%2));
   if(payload=="")
     { record.view.generation=old; reason="STORE_ENCODING_FAILED"; return(false); }
   FolderCreate("JPWealth",FILE_COMMON);
   FolderCreate(JPW_RISK_FOLDER,FILE_COMMON);
   const int handle=FileOpen(path+".tmp",FILE_WRITE|FILE_TXT|FILE_ANSI|FILE_COMMON,0,CP_UTF8);
   if(handle==INVALID_HANDLE) { record.view.generation=old; reason="STORE_OPEN_FAILED"; return(false); }
   ResetLastError(); const uint written=FileWriteString(handle,payload); FileFlush(handle);
   const bool flushed=(written>0 && GetLastError()==0); FileClose(handle);
   string read=""; JPWRiskRecord check;
   if(!flushed || !JPWRiskReadPayload(path+".tmp",read) || read!=payload || !JPWRiskDecode(read,check) ||
      !FileMove(path+".tmp",FILE_COMMON,path,FILE_COMMON|FILE_REWRITE) ||
      !JPWRiskReadPayload(path,read) || read!=payload)
      { record.view.generation=old; reason="STORE_COMMIT_UNCONFIRMED"; return(false); }
   reason="PERSISTED_AND_READ_BACK"; return(true);
  }
bool JPWRiskAppendReceipt(JPWRiskRecord &record,const string event,string &reason)
  {
   // Local structured financial audit, distinct from technical diagnostics.
   const string payload=JPWRiskEncode(record);
   if(payload=="" || event=="" || StringFind(event,"\n")>=0) return(false);
   const string path=JPW_RISK_FOLDER+record.view.account_key+".receipts";
   const int h=FileOpen(path,FILE_READ|FILE_WRITE|FILE_TXT|FILE_ANSI|FILE_COMMON|FILE_SHARE_READ,0,CP_UTF8);
   if(h==INVALID_HANDLE) { reason="RECEIPT_OPEN_FAILED"; return(false); }
   if(FileSize(h)>67108864) { FileClose(h); reason="RECEIPT_CAPACITY_REACHED_PRESERVED"; return(false); }
   const long offset=(long)FileSize(h);
   FileSeek(h,0,SEEK_END); ResetLastError();
   const string body=JPWProfileFrame(event)+JPWProfileFrame(payload);
   const uint n=FileWriteString(h,body+"\r\n"); FileFlush(h);
   bool ok=(n>0 && GetLastError()==0);
   if(ok) ok=(FileSeek(h,offset,SEEK_SET) && FileReadString(h)==body);
   FileClose(h); reason=(ok ? "RECEIPT_APPENDED" : "RECEIPT_WRITE_UNCONFIRMED"); return(ok);
  }
bool JPWRiskReadView(JPWAccount &account,JPWRiskView &view,string &reason)
  {
   string key=""; JPWRiskRecord record;
   if(!JPWRiskAccountKey(account,key) || !JPWRiskLoadRecord(key,record,reason)) return(false);
   view=record.view;
   const long now=(long)TimeGMT();
   if(now<=0 || view.observed_utc>now+2 || now-view.observed_utc>30)
     { view.quality="N/A"; view.demo_armed=false; view.reason="LAST_NOT_RECENT_EXECUTOR_NOT_CONFIRMED"; }
   return(true);
  }
#endif
