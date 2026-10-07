#ifndef JPW_ALAVANCAGEM_MDD_MQH
#define JPW_ALAVANCAGEM_MDD_MQH
#include <JPWealth/JPW_Alavancagem_Core.mqh>

// Registro local de um maximo observado, nunca um MDD de pico a vale.
// Os nomes de arquivo so contem hashes; nenhuma identidade real e registrada.
#define JPW_MDD_FOLDER "JPWealth\\Alavancagem\\"
#define JPW_MDD_METRIC_ID "max_observed_balance_dd_pct"
#define JPW_MDD_TIME_BASIS "local_pc_utc"
#define JPW_MDD_MAX_BYTES 2048

enum JPW_MDD_STATE
  {
   JPW_MDD_VALID=0,
   JPW_MDD_ABSENT,
   JPW_MDD_INVALID,
   JPW_MDD_INCOMPATIBLE,
   JPW_MDD_IO_ERROR,
   JPW_MDD_BUSY,
   JPW_MDD_ACCOUNT_UNAVAILABLE
  };

struct JPWMDDRecord
  {
   int schema;
   string metric_id;
   string account_key;
   string currency;
   double account_scale;
   datetime observation_started_at;
   double max_percent;
   double balance_at_max;
   double equity_at_max;
   datetime observed_at_utc;
   string time_basis;
   string producer_version;
   long generation;
   string checksum;
  };

void JPWMDDClear(JPWMDDRecord &record)
  {
   record.schema=0;
   record.metric_id="";
   record.account_key="";
   record.currency="";
   record.account_scale=0.0;
   record.observation_started_at=0;
   record.max_percent=0.0;
   record.balance_at_max=0.0;
   record.equity_at_max=0.0;
   record.observed_at_utc=0;
   record.time_basis="";
   record.producer_version="";
   record.generation=0;
   record.checksum="";
  }

bool JPWMDDHash(const string value,string &hex)
  {
   hex="";
   uchar source[];
   uchar key[];
   uchar digest[];
   const int copied=StringToCharArray(value,source,0,WHOLE_ARRAY,CP_UTF8);
   if(copied<=0 || ArrayResize(source,copied-1)!=copied-1) return(false);
   if(CryptEncode(CRYPT_HASH_SHA256,source,key,digest)!=32) return(false);
   for(int i=0;i<32;i++) hex+=StringFormat("%02x",(int)digest[i]);
   return(StringLen(hex)==64);
  }

bool JPWMDDIsHash(const string value)
  {
   if(StringLen(value)!=64) return(false);
   for(int i=0;i<64;i++)
     {
      const ushort c=StringGetCharacter(value,i);
      if(!((c>='0' && c<='9') || (c>='a' && c<='f'))) return(false);
     }
   return(true);
  }

string JPWMDDFrame(const string value)
  {
   return(IntegerToString(StringLen(value))+":"+value);
  }

bool JPWMDDAccountKey(JPWAccount &account,string &key,
                      string &currency,double &scale)
  {
   key="";
   currency=JPWNormalizeCurrency(account.currency);
   string target="";
   scale=0.0;
   if(account.login<=0 || account.server=="" ||
      !JPWAccountUnits(currency,target,scale)) return(false);
   const string raw=JPWMDDFrame(account.server)+
                    JPWMDDFrame(IntegerToString(account.login))+
                    JPWMDDFrame(currency)+
                    JPWMDDFrame(scale==100.0 ? "100" : "1")+
                    JPWMDDFrame(JPW_MDD_METRIC_ID);
   return(JPWMDDHash(raw,key));
  }

bool JPWMDDVersionValid(const string version)
  {
   const int size=StringLen(version);
   if(size<1 || size>40) return(false);
   for(int i=0;i<size;i++)
     {
      const ushort c=StringGetCharacter(version,i);
      if(!((c>='0' && c<='9') || (c>='A' && c<='Z') ||
           (c>='a' && c<='z') || c=='.' || c=='-' || c=='_')) return(false);
     }
   return(true);
  }

bool JPWMDDRecordValid(JPWMDDRecord &record)
  {
   if(record.schema!=1 || record.metric_id!=JPW_MDD_METRIC_ID ||
      !JPWMDDIsHash(record.account_key) ||
      record.currency!=JPWNormalizeCurrency(record.currency) ||
      record.time_basis!=JPW_MDD_TIME_BASIS ||
      !JPWMDDVersionValid(record.producer_version) ||
      record.generation<1 || record.generation>1000000000 ||
      record.observation_started_at<=0 ||
      record.observed_at_utc<record.observation_started_at ||
      !MathIsValidNumber(record.max_percent) ||
      record.max_percent<0.0) return(false);
   string target="";
   double scale=0.0;
   if(!JPWAccountUnits(record.currency,target,scale) ||
      record.account_scale!=scale) return(false);
   double derived=0.0;
   if(!JPWBalanceDDPercent(record.balance_at_max,
                           record.equity_at_max,derived)) return(false);
   const double tolerance=1e-9*MathMax(MathAbs(derived),
                                       MathAbs(record.max_percent));
   return(MathAbs(derived-record.max_percent)<=tolerance);
  }

bool JPWMDDParseUnsigned(const string raw,const long maximum,long &value)
  {
   value=0;
   if(raw=="" || StringLen(raw)>12) return(false);
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

bool JPWMDDParseDouble(const string raw,double &value)
  {
   value=StringToDouble(raw);
   return(raw!="" && MathIsValidNumber(value) &&
          DoubleToString(value,-16)==raw);
  }

bool JPWMDDEncode(JPWMDDRecord &record,string &content)
  {
   content="";
   if(!JPWMDDRecordValid(record)) return(false);
   const string body="JPW_MDD|1\nMETRIC|"+record.metric_id+
                     "\nKEY|"+record.account_key+
                     "\nCURRENCY|"+record.currency+
                     "\nSCALE|"+(record.account_scale==100.0 ? "100" : "1")+
                     "\nSTART|"+IntegerToString((long)record.observation_started_at)+
                     "\nMAX|"+DoubleToString(record.max_percent,-16)+
                     "\nBALANCE|"+DoubleToString(record.balance_at_max,-16)+
                     "\nEQUITY|"+DoubleToString(record.equity_at_max,-16)+
                     "\nOBSERVED|"+IntegerToString((long)record.observed_at_utc)+
                     "\nBASIS|"+record.time_basis+
                     "\nVERSION|"+record.producer_version+
                     "\nGEN|"+IntegerToString(record.generation)+"\n";
   if(!JPWMDDHash(body,record.checksum)) return(false);
   content=body+"SHA256|"+record.checksum;
   return(StringLen(content)<=JPW_MDD_MAX_BYTES);
  }

JPW_MDD_STATE JPWMDDDecode(const string content,const string expected_key,
                            JPWMDDRecord &record)
  {
   JPWMDDClear(record);
   const int first_newline=StringFind(content,"\n");
   if(first_newline>0 && StringFind(content,"JPW_MDD|")==0 &&
      StringSubstr(content,0,first_newline)!="JPW_MDD|1")
      return(JPW_MDD_INCOMPATIBLE);
   if(StringLen(content)<200 || StringLen(content)>JPW_MDD_MAX_BYTES ||
      !JPWMDDIsHash(expected_key)) return(JPW_MDD_INVALID);
   string lines[];
   if(StringSplit(content,'\n',lines)!=14) return(JPW_MDD_INVALID);
   if(lines[0]!="JPW_MDD|1" ||
      lines[1]!="METRIC|"+JPW_MDD_METRIC_ID ||
      lines[2]!="KEY|"+expected_key ||
      StringFind(lines[3],"CURRENCY|")!=0 ||
      StringFind(lines[4],"SCALE|")!=0 ||
      StringFind(lines[5],"START|")!=0 ||
      StringFind(lines[6],"MAX|")!=0 ||
      StringFind(lines[7],"BALANCE|")!=0 ||
      StringFind(lines[8],"EQUITY|")!=0 ||
      StringFind(lines[9],"OBSERVED|")!=0 ||
      lines[10]!="BASIS|"+JPW_MDD_TIME_BASIS ||
      StringFind(lines[11],"VERSION|")!=0 ||
      StringFind(lines[12],"GEN|")!=0 ||
      StringFind(lines[13],"SHA256|")!=0)
      return(JPW_MDD_INVALID);
   string body="";
   for(int i=0;i<13;i++) body+=lines[i]+"\n";
   string checksum="";
   if(!JPWMDDHash(body,checksum) || !JPWMDDIsHash(StringSubstr(lines[13],7)) ||
      checksum!=StringSubstr(lines[13],7)) return(JPW_MDD_INVALID);
   record.schema=1;
   record.metric_id=JPW_MDD_METRIC_ID;
   record.account_key=expected_key;
   record.currency=StringSubstr(lines[3],9);
   const string scale_text=StringSubstr(lines[4],6);
   if(scale_text!="1" && scale_text!="100") return(JPW_MDD_INVALID);
   record.account_scale=(scale_text=="100" ? 100.0 : 1.0);
   long parsed=0;
   if(!JPWMDDParseUnsigned(StringSubstr(lines[5],6),5000000000,parsed))
      return(JPW_MDD_INVALID);
   record.observation_started_at=(datetime)parsed;
   if(!JPWMDDParseDouble(StringSubstr(lines[6],4),record.max_percent) ||
      !JPWMDDParseDouble(StringSubstr(lines[7],8),record.balance_at_max) ||
      !JPWMDDParseDouble(StringSubstr(lines[8],7),record.equity_at_max) ||
      !JPWMDDParseUnsigned(StringSubstr(lines[9],9),5000000000,parsed))
      return(JPW_MDD_INVALID);
   record.observed_at_utc=(datetime)parsed;
   record.time_basis=JPW_MDD_TIME_BASIS;
   record.producer_version=StringSubstr(lines[11],8);
   if(!JPWMDDParseUnsigned(StringSubstr(lines[12],4),1000000000,parsed))
      return(JPW_MDD_INVALID);
   record.generation=parsed;
   record.checksum=checksum;
   if(!JPWMDDRecordValid(record)) return(JPW_MDD_INVALID);
   string canonical="";
   if(!JPWMDDEncode(record,canonical) || canonical!=content)
      return(JPW_MDD_INVALID);
   return(JPW_MDD_VALID);
  }

JPW_MDD_STATE JPWMDDReadText(const string filename,string &content)
  {
   content="";
   const int handle=FileOpen(filename,FILE_READ|FILE_BIN);
   if(handle==INVALID_HANDLE) return(JPW_MDD_IO_ERROR);
   const ulong size=FileSize(handle);
   if(size==0 || size>(ulong)JPW_MDD_MAX_BYTES)
     { FileClose(handle); return(JPW_MDD_INVALID); }
   uchar bytes[];
   if(ArrayResize(bytes,(int)size)!=(int)size ||
      FileReadArray(handle,bytes,0,(int)size)!=(uint)size)
     { FileClose(handle); return(JPW_MDD_IO_ERROR); }
   FileClose(handle);
   for(int i=0;i<(int)size;i++)
      if((bytes[i]<32 || bytes[i]>126) && bytes[i]!=10)
         return(JPW_MDD_INVALID);
   content=CharArrayToString(bytes,0,(int)size,CP_UTF8);
   return(StringLen(content)==(int)size ? JPW_MDD_VALID : JPW_MDD_INVALID);
  }

bool JPWMDDWriteText(const string filename,const string content)
  {
   uchar bytes[];
   const int copied=StringToCharArray(content,bytes,0,WHOLE_ARRAY,CP_UTF8);
   if(copied<=1 || ArrayResize(bytes,copied-1)!=copied-1 ||
      copied-1>JPW_MDD_MAX_BYTES) return(false);
   const int handle=FileOpen(filename,FILE_WRITE|FILE_BIN);
   if(handle==INVALID_HANDLE) return(false);
   const uint written=FileWriteArray(handle,bytes,0,ArraySize(bytes));
   FileFlush(handle);
   FileClose(handle);
   return(written==(uint)ArraySize(bytes));
  }

// Leitura sob o mesmo lock utilizado na escrita. Uma versao futura em
// qualquer slot exige revisao explicita antes de sobrescrever qualquer dado.
JPW_MDD_STATE JPWMDDLoadState(JPWAccount &account,const string folder,
                              JPWMDDRecord &confirmed,int &active_slot)
  {
   JPWMDDClear(confirmed);
   active_slot=-1;
   string key="";
   string currency="";
   double scale=0.0;
   if(!JPWMDDAccountKey(account,key,currency,scale)) return(JPW_MDD_INVALID);
   int existing=0;
   int valid=0;
   bool io_error=false;
   bool incompatible=false;
   string best_content="";
   JPWMDDRecord first_valid;
   bool seen_valid=false;
   for(int slot=0;slot<2;slot++)
     {
      const string filename=folder+key+(slot==0 ? ".a" : ".b");
      if(!FileIsExist(filename)) continue;
      existing++;
      string content="";
      const JPW_MDD_STATE read_state=JPWMDDReadText(filename,content);
      if(read_state==JPW_MDD_IO_ERROR)
        { io_error=true; continue; }
      if(read_state!=JPW_MDD_VALID) continue;
      JPWMDDRecord parsed;
      const JPW_MDD_STATE decoded=JPWMDDDecode(content,key,parsed);
      if(decoded==JPW_MDD_INCOMPATIBLE)
        { incompatible=true; continue; }
      if(decoded!=JPW_MDD_VALID || parsed.currency!=currency ||
         parsed.account_scale!=scale) continue;
      if(seen_valid)
        {
         const bool newer=(parsed.generation>first_valid.generation);
         const bool older=(parsed.generation<first_valid.generation);
         if(parsed.observation_started_at!=first_valid.observation_started_at ||
            (newer && (parsed.generation!=first_valid.generation+1 ||
                       parsed.max_percent<=first_valid.max_percent)) ||
            (older && (first_valid.generation!=parsed.generation+1 ||
                       first_valid.max_percent<=parsed.max_percent)))
           { JPWMDDClear(confirmed); active_slot=-1; return(JPW_MDD_INVALID); }
        }
      else
        {
         first_valid=parsed;
         seen_valid=true;
        }
      valid++;
      if(parsed.generation==confirmed.generation && valid>1 &&
         content!=best_content)
        { JPWMDDClear(confirmed); active_slot=-1; return(JPW_MDD_INVALID); }
      if(parsed.generation>confirmed.generation)
        {
         confirmed=parsed;
         active_slot=slot;
         best_content=content;
        }
     }
   if(incompatible)
     { JPWMDDClear(confirmed); active_slot=-1; return(JPW_MDD_INCOMPATIBLE); }
   if(io_error)
     { JPWMDDClear(confirmed); active_slot=-1; return(JPW_MDD_IO_ERROR); }
   if(valid>0) return(JPW_MDD_VALID);
   JPWMDDClear(confirmed);
   active_slot=-1;
   return(existing==0 ? JPW_MDD_ABSENT : JPW_MDD_INVALID);
  }

// Consulta sem criar arquivo ou pasta. O lock preexistente e aberto apenas
// para leitura, sem compartilhamento, e liberado antes de qualquer interface.
// Se houver slot sem lock, a leitura nao e considerada segura.
JPW_MDD_STATE JPWMDDReadOnly(JPWAccount &account,const string folder,
                             JPWMDDRecord &confirmed)
  {
   JPWMDDClear(confirmed);
   string key="";
   string currency="";
   double scale=0.0;
   if(!JPWMDDAccountKey(account,key,currency,scale))
      return(JPW_MDD_ACCOUNT_UNAVAILABLE);
   if(StringLen(folder)<StringLen(JPW_MDD_FOLDER) ||
      StringFind(folder,JPW_MDD_FOLDER)!=0 ||
      StringFind(folder,"..")>=0 || StringFind(folder,":")>=0 ||
      StringFind(folder,"/")>=0 ||
      StringSubstr(folder,StringLen(folder)-1)!="\\")
      return(JPW_MDD_INVALID);
   const string lock_name=folder+key+".lock";
   const int lock=FileOpen(lock_name,FILE_READ|FILE_BIN);
   if(lock==INVALID_HANDLE)
     {
      if(FileIsExist(lock_name)) return(JPW_MDD_BUSY);
      if(FileIsExist(folder+key+".a") || FileIsExist(folder+key+".b"))
         return(JPW_MDD_IO_ERROR);
      return(JPW_MDD_ABSENT);
     }
   int active=-1;
   const JPW_MDD_STATE state=JPWMDDLoadState(account,folder,confirmed,active);
   FileClose(lock);
   if(state!=JPW_MDD_VALID) JPWMDDClear(confirmed);
   return(state);
  }

// A conta pode mudar enquanto os slots sao lidos. O chamador faz uma nova
// captura imediatamente apos JPWMDDReadOnly e antes de mostrar o resultado.
JPW_MDD_STATE JPWMDDConfirmAccount(JPWAccount &before,JPWAccount &after,
                                   const JPW_MDD_STATE state,
                                   JPWMDDRecord &confirmed)
  {
   if(state!=JPW_MDD_VALID) JPWMDDClear(confirmed);
   string key="";
   string currency="";
   double scale=0.0;
   if(!JPWMDDAccountKey(after,key,currency,scale) ||
      !JPWAccountsEqual(before,after) ||
      (state==JPW_MDD_VALID && confirmed.account_key!=key))
     {
      JPWMDDClear(confirmed);
      return(JPW_MDD_ACCOUNT_UNAVAILABLE);
     }
   return(state);
  }

// Sem espera: duas instancias disputam o mesmo arquivo exclusivo. Sob o
// handle, relemos o maximo antes da comparacao, impedindo regressao por
// snapshot antigo da instancia chamadora.
JPW_MDD_STATE JPWMDDObserve(JPWAccount &account,const double balance,
                             const double equity,const double dd_percent,
                             const datetime observed_at,const string version,
                             const string folder,JPWMDDRecord &confirmed)
  {
   JPWMDDClear(confirmed);
   string key="";
   string currency="";
   double scale=0.0;
   double derived=0.0;
   if(!JPWMDDAccountKey(account,key,currency,scale) ||
      !JPWBalanceDDPercent(balance,equity,derived) ||
      !MathIsValidNumber(dd_percent) || dd_percent<0.0 ||
      MathAbs(derived-dd_percent)>1e-9*MathMax(MathAbs(derived),
                                               MathAbs(dd_percent)) ||
      observed_at<=0 || !JPWMDDVersionValid(version) ||
      StringFind(folder,JPW_MDD_FOLDER)!=0 ||
      StringFind(folder,"..")>=0 || StringFind(folder,":")>=0 ||
      StringFind(folder,"/")>=0 ||
      StringSubstr(folder,StringLen(folder)-1)!="\\")
      return(JPW_MDD_INVALID);
   // FILE_SHARE_READ e FILE_SHARE_WRITE ausentes: falha significa disputa ou
   // impossibilidade de abrir. Nenhuma gravacao e declarada nesses estados.
   const int lock=FileOpen(folder+key+".lock",FILE_READ|FILE_WRITE|FILE_BIN);
   if(lock==INVALID_HANDLE) return(JPW_MDD_BUSY);
   int active=-1;
   JPW_MDD_STATE state=JPWMDDLoadState(account,folder,confirmed,active);
   if(state!=JPW_MDD_VALID && state!=JPW_MDD_ABSENT)
     { JPWMDDClear(confirmed); FileClose(lock); return(state); }
   if(state==JPW_MDD_VALID && dd_percent<=confirmed.max_percent)
     { FileClose(lock); return(JPW_MDD_VALID); }
   if(state==JPW_MDD_VALID && observed_at<confirmed.observed_at_utc)
     { FileClose(lock); return(JPW_MDD_INVALID); }
   JPWMDDRecord next;
   JPWMDDClear(next);
   next.schema=1;
   next.metric_id=JPW_MDD_METRIC_ID;
   next.account_key=key;
   next.currency=currency;
   next.account_scale=scale;
   next.observation_started_at=(state==JPW_MDD_VALID ?
                                confirmed.observation_started_at : observed_at);
   next.max_percent=dd_percent;
   next.balance_at_max=balance;
   next.equity_at_max=equity;
   next.observed_at_utc=observed_at;
   next.time_basis=JPW_MDD_TIME_BASIS;
   next.producer_version=version;
   next.generation=(state==JPW_MDD_VALID ? confirmed.generation+1 : 1);
   string content="";
   if(!JPWMDDEncode(next,content))
     { FileClose(lock); return(JPW_MDD_INVALID); }
   const string temp=folder+key+"."+
                     IntegerToString((long)ChartID())+"."+
                     IntegerToString((long)GetTickCount64())+".tmp";
   if(FileIsExist(temp))
     { FileClose(lock); return(JPW_MDD_IO_ERROR); }
   if(!JPWMDDWriteText(temp,content))
     { FileDelete(temp); FileClose(lock); return(JPW_MDD_IO_ERROR); }
   string readback="";
   JPWMDDRecord checked;
   if(JPWMDDReadText(temp,readback)!=JPW_MDD_VALID || readback!=content ||
      JPWMDDDecode(readback,key,checked)!=JPW_MDD_VALID ||
      checked.generation!=next.generation)
     { FileDelete(temp); FileClose(lock); return(JPW_MDD_IO_ERROR); }
   const int target=(active==0 ? 1 : 0);
   const string destination=folder+key+(target==0 ? ".a" : ".b");
   if(!FileMove(temp,0,destination,FILE_REWRITE))
     { FileDelete(temp); FileClose(lock); return(JPW_MDD_IO_ERROR); }
   readback="";
   if(JPWMDDReadText(destination,readback)!=JPW_MDD_VALID ||
      readback!=content ||
      JPWMDDDecode(readback,key,checked)!=JPW_MDD_VALID ||
      checked.generation!=next.generation)
     { FileClose(lock); return(JPW_MDD_IO_ERROR); }
   int confirmed_slot=-1;
   state=JPWMDDLoadState(account,folder,confirmed,confirmed_slot);
   FileClose(lock);
   if(state!=JPW_MDD_VALID || confirmed_slot!=target ||
      confirmed.generation!=next.generation) return(JPW_MDD_IO_ERROR);
   return(JPW_MDD_VALID);
  }

#endif
