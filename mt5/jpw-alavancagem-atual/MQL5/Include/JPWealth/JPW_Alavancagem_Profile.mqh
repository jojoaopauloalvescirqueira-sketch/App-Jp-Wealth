#ifndef JPW_ALAVANCAGEM_PROFILE_MQH
#define JPW_ALAVANCAGEM_PROFILE_MQH
#include <JPWealth/JPW_Alavancagem_Core.mqh>

// Perfil tecnico local da ferramenta MT5. O arquivo nunca contem login,
// servidor, moeda da conta, equity, tickets, volumes ou nomes de simbolos.
// Dois slots preservam a ultima geracao valida durante uma troca interrompida.
#define JPW_PROFILE_MAX_ENTRIES 256
#define JPW_PROFILE_MAX_BYTES 65536
#define JPW_PROFILE_FOLDER "JPWealth\\Alavancagem\\"

struct JPWProfileEntry
  {
   string symbol_hash;
   string spec_hash;
   double scale;
   datetime verified_at;
  };

enum JPW_PROFILE_STATE
  {
   JPW_PROFILE_ABSENT=0,
   JPW_PROFILE_VALID=1,
   JPW_PROFILE_INVALID=2
  };

bool JPWProfileHash(const string value,string &hex)
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

bool JPWProfileIsHash(const string value)
  {
   if(StringLen(value)!=64) return(false);
   for(int i=0;i<64;i++)
     {
      const ushort c=StringGetCharacter(value,i);
      if(!((c>='0' && c<='9') || (c>='a' && c<='f'))) return(false);
     }
   return(true);
  }

string JPWProfileFrame(const string value)
  {
   return(IntegerToString(StringLen(value))+":"+value);
  }

bool JPWProfileAccountHash(JPWAccount &account,string &key)
  {
   key="";
   if(account.login<=0 || account.server=="" || account.currency=="") return(false);
   const string raw=JPWProfileFrame(account.server)+
                    JPWProfileFrame(IntegerToString(account.login))+
                    JPWProfileFrame(JPWNormalizeCurrency(account.currency));
   return(JPWProfileHash(raw,key));
  }

bool JPWProfileSignature(JPWInstrument &instrument,string &signature)
  {
   signature="";
   if(instrument.symbol=="" || !JPWFinitePositive(instrument.contract_size))
      return(false);
   double tick_size=0.0;
   double volume_min=0.0;
   double volume_max=0.0;
   double volume_step=0.0;
   long digits=-1;
   string basis="";
   string isin="";
   if(!SymbolInfoDouble(instrument.symbol,SYMBOL_TRADE_TICK_SIZE,tick_size) ||
      !SymbolInfoDouble(instrument.symbol,SYMBOL_VOLUME_MIN,volume_min) ||
      !SymbolInfoDouble(instrument.symbol,SYMBOL_VOLUME_MAX,volume_max) ||
      !SymbolInfoDouble(instrument.symbol,SYMBOL_VOLUME_STEP,volume_step) ||
      !SymbolInfoInteger(instrument.symbol,SYMBOL_DIGITS,digits) ||
      !JPWFinitePositive(tick_size) || !JPWFinitePositive(volume_min) ||
      !JPWFinitePositive(volume_step) || volume_max<volume_min ||
      digits<0 || digits>16)
      return(false);
   SymbolInfoString(instrument.symbol,SYMBOL_BASIS,basis);
   SymbolInfoString(instrument.symbol,SYMBOL_ISIN,isin);
   if(instrument.underlying_verified!=(basis!="" || isin!="")) return(false);
   const string raw=JPWProfileFrame(instrument.symbol)+
                    JPWProfileFrame(IntegerToString(instrument.calc_mode))+
                    JPWProfileFrame(JPWNormalizeCurrency(instrument.base))+
                    JPWProfileFrame(JPWNormalizeCurrency(instrument.profit))+
                    JPWProfileFrame(DoubleToString(instrument.contract_size,16))+
                    JPWProfileFrame(DoubleToString(tick_size,16))+
                    JPWProfileFrame(IntegerToString(digits))+
                    JPWProfileFrame(DoubleToString(volume_min,16))+
                    JPWProfileFrame(DoubleToString(volume_max,16))+
                    JPWProfileFrame(DoubleToString(volume_step,16))+
                    JPWProfileFrame(basis)+JPWProfileFrame(isin);
   return(JPWProfileHash(raw,signature));
  }

bool JPWProfileParseNumber(const string raw,const long maximum,long &value)
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

bool JPWProfileEntryValid(JPWProfileEntry &entry)
  {
   return(JPWProfileIsHash(entry.symbol_hash) &&
          JPWProfileIsHash(entry.spec_hash) &&
          JPWContractScaleValid(entry.scale) && entry.verified_at>0);
  }

string JPWProfileScaleText(const double scale)
  {
   return(scale==1.0 ? "1" : "0.01");
  }

bool JPWProfileEncode(const string account_hash,const long generation,
                      JPWProfileEntry &entries[],string &content)
  {
   content="";
   const int count=ArraySize(entries);
   if(!JPWProfileIsHash(account_hash) || generation<=0 ||
      count<1 || count>JPW_PROFILE_MAX_ENTRIES) return(false);
   string body="JPWLEVERAGE_PROFILE|1\nACCOUNT|"+account_hash+"\nGEN|"+
               IntegerToString(generation)+"\nCOUNT|"+IntegerToString(count)+"\n";
   for(int i=0;i<count;i++)
     {
      if(!JPWProfileEntryValid(entries[i])) return(false);
      for(int j=0;j<i;j++)
         if(entries[i].symbol_hash==entries[j].symbol_hash) return(false);
      body+="E|"+entries[i].symbol_hash+"|"+entries[i].spec_hash+"|"+
            JPWProfileScaleText(entries[i].scale)+"|"+
            IntegerToString((long)entries[i].verified_at)+"\n";
     }
   string checksum="";
   if(!JPWProfileHash(body,checksum)) return(false);
   content=body+"SHA256|"+checksum;
   return(StringLen(content)<=JPW_PROFILE_MAX_BYTES);
  }

bool JPWProfileDecode(const string content,const string account_hash,
                      JPWProfileEntry &entries[],long &generation)
  {
   ArrayResize(entries,0);
   generation=0;
   if(StringLen(content)<150 || StringLen(content)>JPW_PROFILE_MAX_BYTES ||
      !JPWProfileIsHash(account_hash)) return(false);
   string lines[];
   const int line_count=StringSplit(content,'\n',lines);
   if(line_count<6 || lines[0]!="JPWLEVERAGE_PROFILE|1" ||
      lines[1]!="ACCOUNT|"+account_hash ||
      StringFind(lines[2],"GEN|")!=0 ||
      StringFind(lines[3],"COUNT|")!=0) return(false);
   long count=0;
   if(!JPWProfileParseNumber(StringSubstr(lines[2],4),1000000000,generation) ||
      generation<=0 ||
      !JPWProfileParseNumber(StringSubstr(lines[3],6),JPW_PROFILE_MAX_ENTRIES,count) ||
      count<=0 || line_count!=5+(int)count) return(false);
   string footer[];
   if(StringSplit(lines[line_count-1],'|',footer)!=2 ||
      footer[0]!="SHA256" || !JPWProfileIsHash(footer[1])) return(false);
   string body="";
   for(int i=0;i<line_count-1;i++) body+=lines[i]+"\n";
   string actual="";
   if(!JPWProfileHash(body,actual) || actual!=footer[1]) return(false);
   if(ArrayResize(entries,(int)count)!=(int)count) return(false);
   for(int i=0;i<(int)count;i++)
     {
      string fields[];
      if(StringSplit(lines[4+i],'|',fields)!=5 || fields[0]!="E" ||
         !JPWProfileIsHash(fields[1]) || !JPWProfileIsHash(fields[2]) ||
         (fields[3]!="1" && fields[3]!="0.01")) return(false);
      long verified=0;
      if(!JPWProfileParseNumber(fields[4],5000000000,verified) || verified<=0)
         return(false);
      entries[i].symbol_hash=fields[1];
      entries[i].spec_hash=fields[2];
      entries[i].scale=(fields[3]=="1" ? 1.0 : 0.01);
      entries[i].verified_at=(datetime)verified;
      for(int j=0;j<i;j++)
         if(entries[i].symbol_hash==entries[j].symbol_hash) return(false);
     }
   return(true);
  }

bool JPWProfileReadText(const string filename,string &content)
  {
   content="";
   const int handle=FileOpen(filename,FILE_READ|FILE_BIN);
   if(handle==INVALID_HANDLE) return(false);
   const long size=FileSize(handle);
   if(size<=0 || size>JPW_PROFILE_MAX_BYTES)
     { FileClose(handle); return(false); }
   uchar bytes[];
   if(ArrayResize(bytes,(int)size)!=(int)size ||
      FileReadArray(handle,bytes,0,(int)size)!=(uint)size)
     { FileClose(handle); return(false); }
   FileClose(handle);
   for(int i=0;i<(int)size;i++)
      if((bytes[i]<32 || bytes[i]>126) && bytes[i]!=10) return(false);
   content=CharArrayToString(bytes,0,(int)size,CP_UTF8);
   return(StringLen(content)==(int)size);
  }

bool JPWProfileWriteText(const string filename,const string content)
  {
   uchar bytes[];
   const int copied=StringToCharArray(content,bytes,0,WHOLE_ARRAY,CP_UTF8);
   if(copied<=1 || ArrayResize(bytes,copied-1)!=copied-1 ||
      copied-1>JPW_PROFILE_MAX_BYTES) return(false);
   const int handle=FileOpen(filename,FILE_WRITE|FILE_BIN);
   if(handle==INVALID_HANDLE) return(false);
   const uint written=FileWriteArray(handle,bytes,0,ArraySize(bytes));
   FileFlush(handle);
   FileClose(handle);
   return(written==(uint)ArraySize(bytes));
  }

// Escolhe somente a geracao valida mais nova. Slots validos com a mesma
// geracao e bytes diferentes sao ambiguidade, nao empate resolvido por ordem.
JPW_PROFILE_STATE JPWProfileLoadState(JPWAccount &account,
                                      JPWProfileEntry &entries[],
                                      long &generation,int &active_slot)
  {
   ArrayResize(entries,0);
   generation=0;
   active_slot=-1;
   string key="";
   if(!JPWProfileAccountHash(account,key)) return(JPW_PROFILE_INVALID);
   int existing=0;
   int valid=0;
   string best_content="";
   for(int slot=0;slot<2;slot++)
     {
      const string filename=JPW_PROFILE_FOLDER+key+(slot==0 ? ".a" : ".b");
      if(!FileIsExist(filename)) continue;
      existing++;
      string content="";
      JPWProfileEntry parsed[];
      long parsed_generation=0;
      if(!JPWProfileReadText(filename,content) ||
         !JPWProfileDecode(content,key,parsed,parsed_generation)) continue;
      valid++;
      if(parsed_generation==generation && valid>1 && content!=best_content)
         return(JPW_PROFILE_INVALID);
      if(parsed_generation>generation)
        {
         generation=parsed_generation;
         active_slot=slot;
         best_content=content;
         if(ArrayResize(entries,ArraySize(parsed))!=ArraySize(parsed))
            return(JPW_PROFILE_INVALID);
         for(int i=0;i<ArraySize(parsed);i++) entries[i]=parsed[i];
        }
     }
   if(valid>0) return(JPW_PROFILE_VALID);
   return(existing==0 ? JPW_PROFILE_ABSENT : JPW_PROFILE_INVALID);
  }

bool JPWProfileLoad(JPWAccount &account,JPWProfileEntry &entries[])
  {
   long generation=0;
   int slot=-1;
   return(JPWProfileLoadState(account,entries,generation,slot)==JPW_PROFILE_VALID);
  }

bool JPWProfileFind(JPWInstrument &instrument,JPWProfileEntry &entries[],
                    double &scale)
  {
   scale=0.0;
   string symbol_hash="";
   string spec_hash="";
   if(!JPWProfileHash(instrument.symbol,symbol_hash) ||
      !JPWProfileSignature(instrument,spec_hash)) return(false);
   for(int i=0;i<ArraySize(entries);i++)
      if(entries[i].symbol_hash==symbol_hash)
        {
         if(!JPWProfileEntryValid(entries[i]) ||
            entries[i].spec_hash!=spec_hash) return(false);
         scale=entries[i].scale;
         return(true);
        }
   return(false);
  }

bool JPWProfileSaveLocked(JPWAccount &account,JPWProfileEntry &entries[])
  {
   string key="";
   if(!JPWProfileAccountHash(account,key)) return(false);
   JPWProfileEntry previous[];
   long generation=0;
   int active=-1;
   const JPW_PROFILE_STATE state=JPWProfileLoadState(account,previous,
                                                     generation,active);
   if(state==JPW_PROFILE_INVALID || generation>=1000000000) return(false);
   JPWProfileEntry merged[];
   if(ArrayResize(merged,ArraySize(entries))!=ArraySize(entries)) return(false);
   for(int i=0;i<ArraySize(entries);i++) merged[i]=entries[i];
   // Mesclar sob o lock: outra execucao pode ter confirmado um simbolo desde
   // que o chamador carregou seu snapshot. Nunca apagar a verificacao mais nova.
   for(int i=0;i<ArraySize(previous);i++)
     {
      int found=-1;
      for(int j=0;j<ArraySize(merged);j++)
         if(merged[j].symbol_hash==previous[i].symbol_hash)
           { found=j; break; }
      if(found<0)
        {
         const int n=ArraySize(merged);
         if(ArrayResize(merged,n+1)!=n+1) return(false);
         merged[n]=previous[i];
        }
      else if(previous[i].verified_at>merged[found].verified_at)
        {
         if(previous[i].spec_hash!=merged[found].spec_hash ||
            previous[i].scale!=merged[found].scale) return(false);
         merged[found]=previous[i];
        }
      else if(previous[i].verified_at==merged[found].verified_at &&
              (previous[i].spec_hash!=merged[found].spec_hash ||
               previous[i].scale!=merged[found].scale)) return(false);
     }
   const long next=generation+1;
   string content="";
   if(!JPWProfileEncode(key,next,merged,content)) return(false);
   const string temp=JPW_PROFILE_FOLDER+key+"."+
                     IntegerToString((long)ChartID())+"."+
                     IntegerToString((long)GetTickCount64())+".tmp";
   if(FileIsExist(temp)) return(false);
   if(!JPWProfileWriteText(temp,content))
     { FileDelete(temp); return(false); }
   string readback="";
   JPWProfileEntry checked[];
   long checked_generation=0;
   if(!JPWProfileReadText(temp,readback) || readback!=content ||
      !JPWProfileDecode(readback,key,checked,checked_generation) ||
      checked_generation!=next)
     { FileDelete(temp); return(false); }
   const int target=(active==0 ? 1 : 0);
   const string destination=JPW_PROFILE_FOLDER+key+
                            (target==0 ? ".a" : ".b");
   if(!FileMove(temp,0,destination,FILE_REWRITE))
     { FileDelete(temp); return(false); }
   string committed="";
   if(!JPWProfileReadText(destination,committed) || committed!=content)
      return(false);
   JPWProfileEntry confirmed[];
   long confirmed_generation=0;
   int confirmed_slot=-1;
   if(JPWProfileLoadState(account,confirmed,confirmed_generation,
                          confirmed_slot)!=JPW_PROFILE_VALID ||
      confirmed_generation!=next || confirmed_slot!=target)
      return(false);
   return(true);
  }

bool JPWProfileSave(JPWAccount &account,JPWProfileEntry &entries[])
  {
   string key="";
   if(!JPWProfileAccountHash(account,key)) return(false);
   // Sem FILE_SHARE_READ/WRITE: o terminal concede um unico handle por conta.
   // O arquivo de lock pode permanecer; o handle e liberado mesmo se o script
   // terminar antes de gravar. Todos os relê/saves ocorrem sob este handle.
   const int lock=FileOpen(JPW_PROFILE_FOLDER+key+".lock",
                           FILE_READ|FILE_WRITE|FILE_BIN);
   if(lock==INVALID_HANDLE) return(false);
   const bool saved=JPWProfileSaveLocked(account,entries);
   FileClose(lock);
   return(saved);
  }

// Tick value fornece uma segunda observacao da unidade contratual. A rota
// armazenada pode estar antiga para uma estimativa; incoerencia ainda bloqueia.
bool JPWProfileTickConsistent(JPWInstrument &instrument,const double scale,
                              JPWAccount &account,JPWQuote &quotes[],
                              const long now_ms,const bool clock_valid,
                              const bool connected)
  {
   if(!JPWContractScaleValid(scale)) return(false);
   string target="";
   double divisor=0.0;
   if(!JPWAccountUnits(account.currency,target,divisor)) return(false);
   double tick_size=0.0;
   double profit_value=0.0;
   double loss_value=0.0;
   if(!SymbolInfoDouble(instrument.symbol,SYMBOL_TRADE_TICK_SIZE,tick_size) ||
      !SymbolInfoDouble(instrument.symbol,SYMBOL_TRADE_TICK_VALUE_PROFIT,profit_value) ||
      !SymbolInfoDouble(instrument.symbol,SYMBOL_TRADE_TICK_VALUE_LOSS,loss_value) ||
      !JPWFinitePositive(tick_size) || !JPWFinitePositive(profit_value) ||
      !JPWFinitePositive(loss_value)) return(false);
   double rate=1.0;
   if(instrument.profit!=target)
     {
      JPWRoute previous;
      previous.valid=false;
      JPWRoute chosen;
      bool estimated=false;
      long oldest=0;
      if(!JPWFindRouteReading(instrument.profit,target,quotes,now_ms,30,
                              clock_valid,connected,previous,chosen,rate,
                              estimated,oldest)) return(false);
     }
   const double expected=tick_size*instrument.contract_size*scale*rate*divisor;
   if(!JPWFinitePositive(expected)) return(false);
   return(MathAbs(profit_value-expected)<=expected*0.01 &&
          MathAbs(loss_value-expected)<=expected*0.01);
  }

#endif
