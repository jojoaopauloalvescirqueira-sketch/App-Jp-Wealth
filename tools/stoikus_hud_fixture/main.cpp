void JPWRenderHUD(){JPWStoikusHUDRender();}
void draw(){JPWStoikusHUDRender();}
void click(string suffix,int kind=CHARTEVENT_OBJECT_CLICK){clock_ms+=500;string route;long x=0;double y=0;assert(JPWStoikusHUDEvent(kind,x,y,g_panel_prefix+suffix,route));}
int main(){
 assert(StringLen("−")==1&&StringGetCharacter("·",0)==183&&StringSubstr("ç·",0,1)=="ç"&&StringFind("ç· ação","ação")==3);
 JPWStoikusVisualLoad();chart_width=1200;chart_height=1800;g_cockpit_prefs.visible_mask=127;
 for(auto &m:g_cockpit_snapshot.metric){m.value="2.75x";m.reason="fixture";m.quality=JPW_VIEW_CURRENT;}
 for(string suffix:{"HUD_RESTORE","HUD_MODE","HUD_OPACITY","HUD_RESET"})ObjectCreate(0,g_panel_prefix+suffix,OBJ_BUTTON,0,0,0);
 ObjectCreate(0,g_panel_prefix+"HUD_FOREIGN",OBJ_LABEL,0,0,0);
 ObjectCreate(0,g_panel_prefix+"3",OBJ_BUTTON,0,0,0);
 draw();for(string suffix:{"HUD_RESTORE","HUD_MODE","HUD_OPACITY","HUD_RESET"})assert(!objects.count(g_panel_prefix+suffix));assert(objects.count(g_panel_prefix+"HUD_FOREIGN"));assert(!objects.count(g_panel_prefix+"3"));assert(objects.count(g_panel_prefix+"0")&&objects.count(g_panel_prefix+"5")&&!objects.count(g_panel_prefix+"1"));
 assert(g_stoikus_surfaces[JPWStoikusHUDSlot(g_panel_prefix+"0")].key.find("Conta inteira")!=string::npos);
 assert(!g_hud_summary); assert(resources.at(JPWStoikusHUDResource(g_panel_prefix+"HUD_BG"))[0]>>24==179);
 int before=resource_writes;draw();assert(resource_writes==before&&writes==0);
 for(int transparency:{0,30,100}){g_stoikus_visual.transparency=transparency;draw();assert(resources.at(JPWStoikusHUDResource(g_panel_prefix+"HUD_BG"))[0]>>24==uint(JPWStoikusAlpha(transparency)));auto row=resources.at(JPWStoikusHUDResource(g_panel_prefix+"0"));bool ink=false;for(auto pixel:row){assert(pixel>>24==0||pixel>>24==255);ink|=pixel>>24==255;}assert(ink);}
 // Pair arrives after the first action changes the layout: must execute once.
 int i=JPWStoikusHUDSlot(g_panel_prefix+"HUD_MIN");long x=g_stoikus_surfaces[i].x+4;double y=g_stoikus_surfaces[i].y+4;string route;
 assert(JPWStoikusHUDEvent(CHARTEVENT_OBJECT_CLICK,x,y,g_panel_prefix+"HUD_MIN",route));assert(g_stoikus_visual.collapsed);
 JPWStoikusHUDEvent(CHARTEVENT_CLICK,x,y,"",route);assert(g_stoikus_visual.collapsed);
 clock_ms+=500; i=JPWStoikusHUDSlot(g_panel_prefix+"HUD_RESTORE");x=g_stoikus_surfaces[i].x+4;y=g_stoikus_surfaces[i].y+4;
 JPWStoikusHUDEvent(CHARTEVENT_CLICK,x,y,"",route);assert(!g_stoikus_visual.collapsed);route="";
 JPWStoikusHUDEvent(CHARTEVENT_OBJECT_CLICK,x,y,g_panel_prefix+"HUD_RESTORE",route);assert(route=="");
 // A stale second event may name the new object at the same location.
 click("HUD_MIN");clock_ms+=500;i=JPWStoikusHUDSlot(g_panel_prefix+"HUD_RESTORE");x=g_stoikus_surfaces[i].x+4;y=g_stoikus_surfaces[i].y+4;
 JPWStoikusHUDEvent(CHARTEVENT_OBJECT_CLICK,x,y,g_panel_prefix+"HUD_RESTORE",route);assert(!g_stoikus_visual.collapsed);
 JPWStoikusHUDEvent(CHARTEVENT_CLICK,x,y,"",route);assert(route=="");
 string saved=ObjectGetString(0,JPW_STOIKUS_VISUAL_OBJECT,OBJPROP_TEXT);JPWStoikusVisual next=g_stoikus_visual;next.transparency=20;fail_write=true;assert(!JPWStoikusVisualSave(next));assert(ObjectGetString(0,JPW_STOIKUS_VISUAL_OBJECT,OBJPROP_TEXT)==saved);
 fail_write=true;corrupt_read=2;assert(!JPWStoikusVisualSave(next));assert(g_stoikus_visual_notice.find("Falha ao salvar e restaurar")!=string::npos);corrupt_read=0;
 corrupt_read=2;assert(!JPWStoikusVisualSave(next));assert(ObjectGetString(0,JPW_STOIKUS_VISUAL_OBJECT,OBJPROP_TEXT)==saved);
 ObjectSetString(0,JPW_STOIKUS_VISUAL_OBJECT,OBJPROP_TEXT,"broken");JPWStoikusVisualLoad();assert(g_stoikus_visual_invalid);assert(!JPWStoikusVisualSave(next));assert(ObjectGetString(0,JPW_STOIKUS_VISUAL_OBJECT,OBJPROP_TEXT)=="broken");assert(JPWStoikusVisualSave(next,true));
 fail_resource=true;g_stoikus_visual.transparency=40;draw();assert(objects[g_panel_prefix+"HUD_BG"].number[-1]==OBJ_RECTANGLE_LABEL);assert(g_stoikus_visual_notice!="");fail_resource=false;draw();assert(objects[g_panel_prefix+"HUD_BG"].number[-1]==OBJ_BITMAP_LABEL);
 fail_bitmap=true;g_stoikus_visual.transparency=50;draw();assert(objects[g_panel_prefix+"HUD_BG"].number[-1]==OBJ_RECTANGLE_LABEL);fail_bitmap=false;draw();
 // Geometry stable across values and availability; matrix includes small charts.
 for(double dpi:{1.,1.25,1.5,2.}) for(int font:{8,10,20,40}) for(int mask:{0,1,32,127}) for(int mode:{0,1}) {
  scale=dpi;InpFontSize=font;chart_width=1920;chart_height=5000;g_cockpit_prefs.visible_mask=mask;g_stoikus_visual.mode=mode;
  g_stoikus_visual.collapsed=false;draw();int h=g_stoikus_hud.height;
  for(int metric=0;metric<7;metric++) assert(bool(objects.count(g_panel_prefix+IntegerToString(metric)))==JPWStoikusMetricVisible(mode,mask,metric));
  g_cockpit_snapshot.metric[0].value="9876543210987654321098765432109876543210 x";g_cockpit_snapshot.metric[5].quality=JPW_VIEW_NA;
  draw();assert(g_stoikus_hud.height==h);
  if(JPWStoikusMetricVisible(mode,mask,5))assert(g_stoikus_surfaces[JPWStoikusHUDSlot(g_panel_prefix+"HUD_NOTICE")].key.find("Leitura indisponível")!=string::npos);assert(g_stoikus_hud.width<=int(480*scale+.5));
  for(auto &entry:resources) assert(entry.second.size()*4<=8000000);
 }
 scale=1.;InpFontSize=10;chart_width=1200;chart_height=1800;g_cockpit_prefs.visible_mask=127;g_stoikus_visual.mode=0;draw();
 // Scope too long hides the amount and gives named details access.
 risk_scope=string(200,'W');draw();i=JPWStoikusHUDSlot(g_panel_prefix+"5");assert(g_stoikus_surfaces[i].key.find("Detalhes")!=string::npos);
 assert(objects[g_panel_prefix+"5"].text[OBJPROP_TOOLTIP].find(risk_scope)!=string::npos);
 clock_ms+=500;route="";assert(JPWStoikusHUDEvent(CHARTEVENT_OBJECT_CLICK,x,y,g_panel_prefix+"5",route));assert(route==g_panel_prefix+"5");
 // Persist one independent field without changing Account geometry or financial draft.
 next=g_stoikus_visual;next.account_x=101;next.account_y=202;next.account_positioned=true;assert(JPWStoikusVisualSave(next));
 int draftmask=g_cockpit_draft.visible_mask;click("HUD_OPTIONS");click("HUD_OPACITY");assert(g_stoikus_visual.account_x==101&&g_cockpit_draft.visible_mask==draftmask);
 // Gesture scroll state is restored on completion, cancel, and deinit.
 g_stoikus_options=false;draw();x=g_stoikus_hud.x+95;y=g_stoikus_hud.y+10;scroll=false;
 JPWStoikusHUDEvent(CHARTEVENT_MOUSE_MOVE,x,y,"1",route);assert(g_stoikus_drag);int oldwrites=writes;
 long dx=x+70;double dy=y+30;JPWStoikusHUDEvent(CHARTEVENT_MOUSE_MOVE,dx,dy,"1",route);assert(writes==oldwrites);
 JPWStoikusHUDEvent(CHARTEVENT_MOUSE_MOVE,dx,dy,"0",route);assert(!g_stoikus_drag&&!scroll&&writes==oldwrites+1);
 scroll=true;x=g_stoikus_hud.x+95;y=g_stoikus_hud.y+10;JPWStoikusHUDEvent(CHARTEVENT_MOUSE_MOVE,x,y,"1",route);assert(!scroll);
 long escape=27;double unused=0;JPWStoikusHUDEvent(CHARTEVENT_KEYDOWN,escape,unused,"",route);assert(scroll&&!g_stoikus_drag);
 JPWNoCudaUIRect reserved;assert(JPWNoCudaUICockpitHUD(chart_width,chart_height,reserved));assert(reserved.x==g_stoikus_hud.x&&reserved.y==g_stoikus_hud.y&&reserved.width==g_stoikus_hud.width);
 for(int size:{60,240,600}) {chart_width=size;chart_height=size;draw(); if(size>=240)assert(JPWNoCudaUICockpitHUD(size,size,reserved));}
 chart_width=1200;chart_height=1800;draw();
 // Central owner geometry blocks bare coordinate actions/drag underneath it.
 central_owner="JPW_NOCUDA_1_";string overlay=central_owner+"UI_BG";ObjectCreate(0,overlay,OBJ_RECTANGLE_LABEL,0,0,0);
 ObjectSetInteger(0,overlay,OBJPROP_XDISTANCE,g_stoikus_hud.x);ObjectSetInteger(0,overlay,OBJPROP_YDISTANCE,g_stoikus_hud.y);
 ObjectSetInteger(0,overlay,OBJPROP_XSIZE,g_stoikus_hud.width);ObjectSetInteger(0,overlay,OBJPROP_YSIZE,g_stoikus_hud.height);
 i=JPWStoikusHUDSlot(g_panel_prefix+"HUD_MIN");x=g_stoikus_surfaces[i].x+4;y=g_stoikus_surfaces[i].y+4;clock_ms+=500;
 assert(!JPWStoikusHUDEvent(CHARTEVENT_CLICK,x,y,"",route));assert(!g_stoikus_visual.collapsed);
 x=g_stoikus_hud.x+95;y=g_stoikus_hud.y+10;assert(!JPWStoikusHUDEvent(CHARTEVENT_MOUSE_MOVE,x,y,"1",route));assert(!g_stoikus_drag);
 ObjectDelete(0,overlay);central_owner="";
 // Template recheck during a gesture must replace, never resurrect, prior preferences.
 x=g_stoikus_hud.x+95;y=g_stoikus_hud.y+10;scroll=true;JPWStoikusHUDEvent(CHARTEVENT_MOUSE_MOVE,x,y,"1",route);assert(g_stoikus_drag);
 JPWStoikusVisual external=g_stoikus_visual;external.transparency=80;external.account_x=808;external.account_y=909;
 ObjectSetString(0,JPW_STOIKUS_VISUAL_OBJECT,OBJPROP_TEXT,JPWStoikusVisualEncode(external));draw();
 JPWStoikusHUDEvent(CHARTEVENT_KEYDOWN,escape,unused,"",route);assert(!g_stoikus_drag&&scroll);assert(g_stoikus_visual.account_x==808&&g_stoikus_visual.transparency==80);
 next=g_stoikus_visual;next.transparency=90;assert(JPWStoikusVisualSave(next));assert(g_stoikus_visual.account_x==808&&g_stoikus_visual.account_y==909);
 // Exercise the actual indicator wrapper and actual keyboard ownership gate.
 clock_ms+=1000;long foreign_x=1100;double foreign_y=1200;OnChartEvent(CHARTEVENT_OBJECT_CLICK,foreign_x,foreign_y,"FOREIGN_EDITOR");
 x=g_stoikus_hud.x+95;y=g_stoikus_hud.y+10;scroll=true;OnChartEvent(CHARTEVENT_MOUSE_MOVE,x,y,"1");assert(g_stoikus_drag&&!scroll);
 OnChartEvent(CHARTEVENT_KEYDOWN,escape,unused,"");assert(!g_stoikus_drag&&scroll);
 int dispatched=generic_events;long key=65;OnChartEvent(CHARTEVENT_KEYDOWN,key,unused,"");assert(generic_events==dispatched);
 // Foreign type and late template replacement cannot be overwritten by stale UI.
 saved=ObjectGetString(0,JPW_STOIKUS_VISUAL_OBJECT,OBJPROP_TEXT);objects[JPW_STOIKUS_VISUAL_OBJECT].number[-1]=OBJ_BUTTON;
 next=g_stoikus_visual;assert(!JPWStoikusVisualSave(next));assert(ObjectGetString(0,JPW_STOIKUS_VISUAL_OBJECT,OBJPROP_TEXT)==saved);
 objects[JPW_STOIKUS_VISUAL_OBJECT].number[-1]=OBJ_LABEL;
 next=g_stoikus_visual;next.transparency=80;ObjectSetString(0,JPW_STOIKUS_VISUAL_OBJECT,OBJPROP_TEXT,JPWStoikusVisualEncode(next));
 JPWStoikusVisual stale=g_stoikus_visual;assert(!JPWStoikusVisualSave(stale));assert(g_stoikus_visual.transparency==80);
 objects["FOREIGN"].text[1]="keep";JPWStoikusHUDCleanup();assert(resources.empty()&&objects.count("FOREIGN"));
 g_stoikus_visual.collapsed=true;for(string suffix:{"HUD_MIN","HUD_OPTIONS","HUD_MODE","HUD_OPACITY","HUD_RESET","HUD_RESIZE","HUD_NOTICE"})ObjectCreate(0,g_panel_prefix+suffix,OBJ_BUTTON,0,0,0);
 draw();for(string suffix:{"HUD_MIN","HUD_OPTIONS","HUD_MODE","HUD_OPACITY","HUD_RESET","HUD_RESIZE","HUD_NOTICE"})assert(!objects.count(g_panel_prefix+suffix));assert(objects.count(g_panel_prefix+"HUD_RESTORE"));JPWStoikusHUDCleanup();
 std::cout<<"PASS production HUD pixels/cache/prefs/events/fallback/cleanup; native NOT_RUN\n";
}
