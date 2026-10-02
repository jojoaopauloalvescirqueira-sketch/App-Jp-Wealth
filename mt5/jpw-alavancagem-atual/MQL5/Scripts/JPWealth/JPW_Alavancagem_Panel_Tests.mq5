#property copyright "JP Wealth"
#property version "1.50"
#include <JPWealth/JPW_Alavancagem_Panel.mqh>

int failures=0,asserts=0;
void Check(const bool passed,const string message)
  { asserts++; if(!passed) { failures++; Print("FAIL: ",message); } }
void OnStart()
  {
   int widths[4]={240,320,390,1440};
   int heights[3]={240,480,900};
   int dpi[4]={100,125,150,200};
   for(int w=0;w<4;w++) for(int h=0;h<3;h++) for(int d=0;d<4;d++)
     {
      const int text=(12*dpi[d]+99)/100;
      JPWPanelRect dialog;
      int pad=0,line=0,control=0,cy=0,ch=0,fy=0;
      Check(JPWPanelDialog(widths[w],heights[h],text,text/2,dialog,pad,line,control,cy,ch,fy),"dialog geometry");
      Check(dialog.x>=0 && dialog.y>=0 && dialog.x+dialog.width<=widths[w] &&
            dialog.y+dialog.height<=heights[h],"dialog inside chart");
      Check(fy>=dialog.y && fy+control<=dialog.y+dialog.height,"footer reachable");
      Check(MathAbs(2*dialog.x+dialog.width-widths[w])<=1 &&
            MathAbs(2*dialog.y+dialog.height-heights[h])<=1,"dialog centered");
      const int reserved=JPWPanelHUDReservedWidth(widths[w],text,6,90);
      Check(reserved>=90 && reserved<=widths[w]-16,"HUD reserved width inside chart");
      for(int corner=0;corner<4;corner++)
        {
         JPWPanelRect hud;
         const int block=4*(text+4)+control+4;
         Check(JPWPanelHUD(widths[w],heights[h],180,block,16,40,(corner%2)==1,corner>=2,hud),"HUD geometry");
         Check(hud.x>=0 && hud.y>=0 && hud.x+hud.width<=widths[w] &&
               hud.y+hud.height<=heights[h],"HUD including button inside chart");
        }
      int rows=JPWPanelPageRows(ch,2*line+control);
      if(rows>0) Check(JPWPanelPageCount(17,rows)*rows>=17,"all fields reachable via pages");
     }
   Check(JPWPanelHUDReservedWidth(1440,24,6,90)>
         JPWPanelHUDReservedWidth(1440,12,6,90),"HUD width follows measured DPI");
   Print("JPW_Alavancagem_Panel_Tests ",failures==0 ? "PASS: " : "FAIL: ",asserts," asserts; ",failures," failures");
  }
