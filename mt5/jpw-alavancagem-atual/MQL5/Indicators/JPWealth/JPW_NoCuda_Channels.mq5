#property copyright "JP Wealth"
#property version   "1.30"
#property description "JPW GENETRIX · NoCuda: Fibonacci nativo como editor; estudos manuais preservados."
#property indicator_chart_window
#property indicator_buffers 0
#property indicator_plots 0

#include <JPWealth/JPW_Alavancagem_Version.mqh>
#include <JPWealth/JPW_NoCuda_Core.mqh>
#include <JPWealth/JPW_NoCuda_Terminal.mqh>
#include <JPWealth/JPW_NoCuda_Projection.mqh>
#include <JPWealth/JPW_NoCuda_Store.mqh>
#include <JPWealth/JPW_NoCuda_Render.mqh>
#include <JPWealth/JPW_NoCuda_UI.mqh>

input ENUM_TIMEFRAMES InpSourceTimeframe=PERIOD_H1;
input bool InpFullMesh=true;
input string InpPipSymbol=""; // Opcional: apenas para o simbolo exato.
input double InpPipSize=0.0;
input int InpMaxQuoteAgeSeconds=30;

CCanvas g_nocuda_canvas;
bool g_nocuda_canvas_ready=false;
string g_nocuda_prefix="";
string g_nocuda_symbol="",g_nocuda_feed="",g_nocuda_store_key="";
ENUM_TIMEFRAMES g_nocuda_source_tf=PERIOD_H1;
string g_nocuda_studies[];
int g_nocuda_study_index=-1,g_nocuda_expected_generation=0;
JPWNoCudaRecord g_nocuda_head,g_nocuda_view,g_nocuda_draft;
bool g_nocuda_has_head=false,g_nocuda_has_view=false,g_nocuda_is_draft=false;
bool g_nocuda_panel_open=false,g_nocuda_visible=true,g_nocuda_full_mesh=true;
bool g_nocuda_geometry_valid=false,g_nocuda_history_diverged=false;
JPWNoCudaGeometry g_nocuda_geometry;
int g_nocuda_tab=0,g_nocuda_pick=0,g_nocuda_level=36;
int g_nocuda_measure_page=0,g_nocuda_page=0;
bool g_nocuda_panel_focus=false,g_nocuda_skip_field_capture=false;
string g_nocuda_level_input="",g_nocuda_last_distance="",g_nocuda_last_quote="";
JPWNoCudaDailyResult g_nocuda_daily;
bool g_nocuda_show_refs=false;
string g_nocuda_date="",g_nocuda_reference_reason="";
ulong g_nocuda_daily_checked_ms=0;
string g_nocuda_status="",g_nocuda_justification="";
string g_nocuda_visual_error="";
string g_nocuda_preferred_study="";
datetime g_nocuda_a_open=0,g_nocuda_b_open=0,g_nocuda_c_open=0;
datetime g_nocuda_a_known=0,g_nocuda_b_known=0,g_nocuda_c_known=0;
double g_nocuda_a_close=0.0,g_nocuda_b_close=0.0,g_nocuda_c_close=0.0;
datetime g_nocuda_last_bar=0;
long g_nocuda_last_width=0,g_nocuda_last_height=0;
long g_nocuda_last_quote_msc=0;
// MT5 can report one object interaction as both a chart click and an object
// click. The order is not part of the event contract. Defer bare chart picks
// until the next timer so a paired object event can cancel either ordering.
bool g_nocuda_pending_pick=false,g_nocuda_recent_object=false;
int g_nocuda_pending_x=0,g_nocuda_pending_y=0;
int g_nocuda_object_x=0,g_nocuda_object_y=0;
ulong g_nocuda_pending_ms=0,g_nocuda_object_ms=0;


#include <JPWealth/JPW_NoCuda_Fibo_Controller.mqh>

void JPWNoCudaClearDaily()
  {
   JPWNoCudaDailyClear(g_nocuda_daily);
   g_nocuda_show_refs=false;
   g_nocuda_reference_reason="";
   g_nocuda_daily_checked_ms=0;
   JPWNoCudaRemoveDailyReferences(g_nocuda_prefix);
  }

void JPWNoCudaChartInteraction(const int x,const int y)
  {
   if(g_nocuda_is_draft && g_nocuda_pick>=1 && g_nocuda_pick<=3)
      JPWNoCudaPickAt(x,y);
   else JPWNoCudaSelectLineAt(x,y);
  }

bool JPWNoCudaSameClick(const int x1,const int y1,
                        const int x2,const int y2)
  { return(MathAbs(x1-x2)<=4 && MathAbs(y1-y2)<=4); }

void JPWNoCudaObjectClick(const int x,const int y)
  {
   const ulong now=GetTickCount64();
   if(g_nocuda_pending_pick)
     {
      const bool paired=now-g_nocuda_pending_ms<=1500 &&
                        JPWNoCudaSameClick(x,y,g_nocuda_pending_x,
                                            g_nocuda_pending_y);
      const int prior_x=g_nocuda_pending_x,prior_y=g_nocuda_pending_y;
      g_nocuda_pending_pick=false;
      // A separate earlier chart click should use its original pick mode
      // before an object action can arm another anchor.
      if(!paired) JPWNoCudaChartInteraction(prior_x,prior_y);
     }
   g_nocuda_recent_object=true;
   g_nocuda_object_x=x; g_nocuda_object_y=y;
   g_nocuda_object_ms=now;
  }

void JPWNoCudaFlushChartClick()
  {
   if(!g_nocuda_pending_pick) return;
   const int x=g_nocuda_pending_x,y=g_nocuda_pending_y;
   g_nocuda_pending_pick=false;
   // Timer delivery, rather than wall-clock age, provides the event-queue
   // boundary. Never use a pending click after the chart context changes.
   if(_Symbol==g_nocuda_symbol &&
      AccountInfoString(ACCOUNT_SERVER)==g_nocuda_feed)
      JPWNoCudaChartInteraction(x,y);
  }

void JPWNoCudaChartClick(const int x,const int y)
  {
   const ulong now=GetTickCount64();
   if(g_nocuda_recent_object && now-g_nocuda_object_ms<=1500 &&
      JPWNoCudaSameClick(x,y,g_nocuda_object_x,g_nocuda_object_y))
     { g_nocuda_recent_object=false; return; }
   g_nocuda_panel_focus=false;
   if(g_nocuda_pending_pick)
     {
      if(now-g_nocuda_pending_ms<=1500 &&
         JPWNoCudaSameClick(x,y,g_nocuda_pending_x,g_nocuda_pending_y))
         return;
      JPWNoCudaFlushChartClick();
     }
   g_nocuda_pending_pick=true;
   g_nocuda_pending_x=x; g_nocuda_pending_y=y;
   g_nocuda_pending_ms=now;
  }

#define JPW_NOCUDA_CHART_STATE "JPW_NOCUDA_VIEW_V1"

// A hidden chart object holds display choices for a manually saved MT5
// template. Its behavior across template reloads still requires native proof.
void JPWNoCudaSaveChartState()
  {
   if(g_nocuda_store_key=="") return;
   string context="";
   if(!JPWNoCudaStoreHash(
      JPWNoCudaStoreFrame(g_nocuda_store_key)+
      JPWNoCudaStoreFrame(g_nocuda_symbol),context)) return;
   if(ObjectFind(0,JPW_NOCUDA_CHART_STATE)<0)
      if(!ObjectCreate(0,JPW_NOCUDA_CHART_STATE,OBJ_LABEL,0,0,0))
         return;
   ObjectSetInteger(0,JPW_NOCUDA_CHART_STATE,OBJPROP_CORNER,
                    CORNER_LEFT_UPPER);
   ObjectSetInteger(0,JPW_NOCUDA_CHART_STATE,OBJPROP_XDISTANCE,-10000);
   ObjectSetInteger(0,JPW_NOCUDA_CHART_STATE,OBJPROP_YDISTANCE,-10000);
   ObjectSetInteger(0,JPW_NOCUDA_CHART_STATE,OBJPROP_HIDDEN,true);
   ObjectSetInteger(0,JPW_NOCUDA_CHART_STATE,OBJPROP_SELECTABLE,false);
   ObjectSetString(0,JPW_NOCUDA_CHART_STATE,OBJPROP_TEXT,"");
   const string selected=(g_nocuda_has_view ?
                          g_nocuda_view.study_id : "none");
   const string data=context+"|"+IntegerToString((int)g_nocuda_source_tf)+
      "|"+selected+"|"+IntegerToString(g_nocuda_visible ? 1 : 0)+
      "|"+IntegerToString(g_nocuda_full_mesh ? 1 : 0)+
      "|"+IntegerToString(g_nocuda_level);
   ObjectSetString(0,JPW_NOCUDA_CHART_STATE,OBJPROP_TOOLTIP,data);
  }

void JPWNoCudaLoadChartState()
  {
   if(g_nocuda_store_key=="" ||
      ObjectFind(0,JPW_NOCUDA_CHART_STATE)<0) return;
   string context="";
   if(!JPWNoCudaStoreHash(
      JPWNoCudaStoreFrame(g_nocuda_store_key)+
      JPWNoCudaStoreFrame(g_nocuda_symbol),context)) return;
   string fields[];
   const string payload=ObjectGetString(0,JPW_NOCUDA_CHART_STATE,
                                        OBJPROP_TOOLTIP);
   if(StringSplit(payload,'|',fields)!=6 || fields[0]!=context)
     { g_nocuda_status="Preferência do gráfico incompatível; padrão preservado.";
       return; }
   const int tf=(int)StringToInteger(fields[1]);
   const int visible=(int)StringToInteger(fields[3]);
   const int mesh=(int)StringToInteger(fields[4]);
   const int level=(int)StringToInteger(fields[5]);
   if(fields[1]!=IntegerToString(tf) ||
      fields[5]!=IntegerToString(level) ||
      tf<=0 || PeriodSeconds((ENUM_TIMEFRAMES)tf)<=0 ||
      (fields[2]!="none" && !JPWNoCudaStoreIsHash(fields[2])) ||
      (fields[3]!="0" && fields[3]!="1") ||
      (fields[4]!="0" && fields[4]!="1") ||
      level<0 || level>64)
     { g_nocuda_status="Preferência visual inválida; padrão preservado.";
       return; }
   g_nocuda_source_tf=(ENUM_TIMEFRAMES)tf;
   g_nocuda_preferred_study=(fields[2]=="none" ? "" : fields[2]);
   g_nocuda_visible=(visible==1);
   g_nocuda_full_mesh=(mesh==1);
   g_nocuda_level=level;
  }

string JPWNoCudaTfLabel(const ENUM_TIMEFRAMES tf)
  {
   string value=EnumToString(tf);
   StringReplace(value,"PERIOD_","");
   return(value);
  }

string JPWNoCudaStoreStateText(const JPWNoCudaStoreResult state,
                              const string detail)
  {
   string label="Registro indisponível";
   if(state==JPW_NOCUDA_STORE_ABSENT) label="Nenhum estudo salvo";
   if(state==JPW_NOCUDA_STORE_BUSY) label="Registro ocupado";
   if(state==JPW_NOCUDA_STORE_CORRUPT) label="Registro corrompido";
   if(state==JPW_NOCUDA_STORE_INCOMPATIBLE) label="Versão do registro incompatível";
   if(state==JPW_NOCUDA_STORE_CONFLICT) label="Conflito com outro editor";
   if(detail!="") label+=" · "+detail;
   return(label);
  }

void JPWNoCudaUseRecord(const JPWNoCudaRecord &record)
  {
   JPWNoCudaClearDaily();
   g_nocuda_a_open=(datetime)record.a_open;
   g_nocuda_b_open=(datetime)record.b_open;
   g_nocuda_c_open=(datetime)record.c_open;
   g_nocuda_a_known=(datetime)record.a_known;
   g_nocuda_b_known=(datetime)record.b_known;
   g_nocuda_c_known=(datetime)record.c_known;
   g_nocuda_a_close=record.a_close;
   g_nocuda_b_close=record.b_close;
   g_nocuda_c_close=record.c_close;
  }

void JPWNoCudaClearAnchors()
  {
   JPWNoCudaClearDaily();
   g_nocuda_a_open=0; g_nocuda_b_open=0; g_nocuda_c_open=0;
   g_nocuda_a_known=0; g_nocuda_b_known=0; g_nocuda_c_known=0;
   g_nocuda_a_close=0.0; g_nocuda_b_close=0.0; g_nocuda_c_close=0.0;
   g_nocuda_geometry_valid=false;
   g_nocuda_history_diverged=false;
  }

// The accepted revision is immutable. A changed broker history is displayed
// as divergence; a redraw never updates the revision or its Close values.
bool JPWNoCudaCheckSavedHistory(const JPWNoCudaRecord &record,string &reason)
  {
   int shift=0; double closed=0.0; datetime known=0;
   if(!JPWNoCudaExactBar(record.symbol,(ENUM_TIMEFRAMES)record.source_tf,
                        (datetime)record.a_open,shift,closed,known) ||
      closed!=record.a_close || (long)known!=record.a_known)
     { reason="Histórico-fonte divergiu na âncora A; revise explicitamente."; return(false); }
   if(!JPWNoCudaExactBar(record.symbol,(ENUM_TIMEFRAMES)record.source_tf,
                        (datetime)record.b_open,shift,closed,known) ||
      closed!=record.b_close || (long)known!=record.b_known)
     { reason="Histórico-fonte divergiu na âncora B; revise explicitamente."; return(false); }
   if(!JPWNoCudaExactBar(record.symbol,(ENUM_TIMEFRAMES)record.source_tf,
                        (datetime)record.c_open,shift,closed,known) ||
      closed!=record.c_close || (long)known!=record.c_known)
     { reason="Histórico-fonte divergiu na âncora C; revise explicitamente."; return(false); }
   datetime first=0,last=0; int count=0; string signature="";
   if(!JPWNoCudaSourceSignature(record.symbol,
                               (ENUM_TIMEFRAMES)record.source_tf,
                               (datetime)record.a_open,(datetime)record.b_open,
                               (datetime)record.c_open,first,last,count,
                               signature,reason)) return(false);
   if((long)first!=record.range_first_open ||
      (long)last!=record.range_last_open ||
      count!=record.range_bar_count || signature!=record.source_signature)
     { reason="Histórico-fonte mudou; crie uma revisão explícita."; return(false); }
   reason="";
   return(true);
  }

bool JPWNoCudaBuildCurrentGeometry(string &reason)
  {
   g_nocuda_geometry_valid=false;
   if(g_nocuda_a_open<=0 || g_nocuda_b_open<=0 || g_nocuda_c_open<=0)
     { reason="Marque A, B e C sobre barras já encerradas."; return(false); }
   const int a=iBarShift(g_nocuda_symbol,g_nocuda_source_tf,g_nocuda_a_open,true);
   const int b=iBarShift(g_nocuda_symbol,g_nocuda_source_tf,g_nocuda_b_open,true);
   const int c=iBarShift(g_nocuda_symbol,g_nocuda_source_tf,g_nocuda_c_open,true);
   if(a<1 || b<1 || c<1)
     { reason="Âncoras sem barras-fonte confirmadas."; return(false); }
   const int oldest=MathMax(a,MathMax(b,c));
   const long jA=(long)(oldest-a),jB=(long)(oldest-b),jC=(long)(oldest-c);
   g_nocuda_geometry_valid=JPWNoCudaBuildGeometry(
      jA,g_nocuda_a_close,jB,g_nocuda_b_close,jC,g_nocuda_c_close,
      g_nocuda_geometry,reason);
   return(g_nocuda_geometry_valid);
  }

void JPWNoCudaRefreshGeometry()
  {
   string reason="";
   g_nocuda_visual_error="";
   if(g_nocuda_is_draft)
     {
      JPWNoCudaBuildCurrentGeometry(reason);
      if(reason!="" && g_nocuda_a_open>0 && g_nocuda_b_open>0 &&
         g_nocuda_c_open>0) g_nocuda_visual_error=reason;
     }
   else if(g_nocuda_has_view)
     {
      g_nocuda_history_diverged=!JPWNoCudaCheckSavedHistory(
         g_nocuda_view,reason);
      if(g_nocuda_history_diverged)
        { g_nocuda_geometry_valid=false; g_nocuda_visual_error=reason;
          JPWNoCudaClearDaily(); }
      else
        {
         g_nocuda_geometry_valid=JPWNoCudaBuildGeometry(
            g_nocuda_view.a_ordinal,g_nocuda_view.a_close,
            g_nocuda_view.b_ordinal,g_nocuda_view.b_close,
            g_nocuda_view.c_ordinal,g_nocuda_view.c_close,
            g_nocuda_geometry,reason);
         if(!g_nocuda_geometry_valid) g_nocuda_visual_error=reason;
        }
     }
   else g_nocuda_geometry_valid=false;
  }

void JPWNoCudaPaint()
  {
   if(g_ncf_mode) { JPWNCFPaint(); return; }
   JPWNoCudaRefreshGeometry();
   string reason="";
   const bool draw_geometry=g_nocuda_geometry_valid &&
                            !g_nocuda_history_diverged;
   const bool painted=JPWNoCudaCanvasPaint(
      g_nocuda_canvas,g_nocuda_canvas_ready,
      g_nocuda_prefix,g_nocuda_symbol,g_nocuda_source_tf,
      g_nocuda_a_open,g_nocuda_a_close,g_nocuda_b_open,g_nocuda_b_close,
      g_nocuda_c_open,g_nocuda_c_close,g_nocuda_geometry,
      draw_geometry,g_nocuda_full_mesh,g_nocuda_visible,
      g_nocuda_is_draft,g_nocuda_level,reason);
   if(reason=="Marque A, B e C para conferir a malha." &&
      !g_nocuda_is_draft && !g_nocuda_has_view) reason="";
   if(reason!="" && reason!="Canal oculto." &&
      (g_nocuda_visual_error=="" || !painted))
      g_nocuda_visual_error=reason;
   if(!painted && g_nocuda_daily.valid) JPWNoCudaClearDaily();
   if(g_nocuda_show_refs && g_nocuda_daily.valid)
      JPWNoCudaDrawDailyReferences(g_nocuda_prefix,g_nocuda_daily,
                                   g_nocuda_reference_reason);
  }

string JPWNoCudaAnchorText(const string label,const datetime opened,
                          const double closed)
  {
   if(opened<=0) return(label+": selecione o fechamento de um candle encerrado");
   return(label+": "+TimeToString(opened,TIME_DATE|TIME_MINUTES)+
          " · Close "+DoubleToString(closed,_Digits));
  }

void JPWNoCudaReadJustification()
  {
   if(g_nocuda_is_draft &&
      ObjectFind(0,g_nocuda_prefix+"UI_JUST")>=0)
      g_nocuda_justification=ObjectGetString(
         0,g_nocuda_prefix+"UI_JUST",OBJPROP_TEXT);
   if(ObjectFind(0,g_nocuda_prefix+"UI_LEVEL_INPUT")>=0)
      g_nocuda_level_input=ObjectGetString(0,g_nocuda_prefix+"UI_LEVEL_INPUT",OBJPROP_TEXT);
   if(ObjectFind(0,g_nocuda_prefix+"UI_DATE")>=0)
     {
      const string date=ObjectGetString(0,g_nocuda_prefix+"UI_DATE",OBJPROP_TEXT);
      if(date!=g_nocuda_date)
        { g_nocuda_date=date; JPWNoCudaClearDaily(); }
     }
  }

void JPWNoCudaMeasurements(string &distance,string &quote)
  {
   distance="N/A · geometria ou cotação indisponível";
   quote="";
   if(!g_nocuda_geometry_valid || g_nocuda_history_diverged) return;
   MqlTick tick;
   if(!SymbolInfoTick(g_nocuda_symbol,tick)) return;
   const bool bid_ok=MathIsValidNumber(tick.bid) && tick.bid>0.0;
   const bool last_ok=MathIsValidNumber(tick.last) && tick.last>0.0;
   if(!bid_ok && !last_ok) return;
   const double market=(bid_ok ? tick.bid : tick.last);
   const string side=(bid_ok ? "Bid" : "Last");
   double level=0.0;
   JPWNoCudaTimePoint resolved;
   string reason="";
   if(!JPWNoCudaLevelValue(g_nocuda_level,level) ||
      !JPWNoCudaPriceAtTime(g_nocuda_symbol,g_nocuda_source_tf,
          g_nocuda_a_open,g_nocuda_geometry,level,(datetime)tick.time,
          resolved,reason))
     { distance="N/A · "+reason; return; }
   const double price=resolved.price;
   const double point=SymbolInfoDouble(g_nocuda_symbol,SYMBOL_POINT);
   if(!MathIsValidNumber(point) || point<=0.0) return;
   const double delta=market-price;
   distance=side+" − linha: "+DoubleToString(delta,_Digits)+
            " · "+DoubleToString(delta/point,1)+" pontos";
   if(InpPipSymbol==g_nocuda_symbol &&
      MathIsValidNumber(InpPipSize) && InpPipSize>0.0)
      distance+=" · "+DoubleToString(delta/InpPipSize,1)+" pips";
   const long now=(long)TimeTradeServer();
   const long age=(now>0 && tick.time>0 ? now-(long)tick.time : -1);
   const bool current=TerminalInfoInteger(TERMINAL_CONNECTED)!=0 &&
                      age>=0 && age<=InpMaxQuoteAgeSeconds;
   quote=side+" "+DoubleToString(market,_Digits)+" · "+
         TimeToString((datetime)tick.time,TIME_DATE|TIME_SECONDS)+
         " servidor · "+(current ? "Current" : "Estimated")+
         " · geometria "+(resolved.estimated ? "Estimated" : "Observed")+
         (resolved.outside_session ? " · interpolação fora da sessão" : "")+
         (g_nocuda_is_draft ? " · prévia" : "");
  }

bool JPWNoCudaPanelContains(const int x,const int y)
  {
   const int cw=(int)ChartGetInteger(0,CHART_WIDTH_IN_PIXELS);
   const int ch=(int)ChartGetInteger(0,CHART_HEIGHT_IN_PIXELS);
   if(!g_nocuda_panel_open || cw<300 || ch<230) return(false);
   const int w=MathMin(960,cw-24),h=MathMin(700,ch-24);
   return(x>=(cw-w)/2 && x<(cw+w)/2 &&
          y>=(ch-h)/2 && y<(ch+h)/2);
  }

void JPWNoCudaSelectLineAt(const int x,const int y)
  {
   if(!g_nocuda_geometry_valid || g_nocuda_history_diverged ||
      !g_nocuda_visible || JPWNoCudaPanelContains(x,y)) return;
   int window=0;
   datetime at=0;
   double cursor=0.0;
   if(!ChartXYToTimePrice(0,x,y,window,at,cursor) || window!=0 ||
      at>iTime(g_nocuda_symbol,g_nocuda_source_tf,0)) return;
   JPWNoCudaTimePoint resolved;
   string reason="";
   if(!JPWNoCudaPriceAtTime(g_nocuda_symbol,g_nocuda_source_tf,
      g_nocuda_a_open,g_nocuda_geometry,0.0,at,resolved,reason)) return;
   int selected=-1;
   double nearest=9.0;
   for(int k=0;k<65;k++)
     {
      if(!g_nocuda_full_mesh && k!=32 && k!=36 && k!=40 &&
         k!=g_nocuda_level) continue;
      double level=0.0,price=0.0;
      int px=0,py=0;
      if(!JPWNoCudaLevelValue(k,level) ||
         !JPWNoCudaPriceAt(g_nocuda_geometry,level,resolved.ordinal,price) ||
         !ChartTimePriceToXY(0,0,at,price,px,py)) continue;
      const double distance=MathAbs((double)py-(double)y);
      if(distance<nearest)
        { selected=k; nearest=distance; }
     }
   if(selected<0 || selected==g_nocuda_level) return;
   JPWNoCudaReadJustification();
   g_nocuda_level_input=""; g_nocuda_skip_field_capture=true;
   g_nocuda_level=selected;
   JPWNoCudaClearDaily();
   g_nocuda_status="Linha selecionada · confira o nível em Medidas";
   JPWNoCudaSaveChartState();
   JPWNoCudaPaint(); JPWNoCudaDrawUI(); ChartRedraw(0);
  }

bool JPWNoCudaDateValue(const string text,datetime &day)
  {
   day=0;
   if(StringLen(text)!=10) return(false);
   const datetime parsed=StringToTime(text+" 00:00");
   if(parsed<=0 || TimeToString(parsed,TIME_DATE)!=text) return(false);
   day=parsed;
   return(true);
  }

bool JPWNoCudaSelectLevelText(const string text)
  {
   string value=text;
   StringTrimLeft(value); StringTrimRight(value);
   if(StringLen(value)==0) return(false);
   int separators=0,digits=0;
   for(int i=0;i<StringLen(value);i++)
     {
      const ushort c=StringGetCharacter(value,i);
      if(c>='0' && c<='9') digits++;
      else if(c=='.' || c==',') separators++;
      else if((c=='-' || c=='+') && i==0) continue;
      else return(false);
     }
   if(digits==0 || separators>1) return(false);
   StringReplace(value,",",".");
   const double level=StringToDouble(value);
   if(!MathIsValidNumber(level) || level<-4.0 || level>4.0) return(false);
   const int index=(int)MathRound((level+4.0)*8.0);
   double exact=0.0;
   if(!MathIsValidNumber(level) || !JPWNoCudaLevelValue(index,exact) ||
      MathAbs(level-exact)>1.0e-9) return(false);
   g_nocuda_level=index;
   JPWNoCudaClearDaily();
   JPWNoCudaSaveChartState();
   return(true);
  }

void JPWNoCudaConsultDay()
  {
   JPWNoCudaReadJustification();
   JPWNoCudaClearDaily();
   JPWNoCudaRefreshGeometry();
   datetime day=0;
   double level=0.0;
   if(!JPWNoCudaDateValue(g_nocuda_date,day))
     { g_nocuda_daily.reason="Use uma data válida no formato YYYY.MM.DD."; return; }
   if(!g_nocuda_geometry_valid || g_nocuda_history_diverged)
     { g_nocuda_daily.reason="N/A · geometria ausente ou histórico divergente."; return; }
   if(!JPWNoCudaLevelValue(g_nocuda_level,level)) return;
   JPWNoCudaProjectDay(g_nocuda_symbol,g_nocuda_source_tf,g_nocuda_a_open,
                      g_nocuda_geometry,level,day,g_nocuda_daily);
   g_nocuda_daily_checked_ms=GetTickCount64();
  }

// A query is transient but must not survive a broker-history correction as if
// its old geometry were still coherent. This read-only check is bounded to
// one query per five seconds; it never silently replaces accepted prices.
bool JPWNoCudaRevalidateDaily()
  {
   if(!g_nocuda_daily.valid && !g_nocuda_daily.no_session) return(true);
   const ulong now=GetTickCount64();
   if(now>=g_nocuda_daily_checked_ms && now-g_nocuda_daily_checked_ms<5000)
      return(true);
   g_nocuda_daily_checked_ms=now;
   JPWNoCudaRefreshGeometry();
   if(!g_nocuda_daily.valid && !g_nocuda_daily.no_session) return(false);
   JPWNoCudaDailyResult check;
   double level=0.0;
   const bool ready=g_nocuda_geometry_valid && !g_nocuda_history_diverged &&
                    JPWNoCudaLevelValue(g_nocuda_level,level);
   const bool calculated=(ready && JPWNoCudaProjectDay(g_nocuda_symbol,
      g_nocuda_source_tf,g_nocuda_a_open,g_nocuda_geometry,level,g_nocuda_daily.day,check));
   if(!ready || (!calculated && !check.no_session) ||
      check.valid!=g_nocuda_daily.valid || check.no_session!=g_nocuda_daily.no_session ||
      check.estimated!=g_nocuda_daily.estimated ||
      check.start_price!=g_nocuda_daily.start_price ||
      check.mid_price!=g_nocuda_daily.mid_price ||
      check.end_price!=g_nocuda_daily.end_price ||
      check.start_outside!=g_nocuda_daily.start_outside ||
      check.mid_outside!=g_nocuda_daily.mid_outside ||
      check.end_outside!=g_nocuda_daily.end_outside ||
      check.source!=g_nocuda_daily.source ||
      check.source_signature!=g_nocuda_daily.source_signature)
     {
      JPWNoCudaClearDaily();
      g_nocuda_daily.reason="Fonte mudou ou ficou indisponível: consulte o dia novamente.";
      return(false);
     }
   return(true);
  }

void JPWNoCudaDrawUI()
  {
   if(g_ncf_mode) { JPWNCFDraw(); return; }
   if(!g_nocuda_skip_field_capture) JPWNoCudaReadJustification();
   g_nocuda_skip_field_capture=false;
   JPWNoCudaUIView view;
   view.open=g_nocuda_panel_open;
   view.draft=g_nocuda_is_draft;
   view.channel_visible=g_nocuda_visible;
   view.full_mesh=g_nocuda_full_mesh;
   view.geometry_valid=g_nocuda_geometry_valid;
   view.history_diverged=g_nocuda_history_diverged;
   view.anchor_a=(g_nocuda_a_open>0);
   view.anchor_b=(g_nocuda_b_open>0);
   view.anchor_c=(g_nocuda_c_open>0);
   view.tab=g_nocuda_tab;
   view.page=g_nocuda_page;
   view.measure_page=g_nocuda_measure_page;
   view.pick=g_nocuda_pick;
   view.level_index=g_nocuda_level;
   view.level_input=g_nocuda_level_input;
   view.revision=(g_nocuda_has_view ? g_nocuda_view.revision : 0);
   view.head_revision=(g_nocuda_has_head ? g_nocuda_head.revision : 0);
   view.study_index=g_nocuda_study_index;
   view.study_count=ArraySize(g_nocuda_studies);
   view.symbol=g_nocuda_symbol;
   view.source_tf=JPWNoCudaTfLabel(g_nocuda_source_tf);
   view.status=(g_nocuda_status=="" ?
      (g_nocuda_is_draft ? "Rascunho · ainda não confirmado" :
       "Estudo local · nenhuma ordem é enviada") : g_nocuda_status);
   if(g_nocuda_visual_error!="") view.status=g_nocuda_visual_error;
   if(PeriodSeconds(_Period)>PeriodSeconds(g_nocuda_source_tf))
      view.status+=" · visualização agregada";
   if(g_nocuda_tab==2)
     {
      view.a_text=(g_nocuda_has_view ?
         JPWNoCudaAnchorText("A · nível 0",(datetime)g_nocuda_view.a_open,
                             g_nocuda_view.a_close) : "A: sem revisão confirmada");
      view.b_text=(g_nocuda_has_view ?
         JPWNoCudaAnchorText("B · nível 0",(datetime)g_nocuda_view.b_open,
                             g_nocuda_view.b_close) : "B: sem revisão confirmada");
      view.c_text=(g_nocuda_has_view ?
         JPWNoCudaAnchorText("C · nível 1",(datetime)g_nocuda_view.c_open,
                             g_nocuda_view.c_close) : "C: sem revisão confirmada");
     }
   else
     {
      view.a_text=JPWNoCudaAnchorText("A · nível 0",g_nocuda_a_open,
                                     g_nocuda_a_close);
      view.b_text=JPWNoCudaAnchorText("B · nível 0",g_nocuda_b_open,
                                     g_nocuda_b_close);
      view.c_text=JPWNoCudaAnchorText("C · nível 1",g_nocuda_c_open,
                                     g_nocuda_c_close);
     }
   view.width_text="N/A · marque três âncoras";
   view.width_price=""; view.subdivision_price="";
   view.level_text="N/A · sem geometria";
   if(g_nocuda_geometry_valid)
     {
      view.width_price=DoubleToString(g_nocuda_geometry.width,_Digits);
      view.subdivision_price=DoubleToString(g_nocuda_geometry.subdivision,_Digits);
      view.width_text="Largura "+DoubleToString(g_nocuda_geometry.width,_Digits)+
         " · 1/8 "+DoubleToString(g_nocuda_geometry.subdivision,_Digits);
      const double point=SymbolInfoDouble(g_nocuda_symbol,SYMBOL_POINT);
      if(MathIsValidNumber(point) && point>0.0)
         view.width_text+=" · "+
            DoubleToString(g_nocuda_geometry.width/point,1)+
            " / "+DoubleToString(g_nocuda_geometry.subdivision/point,1)+
            " pontos";
      double level=0.0,at_a=0.0;
      if(JPWNoCudaLevelValue(g_nocuda_level,level) &&
         JPWNoCudaPriceAt(g_nocuda_geometry,level,
            (double)g_nocuda_geometry.origin_ordinal,at_a))
         view.level_text="Nível "+DoubleToString(level,3)+
                         " · preço em A "+DoubleToString(at_a,_Digits);
     }
   JPWNoCudaMeasurements(view.distance_text,view.quote_text);
   g_nocuda_last_distance=view.distance_text; g_nocuda_last_quote=view.quote_text;
   view.date=g_nocuda_date;
   view.daily_valid=g_nocuda_daily.valid;
   view.references=g_nocuda_show_refs;
   view.daily_state=(g_nocuda_daily.no_session ?
      (g_nocuda_daily.estimated ? "Sem sessão · Estimated" : "Sem sessão") :
      (g_nocuda_daily.valid ? (g_nocuda_daily.estimated ? "Estimated" : "Observed") : "N/A"));
   if(g_nocuda_is_draft) view.daily_state+=" · Prévia";
   view.daily_source=g_nocuda_daily.source;
   if(g_nocuda_daily.generated>0)
      view.daily_source+=" · consultado em "+
         TimeToString(g_nocuda_daily.generated,TIME_DATE|TIME_SECONDS)+" servidor";
   view.daily_reason=g_nocuda_daily.reason;
   if(g_nocuda_reference_reason!="") view.daily_reason+=" · "+g_nocuda_reference_reason;
   if(g_nocuda_daily.valid)
     {
      view.daily_start="00h: "+DoubleToString(g_nocuda_daily.start_price,_Digits);
      view.daily_mid="12h: "+DoubleToString(g_nocuda_daily.mid_price,_Digits);
      view.daily_end="24h: "+DoubleToString(g_nocuda_daily.end_price,_Digits);
      view.daily_mean="Média dos extremos: "+DoubleToString(g_nocuda_daily.mean_price,_Digits);
      view.daily_range="Faixa: "+DoubleToString(g_nocuda_daily.min_price,_Digits)+
                      " / "+DoubleToString(g_nocuda_daily.max_price,_Digits);
      if(g_nocuda_daily.start_outside || g_nocuda_daily.mid_outside || g_nocuda_daily.end_outside)
         view.daily_reason+=" · interpolação fora da sessão: "+
            (g_nocuda_daily.start_outside ? "00h " : "")+
            (g_nocuda_daily.mid_outside ? "12h " : "")+
            (g_nocuda_daily.end_outside ? "24h" : "");
     }
   else
     { view.daily_start="00h: —"; view.daily_mid="12h: —"; view.daily_end="24h: —";
       view.daily_mean="Média dos extremos: —"; view.daily_range="Faixa: —"; }
   view.history_text=(g_nocuda_has_view ?
      "Confirmado em "+TimeToString((datetime)g_nocuda_view.confirmed_utc,
                                   TIME_DATE|TIME_SECONDS)+" UTC (computador)" :
      "Sem revisão confirmada para este gráfico.");
   view.study_id=(g_nocuda_has_view ?
      g_nocuda_view.study_id : "—");
   view.justification=(g_nocuda_tab==2 ?
      (g_nocuda_has_view ? g_nocuda_view.justification : "") :
      (g_nocuda_is_draft ? g_nocuda_justification :
       (g_nocuda_has_view ? g_nocuda_view.justification : "")));
   JPWNoCudaUIRender(g_nocuda_prefix,view);
   JPWNCFDraw();
   static string last_layout_reason="";
   if(g_nocuda_ui_launcher_reason!=last_layout_reason)
     { if(g_nocuda_ui_launcher_reason!="") Print(g_nocuda_ui_launcher_reason);
       last_layout_reason=g_nocuda_ui_launcher_reason; }
   if(g_nocuda_tab==1) g_nocuda_measure_page=g_nocuda_ui_page;
   else g_nocuda_page=g_nocuda_ui_page;
  }

bool JPWNoCudaLoadStudy(const int index,const int revision=0)
  {
   if(index<0 || index>=ArraySize(g_nocuda_studies)) return(false);
   JPWNoCudaRecord head,view;
   string reason="";
   JPWNoCudaStoreResult state=JPWNoCudaStoreLoadHead(
      g_nocuda_store_key,g_nocuda_studies[index],head,reason);
   if(state!=JPW_NOCUDA_STORE_VALID)
     { g_nocuda_status=JPWNoCudaStoreStateText(state,reason); return(false); }
   view=head;
   if(revision>0 && revision<head.revision)
     {
      state=JPWNoCudaStoreLoadRevision(g_nocuda_store_key,
             g_nocuda_studies[index],revision,view,reason);
      if(state!=JPW_NOCUDA_STORE_VALID)
        { g_nocuda_status=JPWNoCudaStoreStateText(state,reason); return(false); }
     }
   if(head.symbol!=g_nocuda_symbol || head.feed!=g_nocuda_feed ||
      head.source_tf!=(int)g_nocuda_source_tf)
     { g_nocuda_status="Estudo incompatível com o gráfico ou feed."; return(false); }
   g_nocuda_head=head; g_nocuda_view=view;
   g_nocuda_has_head=true; g_nocuda_has_view=true;
   g_nocuda_study_index=index; g_nocuda_is_draft=false;
   g_nocuda_expected_generation=head.revision;
   JPWNoCudaUseRecord(view);
   g_nocuda_status=(view.revision<head.revision ?
      "Revisão histórica · apenas consulta" : "Revisão confirmada");
   JPWNoCudaRefreshGeometry();
   return(true);
  }

bool JPWNoCudaReloadStudies()
  {
   ArrayResize(g_nocuda_studies,0);
   g_nocuda_study_index=-1;
   g_nocuda_has_head=false; g_nocuda_has_view=false;
   JPWNoCudaClearAnchors();
   string reason="";
   const JPWNoCudaStoreResult state=JPWNoCudaStoreList(
      g_nocuda_store_key,g_nocuda_symbol,(int)g_nocuda_source_tf,
      g_nocuda_studies,reason);
   if(state==JPW_NOCUDA_STORE_ABSENT)
     { g_nocuda_status="Nenhum estudo salvo · clique em Novo"; return(true); }
   if(state!=JPW_NOCUDA_STORE_VALID)
     { g_nocuda_status=JPWNoCudaStoreStateText(state,reason); return(false); }
   if(g_nocuda_preferred_study!="")
      for(int i=0;i<ArraySize(g_nocuda_studies);i++)
         if(g_nocuda_studies[i]==g_nocuda_preferred_study)
            return(JPWNoCudaLoadStudy(i));
   return(JPWNoCudaLoadStudy(0));
  }

void JPWNoCudaNewDraft()
  {
   if(g_nocuda_store_key=="")
     { g_nocuda_status="Identidade da instalação/feed indisponível."; return; }
   JPWNoCudaStoreClear(g_nocuda_draft);
   g_nocuda_draft.store_key=g_nocuda_store_key;
   g_nocuda_draft.symbol=g_nocuda_symbol;
   g_nocuda_draft.feed=g_nocuda_feed;
   g_nocuda_draft.source_tf=(int)g_nocuda_source_tf;
   g_nocuda_draft.convention=JPW_NOCUDA_GEOMETRY_CONVENTION;
   if(!JPWNoCudaStoreNewStudyId(g_nocuda_store_key,g_nocuda_symbol,
       (long)TimeGMT(),(long)GetMicrosecondCount(),g_nocuda_draft.study_id))
     { g_nocuda_status="Não foi possível criar identidade do estudo."; return; }
   g_nocuda_expected_generation=0;
   g_nocuda_is_draft=true; g_nocuda_pick=1;
   g_nocuda_page=0;
   g_nocuda_panel_open=false;
   g_nocuda_justification="";
   JPWNoCudaClearAnchors();
   g_nocuda_status="1/3 · clique em A: fechamento de candle encerrado";
  }

void JPWNoCudaEditDraft()
  {
   if(!g_nocuda_has_head)
     { g_nocuda_status="Não há estudo confirmado para editar."; return; }
   g_nocuda_draft=g_nocuda_head;
   g_nocuda_expected_generation=g_nocuda_head.revision;
   g_nocuda_is_draft=true; g_nocuda_pick=0;
   g_nocuda_page=0;
   g_nocuda_justification="";
   JPWNoCudaUseRecord(g_nocuda_head);
   g_nocuda_history_diverged=false;
   int shift=0; double closed=0.0; datetime known=0;
   int reset_count=0;
   if(!JPWNoCudaExactBar(g_nocuda_symbol,g_nocuda_source_tf,
       g_nocuda_a_open,shift,closed,known) ||
      closed!=g_nocuda_a_close || known!=g_nocuda_a_known)
     { g_nocuda_a_open=0; g_nocuda_a_close=0.0; g_nocuda_a_known=0;
       reset_count++; }
   if(!JPWNoCudaExactBar(g_nocuda_symbol,g_nocuda_source_tf,
       g_nocuda_b_open,shift,closed,known) ||
      closed!=g_nocuda_b_close || known!=g_nocuda_b_known)
     { g_nocuda_b_open=0; g_nocuda_b_close=0.0; g_nocuda_b_known=0;
       reset_count++; }
   if(!JPWNoCudaExactBar(g_nocuda_symbol,g_nocuda_source_tf,
       g_nocuda_c_open,shift,closed,known) ||
      closed!=g_nocuda_c_close || known!=g_nocuda_c_known)
     { g_nocuda_c_open=0; g_nocuda_c_close=0.0; g_nocuda_c_known=0;
       reset_count++; }
   g_nocuda_status=(reset_count>0 ?
      "Histórico mudou · marque as âncoras corrigidas no rascunho" :
      "Edição em rascunho · confirmar cria nova revisão");
  }

void JPWNoCudaCancelDraft()
  {
   JPWNoCudaClearDaily();
   g_nocuda_is_draft=false; g_nocuda_pick=0;
   g_nocuda_justification="";
   if(g_nocuda_has_view)
     { JPWNoCudaUseRecord(g_nocuda_view); g_nocuda_status="Rascunho descartado"; }
   else
     { JPWNoCudaClearAnchors(); g_nocuda_status="Rascunho descartado"; }
  }

// Confirmation validates the current source range a second time. Only this
// path invokes the SQLite write; painting, zoom and ticks remain read-only.
bool JPWNoCudaConfirmDraft()
  {
   if(!g_nocuda_is_draft)
     { g_nocuda_status="Abra um rascunho antes de confirmar."; return(false); }
   JPWNoCudaReadJustification();
   StringTrimLeft(g_nocuda_justification);
   StringTrimRight(g_nocuda_justification);
   if(!JPWNoCudaStoreSafeText(g_nocuda_justification,1024))
     { g_nocuda_status="Explique a escolha das âncoras (até 1024 caracteres).";
       return(false); }
   string reason="";
   if(!JPWNoCudaBuildCurrentGeometry(reason))
     { g_nocuda_status=reason; return(false); }
   int a=0,b=0,c=0;
   double pa=0.0,pb=0.0,pc=0.0;
   datetime ka=0,kb=0,kc=0;
   if(!JPWNoCudaExactBar(g_nocuda_symbol,g_nocuda_source_tf,
                        g_nocuda_a_open,a,pa,ka) ||
      !JPWNoCudaExactBar(g_nocuda_symbol,g_nocuda_source_tf,
                        g_nocuda_b_open,b,pb,kb) ||
      !JPWNoCudaExactBar(g_nocuda_symbol,g_nocuda_source_tf,
                        g_nocuda_c_open,c,pc,kc))
     { g_nocuda_status="Histórico-fonte incompleto; rascunho preservado.";
       return(false); }
   // An existing draft may come from an older source revision. Re-select
   // changed bars explicitly; never silently rewrite their Close values.
   if(pa!=g_nocuda_a_close || pb!=g_nocuda_b_close ||
      pc!=g_nocuda_c_close || ka!=g_nocuda_a_known ||
      kb!=g_nocuda_b_known || kc!=g_nocuda_c_known)
     { g_nocuda_status="Close ou disponibilidade mudou; marque a âncora corrigida.";
       return(false); }
   datetime first=0,last=0; int count=0; string signature="";
   if(!JPWNoCudaSourceSignature(g_nocuda_symbol,g_nocuda_source_tf,
      g_nocuda_a_open,g_nocuda_b_open,g_nocuda_c_open,
      first,last,count,signature,reason))
     { g_nocuda_status=reason; return(false); }
   const int oldest=MathMax(a,MathMax(b,c));
   const int newest=MathMin(a,MathMin(b,c));
   if(count!=oldest-newest+1 ||
      iTime(g_nocuda_symbol,g_nocuda_source_tf,oldest)!=first ||
      iTime(g_nocuda_symbol,g_nocuda_source_tf,newest)!=last)
     { g_nocuda_status="Contagem de candles-fonte inconsistente.";
       return(false); }
   // Re-sample the complete range and its three Close values immediately
   // before the write. A broker-history refresh between separate reads must
   // never pair old anchors with a signature of newer source bars.
   datetime first_check=0,last_check=0;
   int count_check=0; string signature_check="";
   if(!JPWNoCudaSourceSignature(g_nocuda_symbol,g_nocuda_source_tf,
      g_nocuda_a_open,g_nocuda_b_open,g_nocuda_c_open,
      first_check,last_check,count_check,signature_check,reason) ||
      first_check!=first || last_check!=last ||
      count_check!=count || signature_check!=signature ||
      !JPWNoCudaExactBar(g_nocuda_symbol,g_nocuda_source_tf,
         g_nocuda_a_open,a,pa,ka) ||
      !JPWNoCudaExactBar(g_nocuda_symbol,g_nocuda_source_tf,
         g_nocuda_b_open,b,pb,kb) ||
      !JPWNoCudaExactBar(g_nocuda_symbol,g_nocuda_source_tf,
         g_nocuda_c_open,c,pc,kc) ||
      pa!=g_nocuda_a_close || pb!=g_nocuda_b_close ||
      pc!=g_nocuda_c_close || ka!=g_nocuda_a_known ||
      kb!=g_nocuda_b_known || kc!=g_nocuda_c_known)
     { g_nocuda_status="Histórico mudou durante a conferência; rascunho preservado.";
       return(false); }
   g_nocuda_draft.range_first_open=(long)first;
   g_nocuda_draft.range_last_open=(long)last;
   g_nocuda_draft.range_bar_count=count;
   g_nocuda_draft.source_signature=signature;
   g_nocuda_draft.a_open=(long)g_nocuda_a_open;
   g_nocuda_draft.a_known=(long)g_nocuda_a_known;
   g_nocuda_draft.a_ordinal=(long)(oldest-a);
   g_nocuda_draft.a_close=g_nocuda_a_close;
   g_nocuda_draft.b_open=(long)g_nocuda_b_open;
   g_nocuda_draft.b_known=(long)g_nocuda_b_known;
   g_nocuda_draft.b_ordinal=(long)(oldest-b);
   g_nocuda_draft.b_close=g_nocuda_b_close;
   g_nocuda_draft.c_open=(long)g_nocuda_c_open;
   g_nocuda_draft.c_known=(long)g_nocuda_c_known;
   g_nocuda_draft.c_ordinal=(long)(oldest-c);
   g_nocuda_draft.c_close=g_nocuda_c_close;
   g_nocuda_draft.confirmed_utc=(long)TimeGMT();
   g_nocuda_draft.justification=g_nocuda_justification;
   const JPWNoCudaStoreResult state=JPWNoCudaStoreConfirm(
      g_nocuda_draft,g_nocuda_expected_generation,reason);
   if(state!=JPW_NOCUDA_STORE_VALID)
     { g_nocuda_status=JPWNoCudaStoreStateText(state,reason)+
                       " · rascunho preservado";
       return(false); }
   const JPWNoCudaRecord durable=g_nocuda_draft;
   const string new_id=durable.study_id;
   g_nocuda_is_draft=false; g_nocuda_pick=0;
   if(!JPWNoCudaReloadStudies())
     {
      g_nocuda_head=durable; g_nocuda_view=durable;
      g_nocuda_has_head=true; g_nocuda_has_view=true;
      JPWNoCudaUseRecord(durable);
      g_nocuda_status="Revisão gravada e verificada; lista indisponível";
      JPWNoCudaSaveChartState();
      return(true);
     }
   bool found=false;
   for(int i=0;i<ArraySize(g_nocuda_studies);i++)
      if(g_nocuda_studies[i]==new_id)
        { found=JPWNoCudaLoadStudy(i); break; }
   if(!found)
     {
      g_nocuda_head=durable; g_nocuda_view=durable;
      g_nocuda_has_head=true; g_nocuda_has_view=true;
      JPWNoCudaUseRecord(durable);
      g_nocuda_status="Revisão gravada e verificada; lista não confirmou seleção";
     }
   else g_nocuda_status="Revisão confirmada e relida";
   JPWNoCudaSaveChartState();
   return(true);
  }

bool JPWNoCudaSetDraftAnchor(const int anchor,const datetime opened,
                              const double closed,const datetime known,
                              string &reason)
  {
   if(anchor<1 || anchor>3 || opened<=0 || known<=opened ||
      !MathIsValidNumber(closed) || closed<=0.0)
     { reason="Fechamento ou disponibilidade inválidos."; return(false); }
   const datetime a=(anchor==1 ? opened : g_nocuda_a_open);
   const datetime b=(anchor==2 ? opened : g_nocuda_b_open);
   const datetime c=(anchor==3 ? opened : g_nocuda_c_open);
   if(a>0 && b>0 && a==b)
     { reason="A e B precisam estar em candles distintos. Tente novamente.";
       return(false); }
   if(a>0 && b>0 && c>0)
     {
      const int sa=iBarShift(g_nocuda_symbol,g_nocuda_source_tf,a,true);
      const int sb=iBarShift(g_nocuda_symbol,g_nocuda_source_tf,b,true);
      const int sc=iBarShift(g_nocuda_symbol,g_nocuda_source_tf,c,true);
      const int oldest=MathMax(sa,MathMax(sb,sc));
      JPWNoCudaGeometry candidate;
      if(sa<1 || sb<1 || sc<1 || !JPWNoCudaBuildGeometry(
         oldest-sa,(anchor==1 ? closed : g_nocuda_a_close),
         oldest-sb,(anchor==2 ? closed : g_nocuda_b_close),
         oldest-sc,(anchor==3 ? closed : g_nocuda_c_close),candidate,reason))
        { reason="Âncora recusada: "+reason+" · selecione outro fechamento.";
          return(false); }
     }
   if(anchor==1)
     { g_nocuda_a_open=opened; g_nocuda_a_close=closed; g_nocuda_a_known=known; }
   if(anchor==2)
     { g_nocuda_b_open=opened; g_nocuda_b_close=closed; g_nocuda_b_known=known; }
   if(anchor==3)
     { g_nocuda_c_open=opened; g_nocuda_c_close=closed; g_nocuda_c_known=known; }
   JPWNoCudaClearDaily();
   return(true);
  }

void JPWNoCudaPickAt(const int x,const int y)
  {
   if(!g_nocuda_is_draft || g_nocuda_pick<1 || g_nocuda_pick>3) return;
   if(JPWNoCudaPanelContains(x,y)) return;
   datetime opened=0,known=0; double closed=0.0;
   string reason="";
   if(!JPWNoCudaClickedClose(g_nocuda_symbol,g_nocuda_source_tf,
                             x,y,opened,closed,known,reason))
     { g_nocuda_status=reason; JPWNoCudaDrawUI(); return; }
   if(!JPWNoCudaSetDraftAnchor(g_nocuda_pick,opened,closed,known,reason))
     { g_nocuda_status=reason; JPWNoCudaDrawUI(); return; }
   if(g_nocuda_pick<3)
     { g_nocuda_pick++; g_nocuda_panel_open=false;
       g_nocuda_status=(g_nocuda_pick==2 ?
          "2/3 · clique em B: outro candle encerrado" :
          "3/3 · clique em C: fechamento que define a largura"); }
   else
     { g_nocuda_pick=0; g_nocuda_panel_open=true; g_nocuda_tab=0;
       g_nocuda_status="Prévia pronta · confira as âncoras e confirme ou cancele"; }
   JPWNoCudaPaint(); JPWNoCudaDrawUI(); ChartRedraw(0);
  }

void JPWNoCudaDragAnchor(const string object)
  {
   if(!g_nocuda_is_draft ||
      StringFind(object,g_nocuda_prefix+"DRAW_ANCHOR_")!=0) return;
   const string id=StringSubstr(object,
      StringLen(g_nocuda_prefix+"DRAW_ANCHOR_"));
   if(id!="A" && id!="B" && id!="C") return;
   const datetime released=(datetime)ObjectGetInteger(
      0,object,OBJPROP_TIME,0);
   datetime opened=0,known=0; double closed=0.0;
   string reason="";
   if(!JPWNoCudaSnapCloseAtTime(g_nocuda_symbol,g_nocuda_source_tf,
                                released,opened,closed,known,reason))
     { g_nocuda_status=reason; JPWNoCudaPaint(); JPWNoCudaDrawUI();
       return; }
   if(!JPWNoCudaSetDraftAnchor(id=="A" ? 1 : (id=="B" ? 2 : 3),
                              opened,closed,known,reason))
     { g_nocuda_status=reason; JPWNoCudaPaint(); JPWNoCudaDrawUI(); return; }
   g_nocuda_status="Âncora arrastada e ajustada ao Close da fonte";
   JPWNoCudaPaint(); JPWNoCudaDrawUI(); ChartRedraw(0);
  }

ENUM_TIMEFRAMES JPWNoCudaNextTf(const ENUM_TIMEFRAMES tf)
  {
   if(tf==PERIOD_H1) return(PERIOD_M15);
   if(tf==PERIOD_M15) return(PERIOD_H4);
   if(tf==PERIOD_H4) return(PERIOD_D1);
   return(PERIOD_H1);
  }

void JPWNoCudaAction(const string object)
  {
   const string name=StringSubstr(object,StringLen(g_nocuda_prefix));
   if(name=="UI_OPEN")
     { JPWNoCudaReadJustification(); g_nocuda_skip_field_capture=true;
       g_nocuda_panel_focus=true; g_nocuda_ui_editing="";
       if(!g_nocuda_panel_open && !JPWUIAcquire(g_nocuda_prefix)) return;
       g_nocuda_panel_open=!g_nocuda_panel_open;
       if(!g_nocuda_panel_open) JPWUIRelease(g_nocuda_prefix);
       g_nocuda_pick=0; JPWNoCudaDrawUI(); return; }
   if(!g_nocuda_panel_open || StringFind(name,"UI_")!=0) return;
   // Text fields and labels are objects too. Recreating an OBJ_EDIT when it
   // receives focus would prevent the user from entering a justification.
   if(name!="UI_CLOSE" && StringFind(name,"UI_TAB_")!=0 &&
      name!="UI_NEW" && name!="UI_EDIT" && name!="UI_CANCEL" &&
      name!="UI_CONFIRM" && name!="UI_PICK_A" &&
      name!="UI_PICK_B" && name!="UI_PICK_C" && name!="UI_TF" &&
      name!="UI_VIS" && name!="UI_MESH" &&
      name!="UI_LEVEL_PREV" && name!="UI_LEVEL_NEXT" &&
      name!="UI_LEVEL_APPLY" && name!="UI_DAILY_QUERY" &&
      name!="UI_DAILY_REFS" && name!="UI_MEASURE_PAGE" &&
      name!="UI_PAGE_PREV" && name!="UI_PAGE_NEXT" &&
      name!="UI_STUDY_PREV" && name!="UI_STUDY_NEXT" &&
      name!="UI_REV_PREV" && name!="UI_REV_NEXT") return;
   JPWNoCudaReadJustification();
   g_nocuda_skip_field_capture=true; g_nocuda_ui_editing="";
   if(name=="UI_CLOSE")
     { JPWUIRelease(g_nocuda_prefix); g_nocuda_panel_open=false; g_nocuda_pick=0; }
   else if(StringFind(name,"UI_TAB_")==0)
     { g_nocuda_tab=(int)StringToInteger(StringSubstr(name,7));
       g_nocuda_pick=0; g_nocuda_page=0; g_nocuda_measure_page=0; }
   else if(name=="UI_NEW") JPWNoCudaNewDraft();
   else if(name=="UI_EDIT") JPWNoCudaEditDraft();
   else if(name=="UI_CANCEL") JPWNoCudaCancelDraft();
   else if(name=="UI_CONFIRM") JPWNoCudaConfirmDraft();
   else if(name=="UI_PICK_A" || name=="UI_PICK_B" || name=="UI_PICK_C")
     {
      if(!g_nocuda_is_draft)
        g_nocuda_status="Use Novo ou Editar antes de marcar uma âncora.";
      else
        {
         g_nocuda_pick=(name=="UI_PICK_A" ? 1 :
                       (name=="UI_PICK_B" ? 2 : 3));
         g_nocuda_panel_open=false;
         g_nocuda_status="Clique num candle do gráfico; será usado o Close.";
        }
     }
   else if(name=="UI_TF")
     {
      if(g_nocuda_is_draft)
         g_nocuda_status="Confirme ou cancele o rascunho antes de mudar a fonte.";
      else
        { g_nocuda_source_tf=JPWNoCudaNextTf(g_nocuda_source_tf);
          g_nocuda_preferred_study="";
          JPWNoCudaReloadStudies();
          JPWNoCudaSaveChartState(); }
     }
   else if(name=="UI_VIS")
     { g_nocuda_visible=!g_nocuda_visible;
       JPWNoCudaSaveChartState(); }
   else if(name=="UI_MESH")
     { g_nocuda_full_mesh=!g_nocuda_full_mesh;
       JPWNoCudaSaveChartState(); }
   else if(name=="UI_LEVEL_PREV")
     { g_nocuda_level=MathMax(0,g_nocuda_level-1);
       JPWNoCudaClearDaily();
       JPWNoCudaSaveChartState(); }
   else if(name=="UI_LEVEL_NEXT")
     { g_nocuda_level=MathMin(64,g_nocuda_level+1);
       JPWNoCudaClearDaily();
       JPWNoCudaSaveChartState(); }
   else if(name=="UI_LEVEL_APPLY")
     {
      if(!JPWNoCudaSelectLevelText(ObjectGetString(
            0,g_nocuda_prefix+"UI_LEVEL_INPUT",OBJPROP_TEXT)))
         g_nocuda_status="Use um dos 65 níveis: -4 a +4, passo 0,125.";
      else g_nocuda_level_input="";
     }
   else if(name=="UI_DAILY_QUERY") JPWNoCudaConsultDay();
   else if(name=="UI_DAILY_REFS")
     {
      if(!g_nocuda_daily.valid)
         g_nocuda_status="Consulte uma data válida antes de mostrar referências.";
      else g_nocuda_show_refs=!g_nocuda_show_refs;
     }
   else if(name=="UI_MEASURE_PAGE" || name=="UI_PAGE_NEXT" || name=="UI_PAGE_PREV")
     {
      const int direction=(name=="UI_PAGE_PREV" ? -1 : 1);
      if(g_nocuda_tab==1) g_nocuda_measure_page=MathMax(0,MathMin(g_nocuda_ui_pages-1,g_nocuda_measure_page+direction));
      else g_nocuda_page=MathMax(0,MathMin(g_nocuda_ui_pages-1,g_nocuda_page+direction));
     }
   else if(name=="UI_STUDY_PREV" || name=="UI_STUDY_NEXT")
     {
      if(g_nocuda_is_draft)
         g_nocuda_status="Confirme ou cancele o rascunho antes de navegar.";
      else
        {
         const int next=g_nocuda_study_index+
                        (name=="UI_STUDY_NEXT" ? 1 : -1);
         if(JPWNoCudaLoadStudy(next))
           { g_nocuda_preferred_study=g_nocuda_view.study_id;
             JPWNoCudaSaveChartState(); }
        }
     }
   else if(name=="UI_REV_PREV" || name=="UI_REV_NEXT")
     {
      if(g_nocuda_is_draft)
         g_nocuda_status="Confirme ou cancele o rascunho antes de navegar.";
      else if(g_nocuda_has_view && g_nocuda_has_head)
        {
         const int next=g_nocuda_view.revision+
                        (name=="UI_REV_NEXT" ? 1 : -1);
         if(next>=1 && next<=g_nocuda_head.revision)
            if(JPWNoCudaLoadStudy(g_nocuda_study_index,next))
              JPWNoCudaSaveChartState();
        }
     }
   if(name=="UI_VIS" || name=="UI_MESH" ||
      name=="UI_NEW" || name=="UI_EDIT" || name=="UI_CANCEL" ||
      name=="UI_CONFIRM" || name=="UI_TF" ||
      StringFind(name,"UI_LEVEL_")==0 || name=="UI_DAILY_REFS" ||
      name=="UI_DAILY_QUERY" ||
      StringFind(name,"UI_STUDY_")==0 ||
      StringFind(name,"UI_REV_")==0)
      JPWNoCudaPaint();
   JPWNoCudaDrawUI(); ChartRedraw(0);
  }

int OnInit()
  {
   if(InpMaxQuoteAgeSeconds<1 || InpMaxQuoteAgeSeconds>3600 ||
      InpSourceTimeframe==PERIOD_CURRENT ||
      PeriodSeconds(InpSourceTimeframe)<=0 ||
      (InpPipSymbol!="" && (!MathIsValidNumber(InpPipSize) ||
                             InpPipSize<=0.0)))
      return(INIT_PARAMETERS_INCORRECT);
   IndicatorSetString(INDICATOR_SHORTNAME,JPW_NOCUDA_SHORTNAME);
   int copies=0;
   for(int i=0;i<ChartIndicatorsTotal(0,0);i++)
      if(ChartIndicatorName(0,0,i)==JPW_NOCUDA_SHORTNAME ||
         ChartIndicatorName(0,0,i)=="JPW_NoCuda_Channels") copies++;
   if(copies>1)
     { Print("JPW NoCuda Channels: mantenha uma instância por gráfico.");
       return(INIT_FAILED); }
   g_nocuda_prefix="JPWNC_"+IntegerToString(ChartID())+"_"+
                   IntegerToString((long)GetMicrosecondCount())+"_";
   g_nocuda_symbol=_Symbol;
   g_nocuda_feed=AccountInfoString(ACCOUNT_SERVER);
   g_nocuda_source_tf=InpSourceTimeframe;
   g_nocuda_full_mesh=InpFullMesh;
   JPWNoCudaClearDaily();
   const datetime date_reference=TimeTradeServer();
   g_nocuda_date=(date_reference>0 ? TimeToString(date_reference,TIME_DATE) : "");
   JPWNoCudaStoreClear(g_nocuda_head);
   JPWNoCudaStoreClear(g_nocuda_view);
   JPWNoCudaStoreClear(g_nocuda_draft);
   if(JPWNoCudaStoreKey(TerminalInfoString(TERMINAL_DATA_PATH),
                       g_nocuda_feed,g_nocuda_store_key))
     { JPWNoCudaLoadChartState(); JPWNoCudaReloadStudies(); }
   else g_nocuda_status="Feed ou instalação indisponível; gravação bloqueada.";
   JPWNCFInit();
   if(!EventSetTimer(1))
     { Print("JPW NoCuda Channels: timer indisponível; seleção de âncoras bloqueada.");
       return(INIT_FAILED); }
   JPWNoCudaPaint(); JPWNoCudaDrawUI();
   return(INIT_SUCCEEDED);
  }

void OnDeinit(const int reason)
  {
   EventKillTimer();
   JPWNCFShutdown();
   if(g_nocuda_canvas_ready) g_nocuda_canvas.Destroy();
   g_nocuda_canvas_ready=false;
   JPWNoCudaUIClear(g_nocuda_prefix);
   JPWNoCudaRemoveDrawingObjects(g_nocuda_prefix);
   if(reason==REASON_REMOVE) ObjectDelete(0,JPW_NOCUDA_CHART_STATE);
   ChartRedraw(0);
  }

int OnCalculate(const int rates_total,const int prev_calculated,
                const datetime &time[],const double &open[],
                const double &high[],const double &low[],
                const double &close[],const long &tick_volume[],
                const long &volume[],const int &spread[])
  { return(rates_total); }

// A context change invalidates both editors before either can be used again.
// Updating only the visible mode would leave the other store in the old feed.
void JPWNoCudaResetContext(const string symbol,const string feed)
  {
      JPWNCFShutdown();
      JPWNoCudaUIClear(g_nocuda_prefix);
      JPWNoCudaRemoveDrawingObjects(g_nocuda_prefix);
      if(g_nocuda_canvas_ready) g_nocuda_canvas.Destroy();
      g_nocuda_canvas_ready=false;
      g_nocuda_symbol=symbol; g_nocuda_feed=feed;
      g_nocuda_store_key="";
      g_nocuda_has_head=false; g_nocuda_has_view=false;
      JPWNoCudaStoreClear(g_nocuda_head); JPWNoCudaStoreClear(g_nocuda_view);
      JPWNoCudaStoreClear(g_nocuda_draft);
      ArrayResize(g_nocuda_studies,0); g_nocuda_study_index=-1;
      g_nocuda_is_draft=false; g_nocuda_pick=0;
      JPWNoCudaClearAnchors();
      g_nocuda_preferred_study="";
      g_nocuda_source_tf=InpSourceTimeframe;
      g_nocuda_visible=true;
      g_nocuda_full_mesh=InpFullMesh;
      g_nocuda_level=36;
      g_nocuda_pending_pick=false; g_nocuda_recent_object=false;
      g_nocuda_date=""; g_nocuda_level_input="";
      g_nocuda_skip_field_capture=true; g_nocuda_panel_focus=false; g_nocuda_ui_editing="";
      if(JPWNoCudaStoreKey(TerminalInfoString(TERMINAL_DATA_PATH),
                          feed,g_nocuda_store_key))
        { JPWNoCudaLoadChartState(); JPWNoCudaReloadStudies(); }
      else
        { g_nocuda_store_key="";
          g_nocuda_has_head=false; g_nocuda_has_view=false;
          ArrayResize(g_nocuda_studies,0);
          g_nocuda_status="Contexto de feed indisponível."; }
      JPWNCFInit();
      g_ncf_notice="Contexto alterado; estudos conferidos no novo símbolo/feed. Nenhum vínculo retomado automaticamente.";
  }

void OnTimer()
  {
   const string current_feed=AccountInfoString(ACCOUNT_SERVER);
   if(_Symbol!=g_nocuda_symbol || current_feed!=g_nocuda_feed)
     {
      JPWNoCudaResetContext(_Symbol,current_feed);
      JPWNoCudaPaint(); JPWNoCudaDrawUI();
      return;
     }
   if(g_ncf_mode) { JPWNCFTimer(); return; }
   JPWNoCudaFlushChartClick();
   if((g_nocuda_daily.valid || g_nocuda_daily.no_session) && (g_nocuda_show_refs ||
      (g_nocuda_panel_open && g_nocuda_tab==1)))
     {
      if(!JPWNoCudaRevalidateDaily())
        { JPWNoCudaPaint(); JPWNoCudaDrawUI(); }
     }
   const datetime source_bar=iTime(g_nocuda_symbol,g_nocuda_source_tf,0);
   const long width=ChartGetInteger(0,CHART_WIDTH_IN_PIXELS);
   const long height=ChartGetInteger(0,CHART_HEIGHT_IN_PIXELS);
   if(source_bar!=g_nocuda_last_bar || width!=g_nocuda_last_width ||
      height!=g_nocuda_last_height)
     {
      if(source_bar!=g_nocuda_last_bar) JPWNoCudaClearDaily();
      g_nocuda_last_bar=source_bar;
      g_nocuda_last_width=width; g_nocuda_last_height=height;
      JPWNoCudaPaint(); JPWNoCudaDrawUI();
      return;
     }
   if(JPWNoCudaUILauncherReservationChanged())
     { JPWNoCudaDrawUI(); ChartRedraw(0); }
   if(g_nocuda_panel_open && g_nocuda_tab==1)
     {
      string distance="",quote="";
      JPWNoCudaMeasurements(distance,quote);
      if(distance!=g_nocuda_last_distance || quote!=g_nocuda_last_quote)
        { JPWNoCudaDrawUI(); ChartRedraw(0); }
     }
  }

void OnChartEvent(const int id,const long &lparam,const double &dparam,
                  const string &sparam)
  {
   if(_Symbol!=g_nocuda_symbol || AccountInfoString(ACCOUNT_SERVER)!=g_nocuda_feed)
     { g_nocuda_pending_pick=false; JPWNoCudaClearDaily(); return; }
   if(JPWNCFHandleEvent(id,lparam,dparam,sparam)) return;
   if(JPWUIOwner()!="" && !JPWUIOwns(g_nocuda_prefix) &&
      (id==CHARTEVENT_CLICK || id==CHARTEVENT_KEYDOWN || id==CHARTEVENT_OBJECT_DRAG)) return;
   if(id==CHARTEVENT_OBJECT_ENDEDIT && StringFind(sparam,g_nocuda_prefix+"UI_")==0)
     { JPWNoCudaReadJustification(); g_nocuda_ui_editing=""; return; }
   if(id==CHARTEVENT_KEYDOWN && g_nocuda_panel_open && g_nocuda_panel_focus && JPWUIOwns(g_nocuda_prefix) && g_nocuda_ui_editing=="")
     {
      if(lparam==27) { JPWNoCudaAction(g_nocuda_prefix+"UI_CLOSE"); return; }
      if(lparam==9)
        {
         const bool reverse=(((int)TerminalInfoInteger(TERMINAL_KEYSTATE_SHIFT)&0x8000)!=0);
         g_nocuda_ui_focus=JPWNoCudaUIFocusCycle(g_nocuda_prefix,g_nocuda_ui_focus,reverse);
         JPWNoCudaDrawUI(); return;
        }
      if(lparam==13 && StringFind(g_nocuda_ui_focus,g_nocuda_prefix+"UI_")==0)
        { JPWNoCudaAction(g_nocuda_ui_focus); return; }
     }
   if(id==CHARTEVENT_OBJECT_DRAG)
     { JPWNoCudaDragAnchor(sparam); return; }
   if(id==CHARTEVENT_OBJECT_CLICK)
     {
      JPWNoCudaObjectClick((int)lparam,(int)dparam);
      if(StringFind(sparam,g_nocuda_prefix+"UI_")==0)
        {
         g_nocuda_panel_focus=true;
         if(sparam==g_nocuda_prefix+"UI_JUST" || sparam==g_nocuda_prefix+"UI_DATE" ||
            sparam==g_nocuda_prefix+"UI_LEVEL_INPUT") g_nocuda_ui_editing=sparam;
         else
           { g_nocuda_ui_editing="";
             if(ObjectGetInteger(0,sparam,OBJPROP_TYPE)==OBJ_BUTTON) g_nocuda_ui_focus=sparam; }
         JPWNoCudaAction(sparam); return;
        }
      if(sparam==g_nocuda_prefix+"CANVAS" ||
         StringFind(sparam,g_nocuda_prefix+"DRAW_")==0)
        { g_nocuda_panel_focus=false; g_nocuda_ui_editing="";
          JPWNoCudaChartInteraction((int)lparam,(int)dparam); return; }
      g_nocuda_panel_focus=false; g_nocuda_ui_editing="";
      return; // Other indicators own their objects and shortcuts.
     }
   if(id==CHARTEVENT_CLICK)
     { JPWNoCudaChartClick((int)lparam,(int)dparam); return; }
   if(id==CHARTEVENT_CHART_CHANGE)
     { g_nocuda_pending_pick=false;
       JPWNoCudaPaint(); JPWNoCudaDrawUI(); }
  }
