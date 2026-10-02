#ifndef JPW_SIGNAL_COPY_TYPES_MQH
#define JPW_SIGNAL_COPY_TYPES_MQH
#include <JPWealth/JPW_Alavancagem_Core.mqh>
// Local transient message data. Never a trade request or financial store schema.
#define JPW_SIGNAL_POSITION 1
#define JPW_SIGNAL_PENDING 2
#define JPW_SIGNAL_MAX_ROWS 512
enum JPW_SIGNAL_STAGE
  { JPW_SIGNAL_SELECT=0, JPW_SIGNAL_STRUCTURE=1, JPW_SIGNAL_PREVIEW=2, JPW_SIGNAL_TEXT=3 };
enum JPW_SIGNAL_ORIGIN
  { JPW_SIGNAL_INFERRED=0, JPW_SIGNAL_REFERENCE=1, JPW_SIGNAL_CONFIRMED=2 };
struct JPWSignalRow
  {
   int kind;
   ulong ticket;
   long identifier;
   long opened_msc;
   long updated_msc;
   string symbol;
   int side;
   int order_type;
   int order_state;
   long expiration;
   double volume;
   double initial_volume;
   double entry;
   double sl;
   double tp;
   double stop_limit;
   int digits;
   int volume_digits;
  };
struct JPWSignalCapture
  {
   JPWAccount account;
   string context;
   string digest;
   long margin_mode;
   bool reference_closed; long reference_identifier;
   double balance;
   double equity;
   double profit;
   double credit;
   long observed_utc;
   ulong accepted_ms;
  };
struct JPWSignalMember
  {
   int row;
   bool included;
   int role; // 0 unspecified; 1 Genesis; 2 Defense 1; no artificial limit 4.
   JPW_SIGNAL_ORIGIN origin;
  };
struct JPWSignalMetrics
  {
   bool leverage_valid;
   bool scenario_valid;
   bool floating_valid;
   bool root_valid;
   bool stop_valid;
   double leverage;
   double scenario_leverage;
   double floating_percent;
   double root_1w;
   double root_2w;
   double factor;
   int n_1w;
   int n_2w;
   double atr;
   double bid;
   double ask;
   double point;
   double tick_size;
   long quote_time_msc;
   long atr_bar_time;
   int leverage_quality; // 0 N/A, 1 Estimated, 2 Current; reuse existing policy.
   int root_quality;
   int quote_quality;
   int floating_quality;
   string leverage_reason;
   string root_reason;
   string stop_reason;
   string floating_reason;
  };
void JPWSignalClearMetrics(JPWSignalMetrics &m)
  {
   m.leverage_valid=false; m.scenario_valid=false; m.floating_valid=false;
   m.root_valid=false; m.stop_valid=false;
   m.leverage=0; m.scenario_leverage=0; m.floating_percent=0;
   m.root_1w=0; m.root_2w=0; m.factor=0; m.n_1w=0; m.n_2w=0;
   m.atr=0; m.bid=0; m.ask=0; m.point=0; m.tick_size=0;
   m.quote_time_msc=0; m.atr_bar_time=0;
   m.leverage_quality=0; m.root_quality=0; m.quote_quality=0; m.floating_quality=0;
   m.leverage_reason="Aguardando coleta"; m.root_reason="Aguardando coleta";
   m.stop_reason="Aguardando cotação"; m.floating_reason="Aguardando conta";
  }
#endif
