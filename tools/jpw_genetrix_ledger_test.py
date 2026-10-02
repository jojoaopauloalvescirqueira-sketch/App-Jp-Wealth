#!/usr/bin/env python3
"""Compile actual MQL ledger Core/Store and synthetic script with a small C++
compatibility layer. SQLite operations execute against actual SQLite, not a
mocked ledger. No terminal/account/trading API is available to this harness.
Native MQL compile, Terminal reconciliation and GUI acceptance remain NOT_RUN.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import re
import subprocess
import tempfile
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "mt5/jpw-alavancagem-atual/MQL5"
CORE = BASE / "Include/JPWealth/JPW_Genetrix_Ledger_Core.mqh"
STORE = BASE / "Include/JPWealth/JPW_Genetrix_Ledger_Store.mqh"
SCRIPT = BASE / "Scripts/JPWealth/JPW_Genetrix_Ledger_Tests.mq5"
ORACLES = ROOT / "tests/fixtures/genetrix/ledger-oracles-v1.json"

SHIM = r'''
#include <algorithm>
#include <climits>
#include <cmath>
#include <cstdio>
#include <cstdlib>
#include <filesystem>
#include <iomanip>
#include <iostream>
#include <map>
#include <sstream>
#include <stdexcept>
#include <string>
#include <vector>
#include <sqlite3.h>
#ifdef __APPLE__
#include <CommonCrypto/CommonDigest.h>
#else
#include <openssl/sha.h>
#endif
using string=std::string; using uchar=unsigned char; using ushort=unsigned short;
constexpr int INVALID_HANDLE=-1, WHOLE_ARRAY=-1, CP_UTF8=65001;
constexpr int DATABASE_OPEN_READONLY=1, DATABASE_OPEN_READWRITE=2, DATABASE_OPEN_CREATE=4;
constexpr int ERR_DATABASE_NO_MORE_DATA=5126;
string host_root; int host_error=0,host_handle=1,host_asserts=0;
std::map<int,sqlite3*> host_dbs; std::map<int,sqlite3_stmt*> host_statements;
void ResetLastError(){host_error=0;} int GetLastError(){return host_error;}
template<class T> int ArraySize(const std::vector<T>& a){return (int)a.size();}
template<class T> int ArrayResize(std::vector<T>& a,int n){if(n<0)return -1;a.resize(n);return n;}
template<class T> bool ArraySort(std::vector<T>& a){std::sort(a.begin(),a.end());return true;}
double MathAbs(double v){return std::abs(v);} double MathMax(double a,double b){return std::max(a,b);}
bool MathIsValidNumber(double v){return std::isfinite(v);}
string IntegerToString(long v){return std::to_string(v);}
string DoubleToString(double v,int n){std::ostringstream s;s<<std::fixed<<std::setprecision(n)<<v;return s.str();}
int StringLen(const string& s){return (int)s.size();}
ushort StringGetCharacter(const string& s,int i){return (uchar)s.at(i);}
string StringSubstr(const string& s,int p,int n=-1){return s.substr(p,n<0 ? string::npos : (size_t)n);}
int StringFind(const string& s,const string& t,int p=0){auto n=s.find(t,p);return n==string::npos ? -1 : (int)n;}
int StringCompare(const string& a,const string& b){return a.compare(b);}
int StringSplit(const string& s,ushort sep,std::vector<string>& a){a.clear();size_t p=0,n;while((n=s.find((char)sep,p))!=string::npos){a.push_back(s.substr(p,n-p));p=n+1;}a.push_back(s.substr(p));return ArraySize(a);}
long StringToInteger(const string& s){try{return std::stol(s);}catch(...){return 0;}}
double StringToDouble(const string& s){try{return std::stod(s);}catch(...){return 0;}}
string StringFormat(const char* format,int n){char b[100];std::snprintf(b,sizeof(b),format,n);return b;}
int StringToCharArray(const string& s,std::vector<uchar>& b,int,int,int){b.assign(s.begin(),s.end());b.push_back(0);return ArraySize(b);}
string CharArrayToString(const std::vector<uchar>& b,int p,int n,int){return string(b.begin()+p,b.begin()+p+n);}
template<class... T> void Print(const T&... t){(std::cout<<...<<t)<<'\n';}
bool JPWRaizNIsHash(const string& s){return s.size()==64 && s.find_first_not_of("0123456789abcdef")==string::npos;}
bool JPWRaizNHash(const string& s,string& out){unsigned char b[32];
#ifdef __APPLE__
CC_SHA256(s.data(),(CC_LONG)s.size(),b);
#else
SHA256((const unsigned char*)s.data(),s.size(),b);
#endif
out="";for(int i=0;i<32;i++)out+=StringFormat("%02x",b[i]);return true;}
string host_path(string s){std::replace(s.begin(),s.end(),'\\','/');return host_root+"/"+s;}
bool FileIsExist(const string& s){return std::filesystem::exists(host_path(s));}
bool FolderCreate(const string& s){std::error_code e;std::filesystem::create_directories(host_path(s),e);return !e;}
int DatabaseOpen(const string& path,int flags){sqlite3* db=nullptr;int f=(flags&DATABASE_OPEN_READONLY)?SQLITE_OPEN_READONLY:SQLITE_OPEN_READWRITE;if(flags&DATABASE_OPEN_CREATE)f|=SQLITE_OPEN_CREATE;int rc=sqlite3_open_v2(host_path(path).c_str(),&db,f,nullptr);if(rc!=SQLITE_OK){if(db)sqlite3_close(db);host_error=rc;return -1;}int h=host_handle++;host_dbs[h]=db;return h;}
void DatabaseClose(int h){if(host_dbs.count(h)){sqlite3_close(host_dbs[h]);host_dbs.erase(h);}}
int DatabasePrepare(int h,const string& sql){sqlite3_stmt* q=nullptr;int rc=sqlite3_prepare_v2(host_dbs.at(h),sql.c_str(),-1,&q,nullptr);if(rc!=SQLITE_OK){host_error=rc;return -1;}int n=host_handle++;host_statements[n]=q;return n;}
bool DatabaseBind(int q,int i,long x){return sqlite3_bind_int64(host_statements.at(q),i+1,x)==SQLITE_OK;}
bool DatabaseBind(int q,int i,int x){return DatabaseBind(q,i,(long)x);}
bool DatabaseBind(int q,int i,double x){return sqlite3_bind_double(host_statements.at(q),i+1,x)==SQLITE_OK;}
bool DatabaseBind(int q,int i,const string& x){return sqlite3_bind_text(host_statements.at(q),i+1,x.c_str(),(int)x.size(),SQLITE_TRANSIENT)==SQLITE_OK;}
bool DatabaseRead(int q){int rc=sqlite3_step(host_statements.at(q));host_error=rc==SQLITE_DONE?ERR_DATABASE_NO_MORE_DATA:(rc==SQLITE_ROW?0:rc);return rc==SQLITE_ROW;}
void DatabaseFinalize(int q){if(host_statements.count(q)){sqlite3_finalize(host_statements[q]);host_statements.erase(q);}}
bool DatabaseColumnLong(int q,int i,long& n){if(sqlite3_column_type(host_statements.at(q),i)!=SQLITE_INTEGER)return false;n=(long)sqlite3_column_int64(host_statements.at(q),i);return true;}
bool DatabaseColumnInteger(int q,int i,int& n){long v=0;if(!DatabaseColumnLong(q,i,v))return false;n=(int)v;return true;}
bool DatabaseColumnText(int q,int i,string& s){if(sqlite3_column_type(host_statements.at(q),i)!=SQLITE_TEXT)return false;s=(const char*)sqlite3_column_text(host_statements.at(q),i);return true;}
bool DatabaseExecute(int h,const string& sql){int rc=sqlite3_exec(host_dbs.at(h),sql.c_str(),nullptr,nullptr,nullptr);host_error=rc==SQLITE_OK?0:rc;return rc==SQLITE_OK;}
bool DatabaseTransactionBegin(int h){return DatabaseExecute(h,"BEGIN");}
bool DatabaseTransactionCommit(int h){return DatabaseExecute(h,"COMMIT");}
bool DatabaseTransactionRollback(int h){return DatabaseExecute(h,"ROLLBACK");}
void REQUIRE(bool ok,const string& label){host_asserts++;if(!ok)throw std::runtime_error(label);}
long scalar(int db,const string& sql){int q=DatabasePrepare(db,sql);long n=-1;REQUIRE(q!=-1 && DatabaseRead(q) && DatabaseColumnLong(q,0,n),"scalar "+sql);DatabaseFinalize(q);return n;}
'''

ADAPTER_SHIM = r'''
using ulong=unsigned long;
struct MqlTick {long time_msc;};
enum {POSITION_IDENTIFIER=1,POSITION_TIME_MSC,POSITION_TYPE,POSITION_SYMBOL,POSITION_VOLUME,POSITION_PROFIT,POSITION_SWAP,POSITION_TYPE_BUY=20,POSITION_TYPE_SELL=21};
enum {ACCOUNT_MARGIN_MODE=1,ACCOUNT_BALANCE=2,ACCOUNT_MARGIN_MODE_RETAIL_HEDGING=2,TERMINAL_CONNECTED=3};
int host_position_count_calls=0,host_order_count_calls=0,host_count_race=0;
string host_identity_a,host_identity_b;bool host_switched=false,host_switch_in_live=false;
ulong GetTickCount64(){return 100;}
long AccountInfoInteger(int){return ACCOUNT_MARGIN_MODE_RETAIL_HEDGING;}
long TerminalInfoInteger(int){return 1;}
bool GlobalVariableGet(const string&,double& v){v=100;return true;}
bool JPWLedgerIdentity(string& k,string& c){k=host_switched?host_identity_b:host_identity_a;c="USD";return true;}
bool JPWLedgerAccountDouble(int,double& v){v=997.8;return true;}
long TimeTradeServer(){return 1000;}
int PositionsTotal(){host_position_count_calls++;return host_count_race==1&&host_position_count_calls>1?2:1;}
int OrdersTotal(){host_order_count_calls++;return host_count_race==2&&host_order_count_calls>1?1:0;}
ulong PositionGetTicket(int i){return i==0?700:0;}
bool PositionSelectByTicket(ulong t){if(host_switch_in_live)host_switched=true;return t==700;}
bool PositionGetInteger(int prop,long& v){if(prop==POSITION_IDENTIFIER)v=700;else if(prop==POSITION_TIME_MSC)v=1000;else if(prop==POSITION_TYPE)v=POSITION_TYPE_BUY;else return false;return true;}
bool PositionGetString(int prop,string& v){if(prop!=POSITION_SYMBOL)return false;v="TEST";return true;}
bool PositionGetDouble(int prop,double& v){if(prop==POSITION_VOLUME)v=.1;else if(prop==POSITION_PROFIT)v=50;else if(prop==POSITION_SWAP)v=-.5;else return false;return true;}
bool SymbolInfoTick(const string&,MqlTick& t){t.time_msc=1000900;return true;}
ulong OrderGetTicket(int){return 0;}
bool OrderSelect(ulong){return false;}
bool JPWLedgerReadOrder(ulong,bool,JPWLedgerOrder&,bool&){return false;}
'''

HOST_TESTS = r'''
void host_checks(){
REQUIRE(JPWLedgerTickFresh(1000000,1000900),"fractional milliseconds in current server second fresh");
REQUIRE(JPWLedgerTickFresh(1000000,970000),"30 second age inclusive fresh");
REQUIRE(!JPWLedgerTickFresh(1000000,969999),"age above 30 seconds unavailable");
REQUIRE(JPWLedgerTickFresh(1000000,1002000),"two second future skew inclusive fresh");
REQUIRE(!JPWLedgerTickFresh(1000000,1002001),"future beyond two seconds unavailable");
REQUIRE(!JPWLedgerTickFresh(0,1000)&&!JPWLedgerTickFresh(1000,0)&&!JPWLedgerTickFresh(-1,1)&&!JPWLedgerTickFresh(1,-1),"invalid clock/tick unavailable");
std::vector<JPWLedgerPosition>adapter_positions;std::vector<JPWLedgerOrder>adapter_orders;bool adapter_fresh=false;string adapter_reason;
for(int race=0;race<3;race++){
host_position_count_calls=0;host_order_count_calls=0;host_count_race=race;
bool ok=JPWLedgerReadLive(adapter_positions,adapter_orders,adapter_fresh,adapter_reason);
if(race==0)REQUIRE(ok&&adapter_fresh&&adapter_positions.size()==1,"actual ReadLive fractional tick current");
else REQUIRE(!ok&&!adapter_fresh&&adapter_positions.empty(),race==1?"actual ReadLive new position race blocks prefix":"actual ReadLive new order race blocks prefix");}
std::vector<JPWLedgerDeal>d;std::vector<JPWLedgerOrder>o;std::vector<JPWLedgerPosition>p;
std::vector<JPWLedgerCycle>c;JPWLedgerView v;string why;
JPWLedgerTestFixture(1,d,o,p,v);REQUIRE(JPWLedgerBuild(d,o,p,v,c,why),"base build");
REQUIRE(c[0].members_available&&c[0].member_identifiers=="700","partial position includes original identifier");
auto saved=c[0];std::reverse(d.begin(),d.end());REQUIRE(JPWLedgerBuild(d,o,p,v,c,why)&&c[0].cycle_id==saved.cycle_id&&JPWLedgerNear(c[0].compensated,saved.compensated),"chronological replay");
REQUIRE(c[0].members_available&&c[0].member_identifiers==saved.member_identifiers,"member replay stable");
d.push_back(d[0]);REQUIRE(!JPWLedgerBuild(d,o,p,v,c,why),"duplicate deal rejected");
JPWLedgerTestFixture(1,d,o,p,v);v.margin_mode=0;REQUIRE(!JPWLedgerBuild(d,o,p,v,c,why),"netting N/A");
JPWLedgerTestFixture(1,d,o,p,v);v.balance=0;REQUIRE(JPWLedgerBuild(d,o,p,v,c,why)&&c[0].amount_valid&&!c[0].percent_valid,"zero balance percent N/A");
v.balance=-1;REQUIRE(JPWLedgerBuild(d,o,p,v,c,why)&&!c[0].percent_valid,"negative balance percent N/A");
JPWLedgerTestFixture(6,d,o,p,v);d[0].commission=0;d[0].fee=0;REQUIRE(JPWLedgerBuild(d,o,p,v,c,why)&&c[0].amount_valid&&c[0].compensated==0,"confirmed zero valid");
d.clear();REQUIRE(!JPWLedgerBuild(d,o,p,v,c,why),"missing origin not zero");
JPWLedgerTestFixture(2,d,o,p,v);REQUIRE(JPWLedgerBuild(d,o,p,v,c,why)&&c.size()==1&&c[0].genesis_identifier==700&&c[0].genesis_deal==100,"closed genesis no promotion");
REQUIRE(c[0].member_identifiers=="700,800"&&c[0].members_available,"closed Genesis retained in all-member projection");
JPWLedgerTestFixture(3,d,o,p,v);REQUIRE(JPWLedgerBuild(d,o,p,v,c,why)&&c.size()==1&&c[0].open_positions==2&&c[0].genesis_identifier==700,"new defense same cycle");
REQUIRE(c[0].member_identifiers=="700,800,900","all three members including closed Genesis");
JPWLedgerTestFixture(9,d,o,p,v);REQUIRE(JPWLedgerBuild(d,o,p,v,c,why)&&c[0].member_identifiers=="700"&&c[0].genesis_identifier==700,"rollover ticket change never substitutes membership identifier");
JPWLedgerCycle decoded_members;string encoded_members=JPWLedgerEncodeCycle(c[0]);
REQUIRE(JPWLedgerDecodeCycle(encoded_members,decoded_members)&&decoded_members.members_available&&decoded_members.member_identifiers=="700","v2 cycle codec membership roundtrip");
string legacy_members=JPWLedgerEncodeCycleV1(c[0]);
REQUIRE(JPWLedgerDecodeCycle(legacy_members,decoded_members)&&!decoded_members.members_available&&decoded_members.member_identifiers.empty()&&JPWLedgerNear(decoded_members.compensated,c[0].compensated),"v1 codec absent list unavailable not proven empty");
REQUIRE(JPWLedgerDecodeCycle(JPWLedgerEncodeCycle(decoded_members),decoded_members)&&!decoded_members.members_available,"legacy reencoding cannot invent availability");
auto empty_members=c[0];empty_members.members_available=true;empty_members.member_identifiers="";
empty_members.genesis_inferred=false;empty_members.genesis_ambiguous=false;empty_members.genesis_identifier=0;empty_members.genesis_deal=0;
REQUIRE(JPWLedgerMemberListStructureValid(empty_members)&&!JPWLedgerMemberListValid(empty_members),"prefinal structure cannot validate empty final open projection");
REQUIRE(!JPWLedgerDecodeCycle(JPWLedgerEncodeCycle(empty_members),decoded_members),"v2 open position with available empty members rejected");
empty_members.state=4;empty_members.open_positions=0;empty_members.amount_valid=false;empty_members.percent_valid=false;
REQUIRE(JPWLedgerMemberListValid(empty_members)&&JPWLedgerDecodeCycle(JPWLedgerEncodeCycle(empty_members),decoded_members)&&decoded_members.members_available&&decoded_members.member_identifiers.empty(),"v2 pre-execution provisional empty observed list accepted");
empty_members.state=2;REQUIRE(!JPWLedgerDecodeCycle(JPWLedgerEncodeCycle(empty_members),decoded_members),"v2 nonprovisional pending empty members rejected");
empty_members.state=3;REQUIRE(!JPWLedgerDecodeCycle(JPWLedgerEncodeCycle(empty_members),decoded_members),"v2 closed cycle empty members rejected");
empty_members.state=4;empty_members.amount_valid=true;REQUIRE(!JPWLedgerDecodeCycle(JPWLedgerEncodeCycle(empty_members),decoded_members),"v2 empty members cannot certify amount");
empty_members.amount_valid=false;empty_members.percent_valid=true;REQUIRE(!JPWLedgerDecodeCycle(JPWLedgerEncodeCycle(empty_members),decoded_members),"v2 empty members cannot certify percent");
empty_members.percent_valid=false;empty_members.open_positions=1;REQUIRE(!JPWLedgerDecodeCycle(JPWLedgerEncodeCycle(empty_members),decoded_members),"v2 provisional empty members cannot hide live position");
empty_members.open_positions=0;empty_members.genesis_identifier=700;REQUIRE(!JPWLedgerDecodeCycle(JPWLedgerEncodeCycle(empty_members),decoded_members),"v2 empty members cannot omit positive Genesis identifier");
empty_members.genesis_identifier=0;empty_members.genesis_deal=100;REQUIRE(!JPWLedgerDecodeCycle(JPWLedgerEncodeCycle(empty_members),decoded_members),"v2 empty members cannot omit Genesis execution");
empty_members.genesis_deal=0;empty_members.genesis_ambiguous=true;REQUIRE(!JPWLedgerDecodeCycle(JPWLedgerEncodeCycle(empty_members),decoded_members),"v2 empty members cannot hide ambiguous executed Genesis");
auto invalid_member=c[0];invalid_member.member_identifiers="700,700";REQUIRE(!JPWLedgerMemberListValid(invalid_member),"duplicate members rejected");
invalid_member.member_identifiers="800,700";REQUIRE(!JPWLedgerMemberListValid(invalid_member),"nonascending member list rejected");
invalid_member.member_identifiers="00700";REQUIRE(!JPWLedgerMemberListValid(invalid_member),"noncanonical identifier rejected");
invalid_member.member_identifiers="700,";REQUIRE(!JPWLedgerMemberListValid(invalid_member),"trailing member delimiter rejected");
invalid_member.member_identifiers="800";REQUIRE(!JPWLedgerMemberListValid(invalid_member),"missing original Genesis membership rejected");
auto cross_cycle=c;cross_cycle.push_back(c[0]);cross_cycle[1].cycle_id="other-cycle";REQUIRE(!JPWLedgerMembershipProjectionValid(cross_cycle),"identifier cannot belong to two cycles in one account projection");
cross_cycle[1].member_identifiers="800";cross_cycle[1].genesis_identifier=800;cross_cycle[1].cycle_id=c[0].cycle_id;REQUIRE(!JPWLedgerMembershipProjectionValid(cross_cycle),"duplicate cycle projection rejected");
JPWLedgerTestFixture(5,d,o,p,v);REQUIRE(JPWLedgerBuild(d,o,p,v,c,why)&&c.size()==1&&c[0].genesis_identifier==700&&c[0].state==1,"pending transition continuous");
o[0].volume=.03;REQUIRE(JPWLedgerBuild(d,o,p,v,c,why)&&!c[0].amount_valid,"missing partial fill not complete");
d.clear();p.clear();JPWLedgerTestView(v,1000);JPWLedgerTestOrder(o);REQUIRE(JPWLedgerBuild(d,o,p,v,c,why)&&c.size()==1&&c[0].state==4&&!c[0].amount_valid&&!c[0].genesis_inferred,"pending metadata before genesis");
o[0].state=2;o[0].done_msc=3000;REQUIRE(JPWLedgerBuild(d,o,p,v,c,why)&&c[0].state==4&&!c[0].amount_valid,"canceled provisional not financial zero");
JPWLedgerTestFixture(13,d,o,p,v);JPWLedgerTestDeal(d,104,0,700,4000,0,0,0,-3,0,0,0,2);REQUIRE(JPWLedgerBuild(d,o,p,v,c,why)&&c.size()==1&&c[0].state==3&&JPWLedgerNear(c[0].compensated,42.1),"late cost original closed cycle");
JPWLedgerTestFixture(13,d,o,p,v);JPWLedgerTestDeal(d,105,900,900,5000,1,0,.01,0,0,0,0);JPWLedgerTestLive(p,900,.01,2,0);REQUIRE(JPWLedgerBuild(d,o,p,v,c,why)&&c.size()==2&&c[1].genesis_identifier==900,"new cycle after reconciled flat");
JPWLedgerTestFixture(1,d,o,p,v);d[0].deleted=1;bool tombstone_ok=JPWLedgerBuild(d,o,p,v,c,why);REQUIRE(!tombstone_ok || (!c.empty()&&!c[0].amount_valid),"explicit opening tombstone cannot fabricate complete");
JPWLedgerTestFixture(1,d,o,p,v);v.history_complete=false;v.costs_complete=false;REQUIRE(JPWLedgerBuild(d,o,p,v,c,why)&&!c[0].amount_valid&&c[0].partial,"query without coverage N/A");
REQUIRE(c[0].members_available&&c[0].member_identifiers=="700"&&!c[0].history_complete,"observed member availability never certifies complete historical coverage");
// Regression witnesses for the three author-review genealogy/cost findings.
d.clear();p.clear();JPWLedgerTestView(v,1000);JPWLedgerTestOrder(o,3);
JPWLedgerTestDeal(d,300,300,300,5000,1,0,.02,0,0,0,0);JPWLedgerTestLive(p,300,.02,0,0);
REQUIRE(JPWLedgerBuild(d,o,p,v,c,why)&&c.size()==1&&!c[0].amount_valid,"missing pending execution cannot authorize new complete cycle");
for(int ordering=0;ordering<2;ordering++){
d.clear();o.clear();p.clear();JPWLedgerTestView(v,1000);JPWLedgerTestDeal(d,100,700,700,1000,1,0,.1,0,0,0,0);
JPWLedgerTestDeal(d,ordering==0?101:102,701,700,2000,-1,1,.1,10,0,0,0);
JPWLedgerTestDeal(d,ordering==0?102:101,800,800,2000,1,0,.1,0,0,0,0);JPWLedgerTestLive(p,800,.1,2,0);
REQUIRE(JPWLedgerBuild(d,o,p,v,c,why)&&c.size()==1&&c[0].genesis_ambiguous&&!c[0].amount_valid,"same-millisecond boundary ambiguity both ticket orders");}
JPWLedgerTestFixture(14,d,o,p,v);d[2].adjustment_of=0;d[2].time_msc=1500;
REQUIRE(JPWLedgerBuild(d,o,p,v,c,why)&&c[0].partial&&!c[0].costs_complete,"unrelated adjustment cannot resolve cancellation");
JPWLedgerTestView(v,1000);v.account_key="account-A";
REQUIRE(!JPWLedgerApplyDeclaredCoverage(v,false,false,"","account-A")&&!v.history_complete&&!v.costs_complete,"coverage defaults fail closed");
REQUIRE(!JPWLedgerApplyDeclaredCoverage(v,true,true,"   ","account-A")&&!v.history_complete,"declaration without reference rejected");
REQUIRE(!JPWLedgerApplyDeclaredCoverage(v,true,true,"file:synthetic-evidence","account-B"),"coverage bound account");
REQUIRE(JPWLedgerApplyDeclaredCoverage(v,true,true,"file:synthetic-evidence","account-A")&&v.history_complete&&v.costs_complete&&StringFind(v.reason,"DECLARADA")>=0,"coverage declared not verified");
JPWLedgerTestFixture(1,d,o,p,v);v.account_key="account-A";JPWLedgerApplyDeclaredCoverage(v,true,true,"file:synthetic-evidence","account-A");p[0].volume=.07;REQUIRE(JPWLedgerBuild(d,o,p,v,c,why)&&!c[0].amount_valid,"conflict overrides declaration");
// Actual production Store and SQLite: identities here are synthetic digests.
string key,token,composition;JPWRaizNHash("synthetic-account-A",key);JPWRaizNHash("synthetic-publisher",token);JPWRaizNHash("synthetic-composition",composition);
int db=-1;REQUIRE(JPWLedgerOpen(key,true,db,why),"new store");std::vector<long>deletes;
auto capture=[&](int n){JPWLedgerTestFixture(n,d,o,p,v);v.account_key=key;v.publisher_token=token;return JPWLedgerCommitCollection(db,d,o,p,deletes,false,v,composition,why);};
REQUIRE(capture(1),"atomic capture");REQUIRE(scalar(db,"SELECT COUNT(*) FROM ledger_deal_revisions")==2,"first raw revisions");
REQUIRE(capture(1),"identical replay");REQUIRE(scalar(db,"SELECT COUNT(*) FROM ledger_deal_revisions")==2,"replay no double booking/revision");
JPWLedgerView read;string observed;REQUIRE(JPWLedgerReadProjection(db,key,read,c,observed,why)&&JPWLedgerNear(c[0].compensated,46.42),"generation readback");long gen=read.generation;
REQUIRE(c[0].members_available&&c[0].member_identifiers=="700","stored generation exposes reconciled members");
string legacy_payload=JPWLedgerEncodeCycleV1(c[0]),legacy_digest;JPWRaizNHash(legacy_payload,legacy_digest);
int legacy_query=DatabasePrepare(db,"UPDATE ledger_projection SET payload=?1,digest=?2 WHERE generation=?3");
REQUIRE(legacy_query!=-1&&DatabaseBind(legacy_query,0,legacy_payload)&&DatabaseBind(legacy_query,1,legacy_digest)&&DatabaseBind(legacy_query,2,gen),"legacy projection fixture bound write");DatabaseRead(legacy_query);DatabaseFinalize(legacy_query);
REQUIRE(JPWLedgerReadProjection(db,key,read,c,observed,why)&&!c[0].members_available&&c[0].member_identifiers.empty(),"real SQLite v1 cache reads members unavailable");
REQUIRE(capture(1)&&JPWLedgerReadProjection(db,key,read,c,observed,why)&&c[0].members_available&&c[0].member_identifiers=="700","raw replay upgrades member projection without monetary mutation");gen=read.generation;
string wrong_account;JPWRaizNHash("foreign-account",wrong_account);REQUIRE(!JPWLedgerReadProjection(db,wrong_account,read,c,observed,why)&&c.empty()&&read.quality==0,"membership cannot be read under another account key");
DatabaseClose(db);REQUIRE(JPWLedgerOpen(key,true,db,why),"recovery fresh handle");REQUIRE(JPWLedgerReadProjection(db,key,read,c,observed,why)&&read.generation==gen&&JPWLedgerNear(c[0].compensated,46.42),"recovery same money");
REQUIRE(capture(12),"DEAL_UPDATE revised");REQUIRE(scalar(db,"SELECT COUNT(*) FROM ledger_deal_revisions")==3,"update once");REQUIRE(capture(12)&&scalar(db,"SELECT COUNT(*) FROM ledger_deal_revisions")==3,"update replay no duplicate");
REQUIRE(JPWLedgerReadProjection(db,key,read,c,observed,why)&&JPWLedgerNear(c[0].compensated,46.02),"revised money");
gen=read.generation;d.push_back(d[0]);REQUIRE(!JPWLedgerCommitCollection(db,d,o,p,deletes,false,v,composition,why)&&scalar(db,"SELECT generation FROM ledger_meta")==gen,"conflicting input duplicate cannot collapse through upsert");d.pop_back();
REQUIRE(DatabaseTransactionBegin(db),"begin rollback");d[0].commission=-999;REQUIRE(JPWLedgerUpsert(db,"ledger_deals",d[0].ticket,JPWLedgerEncodeDeal(d[0]),100,why),"staged raw mutation");REQUIRE(DatabaseTransactionRollback(db),"rollback");std::vector<JPWLedgerDeal>raw;std::vector<JPWLedgerOrder>orders;REQUIRE(JPWLedgerLoadRaw(db,raw,orders,why)&&JPWLedgerNear(raw[0].commission,-2.4)&&scalar(db,"SELECT COUNT(*) FROM ledger_deal_revisions")==3,"rollback preserves raw audit");
JPWLedgerTestFixture(12,d,o,p,v);d.resize(1);v.account_key=key;v.publisher_token=token;REQUIRE(JPWLedgerCommitCollection(db,d,o,p,deletes,false,v,composition,why),"partial selection retained");REQUIRE(JPWLedgerLoadRaw(db,raw,orders,why)&&raw.size()==2&&!raw[1].deleted,"absence not tombstone");REQUIRE(JPWLedgerReadProjection(db,key,read,c,observed,why)&&!c[0].amount_valid,"incomplete selection not complete");
deletes={101};REQUIRE(JPWLedgerCommitCollection(db,d,o,p,deletes,false,v,composition,why),"witnessed delete persisted");REQUIRE(JPWLedgerLoadRaw(db,raw,orders,why)&&raw[1].deleted,"delete explicit tombstone");long revisions=scalar(db,"SELECT COUNT(*) FROM ledger_deal_revisions");REQUIRE(JPWLedgerCommitCollection(db,d,o,p,deletes,false,v,composition,why)&&scalar(db,"SELECT COUNT(*) FROM ledger_deal_revisions")==revisions,"delete replay once");
deletes.clear();REQUIRE(capture(12),"latest source restoration revises tombstone");REQUIRE(JPWLedgerReadProjection(db,key,read,c,observed,why)&&c[0].amount_valid,"restored source complete synthetic");
deletes={9999};REQUIRE(capture(12),"unknown delete origin fault");DatabaseClose(db);REQUIRE(JPWLedgerOpen(key,true,db,why),"unknown fault reopen");REQUIRE(scalar(db,"SELECT COUNT(*) FROM ledger_faults")==1,"unknown delete fault survives restart");deletes.clear();REQUIRE(capture(12)&&JPWLedgerReadProjection(db,key,read,c,observed,why)&&!c[0].amount_valid,"fault not silent reset");
JPWLedgerTestFixture(12,d,o,p,v);JPWLedgerTestDeal(d,9999,0,0,5000,0,0,0,0,0,0,0,3);v.account_key=key;v.publisher_token=token;REQUIRE(JPWLedgerCommitCollection(db,d,o,p,deletes,false,v,composition,why)&&scalar(db,"SELECT COUNT(*) FROM ledger_faults")==0,"source witnessed revision clears origin fault");
// SQL strings remain bound even when a symbol contains apostrophes/pipes.
JPWLedgerDeal hostile=d[0];hostile.ticket=500;hostile.symbol="Q'|'; DROP TABLE ledger_meta; --";string encoded=JPWLedgerEncodeDeal(hostile);JPWLedgerDeal decoded;REQUIRE(JPWLedgerDecodeDeal(encoded,decoded)&&decoded.symbol==hostile.symbol,"strict text roundtrip");REQUIRE(DatabaseTransactionBegin(db)&&JPWLedgerUpsert(db,"ledger_deals",500,encoded,100,why)&&DatabaseTransactionRollback(db),"bound SQL hostile text");REQUIRE(scalar(db,"SELECT COUNT(*) FROM ledger_meta")==1,"SQL schema preserved");
gen=scalar(db,"SELECT generation FROM ledger_meta");REQUIRE(DatabaseExecute(db,"UPDATE ledger_deals SET digest='broken' WHERE ticket=100"),"inject raw corruption");REQUIRE(!JPWLedgerCommitCollection(db,d,o,p,deletes,false,v,composition,why)&&scalar(db,"SELECT generation FROM ledger_meta")==gen,"corruption cannot be overwritten/reset");
DatabaseClose(db);REQUIRE(JPWLedgerOpen(key,false,db,why),"reader metadata available");REQUIRE(DatabaseExecute(db,"SELECT 1"),"readonly reader available");REQUIRE(!DatabaseExecute(db,"DELETE FROM ledger_deals"),"reader cannot mutate");DatabaseClose(db);
string keyB;JPWRaizNHash("synthetic-account-B",keyB);REQUIRE(JPWLedgerOpen(keyB,true,db,why),"separate account store");REQUIRE(scalar(db,"SELECT COUNT(*) FROM ledger_deals")==0,"same identifiers cannot cross account");REQUIRE(DatabaseExecute(db,"UPDATE ledger_meta SET schema_version=999"),"inject incompatible schema");DatabaseClose(db);REQUIRE(!JPWLedgerOpen(keyB,true,db,why),"incompatible schema no migration/reset");
// Cache projection corruption is independently rejected by a reader.
string keyC;JPWRaizNHash("synthetic-account-C",keyC);key=keyC;REQUIRE(JPWLedgerOpen(key,true,db,why)&&capture(1),"projection fixture");REQUIRE(DatabaseExecute(db,"UPDATE ledger_projection SET digest='broken'"),"inject projection corruption");REQUIRE(!JPWLedgerReadProjection(db,key,read,c,observed,why)&&c.empty()&&read.quality==0,"corrupt projection gives empty N/A");DatabaseClose(db);
string keyD;JPWRaizNHash("synthetic-account-recovery",keyD);key=keyD;REQUIRE(JPWLedgerOpen(key,true,db,why)&&capture(1),"cross-process recovery seed");DatabaseClose(db);
string keyE;JPWRaizNHash("synthetic-account-audit-loss",keyE);key=keyE;REQUIRE(JPWLedgerOpen(key,true,db,why)&&capture(1),"audit loss fixture");REQUIRE(DatabaseExecute(db,"DELETE FROM ledger_deals WHERE ticket=101"),"inject missing latest raw row");REQUIRE(!JPWLedgerLoadRaw(db,raw,orders,why),"audit witness refuses lost latest raw set");DatabaseClose(db);
// Execute the REAL Bridge body against actual SQLite and controlled native API
// seams, including an account switch after its initial identity guards.
JPWRaizNHash("synthetic-account-bridge-A",host_identity_a);JPWRaizNHash("synthetic-account-bridge-B",host_identity_b);key=host_identity_a;
JPWLedgerTestFixture(0,d,o,p,v);v.account_key=key;v.publisher_token=token;
REQUIRE(JPWLedgerComposition(p,o,key,v.balance,2,composition)&&JPWLedgerOpen(key,true,db,why)&&JPWLedgerCommitCollection(db,d,o,p,deletes,false,v,composition,why),"real Bridge SQLite fixture");DatabaseClose(db);
host_count_race=0;host_position_count_calls=0;host_order_count_calls=0;host_switched=false;host_switch_in_live=false;
REQUIRE(JPWLedgerBridgeRefresh(c,read,why)&&read.quality==1&&c.size()==1,"real Bridge current controlled observation");
host_position_count_calls=0;host_order_count_calls=0;host_switch_in_live=true;
REQUIRE(!JPWLedgerBridgeRefresh(c,read,why)&&c.empty()&&read.quality==0,"real Bridge account switch during Live returns empty N/A");host_switch_in_live=false;
Print("HOST_ASSERTIONS|",host_asserts);
}
void host_restart(const bool crash){
string key,token,composition,why;JPWRaizNHash("synthetic-account-recovery",key);JPWRaizNHash("synthetic-publisher",token);JPWRaizNHash("synthetic-composition",composition);
int db=-1;REQUIRE(JPWLedgerOpen(key,true,db,why),"restart store open");std::vector<JPWLedgerDeal>d;std::vector<JPWLedgerOrder>o;std::vector<JPWLedgerPosition>p;std::vector<JPWLedgerCycle>c;JPWLedgerView v;std::vector<long>deletes;
JPWLedgerTestFixture(1,d,o,p,v);v.account_key=key;v.publisher_token=token;
if(crash){REQUIRE(DatabaseTransactionBegin(db),"crash staged transaction");d[0].commission=-999;REQUIRE(JPWLedgerUpsert(db,"ledger_deals",100,JPWLedgerEncodeDeal(d[0]),100,why),"crash staged raw");REQUIRE(JPWLedgerBuild(d,o,p,v,c,why)&&JPWLedgerWriteProjection(db,v,c,composition,why),"crash staged generation");std::_Exit(99);}
REQUIRE(JPWLedgerReadProjection(db,key,v,c,composition,why)&&v.generation==1&&JPWLedgerNear(c[0].compensated,46.42),"fresh process rollback preserves prior generation");
REQUIRE(JPWLedgerLoadRaw(db,d,o,why)&&JPWLedgerNear(d[0].commission,-2)&&scalar(db,"SELECT COUNT(*) FROM ledger_deal_revisions")==2,"fresh process rollback preserves audit and raw");
JPWLedgerTestFixture(1,d,o,p,v);v.account_key=key;v.publisher_token=token;REQUIRE(JPWLedgerCommitCollection(db,d,o,p,deletes,false,v,composition,why)&&scalar(db,"SELECT COUNT(*) FROM ledger_deal_revisions")==2,"fresh process replay idempotent");DatabaseClose(db);Print("FRESH_PROCESS_RECOVERY|PASS|",host_asserts);
}
int main(int argc,char** argv){if(argc<2||argc>3)return 2;host_root=argv[1];try{if(argc==3){host_restart(string(argv[2])=="crash");return 0;}OnStart();REQUIRE(JPWLedgerTestFailures==0,"MQL synthetic fixture build failures");host_checks();return 0;}catch(const std::exception& e){std::cerr<<"HOST_FAIL "<<e.what()<<'\n';return 1;}}
'''

def translate(source: str) -> str:
    # Syntax-only bridge. All production function bodies and accounting logic
    # remain unchanged; arrays use vectors and native builtins use host shims.
    source = re.sub(r'^\s*#(?:include|property).*$', '', source, flags=re.M)
    source = re.sub(r'\b(\w+)\s+&(\w+)\[\]', r'std::vector<\1> &\2', source)
    source = re.sub(r'\b(\w+)\s+(\w+)\[\]\s*;', r'std::vector<\1> \2;', source)
    source = source.replace('"SELECT ticket,payload,digest FROM "+', 'string("SELECT ticket,payload,digest FROM ")+')
    source = source.replace('JPW_LEDGER_FOLDER+"ledger_"', 'string(JPW_LEDGER_FOLDER)+"ledger_"')
    return source

def extract_function(source: str, name: str) -> str:
    start = source.index('bool ' + name + '(')
    opening = source.index('{', start)
    depth = 1
    i = opening + 1
    while depth:
        depth += (source[i] == '{') - (source[i] == '}')
        i += 1
    return source[start:i]

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--receipt', type=Path)
    args = parser.parse_args()
    oracle = json.loads(ORACLES.read_text())
    source_paths = [CORE, STORE, SCRIPT, ORACLES, ORACLES.with_name('risk-oracles-v1.json'), BASE / 'Include/JPWealth/JPW_Genetrix_Ledger_Terminal.mqh', BASE / 'Include/JPWealth/JPW_Genetrix_Ledger_Bridge.mqh', BASE / 'Experts/JPWealth/JPW_Genetrix_Accountant.mq5', Path(__file__).resolve()]
    hashes = {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in source_paths}
    with tempfile.TemporaryDirectory(prefix='jpw-ledger-host-') as temp:
        temp = Path(temp)
        cpp = temp / 'ledger.cpp'
        terminal_source = (BASE / 'Include/JPWealth/JPW_Genetrix_Ledger_Terminal.mqh').read_text()
        actual_live = extract_function(terminal_source, 'JPWLedgerReadLive')
        actual_composition = extract_function(terminal_source, 'JPWLedgerComposition')
        actual_bridge = (BASE / 'Include/JPWealth/JPW_Genetrix_Ledger_Bridge.mqh').read_text()
        cpp.write_text(SHIM + '\n' + translate(CORE.read_text()) + '\n' + translate(STORE.read_text()) + '\n' + ADAPTER_SHIM + '\n' + translate(actual_live) + '\n' + translate(actual_composition) + '\n' + translate(actual_bridge) + '\n' + translate(SCRIPT.read_text()) + '\n' + HOST_TESTS)
        binary = temp / 'ledger'
        compile_cmd = ['clang++', '-std=c++17', '-Wall', '-Wextra', '-Wno-unused-parameter', '-Wno-deprecated-declarations', str(cpp), '-lsqlite3', '-o', str(binary)]
        if __import__('sys').platform != 'darwin':
            compile_cmd.append('-lcrypto')
        build = subprocess.run(compile_cmd, text=True, capture_output=True)
        if build.returncode:
            print(build.stderr)
            return build.returncode
        result = subprocess.run([str(binary), str(temp / 'files')], text=True, capture_output=True)
        print(result.stdout, end='')
        if result.returncode:
            print(result.stderr, end='')
            return result.returncode
        crash = subprocess.run([str(binary), str(temp / 'files'), 'crash'], text=True, capture_output=True)
        assert crash.returncode == 99, (crash.returncode, crash.stderr)
        recovery = subprocess.run([str(binary), str(temp / 'files'), 'recover'], text=True, capture_output=True)
        print(recovery.stdout, end='')
        assert recovery.returncode == 0, recovery.stderr
        host_count = re.findall(r'^HOST_ASSERTIONS\|(\d+)$', result.stdout, re.M)
        recovery_count = re.findall(r'^FRESH_PROCESS_RECOVERY\|PASS\|(\d+)$', recovery.stdout, re.M)
        assert len(host_count) == 1 and len(recovery_count) == 1
        vectors = {}
        for line in result.stdout.splitlines():
            if line.startswith('LEDGER_VECTOR|'):
                _, case_id, r, u, c, pct, balance, state, valid, partial, ambiguous, members_available, member_identifiers = line.split('|')
                if case_id in vectors:
                    raise AssertionError(f'duplicate result {case_id}')
                vectors[case_id] = dict(realized_posted=r, floating_remaining=u, compensated=c, percent=pct, balance=balance, state=int(state), valid=valid == '1', partial=partial == '1', ambiguous=ambiguous == '1', members_available=members_available == '1', member_identifiers=member_identifiers)
        assert set(vectors) == {c['id'] for c in oracle['cases']}
        mapping = []
        for expected in oracle['cases']:
            actual = vectors[expected['id']]
            for field in ('realized_posted', 'floating_remaining', 'compensated', 'balance'):
                assert abs(Decimal(actual[field]) - Decimal(expected[field])) < Decimal('0.00000001'), (expected['id'], field, actual[field], expected[field])
            assert abs(Decimal(actual['percent']) - Decimal(expected['percent_exact'])) < Decimal('0.00000001'), expected['id']
            assert Decimal(actual['percent']).quantize(Decimal('.01'), rounding=ROUND_HALF_UP) == Decimal(expected['percent_display']), expected['id']
            state = expected['expected_state']
            assert actual['valid'], expected['id']
            assert actual['partial'] == (state == 'partial'), expected['id']
            assert actual['ambiguous'] == (state == 'genesis_ambiguous'), expected['id']
            if state == 'closed': assert actual['state'] == 3
            if state == 'open_pending': assert actual['state'] == 2
            mapping.append({'id': expected['id'], 'oracle_expected_state': state, 'status': 'PASS', 'evidence': 'JPWLedgerTestFixture raw field mapping; production JPWLedgerBuild output; frozen Decimal amount/percent/state assertions', 'actual': actual})
        labels = re.findall(r'REQUIRE\([^\n]*?,\s*"([^"\n]+)"\)', HOST_TESTS)
        receipt = {'schema': 'jpw-ledger-host-receipt/v1', 'host_core': 'PASS', 'host_sqlite_store': 'PASS', 'cross_process_crash_recovery': 'PASS: separate seed, interrupted uncommitted write, recovery/replay OS processes using the same SQLite file', 'host_assertion_count': int(host_count[0]), 'recovery_assertion_count': int(recovery_count[0]), 'fixture_mapping': 'field-mapped synthetic inputs, not a real account replay', 'source_sha256': hashes, 'cases': mapping, 'non_numeric_checks': oracle['required_non_numeric'], 'executed_assertions': labels, 'assertion_labels_note': 'Source-location labels can repeat or execute more than once; runtime counters above are the actual execution counts.', 'native_mql_compile': 'NOT_RUN', 'terminal_adapter_reconciliation': 'NOT_RUN', 'native_singleton_lease': 'NOT_RUN', 'mt5_runtime': 'NOT_RUN', 'real_account_or_trades': 'NOT_RUN', 'limits': 'Host shims do not prove native MQL API/ABI, broker coverage, terminal transaction races or UI rendering. DECLARED coverage is conditional operator evidence, not automatic verification.'}
        if args.receipt:
            args.receipt.parent.mkdir(parents=True, exist_ok=True)
            args.receipt.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + '\n')
        print(json.dumps({'host_core': 'PASS', 'host_sqlite_store': 'PASS', 'independent_oracles': len(mapping), 'native_mt5': 'NOT_RUN'}))
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
