#ifndef JPW_NOCUDA_FIBO_TERMINAL_MQH
#define JPW_NOCUDA_FIBO_TERMINAL_MQH
#include <JPWealth/JPW_NoCuda_Fibo_Core.mqh>
// No trading/account API. Only chart objects and the caller's exact symbol.
#define JPW_NCF_CAPTURE_BUDGET_MS 500
int JPWNCFCatalog(const long chart,string &names[])
  {
   ArrayResize(names,0);
   const int total=ObjectsTotal(chart,0,OBJ_FIBOCHANNEL);
   if(total<0 || total>10000) return(-1);
   for(int i=0;i<total;i++)
     {
      string name=ObjectName(chart,i,0,OBJ_FIBOCHANNEL);
      if(name=="" || StringFind(name,"JPWNCF_")==0) continue;
      int n=ArraySize(names); if(ArrayResize(names,n+1)!=n+1) return(-1);
      names[n]=name;
     }
   return(ArraySize(names));
  }
bool JPWNCFReadInteger(const long chart,const string name,
                       const ENUM_OBJECT_PROPERTY_INTEGER property,const int modifier,long &out)
  { ResetLastError(); return(ObjectGetInteger(chart,name,property,modifier,out) && GetLastError()==0); }
bool JPWNCFReadDouble(const long chart,const string name,
                      const ENUM_OBJECT_PROPERTY_DOUBLE property,const int modifier,double &out)
  { ResetLastError(); return(ObjectGetDouble(chart,name,property,modifier,out) && GetLastError()==0); }
bool JPWNCFReadString(const long chart,const string name,
                      const ENUM_OBJECT_PROPERTY_STRING property,const int modifier,string &out)
  { ResetLastError(); return(ObjectGetString(chart,name,property,modifier,out) && GetLastError()==0); }
JPWNCFStatus JPWNCFReadObject(const long chart,const string name,const int reference_tf,
                             const string symbol,const string feed,JPWNCFSnapshot &s,string &reason)
  {
   JPWNCFClear(s); reason="Canal Fibonacci nao encontrado";
   if(ObjectFind(chart,name)!=0) return(JPW_NCF_ABSENT);
   long type=0,count=0;
   if(!JPWNCFReadInteger(chart,name,OBJPROP_TYPE,0,type) || type!=OBJ_FIBOCHANNEL ||
      !JPWNCFReadInteger(chart,name,OBJPROP_LEVELS,0,count)) return(JPW_NCF_INVALID);
   if(count!=JPW_NCF_LEVELS)
     { reason="O canal precisa ter os 65 niveis originais"; return(JPW_NCF_INVALID); }
   s.source_name=name; s.symbol=symbol; s.feed=feed; s.reference_tf=reference_tf;
   s.captured_utc=(long)TimeGMT();
   if(!JPWNCFReadInteger(chart,name,OBJPROP_CREATETIME,0,s.source_created)) return(JPW_NCF_IO_ERROR);
   for(int i=0;i<3;i++) if(!JPWNCFReadInteger(chart,name,OBJPROP_TIME,i,s.anchor_time[i]) ||
      !JPWNCFReadDouble(chart,name,OBJPROP_PRICE,i,s.anchor_price[i])) return(JPW_NCF_IO_ERROR);
   long color_value=0,style=0,width=0,left=0,right=0,back=0,hidden=0,selectable=0;
   if(!JPWNCFReadInteger(chart,name,OBJPROP_COLOR,0,color_value) ||
      !JPWNCFReadInteger(chart,name,OBJPROP_STYLE,0,style) ||
      !JPWNCFReadInteger(chart,name,OBJPROP_WIDTH,0,width) ||
      !JPWNCFReadInteger(chart,name,OBJPROP_RAY_LEFT,0,left) ||
      !JPWNCFReadInteger(chart,name,OBJPROP_RAY_RIGHT,0,right) ||
      !JPWNCFReadInteger(chart,name,OBJPROP_BACK,0,back) ||
      !JPWNCFReadInteger(chart,name,OBJPROP_HIDDEN,0,hidden) ||
      !JPWNCFReadInteger(chart,name,OBJPROP_SELECTABLE,0,selectable) ||
      !JPWNCFReadInteger(chart,name,OBJPROP_TIMEFRAMES,0,s.timeframes)) return(JPW_NCF_IO_ERROR);
   s.line_color=(int)color_value; s.line_style=(int)style; s.line_width=(int)width;
   s.ray_left=(left!=0); s.ray_right=(right!=0); s.back=(back!=0);
   s.hidden=(hidden!=0); s.selectable=(selectable!=0);
   for(int i=0;i<JPW_NCF_LEVELS;i++)
     {
      if(!JPWNCFReadDouble(chart,name,OBJPROP_LEVELVALUE,i,s.levels[i].value) ||
         !JPWNCFReadString(chart,name,OBJPROP_LEVELTEXT,i,s.levels[i].label) ||
         !JPWNCFReadInteger(chart,name,OBJPROP_LEVELCOLOR,i,color_value) ||
         !JPWNCFReadInteger(chart,name,OBJPROP_LEVELSTYLE,i,style) ||
         !JPWNCFReadInteger(chart,name,OBJPROP_LEVELWIDTH,i,width)) return(JPW_NCF_IO_ERROR);
      s.levels[i].line_color=(int)color_value; s.levels[i].line_style=(int)style; s.levels[i].line_width=(int)width;
     }
   reason=""; return(JPW_NCF_VALID);
  }
JPWNCFStatus JPWNCFCapture(const long chart,const string name,const int reference_tf,
                          const string symbol,const string feed,JPWNCFSnapshot &out,string &reason)
  {
   JPWNCFClear(out); reason="";
   const ulong started=GetTickCount64();
   if((int)ChartPeriod(chart)!=reference_tf || ChartSymbol(chart)!=symbol ||
      PeriodSeconds((ENUM_TIMEFRAMES)reference_tf)<=0)
     { reason="Volte ao periodo de referencia para sincronizar"; return(JPW_NCF_CHANGED); }
   JPWNCFSnapshot a,b; JPWNCFStatus status=JPWNCFReadObject(chart,name,reference_tf,symbol,feed,a,reason);
   if(status!=JPW_NCF_VALID) return(status);
   long earliest=a.anchor_time[0],latest=a.anchor_time[0];
   for(int i=1;i<3;i++) { if(a.anchor_time[i]<earliest) earliest=a.anchor_time[i]; if(a.anchor_time[i]>latest) latest=a.anchor_time[i]; }
   // Need the actual left bracket, not a fabricated opening at the anchor time.
   int left=iBarShift(symbol,(ENUM_TIMEFRAMES)reference_tf,(datetime)earliest,false);
   if(left<1 || left+1>JPW_NCF_MAX_OPENS)
     { reason="Historico insuficiente para delimitar as ancoras"; return(JPW_NCF_INVALID); }
   datetime times[]; ArraySetAsSeries(times,false);
   const int copied=CopyTime(symbol,(ENUM_TIMEFRAMES)reference_tf,0,left+1,times);
   if(copied!=left+1 || copied<2 || (long)times[copied-1]<latest)
     { reason="A ancora mais recente ainda nao possui delimitador carregado"; return(JPW_NCF_INVALID); }
   if(ArrayResize(a.opens,copied)!=copied) return(JPW_NCF_IO_ERROR);
   for(int i=0;i<copied;i++) a.opens[i]=(long)times[i];
   a.domain_from=a.opens[0]; a.domain_to=a.opens[copied-1];
   // Second object AND series reads detect mutations in this one bounded attempt.
   status=JPWNCFReadObject(chart,name,reference_tf,symbol,feed,b,reason);
   datetime verify[]; ArraySetAsSeries(verify,false);
   const int verified=CopyTime(symbol,(ENUM_TIMEFRAMES)reference_tf,0,left+1,verify);
   bool stable=(status==JPW_NCF_VALID && verified==copied && a.source_created==b.source_created &&
                JPWNCFSourceWire(a)==JPWNCFSourceWire(b));
   for(int i=0;i<copied && stable;i++) stable=(times[i]==verify[i]);
   if(!stable || ChartSymbol(chart)!=symbol || (int)ChartPeriod(chart)!=reference_tf ||
      GetTickCount64()-started>JPW_NCF_CAPTURE_BUDGET_MS)
     { reason="Objeto, historico ou contexto mudou durante a captura; tente novamente"; return(JPW_NCF_CHANGED); }
   status=JPWNCFValidate(a,reason);
   if(status!=JPW_NCF_VALID) return(status);
   if(!JPWNCFCopy(a,out)) return(JPW_NCF_IO_ERROR);
   return(JPW_NCF_VALID);
  }
JPWNCFStatus JPWNCFClone(const long chart,const string newname,const JPWNCFSnapshot &s,string &reason)
  {
   JPWNCFStatus status=JPWNCFValidate(s,reason);
   if(status!=JPW_NCF_VALID) return(status);
   // Native rendering only on its captured chart timeframe; other TF must use
   // the separately gated invariant resolver, never a reinterpreted native clone.
   if(ChartSymbol(chart)!=s.symbol || (int)ChartPeriod(chart)!=s.reference_tf)
     { reason="Clone nativo permitido apenas no periodo de referencia"; return(JPW_NCF_CHANGED); }
   if(newname=="" || newname==s.source_name || StringFind(newname,"JPWNCF_")!=0 || ObjectFind(chart,newname)>=0)
     { reason="Nome de clone reservado ou ja utilizado"; return(JPW_NCF_CONFLICT); }
   bool ok=ObjectCreate(chart,newname,OBJ_FIBOCHANNEL,0,(datetime)s.anchor_time[0],s.anchor_price[0],
      (datetime)s.anchor_time[1],s.anchor_price[1],(datetime)s.anchor_time[2],s.anchor_price[2]);
   ok=ok && ObjectSetInteger(chart,newname,OBJPROP_LEVELS,JPW_NCF_LEVELS) &&
      ObjectSetInteger(chart,newname,OBJPROP_COLOR,s.line_color) && ObjectSetInteger(chart,newname,OBJPROP_STYLE,s.line_style) &&
      ObjectSetInteger(chart,newname,OBJPROP_WIDTH,s.line_width) && ObjectSetInteger(chart,newname,OBJPROP_RAY_LEFT,s.ray_left) &&
      ObjectSetInteger(chart,newname,OBJPROP_RAY_RIGHT,s.ray_right) && ObjectSetInteger(chart,newname,OBJPROP_BACK,s.back) &&
      ObjectSetInteger(chart,newname,OBJPROP_HIDDEN,s.hidden) && ObjectSetInteger(chart,newname,OBJPROP_SELECTABLE,s.selectable) &&
      ObjectSetInteger(chart,newname,OBJPROP_TIMEFRAMES,s.timeframes);
   for(int i=0;i<JPW_NCF_LEVELS && ok;i++) ok=ObjectSetDouble(chart,newname,OBJPROP_LEVELVALUE,i,s.levels[i].value) &&
      ObjectSetString(chart,newname,OBJPROP_LEVELTEXT,i,s.levels[i].label) &&
      ObjectSetInteger(chart,newname,OBJPROP_LEVELCOLOR,i,s.levels[i].line_color) &&
      ObjectSetInteger(chart,newname,OBJPROP_LEVELSTYLE,i,s.levels[i].line_style) &&
      ObjectSetInteger(chart,newname,OBJPROP_LEVELWIDTH,i,s.levels[i].line_width);
   JPWNCFSnapshot actual;
   if(ok) ok=JPWNCFReadObject(chart,newname,s.reference_tf,s.symbol,s.feed,actual,reason)==JPW_NCF_VALID &&
             JPWNCFSourceWire(actual)==JPWNCFSourceWire(s);
   if(!ok) { ObjectDelete(chart,newname); reason="Clone nao confirmado pela releitura das propriedades"; return(JPW_NCF_IO_ERROR); }
   reason="Propriedades clonadas; paridade geometrica entre periodos ainda nao comprovada";
   return(JPW_NCF_VALID);
  }
// Laboratory oracle only: OBJ_CHANNEL is documented for GetValueByTime.
// Agreement with this auxiliary is NOT evidence that FiboChannel uses its axis.
bool JPWNCFChannelOracle(const long chart,const string name,const JPWNCFSnapshot &s,
                         const long when,double &line0,double &line1,string &reason)
  {
   line0=0; line1=0;
   if(StringFind(name,"JPWNCF_LAB_")!=0 || ObjectFind(chart,name)>=0)
     { reason="Nome de laboratorio indisponivel"; return(false); }
   bool ok=ObjectCreate(chart,name,OBJ_CHANNEL,0,(datetime)s.anchor_time[0],s.anchor_price[0],
      (datetime)s.anchor_time[1],s.anchor_price[1],(datetime)s.anchor_time[2],s.anchor_price[2]);
   if(ok)
     {
      ResetLastError(); line0=ObjectGetValueByTime(chart,name,(datetime)when,0); ok=GetLastError()==0;
      ResetLastError(); line1=ObjectGetValueByTime(chart,name,(datetime)when,1); ok=ok && GetLastError()==0;
     }
   ObjectDelete(chart,name);
   reason="Somente oraculo OBJ_CHANNEL; Fibonacci nativo continua UNVERIFIED_NATIVE";
   return(ok && JPWNCFFinitePositive(line0) && JPWNCFFinitePositive(line1));
  }
#endif
