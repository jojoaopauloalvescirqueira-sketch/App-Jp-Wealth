#ifndef JPW_ALAVANCAGEM_SAMPLES_MQH
#define JPW_ALAVANCAGEM_SAMPLES_MQH
// Runtime-only accepted evidence. No account identifiers or financial persistence.
enum JPW_SAMPLE_REASON
  {
   JPW_SAMPLE_WAITING=0, JPW_SAMPLE_CONFIRMED=1, JPW_SAMPLE_ESTIMATED=2,
   JPW_SAMPLE_UNAVAILABLE=3, JPW_SAMPLE_CONTEXT_CHANGED=4, JPW_SAMPLE_EXPIRED=5
  };
enum JPW_SAMPLE_VALUE_KIND { JPW_SAMPLE_NONE=0, JPW_SAMPLE_NUMERIC=1, JPW_SAMPLE_STATE=2 };
struct JPWMetricSample
  {
   long id;
   string context_key;
   JPW_SAMPLE_VALUE_KIND value_kind;
   double numeric_value;
   bool has_value;
   string unit;
   int quality;
   JPW_SAMPLE_REASON reason_code;
   string source;
   long observed_utc;
   long source_time_msc;
   ulong accepted_monotonic_ms;
   ulong valid_until_monotonic_ms;
   bool valid;
  };
void JPWSampleInvalidate(JPWMetricSample &sample,const JPW_SAMPLE_REASON reason)
  {
   sample.valid=false; sample.has_value=false; sample.quality=0;
   sample.value_kind=JPW_SAMPLE_NONE; sample.numeric_value=0.0;
   sample.reason_code=reason;
  }
bool JPWSampleAccept(JPWMetricSample &sample,long &sequence,const string context,
                     const double value,const bool has_value,const string unit,
                     const int quality,const JPW_SAMPLE_REASON reason,const string source,
                     const long observed_utc,const long source_time_msc,const ulong monotonic_ms)
  {
   if(context=="" || sequence<0 || sequence==LONG_MAX || quality<0 || quality>2 ||
      observed_utc<=0 || (has_value && !MathIsValidNumber(value))) { JPWSampleInvalidate(sample,JPW_SAMPLE_CONTEXT_CHANGED); return(false); }
   sequence++;
   sample.id=sequence; sample.context_key=context;
   sample.numeric_value=(quality!=0 && has_value && MathIsValidNumber(value) ? value : 0.0);
   sample.has_value=quality!=0 && has_value && MathIsValidNumber(value);
   sample.value_kind=(quality==0 ? JPW_SAMPLE_NONE : (sample.has_value ? JPW_SAMPLE_NUMERIC : JPW_SAMPLE_STATE));
   sample.unit=unit; sample.quality=quality; sample.reason_code=reason;
   sample.source=source; sample.observed_utc=observed_utc;
   sample.source_time_msc=source_time_msc; sample.accepted_monotonic_ms=monotonic_ms;
   sample.valid_until_monotonic_ms=monotonic_ms+30000;
   sample.valid=(quality!=0); return(true);
  }
bool JPWSampleContextValid(JPWMetricSample &sample,const string context)
  { return(context!="" && sample.context_key==context && sample.id>0); }
bool JPWSampleDisplayValid(JPWMetricSample &sample,const string context,const ulong now)
  { return(JPWSampleContextValid(sample,context) && sample.valid &&
           now>=sample.accepted_monotonic_ms && now<=sample.valid_until_monotonic_ms); }
enum JPW_TECHNICAL_HEALTH { JPW_HEALTH_NORMAL=0, JPW_HEALTH_ATTENTION=1, JPW_HEALTH_UNAVAILABLE=2 };
JPW_TECHNICAL_HEALTH JPWTechnicalHealthEvaluate(const bool context_valid,
   const bool diagnostic_accessible,const bool diagnostic_write_ok,
   const int pending_events,const bool queue_lost,const bool observer_recent,
   const bool budget_deferred)
  {
   if(!context_valid) return(JPW_HEALTH_UNAVAILABLE);
   if(!diagnostic_accessible || !diagnostic_write_ok || pending_events>0 ||
      queue_lost || !observer_recent || budget_deferred) return(JPW_HEALTH_ATTENTION);
   return(JPW_HEALTH_NORMAL);
  }
#endif
