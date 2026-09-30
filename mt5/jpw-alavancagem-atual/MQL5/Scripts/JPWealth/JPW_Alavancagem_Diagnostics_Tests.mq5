#property copyright "JP Wealth"
#include <JPWealth/JPW_Alavancagem_Version.mqh>
#property version JPW_PRODUCT_MQL_VERSION
#property script_show_inputs
#property description "Testes tecnicos sinteticos; executar apenas em MT5 isolado. Nenhuma leitura de conta."
#include <JPWealth/JPW_Alavancagem_Diagnostics.mqh>

int g_diag_pass=0,g_diag_fail=0;
void JPWDiagAssert(const bool condition,const string label)
  {
   if(condition) g_diag_pass++;
   else { g_diag_fail++; Print("DIAGNOSTICS FAIL: ",label); }
  }
void OnStart()
  {
   // Unique synthetic subfolder; never deletes or reads production records.
   const string folder=JPW_DIAG_FOLDER+"Synthetic\\test_"+
      IntegerToString((long)GetTickCount64())+"\\";
   string context="";
   for(int i=0;i<64;i++) context+="a";
   string reason="";
   const long now=(long)TimeGMT();
   JPWDiagAssert(JPWDiagEventValid(JPW_DIAG_OBSERVER,JPW_DIAG_QUEUE_OVERFLOW,1,now,100),"valid event");
   JPWDiagAssert(!JPWDiagEventValid(99,JPW_DIAG_QUEUE_OVERFLOW,1,now,100),"unknown component rejected");
   JPWDiagAssert(JPWDiagCreatesCoverageGap(JPW_DIAG_RETRY_EXHAUSTED),"retry exhaustion is a gap");
   JPWDiagAssert(!JPWDiagCreatesCoverageGap(JPW_DIAG_RECONSTRUCTED),"reconstruction never certifies completeness");
   JPWDiagAssert(JPWDiagRecordAt(context,JPW_DIAG_OBSERVER,JPW_DIAG_QUEUE_OVERFLOW,
                               1,now,100,reason,folder)==JPW_STORE_VALID,"first durable gap");
   JPWDiagAssert(JPWDiagRecordAt(context,JPW_DIAG_OBSERVER,JPW_DIAG_QUEUE_OVERFLOW,
                               2,now+1,200,reason,folder)==JPW_STORE_VALID,"coalesced durable gap");
   int db=INVALID_HANDLE,lock=INVALID_HANDLE;
   JPWDiagAssert(JPWDiagOpen(folder,false,db,lock,reason)==JPW_STORE_VALID,"read-only open");
   long count=0,repeats=0;
   JPWDiagAssert(JPWDiagScalar(db,"SELECT COUNT(*) FROM diag_events",count) && count==1,"coalesce row count");
   JPWDiagAssert(JPWDiagScalar(db,"SELECT repetitions FROM diag_events",repeats) && repeats==2,"coalesce count");
   int other_db=INVALID_HANDLE,other_lock=INVALID_HANDLE;
   JPWDiagAssert(JPWDiagOpen(folder,false,other_db,other_lock,reason)==JPW_STORE_BUSY,"exclusive lock no wait");
   JPWDiagClose(db,lock);
   string preview="",path="",summary="";
   JPWDiagAssert(JPWDiagSummary(context,summary,reason,folder)==JPW_STORE_VALID &&
      StringFind(summary,"incompleta (lacuna registrada)")>=0,
      "summary reports confirmed synthetic coverage gap");
   JPWDiagAssert(JPWDiagPreview(context,preview,reason,folder)==JPW_STORE_VALID,"preview validated rows");
   JPWDiagAssert(JPWDiagExport(context,preview,path,reason,folder)==JPW_STORE_VALID,"exact preview export readback");
   JPWDiagAssert(JPWDiagExport(context,"injected financial text",path,reason,folder)==JPW_STORE_BUSY,"arbitrary export refused");
   // Malformed checksum must be preserved and reported, not silently reset.
   JPWDiagAssert(JPWDiagOpen(folder,true,db,lock,reason)==JPW_STORE_VALID,"writer reopen");
   JPWDiagAssert(DatabaseExecute(db,"UPDATE diag_events SET checksum='invalid'"),"synthetic corruption injected");
   JPWDiagClose(db,lock);
   JPWDiagAssert(JPWDiagPreview(context,preview,reason,folder)==JPW_STORE_CORRUPT,"corruption refused");
   JPWDiagAssert(JPWDiagSummary(context,summary,reason,folder)==JPW_STORE_CORRUPT,
      "summary refuses corrupted synthetic record");
   Print("JPW_Alavancagem_Diagnostics_Tests ",(g_diag_fail==0 ? "PASS" : "FAIL"),
         ": ",g_diag_pass," passed; ",g_diag_fail," failed; synthetic folder: ",folder);
  }
