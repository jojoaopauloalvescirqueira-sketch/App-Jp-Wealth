#ifndef JPW_STOIKUS_VISUAL_MQH
#define JPW_STOIKUS_VISUAL_MQH
#define JPW_STOIKUS_VISUAL_OBJECT "JPW_STOIKUS_VISUAL_V1"
// Logical pixels only. Legacy input offsets remain physical until first gesture.
struct JPWStoikusVisual
  {
   int mode; bool collapsed; int transparency,width;
   bool positioned; int x,y;
   bool account_positioned; int account_x,account_y,account_width,account_height;
   bool account_minimized;
  };
void JPWStoikusVisualDefault(JPWStoikusVisual &p)
  {
   p.mode=0; p.collapsed=false; p.transparency=30; p.width=280;
   p.positioned=false; p.x=0; p.y=0; p.account_positioned=false;
   p.account_x=0; p.account_y=0; p.account_width=720; p.account_height=520; p.account_minimized=false;
  }
bool JPWStoikusVisualValid(const JPWStoikusVisual &p)
  {
   return(p.mode>=0 && p.mode<=1 && p.transparency>=0 && p.transparency<=100 && p.transparency%10==0 &&
      p.width>=120 && p.width<=480 && p.x>=0 && p.x<=100000 && p.y>=0 && p.y<=100000 &&
      p.account_x>=0 && p.account_x<=100000 && p.account_y>=0 && p.account_y<=100000 &&
      p.account_width>=240 && p.account_width<=100000 && p.account_height>=160 && p.account_height<=100000);
  }
string JPWStoikusVisualEncode(const JPWStoikusVisual &p)
  {
   if(!JPWStoikusVisualValid(p)) return("");
   return("V1|"+IntegerToString(p.mode)+"|"+IntegerToString((int)p.collapsed)+"|"+IntegerToString(p.transparency)+"|"+
      IntegerToString(p.width)+"|"+IntegerToString((int)p.positioned)+"|"+IntegerToString(p.x)+"|"+IntegerToString(p.y)+"|"+
      IntegerToString((int)p.account_positioned)+"|"+IntegerToString(p.account_x)+"|"+IntegerToString(p.account_y)+"|"+
      IntegerToString(p.account_width)+"|"+IntegerToString(p.account_height)+"|"+IntegerToString((int)p.account_minimized));
  }
bool JPWStoikusVisualDecode(const string text,JPWStoikusVisual &p)
  {
   if(StringFind(text,"V1|")!=0) return(false);
   int v[13]; int start=3;
   for(int i=0;i<13;i++)
     {
      int end=StringFind(text,"|",start);
      if(i<12 && end<0) return(false);
      if(i==12) { if(end>=0) return(false); end=StringLen(text); }
      int len=end-start; if(len<1 || len>6) return(false);
      for(int k=start;k<end;k++) if(StringGetCharacter(text,k)<'0' || StringGetCharacter(text,k)>'9') return(false);
      v[i]=(int)StringToInteger(StringSubstr(text,start,len)); start=end+1;
     }
   if(v[1]>1 || v[4]>1 || v[7]>1 || v[12]>1) return(false);
   JPWStoikusVisual q; q.mode=v[0]; q.collapsed=(v[1]==1); q.transparency=v[2]; q.width=v[3];
   q.positioned=(v[4]==1); q.x=v[5]; q.y=v[6]; q.account_positioned=(v[7]==1);
   q.account_x=v[8]; q.account_y=v[9]; q.account_width=v[10]; q.account_height=v[11]; q.account_minimized=(v[12]==1);
   if(!JPWStoikusVisualValid(q) || JPWStoikusVisualEncode(q)!=text) return(false);
   p=q; return(true);
  }
int JPWStoikusAlpha(const int transparency) { return((int)MathRound(255.0*(100-transparency)/100.0)); }
int JPWStoikusClamp(const int value,const int lo,const int hi) { return(MathMax(lo,MathMin(value,MathMax(lo,hi)))); }
int JPWStoikusHUDWidth(const int chart,const int logical,const int measured_min,const double scale)
  { return(MathMax(0,MathMin(chart,MathMin((int)(480*scale+0.5),MathMax(measured_min,(int)(logical*scale+0.5)))))); }
bool JPWStoikusMetricVisible(const int mode,const int mask,const int metric)
  { return(metric>=0 && metric<7 && (mask&(1<<metric))!=0 && (mode==1 || metric==0 || metric==5)); }
#endif
