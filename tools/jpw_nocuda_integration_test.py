#!/usr/bin/env python3
"""Source-linked host checks for the NoCuda terminal adapter and view contract.

Compiles selected production MQL5 functions with synthetic MT5 API responses.
Static checks cover boundaries that cannot be exercised without a native chart.
This is not a MetaEditor compile or a native MT5 interaction test.
"""

from __future__ import annotations

import hashlib
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import unittest
from leverage_source import expanded_source


ROOT = Path(__file__).resolve().parents[1]
INCLUDE = ROOT / "mt5/jpw-alavancagem-atual/MQL5/Include/JPWealth"
CORE = INCLUDE / "JPW_NoCuda_Core.mqh"
TERMINAL = INCLUDE / "JPW_NoCuda_Terminal.mqh"
RENDER = INCLUDE / "JPW_NoCuda_Render.mqh"
UI = INCLUDE / "JPW_NoCuda_UI.mqh"
STORE = INCLUDE / "JPW_NoCuda_Store.mqh"
PROJECTION_CORE = INCLUDE / "JPW_NoCuda_Projection_Core.mqh"
INDICATOR = ROOT / "mt5/jpw-alavancagem-atual/MQL5/Indicators/JPWealth/JPW_NoCuda_Channels.mq5"


def function(text: str, name: str) -> str:
    """Return a production function including its body, preserving source code."""
    match = re.search(r"\b(?:bool|void|int|double|string|datetime)\s+" +
                      re.escape(name) + r"\s*\(", text)
    if not match:
        raise AssertionError(f"missing production function {name}")
    opening = text.find("{", match.end())
    if opening < 0:
        raise AssertionError(f"missing body for {name}")
    depth = 0
    for offset in range(opening, len(text)):
        if text[offset] == "{":
            depth += 1
        elif text[offset] == "}":
            depth -= 1
            if depth == 0:
                return text[match.start():offset + 1]
    raise AssertionError(f"unclosed body for {name}")


HOST_SHIM = r'''
#include <algorithm>
#include <cmath>
#include <iostream>
#include <string>
#include <vector>
using string = std::string;
using datetime = long long;
using ENUM_TIMEFRAMES = int;
struct MqlRates { datetime time; double close; };
struct Feed { int tf; int seconds; std::vector<MqlRates> bars; };
constexpr int CHART_WIDTH_IN_PIXELS=1,CHART_HEIGHT_IN_PIXELS=2;
long long ChartGetInteger(int,int property) { return property==1 ? 800 : 600; }
int MathMax(int a,int b) { return std::max(a,b); }
int MathMin(int a,int b) { return std::min(a,b); }
void JPWNoCudaClearDaily() {}
bool g_nocuda_panel_open=false;
int g_nocuda_pick=1,g_nocuda_tab=0;
constexpr int PERIOD_H1 = 16385;
constexpr int PERIOD_D1 = 16408;
std::vector<Feed> feeds = {
  {PERIOD_H1, 3600, {{3600,1.1000},{7200,1.1010},{10800,1.1020},
                     {14400,1.1030},{100000,1.1040}}},
  {PERIOD_D1, 86400, {{1000,2.0000},{87400,2.0100},{173800,2.0200}}}
};
int chart_tf = PERIOD_H1;
const Feed* feed_for(int tf) {
  for (const auto &feed : feeds) if (feed.tf == tf) return &feed;
  return nullptr;
}
bool ChartXYToTimePrice(long long, int x, int y, int &subwindow,
                        datetime &time, double &price) {
  if (x < 0) return false;
  subwindow = (y == 99 ? 1 : 0);
  time = x;
  price = 9.9999; // The adapter must ignore cursor price.
  return true;
}
int iBarShift(const string &, int tf, datetime time, bool exact) {
  const Feed* f = feed_for(tf);
  if (!f) return -1;
  for (int i = int(f->bars.size()) - 1; i >= 0; --i)
    if ((exact && f->bars[i].time == time) ||
        (!exact && f->bars[i].time <= time))
      return int(f->bars.size()) - 1 - i;
  return -1;
}
datetime iTime(const string &, int tf, int shift) {
  const Feed* f = feed_for(tf);
  if (!f || shift < 0 || shift >= int(f->bars.size())) return 0;
  return f->bars[f->bars.size() - 1 - shift].time;
}
double iClose(const string &, int tf, int shift) {
  const Feed* f = feed_for(tf);
  if (!f || shift < 0 || shift >= int(f->bars.size())) return 0;
  return f->bars[f->bars.size() - 1 - shift].close;
}
int PeriodSeconds(int tf) {
  const Feed* f = feed_for(tf);
  return f ? f->seconds : 0;
}
bool MathIsValidNumber(double value) { return std::isfinite(value); }
double MathAbs(double value) { return std::abs(value); }
int StringFind(const string& value,const string& needle) {
  const auto at=value.find(needle); return at==string::npos ? -1 : int(at);
}
int StringLen(const string& value) { return int(value.size()); }
string StringSubstr(const string& value,int start) { return value.substr(start); }
constexpr int OBJPROP_TIME=1;
datetime drag_release=0;
long long ObjectGetInteger(int,const string&,int,int) { return drag_release; }
string g_nocuda_prefix="JPWNC_TEST_",g_nocuda_symbol="EURUSD.synthetic";
string g_nocuda_status="";
bool g_nocuda_is_draft=false;
ENUM_TIMEFRAMES g_nocuda_source_tf=PERIOD_H1;
datetime g_nocuda_a_open=0,g_nocuda_b_open=0,g_nocuda_c_open=0;
datetime g_nocuda_a_known=0,g_nocuda_b_known=0,g_nocuda_c_known=0;
double g_nocuda_a_close=0,g_nocuda_b_close=0,g_nocuda_c_close=0;
void JPWNoCudaPaint() {}
void JPWNoCudaDrawUI() {}
void ChartRedraw(int) {}
int failures = 0,checks=0;
void check(bool truth, const char* label) {
  ++checks;
  if (!truth) { ++failures; std::cerr << "FAIL: " << label << '\n'; }
}
'''


HOST_CASES = r'''
int main() {
  datetime opened=0, known=0;
  double closed=0;
  string reason;
  const string symbol="EURUSD.synthetic";
  check(JPWNoCudaClickedClose(symbol,PERIOD_H1,11000,1,
                             opened,closed,known,reason) &&
        opened==10800 && std::abs(closed-1.1020)<1e-12 && known==14400,
        "H1 click snaps to completed source Close and its next opening");
  chart_tf=PERIOD_D1;
  check(JPWNoCudaClickedClose(symbol,PERIOD_H1,11000,1,
                             opened,closed,known,reason) &&
        opened==10800 && std::abs(closed-1.1020)<1e-12,
        "chart timeframe change cannot change explicit H1 source selection");
  chart_tf=PERIOD_H1;
  check(JPWNoCudaClickedClose(symbol,PERIOD_D1,87500,1,
                             opened,closed,known,reason) &&
        opened==87400 && std::abs(closed-2.0100)<1e-12 && known==173800,
        "explicit D1 source selects its own completed bar on an H1 chart");
  check(!JPWNoCudaClickedClose(symbol,PERIOD_H1,100010,1,
                              opened,closed,known,reason),
        "currently open source bar cannot be an anchor");
  check(!JPWNoCudaClickedClose(symbol,PERIOD_H1,50000,1,
                              opened,closed,known,reason),
        "missing interval cannot be mapped to an old candle");
  check(!JPWNoCudaClickedClose(symbol,PERIOD_H1,11000,99,
                              opened,closed,known,reason),
        "click outside the main chart cannot pick an anchor");
  int shift=-1;
  check(JPWNoCudaExactBar(symbol,PERIOD_H1,10800,shift,closed,known) &&
        shift==2 && std::abs(closed-1.1020)<1e-12 && known==14400,
        "exact lookup uses source bar opening and source Close");
  check(!JPWNoCudaExactBar(symbol,PERIOD_H1,11000,shift,closed,known),
        "non-opening time cannot identify a source bar");
  check(!JPWNoCudaExactBar(symbol,PERIOD_H1,100000,shift,closed,known),
        "current source bar is never a confirmed anchor");
  check(!JPWNoCudaClickedClose(symbol,0,11000,1,
                              opened,closed,known,reason),
        "unavailable source timeframe must be refused");
  feeds[0].bars[2].close=0.0;
  check(!JPWNoCudaClickedClose(symbol,PERIOD_H1,11000,1,
                              opened,closed,known,reason),
        "unavailable source Close must be refused");
  feeds[0].bars[2].close=1.1020;
  g_nocuda_is_draft=true;
  drag_release=11000;
  JPWNoCudaDragAnchor("JPWNC_TEST_DRAW_ANCHOR_A");
  check(g_nocuda_a_open==10800 && std::abs(g_nocuda_a_close-1.1020)<1e-12 &&
        g_nocuda_a_known==14400,
        "dragged A snaps to completed source Close");
  drag_release=50000;
  JPWNoCudaDragAnchor("JPWNC_TEST_DRAW_ANCHOR_A");
  check(g_nocuda_a_open==10800 && std::abs(g_nocuda_a_close-1.1020)<1e-12,
        "drag into missing interval leaves draft anchor unchanged");
  drag_release=7201;
  JPWNoCudaDragAnchor("JPWNC_TEST_DRAW_ANCHOR_B");
  check(g_nocuda_b_open==7200 && std::abs(g_nocuda_b_close-1.1010)<1e-12,
        "dragged B snaps to source Close");
  feeds[0].bars[0].close=1.1040; // C must define nonzero signed width.
  drag_release=3601;
  JPWNoCudaDragAnchor("JPWNC_TEST_DRAW_ANCHOR_C");
  check(g_nocuda_c_open==3600 && std::abs(g_nocuda_c_close-1.1040)<1e-12,
        "dragged C snaps to source Close");
  drag_release=11000;
  JPWNoCudaDragAnchor("OTHER_DRAW_ANCHOR_B");
  check(g_nocuda_b_open==7200, "foreign anchor drag is ignored");
  g_nocuda_is_draft=false;
  JPWNoCudaDragAnchor("JPWNC_TEST_DRAW_ANCHOR_A");
  check(g_nocuda_a_open==10800, "confirmed anchor cannot be dragged");
  feeds[0].bars[0].close=1.1000;
  feeds[0].bars[1].close=1.1050;
  g_nocuda_is_draft=true; g_nocuda_pick=1;
  g_nocuda_a_open=g_nocuda_b_open=g_nocuda_c_open=0;
  g_nocuda_panel_open=false;
  JPWNoCudaPickAt(3601,1);
  check(g_nocuda_a_open==3600 && g_nocuda_pick==2 && !g_nocuda_panel_open,
        "production picker advances A to B and keeps candles unobstructed");
  JPWNoCudaPickAt(3601,1);
  check(g_nocuda_b_open==0 && g_nocuda_pick==2,
        "duplicate A/B is refused without disarming B");
  JPWNoCudaPickAt(10801,1);
  check(g_nocuda_b_open==10800 && g_nocuda_pick==3,
        "production picker advances distinct B to C");
  JPWNoCudaPickAt(3601,1);
  check(g_nocuda_c_open==0 && g_nocuda_pick==3,
        "zero-width C is refused without disarming C");
  JPWNoCudaPickAt(7201,1);
  check(g_nocuda_c_open==7200 && g_nocuda_pick==0 && g_nocuda_panel_open,
        "valid C opens preview and never confirms the draft");
  drag_release=10801;
  JPWNoCudaDragAnchor("JPWNC_TEST_DRAW_ANCHOR_A");
  check(g_nocuda_a_open==3600 && g_nocuda_b_open==10800,
        "drag refuses duplicate AB and restores accepted draft geometry");
  std::cout << "HOST_NOCUDA_ADAPTER: " << (checks-failures) << "/" << checks << " PASS\n";
  std::cout << "MQL5_NATIVE_COMPILATION: NOT_RUN; MQL5_NATIVE_EXECUTION: NOT_RUN\n";
  return failures ? 1 : 0;
}
'''


ACTION_SHIM = r'''
#include <algorithm>
#include <iostream>
#include <string>
#include <vector>
#include <map>
using string = std::string;
using ENUM_TIMEFRAMES = int;
using ulong = unsigned long;
constexpr int CHARTEVENT_OBJECT_CLICK=1;
constexpr int CHARTEVENT_CLICK=2;
constexpr int CHARTEVENT_CHART_CHANGE=3;
constexpr int CHARTEVENT_OBJECT_DRAG=4;
constexpr int PERIOD_H1=16385, PERIOD_M15=15;
constexpr int ACCOUNT_SERVER=1;
string _Symbol="EURUSD.synthetic",g_nocuda_symbol="EURUSD.synthetic";
string g_nocuda_feed="synthetic-server";
string AccountInfoString(int) { return "synthetic-server"; }
ulong mock_ms=0;
ulong GetTickCount64() { return mock_ms; }
struct Record { int revision=0; string study_id="study-A"; };
string g_nocuda_prefix="JPWNC_TEST_", g_nocuda_status="";
string g_nocuda_preferred_study="";
bool g_nocuda_panel_open=true, g_nocuda_is_draft=false;
bool g_nocuda_visible=true, g_nocuda_full_mesh=true;
bool g_nocuda_has_view=true, g_nocuda_has_head=true;
int g_nocuda_pick=0, g_nocuda_tab=0, g_nocuda_level=36;
bool g_nocuda_pending_pick=false,g_nocuda_recent_object=false;
int g_nocuda_pending_x=0,g_nocuda_pending_y=0;
int g_nocuda_object_x=0,g_nocuda_object_y=0;
ulong g_nocuda_pending_ms=0,g_nocuda_object_ms=0;
int g_nocuda_study_index=0;
ENUM_TIMEFRAMES g_nocuda_source_tf=PERIOD_H1;
Record g_nocuda_view{1}, g_nocuda_head{2};
std::vector<string> g_nocuda_studies={"study-A", "study-B"};
int confirm_calls=0, cancel_calls=0, load_calls=0, reload_calls=0;
int paint_calls=0, ui_calls=0, pick_calls=0, drag_calls=0, chart_save_calls=0;
int failures=0,checks=0;
void check(bool truth,const char* label) {
  ++checks;
  if (!truth) { ++failures; std::cerr << "FAIL: " << label << '\n'; }
}
int StringLen(const string& s) { return int(s.size()); }
string StringSubstr(const string& s,int start) { return s.substr(start); }
int StringFind(const string& s,const string& needle) {
  const auto pos=s.find(needle); return pos==string::npos ? -1 : int(pos);
}
long StringToInteger(const string& s) { return std::stol(s); }
int MathMax(int a,int b) { return std::max(a,b); }
int MathMin(int a,int b) { return std::min(a,b); }
int MathAbs(int value) { return std::abs(value); }
int ArraySize(const std::vector<string>& values) { return int(values.size()); }
struct Daily { bool valid=false; };
Daily g_nocuda_daily;
bool g_nocuda_show_refs=false;
int g_nocuda_measure_page=0,g_nocuda_page=0;
bool g_nocuda_panel_focus=false,g_nocuda_skip_field_capture=false;
string g_nocuda_level_input="",g_nocuda_ui_editing="",g_nocuda_ui_focus="";
int g_nocuda_ui_pages=5;
constexpr int CHARTEVENT_OBJECT_ENDEDIT=24,CHARTEVENT_KEYDOWN=25;
constexpr int TERMINAL_KEYSTATE_SHIFT=18,OBJPROP_TYPE=2,OBJ_BUTTON=3,OBJ_LABEL=1;
constexpr int OBJPROP_TOOLTIP=9,OBJPROP_XDISTANCE=10,OBJPROP_YDISTANCE=11,OBJPROP_HIDDEN=12,OBJPROP_SELECTABLE=13,OBJPROP_SELECTED=14,OBJ_EDIT=4;
std::map<string,string> focus_objects;
std::map<string,int> focus_object_types;
std::vector<string> focus_events;
int ObjectFind(int,const string&name){return focus_objects.count(name)?0:-1;}
bool ObjectCreate(int,const string&name,int type,int,int,int){focus_objects[name]="";focus_object_types[name]=type;return true;}
bool ObjectSetInteger(int,const string&,int,long){return true;}
bool ObjectSetString(int,const string&name,int,const string&value){focus_objects[name]=value;return true;}
bool ObjectDelete(int,const string&name){return focus_objects.erase(name)>0;}
bool EventChartCustom(int,int,long,double,const string&owner){focus_events.push_back(owner);return true;}
// This replay targets legacy Close drawing. Native Fibo dispatch is tested by
// its separate renderer/core integration; only the dispatch boundary is stubbed.
bool g_ncf_mode=false;int ncf_dispatch_calls=0;
bool JPWNCFHandleEvent(int,const long&,const double&,const string&){ncf_dispatch_calls++;return g_ncf_mode;}
int shift_key=0;
int TerminalInfoInteger(int) { return shift_key; }
int ObjectGetInteger(int,const string&name,int prop) { return prop==OBJPROP_TYPE&&focus_object_types.count(name)?focus_object_types[name]:0; }
string JPWNoCudaUIFocusCycle(const string& prefix,const string&,bool reverse) { return prefix+(reverse ? "UI_CLOSE" : "UI_PAGE_NEXT"); }
constexpr int OBJPROP_TEXT=1;
string ObjectGetString(int,const string&name,int) { return focus_objects.count(name)?focus_objects[name]:"0.5"; }
void JPWNoCudaClearDaily() {}
void JPWNoCudaConsultDay() {}
bool JPWNoCudaSelectLevelText(const string&) { return true; }
int JPWNoCudaUIMeasurePages() { return 2; }
int select_calls=0;
void JPWNoCudaSelectLineAt(int,int) { ++select_calls; }
void JPWNoCudaReadJustification() {}
void JPWNoCudaDrawUI() { ++ui_calls; }
void ChartRedraw(int) {}
void JPWNoCudaNewDraft() { g_nocuda_is_draft=true; }
void JPWNoCudaEditDraft() { g_nocuda_is_draft=true; }
void JPWNoCudaCancelDraft() { ++cancel_calls; g_nocuda_is_draft=false; }
bool JPWNoCudaConfirmDraft() { ++confirm_calls; return true; }
void JPWNoCudaPaint() { ++paint_calls; }
bool JPWNoCudaReloadStudies() { ++reload_calls; return true; }
bool JPWNoCudaLoadStudy(int, int=0) { ++load_calls; return true; }
ENUM_TIMEFRAMES JPWNoCudaNextTf(ENUM_TIMEFRAMES tf) {
  return tf==PERIOD_H1 ? PERIOD_M15 : PERIOD_H1;
}
void JPWNoCudaPickAt(int,int) { ++pick_calls; }
void JPWNoCudaDragAnchor(const string&) { ++drag_calls; }
void JPWNoCudaSaveChartState() { ++chart_save_calls; }
'''


ACTION_CASES = r'''
void object_click(const string& name) {
  OnChartEvent(CHARTEVENT_OBJECT_CLICK,11L,12.0,name);
}
void object_click_at(const string& name,int x,int y) {
  if (name.find("JPWNC_TEST_UI_")==0) g_nocuda_panel_open=true;
  OnChartEvent(CHARTEVENT_OBJECT_CLICK,x,double(y),name);
}
int main() {
  object_click("OTHER_UI_CONFIRM");
  check(confirm_calls==0 && paint_calls==0,
        "foreign indicator object cannot trigger NoCuda action");
  const int before_edit_focus=ui_calls;
  object_click("JPWNC_TEST_UI_JUST");
  check(ui_calls==before_edit_focus && confirm_calls==0,
        "focusing the justification edit must not recreate its control");
  OnChartEvent(CHARTEVENT_CHART_CHANGE,0L,0.0,"");
  check(confirm_calls==0 && paint_calls==1 && chart_save_calls==0,
        "chart change repaints without writing revision or chart state");
  g_nocuda_is_draft=true;
  g_nocuda_pick=1;
  mock_ms+=2000; // The previous foreign-object click is a separate gesture.
  OnChartEvent(CHARTEVENT_CLICK,11L,12.0,"");
  check(confirm_calls==0 && pick_calls==0 && g_nocuda_pending_pick,
        "bare chart click waits for a possible paired object event");
  JPWNoCudaFlushChartClick();
  check(confirm_calls==0 && pick_calls==1,
        "unpaired chart click picks once, without confirming");
  object_click_at("COCKPIT_CONTROL",31,32);
  OnChartEvent(CHARTEVENT_CLICK,31L,32.0,"");
  JPWNoCudaFlushChartClick();
  check(pick_calls==1,
        "foreign object then generic chart click cannot pick an anchor");
  mock_ms+=2000;
  OnChartEvent(CHARTEVENT_CLICK,41L,42.0,"");
  object_click_at("COCKPIT_CONTROL",41,42);
  JPWNoCudaFlushChartClick();
  check(pick_calls==1,
        "generic chart click then foreign object cannot pick an anchor");
  g_nocuda_is_draft=true;
  mock_ms+=2000;
  OnChartEvent(CHARTEVENT_CLICK,51L,52.0,"");
  object_click_at("JPWNC_TEST_UI_PICK_A",51,52);
  JPWNoCudaFlushChartClick();
  check(pick_calls==1 && g_nocuda_pick==1,
        "click-first NoCuda control arms A without selecting underlying bar");
  mock_ms+=2000;
  object_click_at("JPWNC_TEST_UI_PICK_B",61,62);
  OnChartEvent(CHARTEVENT_CLICK,61L,62.0,"");
  JPWNoCudaFlushChartClick();
  check(pick_calls==1 && g_nocuda_pick==2,
        "object-first NoCuda control arms B without selecting underlying bar");
  mock_ms+=2000;
  object_click_at("JPWNC_TEST_CANVAS",71,72);
  OnChartEvent(CHARTEVENT_CLICK,71L,72.0,"");
  JPWNoCudaFlushChartClick();
  check(pick_calls==2,
        "NoCuda canvas object plus generic click selects exactly once");
  mock_ms+=2000;
  OnChartEvent(CHARTEVENT_CLICK,81L,82.0,"");
  object_click_at("JPWNC_TEST_CANVAS",81,82);
  JPWNoCudaFlushChartClick();
  check(pick_calls==3,
        "generic click before NoCuda canvas object selects exactly once");
  mock_ms+=2000;
  OnChartEvent(CHARTEVENT_CLICK,91L,92.0,"");
  g_nocuda_panel_open=true;
  object_click("JPWNC_TEST_UI_PICK_C");
  check(pick_calls==4 && g_nocuda_pick==3,
        "independent earlier chart click is resolved before next UI action");
  mock_ms+=2000;
  OnChartEvent(CHARTEVENT_CLICK,101L,102.0,"");
  _Symbol="OTHER.synthetic";
  JPWNoCudaFlushChartClick();
  check(pick_calls==4,
        "context switch discards an unresolved chart click");
  _Symbol=g_nocuda_symbol;
  mock_ms+=2000;
  OnChartEvent(CHARTEVENT_CLICK,111L,112.0,"");
  OnChartEvent(CHARTEVENT_CHART_CHANGE,0L,0.0,"");
  JPWNoCudaFlushChartClick();
  check(pick_calls==4,
        "chart geometry change discards old pixel coordinates");
  OnChartEvent(CHARTEVENT_OBJECT_DRAG,0L,0.0,"JPWNC_TEST_DRAW_ANCHOR_A");
  check(confirm_calls==0 && drag_calls==1,
        "anchor drag does not confirm a revision");
  g_nocuda_panel_open=true;
  object_click("JPWNC_TEST_UI_CANCEL");
  check(confirm_calls==0 && cancel_calls==1 && chart_save_calls==0,
        "Cancel does not reach a write path");
  object_click("JPWNC_TEST_UI_VIS");
  object_click("JPWNC_TEST_UI_MESH");
  check(confirm_calls==0 && !g_nocuda_visible && !g_nocuda_full_mesh,
        "view toggles do not confirm or modify study revision");
  g_nocuda_is_draft=true;
  object_click("JPWNC_TEST_UI_TF");
  check(g_nocuda_source_tf==PERIOD_H1 && reload_calls==0 && confirm_calls==0,
        "source timeframe cannot change during an unconfirmed draft");
  g_nocuda_is_draft=false;
  object_click("JPWNC_TEST_UI_TF");
  check(g_nocuda_source_tf==PERIOD_M15 && reload_calls==1 && confirm_calls==0,
        "explicit source timeframe change reloads context without writing");
  g_nocuda_is_draft=true;
  object_click("JPWNC_TEST_UI_STUDY_NEXT");
  object_click("JPWNC_TEST_UI_REV_NEXT");
  check(load_calls==0 && confirm_calls==0,
        "study and revision navigation blocked while drafting");
  g_nocuda_is_draft=false;
  object_click("JPWNC_TEST_UI_STUDY_NEXT");
  object_click("JPWNC_TEST_UI_REV_NEXT");
  check(load_calls==2 && confirm_calls==0,
        "navigation loads studies without confirming");
  g_nocuda_level=0;
  object_click("JPWNC_TEST_UI_LEVEL_PREV");
  check(g_nocuda_level==0, "level selector cannot go below -4");
  g_nocuda_level=64;
  object_click("JPWNC_TEST_UI_LEVEL_NEXT");
  check(g_nocuda_level==64, "level selector cannot go above +4");
  g_nocuda_panel_open=false;
  object_click("JPWNC_TEST_UI_CONFIRM");
  check(confirm_calls==0, "closed panel cannot confirm a revision");
  object_click("JPWNC_TEST_UI_OPEN");
  object_click("JPWNC_TEST_UI_CONFIRM");
  check(confirm_calls==1, "only explicit Confirm reaches revision confirmation");
  g_nocuda_is_draft=false;
  mock_ms+=2000;
  const int before_select=select_calls;
  OnChartEvent(CHARTEVENT_CLICK,161L,162.0,"");
  object_click_at("COCKPIT_OTHER_CONTROL",161,162);
  JPWNoCudaFlushChartClick();
  check(select_calls==before_select,"foreign control cannot select a line outside pick mode");
  mock_ms+=2000;
  OnChartEvent(CHARTEVENT_CLICK,171L,172.0,"");
  object_click_at("JPWNC_TEST_CANVAS",171,172);
  JPWNoCudaFlushChartClick();
  check(select_calls==before_select+1,"canvas click selects line exactly once outside pick mode");
  g_nocuda_panel_open=true;g_nocuda_panel_focus=false;g_nocuda_ui_editing="";
  object_click("JPWNC_TEST_UI_TAB_1");
  OnChartEvent(CHARTEVENT_CLICK,11,12.0,"");
  check(g_nocuda_panel_focus,"paired bare click after own object retains keyboard focus");
  OnChartEvent(CHARTEVENT_CLICK,81,82.0,"");
  object_click_at("JPWNC_TEST_UI_TAB_1",81,82);
  check(g_nocuda_panel_focus,"paired object after bare click restores own keyboard focus");
  g_nocuda_panel_focus=false;
  const int prior_keyboard_ui=ui_calls;
  OnChartEvent(CHARTEVENT_KEYDOWN,9,0.0,"");
  check(ui_calls==prior_keyboard_ui,"keyboard outside own focus does not navigate");
  g_nocuda_is_draft=true;g_nocuda_panel_focus=true;g_nocuda_ui_editing="JPWNC_TEST_UI_DATE";
  OnChartEvent(CHARTEVENT_KEYDOWN,27,0.0,"");
  check(!g_nocuda_panel_open && g_nocuda_is_draft,"Escape during field edit closes the panel preserving its draft");
  object_click("JPWNC_TEST_UI_OPEN");
  for(const auto& name:{"JPWNC_TEST_UI_PAGE_NEXT","JPWNC_TEST_UI_CLOSE"}){focus_objects[name]="synthetic visible button";focus_object_types[name]=OBJ_BUTTON;}
  g_nocuda_panel_focus=true;
  g_nocuda_ui_editing="";shift_key=0;OnChartEvent(CHARTEVENT_KEYDOWN,9,0.0,"");
  check(g_nocuda_ui_focus=="JPWNC_TEST_UI_PAGE_NEXT","Tab focuses a visible own button");
  g_nocuda_measure_page=0;g_nocuda_tab=1;OnChartEvent(CHARTEVENT_KEYDOWN,13,0.0,"");
  check(g_nocuda_measure_page==1,"Enter activates focused page navigation");
  shift_key=0x8000;OnChartEvent(CHARTEVENT_KEYDOWN,9,0.0,"");
  check(g_nocuda_ui_focus=="JPWNC_TEST_UI_CLOSE","Shift Tab reverses own focus");
  OnChartEvent(CHARTEVENT_KEYDOWN,13,0.0,"");
  check(!g_nocuda_panel_open,"Enter on Close closes without discarding draft");
  object_click("JPWNC_TEST_UI_OPEN");
  check(JPWUIOwns(g_nocuda_prefix),"production launcher reacquires focus after closing legacy panel");
  OnChartEvent(CHARTEVENT_KEYDOWN,27,0.0,"");
  check(!g_nocuda_panel_open,"Escape closes own panel when not editing");
  g_nocuda_panel_open=true;g_nocuda_panel_focus=true;object_click("FOREIGN_COCKPIT_BUTTON");
  check(!g_nocuda_panel_focus,"foreign indicator control releases NoCuda keyboard focus");
  check(ncf_dispatch_calls>0 && !g_ncf_mode,"legacy replay explicitly routes through inactive native-Fibo dispatch boundary");
  check(JPWUIAcquire("COCKPIT_TEST_") && JPWUIOwns("COCKPIT_TEST_"),"shared focus can transfer to Cockpit without data writes");
  JPWUIRelease(g_nocuda_prefix);
  check(JPWUIOwns("COCKPIT_TEST_"),"legacy NoCuda cannot release Cockpit ownership");
  std::cout << "HOST_NOCUDA_ACTIONS: " << (checks-failures)
            << "/" << checks << " PASS\n";
  return failures ? 1 : 0;
}
'''


UI_SHIM = r'''
#include <iostream>
#include <string>
#include <vector>
#include <unordered_map>
#include <iomanip>
#include <sstream>
#include <algorithm>
#include <fstream>
#include <cstdlib>
#include <cmath>
using string=std::string; using color=int; using uint=unsigned int;
using ENUM_OBJECT=int; using ENUM_OBJECT_PROPERTY_STRING=int;
constexpr int CHART_WIDTH_IN_PIXELS=1,CHART_HEIGHT_IN_PIXELS=2,CHART_COLOR_BACKGROUND=3;
constexpr int OBJ_RECTANGLE_LABEL=1,OBJ_LABEL=2,OBJ_BUTTON=3,OBJ_EDIT=4;
constexpr int OBJ_BITMAP_LABEL=5,OBJPROP_BMPFILE=104,OBJPROP_BACK=15,OBJPROP_ZORDER=16,TERMINAL_SCREEN_DPI=1;
constexpr int OBJPROP_CORNER=1,OBJPROP_XDISTANCE=2,OBJPROP_YDISTANCE=3,OBJPROP_XSIZE=4,OBJPROP_YSIZE=5;
constexpr int OBJPROP_BGCOLOR=6,OBJPROP_COLOR=7,OBJPROP_SELECTABLE=8,OBJPROP_HIDDEN=9,OBJPROP_ANCHOR=10;
constexpr int OBJPROP_FONTSIZE=11,OBJPROP_BORDER_COLOR=12,OBJPROP_STATE=13,OBJPROP_TYPE=14;
constexpr int OBJPROP_FONT=101,OBJPROP_TEXT=102,OBJPROP_TOOLTIP=103,OBJPROP_READONLY=105;
constexpr int CORNER_LEFT_UPPER=0,ANCHOR_LEFT_UPPER=0;
struct Rect { int x=0,y=0,w=0,h=0,type=0,font=10,ink=0,fill=0,corner=0; string text,tooltip; bool state=false; };
std::unordered_map<string,Rect> controls;
std::unordered_map<string,string> labels;
std::vector<string> object_order;
int chart_width=800,chart_height=404,measured_line=12,background=0xffffff,current_font=100;
long TerminalInfoInteger(int) { return measured_line*96/12; }

double MathRound(double value){return std::round(value);}
double MathSqrt(double value){return std::sqrt(value);}
uint StringGetCharacter(const string&value,int index){return (unsigned char)value.at(index);}
uint ColorToARGB(color value,int alpha){return ((uint)alpha<<24)|(uint(value)&0xffffff);}
constexpr int COLOR_FORMAT_ARGB_NORMALIZE=1;
template<class T>void ArrayInitialize(std::vector<T>&values,int value){std::fill(values.begin(),values.end(),value);}
std::unordered_map<string,std::vector<uint>> icon_resources;
bool ResourceCreate(const string&name,const std::vector<uint>&pixels,int width,int height,int,int,int,int){
 if(width<=0||height<=0||pixels.size()!=size_t(width*height))return false;
 icon_resources[name]=pixels;return true;
}
bool ResourceFree(const string&name){return icon_resources.erase(name)>0;}

int creates=0,deletes=0,text_writes=0;
bool g_nocuda_is_draft=true;
string g_nocuda_prefix="JPWNC_TEST_",g_nocuda_justification="",g_nocuda_date="",g_nocuda_level_input="";
void JPWNoCudaClearDaily() {}
int MathMax(int a,int b) { return std::max(a,b); }
int MathMin(int a,int b) { return std::min(a,b); }
template<typename T> int ArraySize(const std::vector<T>& a) { return int(a.size()); }
template<typename T> int ArrayResize(std::vector<T>& a,int n) { a.resize(n); return n; }
constexpr int FW_NORMAL=0;
bool TextSetFont(const string&,int size,int=0) { current_font=std::abs(size); return true; }
bool TextGetSize(const string& text,unsigned int& w,unsigned int& h) {
 h=measured_line*current_font/100; w=int(text.size())*measured_line*current_font/210; return true;
}
string DoubleToString(double value,int places) { std::ostringstream out; out<<std::fixed<<std::setprecision(places)<<value; return out.str(); }
long long ChartGetInteger(int,int property) {
 if(property==CHART_WIDTH_IN_PIXELS) return chart_width;
 if(property==CHART_HEIGHT_IN_PIXELS) return chart_height;
 return background;
}
long long ChartID() { return 123456; }
string StringFormat(const string&,long long id) { return "JPW_LEV_"+std::to_string(id)+"_HUD_BG"; }
int ObjectFind(int,const string& name) { return controls.count(name) ? 0 : -1; }
bool ObjectCreate(int,const string& name,int type,int,long long,double) {
 if(controls.count(name)) return false; controls[name].type=type; object_order.push_back(name); ++creates; return true;
}
bool ObjectDelete(int,const string& name) {
 if(!controls.count(name)) return false; controls.erase(name); labels.erase(name);
 object_order.erase(std::remove(object_order.begin(),object_order.end(),name),object_order.end()); ++deletes; return true;
}
int ObjectsTotal(int,int,int) { return int(object_order.size()); }
string ObjectName(int,int index,int,int) { return object_order.at(index); }
void text_bounds(Rect& r) {
 if(r.type==OBJ_LABEL) { const int old=current_font; current_font=r.font*10; uint w,h;TextGetSize(r.text,w,h);r.w=int(w);r.h=int(h); current_font=old; }
}
bool ObjectSetInteger(int,const string& name,int prop,long long val) {
 if(!controls.count(name)) return false; auto& r=controls[name];
 if(prop==OBJPROP_CORNER) r.corner=int(val);
 if(prop==OBJPROP_XDISTANCE) r.x=int(val); if(prop==OBJPROP_YDISTANCE) r.y=int(val);
 if(prop==OBJPROP_XSIZE) r.w=int(val); if(prop==OBJPROP_YSIZE) r.h=int(val);
 if(prop==OBJPROP_COLOR) r.ink=int(val); if(prop==OBJPROP_BGCOLOR) r.fill=int(val);
 if(prop==OBJPROP_STATE) r.state=bool(val); if(prop==OBJPROP_FONTSIZE) {r.font=int(val);text_bounds(r);} return true;
}
long long ObjectGetInteger(int,const string& name,int prop) {
 if(!controls.count(name)) return 0; const auto& r=controls.at(name);
 if(prop==OBJPROP_TYPE) return r.type; if(prop==OBJPROP_CORNER) return r.corner;
 if(prop==OBJPROP_XDISTANCE) return r.x; if(prop==OBJPROP_YDISTANCE) return r.y;
 if(prop==OBJPROP_XSIZE) return r.w; if(prop==OBJPROP_YSIZE) return r.h; return r.state;
}
string ObjectGetString(int,const string& name,int prop) {
 if(!controls.count(name)) return "";const auto& r=controls.at(name);
 return prop==OBJPROP_TEXT ? r.text : (prop==OBJPROP_TOOLTIP ? r.tooltip : "Arial");
}
bool ObjectSetString(int,const string& name,int prop,const string& value) {
 if(!controls.count(name)) return false;auto& r=controls[name];
 if(prop==OBJPROP_TEXT) { r.text=value;labels[name]=value;++text_writes;text_bounds(r); }
 if(prop==OBJPROP_TOOLTIP) r.tooltip=value; return true;
}
string IntegerToString(int v) { return std::to_string(v); }
int StringLen(const string& v) { return int(v.size()); }
string StringSubstr(const string& v,int start,int length) { return v.substr(start,length); }
string StringSubstr(const string& v,int start) { return v.substr(start); }
int StringFind(const string& text,const string& part,int start=0) { const auto at=text.find(part,start);return at==string::npos ? -1 : int(at); }
string json_escape(const string& value) { string out;for(char ch:value) { if(ch=='"' || ch=='\\') out+='\\';if(ch=='\n') {out+="\\n";continue;}out+=ch;} return out; }
void export_objects(const string& file) {
 std::ofstream out(file);out<<"{\"width\":"<<chart_width<<",\"height\":"<<chart_height<<",\"background\":"<<background<<",\"objects\":[";
 bool first=true;for(const auto& name:object_order) {const auto& r=controls.at(name); if(!first) out<<',';first=false;
 out<<"{\"id\":\""<<json_escape(name)<<"\",\"type\":"<<r.type<<",\"x\":"<<r.x<<",\"y\":"<<r.y<<",\"w\":"<<r.w<<",\"h\":"<<r.h<<",\"text\":\""<<json_escape(r.text)<<"\",\"font\":\"Arial\",\"size\":"<<r.font<<",\"color\":"<<r.ink<<",\"background\":"<<r.fill<<",\"state\":"<<(r.state ? "true" : "false")<<"}"; }
 out<<"],\"evidence\":\"source-linked simulated MT5 objects; native NOT_RUN\"}";
}
'''

UI_CASES = r'''
bool overlaps(const Rect& a,const Rect& b) { return a.x<b.x+b.w && b.x<a.x+a.w && a.y<b.y+b.h && b.y<a.y+a.h; }
int main() {
 JPWNoCudaUIView v{};v.open=true;v.symbol="EURUSD.synthetic";v.source_tf="H1";
 v.draft=true;v.geometry_valid=true;v.anchor_a=v.anchor_b=v.anchor_c=true;
 v.a_text="A · nível 0: 2026.09.28 08:00 · Close 1.10000";
 v.b_text="B · nível 0: 2026.09.28 12:00 · Close 1.10200";
 v.c_text="C · nível 1: 2026.09.28 10:00 · Close 1.10500";
 v.width_text="Largura 0.00400 · 1/8 0.00050 · 400.0 / 50.0 pontos";v.width_price="0.00400";v.subdivision_price="0.00050";
 v.justification="Estudo sintético; confirmação explícita da geometria.";
 v.date="2026.10.05";v.daily_valid=true;v.daily_state="Estimated";
 v.daily_start="00h: 1.11111111";v.daily_mid="12h: 1.22222222";v.daily_end="24h: 1.33333333";
 v.daily_mean="Média dos extremos: 1.22222222";v.daily_range="Faixa: 1.11111111 / 1.33333333";
 v.daily_source="Sessões semanais do símbolo exato, conferidas contra 14 dias civis encerrados.";
 v.daily_reason="Futuro estimado; exceções de calendário não confirmadas. Data no horário do servidor.";
 v.distance_text="Linha escolhida 1.12345 · distância 0.00450 · 450.0 pontos";
 v.quote_text="Bid 1.12795 · 2026.09.30 14:18:30 servidor · Current";
 v.study_id="SYNTHETIC-001";v.study_count=2;v.study_index=0;v.revision=2;v.head_revision=3;
 v.history_text="Confirmado em 2026.09.30 14:16:20 UTC (computador).";
 int failures=0,checks=0;
 for(int width:{300,390,800,1440}) for(int height:{380,390,400,402,420,499,500,520,560,700})
  for(int measured:{12,16,20,26,32}) for(int dark:{0,1}) for(int tab=0;tab<3;tab++) {
   chart_width=width;chart_height=height+24;measured_line=measured;background=dark ? 0x101010 : 0xffffff;
   v.tab=tab; bool seen[5]={false,false,false,false,false};bool fallback=false;
   for(int page=0;page<40;page++) {
    v.page=page;v.measure_page=page;JPWNoCudaUIRender("JPWNC_TEST_",v);
    if(!controls.count("JPWNC_TEST_UI_BG")) {
     fallback=true;++checks;
     if(!controls.count("JPWNC_TEST_UI_OPEN")) {
      const int margin=JPWUIDesignPx(8),lw=JPWUIDesignButtonWidth("NoCuda · Gráficos",10,true),lh=JPWNoCudaUIButtonHeight();
      if((width>=lw+2*margin&&chart_height>=lh+2*margin)||g_nocuda_ui_launcher_reason.find("espaço livre insuficiente")==string::npos){++failures;std::cerr<<"FAIL feasible fallback launcher omitted or missing unavailable reason\n";}
     }
     break;
    }
    ++checks;if(controls.count("JPWNC_TEST_UI_OPEN")) {++failures;std::cerr<<"FAIL launcher under open modal\n";}
    const auto modal=controls.at("JPWNC_TEST_UI_BG");
    fallback=controls.count("JPWNC_TEST_UI_SMALL");
    for(const auto& item:controls) {
     if(item.first=="JPWNC_TEST_UI_OPEN" || item.first=="JPWNC_TEST_UI_PICK_HINT") continue;
     const auto& r=item.second;++checks;
     if(r.x<modal.x || r.y<modal.y || r.x+r.w>modal.x+modal.w || r.y+r.h>modal.y+modal.h || r.w<0 || r.h<0) {
      ++failures;if(failures<20)std::cerr<<"FAIL bounds: "<<item.first<<" "<<width<<"x"<<height<<" scale "<<measured<<" tab "<<tab<<" page "<<page<<" rect "<<r.x<<","<<r.y<<","<<r.w<<","<<r.h<<'\n';
     }
     string owner;
     if(item.first.find("JPWNC_TEST_UI_DAILY_")==0 && item.first.find("CARD")==string::npos && item.first!="JPWNC_TEST_UI_DAILY_STATE" && item.first!="JPWNC_TEST_UI_DAILY_REFS") {
      const string suffix=item.first.substr(string("JPWNC_TEST_UI_DAILY_").size());
      if(!suffix.empty() && suffix[0]>='0' && suffix[0]<='4') owner="JPWNC_TEST_UI_DAILY_CARD_"+suffix.substr(0,1);
     }
     if(item.first.find("JPWNC_TEST_UI_RECORD_LINE_")==0) owner="JPWNC_TEST_UI_RECORD_CARD";
     if(controls.count("JPWNC_TEST_UI_CONFIRM_CARD") &&
        (item.first.find("JPWNC_TEST_UI_WIDTH")==0 || item.first=="JPWNC_TEST_UI_PREVIEW" || item.first.find("JPWNC_TEST_UI_JUST")==0)) owner="JPWNC_TEST_UI_CONFIRM_CARD";
     for(const string anchor:{"A","B","C"}) {
      if(item.first=="JPWNC_TEST_UI_"+anchor || item.first=="JPWNC_TEST_UI_"+anchor+"_B" || item.first=="JPWNC_TEST_UI_"+anchor+"_C" ||
         item.first.find("JPWNC_TEST_UI_DATE_"+anchor)==0 || item.first=="JPWNC_TEST_UI_PICK_"+anchor || item.first=="JPWNC_TEST_UI_ANCHOR_TITLE_"+anchor)
       owner="JPWNC_TEST_UI_ANCHOR_CARD_"+anchor;
     }
     if(controls.count(owner)) {++checks;const auto& box=controls.at(owner);
      if(r.x<box.x || r.y<box.y || r.x+r.w>box.x+box.w || r.y+r.h>box.y+box.h) {++failures;if(failures<20)std::cerr<<"FAIL body/card bounds "<<item.first<<" "<<width<<"x"<<height<<" scale "<<measured<<'\n';}
     }
     if(r.type==OBJ_BUTTON) for(const auto& other:controls) {
      if(other.first<=item.first || other.second.type!=OBJ_BUTTON || other.first=="JPWNC_TEST_UI_OPEN") continue;
      ++checks;if(overlaps(r,other.second)) {++failures;if(failures<20)std::cerr<<"FAIL buttons overlap "<<item.first<<" / "<<other.first<<'\n';}
     }
    }
    for(int i=0;i<5;i++) {
     const string id="JPWNC_TEST_UI_DAILY_"+std::to_string(i);
     if(controls.count(id)) {seen[i]=true;++checks;
      if(labels.at(id).find("…")!=string::npos) {++failures;std::cerr<<"FAIL ellipsis on price row "<<id<<'\n';}
     }
    }
    if(page+1>=g_nocuda_ui_pages) break;
   }
   if(tab==1 && !fallback) for(bool visible:seen) {++checks;if(!visible) {++failures;std::cerr<<"FAIL inaccessible daily result\n";}}
  }
 // Source-linked coexistence: only native HUD rectangle, four corners, no live-value dependency.
 const string companion="JPW_LEV_123456_HUD_BG";
 int coexist_checks=0;
 for(int width:{300,390,800,1440}) for(int height:{260,404,724})
  for(int measured:{12,20,26,32}) for(int corner=0;corner<4;corner++)
   for(int hidden=0;hidden<2;hidden++) for(int pick=0;pick<2;pick++) {
    chart_width=width;chart_height=height;measured_line=measured;v.open=false;v.pick=pick;v.tab=0;
    uint bw=0,bheight=0;TextSetFont("Arial",-80);TextGetSize("Cockpit",bw,bheight);
    const int hw=JPWPanelHUDReservedWidth(width,measured,6,int(bw)+12);
    const int rows=(hidden || 6*(measured+2)+int(bheight)+8+18>height-8 ? 1 : 6);
    const int hh=rows*(measured+2)+int(bheight)+8+18;
    JPWPanelRect actual;
    if(!JPWPanelHUD(width,height,hw,hh,12,corner>=2 ? 40 : std::max(44,measured*3+10),corner==1 || corner==3,corner>=2,actual)) continue;
    Rect hud;hud.type=OBJ_RECTANGLE_LABEL;hud.corner=CORNER_LEFT_UPPER;hud.w=actual.width;hud.h=actual.height;
    hud.x=actual.x;hud.y=actual.y;
    controls[companion]=hud;
    v.status="Marque A · preço sintético 1.10000";JPWNoCudaUIRender("JPWNC_TEST_",v);
    ++checks;++coexist_checks;
    if(!controls.count("JPWNC_TEST_UI_OPEN")) {
     const int margin=JPWUIDesignPx(8),lw=JPWUIDesignButtonWidth("NoCuda · Gráficos",10,true),lh=JPWNoCudaUIButtonHeight();
     bool fits=false;
     // With a single reserved rectangle, a fit exists iff one of its four
     // exterior strips can contain the whole button within the chart margins.
     if(width>=lw+2*margin&&height>=lh+2*margin)
       fits=(hud.x-margin>=lw||width-margin-hud.x-hud.w>=lw||hud.y-margin>=lh||height-margin-hud.y-hud.h>=lh);
     if(fits||g_nocuda_ui_launcher_reason.find("espaço livre insuficiente")==string::npos){++failures;std::cerr<<"FAIL feasible launcher omitted or unavailable reason absent\n";}
     continue;
    }
    const Rect launcher=controls.at("JPWNC_TEST_UI_OPEN");
    ++checks;++coexist_checks;if(JPWNoCudaUILauncherReservationChanged()) {++failures;std::cerr<<"FAIL reservation not remembered\n";}
    // Late attach/remove and move are the only triggers, not financial prose.
    controls[companion].x+=1;++checks;++coexist_checks;if(!JPWNoCudaUILauncherReservationChanged()) ++failures;
    controls[companion]=hud;
    for(const auto& item:controls) if(item.first.find("JPWNC_TEST_UI_")==0) {
     const auto& r=item.second;++checks;++coexist_checks;
     if(overlaps(r,hud) || r.x<0 || r.y<0 || r.x+r.w>width || r.y+r.h>height) {
      ++failures;if(failures<20) std::cerr<<"FAIL companion overlap/bounds "<<item.first<<" "<<width<<"x"<<height<<" font "<<measured<<" corner "<<corner<<"\n";
     }
    }
    // Changing labels/financial-value prose cannot move the reserved launcher.
    for(int tick=0;tick<4;tick++) {
     v.status=tick%2 ? "A · valor diferente 12345.67890" : "A · outro estado mais longo e preço 1.2";
     JPWNoCudaUIRender("JPWNC_TEST_",v);const auto& current=controls.at("JPWNC_TEST_UI_OPEN");
     ++checks;++coexist_checks;if(current.x!=launcher.x || current.y!=launcher.y || current.w!=launcher.w || current.h!=launcher.h) {
      ++failures;std::cerr<<"FAIL launcher moved by live text\n";
     }
    }
   }
 ObjectDelete(0,companion);
 // An absent or unrelated HUD does not reserve space.
 chart_width=390;chart_height=404;measured_line=12;v.open=false;v.pick=0;
 JPWNoCudaUIRender("JPWNC_TEST_",v);++checks;++coexist_checks;
 const auto standalone=controls.at("JPWNC_TEST_UI_OPEN");
 if(standalone.x!=JPWUIDesignPx(12) || standalone.y!=chart_height-JPWNoCudaUIButtonHeight()-JPWUIDesignPx(12)) ++failures;
 // Panel-height fallback keeps access and never overlays a companion HUD.
 controls[companion]={};controls[companion].type=OBJ_RECTANGLE_LABEL;controls[companion].w=366;controls[companion].h=90;
 controls[companion].x=12;controls[companion].y=130;chart_width=390;chart_height=260;measured_line=32;v.open=true;v.pick=1;
 JPWNoCudaUIRender("JPWNC_TEST_",v);++checks;++coexist_checks;
 if(controls.count("JPWNC_TEST_UI_OPEN")){if(overlaps(controls.at("JPWNC_TEST_UI_OPEN"),controls.at(companion))) ++failures;}else if(g_nocuda_ui_launcher_reason.empty()) ++failures;
 ObjectDelete(0,companion);++checks;++coexist_checks;if(!JPWNoCudaUILauncherReservationChanged()) ++failures;
 // No physically available area produces an explicit reason, not silent disappearance.
 chart_width=100;chart_height=90;measured_line=32;controls[companion]={};controls[companion].type=OBJ_RECTANGLE_LABEL;
 controls[companion].w=100;controls[companion].h=90;v.open=false;v.pick=0;
 JPWNoCudaUIRender("JPWNC_TEST_",v);++checks;++coexist_checks;
 if(controls.count("JPWNC_TEST_UI_OPEN") || g_nocuda_ui_launcher_reason.empty()) ++failures;
 ObjectDelete(0,companion);v.open=true;v.pick=0;
 std::cout<<"HOST_NOCUDA_COCKPIT_COEXISTENCE: "<<coexist_checks<<" reserved-HUD, DPI, resize and live-text stability checks\n";
 // Existing fields survive same-page updates; resize follows the focused edit.
 chart_width=980;chart_height=724;measured_line=12;background=0xffffff;v.tab=0;v.page=99;
 JPWNoCudaUIRender("JPWNC_TEST_",v);
 g_nocuda_ui_editing="JPWNC_TEST_UI_JUST";
 ObjectSetString(0,g_nocuda_ui_editing,OBJPROP_TEXT,"rascunho ainda digitado");
 JPWNoCudaReadJustification();++checks;
 if(g_nocuda_justification!="rascunho ainda digitado") ++failures;
 const int created=creates,deleted=deletes;
 JPWNoCudaUIRender("JPWNC_TEST_",v);++checks;
 if(creates!=created || deletes!=deleted || ObjectGetString(0,g_nocuda_ui_editing,OBJPROP_TEXT)!="rascunho ainda digitado") {++failures;std::cerr<<"FAIL draft object recreate/loss\n";}
 chart_width=390;v.page=0;JPWNoCudaUIRender("JPWNC_TEST_",v);++checks;
 if(!controls.count("JPWNC_TEST_UI_JUST") || ObjectGetString(0,"JPWNC_TEST_UI_JUST",OBJPROP_TEXT)!="rascunho ainda digitado") {++failures;std::cerr<<"FAIL resize draft edit loss\n";}
 g_nocuda_ui_editing="";v.tab=1;v.measure_page=0;chart_width=980;chart_height=724;
 JPWNoCudaUIRender("JPWNC_TEST_",v);g_nocuda_ui_editing="JPWNC_TEST_UI_DATE";
 ObjectSetString(0,g_nocuda_ui_editing,OBJPROP_TEXT,"2026.10.12");
 JPWNoCudaReadJustification();++checks;
 if(g_nocuda_date!="2026.10.12") ++failures;
 v.date=g_nocuda_date; // current controller projection after the real capture
 chart_height=424;measured_line=26;JPWNoCudaUIRender("JPWNC_TEST_",v);++checks;
 if(controls.count("JPWNC_TEST_UI_DATE")){
  if(ObjectGetString(0,"JPWNC_TEST_UI_DATE",OBJPROP_TEXT)!="2026.10.12"){++failures;std::cerr<<"FAIL resize date edit loss\n";}
 }else if(g_nocuda_date!="2026.10.12"||g_nocuda_ui_editing!=""||!controls.count("JPWNC_TEST_UI_OPEN")){++failures;std::cerr<<"FAIL unavailable resize loses date or leaves dangling edit\n";}
 chart_height=724;v.measure_page=1;JPWNoCudaUIRender("JPWNC_TEST_",v);++checks;
 if(!controls.count("JPWNC_TEST_UI_DATE")||ObjectGetString(0,"JPWNC_TEST_UI_DATE",OBJPROP_TEXT)!="2026.10.12"){++failures;std::cerr<<"FAIL resized date does not return intact\n";}
 g_nocuda_ui_editing="";
 if(const char* directory=std::getenv("JPW_NOCUDA_VISUAL_DIR")) {
  for(int width:{960,390}) for(int measured:{12,32}) {
   chart_width=width;chart_height=724;measured_line=measured;background=0xffffff;v.open=false;v.pick=1;v.status="Marque A · fechamento de barra encerrada";
   uint bw=0,bheight=0;TextSetFont("Arial",-80);TextGetSize("Cockpit",bw,bheight);
   Rect hud;hud.type=OBJ_RECTANGLE_LABEL;hud.corner=0;hud.x=12;hud.w=JPWPanelHUDReservedWidth(width,measured,6,int(bw)+12);
   hud.h=6*(measured+2)+int(bheight)+8+18;hud.y=chart_height-40-hud.h;controls[companion]=hud;
   JPWNoCudaUIRender("JPWNC_TEST_",v);export_objects(string(directory)+"/coexist-lower-left-"+std::to_string(width)+"-"+std::to_string(measured)+".json");
   ObjectDelete(0,companion);
  }
  v.open=true;v.pick=0;
  for(int width:{960,390}) for(int dark:{0,1}) for(int tab=0;tab<3;tab++) {
   chart_width=width;chart_height=724;measured_line=12;background=dark ? 0x101010 : 0xffffff;
   v.tab=tab;v.page=0;v.measure_page=(tab==1 ? 1 : 0);
   JPWNoCudaUIRender("JPWNC_TEST_",v);
   export_objects(string(directory)+"/nocuda-"+std::to_string(tab)+"-"+std::to_string(width)+(dark ? "-dark.json" : "-light.json"));
  }
 }
 std::cout<<"HOST_NOCUDA_UI_GEOMETRY: "<<(checks-failures)<<"/"<<checks<<" measured bounds, button, full-price and field-preservation checks\n";
 std::cout<<"NATIVE_MT5: NOT_RUN; simulated font metrics do not prove DPI rendering\n";
 return failures ? 1 : 0;
}
'''


SIGNATURE_SHIM = r'''
#include <algorithm>
#include <cmath>
#include <cstdint>
#include <cstdio>
#include <iostream>
#include <string>
#include <vector>
using string = std::string;
using datetime = long long;
using ENUM_TIMEFRAMES = int;
using uchar = unsigned char;
constexpr int PERIOD_H1=16385, PERIOD_D1=16408;
constexpr int WHOLE_ARRAY=-1, CP_UTF8=65001, CRYPT_HASH_SHA256=1;
struct MqlRates { datetime time; double close; };
std::vector<MqlRates> synthetic_bars = {
  {3600,1.1000},{7200,1.1010},{10800,1.1020},{14400,1.1030},
  {100000,1.1040}
};
datetime MathMin(datetime a,datetime b) { return std::min(a,b); }
datetime MathMax(datetime a,datetime b) { return std::max(a,b); }
bool MathIsValidNumber(double value) { return std::isfinite(value); }
int CopyRates(const string&,int tf,datetime first,datetime last,
              std::vector<MqlRates>& out) {
  out.clear();
  if (tf!=PERIOD_H1) return 0;
  for (const auto& bar : synthetic_bars)
    if (bar.time>=first && bar.time<=last) out.push_back(bar);
  return int(out.size());
}
template<typename T> int ArraySize(const std::vector<T>& data) {
  return int(data.size());
}
int ArrayResize(std::vector<uchar>& data,int size) {
  data.resize(size); return int(data.size());
}
string StringFormat(const char*,long opened,double closed) {
  char buffer[128];
  std::snprintf(buffer,sizeof(buffer),"%lld|%.17g;",
                static_cast<long long>(opened),closed);
  return buffer;
}
string StringFormat(const char*,int value) {
  char buffer[8];
  std::snprintf(buffer,sizeof(buffer),"%02x",value);
  return buffer;
}
int StringToCharArray(const string& value,std::vector<uchar>& out,
                      int,int,int) {
  out.assign(value.begin(),value.end());
  out.push_back(0);
  return int(out.size());
}
int CryptEncode(int algorithm,const std::vector<uchar>& source,
                const std::vector<uchar>&,std::vector<uchar>& digest) {
  if (algorithm!=CRYPT_HASH_SHA256) return 0;
  // Deterministic host stand-in: tests source canonicalization and change
  // detection; MT5's SHA-256 primitive itself is not executed here.
  std::uint64_t states[4]={
    14695981039346656037ULL,1099511628211ULL,
    7809847782465536322ULL,1609587929392839161ULL
  };
  for (const auto value : source)
    for (int i=0;i<4;i++) {
      states[i]^=std::uint64_t(value)+std::uint64_t(i*37);
      states[i]*=1099511628211ULL;
    }
  digest.resize(32);
  for (int i=0;i<4;i++)
    for (int byte=0;byte<8;byte++)
      digest[i*8+byte]=uchar(states[i]>>(byte*8));
  return 32;
}
int failures=0;
void check(bool truth,const char* label) {
  if (!truth) { ++failures; std::cerr << "FAIL: " << label << '\n'; }
}
'''


SIGNATURE_CASES = r'''
int main() {
  datetime first=0,last=0;
  int count=0;
  string signature,reason;
  const string symbol="EURUSD.synthetic";
  check(JPWNoCudaSourceSignature(symbol,PERIOD_H1,7200,10800,14400,
        first,last,count,signature,reason) &&
        first==7200 && last==14400 && count==3 && signature.size()==64,
        "exact source span and bar count are signed");
  const string original=signature;
  synthetic_bars[2].close=1.2020;
  check(JPWNoCudaSourceSignature(symbol,PERIOD_H1,7200,10800,14400,
        first,last,count,signature,reason) && signature!=original && count==3,
        "corrected interior Close changes source signature");
  synthetic_bars[2].close=1.1020;
  synthetic_bars.insert(synthetic_bars.begin()+2,{9000,1.1015});
  check(JPWNoCudaSourceSignature(symbol,PERIOD_H1,7200,10800,14400,
        first,last,count,signature,reason) && signature!=original && count==4,
        "inserted source bar changes count and signature");
  synthetic_bars.erase(synthetic_bars.begin()+2);
  synthetic_bars.erase(synthetic_bars.begin()+1);
  check(!JPWNoCudaSourceSignature(symbol,PERIOD_H1,7200,10800,14400,
        first,last,count,signature,reason),
        "missing first anchor bar fails closed");
  synthetic_bars.insert(synthetic_bars.begin()+1,{7200,1.1010});
  synthetic_bars[2].close=0.0;
  check(!JPWNoCudaSourceSignature(symbol,PERIOD_H1,7200,10800,14400,
        first,last,count,signature,reason),
        "invalid interior Close fails closed");
  synthetic_bars[2].close=1.1020;
  check(!JPWNoCudaSourceSignature(symbol,PERIOD_D1,7200,10800,14400,
        first,last,count,signature,reason),
        "history lookup cannot silently switch source timeframe");
  std::cout << "HOST_NOCUDA_SIGNATURE: " << (6-failures) << "/6 PASS"
            << " (deterministic crypto stand-in)\n";
  return failures ? 1 : 0;
}
'''


PROJECTION_SHIM = r'''
#include <cmath>
#include <iostream>
#include <string>
using string = std::string;
bool MathIsValidNumber(double value) { return std::isfinite(value); }
double MathAbs(double value) { return std::abs(value); }
int failures=0;
void check(bool truth,const char* label) {
  if (!truth) { ++failures; std::cerr << "FAIL: " << label << '\n'; }
}
'''


INPUT_SHIM = r"""
#include <cmath>
#include <ctime>
#include <iomanip>
#include <iostream>
#include <sstream>
#include <string>
using string=std::string;
using datetime=long long;
using ushort=unsigned short;
constexpr int TIME_DATE=1;
int g_nocuda_level=36,clears=0,saves=0,checks=0,failures=0;
void JPWNoCudaClearDaily() { ++clears; }
void JPWNoCudaSaveChartState() { ++saves; }
int StringLen(const string& s) { return int(s.size()); }
ushort StringGetCharacter(const string& s,int i) { return ushort(s.at(i)); }
void StringTrimLeft(string& s) { const auto n=s.find_first_not_of(" \t\n"); s=n==string::npos ? "" : s.substr(n); }
void StringTrimRight(string& s) { const auto n=s.find_last_not_of(" \t\n"); if(n==string::npos) s=""; else s.resize(n+1); }
void StringReplace(string& s,const string& a,const string& b) { const auto at=s.find(a); if(at!=string::npos) s.replace(at,a.size(),b); }
bool MathIsValidNumber(double v) { return std::isfinite(v); }
double MathAbs(double v) { return std::abs(v); }
double MathRound(double v) { return std::round(v); }
double StringToDouble(const string& s) { try { return std::stod(s); } catch(...) { return 0; } }
datetime StringToTime(const string& s) {
  std::tm civil{}; std::istringstream in(s); in>>std::get_time(&civil,"%Y.%m.%d %H:%M");
  if(in.fail()) return 0; return timegm(&civil);
}
string TimeToString(datetime value,int) {
  const std::time_t at=value; const auto tm=std::gmtime(&at); char out[32];
  std::strftime(out,sizeof(out),"%Y.%m.%d",tm); return out;
}
void check(bool ok,const char* label) { ++checks; if(!ok) { ++failures;std::cerr<<"FAIL: "<<label<<'\n'; } }
"""

INPUT_CASES = r"""
int main() {
  datetime day=0;
  check(JPWNoCudaDateValue("2026.09.30",day) && TimeToString(day,TIME_DATE)=="2026.09.30","server date accepted exactly");
  check(JPWNoCudaDateValue("2028.02.29",day),"valid leap date");
  for(const string bad : {"2026.02.29","2026.04.31","2026.13.01","2026.00.01","2026.09.00","2026.09.30junk","2026.9.30"," 2026.09.30","2026.09.30 12:00","","junk"})
    check(!JPWNoCudaDateValue(bad,day) && day==0,"invalid or normalized date rejected");
  for(int k=0;k<65;k++) {
    std::ostringstream value; value<<std::fixed<<std::setprecision(3)<<(-4.0+k/8.0);
    check(JPWNoCudaSelectLevelText(value.str()) && g_nocuda_level==k,"each of65 grid levels selectable");
  }
  check(JPWNoCudaSelectLevelText("+0,125") && g_nocuda_level==33,"comma decimal and explicit plus accepted");
  for(const string bad : {"nan","inf","junk","1e9","-4.125","4.125","0.1",".","-","++1","0..5","0,0.5",""}) {
    const int before=g_nocuda_level,before_clears=clears,before_saves=saves;
    check(!JPWNoCudaSelectLevelText(bad) && g_nocuda_level==before && clears==before_clears && saves==before_saves,
          "invalid level leaves selected level and state unchanged");
  }
  std::cout<<"HOST_NOCUDA_INPUTS: "<<(checks-failures)<<"/"<<checks<<" PASS\n";
  return failures ? 1 : 0;
}
"""

REFERENCE_SHIM = r"""
#include <algorithm>
#include <cmath>
#include <iostream>
#include <string>
#include <vector>
using string=std::string;
using datetime=long long;
using color=int;
constexpr int CHART_WIDTH_IN_PIXELS=1,CHART_HEIGHT_IN_PIXELS=2,CHART_COLOR_BACKGROUND=3;
int mode=0,measured_label=20,checks=0,failures=0;
std::vector<string> owned;
constexpr datetime DAY=86400;
long long ChartGetInteger(int,int property) { return property==1 ? 640 : property==2 ? 480 : 0xffffff; }
int MathMax(int a,int b) { return std::max(a,b); }
double MathAbs(double v) { return std::abs(v); }
bool MathIsValidNumber(double v) { return std::isfinite(v); }
bool TextSetFont(const string&,int) { return true; }
bool TextGetSize(const string&,unsigned int& width,unsigned int& height) { width=measured_label;height=12;return true; }
int ObjectsTotal(int,int,int) { return int(owned.size()); }
string ObjectName(int,int index,int,int) { return owned.at(index); }
int StringFind(const string& value,const string& what) { const auto at=value.find(what);return at==string::npos ? -1 : int(at); }
bool ObjectDelete(int,const string& name) { const auto at=std::find(owned.begin(),owned.end(),name);if(at!=owned.end()) owned.erase(at);return true; }
bool ChartTimePriceToXY(int,int,datetime at,double,int& x,int& y) {
  const int i=int((at-DAY)/43200); x=100+i*120; y=100+i*40;
  if(mode==1) x=100;
  if(mode==2) x=100+i*10;
  if(mode==3) x=340-i*120;
  if(mode==7) x=700;
  return true;
}
bool ChartXYToTimePrice(int,int x,int y,int& sub,datetime& at,double& price) {
  int i=int((x-100)/120);
  if(mode==1 || mode==2) i=int((y-100)/40);
  if(mode==3) i=int((340-x)/120);
  sub=(mode==6 ? 1 : 0); at=DAY+i*43200+(mode==4 ? 3600 : 0);
  price=1.1+i*.1+(y-(100+i*40))*.001+(mode==5 ? .01 : 0);
  return true;
}
void JPWNoCudaDrawMilestone(const string& prefix,const string& id,datetime,double,color) {
  owned.push_back(prefix+"DRAW_LABEL_"+id);
}
void check(bool ok,const char* label) { ++checks;if(!ok) { ++failures;std::cerr<<"FAIL: "<<label<<'\n'; } }
"""

REFERENCE_CASES = r"""
int main() {
  JPWNoCudaDailyResult daily{};
  daily.valid=true;daily.day=DAY;daily.start_price=1.1;daily.mid_price=1.2;daily.end_price=1.3;
  string reason;
  check(JPWNoCudaDrawDailyReferences("OWN_",daily,reason) && owned.size()==3,"exact three reference dates accepted");
  for(int failure : {1,2,3,4,5,6,7}) {
    mode=failure;
    check(!JPWNoCudaDrawDailyReferences("OWN_",daily,reason) && owned.empty(),
          "collapsed close reversed stale price shifted or offscreen dates refuse all marks");
  }
  mode=0;measured_label=130;
  check(!JPWNoCudaDrawDailyReferences("OWN_",daily,reason),"highDPI label collision refuses menu-only projection");
  measured_label=20;daily.valid=false;
  check(!JPWNoCudaDrawDailyReferences("OWN_",daily,reason) && owned.empty(),"unavailable daily query has no marks");
  owned={"FOREIGN_DRAW_LABEL_REF_00h","OWN_DRAW_LABEL_REF_00h"};
  JPWNoCudaRemoveDailyReferences("OWN_");
  check(owned.size()==1 && owned[0]=="FOREIGN_DRAW_LABEL_REF_00h","cleanup respects marker ownership");
  std::cout<<"HOST_NOCUDA_REFERENCE_PIXELS: "<<(checks-failures)<<"/"<<checks<<" PASS\n";
  return failures ? 1 : 0;
}
"""


REVALIDATE_SHIM = r"""
#include <iostream>
#include <string>
using string=std::string;
using datetime=long long;
using ulong=unsigned long;
ulong mock_ms=6000,g_nocuda_daily_checked_ms=0;
bool g_nocuda_geometry_valid=true,g_nocuda_history_diverged=false,g_nocuda_show_refs=true;
int g_nocuda_level=36,g_nocuda_source_tf=16385;
datetime g_nocuda_a_open=86400;
string g_nocuda_prefix="OWN_",g_nocuda_symbol="EURUSD.synthetic",g_nocuda_reference_reason;
int refreshes=0,reads=0,removed=0,checks=0,failures=0;
ulong GetTickCount64() { return mock_ms; }
void JPWNoCudaRefreshGeometry() { ++refreshes; }
void JPWNoCudaRemoveDailyReferences(const string&) { ++removed; }
void check(bool ok,const char* label) { ++checks;if(!ok) { ++failures;std::cerr<<"FAIL: "<<label<<'\n'; } }
"""

REVALIDATE_CASES = r"""
void populate(bool no_session=false) {
  JPWNoCudaDailyClear(g_nocuda_daily);
  g_nocuda_daily.valid=!no_session;g_nocuda_daily.no_session=no_session;
  g_nocuda_daily.day=86400;g_nocuda_daily.generated=100;
  g_nocuda_daily.estimated=true;
  g_nocuda_daily.start_price=1.1;g_nocuda_daily.mid_price=1.2;g_nocuda_daily.end_price=1.3;
  g_nocuda_daily.mean_price=1.2;g_nocuda_daily.min_price=1.1;g_nocuda_daily.max_price=1.3;
  g_nocuda_daily.source="syntheticweekly";g_nocuda_daily.source_signature="timeline-A";
  answer=g_nocuda_daily;answer.generated=200;
  g_nocuda_daily_checked_ms=0;g_nocuda_show_refs=true;
}
int main() {
  populate();
  check(JPWNoCudaRevalidateDaily() && reads==1 && g_nocuda_daily.generated==100,
        "same coherent source keeps original query time and accepted values");
  mock_ms++;
  check(JPWNoCudaRevalidateDaily() && reads==1 && refreshes==1,"five second cadence prevents redundant reads");
  mock_ms+=6000;answer.source_signature="timeline-B";
  check(!JPWNoCudaRevalidateDaily() && !g_nocuda_daily.valid && !g_nocuda_show_refs &&
        g_nocuda_daily.start_price==0 && removed==1,"history correction beyondanchors clears query and marks even when prices unchanged");
  populate();mock_ms+=6000;answer.valid=false;answer.no_session=false;
  check(!JPWNoCudaRevalidateDaily() && !g_nocuda_daily.valid,"read failure cannot retain old query as valid");
  populate(true);mock_ms+=6000;
  check(JPWNoCudaRevalidateDaily() && g_nocuda_daily.no_session,
        "closed day is revalidated even without numeric values");
  mock_ms+=6000;answer.source_signature="calendar-change";
  check(!JPWNoCudaRevalidateDaily() && !g_nocuda_daily.no_session,"closed-day metadata change invalidates previous no-session result");
  populate();mock_ms+=6000;g_nocuda_geometry_valid=false;
  const int before=reads;
  check(!JPWNoCudaRevalidateDaily() && reads==before,"missinggeometry never recalculates oldcontext");
  std::cout<<"HOST_NOCUDA_QUERY_REVALIDATION: "<<(checks-failures)<<"/"<<checks<<" PASS\n";
  return failures ? 1 : 0;
}
"""


class NoCudaIntegration(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.terminal = TERMINAL.read_text(encoding="utf-8")
        cls.core = CORE.read_text(encoding="utf-8")
        cls.render = RENDER.read_text(encoding="utf-8")
        cls.ui = UI.read_text(encoding="utf-8")
        cls.store = STORE.read_text(encoding="utf-8")
        cls.indicator = INDICATOR.read_text(encoding="utf-8")
        cls.projection_core = PROJECTION_CORE.read_text(encoding="utf-8")

    def test_source_candle_adapter_host(self) -> None:
        compiler = shutil.which("clang++") or shutil.which("g++")
        if compiler is None:
            self.fail("ENVIRONMENT_ERROR: no host C++ compiler")
        production = "\n".join(function(self.terminal, name) for name in
                               ("JPWNoCudaSnapCloseAtTime",
                                "JPWNoCudaClickedClose", "JPWNoCudaExactBar"))
        geometry_type=re.search(r"struct\s+JPWNoCudaGeometry\s*\{.*?\};", self.core, re.S).group(0)
        production = geometry_type + "\n" + "\n".join(function(self.core,n) for n in
            ("JPWNoCudaClearGeometry","JPWNoCudaBuildGeometry")) + "\n" + production
        production += "\n" + function(self.indicator,"JPWNoCudaSetDraftAnchor")
        production += "\n" + function(self.indicator, "JPWNoCudaDragAnchor")
        production += "\n" + function(self.indicator,"JPWNoCudaPanelContains")
        production += "\n" + function(self.indicator,"JPWNoCudaPickAt")
        with tempfile.TemporaryDirectory(prefix="jpw-nocuda-adapter-") as temp:
            source = Path(temp) / "adapter.cpp"
            binary = Path(temp) / "adapter"
            source.write_text(HOST_SHIM + production + HOST_CASES,
                              encoding="utf-8")
            compile_result = subprocess.run(
                [compiler, "-std=c++17", "-Wall", "-Wextra", "-Werror",
                 str(source), "-o", str(binary)],
                text=True, capture_output=True, timeout=60, check=False)
            self.assertEqual(compile_result.returncode, 0,
                             compile_result.stderr or compile_result.stdout)
            result = subprocess.run([str(binary)], text=True,
                                    capture_output=True, timeout=60,
                                    check=False)
            self.assertEqual(result.returncode, 0,
                             result.stderr or result.stdout)
            print(result.stdout, end="")

    def test_controller_actions_host(self) -> None:
        compiler = shutil.which("clang++") or shutil.which("g++")
        if compiler is None:
            self.fail("ENVIRONMENT_ERROR: no host C++ compiler")
        production = "\n".join(function(self.indicator, name) for name in
                               ("JPWNoCudaChartInteraction", "JPWNoCudaSameClick", "JPWNoCudaObjectClick",
                                "JPWNoCudaFlushChartClick", "JPWNoCudaChartClick",
                                "JPWNoCudaAction", "OnChartEvent"))
        with tempfile.TemporaryDirectory(prefix="jpw-nocuda-actions-") as temp:
            source = Path(temp) / "actions.cpp"
            binary = Path(temp) / "actions"
            focus=(UI.parent/"JPW_UI_Focus.mqh").read_text()
            source.write_text(ACTION_SHIM + focus + production + ACTION_CASES,
                              encoding="utf-8")
            compile_result = subprocess.run(
                [compiler, "-std=c++17", "-Wall", "-Wextra", "-Werror",
                 str(source), "-o", str(binary)], text=True,
                capture_output=True, timeout=60, check=False)
            self.assertEqual(compile_result.returncode, 0,
                             compile_result.stderr or compile_result.stdout)
            result = subprocess.run([str(binary)], text=True,
                                    capture_output=True, timeout=60,
                                    check=False)
            self.assertEqual(result.returncode, 0,
                             result.stderr or result.stdout)
            print(result.stdout, end="")

    def compile_behavior(self, prefix: str, shim: str, production: str, cases: str) -> None:
        compiler=shutil.which("clang++") or shutil.which("g++")
        self.assertIsNotNone(compiler,"ENVIRONMENT_ERROR: no host C++ compiler")
        with tempfile.TemporaryDirectory(prefix=prefix) as temp:
            source=Path(temp)/"behavior.cpp"; binary=Path(temp)/"behavior"
            source.write_text(shim+production+cases,encoding="utf-8")
            result=subprocess.run([compiler,"-std=c++17","-Wall","-Wextra","-Werror",str(source),"-o",str(binary)],
                                  capture_output=True,text=True,timeout=60,check=False)
            self.assertEqual(result.returncode,0,result.stderr or result.stdout)
            result=subprocess.run([str(binary)],capture_output=True,text=True,timeout=60,check=False)
            self.assertEqual(result.returncode,0,result.stderr or result.stdout)
            print(result.stdout,end="")

    def test_strict_date_and_all65_level_inputs_host(self) -> None:
        production="\n".join((function(self.core,"JPWNoCudaLevelValue"),
            function(self.indicator,"JPWNoCudaDateValue"),
            function(self.indicator,"JPWNoCudaSelectLevelText")))
        self.compile_behavior("jpw-nocuda-inputs-",INPUT_SHIM,production,INPUT_CASES)

    def test_reference_roundtrip_ownership_and_spacing_host(self) -> None:
        daily=re.search(r"struct\s+JPWNoCudaDailyResult\s*\{.*?\};",self.projection_core,re.S).group(0)
        production=daily+"\n"+"\n".join(function(self.render,name) for name in
            ("JPWNoCudaRemoveDailyReferences","JPWNoCudaReferencePoint","JPWNoCudaDrawDailyReferences"))
        production=re.sub(r"C'[^']+'","0",production)
        self.compile_behavior("jpw-nocuda-reference-",REFERENCE_SHIM,production,REFERENCE_CASES)

    def test_query_revalidation_on_history_or_session_change_host(self) -> None:
        types="\n".join(re.search(r"struct\s+"+name+r"\s*\{.*?\};",source,re.S).group(0)
                           for name,source in (("JPWNoCudaGeometry",self.core),
                                              ("JPWNoCudaDailyResult",self.projection_core)))
        production=types+"\n"+function(self.projection_core,"JPWNoCudaDailyClear")
        production+="\nJPWNoCudaDailyResult g_nocuda_daily,answer; JPWNoCudaGeometry g_nocuda_geometry;\n"
        production+="bool JPWNoCudaProjectDay(const string&,int,datetime,const JPWNoCudaGeometry&,double,datetime,JPWNoCudaDailyResult& out) { ++reads;out=answer;return out.valid; }\n"
        production+="\n"+function(self.core,"JPWNoCudaLevelValue")
        production+="\n"+function(self.indicator,"JPWNoCudaClearDaily")
        production+="\n"+function(self.indicator,"JPWNoCudaRevalidateDaily")
        self.compile_behavior("jpw-nocuda-revalidation-",REVALIDATE_SHIM,production,REVALIDATE_CASES)

    def test_transient_query_has_no_store_write_path(self) -> None:
        for name in ("JPWNoCudaClearDaily","JPWNoCudaConsultDay","JPWNoCudaRevalidateDaily"):
            self.assertNotRegex(function(self.indicator,name),r"DatabaseExecute|FileWrite|StoreConfirm|StoreInsertRevision|SaveChartState")
        refresh=function(self.indicator,"JPWNoCudaRefreshGeometry")
        self.assertIn("JPWNoCudaClearDaily()",refresh)
        for name in ("JPWNoCudaUseRecord","JPWNoCudaClearAnchors","JPWNoCudaCancelDraft","JPWNoCudaSetDraftAnchor"):
            self.assertIn("JPWNoCudaClearDaily()",function(self.indicator,name))
        timer=function(self.indicator,"OnTimer")
        self.assertIn("if(source_bar!=g_nocuda_last_bar) JPWNoCudaClearDaily()",timer)
        self.assertIn("JPWNoCudaRevalidateDaily()",timer)

    def test_pending_anchor_pick_requires_timer(self) -> None:
        self.assertIn("JPWNoCudaFlushChartClick();", function(self.indicator,
                                                           "OnTimer"))
        init = function(self.indicator, "OnInit")
        self.assertRegex(init, r"if\(!EventSetTimer\(1\)\)\s*\{")
        self.assertIn("return(INIT_FAILED)", init)

    def test_source_signature_host(self) -> None:
        compiler = shutil.which("clang++") or shutil.which("g++")
        if compiler is None:
            self.fail("ENVIRONMENT_ERROR: no host C++ compiler")
        production = function(self.terminal, "JPWNoCudaSourceSignature")
        production = production.replace("MqlRates bars[];",
                                        "std::vector<MqlRates> bars;")
        production = production.replace(
            "uchar source[]; uchar key[]; uchar digest[];",
            "std::vector<uchar> source,key,digest;")
        with tempfile.TemporaryDirectory(prefix="jpw-nocuda-signature-") as temp:
            source = Path(temp) / "signature.cpp"
            binary = Path(temp) / "signature"
            source.write_text(SIGNATURE_SHIM + production + SIGNATURE_CASES,
                              encoding="utf-8")
            compile_result = subprocess.run(
                [compiler, "-std=c++17", "-Wall", "-Wextra", "-Werror",
                 str(source), "-o", str(binary)], text=True,
                capture_output=True, timeout=60, check=False)
            self.assertEqual(compile_result.returncode, 0,
                             compile_result.stderr or compile_result.stdout)
            result = subprocess.run([str(binary)], text=True,
                                    capture_output=True, timeout=60,
                                    check=False)
            self.assertEqual(result.returncode, 0,
                             result.stderr or result.stdout)
            print(result.stdout, end="")

    def test_source_bar_projection_survives_chart_timeframe_and_decimation(self) -> None:
        compiler = shutil.which("clang++") or shutil.which("g++")
        if compiler is None:
            self.fail("ENVIRONMENT_ERROR: no host C++ compiler")
        geometry_type = re.search(r"\bstruct\s+JPWNoCudaGeometry\s*\{.*?\};",
                                  self.core, flags=re.DOTALL)
        self.assertIsNotNone(geometry_type)
        paint = function(self.render, "JPWNoCudaCanvasPaint")
        self.assertIn("JPWNoCudaProjectionLoadTimeline(symbol,source_tf,a_open,",paint)
        self.assertIn("JPWNoCudaProjectionResolveValidated(timeline.opens,timeline.observed_count,",paint)
        decimate_match = re.search(r"if\(x0==last_drawn_x && i<total-1\)"
                                   r"\s*continue;", paint)
        self.assertIsNotNone(decimate_match)
        self.assertLess(paint.index("JPWNoCudaPriceAt(geometry,0.0,"),
                        decimate_match.start(),
                        "same-pixel culling must follow source-bar calculation")
        self.assertLess(paint.index("if(x0>=0 && x0<width) last_visible=i"),
                        decimate_match.start(),
                        "culling cannot change the last visible source bar")
        production = "\n".join((geometry_type.group(0),
                                function(self.core, "JPWNoCudaClearGeometry"),
                                function(self.core, "JPWNoCudaBuildGeometry"),
                                function(self.core, "JPWNoCudaPriceAt")))
        for name in ("JPWNoCudaTimePoint","JPWNoCudaProjectionSession"):
            production += "\n"+re.search(r"struct\s+"+name+r"\s*\{.*?\};",self.projection_core,re.S).group(0)
        production += "\n"+"\n".join(function(self.projection_core,name) for name in
            ("JPWNoCudaTimePointClear","JPWNoCudaProjectionSessionContains",
             "JPWNoCudaSourceOpeningOrdinal","JPWNoCudaProjectionFloorOpening",
             "JPWNoCudaProjectionResolveValidated"))
        production=production.replace("const datetime &opens[]","const std::vector<datetime>& opens")
        production=production.replace("JPWNoCudaProjectionSession &sessions[]","std::vector<JPWNoCudaProjectionSession>& sessions")
        decimate = decimate_match.group(0).replace("continue;", "return false;")
        cases = f'''
int main() {{
  JPWNoCudaGeometry geometry;
  string reason;
  check(JPWNoCudaBuildGeometry(5,1.1000,9,1.1020,7,1.1050,
                              geometry,reason),"synthetic H1 source geometry");
  const int anchor_shift=10;
  std::vector<datetime> opens;
  for(int i=0;i<21;i++) opens.push_back((i+1)*3600);
  std::vector<JPWNoCudaProjectionSession> sessions;
  auto ordinal_for=[&](int first_shift,int i)->double {{
    JPWNoCudaTimePoint point;
    const datetime a=opens[opens.size()-1-anchor_shift];
    const datetime at=opens[opens.size()-1-(first_shift-i)];
    if(!JPWNoCudaProjectionResolveValidated(opens,int(opens.size()),a,geometry,
        0.0,at,3600,sessions,false,point,reason)) return -999;
    return point.ordinal;
  }};
  const long on_h1_chart=ordinal_for(12,5); // source shift = 7
  const long on_m15_chart=ordinal_for(9,2); // same source shift = 7
  check(on_h1_chart==8 && on_m15_chart==8,
        "H1 and M15 viewports keep the same source ordinal");
  double h1_price=0,m15_price=0;
  check(JPWNoCudaPriceAt(geometry,0.5,(double)on_h1_chart,h1_price) &&
        JPWNoCudaPriceAt(geometry,0.5,(double)on_m15_chart,m15_price) &&
        std::abs(h1_price-m15_price)<1e-12 &&
        std::abs(h1_price-1.1035)<1e-12,
        "same source timestamp projects to the same price on both charts");
  auto should_draw=[](int x0,int last_drawn_x,int i,int total)->bool {{
    {decimate}
    return true;
  }};
  check(!should_draw(42,42,1,4) && should_draw(42,42,3,4),
        "same-pixel culling skips intermediate vertex but keeps final vertex");
  double price_before_skip=0;
  check(JPWNoCudaPriceAt(geometry,0.5,(double)on_h1_chart,
                             price_before_skip) &&
        !should_draw(42,42,1,4) &&
        std::abs(price_before_skip-h1_price)<1e-12,
        "display culling does not alter calculated source-bar price");
  std::cout << "HOST_NOCUDA_PROJECTION: " << (4-failures)
            << "/4 PASS (H1 source on H1/M15 viewports)\\n";
  return failures ? 1 : 0;
}}
'''
        with tempfile.TemporaryDirectory(prefix="jpw-nocuda-projection-") as temp:
            source = Path(temp) / "projection.cpp"
            binary = Path(temp) / "projection"
            source.write_text(PROJECTION_SHIM + "\n#include <vector>\nusing datetime=long long;\ntemplate<typename T> int ArraySize(const std::vector<T>& values) { return int(values.size()); }\n" + production + cases,
                              encoding="utf-8")
            compile_result = subprocess.run(
                [compiler, "-std=c++17", "-Wall", "-Wextra", "-Werror",
                 str(source), "-o", str(binary)], text=True,
                capture_output=True, timeout=60, check=False)
            self.assertEqual(compile_result.returncode, 0,
                             compile_result.stderr or compile_result.stdout)
            result = subprocess.run([str(binary)], text=True,
                                    capture_output=True, timeout=60,
                                    check=False)
            self.assertEqual(result.returncode, 0,
                             result.stderr or result.stdout)
            print(result.stdout, end="")

    def test_compact_chart_controls_do_not_overlap(self) -> None:
        compiler = shutil.which("clang++") or shutil.which("g++")
        if compiler is None:
            self.fail("ENVIRONMENT_ERROR: no host C++ compiler")
        view_match = re.search(r"\bstruct\s+JPWNoCudaUIView\s*\{.*?\};",
                               self.ui, flags=re.DOTALL)
        self.assertIsNotNone(view_match)
        production = expanded_source(UI)
        production = re.sub(r'^#(?:if.*|endif.*|resource.*)\n', '', production, flags=re.MULTILINE)
        production = re.sub(r'^#define\s+(JPW_NOCUDA_UI_MQH|JPW_GENETRIX_BRAND_MQH|JPW_ALAVANCAGEM_VERSION_MQH)\s*\n', '', production, flags=re.MULTILINE)
        production = re.sub(r"string\s+&([a-z_]+)\[\]", r"std::vector<string>& \1", production)
        production = re.sub(r"string\s+([a-z_]+)\[\];", r"std::vector<string> \1;", production)
        production = re.sub(r"uint\s+&([a-z_]+)\[\]",r"std::vector<uint>& \1",production)
        production = re.sub(r"uint\s+([a-z_]+)\[\];",r"std::vector<uint> \1;",production)
        production = production.replace("int JPWUIDesignNavColumns(std::vector<string>& labels,","template<class Labels> int JPWUIDesignNavColumns(Labels &labels,")
        # Convert native color literals exactly, retaining the palette in the
        # optional JSON preview of the production presenter objects.
        production = re.sub(r"C'(\d+),(\d+),(\d+)'", lambda m: str(int(m[1])+(int(m[2])<<8)+(int(m[3])<<16)), production)
        panel_source=(INCLUDE / "JPW_Alavancagem_Panel.mqh").read_text(encoding="utf-8")
        production += "\n" + re.search(r"struct JPWPanelRect\s*\{.*?\};",panel_source,flags=re.DOTALL)[0]
        production += "\n" + function(panel_source,"JPWPanelClamp") + "\n" + function(panel_source,"JPWPanelHUD") + "\n" + function(panel_source,"JPWPanelHUDReservedWidth")
        production += "\n" + function(self.indicator,"JPWNoCudaReadJustification")
        with tempfile.TemporaryDirectory(prefix="jpw-nocuda-ui-") as temp:
            source = Path(temp) / "ui.cpp"
            binary = Path(temp) / "ui"
            source.write_text(UI_SHIM + production + UI_CASES,
                              encoding="utf-8")
            compile_result = subprocess.run(
                [compiler, "-std=c++17", "-Wall", "-Wextra", "-Werror",
                 str(source), "-o", str(binary)], text=True,
                capture_output=True, timeout=60, check=False)
            self.assertEqual(compile_result.returncode, 0,
                             compile_result.stderr or compile_result.stdout)
            result = subprocess.run([str(binary)], text=True,
                                    capture_output=True, timeout=60,
                                    check=False)
            self.assertEqual(result.returncode, 0,
                             result.stderr or result.stdout)
            print(result.stdout, end="")

    def test_source_period_is_carried_through_read_and_render(self) -> None:
        for name in ("JPWNoCudaSourceSignature", "JPWNoCudaVisibleBars"):
            body = function(self.terminal, name)
            self.assertIn("CopyRates(symbol,source_tf,", body)
            self.assertNotRegex(body, r"\b(?:PERIOD_CURRENT|_Period)\b")
        visible = function(self.terminal, "JPWNoCudaVisibleBars")
        self.assertEqual(visible.count("iBarShift(symbol,source_tf,"), 2)
        paint = function(self.render, "JPWNoCudaCanvasPaint")
        self.assertIn("JPWNoCudaExactBar(symbol,source_tf,", paint)
        self.assertIn("JPWNoCudaVisibleBars(symbol,source_tf,", paint)
        self.assertNotRegex(paint, r"\b(?:PERIOD_CURRENT|_Period)\b")
        self.assertIn("bars[i].time,PeriodSeconds(source_tf)", paint)

    def test_paint_and_view_have_no_study_write_boundary(self) -> None:
        for name, source in (("render", self.render),
                             ("ui", self.ui),
                             ("terminal", self.terminal)):
            with self.subTest(surface=name):
                self.assertNotRegex(source,
                    r"\b(?:DatabaseOpen|DatabaseExecute|DatabaseTransactionCommit|"
                    r"JPWNoCudaStoreOpen|JPWNoCudaStoreConfirm|FileOpen|"
                    r"FileWrite|FileDelete)\s*\(")
        self.assertIn("JPWNoCudaRemoveDrawingObjects(prefix)", self.render)
        self.assertIn('prefix+"DRAW_"', self.render)
        self.assertIn('prefix+"UI_"', self.ui)

    def test_view_offers_all_required_study_controls(self) -> None:
        view = function(self.ui, "JPWNoCudaUIRender")
        for required in ("UI_OPEN", "UI_TAB_", "UI_CONFIRM", "UI_CANCEL", "UI_TF",
                         "UI_VIS", "UI_MESH", "UI_WIDTH", "UI_LEVEL",
                         "UI_JUST"):
            with self.subTest(control=required):
                self.assertIn('prefix+"' + required + '"', view)
        for anchor in ("A", "B", "C"):
            self.assertIn('"'+anchor+'"', view)
        self.assertIn('prefix+"UI_PICK_"+ids[a]', view)
        self.assertIn('"STUDY_PREV","STUDY_NEXT","REV_PREV","REV_NEXT"', view)
        for tab in ("Desenho", "Medidas", "Registro"):
            self.assertIn(tab, view)
        self.assertIn('if(!v.open', view)
        self.assertIn('prefix+"UI_OPEN"', view)
        self.assertNotIn("JPWNoCudaUIClear(prefix)", view,
                         "redraw retains existing widgets and removes only stale objects")
        self.assertIn("v.status", view)
        self.assertIn("v.source_tf", view)
        self.assertIn("v.history_text", view)

    def test_store_is_only_revision_write_api(self) -> None:
        confirm = self.store.split("JPWNoCudaStoreResult JPWNoCudaStoreConfirm(", 1)[1]
        self.assertIn("JPWNoCudaStoreInsertRevision(db,next)", confirm)
        self.assertIn("JPWNoCudaStoreWriteHead(db,next,previous)", confirm)
        self.assertIn("DatabaseTransactionCommit(db)", confirm)
        before = self.store.split("JPWNoCudaStoreResult JPWNoCudaStoreConfirm(", 1)[0]
        self.assertEqual(before.count("JPWNoCudaStoreInsertRevision(db,"), 0)

    def test_only_explicit_confirm_can_reach_revision_write(self) -> None:
        source = self.indicator
        confirm = function(source, "JPWNoCudaConfirmDraft")
        action = function(source, "JPWNoCudaAction")
        event = function(source, "OnChartEvent")
        self.assertEqual(source.count("JPWNoCudaStoreConfirm("), 1)
        self.assertIn("JPWNoCudaStoreConfirm(\n", confirm)
        self.assertRegex(action,
                         r'else if\(name=="UI_CONFIRM"\)\s*JPWNoCudaConfirmDraft\(\);')
        self.assertEqual(source.count("JPWNoCudaConfirmDraft("), 2)
        self.assertIn("if(id==CHARTEVENT_OBJECT_CLICK)", event)
        self.assertIn('StringFind(sparam,g_nocuda_prefix+"UI_")==0', event)
        self.assertIn("JPWNoCudaAction(sparam)", event)
        self.assertIn('if(id==CHARTEVENT_CHART_CHANGE)', event)
        self.assertNotIn("JPWNoCudaConfirmDraft", event)
        for name in ("OnCalculate", "OnTimer", "JPWNoCudaPaint",
                     "JPWNoCudaDrawUI", "JPWNoCudaRefreshGeometry",
                     "JPWNoCudaPickAt", "JPWNoCudaCancelDraft"):
            with self.subTest(event_or_view=name):
                body = function(source, name)
                self.assertNotRegex(body,
                    r"\b(?:JPWNoCudaStoreConfirm|JPWNoCudaConfirmDraft|"
                    r"JPWNoCudaStoreInsertRevision|DatabaseExecute|FileWrite)\s*\(")
        self.assertIn("g_nocuda_is_draft=false", function(source, "JPWNoCudaCancelDraft"))
        self.assertIn("rascunho preservado", confirm)

    def test_context_identity_and_history_verification(self) -> None:
        source = self.indicator
        init = function(source, "OnInit")
        timer = function(source, "OnTimer")
        action = function(source, "JPWNoCudaAction")
        load = function(source, "JPWNoCudaLoadStudy")
        draft = function(source, "JPWNoCudaNewDraft")
        saved = function(source, "JPWNoCudaCheckSavedHistory")
        self.assertIn("InpSourceTimeframe=PERIOD_H1", source)
        self.assertIn("g_nocuda_symbol=_Symbol", init)
        self.assertIn("g_nocuda_feed=AccountInfoString(ACCOUNT_SERVER)", init)
        self.assertIn("g_nocuda_source_tf=InpSourceTimeframe", init)
        self.assertIn("TerminalInfoString(TERMINAL_DATA_PATH)", init)
        self.assertIn("g_nocuda_store_key", init)
        for field in ("store_key", "symbol", "feed", "source_tf", "convention"):
            self.assertIn("g_nocuda_draft." + field, draft)
        self.assertRegex(load,
            r"head\.symbol!=g_nocuda_symbol\s*\|\|\s*head\.feed!=g_nocuda_feed")
        self.assertIn("head.source_tf!=(int)g_nocuda_source_tf", load)
        self.assertIn("_Symbol!=g_nocuda_symbol || current_feed!=g_nocuda_feed", timer)
        reset = function(source, "JPWNoCudaResetContext")
        self.assertIn("JPWNoCudaResetContext(_Symbol,current_feed)", timer)
        self.assertLess(timer.index("JPWNoCudaResetContext"), timer.index("if(g_ncf_mode)"))
        self.assertIn("JPWNoCudaClearAnchors()", reset)
        self.assertIn("JPWNoCudaReloadStudies()", reset)
        self.assertIn("JPWNCFShutdown()", reset)
        self.assertIn("JPWNCFInit()", reset)
        self.assertIn('g_nocuda_store_key=""', reset)
        self.assertIn('else if(name=="UI_TF")', action)
        self.assertIn("if(g_nocuda_is_draft)", action)
        self.assertIn("g_nocuda_source_tf=JPWNoCudaNextTf(g_nocuda_source_tf)", action)
        self.assertIn("JPWNoCudaReloadStudies()", action)
        self.assertIn("JPWNoCudaSourceSignature(record.symbol,", saved)
        self.assertIn("signature!=record.source_signature", saved)

    def test_duplicate_attach_guard_precedes_state_access(self) -> None:
        init = function(self.indicator, "OnInit")
        self.assertIn('IndicatorSetString(INDICATOR_SHORTNAME,JPW_NOCUDA_SHORTNAME)', init)
        self.assertIn("ChartIndicatorsTotal(0,0)", init)
        self.assertIn('ChartIndicatorName(0,0,i)=="JPW_NoCuda_Channels"', init)
        self.assertIn("ChartIndicatorName(0,0,i)==JPW_NOCUDA_SHORTNAME", init)
        self.assertIsNotNone(
            re.search(r"if\(copies>1\).*?return\(INIT_FAILED\)",
                      init, flags=re.DOTALL),
            "same-chart duplicate must be refused")
        self.assertLess(init.index("if(copies>1)"),
                        init.index("JPWNoCudaStoreKey("),
                        "guard must run before shared chart state or DB access")
        self.assertLess(init.index("if(copies>1)"),
                        init.index("EventSetTimer(1)"))

    def test_chart_view_state_is_context_bound_and_not_saved_on_repaint(self) -> None:
        source = self.indicator
        save = function(source, "JPWNoCudaSaveChartState")
        load = function(source, "JPWNoCudaLoadChartState")
        init = function(source, "OnInit")
        deinit = function(source, "OnDeinit")
        self.assertIn("JPWNoCudaStoreFrame(g_nocuda_store_key)", save)
        self.assertIn("JPWNoCudaStoreFrame(g_nocuda_symbol)", save)
        self.assertIn("IntegerToString((int)g_nocuda_source_tf)", save)
        self.assertIn("fields[0]!=context", load)
        self.assertIn("PeriodSeconds((ENUM_TIMEFRAMES)tf)<=0", load)
        self.assertIn("level<0 || level>64", load)
        self.assertIn("JPWNoCudaLoadChartState()", init)
        self.assertIn("if(reason==REASON_REMOVE)", deinit)
        for name in ("OnTimer", "OnCalculate", "OnChartEvent",
                     "JPWNoCudaPaint", "JPWNoCudaDrawUI",
                     "JPWNoCudaRefreshGeometry", "JPWNoCudaPickAt",
                     "JPWNoCudaDragAnchor"):
            with self.subTest(repaint_or_pick=name):
                self.assertNotIn("JPWNoCudaSaveChartState()",
                                 function(source, name))

    def test_selected_level_and_quote_are_observations(self) -> None:
        measurements = function(self.indicator, "JPWNoCudaMeasurements")
        self.assertIn("JPWNoCudaLevelValue(g_nocuda_level,level)", measurements)
        self.assertIn("JPWNoCudaPriceAtTime(g_nocuda_symbol,g_nocuda_source_tf,",
                      measurements)
        self.assertIn("resolved.estimated", measurements)
        self.assertNotIn("iBarShift", measurements)
        self.assertIn("InpPipSymbol==g_nocuda_symbol", measurements)
        self.assertIn("InpPipSize>0.0", measurements)
        self.assertIn('"Current" : "Estimated"', measurements)
        self.assertNotIn("JPWNoCudaStoreConfirm", measurements)
        self.assertNotRegex(self.indicator, r"\b(?:OrderSend|CTrade|trade\.Buy|trade\.Sell)\b")

    def test_source_identity_report(self) -> None:
        identities = {path.name: hashlib.sha256(path.read_bytes()).hexdigest()
                      for path in (CORE, TERMINAL, RENDER, UI, STORE, INDICATOR)}
        print("NOCUDA_INTEGRATION_SOURCES:", identities)


if __name__ == "__main__":
    unittest.main(verbosity=2)
