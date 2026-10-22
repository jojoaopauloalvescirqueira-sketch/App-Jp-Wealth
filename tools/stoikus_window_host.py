"""Production HUD extraction plus observable host-native seams; never MT5 proof."""
from pathlib import Path
import re
from leverage_host_shim import translate_arrays
from leverage_panel_test import body_of
INC=Path(__file__).resolve().parents[1]/'mt5/jpw-alavancagem-atual/MQL5/Include/JPWealth'
def production(events_only=False):
    visual=(INC/'JPW_Stoikus_Visual.mqh').read_text()
    hud=(INC/'JPW_Stoikus_HUD.mqh').read_text()
    # Includes are loaded in their production order. Focus is already supplied
    # by callers; all three panel modules and the visual codec are real source.
    def expand(name, seen):
        if name in seen or name=='JPW_UI_Focus.mqh': return ''
        seen.add(name)
        return re.sub(r'#include <JPWealth/([^>]+)>',lambda m:expand(m[1],seen),(INC/name).read_text())
    if not events_only:
        cockpit=(INC/'JPW_Alavancagem_Cockpit.mqh').read_text()
        codec=cockpit[cockpit.index('void JPWCockpitDefault('):cockpit.index('bool JPWCockpitVisible(')]
        constants='\n'.join(line for line in cockpit.splitlines() if line.startswith('#define JPW_COCKPIT_') and not line.startswith('#define JPW_COCKPIT_METRIC_COUNT'))
        return translate_arrays(constants+'\n'+codec+expand('JPW_Stoikus_HUD.mqh',set()))
    hud=re.sub(r'^#include[^\n]*','',hud,flags=re.M)
    if events_only:
        start=hud.index('string JPWStoikusHUDResource(')
        state=hud[:start]
        functions=[]
        for signature in ['void JPWStoikusHUDCancel()', 'string JPWStoikusHUDHit(const int x,const int y)', 'bool JPWStoikusHUDCovered(const int x,const int y)', 'bool JPWStoikusHUDEvent(const int id,const long &lparam,const double &dparam,const string &sparam,string &route)']:
            functions.append(signature+'{'+body_of(hud,signature)+'}\n')
        prefs=(INC/'JPW_Stoikus_PanelPrefs.mqh').read_text()
        bridge=(INC/'JPW_Stoikus_PanelBridge.mqh').read_text()
        editor=(INC/'JPW_Stoikus_PanelEditor.mqh').read_text()
        render='void JPWStoikusPanelEditorRender(const int cw,const int ch,const color ink,const color fill)'
        actual_render=render+'{'+body_of(editor,render)+'}'
        # Event-only fixtures intentionally have no painter. Keep every state,
        # codec, persistence and editor event function real; exclude the unused
        # render body rather than replacing editor outcomes.
        start=editor.index(render);stop=editor.index('bool JPWStoikusPanelEditorKey(',start)
        editor=editor[:start]+editor[stop:]
        hud=state+'\n'+prefs+bridge+'extern bool g_raiz_details_open;\n'+editor+'\nint g_stoikus_metric_page=0;\n'+'\n'.join(functions)+'\n#endif\n'
    return translate_arrays(visual+'\n'+hud)

def native(existing, panel=False):
    """Only OS API/type seams absent from the caller; no product helper replacements."""
    out='#include <vector>\n#include <map>\nusing uchar=unsigned char;\n'
    constants={'CHART_MOUSE_SCROLL':600,'CHARTEVENT_MOUSE_MOVE':601,'CHARTEVENT_CLICK':602,'CHARTEVENT_OBJECT_CLICK':603,'CHARTEVENT_CHART_CHANGE':604,'CHARTEVENT_KEYDOWN':605,'CHARTEVENT_CUSTOM':1000,'TA_LEFT':0,'TA_TOP':0,'COLOR_FORMAT_ARGB_NORMALIZE':0,'OBJ_BITMAP_LABEL':606,'OBJ_RECTANGLE_LABEL':607,'OBJPROP_XSIZE':608,'OBJPROP_YSIZE':609,'CHART_WIDTH_IN_PIXELS':610,'CHART_HEIGHT_IN_PIXELS':611}
    for name,value in constants.items():
        if not re.search(r'\b'+name+r'\s*=',existing):out+=f'constexpr int {name}={value};\n'
    for name,definition in {
      'ObjectGetString':'string ObjectGetString(int,const string&n,int p){auto o=objects.find(n);if(o==objects.end())return \"\";auto v=o->second.text.find(p);return v==o->second.text.end()?\"\":v->second;}',
      'MathIsValidNumber':'bool MathIsValidNumber(double v){return std::isfinite(v);}',
      'StringToInteger':'long StringToInteger(const string&s){try{return std::stol(s);}catch(...){return 0;}}',
      'StringSubstr':'string StringSubstr(const string&s,int a,int n=-1){return s.substr(a,n<0?string::npos:n);}',
      'MathMin':'template<class A,class B>A MathMin(A a,B b){return a<b?a:(A)b;}',
      'MathRound':'double MathRound(double v){return std::round(v);}',
      'ArrayResize':'template<class T>int ArrayResize(std::vector<T>&v,int n){v.resize(n);return n;}',
      'ArrayInitialize':'template<class T,class U>void ArrayInitialize(std::vector<T>&v,U x){std::fill(v.begin(),v.end(),x);}',
      'ColorToARGB':'uint ColorToARGB(color c,uint a=255){return (a<<24)|((uint(c)&255)<<16)|(uint(c)&65280)|((uint(c)>>16)&255);}',
    }.items():
        if not re.search(r'\b'+name+r'\s*\([^;{}]*\)\s*\{',existing):out+=definition+'\n'
    if re.search(r'\bStringSubstr\s*\(',existing):out+='string StringSubstr(const string&s,int a){return s.substr(a); }\n'
    out+='int StringFind(const string&s,const string&n,int a){auto p=s.find(n,a);return p==string::npos?-1:(int)p;}\n'
    out+='''bool host_window_scroll=true;
bool ChartSetInteger(int,int p,long v){if(p==CHART_MOUSE_SCROLL)host_window_scroll=v;return true;}
long WindowChartGetInteger(int c,int p){return p==CHART_MOUSE_SCROLL?host_window_scroll:ChartGetInteger(c,p);}
#define ChartGetInteger WindowChartGetInteger
'''
    if not panel: return out
    out += r"""
#include <cstdio>
#include <sstream>
"""
    definitions={
     'TERMINAL_KEYSTATE_SHIFT':'constexpr int TERMINAL_KEYSTATE_SHIFT=1001;',
     'MathFloor':'double MathFloor(double v){return std::floor(v);}',
     'GetMicrosecondCount':'ulong GetMicrosecondCount(){return GetTickCount64()*1000+1;}',
     'StringFormat':'template<class... A>string StringFormat(const string &f,A...a){char b[256];std::snprintf(b,sizeof(b),f.c_str(),a...);return b;}',
     'StringSplit':'int StringSplit(const string&s,int d,std::vector<string>&v){v.clear();size_t start=0;for(size_t i=0;i<=s.size();i++)if(i==s.size()||s[i]==d){v.push_back(s.substr(start,i-start));start=i+1;}return v.size();}'
    }
    for name,definition in definitions.items():
        if name not in existing:out+=definition+'\n'
    return out


RASTER=r'''
struct HostWindowText {string text;int x,y,font;uint ink,w,h;};
std::vector<HostWindowText> host_window_pending;
std::map<string,std::vector<HostWindowText>> host_window_text;
std::map<string,std::vector<uint>> host_window_resources;
bool host_window_resource_fail=false,host_window_text_fail=false;int host_window_text_calls=0,host_window_resource_calls=0;
bool TextOut(const string&text,int x,int y,uint,std::vector<uint>&pixels,uint w,uint h,uint ink,int){
 host_window_text_calls++;host_window_pending.push_back({text,x,y,measured_font,ink,w,h});
 if(host_window_text_fail){host_window_pending.clear();return false;}
 uint tw,th;TextGetSize(text,tw,th);
 const int left=std::max(0,x),right=std::min((int)w,x+(int)tw);
 const int top=std::max(0,y),bottom=std::min((int)h,y+(int)th);
 if(left<right)for(int yy=top;yy<bottom;yy++)std::fill(pixels.begin()+yy*w+left,pixels.begin()+yy*w+right,ink);
 return true;
}
bool ResourceCreate(const string&n,const std::vector<uint>&p,int w,int h,int,int,int,int){
 host_window_resource_calls++;if(host_window_resource_fail){host_window_pending.clear();return false;}
 if(p.size()!=size_t(w*h))return false;
 host_window_resources[n]=p;host_window_text[n]=host_window_pending;host_window_pending.clear();return true;
}
bool ResourceFree(const string&n){host_window_text.erase(n);return host_window_resources.erase(n)>0;}
string WindowText(const string&name){string result;for(const auto&t:host_window_text[name+"_ARGB"]){if(!result.empty())result+=" ";result+=t.text;}return result;}
string WindowCaption(const string&name){return objects.count(name)&&objects.at(name).number.at(-1)==OBJ_BUTTON?objects.at(name).text.at(OBJPROP_TEXT):WindowText(name);}
bool WindowTextValid(const string&name,const int padding=0){
 auto object=objects.find(name);if(object==objects.end())return false;
 const auto &n=object->second.number;auto prop=[&](int p){auto at=n.find(p);return at==n.end()?0L:at->second;};
 const long w=prop(OBJPROP_XSIZE),h=prop(OBJPROP_YSIZE);if(w<=0||h<=0)return false;
 if(prop(-1)==OBJ_BITMAP_LABEL){
  const string key=name+"_ARGB";auto lines=host_window_text.find(key);auto pixels=host_window_resources.find(key);
  if(lines==host_window_text.end()||lines->second.empty()||pixels==host_window_resources.end()||pixels->second.size()!=size_t(w*h))return false;
  for(const auto&t:lines->second){
   uint tw=0,th=0;if(t.text.empty()||t.font<=0||!TextSetFont("Arial",-10*t.font,FW_NORMAL)||!TextGetSize(t.text,tw,th))return false;
   if(t.w!=w||t.h!=h||t.x<padding||t.y<0||t.x+(long)tw>w||t.y+(long)th>h||(t.ink>>24)!=255)return false;
  }
  return true;
 }
 if(prop(-1)==OBJ_BUTTON){
  auto text=object->second.text.find(OBJPROP_TEXT);const int font=(int)prop(OBJPROP_FONTSIZE);uint tw=0,th=0;
  return text!=object->second.text.end()&&!text->second.empty()&&font>0&&TextSetFont("Arial",-10*font,FW_NORMAL)&&TextGetSize(text->second,tw,th)&&tw+2*padding<=w&&th+2*padding<=h;
 }
 return false;
}

'''

def event_adapter(existing, focus_present=False):
    """Add actual persistence/hit/gesture/event functions to old event-only fixtures."""
    base=''
    if 'using color=' not in existing:base+='using color=int;\n'
    if not re.search(r'using\s+uint\s*=',existing):base+='using uint=unsigned int;\n'
    if not re.search(r'using\s+ushort\s*=',existing):base+='using ushort=unsigned short;\n'
    if 'std::map<string' not in existing:
        base+='''#include <map>
constexpr int OBJPROP_TEXT=1,OBJPROP_TOOLTIP=2,OBJPROP_TYPE=3,OBJPROP_XDISTANCE=4,OBJPROP_YDISTANCE=5,OBJPROP_HIDDEN=6,OBJPROP_SELECTABLE=7,OBJPROP_CORNER=8,OBJ_LABEL=1,CORNER_LEFT_UPPER=0;
struct HostEventObject {std::map<int,long> number;std::map<int,string> text;};
std::map<string,HostEventObject> objects;
int ObjectFind(int,const string&n){return objects.count(n)?0:-1;}
bool ObjectCreate(int,const string&n,int kind,int,int,int){objects[n].number[OBJPROP_TYPE]=kind;return true;}
bool ObjectDelete(int,const string&n){return objects.erase(n)>0;}
long ObjectGetInteger(int,const string&n,int p){return objects[n].number[p];}
bool ObjectSetInteger(int,const string&n,int p,long v){objects[n].number[p]=v;return true;}
bool ObjectSetString(int,const string&n,int p,const string&v){objects[n].text[p]=v;return true;}
long ChartGetInteger(int,int){return 800;}
string IntegerToString(int n){return std::to_string(n);}
int StringLen(const string&s){return s.size();}
ushort StringGetCharacter(const string&s,int i){return (unsigned char)s.at(i);}
template<class A,class B>A MathMax(A a,B b){return a>b?a:(A)b;}
int host_hud_redraws=0;void JPWRenderHUD(){host_hud_redraws++;}
int host_owner_events=0;bool EventChartCustom(int,int,long,double,const string&){host_owner_events++;return true;}
'''
    base+=native(existing+base,panel=True)
    base+='struct JPWPanelRect{int x=0,y=0,width=0,height=0;};\n'
    design=(INC/'JPW_UI_Design.mqh').read_text()
    # The event fixtures use native DPI96; production scaling still executes.
    if 'TerminalInfoInteger' not in existing:base+='long TerminalInfoInteger(int){return 96;}\n'
    base+='constexpr int TERMINAL_SCREEN_DPI=490;\n'
    for sig in ['double JPWUIDesignScale()','int JPWUIDesignPx(const int logical)']:
        base+=sig+'{'+body_of(design,sig)+'}\n'
    if focus_present:base+='string JPWUIOwner();bool JPWUIOwns(const string);bool JPWUIAcquire(const string);void JPWUIRelease(const string);\n#define JPW_UI_OWNER_EVENT 3107\n'
    else:base+=(INC/'JPW_UI_Focus.mqh').read_text()
    if not focus_present:
        cockpit=(INC/'JPW_Alavancagem_Cockpit.mqh').read_text()
        base+='struct JPWCockpitPrefs'+cockpit.split('struct JPWCockpitPrefs',1)[1].split('};',1)[0]+'};\n'
        base+='\n'.join(line for line in cockpit.splitlines() if line.startswith('#define JPW_COCKPIT_'))+'\n'
        base+=cockpit[cockpit.index('void JPWCockpitDefault('):cockpit.index('bool JPWCockpitVisible(')]
    result=base+production(events_only=True)
    result+=(INC/'JPW_Stoikus_Window.mqh').read_text()
    present=(INC/'JPW_Alavancagem_Presentation.mqh').read_text()
    actions=(INC/'JPW_Alavancagem_Actions.mqh').read_text()
    for name in ['JPW_ACTION_MINIMIZE','JPW_ACTION_PANEL_CUSTOMIZE']:
        match=re.search(r'const int '+name+r'=\d+;',present);assert match,name
        result+=match[0]+'\n'
    result+='JPWStoikusWindowGesture g_account_window_gesture;JPWPanelRect g_account_window_rect,g_details_rect;int g_details_control=36,g_details_pad=8;\n'
    result+='bool JPWUIOwns(const string owner);void JPWUIRelease(const string owner);void JPWRaizSaveVisibleFields();void JPWRaizPanelDestroy();\n'
    if not focus_present:
        # The focused keyboard fixture retains observable external render/field boundaries.
        result+='bool g_raiz_details_open=false,g_jpw_focus_suspended=false;int host_account_saves=0,host_account_destroys=0,host_account_renders=0,host_account_invalidations=0;\n'
        result+='void JPWRaizSaveVisibleFields(){host_account_saves++;}void JPWRaizPanelDestroy(){host_account_destroys++;}void JPWRenderRaizDetails(){host_account_renders++;}void JPWInvalidateDialogContent(int=-1){host_account_invalidations++;}\n'
        for sig in ['string JPWRaizUI(const string suffix)', 'string JPWActionObject(const int action)']:
            result+=sig+'{'+body_of(present,sig)+'}\n'
    for sig in ['void JPWAccountMinimize()', 'bool JPWAccountWindowEvent(const int id,const long &lp,const double &dp,const string &sp)']:
        result+=sig+'{'+body_of(actions,sig)+'}\n'
    return translate_arrays(result)

def layout_text():
    """Synthetic native metrics, actual cached text width and paragraph wrapping."""
    design=(INC/'JPW_UI_Design.mqh').read_text();present=(INC/'JPW_Alavancagem_Presentation.mqh').read_text()
    code=r'''
#include <codecvt>
#include <locale>
#include <sstream>
using uint=unsigned int;
constexpr int FW_NORMAL=400;
int host_layout_font=11;
std::u32string WindowUnicode(const string&s){std::wstring_convert<std::codecvt_utf8<char32_t>,char32_t> c;return c.from_bytes(s);}
int StringLen(const string&s){return WindowUnicode(s).size();}
ushort StringGetCharacter(const string&s,int n){return WindowUnicode(s).at(n);}
string StringSubstr(const string&s,int a,int n=-1){std::wstring_convert<std::codecvt_utf8<char32_t>,char32_t> c;return c.to_bytes(WindowUnicode(s).substr(a,n<0?std::u32string::npos:n));}
int StringSplit(const string&s,char d,std::vector<string>&v){v.clear();std::stringstream in(s);string item;while(std::getline(in,item,d))v.push_back(item);return v.size();}
template<class T>int ArrayResize(std::vector<T>&v,int n){v.resize(n);return n;}
bool TextSetFont(const string&,int font,int=FW_NORMAL){host_layout_font=-font/10;return host_layout_font>0;}
bool TextGetSize(const string&s,uint&w,uint&h){h=std::max(12,(host_layout_font*4*mock_screen_dpi+287)/288);w=(uint)(StringLen(s)*h*.48);return true;}
struct JPWUIDesignTextMeasure{string label;int font,dpi,width;bool ready;};JPWUIDesignTextMeasure g_jpw_ui_text_measure[128];
bool g_details_frame_active=false;
'''
    for src,sig in [(design,'uint JPWUIDesignHash(const string value)'),(design,'int JPWUIDesignTextWidth(const string label,const int font)'),(present,'void JPWDetailsAppendLine(const string row,string &lines[])'),(present,'void JPWDetailsWrap(const string paragraph,const int width,string &lines[])')]:
        code+=sig+'{'+body_of(src,sig)+'}\n'
    return translate_arrays(code)


def hud_native_text(cpp):
    """Replace only native string/text seams in the assembled strict HUD fixture.

    Indexes use UTF-16 code units, matching MQL strings. Whole surrogate pairs
    round-trip; lone-surrogate substrings are outside these UTF-8 fixtures.
    The synthetic font metric applies terminal DPI exactly once.
    """
    pattern = r'\b(?:int|string|ushort)\s+(?:StringLen|StringGetCharacter|StringSubstr|StringFind)\s*\([^;{}]*\)\s*\{'
    while match := re.search(pattern, cpp):
        stop=match.end(); depth=1
        while depth:
            depth+=(cpp[stop]=='{')-(cpp[stop]=='}'); stop+=1
        cpp=cpp[:match.start()]+cpp[stop:]
    pattern=r'\bbool\s+TextGetSize\s*\([^;{}]*\)\s*\{'
    matches=list(re.finditer(pattern,cpp)); assert len(matches)==1,'strict HUD TextGetSize seam drift'
    match=matches[0];stop=match.end();depth=1
    while depth:
        depth+=(cpp[stop]=='{')-(cpp[stop]=='}');stop+=1
    cpp=cpp[:match.start()]+r'''extern int mock_screen_dpi;
bool TextGetSize(const string&value,uint&width,uint&height){
 const double dpi=mock_screen_dpi/96.0;
 width=(uint)std::lround(StringLen(value)*std::max(8,measured_font)*dpi);
 height=(uint)std::lround(std::max(12,measured_font*3/2)*dpi);
 return true;
}'''+cpp[stop:]
    return r'''
#include <string>
#include <codecvt>
#include <locale>
#include <map>
// Cache pure UTF8-to-UTF16 conversion only, bounded to1024 strings. Native
// APIs return values; a local reference never survives another cache lookup.
// StringFind copies its haystack before looking up the needle (which may evict).
const std::u16string& HUDNativeUTF16(const std::string&s){
 static std::map<std::string,std::u16string> cache;
 auto found=cache.find(s);if(found!=cache.end())return found->second;
 std::wstring_convert<std::codecvt_utf8_utf16<char16_t>,char16_t> c;auto value=c.from_bytes(s);
 if(cache.size()>=1024)cache.clear();return cache.emplace(s,std::move(value)).first->second;
}
int StringLen(const std::string&s){return (int)HUDNativeUTF16(s).size();}
unsigned short StringGetCharacter(const std::string&s,int at){const auto &u=HUDNativeUTF16(s);return at<0||at>=(int)u.size()?0:(unsigned short)u[at];}
std::string StringSubstr(const std::string&s,int at,int length=-1){const auto &u=HUDNativeUTF16(s);if(at<0||at>=(int)u.size())return "";std::wstring_convert<std::codecvt_utf8_utf16<char16_t>,char16_t> c;return c.to_bytes(u.substr(at,length<0?std::u16string::npos:(size_t)length));}
int StringFind(const std::string&s,const std::string&needle,int at=0){if(at<0)return -1;const auto haystack=HUDNativeUTF16(s);auto pos=haystack.find(HUDNativeUTF16(needle),at);return pos==std::u16string::npos?-1:(int)pos;}
''' + cpp
