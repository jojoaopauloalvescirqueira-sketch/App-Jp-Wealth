#ifndef JPW_ALAVANCAGEM_COCKPIT_MQH
#define JPW_ALAVANCAGEM_COCKPIT_MQH

#include <JPWealth/JPW_Alavancagem_Samples.mqh>

// Presentation only. This chart/template preference contains no account or
// financial data and never changes collection, calculations, or MDD writes.
#define JPW_COCKPIT_PREF_OBJECT "JPW_COCKPIT_PREF_V3"
#define JPW_COCKPIT_PREF_V2_OBJECT "JPW_COCKPIT_PREF_V2"
#define JPW_COCKPIT_PREF_LEGACY_OBJECT "JPW_COCKPIT_PREF_V1"
#define JPW_COCKPIT_PREF_VERSION 3
#define JPW_COCKPIT_ALL_VISIBLE 127
#define JPW_COCKPIT_METRIC_COUNT 7

enum JPW_VIEW_QUALITY
  {
   JPW_VIEW_NA=0,
   JPW_VIEW_CURRENT=1,
   JPW_VIEW_ESTIMATED=2
  };

struct JPWCockpitPrefs
  {
   int visible_mask; // Leverage, P/L, SL, 1W, 2W, stop risk, compensated.
   int corner;       // ENUM_BASE_CORNER as an integer, 0..3.
   int density;      // 0 compact, 1 normal.
  };

struct JPWCockpitMetric
  {
   JPWMetricSample sample;
   string title;
   string value;
   string reason;
   string detail;
   JPW_VIEW_QUALITY quality;
  };

struct JPWCockpitSnapshot
  {
   long sequence;
   string symbol;
   string account_key; // Runtime-only. Never serialized to the chart object.
   JPWCockpitMetric metric[JPW_COCKPIT_METRIC_COUNT];
  };

// Stable route/action names; V3 adds one visual bit, never a cycle/account ID.
enum JPW_COCKPIT_ROUTE
  {
   JPW_ROUTE_SCENARIOS=0, JPW_ROUTE_DECLARE=1, JPW_ROUTE_JUSTIFY=2,
   JPW_ROUTE_BIND=3, JPW_ROUTE_LEGACY_SUMMARY=4, JPW_ROUTE_LEGACY_NF=5,
   JPW_ROUTE_FACTOR=6, JPW_ROUTE_OVERVIEW=7, JPW_ROUTE_METRIC=8,
   JPW_ROUTE_PROVENANCE=9, JPW_ROUTE_SETTINGS=10, JPW_ROUTE_STOPS=11,
   JPW_ROUTE_RAIZN=12, JPW_ROUTE_SYSTEM=13, JPW_ROUTE_STOP_ROW=14,
   JPW_ROUTE_EXPORT=15, JPW_ROUTE_LEDGER_CYCLES=16,
   JPW_ROUTE_PERSONAL_HISTORY=17, JPW_ROUTE_PERSONAL_DETAIL=18, JPW_ROUTE_PERSONAL_EXPORT=19
  };
enum JPW_COCKPIT_ACTION
  {
   JPW_ACTION_DECLARE=0, JPW_ACTION_BIND=1, JPW_ACTION_LEGACY_APPLY=2,
   JPW_ACTION_LEGACY_CANCEL=5, JPW_ACTION_COMPARE=6,
   JPW_ACTION_LEGACY_PREVIOUS=7, JPW_ACTION_LEGACY_NEXT=8,
   JPW_ACTION_HOME=10, JPW_ACTION_FACTOR=11, JPW_ACTION_ADVANCED=12,
   JPW_ACTION_REFRESH=13, JPW_ACTION_LEGACY_NF=14,
   JPW_ACTION_FACTOR_15=15, JPW_ACTION_FACTOR_18=16,
   JPW_ACTION_PRIMARY=20, JPW_ACTION_SECONDARY=21,
   JPW_ACTION_APPLY=27, JPW_ACTION_CANCEL=28, JPW_ACTION_RESET=29,
   JPW_ACTION_CORNER=30, JPW_ACTION_DENSITY=31, JPW_ACTION_CLOSE=37,
   JPW_ACTION_PREVIOUS=38, JPW_ACTION_NEXT=39, JPW_ACTION_TAB_FIRST=40,
   JPW_ACTION_TAB_STOPS=41, JPW_ACTION_TAB_RAIZN=42,
   JPW_ACTION_TAB_SYSTEM=43, JPW_ACTION_TAB_SETTINGS=44,
   JPW_ACTION_HEADER_CLOSE=45, JPW_ACTION_POSITIONS_SCOPE=46,
   JPW_ACTION_POSITIONS_UP=47, JPW_ACTION_POSITIONS_DOWN=48,
   JPW_ACTION_CARD_FIRST=50, JPW_ACTION_VISIBILITY_FIRST=60,
   JPW_ACTION_STOP_ROW_FIRST=80, JPW_ACTION_EXPORT=96,
   JPW_ACTION_LEDGER_CYCLE_FIRST=100, JPW_ACTION_TAB_HISTORY=120,
   JPW_ACTION_HISTORY_ACCOUNT=121, JPW_ACTION_HISTORY_REFRESH=122,
   JPW_ACTION_HISTORY_ROW_FIRST=130
  };
string JPWCockpitCornerName(const int corner)
  {
   if(corner==CORNER_LEFT_UPPER) return("Superior esquerdo");
   if(corner==CORNER_LEFT_LOWER) return("Inferior esquerdo");
   if(corner==CORNER_RIGHT_UPPER) return("Superior direito");
   if(corner==CORNER_RIGHT_LOWER) return("Inferior direito");
   return("Canto inválido");
  }
int JPWCockpitNextCorner(const int corner)
  {
   if(corner==CORNER_LEFT_UPPER) return(CORNER_RIGHT_UPPER);
   if(corner==CORNER_RIGHT_UPPER) return(CORNER_RIGHT_LOWER);
   if(corner==CORNER_RIGHT_LOWER) return(CORNER_LEFT_LOWER);
   return(CORNER_LEFT_UPPER);
  }
int JPWCockpitHUDTarget(const bool summary,const int summary_source,const int object_index)
  { return(summary ? summary_source : object_index); }

void JPWCockpitDefault(JPWCockpitPrefs &prefs,const int initial_corner=0)
  {
   prefs.visible_mask=JPW_COCKPIT_ALL_VISIBLE;
   prefs.corner=(initial_corner>=0 && initial_corner<=3 ? initial_corner : 0);
   prefs.density=0;
  }

bool JPWCockpitValid(JPWCockpitPrefs &prefs)
  {
   return(prefs.visible_mask>=0 && prefs.visible_mask<=JPW_COCKPIT_ALL_VISIBLE &&
          prefs.corner>=0 && prefs.corner<=3 &&
          (prefs.density==0 || prefs.density==1));
  }

int JPWCockpitChecksumVersion(JPWCockpitPrefs &prefs,const int version)
  {
   return((((version*131+prefs.visible_mask)*131+
             prefs.corner)*131+prefs.density)%1000003);
  }

int JPWCockpitChecksum(JPWCockpitPrefs &prefs)
  { return(JPWCockpitChecksumVersion(prefs,JPW_COCKPIT_PREF_VERSION)); }

string JPWCockpitEncode(JPWCockpitPrefs &prefs)
  {
   if(!JPWCockpitValid(prefs)) return("");
   return(StringFormat("JPWCOCKPIT|%d|%d|%d|%d|%d",
                       JPW_COCKPIT_PREF_VERSION,prefs.visible_mask,
                       prefs.corner,prefs.density,JPWCockpitChecksum(prefs)));
  }

bool JPWCockpitParseUnsigned(const string raw,int &value)
  {
   value=0;
   if(raw=="" || StringLen(raw)>8) return(false);
   for(int i=0;i<StringLen(raw);i++)
     {
      const ushort digit=StringGetCharacter(raw,i);
      if(digit<'0' || digit>'9' || value>1000000) return(false);
      value=value*10+(int)(digit-'0');
     }
   return(true);
  }

bool JPWCockpitDecode(const string encoded,JPWCockpitPrefs &prefs)
  {
   string part[];
   if(StringSplit(encoded,'|',part)!=6 || part[0]!="JPWCOCKPIT") return(false);
   int version=0,mask=0,corner=0,density=0,checksum=0;
   if(!JPWCockpitParseUnsigned(part[1],version) ||
      !JPWCockpitParseUnsigned(part[2],mask) ||
      !JPWCockpitParseUnsigned(part[3],corner) ||
      !JPWCockpitParseUnsigned(part[4],density) ||
      !JPWCockpitParseUnsigned(part[5],checksum) ||
      (version!=1 && version!=2 && version!=JPW_COCKPIT_PREF_VERSION)) return(false);
   JPWCockpitPrefs candidate;
   candidate.visible_mask=mask; candidate.corner=corner; candidate.density=density;
   // Check the OLD checksum before adding bits. Preserve every old bit,
   // corner and density, including a deliberately all-hidden template.
   if(version==1 || version==2)
     {
      const int maximum=(version==1 ? 31 : 63);
      if(mask<0 || mask>maximum || corner<0 || corner>3 || density<0 || density>1 ||
         JPWCockpitChecksumVersion(candidate,version)!=checksum) return(false);
      candidate.visible_mask=(mask==0 ? 0 : mask|(version==1 ? 96 : 64));
     }
   if(!JPWCockpitValid(candidate) ||
      (version==JPW_COCKPIT_PREF_VERSION && JPWCockpitChecksum(candidate)!=checksum))
      return(false);
   prefs=candidate;
   return(true);
  }

bool JPWCockpitVisible(JPWCockpitPrefs &prefs,const int metric)
  { return(metric>=0 && metric<JPW_COCKPIT_METRIC_COUNT &&
         ((prefs.visible_mask & (1<<metric))!=0)); }

string JPWCockpitQualityText(const JPW_VIEW_QUALITY quality)
  {
   if(quality==JPW_VIEW_CURRENT) return("Current");
   if(quality==JPW_VIEW_ESTIMATED) return("Estimated");
   return("N/A");
  }

#endif
