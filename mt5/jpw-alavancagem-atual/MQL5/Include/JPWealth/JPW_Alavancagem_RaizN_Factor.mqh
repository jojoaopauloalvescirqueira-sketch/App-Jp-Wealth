#ifndef JPW_ALAVANCAGEM_RAIZN_FACTOR_MQH
#define JPW_ALAVANCAGEM_RAIZN_FACTOR_MQH
#include <Math\Stat\Normal.mqh>
#include <JPWealth/JPW_Alavancagem_RaizN_Store.mqh>

// Escolha diagnostica local para os horizontes automaticos 1W/2W. Esta
// preferencia nao homologa P-21, nao altera N/F manual ou cenario declarado.
#define JPW_RAIZN_FACTOR_DEFAULT 1.5

struct JPWRaizNFactorPreference
  {
   string account_key;
   string symbol;
   long generation;
   double factor;
   datetime confirmed_at; // UTC observado pelo computador no ato de Aplicar.
  };

void JPWRaizNFactorClear(JPWRaizNFactorPreference &preference)
  {
   preference.account_key=""; preference.symbol="";
   preference.generation=0; preference.factor=0.0;
   preference.confirmed_at=0;
  }

bool JPWRaizNFactorAllowed(const double factor)
  { return(MathIsValidNumber(factor) && (factor==1.5 || factor==1.8)); }

// Probabilidade ideal de primeiro NAO toque de uma barreira adversa fixa
// criada em P0: 2*Phi(sqrt(8/pi)*F)-1. Nao mede SL real, chance de lucro,
// drift, gaps ou cobertura empirica. A saida e percentual (98.33 = 98.33%).
bool JPWRaizNNoTouchProbability(const double factor,double &percent)
  {
   percent=0.0;
   if(!JPWRaizNFactorAllowed(factor)) return(false);
   const double x=MathSqrt(8.0/3.14159265358979323846)*factor;
   if(!MathIsValidNumber(x) || x<=0.0) return(false);
   int error_code=0;
   const double cdf=MathCumulativeDistributionNormal(x,0.0,1.0,error_code);
   if(error_code!=0 || !MathIsValidNumber(cdf) || cdf<=0.5 || cdf>=1.0)
      return(false);
   const double result=100.0*(2.0*cdf-1.0);
   if(!MathIsValidNumber(result) || result<=0.0 || result>=100.0)
      return(false);
   percent=result;
   return(true);
  }

bool JPWRaizNFactorKey(const string server,const long login,
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
                         JPWRaizNFrame("raiz_n_factor_preference_v1");
   return(JPWRaizNHash(identity,key));
  }

string JPWRaizNFactorBase(const string folder,const string key)
  { return(folder+"rn_factor_"+StringSubstr(key,0,JPW_RAIZN_NAME_HEX)); }

bool JPWRaizNFactorValid(JPWRaizNFactorPreference &preference)
  {
   return(JPWRaizNIsHash(preference.account_key) &&
          JPWRaizNSymbolValid(preference.symbol) &&
          preference.generation>=1 && preference.generation<=1000000000 &&
          JPWRaizNFactorAllowed(preference.factor) &&
          preference.confirmed_at>0 &&
          (long)preference.confirmed_at<=5000000000);
  }

bool JPWRaizNFactorEncode(JPWRaizNFactorPreference &preference,
                          string &content)
  {
   content="";
   if(!JPWRaizNFactorValid(preference)) return(false);
   string symbol="";
   if(!JPWRaizNTextHex(preference.symbol,symbol)) return(false);
   const string body="JPW_RAIZN_FACTOR|1\nKEY|"+preference.account_key+
                     "\nSYMBOL_HEX|"+symbol+
                     "\nGEN|"+IntegerToString(preference.generation)+
                     "\nF|"+DoubleToString(preference.factor,-16)+
                     "\nCONFIRMED_UTC|"+
                        IntegerToString((long)preference.confirmed_at)+"\n";
   string hash="";
   if(!JPWRaizNHash(body,hash)) return(false);
   content=body+"SHA256|"+hash;
   return(StringLen(content)<=JPW_RAIZN_MAX_BYTES);
  }

JPW_RAIZN_STATE JPWRaizNFactorDecode(const string content,const string key,
                                     const string symbol,
                                     JPWRaizNFactorPreference &preference)
  {
   JPWRaizNFactorClear(preference);
   const int newline=StringFind(content,"\n");
   if(newline>0 && StringFind(content,"JPW_RAIZN_FACTOR|")==0 &&
      StringSubstr(content,0,newline)!="JPW_RAIZN_FACTOR|1")
      return(JPW_RAIZN_INCOMPATIBLE);
   string lines[];
   if(StringSplit(content,'\n',lines)!=7 ||
      lines[0]!="JPW_RAIZN_FACTOR|1" || lines[1]!="KEY|"+key ||
      StringFind(lines[2],"SYMBOL_HEX|")!=0 ||
      StringFind(lines[3],"GEN|")!=0 ||
      StringFind(lines[4],"F|")!=0 ||
      StringFind(lines[5],"CONFIRMED_UTC|")!=0 ||
      StringFind(lines[6],"SHA256|")!=0) return(JPW_RAIZN_INVALID);
   string body="",hash="";
   for(int i=0;i<6;i++) body+=lines[i]+"\n";
   if(!JPWRaizNHash(body,hash) || lines[6]!="SHA256|"+hash)
      return(JPW_RAIZN_INVALID);
   JPWRaizNFactorPreference parsed;
   JPWRaizNFactorClear(parsed); parsed.account_key=key;
   long confirmed=0;
   if(!JPWRaizNTextFromHex(StringSubstr(lines[2],11),parsed.symbol) ||
      parsed.symbol!=symbol ||
      !JPWRaizNUnsigned(StringSubstr(lines[3],4),1000000000,
                         parsed.generation) ||
      !JPWRaizNDouble(StringSubstr(lines[4],2),parsed.factor) ||
      !JPWRaizNUnsigned(StringSubstr(lines[5],14),5000000000,confirmed))
      return(JPW_RAIZN_INVALID);
   parsed.confirmed_at=(datetime)confirmed;
   string canonical="";
   if(!JPWRaizNFactorEncode(parsed,canonical) || canonical!=content)
      return(JPW_RAIZN_INVALID);
   preference=parsed;
   return(JPW_RAIZN_VALID);
  }

string JPWRaizNFactorReason(const JPW_RAIZN_STATE state)
  {
   switch(state)
     {
      case JPW_RAIZN_VALID: return("");
      case JPW_RAIZN_ABSENT: return("Sem escolha salva; F 1,5 diagnostico padrao.");
      case JPW_RAIZN_INVALID: return("Escolha de F invalida ou corrompida; dados preservados.");
      case JPW_RAIZN_INCOMPATIBLE: return("Versao da escolha de F incompativel; dados preservados.");
      case JPW_RAIZN_IO_ERROR: return("Leitura ou gravacao de F nao confirmada; dados preservados.");
      case JPW_RAIZN_BUSY: return("Escolha de F ocupada; tente novamente.");
      case JPW_RAIZN_ACCOUNT_UNAVAILABLE: return("Identidade da conta indisponivel.");
      case JPW_RAIZN_CONFLICT: return("F alterado por outra instancia; reabra Details antes de aplicar.");
     }
   return("Escolha de F indisponivel.");
  }

// Interno: exige lock exclusivo, nao cria nem repara slots em leitura.
JPW_RAIZN_STATE JPWRaizNFactorLoadLocked(const string base,const string key,
                                         const string symbol,
                                         JPWRaizNFactorPreference &preference,
                                         int &active)
  {
   JPWRaizNFactorClear(preference); active=-1;
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
      JPWRaizNFactorPreference found;
      const JPW_RAIZN_STATE state=JPWRaizNFactorDecode(content,key,symbol,found);
      if(state==JPW_RAIZN_INCOMPATIBLE) { incompatible=true; continue; }
      if(state!=JPW_RAIZN_VALID) continue;
      if(active>=0)
        {
         if(found.generation==preference.generation && content!=selected)
           { JPWRaizNFactorClear(preference); return(JPW_RAIZN_INVALID); }
         if(found.generation>preference.generation+1 ||
            preference.generation>found.generation+1)
           { JPWRaizNFactorClear(preference); return(JPW_RAIZN_INVALID); }
        }
      if(active<0 || found.generation>preference.generation)
        { preference=found; active=slot; selected=content; }
     }
   if(incompatible)
     { JPWRaizNFactorClear(preference); return(JPW_RAIZN_INCOMPATIBLE); }
   if(io_error)
     { JPWRaizNFactorClear(preference); return(JPW_RAIZN_IO_ERROR); }
   if(active>=0) return(JPW_RAIZN_VALID);
   return(exists ? JPW_RAIZN_INVALID : JPW_RAIZN_ABSENT);
  }

JPW_RAIZN_STATE JPWRaizNFactorLoad(const string folder,const string key,
                                   const string symbol,
                                   JPWRaizNFactorPreference &preference,
                                   string &reason)
  {
   JPWRaizNFactorClear(preference); reason="";
   if(!JPWRaizNFolderValid(folder) || !JPWRaizNIsHash(key) ||
      !JPWRaizNSymbolValid(symbol))
     { reason=JPWRaizNFactorReason(JPW_RAIZN_INVALID); return(JPW_RAIZN_INVALID); }
   const string base=JPWRaizNFactorBase(folder,key);
   const int lock=FileOpen(base+".lock",FILE_READ|FILE_BIN);
   if(lock==INVALID_HANDLE)
     {
      JPW_RAIZN_STATE state=JPW_RAIZN_ABSENT;
      if(FileIsExist(base+".lock")) state=JPW_RAIZN_BUSY;
      else if(FileIsExist(base+".a") || FileIsExist(base+".b"))
         state=JPW_RAIZN_IO_ERROR;
      reason=JPWRaizNFactorReason(state);
      return(state);
     }
   int active=-1;
   const JPW_RAIZN_STATE state=JPWRaizNFactorLoadLocked(base,key,symbol,
                                                         preference,active);
   FileClose(lock);
   reason=JPWRaizNFactorReason(state);
   return(state);
  }

// CAS da geracao sob o mesmo lock da releitura/escrita. Erros nao alteram o
// objeto do chamador; Cancelar nao chama esta funcao e nao grava preferencia.
JPW_RAIZN_STATE JPWRaizNFactorSave(const string folder,const string key,
                                   const string symbol,
                                   const long expected_generation,
                                   JPWRaizNFactorPreference &preference,
                                   string &reason)
  {
   reason="";
   if(!JPWRaizNFolderValid(folder) || !JPWRaizNIsHash(key) ||
      !JPWRaizNSymbolValid(symbol) || expected_generation<0 ||
      expected_generation>=1000000000 || preference.account_key!=key ||
      preference.symbol!=symbol)
     { reason=JPWRaizNFactorReason(JPW_RAIZN_INVALID); return(JPW_RAIZN_INVALID); }
   JPWRaizNFactorPreference next;
   next=preference; next.generation=expected_generation+1;
   string content="";
   if(!JPWRaizNFactorEncode(next,content))
     { reason=JPWRaizNFactorReason(JPW_RAIZN_INVALID); return(JPW_RAIZN_INVALID); }
   FolderCreate("JPWealth"); FolderCreate("JPWealth\\Alavancagem");
   FolderCreate(StringSubstr(folder,0,StringLen(folder)-1));
   const string base=JPWRaizNFactorBase(folder,key);
   const int lock=FileOpen(base+".lock",FILE_READ|FILE_WRITE|FILE_BIN);
   if(lock==INVALID_HANDLE)
     {
      const JPW_RAIZN_STATE state=(FileIsExist(base+".lock") ?
                                    JPW_RAIZN_BUSY : JPW_RAIZN_IO_ERROR);
      reason=JPWRaizNFactorReason(state); return(state);
     }
   JPWRaizNFactorPreference current; int active=-1;
   JPW_RAIZN_STATE state=JPWRaizNFactorLoadLocked(base,key,symbol,current,active);
   if((state==JPW_RAIZN_ABSENT && expected_generation!=0) ||
      (state==JPW_RAIZN_VALID && current.generation!=expected_generation))
      state=JPW_RAIZN_CONFLICT;
   if(state!=JPW_RAIZN_ABSENT && state!=JPW_RAIZN_VALID)
     { FileClose(lock); reason=JPWRaizNFactorReason(state); return(state); }
   const int target=(active==0 ? 1 : 0);
   const string destination=base+(target==0 ? ".a" : ".b");
   if(!JPWRaizNWriteVerified(base,destination,content))
     {
      FileClose(lock); reason=JPWRaizNFactorReason(JPW_RAIZN_IO_ERROR);
      return(JPW_RAIZN_IO_ERROR);
     }
   JPWRaizNFactorPreference checked; int checked_slot=-1;
   state=JPWRaizNFactorLoadLocked(base,key,symbol,checked,checked_slot);
   string checked_content="";
   if(state!=JPW_RAIZN_VALID || checked_slot!=target ||
      !JPWRaizNFactorEncode(checked,checked_content) || checked_content!=content)
     {
      FileClose(lock); reason=JPWRaizNFactorReason(JPW_RAIZN_IO_ERROR);
      return(JPW_RAIZN_IO_ERROR);
     }
   FileClose(lock);
   preference=checked;
   return(JPW_RAIZN_VALID);
  }
#endif
