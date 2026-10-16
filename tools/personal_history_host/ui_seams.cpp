// Native chart primitives are instrumented seams; the PersonalHistory renderer
// and action control flow come from the production source, not these functions.
enum {JPW_ROUTE_PERSONAL_HISTORY=17,JPW_ROUTE_PERSONAL_DETAIL=18,JPW_ROUTE_PERSONAL_EXPORT=19,
JPW_ROUTE_SETTINGS=2,JPW_SIGNAL_ROUTE=1000,JPW_ACTION_TAB_HISTORY=120,
JPW_ACTION_HISTORY_ACCOUNT=121,JPW_ACTION_HISTORY_REFRESH=122,JPW_ACTION_HISTORY_ROW_FIRST=130,JPW_ACTION_HISTORY_CHOICE_FIRST=140,
JPW_ACTION_PREVIOUS=1,JPW_ACTION_NEXT=2,JPW_ACTION_PRIMARY=3,JPW_ACTION_SECONDARY=4,OBJPROP_STATE=1};
int g_raiz_tab=JPW_ROUTE_PERSONAL_HISTORY,g_cockpit_page=0,g_raiz_page=0;
int g_cockpit_prefs=73,g_cockpit_draft=73;bool g_cockpit_reset_requested=false;
int g_details_pad=5,g_details_line=20,g_details_control=25;
std::map<string,string>host_labels,host_buttons;
string JPWActionObject(int action){return "button_"+IntegerToString(action);}
int ObjectFind(int,const string& target){return host_buttons.count(target)?0:-1;}
bool ObjectSetInteger(int,const string&,int,bool){return true;}
void ChartRedraw(int){}
void JPWRaizPanelDestroy(){host_labels.clear();host_buttons.clear();}
void JPWRenderRaizDetails(){}
void JPWSignalClear(){}
void JPWRenderHUD(){}
void JPWRaizSaveVisibleFields(){}
void JPWDetailsWrap(const string& text,int,std::vector<string>& lines){lines.push_back(text);}
bool JPWRaizCreateLabel(const string& name,const string& text,int,int){host_labels[name]=text;return true;}
bool JPWRaizCreateButton(int action,const string& text,int,int,int){host_buttons[JPWActionObject(action)]=text;return true;}
int JPWPanelPageCount(int count,int rows){return std::max(1,(count+rows-1)/rows);}
int JPWPanelClamp(int value,int lo,int hi){return std::max(lo,std::min(value,hi));}
double MathMin(double a,double b){return std::min(a,b);}

// Terminal/budget primitives only. CollectUI and all IO jobs execute real source.
bool g_account_known=true,g_raiz_details_open=false;string g_diagnostic_context="";
bool JPWCoordinatorBudgetRemaining(){return true;}
void JPWPersonalReadPresence(){}

bool g_cockpit_sections_open=false;
