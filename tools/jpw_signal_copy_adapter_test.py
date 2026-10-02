#!/usr/bin/env python3
"""Execute the distributed read-only Signal Copy adapter with synthetic APIs.

Whole native-provider/collector/store/core bodies execute under the host MQL
primitive shim. Fixtures use isolated temporary files and no real terminal.
This is not MetaEditor compilation, native locks/durability, interaction or
clipboard evidence. Receipts identify every exact source and test boundary.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import leverage_config_test as base
import jpw_signal_copy_test as signal_core

ROOT = Path(__file__).resolve().parents[1]
MQL = ROOT / "mt5/jpw-alavancagem-atual/MQL5/Include/JPWealth"
NAMES = ["JPW_Alavancagem_Core.mqh", "JPW_Alavancagem_RaizN_Core.mqh",
         "JPW_SignalCopy_Types.mqh", "JPW_SignalCopy_Core.mqh",
         "JPW_Alavancagem_Profile.mqh", "JPW_Alavancagem_Genesis_Store.mqh",
         "JPW_Alavancagem_RaizN_Store.mqh", "JPW_Alavancagem_RaizN_Factor.mqh",
         "JPW_Alavancagem_RaizN_Live.mqh", "JPW_Alavancagem_RaizN_Horizon.mqh",
         "JPW_SignalCopy_Terminal.mqh"]
FILES = [MQL / name for name in NAMES]

SHIM = r'''
#include <ctime>
#include <set>
using ENUM_ACCOUNT_INFO_DOUBLE=int;
using ENUM_TIMEFRAMES=int;
using ENUM_DAY_OF_WEEK=int;
constexpr int PERIOD_CURRENT=0,PERIOD_H4=240,SERIES_SYNCHRONIZED=1;
enum {ACCOUNT_LOGIN=100,ACCOUNT_MARGIN_MODE,ACCOUNT_SERVER,ACCOUNT_CURRENCY,
 ACCOUNT_BALANCE,ACCOUNT_EQUITY,ACCOUNT_PROFIT,ACCOUNT_CREDIT,
 TERMINAL_DATA_PATH,TERMINAL_CONNECTED,
 SYMBOL_DIGITS,SYMBOL_VOLUME_STEP,SYMBOL_TRADE_CONTRACT_SIZE,SYMBOL_TRADE_CALC_MODE,
 SYMBOL_CURRENCY_BASE,SYMBOL_CURRENCY_PROFIT,SYMBOL_BASIS,SYMBOL_ISIN,SYMBOL_CUSTOM,
 SYMBOL_SELECT,SYMBOL_POINT,SYMBOL_TRADE_TICK_SIZE,SYMBOL_TRADE_TICK_VALUE_PROFIT,
 SYMBOL_TRADE_TICK_VALUE_LOSS,SYMBOL_VOLUME_MIN,SYMBOL_VOLUME_MAX,
 POSITION_IDENTIFIER,POSITION_TIME_MSC,POSITION_TIME_UPDATE_MSC,POSITION_TYPE,
 POSITION_SYMBOL,POSITION_VOLUME,POSITION_PRICE_OPEN,POSITION_SL,POSITION_TP,
 ORDER_TYPE,ORDER_STATE,ORDER_POSITION_ID,ORDER_TIME_SETUP_MSC,ORDER_TIME_EXPIRATION,
 ORDER_SYMBOL,ORDER_VOLUME_CURRENT,ORDER_VOLUME_INITIAL,ORDER_PRICE_OPEN,ORDER_SL,
 ORDER_TP,ORDER_PRICE_STOPLIMIT};
enum {ORDER_STATE_STARTED=0,ORDER_STATE_PLACED=1,ORDER_STATE_CANCELED=2,
 ORDER_STATE_PARTIAL=3,ORDER_STATE_FILLED=4,ORDER_STATE_REJECTED=5,
 ORDER_STATE_EXPIRED=6,ORDER_STATE_REQUEST_ADD=7,ORDER_STATE_REQUEST_MODIFY=8,
 ORDER_STATE_REQUEST_CANCEL=9};
long api_error=0;
ulong api_mono=100000,api_clock_step=1;
datetime api_server=1790856120;
long api_login=424242,api_margin=ACCOUNT_MARGIN_MODE_RETAIL_HEDGING;
string api_currency="USD",api_server_name="SYNTHETIC-only",api_install="SYNTHETIC-install";
double api_balance=1000,api_equity=900,api_profit=-100,api_credit=0;
bool api_connected=true,api_property_failure=false,api_roll=false,api_horizon_failure=false;
int api_positions_reads=0,api_identity_reads=0,api_tp_mutation_at=0,api_tp_mutation_repeat=0;
int api_login_change_at=0,api_balance_change_at=0;

// Row vectors are declared after Types; native property adapters below use an
// independent terminal tuple so collector correctness is not a test copy.
struct NativeRow {ulong ticket;long id,opened,updated;string symbol;int side,type,state;
 long expires;double vol,initial,entry,sl,tp,stoplimit;};
std::vector<NativeRow> native_positions,native_orders;
int selected_position=-1,selected_order=-1;
struct NativeSymbol {string base,profit;int mode=SYMBOL_CALC_MODE_FOREX,digits=5;
 double contract=100000,bid=.5999,ask=.6001,step=.01,point=.00001,tick_size=.00001,
 tick_profit=1,tick_loss=1,atr=.004;long time_msc=0;bool sync=true,selected=true,quote_ok=true;
 int bars=100;};
std::map<string,NativeSymbol> symbols;
std::vector<string> symbol_list;
struct MqlTick {double bid,ask;long time_msc;};
struct MqlDateTime {int year,mon,day,hour,min,sec,day_of_week,day_of_year;};
int api_next_handle=55,api_buffer_reads=0,api_release_reads=0;
std::map<int,string> api_handles;
std::set<string> api_tick_symbols,api_atr_symbols,api_session_symbols;
void ResetLastError(){api_error=0;}
long GetLastError(){return api_error;}
ulong GetTickCount64(){api_mono+=api_clock_step;return api_mono;}
datetime TimeCurrent(){return api_server;}
datetime TimeLocal(){return api_server;}
datetime TimeTradeServer(){return api_server;}
datetime TimeGMT(){return api_server;}
double MathRound(double value){return std::round(value);}
double MathCumulativeDistributionNormal(double x,double mean,double sigma,int &error){
 error=0;return .5*(1+std::erf((x-mean)/(sigma*std::sqrt(2.))));}
bool TimeToStruct(datetime value,MqlDateTime &out){
 std::time_t t=value;std::tm* p=std::gmtime(&t);if(!p)return false;
 out={p->tm_year+1900,p->tm_mon+1,p->tm_mday,p->tm_hour,p->tm_min,p->tm_sec,p->tm_wday,p->tm_yday};return true;}
datetime StringToTime(const string &s){std::tm p={};std::istringstream stream(s);
 stream>>std::get_time(&p,"%Y.%m.%d %H:%M:%S");if(stream.fail())return 0;return timegm(&p);}
long AccountInfoInteger(int property){
 if(property==ACCOUNT_LOGIN){++api_identity_reads;
   if(api_login_change_at>0&&api_identity_reads==api_login_change_at)++api_login;
   if(api_balance_change_at>0&&api_identity_reads==api_balance_change_at)api_balance+=1;
   return api_login;}if(property==ACCOUNT_MARGIN_MODE)return api_margin;api_error=1;return 0;}
string AccountInfoString(int property){if(property==ACCOUNT_SERVER)return api_server_name;
 if(property==ACCOUNT_CURRENCY)return api_currency;api_error=1;return "";}
double AccountInfoDouble(int property){if(api_property_failure&&property==ACCOUNT_PROFIT){api_error=1;return 0;}
 if(property==ACCOUNT_BALANCE)return api_balance;if(property==ACCOUNT_EQUITY)return api_equity;
 if(property==ACCOUNT_PROFIT)return api_profit;if(property==ACCOUNT_CREDIT)return api_credit;api_error=1;return 0;}
string TerminalInfoString(int property){return property==TERMINAL_DATA_PATH?api_install:"";}
long TerminalInfoInteger(int property){return property==TERMINAL_CONNECTED&&api_connected;}
bool SymbolInfoInteger(const string&s,int property,long &out){auto it=symbols.find(s);if(it==symbols.end())return false;
 auto &v=it->second;switch(property){case SYMBOL_DIGITS:out=v.digits;break;
 case SYMBOL_TRADE_CALC_MODE:out=v.mode;break;case SYMBOL_CUSTOM:out=0;break;
 case SYMBOL_SELECT:out=v.selected;break;default:return false;}return true;}
bool SymbolInfoDouble(const string&s,int property,double &out){auto it=symbols.find(s);if(it==symbols.end())return false;
 auto &v=it->second;switch(property){case SYMBOL_VOLUME_STEP:out=v.step;break;
 case SYMBOL_TRADE_CONTRACT_SIZE:out=v.contract;break;case SYMBOL_POINT:out=v.point;break;
 case SYMBOL_TRADE_TICK_SIZE:out=v.tick_size;break;case SYMBOL_TRADE_TICK_VALUE_PROFIT:out=v.tick_profit;break;
 case SYMBOL_TRADE_TICK_VALUE_LOSS:out=v.tick_loss;break;case SYMBOL_VOLUME_MIN:out=.01;break;
 case SYMBOL_VOLUME_MAX:out=100;break;default:return false;}return true;}
bool SymbolInfoString(const string&s,int property,string &out){auto it=symbols.find(s);if(it==symbols.end())return false;
 if(property==SYMBOL_CURRENCY_BASE)out=it->second.base;else if(property==SYMBOL_CURRENCY_PROFIT)out=it->second.profit;
 else if(property==SYMBOL_BASIS||property==SYMBOL_ISIN)out="";else return false;return true;}
bool SymbolSelect(const string&s,bool selected){auto it=symbols.find(s);if(it==symbols.end())return false;it->second.selected=selected;return true;}
bool SymbolInfoTick(const string&s,MqlTick &out){api_tick_symbols.insert(s);auto it=symbols.find(s);
 if(it==symbols.end()||!it->second.quote_ok)return false;auto&v=it->second;out={v.bid,v.ask,v.time_msc};return true;}
bool SeriesInfoInteger(const string&s,int timeframe,int property,long &out){auto it=symbols.find(s);
 if(it==symbols.end()||property!=SERIES_SYNCHRONIZED)return false;out=it->second.sync;return true;}
int SymbolsTotal(bool){return (int)symbol_list.size();}
string SymbolName(int index,bool){return index>=0&&index<(int)symbol_list.size()?symbol_list[index]:"";}
int PositionsTotal(){++api_positions_reads;
 if(!native_positions.empty()&&((api_tp_mutation_at>0&&api_positions_reads==api_tp_mutation_at)||api_tp_mutation_repeat))native_positions[0].tp+=.001;
 return (int)native_positions.size();}
int OrdersTotal(){return (int)native_orders.size();}
ulong PositionGetTicket(int index){selected_position=index;return index>=0&&index<(int)native_positions.size()?native_positions[index].ticket:0;}
bool PositionSelectByTicket(ulong ticket){for(int i=0;i<(int)native_positions.size();i++)if(native_positions[i].ticket==ticket){selected_position=i;return true;}return false;}
bool PositionGetInteger(int property,long &out){if(selected_position<0||api_property_failure)return false;auto&r=native_positions[selected_position];
 if(property==POSITION_IDENTIFIER)out=r.id;else if(property==POSITION_TIME_MSC)out=r.opened;
 else if(property==POSITION_TIME_UPDATE_MSC)out=r.updated;else if(property==POSITION_TYPE)out=r.side;else return false;return true;}
bool PositionGetString(int property,string &out){if(selected_position<0||property!=POSITION_SYMBOL)return false;out=native_positions[selected_position].symbol;return true;}
bool PositionGetDouble(int property,double &out){if(selected_position<0)return false;auto&r=native_positions[selected_position];
 if(property==POSITION_VOLUME)out=r.vol;else if(property==POSITION_PRICE_OPEN)out=r.entry;
 else if(property==POSITION_SL)out=r.sl;else if(property==POSITION_TP)out=r.tp;else return false;return true;}
ulong OrderGetTicket(int index){selected_order=index;return index>=0&&index<(int)native_orders.size()?native_orders[index].ticket:0;}
bool OrderSelect(ulong ticket){for(int i=0;i<(int)native_orders.size();i++)if(native_orders[i].ticket==ticket){selected_order=i;return true;}return false;}
bool OrderGetInteger(int property,long &out){if(selected_order<0)return false;auto&r=native_orders[selected_order];
 if(property==ORDER_TYPE)out=r.type;else if(property==ORDER_STATE)out=r.state;else if(property==ORDER_POSITION_ID)out=r.id;
 else if(property==ORDER_TIME_SETUP_MSC)out=r.opened;else if(property==ORDER_TIME_EXPIRATION)out=r.expires;else return false;return true;}
bool OrderGetString(int property,string &out){if(selected_order<0||property!=ORDER_SYMBOL)return false;out=native_orders[selected_order].symbol;return true;}
bool OrderGetDouble(int property,double &out){if(selected_order<0)return false;auto&r=native_orders[selected_order];
 if(property==ORDER_VOLUME_CURRENT)out=r.vol;else if(property==ORDER_VOLUME_INITIAL)out=r.initial;
 else if(property==ORDER_PRICE_OPEN)out=r.entry;else if(property==ORDER_SL)out=r.sl;else if(property==ORDER_TP)out=r.tp;
 else if(property==ORDER_PRICE_STOPLIMIT)out=r.stoplimit;else return false;return true;}
int iATR(const string&s,int timeframe,int period){api_atr_symbols.insert(s);
 if(!symbols.count(s)||timeframe!=PERIOD_H4||period!=55)return INVALID_HANDLE;
 int handle=api_next_handle++;api_handles[handle]=s;return handle;}
bool IndicatorRelease(int handle){++api_release_reads;return api_handles.erase(handle)>0;}
int Bars(const string&s,int tf){return symbols.count(s)&&tf==PERIOD_H4?symbols[s].bars:0;}
int BarsCalculated(int handle){return api_handles.count(handle)?symbols[api_handles[handle]].bars:0;}
template<size_t N>int CopyTime(const string&s,int tf,int shift,int count,datetime (&out)[N]){
 if(!symbols.count(s)||tf!=PERIOD_H4||count!=1||N!=1||(shift!=0&&shift!=1))return -1;
 out[0]=(api_server/14400)*14400-shift*14400;return 1;}
int CopyTime(const string&s,int tf,datetime start,datetime end,std::vector<datetime>&out){
 out.clear();if(!symbols.count(s)||tf!=PERIOD_H4||api_horizon_failure)return -1;
 for(long t=((start+14399)/14400)*14400;t<=end;t+=14400)out.push_back(t);return (int)out.size();}
template<size_t N>int CopyBuffer(int handle,int buffer,int shift,int count,double (&out)[N]){
 if(!api_handles.count(handle)||buffer!=0||shift!=1||count!=1||N!=1)return -1;
 ++api_buffer_reads;out[0]=symbols[api_handles[handle]].atr;
 if(api_roll)api_server+=14400;return 1;}
bool SymbolInfoSessionQuote(const string&s,int dow,uint index,datetime &from,datetime &to){
 api_session_symbols.insert(s);if(!symbols.count(s)||index!=0)return false;from=0;to=86400;return true;}
long FileLoad(const string &path,std::vector<uchar> &out){std::ifstream f(LocalPath(path),std::ios::binary);
 if(!f)return -1;out.assign(std::istreambuf_iterator<char>(f),{});return (long)out.size();}
// Match the native destination-size contract: copied elements do not shrink it.
template<class T>int ArrayCopy(std::vector<T>&to,const std::vector<T>&from){
 if(to.size()<from.size())to.resize(from.size());
 std::copy(from.begin(),from.end(),to.begin());return (int)from.size();}
'''

MAIN = r'''
int checks=0,failed=0;
void Check(bool ok,const string&name){++checks;Print(ok?"PASS: ":"FAIL: ",name);if(!ok)++failed;}
bool Near(double a,double b){return std::abs(a-b)<1e-9;}
void Fixture(){
 JPWSignalTerminalReset();native_positions.clear();native_orders.clear();symbols.clear();symbol_list.clear();
 
 api_login=424242;api_currency="USD";api_margin=ACCOUNT_MARGIN_MODE_RETAIL_HEDGING;
 api_balance=1000;api_equity=900;api_profit=-100;api_credit=0;api_connected=true;
 api_error=0;api_property_failure=false;api_roll=false;api_horizon_failure=false;
 api_positions_reads=api_identity_reads=api_tp_mutation_at=api_tp_mutation_repeat=0;
 api_login_change_at=api_balance_change_at=0;api_clock_step=1;
 NativeSymbol n;n.base="NZD";n.profit="USD";n.time_msc=api_server*1000;symbols["NZDUSD.m"]=n;
 NativeSymbol e=n;e.base="EUR";e.bid=1.0999;e.ask=1.1001;e.atr=.002;symbols["EURUSD"]=e;
 symbol_list={"NZDUSD.m","EURUSD"};
 native_positions.push_back({1001,2001,api_server*1000-10000,api_server*1000-5000,"NZDUSD.m",0,0,1,0,.1,.1,.62,.55,.7,0});
 native_positions.push_back({1002,2002,api_server*1000-8000,api_server*1000-4000,"EURUSD",1,0,1,0,.2,.2,1.12,1.2,1.,0});
 native_orders.push_back({3001,0,api_server*1000-1000,0,"NZDUSD.m",0,ORDER_TYPE_BUY_LIMIT,ORDER_STATE_PARTIAL,0,.05,.15,.59,.55,.7,0});
 native_orders.push_back({3002,0,api_server*1000-500,0,"EURUSD",1,ORDER_TYPE_SELL_STOP,ORDER_STATE_PLACED,0,.4,.4,1.08,1.2,1.,0});
 api_tick_symbols.clear();api_atr_symbols.clear();api_session_symbols.clear();
}
string Disk(){string out="";for(auto& e:fs::recursive_directory_iterator(file_root)){if(e.is_regular_file()){
 std::ifstream f(e.path(),std::ios::binary);out+=e.path().filename().string()+":"+string(std::istreambuf_iterator<char>(f),{}); }}return out;}
int main(int argc,char**argv){if(argc!=2)return 2;file_root=fs::path(argv[1]);fs::create_directories(file_root);
 Fixture();JPWSignalCapture c;std::vector<JPWSignalRow> rows;string reason;
 Check(JPWSignalCollect(c,rows,reason)&&rows.size()==4&&rows[0].tp==.7&&rows[2].volume==.05,"full catalog includes TP and remaining pending volume");
 Check(c.reference_identifier==0&&!c.reference_closed&&!c.context.empty()&&c.context.find("424242")==string::npos,"opaque context and transient reference initialized");
 string before_digest=c.digest;std::reverse(native_positions.begin(),native_positions.end());
 Check(JPWSignalRevalidate(c,rows,reason),"enumeration order is not composition identity");
 api_equity=890;api_profit=-110;
 Check(JPWSignalRevalidate(c,rows,reason)&&c.equity==900,"equity/profit movement allowed, accepted equity frozen");
 native_positions[0].tp+=.001;Check(!JPWSignalRevalidate(c,rows,reason),"TP change rejects prepared/export snapshot");
 native_positions[0].tp-=.001;native_orders[0].vol=.04;Check(!JPWSignalRevalidate(c,rows,reason),"remaining pending volume change rejects snapshot");
 native_orders[0].vol=.05;api_balance+=1;Check(!JPWSignalRevalidate(c,rows,reason),"balance/context change rejects snapshot");

 Fixture();Check(JPWSignalCollect(c,rows,reason),"full tuple mutation fixture accepted");
 for(int field=0;field<8;field++){auto saved=native_orders[0];
  if(field==0)native_orders[0].tp+=.01;else if(field==1)native_orders[0].sl+=.01;
  else if(field==2)native_orders[0].entry+=.01;else if(field==3)native_orders[0].initial+=.01;
  else if(field==4)native_orders[0].expires=api_server+3600;else if(field==5)native_orders[0].state=ORDER_STATE_PLACED;
  else if(field==6)native_orders[0].stoplimit=.58;else native_orders[0].opened--;
  Check(!JPWSignalRevalidate(c,rows,reason),"pending fulltuple field mutation "+std::to_string(field)+" invalidates export");native_orders[0]=saved;}
 Check(JPWSignalRevalidate(c,rows,reason),"restored full tuple revalidates");
 api_property_failure=true;Check(!JPWSignalRevalidate(c,rows,reason)&&!JPWSignalAdapterDeferred(),"definitive read error is not stale typed deferment");api_property_failure=false;
 Fixture();api_tp_mutation_at=2;Check(JPWSignalCollect(c,rows,reason)&&api_positions_reads==4,"one bounded repeat converges after TP race");
 Fixture();api_tp_mutation_repeat=1;Check(!JPWSignalCollect(c,rows,reason)&&api_positions_reads==4&&rows.empty(),"persistent composition race rejected after one retry");
 Fixture();api_property_failure=true;Check(!JPWSignalCollect(c,rows,reason)&&rows.empty(),"read error rejected rather than artificial zero");
 Fixture();api_login_change_at=2;Check(JPWSignalCollect(c,rows,reason)&&c.account.login==424243&&api_positions_reads==4,"account race repeated once and accepted new stable context");
 Fixture();api_balance_change_at=2;Check(JPWSignalCollect(c,rows,reason)&&c.balance==1001,"balance race repeated with coherent new sample");
 Fixture();api_clock_step=1000;Check(!JPWSignalCollect(c,rows,reason)&&JPWSignalAdapterDeferred(),"500ms budget exposes typed deferment");
 Fixture();Check(JPWSignalCollect(c,rows,reason),"metrics fixture accepted");
 JPWSignalMetrics m;string files_before=Disk();
 Check(JPWSignalCollectMetrics(c,rows,2,m,reason)&&m.leverage_valid&&m.scenario_valid&&m.root_valid,"exact metrics adapter with real financial and RootN kernels");
 Check(Near(m.leverage,(.1*100000*.6+.2*100000*1.1)/900)&&Near(m.scenario_leverage,(.15*100000*.6+.2*100000*1.1)/900),"whole-account gross and ONLY selected remaining pending hypothetical fill");
 Check(Near(m.floating_percent,-10)&&Near(m.factor,1.5)&&m.n_1w==42&&m.n_2w==84,"floating currency units cancel, absent preference F1.5, counted 24/7 horizons");
 Check(m.root_quality==1&&m.quote_quality==1&&m.leverage_quality==1,"initial cached quote has no new-tick Current claim; projected calendar Estimated");
 double d=0,pct=0;JPWRaizNCalculate(.6,.004,42,1.5,d,pct);
 Check(Near(m.root_1w,pct)&&Near((m.bid+m.ask)/2,.6)&&m.atr==.004,"both horizons use selected exact symbol same ATR and Bid/Ask");
 Check(Disk()==files_before&&handles.empty(),"metrics and collection do not write financial files or hold locks");
 api_server++;for(auto&pair:symbols)pair.second.time_msc=api_server*1000;
 Check(JPWSignalCollectMetrics(c,rows,0,m,reason)&&Near(m.scenario_leverage,m.leverage)&&m.leverage_quality==2,"selected existing position not duplicated; new quote restores current leverage");
 Check(m.quote_quality==2&&m.root_quality==1,"new symbol tick confirmed, future weekly calendar still Estimated");
 Check(JPWSignalCollectMetrics(c,rows,1,m,reason)&&m.root_valid&&m.atr==.002&&Near((m.bid+m.ask)/2,1.1),"selected symbol differing chart owns independent ATR/price context");
 Check(api_atr_symbols.count("EURUSD")&&api_session_symbols.count("EURUSD")&&api_release_reads>0,"exact-symbol calendar/ATR and released previous handle");
 api_connected=false;Check(JPWSignalCollectMetrics(c,rows,1,m,reason)&&m.leverage_quality==1&&m.root_quality==1,"offline complete sample estimated independently");
 api_connected=true;Check(JPWSignalCollectMetrics(c,rows,1,m,reason)&&m.quote_quality==1,"reconnection requires fresh selected-symbol tick");
 api_server++;symbols["EURUSD"].time_msc=api_server*1000;symbols["NZDUSD.m"].time_msc=api_server*1000;
 Check(JPWSignalCollectMetrics(c,rows,1,m,reason)&&m.quote_quality==2,"reconnection fresh tick restores quote quality");
 symbols["EURUSD"].bars=10;g_signal_root_cache.valid=false;
 Check(JPWSignalCollectMetrics(c,rows,1,m,reason)&&!m.root_valid&&m.leverage_valid&&m.floating_valid,"insufficient ATR independent from valid account metrics");
 symbols["EURUSD"].bars=100;g_signal_root_cache.valid=false;api_roll=true;
 Check(JPWSignalCollectMetrics(c,rows,1,m,reason)&&!m.root_valid,"ATR H4 rollover race rejected");api_roll=false;
 Fixture();api_margin=ACCOUNT_MARGIN_MODE_RETAIL_NETTING;native_positions.resize(1);native_orders.resize(1);
 native_orders[0].side=1;native_orders[0].type=ORDER_TYPE_SELL_STOP;native_orders[0].vol=.04;
 Check(JPWSignalCollect(c,rows,reason)&&JPWSignalCollectMetrics(c,rows,1,m,reason)&&Near(m.scenario_leverage,.06*100000*.6/900),"netting opposite pending reduces aggregate rather than blindly adds");
 native_orders[0].vol=.1;Check(JPWSignalCollect(c,rows,reason)&&JPWSignalCollectMetrics(c,rows,1,m,reason)&&Near(m.scenario_leverage,0),"netting hypothetical flatten yields confirmed zero gross");
 native_orders[0].vol=.15;Check(JPWSignalCollect(c,rows,reason)&&JPWSignalCollectMetrics(c,rows,1,m,reason)&&Near(m.scenario_leverage,.05*100000*.6/900),"netting reversal uses remaining opposite signed volume");
 Fixture();Check(JPWSignalCollect(c,rows,reason),"reference fixture accepted");int index=-1;long identifier=0;bool closed=false;
 Check(JPWSignalReadReference(c,rows,0,0,index,identifier,closed,reason)&&identifier==0&&!closed,"absent Genesis permits only inference");
 JPWGenesisRecord record;Check(JPWGenesisCreate(c.account,0,JPW_GENESIS_FOLDER,1001,2001,"NZDUSD.m",0,native_positions[0].opened,record)==JPW_GENESIS_VALID,"synthetic Genesis record created solely by fixture setup");
 string stored=Disk();Check(JPWSignalReadReference(c,rows,0,0,index,identifier,closed,reason)&&index==0&&identifier==2001&&!closed&&Disk()==stored,"read-only existing reference stable identifier, no save");

 Check(JPWSignalReadReference(c,rows,1,0,index,identifier,closed,reason)&&identifier==0,"other-symbol reference excluded without redefining account operation");
 Check(JPWGenesisTransition(c.account,0,JPW_GENESIS_FOLDER,2001,JPW_GENESIS_CLOSED,record)==JPW_GENESIS_VALID,"fixture transitions reference to closed");
 stored=Disk();Check(JPWSignalReadReference(c,rows,0,0,index,identifier,closed,reason)&&closed&&identifier==2001&&index==-1&&Disk()==stored,"closed reference retained without promoting oldest remaining position");
 string genesis_key;JPWGenesisAccountKey(c.account,0,genesis_key);
 int genesis_lock=FileOpen(JPWGenesisBase(JPW_GENESIS_FOLDER,genesis_key)+".lock",FILE_READ|FILE_WRITE|FILE_BIN);
 Check(!JPWSignalReadReference(c,rows,0,0,index,identifier,closed,reason),"busy Genesis blocks fictitious successor inference");FileClose(genesis_lock);
 Fixture();Check(JPWSignalCollect(c,rows,reason),"factor fixture accepted");string factor_key;
 JPWRaizNFactorKey(c.account.server,c.account.login,c.account.currency,1,api_install,"NZDUSD.m",factor_key);
 JPWRaizNFactorPreference preference;JPWRaizNFactorClear(preference);preference.account_key=factor_key;
 preference.symbol="NZDUSD.m";preference.factor=1.8;preference.confirmed_at=api_server;
 Check(JPWRaizNFactorSave(JPW_RAIZN_FOLDER,factor_key,"NZDUSD.m",0,preference,reason)==JPW_RAIZN_VALID,"fixture writes explicit F1.8 via real versioned store");
 stored=Disk();Check(JPWSignalCollectMetrics(c,rows,0,m,reason)&&m.root_valid&&m.factor==1.8&&Disk()==stored,"selected-symbol F preference read-only respected");
 int factor_lock=FileOpen(JPWRaizNFactorBase(JPW_RAIZN_FOLDER,factor_key)+".lock",FILE_READ|FILE_WRITE|FILE_BIN);
 Check(JPWSignalCollectMetrics(c,rows,0,m,reason)&&!m.root_valid&&m.leverage_valid&&m.floating_valid,"busy F record produces RootN N/A without fallback, independent metrics valid");FileClose(factor_lock);
 {std::ofstream f(LocalPath(JPWRaizNFactorBase(JPW_RAIZN_FOLDER,factor_key)+".a"),std::ios::binary|std::ios::trunc);f<<"CORRUPT";}
 stored=Disk();Check(JPWSignalCollectMetrics(c,rows,0,m,reason)&&!m.root_valid&&m.factor==0&&Disk()==stored,"corrupt F refuses silent default and leaves financial bytes untouched");
 // Fresh identity avoids old preference fixtures; no account data is real.
 Fixture();api_login=515151;api_currency=" usc ";api_balance=100000;api_equity=90000;api_profit=-10000;
 for(auto &pair:symbols){pair.second.tick_profit=100;pair.second.tick_loss=100;}
 Check(JPWSignalCollect(c,rows,reason)&&c.account.currency=="USC","USC normalization is account property, not broker suffix");
 Check(JPWSignalCollectMetrics(c,rows,2,m,reason)&&!m.leverage_valid&&m.root_valid&&m.floating_valid,"unconfirmed USC contract blocks leverage only");
 std::vector<JPWProfileEntry> profile;
 for(const string&name:symbol_list){JPWInstrument ins;JPWSignalReadInstrument(name,ins);JPWProfileEntry e;
 JPWProfileHash(name,e.symbol_hash);JPWProfileSignature(ins,e.spec_hash);e.scale=1;e.verified_at=api_server;profile.push_back(e);}
 Check(JPWProfileSave(c.account,profile),"fixture verifies normal contract unit scales using real profile store");
 stored=Disk();Check(JPWSignalCollectMetrics(c,rows,2,m,reason)&&m.leverage_valid&&Near(m.leverage,(6000.+22000.)/900.)&&Near(m.floating_percent,-10)&&Disk()==stored,"USD1000 and USC100000 equity equivalent without unilateral factor100");
 Fixture();api_login=616161;api_currency="USC";api_balance=1000;api_equity=900;api_profit=-100;
 symbols["NZDUSD.m"].tick_profit=symbols["NZDUSD.m"].tick_loss=1;
 symbols["EURUSD"].contract=1000;symbols["EURUSD"].tick_profit=symbols["EURUSD"].tick_loss=1;
 Check(JPWSignalCollect(c,rows,reason),"heterogeneous USC fixture accepted");profile.clear();
 for(const string&name:symbol_list){JPWInstrument ins;JPWSignalReadInstrument(name,ins);JPWProfileEntry e;
 JPWProfileHash(name,e.symbol_hash);JPWProfileSignature(ins,e.spec_hash);e.scale=name=="NZDUSD.m"?.01:1.;e.verified_at=api_server;profile.push_back(e);}
 Check(JPWProfileSave(c.account,profile)&&JPWSignalCollectMetrics(c,rows,2,m,reason)&&m.leverage_valid&&Near(m.leverage,(60.+220.)/9.),"per-symbol scales100000cent and1000units without duplicate normalization");
 symbols["NZDUSD.m"].contract=200000;
 Check(JPWSignalCollectMetrics(c,rows,2,m,reason)&&!m.leverage_valid&&m.root_valid,"contract change invalidates USC profile without masking selected RootN");
 Fixture();api_login=717171;Check(JPWSignalCollect(c,rows,reason),"catalog deferred fixture accepted");
 for(int i=0;i<180;i++){string name="SYNTHETIC-catalog-"+std::to_string(i);NativeSymbol v=symbols["EURUSD"];v.mode=SYMBOL_CALC_MODE_CFD;symbols[name]=v;symbol_list.push_back(name);}
 bool done=JPWSignalCollectMetrics(c,rows,2,m,reason);Check(!done&&JPWSignalAdapterDeferred()&&!m.leverage_valid,"partial catalog is typed deferred, not a final subtotal or false-ready response");
 int turns=0;while(!done&&JPWSignalAdapterDeferred()&&turns++<20)done=JPWSignalCollectMetrics(c,rows,2,m,reason);
 Check(done&&m.leverage_valid&&turns>0&&turns<20&&!JPWSignalAdapterDeferred(),"lazy catalog progresses across bounded timer requests then completes");
 symbols["EURUSD"].base="GBP";
 Check(!JPWSignalCollectMetrics(c,rows,2,m,reason)&&JPWSignalAdapterDeferred(),"catalog metadata drift invalidates cached edges and requests recollection");
 Fixture();api_login=818181;Check(JPWSignalCollect(c,rows,reason),"failure independence fixture accepted");
 symbols["EURUSD"].quote_ok=false;
 Check(JPWSignalCollectMetrics(c,rows,0,m,reason)&&!m.leverage_valid&&m.root_valid&&m.floating_valid,"whole-account conversion/quote failure never reports partial leverage");
 symbols["EURUSD"].quote_ok=true;api_horizon_failure=true;
 Check(JPWSignalCollectMetrics(c,rows,0,m,reason)&&m.leverage_valid&&!m.root_valid,"incomplete H4 calendar refuses RootN independently");
 api_horizon_failure=false;api_equity=0;Check(JPWSignalCollect(c,rows,reason)&&JPWSignalCollectMetrics(c,rows,0,m,reason)&&!m.leverage_valid&&m.floating_valid&&m.root_valid,"nonpositive equity blocks leverage while balance/profit remain valid");
 Fixture();api_login=919191;api_margin=ACCOUNT_MARGIN_MODE_EXCHANGE;
 Check(JPWSignalCollect(c,rows,reason)&&JPWSignalCollectMetrics(c,rows,2,m,reason)&&m.leverage_valid&&!m.scenario_valid,"exchange pending hypothetical fill unsupported, no invented aggregate transformation");

 Fixture();api_login=929292;api_currency="CAD";
 NativeSymbol cad=symbols["EURUSD"];cad.base="USD";cad.profit="CAD";cad.bid=1.3999;cad.ask=1.4001;
 symbols["USDCAD"]=cad;symbol_list.push_back("USDCAD");
 NativeSymbol stale=cad;stale.base="NZD";stale.bid=9.9999;stale.ask=10.0001;stale.time_msc=api_server*1000-600000;
 symbols["NZDCAD.old"]=stale;symbol_list.push_back("NZDCAD.old");
 Check(JPWSignalCollect(c,rows,reason)&&JPWSignalCollectMetrics(c,rows,2,m,reason),"direct/indirect quote route fixture accepted");
 api_server++;for(auto &pair:symbols)if(pair.first!="NZDCAD.old")pair.second.time_msc=api_server*1000;
 Check(JPWSignalCollectMetrics(c,rows,2,m,reason)&&m.leverage_valid&&m.leverage_quality==2&&Near(m.leverage,28000.*1.4/900.),"fresh two-leg conversion preferred over stale direct cached route");
 Fixture();api_login=939393;api_currency="NZD";
 Check(JPWSignalCollect(c,rows,reason)&&JPWSignalCollectMetrics(c,rows,2,m,reason)&&m.leverage_valid&&Near(m.leverage,(10000.+22000./.6)/900.),"inverse conversion preserves entire-account gross denominator units");
 Fixture();api_login=949494;native_positions[0].tp=std::numeric_limits<double>::quiet_NaN();
 Check(!JPWSignalCollect(c,rows,reason)&&rows.empty(),"nonfinite TP property fails closed");
 Fixture();api_login=959595;Check(JPWSignalCollect(c,rows,reason),"age invalidation fixture accepted");
 api_mono=c.accepted_ms+30001;Check(!JPWSignalRevalidate(c,rows,reason),"expired accepted capture cannot prepare/export");
 Fixture();api_login=959596;Check(JPWSignalCollect(c,rows,reason),"expiry crossing fixture accepted");
 api_mono=c.accepted_ms+29990;
 Check(!JPWSignalRevalidate(c,rows,reason)&&api_mono>c.accepted_ms+30000&&!JPWSignalAdapterDeferred(),"capture expiring DURING revalidation rejects prepare/export definitively");
 Check(JPWSignalRevalidate(c,rows,reason,0,false),"composition-only monitor remains valid across30s boundary");

 Fixture();api_login=969696;Check(JPWSignalCollect(c,rows,reason)&&JPWSignalCollectMetrics(c,rows,2,m,reason),"renewal fixture accepted with frozen metrics");
 c.reference_closed=true;c.reference_identifier=2001;const string old_digest=c.digest;
 const double frozen_equity=c.equity,frozen_leverage=m.leverage,frozen_floating=m.floating_percent;
 const ulong old_accepted=c.accepted_ms;api_mono=old_accepted+31000;api_server+=31;
 api_equity=880;api_profit=-120;
 Check(!JPWSignalRevalidate(c,rows,reason),"default revalidate still rejects31s frozen reading");
 Check(JPWSignalRevalidate(c,rows,reason,0,false)&&c.equity==frozen_equity&&m.leverage==frozen_leverage&&m.floating_percent==frozen_floating,"composition-only monitor tolerates age without changing frozen capture/metrics");
 Check(JPWSignalRenewCapture(c,rows,reason)&&c.accepted_ms>old_accepted&&c.equity==880&&c.profit==-120&&c.digest==old_digest&&c.reference_closed&&c.reference_identifier==2001,"first-preview renewal updates BEPC/times with identical composition and preserves reference");
 Check(m.leverage==frozen_leverage&&m.floating_percent==frozen_floating&&JPWSignalRevalidate(c,rows,reason),"renewal cannot mutate existing metrics; renewed reading fresh");
 const ulong accepted_after=c.accepted_ms;const double equity_after=c.equity;
 native_positions[0].tp+=.001;api_equity=870;
 Check(!JPWSignalRenewCapture(c,rows,reason)&&c.accepted_ms==accepted_after&&c.equity==equity_after,"TP drift refuses renewal and keeps previous capture intact");
 native_positions[0].tp-=.001;api_login++;
 Check(!JPWSignalRenewCapture(c,rows,reason)&&c.accepted_ms==accepted_after&&c.equity==equity_after,"account change refuses renewal atomically");api_login--;
 api_clock_step=1000;
 Check(!JPWSignalRenewCapture(c,rows,reason)&&JPWSignalAdapterDeferred()&&c.accepted_ms==accepted_after,"renewal deadline is typed deferred without partial update");api_clock_step=1;
 Fixture();Check(JPWSignalCollect(c,rows,reason)&&rows.size()==4,"reused output starts with full catalogue");
 native_positions.pop_back();native_orders.pop_back();
 Check(JPWSignalCollect(c,rows,reason)&&rows.size()==2&&rows[0].ticket==1001&&rows[1].ticket==3001,"reused output shrinks to exact live composition");
 native_positions.clear();native_orders.clear();
 Check(JPWSignalCollect(c,rows,reason)&&rows.empty()&&!c.digest.empty(),"reused output becomes coherently empty without stale tails");
 JPWSignalTerminalReset();Check(api_handles.empty(),"deinitialization releases private ATR handles");
 Print("HOST_SIGNAL_COPY_ADAPTER: ",checks-failed," PASS / ",failed," FAIL");
 Print("MQL5_NATIVE_COMPILATION: NOT_RUN; MQL5_NATIVE_EXECUTION: NOT_RUN; NATIVE_COPY: NOT_RUN");
 return failed?1:0;}
'''


def translate(source: str) -> str:
    # Mechanical declaration splitting, not behavior substitution.
    source = re.sub(r"\b(\w+)\s+(\w+)\[\],(\w+)\[\];", r"\1 \2[]; \1 \3[];", source)
    return signal_core.translate(source)


def run(output: Path | None) -> int:
    compiler = shutil.which("clang++") or shutil.which("g++")
    if not compiler:
        print("ENVIRONMENT_ERROR: host compiler unavailable; MT5 native NOT_RUN")
        return 2
    identity = {"test": "jpw_signal_copy_adapter", "kind": "HOST_SYNTHETIC_NOT_MQL5", "compiler": compiler,
                "source_sha256": {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in FILES},
                "limitations": "Synthetic native APIs; exact collectors, stores, routes, live ATR and math bodies. No real account, native MT5, OS-lock/crash proof or clipboard."}
    print(json.dumps(identity, indent=2))
    if output:
        output.mkdir(parents=True, exist_ok=False)
        (output / "source-identity.json").write_text(json.dumps(identity, indent=2)+"\n")
    prim = re.sub(r"ulong GetTickCount64\(\)\{[^\n]+\}\n", "", base.SHIM)
    prim = re.sub(r"datetime Time(?:Local|Current)\(\)\{[^\n]+\}\n", "", prim)
    extra = signal_core.EXTRA_SHIM.split("int main(){", 1)[0]
    shim = SHIM
    main = MAIN
    receipts = []
    with tempfile.TemporaryDirectory(prefix="jpw-signal-adapter-synthetic-") as tmp:
        source,binary=Path(tmp)/"signal_adapter.cpp",Path(tmp)/"signal_adapter"
        source.write_text(prim+"\n"+extra+"\n"+shim+"\n"+
                          "\n".join(translate(p.read_text()) for p in FILES)+"\n"+main)
        if output: shutil.copy2(source,output/source.name)
        commands=[[compiler,"--version"],[compiler,"-std=c++17","-Wall","-Wextra","-Wno-unused-parameter","-Wno-deprecated-declarations",str(source),"-o",str(binary)]+([] if sys.platform=="darwin" else ["-lcrypto"]),[str(binary),str(Path(tmp)/"isolated-files")]]
        for i,command in enumerate(commands):
            result=subprocess.run(command,text=True,capture_output=True,check=False,timeout=60)
            print(result.stdout,end="");print(result.stderr,end="")
            receipts.append({"command":command,"exit_code":result.returncode})
            if output:
                (output/f"{i}-stdout.txt").write_text(result.stdout)
                (output/f"{i}-stderr.txt").write_text(result.stderr)
                (output/"commands.json").write_text(json.dumps(receipts,indent=2)+"\n")
            if result.returncode:
                print("PRODUCT_FAIL: source-linked host adapter",result.returncode)
                return result.returncode
    after={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in FILES}
    if after!=identity["source_sha256"]:
        print("PRODUCT_FAIL: source changed during validation")
        return 1
    if output: (output/"summary.json").write_text(json.dumps({**identity,"status":"PASS","source_unchanged":True,"commands":receipts},indent=2)+"\n")
    return 0

if __name__=="__main__":
    parser=argparse.ArgumentParser();parser.add_argument("--evidence-dir",type=Path)
    raise SystemExit(run(parser.parse_args().evidence_dir))
