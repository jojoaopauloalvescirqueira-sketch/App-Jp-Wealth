#ifndef JPW_ALAVANCAGEM_RAIZN_STORE_MQH
#define JPW_ALAVANCAGEM_RAIZN_STORE_MQH
#include <JPWealth/JPW_Alavancagem_Core.mqh>
#include <JPWealth/JPW_Alavancagem_RaizN_Core.mqh>

// Registro local de cenarios declarados. Nunca usa FILE_COMMON, nem altera
// os formatos de MDD, Genese ou do perfil USC. A instalacao entra na chave
// opaca; nomes de arquivos nao contem login, servidor ou simbolo em claro.
#define JPW_RAIZN_FOLDER "JPWealth\\Alavancagem\\"
#define JPW_RAIZN_MAX_BYTES 8192
#define JPW_RAIZN_MAX_TEXT_BYTES 512
#define JPW_RAIZN_MODEL_VERSION "JPW-RAIZ-N/1.0"
#define JPW_RAIZN_NAME_HEX 20

enum JPW_RAIZN_STATE
  {
   JPW_RAIZN_VALID=0,
   JPW_RAIZN_ABSENT,
   JPW_RAIZN_INVALID,
   JPW_RAIZN_INCOMPATIBLE,
   JPW_RAIZN_IO_ERROR,
   JPW_RAIZN_BUSY,
   JPW_RAIZN_ACCOUNT_UNAVAILABLE,
   JPW_RAIZN_CONFLICT
  };

struct JPWRaizNScenario
  {
   int schema;
   string model_version; // versao da convencao matematica, nao do arquivo.
   string account_key;
   string scenario_id;
   string symbol;
   double p0;
   string p0_origin;
   datetime decision_server_time;
   double atr;
   string atr_source; // MT5 ou DECLARED.
   string atr_provenance;
   string atr_variant;
   datetime atr_bar_server_time;
   int n_h4;
   string n_reason;
   double factor;
   string factor_status; // DECLARED, ILLUSTRATIVE ou SOURCED.
   string factor_source;
   string factor_reason;
   datetime confirmed_at_utc;
   bool retrospective;
   int declared_side; // +1 compra, -1 venda, 0 indefinido.
   string parent_id;
   string revision_reason;
  };

struct JPWRaizNBinding
  {
   string scenario_id;
   long identifier;
   long origin_ticket;
   long direction;
   JPW_RAIZN_STATE state; // estado opcional; nunca invalida o cenario.
  };

void JPWRaizNClearScenario(JPWRaizNScenario &record)
  {
   record.schema=0; record.model_version="";
   record.account_key=""; record.scenario_id="";
   record.symbol=""; record.p0=0.0; record.p0_origin="";
   record.decision_server_time=0; record.atr=0.0; record.atr_source="";
   record.atr_provenance=""; record.atr_variant="";
   record.atr_bar_server_time=0; record.n_h4=0;
   record.n_reason=""; record.factor=0.0; record.factor_status="";
   record.factor_source=""; record.factor_reason="";
   record.confirmed_at_utc=0; record.retrospective=false;
   record.declared_side=0;
   record.parent_id=""; record.revision_reason="";
  }

void JPWRaizNClearBinding(JPWRaizNBinding &binding)
  {
   binding.scenario_id=""; binding.identifier=0;
   binding.origin_ticket=0; binding.direction=-1;
   binding.state=JPW_RAIZN_ABSENT;
  }

bool JPWRaizNHash(const string value,string &hex)
  {
   hex="";
   uchar source[]; uchar key[]; uchar digest[];
   const int copied=StringToCharArray(value,source,0,WHOLE_ARRAY,CP_UTF8);
   if(copied<=0 || ArrayResize(source,copied-1)!=copied-1) return(false);
   if(CryptEncode(CRYPT_HASH_SHA256,source,key,digest)!=32) return(false);
   for(int i=0;i<32;i++) hex+=StringFormat("%02x",(int)digest[i]);
   return(StringLen(hex)==64);
  }

bool JPWRaizNIsHash(const string value)
  {
   if(StringLen(value)!=64) return(false);
   for(int i=0;i<64;i++)
     {
      const ushort c=StringGetCharacter(value,i);
      if(!((c>='0' && c<='9') || (c>='a' && c<='f'))) return(false);
     }
   return(true);
  }

string JPWRaizNFrame(const string value)
  { return(IntegerToString(StringLen(value))+":"+value); }

bool JPWRaizNFolderValid(const string folder)
  {
   return(StringLen(folder)>=StringLen(JPW_RAIZN_FOLDER) &&
          StringFind(folder,JPW_RAIZN_FOLDER)==0 &&
          StringFind(folder,"..")<0 && StringFind(folder,":")<0 &&
          StringFind(folder,"/")<0 &&
          StringSubstr(folder,StringLen(folder)-1)=="\\");
  }

bool JPWRaizNSymbolValid(const string symbol)
  {
   if(symbol=="" || StringLen(symbol)>128) return(false);
   uchar bytes[];
   const int copied=StringToCharArray(symbol,bytes,0,WHOLE_ARRAY,CP_UTF8);
   return(copied>1 && copied-1<=256);
  }

bool JPWRaizNAccountSymbolKey(JPWAccount &account,const string symbol,
                              const string installation_id,string &key)
  {
   key="";
   string target=""; double scale=0.0;
   const string currency=JPWNormalizeCurrency(account.currency);
   if(account.login<=0 || account.server=="" ||
      installation_id=="" || !JPWRaizNSymbolValid(symbol) ||
      !JPWAccountUnits(currency,target,scale)) return(false);
   const string raw=JPWRaizNFrame(account.server)+
                    JPWRaizNFrame(IntegerToString(account.login))+
                    JPWRaizNFrame(currency)+
                    JPWRaizNFrame(scale==100.0 ? "100" : "1")+
                    JPWRaizNFrame(installation_id)+
                    JPWRaizNFrame(symbol)+
                    JPWRaizNFrame("raiz_n_v1");
   return(JPWRaizNHash(raw,key));
  }

bool JPWRaizNTextHex(const string value,string &hex)
  {
   hex=""; uchar bytes[];
   const int copied=StringToCharArray(value,bytes,0,WHOLE_ARRAY,CP_UTF8);
   if(copied<=0 || copied-1>JPW_RAIZN_MAX_TEXT_BYTES ||
      ArrayResize(bytes,copied-1)!=copied-1) return(false);
   for(int i=0;i<copied-1;i++) hex+=StringFormat("%02x",(int)bytes[i]);
   return(true);
  }

int JPWRaizNHexDigit(const ushort c)
  {
   if(c>='0' && c<='9') return((int)(c-'0'));
   if(c>='a' && c<='f') return((int)(c-'a')+10);
   return(-1);
  }

bool JPWRaizNTextFromHex(const string hex,string &value)
  {
   value=""; const int length=StringLen(hex);
   if(length>2*JPW_RAIZN_MAX_TEXT_BYTES || length%2!=0) return(false);
   uchar bytes[];
   if(ArrayResize(bytes,length/2)!=length/2) return(false);
   for(int i=0;i<length/2;i++)
     {
      const int hi=JPWRaizNHexDigit(StringGetCharacter(hex,2*i));
      const int lo=JPWRaizNHexDigit(StringGetCharacter(hex,2*i+1));
      if(hi<0 || lo<0) return(false);
      bytes[i]=(uchar)(16*hi+lo);
     }
   value=CharArrayToString(bytes,0,length/2,CP_UTF8);
   string canonical="";
   return(JPWRaizNTextHex(value,canonical) && canonical==hex);
  }

bool JPWRaizNUnsigned(const string raw,const long maximum,long &value)
  {
   value=0;
   if(raw=="" || StringLen(raw)>19) return(false);
   for(int i=0;i<StringLen(raw);i++)
     {
      const ushort c=StringGetCharacter(raw,i);
      if(c<'0' || c>'9') return(false);
      const long digit=(long)(c-'0');
      if(value>(maximum-digit)/10) return(false);
      value=value*10+digit;
     }
   return(true);
  }

bool JPWRaizNDouble(const string raw,double &value)
  {
   value=StringToDouble(raw);
   return(raw!="" && MathIsValidNumber(value) &&
          DoubleToString(value,-16)==raw);
  }

bool JPWRaizNScenarioValid(JPWRaizNScenario &record)
  {
   if(record.schema!=1 ||
      record.model_version!=JPW_RAIZN_MODEL_VERSION ||
      !JPWRaizNIsHash(record.account_key) ||
      !JPWRaizNSymbolValid(record.symbol) ||
      !JPWFinitePositive(record.p0) || !JPWFinitePositive(record.atr) ||
      !JPWFinitePositive(record.factor) || record.n_h4<=0 ||
      record.n_h4>1000000 || record.decision_server_time<=0 ||
      record.atr_bar_server_time<=0 || record.confirmed_at_utc<=0 ||
      !JPWRaizNBarClosedBy(record.atr_bar_server_time,
                           record.decision_server_time) ||
      (record.atr_source!="MT5" && record.atr_source!="DECLARED") ||
      record.atr_provenance=="" ||
      (record.factor_status!="DECLARED" &&
       record.factor_status!="ILLUSTRATIVE" &&
       record.factor_status!="SOURCED") ||
      (record.factor_status=="SOURCED" && record.factor_source=="") ||
      (record.declared_side!=-1 && record.declared_side!=0 &&
       record.declared_side!=1) ||
      record.p0_origin=="" || record.atr_variant=="" ||
      record.n_reason=="" || record.factor_reason=="" ||
      (record.parent_id!="" && !JPWRaizNIsHash(record.parent_id)) ||
      (record.parent_id=="" && record.revision_reason!="") ||
      (record.parent_id!="" && record.revision_reason==""))
      return(false);
   string encoded="";
   if(!JPWRaizNTextHex(record.symbol,encoded) ||
      !JPWRaizNTextHex(record.p0_origin,encoded) ||
      !JPWRaizNTextHex(record.atr_provenance,encoded) ||
      !JPWRaizNTextHex(record.atr_variant,encoded) ||
      !JPWRaizNTextHex(record.n_reason,encoded) ||
      !JPWRaizNTextHex(record.factor_source,encoded) ||
      !JPWRaizNTextHex(record.factor_reason,encoded) ||
      !JPWRaizNTextHex(record.revision_reason,encoded)) return(false);
   return(record.scenario_id=="" || JPWRaizNIsHash(record.scenario_id));
  }

// O ID e o SHA-256 do corpo canonico imutavel; o proprio conteudo funciona
// como recibo de identidade. Vinculos e comparacoes usam arquivos separados.
bool JPWRaizNEncodeScenario(JPWRaizNScenario &record,string &content)
  {
   content="";
   if(!JPWRaizNScenarioValid(record)) return(false);
   string symbol="",p0_origin="",provenance="",variant="";
   string n_reason="",f_source="",f_reason="",rev="";
   if(!JPWRaizNTextHex(record.symbol,symbol) ||
      !JPWRaizNTextHex(record.p0_origin,p0_origin) ||
      !JPWRaizNTextHex(record.atr_provenance,provenance) ||
      !JPWRaizNTextHex(record.atr_variant,variant) ||
      !JPWRaizNTextHex(record.n_reason,n_reason) ||
      !JPWRaizNTextHex(record.factor_source,f_source) ||
      !JPWRaizNTextHex(record.factor_reason,f_reason) ||
      !JPWRaizNTextHex(record.revision_reason,rev)) return(false);
   const string body="JPW_RAIZN_SCENARIO|1\nKEY|"+record.account_key+
                     "\nSYMBOL_HEX|"+symbol+
                     "\nP0|"+DoubleToString(record.p0,-16)+
                     "\nP0_ORIGIN_HEX|"+p0_origin+
                     "\nDECISION_SERVER_TIME|"+
                       IntegerToString((long)record.decision_server_time)+
                     "\nATR|"+DoubleToString(record.atr,-16)+
                     "\nATR_SOURCE|"+record.atr_source+
                     "\nATR_PROVENANCE_HEX|"+provenance+
                     "\nATR_VARIANT_HEX|"+variant+
                     "\nATR_BAR_SERVER_TIME|"+
                       IntegerToString((long)record.atr_bar_server_time)+
                     "\nN_H4|"+IntegerToString(record.n_h4)+
                     "\nN_REASON_HEX|"+n_reason+
                     "\nFACTOR|"+DoubleToString(record.factor,-16)+
                     "\nFACTOR_STATUS|"+record.factor_status+
                     "\nFACTOR_SOURCE_HEX|"+f_source+
                     "\nFACTOR_REASON_HEX|"+f_reason+
                     "\nCONFIRMED_AT_UTC|"+
                       IntegerToString((long)record.confirmed_at_utc)+
                     "\nRETROSPECTIVE|"+(record.retrospective ? "1" : "0")+
                     "\nDECLARED_SIDE|"+IntegerToString(record.declared_side)+
                     "\nPARENT|"+record.parent_id+
                     "\nREVISION_REASON_HEX|"+rev+
                     "\nMODEL_VERSION|"+record.model_version+"\n";
   string id="";
   if(!JPWRaizNHash(body,id) ||
      (record.scenario_id!="" && record.scenario_id!=id)) return(false);
   record.scenario_id=id;
   content=body+"SHA256|"+id;
   return(StringLen(content)<=JPW_RAIZN_MAX_BYTES);
  }

JPW_RAIZN_STATE JPWRaizNDecodeScenario(const string content,
                                        const string expected_key,
                                        const string expected_id,
                                        JPWRaizNScenario &record)
  {
   JPWRaizNClearScenario(record);
   const int newline=StringFind(content,"\n");
   if(newline>0 && StringFind(content,"JPW_RAIZN_SCENARIO|")==0 &&
      StringSubstr(content,0,newline)!="JPW_RAIZN_SCENARIO|1")
      return(JPW_RAIZN_INCOMPATIBLE);
   if(StringLen(content)>JPW_RAIZN_MAX_BYTES ||
      !JPWRaizNIsHash(expected_key) || !JPWRaizNIsHash(expected_id))
      return(JPW_RAIZN_INVALID);
   string lines[];
   if(StringSplit(content,'\n',lines)!=24 ||
      lines[0]!="JPW_RAIZN_SCENARIO|1" ||
      lines[1]!="KEY|"+expected_key ||
      StringFind(lines[2],"SYMBOL_HEX|")!=0 ||
      StringFind(lines[3],"P0|")!=0 ||
      StringFind(lines[4],"P0_ORIGIN_HEX|")!=0 ||
      StringFind(lines[5],"DECISION_SERVER_TIME|")!=0 ||
      StringFind(lines[6],"ATR|")!=0 ||
      StringFind(lines[7],"ATR_SOURCE|")!=0 ||
      StringFind(lines[8],"ATR_PROVENANCE_HEX|")!=0 ||
      StringFind(lines[9],"ATR_VARIANT_HEX|")!=0 ||
      StringFind(lines[10],"ATR_BAR_SERVER_TIME|")!=0 ||
      StringFind(lines[11],"N_H4|")!=0 ||
      StringFind(lines[12],"N_REASON_HEX|")!=0 ||
      StringFind(lines[13],"FACTOR|")!=0 ||
      StringFind(lines[14],"FACTOR_STATUS|")!=0 ||
      StringFind(lines[15],"FACTOR_SOURCE_HEX|")!=0 ||
      StringFind(lines[16],"FACTOR_REASON_HEX|")!=0 ||
      StringFind(lines[17],"CONFIRMED_AT_UTC|")!=0 ||
      StringFind(lines[18],"RETROSPECTIVE|")!=0 ||
      StringFind(lines[19],"DECLARED_SIDE|")!=0 ||
      StringFind(lines[20],"PARENT|")!=0 ||
      StringFind(lines[21],"REVISION_REASON_HEX|")!=0 ||
      StringFind(lines[22],"MODEL_VERSION|")!=0 ||
      lines[23]!="SHA256|"+expected_id) return(JPW_RAIZN_INVALID);
   if(lines[22]!="MODEL_VERSION|"+JPW_RAIZN_MODEL_VERSION)
      return(JPW_RAIZN_INCOMPATIBLE);
   string body="";
   for(int i=0;i<23;i++) body+=lines[i]+"\n";
   string id="";
   if(!JPWRaizNHash(body,id) || id!=expected_id)
      return(JPW_RAIZN_INVALID);
   record.schema=1; record.model_version=JPW_RAIZN_MODEL_VERSION;
   record.account_key=expected_key;
   record.scenario_id=expected_id;
   if(!JPWRaizNTextFromHex(StringSubstr(lines[2],11),record.symbol) ||
      !JPWRaizNDouble(StringSubstr(lines[3],3),record.p0) ||
      !JPWRaizNTextFromHex(StringSubstr(lines[4],14),record.p0_origin) ||
      !JPWRaizNDouble(StringSubstr(lines[6],4),record.atr) ||
      !JPWRaizNTextFromHex(StringSubstr(lines[8],19),record.atr_provenance) ||
      !JPWRaizNTextFromHex(StringSubstr(lines[9],16),record.atr_variant) ||
      !JPWRaizNTextFromHex(StringSubstr(lines[12],13),record.n_reason) ||
      !JPWRaizNDouble(StringSubstr(lines[13],7),record.factor) ||
      !JPWRaizNTextFromHex(StringSubstr(lines[15],18),record.factor_source) ||
      !JPWRaizNTextFromHex(StringSubstr(lines[16],18),record.factor_reason) ||
      !JPWRaizNTextFromHex(StringSubstr(lines[21],20),record.revision_reason))
      return(JPW_RAIZN_INVALID);
   record.atr_source=StringSubstr(lines[7],11);
   record.factor_status=StringSubstr(lines[14],14);
   record.parent_id=StringSubstr(lines[20],7);
   if(lines[18]!="RETROSPECTIVE|0" &&
      lines[18]!="RETROSPECTIVE|1") return(JPW_RAIZN_INVALID);
   record.retrospective=(lines[18]=="RETROSPECTIVE|1");
   if(lines[19]!="DECLARED_SIDE|-1" && lines[19]!="DECLARED_SIDE|0" &&
      lines[19]!="DECLARED_SIDE|1") return(JPW_RAIZN_INVALID);
   record.declared_side=(int)StringToInteger(StringSubstr(lines[19],14));
   long numeric=0;
   if(!JPWRaizNUnsigned(StringSubstr(lines[5],21),5000000000,numeric))
      return(JPW_RAIZN_INVALID);
   record.decision_server_time=(datetime)numeric;
   if(!JPWRaizNUnsigned(StringSubstr(lines[10],20),5000000000,numeric))
      return(JPW_RAIZN_INVALID);
   record.atr_bar_server_time=(datetime)numeric;
   if(!JPWRaizNUnsigned(StringSubstr(lines[11],5),1000000,numeric))
      return(JPW_RAIZN_INVALID);
   record.n_h4=(int)numeric;
   if(!JPWRaizNUnsigned(StringSubstr(lines[17],17),5000000000,numeric))
      return(JPW_RAIZN_INVALID);
   record.confirmed_at_utc=(datetime)numeric;
   string canonical="";
   if(!JPWRaizNScenarioValid(record) ||
      !JPWRaizNEncodeScenario(record,canonical) || canonical!=content)
      return(JPW_RAIZN_INVALID);
   return(JPW_RAIZN_VALID);
  }

string JPWRaizNBase(const string folder,const string account_key)
  { return(folder+"rn_"+StringSubstr(account_key,0,JPW_RAIZN_NAME_HEX)); }

string JPWRaizNScenarioBase(const string folder,const string account_key,
                            const string scenario_id)
  { return(JPWRaizNBase(folder,account_key)+"_"+
           StringSubstr(scenario_id,0,JPW_RAIZN_NAME_HEX)+".scn"); }

JPW_RAIZN_STATE JPWRaizNReadText(const string filename,string &content)
  {
   content="";
   const int handle=FileOpen(filename,FILE_READ|FILE_BIN);
   if(handle==INVALID_HANDLE) return(JPW_RAIZN_IO_ERROR);
   const long size=FileSize(handle);
   if(size<=0 || size>JPW_RAIZN_MAX_BYTES)
     { FileClose(handle); return(JPW_RAIZN_INVALID); }
   uchar bytes[];
   if(ArrayResize(bytes,(int)size)!=(int)size ||
      FileReadArray(handle,bytes,0,(int)size)!=(uint)size)
     { FileClose(handle); return(JPW_RAIZN_IO_ERROR); }
   FileClose(handle);
   for(int i=0;i<(int)size;i++)
      if((bytes[i]<32 || bytes[i]>126) && bytes[i]!=10)
         return(JPW_RAIZN_INVALID);
   content=CharArrayToString(bytes,0,(int)size,CP_UTF8);
   return(StringLen(content)==(int)size ? JPW_RAIZN_VALID :
          JPW_RAIZN_INVALID);
  }

bool JPWRaizNWriteText(const string filename,const string content)
  {
   uchar bytes[];
   const int copied=StringToCharArray(content,bytes,0,WHOLE_ARRAY,CP_UTF8);
   if(copied<=1 || copied-1>JPW_RAIZN_MAX_BYTES ||
      ArrayResize(bytes,copied-1)!=copied-1) return(false);
   const int handle=FileOpen(filename,FILE_WRITE|FILE_BIN);
   if(handle==INVALID_HANDLE) return(false);
   const uint written=FileWriteArray(handle,bytes,0,ArraySize(bytes));
   FileFlush(handle);
   FileClose(handle);
   return(written==(uint)ArraySize(bytes));
  }

// Escreve temporario, le de volta e move sob lock. O destino anterior fica
// no outro slot ate a nova geracao ser confirmada por leitura.
bool JPWRaizNWriteVerified(const string base,const string destination,
                           const string content)
  {
   const string temp=base+"."+IntegerToString((long)ChartID())+"."+
                     IntegerToString((long)GetTickCount64())+".tmp";
   if(FileIsExist(temp)) return(false);
   if(!JPWRaizNWriteText(temp,content))
     { FileDelete(temp); return(false); }
   string readback="";
   if(JPWRaizNReadText(temp,readback)!=JPW_RAIZN_VALID ||
      readback!=content ||
      !FileMove(temp,0,destination,FILE_REWRITE))
     { FileDelete(temp); return(false); }
   readback="";
   return(JPWRaizNReadText(destination,readback)==JPW_RAIZN_VALID &&
          readback==content);
  }

bool JPWRaizNEncodePointer(const string key,const string scenario_id,
                           const long generation,string &content)
  {
   content="";
   if(!JPWRaizNIsHash(key) || !JPWRaizNIsHash(scenario_id) ||
      generation<1 || generation>1000000000) return(false);
   const string body="JPW_RAIZN_ACTIVE|1\nKEY|"+key+
                     "\nID|"+scenario_id+
                     "\nGEN|"+IntegerToString(generation)+"\n";
   string checksum="";
   if(!JPWRaizNHash(body,checksum)) return(false);
   content=body+"SHA256|"+checksum;
   return(true);
  }

JPW_RAIZN_STATE JPWRaizNDecodePointer(const string content,
                                       const string key,string &scenario_id,
                                       long &generation)
  {
   scenario_id=""; generation=0;
   const int newline=StringFind(content,"\n");
   if(newline>0 && StringFind(content,"JPW_RAIZN_ACTIVE|")==0 &&
      StringSubstr(content,0,newline)!="JPW_RAIZN_ACTIVE|1")
      return(JPW_RAIZN_INCOMPATIBLE);
   string lines[];
   if(StringSplit(content,'\n',lines)!=5 ||
      lines[0]!="JPW_RAIZN_ACTIVE|1" || lines[1]!="KEY|"+key ||
      StringFind(lines[2],"ID|")!=0 ||
      StringFind(lines[3],"GEN|")!=0 ||
      StringFind(lines[4],"SHA256|")!=0)
      return(JPW_RAIZN_INVALID);
   const string body=lines[0]+"\n"+lines[1]+"\n"+lines[2]+"\n"+
                     lines[3]+"\n";
   string checksum="";
   if(!JPWRaizNHash(body,checksum) ||
      lines[4]!="SHA256|"+checksum) return(JPW_RAIZN_INVALID);
   scenario_id=StringSubstr(lines[2],3);
   if(!JPWRaizNIsHash(scenario_id) ||
      !JPWRaizNUnsigned(StringSubstr(lines[3],4),1000000000,generation) ||
      generation<=0) return(JPW_RAIZN_INVALID);
   string canonical="";
   return(JPWRaizNEncodePointer(key,scenario_id,generation,canonical) &&
          canonical==content ? JPW_RAIZN_VALID : JPW_RAIZN_INVALID);
  }

// Chamador detem o lock. Versao futura em qualquer slot bloqueia escrita.
JPW_RAIZN_STATE JPWRaizNLoadPointer(const string base,const string key,
                                     string &scenario_id,long &generation,
                                     int &active_slot)
  {
   scenario_id=""; generation=0; active_slot=-1;
   bool exists=false,io_error=false,incompatible=false;
   for(int slot=0;slot<2;slot++)
     {
      const string filename=base+".active"+(slot==0 ? ".a" : ".b");
      if(!FileIsExist(filename)) continue;
      exists=true;
      string content="";
      const JPW_RAIZN_STATE read=JPWRaizNReadText(filename,content);
      if(read==JPW_RAIZN_IO_ERROR) { io_error=true; continue; }
      if(read!=JPW_RAIZN_VALID) continue;
      string found_id=""; long found_generation=0;
      const JPW_RAIZN_STATE decoded=
         JPWRaizNDecodePointer(content,key,found_id,found_generation);
      if(decoded==JPW_RAIZN_INCOMPATIBLE)
        { incompatible=true; continue; }
      if(decoded!=JPW_RAIZN_VALID) continue;
      if(found_generation==generation && active_slot>=0 &&
         found_id!=scenario_id) return(JPW_RAIZN_INVALID);
      if(found_generation>generation)
        {
         if(active_slot>=0 && found_generation!=generation+1)
            return(JPW_RAIZN_INVALID);
         scenario_id=found_id; generation=found_generation;
         active_slot=slot;
        }
      else if(active_slot>=0 && found_generation<generation &&
              generation!=found_generation+1)
         return(JPW_RAIZN_INVALID);
     }
   if(incompatible) return(JPW_RAIZN_INCOMPATIBLE);
   if(io_error) return(JPW_RAIZN_IO_ERROR);
   if(active_slot>=0) return(JPW_RAIZN_VALID);
   return(exists ? JPW_RAIZN_INVALID : JPW_RAIZN_ABSENT);
  }

JPW_RAIZN_STATE JPWRaizNLoadScenario(const string folder,const string key,
                                      const string scenario_id,
                                      JPWRaizNScenario &record)
  {
   JPWRaizNClearScenario(record);
   if(!JPWRaizNIsHash(scenario_id)) return(JPW_RAIZN_INVALID);
   const string base=JPWRaizNScenarioBase(folder,key,scenario_id);
   bool exists=false,io_error=false,incompatible=false,valid=false;
   string first_content="";
   for(int slot=0;slot<2;slot++)
     {
      const string filename=base+(slot==0 ? ".a" : ".b");
      if(!FileIsExist(filename)) continue;
      exists=true;
      string content="";
      const JPW_RAIZN_STATE read=JPWRaizNReadText(filename,content);
      if(read==JPW_RAIZN_IO_ERROR) { io_error=true; continue; }
      if(read!=JPW_RAIZN_VALID) continue;
      JPWRaizNScenario parsed;
      const JPW_RAIZN_STATE decoded=
         JPWRaizNDecodeScenario(content,key,scenario_id,parsed);
      if(decoded==JPW_RAIZN_INCOMPATIBLE)
        { incompatible=true; continue; }
      if(decoded!=JPW_RAIZN_VALID) continue;
      if(valid && content!=first_content) return(JPW_RAIZN_INVALID);
      record=parsed; first_content=content; valid=true;
     }
   if(incompatible) { JPWRaizNClearScenario(record); return(JPW_RAIZN_INCOMPATIBLE); }
   if(io_error) { JPWRaizNClearScenario(record); return(JPW_RAIZN_IO_ERROR); }
   if(valid) return(JPW_RAIZN_VALID);
   return(exists ? JPW_RAIZN_INVALID : JPW_RAIZN_ABSENT);
  }

// Cenario imutavel redundante. Um slot valido recupera um slot truncado;
// ambos invalidos nao autorizam sobrescrita silenciosa do ID antigo.
JPW_RAIZN_STATE JPWRaizNWriteScenario(const string folder,const string key,
                                       JPWRaizNScenario &record)
  {
   string content="";
   if(!JPWRaizNEncodeScenario(record,content)) return(JPW_RAIZN_INVALID);
   JPWRaizNScenario previous;
   const JPW_RAIZN_STATE prior=
      JPWRaizNLoadScenario(folder,key,record.scenario_id,previous);
   const string base=JPWRaizNScenarioBase(folder,key,record.scenario_id);
   if(prior==JPW_RAIZN_VALID)
     {
      for(int slot=0;slot<2;slot++)
        {
         const string file=base+(slot==0 ? ".a" : ".b");
         string saved="";
         if(JPWRaizNReadText(file,saved)==JPW_RAIZN_VALID &&
            saved==content) continue;
         if(!JPWRaizNWriteVerified(base,file,content))
            return(JPW_RAIZN_IO_ERROR);
        }
      return(JPW_RAIZN_VALID);
     }
   if(prior!=JPW_RAIZN_ABSENT) return(prior);
   if(!JPWRaizNWriteVerified(base,base+".a",content) ||
      !JPWRaizNWriteVerified(base,base+".b",content))
      return(JPW_RAIZN_IO_ERROR);
   const JPW_RAIZN_STATE checked=
      JPWRaizNLoadScenario(folder,key,record.scenario_id,previous);
   return(checked==JPW_RAIZN_VALID ? JPW_RAIZN_VALID : checked);
  }

string JPWRaizNBindingBase(const string folder,const string key,
                            const string scenario_id)
  { return(JPWRaizNBase(folder,key)+"_"+
           StringSubstr(scenario_id,0,JPW_RAIZN_NAME_HEX)+".bind"); }

string JPWRaizNComparisonBase(const string folder,const string key,
                               const string scenario_id,const string receipt_id)
  { return(JPWRaizNBase(folder,key)+"_"+
           StringSubstr(scenario_id,0,JPW_RAIZN_NAME_HEX)+"_"+
           StringSubstr(receipt_id,0,JPW_RAIZN_NAME_HEX)+".cmp"); }

bool JPWRaizNEncodeBinding(const string key,JPWRaizNBinding &binding,
                           const long generation,string &content)
  {
   content="";
   if(!JPWRaizNIsHash(key) || !JPWRaizNIsHash(binding.scenario_id) ||
      binding.identifier<=0 || binding.origin_ticket<=0 ||
      (binding.direction!=POSITION_TYPE_BUY &&
       binding.direction!=POSITION_TYPE_SELL) ||
      generation<1 || generation>1000000000) return(false);
   const string body="JPW_RAIZN_BINDING|1\nKEY|"+key+
                     "\nSCENARIO|"+binding.scenario_id+
                     "\nIDENTIFIER|"+IntegerToString(binding.identifier)+
                     "\nORIGIN_TICKET|"+IntegerToString(binding.origin_ticket)+
                     "\nDIRECTION|"+IntegerToString(binding.direction)+
                     "\nGEN|"+IntegerToString(generation)+"\n";
   string checksum="";
   if(!JPWRaizNHash(body,checksum)) return(false);
   content=body+"SHA256|"+checksum;
   return(true);
  }

JPW_RAIZN_STATE JPWRaizNDecodeBinding(const string content,const string key,
                                       const string scenario_id,
                                       JPWRaizNBinding &binding,
                                       long &generation)
  {
   JPWRaizNClearBinding(binding); generation=0;
   const int newline=StringFind(content,"\n");
   if(newline>0 && StringFind(content,"JPW_RAIZN_BINDING|")==0 &&
      StringSubstr(content,0,newline)!="JPW_RAIZN_BINDING|1")
      return(JPW_RAIZN_INCOMPATIBLE);
   string lines[];
   if(StringSplit(content,'\n',lines)!=8 ||
      lines[0]!="JPW_RAIZN_BINDING|1" || lines[1]!="KEY|"+key ||
      lines[2]!="SCENARIO|"+scenario_id ||
      StringFind(lines[3],"IDENTIFIER|")!=0 ||
      StringFind(lines[4],"ORIGIN_TICKET|")!=0 ||
      StringFind(lines[5],"DIRECTION|")!=0 ||
      StringFind(lines[6],"GEN|")!=0 ||
      StringFind(lines[7],"SHA256|")!=0) return(JPW_RAIZN_INVALID);
   string body="";
   for(int i=0;i<7;i++) body+=lines[i]+"\n";
   string checksum="";
   if(!JPWRaizNHash(body,checksum) ||
      lines[7]!="SHA256|"+checksum) return(JPW_RAIZN_INVALID);
   binding.scenario_id=scenario_id;
   if(!JPWRaizNUnsigned(StringSubstr(lines[3],11),LONG_MAX,
                         binding.identifier) ||
      !JPWRaizNUnsigned(StringSubstr(lines[4],14),LONG_MAX,
                         binding.origin_ticket) ||
      !JPWRaizNUnsigned(StringSubstr(lines[6],4),1000000000,
                         generation) ||
      binding.identifier<=0 || binding.origin_ticket<=0 ||
      generation<=0 ||
      (lines[5]!="DIRECTION|0" && lines[5]!="DIRECTION|1"))
      return(JPW_RAIZN_INVALID);
   binding.direction=(long)StringToInteger(StringSubstr(lines[5],10));
   string canonical="";
   return(JPWRaizNEncodeBinding(key,binding,generation,canonical) &&
          canonical==content ? JPW_RAIZN_VALID : JPW_RAIZN_INVALID);
  }

// Chamador detem o lock exclusivo do simbolo. Um slot valido recupera
// truncamento do outro; versao futura ou geracoes incoerentes bloqueiam.
JPW_RAIZN_STATE JPWRaizNLoadBinding(const string folder,const string key,
                                     const string scenario_id,
                                     JPWRaizNBinding &binding,
                                     long &generation,int &active_slot)
  {
   JPWRaizNClearBinding(binding); generation=0; active_slot=-1;
   const string base=JPWRaizNBindingBase(folder,key,scenario_id);
   bool exists=false,io_error=false,incompatible=false;
   for(int slot=0;slot<2;slot++)
     {
      const string file=base+(slot==0 ? ".a" : ".b");
      if(!FileIsExist(file)) continue;
      exists=true;
      string content="";
      const JPW_RAIZN_STATE read=JPWRaizNReadText(file,content);
      if(read==JPW_RAIZN_IO_ERROR) { io_error=true; continue; }
      if(read!=JPW_RAIZN_VALID) continue;
      JPWRaizNBinding parsed; long found_generation=0;
      const JPW_RAIZN_STATE decoded=
         JPWRaizNDecodeBinding(content,key,scenario_id,parsed,found_generation);
      if(decoded==JPW_RAIZN_INCOMPATIBLE)
        { incompatible=true; continue; }
      if(decoded!=JPW_RAIZN_VALID) continue;
      if(active_slot>=0 && found_generation==generation &&
         (parsed.identifier!=binding.identifier ||
          parsed.origin_ticket!=binding.origin_ticket ||
          parsed.direction!=binding.direction)) return(JPW_RAIZN_INVALID);
      if(found_generation>generation)
        {
         if(active_slot>=0 && found_generation!=generation+1)
            return(JPW_RAIZN_INVALID);
         binding=parsed; generation=found_generation; active_slot=slot;
        }
      else if(active_slot>=0 && found_generation<generation &&
              generation!=found_generation+1)
         return(JPW_RAIZN_INVALID);
     }
   if(incompatible) { JPWRaizNClearBinding(binding); return(JPW_RAIZN_INCOMPATIBLE); }
   if(io_error) { JPWRaizNClearBinding(binding); return(JPW_RAIZN_IO_ERROR); }
   if(active_slot>=0) return(JPW_RAIZN_VALID);
   return(exists ? JPW_RAIZN_INVALID : JPW_RAIZN_ABSENT);
  }

// Leitura nao cria arquivos. A ausencia de lock com slots presentes e erro;
// leitura concorrente de outra instancia devolve BUSY sem esperar.
JPW_RAIZN_STATE JPWRaizNReadActive(JPWAccount &account,const string symbol,
                                    const string installation_id,
                                    const string folder,
                                    JPWRaizNScenario &scenario,
                                    JPWRaizNBinding &binding)
  {
   JPWRaizNClearScenario(scenario); JPWRaizNClearBinding(binding);
   string key="";
   if(!JPWRaizNAccountSymbolKey(account,symbol,installation_id,key))
      return(JPW_RAIZN_ACCOUNT_UNAVAILABLE);
   if(!JPWRaizNFolderValid(folder)) return(JPW_RAIZN_INVALID);
   const string base=JPWRaizNBase(folder,key);
   const int lock=FileOpen(base+".lock",FILE_READ|FILE_BIN);
   if(lock==INVALID_HANDLE)
     {
      if(FileIsExist(base+".lock")) return(JPW_RAIZN_BUSY);
      if(FileIsExist(base+".active.a") || FileIsExist(base+".active.b"))
         return(JPW_RAIZN_IO_ERROR);
      return(JPW_RAIZN_ABSENT);
     }
   string id=""; long generation=0; int active=-1;
   JPW_RAIZN_STATE state=JPWRaizNLoadPointer(base,key,id,generation,active);
   if(state==JPW_RAIZN_VALID)
     {
      state=JPWRaizNLoadScenario(folder,key,id,scenario);
      if(state==JPW_RAIZN_ABSENT) state=JPW_RAIZN_INVALID;
     }
   if(state==JPW_RAIZN_VALID)
     {
      long binding_generation=0; int binding_slot=-1;
      const JPW_RAIZN_STATE bound=JPWRaizNLoadBinding(folder,key,id,binding,
                                   binding_generation,binding_slot);
      if(bound!=JPW_RAIZN_VALID) JPWRaizNClearBinding(binding);
      binding.state=bound;
     }
   FileClose(lock);
   if(state!=JPW_RAIZN_VALID)
     { JPWRaizNClearScenario(scenario); JPWRaizNClearBinding(binding); }
   return(state);
  }

JPW_RAIZN_STATE JPWRaizNConfirm(JPWAccount &account,const string symbol,
                                 const string installation_id,
                                 const string folder,
                                 JPWRaizNScenario &draft,
                                 const string expected_active_id,
                                 JPWRaizNScenario &confirmed)
  {
   JPWRaizNClearScenario(confirmed);
   string key="";
   if(!JPWRaizNAccountSymbolKey(account,symbol,installation_id,key))
      return(JPW_RAIZN_ACCOUNT_UNAVAILABLE);
   if(!JPWRaizNFolderValid(folder) ||
      (expected_active_id!="" && !JPWRaizNIsHash(expected_active_id)) ||
      draft.symbol!=symbol || draft.account_key!=key ||
      draft.parent_id!=expected_active_id ||
      (expected_active_id=="" && draft.revision_reason!="") ||
      (expected_active_id!="" && draft.revision_reason==""))
      return(JPW_RAIZN_INVALID);
   string scenario_content="";
   if(!JPWRaizNEncodeScenario(draft,scenario_content))
      return(JPW_RAIZN_INVALID);
   if(!FolderCreate(StringSubstr(folder,0,StringLen(folder)-1)))
      return(JPW_RAIZN_IO_ERROR);
   const string base=JPWRaizNBase(folder,key);
   const int lock=FileOpen(base+".lock",FILE_READ|FILE_WRITE|FILE_BIN);
   if(lock==INVALID_HANDLE) return(JPW_RAIZN_BUSY);
   string current_id=""; long generation=0; int active=-1;
   JPW_RAIZN_STATE state=JPWRaizNLoadPointer(base,key,current_id,
                                               generation,active);
   if(state!=JPW_RAIZN_VALID && state!=JPW_RAIZN_ABSENT)
     { FileClose(lock); return(state); }
   if((state==JPW_RAIZN_ABSENT && expected_active_id!="") ||
      (state==JPW_RAIZN_VALID && current_id!=expected_active_id))
     { FileClose(lock); return(JPW_RAIZN_CONFLICT); }
   if(state==JPW_RAIZN_VALID)
     {
      JPWRaizNScenario prior;
      const JPW_RAIZN_STATE checked=
         JPWRaizNLoadScenario(folder,key,current_id,prior);
      if(checked!=JPW_RAIZN_VALID)
        { FileClose(lock); return(checked==JPW_RAIZN_ABSENT ?
                                 JPW_RAIZN_INVALID : checked); }
     }
   if(generation>=1000000000)
     { FileClose(lock); return(JPW_RAIZN_INVALID); }
   state=JPWRaizNWriteScenario(folder,key,draft);
   if(state!=JPW_RAIZN_VALID)
     { FileClose(lock); return(state); }
   string pointer="";
   if(!JPWRaizNEncodePointer(key,draft.scenario_id,generation+1,pointer))
     { FileClose(lock); return(JPW_RAIZN_INVALID); }
   const int target=(active==0 ? 1 : 0);
   const string destination=base+".active"+(target==0 ? ".a" : ".b");
   if(!JPWRaizNWriteVerified(base,destination,pointer))
     { FileClose(lock); return(JPW_RAIZN_IO_ERROR); }
   string checked_id=""; long checked_generation=0; int checked_slot=-1;
   state=JPWRaizNLoadPointer(base,key,checked_id,checked_generation,
                              checked_slot);
   if(state!=JPW_RAIZN_VALID || checked_id!=draft.scenario_id ||
      checked_generation!=generation+1 || checked_slot!=target)
     { FileClose(lock); return(JPW_RAIZN_IO_ERROR); }
   state=JPWRaizNLoadScenario(folder,key,checked_id,confirmed);
   FileClose(lock);
   if(state!=JPW_RAIZN_VALID) JPWRaizNClearScenario(confirmed);
   return(state);
  }

JPW_RAIZN_STATE JPWRaizNBind(JPWAccount &account,const string symbol,
                              const string installation_id,
                              const string folder,const string scenario_id,
                              const long identifier,const long ticket,
                              const long direction,JPWRaizNBinding &confirmed)
  {
   JPWRaizNClearBinding(confirmed);
   string key="";
   if(!JPWRaizNAccountSymbolKey(account,symbol,installation_id,key))
      return(JPW_RAIZN_ACCOUNT_UNAVAILABLE);
   if(!JPWRaizNFolderValid(folder) || !JPWRaizNIsHash(scenario_id) ||
      identifier<=0 || ticket<=0 ||
      (direction!=POSITION_TYPE_BUY && direction!=POSITION_TYPE_SELL))
      return(JPW_RAIZN_INVALID);
   const string base=JPWRaizNBase(folder,key);
   const int lock=FileOpen(base+".lock",FILE_READ|FILE_WRITE|FILE_BIN);
   if(lock==INVALID_HANDLE) return(JPW_RAIZN_BUSY);
   string active_id=""; long pointer_generation=0; int pointer_slot=-1;
   JPW_RAIZN_STATE state=JPWRaizNLoadPointer(base,key,active_id,
                                               pointer_generation,pointer_slot);
   if(state!=JPW_RAIZN_VALID || active_id!=scenario_id)
     { FileClose(lock); return(state==JPW_RAIZN_VALID ?
                               JPW_RAIZN_CONFLICT : state); }
   JPWRaizNScenario scenario;
   state=JPWRaizNLoadScenario(folder,key,scenario_id,scenario);
   if(state!=JPW_RAIZN_VALID || scenario.symbol!=symbol ||
      (scenario.declared_side!=1 && scenario.declared_side!=-1) ||
      (scenario.declared_side==1 && direction!=POSITION_TYPE_BUY) ||
      (scenario.declared_side==-1 && direction!=POSITION_TYPE_SELL))
     { FileClose(lock); return(state==JPW_RAIZN_VALID ?
                               JPW_RAIZN_INVALID : state); }
   JPWRaizNBinding existing; long generation=0; int active=-1;
   state=JPWRaizNLoadBinding(folder,key,scenario_id,existing,
                              generation,active);
   if(state==JPW_RAIZN_VALID)
     {
      if(existing.identifier==identifier && existing.direction==direction &&
         existing.origin_ticket==ticket)
        {
         string content="";
         if(!JPWRaizNEncodeBinding(key,existing,generation,content))
           { FileClose(lock); return(JPW_RAIZN_INVALID); }
         const string repair_base=JPWRaizNBindingBase(folder,key,scenario_id);
         for(int slot=0;slot<2;slot++)
           {
            const string file=repair_base+(slot==0 ? ".a" : ".b");
            string saved="";
            if(JPWRaizNReadText(file,saved)==JPW_RAIZN_VALID &&
               saved==content) continue;
            if(!JPWRaizNWriteVerified(repair_base,file,content))
              { FileClose(lock); return(JPW_RAIZN_IO_ERROR); }
           }
         confirmed=existing; confirmed.state=JPW_RAIZN_VALID;
         FileClose(lock);
         return(JPW_RAIZN_VALID);
        }
      FileClose(lock);
      return(JPW_RAIZN_CONFLICT);
     }
   if(state!=JPW_RAIZN_ABSENT)
     { FileClose(lock); return(state); }
   JPWRaizNBinding next;
   next.scenario_id=scenario_id; next.identifier=identifier;
   next.origin_ticket=ticket; next.direction=direction;
   string content="";
   if(!JPWRaizNEncodeBinding(key,next,1,content))
     { FileClose(lock); return(JPW_RAIZN_INVALID); }
   const string binding_base=JPWRaizNBindingBase(folder,key,scenario_id);
   if(!JPWRaizNWriteVerified(binding_base,binding_base+".a",content) ||
      !JPWRaizNWriteVerified(binding_base,binding_base+".b",content))
     { FileClose(lock); return(JPW_RAIZN_IO_ERROR); }
   long checked_generation=0; int checked_slot=-1;
   state=JPWRaizNLoadBinding(folder,key,scenario_id,confirmed,
                              checked_generation,checked_slot);
   FileClose(lock);
   if(state!=JPW_RAIZN_VALID) JPWRaizNClearBinding(confirmed);
   else confirmed.state=JPW_RAIZN_VALID;
   return(state);
  }

// Recibo imutavel de uma comparacao solicitada pelo operador. Nunca e
// acionado pelo timer; nao altera cenario, vinculo, SL ou posicao.
JPW_RAIZN_STATE JPWRaizNRecordComparison(
   JPWAccount &account,const string symbol,const string installation_id,
   const string folder,const string scenario_id,const long identifier,
   const double sl,const datetime observed_at_utc,string &receipt_id)
  {
   receipt_id="";
   string key="";
   if(!JPWRaizNAccountSymbolKey(account,symbol,installation_id,key))
      return(JPW_RAIZN_ACCOUNT_UNAVAILABLE);
   if(!JPWRaizNFolderValid(folder) || !JPWRaizNIsHash(scenario_id) ||
      identifier<=0 || !JPWFinitePositive(sl) || observed_at_utc<=0)
      return(JPW_RAIZN_INVALID);
   const string base=JPWRaizNBase(folder,key);
   const int lock=FileOpen(base+".lock",FILE_READ|FILE_WRITE|FILE_BIN);
   if(lock==INVALID_HANDLE) return(JPW_RAIZN_BUSY);
   string active_id=""; long pointer_generation=0; int pointer_slot=-1;
   JPW_RAIZN_STATE state=JPWRaizNLoadPointer(base,key,active_id,
                                               pointer_generation,pointer_slot);
   if(state!=JPW_RAIZN_VALID || active_id!=scenario_id)
     { FileClose(lock); return(state==JPW_RAIZN_VALID ?
                               JPW_RAIZN_CONFLICT : state); }
   JPWRaizNScenario scenario;
   state=JPWRaizNLoadScenario(folder,key,scenario_id,scenario);
   if(state!=JPW_RAIZN_VALID)
     { FileClose(lock); return(state); }
   JPWRaizNBinding binding; long bind_generation=0; int bind_slot=-1;
   state=JPWRaizNLoadBinding(folder,key,scenario_id,binding,
                              bind_generation,bind_slot);
   if(state!=JPW_RAIZN_VALID || binding.identifier!=identifier)
     { FileClose(lock); return(state==JPW_RAIZN_VALID ?
                               JPW_RAIZN_CONFLICT : state); }
   double dprice=0.0,dpct=0.0,slprice=0.0,slpct=0.0;
   double gapprice=0.0,gappct=0.0;
   const JPW_RAIZN_SIDE side=(binding.direction==POSITION_TYPE_BUY ?
                              JPW_RAIZN_SIDE_BUY : JPW_RAIZN_SIDE_SELL);
   if(JPWRaizNCalculate(scenario.p0,scenario.atr,scenario.n_h4,
                        scenario.factor,dprice,dpct)!=JPW_RAIZN_OK ||
      JPWRaizNCompareSL(side,scenario.p0,sl,dprice,
                        slprice,slpct,gapprice,gappct)!=JPW_RAIZN_SL_OK)
     { FileClose(lock); return(JPW_RAIZN_INVALID); }
   const string body="JPW_RAIZN_COMPARISON|1\nKEY|"+key+
      "\nSCENARIO|"+scenario_id+
      "\nIDENTIFIER|"+IntegerToString(identifier)+
      "\nDIRECTION|"+IntegerToString(binding.direction)+
      "\nSL|"+DoubleToString(sl,-16)+
      "\nRAIZ_PRICE|"+DoubleToString(dprice,-16)+
      "\nRAIZ_PERCENT|"+DoubleToString(dpct,-16)+
      "\nP0_TO_SL_PRICE|"+DoubleToString(slprice,-16)+
      "\nP0_TO_SL_PERCENT|"+DoubleToString(slpct,-16)+
      "\nGAP_PRICE|"+DoubleToString(gapprice,-16)+
      "\nGAP_PERCENT|"+DoubleToString(gappct,-16)+
      "\nOBSERVED_UTC|"+IntegerToString((long)observed_at_utc)+"\n";
   string checksum="";
   if(!JPWRaizNHash(body,checksum))
     { FileClose(lock); return(JPW_RAIZN_IO_ERROR); }
   const string content=body+"SHA256|"+checksum;
   const string receipt_base=JPWRaizNComparisonBase(folder,key,scenario_id,
                                                     checksum);
   bool exists=false,matching=false;
   for(int slot=0;slot<2;slot++)
     {
      const string file=receipt_base+(slot==0 ? ".a" : ".b");
      if(!FileIsExist(file)) continue;
      exists=true;
      string saved="";
      if(JPWRaizNReadText(file,saved)==JPW_RAIZN_VALID && saved==content)
         matching=true;
     }
   if(exists)
     {
      if(!matching)
        { FileClose(lock); return(JPW_RAIZN_INVALID); }
      for(int slot=0;slot<2;slot++)
        {
         const string file=receipt_base+(slot==0 ? ".a" : ".b");
         string saved="";
         if(JPWRaizNReadText(file,saved)==JPW_RAIZN_VALID &&
            saved==content) continue;
         if(!JPWRaizNWriteVerified(receipt_base,file,content))
           { FileClose(lock); return(JPW_RAIZN_IO_ERROR); }
        }
      FileClose(lock); receipt_id=checksum; return(JPW_RAIZN_VALID);
     }
   if(!JPWRaizNWriteVerified(receipt_base,receipt_base+".a",content) ||
      !JPWRaizNWriteVerified(receipt_base,receipt_base+".b",content))
     { FileClose(lock); return(JPW_RAIZN_IO_ERROR); }
   string a="",b="";
   const bool persisted=
      JPWRaizNReadText(receipt_base+".a",a)==JPW_RAIZN_VALID &&
      JPWRaizNReadText(receipt_base+".b",b)==JPW_RAIZN_VALID &&
      a==content && b==content;
   FileClose(lock);
   if(!persisted) return(JPW_RAIZN_IO_ERROR);
   receipt_id=checksum;
   return(JPW_RAIZN_VALID);
  }

#endif
