#include <cassert>
#include <cstdio>
#include <codecvt>
#include <locale>
using uchar=unsigned char; using ulong=unsigned long; using ENUM_OBJECT=int; using ushort=unsigned short;
constexpr int CHART_MOUSE_SCROLL=50,CHART_EVENT_MOUSE_MOVE=51,TA_LEFT=0,TA_TOP=0,COLOR_FORMAT_ARGB_NORMALIZE=0;
constexpr int CHARTEVENT_CLICK=10,CHARTEVENT_OBJECT_CLICK=11,CHARTEVENT_MOUSE_MOVE=12,CHARTEVENT_CHART_CHANGE=13,CHARTEVENT_KEYDOWN=14,CHARTEVENT_CUSTOM=1000,JPW_UI_OWNER_EVENT=3107;
bool scroll=true,fail_resource=false,fail_write=false,fail_readback=false,fail_bitmap=false; int writes=0,resource_writes=0,corrupt_read=0; ulong clock_ms=1000; double scale=1.;
ulong GetTickCount64(){return clock_ms;}
bool ChartSetInteger(int,int property,long value){if(property==CHART_MOUSE_SCROLL)scroll=value;return true;}
long HostChartGetInteger(int c,int p){return p==CHART_MOUSE_SCROLL?scroll:ChartGetInteger(c,p);}
#define ChartGetInteger HostChartGetInteger
string ObjectGetString(int,const string& name,int p){string s=objects[name].text[p];if(corrupt_read>0&&--corrupt_read==0)return "corrupt";if(fail_readback&&p==OBJPROP_TEXT&&name=="JPW_STOIKUS_VISUAL_V1"){fail_readback=false;return "corrupted";}return s;}
bool HostObjectSetString(int c,const string&name,int p,const string&v){if(fail_bitmap&&p==OBJPROP_BMPFILE)return false;if(name=="JPW_STOIKUS_VISUAL_V1"&&p==OBJPROP_TEXT){writes++;if(fail_write){fail_write=false;return false;}}return ObjectSetString(c,name,p,v);}
#define ObjectSetString HostObjectSetString
long StringToInteger(string s){try{return std::stol(s);}catch(...){return 0;}}
// MQL strings index Unicode characters, not UTF-8 transport bytes.
std::u32string HostUnicode(const string&s){std::wstring_convert<std::codecvt_utf8<char32_t>,char32_t> c;return c.from_bytes(s);}
int StringFind(string s,string p,int a=0){auto n=HostUnicode(s).find(HostUnicode(p),a);return n==std::u32string::npos?-1:n;}
string StringSubstr(string s,int a,int n=-1){std::wstring_convert<std::codecvt_utf8<char32_t>,char32_t> c;return c.to_bytes(HostUnicode(s).substr(a,n<0?std::u32string::npos:n));}
ushort StringGetCharacter(string s,int i){return (ushort)HostUnicode(s).at(i);}
double MathRound(double a){return std::round(a);}
int JPWUIDesignPx(int px){return int(px*scale+.5);} double JPWUIDesignScale(){return scale;}
struct JPWPanelRect{int x,y,width,height;};
color JPWPanelSurface(color){return 0x222222;} color JPWPanelTextColor(color,color){return 0xffffff;}
bool JPWUIDesignEnsure(string n,int kind){if(!objects.count(n))ObjectCreate(0,n,kind,0,0,0);return objects[n].number[-1]==kind;}
bool JPWUIDesignDelete(string n){return ObjectDelete(0,n);} void JPWUIDesignDeleteIcon(string n){ObjectDelete(0,n);}
bool JPWUIDesignSetInteger(string n,int p,long v){return ObjectSetInteger(0,n,p,v);}
bool JPWUIDesignSetString(string n,int p,string v){return ObjectSetString(0,n,p,v);}
template<class T>int ArrayResize(std::vector<T>&v,int n){v.resize(n);return n;} template<class T>int ArraySize(const std::vector<T>&v){return v.size();}
template<class T,class U>void ArrayInitialize(std::vector<T>&v,U x){std::fill(v.begin(),v.end(),x);}
uint ColorToARGB(color c,uint a=255){return (a<<24)|((uint(c)&255)<<16)|(uint(c)&65280)|((uint(c)>>16)&255);}
std::map<string,std::vector<uint>> resources;
bool ResourceCreate(string n,const std::vector<uint>&v,int w,int h,int,int,int,int){resource_writes++;if(fail_resource)return false;assert(v.size()==size_t(w*h));resources[n]=v;return true;}
bool ResourceFree(string n){return resources.erase(n)>0;}
// Synthetic ink rectangle seam; glyph rasterization and native compositing remain NOT_RUN.
bool TextOut(string text,int x,int y,uint,std::vector<uint>&v,uint w,uint h,uint ink,int){uint tw,th;TextGetSize(text,tw,th);for(int yy=y;yy<y+int(th)&&yy<int(h);yy++)for(int xx=x;xx<x+int(tw)&&xx<int(w);xx++)if(xx>=0&&yy>=0)v[yy*w+xx]=ink;return true;}
string JPWCockpitMetricValue(int,string value){return value;} string JPWCockpitQualityLabel(string q){return q;}
string risk_scope="EURUSD · Compra"; string JPWRiskDisplayScope(){return risk_scope;}
int JPWCockpitPresentationIndex(int slot){const int order[7]={0,5,1,2,3,4,6};return order[slot];}
void JPWHUDUnavailable(string){} void JPWRenderHUD();

#ifndef JPW_HUD_PANEL_NATIVE
string central_owner=""; string JPWUIOwner(){return central_owner;}
#endif

using JPWNoCudaUIRect=JPWPanelRect; long ChartID(){return 1;} string StringFormat(string,long){return g_panel_prefix+"HUD_BG";}
#ifdef JPW_HUD_PANEL_NATIVE
template<class... A>string StringFormat(const string&f,A...a){char b[256];std::snprintf(b,sizeof(b),f.c_str(),a...);return b;}
#endif
bool MathIsValidNumber(double n){return std::isfinite(n);} long MathAbs(long n){return std::abs(n);}
void JPWUIDesignBeginPass(){} void JPWUIDesignEndPass(){}
int generic_events=0;void JPWHandleChartEvent(int,const long&,const double&,const string&){generic_events++;}
bool JPWGenetrixHandleCycleEvent(int,const long&,const string&){return false;}

#ifdef JPW_HUD_PANEL_NATIVE
#include <cstdio>
constexpr int TERMINAL_KEYSTATE_SHIFT=1001;
long TerminalInfoInteger(int){return 0;}
double MathFloor(double v){return std::floor(v);}
ulong GetMicrosecondCount(){return clock_ms*1000+1;}
bool EventChartCustom(long,int,long,double,const string&){return true;}
int StringSplit(const string&s,int d,std::vector<string>&v){v.clear();size_t start=0;for(size_t i=0;i<=s.size();i++)if(i==s.size()||s[i]==d){v.push_back(s.substr(start,i-start));start=i+1;}return v.size();}

#endif
