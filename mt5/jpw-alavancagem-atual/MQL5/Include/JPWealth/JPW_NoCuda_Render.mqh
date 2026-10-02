#ifndef JPW_NOCUDA_RENDER_MQH
#define JPW_NOCUDA_RENDER_MQH

#include <Canvas\Canvas.mqh>
#include <JPWealth/JPW_NoCuda_Core.mqh>
#include <JPWealth/JPW_NoCuda_Terminal.mqh>
#include <JPWealth/JPW_NoCuda_Projection.mqh>

void JPWNoCudaRemoveDailyReferences(const string prefix)
  {
   for(int i=ObjectsTotal(0,0,-1)-1;i>=0;i--)
     {
      const string name=ObjectName(0,i,0,-1);
      if(StringFind(name,prefix+"DRAW_LABEL_REF_")==0) ObjectDelete(0,name);
     }
  }

// Dates are never placed using an invented screen calendar. A successful
// forward conversion alone is insufficient: all three dates must survive the
// inverse mapping in the main viewport and occupy distinguishable pixels.
bool JPWNoCudaReferencePoint(const datetime at,const double price,
                            int &x,int &y)
  {
   const int w=(int)ChartGetInteger(0,CHART_WIDTH_IN_PIXELS);
   const int h=(int)ChartGetInteger(0,CHART_HEIGHT_IN_PIXELS);
   if(!ChartTimePriceToXY(0,0,at,price,x,y) || x<0 || x>=w || y<0 || y>=h)
      return(false);
   int subwindow=0;
   datetime restored=0,neighbor_time=0;
   double restored_price=0.0,neighbor_price=0.0;
   if(!ChartXYToTimePrice(0,x,y,subwindow,restored,restored_price) ||
      subwindow!=0 || restored!=at || !MathIsValidNumber(restored_price) ||
      !ChartXYToTimePrice(0,x,(y<h-1 ? y+1 : y-1),subwindow,
                           neighbor_time,neighbor_price) ||
      subwindow!=0 || !MathIsValidNumber(neighbor_price)) return(false);
   const double tolerance=MathAbs(neighbor_price-restored_price)*0.51+
                          MathAbs(price)*1.0e-12;
   return(MathAbs(restored_price-price)<=tolerance);
  }

bool JPWNoCudaDrawDailyReferences(const string prefix,
                                 const JPWNoCudaDailyResult &daily,
                                 string &reason)
  {
   JPWNoCudaRemoveDailyReferences(prefix);
   if(!daily.valid)
     { reason="Consulta diária indisponível; referências somente no menu.";
       return(false); }
   int x0=0,y0=0,x12=0,y12=0,x24=0,y24=0;
   uint label_width=0,label_height=0;
   int separation=40;
   if(TextSetFont("Arial",-80) && TextGetSize("24h",label_width,label_height))
      separation=MathMax(separation,(int)label_width+8);
   if(!JPWNoCudaReferencePoint(daily.day,daily.start_price,x0,y0) ||
      !JPWNoCudaReferencePoint(daily.day+43200,daily.mid_price,x12,y12) ||
      !JPWNoCudaReferencePoint(daily.day+86400,daily.end_price,x24,y24) ||
      x12-x0<separation || x24-x12<separation)
     { reason="Datas fora da tela ou sem projeção visual exata: consulte o menu.";
       return(false); }
   const int packed=(int)ChartGetInteger(0,CHART_COLOR_BACKGROUND);
   const bool dark=(299*(packed&255)+587*((packed>>8)&255)+114*((packed>>16)&255)<140000);
   const color ink=(dark ? C'224,200,118' : C'132,100,24');
   JPWNoCudaDrawMilestone(prefix,"REF_00h",daily.day,daily.start_price,ink);
   JPWNoCudaDrawMilestone(prefix,"REF_12h",daily.day+43200,daily.mid_price,ink);
   JPWNoCudaDrawMilestone(prefix,"REF_24h",daily.day+86400,daily.end_price,ink);
   reason="Referências 00h / 12h / 24h verificadas na área do gráfico.";
   return(true);
  }

void JPWNoCudaRemoveDrawingObjects(const string prefix)
  {
   for(int i=ObjectsTotal(0,0,-1)-1;i>=0;i--)
     {
      const string name=ObjectName(0,i,0,-1);
      if(StringFind(name,prefix+"DRAW_")==0) ObjectDelete(0,name);
     }
  }

void JPWNoCudaDrawAnchor(const string prefix,const string id,
                        const datetime opened,const double closed,
                        const color ink,const bool editable)
  {
   const string name=prefix+"DRAW_ANCHOR_"+id;
   if(opened<=0 || !MathIsValidNumber(closed) || closed<=0.0)
     { ObjectDelete(0,name); return; }
   if(ObjectFind(0,name)<0 && !ObjectCreate(0,name,OBJ_ARROW,0,opened,closed)) return;
   ObjectMove(0,name,0,opened,closed);
   ObjectSetInteger(0,name,OBJPROP_ARROWCODE,159);
   ObjectSetInteger(0,name,OBJPROP_COLOR,ink);
   ObjectSetInteger(0,name,OBJPROP_WIDTH,2);
   ObjectSetInteger(0,name,OBJPROP_SELECTABLE,editable);
   ObjectSetInteger(0,name,OBJPROP_SELECTED,false);
   ObjectSetInteger(0,name,OBJPROP_HIDDEN,true);
   ObjectSetString(0,name,OBJPROP_TOOLTIP,id+" · Close "+DoubleToString(closed,_Digits));
  }

void JPWNoCudaDrawMilestone(const string prefix,const string id,
                           const datetime opened,const double value,
                           const color ink)
  {
   const string name=prefix+"DRAW_LABEL_"+id;
   if(opened<=0 || !MathIsValidNumber(value))
     { ObjectDelete(0,name); return; }
   if(ObjectFind(0,name)<0 && !ObjectCreate(0,name,OBJ_TEXT,0,opened,value)) return;
   ObjectMove(0,name,0,opened,value);
   ObjectSetInteger(0,name,OBJPROP_COLOR,ink);
   ObjectSetInteger(0,name,OBJPROP_FONTSIZE,8);
   ObjectSetInteger(0,name,OBJPROP_ANCHOR,ANCHOR_LEFT);
   ObjectSetInteger(0,name,OBJPROP_SELECTABLE,false);
   ObjectSetInteger(0,name,OBJPROP_HIDDEN,true);
   const bool reference=(StringFind(id,"REF_")==0);
   ObjectSetString(0,name,OBJPROP_TEXT,reference ? StringSubstr(id,4) : id);
   ObjectSetString(0,name,OBJPROP_TOOLTIP,reference ?
      "NoCuda · horário do servidor · "+TimeToString(opened,TIME_DATE|TIME_MINUTES)+
      " · "+DoubleToString(value,_Digits) : "NoCuda · nível "+id);
  }

// All vertices use source-bar ordinals. ChartTimePriceToXY is only a view
// projection; chart timeframe never enters slope/width arithmetic.
bool JPWNoCudaCanvasPaint(CCanvas &canvas,bool &canvas_ready,
                          const string prefix,const string symbol,
                          const ENUM_TIMEFRAMES source_tf,
                          const datetime a_open,const double a_close,
                          const datetime b_open,const double b_close,
                          const datetime c_open,const double c_close,
                          const JPWNoCudaGeometry &geometry,
                          const bool has_geometry,const bool full_mesh,
                          const bool channel_visible,const bool editable,
                          const int selected_level,
                          string &reason)
  {
   const int width=(int)ChartGetInteger(0,CHART_WIDTH_IN_PIXELS);
   const int height=(int)ChartGetInteger(0,CHART_HEIGHT_IN_PIXELS);
   if(width<20 || height<20)
     { reason="Gráfico pequeno demais."; return(false); }
   if(!canvas_ready || canvas.Width()!=width || canvas.Height()!=height)
     {
      if(canvas_ready) canvas.Destroy();
      canvas_ready=canvas.CreateBitmapLabel(0,0,prefix+"CANVAS",0,0,width,height,
                                            COLOR_FORMAT_ARGB_NORMALIZE);
      if(!canvas_ready)
        { reason="Camada gráfica indisponível."; return(false); }
      ObjectSetInteger(0,prefix+"CANVAS",OBJPROP_BACK,true);
      ObjectSetInteger(0,prefix+"CANVAS",OBJPROP_SELECTABLE,false);
      ObjectSetInteger(0,prefix+"CANVAS",OBJPROP_HIDDEN,true);
     }
   canvas.Erase(0x00000000);
   JPWNoCudaRemoveDrawingObjects(prefix);
   if(!channel_visible)
     { canvas.Update(); reason="Canal oculto."; return(true); }
   const color chart_bg=(color)ChartGetInteger(0,CHART_COLOR_BACKGROUND);
   const int packed=(int)chart_bg;
   const bool dark=(299*(packed&255)+587*((packed>>8)&255)+114*((packed>>16)&255)<140000);
   const color ink=(dark ? C'189,213,231' : C'74,100,122');
   JPWNoCudaDrawAnchor(prefix,"A",a_open,a_close,ink,editable);
   JPWNoCudaDrawAnchor(prefix,"B",b_open,b_close,ink,editable);
   JPWNoCudaDrawAnchor(prefix,"C",c_open,c_close,ink,editable);
   if(!has_geometry || a_open<=0 || b_open<=0 || c_open<=0)
     { canvas.Update(); reason="Marque A, B e C para conferir a malha."; return(true); }

   int anchor_shift=0;
   double verified_close=0.0;
   datetime known_after=0;
   if(!JPWNoCudaExactBar(symbol,source_tf,a_open,anchor_shift,verified_close,known_after))
     { canvas.Update(); reason="Âncora A não consta no histórico-fonte."; return(false); }
   MqlRates bars[];
   int first_shift=0;
   if(!JPWNoCudaVisibleBars(symbol,source_tf,bars,first_shift,reason))
     { canvas.Update(); return(false); }

   int last_x[65],last_y[65];
   bool last_valid[65];
   for(int k=0;k<65;k++) last_valid[k]=false;
   const int total=ArraySize(bars);
   if(total<1)
     { canvas.Update(); reason="Faixa observada vazia."; return(false); }
   JPWNoCudaProjectionTimeline timeline;
   if(!JPWNoCudaProjectionLoadTimeline(symbol,source_tf,a_open,bars[0].time,
       bars[total-1].time,timeline,reason))
     { canvas.Update(); return(false); }
   JPWNoCudaTimePoint resolved;
   int last_visible=-1;
   int last_drawn_x=-2147483647;
   for(int i=0;i<total;i++)
     {
      if(!JPWNoCudaProjectionResolveValidated(timeline.opens,timeline.observed_count,
         a_open,geometry,0.0,bars[i].time,PeriodSeconds(source_tf),timeline.sessions,
         false,resolved,reason))
        { canvas.Erase(0x00000000); canvas.Update(); return(false); }
      const double ordinal=resolved.ordinal;
      double p0=0.0,p1=0.0;
      if(!JPWNoCudaPriceAt(geometry,0.0,(double)ordinal,p0) ||
         !JPWNoCudaPriceAt(geometry,1.0,(double)ordinal,p1)) continue;
      int x0=0,y0=0,x1=0,y1=0;
      if(!ChartTimePriceToXY(0,0,bars[i].time,p0,x0,y0) ||
         !ChartTimePriceToXY(0,0,bars[i].time,p1,x1,y1)) continue;
      if(x0>=0 && x0<width) last_visible=i;
      // When many H1 bars occupy one display pixel, retain one vertex for
      // that pixel. Full source ordinals and the signed geometry are unchanged.
      if(x0==last_drawn_x && i<total-1) continue;
      last_drawn_x=x0;
      for(int k=0;k<65;k++)
        {
         if(!full_mesh && k!=32 && k!=36 && k!=40 && k!=selected_level) continue;
         double level=0.0;
         if(!JPWNoCudaLevelValue(k,level)) continue;
         const int yy=(int)MathRound((double)y0+level*((double)y1-(double)y0));
         const bool major=(k==32 || k==36 || k==40);
         const uint rgba=ColorToARGB(ink,(uchar)(k==selected_level ? 245 :
                                             (major ? 190 : 62)));
         if(last_valid[k] && (x0>=0 || last_x[k]>=0) &&
            (x0<width || last_x[k]<width) &&
            (yy>=0 || last_y[k]>=0) && (yy<height || last_y[k]<height))
            canvas.Line(last_x[k],last_y[k],x0,yy,rgba);
         last_x[k]=x0;
         last_y[k]=yy;
         last_valid[k]=true;
        }
     }
   canvas.Update();
   if(last_visible>=0)
     {
      const datetime end_time=bars[last_visible].time;
      if(!JPWNoCudaProjectionResolveValidated(timeline.opens,timeline.observed_count,
         a_open,geometry,0.0,end_time,PeriodSeconds(source_tf),timeline.sessions,
         false,resolved,reason))
        { reason="Ordinal-fonte indisponível."; return(false); }
      const double end_ordinal=resolved.ordinal;
      double price=0.0;
      if(JPWNoCudaPriceAt(geometry,0.0,(double)end_ordinal,price))
         JPWNoCudaDrawMilestone(prefix,"0",end_time,price,ink);
      if(JPWNoCudaPriceAt(geometry,0.5,(double)end_ordinal,price))
         JPWNoCudaDrawMilestone(prefix,"0.5",end_time,price,ink);
      if(JPWNoCudaPriceAt(geometry,1.0,(double)end_ordinal,price))
         JPWNoCudaDrawMilestone(prefix,"1",end_time,price,ink);
     }
   reason="";
   return(true);
  }

#endif
