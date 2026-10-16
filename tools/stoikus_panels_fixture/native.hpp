#include <string>
#include <algorithm>
#include <cmath>
#include <iostream>
using string=std::string; using uint=unsigned int;
double scale=1.; int cw=2000,ch=1600,font_height=16;
const int CHART_WIDTH_IN_PIXELS=1,CHART_HEIGHT_IN_PIXELS=2;
extern bool scroll_enabled;
int ChartGetInteger(int,int property){return property==3?scroll_enabled:(property==CHART_WIDTH_IN_PIXELS?cw:ch);}
int MathMin(int a,int b){return std::min(a,b);} int MathMax(int a,int b){return std::max(a,b);}
int JPWUIDesignPx(int n){return std::max(1,int(std::round(n*scale)));}
bool TextSetFont(string,int){return true;}
bool TextGetSize(string,uint&w,uint&h){w=16*scale;h=font_height;return true;}
int JPWUIDesignButtonWidth(string label,int font){return int(label.size()*font*.65*scale)+JPWUIDesignPx(24);}
int failures=0;
void check(bool value,string message){if(!value){std::cerr<<"FAIL "<<message<<"\n";failures++;}}

bool g_manual_positioned=false;int g_manual_width=680,g_manual_height=500;
