#property copyright "JP Wealth"
#property version   "1.40"
#property description "Testes sinteticos de persistencia local da Raiz N."

#include <JPWealth/JPW_Alavancagem_RaizN_Store.mqh>

// Executar apenas em terminal isolado. Nao acessa identidade, cotacao ou
// posicao real; os registros de teste ficam em subpasta unica sintetica.
int g_raizn_store_passes=0;
int g_raizn_store_failures=0;

void JPWRaizNStoreAssert(const bool condition,const string label)
  {
   if(condition) g_raizn_store_passes++;
   else
     {
      g_raizn_store_failures++;
      Print("FAIL: ",label);
     }
  }

void JPWRaizNStoreAccount(JPWAccount &account,const long login,
                          const string currency)
  {
   account.login=login;
   account.server="SYNTHETIC.RAIZN.TEST";
   account.currency=currency;
  }

void JPWRaizNStoreFixture(JPWRaizNScenario &record,const string key,
                          const string symbol)
  {
   JPWRaizNClearScenario(record);
   record.schema=1;
   record.model_version=JPW_RAIZN_MODEL_VERSION;
   record.account_key=key;
   record.symbol=symbol;
   record.p0=1.2;
   record.p0_origin="DECLARED SYNTHETIC";
   record.decision_server_time=D'2026.09.28 08:00:00';
   record.atr=0.01;
   record.atr_source="DECLARED";
   record.atr_provenance="synthetic fixture";
   record.atr_variant="ATR55 H4 synthetic";
   record.atr_bar_server_time=D'2026.09.28 04:00:00';
   record.n_h4=4;
   record.n_reason="synthetic interval";
   record.factor=1.25;
   record.factor_status="DECLARED";
   record.factor_source="";
   record.factor_reason="synthetic declaration";
   record.confirmed_at_utc=D'2026.09.28 08:01:00';
   record.retrospective=false;
   record.declared_side=1;
  }

void JPWRaizNStoreTestCodec(JPWAccount &account,const string symbol,
                            const string installation_id)
  {
   string key="";
   JPWRaizNStoreAssert(JPWRaizNAccountSymbolKey(account,symbol,
                                                installation_id,key),
                        "synthetic account-symbol-installation key");
   JPWRaizNScenario record;
   JPWRaizNStoreFixture(record,key,symbol);
   string content="";
   JPWRaizNStoreAssert(JPWRaizNEncodeScenario(record,content) &&
                        JPWRaizNIsHash(record.scenario_id),
                        "scenario receipt is content hash");
   JPWRaizNScenario decoded;
   JPWRaizNStoreAssert(JPWRaizNDecodeScenario(content,key,
                                              record.scenario_id,decoded)==
                        JPW_RAIZN_VALID && decoded.p0==record.p0 &&
                        decoded.atr==record.atr &&
                        decoded.n_h4==record.n_h4 &&
                        decoded.factor==record.factor &&
                        decoded.model_version==JPW_RAIZN_MODEL_VERSION,
                        "scenario codec round trip");
   string altered=content;
   const int changed=StringReplace(altered,"P0|","P0|9");
   JPWRaizNStoreAssert(changed==1 &&
                        JPWRaizNDecodeScenario(altered,key,
                                               record.scenario_id,decoded)==
                        JPW_RAIZN_INVALID,
                        "modified scenario rejected by receipt");
   JPWRaizNStoreAssert(JPWRaizNDecodeScenario(
                        "JPW_RAIZN_SCENARIO|2\nFUTURE|1",key,
                        record.scenario_id,decoded)==JPW_RAIZN_INCOMPATIBLE,
                        "future scenario schema rejected");
   altered=content;
   const int model_changes=StringReplace(
      altered,"MODEL_VERSION|"+JPW_RAIZN_MODEL_VERSION,
      "MODEL_VERSION|UNSUPPORTED");
   JPWRaizNStoreAssert(model_changes==1 &&
                        JPWRaizNDecodeScenario(altered,key,
                                               record.scenario_id,decoded)==
                        JPW_RAIZN_INCOMPATIBLE,
                        "unsupported mathematical model refused");
  }

void JPWRaizNStoreTestKeys(JPWAccount &account,const string symbol,
                           const string installation_id)
  {
   string original="",different="";
   JPWRaizNStoreAssert(JPWRaizNAccountSymbolKey(account,symbol,
                                                installation_id,original),
                        "base key available");
   JPWAccount another;
   JPWRaizNStoreAccount(another,991002,"USD");
   JPWRaizNStoreAssert(JPWRaizNAccountSymbolKey(another,symbol,
                                                installation_id,different) &&
                        different!=original,
                        "account switch changes key");
   JPWRaizNStoreAssert(JPWRaizNAccountSymbolKey(account,symbol,
                                                "SYNTH-INSTALL-B",different) &&
                        different!=original,
                        "installation switch changes key");
   JPWRaizNStoreAssert(JPWRaizNAccountSymbolKey(account,"SYNTH.XAUUSD",
                                                installation_id,different) &&
                        different!=original,
                        "symbol switch changes key");
   JPWRaizNStoreAssert(JPWRaizNAccountSymbolKey(account,symbol,
                                                installation_id,original),
                        "base key rederived");
   JPWRaizNStoreAccount(another,991001,"USD");
   another.server="SYNTHETIC.OTHER.SERVER";
   JPWRaizNStoreAssert(JPWRaizNAccountSymbolKey(another,symbol,
                                                installation_id,different) &&
                        different!=original,
                        "server switch changes key");
   JPWRaizNStoreAccount(another,991001," usd ");
   JPWRaizNStoreAssert(JPWRaizNAccountSymbolKey(another,symbol,
                                                installation_id,different) &&
                        different==original,
                        "currency normalization keeps key");
   JPWRaizNStoreAccount(another,991001,"USC");
   JPWRaizNStoreAssert(JPWRaizNAccountSymbolKey(another,symbol,
                                                installation_id,different) &&
                        different!=original,
                        "USC account scale changes key");
  }

void JPWRaizNStoreTestLifecycle(const string folder,
                                const string symbol,
                                const string installation_id)
  {
   JPWAccount account;
   JPWRaizNStoreAccount(account,991101,"USD");
   string key="";
   JPWRaizNStoreAssert(JPWRaizNAccountSymbolKey(account,symbol,
                                                installation_id,key),
                        "lifecycle key");
   JPWRaizNScenario active;
   JPWRaizNBinding binding;
   JPWRaizNStoreAssert(JPWRaizNReadActive(account,symbol,installation_id,
                                          folder,active,binding)==
                        JPW_RAIZN_ABSENT,
                        "absent scenario is explicit");
   JPWRaizNScenario draft;
   JPWRaizNStoreFixture(draft,key,symbol);
   JPWRaizNScenario first;
   JPWRaizNStoreAssert(JPWRaizNConfirm(account,symbol,installation_id,
                                       folder,draft,"",first)==
                        JPW_RAIZN_VALID &&
                        JPWRaizNIsHash(first.scenario_id),
                        "first scenario confirmed");
   const string first_id=first.scenario_id;
   JPWRaizNStoreAssert(JPWRaizNReadActive(account,symbol,installation_id,
                                          folder,active,binding)==
                        JPW_RAIZN_VALID &&
                        active.scenario_id==first_id &&
                        binding.scenario_id=="" &&
                        binding.state==JPW_RAIZN_ABSENT,
                        "confirmed scenario survives read without binding");
   JPWRaizNStoreAssert(JPWRaizNConfirm(account,symbol,installation_id,
                                       folder,draft,"",active)==
                        JPW_RAIZN_CONFLICT,
                        "second instance cannot reconfirm against absence");
   JPWRaizNBinding attached;
   JPWRaizNStoreAssert(JPWRaizNBind(account,symbol,installation_id,folder,
                                    first_id,991001,991002,
                                    POSITION_TYPE_BUY,attached)==
                        JPW_RAIZN_VALID &&
                        attached.scenario_id==first_id &&
                        attached.identifier==991001,
                        "explicit synthetic position binding");
   JPWRaizNStoreAssert(JPWRaizNBind(account,symbol,installation_id,folder,
                                    first_id,991001,991002,
                                    POSITION_TYPE_BUY,attached)==
                        JPW_RAIZN_VALID,
                        "same binding is idempotent");
   JPWRaizNStoreAssert(JPWRaizNBind(account,symbol,installation_id,folder,
                                    first_id,991003,991002,
                                    POSITION_TYPE_BUY,attached)==
                        JPW_RAIZN_CONFLICT,
                        "conflicting position identifier is refused");
   JPWRaizNStoreAssert(JPWRaizNBind(account,symbol,installation_id,folder,
                                    first_id,991001,991002,
                                    POSITION_TYPE_SELL,attached)==
                        JPW_RAIZN_INVALID,
                        "declared BUY cannot bind SELL");
   JPWRaizNStoreAssert(JPWRaizNReadActive(account,symbol,installation_id,
                                          folder,active,binding)==
                        JPW_RAIZN_VALID &&
                        active.scenario_id==first_id &&
                        binding.identifier==991001,
                        "binding survives restart-style read");

   JPWRaizNScenario revision;
   JPWRaizNStoreFixture(revision,key,symbol);
   revision.p0=1.21;
   revision.parent_id=first_id;
   revision.revision_reason="synthetic correction of declared P0";
   revision.confirmed_at_utc=D'2026.09.28 08:02:00';
   JPWRaizNScenario second;
   JPWRaizNStoreAssert(JPWRaizNConfirm(account,symbol,installation_id,
                                       folder,revision,first_id,second)==
                        JPW_RAIZN_VALID &&
                        second.scenario_id!=first_id &&
                        second.parent_id==first_id,
                        "revision creates a new immutable receipt");
   JPWRaizNScenario previous;
   JPWRaizNStoreAssert(JPWRaizNLoadScenario(folder,key,first_id,previous)==
                        JPW_RAIZN_VALID && previous.p0==1.2 &&
                        previous.parent_id=="",
                        "prior receipt remains readable and unchanged");
   JPWRaizNStoreAssert(JPWRaizNReadActive(account,symbol,installation_id,
                                          folder,active,binding)==
                        JPW_RAIZN_VALID &&
                        active.scenario_id==second.scenario_id &&
                        active.p0==1.21 && binding.scenario_id=="" &&
                        binding.state==JPW_RAIZN_ABSENT,
                        "active pointer advances without inheriting binding");
   JPWRaizNStoreAssert(JPWRaizNConfirm(account,symbol,installation_id,
                                       folder,revision,first_id,active)==
                        JPW_RAIZN_CONFLICT,
                        "stale editor cannot overwrite newer active receipt");
   JPWRaizNStoreAssert(JPWRaizNBind(account,symbol,installation_id,folder,
                                    first_id,991001,991002,
                                    POSITION_TYPE_BUY,attached)==
                        JPW_RAIZN_CONFLICT,
                        "inactive scenario cannot receive new binding");
   JPWRaizNStoreAssert(JPWRaizNBind(account,symbol,installation_id,folder,
                                    second.scenario_id,991004,991005,
                                    POSITION_TYPE_BUY,attached)==
                        JPW_RAIZN_VALID && attached.identifier==991004,
                        "new revision can be bound explicitly");
   long binding_generation=0;
   int binding_slot=-1;
   JPWRaizNBinding old_binding;
   JPWRaizNStoreAssert(JPWRaizNLoadBinding(folder,key,first_id,old_binding,
                              binding_generation,binding_slot)==
                        JPW_RAIZN_VALID && old_binding.identifier==991001,
                        "old immutable binding remains available by receipt");
  }

void JPWRaizNStoreTestRecovery(const string folder,
                               const string symbol,
                               const string installation_id)
  {
   JPWAccount account;
   JPWRaizNStoreAccount(account,991201,"USD");
   string key="";
   JPWRaizNStoreAssert(JPWRaizNAccountSymbolKey(account,symbol,
                                                installation_id,key),
                        "recovery key");
   JPWRaizNScenario draft;
   JPWRaizNStoreFixture(draft,key,symbol);
   JPWRaizNScenario confirmed;
   JPWRaizNStoreAssert(JPWRaizNConfirm(account,symbol,installation_id,
                                       folder,draft,"",confirmed)==
                        JPW_RAIZN_VALID,
                        "recovery scenario confirmed");
   const string id=confirmed.scenario_id;
   const string scenario_base=JPWRaizNScenarioBase(folder,key,id);
   JPWRaizNStoreAssert(JPWRaizNWriteText(scenario_base+".a","truncated"),
                        "one scenario slot truncated");
   JPWRaizNScenario loaded;
   JPWRaizNBinding binding;
   JPWRaizNStoreAssert(JPWRaizNReadActive(account,symbol,installation_id,
                                          folder,loaded,binding)==
                        JPW_RAIZN_VALID && loaded.scenario_id==id,
                        "other scenario slot recovers receipt");
   JPWRaizNStoreAssert(JPWRaizNWriteText(scenario_base+".b","truncated"),
                        "second scenario slot truncated");
   JPWRaizNStoreAssert(JPWRaizNReadActive(account,symbol,installation_id,
                                          folder,loaded,binding)==
                        JPW_RAIZN_INVALID,
                        "two corrupt scenario slots block active read");
   JPWRaizNScenario attempted;
   JPWRaizNStoreFixture(attempted,key,symbol);
   attempted.p0=1.3;
   attempted.parent_id=id;
   attempted.revision_reason="synthetic correction";
   JPWRaizNStoreAssert(JPWRaizNConfirm(account,symbol,installation_id,
                                       folder,attempted,id,loaded)==
                        JPW_RAIZN_INVALID,
                        "two corrupt scenario slots block revision");

   JPWAccount pointer_account;
   JPWRaizNStoreAccount(pointer_account,991202,"USD");
   string pointer_key="";
   JPWRaizNStoreAssert(JPWRaizNAccountSymbolKey(pointer_account,symbol,
                                                installation_id,pointer_key),
                        "pointer recovery key");
   JPWRaizNStoreFixture(draft,pointer_key,symbol);
   JPWRaizNStoreAssert(JPWRaizNConfirm(pointer_account,symbol,installation_id,
                                       folder,draft,"",confirmed)==
                        JPW_RAIZN_VALID,
                        "pointer recovery scenario confirmed");
   const string first_pointer_id=confirmed.scenario_id;
   JPWRaizNScenario pointer_revision;
   JPWRaizNStoreFixture(pointer_revision,pointer_key,symbol);
   pointer_revision.p0=1.31;
   pointer_revision.parent_id=first_pointer_id;
   pointer_revision.revision_reason="synthetic pointer recovery";
   pointer_revision.confirmed_at_utc=D'2026.09.28 08:02:00';
   JPWRaizNStoreAssert(JPWRaizNConfirm(pointer_account,symbol,
                                       installation_id,folder,pointer_revision,
                                       first_pointer_id,confirmed)==
                        JPW_RAIZN_VALID &&
                        confirmed.scenario_id!=first_pointer_id,
                        "pointer recovery creates second generation");
   const string base=JPWRaizNBase(folder,pointer_key);
   JPWRaizNStoreAssert(JPWRaizNWriteText(base+".active.b","truncated"),
                        "newer active-pointer slot truncated");
   JPWRaizNStoreAssert(JPWRaizNReadActive(pointer_account,symbol,
                                          installation_id,folder,loaded,
                                          binding)==JPW_RAIZN_VALID &&
                        loaded.scenario_id==first_pointer_id,
                        "older valid pointer recovers active scenario");
   JPWRaizNStoreAssert(JPWRaizNWriteText(base+".active.b",
                        "JPW_RAIZN_ACTIVE|2\nFUTURE|1"),
                        "future pointer schema fixture");
   JPWRaizNStoreAssert(JPWRaizNReadActive(pointer_account,symbol,
                                          installation_id,folder,loaded,
                                          binding)==JPW_RAIZN_INCOMPATIBLE,
                        "future pointer schema blocks old valid slot");
   JPWRaizNStoreAssert(JPWRaizNWriteText(base+".active.b","truncated"),
                        "future pointer replaced by corrupt fixture");
   JPWRaizNStoreAssert(JPWRaizNWriteText(base+".active.a","truncated"),
                        "older active-pointer slot truncated");
   JPWRaizNStoreAssert(JPWRaizNReadActive(pointer_account,symbol,
                                          installation_id,folder,loaded,
                                          binding)==JPW_RAIZN_INVALID,
                        "both pointer slots corrupt block read");

   JPWAccount binding_account;
   JPWRaizNStoreAccount(binding_account,991203,"USD");
   string binding_key="";
   JPWRaizNStoreAssert(JPWRaizNAccountSymbolKey(binding_account,symbol,
                                                installation_id,binding_key),
                        "binding recovery key");
   JPWRaizNStoreFixture(draft,binding_key,symbol);
   JPWRaizNStoreAssert(JPWRaizNConfirm(binding_account,symbol,
                                       installation_id,folder,draft,"",
                                       confirmed)==JPW_RAIZN_VALID,
                        "binding recovery scenario confirmed");
   JPWRaizNStoreAssert(JPWRaizNBind(binding_account,symbol,installation_id,
                                    folder,confirmed.scenario_id,991211,
                                    991212,POSITION_TYPE_BUY,binding)==
                        JPW_RAIZN_VALID,
                        "binding recovery fixture confirmed");
   const string binding_base=JPWRaizNBindingBase(folder,binding_key,
                                                 confirmed.scenario_id);
   JPWRaizNStoreAssert(JPWRaizNWriteText(binding_base+".a","truncated"),
                        "one binding slot truncated");
   JPWRaizNStoreAssert(JPWRaizNReadActive(binding_account,symbol,
                                          installation_id,folder,loaded,
                                          binding)==JPW_RAIZN_VALID &&
                        binding.identifier==991211,
                        "other binding slot recovers linked identifier");
   JPWRaizNStoreAssert(JPWRaizNWriteText(binding_base+".b","truncated"),
                        "second binding slot truncated");
   JPWRaizNStoreAssert(JPWRaizNReadActive(binding_account,symbol,
                                          installation_id,folder,loaded,
                                          binding)==JPW_RAIZN_VALID &&
                        loaded.scenario_id==confirmed.scenario_id &&
                        binding.state==JPW_RAIZN_INVALID &&
                        binding.scenario_id=="",
                        "corrupt binding preserves scenario with invalid state");
   JPWRaizNStoreAssert(JPWRaizNBind(binding_account,symbol,installation_id,
                                    folder,confirmed.scenario_id,991211,
                                    991212,POSITION_TYPE_BUY,binding)==
                        JPW_RAIZN_INVALID,
                        "two corrupt binding slots block rebinding");
   string refused_receipt="";
   JPWRaizNStoreAssert(JPWRaizNRecordComparison(
                        binding_account,symbol,installation_id,folder,
                        confirmed.scenario_id,991211,1.18,
                        D'2026.09.28 08:03:00',refused_receipt)==
                        JPW_RAIZN_INVALID && refused_receipt=="",
                        "two corrupt binding slots block comparison receipt");
  }

void JPWRaizNStoreTestAccountAndLock(const string folder,
                                     const string symbol,
                                     const string installation_id)
  {
   JPWAccount account;
   JPWRaizNStoreAccount(account,991301,"USD");
   string key="";
   JPWRaizNStoreAssert(JPWRaizNAccountSymbolKey(account,symbol,
                                                installation_id,key),
                        "lock account key");
   JPWRaizNScenario draft;
   JPWRaizNStoreFixture(draft,key,symbol);
   JPWRaizNScenario confirmed;
   JPWRaizNStoreAssert(JPWRaizNConfirm(account,symbol,installation_id,
                                       folder,draft,"",confirmed)==
                        JPW_RAIZN_VALID,
                        "lock fixture confirmed");
   JPWAccount other;
   JPWRaizNStoreAccount(other,991302,"USD");
   JPWRaizNBinding binding;
   JPWRaizNStoreAssert(JPWRaizNReadActive(other,symbol,installation_id,
                                          folder,confirmed,binding)==
                        JPW_RAIZN_ABSENT,
                        "other account cannot see scenario");
   const string lock_path=JPWRaizNBase(folder,key)+".lock";
   const int lock=FileOpen(lock_path,FILE_READ|FILE_WRITE|FILE_BIN);
   JPWRaizNStoreAssert(lock!=INVALID_HANDLE,
                        "synthetic lock held exclusively");
   if(lock!=INVALID_HANDLE)
     {
      JPWRaizNStoreAssert(JPWRaizNReadActive(account,symbol,
                                             installation_id,folder,confirmed,
                                             binding)==JPW_RAIZN_BUSY,
                           "reader defers while lock is held");
      JPWRaizNStoreAssert(JPWRaizNConfirm(account,symbol,
                                          installation_id,folder,draft,"",
                                          confirmed)==JPW_RAIZN_BUSY,
                           "writer defers while lock is held");
      JPWRaizNStoreAssert(JPWRaizNBind(account,symbol,installation_id,folder,
                                       draft.scenario_id,991301,991302,
                                       POSITION_TYPE_BUY,binding)==
                           JPW_RAIZN_BUSY,
                           "binding defers while lock is held");
      FileClose(lock);
     }
   JPWRaizNStoreAssert(JPWRaizNReadActive(account,symbol,installation_id,
                                          folder,confirmed,binding)==
                        JPW_RAIZN_VALID,
                        "reader resumes after lock release");
  }

void JPWRaizNStoreTestComparison(const string folder,
                                 const string symbol,
                                 const string installation_id)
  {
   JPWAccount account;
   JPWRaizNStoreAccount(account,991401,"USD");
   string key="";
   JPWRaizNStoreAssert(JPWRaizNAccountSymbolKey(account,symbol,
                                                installation_id,key),
                        "comparison account key");
   JPWRaizNScenario draft;
   JPWRaizNStoreFixture(draft,key,symbol);
   JPWRaizNScenario scenario;
   JPWRaizNStoreAssert(JPWRaizNConfirm(account,symbol,installation_id,
                                       folder,draft,"",scenario)==
                        JPW_RAIZN_VALID,
                        "comparison scenario explicitly confirmed");
   JPWRaizNBinding binding;
   JPWRaizNStoreAssert(JPWRaizNBind(account,symbol,installation_id,folder,
                                    scenario.scenario_id,991411,991412,
                                    POSITION_TYPE_BUY,binding)==
                        JPW_RAIZN_VALID &&
                        binding.identifier==991411,
                        "comparison requires explicit bound identifier");
   const string scenario_base=JPWRaizNScenarioBase(folder,key,
                                                   scenario.scenario_id);
   string original_a="",original_b="";
   JPWRaizNStoreAssert(JPWRaizNReadText(scenario_base+".a",original_a)==
                        JPW_RAIZN_VALID &&
                        JPWRaizNReadText(scenario_base+".b",original_b)==
                        JPW_RAIZN_VALID && original_a==original_b,
                        "scenario slots captured before comparison");
   const datetime first_at=D'2026.09.28 08:03:00';
   string receipt_id="";
   JPWRaizNStoreAssert(JPWRaizNRecordComparison(
                        account,symbol,installation_id,folder,
                        scenario.scenario_id,991411,1.18,first_at,
                        receipt_id)==JPW_RAIZN_VALID &&
                        JPWRaizNIsHash(receipt_id),
                        "adverse BUY SL creates comparison receipt");
   const string first_id=receipt_id;
   const string first_base=JPWRaizNComparisonBase(folder,key,
                                                  scenario.scenario_id,
                                                  first_id);
   const int comparison_name_len=StringLen(first_base)-StringLen(folder);
   // O temporario acrescenta ponto, ChartID(ate 20 digitos), ponto,
   // GetTickCount64(ate 20 digitos) e ".tmp" ao basename.
   const int worst_temp_name_len=comparison_name_len+1+20+1+20+4;
   JPWRaizNStoreAssert(
      StringLen(JPWRaizNBase(folder,key))-StringLen(folder)<90 &&
      StringLen(scenario_base)-StringLen(folder)<90 &&
      StringLen(JPWRaizNBindingBase(folder,key,scenario.scenario_id))-
         StringLen(folder)<90 &&
      comparison_name_len<90 && worst_temp_name_len<135,
      "compact basenames fit slot and temporary path budgets");
   string first_a="",first_b="";
   JPWRaizNStoreAssert(JPWRaizNReadText(first_base+".a",first_a)==
                        JPW_RAIZN_VALID &&
                        JPWRaizNReadText(first_base+".b",first_b)==
                        JPW_RAIZN_VALID && first_a==first_b &&
                        StringFind(first_a,"JPW_RAIZN_COMPARISON|1\n")==0 &&
                        StringFind(first_a,"\nSCENARIO|"+
                                   scenario.scenario_id+"\n")>=0 &&
                        StringFind(first_a,"\nIDENTIFIER|991411\n")>=0 &&
                        StringFind(first_a,"\nGAP_PRICE|")>=0,
                        "receipt stores scenario, binding and computed gap");
   string repeat_id="";
   JPWRaizNStoreAssert(JPWRaizNRecordComparison(
                        account,symbol,installation_id,folder,
                        scenario.scenario_id,991411,1.18,first_at,
                        repeat_id)==JPW_RAIZN_VALID &&
                        repeat_id==first_id,
                        "same comparison and timestamp are idempotent");
   string unchanged_a="",unchanged_b="";
   JPWRaizNStoreAssert(JPWRaizNReadText(first_base+".a",unchanged_a)==
                        JPW_RAIZN_VALID &&
                        JPWRaizNReadText(first_base+".b",unchanged_b)==
                        JPW_RAIZN_VALID &&
                        unchanged_a==first_a && unchanged_b==first_b,
                        "idempotent request leaves receipt slots unchanged");
   const datetime later_at=D'2026.09.28 08:04:00';
   string later_id="";
   JPWRaizNStoreAssert(JPWRaizNRecordComparison(
                        account,symbol,installation_id,folder,
                        scenario.scenario_id,991411,1.18,later_at,
                        later_id)==JPW_RAIZN_VALID &&
                        JPWRaizNIsHash(later_id) && later_id!=first_id,
                        "later observation creates distinct receipt");
   const string later_base=JPWRaizNComparisonBase(folder,key,
                                                  scenario.scenario_id,
                                                  later_id);
   string later_a="",later_b="";
   JPWRaizNStoreAssert(JPWRaizNReadText(later_base+".a",later_a)==
                        JPW_RAIZN_VALID &&
                        JPWRaizNReadText(later_base+".b",later_b)==
                        JPW_RAIZN_VALID && later_a==later_b &&
                        later_a!=first_a,
                        "later receipt occupies new immutable slots");
   JPWRaizNStoreAssert(JPWRaizNReadText(first_base+".a",unchanged_a)==
                        JPW_RAIZN_VALID &&
                        JPWRaizNReadText(first_base+".b",unchanged_b)==
                        JPW_RAIZN_VALID &&
                        unchanged_a==first_a && unchanged_b==first_b,
                        "later receipt does not overwrite prior receipt");

   string refused_id="";
   JPWRaizNStoreAssert(JPWRaizNRecordComparison(
                        account,symbol,installation_id,folder,
                        scenario.scenario_id,991411,0.0,later_at,
                        refused_id)==JPW_RAIZN_INVALID && refused_id=="",
                        "missing SL has no comparison receipt");
   JPWRaizNStoreAssert(JPWRaizNRecordComparison(
                        account,symbol,installation_id,folder,
                        scenario.scenario_id,991411,1.22,later_at,
                        refused_id)==JPW_RAIZN_INVALID && refused_id=="",
                        "profit-protected SL has no adverse comparison");
   JPWRaizNStoreAssert(JPWRaizNRecordComparison(
                        account,symbol,installation_id,folder,
                        scenario.scenario_id,991499,1.18,later_at,
                        refused_id)==JPW_RAIZN_CONFLICT && refused_id=="",
                        "wrong position identifier is refused");
   JPWAccount other;
   JPWRaizNStoreAccount(other,991402,"USD");
   JPWRaizNStoreAssert(JPWRaizNRecordComparison(
                        other,symbol,installation_id,folder,
                        scenario.scenario_id,991411,1.18,later_at,
                        refused_id)==JPW_RAIZN_ABSENT && refused_id=="",
                        "another account cannot record this comparison");
   JPWRaizNStoreAssert(JPWRaizNReadText(scenario_base+".a",unchanged_a)==
                        JPW_RAIZN_VALID &&
                        JPWRaizNReadText(scenario_base+".b",unchanged_b)==
                        JPW_RAIZN_VALID &&
                        unchanged_a==original_a &&
                        unchanged_b==original_b,
                        "comparison never mutates scenario slots");
  }

void OnStart()
  {
   const string root=JPW_RAIZN_FOLDER+"SyntheticRaizNTests\\";
   const string folder=root+IntegerToString((long)TimeLocal())+"_"+
                       IntegerToString((long)GetTickCount64())+"\\";
   FolderCreate("JPWealth");
   FolderCreate("JPWealth\\Alavancagem");
   FolderCreate("JPWealth\\Alavancagem\\SyntheticRaizNTests");
   if(!FolderCreate(StringSubstr(folder,0,StringLen(folder)-1)))
     {
      Print("JPW RaizN store tests NOT_RUN: synthetic folder unavailable");
      return;
     }
   JPWAccount account;
   JPWRaizNStoreAccount(account,991001,"USD");
   const string symbol="SYNTH.EURUSD";
   const string installation_id="SYNTH-INSTALL-A";
   JPWRaizNStoreTestCodec(account,symbol,installation_id);
   JPWRaizNStoreTestKeys(account,symbol,installation_id);
   JPWRaizNStoreTestLifecycle(folder,symbol,installation_id);
   JPWRaizNStoreTestRecovery(folder,symbol,installation_id);
   JPWRaizNStoreTestAccountAndLock(folder,symbol,installation_id);
   JPWRaizNStoreTestComparison(folder,symbol,installation_id);
   if(g_raizn_store_failures==0)
      PrintFormat("JPW_Alavancagem_RaizN_Store_Tests PASS: %d asserts",
                  g_raizn_store_passes);
   else
      PrintFormat("JPW_Alavancagem_RaizN_Store_Tests FAIL: %d of %d asserts",
                  g_raizn_store_failures,
                  g_raizn_store_passes+g_raizn_store_failures);
  }
