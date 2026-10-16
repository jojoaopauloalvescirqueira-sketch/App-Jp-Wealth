#ifndef JPW_GENETRIX_BRAND_MQH
#define JPW_GENETRIX_BRAND_MQH
#include <JPWealth/JPW_Alavancagem_Version.mqh>
#include <JPWealth/JPW_UI_Design.mqh>

// Presentation only. Approved Stoikus by JP Wealth signature; the original
// red institutional wordmark is embedded without redrawing its lettering.
// No account reads, preferences, financial records or model state live here.
#resource "\\Images\\JPWealth\\JPW_Stoikus_Logo_Light_100.bmp"
#resource "\\Images\\JPWealth\\JPW_Stoikus_Logo_Light_125.bmp"
#resource "\\Images\\JPWealth\\JPW_Stoikus_Logo_Light_150.bmp"
#resource "\\Images\\JPWealth\\JPW_Stoikus_Logo_Light_200.bmp"
#resource "\\Images\\JPWealth\\JPW_Stoikus_Logo_Dark_100.bmp"
#resource "\\Images\\JPWealth\\JPW_Stoikus_Logo_Dark_125.bmp"
#resource "\\Images\\JPWealth\\JPW_Stoikus_Logo_Dark_150.bmp"
#resource "\\Images\\JPWealth\\JPW_Stoikus_Logo_Dark_200.bmp"

int JPWGenetrixTextWidth(const string text,const int font)
  { return(JPWUIDesignTextWidth(text,font)); }

string JPWGenetrixHeaderText(const string section,const int width,const int font)
  {
   const string full=(string)JPW_PRODUCT_NAME+" by JP Wealth"+(section=="" ? "" : " · "+section);
   if(JPWGenetrixTextWidth(full,font)<=width) return(full);
   const string compact=JPW_PRODUCT_NAME+(section=="" ? "" : " · "+section);
   if(JPWGenetrixTextWidth(compact,font)<=width) return(compact);
   // Location/function comes before optional branding. Never spend the scarce
   // title area on only the product name when the complete section still fits.
   if(section!="" && JPWGenetrixTextWidth(section,font)<=width) return(section);
   if(section!="")
     {
      const int first=StringFind(section," · ");
      const int last=(first>=0 ? StringFind(section," · ",first+3) : -1);
      // Hide an instrument suffix before discarding the functional section.
      const string functional=(last>0 ? StringSubstr(section,0,last) : section);
      if(JPWGenetrixTextWidth(functional,font)<=width) return(functional);
      const int separator=StringFind(section," · ");
      const string module=(separator>0 ? StringSubstr(section,0,separator) : section);
      if(JPWGenetrixTextWidth(module,font)<=width) return(module);
     }
   if(section=="" && JPWGenetrixTextWidth(JPW_PRODUCT_NAME,font)<=width) return(JPW_PRODUCT_NAME);
   return(""); // An independent exit remains available in reduced layouts.
  }

bool JPWGenetrixHeader(const string logo_name,const string text_name,
                       const int x,const int y,const int width,const int height,
                       const int font,const color ink,const bool dark,
                       const string section,const int zorder=4)
  {
   if(width<=0 || height<=0)
     { JPWUIDesignDelete(logo_name); JPWUIDesignDelete(text_name); return(false); }
   const int screen_dpi=(int)TerminalInfoInteger(TERMINAL_SCREEN_DPI);
   const int variant=(screen_dpi>=168 ? 3 : (screen_dpi>=132 ? 2 : (screen_dpi>=108 ? 1 : 0)));
   int widths[4]={240,300,360,480},heights[4]={28,35,42,56};
   string scales[4]={"100","125","150","200"};
   // Do not shrink the endorsement at high DPI to force decoration into a
   // short slot. The functional title remains the measured textual fallback.
   const int gap=(section!="" ? JPWUIDesignPx(12) : 0);
   const string identity=(string)JPW_PRODUCT_NAME+" by JP Wealth";
   const string full=identity+(section=="" ? "" : " · "+section);
   const int label_width=(section!="" ? JPWGenetrixTextWidth(section,font) : 0);
   bool branded=false;
   if(height>=heights[variant] && width>=widths[variant]+gap+label_width)
     {
      const string resource=(string)"::Images\\JPWealth\\JPW_Stoikus_Logo_"+
         (dark ? "Dark_" : "Light_")+scales[variant]+".bmp";
      branded=JPWUIDesignEnsure(logo_name,OBJ_BITMAP_LABEL) &&
         JPWUIDesignSetString(logo_name,OBJPROP_BMPFILE,resource);
      if(branded)
        {
         bool complete=true;
         complete=JPWUIDesignSetInteger(logo_name,OBJPROP_CORNER,CORNER_LEFT_UPPER) && complete;
         complete=JPWUIDesignSetInteger(logo_name,OBJPROP_ANCHOR,ANCHOR_LEFT_UPPER) && complete;
         complete=JPWUIDesignSetInteger(logo_name,OBJPROP_XDISTANCE,x) && complete;
         complete=JPWUIDesignSetInteger(logo_name,OBJPROP_YDISTANCE,y+(height-heights[variant])/2) && complete;
         complete=JPWUIDesignSetInteger(logo_name,OBJPROP_XSIZE,widths[variant]) && complete;
         complete=JPWUIDesignSetInteger(logo_name,OBJPROP_YSIZE,heights[variant]) && complete;
         complete=JPWUIDesignSetInteger(logo_name,OBJPROP_SELECTABLE,false) && complete;
         complete=JPWUIDesignSetInteger(logo_name,OBJPROP_HIDDEN,true) && complete;
         complete=JPWUIDesignSetInteger(logo_name,OBJPROP_BACK,false) && complete;
         complete=JPWUIDesignSetInteger(logo_name,OBJPROP_ZORDER,zorder) && complete;
         complete=JPWUIDesignSetString(logo_name,OBJPROP_TOOLTIP,identity) && complete;
         branded=complete;
        }
     }
   if(!branded) JPWUIDesignDelete(logo_name);
   const int offset=(branded ? widths[variant]+gap : 0);
   const string caption=(branded ? section : JPWGenetrixHeaderText(section,width-offset,font));
   if(caption=="") { JPWUIDesignDelete(text_name); return(branded); }
   if(!JPWUIDesignEnsure(text_name,OBJ_LABEL)) return(branded);
   JPWUIDesignSetInteger(text_name,OBJPROP_CORNER,CORNER_LEFT_UPPER);
   JPWUIDesignSetInteger(text_name,OBJPROP_ANCHOR,ANCHOR_LEFT_UPPER);
   JPWUIDesignSetInteger(text_name,OBJPROP_XDISTANCE,x+offset);
   uint title_width=0,title_height=0;
   const bool measured=TextSetFont("Arial",-10*font) && TextGetSize("Ag",title_width,title_height);
   const int title_offset=(measured ? MathMax(0,(height-(int)title_height)/2) : 0);
   JPWUIDesignSetInteger(text_name,OBJPROP_YDISTANCE,y+title_offset);
   JPWUIDesignSetInteger(text_name,OBJPROP_XSIZE,width-offset);
   JPWUIDesignSetInteger(text_name,OBJPROP_YSIZE,height);
   JPWUIDesignSetInteger(text_name,OBJPROP_FONTSIZE,font);
   JPWUIDesignSetInteger(text_name,OBJPROP_COLOR,ink);
   JPWUIDesignSetInteger(text_name,OBJPROP_SELECTABLE,false);
   JPWUIDesignSetInteger(text_name,OBJPROP_HIDDEN,true);
   JPWUIDesignSetInteger(text_name,OBJPROP_ZORDER,zorder);
   JPWUIDesignSetString(text_name,OBJPROP_FONT,"Arial");
   JPWUIDesignSetString(text_name,OBJPROP_TEXT,caption);
   JPWUIDesignSetString(text_name,OBJPROP_TOOLTIP,full);
   return(branded);
  }
#endif
