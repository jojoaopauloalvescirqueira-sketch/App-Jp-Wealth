#property copyright "JP Wealth"
#property version   "1.70"
#property description "F diagnostico e nao toque teorico: fixtures locais sinteticas."
#include <JPWealth/JPW_Alavancagem_RaizN_Factor.mqh>
#include <JPWealth/JPW_Alavancagem_RaizN_Config.mqh>

// Somente em terminal MT5 isolado. Nao le conta, posicoes nem cotacoes reais.
// Cada execucao usa uma subpasta sintetica exclusiva e nao limpa outros dados.
int g_factor_pass=0,g_factor_fail=0;

void FactorAssert(const bool ok,const string label)
  {
   if(ok) g_factor_pass++;
   else { g_factor_fail++; Print("FAIL: ",label); }
  }

bool FactorKey(const long login,const string symbol,string &key)
  {
   return(JPWRaizNFactorKey("SYNTH.FACTOR.SERVER",login,"USD",1.0,
                            "SYNTH.FACTOR.INSTALL",symbol,key));
  }

void FactorFixture(const string key,const string symbol,
                   JPWRaizNFactorPreference &preference)
  {
   JPWRaizNFactorClear(preference);
   preference.account_key=key; preference.symbol=symbol;
   preference.factor=1.5;
   preference.confirmed_at=D'2026.09.29 12:00:00';
  }

void FactorTestMath()
  {
   double p15=0.0,p18=0.0,none=0.0;
   FactorAssert(JPWRaizNFactorAllowed(1.5) &&
                JPWRaizNFactorAllowed(1.8) &&
                !JPWRaizNFactorAllowed(1.25) &&
                !JPWRaizNFactorAllowed(0.0),
                "only approved diagnostic options accepted");
   FactorAssert(JPWRaizNNoTouchProbability(1.5,p15) &&
                MathAbs(p15-98.33185087499388)<0.00001,
                "F1.5 theoretical first non-touch reference");
   FactorAssert(JPWRaizNNoTouchProbability(1.8,p18) &&
                MathAbs(p18-99.59261292949151)<0.00001 && p18>p15,
                "F1.8 theoretical first non-touch reference");
   none=77.0;
   FactorAssert(!JPWRaizNNoTouchProbability(1.25,none) && none==0.0,
                "unsupported F has no probability");
   double d1=0.0,d2=0.0,pct1=0.0,pct2=0.0;
   FactorAssert(JPWRaizNCalculate(100.0,0.4,30,1.5,d1,pct1)==JPW_RAIZN_OK &&
                JPWRaizNCalculate(100.0,0.4,60,1.5,d2,pct2)==JPW_RAIZN_OK &&
                MathAbs(d1-0.4*MathSqrt(30.0)*1.5)<1e-12 &&
                MathAbs(d2-0.4*MathSqrt(60.0)*1.5)<1e-12 &&
                d2>d1 && pct2>pct1,
                "1W/2W distance depends on N with same F");
   double same=0.0;
   FactorAssert(JPWRaizNNoTouchProbability(1.5,same) && same==p15,
                "theoretical probability independent of horizon N");
   FactorAssert(JPWRaizNCalculate(100.0,0.4,30,1.8,d1,pct1)==JPW_RAIZN_OK &&
                MathAbs(pct1-100.0*(0.4*MathSqrt(30.0)*1.8)/100.0)<1e-12,
                "F1.8 scales price and percent without changing base units");
  }

void FactorTestCodecAndIdentity()
  {
   const string symbol="SYNTH.NZDUSD.m";
   string key="",other="",legacy="";
   FactorAssert(FactorKey(991001,symbol,key),"synthetic key generated");
   FactorAssert(JPWRaizNFactorKey("SYNTH.FACTOR.SERVER",991001," usd ",1.0,
                  "SYNTH.FACTOR.INSTALL",symbol,other) && other==key,
                  "currency normalized");
   FactorAssert(FactorKey(991002,symbol,other) && other!=key,
                "account isolation");
   FactorAssert(FactorKey(991001,"SYNTH.NZDUSD",other) && other!=key,
                "exact broker symbol isolation");
   FactorAssert(JPWRaizNFactorKey("SYNTH.OTHER.SERVER",991001,"USD",1.0,
                  "SYNTH.FACTOR.INSTALL",symbol,other) && other!=key,
                  "server isolation");
   FactorAssert(JPWRaizNFactorKey("SYNTH.FACTOR.SERVER",991001,"USD",1.0,
                  "SYNTH.OTHER.INSTALL",symbol,other) && other!=key,
                  "installation isolation");
   FactorAssert(JPWRaizNFactorKey("SYNTH.FACTOR.SERVER",991001,"USC",100.0,
                  "SYNTH.FACTOR.INSTALL",symbol,other) && other!=key,
                  "USC identity distinct without changing price scale");
   FactorAssert(!JPWRaizNFactorKey("SYNTH.FACTOR.SERVER",991001,"USC",1.0,
                  "SYNTH.FACTOR.INSTALL",symbol,other) && other=="",
                  "wrong USC scale refused");
   FactorAssert(!JPWRaizNFactorKey("SYNTH.FACTOR.SERVER",0,"USD",1.0,
                  "SYNTH.FACTOR.INSTALL",symbol,other),
                  "unknown account refused");
   FactorAssert(JPWRaizNConfigKey("SYNTH.FACTOR.SERVER",991001,"USD",1.0,
                  "SYNTH.FACTOR.INSTALL",symbol,legacy) && legacy!=key &&
                  JPWRaizNFactorBase(JPW_RAIZN_FOLDER,key)!=
                  JPWRaizNConfigBase(JPW_RAIZN_FOLDER,legacy),
                  "new factor store separate from legacy manual N/F");

   JPWRaizNFactorPreference preference,decoded;
   FactorFixture(key,symbol,preference); preference.generation=1;
   string content="";
   FactorAssert(JPWRaizNFactorEncode(preference,content),"valid codec encoded");
   FactorAssert(JPWRaizNFactorDecode(content,key,symbol,decoded)==JPW_RAIZN_VALID &&
                decoded.factor==1.5 && decoded.generation==1 &&
                decoded.confirmed_at==preference.confirmed_at,
                "factor preference canonical round trip");
   string changed=content;
   StringReplace(changed,"F|1.5","F|1.8");
   FactorAssert(JPWRaizNFactorDecode(changed,key,symbol,decoded)==JPW_RAIZN_INVALID &&
                decoded.factor==0.0,"checksum blocks edited F");
   FactorAssert(JPWRaizNFactorDecode(content,key,"SYNTH.USDJPY",decoded)==
                JPW_RAIZN_INVALID,"wrong symbol refused");
   FactorAssert(JPWRaizNFactorDecode("JPW_RAIZN_FACTOR|2\nFUTURE|1",key,symbol,
                                      decoded)==JPW_RAIZN_INCOMPATIBLE,
                "future schema distinct from corruption");
   preference.factor=1.25;
   FactorAssert(!JPWRaizNFactorEncode(preference,changed),
                "unsupported factor cannot persist");
  }

void FactorTestLifecycle(const string folder)
  {
   const string symbol="SYNTH.NZDUSD.m";
   string key="",reason="";
   FactorAssert(FactorKey(991101,symbol,key),"lifecycle key");
   const string base=JPWRaizNFactorBase(folder,key);
   JPWRaizNFactorPreference preference,loaded;
   FactorAssert(JPWRaizNFactorLoad(folder,key,symbol,loaded,reason)==JPW_RAIZN_ABSENT &&
                loaded.factor==0.0 && !FileIsExist(base+".lock") &&
                JPW_RAIZN_FACTOR_DEFAULT==1.5,
                "absent preference permits explicit default without writing");
   FactorFixture(key,symbol,preference);
   FactorAssert(JPWRaizNFactorSave(folder,key,symbol,0,preference,reason)==JPW_RAIZN_VALID &&
                preference.generation==1,"first Apply saves F1.5");
   string first="",after="";
   FactorAssert(JPWRaizNReadText(base+".a",first)==JPW_RAIZN_VALID,
                "first slot captured");
   JPWRaizNFactorPreference draft;
   draft=preference; draft.factor=1.8;
   // Cancelar nao chama Save; o registro persistido continua byte-identico.
   FactorAssert(JPWRaizNFactorLoad(folder,key,symbol,loaded,reason)==JPW_RAIZN_VALID &&
                loaded.factor==1.5 && loaded.generation==1,
                "Cancel leaves active F unchanged");
   FactorAssert(JPWRaizNReadText(base+".a",after)==JPW_RAIZN_VALID &&
                after==first && !FileIsExist(base+".b"),
                "Cancel and read preserve bytes");
   FactorAssert(JPWRaizNFactorSave(folder,key,symbol,1,draft,reason)==JPW_RAIZN_VALID &&
                draft.factor==1.8 && draft.generation==2,
                "Apply F1.8 advances generation");
   FactorAssert(JPWRaizNFactorLoad(folder,key,symbol,loaded,reason)==JPW_RAIZN_VALID &&
                loaded.factor==1.8 && loaded.generation==2,
                "restart restores selected F1.8");
   FactorAssert(JPWRaizNReadText(base+".a",after)==JPW_RAIZN_VALID &&
                after==first && FileIsExist(base+".b"),
                "previous generation survives slot rotation");
   JPWRaizNFactorPreference stale;
   stale=preference; stale.factor=1.5;
   FactorAssert(JPWRaizNFactorSave(folder,key,symbol,1,stale,reason)==JPW_RAIZN_CONFLICT &&
                stale.generation==1,"second instance stale Apply refused");
   string other="";
   FactorAssert(FactorKey(991102,symbol,other) &&
                JPWRaizNFactorLoad(folder,other,symbol,loaded,reason)==JPW_RAIZN_ABSENT,
                "other account does not inherit F1.8");

   const int held=FileOpen(base+".lock",FILE_READ|FILE_WRITE|FILE_BIN);
   FactorAssert(held!=INVALID_HANDLE,"exclusive lock acquired for contention");
   if(held!=INVALID_HANDLE)
     {
      FactorAssert(JPWRaizNFactorLoad(folder,key,symbol,loaded,reason)==JPW_RAIZN_BUSY,
                   "busy load refuses immediately");
      FactorAssert(JPWRaizNFactorSave(folder,key,symbol,2,draft,reason)==JPW_RAIZN_BUSY,
                   "busy Apply refuses immediately");
      FileClose(held);
     }
  }

void FactorTestCorruption(const string folder)
  {
   const string symbol="SYNTH.NZDUSD.m";
   string key="",reason="",first="",after="";
   FactorAssert(FactorKey(991201,symbol,key),"recovery key");
   JPWRaizNFactorPreference preference,loaded;
   FactorFixture(key,symbol,preference);
   FactorAssert(JPWRaizNFactorSave(folder,key,symbol,0,preference,reason)==JPW_RAIZN_VALID,
                "recovery baseline saved");
   const string base=JPWRaizNFactorBase(folder,key);
   FactorAssert(JPWRaizNReadText(base+".a",first)==JPW_RAIZN_VALID,
                "recovery baseline bytes captured");
   FactorAssert(JPWRaizNWriteText(base+".b","partial generation"),
                "simulate interrupted alternate slot");
   FactorAssert(JPWRaizNFactorLoad(folder,key,symbol,loaded,reason)==JPW_RAIZN_VALID &&
                loaded.factor==1.5 && loaded.generation==1,
                "one valid slot recovers without silent default");
   FactorAssert(JPWRaizNReadText(base+".a",after)==JPW_RAIZN_VALID && after==first,
                "read does not repair surviving slot");
   preference.factor=1.8;
   FactorAssert(JPWRaizNFactorSave(folder,key,symbol,1,preference,reason)==JPW_RAIZN_VALID &&
                preference.generation==2,"explicit Apply replaces partial alternate");
   FactorAssert(JPWRaizNWriteText(base+".a","corrupt A") &&
                JPWRaizNWriteText(base+".b","corrupt B"),
                "simulate both slots corrupted");
   FactorAssert(JPWRaizNFactorLoad(folder,key,symbol,loaded,reason)==JPW_RAIZN_INVALID &&
                loaded.factor==0.0 &&
                JPWRaizNFactorSave(folder,key,symbol,2,preference,reason)==JPW_RAIZN_INVALID,
                "both corrupt slots block default and overwrite");

   FactorAssert(FactorKey(991202,symbol,key),"future-version key");
   FactorFixture(key,symbol,preference);
   FactorAssert(JPWRaizNFactorSave(folder,key,symbol,0,preference,reason)==JPW_RAIZN_VALID,
                "future-version baseline saved");
   const string future=JPWRaizNFactorBase(folder,key);
   FactorAssert(JPWRaizNWriteText(future+".b","JPW_RAIZN_FACTOR|2\nFUTURE|1"),
                "simulate future schema beside supported slot");
   FactorAssert(JPWRaizNFactorLoad(folder,key,symbol,loaded,reason)==JPW_RAIZN_INCOMPATIBLE &&
                loaded.factor==0.0 &&
                JPWRaizNFactorSave(folder,key,symbol,1,preference,reason)==
                   JPW_RAIZN_INCOMPATIBLE,
                "future schema blocks fallback and overwrite");

   FactorAssert(FactorKey(991203,symbol,key),"ambiguous-generation key");
   FactorFixture(key,symbol,preference);
   FactorAssert(JPWRaizNFactorSave(folder,key,symbol,0,preference,reason)==JPW_RAIZN_VALID,
                "ambiguous-generation baseline saved");
   preference.factor=1.8;
   string conflicting="";
   FactorAssert(JPWRaizNFactorEncode(preference,conflicting) &&
                JPWRaizNWriteText(JPWRaizNFactorBase(folder,key)+".b",conflicting),
                "simulate conflicting same generation");
   FactorAssert(JPWRaizNFactorLoad(folder,key,symbol,loaded,reason)==JPW_RAIZN_INVALID &&
                JPWRaizNFactorSave(folder,key,symbol,1,preference,reason)==JPW_RAIZN_INVALID,
                "same-generation divergence blocks use and Apply");
  }

void OnStart()
  {
   const string root=JPW_RAIZN_FOLDER+"SyntheticFactorTests\\";
   const string folder=root+IntegerToString((long)TimeLocal())+"_"+
                       IntegerToString((long)GetTickCount64())+"\\";
   FolderCreate("JPWealth"); FolderCreate("JPWealth\\Alavancagem");
   FolderCreate(StringSubstr(root,0,StringLen(root)-1));
   if(!FolderCreate(StringSubstr(folder,0,StringLen(folder)-1)))
     { Print("JPW factor tests NOT_RUN: synthetic folder unavailable"); return; }
   FactorTestMath();
   FactorTestCodecAndIdentity();
   FactorTestLifecycle(folder);
   FactorTestCorruption(folder);
   if(g_factor_fail==0)
      PrintFormat("JPW RaizN factor PASS: %d asserts",g_factor_pass);
   else PrintFormat("JPW RaizN factor PRODUCT_FAIL: %d/%d failed",
                    g_factor_fail,g_factor_pass+g_factor_fail);
  }
