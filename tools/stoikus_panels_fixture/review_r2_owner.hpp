const int JPW_ACTION_MINIMIZE=161,JPW_UI_OWNER_EVENT=3107;
JPWStoikusWindowGesture g_account_window_gesture={};JPWPanelRect g_account_window_rect={100,100,720,520,false},g_details_rect=g_account_window_rect;
bool g_raiz_details_open=true,g_jpw_focus_suspended=false,g_stoikus_drag=false,g_stoikus_resize=false;
int g_details_control=36,g_details_pad=8,captured=0,destroyed=0,rendered=0,hud_rendered=0;
string g_panel_prefix="P",owner="P",edit="pending justification",draft="";
struct JPWStoikusVisual{bool account_positioned=false;int account_x=0,account_y=0,account_width=720,account_height=520;};
JPWStoikusVisual g_stoikus_visual;
string JPWActionObject(int n){return std::to_string(n);}void JPWAccountMinimize(){}
void JPWRaizSaveVisibleFields(){captured++;draft=edit;}void JPWRaizPanelDestroy(){destroyed++;}
void JPWRenderHUD(){hud_rendered++;}void JPWRenderRaizDetails(){rendered++;}void JPWInvalidateDialogContent(){}
bool JPWStoikusVisualSave(JPWStoikusVisual){return true;}double JPWUIDesignScale(){return scale;}double MathRound(double v){return std::round(v);}
string JPWUIOwner(){return owner;}
void JPWUIDesignBeginPass(){}void JPWUIDesignEndPass(){}void JPWStoikusHUDCancel(){}
bool JPWCockpitAcceptChartEvent(int,long,double,string){return true;}
bool JPWStoikusHUDEvent(int,long,double,string,string&){return false;}
bool JPWGenetrixHandleCycleEvent(int,long,string){return false;}
void JPWHandleChartEvent(int,const long&,const double&,const string&);
