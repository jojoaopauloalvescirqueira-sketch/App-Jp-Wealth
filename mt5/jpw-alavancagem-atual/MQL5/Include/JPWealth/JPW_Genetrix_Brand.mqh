#ifndef JPW_GENETRIX_BRAND_MQH
#define JPW_GENETRIX_BRAND_MQH
#include <JPWealth/JPW_Alavancagem_Version.mqh>

// Presentation only. The bitmap is derived from the existing website wordmark.
// No account reads, preferences, financial records or model state live here.
#resource "\\Images\\JPWealth\\JPW_Genetrix_Logo_Light_100.bmp"
#resource "\\Images\\JPWealth\\JPW_Genetrix_Logo_Light_125.bmp"
#resource "\\Images\\JPWealth\\JPW_Genetrix_Logo_Light_150.bmp"
#resource "\\Images\\JPWealth\\JPW_Genetrix_Logo_Light_200.bmp"
#resource "\\Images\\JPWealth\\JPW_Genetrix_Logo_Dark_100.bmp"
#resource "\\Images\\JPWealth\\JPW_Genetrix_Logo_Dark_125.bmp"
#resource "\\Images\\JPWealth\\JPW_Genetrix_Logo_Dark_150.bmp"
#resource "\\Images\\JPWealth\\JPW_Genetrix_Logo_Dark_200.bmp"

int JPWGenetrixTextWidth(const string text,const int font)
  {
   uint width=0,height=0;
   if(TextSetFont("Arial",-10*font) && TextGetSize(text,width,height)) return((int)width);
   return(StringLen(text)*MathMax(6,font));
  }

string JPWGenetrixHeaderText(const string section,const int width,const int font)
  {
   const string full=JPW_PRODUCT_NAME+(section=="" ? "" : " · "+section);
   if(JPWGenetrixTextWidth(full,font)<=width) return(full);
   if(JPWGenetrixTextWidth(JPW_PRODUCT_NAME,font)<=width) return(JPW_PRODUCT_NAME);
   if(JPWGenetrixTextWidth("GENETRIX",font)<=width) return("GENETRIX");
   if(JPWGenetrixTextWidth("JPW",font)<=width) return("JPW");
   return(""); // The escape control remains independent of this small title area.
  }

bool JPWGenetrixHeader(const string logo_name,const string text_name,
                       const int x,const int y,const int width,const int height,
                       const int font,const color ink,const bool dark,
                       const string section,const int zorder=4)
  {
   if(width<=0 || height<=0)
     { ObjectDelete(0,logo_name); ObjectDelete(0,text_name); return(false); }
   const int screen_dpi=(int)TerminalInfoInteger(TERMINAL_SCREEN_DPI);
   int variant=(screen_dpi>=168 ? 3 : (screen_dpi>=132 ? 2 : (screen_dpi>=108 ? 1 : 0)));
   int widths[4]={147,184,221,295},heights[4]={16,20,24,32};
   string scales[4]={"100","125","150","200"};
   while(variant>0 && heights[variant]>height) variant--;
   const int gap=MathMax(8,font);
   const string full=JPW_PRODUCT_NAME+(section=="" ? "" : " · "+section);
   const int label_width=JPWGenetrixTextWidth(JPW_PRODUCT_NAME,font);
   bool branded=false;
   if(height>=heights[variant] && width>=widths[variant]+gap+label_width)
     {
      const string resource=(string)"::Images\\JPWealth\\JPW_Genetrix_Logo_"+
         (dark ? "Dark_" : "Light_")+scales[variant]+".bmp";
      if(ObjectFind(0,logo_name)<0) ObjectCreate(0,logo_name,OBJ_BITMAP_LABEL,0,0,0);
      branded=ObjectFind(0,logo_name)>=0 &&
         ObjectSetString(0,logo_name,OBJPROP_BMPFILE,resource);
      if(branded)
        {
         ObjectSetInteger(0,logo_name,OBJPROP_CORNER,CORNER_LEFT_UPPER);
         ObjectSetInteger(0,logo_name,OBJPROP_ANCHOR,ANCHOR_LEFT_UPPER);
         ObjectSetInteger(0,logo_name,OBJPROP_XDISTANCE,x);
         ObjectSetInteger(0,logo_name,OBJPROP_YDISTANCE,y+(height-heights[variant])/2);
         ObjectSetInteger(0,logo_name,OBJPROP_XSIZE,widths[variant]);
         ObjectSetInteger(0,logo_name,OBJPROP_YSIZE,heights[variant]);
         ObjectSetInteger(0,logo_name,OBJPROP_SELECTABLE,false);
         ObjectSetInteger(0,logo_name,OBJPROP_HIDDEN,true);
         ObjectSetInteger(0,logo_name,OBJPROP_BACK,false);
         ObjectSetInteger(0,logo_name,OBJPROP_ZORDER,zorder);
         ObjectSetString(0,logo_name,OBJPROP_TOOLTIP,JPW_PRODUCT_NAME);
        }
     }
   if(!branded) ObjectDelete(0,logo_name);
   const int offset=(branded ? widths[variant]+gap : 0);
   const string caption=JPWGenetrixHeaderText(section,width-offset,font);
   if(caption=="") { ObjectDelete(0,text_name); return(branded); }
   if(ObjectFind(0,text_name)<0) ObjectCreate(0,text_name,OBJ_LABEL,0,0,0);
   if(ObjectFind(0,text_name)<0) return(branded);
   ObjectSetInteger(0,text_name,OBJPROP_CORNER,CORNER_LEFT_UPPER);
   ObjectSetInteger(0,text_name,OBJPROP_ANCHOR,ANCHOR_LEFT_UPPER);
   ObjectSetInteger(0,text_name,OBJPROP_XDISTANCE,x+offset);
   ObjectSetInteger(0,text_name,OBJPROP_YDISTANCE,y);
   ObjectSetInteger(0,text_name,OBJPROP_XSIZE,width-offset);
   ObjectSetInteger(0,text_name,OBJPROP_YSIZE,height);
   ObjectSetInteger(0,text_name,OBJPROP_FONTSIZE,font);
   ObjectSetInteger(0,text_name,OBJPROP_COLOR,ink);
   ObjectSetInteger(0,text_name,OBJPROP_SELECTABLE,false);
   ObjectSetInteger(0,text_name,OBJPROP_HIDDEN,true);
   ObjectSetInteger(0,text_name,OBJPROP_ZORDER,zorder);
   ObjectSetString(0,text_name,OBJPROP_FONT,"Arial");
   ObjectSetString(0,text_name,OBJPROP_TEXT,caption);
   ObjectSetString(0,text_name,OBJPROP_TOOLTIP,full);
   return(branded);
  }
#endif
