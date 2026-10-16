int main(){int failures=0;auto check=[&](bool ok,string msg){if(!ok){failures++;std::cerr<<"FAIL "<<msg<<"\n";}};
 for(bool was_scroll:{true,false})for(bool editing:{false,true}){
   objects.clear();JPWUIAcquire(g_nocuda_prefix);g_ncf_ui.open=true;g_ncf_ui.justification="draft before";
   g_fc_gesture=false;g_fc_mouse_down=false;g_fc_scroll_captured=false;host_mouse_scroll=was_scroll;
   g_fc_draft.x=100;g_fc_draft.y=100;g_fc_draft.width=680;g_fc_draft.height=500;
   string handle=JPWNoCudaFiboUIName(g_nocuda_prefix,"FC_DRAG");ObjectCreate(0,handle,OBJ_BUTTON,0,0,0);
   ObjectSetInteger(0,handle,OBJPROP_XDISTANCE,100);ObjectSetInteger(0,handle,OBJPROP_YDISTANCE,100);ObjectSetInteger(0,handle,OBJPROP_XSIZE,300);ObjectSetInteger(0,handle,OBJPROP_YSIZE,36);
   string edit=JPWNoCudaFiboUIName(g_nocuda_prefix,"FC_JUST");ObjectCreate(0,edit,OBJ_EDIT,0,0,0);ObjectSetString(0,edit,OBJPROP_TEXT,"pending justification");
   g_fc_editing=editing?edit:"";const string prior_editor=g_fc_editing;
   long x=110;double y=125;string down="1";OnChartEvent(CHARTEVENT_MOUSE_MOVE,x,y,down);
   check(g_fc_gesture&&!host_mouse_scroll,"actual wrapper arms Fibo drag while retaining editor");
   const int writes=all_writes;action_calls=0;long escape=27;double zero=0;string empty="";
   OnChartEvent(CHARTEVENT_KEYDOWN,escape,zero,empty);
   check(!g_fc_gesture&&!g_fc_scroll_captured&&host_mouse_scroll==was_scroll,"Escape releases gesture and restores prior scroll");
   check(g_ncf_ui.open&&g_ncf_ui.justification=="pending justification"&&g_fc_editing==prior_editor,"Escape gesture preserves panel draft and editor");
   check(action_calls==0&&all_writes==writes,"Escape gesture never closes/confirms/saves preferences");
 }
 // Ordinary Escape still follows the prior editor and panel-close contracts.
 for(bool editing:{false,true}){
   g_fc_gesture=false;g_fc_scroll_captured=false;g_ncf_ui.open=true;g_fc_editing=editing?JPWNoCudaFiboUIName(g_nocuda_prefix,"FC_JUST"):"";action_calls=0;
   long escape=27;double zero=0;string empty="";OnChartEvent(CHARTEVENT_KEYDOWN,escape,zero,empty);
   check(editing?g_ncf_ui.open&&g_fc_editing==""&&action_calls==0:!g_ncf_ui.open&&action_calls==1,"non-gesture Escape keeps existing semantics");
 }
 std::cout<<"Actual NoCuda wrapper Fibo Escape failures="<<failures<<"; native NOT_RUN\n";return failures?1:0;}
