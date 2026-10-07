#ifndef JPW_UI_DESIGN_MQH
#define JPW_UI_DESIGN_MQH

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
   uint width=0,height=0;
   if(TextSetFont("Arial",-10*font,FW_NORMAL) && TextGetSize(label,width,height))
      return((int)width);
   // Measurement failure must not shrink an essential action to a tiny target.
   return(StringLen(label)*MathMax(JPWUIDesignPx(8),font));
  }
int JPWUIDesignButtonWidth(const string label,const int font,const bool icon=false)
  { return(JPWUIDesignTextWidth(label,font)+JPWUIDesignPx(24)+(icon ? JPWUIDesignPx(24) : 0)); }

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
   const string resource=JPWUIDesignIconResource(name);
   if(!ResourceCreate(resource,pixels,size,size,0,0,size,COLOR_FORMAT_ARGB_NORMALIZE)) return(false);
   if(ObjectFind(0,name)<0 && !ObjectCreate(0,name,OBJ_BITMAP_LABEL,0,0,0))
     { ResourceFree(resource); return(false); }
   ObjectSetInteger(0,name,OBJPROP_CORNER,CORNER_LEFT_UPPER);
   ObjectSetInteger(0,name,OBJPROP_ANCHOR,ANCHOR_LEFT_UPPER);
   ObjectSetInteger(0,name,OBJPROP_XDISTANCE,x);
   ObjectSetInteger(0,name,OBJPROP_YDISTANCE,y);
   ObjectSetInteger(0,name,OBJPROP_XSIZE,size);
   ObjectSetInteger(0,name,OBJPROP_YSIZE,size);
   ObjectSetInteger(0,name,OBJPROP_BACK,false);
   ObjectSetInteger(0,name,OBJPROP_ZORDER,3);
   ObjectSetInteger(0,name,OBJPROP_SELECTABLE,false);
   ObjectSetInteger(0,name,OBJPROP_HIDDEN,true);
   ObjectSetString(0,name,OBJPROP_BMPFILE,"::"+resource);
   ObjectSetString(0,name,OBJPROP_TOOLTIP,"\n");
   return(true);
  }
void JPWUIDesignDeleteIcon(const string name)
  { ObjectDelete(0,name); ResourceFree(JPWUIDesignIconResource(name)); }

#endif
