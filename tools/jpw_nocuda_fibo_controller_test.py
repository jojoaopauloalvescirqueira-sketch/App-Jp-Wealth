#!/usr/bin/env python3
"""Run the production controller+sync+core+capture+store with real host SQLite.
Only MT5 APIs and presentation are seams; no replacement of controller logic.
"""
from pathlib import Path
import argparse, importlib.util, hashlib, json, re, shutil, subprocess, tempfile, sys
ROOT=Path(__file__).resolve().parents[1];INC=ROOT/'mt5/jpw-alavancagem-atual/MQL5/Include/JPWealth'
def module(name,file):
    spec=importlib.util.spec_from_file_location(name,ROOT/'tools'/file);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
ct=module('core','jpw_nocuda_fibo_test.py');db=module('db','jpw_nocuda_fibo_store_runtime_test.py');term=module('term','jpw_nocuda_fibo_terminal_test.py')
UISEAMS=r'''
#define JPW_PRODUCT_VERSION string("1.16.0")
#define JPW_BUILD_ID string("HOST_SYNTHETIC_BUILD")
#define _Period period
#define _Symbol symbol
#define ACCOUNT_SERVER 101
#define PERIOD_M15 15
#define PERIOD_M30 30
#define PERIOD_H1 60
#define PERIOD_H4 16388
#define PERIOD_D1 16408
#define PERIOD_W1 32769
#define OBJ_ALL_PERIODS 2097151
#define OBJ_NO_PERIODS 0
#define OBJ_LABEL 90
#define OBJ_EDIT 91
#define SYMBOL_CHART_MODE 1
#define SYMBOL_CHART_MODE_LAST 1
#define SYMBOL_DIGITS 2
#define TERMINAL_CONNECTED 1
#define TERMINAL_DATA_PATH 2
#define TERMINAL_KEYSTATE_SHIFT 3
#define TIME_DATE 1
#define TIME_MINUTES 2
#define TIME_SECONDS 4
#define CHART_EVENT_MOUSE_MOVE 1
#define CHART_EVENT_OBJECT_DELETE 2
#define CHART_EVENT_OBJECT_CREATE 3
#define CHART_EVENT_MOUSE_WHEEL 4
#define CHARTEVENT_CUSTOM 1000
#define CHARTEVENT_OBJECT_CHANGE 1
#define CHARTEVENT_OBJECT_DRAG 2
#define CHARTEVENT_OBJECT_DELETE 3
#define CHARTEVENT_MOUSE_MOVE 4
#define CHARTEVENT_OBJECT_ENDEDIT 5
#define CHARTEVENT_OBJECT_CLICK 6
#define CHARTEVENT_KEYDOWN 7
#define CHARTEVENT_CHART_CHANGE 8
#define CHARTEVENT_MOUSE_WHEEL 9
#define JPW_UI_OWNER_EVENT 17
#define clrNONE -1
int InpSourceTimeframe=60,InpMaxQuoteAgeSeconds=30;
string g_nocuda_symbol="SYNTHETIC",g_nocuda_feed="TEST_ONLY",g_nocuda_prefix="TEST_";
bool g_nocuda_panel_open=false,g_nocuda_panel_focus=false,g_nocuda_canvas_ready=false;
struct FakeCanvas{void Destroy(){}}g_nocuda_canvas;
string g_fc_editing,g_fc_focus,ui_owner;
JPWNoCudaFiboUIPrefs g_fc_pref;
JPWNoCudaFiboUILayout g_fc_layout;
void JPWNoCudaFiboUILoadPrefs(){}
void JPWNoCudaFiboUIScroll(int){}
std::map<string,string>action_ids;
template<class T>T MathMax(T a,T b){return std::max(a,b);}
template<class T>T MathMin(T a,T b){return std::min(a,b);}
string EnumToString(int n){return "TF"+std::to_string(n);}
string DoubleToString(double v,int digits){char b[128];std::snprintf(b,sizeof(b),"%.*f",digits,v);return b;}
string TimeToString(long t,int){return std::to_string(t);}
long StringToTime(const string&t){return StringToInteger(t);}
int StringReplace(string&s,const string&a,const string&b){int n=0;size_t pos=0;while((pos=s.find(a,pos))!=string::npos){s.replace(pos,a.size(),b);pos+=b.size();n++;}return n;}
int StringTrimLeft(string&s){auto n=s.find_first_not_of(" \t\r\n");int c=n==string::npos?(int)s.size():(int)n;s.erase(0,c);return c;}
int StringTrimRight(string&s){auto n=s.find_last_not_of(" \t\r\n");int c=n==string::npos?(int)s.size():(int)(s.size()-n-1);s.resize(s.size()-c);return c;}
int StringSplit(const string&s,char delimiter,std::vector<string>&out){out.clear();size_t at=0;for(;;){auto end=s.find(delimiter,at);out.push_back(s.substr(at,end==string::npos?string::npos:end-at));if(end==string::npos)break;at=end+1;}return (int)out.size();}
long ObjectGetInteger(long c,const string&n,ENUM_OBJECT_PROPERTY_INTEGER p,int i=0){long v=0;ObjectGetInteger(c,n,p,i,v);return v;}
double ObjectGetDouble(long c,const string&n,ENUM_OBJECT_PROPERTY_DOUBLE p,int i=0){double v=0;ObjectGetDouble(c,n,p,i,v);return v;}
string ObjectGetString(long c,const string&n,ENUM_OBJECT_PROPERTY_STRING p,int i=0){string v;ObjectGetString(c,n,p,i,v);return v;}
bool ObjectSetString(long c,const string&n,int p,const string&v){return ObjectSetString(c,n,p,0,v);}
struct MqlTick{double bid,ask,last;long time;};
struct MqlRates{long time;double open,high,low,close;};
bool SymbolInfoInteger(const string&,int prop,long&v){v=prop==SYMBOL_DIGITS?5:0;return true;}
long SymbolInfoInteger(const string&s,int prop){long v;SymbolInfoInteger(s,prop,v);return v;}
bool SymbolInfoTick(const string&,MqlTick&t){t.bid=1.12;t.ask=1.13;t.last=1.12;t.time=1800000000;return true;}
long TimeTradeServer(){return 1800000000;}
string AccountInfoString(int){return synthetic_feed;}
long TerminalInfoInteger(int prop){return prop==TERMINAL_CONNECTED?1:0;}
string TerminalInfoString(int){return "SYNTHETIC_INSTALLATION";}
unsigned long GetMicrosecondCount(){static unsigned long n=10000;return ++n;}
bool ChartSetInteger(long,int,long){return true;}
int CopyRates(const string&,int,int shift,int count,std::vector<MqlRates>&out){if(flip_feed_during_rates){synthetic_feed="SYNTHETIC_RACE_FEED";flip_feed_during_rates=false;}if(shift<0||count!=1||shift>=(int)times.size())return 0;out.resize(1);out[0]={times[times.size()-1-shift],1.1,1.3,1.0,1.2};return 1;}
void JPWNoCudaReadJustification(){}
void JPWNoCudaUIClear(const string&){}
bool JPWUIAcquire(const string&p){ui_owner=p;return true;}
bool JPWUIOwns(const string&p){return ui_owner==p;}
string JPWUIOwner(){return ui_owner;}
int manual_paints=0,manual_ui_draws=0;
void JPWNoCudaPaint(){manual_paints++;}
void JPWNoCudaDrawUI(){manual_ui_draws++;}
void JPWUIRelease(const string&p){if(ui_owner==p)ui_owner="";}
void JPWNoCudaFiboUIClear(const string&){}
void JPWNoCudaFiboUIDraw(const string&,const JPWNoCudaFiboView&){}
void JPWNoCudaFiboUIFieldCapture(const string&,JPWNoCudaFiboView&){}
bool JPWNoCudaFiboUIActions(const string&){return false;}
string JPWNoCudaFiboUIActionID(const string&a){return action_ids[a];}
string JPWNoCudaFiboUIName(const string&p,const string&a){return p+"FC_"+a;}
string JPWNoCudaFiboUIHitAction(const string&p,const string&n){string prefix=p+"FC_";return n.rfind(prefix,0)==0?n.substr(prefix.size()):"";}
string JPWNoCudaFiboUIFocusCycle(const string&n,bool){return n;}
bool JPWNoCudaFiboUIHandleGeometry(const string&,int,long,double,const string&){return false;}
'''

CONTEXTSEAMS=r'''
string g_nocuda_store_key,g_nocuda_preferred_study,g_nocuda_date,g_nocuda_level_input,g_nocuda_ui_editing,g_nocuda_status;
JPWNoCudaRecord g_nocuda_head,g_nocuda_view,g_nocuda_draft;
std::vector<string> g_nocuda_studies;
int g_nocuda_study_index=-1,g_nocuda_pick=0,g_nocuda_level=36,g_nocuda_source_tf=60;
bool g_nocuda_has_head=false,g_nocuda_has_view=false,g_nocuda_is_draft=false,g_nocuda_visible=true,g_nocuda_full_mesh=true,InpFullMesh=true;
bool g_nocuda_pending_pick=false,g_nocuda_recent_object=false,g_nocuda_skip_field_capture=false,g_nocuda_geometry_valid=false,g_nocuda_history_diverged=false;
long g_nocuda_a_open=0,g_nocuda_b_open=0,g_nocuda_c_open=0,g_nocuda_a_known=0,g_nocuda_b_known=0,g_nocuda_c_known=0;
double g_nocuda_a_close=0,g_nocuda_b_close=0,g_nocuda_c_close=0;
void JPWNoCudaRemoveDrawingObjects(const string&){}
void JPWNoCudaLoadChartState(){}
void JPWNoCudaReloadStudies(){}
void JPWNoCudaClearDaily(){}
'''

TEST=r'''
long CountSyntheticRows(const string&key,const string&table){int handle=-1;string reason;long result=-1;if(JPWNCFStoreOpen(key,false,handle,reason)!=JPW_NCF_VALID)return -1;int q=DatabasePrepare(handle,"SELECT COUNT(*) FROM "+table);if(q>=0&&DatabaseRead(q))DatabaseColumnLong(q,0,result);if(q>=0)DatabaseFinalize(q);DatabaseClose(handle);return result;}
int main(int argc,char**argv){if(argc!=2)return 2;root_path=argv[1];JPWNCFSnapshot seed;NCFFixture(seed);times=seed.opens;string reason;
NCFCheck(JPWNCFClone(0,"JPWNCF_seed",seed,reason)==JPW_NCF_VALID,"fixture native object");objects["native"]=objects["JPWNCF_seed"];objects["other"]=objects["JPWNCF_seed"];objects.erase("JPWNCF_seed");
JPWNCFInit();action_ids["FC_SOURCE_0"]="native";action_ids["FC_SOURCE_1"]="other";
JPWNCFAction("FC_OPEN");NCFCheck(g_ncf_ui.open&&JPWUIOwns(g_nocuda_prefix),"open acquires UI focus");
JPWNCFAction("FC_SOURCE_0");JPWNCFAction("FC_IMPORT");NCFCheck(g_ncf_import,"explicit import preview");JPWNCFAction("FC_CONFIRM_IMPORT");
NCFCheck(g_ncf_has&&g_ncf_link&&g_ncf_head.revision==1,"confirm stores exact snapshot");
for(int i=0;i<3;i++){elapsed+=100;JPWNCFTimer();}NCFCheck(g_ncf_head.revision==1,"ticks without source edit do not persist");
JPWNCFAction("FC_IMPORT");string frozen_preview=JPWNCFPack(g_ncf_preview);double original_c=objects["native"].doubles[{OBJPROP_PRICE,2}];objects["native"].doubles[{OBJPROP_PRICE,2}]+=0.0005;
elapsed=700;JPWNCFTimer();NCFCheck(JPWNCFPack(g_ncf_preview)==frozen_preview&&g_ncf_head.revision==1,"import preview frozen while timer runs");JPWNCFAction("FC_IMPORT_CANCEL");NCFCheck(!g_ncf_import&&g_ncf_has&&g_ncf_sync.armed&&g_ncf_head.revision==1,"cancel preserves prior study and mode");objects["native"].doubles[{OBJPROP_PRICE,2}]=original_c;
int revision=g_ncf_head.revision;for(int i=0;i<5;i++)JPWNCFDraw();
JPWNCFHead h;JPWNCFSnapshot load;NCFCheck(JPWNCFLoadHead(g_ncf_key,g_ncf_id,h,load,reason)==JPW_NCF_VALID&&h.revision==revision,"redraw never persists");
objects["native"].doubles[{OBJPROP_PRICE,1}]+=0.0001;elapsed=1000;JPWNCFHandleEvent(CHARTEVENT_OBJECT_DRAG,0,0,"native");JPWNCFTimer();elapsed=1800;JPWNCFTimer();
NCFCheck(g_ncf_head.revision==2,"completed stable gesture creates one revision");JPWNCFHandleEvent(CHARTEVENT_OBJECT_DRAG,0,0,"native");elapsed=2600;JPWNCFTimer();NCFCheck(g_ncf_head.revision==2,"duplicate finish does not duplicate revision");
objects["native"].doubles[{OBJPROP_PRICE,2}]+=0.0001;elapsed=2700;JPWNCFTimer();elapsed=3400;JPWNCFTimer();NCFCheck(g_ncf_head.revision==2,"old finish cannot authorize later programmatic change");
JPWNCFHandleEvent(CHARTEVENT_MOUSE_MOVE,0,0,"1");objects["native"].doubles[{OBJPROP_PRICE,1}]+=0.0001;JPWNCFHandleEvent(CHARTEVENT_OBJECT_DRAG,0,0,"native");JPWNCFTimer();elapsed=4200;JPWNCFTimer();NCFCheck(g_ncf_head.revision==2,"held mouse prevents checkpoint");
JPWNCFHandleEvent(CHARTEVENT_MOUSE_MOVE,0,0,"0");catalog_page_queries=0;JPWNCFTimer();NCFCheck(catalog_page_queries==0&&g_ncf_records_dirty,"timer save defers record metadata refresh");NCFCheck(g_ncf_head.revision==3,"release finishes one revision");
g_ncf_ui.selected_value="-1.5";JPWNCFAction("FC_LEVEL_APPLY");g_ncf_ui.selected_value="abc";JPWNCFAction("FC_LEVEL_APPLY");NCFCheck(g_ncf_selected_raw==-1.5&&g_ncf_saved.levels[g_ncf_level].value==-1.5,"malformed raw level not silently zero");
JPWNCFLevel original_level=g_ncf_saved.levels[0];g_ncf_saved.levels[0]=g_ncf_saved.levels[g_ncf_level];g_ncf_saved.levels[g_ncf_level]=original_level;JPWNCFInvalidateMeasures();NCFCheck(g_ncf_level==0&&g_ncf_selected_raw==-1.5,"selected raw level survives source array reorder");JPWNCFCopy(g_ncf_preview,g_ncf_saved);JPWNCFInvalidateMeasures();
JPWNCFAction("FC_SOURCE_HIDE");NCFCheck(g_ncf_hidden&&objects["native"].ints[{OBJPROP_TIMEFRAMES,0}]==0,"hide source after explicit command");JPWNCFAction("FC_SOURCE_1");
NCFCheck(!g_ncf_link&&!g_ncf_sync.armed,"selection cannot replace source while linked");NCFCheck(objects["native"].ints[{OBJPROP_TIMEFRAMES,0}]==seed.timeframes,"selection restores former source visibility");
JPWNCFAction("FC_SOURCE_0");JPWNCFAction("FC_SYNC_RESUME");NCFCheck(g_ncf_link,"resume explicitly rechecks origin");
times[3]++;elapsed=40000;JPWNCFTimer();NCFCheck(!g_ncf_sync.armed&&g_ncf_head.revision==3,"history correction suspends without new revision");times=seed.opens;
JPWNCFAction("FC_SYNC_RESUME");NCFCheck(!g_ncf_sync.armed,"resume alone cannot accept corrected history");
objects["native"].ints[{OBJPROP_TIMEFRAMES,0}]=2048;
JPWNCFAction("FC_REFRESH_SOURCE");NCFCheck(!g_ncf_sync.armed&&g_ncf_head.paused==1&&g_ncf_head.revision==4,"explicit history revision accepted while preserving paused follow mode");
JPWNCFAction("FC_SYNC_RESUME");NCFCheck(g_ncf_sync.armed&&g_ncf_head.revision==4,"explicit resume follows the accepted history without another revision");
NCFCheck(g_ncf_original_mask==2048&&g_ncf_saved.timeframes==2048,"explicit history acceptance updates restore mask");
JPWNCFAction("FC_SOURCE_HIDE");NCFCheck(g_ncf_hidden&&objects["native"].ints[{OBJPROP_TIMEFRAMES,0}]==0,"history revision source can be hidden");
JPWNCFAction("FC_SOURCE_SHOW");NCFCheck(!g_ncf_hidden&&objects["native"].ints[{OBJPROP_TIMEFRAMES,0}]==2048,"show after history revision restores its updated visibility");
period=15;objects["native"].doubles[{OBJPROP_PRICE,1}]+=0.0001;JPWNCFHandleEvent(CHARTEVENT_OBJECT_DRAG,0,0,"native");JPWNCFTimer();NCFCheck(!g_ncf_sync.armed&&g_ncf_head.revision==4,"edit in other TF suspends without reinterpretation");
period=60;JPWNCFAction("FC_SYNC_RESUME");JPWNCFTimer();elapsed=41000;JPWNCFTimer();NCFCheck(g_ncf_head.revision==5,"reference TF plus explicit resume accepts revised properties");
JPWNCFAction("FC_SOURCE_HIDE");objects["native"].ints[{OBJPROP_TIMEFRAMES,0}]=1024;elapsed=42000;JPWNCFHandleEvent(CHARTEVENT_OBJECT_CHANGE,0,0,"native");JPWNCFTimer();elapsed=42800;JPWNCFTimer();
NCFCheck(!g_ncf_hidden&&g_ncf_original_mask==1024&&g_ncf_head.revision==6,"user native visibility change replaces restored mask");
JPWNCFAction("FC_SOURCE_HIDE");JPWNCFAction("FC_UNLINK");NCFCheck(objects["native"].ints[{OBJPROP_TIMEFRAMES,0}]==1024,"unlink restores latest confirmed user visibility");
JPWNCFAction("FC_SYNC_RESUME");objects["renamed"]=objects["native"];objects.erase("native");JPWNCFHandleEvent(CHARTEVENT_OBJECT_DELETE,0,0,"native");NCFCheck(!g_ncf_link&&g_ncf_sync.phase==JPW_NCF_DETACHED,"rename delete event cannot reconnect to new name");
NCFCheck(g_ncf_clone!=""&&objects.count(g_ncf_clone),"source deletion leaves independent reference clone");
NCFCheck(JPWNCFLoadHead(g_ncf_key,g_ncf_id,h,load,reason)==JPW_NCF_VALID&&h.revision==6,"source deletion preserves study");
// Metadata browsing must never load full temporal arrays. Direct Save calls below
// construct isolated revisions through the production transaction/CAS path.
JPWNCFSnapshot catalog_seed;JPWNCFCopy(g_ncf_saved,catalog_seed);bool fixture_ok=true;
for(int i=0;i<25;i++){catalog_seed.anchor_price[2]+=0.000001;JPWNCFHead next;fixture_ok=fixture_ok&&JPWNCFSave(g_ncf_key,g_ncf_id,g_ncf_head.generation,catalog_seed,"metadata paging fixture",next,reason)==JPW_NCF_VALID;g_ncf_head=next;}
NCFCheck(fixture_ok&&g_ncf_head.revision==31,"isolated catalog fixture creates immutable revisions");JPWNCFCopy(catalog_seed,g_ncf_saved);
payload_selects=0;catalog_reads=0;JPWNCFAction("FC_RECORD_VERSIONS");
NCFCheck(g_ncf_ui.records.size()==20&&g_ncf_catalog_more&&g_ncf_catalog_offset==0,"first controller catalog page bounded twenty");
NCFCheck(payload_selects==0&&catalog_reads==21,"first catalog page only limit plus one metadata");
string first_record=g_ncf_ui.records[0].id;payload_selects=0;catalog_reads=0;JPWNCFAction("FC_RECORD_NEXT");
NCFCheck(g_ncf_ui.records.size()==11&&!g_ncf_catalog_more&&g_ncf_catalog_offset==20,"second catalog page remaining metadata");
NCFCheck(payload_selects==0&&catalog_reads==11,"next page avoids temporal payloads");
JPWNCFAction("FC_RECORD_PREV");NCFCheck(g_ncf_catalog_offset==0&&g_ncf_ui.records[0].id==first_record,"back restores metadata page");
int before_generation=g_ncf_head.generation;string before_restore=JPWNCFPack(g_ncf_saved);g_ncf_record_revision=999;JPWNCFAction("FC_RESTORE_RECORD");
NCFCheck(g_ncf_head.generation==before_generation&&JPWNCFPack(g_ncf_saved)==before_restore,"failed restore preload preserves accepted snapshot");
JPWNCFSnapshot earliest;NCFCheck(JPWNCFLoadRevision(g_ncf_key,g_ncf_id,1,earliest,reason)==JPW_NCF_VALID,"restore target available");g_ncf_record_revision=1;JPWNCFAction("FC_RESTORE_RECORD");
NCFCheck(g_ncf_head.revision==32&&g_ncf_head.paused==1&&!g_ncf_sync.armed&&!g_ncf_link&&JPWNCFPack(g_ncf_saved)==JPWNCFPack(earliest),"restore creates new paused revision from preloaded target");
// Synthetic focus broker: controller event routing is real; native focus itself
// is not claimed by this host suite.
JPWNCFAction("FC_OPEN");JPWNCFHandleEvent(CHARTEVENT_CUSTOM+JPW_UI_OWNER_EVENT,0,0,"stale_owner");NCFCheck(g_ncf_ui.open,"stale queued ownership event cannot close current window");
ui_owner="other_indicator";JPWNCFHandleEvent(CHARTEVENT_CUSTOM+JPW_UI_OWNER_EVENT,0,0,"other_indicator");NCFCheck(!g_ncf_ui.open,"current other owner closes this cockpit");
JPWNCFAction("FC_OPEN");int before_manual_paints=manual_paints,before_manual_ui=manual_ui_draws;JPWNCFHandleEvent(CHARTEVENT_OBJECT_CLICK,0,0,JPWNoCudaFiboUIName(g_nocuda_prefix,"FC_MANUAL"));
NCFCheck(!g_ncf_mode&&g_nocuda_panel_open&&manual_paints==before_manual_paints+1&&manual_ui_draws==before_manual_ui+1,"manual transition paints in same event");
JPWNCFHandleEvent(CHARTEVENT_OBJECT_CLICK,0,0,JPWNoCudaFiboUIName(g_nocuda_prefix,"FC_OPEN"));NCFCheck(g_ncf_mode&&g_ncf_ui.open&&!g_nocuda_panel_open,"Fibonacci reopen exits manual panel immediately");
JPWNCFAction("FC_CLOSE");NCFCheck(!g_ncf_ui.open&&!JPWUIOwns(g_nocuda_prefix),"close accessible releases focus");
// Exercise the real main-indicator context reset in both modes. Legacy chart
// loading/rendering are seams; legacy key derivation/record clearing are real.
const string old_key=g_ncf_key;JPWNCFHead old_head;JPWNCFSnapshot old_snapshot;
NCFCheck(JPWNCFLoadHead(old_key,g_ncf_id,old_head,old_snapshot,reason)==JPW_NCF_VALID,"old feed captured before reset");const string old_id=g_ncf_id;
g_ncf_mode=false;g_nocuda_store_key="STALE_LEGACY_KEY";g_nocuda_has_head=true;g_nocuda_head.study_id="old";g_nocuda_is_draft=true;g_nocuda_draft.study_id="draft";g_nocuda_studies.push_back("old");g_nocuda_a_open=123;g_nocuda_pending_pick=true;
synthetic_feed="SYNTHETIC_FEED_B";JPWNoCudaResetContext(symbol,synthetic_feed);const string key_b=g_ncf_key;string expected_legacy;
JPWNoCudaStoreKey("SYNTHETIC_INSTALLATION","SYNTHETIC_FEED_B",expected_legacy);
NCFCheck(key_b!=old_key&&g_nocuda_store_key==expected_legacy&&!g_ncf_has&&!g_ncf_link,"manual-mode reset replaces both feed store keys");
NCFCheck(!g_nocuda_has_head&&!g_nocuda_is_draft&&g_nocuda_head.study_id==""&&g_nocuda_draft.study_id==""&&g_nocuda_studies.empty()&&g_nocuda_a_open==0&&!g_nocuda_pending_pick,"context invalidates stale manual data and draft");
JPWNCFHandleEvent(CHARTEVENT_OBJECT_CLICK,0,0,JPWNoCudaFiboUIName(g_nocuda_prefix,"FC_OPEN"));action_ids["FC_SOURCE_2"]="renamed";JPWNCFAction("FC_SOURCE_2");JPWNCFAction("FC_IMPORT");JPWNCFAction("FC_CONFIRM_IMPORT");
NCFCheck(g_ncf_has&&g_ncf_key==key_b&&g_ncf_saved.feed=="SYNTHETIC_FEED_B"&&g_ncf_head.revision==1,"switch from manual then import writes only new feed");
NCFCheck(JPWNCFLoadHead(old_key,old_id,h,load,reason)==JPW_NCF_VALID&&h.generation==old_head.generation,"feed B import does not mutate feed A study");
const string feed_b_id=g_ncf_id;synthetic_feed="SYNTHETIC_FEED_C";JPWNoCudaResetContext(symbol,synthetic_feed);const string key_c=g_ncf_key;
NCFCheck(key_c!=old_key&&key_c!=key_b&&!g_ncf_has&&g_nocuda_feed=="SYNTHETIC_FEED_C","Fibonacci-mode reset invalidates account feed context");
JPWNCFAction("FC_MANUAL");JPWNCFHandleEvent(CHARTEVENT_OBJECT_CLICK,0,0,JPWNoCudaFiboUIName(g_nocuda_prefix,"FC_OPEN"));JPWNCFAction("FC_SOURCE_2");JPWNCFAction("FC_IMPORT");JPWNCFAction("FC_CONFIRM_IMPORT");
NCFCheck(g_ncf_has&&g_ncf_key==key_c&&g_ncf_saved.feed=="SYNTHETIC_FEED_C"&&g_ncf_head.revision==1,"mode roundtrip after reset cannot reuse old feed key");
NCFCheck(JPWNCFLoadHead(key_b,feed_b_id,h,load,reason)==JPW_NCF_VALID&&h.revision==1,"feed C import leaves feed B study intact");
// The live server seam may change from inside a terminal API. The guard below
// is the actual production JPWNCFContextCurrent, not a test replacement.
const string race_key=g_ncf_key,race_id=g_ncf_id;const long revisions_before_races=CountSyntheticRows(race_key,"fibo_revisions"),heads_before_races=CountSyntheticRows(race_key,"fibo_heads");
JPWNCFAction("FC_IMPORT");NCFCheck(g_ncf_import,"race confirm begins from valid frozen preview");flip_feed_during_time=true;JPWNCFAction("FC_CONFIRM_IMPORT");
NCFCheck(synthetic_feed=="SYNTHETIC_RACE_FEED"&&!g_ncf_has&&!g_ncf_link&&!g_ncf_import&&!g_ncf_sync.armed,"feed flip during confirm capture invalidates context");
NCFCheck(CountSyntheticRows(race_key,"fibo_revisions")==revisions_before_races&&CountSyntheticRows(race_key,"fibo_heads")==heads_before_races,"confirm race cannot create a study or revision");
synthetic_feed="SYNTHETIC_FEED_C";JPWNoCudaResetContext(symbol,synthetic_feed);JPWNCFAction("FC_OPEN");JPWNCFAction("FC_SYNC_RESUME");
NCFCheck(g_ncf_has&&g_ncf_link&&g_ncf_sync.armed,"race timer fixture resumes stored study");objects["renamed"].doubles[{OBJPROP_PRICE,1}]+=0.0001;elapsed=50000;JPWNCFHandleEvent(CHARTEVENT_OBJECT_DRAG,0,0,"renamed");JPWNCFTimer();
const long revisions_before_timer_race=CountSyntheticRows(race_key,"fibo_revisions");elapsed=50800;flip_feed_during_time=true;JPWNCFTimer();
NCFCheck(synthetic_feed=="SYNTHETIC_RACE_FEED"&&!g_ncf_has&&!g_ncf_link&&!g_ncf_sync.armed,"feed flip during timer capture invalidates context before checkpoint");
NCFCheck(CountSyntheticRows(race_key,"fibo_revisions")==revisions_before_timer_race,"timer capture race cannot write a revision");
synthetic_feed="SYNTHETIC_FEED_C";JPWNoCudaResetContext(symbol,synthetic_feed);JPWNCFAction("FC_OPEN");g_ncf_ui.observation_time=IntegerToString(times[1]);g_ncf_ui.observation_note="Isolated synthetic manual observation";
const long notes_before_race=CountSyntheticRows(race_key,"fibo_notes");flip_feed_during_rates=true;JPWNCFAction("FC_TOUCH_SAVE");
NCFCheck(synthetic_feed=="SYNTHETIC_RACE_FEED"&&!g_ncf_has&&!g_ncf_link&&g_ncf_ui.records.empty(),"feed flip inside CopyRates invalidates manual observation");
NCFCheck(CountSyntheticRows(race_key,"fibo_notes")==notes_before_race,"manual observation race cannot persist a note");
NCFCheck(JPWNCFLoadHead(race_key,race_id,h,load,reason)==JPW_NCF_VALID&&h.revision==1,"all context races preserve original confirmed revision");
synthetic_feed="SYNTHETIC_FEED_C";JPWNoCudaResetContext(symbol,synthetic_feed);symbol="OTHER_SYNTHETIC_SYMBOL";JPWNCFAction("FC_SYNC_PAUSE");
NCFCheck(!g_ncf_has&&!g_ncf_link&&!g_ncf_sync.armed,"symbol change at action entry invalidates current study");
NCFCheck(JPWNCFLoadHead(race_key,race_id,h,load,reason)==JPW_NCF_VALID&&h.revision==1,"entry guard does not mutate original study");symbol="SYNTHETIC";
JPWNCFShutdown();NCFCheck(databases.empty()&&statements.empty(),"no database handles retained");
Print("Controller production flow: ",jpw_ncf_asserts," asserts; failures=",jpw_ncf_failed,"; native NOT_RUN");return jpw_ncf_failed?1:0;}
'''
def transform(s):
    s=re.sub(r'^#include[^\n]*\n','',s,flags=re.M)
    s=s.replace('string names[]','std::vector<string> names').replace('string ids[],reason=""','std::vector<string> ids; string reason=""').replace('string f[]','std::vector<string> f').replace('MqlRates rates[]','std::vector<MqlRates> rates')
    s=re.sub(r'\b(int|string|JPWNCFNoteRow|JPWNCFCatalogRow) ([a-zA-Z_]\w*)\[\];',r'std::vector<\1> \2;',s)
    return s

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--evidence-dir');args=ap.parse_args();compiler=shutil.which('clang++')or shutil.which('g++')
    shim=ct.SHIM.replace('string StringFormat(const char* fmt,double value)','template<class T> string StringFormat(const char* fmt,T value)')
    termshim=term.SHIM.replace('void ResetLastError(){error=0;}int GetLastError(){return error;}','').replace('int error=0,period=60,copy_count=0,mode=0;','int period=60,copy_count=0,mode=0;').replace('error=1','last_error=1')
    termshim=termshim.replace('int period=60,copy_count=0,mode=0;', 'int period=60,copy_count=0,mode=0;string synthetic_feed="TEST_ONLY";bool flip_feed_during_time=false,flip_feed_during_rates=false;').replace('std::vector<long>&out){copy_count++;', 'std::vector<long>&out){if(flip_feed_during_time){synthetic_feed="SYNTHETIC_RACE_FEED";flip_feed_during_time=false;}copy_count++;')
    termshim=termshim.replace('OBJPROP_LEVELWIDTH};','OBJPROP_LEVELWIDTH,OBJPROP_XDISTANCE,OBJPROP_YDISTANCE,OBJPROP_SELECTED};').replace('OBJPROP_LEVELTEXT};','OBJPROP_LEVELTEXT,OBJPROP_TOOLTIP};')
    termshim=termshim.replace('long t1,double p1,long t2,double p2','long t1=0,double p1=0,long t2=0,double p2=0')
    core=db.transform(ct.CORE.read_text());store=db.transform(db.STORE.read_text());terminal=(INC/'JPW_NoCuda_Fibo_Terminal.mqh').read_text()
    terminal=re.sub(r'^#include.*\n','',terminal,flags=re.M).replace('string &names[]','std::vector<string> &names').replace('datetime times[];','std::vector<datetime> times;').replace('datetime verify[];','std::vector<datetime> verify;')
    ui=(INC/'JPW_NoCuda_Fibo_UI.mqh').read_text();types=ui[ui.index('struct JPWNoCudaFiboUIItem'):ui.index('JPWNoCudaFiboUIPrefs g_fc_pref')]
    types=re.sub(r'JPWNoCudaFiboUIItem (\w+)\[\];',r'std::vector<JPWNoCudaFiboUIItem> \1;',types)
    fixture=re.sub(r'^#(?:include|property).*\n','',ct.SCRIPT.read_text(),flags=re.M)
    sync=(INC/'JPW_NoCuda_Fibo_Sync.mqh').read_text();controller=transform((INC/'JPW_NoCuda_Fibo_Controller.mqh').read_text())
    mainpath=ROOT/'mt5/jpw-alavancagem-atual/MQL5/Indicators/JPWealth/JPW_NoCuda_Channels.mq5'
    mainsource=mainpath.read_text()
    context_reset=mainsource[mainsource.index('void JPWNoCudaResetContext('):mainsource.index('void OnTimer()',mainsource.index('void JPWNoCudaResetContext('))]
    clear_anchors=mainsource[mainsource.index('void JPWNoCudaClearAnchors()'):mainsource.index('// The accepted revision',mainsource.index('void JPWNoCudaClearAnchors()'))]
    legacy_path=INC/'JPW_NoCuda_Store.mqh';legacy=legacy_path.read_text()
    legacy_defs=db.transform(legacy[legacy.index('struct JPWNoCudaRecord'):legacy.index('bool JPWNoCudaStoreNewStudyId')])
    legacy_defs=re.sub(r'uchar (\w+)\[\];',r'std::vector<uchar> \1;',legacy_defs)
    dbshim=db.DBSHIM.replace('int payload_selects=0,catalog_reads=0;', 'int payload_selects=0,catalog_reads=0,catalog_page_queries=0;').replace('int DatabasePrepare(int h,const string&q){', 'int DatabasePrepare(int h,const string&q){if(q.rfind("SELECT c.kind",0)==0)catalog_page_queries++;')
    code=shim+dbshim+termshim+'\nconstexpr int OBJ_BUTTON=100;\n'+core+store+db.DBREAD+terminal+types+UISEAMS+sync+controller+legacy_defs+CONTEXTSEAMS+clear_anchors+context_reset+fixture+TEST
    with tempfile.TemporaryDirectory(prefix='jpw-ncf-controller-')as temp:
        src=Path(temp)/'controller.cpp';src.write_text(code);exe=Path(temp)/'controller';flags=['-lsqlite3']+([]if sys.platform=='darwin'else['-lcrypto'])
        compiled=subprocess.run([compiler,'-std=c++17','-Wall','-Wextra','-Werror','-Wno-deprecated-declarations',str(src),'-o',str(exe),*flags],text=True,capture_output=True)
        run=subprocess.run([str(exe),temp],text=True,capture_output=True)if compiled.returncode==0 else None
        files=[ct.CORE,db.STORE,INC/'JPW_NoCuda_Fibo_Terminal.mqh',INC/'JPW_NoCuda_Fibo_Sync.mqh',INC/'JPW_NoCuda_Fibo_Controller.mqh',mainpath,legacy_path,INC/'JPW_NoCuda_Fibo_UI.mqh',Path(__file__)]
        report={'status':'PASS'if run and run.returncode==0 else'PRODUCT_FAIL','scope':'production controller + capture + core + sync + store + main context reset; host SQLite/SHA256; UI and MT5 API seams; legacy key/clear real; legacy loading/drawing outside scope','native':'NOT_RUN','sha256':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest()for p in files},'compiler_log':compiled.stdout+compiled.stderr,'output':run.stdout+run.stderr if run else''}
        if args.evidence_dir:
            out=Path(args.evidence_dir);out.mkdir(parents=True,exist_ok=True);(out/'fibo-controller-runtime.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
        print(json.dumps(report,ensure_ascii=False,indent=2));return 0 if report['status']=='PASS'else 1
if __name__=='__main__':raise SystemExit(main())
