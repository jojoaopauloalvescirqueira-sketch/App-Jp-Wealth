#property copyright "JP Wealth"
#property version   "1.50"
#property description "Configuracao corrente Raiz N: fixtures locais sinteticas."
#include <JPWealth/JPW_Alavancagem_RaizN_Config.mqh>

// Somente em terminal isolado. Nenhuma leitura de conta, posicao ou cotacao.
// Cada execucao cria uma subpasta sintetica exclusiva, sem limpar dados antigos.
int g_cfg_pass=0,g_cfg_fail=0;

void ConfigAssert(const bool ok,const string label)
  {
   if(ok) g_cfg_pass++;
   else { g_cfg_fail++; Print("FAIL: ",label); }
  }

bool ConfigKey(const long login,const string symbol,string &key)
  {
   return(JPWRaizNConfigKey("SYNTH.CONFIG.SERVER",login,"USD",1.0,
                             "SYNTH.CONFIG.INSTALL",symbol,key));
  }

void ConfigFixture(const string key,const string symbol,JPWRaizNConfig &config)
  {
   JPWRaizNConfigClear(config);
   config.account_key=key; config.symbol=symbol;
   config.n=30; config.f=1.25;
   config.n_reason="Horizonte sintetico de 30 candles H4";
   config.f_reason="Fator sintetico declarado, sem valor universal";
   config.confirmed_at=D'2026.09.29 12:00:00';
  }

void ConfigTestCodecAndKeys()
  {
   const string symbol="SYNTH.EURUSD";
   string key="",other="";
   ConfigAssert(ConfigKey(993001,symbol,key),"base synthetic key");
   ConfigAssert(JPWRaizNConfigKey("SYNTH.CONFIG.SERVER",993001," usd ",1.0,
                   "SYNTH.CONFIG.INSTALL",symbol,other) && other==key,
                   "currency normalized, identity stable");
   ConfigAssert(ConfigKey(993002,symbol,other) && other!=key,"account isolation");
   ConfigAssert(ConfigKey(993001,"SYNTH.EURUSD.m",other) && other!=key,
                   "exact symbol includes broker suffix");
   ConfigAssert(ConfigKey(993001,"synth.eurusd",other) && other!=key,
                   "symbol case is not guessed");
   ConfigAssert(JPWRaizNConfigKey("SYNTH.OTHER.SERVER",993001,"USD",1.0,
                   "SYNTH.CONFIG.INSTALL",symbol,other) && other!=key,
                   "server isolation");
   ConfigAssert(JPWRaizNConfigKey("SYNTH.CONFIG.SERVER",993001,"USD",1.0,
                   "SYNTH.OTHER.INSTALL",symbol,other) && other!=key,
                   "installation isolation");
   ConfigAssert(JPWRaizNConfigKey("SYNTH.CONFIG.SERVER",993001,"USC",100.0,
                   "SYNTH.CONFIG.INSTALL",symbol,other) && other!=key,
                   "USC scale participates in opaque identity");
   ConfigAssert(!JPWRaizNConfigKey("SYNTH.CONFIG.SERVER",993001,"USC",1.0,
                   "SYNTH.CONFIG.INSTALL",symbol,other) && other=="",
                   "wrong USC account scale refused");
   ConfigAssert(!JPWRaizNConfigKey("SYNTH.CONFIG.SERVER",0,"USD",1.0,
                   "SYNTH.CONFIG.INSTALL",symbol,other),"missing login refused");
   JPWAccount account;
   account.login=993001; account.server="SYNTH.CONFIG.SERVER"; account.currency="USD";
   ConfigAssert(JPWRaizNAccountSymbolKey(account,symbol,"SYNTH.CONFIG.INSTALL",other) &&
                   other!=key,"live config domain separate from legacy scenario domain");
   ConfigAssert(JPWRaizNConfigBase(JPW_RAIZN_FOLDER,key)!=
                   JPWRaizNBase(JPW_RAIZN_FOLDER,other),"distinct filename namespace");

   JPWRaizNConfig value,decoded;
   ConfigFixture(key,symbol,value); value.generation=1;
   string content="";
   ConfigAssert(JPWRaizNConfigEncode(value,content),"valid codec encoded");
   ConfigAssert(JPWRaizNConfigDecode(content,key,symbol,decoded)==JPW_RAIZN_VALID &&
                   decoded.n==30 && decoded.f==1.25 && decoded.generation==1 &&
                   decoded.n_reason==value.n_reason && decoded.f_reason==value.f_reason,
                   "complete config round trip");
   string changed=content;
   StringReplace(changed,"N_H4|30","N_H4|31");
   ConfigAssert(JPWRaizNConfigDecode(changed,key,symbol,decoded)==JPW_RAIZN_INVALID &&
                   decoded.n==0,"checksum rejects edited configuration without fallback");
   ConfigAssert(JPWRaizNConfigDecode(content,key,"SYNTH.USDJPY",decoded)==
                   JPW_RAIZN_INVALID,"wrong symbol refused even with valid checksum");
   ConfigAssert(JPWRaizNConfigDecode("JPW_RAIZN_CONFIG|2\nFUTURE|1",key,symbol,decoded)==
                   JPW_RAIZN_INCOMPATIBLE,"future version distinct from corruption");
   value.n=0;
   ConfigAssert(!JPWRaizNConfigEncode(value,changed),"N missing has no default");
   value.n=30; value.f=0.0;
   ConfigAssert(!JPWRaizNConfigEncode(value,changed),"F missing has no default");
   value.f=1.25; value.n_reason="   ";
   ConfigAssert(!JPWRaizNConfigEncode(value,changed),"blank justification refused");
   value.n_reason="Synthetic"; value.f_reason="line\nbreak";
   ConfigAssert(!JPWRaizNConfigEncode(value,changed),"control characters refused");
  }

void ConfigTestLifecycle(const string folder)
  {
   const string symbol="SYNTH.EURUSD";
   string key="",reason="";
   ConfigAssert(ConfigKey(993101,symbol,key),"lifecycle key");
   const string base=JPWRaizNConfigBase(folder,key);
   JPWRaizNConfig value,loaded;
   ConfigAssert(JPWRaizNConfigLoad(folder,key,symbol,loaded,reason)==JPW_RAIZN_ABSENT &&
                   !FileIsExist(base+".lock") && loaded.n==0,
                   "first read absent, no lock or default created");
   ConfigFixture(key,symbol,value);
   ConfigAssert(JPWRaizNConfigSave(folder,key,symbol,0,value,reason)==JPW_RAIZN_VALID &&
                   value.generation==1,"explicit first Apply persists generation one");
   string before_a="",before_b="";
   ConfigAssert(JPWRaizNReadText(base+".a",before_a)==JPW_RAIZN_VALID,
                   "first generation receipt captured");
   JPWRaizNConfig cancelled;
   cancelled=value;
   cancelled.n=12; cancelled.f=2.0;
   // Cancelar descarta este rascunho: nenhuma chamada a Save.
   ConfigAssert(JPWRaizNConfigLoad(folder,key,symbol,loaded,reason)==JPW_RAIZN_VALID &&
                   loaded.n==30 && loaded.f==1.25 && loaded.generation==1,
                   "discarded draft leaves confirmed config unchanged");
   string after_a="";
   ConfigAssert(JPWRaizNReadText(base+".a",after_a)==JPW_RAIZN_VALID &&
                   before_a==after_a && !FileIsExist(base+".b"),
                   "read and Cancel preserve byte identity");

   JPWRaizNConfig stale;
   stale=value;
   value.n=31; value.confirmed_at++;
   ConfigAssert(JPWRaizNConfigSave(folder,key,symbol,1,value,reason)==JPW_RAIZN_VALID &&
                   value.generation==2,"second Apply rotates to generation two");
   ConfigAssert(JPWRaizNReadText(base+".a",after_a)==JPW_RAIZN_VALID &&
                   after_a==before_a && JPWRaizNReadText(base+".b",before_b)==JPW_RAIZN_VALID,
                   "rotation preserves prior generation");
   stale.n=99;
   ConfigAssert(JPWRaizNConfigSave(folder,key,symbol,1,stale,reason)==JPW_RAIZN_CONFLICT &&
                   stale.generation==1,"stale second-instance Apply refused");
   ConfigAssert(JPWRaizNConfigLoad(folder,key,symbol,loaded,reason)==JPW_RAIZN_VALID &&
                   loaded.generation==2 && loaded.n==31,"restart-style read takes newest generation");
   string checked="";
   ConfigAssert(JPWRaizNReadText(base+".b",checked)==JPW_RAIZN_VALID && checked==before_b,
                   "conflicting Apply cannot mutate active slot");
   string other="";
   ConfigAssert(ConfigKey(993102,symbol,other) &&
                   JPWRaizNConfigLoad(folder,other,symbol,loaded,reason)==JPW_RAIZN_ABSENT,
                   "account switch cannot reuse another config");

   const int held=FileOpen(base+".lock",FILE_READ|FILE_WRITE|FILE_BIN);
   ConfigAssert(held!=INVALID_HANDLE,"exclusive test lock acquired");
   if(held!=INVALID_HANDLE)
     {
      ConfigAssert(JPWRaizNConfigLoad(folder,key,symbol,loaded,reason)==JPW_RAIZN_BUSY,
                      "concurrent read refuses immediately");
      ConfigAssert(JPWRaizNConfigSave(folder,key,symbol,2,value,reason)==JPW_RAIZN_BUSY,
                      "concurrent Apply refuses immediately");
      FileClose(held);
     }
   ConfigAssert(JPWRaizNConfigLoad(folder,key,symbol,loaded,reason)==JPW_RAIZN_VALID &&
                   loaded.generation==2,"lock released after read and conflict");
   const int after=FileOpen(base+".lock",FILE_READ|FILE_WRITE|FILE_BIN);
   ConfigAssert(after!=INVALID_HANDLE,"load leaves no retained lock");
   if(after!=INVALID_HANDLE) FileClose(after);
   ConfigAssert(JPWRaizNConfigSave(folder,key,symbol,LONG_MAX,value,reason)==JPW_RAIZN_INVALID,
                   "generation overflow refused before arithmetic");

   string usc_key="";
   ConfigAssert(JPWRaizNConfigKey("SYNTH.CONFIG.SERVER",993103,"USC",100.0,
                   "SYNTH.CONFIG.INSTALL",symbol,usc_key),"USC lifecycle key");
   ConfigFixture(usc_key,symbol,value);
   ConfigAssert(JPWRaizNConfigSave(folder,usc_key,symbol,0,value,reason)==JPW_RAIZN_VALID &&
                   JPWRaizNConfigLoad(folder,usc_key,symbol,loaded,reason)==JPW_RAIZN_VALID &&
                   loaded.n==30 && loaded.f==1.25,
                   "USC config preserves dimensionless N and F without scaling");
  }

void ConfigTestRecovery(const string folder)
  {
   const string symbol="SYNTH.XAUUSD";
   string key="",reason="";
   ConfigAssert(ConfigKey(993201,symbol,key),"recovery key");
   const string base=JPWRaizNConfigBase(folder,key);
   JPWRaizNConfig value,loaded;
   ConfigFixture(key,symbol,value);
   ConfigAssert(JPWRaizNConfigSave(folder,key,symbol,0,value,reason)==JPW_RAIZN_VALID,
                   "recovery baseline saved");
   string first="";
   ConfigAssert(JPWRaizNReadText(base+".a",first)==JPW_RAIZN_VALID,
                   "recovery baseline bytes captured");
   ConfigAssert(JPWRaizNWriteText(base+".b","JPW_RAIZN_CONFIG|1\nKEY|truncated"),
                   "simulate interrupted alternate-slot write");
   ConfigAssert(JPWRaizNConfigLoad(folder,key,symbol,loaded,reason)==JPW_RAIZN_VALID &&
                   loaded.generation==1 && loaded.n==30,
                   "valid slot recovers truncated alternate without fallback defaults");
   string checked="";
   ConfigAssert(JPWRaizNReadText(base+".a",checked)==JPW_RAIZN_VALID && checked==first,
                   "recovery read never repairs original bytes");
   value.n=32;
   ConfigAssert(JPWRaizNConfigSave(folder,key,symbol,1,value,reason)==JPW_RAIZN_VALID &&
                   value.generation==2,"explicit Apply can replace interrupted alternate");

   const int denied=FileOpen(base+".b",FILE_READ|FILE_BIN);
   ConfigAssert(denied!=INVALID_HANDLE,"simulate unavailable active slot");
   if(denied!=INVALID_HANDLE)
     {
      ConfigAssert(JPWRaizNConfigSave(folder,key,symbol,2,value,reason)==JPW_RAIZN_IO_ERROR,
                      "incomplete read refuses write despite other valid slot");
      FileClose(denied);
     }
   ConfigAssert(JPWRaizNReadText(base+".a",checked)==JPW_RAIZN_VALID && checked==first,
                   "refused write preserves prior slot");
   ConfigAssert(JPWRaizNWriteText(base+".a","corrupt A") &&
                   JPWRaizNWriteText(base+".b","corrupt B"),"simulate both corrupted slots");
   ConfigAssert(JPWRaizNConfigLoad(folder,key,symbol,loaded,reason)==JPW_RAIZN_INVALID &&
                   loaded.n==0,"both corrupt slots block, never synthesize defaults");
   ConfigAssert(JPWRaizNConfigSave(folder,key,symbol,2,value,reason)==JPW_RAIZN_INVALID,
                   "both corrupt slots cannot be silently overwritten");
   ConfigAssert(JPWRaizNReadText(base+".a",checked)==JPW_RAIZN_VALID && checked=="corrupt A",
                   "corrupt original preserved for diagnosis");

   ConfigAssert(ConfigKey(993202,symbol,key),"future-version key");
   ConfigFixture(key,symbol,value);
   ConfigAssert(JPWRaizNConfigSave(folder,key,symbol,0,value,reason)==JPW_RAIZN_VALID,
                   "future-version baseline saved");
   const string future=JPWRaizNConfigBase(folder,key);
   ConfigAssert(JPWRaizNWriteText(future+".b","JPW_RAIZN_CONFIG|2\nFUTURE|1"),
                   "simulate future slot beside supported slot");
   ConfigAssert(JPWRaizNConfigLoad(folder,key,symbol,loaded,reason)==JPW_RAIZN_INCOMPATIBLE,
                   "future slot blocks fallback to old supported version");
   ConfigAssert(JPWRaizNConfigSave(folder,key,symbol,1,value,reason)==JPW_RAIZN_INCOMPATIBLE,
                   "future version cannot be overwritten");

   ConfigAssert(ConfigKey(993203,symbol,key),"ambiguous generations key");
   ConfigFixture(key,symbol,value);
   ConfigAssert(JPWRaizNConfigSave(folder,key,symbol,0,value,reason)==JPW_RAIZN_VALID,
                   "ambiguous-generation baseline saved");
   value.n=41;
   string conflicting="";
   ConfigAssert(JPWRaizNConfigEncode(value,conflicting) &&
                   JPWRaizNWriteText(JPWRaizNConfigBase(folder,key)+".b",conflicting),
                   "simulate different content with same generation");
   ConfigAssert(JPWRaizNConfigLoad(folder,key,symbol,loaded,reason)==JPW_RAIZN_INVALID,
                   "equal generations cannot disagree");
   ConfigAssert(JPWRaizNConfigSave(folder,key,symbol,1,value,reason)==JPW_RAIZN_INVALID,
                   "ambiguous generation blocks Apply");
  }

void ConfigTestLegacyPreserved(const string folder)
  {
   JPWAccount account;
   account.server="SYNTH.CONFIG.SERVER"; account.login=993301; account.currency="USD";
   const string symbol="SYNTH.NZDUSD",installation="SYNTH.CONFIG.INSTALL";
   string legacy_key="",key="",reason="";
   ConfigAssert(JPWRaizNAccountSymbolKey(account,symbol,installation,legacy_key) &&
                   ConfigKey(account.login,symbol,key),"legacy and live identities available");
   JPWRaizNScenario scenario;
   JPWRaizNClearScenario(scenario);
   scenario.schema=1; scenario.model_version=JPW_RAIZN_MODEL_VERSION;
   scenario.account_key=legacy_key; scenario.symbol=symbol;
   scenario.p0=100.0; scenario.p0_origin="SYNTH DECLARED";
   scenario.decision_server_time=D'2026.09.29 08:00:00';
   scenario.atr=0.4; scenario.atr_source="DECLARED";
   scenario.atr_provenance="synthetic"; scenario.atr_variant="synthetic ATR";
   scenario.atr_bar_server_time=D'2026.09.29 04:00:00';
   scenario.n_h4=30; scenario.n_reason="synthetic";
   scenario.factor=1.25; scenario.factor_status="DECLARED";
   scenario.factor_reason="synthetic";
   scenario.confirmed_at_utc=D'2026.09.29 08:01:00';
   scenario.declared_side=1;
   JPWRaizNScenario confirmed;
   ConfigAssert(JPWRaizNConfirm(account,symbol,installation,folder,scenario,"",confirmed)==
                   JPW_RAIZN_VALID,"synthetic legacy scenario confirmed");
   const string old_base=JPWRaizNScenarioBase(folder,legacy_key,confirmed.scenario_id);
   string before_a="",before_b="",before_pointer="";
   ConfigAssert(JPWRaizNReadText(old_base+".a",before_a)==JPW_RAIZN_VALID &&
                   JPWRaizNReadText(old_base+".b",before_b)==JPW_RAIZN_VALID &&
                   JPWRaizNReadText(JPWRaizNBase(folder,legacy_key)+".active.a",before_pointer)==
                      JPW_RAIZN_VALID,"capture real legacy-format bytes");
   JPWRaizNConfig value;
   ConfigFixture(key,symbol,value);
   ConfigAssert(JPWRaizNConfigSave(folder,key,symbol,0,value,reason)==JPW_RAIZN_VALID,
                   "live config beside legacy scenario");
   value.n=40;
   ConfigAssert(JPWRaizNConfigSave(folder,key,symbol,1,value,reason)==JPW_RAIZN_VALID,
                   "revise live N without scenario mutation");
   string after_a="",after_b="",after_pointer="";
   ConfigAssert(JPWRaizNReadText(old_base+".a",after_a)==JPW_RAIZN_VALID &&
                   JPWRaizNReadText(old_base+".b",after_b)==JPW_RAIZN_VALID &&
                   JPWRaizNReadText(JPWRaizNBase(folder,legacy_key)+".active.a",after_pointer)==
                      JPW_RAIZN_VALID &&
                   before_a==after_a && before_b==after_b && before_pointer==after_pointer,
                   "both legacy scenario slots and active pointer remain byte-identical");
   JPWRaizNBinding binding;
   ConfigAssert(JPWRaizNReadActive(account,symbol,installation,folder,scenario,binding)==
                   JPW_RAIZN_VALID && scenario.scenario_id==confirmed.scenario_id &&
                   scenario.n_h4==30,"advanced scenario still loads its original N");
  }

void OnStart()
  {
   const string root=JPW_RAIZN_FOLDER+"SyntheticRaizNConfigTests\\";
   const string folder=root+IntegerToString((long)TimeLocal())+"_"+
                       IntegerToString((long)GetTickCount64())+"\\";
   FolderCreate("JPWealth"); FolderCreate("JPWealth\\Alavancagem");
   FolderCreate(StringSubstr(root,0,StringLen(root)-1));
   if(!FolderCreate(StringSubstr(folder,0,StringLen(folder)-1)))
     { Print("JPW RaizN config tests NOT_RUN: synthetic folder unavailable"); return; }
   ConfigTestCodecAndKeys();
   ConfigTestLifecycle(folder);
   ConfigTestRecovery(folder);
   ConfigTestLegacyPreserved(folder);
   if(g_cfg_fail==0)
      PrintFormat("JPW_Alavancagem_RaizN_Config_Tests PASS: %d asserts",g_cfg_pass);
   else
      PrintFormat("JPW_Alavancagem_RaizN_Config_Tests FAIL: %d of %d asserts",
                  g_cfg_fail,g_cfg_pass+g_cfg_fail);
  }
