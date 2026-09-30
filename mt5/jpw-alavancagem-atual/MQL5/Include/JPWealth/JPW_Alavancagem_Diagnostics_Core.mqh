#ifndef JPW_ALAVANCAGEM_DIAGNOSTICS_CORE_MQH
#define JPW_ALAVANCAGEM_DIAGNOSTICS_CORE_MQH
#include <JPWealth/JPW_Alavancagem_Version.mqh>
#include <JPWealth/JPW_Alavancagem_Store_Result.mqh>
#define JPW_DIAG_SCHEMA 1
#define JPW_DIAG_RETENTION_SECONDS 2592000
#define JPW_DIAG_MAX_ROWS 8192
#define JPW_DIAG_COALESCE_SECONDS 60
#define JPW_DIAG_DB_LIMIT_BYTES 8388608
#define JPW_DIAG_EXPORT_LIMIT_BYTES 65536
// 8 MiB database + at most 8 MiB DELETE journal + fixed 64 KiB export,
// leaving margin below 20 MiB. No WAL, backups or per-account DB proliferation.
enum JPWDiagComponent
  {
   JPW_DIAG_INDICATOR=1, JPW_DIAG_OBSERVER=2, JPW_DIAG_STORAGE=3,
   JPW_DIAG_UI=4, JPW_DIAG_SUPERVISOR=5
  };
enum JPWDiagCode
  {
   JPW_DIAG_SESSION_START=1, JPW_DIAG_SESSION_END=2,
   JPW_DIAG_CONTEXT_CHANGED=3, JPW_DIAG_QUEUE_OVERFLOW=4,
   JPW_DIAG_RETRY_EXHAUSTED=5, JPW_DIAG_WRITE_FAILED=6,
   JPW_DIAG_RECONSTRUCTED=7, JPW_DIAG_SETTINGS_APPLIED=8,
   JPW_DIAG_QUALITY_CHANGED=9, JPW_DIAG_BUDGET_DEFERRED=10,
   JPW_DIAG_STORAGE_BUSY=11, JPW_DIAG_DATA_UNAVAILABLE=12,
   JPW_DIAG_CAPTURE_RESUMED=13, JPW_DIAG_STORAGE_CORRUPT=14,
   JPW_DIAG_STORAGE_INCOMPATIBLE=15
  };
enum JPWDiagCoverage
  {
   JPW_DIAG_COVERAGE_UNKNOWN=0, JPW_DIAG_COVERAGE_INCOMPLETE=1
   // No COMPLETE state: retained evidence cannot prove unobserved periods.
  };
struct JPWDiagTiming
  {
   long cycles;
   long deferred;
   long last_duration_ms;
   long max_duration_ms;
  };
bool JPWDiagEventValid(const int component,const int code,
                       const long sample_id,const long utc,const long mono)
  {
   return(component>=JPW_DIAG_INDICATOR && component<=JPW_DIAG_SUPERVISOR &&
          code>=JPW_DIAG_SESSION_START && code<=JPW_DIAG_STORAGE_INCOMPATIBLE &&
          sample_id>=0 && utc>0 && mono>=0);
  }
bool JPWDiagCreatesCoverageGap(const int code)
  {
   return(code==JPW_DIAG_QUEUE_OVERFLOW || code==JPW_DIAG_RETRY_EXHAUSTED ||
          code==JPW_DIAG_WRITE_FAILED || code==JPW_DIAG_STORAGE_CORRUPT ||
          code==JPW_DIAG_STORAGE_INCOMPATIBLE);
  }
bool JPWDiagCanCoalesce(const int component,const int code,const string context,
                        const long utc,const int previous_component,
                        const int previous_code,const string previous_context,
                        const long previous_utc)
  {
   return(component==previous_component && code==previous_code &&
          context==previous_context && utc>=previous_utc &&
          utc-previous_utc<=JPW_DIAG_COALESCE_SECONDS);
  }
void JPWDiagTimingRecord(JPWDiagTiming &timing,const long duration_ms,
                         const bool deferred)
  {
   if(duration_ms<0) return;
   if(timing.cycles<LONG_MAX) timing.cycles++;
   if(deferred && timing.deferred<LONG_MAX) timing.deferred++;
   timing.last_duration_ms=duration_ms;
   if(duration_ms>timing.max_duration_ms) timing.max_duration_ms=duration_ms;
  }
string JPWDiagCodeLabel(const int code)
  {
   switch(code)
     {
      case JPW_DIAG_SESSION_START: return("SESSION_START");
      case JPW_DIAG_SESSION_END: return("SESSION_END");
      case JPW_DIAG_CONTEXT_CHANGED: return("CONTEXT_CHANGED");
      case JPW_DIAG_QUEUE_OVERFLOW: return("QUEUE_OVERFLOW");
      case JPW_DIAG_RETRY_EXHAUSTED: return("RETRY_EXHAUSTED");
      case JPW_DIAG_WRITE_FAILED: return("WRITE_FAILED");
      case JPW_DIAG_RECONSTRUCTED: return("RECONSTRUCTED");
      case JPW_DIAG_SETTINGS_APPLIED: return("SETTINGS_APPLIED");
      case JPW_DIAG_QUALITY_CHANGED: return("QUALITY_CHANGED");
      case JPW_DIAG_BUDGET_DEFERRED: return("BUDGET_DEFERRED");
      case JPW_DIAG_STORAGE_BUSY: return("STORAGE_BUSY");
      case JPW_DIAG_DATA_UNAVAILABLE: return("DATA_UNAVAILABLE");
      case JPW_DIAG_CAPTURE_RESUMED: return("CAPTURE_RESUMED");
      case JPW_DIAG_STORAGE_CORRUPT: return("STORAGE_CORRUPT");
      case JPW_DIAG_STORAGE_INCOMPATIBLE: return("STORAGE_INCOMPATIBLE");
     }
   return("INVALID_CODE");
  }
#endif
