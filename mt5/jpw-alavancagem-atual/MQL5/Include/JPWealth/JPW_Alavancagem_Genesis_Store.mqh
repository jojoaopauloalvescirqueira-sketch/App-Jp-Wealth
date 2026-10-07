#ifndef JPW_ALAVANCAGEM_GENESIS_STORE_MQH
#define JPW_ALAVANCAGEM_GENESIS_STORE_MQH
#include <JPWealth/JPW_Alavancagem_Core.mqh>

// A referencia da Genese e independente do registro de MDD. O diretorio
// MQL5/Files pertence a uma instalacao do terminal; o nome de cada arquivo
// contem apenas um hash da conta e do seletor, nunca login ou servidor.
#define JPW_GENESIS_FOLDER "JPWealth\\Alavancagem\\"
#define JPW_GENESIS_MAX_BYTES 2048
#define JPW_GENESIS_MAX_SYMBOL_BYTES 256

enum JPW_GENESIS_STORE_STATE
  {
   JPW_GENESIS_VALID=0,
   JPW_GENESIS_ABSENT,
   JPW_GENESIS_INVALID,
   JPW_GENESIS_INCOMPATIBLE,
   JPW_GENESIS_IO_ERROR,
   JPW_GENESIS_BUSY,
   JPW_GENESIS_ACCOUNT_UNAVAILABLE
  };

enum JPW_GENESIS_REF_STATE
  {
   JPW_GENESIS_ACTIVE=1,
   JPW_GENESIS_CLOSED=2,
   JPW_GENESIS_REVERSED=3
  };

struct JPWGenesisRecord
  {
   int schema;
   string account_key;
   long selector_ticket;
   long origin_ticket;
   long identifier;
   string symbol;
   long direction;
   long opened_msc;
   JPW_GENESIS_REF_STATE reference_state;
   long generation;
   string checksum;
  };

void JPWGenesisClear(JPWGenesisRecord &record)
  {
   record.schema=0;
   record.account_key="";
   record.selector_ticket=0;
   record.origin_ticket=0;
   record.identifier=0;
   record.symbol="";
   record.direction=-1;
   record.opened_msc=0;
   record.reference_state=JPW_GENESIS_ACTIVE;
   record.generation=0;
   record.checksum="";
  }

bool JPWGenesisHash(const string value,string &hex)
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

bool JPWGenesisIsHash(const string value)
  {
   if(StringLen(value)!=64) return(false);
   for(int i=0;i<64;i++)
     {
      const ushort c=StringGetCharacter(value,i);
      if(!((c>='0' && c<='9') || (c>='a' && c<='f'))) return(false);
     }
   return(true);
  }

string JPWGenesisFrame(const string value)
  {
   return(IntegerToString(StringLen(value))+":"+value);
  }

bool JPWGenesisAccountKey(JPWAccount &account,const long selector_ticket,
                          string &key)
  {
   key="";
   const string raw_currency=JPWNormalizeCurrency(account.currency);
   string currency="";
   double scale=0.0;
   if(account.login<=0 || account.server=="" || selector_ticket<0 ||
      !JPWAccountUnits(raw_currency,currency,scale)) return(false);
   const string raw=JPWGenesisFrame(account.server)+
                    JPWGenesisFrame(IntegerToString(account.login))+
                    JPWGenesisFrame(raw_currency)+
                    JPWGenesisFrame(scale==100.0 ? "100" : "1")+
                    JPWGenesisFrame(IntegerToString(selector_ticket))+
                    JPWGenesisFrame("genesis_reference_v1");
   return(JPWGenesisHash(raw,key));
  }

bool JPWGenesisFolderValid(const string folder)
  {
   return(StringLen(folder)>=StringLen(JPW_GENESIS_FOLDER) &&
          StringFind(folder,JPW_GENESIS_FOLDER)==0 &&
          StringFind(folder,"..")<0 && StringFind(folder,":")<0 &&
          StringFind(folder,"/")<0 &&
          StringSubstr(folder,StringLen(folder)-1)=="\\");
  }

string JPWGenesisBase(const string folder,const string key)
  {
   return(folder+"genesis_"+key);
  }

bool JPWGenesisSymbolHex(const string symbol,string &hex)
  {
   hex="";
   uchar bytes[];
   const int copied=StringToCharArray(symbol,bytes,0,WHOLE_ARRAY,CP_UTF8);
   if(copied<=1 || copied-1>JPW_GENESIS_MAX_SYMBOL_BYTES ||
      ArrayResize(bytes,copied-1)!=copied-1) return(false);
   for(int i=0;i<copied-1;i++) hex+=StringFormat("%02x",(int)bytes[i]);
   return(StringLen(hex)==2*(copied-1));
  }

int JPWGenesisHexDigit(const ushort c)
  {
   if(c>='0' && c<='9') return((int)(c-'0'));
   if(c>='a' && c<='f') return((int)(c-'a')+10);
   return(-1);
  }

bool JPWGenesisSymbolFromHex(const string hex,string &symbol)
  {
   symbol="";
   const int len=StringLen(hex);
   if(len<2 || len>2*JPW_GENESIS_MAX_SYMBOL_BYTES || len%2!=0) return(false);
   uchar bytes[];
   if(ArrayResize(bytes,len/2)!=len/2) return(false);
   for(int i=0;i<len/2;i++)
     {
      const int hi=JPWGenesisHexDigit(StringGetCharacter(hex,2*i));
      const int lo=JPWGenesisHexDigit(StringGetCharacter(hex,2*i+1));
      if(hi<0 || lo<0) return(false);
      bytes[i]=(uchar)(16*hi+lo);
     }
   symbol=CharArrayToString(bytes,0,len/2,CP_UTF8);
   string canonical="";
   return(JPWGenesisSymbolHex(symbol,canonical) && canonical==hex);
  }

bool JPWGenesisParseUnsigned(const string raw,const long maximum,long &value)
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

bool JPWGenesisRecordValid(JPWGenesisRecord &record)
  {
   if(record.schema!=1 || !JPWGenesisIsHash(record.account_key) ||
      record.selector_ticket<0 || record.origin_ticket<=0 ||
      (record.selector_ticket>0 &&
       record.selector_ticket!=record.origin_ticket) ||
      record.identifier<=0 || record.opened_msc<=0 ||
      (record.direction!=POSITION_TYPE_BUY &&
       record.direction!=POSITION_TYPE_SELL) ||
      (record.reference_state!=JPW_GENESIS_ACTIVE &&
       record.reference_state!=JPW_GENESIS_CLOSED &&
       record.reference_state!=JPW_GENESIS_REVERSED) ||
      record.generation<1 || record.generation>1000000000)
      return(false);
   string hex="";
   return(JPWGenesisSymbolHex(record.symbol,hex));
  }

bool JPWGenesisSameIdentity(JPWGenesisRecord &a,JPWGenesisRecord &b)
  {
   return(a.account_key==b.account_key &&
          a.selector_ticket==b.selector_ticket &&
          a.origin_ticket==b.origin_ticket &&
          a.identifier==b.identifier && a.symbol==b.symbol &&
          a.direction==b.direction && a.opened_msc==b.opened_msc);
  }

bool JPWGenesisEncode(JPWGenesisRecord &record,string &content)
  {
   content="";
   if(!JPWGenesisRecordValid(record)) return(false);
   string symbol_hex="";
   if(!JPWGenesisSymbolHex(record.symbol,symbol_hex)) return(false);
   const string body="JPW_GENESIS|1\nKEY|"+record.account_key+
                     "\nSELECTOR|"+IntegerToString(record.selector_ticket)+
                     "\nORIGIN|"+IntegerToString(record.origin_ticket)+
                     "\nIDENTIFIER|"+IntegerToString(record.identifier)+
                     "\nSYMBOL_HEX|"+symbol_hex+
                     "\nDIRECTION|"+IntegerToString(record.direction)+
                     "\nOPEN_MSC|"+IntegerToString(record.opened_msc)+
                     "\nSTATE|"+IntegerToString((int)record.reference_state)+
                     "\nGEN|"+IntegerToString(record.generation)+"\n";
   if(!JPWGenesisHash(body,record.checksum)) return(false);
   content=body+"SHA256|"+record.checksum;
   return(StringLen(content)<=JPW_GENESIS_MAX_BYTES);
  }

JPW_GENESIS_STORE_STATE JPWGenesisDecode(const string content,
                                         const string expected_key,
                                         JPWGenesisRecord &record)
  {
   JPWGenesisClear(record);
   const int first_newline=StringFind(content,"\n");
   if(first_newline>0 && StringFind(content,"JPW_GENESIS|")==0 &&
      StringSubstr(content,0,first_newline)!="JPW_GENESIS|1")
      return(JPW_GENESIS_INCOMPATIBLE);
   if(StringLen(content)<190 || StringLen(content)>JPW_GENESIS_MAX_BYTES ||
      !JPWGenesisIsHash(expected_key)) return(JPW_GENESIS_INVALID);
   string lines[];
   if(StringSplit(content,'\n',lines)!=11 ||
      lines[0]!="JPW_GENESIS|1" || lines[1]!="KEY|"+expected_key ||
      StringFind(lines[2],"SELECTOR|")!=0 ||
      StringFind(lines[3],"ORIGIN|")!=0 ||
      StringFind(lines[4],"IDENTIFIER|")!=0 ||
      StringFind(lines[5],"SYMBOL_HEX|")!=0 ||
      StringFind(lines[6],"DIRECTION|")!=0 ||
      StringFind(lines[7],"OPEN_MSC|")!=0 ||
      StringFind(lines[8],"STATE|")!=0 ||
      StringFind(lines[9],"GEN|")!=0 ||
      StringFind(lines[10],"SHA256|")!=0)
      return(JPW_GENESIS_INVALID);
   string body="";
   for(int i=0;i<10;i++) body+=lines[i]+"\n";
   string checksum="";
   if(!JPWGenesisHash(body,checksum) ||
      !JPWGenesisIsHash(StringSubstr(lines[10],7)) ||
      checksum!=StringSubstr(lines[10],7)) return(JPW_GENESIS_INVALID);
   long value=0;
   record.schema=1;
   record.account_key=expected_key;
   if(!JPWGenesisParseUnsigned(StringSubstr(lines[2],9),
                               9223372036854775807,value))
      return(JPW_GENESIS_INVALID);
   record.selector_ticket=value;
   if(!JPWGenesisParseUnsigned(StringSubstr(lines[3],7),
                               9223372036854775807,value))
      return(JPW_GENESIS_INVALID);
   record.origin_ticket=value;
   if(!JPWGenesisParseUnsigned(StringSubstr(lines[4],11),
                               9223372036854775807,value))
      return(JPW_GENESIS_INVALID);
   record.identifier=value;
   if(!JPWGenesisSymbolFromHex(StringSubstr(lines[5],11),record.symbol))
      return(JPW_GENESIS_INVALID);
   if(!JPWGenesisParseUnsigned(StringSubstr(lines[6],10),1,value))
      return(JPW_GENESIS_INVALID);
   record.direction=value;
   if(!JPWGenesisParseUnsigned(StringSubstr(lines[7],9),
                               9223372036854775807,value))
      return(JPW_GENESIS_INVALID);
   record.opened_msc=value;
   if(!JPWGenesisParseUnsigned(StringSubstr(lines[8],6),3,value))
      return(JPW_GENESIS_INVALID);
   record.reference_state=(JPW_GENESIS_REF_STATE)value;
   if(!JPWGenesisParseUnsigned(StringSubstr(lines[9],4),1000000000,value))
      return(JPW_GENESIS_INVALID);
   record.generation=value;
   record.checksum=checksum;
   if(!JPWGenesisRecordValid(record)) return(JPW_GENESIS_INVALID);
   string canonical="";
   if(!JPWGenesisEncode(record,canonical) || canonical!=content)
      return(JPW_GENESIS_INVALID);
   return(JPW_GENESIS_VALID);
  }

JPW_GENESIS_STORE_STATE JPWGenesisReadText(const string filename,
                                           string &content)
  {
   content="";
   const int handle=FileOpen(filename,FILE_READ|FILE_BIN);
   if(handle==INVALID_HANDLE) return(JPW_GENESIS_IO_ERROR);
   const ulong size=FileSize(handle);
   if(size==0 || size>(ulong)JPW_GENESIS_MAX_BYTES)
     { FileClose(handle); return(JPW_GENESIS_INVALID); }
   uchar bytes[];
   if(ArrayResize(bytes,(int)size)!=(int)size ||
      FileReadArray(handle,bytes,0,(int)size)!=(uint)size)
     { FileClose(handle); return(JPW_GENESIS_IO_ERROR); }
   FileClose(handle);
   for(int i=0;i<(int)size;i++)
      if((bytes[i]<32 || bytes[i]>126) && bytes[i]!=10)
         return(JPW_GENESIS_INVALID);
   content=CharArrayToString(bytes,0,(int)size,CP_UTF8);
   return(StringLen(content)==(int)size ? JPW_GENESIS_VALID :
          JPW_GENESIS_INVALID);
  }

bool JPWGenesisWriteText(const string filename,const string content)
  {
   uchar bytes[];
   const int copied=StringToCharArray(content,bytes,0,WHOLE_ARRAY,CP_UTF8);
   if(copied<=1 || ArrayResize(bytes,copied-1)!=copied-1 ||
      copied-1>JPW_GENESIS_MAX_BYTES) return(false);
   const int handle=FileOpen(filename,FILE_WRITE|FILE_BIN);
   if(handle==INVALID_HANDLE) return(false);
   const uint written=FileWriteArray(handle,bytes,0,ArraySize(bytes));
   FileFlush(handle);
   FileClose(handle);
   return(written==(uint)ArraySize(bytes));
  }

// O chamador ja detem o lock. Um slot de versao futura bloqueia escrita,
// mesmo quando o outro ainda e valido.
JPW_GENESIS_STORE_STATE JPWGenesisLoadState(JPWAccount &account,
                                            const long selector_ticket,
                                            const string folder,
                                            JPWGenesisRecord &confirmed,
                                            int &active_slot)
  {
   JPWGenesisClear(confirmed);
   active_slot=-1;
   string key="";
   if(!JPWGenesisAccountKey(account,selector_ticket,key) ||
      !JPWGenesisFolderValid(folder)) return(JPW_GENESIS_ACCOUNT_UNAVAILABLE);
   const string base=JPWGenesisBase(folder,key);
   int existing=0;
   int valid=0;
   bool io_error=false;
   bool incompatible=false;
   string best_content="";
   JPWGenesisRecord first_valid;
   bool seen_valid=false;
   for(int slot=0;slot<2;slot++)
     {
      const string filename=base+(slot==0 ? ".a" : ".b");
      if(!FileIsExist(filename)) continue;
      existing++;
      string content="";
      const JPW_GENESIS_STORE_STATE read_state=
         JPWGenesisReadText(filename,content);
      if(read_state==JPW_GENESIS_IO_ERROR)
        { io_error=true; continue; }
      if(read_state!=JPW_GENESIS_VALID) continue;
      JPWGenesisRecord parsed;
      const JPW_GENESIS_STORE_STATE decoded=
         JPWGenesisDecode(content,key,parsed);
      if(decoded==JPW_GENESIS_INCOMPATIBLE)
        { incompatible=true; continue; }
      if(decoded!=JPW_GENESIS_VALID ||
         parsed.selector_ticket!=selector_ticket) continue;
      if(seen_valid)
        {
         const bool newer=(parsed.generation>first_valid.generation);
         const bool older=(parsed.generation<first_valid.generation);
         if(!JPWGenesisSameIdentity(parsed,first_valid) ||
            (newer &&
             (parsed.generation!=first_valid.generation+1 ||
              first_valid.reference_state!=JPW_GENESIS_ACTIVE ||
              parsed.reference_state==JPW_GENESIS_ACTIVE)) ||
            (older &&
             (first_valid.generation!=parsed.generation+1 ||
              parsed.reference_state!=JPW_GENESIS_ACTIVE ||
              first_valid.reference_state==JPW_GENESIS_ACTIVE)))
           { JPWGenesisClear(confirmed); active_slot=-1;
             return(JPW_GENESIS_INVALID); }
        }
      else
        {
         first_valid=parsed;
         seen_valid=true;
        }
      valid++;
      if(parsed.generation==confirmed.generation && valid>1 &&
         content!=best_content)
        { JPWGenesisClear(confirmed); active_slot=-1;
          return(JPW_GENESIS_INVALID); }
      if(parsed.generation>confirmed.generation)
        {
         confirmed=parsed;
         active_slot=slot;
         best_content=content;
        }
     }
   if(incompatible)
     { JPWGenesisClear(confirmed); active_slot=-1;
       return(JPW_GENESIS_INCOMPATIBLE); }
   if(io_error)
     { JPWGenesisClear(confirmed); active_slot=-1;
       return(JPW_GENESIS_IO_ERROR); }
   if(valid>0) return(JPW_GENESIS_VALID);
   JPWGenesisClear(confirmed);
   active_slot=-1;
   return(existing==0 ? JPW_GENESIS_ABSENT : JPW_GENESIS_INVALID);
  }

// Leitura sem criar pasta nem lock. Slots desacompanhados do lock falham
// fechados; nenhum outro processo pode alterar os slots durante esta leitura.
JPW_GENESIS_STORE_STATE JPWGenesisRead(JPWAccount &account,
                                       const long selector_ticket,
                                       const string folder,
                                       JPWGenesisRecord &confirmed)
  {
   JPWGenesisClear(confirmed);
   string key="";
   if(!JPWGenesisAccountKey(account,selector_ticket,key))
      return(JPW_GENESIS_ACCOUNT_UNAVAILABLE);
   if(!JPWGenesisFolderValid(folder)) return(JPW_GENESIS_INVALID);
   const string base=JPWGenesisBase(folder,key);
   const int lock=FileOpen(base+".lock",FILE_READ|FILE_BIN);
   if(lock==INVALID_HANDLE)
     {
      if(FileIsExist(base+".lock")) return(JPW_GENESIS_BUSY);
      if(FileIsExist(base+".a") || FileIsExist(base+".b"))
         return(JPW_GENESIS_IO_ERROR);
      return(JPW_GENESIS_ABSENT);
     }
   int active=-1;
   const JPW_GENESIS_STORE_STATE state=
      JPWGenesisLoadState(account,selector_ticket,folder,confirmed,active);
   FileClose(lock);
   if(state!=JPW_GENESIS_VALID) JPWGenesisClear(confirmed);
   return(state);
  }

JPW_GENESIS_STORE_STATE JPWGenesisConfirmAccount(
   JPWAccount &before,JPWAccount &after,const long selector_ticket,
   const JPW_GENESIS_STORE_STATE state,JPWGenesisRecord &confirmed)
  {
   if(state!=JPW_GENESIS_VALID) JPWGenesisClear(confirmed);
   string before_key="";
   string after_key="";
   if(!JPWGenesisAccountKey(before,selector_ticket,before_key) ||
      !JPWGenesisAccountKey(after,selector_ticket,after_key) ||
      before_key!=after_key || !JPWAccountsEqual(before,after) ||
      (state==JPW_GENESIS_VALID && confirmed.account_key!=after_key))
     {
      JPWGenesisClear(confirmed);
      return(JPW_GENESIS_ACCOUNT_UNAVAILABLE);
     }
   return(state);
  }

// O lock deve permanecer aberto ate a confirmacao final. O slot anterior
// continua valido se a escrita do novo slot for interrompida.
JPW_GENESIS_STORE_STATE JPWGenesisCommitLocked(
   JPWAccount &account,const long selector_ticket,const string folder,
   JPWGenesisRecord &next,const int active_slot,JPWGenesisRecord &confirmed)
  {
   JPWGenesisClear(confirmed);
   string content="";
   if(!JPWGenesisEncode(next,content)) return(JPW_GENESIS_INVALID);
   const string base=JPWGenesisBase(folder,next.account_key);
   const string temp=base+"."+IntegerToString((long)ChartID())+"."+
                     IntegerToString((long)GetTickCount64())+".tmp";
   if(FileIsExist(temp)) return(JPW_GENESIS_IO_ERROR);
   if(!JPWGenesisWriteText(temp,content))
     { FileDelete(temp); return(JPW_GENESIS_IO_ERROR); }
   string readback="";
   JPWGenesisRecord checked;
   if(JPWGenesisReadText(temp,readback)!=JPW_GENESIS_VALID ||
      readback!=content ||
      JPWGenesisDecode(readback,next.account_key,checked)!=JPW_GENESIS_VALID ||
      checked.generation!=next.generation)
     { FileDelete(temp); return(JPW_GENESIS_IO_ERROR); }
   const int target=(active_slot==0 ? 1 : 0);
   const string destination=base+(target==0 ? ".a" : ".b");
   if(!FileMove(temp,0,destination,FILE_REWRITE))
     { FileDelete(temp); return(JPW_GENESIS_IO_ERROR); }
   readback="";
   if(JPWGenesisReadText(destination,readback)!=JPW_GENESIS_VALID ||
      readback!=content ||
      JPWGenesisDecode(readback,next.account_key,checked)!=JPW_GENESIS_VALID ||
      checked.generation!=next.generation)
      return(JPW_GENESIS_IO_ERROR);
   int confirmed_slot=-1;
   const JPW_GENESIS_STORE_STATE state=
      JPWGenesisLoadState(account,selector_ticket,folder,confirmed,
                          confirmed_slot);
   if(state!=JPW_GENESIS_VALID || confirmed_slot!=target ||
      confirmed.generation!=next.generation)
     { JPWGenesisClear(confirmed); return(JPW_GENESIS_IO_ERROR); }
   return(JPW_GENESIS_VALID);
  }

JPW_GENESIS_STORE_STATE JPWGenesisCreate(
   JPWAccount &account,const long selector_ticket,const string folder,
   const long origin_ticket,const long identifier,const string symbol,
   const long direction,const long opened_msc,JPWGenesisRecord &confirmed)
  {
   JPWGenesisClear(confirmed);
   string key="";
   if(!JPWGenesisAccountKey(account,selector_ticket,key))
      return(JPW_GENESIS_ACCOUNT_UNAVAILABLE);
   if(!JPWGenesisFolderValid(folder)) return(JPW_GENESIS_INVALID);
   JPWGenesisRecord next;
   JPWGenesisClear(next);
   next.schema=1;
   next.account_key=key;
   next.selector_ticket=selector_ticket;
   next.origin_ticket=origin_ticket;
   next.identifier=identifier;
   next.symbol=symbol;
   next.direction=direction;
   next.opened_msc=opened_msc;
   next.reference_state=JPW_GENESIS_ACTIVE;
   next.generation=1;
   if(!JPWGenesisRecordValid(next)) return(JPW_GENESIS_INVALID);
   // FolderCreate aceita hierarquia relativa a MQL5/Files e retorna true
   // tambem quando ela ja existe. Nunca usa FILE_COMMON nem caminho externo.
   if(!FolderCreate(StringSubstr(folder,0,StringLen(folder)-1)))
      return(JPW_GENESIS_IO_ERROR);
   const string base=JPWGenesisBase(folder,key);
   const int lock=FileOpen(base+".lock",FILE_READ|FILE_WRITE|FILE_BIN);
   if(lock==INVALID_HANDLE) return(JPW_GENESIS_BUSY);
   int active=-1;
   const JPW_GENESIS_STORE_STATE state=
      JPWGenesisLoadState(account,selector_ticket,folder,confirmed,active);
   if(state==JPW_GENESIS_VALID)
     {
      const bool same=JPWGenesisSameIdentity(next,confirmed);
      FileClose(lock);
      if(same) return(JPW_GENESIS_VALID);
      JPWGenesisClear(confirmed);
      return(JPW_GENESIS_INVALID);
     }
   if(state!=JPW_GENESIS_ABSENT)
     { JPWGenesisClear(confirmed); FileClose(lock); return(state); }
   const JPW_GENESIS_STORE_STATE written=
      JPWGenesisCommitLocked(account,selector_ticket,folder,next,active,
                             confirmed);
   FileClose(lock);
   return(written);
  }

JPW_GENESIS_STORE_STATE JPWGenesisTransition(
   JPWAccount &account,const long selector_ticket,const string folder,
   const long expected_identifier,const JPW_GENESIS_REF_STATE terminal_state,
   JPWGenesisRecord &confirmed)
  {
   JPWGenesisClear(confirmed);
   string key="";
   if(!JPWGenesisAccountKey(account,selector_ticket,key))
      return(JPW_GENESIS_ACCOUNT_UNAVAILABLE);
   if(!JPWGenesisFolderValid(folder) || expected_identifier<=0 ||
      (terminal_state!=JPW_GENESIS_CLOSED &&
       terminal_state!=JPW_GENESIS_REVERSED)) return(JPW_GENESIS_INVALID);
   const string base=JPWGenesisBase(folder,key);
   const int lock=FileOpen(base+".lock",FILE_READ|FILE_WRITE|FILE_BIN);
   if(lock==INVALID_HANDLE) return(JPW_GENESIS_BUSY);
   int active=-1;
   const JPW_GENESIS_STORE_STATE state=
      JPWGenesisLoadState(account,selector_ticket,folder,confirmed,active);
   if(state!=JPW_GENESIS_VALID)
     { JPWGenesisClear(confirmed); FileClose(lock); return(state); }
   if(confirmed.identifier!=expected_identifier ||
      confirmed.reference_state!=JPW_GENESIS_ACTIVE)
     {
      const bool already=(confirmed.identifier==expected_identifier &&
                          confirmed.reference_state==terminal_state);
      FileClose(lock);
      if(already) return(JPW_GENESIS_VALID);
      JPWGenesisClear(confirmed);
      return(JPW_GENESIS_INVALID);
     }
   if(confirmed.generation>=1000000000)
     { JPWGenesisClear(confirmed); FileClose(lock); return(JPW_GENESIS_INVALID); }
   JPWGenesisRecord next=confirmed;
   next.reference_state=terminal_state;
   next.generation++;
   const JPW_GENESIS_STORE_STATE written=
      JPWGenesisCommitLocked(account,selector_ticket,folder,next,active,
                             confirmed);
   FileClose(lock);
   return(written);
  }

#endif
