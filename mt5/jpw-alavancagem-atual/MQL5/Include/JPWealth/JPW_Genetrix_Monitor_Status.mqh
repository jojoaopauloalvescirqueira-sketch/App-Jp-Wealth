#ifndef JPW_GENETRIX_MONITOR_STATUS_MQH
#define JPW_GENETRIX_MONITOR_STATUS_MQH
#include <JPWealth/JPW_Alavancagem_RaizN_Store.mqh>
#include <JPWealth/JPW_Alavancagem_Version.mqh>
// Additive technical diagnostic. Never a financial sample or domain schema.
#define JPW_MONITOR_FOLDER "JPWealth\\Genetrix\\Monitor\\"
#define JPW_MONITOR_STATUS_MAX_BYTES 16384
#define JPW_MONITOR_STATUS_MAX_AGE_MS 30000
enum JPWMonitorModuleState
  { JPW_MONITOR_DETACHED=0,JPW_MONITOR_PREPARING=1,JPW_MONITOR_CURRENT=2,
    JPW_MONITOR_HISTORICAL=3,JPW_MONITOR_CONFLICT=4,JPW_MONITOR_FAILED=5,
    JPW_MONITOR_PARTIAL=6 };
struct JPWMonitorModuleStatus
  {
   int state;
   string quality,reason;
   long observed_utc,observed_mono_ms;
   int progress;
  };
struct JPWMonitorSnapshot
  {
   string account_key,publisher_token,role,product_version,build_id;
   long chart_id,heartbeat_utc,heartbeat_mono_ms;
   bool active,live;
   JPWMonitorModuleStatus stop_risk,personal,ledger,raiz;
   long last_cycle_ms,overruns;
  };
string JPWMonitorLeaseName(const string token)
  { return(JPWRaizNIsHash(token) ? "JPWMN_"+StringSubstr(token,0,48) : ""); }
string JPWMonitorStatusPath(const string key)
  { return(JPWRaizNIsHash(key) ? JPW_MONITOR_FOLDER+"status_"+key+".txt" : ""); }
void JPWMonitorModuleClear(JPWMonitorModuleStatus &module)
  {
   module.state=JPW_MONITOR_DETACHED; module.quality="N/A";
   module.reason="Não anexado"; module.observed_utc=0;
   module.observed_mono_ms=0; module.progress=0;
  }
void JPWMonitorSnapshotClear(JPWMonitorSnapshot &snapshot)
  {
   snapshot.account_key=""; snapshot.publisher_token=""; snapshot.role="";
   snapshot.product_version=""; snapshot.build_id=""; snapshot.chart_id=0;
   snapshot.heartbeat_utc=0; snapshot.heartbeat_mono_ms=0;
   snapshot.active=false; snapshot.live=false;
   snapshot.last_cycle_ms=0; snapshot.overruns=0;
   JPWMonitorModuleClear(snapshot.stop_risk); JPWMonitorModuleClear(snapshot.personal);
   JPWMonitorModuleClear(snapshot.ledger); JPWMonitorModuleClear(snapshot.raiz);
  }
string JPWMonitorStatusHex(const string value)
  {
   if(value=="") return("-");
   uchar bytes[]; string encoded="";
   const int n=StringToCharArray(value,bytes,0,WHOLE_ARRAY,CP_UTF8)-1;
   if(n<1 || n>2048) return("");
   for(int i=0;i<n;i++) encoded+=StringFormat("%02x",(int)bytes[i]);
   return(encoded);
  }
int JPWMonitorStatusDigit(const ushort value)
  { if(value>='0' && value<='9') return((int)(value-'0'));
    if(value>='a' && value<='f') return((int)(value-'a')+10); return(-1); }
bool JPWMonitorStatusUnhex(const string value,string &decoded)
  {
   decoded=""; if(value=="-") return(true);
   const int n=StringLen(value);
   if(n<2 || n>4096 || n%2!=0) return(false);
   uchar bytes[]; if(ArrayResize(bytes,n/2)!=n/2) return(false);
   for(int i=0;i<n/2;i++)
     {
      const int a=JPWMonitorStatusDigit(StringGetCharacter(value,2*i));
      const int b=JPWMonitorStatusDigit(StringGetCharacter(value,2*i+1));
      if(a<0 || b<0) return(false); bytes[i]=(uchar)(16*a+b);
     }
   decoded=CharArrayToString(bytes,0,n/2,CP_UTF8);
   return(JPWMonitorStatusHex(decoded)==value);
  }
bool JPWMonitorStatusInteger(const string value,long &number)
  {
   number=StringToInteger(value);
   return(number>=0 && IntegerToString(number)==value);
  }
bool JPWMonitorModuleValid(JPWMonitorModuleStatus &module)
  {
   return(module.state>=0 && module.state<=6 && module.observed_utc>=0 &&
      module.observed_mono_ms>=0 && module.progress>=0 && module.progress<=100 &&
      (module.quality=="Current" || module.quality=="Estimated" ||
       module.quality=="Partial" || module.quality=="Historical" || module.quality=="N/A") &&
      JPWMonitorStatusHex(module.quality)!="" && JPWMonitorStatusHex(module.reason)!="");
  }
string JPWMonitorModuleEncode(JPWMonitorModuleStatus &module)
  {
   if(!JPWMonitorModuleValid(module)) return("");
   return(IntegerToString(module.state)+"|"+JPWMonitorStatusHex(module.quality)+"|"+
      JPWMonitorStatusHex(module.reason)+"|"+IntegerToString(module.observed_utc)+"|"+
      IntegerToString(module.observed_mono_ms)+"|"+IntegerToString(module.progress));
  }
string JPWMonitorStatusEncode(JPWMonitorSnapshot &snapshot)
  {
   if(!JPWRaizNIsHash(snapshot.account_key) || !JPWRaizNIsHash(snapshot.publisher_token) ||
      !JPWRaizNIsHash(snapshot.build_id) || snapshot.chart_id<0 ||
      snapshot.heartbeat_utc<=0 || snapshot.heartbeat_mono_ms<=0 ||
      snapshot.last_cycle_ms<0 || snapshot.overruns<0 || snapshot.role=="" ||
      snapshot.product_version=="") return("");
   string parts[4];
   parts[0]=JPWMonitorModuleEncode(snapshot.stop_risk);
   parts[1]=JPWMonitorModuleEncode(snapshot.personal);
   parts[2]=JPWMonitorModuleEncode(snapshot.ledger);
   parts[3]=JPWMonitorModuleEncode(snapshot.raiz);
   for(int i=0;i<4;i++) if(parts[i]=="") return("");
   string raw="JPWMONITOR|1|"+snapshot.account_key+"|"+snapshot.publisher_token+"|"+
      JPWMonitorStatusHex(snapshot.role)+"|"+JPWMonitorStatusHex(snapshot.product_version)+"|"+
      snapshot.build_id+"|"+IntegerToString(snapshot.chart_id)+"|"+
      IntegerToString(snapshot.heartbeat_utc)+"|"+IntegerToString(snapshot.heartbeat_mono_ms)+"|"+
      (snapshot.active ? "1" : "0")+"|"+IntegerToString(snapshot.last_cycle_ms)+"|"+
      IntegerToString(snapshot.overruns);
   for(int i=0;i<4;i++) raw+="|"+parts[i];
   string digest="";
   return(JPWRaizNHash(raw,digest) ? raw+"|"+digest : "");
  }
bool JPWMonitorModuleDecode(string &parts[],const int offset,JPWMonitorModuleStatus &module)
  {
   long state=0,progress=0;
   if(!JPWMonitorStatusInteger(parts[offset],state) || state>6 ||
      !JPWMonitorStatusUnhex(parts[offset+1],module.quality) ||
      !JPWMonitorStatusUnhex(parts[offset+2],module.reason) ||
      !JPWMonitorStatusInteger(parts[offset+3],module.observed_utc) ||
      !JPWMonitorStatusInteger(parts[offset+4],module.observed_mono_ms) ||
      !JPWMonitorStatusInteger(parts[offset+5],progress) || progress>100) return(false);
   module.state=(int)state; module.progress=(int)progress;
   return(JPWMonitorModuleValid(module));
  }
bool JPWMonitorStatusDecode(const string raw,JPWMonitorSnapshot &snapshot)
  {
   string parts[]; JPWMonitorSnapshot value; JPWMonitorSnapshotClear(value);
   if(StringSplit(raw,'|',parts)!=38 || parts[0]!="JPWMONITOR" || parts[1]!="1" ||
      !JPWRaizNIsHash(parts[2]) || !JPWRaizNIsHash(parts[3]) || !JPWRaizNIsHash(parts[6]) ||
      !JPWMonitorStatusUnhex(parts[4],value.role) || !JPWMonitorStatusUnhex(parts[5],value.product_version) ||
      !JPWMonitorStatusInteger(parts[7],value.chart_id) ||
      !JPWMonitorStatusInteger(parts[8],value.heartbeat_utc) ||
      !JPWMonitorStatusInteger(parts[9],value.heartbeat_mono_ms) ||
      (parts[10]!="0" && parts[10]!="1") ||
      !JPWMonitorStatusInteger(parts[11],value.last_cycle_ms) ||
      !JPWMonitorStatusInteger(parts[12],value.overruns)) return(false);
   value.account_key=parts[2]; value.publisher_token=parts[3]; value.build_id=parts[6];
   value.active=(parts[10]=="1");
   if(!JPWMonitorModuleDecode(parts,13,value.stop_risk) ||
      !JPWMonitorModuleDecode(parts,19,value.personal) ||
      !JPWMonitorModuleDecode(parts,25,value.ledger) ||
      !JPWMonitorModuleDecode(parts,31,value.raiz) || JPWMonitorStatusEncode(value)!=raw) return(false);
   snapshot=value; return(true);
  }
bool JPWMonitorWriteStatus(JPWMonitorSnapshot &snapshot,string &reason)
  {
   reason=""; const string path=JPWMonitorStatusPath(snapshot.account_key);
   const string raw=JPWMonitorStatusEncode(snapshot);
   if(path=="" || raw=="" || StringLen(raw)>JPW_MONITOR_STATUS_MAX_BYTES)
     { reason="Diagnóstico inválido ou excessivo"; return(false); }
   FolderCreate("JPWealth"); FolderCreate("JPWealth\\Genetrix");
   if(!FolderCreate("JPWealth\\Genetrix\\Monitor"))
     { reason="Diretório diagnóstico indisponível"; return(false); }
   const string temporary=path+"."+StringSubstr(snapshot.publisher_token,0,16)+".tmp";
   const int file=FileOpen(temporary,FILE_WRITE|FILE_BIN);
   if(file==INVALID_HANDLE) { reason="Escrita do diagnóstico indisponível"; return(false); }
   uchar bytes[]; const int count=StringToCharArray(raw,bytes,0,WHOLE_ARRAY,CP_UTF8)-1;
   bool ok=count>0 && ArrayResize(bytes,count)==count && FileWriteArray(file,bytes,0,count)==(uint)count;
   FileFlush(file); FileClose(file);
   if(ok) ok=FileMove(temporary,0,path,FILE_REWRITE);
   if(!ok) reason="Publicação do diagnóstico não confirmada";
   return(ok);
  }
void JPWMonitorModuleHistorical(JPWMonitorModuleStatus &module,const bool live,const ulong now)
  {
   if(module.state!=JPW_MONITOR_CURRENT) return;
   if(!live || module.observed_mono_ms<=0 || now<(ulong)module.observed_mono_ms ||
      now-(ulong)module.observed_mono_ms>JPW_MONITOR_STATUS_MAX_AGE_MS)
     { module.state=JPW_MONITOR_HISTORICAL; module.quality="Historical"; }
  }
bool JPWMonitorReadStatus(const string account_key,JPWMonitorSnapshot &snapshot,string &reason)
  {
   reason=""; JPWMonitorSnapshotClear(snapshot);
   const string path=JPWMonitorStatusPath(account_key);
   const int file=(path=="" ? INVALID_HANDLE : FileOpen(path,FILE_READ|FILE_BIN|FILE_SHARE_READ));
   if(file==INVALID_HANDLE) { reason="Núcleo não confirmado; diagnóstico ausente/indisponível"; return(false); }
   const ulong size=FileSize(file); uchar bytes[];
   if(size==0 || size>(ulong)JPW_MONITOR_STATUS_MAX_BYTES ||
      ArrayResize(bytes,(int)size)!=(int)size || FileReadArray(file,bytes,0,(int)size)!=(uint)size)
     { FileClose(file); reason="Diagnóstico incompleto ou inválido"; return(false); }
   FileClose(file); const string raw=CharArrayToString(bytes,0,(int)size,CP_UTF8);
   if(!JPWMonitorStatusDecode(raw,snapshot) || snapshot.account_key!=account_key)
     { JPWMonitorSnapshotClear(snapshot); reason="Diagnóstico recusado: identidade/checksum/schema"; return(false); }
   const ulong now=GetTickCount64(); double lease=0;
   snapshot.live=snapshot.active && snapshot.heartbeat_mono_ms>0 && now>=(ulong)snapshot.heartbeat_mono_ms &&
      now-(ulong)snapshot.heartbeat_mono_ms<=JPW_MONITOR_STATUS_MAX_AGE_MS &&
      GlobalVariableGet(JPWMonitorLeaseName(snapshot.publisher_token),lease) &&
      lease==(double)snapshot.heartbeat_mono_ms;
   JPWMonitorModuleHistorical(snapshot.stop_risk,snapshot.live,now);
   JPWMonitorModuleHistorical(snapshot.personal,snapshot.live,now);
   JPWMonitorModuleHistorical(snapshot.ledger,snapshot.live,now);
   JPWMonitorModuleHistorical(snapshot.raiz,snapshot.live,now);
   if(!snapshot.live) reason="Registro anterior; presença atual do núcleo não confirmada";
   return(true);
  }
#endif
