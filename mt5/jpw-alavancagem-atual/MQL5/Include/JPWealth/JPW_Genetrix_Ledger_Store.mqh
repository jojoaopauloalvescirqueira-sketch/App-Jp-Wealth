#ifndef JPW_GENETRIX_LEDGER_STORE_MQH
#define JPW_GENETRIX_LEDGER_STORE_MQH
#include <JPWealth/JPW_Genetrix_Ledger_Core.mqh>
#include <JPWealth/JPW_Alavancagem_RaizN_Observer.mqh>
// Own schema/database only. Existing Genesis/MDD/ATR/USC stores are untouched.
#define JPW_LEDGER_SCHEMA 1
#define JPW_LEDGER_FOLDER "JPWealth\\Genetrix\\"
#define JPW_LEDGER_MAX_AGE_MS 30000

string JPWLedgerPath(const string key)
  { return(JPWRaizNIsHash(key) ? JPW_LEDGER_FOLDER+"ledger_"+key+".sqlite" : ""); }
string JPWLedgerLease(const string token)
  { return(JPWRaizNIsHash(token) ? "JPWGL_"+StringSubstr(token,0,48) : ""); }
string JPWLedgerNum(const double x) { return(DoubleToString(x,16)); }
string JPWLedgerInt(const long x) { return(IntegerToString(x)); }
int JPWLedgerHexDigit(const ushort c)
  { if(c>='0' && c<='9') return((int)(c-'0')); if(c>='a' && c<='f') return((int)(c-'a')+10); return(-1); }
string JPWLedgerHex(const string s)
  {
   if(s=="") return("-");
   uchar b[]; string result="";
   int n=StringToCharArray(s,b,0,WHOLE_ARRAY,CP_UTF8)-1;
   if(n<1 || n>4096) return("");
   for(int i=0;i<n;i++) result+=StringFormat("%02x",(int)b[i]);
   return(result);
  }
bool JPWLedgerUnhex(const string s,string &result)
  {
   result=""; if(s=="-") return(true);
   int n=StringLen(s); if(n<2 || n%2!=0 || n>8192) return(false);
   uchar b[]; if(ArrayResize(b,n/2)!=n/2) return(false);
   for(int i=0;i<n/2;i++)
     {
      int a=JPWLedgerHexDigit(StringGetCharacter(s,2*i));
      int c=JPWLedgerHexDigit(StringGetCharacter(s,2*i+1));
      if(a<0 || c<0) return(false); b[i]=(uchar)(16*a+c);
     }
   result=CharArrayToString(b,0,n/2,CP_UTF8);
   return(JPWLedgerHex(result)==s);
  }
string JPWLedgerEncodeDeal(JPWLedgerDeal &d)
  {
   return("1|"+JPWLedgerInt(d.ticket)+"|"+JPWLedgerInt(d.order_ticket)+"|"+
      JPWLedgerInt(d.position_id)+"|"+JPWLedgerInt(d.time_msc)+"|"+JPWLedgerHex(d.symbol)+"|"+
      JPWLedgerInt(d.kind)+"|"+JPWLedgerInt(d.side)+"|"+JPWLedgerInt(d.entry)+"|"+
      JPWLedgerInt(d.reason)+"|"+JPWLedgerNum(d.volume)+"|"+JPWLedgerNum(d.profit)+"|"+
      JPWLedgerNum(d.swap)+"|"+JPWLedgerNum(d.commission)+"|"+JPWLedgerNum(d.fee)+"|"+JPWLedgerInt(d.deleted)+"|"+JPWLedgerInt(d.adjustment_of));
  }
bool JPWLedgerDecodeDeal(const string raw,JPWLedgerDeal &d)
  {
   string p[]; if(StringSplit(raw,'|',p)!=17 || p[0]!="1") return(false);
   d.ticket=StringToInteger(p[1]); d.order_ticket=StringToInteger(p[2]);
   d.position_id=StringToInteger(p[3]); d.time_msc=StringToInteger(p[4]);
   if(!JPWLedgerUnhex(p[5],d.symbol)) return(false);
   d.kind=(int)StringToInteger(p[6]); d.side=(int)StringToInteger(p[7]);
   d.entry=(int)StringToInteger(p[8]); d.reason=(int)StringToInteger(p[9]);
   d.volume=StringToDouble(p[10]); d.profit=StringToDouble(p[11]); d.swap=StringToDouble(p[12]);
   d.commission=StringToDouble(p[13]); d.fee=StringToDouble(p[14]); d.deleted=(int)StringToInteger(p[15]);
   d.adjustment_of=StringToInteger(p[16]);
   return(JPWLedgerDealValid(d) && JPWLedgerEncodeDeal(d)==raw);
  }
string JPWLedgerEncodeOrder(JPWLedgerOrder &o)
  {
   return("1|"+JPWLedgerInt(o.ticket)+"|"+JPWLedgerInt(o.setup_msc)+"|"+
      JPWLedgerInt(o.done_msc)+"|"+JPWLedgerHex(o.symbol)+"|"+JPWLedgerInt(o.side)+"|"+
      JPWLedgerInt(o.state)+"|"+JPWLedgerNum(o.volume));
  }
bool JPWLedgerDecodeOrder(const string raw,JPWLedgerOrder &o)
  {
   string p[]; if(StringSplit(raw,'|',p)!=8 || p[0]!="1") return(false);
   o.ticket=StringToInteger(p[1]); o.setup_msc=StringToInteger(p[2]); o.done_msc=StringToInteger(p[3]);
   if(!JPWLedgerUnhex(p[4],o.symbol)) return(false);
   o.side=(int)StringToInteger(p[5]); o.state=(int)StringToInteger(p[6]); o.volume=StringToDouble(p[7]);
   return(o.ticket>0 && o.setup_msc>0 && o.state>=1 && o.state<=4 &&
      (o.side==1 || o.side==-1) && JPWLedgerFinite(o.volume) && o.volume>=0 && JPWLedgerEncodeOrder(o)==raw);
  }
string JPWLedgerEncodeCycleV1(JPWLedgerCycle &c)
  {
   return("1|"+JPWLedgerHex(c.cycle_id)+"|"+JPWLedgerHex(c.symbol)+"|"+JPWLedgerInt(c.side)+"|"+
      JPWLedgerInt(c.genesis_identifier)+"|"+JPWLedgerInt(c.genesis_deal)+"|"+JPWLedgerInt(c.started_msc)+"|"+
      JPWLedgerInt(c.ended_msc)+"|"+JPWLedgerInt(c.state)+"|"+JPWLedgerInt(c.genesis_inferred)+"|"+
      JPWLedgerInt(c.genesis_ambiguous)+"|"+JPWLedgerNum(c.realized_price)+"|"+JPWLedgerNum(c.realized_swap)+"|"+
      JPWLedgerNum(c.commissions)+"|"+JPWLedgerNum(c.fees)+"|"+JPWLedgerNum(c.unrealized_price)+"|"+
      JPWLedgerNum(c.unrealized_swap)+"|"+JPWLedgerNum(c.compensated)+"|"+JPWLedgerNum(c.percent)+"|"+
      JPWLedgerInt(c.amount_valid)+"|"+JPWLedgerInt(c.percent_valid)+"|"+JPWLedgerInt(c.partial)+"|"+
      JPWLedgerInt(c.history_complete)+"|"+JPWLedgerInt(c.costs_complete)+"|"+JPWLedgerInt(c.open_positions)+"|"+
      JPWLedgerInt(c.pending_orders)+"|"+JPWLedgerHex(c.reason));
  }
string JPWLedgerEncodeCycle(JPWLedgerCycle &c)
  {
   string v1=JPWLedgerEncodeCycleV1(c);
   return("2"+StringSubstr(v1,1)+"|"+JPWLedgerInt(c.members_available)+"|"+
      (c.member_identifiers=="" ? "-" : c.member_identifiers));
  }
bool JPWLedgerDecodeCycle(const string raw,JPWLedgerCycle &c)
  {
   string p[]; int count=StringSplit(raw,'|',p);
   bool old=(count==27 && p[0]=="1"),current=(count==29 && p[0]=="2");
   if(!old && !current) return(false);
   JPWLedgerClearCycle(c);
   if(!JPWLedgerUnhex(p[1],c.cycle_id) || !JPWLedgerUnhex(p[2],c.symbol) || !JPWLedgerUnhex(p[26],c.reason)) return(false);
   c.side=(int)StringToInteger(p[3]); c.genesis_identifier=StringToInteger(p[4]); c.genesis_deal=StringToInteger(p[5]);
   c.started_msc=StringToInteger(p[6]); c.ended_msc=StringToInteger(p[7]); c.state=(int)StringToInteger(p[8]);
   c.genesis_inferred=(bool)StringToInteger(p[9]); c.genesis_ambiguous=(bool)StringToInteger(p[10]);
   c.realized_price=StringToDouble(p[11]); c.realized_swap=StringToDouble(p[12]);
   c.commissions=StringToDouble(p[13]); c.fees=StringToDouble(p[14]);
   c.unrealized_price=StringToDouble(p[15]); c.unrealized_swap=StringToDouble(p[16]);
   c.compensated=StringToDouble(p[17]); c.percent=StringToDouble(p[18]);
   c.amount_valid=(bool)StringToInteger(p[19]); c.percent_valid=(bool)StringToInteger(p[20]); c.partial=(bool)StringToInteger(p[21]);
   c.history_complete=(bool)StringToInteger(p[22]); c.costs_complete=(bool)StringToInteger(p[23]);
   c.open_positions=(int)StringToInteger(p[24]); c.pending_orders=(int)StringToInteger(p[25]);
   if(current) { c.members_available=(bool)StringToInteger(p[27]); c.member_identifiers=(p[28]=="-" ? "" : p[28]); }
   if(c.cycle_id=="" || c.symbol=="" || (c.side!=1 && c.side!=-1) || c.started_msc<=0 ||
      c.ended_msc<0 || c.state<1 || c.state>4 || c.open_positions<0 || c.pending_orders<0 ||
      !JPWLedgerFinite(c.compensated) || !JPWLedgerFinite(c.percent)) return(false);
   double sum=c.realized_price+c.realized_swap+c.commissions+c.fees+c.unrealized_price+c.unrealized_swap;
   return(JPWLedgerNear(sum,c.compensated) && JPWLedgerMemberListValid(c) &&
      (old ? JPWLedgerEncodeCycleV1(c) : JPWLedgerEncodeCycle(c))==raw);
  }
bool JPWLedgerSQL(const int db,const string sql)
  { ResetLastError(); return(DatabaseExecute(db,sql)); }
bool JPWLedgerWriteBound(const int db,const string sql,const long ticket,const long revision,
                         const string payload,const string digest,const long observed)
  {
   int q=DatabasePrepare(db,sql); if(q==INVALID_HANDLE) return(false);
   bool ok=DatabaseBind(q,0,ticket) && DatabaseBind(q,1,revision) &&
      DatabaseBind(q,2,payload) && DatabaseBind(q,3,digest) && DatabaseBind(q,4,observed);
   if(ok) { ResetLastError(); DatabaseRead(q); ok=(GetLastError()==ERR_DATABASE_NO_MORE_DATA); }
   DatabaseFinalize(q); return(ok);
  }
bool JPWLedgerSchema(const int db,const string key)
  {
   if(!DatabaseTransactionBegin(db)) return(false);
   bool ok=JPWLedgerSQL(db,"CREATE TABLE ledger_meta (id INTEGER PRIMARY KEY CHECK(id=1),schema_version INTEGER NOT NULL,account_key TEXT NOT NULL,generation INTEGER NOT NULL,payload TEXT NOT NULL,digest TEXT NOT NULL)") &&
      JPWLedgerSQL(db,"CREATE TABLE ledger_deals (ticket INTEGER PRIMARY KEY,revision INTEGER NOT NULL,payload TEXT NOT NULL,digest TEXT NOT NULL,observed INTEGER NOT NULL)") &&
      JPWLedgerSQL(db,"CREATE TABLE ledger_deal_revisions (ticket INTEGER NOT NULL,revision INTEGER NOT NULL,payload TEXT NOT NULL,digest TEXT NOT NULL,observed INTEGER NOT NULL,PRIMARY KEY(ticket,revision))") &&
      JPWLedgerSQL(db,"CREATE TABLE ledger_orders (ticket INTEGER PRIMARY KEY,revision INTEGER NOT NULL,payload TEXT NOT NULL,digest TEXT NOT NULL,observed INTEGER NOT NULL)") &&
      JPWLedgerSQL(db,"CREATE TABLE ledger_faults (ticket INTEGER PRIMARY KEY,code TEXT NOT NULL)") &&
      JPWLedgerSQL(db,"CREATE TABLE ledger_projection (generation INTEGER NOT NULL,rowno INTEGER NOT NULL,payload TEXT NOT NULL,digest TEXT NOT NULL,PRIMARY KEY(generation,rowno))");
   int q=DatabasePrepare(db,"INSERT INTO ledger_meta VALUES(1,?1,?2,0,'','')");
   if(q==INVALID_HANDLE) ok=false;
   else
     {
      ok=ok && DatabaseBind(q,0,JPW_LEDGER_SCHEMA) && DatabaseBind(q,1,key);
      if(ok) { ResetLastError(); DatabaseRead(q); ok=(GetLastError()==ERR_DATABASE_NO_MORE_DATA); }
      DatabaseFinalize(q);
     }
   if(ok) ok=DatabaseTransactionCommit(db);
   if(!ok) DatabaseTransactionRollback(db);
   return(ok);
  }
bool JPWLedgerOpen(const string key,const bool writer,int &db,string &reason)
  {
   db=INVALID_HANDLE; reason=""; string path=JPWLedgerPath(key);
   if(path=="") { reason="Identidade inválida"; return(false); }
   bool exists=FileIsExist(path);
   if(!exists && !writer) { reason="Ledger ausente; Accountant não confirmado"; return(false); }
   if(writer && !FolderCreate("JPWealth\\Genetrix")) { reason="Diretório indisponível"; return(false); }
   db=DatabaseOpen(path,writer ? DATABASE_OPEN_READWRITE|DATABASE_OPEN_CREATE : DATABASE_OPEN_READONLY);
   if(db==INVALID_HANDLE) { reason="Banco indisponível/ocupado"; return(false); }
   if(!exists && !JPWLedgerSchema(db,key)) { reason="Inicialização recusada"; DatabaseClose(db); db=INVALID_HANDLE; return(false); }
   int q=DatabasePrepare(db,"SELECT schema_version,account_key FROM ledger_meta WHERE id=1");
   int schema=0; string stored="";
   bool ok=q!=INVALID_HANDLE && DatabaseRead(q) && DatabaseColumnInteger(q,0,schema) && DatabaseColumnText(q,1,stored) &&
      schema==JPW_LEDGER_SCHEMA && stored==key;
   if(q!=INVALID_HANDLE) DatabaseFinalize(q);
   if(!ok) { reason="Schema/conta incompatível ou banco corrompido; nenhum reset"; DatabaseClose(db); db=INVALID_HANDLE; }
   return(ok);
  }
// Caller owns a transaction. Identical replay is a no-op; every changed deal
// has a new audited revision. The latest row is never assumed immutable.
bool JPWLedgerUpsert(const int db,const string table,const long ticket,const string payload,
                     const long observed,string &reason)
  {
   reason=""; if(table!="ledger_deals" && table!="ledger_orders") return(false);
   string digest=""; if(!JPWRaizNHash(payload,digest)) return(false);
   int q=DatabasePrepare(db,"SELECT revision,payload,digest FROM "+table+" WHERE ticket=?1");
   if(q==INVALID_HANDLE || !DatabaseBind(q,0,ticket)) { if(q!=INVALID_HANDLE) DatabaseFinalize(q); return(false); }
   ResetLastError(); bool present=DatabaseRead(q); long revision=0; string old="",old_digest="",verified="";
   bool ok=true;
   if(present) ok=DatabaseColumnLong(q,0,revision) && DatabaseColumnText(q,1,old) && DatabaseColumnText(q,2,old_digest) &&
      revision>0 && JPWRaizNHash(old,verified) && verified==old_digest;
   else ok=(GetLastError()==ERR_DATABASE_NO_MORE_DATA);
   DatabaseFinalize(q);
   if(!ok) { reason="Registro bruto corrompido; escrita recusada"; return(false); }
   if(present && old==payload) return(true);
   revision++;
   if(table=="ledger_deals" && !JPWLedgerWriteBound(db,
      "INSERT INTO ledger_deal_revisions VALUES(?1,?2,?3,?4,?5)",ticket,revision,payload,digest,observed)) return(false);
   return(JPWLedgerWriteBound(db,"INSERT OR REPLACE INTO "+table+" VALUES(?1,?2,?3,?4,?5)",
      ticket,revision,payload,digest,observed));
  }
bool JPWLedgerLoadRaw(const int db,JPWLedgerDeal &deals[],JPWLedgerOrder &orders[],string &reason)
  {
   ArrayResize(deals,0); ArrayResize(orders,0); reason="";
   int integrity=DatabasePrepare(db,"PRAGMA quick_check"); string status="";
   bool intact=integrity!=INVALID_HANDLE && DatabaseRead(integrity) && DatabaseColumnText(integrity,0,status) && status=="ok";
   if(integrity!=INVALID_HANDLE) DatabaseFinalize(integrity);
   if(!intact) { reason="Integridade SQLite recusada; nenhum reset"; return(false); }
   // Audit rows witness the latest raw set as well as revisions. Losing a
   // latest row or changing its revision cannot silently empty/restart cycles.
   string audit_sql="SELECT COUNT(*) FROM (SELECT ticket,MAX(revision) AS last_revision FROM ledger_deal_revisions GROUP BY ticket) r LEFT JOIN ledger_deals d ON d.ticket=r.ticket WHERE d.ticket IS NULL OR d.revision<>r.last_revision";
   int audit=DatabasePrepare(db,audit_sql),bad=0;
   intact=audit!=INVALID_HANDLE && DatabaseRead(audit) && DatabaseColumnInteger(audit,0,bad) && bad==0;
   if(audit!=INVALID_HANDLE) DatabaseFinalize(audit);
   audit=DatabasePrepare(db,"SELECT COUNT(*) FROM ledger_deals d LEFT JOIN ledger_deal_revisions r ON r.ticket=d.ticket AND r.revision=d.revision WHERE r.ticket IS NULL OR r.payload<>d.payload OR r.digest<>d.digest");
   intact=intact && audit!=INVALID_HANDLE && DatabaseRead(audit) && DatabaseColumnInteger(audit,0,bad) && bad==0;
   if(audit!=INVALID_HANDLE) DatabaseFinalize(audit);
   if(!intact) { reason="Conjunto bruto/auditoria divergente; escrita recusada"; return(false); }
   for(int table=0;table<2;table++)
     {
      int q=DatabasePrepare(db,"SELECT ticket,payload,digest FROM "+(table==0 ? "ledger_deals" : "ledger_orders")+" ORDER BY ticket");
      if(q==INVALID_HANDLE) return(false);
      bool ok=true; ResetLastError();
      while(DatabaseRead(q))
        {
         long ticket=0; string raw="",digest="",actual="";
         if(!DatabaseColumnLong(q,0,ticket) || !DatabaseColumnText(q,1,raw) || !DatabaseColumnText(q,2,digest) ||
            !JPWRaizNHash(raw,actual) || actual!=digest) { ok=false; break; }
         if(table==0)
           {
            JPWLedgerDeal d; int n=ArraySize(deals);
            if(n>=JPW_LEDGER_MAX_RECORDS || !JPWLedgerDecodeDeal(raw,d) || d.ticket!=ticket || ArrayResize(deals,n+1)!=n+1)
              { ok=false; break; }
            deals[n]=d;
           }
         else
           {
            JPWLedgerOrder o; int n=ArraySize(orders);
            if(n>=JPW_LEDGER_MAX_RECORDS || !JPWLedgerDecodeOrder(raw,o) || o.ticket!=ticket || ArrayResize(orders,n+1)!=n+1)
              { ok=false; break; }
            orders[n]=o;
           }
         ResetLastError();
        }
      if(ok) ok=(GetLastError()==ERR_DATABASE_NO_MORE_DATA);
      DatabaseFinalize(q);
      if(!ok) { reason="Histórico local corrompido/incompatível ou excessivo"; return(false); }
     }
   return(true);
  }
string JPWLedgerEncodeView(JPWLedgerView &v,const int count,const string composition)
  {
   return("1|"+JPWLedgerHex(v.account_key)+"|"+JPWLedgerHex(v.currency)+"|"+JPWLedgerHex(v.publisher_token)+"|"+
      JPWLedgerInt(v.generation)+"|"+JPWLedgerInt(v.observed_utc)+"|"+JPWLedgerInt(v.observed_mono_ms)+"|"+
      JPWLedgerInt(v.margin_mode)+"|"+JPWLedgerNum(v.balance)+"|"+JPWLedgerInt(v.quality)+"|"+
      JPWLedgerInt(v.history_complete)+"|"+JPWLedgerInt(v.costs_complete)+"|"+JPWLedgerInt(v.healthy)+"|"+
      JPWLedgerInt(count)+"|"+JPWLedgerHex(composition)+"|"+JPWLedgerHex(v.reason));
  }
bool JPWLedgerDecodeView(const string raw,JPWLedgerView &v,int &count,string &composition)
  {
   string p[]; if(StringSplit(raw,'|',p)!=16 || p[0]!="1") return(false);
   JPWLedgerClearView(v);
   if(!JPWLedgerUnhex(p[1],v.account_key) || !JPWLedgerUnhex(p[2],v.currency) ||
      !JPWLedgerUnhex(p[3],v.publisher_token) || !JPWLedgerUnhex(p[14],composition) || !JPWLedgerUnhex(p[15],v.reason)) return(false);
   v.generation=StringToInteger(p[4]); v.observed_utc=StringToInteger(p[5]); v.observed_mono_ms=StringToInteger(p[6]);
   v.margin_mode=StringToInteger(p[7]); v.balance=StringToDouble(p[8]); v.quality=(int)StringToInteger(p[9]);
   v.history_complete=(bool)StringToInteger(p[10]); v.costs_complete=(bool)StringToInteger(p[11]); v.healthy=(bool)StringToInteger(p[12]);
   count=(int)StringToInteger(p[13]);
   return(JPWRaizNIsHash(v.account_key) && JPWRaizNIsHash(v.publisher_token) && JPWRaizNIsHash(composition) &&
      v.generation>0 && v.observed_utc>0 && v.observed_mono_ms>0 && v.currency!="" &&
      JPWLedgerFinite(v.balance) && count>=0 && count<=JPW_LEDGER_MAX_CYCLES && v.quality>=0 && v.quality<=2 &&
      JPWLedgerEncodeView(v,count,composition)==raw);
  }
bool JPWLedgerReadProjection(const int db,const string key,JPWLedgerView &view,
                             JPWLedgerCycle &cycles[],string &composition,string &reason)
  {
   JPWLedgerClearView(view); ArrayResize(cycles,0); composition=""; reason="";
   int q=DatabasePrepare(db,"SELECT generation,payload,digest FROM ledger_meta WHERE id=1 AND account_key=?1");
   if(q==INVALID_HANDLE || !DatabaseBind(q,0,key)) { if(q!=INVALID_HANDLE) DatabaseFinalize(q); return(false); }
   string raw="",digest="",actual=""; long generation=0; int count=0;
   bool ok=DatabaseRead(q) && DatabaseColumnLong(q,0,generation) && generation>0 &&
      DatabaseColumnText(q,1,raw) && DatabaseColumnText(q,2,digest) && JPWRaizNHash(raw,actual) && actual==digest &&
      JPWLedgerDecodeView(raw,view,count,composition) && view.account_key==key && view.generation==generation;
   DatabaseFinalize(q);
   if(!ok) { reason="Projeção ausente/corrompida; nenhuma inicialização silenciosa"; return(false); }
   q=DatabasePrepare(db,"SELECT rowno,payload,digest FROM ledger_projection WHERE generation=?1 ORDER BY rowno");
   if(q==INVALID_HANDLE || !DatabaseBind(q,0,generation)) { if(q!=INVALID_HANDLE) DatabaseFinalize(q); return(false); }
   int n=0; ResetLastError();
   while(DatabaseRead(q))
     {
      int row=0; JPWLedgerCycle c;
      if(n>=count || !DatabaseColumnInteger(q,0,row) || row!=n || !DatabaseColumnText(q,1,raw) ||
         !DatabaseColumnText(q,2,digest) || !JPWRaizNHash(raw,actual) || actual!=digest ||
         !JPWLedgerDecodeCycle(raw,c) || ArrayResize(cycles,n+1)!=n+1) { ok=false; break; }
      if(c.percent_valid && (!c.amount_valid || view.balance<=0 ||
         !JPWLedgerNear(c.percent,100.0*(c.compensated/view.balance)))) { ok=false; break; }
      cycles[n++]=c; ResetLastError();
     }
   if(ok) ok=(GetLastError()==ERR_DATABASE_NO_MORE_DATA && n==count && JPWLedgerMembershipProjectionValid(cycles));
   DatabaseFinalize(q);
   if(!ok) { JPWLedgerClearView(view); ArrayResize(cycles,0); reason="Geração incompleta/corrompida"; }
   return(ok);
  }
bool JPWLedgerWriteProjection(const int db,JPWLedgerView &view,JPWLedgerCycle &cycles[],
                              const string composition,string &reason)
  {
   int q=DatabasePrepare(db,"SELECT generation FROM ledger_meta WHERE id=1"); long previous=0;
   bool ok=q!=INVALID_HANDLE && DatabaseRead(q) && DatabaseColumnLong(q,0,previous) && previous>=0 && previous<LONG_MAX-1;
   if(q!=INVALID_HANDLE) DatabaseFinalize(q);
   if(!ok) return(false);
   view.generation=previous+1;
   for(int i=0;i<ArraySize(cycles);i++)
     {
      string raw=JPWLedgerEncodeCycle(cycles[i]),digest="";
      if(!JPWRaizNHash(raw,digest)) return(false);
      q=DatabasePrepare(db,"INSERT INTO ledger_projection VALUES(?1,?2,?3,?4)");
      ok=q!=INVALID_HANDLE && DatabaseBind(q,0,view.generation) && DatabaseBind(q,1,i) && DatabaseBind(q,2,raw) && DatabaseBind(q,3,digest);
      if(ok) { ResetLastError(); DatabaseRead(q); ok=(GetLastError()==ERR_DATABASE_NO_MORE_DATA); }
      if(q!=INVALID_HANDLE) DatabaseFinalize(q);
      if(!ok) return(false);
     }
   string raw=JPWLedgerEncodeView(view,ArraySize(cycles),composition),digest="";
   if(!JPWRaizNHash(raw,digest)) return(false);
   q=DatabasePrepare(db,"UPDATE ledger_meta SET generation=?1,payload=?2,digest=?3 WHERE id=1 AND account_key=?4");
   ok=q!=INVALID_HANDLE && DatabaseBind(q,0,view.generation) && DatabaseBind(q,1,raw) && DatabaseBind(q,2,digest) && DatabaseBind(q,3,view.account_key);
   if(ok) { ResetLastError(); DatabaseRead(q); ok=(GetLastError()==ERR_DATABASE_NO_MORE_DATA); }
   if(q!=INVALID_HANDLE) DatabaseFinalize(q);
   if(!ok) return(false);
   // Projection cache only; raw financial revisions are never rotated/deleted.
   if(!JPWLedgerSQL(db,"DELETE FROM ledger_projection WHERE generation<"+JPWLedgerInt(view.generation-1))) return(false);
   JPWLedgerView checked; JPWLedgerCycle rows[]; string observed="";
   return(JPWLedgerReadProjection(db,view.account_key,checked,rows,observed,reason) && checked.generation==view.generation && observed==composition);
  }
bool JPWLedgerFault(const int db,const long ticket,const bool clear)
  {
   int q=DatabasePrepare(db,clear ? "DELETE FROM ledger_faults WHERE ticket=?1" :
      "INSERT OR IGNORE INTO ledger_faults VALUES(?1,'DELETE_ORIGIN_UNKNOWN')");
   bool ok=q!=INVALID_HANDLE && DatabaseBind(q,0,ticket);
   if(ok) { ResetLastError(); DatabaseRead(q); ok=(GetLastError()==ERR_DATABASE_NO_MORE_DATA); }
   if(q!=INVALID_HANDLE) DatabaseFinalize(q); return(ok);
  }
// All observations, raw revisions and the derived generation commit together.
// Missing source rows are retained and lower completeness, never tombstoned.
bool JPWLedgerCommitCollection(const int db,JPWLedgerDeal &incoming[],JPWLedgerOrder &incoming_orders[],
                               JPWLedgerPosition &live[],long &known_deletes[],const bool queue_loss,
                               JPWLedgerView &view,const string composition,string &reason)
  {
   reason=""; if(!DatabaseTransactionBegin(db)) { reason="Ledger ocupado"; return(false); }
   if(!JPWLedgerUniqueRaw(incoming,incoming_orders,reason))
     { DatabaseTransactionRollback(db); return(false); }
   JPWLedgerDeal old[]; JPWLedgerOrder old_orders[];
   bool ok=JPWLedgerLoadRaw(db,old,old_orders,reason);
   // A damaged published generation cannot be overwritten to mask corruption.
   int meta=DatabasePrepare(db,"SELECT generation FROM ledger_meta WHERE id=1"); long generation=0;
   ok=ok && meta!=INVALID_HANDLE && DatabaseRead(meta) && DatabaseColumnLong(meta,0,generation);
   if(meta!=INVALID_HANDLE) DatabaseFinalize(meta);
   if(ok && generation>0)
     { JPWLedgerView previous; JPWLedgerCycle rows[]; string digest="";
       ok=JPWLedgerReadProjection(db,view.account_key,previous,rows,digest,reason); }
   if(queue_loss && ok) ok=JPWLedgerFault(db,0,false);
   for(int i=0;ok && i<ArraySize(known_deletes);i++)
     {
      bool observed=false;
      for(int j=0;j<ArraySize(incoming);j++) if(incoming[j].ticket==known_deletes[i]) { observed=true; break; }
      if(observed) continue; // latest native state supersedes an earlier queued notice
      bool found=false;
      for(int j=0;j<ArraySize(old);j++) if(old[j].ticket==known_deletes[i])
        { old[j].deleted=1; found=true;
          ok=JPWLedgerUpsert(db,"ledger_deals",old[j].ticket,JPWLedgerEncodeDeal(old[j]),view.observed_utc,reason); break; }
      if(ok) ok=JPWLedgerFault(db,known_deletes[i],found);
     }
   for(int i=0;ok && i<ArraySize(old);i++) if(!old[i].deleted)
     {
      bool observed=false;
      for(int j=0;j<ArraySize(incoming);j++) if(old[i].ticket==incoming[j].ticket) { observed=true; break; }
      if(!observed) view.history_complete=false;
     }
   for(int i=0;ok && i<ArraySize(old_orders);i++) if(old_orders[i].state==1 || old_orders[i].state==4)
     {
      bool observed=false;
      for(int j=0;j<ArraySize(incoming_orders);j++) if(old_orders[i].ticket==incoming_orders[j].ticket) { observed=true; break; }
      if(!observed)
        { old_orders[i].state=4; old_orders[i].done_msc=0; view.history_complete=false;
          ok=JPWLedgerUpsert(db,"ledger_orders",old_orders[i].ticket,JPWLedgerEncodeOrder(old_orders[i]),view.observed_utc,reason); }
     }
   for(int i=0;ok && i<ArraySize(incoming);i++)
      ok=JPWLedgerUpsert(db,"ledger_deals",incoming[i].ticket,JPWLedgerEncodeDeal(incoming[i]),view.observed_utc,reason) &&
         JPWLedgerFault(db,incoming[i].ticket,true);
   for(int i=0;ok && i<ArraySize(incoming_orders);i++)
      ok=JPWLedgerUpsert(db,"ledger_orders",incoming_orders[i].ticket,JPWLedgerEncodeOrder(incoming_orders[i]),view.observed_utc,reason);
   int faults=DatabasePrepare(db,"SELECT COUNT(*) FROM ledger_faults"); int fault_count=0;
   ok=ok && faults!=INVALID_HANDLE && DatabaseRead(faults) && DatabaseColumnInteger(faults,0,fault_count);
   if(faults!=INVALID_HANDLE) DatabaseFinalize(faults);
   if(fault_count>0) view.history_complete=false;
   JPWLedgerDeal current[]; JPWLedgerOrder orders[]; JPWLedgerCycle cycles[];
   if(ok) ok=JPWLedgerLoadRaw(db,current,orders,reason) && JPWLedgerBuild(current,orders,live,view,cycles,reason);
   if(!view.history_complete && view.reason=="") view.reason="Cobertura histórica não reconciliada; nenhuma lacuna convertida em zero";
   if(ok) ok=JPWLedgerWriteProjection(db,view,cycles,composition,reason);
   if(ok) ok=DatabaseTransactionCommit(db);
   if(!ok) { DatabaseTransactionRollback(db); if(reason=="") reason="Transação/releitura recusada"; }
   return(ok);
  }
#endif
