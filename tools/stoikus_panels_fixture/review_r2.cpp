int main(){int failed=0;
 auto check=[&](bool ok,string msg){if(!ok){failed++;std::cerr<<"FAIL "<<msg<<"\n";}};
 for(int d:{100,125,150,200}){
   objects.clear();dpi=d;chart_width=3000;chart_height=2400;g_manual_positioned=false;g_manual_gesture.active=false;
   JPWNoCudaUIView v={};v.open=true;v.tab=0;v.symbol="EURUSD";v.source_tf="H1";
   JPWNoCudaUIRender("P",v);
   check(ObjectFind(0,"PUI_NEW")>=0&&ObjectFind(0,"PUI_PICK_A")>=0,"default manual drawing workflow");
   check(ObjectFind(0,"PUI_PAGE_NEXT")>=0,"default manual pagination");
 }
 dpi=100;chart_width=1440;chart_height=1120;objects.clear();
 JPWNoCudaUIView v={};v.open=true;v.symbol="EURUSD";v.source_tf="H1";
 g_manual_gesture.active=true;g_manual_rect={400,300,36,36,false};JPWNoCudaUIRender("P",v);
 for(auto &entry:objects){auto&o=entry.second;if(o.type!=OBJ_BUTTON&&o.type!=OBJ_EDIT)continue;
   int x=o.number[OBJPROP_XDISTANCE],y=o.number[OBJPROP_YDISTANCE],w=o.number[OBJPROP_XSIZE],h=o.number[OBJPROP_YSIZE];
   check(w>0&&h>0&&x>=0&&y>=0&&x+w<=chart_width&&y+h<=chart_height,"active tiny resize positive controls inside chart");
   if(ObjectFind(0,"PUI_BG")>=0)check(x>=g_manual_rect.x&&y>=g_manual_rect.y&&x+w<=g_manual_rect.x+g_manual_rect.width&&y+h<=g_manual_rect.y+g_manual_rect.height,"active resized controls inside panel");
 }
 objects.clear();g_manual_gesture.active=false;g_manual_positioned=true;g_manual_width=36;g_manual_height=36;
 JPWNoCudaUIRender("P",v);check(ObjectFind(0,"PUI_NEW")>=0&&ObjectFind(0,"PUI_PICK_A")>=0,"legacy undersized preference has usable temporary restore");
 check(g_manual_width==36&&g_manual_height==36,"paint does not rewrite saved geometry");
 objects.clear();g_manual_width=680;g_manual_height=500;g_manual_positioned=false;g_manual_gesture={};JPWNoCudaUIRender("P",v);
 bool committed=false;long rx=g_manual_rect.x+g_manual_rect.width-1;double ry=g_manual_rect.y+g_manual_rect.height-1;string pressed="1",released="0";
 JPWStoikusWindowEvent(g_manual_gesture,g_manual_rect,CHARTEVENT_MOUSE_MOVE,rx,ry,pressed,true,chart_width,chart_height,48,36,committed,480,500);
 rx=-10000;ry=-10000;JPWStoikusWindowEvent(g_manual_gesture,g_manual_rect,CHARTEVENT_MOUSE_MOVE,rx,ry,released,true,chart_width,chart_height,48,36,committed,480,500);
 check(committed&&g_manual_rect.width>=480&&g_manual_rect.height>=500,"manual real resize legible minimum");
 JPWNoCudaUIRememberGeometry();check(g_manual_width>=480&&g_manual_height>=500,"completed manual resize persists recoverable size");
 JPWNoCudaUIRender("P",v);check(ObjectFind(0,"PUI_NEW")>=0&&ObjectFind(0,"PUI_PICK_A")>=0,"completed minimum resize reopens usable workflow");
 JPWPanelRect r={100,100,720,520,false};JPWStoikusWindowGesture g={};bool done=false;long x=110;double y=125;string down="1",up="0";
 JPWStoikusWindowEvent(g,r,CHARTEVENT_MOUSE_MOVE,x,y,down,true,1440,1120,48,36,done);
 const bool consumed=JPWStoikusWindowEvent(g,r,CHARTEVENT_CUSTOM+7,x,y,up,false,1440,1120,48,36,done);
 check(!consumed&&!g.active&&host_mouse_scroll,"owner notification propagates after cancellation");
 for(int delta:{40,-40})for(int edge=0;edge<4;edge++){
   r={100,100,720,520,false};g={};done=false;
   x=edge==0?100:edge==1?819:400;y=edge==2?100:edge==3?619:350;
   JPWStoikusWindowEvent(g,r,CHARTEVENT_MOUSE_MOVE,x,y,down,true,1440,1120,48,36,done);
   check(g.active&&g.resize,"edge arms resize");
   if(edge<2)x+=delta;else y+=delta;
   JPWStoikusWindowEvent(g,r,CHARTEVENT_MOUSE_MOVE,x,y,up,true,1440,1120,48,36,done);
   check(done,"edge completes");
   check(edge==0?r.x==100+delta&&r.x+r.width==820:edge==1?r.x==100&&r.width==720+delta:edge==2?r.y==100+delta&&r.y+r.height==620:r.y==100&&r.height==520+delta,"opposite edge remains anchored");
 }
 std::cout<<"R2 manual/default/active/restore/owner/edges failures="<<failed<<"; native NOT_RUN\n";return failed?1:0;
}
