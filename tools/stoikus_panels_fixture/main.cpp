int main(){
 for(double dpi:{1.,1.25,1.5,2.}){
  scale=dpi;cw=4000;ch=3000;JPWPanelRect rect;
  check(JPWPanelAccount(cw,ch,scale,rect),"account geometry exists");
  check(rect.width==JPWUIDesignPx(720)&&rect.height==JPWUIDesignPx(520),"account default 720x520");
  check(JPWNoCudaUIWidth()==JPWUIDesignPx(680)&&JPWNoCudaUIHeight()==JPWUIDesignPx(500),"manual default 680x500");
  JPWNoCudaFiboUIPrefs fp;JPWNoCudaFiboUIDefault(fp);
  check(fp.width==JPWUIDesignPx(680)&&fp.height==JPWUIDesignPx(500),"fibo default 680x500");
  for(int f:{9,11,16,24}){font_height=int(f*1.5*scale);check(JPWNoCudaUIButtonHeight()==JPWUIDesignControlHeight(font_height),"raw text padded once");}
  for(int size:{24,60,240,640}){cw=size;ch=size;JPWPanelAccount(cw,ch,scale,rect);check(rect.x>=0&&rect.y>=0&&rect.x+rect.width<=cw&&rect.y+rect.height<=ch,"account bounds");check(JPWNoCudaUIWidth()<=cw*85/100&&JPWNoCudaUIWidth()>0,"manual bounded width");}
 }
 for(int size:{1,8,24,60,240}){cw=size;ch=size;JPWNoCudaFiboUIPrefs fp;JPWNoCudaFiboUIDefault(fp);JPWNoCudaFiboUIBounds(fp);check(fp.x>=0&&fp.y>=0&&fp.x+fp.width<=cw&&fp.y+fp.height<=ch,"fibo whole rectangle bounded");}
 scale=1.;string labels[6]={"Overview","Positions","Root N","System","Settings","History"};
 for(int inner=100;inner<=1800;inner+=10){int n=JPWUIDesignNavColumns(labels,6,inner,11,8);check(n==1||n==3||n==6,"six sections use 6, 3+3 or selector");}
 cw=1000;ch=800;scale=1.;JPWNoCudaFiboUIDefault(g_fc_draft);g_fc_pref=g_fc_draft;
 long mx=110;double my=110;string down="1",up="0";
 JPWNoCudaFiboUIHandleGeometry("P",CHARTEVENT_MOUSE_MOVE,mx,my,down);
 check(!scroll_enabled,"owned fibo gesture suspends chart scroll");
 mx=130;my=140;JPWNoCudaFiboUIHandleGeometry("P",CHARTEVENT_MOUSE_MOVE,mx,my,up);
 check(scroll_enabled&&!g_fc_gesture&&saves==1,"fibo release restores and saves once");
 mx=110;my=110;JPWNoCudaFiboUIHandleGeometry("P",CHARTEVENT_MOUSE_MOVE,mx,my,down);
 JPWNoCudaFiboUIHandleGeometry("P",CHARTEVENT_CHART_CHANGE,mx,my,up);
 check(scroll_enabled&&!g_fc_gesture&&saves==1,"resize cancels gesture without save");
 scroll_enabled=false;JPWNoCudaFiboUIHandleGeometry("P",CHARTEVENT_MOUSE_MOVE,mx,my,down);
 JPWNoCudaFiboUIHandleGeometry("P",CHARTEVENT_MOUSE_MOVE,mx,my,up);
 check(!scroll_enabled,"prior disabled scroll preserved");
 scroll_enabled=true;JPWNoCudaFiboUIHandleGeometry("P",CHARTEVENT_MOUSE_MOVE,mx,my,down);owns=false;
 JPWNoCudaFiboUIHandleGeometry("P",CHARTEVENT_MOUSE_MOVE,mx,my,down);
 check(scroll_enabled&&!g_fc_gesture,"ownership loss restores scroll");owns=true;
 JPWPanelRect r={100,100,720,520,false};JPWStoikusWindowGesture gesture={};bool done=false;mx=110;my=110;cw=1000;ch=800;
 JPWStoikusWindowEvent(gesture,r,CHARTEVENT_MOUSE_MOVE,mx,my,down,true,cw,ch,48,36,done);
 check(gesture.active&&!scroll_enabled,"window captures header drag");mx=900;my=700;
 JPWStoikusWindowEvent(gesture,r,CHARTEVENT_MOUSE_MOVE,mx,my,up,true,cw,ch,48,36,done);
 check(done&&scroll_enabled&&r.x+r.width<=cw&&r.y+r.height<=ch,"window bounded complete gesture");
 if(failures){std::cerr<<failures<<" panel regressions\n";return 1;}
 std::cout<<"PASS production panel defaults/DPI/bounds/nav/raw text; native NOT_RUN\n";
}
