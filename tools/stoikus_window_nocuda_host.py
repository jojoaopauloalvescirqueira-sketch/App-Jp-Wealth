"""Additive native/presentation boundaries for legacy NoCuda controller replays.
Production controller/core/store code and expected financial answers are untouched.
"""
from pathlib import Path
import re
from leverage_panel_test import body_of
from leverage_host_shim import source_root
INC=source_root()/'mt5/jpw-alavancagem-atual/MQL5/Include/JPWealth'

def fibo_cancel():
    ui=(INC/'JPW_NoCuda_Fibo_UI.mqh').read_text()
    state=re.search(r'^bool g_fc_scroll_captured=.*?;',ui,re.M)
    assert state
    return state[0]+'\nvoid JPWNoCudaFiboUICancelGeometry(){'+body_of(ui,'void JPWNoCudaFiboUICancelGeometry()')+'}\n'

FIBO_WINDOW_BOUNDARY=r'''
// Existing presentation boundary: record UI persistence intent; no study/store mutation.
std::vector<bool> host_fibo_window_save_requests;
bool JPWNoCudaFiboUIWindowSave(const bool minimized){host_fibo_window_save_requests.push_back(minimized);return true;}
'''

def manual_window(existing, native_scroll=True):
    """Actual shared Window algorithms with explicit manual presentation boundaries."""
    panel=(INC/'JPW_Alavancagem_Panel.mqh').read_text()
    code=''
    constants={'CHART_MOUSE_SCROLL':991,'CHART_WIDTH_IN_PIXELS':992,'CHART_HEIGHT_IN_PIXELS':993,'CHARTEVENT_MOUSE_MOVE':994,'CHARTEVENT_CHART_CHANGE':995,'CHARTEVENT_KEYDOWN':996,'CHARTEVENT_CUSTOM':1000}
    for name,value in constants.items():
        if not re.search(r'(?:#define\s+|\b)'+name+r'(?:\s+|\s*=)',existing):code+=f'enum {{ {name}={value} }};\n'
    if not re.search(r'\bMathMin\s*\([^;{}]*\)\s*\{',existing):code+='template<class T>T MathMin(T a,T b){return a<b?a:b;}\n'
    if not re.search(r'\bJPWPanelRect\s*\{',existing):code+=re.search(r'struct JPWPanelRect\s*\{.*?\};',panel,re.S)[0]+'\n'
    if native_scroll:code+='bool host_nocuda_scroll=true;bool ChartSetInteger(long,int p,long v){if(p==CHART_MOUSE_SCROLL)host_nocuda_scroll=v;return true;}\n'
    if not re.search(r'\bChartGetInteger\s*\([^;{}]*\)\s*\{',existing):code+='long ChartGetInteger(long,int p){return p==CHART_MOUSE_SCROLL?host_nocuda_scroll:(p==CHART_WIDTH_IN_PIXELS?1440:900);}\n'
    code+=(INC/'JPW_Stoikus_Window.mqh').read_text()
    code+='JPWStoikusWindowGesture g_manual_gesture;JPWPanelRect g_manual_rect;bool g_manual_collapsed=false;\n'
    code+='int host_manual_visual_saves=0,host_manual_geometry_saves=0;bool JPWNoCudaUIVisualSave(){host_manual_visual_saves++;return true;}void JPWNoCudaUIRememberGeometry(){host_manual_geometry_saves++;}\n'
    if not re.search(r'\bJPWUIDesignPx\s*\([^;{}]*\)\s*\{',existing):
        design=(INC/'JPW_UI_Design.mqh').read_text()
        code+='enum {TERMINAL_SCREEN_DPI=999};\n'
        if not re.search(r'\bTerminalInfoInteger\s*\([^;{}]*\)\s*\{',existing):code+='long TerminalInfoInteger(int){return 96;}\n'
        if not re.search(r'\bMathRound\s*\([^;{}]*\)\s*\{',existing):code+='#include <cmath>\ndouble MathRound(double v){return std::round(v);}\n'
        for sig in ['double JPWUIDesignScale()', 'int JPWUIDesignPx(const int logical)']:
            code+=sig+'{'+body_of(design,sig)+'}\n'
    return code

def full_ui_native():
    return r'''
enum {CHART_MOUSE_SCROLL=991,CHARTEVENT_CHART_CHANGE=995,CHARTEVENT_KEYDOWN=996,CHARTEVENT_MOUSE_MOVE=994,CHARTEVENT_CUSTOM=1000};
bool host_nocuda_scroll=true;
bool ChartSetInteger(long,int p,long v){if(p==CHART_MOUSE_SCROLL)host_nocuda_scroll=v;return true;}
long long WindowChartGetInteger(int c,int p){return p==CHART_MOUSE_SCROLL?host_nocuda_scroll:ChartGetInteger(c,p);}
#define ChartGetInteger WindowChartGetInteger
long StringToInteger(const string&s){try{return std::stol(s);}catch(...){return 0;}}
int StringSplit(const string&s,char d,std::vector<string>&v){v.clear();std::stringstream in(s);string item;while(std::getline(in,item,d))v.push_back(item);return v.size();}
'''

def manual_signature_fixture(cases):
    """Keep original signature assertions; explicitly provide its wide-window precondition.
    A large chart no longer implicitly enlarges the approved680logical default.
    All following compact/financial/field scenarios retain the default680 width.
    """
    start=' for(int scale:{100,125,150,200}) {'
    end=' for(int width:{300,390,800,1440}) for(int height:{380,390,400,402,420,499,500,520,560,700})'
    assert cases.count(start)==1 and cases.count(end)==1
    return cases.replace(start,' ++checks;if(g_manual_width!=680){++failures;std::cerr<<"FAIL approved default manual logical width680\\n";}\n g_manual_width=960;\n'+start,1).replace(end,' g_manual_width=680;\n'+end,1)
