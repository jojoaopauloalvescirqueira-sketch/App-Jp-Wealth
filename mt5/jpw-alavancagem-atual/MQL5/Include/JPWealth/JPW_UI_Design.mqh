#ifndef JPW_UI_DESIGN_MQH
#define JPW_UI_DESIGN_MQH


// Bounded, instance-local presentation caches. They contain no financial facts.
// A successful queued setter is cached only as our requested appearance. Ensure
// confirms existence separately; cache hits never certify account data quality.
#define JPW_UI_PROPERTY_SLOTS 4096
struct JPWUIDesignProperty
  {
   string name;
   long property;
   bool text_property;
   bool ready;
   long integer;
   string text;
  };
JPWUIDesignProperty g_jpw_ui_properties[JPW_UI_PROPERTY_SLOTS];
bool g_jpw_ui_changed=false;
int g_jpw_ui_pass_depth=0;
ulong g_jpw_ui_set_requests=0,g_jpw_ui_set_skipped=0,g_jpw_ui_creates=0,g_jpw_ui_deletes=0;
uint JPWUIDesignHash(const string value)
  {
   uint hash=2166136261;
   for(int i=0;i<StringLen(value);i++) hash=(hash^(uint)StringGetCharacter(value,i))*16777619;
   return(hash);
  }
int JPWUIDesignPropertySlot(const string name,const long property,const bool text)
  {
   const uint hash=JPWUIDesignHash(name+"|"+IntegerToString(property)+(text ? "S" : "I"));
   const int first=(int)(hash%JPW_UI_PROPERTY_SLOTS);
   for(int probe=0;probe<16;probe++)
     {
      const int slot=(first+probe)%JPW_UI_PROPERTY_SLOTS;
      if(!g_jpw_ui_properties[slot].ready ||
         (g_jpw_ui_properties[slot].name==name && g_jpw_ui_properties[slot].property==property &&
          g_jpw_ui_properties[slot].text_property==text)) return(slot);
     }
   // Bounded collision eviction loses optimization, never the requested update.
   g_jpw_ui_properties[first].ready=false;
   return(first);
  }
void JPWUIDesignForget(const string name)
  {
   for(int i=0;i<JPW_UI_PROPERTY_SLOTS;i++)
      if(g_jpw_ui_properties[i].ready && g_jpw_ui_properties[i].name==name)
        { g_jpw_ui_properties[i].ready=false; g_jpw_ui_properties[i].text=""; }
  }
bool JPWUIDesignSetInteger(const string name,const ENUM_OBJECT_PROPERTY_INTEGER property,const long value)
  {
   const int slot=JPWUIDesignPropertySlot(name,(long)property,false);
   if(property!=OBJPROP_STATE && property!=OBJPROP_SELECTED &&
      g_jpw_ui_properties[slot].ready && g_jpw_ui_properties[slot].integer==value)
     { g_jpw_ui_set_skipped++; return(true); }
   if(!ObjectSetInteger(0,name,property,value))
     { g_jpw_ui_properties[slot].ready=false; return(false); }
   g_jpw_ui_properties[slot].name=name; g_jpw_ui_properties[slot].property=(long)property;
   g_jpw_ui_properties[slot].text_property=false; g_jpw_ui_properties[slot].integer=value;
   g_jpw_ui_properties[slot].ready=true; g_jpw_ui_changed=true; g_jpw_ui_set_requests++;
   return(true);
  }
bool JPWUIDesignSetString(const string name,const ENUM_OBJECT_PROPERTY_STRING property,const string value)
  {
   const int slot=JPWUIDesignPropertySlot(name,(long)property,true);
   const bool editable_text=(property==OBJPROP_TEXT && ObjectGetInteger(0,name,OBJPROP_TYPE)==OBJ_EDIT);
   if(!editable_text && g_jpw_ui_properties[slot].ready && g_jpw_ui_properties[slot].text==value)
     { g_jpw_ui_set_skipped++; return(true); }
   if(!ObjectSetString(0,name,property,value))
     { g_jpw_ui_properties[slot].ready=false; return(false); }
   g_jpw_ui_properties[slot].name=name; g_jpw_ui_properties[slot].property=(long)property;
   g_jpw_ui_properties[slot].text_property=true; g_jpw_ui_properties[slot].text=value;
   g_jpw_ui_properties[slot].ready=true; g_jpw_ui_changed=true; g_jpw_ui_set_requests++;
   return(true);
  }
bool JPWUIDesignEnsure(const string name,const ENUM_OBJECT type)
  {
   // ObjectFind is the synchronization boundary. A queued create is insufficient.
   if(ObjectFind(0,name)>=0) return(ObjectGetInteger(0,name,OBJPROP_TYPE)==type);
   JPWUIDesignForget(name);
   if(!ObjectCreate(0,name,type,0,0,0)) return(false);
   g_jpw_ui_changed=true; g_jpw_ui_creates++;
   return(ObjectFind(0,name)>=0 && ObjectGetInteger(0,name,OBJPROP_TYPE)==type);
  }
bool JPWUIDesignDelete(const string name)
  {
   JPWUIDesignForget(name);
   if(ObjectFind(0,name)<0) return(true);
   const bool queued=ObjectDelete(0,name);
   if(queued) { g_jpw_ui_changed=true; g_jpw_ui_deletes++; }
   return(queued);
  }
void JPWUIDesignBeginPass()
  { if(g_jpw_ui_pass_depth==0) g_jpw_ui_changed=false; g_jpw_ui_pass_depth++; }
void JPWUIDesignEndPass()
  {
   if(g_jpw_ui_pass_depth<=0) return;
   g_jpw_ui_pass_depth--;
   if(g_jpw_ui_pass_depth==0 && g_jpw_ui_changed) ChartRedraw(0);
  }
bool JPWUIDesignDark(const color background)
  {
   const int c=(int)background;
   return(299*(c&255)+587*((c>>8)&255)+114*((c>>16)&255)<140000);
  }
color JPWUIDesignPrimaryFill(const color background) { return(C'48,79,112'); }
color JPWUIDesignPrimaryInk(const color background) { return(C'255,255,255'); }
color JPWUIDesignFocusInk(const color background)
  { return(JPWUIDesignDark(background) ? C'151,185,217' : C'48,79,112'); }
color JPWUIDesignSelectedFill(const color background)
  { return(JPWUIDesignDark(background) ? C'49,59,71' : C'221,232,244'); }
struct JPWUIDesignTextMeasure
  { string label; int font; int dpi; int width; bool ready; };
JPWUIDesignTextMeasure g_jpw_ui_text_measure[128];
struct JPWUIDesignIconState
  { string name; int size; color ink; bool channel; bool ready; };
JPWUIDesignIconState g_jpw_ui_icons[32];
int JPWUIDesignIconSlot(const string name)
  {
   for(int i=0;i<32;i++) if(g_jpw_ui_icons[i].name==name) return(i);
   for(int i=0;i<32;i++) if(g_jpw_ui_icons[i].name=="") return(i);
   return(-1); // Optional decoration: no unbounded resource allocation.
  }

// Presentation only: logical pixels, text measurement, decoration. No account,
// model, trading, preference or financial-record reads/writes live here.
double JPWUIDesignScale()
  {
   const int dpi=(int)TerminalInfoInteger(TERMINAL_SCREEN_DPI);
   return(dpi>0 ? (double)dpi/96.0 : 1.0);
  }
int JPWUIDesignPx(const int logical)
  { return(MathMax(1,(int)MathRound((double)logical*JPWUIDesignScale()))); }
int JPWUIDesignControlHeight(const int measured_text_height)
  { return(MathMax(JPWUIDesignPx(32),measured_text_height+JPWUIDesignPx(16))); }
int JPWUIDesignTextWidth(const string label,const int font)
  {
   const int dpi=(int)TerminalInfoInteger(TERMINAL_SCREEN_DPI);
   // Keep the existing font-selection side effect even on a cached measurement.
   const bool font_ok=TextSetFont("Arial",-10*font,FW_NORMAL);
   const int slot=(int)(JPWUIDesignHash(label+"|"+IntegerToString(font)+"|"+IntegerToString(dpi))%128);
   if(font_ok && g_jpw_ui_text_measure[slot].ready && g_jpw_ui_text_measure[slot].label==label &&
      g_jpw_ui_text_measure[slot].font==font && g_jpw_ui_text_measure[slot].dpi==dpi)
      return(g_jpw_ui_text_measure[slot].width);
   uint width=0,height=0;
   if(font_ok && TextGetSize(label,width,height))
     {
      g_jpw_ui_text_measure[slot].label=label; g_jpw_ui_text_measure[slot].font=font;
      g_jpw_ui_text_measure[slot].dpi=dpi; g_jpw_ui_text_measure[slot].width=(int)width;
      g_jpw_ui_text_measure[slot].ready=true; return((int)width);
     }
   return(StringLen(label)*MathMax(JPWUIDesignPx(8),font));
  }
int JPWUIDesignButtonWidth(const string label,const int font,const bool icon=false)
  { return(JPWUIDesignTextWidth(label,font)+JPWUIDesignPx(24)+(icon ? JPWUIDesignPx(28) : 0)); }

// Choose a grid by actual label extents, including short final rows. Text font
// is already in logical points; DPI is applied only to geometric padding.
int JPWUIDesignNavColumns(string &labels[],const int count,const int inner,
                         const int font,const int gap)
  {
   if(count<1 || inner<1) return(1);
   for(int columns=count;columns>1;columns--)
     {
      const int width=(inner-(columns-1)*gap)/columns;
      bool fits=(width>0);
      for(int i=0;i<count && fits;i++)
         if(JPWUIDesignButtonWidth(labels[i],font)>width) fits=false;
      if(fits) return(columns);
     }
   return(1);
  }

string JPWUIDesignIconResource(const string name)
  {
   uint hash=2166136261;
   for(int i=0;i<StringLen(name);i++)
      hash=(hash^(uint)StringGetCharacter(name,i))*16777619;
   return("JPWDI_"+IntegerToString((long)hash));
  }
void JPWUIDesignIconSegment(uint &pixels[],const int size,
                            const double ax,const double ay,const double bx,const double by,
                            const double stroke,const uint argb)
  {
   const double vx=bx-ax,vy=by-ay,len2=vx*vx+vy*vy;
   const double radius=stroke/2.0;
   for(int y=0;y<size;y++) for(int x=0;x<size;x++)
     {
      double t=(len2>0 ? (((double)x+0.5-ax)*vx+((double)y+0.5-ay)*vy)/len2 : 0);
      t=MathMax(0.0,MathMin(1.0,t));
      const double dx=(double)x+0.5-(ax+t*vx),dy=(double)y+0.5-(ay+t*vy);
      const double distance=MathSqrt(dx*dx+dy*dy);
      const double coverage=MathMax(0.0,MathMin(1.0,radius+0.5-distance));
      const uint alpha=(uint)MathRound(255.0*coverage);
      const uint old_alpha=pixels[y*size+x]>>24;
      if(alpha>old_alpha) pixels[y*size+x]=(argb&0x00FFFFFF)|(alpha<<24);
     }
  }
bool JPWUIDesignIcon(const string name,const int x,const int y,const int size,
                     const color ink,const bool channel)
  {
   if(size<8 || size>128) return(false);
   const int slot=JPWUIDesignIconSlot(name);
   if(slot<0) return(false);
   const bool reusable=(g_jpw_ui_icons[slot].ready && g_jpw_ui_icons[slot].size==size &&
      g_jpw_ui_icons[slot].ink==ink && g_jpw_ui_icons[slot].channel==channel);
   const string resource=JPWUIDesignIconResource(name);
   if(!reusable)
     {
   uint pixels[];
   if(ArrayResize(pixels,size*size)!=size*size) return(false);
   ArrayInitialize(pixels,0);
   const double scale=(double)size/24.0,stroke=1.75*scale;
   const uint argb=ColorToARGB(ink,255);
   if(channel)
     {
      for(int i=0;i<3;i++)
         JPWUIDesignIconSegment(pixels,size,4*scale,(9+5*i)*scale,
                               20*scale,(4+5*i)*scale,stroke,argb);
     }
   else
     {
      JPWUIDesignIconSegment(pixels,size,4*scale,4*scale,20*scale,4*scale,stroke,argb);
      JPWUIDesignIconSegment(pixels,size,20*scale,4*scale,20*scale,20*scale,stroke,argb);
      JPWUIDesignIconSegment(pixels,size,20*scale,20*scale,4*scale,20*scale,stroke,argb);
      JPWUIDesignIconSegment(pixels,size,4*scale,20*scale,4*scale,4*scale,stroke,argb);
      for(int i=0;i<3;i++)
         JPWUIDesignIconSegment(pixels,size,8*scale,(8+4*i)*scale,
                               (i==1 ? 14 : 16)*scale,(8+4*i)*scale,stroke,argb);
     }
   if(!ResourceCreate(resource,pixels,size,size,0,0,size,COLOR_FORMAT_ARGB_NORMALIZE))
     { g_jpw_ui_icons[slot].ready=false; return(false); }
   g_jpw_ui_icons[slot].name=name; g_jpw_ui_icons[slot].size=size;
   g_jpw_ui_icons[slot].ink=ink; g_jpw_ui_icons[slot].channel=channel;
   g_jpw_ui_icons[slot].ready=true; g_jpw_ui_changed=true;
     }
   if(!JPWUIDesignEnsure(name,OBJ_BITMAP_LABEL))
     { ResourceFree(resource); g_jpw_ui_icons[slot].ready=false; return(false); }
   bool properties_ok=true;
   properties_ok=JPWUIDesignSetInteger(name,OBJPROP_CORNER,CORNER_LEFT_UPPER) && properties_ok;
   properties_ok=JPWUIDesignSetInteger(name,OBJPROP_ANCHOR,ANCHOR_LEFT_UPPER) && properties_ok;
   properties_ok=JPWUIDesignSetInteger(name,OBJPROP_XDISTANCE,x) && properties_ok;
   properties_ok=JPWUIDesignSetInteger(name,OBJPROP_YDISTANCE,y) && properties_ok;
   properties_ok=JPWUIDesignSetInteger(name,OBJPROP_XSIZE,size) && properties_ok;
   properties_ok=JPWUIDesignSetInteger(name,OBJPROP_YSIZE,size) && properties_ok;
   properties_ok=JPWUIDesignSetInteger(name,OBJPROP_BACK,false) && properties_ok;
   properties_ok=JPWUIDesignSetInteger(name,OBJPROP_ZORDER,3) && properties_ok;
   properties_ok=JPWUIDesignSetInteger(name,OBJPROP_SELECTABLE,false) && properties_ok;
   properties_ok=JPWUIDesignSetInteger(name,OBJPROP_HIDDEN,true) && properties_ok;
   properties_ok=JPWUIDesignSetString(name,OBJPROP_BMPFILE,"::"+resource) && properties_ok;
   properties_ok=JPWUIDesignSetString(name,OBJPROP_TOOLTIP,"\n") && properties_ok;
   if(!properties_ok)
     {
      JPWUIDesignDelete(name); ResourceFree(resource);
      g_jpw_ui_icons[slot].ready=false;
      return(false); // Decoration failed; caller keeps its textual action.
     }
   return(ObjectFind(0,name)>=0);
  }
void JPWUIDesignDeleteIcon(const string name)
  {
   JPWUIDesignDelete(name); ResourceFree(JPWUIDesignIconResource(name));
   const int slot=JPWUIDesignIconSlot(name);
   if(slot>=0) { g_jpw_ui_icons[slot].name=""; g_jpw_ui_icons[slot].ready=false; }
  }

#endif
