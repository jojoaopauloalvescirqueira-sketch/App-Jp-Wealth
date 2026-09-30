#ifndef JPW_ALAVANCAGEM_RAIZN_CONFIG_MQH
#define JPW_ALAVANCAGEM_RAIZN_CONFIG_MQH
#include <JPWealth/JPW_Alavancagem_RaizN_Store.mqh>

// Configuracao do diagnostico corrente, separada dos cenarios declarados.
// N/F so entram por Aplicar. Leitura/Cancelamento nao criam nem reparam dados.
// A chave contem conta/instalacao/simbolo de forma opaca; nao usamos FILE_COMMON.
struct JPWRaizNConfig
  {
   string account_key;
   string symbol;
   long generation;
   int n;
   double f;
   string n_reason;
   string f_reason;
   datetime confirmed_at; // UTC observado pelo computador ao aplicar.
  };

void JPWRaizNConfigClear(JPWRaizNConfig &config)
  {
   config.account_key=""; config.symbol=""; config.generation=0;
   config.n=0; config.f=0.0; config.n_reason=""; config.f_reason="";
   config.confirmed_at=0;
  }

bool JPWRaizNConfigKey(const string server,const long login,
                         const string currency,const double scale,
                         const string installation,const string symbol,
                         string &key)
  {
   key="";
   const string normalized=JPWNormalizeCurrency(currency);
   string target=""; double expected_scale=0.0;
   if(server=="" || login<=0 || installation=="" ||
      !JPWRaizNSymbolValid(symbol) ||
      !JPWAccountUnits(normalized,target,expected_scale) ||
      !MathIsValidNumber(scale) || scale!=expected_scale) return(false);
   const string identity=JPWRaizNFrame(server)+
                         JPWRaizNFrame(IntegerToString(login))+
                         JPWRaizNFrame(normalized)+
                         JPWRaizNFrame(scale==100.0 ? "100" : "1")+
                         JPWRaizNFrame(installation)+
                         JPWRaizNFrame(symbol)+
                         JPWRaizNFrame("raiz_n_live_config_v1");
   return(JPWRaizNHash(identity,key));
  }

string JPWRaizNConfigBase(const string folder,const string key)
  { return(folder+"rn_cfg_"+StringSubstr(key,0,JPW_RAIZN_NAME_HEX)); }

bool JPWRaizNConfigReasonValid(const string value)
  {
   string trimmed=value;
   StringTrimLeft(trimmed); StringTrimRight(trimmed);
   if(trimmed=="") return(false);
   // Os campos sao linhas de texto; caracteres de controle nao sao rotulos.
   for(int i=0;i<StringLen(value);i++)
      if(StringGetCharacter(value,i)<32) return(false);
   string encoded="";
   return(JPWRaizNTextHex(value,encoded));
  }

bool JPWRaizNConfigValid(JPWRaizNConfig &config)
  {
   return(JPWRaizNIsHash(config.account_key) &&
          JPWRaizNSymbolValid(config.symbol) &&
          config.generation>=1 && config.generation<=1000000000 &&
          config.n>0 && JPWFinitePositive(config.f) &&
          JPWRaizNConfigReasonValid(config.n_reason) &&
          JPWRaizNConfigReasonValid(config.f_reason) &&
          config.confirmed_at>0 && (long)config.confirmed_at<=5000000000);
  }

bool JPWRaizNConfigEncode(JPWRaizNConfig &config,string &content)
  {
   content="";
   if(!JPWRaizNConfigValid(config)) return(false);
   string symbol="",n_reason="",f_reason="";
   if(!JPWRaizNTextHex(config.symbol,symbol) ||
      !JPWRaizNTextHex(config.n_reason,n_reason) ||
      !JPWRaizNTextHex(config.f_reason,f_reason)) return(false);
   const string body="JPW_RAIZN_CONFIG|1\nKEY|"+config.account_key+
                     "\nSYMBOL_HEX|"+symbol+
                     "\nGEN|"+IntegerToString(config.generation)+
                     "\nN_H4|"+IntegerToString(config.n)+
                     "\nF|"+DoubleToString(config.f,-16)+
                     "\nN_REASON_HEX|"+n_reason+
                     "\nF_REASON_HEX|"+f_reason+
                     "\nCONFIRMED_UTC|"+
                        IntegerToString((long)config.confirmed_at)+"\n";
   string hash="";
   if(!JPWRaizNHash(body,hash)) return(false);
   content=body+"SHA256|"+hash;
   return(StringLen(content)<=JPW_RAIZN_MAX_BYTES);
  }

JPW_RAIZN_STATE JPWRaizNConfigDecode(const string content,const string key,
                                       const string symbol,
                                       JPWRaizNConfig &config)
  {
   JPWRaizNConfigClear(config);
   const int newline=StringFind(content,"\n");
   if(newline>0 && StringFind(content,"JPW_RAIZN_CONFIG|")==0 &&
      StringSubstr(content,0,newline)!="JPW_RAIZN_CONFIG|1")
      return(JPW_RAIZN_INCOMPATIBLE);
   string lines[];
   if(StringSplit(content,'\n',lines)!=10 ||
      lines[0]!="JPW_RAIZN_CONFIG|1" || lines[1]!="KEY|"+key ||
      StringFind(lines[2],"SYMBOL_HEX|")!=0 ||
      StringFind(lines[3],"GEN|")!=0 ||
      StringFind(lines[4],"N_H4|")!=0 ||
      StringFind(lines[5],"F|")!=0 ||
      StringFind(lines[6],"N_REASON_HEX|")!=0 ||
      StringFind(lines[7],"F_REASON_HEX|")!=0 ||
      StringFind(lines[8],"CONFIRMED_UTC|")!=0 ||
      StringFind(lines[9],"SHA256|")!=0) return(JPW_RAIZN_INVALID);
   string body="",hash="";
   for(int i=0;i<9;i++) body+=lines[i]+"\n";
   if(!JPWRaizNHash(body,hash) || lines[9]!="SHA256|"+hash)
      return(JPW_RAIZN_INVALID);
   JPWRaizNConfig parsed;
   JPWRaizNConfigClear(parsed); parsed.account_key=key;
   long n=0,confirmed=0;
   if(!JPWRaizNTextFromHex(StringSubstr(lines[2],11),parsed.symbol) ||
      parsed.symbol!=symbol ||
      !JPWRaizNUnsigned(StringSubstr(lines[3],4),1000000000,
                         parsed.generation) ||
      !JPWRaizNUnsigned(StringSubstr(lines[4],5),INT_MAX,n) ||
      !JPWRaizNDouble(StringSubstr(lines[5],2),parsed.f) ||
      !JPWRaizNTextFromHex(StringSubstr(lines[6],13),parsed.n_reason) ||
      !JPWRaizNTextFromHex(StringSubstr(lines[7],13),parsed.f_reason) ||
      !JPWRaizNUnsigned(StringSubstr(lines[8],14),5000000000,confirmed))
      return(JPW_RAIZN_INVALID);
   parsed.n=(int)n; parsed.confirmed_at=(datetime)confirmed;
   string canonical="";
   if(!JPWRaizNConfigEncode(parsed,canonical) || canonical!=content)
      return(JPW_RAIZN_INVALID);
   config=parsed;
   return(JPW_RAIZN_VALID);
  }

string JPWRaizNConfigReason(const JPW_RAIZN_STATE state)
  {
   switch(state)
     {
      case JPW_RAIZN_VALID: return("");
      case JPW_RAIZN_ABSENT: return("Configure N e F para este instrumento.");
      case JPW_RAIZN_INVALID: return("Configuracao invalida ou corrompida; dados preservados.");
      case JPW_RAIZN_INCOMPATIBLE: return("Versao da configuracao incompativel; dados preservados.");
      case JPW_RAIZN_IO_ERROR: return("Leitura ou gravacao nao confirmada; confira o registro antes de reaplicar.");
      case JPW_RAIZN_BUSY: return("Configuracao ocupada ou acesso ao bloqueio recusado; tente aplicar depois.");
      case JPW_RAIZN_ACCOUNT_UNAVAILABLE: return("Identidade da conta indisponivel.");
      case JPW_RAIZN_CONFLICT: return("Configuracao alterada por outra instancia; reabra Details antes de aplicar.");
     }
   return("Configuracao indisponivel.");
  }

// Interno: exige lock exclusivo ja adquirido. Nao cria nem repara slots.
JPW_RAIZN_STATE JPWRaizNConfigLoadLocked(const string base,const string key,
                                         const string symbol,
                                         JPWRaizNConfig &config,int &active)
  {
   JPWRaizNConfigClear(config); active=-1;
   bool exists=false,io_error=false,incompatible=false;
   string selected="";
   for(int slot=0;slot<2;slot++)
     {
      const string path=base+(slot==0 ? ".a" : ".b");
      if(!FileIsExist(path)) continue;
      exists=true;
      string content="";
      const JPW_RAIZN_STATE read=JPWRaizNReadText(path,content);
      if(read==JPW_RAIZN_IO_ERROR) { io_error=true; continue; }
      if(read!=JPW_RAIZN_VALID) continue;
      JPWRaizNConfig found;
      const JPW_RAIZN_STATE state=JPWRaizNConfigDecode(content,key,symbol,found);
      if(state==JPW_RAIZN_INCOMPATIBLE) { incompatible=true; continue; }
      if(state!=JPW_RAIZN_VALID) continue;
      if(active>=0)
        {
         if(found.generation==config.generation && content!=selected)
           { JPWRaizNConfigClear(config); return(JPW_RAIZN_INVALID); }
         if(found.generation>config.generation+1 ||
            config.generation>found.generation+1)
           { JPWRaizNConfigClear(config); return(JPW_RAIZN_INVALID); }
        }
      if(active<0 || found.generation>config.generation)
        { config=found; active=slot; selected=content; }
     }
   if(incompatible)
     { JPWRaizNConfigClear(config); return(JPW_RAIZN_INCOMPATIBLE); }
   if(io_error)
     { JPWRaizNConfigClear(config); return(JPW_RAIZN_IO_ERROR); }
   if(active>=0) return(JPW_RAIZN_VALID);
   return(exists ? JPW_RAIZN_INVALID : JPW_RAIZN_ABSENT);
  }

JPW_RAIZN_STATE JPWRaizNConfigLoad(const string folder,const string key,
                                   const string symbol,JPWRaizNConfig &config,
                                   string &reason)
  {
   JPWRaizNConfigClear(config); reason="";
   if(!JPWRaizNFolderValid(folder) || !JPWRaizNIsHash(key) ||
      !JPWRaizNSymbolValid(symbol))
     { reason=JPWRaizNConfigReason(JPW_RAIZN_INVALID); return(JPW_RAIZN_INVALID); }
   const string base=JPWRaizNConfigBase(folder,key);
   // FILE_SHARE_READ/WRITE ausentes: o mesmo lock exclui leitor e escritor.
   const int lock=FileOpen(base+".lock",FILE_READ|FILE_BIN);
   if(lock==INVALID_HANDLE)
     {
      JPW_RAIZN_STATE state=JPW_RAIZN_ABSENT;
      if(FileIsExist(base+".lock")) state=JPW_RAIZN_BUSY;
      else if(FileIsExist(base+".a") || FileIsExist(base+".b"))
         state=JPW_RAIZN_IO_ERROR;
      reason=JPWRaizNConfigReason(state);
      return(state);
     }
   int active=-1;
   const JPW_RAIZN_STATE state=JPWRaizNConfigLoadLocked(base,key,symbol,config,active);
   FileClose(lock);
   reason=JPWRaizNConfigReason(state);
   return(state);
  }

// CAS de geracao sob o mesmo lock da leitura/escrita. So modifica config
// depois da releitura integral; erro nao pode ser apresentado como Aplicar.
JPW_RAIZN_STATE JPWRaizNConfigSave(const string folder,const string key,
                                   const string symbol,
                                   const long expected_generation,
                                   JPWRaizNConfig &config,string &reason)
  {
   reason="";
   if(!JPWRaizNFolderValid(folder) || !JPWRaizNIsHash(key) ||
      !JPWRaizNSymbolValid(symbol) || expected_generation<0 ||
      expected_generation>=1000000000 || config.account_key!=key ||
      config.symbol!=symbol)
     { reason=JPWRaizNConfigReason(JPW_RAIZN_INVALID); return(JPW_RAIZN_INVALID); }
   JPWRaizNConfig next;
   next=config; next.generation=expected_generation+1;
   string content="";
   if(!JPWRaizNConfigEncode(next,content))
     { reason=JPWRaizNConfigReason(JPW_RAIZN_INVALID); return(JPW_RAIZN_INVALID); }
   FolderCreate("JPWealth"); FolderCreate("JPWealth\\Alavancagem");
   FolderCreate(StringSubstr(folder,0,StringLen(folder)-1));
   const string base=JPWRaizNConfigBase(folder,key);
   const int lock=FileOpen(base+".lock",FILE_READ|FILE_WRITE|FILE_BIN);
   if(lock==INVALID_HANDLE)
     {
      const JPW_RAIZN_STATE state=(FileIsExist(base+".lock") ?
                                    JPW_RAIZN_BUSY : JPW_RAIZN_IO_ERROR);
      reason=JPWRaizNConfigReason(state); return(state);
     }
   JPWRaizNConfig current; int active=-1;
   JPW_RAIZN_STATE state=JPWRaizNConfigLoadLocked(base,key,symbol,current,active);
   if((state==JPW_RAIZN_ABSENT && expected_generation!=0) ||
      (state==JPW_RAIZN_VALID && current.generation!=expected_generation))
      state=JPW_RAIZN_CONFLICT;
   if(state!=JPW_RAIZN_ABSENT && state!=JPW_RAIZN_VALID)
     { FileClose(lock); reason=JPWRaizNConfigReason(state); return(state); }
   const int target=(active==0 ? 1 : 0);
   const string destination=base+(target==0 ? ".a" : ".b");
   if(!JPWRaizNWriteVerified(base,destination,content))
     {
      FileClose(lock); reason=JPWRaizNConfigReason(JPW_RAIZN_IO_ERROR);
      return(JPW_RAIZN_IO_ERROR);
     }
   JPWRaizNConfig checked; int checked_slot=-1;
   state=JPWRaizNConfigLoadLocked(base,key,symbol,checked,checked_slot);
   string checked_content="";
   if(state!=JPW_RAIZN_VALID || checked_slot!=target ||
      !JPWRaizNConfigEncode(checked,checked_content) || checked_content!=content)
     {
      FileClose(lock); reason=JPWRaizNConfigReason(JPW_RAIZN_IO_ERROR);
      return(JPW_RAIZN_IO_ERROR);
     }
   FileClose(lock);
   config=checked;
   return(JPW_RAIZN_VALID);
  }
#endif
