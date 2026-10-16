const int CHARTEVENT_OBJECT_CLICK=1,CHARTEVENT_MOUSE_MOVE=2,CHARTEVENT_CHART_CHANGE=3,CHARTEVENT_KEYDOWN=4,CHARTEVENT_CUSTOM=1000;
const int CHART_MOUSE_SCROLL=3,OBJPROP_XDISTANCE=1,OBJPROP_YDISTANCE=2,OBJPROP_XSIZE=3,OBJPROP_YSIZE=4;
bool scroll_enabled=true;int saves=0;
JPWNoCudaFiboUIPrefs g_fc_pref,g_fc_draft;
bool g_fc_mouse_down=false,g_fc_gesture=false,g_fc_resize=false;
int g_fc_resize_edges=0;
int g_fc_pointer_x=0,g_fc_pointer_y=0,g_fc_start_x=0,g_fc_start_y=0,g_fc_start_w=0,g_fc_start_h=0;
string JPWNoCudaFiboUIName(string p,string n){return p+n;}
int StringToInteger(string s){return std::stoi(s);}
int ObjectFind(int,string){return 0;}
int ObjectGetInteger(int,string n,int p){bool resize=n.find("RESIZE")!=string::npos; if(p==OBJPROP_XDISTANCE)return resize?400:100;if(p==OBJPROP_YDISTANCE)return resize?400:100;return 40;}
bool JPWNoCudaFiboUISavePrefs(){saves++;return true;}
bool ChartSetInteger(int,int,bool value){scroll_enabled=value;return true;}
bool owns=true;bool JPWUIOwns(string){return owns;}

bool g_fc_scroll_captured=false,g_fc_scroll_before=true;
