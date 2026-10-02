#ifndef JPW_UI_FOCUS_MQH
#define JPW_UI_FOCUS_MQH
// Chart-local, ephemeral ownership of keyboard/central-panel interaction.
// No account data, financial side effects or template persistence contract.
#define JPW_UI_OWNER_OBJECT "JPW_UI_OWNER_V1"
#define JPW_UI_OWNER_EVENT 3107

string JPWUIOwner()
  {
   if(ObjectFind(0,JPW_UI_OWNER_OBJECT)<0 ||
      ObjectGetInteger(0,JPW_UI_OWNER_OBJECT,OBJPROP_TYPE)!=OBJ_LABEL) return("");
   return(ObjectGetString(0,JPW_UI_OWNER_OBJECT,OBJPROP_TOOLTIP));
  }

bool JPWUIOwns(const string owner)
  { return(owner!="" && JPWUIOwner()==owner); }

bool JPWUIAcquire(const string owner)
  {
   if(owner=="") return(false);
   if(ObjectFind(0,JPW_UI_OWNER_OBJECT)<0 &&
      !ObjectCreate(0,JPW_UI_OWNER_OBJECT,OBJ_LABEL,0,0,0)) return(false);
   if(ObjectGetInteger(0,JPW_UI_OWNER_OBJECT,OBJPROP_TYPE)!=OBJ_LABEL) return(false);
   ObjectSetInteger(0,JPW_UI_OWNER_OBJECT,OBJPROP_XDISTANCE,100000);
   ObjectSetInteger(0,JPW_UI_OWNER_OBJECT,OBJPROP_YDISTANCE,100000);
   ObjectSetInteger(0,JPW_UI_OWNER_OBJECT,OBJPROP_HIDDEN,true);
   ObjectSetInteger(0,JPW_UI_OWNER_OBJECT,OBJPROP_SELECTABLE,false);
   ObjectSetString(0,JPW_UI_OWNER_OBJECT,OBJPROP_TEXT,"");
   if(!ObjectSetString(0,JPW_UI_OWNER_OBJECT,OBJPROP_TOOLTIP,owner) ||
      !JPWUIOwns(owner)) return(false);
   EventChartCustom(0,JPW_UI_OWNER_EVENT,0,0.0,owner);
   return(true);
  }

void JPWUIRelease(const string owner)
  {
   // Never release another module's ownership.
   if(JPWUIOwns(owner)) ObjectDelete(0,JPW_UI_OWNER_OBJECT);
  }
#endif
