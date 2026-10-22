#ifndef JPW_STOIKUS_PANEL_PREFS_MQH
#define JPW_STOIKUS_PANEL_PREFS_MQH

// Pure presentation preference. Mask bits keep their canonical metric identity;
// order contains all seven metrics, including those currently hidden.
// No chart, file, financial collection or calculation APIs belong here.
#define JPW_STOIKUS_PANEL_PREF_OBJECT "JPW_STOIKUS_PANEL_PREF_V1"

struct JPWStoikusPanelPrefs
  {
   int visible_mask;
   int order[7];
  };

bool JPWStoikusPanelPrefsValid(const JPWStoikusPanelPrefs &p)
  {
   if(p.visible_mask<0 || p.visible_mask>127) return(false);
   int seen=0;
   for(int i=0;i<7;i++)
     {
      const int metric=p.order[i];
      if(metric<0 || metric>6 || (seen & (1<<metric))!=0) return(false);
      seen|=(1<<metric);
     }
   return(seen==127);
  }

void JPWStoikusPanelPrefsDefault(JPWStoikusPanelPrefs &p)
  {
   const int order[7]={0,5,3,4,1,2,6};
   p.visible_mask=57;
   for(int i=0;i<7;i++) p.order[i]=order[i];
  }

// Compatibility is an in-memory projection of what the old HUD displayed.
// The caller supplies its validated legacy mask and mode; nothing is saved.
void JPWStoikusPanelPrefsLegacy(const int mode,const int legacy_mask,JPWStoikusPanelPrefs &p)
  {
   const int order[7]={0,5,1,2,3,4,6};
   p.visible_mask=(mode==0 ? legacy_mask & 33 : legacy_mask);
   for(int i=0;i<7;i++) p.order[i]=order[i];
  }

string JPWStoikusPanelPrefsEncode(const JPWStoikusPanelPrefs &p)
  {
   if(!JPWStoikusPanelPrefsValid(p)) return("");
   return(StringFormat("V1|%d|%d%d%d%d%d%d%d",p.visible_mask,
                       p.order[0],p.order[1],p.order[2],p.order[3],
                       p.order[4],p.order[5],p.order[6]));
  }

// Exact canonical format: V1|decimal-mask|seven metric digits, without padding.
// Stage every field before assigning, so failure never changes the caller.
bool JPWStoikusPanelPrefsDecode(const string text,JPWStoikusPanelPrefs &p)
  {
   const int length=StringLen(text);
   if(length<12 || length>14 || StringSubstr(text,0,3)!="V1|") return(false);
   const int separator=length-8;
   if(StringGetCharacter(text,separator)!='|') return(false);
   if(separator>4 && StringGetCharacter(text,3)=='0') return(false);
   JPWStoikusPanelPrefs candidate;
   candidate.visible_mask=0;
   for(int i=3;i<separator;i++)
     {
      const ushort digit=StringGetCharacter(text,i);
      if(digit<'0' || digit>'9') return(false);
      candidate.visible_mask=candidate.visible_mask*10+(int)(digit-'0');
     }
   for(int i=0;i<7;i++)
     {
      const ushort digit=StringGetCharacter(text,separator+1+i);
      if(digit<'0' || digit>'6') return(false);
      candidate.order[i]=(int)(digit-'0');
     }
   if(!JPWStoikusPanelPrefsValid(candidate)) return(false);
   p=candidate;
   return(true);
  }

// Move exactly one slot in the complete order, independent of visibility.
// Invalid input or a boundary is an atomic refusal.
bool JPWStoikusPanelPrefsMove(JPWStoikusPanelPrefs &p,const int metric,const int direction)
  {
   if(!JPWStoikusPanelPrefsValid(p) || metric<0 || metric>6 ||
      (direction!=-1 && direction!=1)) return(false);
   for(int i=0;i<7;i++)
     {
      if(p.order[i]!=metric) continue;
      const int next=i+direction;
      if(next<0 || next>6) return(false);
      p.order[i]=p.order[next];
      p.order[next]=metric;
      return(true);
     }
   return(false);
  }

#endif
