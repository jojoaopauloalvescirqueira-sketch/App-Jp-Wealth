int main(){int failed=0;auto check=[&](bool ok,string m){if(!ok){failed++;std::cerr<<"FAIL "<<m<<"\n";}};
 dpi=100;chart_width=1440;chart_height=1120;string prefix="P";
 JPWUIAcquire(prefix);ObjectCreate(0,"PFC_BACKGROUND",OBJ_RECTANGLE_LABEL,0,0,0);
 for(int delta:{40,-40})for(int edge=0;edge<4;edge++){
   g_fc_draft.x=100;g_fc_draft.y=100;g_fc_draft.width=680;g_fc_draft.height=500;g_fc_draft.font=11;g_fc_pref=g_fc_draft;
   g_fc_gesture=false;g_fc_mouse_down=false;int before=pref_writes;
   long x=edge==0?100:edge==1?779:400;double y=edge==2?100:edge==3?599:350;string down="1",up="0";
   JPWNoCudaFiboUIHandleGeometry(prefix,CHARTEVENT_MOUSE_MOVE,x,y,down);
   check(g_fc_gesture&&g_fc_resize,"Fibo edge resize starts");check(pref_writes==before,"Fibo edge down never persists");
   if(edge<2)x+=delta;else y+=delta;
   JPWNoCudaFiboUIHandleGeometry(prefix,CHARTEVENT_MOUSE_MOVE,x,y,up);
   check(!g_fc_gesture&&host_mouse_scroll&&pref_writes==before+1,"Fibo edge up persists once and restores scroll");
   check(edge==0?g_fc_draft.x==100+delta&&g_fc_draft.width==680-delta:edge==1?g_fc_draft.x==100&&g_fc_draft.width==680+delta:edge==2?g_fc_draft.y==100+delta&&g_fc_draft.height==500-delta:g_fc_draft.y==100&&g_fc_draft.height==500+delta,"Fibo opposite edge anchored");
 }
 std::cout<<"R2 Fibo edge failures="<<failed<<"; native NOT_RUN\n";return failed?1:0;}
