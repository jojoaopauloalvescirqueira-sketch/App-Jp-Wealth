#ifndef JPW_STOIKUS_PANEL_BRIDGE_MQH
#define JPW_STOIKUS_PANEL_BRIDGE_MQH
// Chart-local presentation handshake. This is neither sample freshness nor an
// authorization boundary. No object, file, terminal-global or account reads.
// EventChartCustom sparam is limited to 63 characters; never send a truncation.
#define JPW_STOIKUS_PANEL_EVENT 3121
// lp: 1/2 Account/NoCuda announce, 3/4 depart, 5 addressed NoCuda open.
// Announce/depart: sp=publisher owner, dp=its live ticket.
// Open: sp=exact NoCuda owner, dp=current Account ticket learned live.
#define JPW_STOIKUS_PANEL_TTL_MS 15000
string g_jpw_panel_self="",g_jpw_panel_peer="";
bool g_jpw_panel_account=false;
ulong g_jpw_panel_seen=0;
double g_jpw_panel_token=0.0,g_jpw_panel_peer_token=0.0;

bool JPWStoikusPanelOwnerValid(const string owner)
  { return(StringLen(owner)>0 && StringLen(owner)<=63); }
bool JPWStoikusPanelTokenValid(const double token)
  { return(MathIsValidNumber(token) && token>0.0 && token<=9007199254740991.0 && MathFloor(token)==token); }
bool JPWStoikusPanelPeerReady(const bool account)
  {
   const ulong now=GetTickCount64();
   return(g_jpw_panel_self!="" && g_jpw_panel_account==account &&
      g_jpw_panel_peer!="" && now>=g_jpw_panel_seen &&
      now-g_jpw_panel_seen<=JPW_STOIKUS_PANEL_TTL_MS);
  }
void JPWStoikusPanelAnnounce(const bool account,const string owner)
  {
   if(!JPWStoikusPanelOwnerValid(owner)) return;
   if(g_jpw_panel_self!="" && (g_jpw_panel_self!=owner || g_jpw_panel_account!=account)) return;
   if(g_jpw_panel_self=="")
     {
      // Exact integer ticket, local to this live publisher. Not a secret.
      const double token=(double)GetTickCount64()*1024.0+(double)(GetMicrosecondCount()%1024)+1.0;
      if(!JPWStoikusPanelTokenValid(token)) return;
      g_jpw_panel_self=owner;g_jpw_panel_account=account;g_jpw_panel_token=token;
     }
   EventChartCustom(0,JPW_STOIKUS_PANEL_EVENT,(account ? 1 : 2),g_jpw_panel_token,owner);
  }
void JPWStoikusPanelDepart(const bool account,const string owner)
  {
   if(owner=="" || owner!=g_jpw_panel_self || account!=g_jpw_panel_account) return;
   EventChartCustom(0,JPW_STOIKUS_PANEL_EVENT,(account ? 3 : 4),g_jpw_panel_token,owner);
   g_jpw_panel_self="";g_jpw_panel_peer="";
   g_jpw_panel_token=0.0;g_jpw_panel_peer_token=0.0;g_jpw_panel_seen=0;
  }
bool JPWStoikusPanelReceive(const int id,const long &lp,const double &dp,const string &sp,
                            const bool account,const string owner,bool &open_requested)
  {
   open_requested=false;
   if(id!=CHARTEVENT_CUSTOM+JPW_STOIKUS_PANEL_EVENT) return(false);
   if(owner=="" || owner!=g_jpw_panel_self || account!=g_jpw_panel_account ||
      !JPWStoikusPanelOwnerValid(sp) || !JPWStoikusPanelTokenValid(dp)) return(true);
   const long announce=(account ? 2 : 1),depart=(account ? 4 : 3);
   if(lp==announce)
     {
      const bool discovered=!JPWStoikusPanelPeerReady(account) ||
         g_jpw_panel_peer!=sp || g_jpw_panel_peer_token!=dp;
      g_jpw_panel_peer=sp;g_jpw_panel_peer_token=dp;g_jpw_panel_seen=GetTickCount64();
      // One reply upon discovery handles either attach order without a loop.
      if(discovered) JPWStoikusPanelAnnounce(account,owner);
     }
   else if(lp==depart && sp==g_jpw_panel_peer && dp==g_jpw_panel_peer_token)
     { g_jpw_panel_peer="";g_jpw_panel_peer_token=0.0;g_jpw_panel_seen=0; }
   else if(!account && lp==5 && sp==owner && JPWStoikusPanelPeerReady(false) &&
           dp==g_jpw_panel_peer_token)
      open_requested=true;
   return(true);
  }
bool JPWStoikusPanelOpenNoCuda(const string owner)
  {
   if(owner=="" || owner!=g_jpw_panel_self || !JPWStoikusPanelPeerReady(true)) return(false);
   return(EventChartCustom(0,JPW_STOIKUS_PANEL_EVENT,5,g_jpw_panel_token,g_jpw_panel_peer));
  }
#endif
