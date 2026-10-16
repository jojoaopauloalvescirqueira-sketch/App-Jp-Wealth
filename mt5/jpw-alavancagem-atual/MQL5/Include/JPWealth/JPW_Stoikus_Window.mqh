#ifndef JPW_STOIKUS_WINDOW_MQH
#define JPW_STOIKUS_WINDOW_MQH
// Runtime visual geometry only. Callers own drafts, routes and persistence.
struct JPWStoikusWindowGesture
  { bool active; bool resize; bool down; bool scroll; int px; int py; int edges; JPWPanelRect start; };
void JPWStoikusWindowBounds(JPWPanelRect &r,const int cw,const int ch)
  {
   r.width=MathMax(1,MathMin(r.width,MathMax(1,cw)));
   r.height=MathMax(1,MathMin(r.height,MathMax(1,ch)));
   r.x=MathMax(0,MathMin(r.x,cw-r.width)); r.y=MathMax(0,MathMin(r.y,ch-r.height));
  }
void JPWStoikusWindowCancel(JPWStoikusWindowGesture &g,JPWPanelRect &r)
  {
   if(g.active) { r=g.start; ChartSetInteger(0,CHART_MOUSE_SCROLL,g.scroll); }
   g.active=false;g.down=false;
  }
// Edges have a full-length target with most of its 36px depth outside the
// panel, preserving controls inset inside it. Corners retain a 36px square.
int JPWStoikusWindowEdges(const JPWPanelRect &r,const int x,const int y,const int grip)
  {
   const int inset=MathMax(2,grip/6),outset=grip-inset;
   if(x<r.x-outset || y<r.y-outset || x>=r.x+r.width+outset || y>=r.y+r.height+outset)return(0);
   int edges=0;
   if(x<r.x+inset)edges|=1;else if(x>=r.x+r.width-inset)edges|=2;
   if(y<r.y+inset)edges|=4;else if(y>=r.y+r.height-inset)edges|=8;
   if(x>=r.x && x<r.x+r.width && y>=r.y && y<r.y+r.height)
     {
      if(x<r.x+grip && y>=r.y+r.height-grip)edges=1|8;
      if(x>=r.x+r.width-grip && y>=r.y+r.height-grip)edges=2|8;
     }
   return(edges);
  }
void JPWStoikusWindowResize(const JPWPanelRect &start,JPWPanelRect &r,const int edges,
   const int dx,const int dy,const int cw,const int ch,const int minimum_width,const int minimum_height)
  {
   r=start;
   const int minw=MathMax(1,MathMin(minimum_width,cw)),minh=MathMax(1,MathMin(minimum_height,ch));
   if((edges&1)!=0){const int right=start.x+start.width;r.x=MathMax(0,MathMin(start.x+dx,right-minw));r.width=right-r.x;}
   else if((edges&2)!=0)r.width=MathMax(MathMin(minw,cw-start.x),MathMin(start.width+dx,cw-start.x));
   if((edges&4)!=0){const int bottom=start.y+start.height;r.y=MathMax(0,MathMin(start.y+dy,bottom-minh));r.height=bottom-r.y;}
   else if((edges&8)!=0)r.height=MathMax(MathMin(minh,ch-start.y),MathMin(start.height+dy,ch-start.y));
   JPWStoikusWindowBounds(r,cw,ch);
  }
bool JPWStoikusWindowEvent(JPWStoikusWindowGesture &g,JPWPanelRect &r,
   const int id,const long &lp,const double &dp,const string &sp,const bool owner,
   const int cw,const int ch,const int header,const int grip,bool &finished,
   const int minimum_width=0,const int minimum_height=0)
  {
   finished=false;
   if(id==CHARTEVENT_CHART_CHANGE || id>=CHARTEVENT_CUSTOM || !owner)
     { JPWStoikusWindowCancel(g,r); return(false); }
   if(id==CHARTEVENT_KEYDOWN && lp==27)
     { const bool active=g.active; JPWStoikusWindowCancel(g,r); return(active); }
   if(id!=CHARTEVENT_MOUSE_MOVE) return(false);
   const int x=(int)lp,y=(int)dp;const bool down=((int)StringToInteger(sp)&1)!=0;
   if(down && !g.down && !g.active)
     {
      const int edges=JPWStoikusWindowEdges(r,x,y,grip);
      const bool move=x>=r.x && x<r.x+r.width-2*grip && y>=r.y && y<r.y+header;
      if(edges!=0 || move)
        {
         g.scroll=(bool)ChartGetInteger(0,CHART_MOUSE_SCROLL);
         if(!ChartSetInteger(0,CHART_MOUSE_SCROLL,false)) return(false);
         g.active=true;g.edges=edges;g.resize=edges!=0;g.start=r;g.px=x;g.py=y;
        }
     }
   g.down=down;if(!g.active)return(false);
   if(g.resize)JPWStoikusWindowResize(g.start,r,g.edges,x-g.px,y-g.py,cw,ch,
      minimum_width>0 ? minimum_width : 6*grip,minimum_height>0 ? minimum_height : 4*grip);
   else {r.x=g.start.x+x-g.px;r.y=g.start.y+y-g.py;JPWStoikusWindowBounds(r,cw,ch);}
   if(!down){ChartSetInteger(0,CHART_MOUSE_SCROLL,g.scroll);g.active=false;finished=true;}
   return(true);
  }
#endif
