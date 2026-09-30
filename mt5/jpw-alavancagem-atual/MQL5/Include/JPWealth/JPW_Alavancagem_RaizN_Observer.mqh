#ifndef JPW_ALAVANCAGEM_RAIZN_OBSERVER_MQH
#define JPW_ALAVANCAGEM_RAIZN_OBSERVER_MQH

#include <JPWealth/JPW_Alavancagem_RaizN_Store.mqh>
#include <JPWealth/JPW_Alavancagem_Store_Result.mqh>

// Registro independente de MDD, Genese, perfil USC e cenarios declarados.
// O observador nao envia ordens. Um snapshot descreve preco EXECUTADO, nao
// o preco de decisao humana nem a intencao de permanencia na operacao.
#define JPW_OBSERVER_FOLDER "JPWealth\\Alavancagem\\"
#define JPW_OBSERVER_SCHEMA 2
#define JPW_OBSERVER_MAX_DEALS 4096
#define JPW_OBSERVER_CAPTURED_EVENT 1
#define JPW_OBSERVER_RECONSTRUCTED 2
#define JPW_OBSERVER_CAPTURE_WINDOW_MS 5000

struct JPWObserverDeal
  {
   long ticket;
   long order_ticket;
   long position_id;
   long time_msc;
   int entry;
   int side; // +1 buy, -1 sell
   string symbol;
   double volume;
   double price;
  };

// A ordem dos campos coincide com o SELECT explicito em JPWObserverReadByKey.
struct JPWObserverSnapshot
  {
   string episode_key;
   string account_key;
   string symbol;
   long position_id;
   long first_deal_ticket;
   long deal_time_msc;
   int side;
   double executed_p0;
   double atr55_h4;
   long atr_bar_open;
   int n_1w;
   int n_2w;
   int status_1w;
   int status_2w;
   string horizon_source;
   string horizon_hash;
   long horizon_observed_utc;
   long observer_recorded_utc;
   long event_arrival_utc; // Callback UTC, not broker execution time.
   long event_processing_delay_ms; // Monotonic callback-to-processing delay.
   int provenance;
   string checksum;
  };

void JPWObserverClear(JPWObserverSnapshot &snapshot)
  {
   snapshot.episode_key=""; snapshot.account_key=""; snapshot.symbol="";
   snapshot.position_id=0; snapshot.first_deal_ticket=0;
   snapshot.deal_time_msc=0; snapshot.side=0; snapshot.executed_p0=0.0;
   snapshot.atr55_h4=0.0; snapshot.atr_bar_open=0;
   snapshot.n_1w=0; snapshot.n_2w=0;
   snapshot.status_1w=0; snapshot.status_2w=0;
   snapshot.horizon_source=""; snapshot.horizon_hash="";
   snapshot.horizon_observed_utc=0; snapshot.observer_recorded_utc=0;
   snapshot.event_arrival_utc=0; snapshot.event_processing_delay_ms=0;
   snapshot.provenance=0; snapshot.checksum="";
  }

bool JPWObserverAccountKey(const string server,const long login,
                           const string currency,const string installation,
                           string &key)
  {
   key="";
   const string normalized=JPWNormalizeCurrency(currency);
   if(server=="" || login<=0 || normalized=="" || installation=="")
      return(false);
   const string raw=JPWRaizNFrame(server)+
                    JPWRaizNFrame(IntegerToString(login))+
                    JPWRaizNFrame(normalized)+
                    JPWRaizNFrame(installation)+
                    JPWRaizNFrame("raiz_n_observer_v1");
   return(JPWRaizNHash(raw,key));
  }

bool JPWObserverEpisodeKey(const string account_key,const string symbol,
                           const long position_id,const long first_deal,
                           string &key)
  {
   key="";
   if(!JPWRaizNIsHash(account_key) || !JPWRaizNSymbolValid(symbol) ||
      position_id<=0 || first_deal<=0) return(false);
   return(JPWRaizNHash(JPWRaizNFrame(account_key)+JPWRaizNFrame(symbol)+
       JPWRaizNFrame(IntegerToString(position_id))+
       JPWRaizNFrame(IntegerToString(first_deal))+
       JPWRaizNFrame("episode_v1"),key));
  }

int JPWObserverCompareDeals(JPWObserverDeal &a,JPWObserverDeal &b)
  {
   if(a.time_msc<b.time_msc) return(-1);
   if(a.time_msc>b.time_msc) return(1);
   if(a.ticket<b.ticket) return(-1);
   if(a.ticket>b.ticket) return(1);
   return(0);
  }

void JPWObserverSortDeals(JPWObserverDeal &deals[],const int left,const int right)
  {
   int i=left,j=right;
   JPWObserverDeal pivot=deals[(left+right)/2];
   while(i<=j)
     {
      while(JPWObserverCompareDeals(deals[i],pivot)<0) i++;
      while(JPWObserverCompareDeals(deals[j],pivot)>0) j--;
      if(i<=j)
        {
         JPWObserverDeal temp=deals[i]; deals[i]=deals[j]; deals[j]=temp;
         i++; j--;
        }
     }
   if(left<j) JPWObserverSortDeals(deals,left,j);
   if(i<right) JPWObserverSortDeals(deals,i,right);
  }

// A lista deve conter a historia completa do identificador. Ela e ordenada
// para nao depender da ordem de chegada de OnTradeTransaction. OUT parcial e
// IN adicional conservam a origem; INOUT de netting abre episodio novo.
bool JPWObserverFindEpisode(JPWObserverDeal &deals[],const long target_ticket,
                            JPWObserverDeal &start,string &reason)
  {
   reason="";
   const int count=ArraySize(deals);
   if(count<1 || count>JPW_OBSERVER_MAX_DEALS || target_ticket<=0)
     { reason="Historico ausente ou excessivo"; return(false); }
   JPWObserverSortDeals(deals,0,count-1);
   // Ticket numbering is a stable tie breaker for sorting, but does not
   // prove execution order within one server millisecond. Refuse such a tie
   // through the target deal instead of inventing the first execution.
   long target_time=0;
   for(int i=0;i<count;i++)
      if(deals[i].ticket==target_ticket)
        { target_time=deals[i].time_msc; break; }
   if(target_time<=0)
     { reason="Negocio alvo ausente do historico completo"; return(false); }
   for(int i=1;i<count;i++)
      if(deals[i].time_msc==deals[i-1].time_msc &&
         deals[i].time_msc<=target_time)
        { reason="Ordem de negocios no mesmo milissegundo ambigua";
          return(false); }
   // MetaQuotes defines POSITION_IDENTIFIER as the opening order's ticket.
   // A selected history beginning at a later same-direction addition still
   // has DEAL_ENTRY_IN; without this anchor it would be misnamed the first
   // execution. If the opening order is absent, refuse reconstruction.
   // This does not certify that every partial fill of the same opening order
   // was delivered; order-volume fields are not a universal completeness
   // proof across active and historical partial orders.
   if(deals[0].entry!=DEAL_ENTRY_IN ||
      deals[0].order_ticket<=0 ||
      deals[0].order_ticket!=deals[0].position_id)
     { reason="Ordem original de abertura ausente do historico"; return(false); }
   double open_volume=0.0;
   int open_side=0;
   long position_id=0;
   string symbol="";
   bool have_start=false;
   for(int i=0;i<count;i++)
     {
      JPWObserverDeal deal=deals[i];
      if(deal.ticket<=0 || deal.order_ticket<=0 || deal.time_msc<=0 ||
         deal.position_id<=0 ||
         !JPWRaizNSymbolValid(deal.symbol) ||
         !JPWFinitePositive(deal.volume) || !JPWFinitePositive(deal.price) ||
         (deal.side!=1 && deal.side!=-1))
        { reason="Negocio invalido no historico"; return(false); }
      if(i==0) { position_id=deal.position_id; symbol=deal.symbol; }
      if(deal.position_id!=position_id || deal.symbol!=symbol)
        { reason="Historico de posicao inconsistente"; return(false); }
      if(deal.entry==DEAL_ENTRY_IN)
        {
         if(open_volume<=0.0)
           { start=deal; open_side=deal.side; open_volume=deal.volume;
             have_start=true; }
         else if(open_side==deal.side) open_volume+=deal.volume;
         else { reason="Direcao IN inconsistente"; return(false); }
        }
      else if(deal.entry==DEAL_ENTRY_OUT || deal.entry==DEAL_ENTRY_OUT_BY)
        {
         if(open_volume<=0.0 || open_side==deal.side ||
            deal.volume>open_volume+1e-8)
           { reason="Fechamento sem abertura comprovada"; return(false); }
         open_volume-=deal.volume;
         if(open_volume<=1e-8) { open_volume=0.0; open_side=0;
                                 have_start=false; }
        }
      else if(deal.entry==DEAL_ENTRY_INOUT)
        {
         if(open_volume<=0.0 || open_side==deal.side ||
            deal.volume<=open_volume+1e-8)
           { reason="Reversao sem origem comprovada"; return(false); }
         open_volume=deal.volume-open_volume;
         open_side=deal.side;
         start=deal; have_start=true;
        }
      else { reason="Tipo de entrada nao suportado"; return(false); }
      if(deal.ticket==target_ticket)
        {
         if(!have_start || open_volume<=0.0)
           { reason="Episodio nao aberto no negocio consultado"; return(false); }
         return(true);
        }
     }
   reason="Negocio alvo ausente do historico completo";
   return(false);
  }

// An initial episode that is still open has a separate live opening-time
// witness. A later partial fill of the SAME original order can satisfy the
// DEAL_ORDER anchor above, but cannot impersonate the position's first deal
// when POSITION_TIME_MSC still identifies the earlier opening. Do not use
// this check for netting reversals: POSITION_IDENTIFIER survives reversal and
// the position's open-time semantics are not this initial-episode contract.
bool JPWObserverInitialPositionMatches(JPWObserverDeal &start,
                                       const long live_position_id,
                                       const string live_symbol,
                                       const int live_side,
                                       const long live_open_msc)
  {
   return(start.entry==DEAL_ENTRY_IN &&
          start.order_ticket==start.position_id &&
          start.position_id==live_position_id &&
          start.symbol==live_symbol && start.side==live_side &&
          start.time_msc>0 && live_open_msc==start.time_msc);
  }

bool JPWObserverSnapshotValid(JPWObserverSnapshot &s)
  {
   string expected="";
   return(JPWRaizNIsHash(s.account_key) &&
          JPWObserverEpisodeKey(s.account_key,s.symbol,s.position_id,
                                s.first_deal_ticket,expected) &&
          s.episode_key==expected && s.deal_time_msc>0 &&
          (s.side==1 || s.side==-1) && JPWFinitePositive(s.executed_p0) &&
          JPWFinitePositive(s.atr55_h4) && s.atr_bar_open>0 &&
          s.atr_bar_open+4*60*60<=s.deal_time_msc/1000 &&
          s.n_1w>=0 && s.n_2w>=0 &&
          s.status_1w>=0 && s.status_1w<=2 &&
          s.status_2w>=0 && s.status_2w<=2 &&
          ((s.status_1w==0 && s.n_1w==0) ||
           (s.status_1w>0 && s.n_1w>0)) &&
          ((s.status_2w==0 && s.n_2w==0) ||
           (s.status_2w>0 && s.n_2w>0)) &&
          s.horizon_observed_utc>0 && s.observer_recorded_utc>0 &&
          s.event_arrival_utc>=0 && s.event_processing_delay_ms>=0 &&
          (s.provenance!=JPW_OBSERVER_CAPTURED_EVENT ||
           (s.event_arrival_utc>0 &&
            s.event_processing_delay_ms<=JPW_OBSERVER_CAPTURE_WINDOW_MS &&
            s.observer_recorded_utc>=s.event_arrival_utc &&
            s.observer_recorded_utc-s.event_arrival_utc<=5)) &&
          (s.provenance==JPW_OBSERVER_CAPTURED_EVENT ||
           s.provenance==JPW_OBSERVER_RECONSTRUCTED));
  }

bool JPWObserverChecksum(JPWObserverSnapshot &s,string &hash)
  {
   hash="";
   if(!JPWObserverSnapshotValid(s)) return(false);
   const string body=JPWRaizNFrame(s.episode_key)+JPWRaizNFrame(s.account_key)+
      JPWRaizNFrame(s.symbol)+JPWRaizNFrame(IntegerToString(s.position_id))+
      JPWRaizNFrame(IntegerToString(s.first_deal_ticket))+
      JPWRaizNFrame(IntegerToString(s.deal_time_msc))+
      JPWRaizNFrame(IntegerToString(s.side))+
      JPWRaizNFrame(DoubleToString(s.executed_p0,-16))+
      JPWRaizNFrame(DoubleToString(s.atr55_h4,-16))+
      JPWRaizNFrame(IntegerToString(s.atr_bar_open))+
      JPWRaizNFrame(IntegerToString(s.n_1w))+
      JPWRaizNFrame(IntegerToString(s.n_2w))+
      JPWRaizNFrame(IntegerToString(s.status_1w))+
      JPWRaizNFrame(IntegerToString(s.status_2w))+
      JPWRaizNFrame(s.horizon_source)+JPWRaizNFrame(s.horizon_hash)+
      JPWRaizNFrame(IntegerToString(s.horizon_observed_utc))+
      JPWRaizNFrame(IntegerToString(s.observer_recorded_utc))+
      JPWRaizNFrame(IntegerToString(s.event_arrival_utc))+
      JPWRaizNFrame(IntegerToString(s.event_processing_delay_ms))+
      JPWRaizNFrame(IntegerToString(s.provenance));
   return(JPWRaizNHash(body,hash));
  }

// Two instances may observe the same opening deal at different times. The
// first full snapshot remains immutable; a later observation is idempotent
// only when the execution facts are identical, not when observation times or
// provenance happen to match.
bool JPWObserverSameExecution(JPWObserverSnapshot &a,JPWObserverSnapshot &b)
  {
   return(a.episode_key==b.episode_key &&
          a.account_key==b.account_key && a.symbol==b.symbol &&
          a.position_id==b.position_id &&
          a.first_deal_ticket==b.first_deal_ticket &&
          a.deal_time_msc==b.deal_time_msc &&
          a.side==b.side && a.executed_p0==b.executed_p0);
  }

string JPWObserverDatabasePath(const string account_key)
  {
   if(!JPWRaizNIsHash(account_key)) return("");
   return(JPW_OBSERVER_FOLDER+"rn_observer_"+
          StringSubstr(account_key,0,24)+".sqlite");
  }

bool JPWObserverInitDatabase(const int db,const string account_key)
  {
   if(db==INVALID_HANDLE || !JPWRaizNIsHash(account_key)) return(false);
   if(!DatabaseTransactionBegin(db)) return(false);
   bool ok=DatabaseExecute(db,
      "CREATE TABLE observer_meta (schema_version INTEGER NOT NULL, account_key TEXT NOT NULL)") &&
      DatabaseExecute(db,
      "CREATE TABLE observer_snapshots ("
      "episode_key TEXT PRIMARY KEY, account_key TEXT NOT NULL, symbol TEXT NOT NULL,"
      "position_id INTEGER NOT NULL, first_deal_ticket INTEGER NOT NULL,"
      "deal_time_msc INTEGER NOT NULL, side INTEGER NOT NULL,"
      "executed_p0 REAL NOT NULL, atr55_h4 REAL NOT NULL,"
      "atr_bar_open INTEGER NOT NULL, n_1w INTEGER NOT NULL, n_2w INTEGER NOT NULL,"
      "status_1w INTEGER NOT NULL, status_2w INTEGER NOT NULL,"
      "horizon_source TEXT NOT NULL, horizon_hash TEXT NOT NULL,"
      "horizon_observed_utc INTEGER NOT NULL, observer_recorded_utc INTEGER NOT NULL,"
      "event_arrival_utc INTEGER NOT NULL, event_processing_delay_ms INTEGER NOT NULL,"
      "provenance INTEGER NOT NULL, checksum TEXT NOT NULL,"
      "UNIQUE(account_key,position_id,first_deal_ticket))");
   if(ok)
     {
      const int q=DatabasePrepare(db,
         "INSERT INTO observer_meta(schema_version,account_key) VALUES(?1,?2)");
      if(q==INVALID_HANDLE) ok=false;
      else
        {
         ok=DatabaseBind(q,0,JPW_OBSERVER_SCHEMA) &&
            DatabaseBind(q,1,account_key);
         if(ok) { ResetLastError(); DatabaseRead(q);
                  ok=(GetLastError()==ERR_DATABASE_NO_MORE_DATA); }
         DatabaseFinalize(q);
        }
     }
   if(ok && DatabaseTransactionCommit(db)) return(true);
   DatabaseTransactionRollback(db);
   return(false);
  }

struct JPWObserverMeta
  {
   int schema_version;
   string account_key;
  };

bool JPWObserverDatabaseCompatible(const int db,const string account_key,
                                    string &reason)
  {
   reason="";
   if(!DatabaseTableExists(db,"observer_meta") ||
      !DatabaseTableExists(db,"observer_snapshots"))
     { reason="Schema do observador ausente ou corrompido"; return(false); }
   const int q=DatabasePrepare(db,
      "SELECT schema_version,account_key FROM observer_meta LIMIT 2");
   if(q==INVALID_HANDLE)
     { reason="Metadados do observador indisponiveis"; return(false); }
   JPWObserverMeta meta;
   bool ok=DatabaseReadBind(q,meta);
   if(ok) { JPWObserverMeta duplicate; ResetLastError();
            ok=!DatabaseReadBind(q,duplicate) &&
            GetLastError()==ERR_DATABASE_NO_MORE_DATA; }
   DatabaseFinalize(q);
   if(!ok || meta.schema_version!=JPW_OBSERVER_SCHEMA ||
      meta.account_key!=account_key)
     { reason="Versao ou identidade do observador incompativel"; return(false); }
   return(true);
  }

bool JPWObserverOpen(const string account_key,const bool write,int &db,
                     string &reason)
  {
   db=INVALID_HANDLE; reason="";
   const string path=JPWObserverDatabasePath(account_key);
   if(path=="") { reason="Identidade do observador indisponivel"; return(false); }
   const bool exists=FileIsExist(path);
   if(!exists && !write)
     { reason="Nenhum snapshot local do observador"; return(false); }
   if(write && !FolderCreate("JPWealth\\Alavancagem"))
     { reason="Pasta local do observador indisponivel"; return(false); }
   db=DatabaseOpen(path,write ? DATABASE_OPEN_READWRITE|DATABASE_OPEN_CREATE :
                              DATABASE_OPEN_READONLY);
   if(db==INVALID_HANDLE)
     { reason="Banco local do observador indisponivel"; return(false); }
   if(!exists && write)
     {
      if(JPWObserverInitDatabase(db,account_key)) return(true);
      reason="Criacao do banco do observador nao confirmada";
     }
   else if(JPWObserverDatabaseCompatible(db,account_key,reason)) return(true);
   DatabaseClose(db); db=INVALID_HANDLE;
   return(false);
  }

JPWStoreResult JPWObserverReadByKeyStatus(const int db,const string key,
                          JPWObserverSnapshot &snapshot,string &reason)
  {
   JPWObserverClear(snapshot); reason="";
   if(db==INVALID_HANDLE || !JPWRaizNIsHash(key))
     { reason="Chave do episodio invalida"; return(JPW_STORE_IO_ERROR); }
   const int q=DatabasePrepare(db,
      "SELECT episode_key,account_key,symbol,position_id,first_deal_ticket,"
      "deal_time_msc,side,executed_p0,atr55_h4,atr_bar_open,n_1w,n_2w,"
      "status_1w,status_2w,horizon_source,horizon_hash,horizon_observed_utc,"
      "observer_recorded_utc,event_arrival_utc,event_processing_delay_ms,"
      "provenance,checksum "
      "FROM observer_snapshots WHERE episode_key=?1");
   if(q==INVALID_HANDLE)
     { reason="Consulta do observador indisponivel"; return(JPW_STORE_IO_ERROR); }
   if(!DatabaseBind(q,0,key))
     { DatabaseFinalize(q); reason="Consulta do observador recusada";
       return(JPW_STORE_IO_ERROR); }
   ResetLastError();
   const bool found=DatabaseReadBind(q,snapshot);
   const int read_error=GetLastError();
   DatabaseFinalize(q);
   if(!found)
     { JPWObserverClear(snapshot);
       reason=(read_error==ERR_DATABASE_NO_MORE_DATA ?
               "Episodio local ausente" : "Leitura do observador falhou");
       return(read_error==ERR_DATABASE_NO_MORE_DATA ? JPW_STORE_ABSENT : JPW_STORE_IO_ERROR); }
   string checksum="";
   if(!JPWObserverChecksum(snapshot,checksum) || snapshot.checksum!=checksum)
     { JPWObserverClear(snapshot); reason="Snapshot local invalido"; return(JPW_STORE_CORRUPT); }
   return(JPW_STORE_VALID);
  }

bool JPWObserverReadByKey(const int db,const string key,
                          JPWObserverSnapshot &snapshot,string &reason)
  {
   return(JPWObserverReadByKeyStatus(db,key,snapshot,reason)==JPW_STORE_VALID);
  }

bool JPWObserverInsertImmutable(const int db,JPWObserverSnapshot &snapshot,
                                string &reason)
  {
   reason="";
   string checksum="";
   if(!JPWObserverChecksum(snapshot,checksum))
     { reason="Snapshot incompleto"; return(false); }
   snapshot.checksum=checksum;
   if(!DatabaseTransactionBegin(db))
     { reason="Banco local ocupado"; return(false); }
   JPWObserverSnapshot existing;
   string read_reason="";
   const JPWStoreResult existing_status=JPWObserverReadByKeyStatus(db,snapshot.episode_key,existing,read_reason);
   if(existing_status==JPW_STORE_VALID)
     {
      const bool same=JPWObserverSameExecution(existing,snapshot);
      if(same && !DatabaseTransactionCommit(db))
        { DatabaseTransactionRollback(db);
          reason="Confirmacao da transacao falhou"; return(false); }
      if(!same) DatabaseTransactionRollback(db);
      if(!same) reason="Conflito: episodio ja registrado com outros bytes";
      return(same);
     }
   if(existing_status!=JPW_STORE_ABSENT)
     { DatabaseTransactionRollback(db); reason=read_reason; return(false); }
   const int q=DatabasePrepare(db,
      "INSERT INTO observer_snapshots VALUES(?1,?2,?3,?4,?5,?6,?7,?8,?9,?10,"
      "?11,?12,?13,?14,?15,?16,?17,?18,?19,?20,?21,?22)");
   bool ok=(q!=INVALID_HANDLE);
   if(ok)
     {
      ok=DatabaseBind(q,0,snapshot.episode_key) &&
         DatabaseBind(q,1,snapshot.account_key) &&
         DatabaseBind(q,2,snapshot.symbol) &&
         DatabaseBind(q,3,snapshot.position_id) &&
         DatabaseBind(q,4,snapshot.first_deal_ticket) &&
         DatabaseBind(q,5,snapshot.deal_time_msc) &&
         DatabaseBind(q,6,snapshot.side) &&
         DatabaseBind(q,7,snapshot.executed_p0) &&
         DatabaseBind(q,8,snapshot.atr55_h4) &&
         DatabaseBind(q,9,snapshot.atr_bar_open) &&
         DatabaseBind(q,10,snapshot.n_1w) &&
         DatabaseBind(q,11,snapshot.n_2w) &&
         DatabaseBind(q,12,snapshot.status_1w) &&
         DatabaseBind(q,13,snapshot.status_2w) &&
         DatabaseBind(q,14,snapshot.horizon_source) &&
         DatabaseBind(q,15,snapshot.horizon_hash) &&
         DatabaseBind(q,16,snapshot.horizon_observed_utc) &&
         DatabaseBind(q,17,snapshot.observer_recorded_utc) &&
         DatabaseBind(q,18,snapshot.event_arrival_utc) &&
         DatabaseBind(q,19,snapshot.event_processing_delay_ms) &&
         DatabaseBind(q,20,snapshot.provenance) &&
         DatabaseBind(q,21,snapshot.checksum);
      if(ok) { ResetLastError(); DatabaseRead(q);
               ok=(GetLastError()==ERR_DATABASE_NO_MORE_DATA); }
      DatabaseFinalize(q);
     }
   JPWObserverSnapshot verified;
   if(ok) ok=JPWObserverReadByKey(db,snapshot.episode_key,verified,read_reason) &&
             verified.checksum==snapshot.checksum;
   if(ok) ok=DatabaseTransactionCommit(db);
   if(!ok) DatabaseTransactionRollback(db);
   if(!ok) reason="Gravacao ou releitura do snapshot nao confirmada";
   return(ok);
  }

// "Latest" significa ultimo registro local; NAO comprova posicao aberta.
bool JPWObserverReadLatestInDb(const int db,const string account_key,
                               const string symbol,
                               JPWObserverSnapshot &snapshot,string &reason)
  {
   JPWObserverClear(snapshot); reason="";
   if(!JPWRaizNIsHash(account_key) || !JPWRaizNSymbolValid(symbol))
     { reason="Conta ou simbolo indisponivel"; return(false); }
   const int q=DatabasePrepare(db,
      "SELECT episode_key FROM observer_snapshots WHERE account_key=?1 "
      "AND symbol=?2 ORDER BY deal_time_msc DESC,first_deal_ticket DESC LIMIT 1");
   if(q==INVALID_HANDLE)
     { reason="Consulta do observador indisponivel"; return(false); }
   string key="";
   bool found=false;
   if(!DatabaseBind(q,0,account_key) || !DatabaseBind(q,1,symbol))
     { DatabaseFinalize(q); reason="Filtro do observador recusado";
       return(false); }
   ResetLastError();
   const bool row=DatabaseRead(q);
   const int read_error=GetLastError();
   if(row) found=DatabaseColumnText(q,0,key);
   DatabaseFinalize(q);
   if(found) found=JPWObserverReadByKey(db,key,snapshot,reason);
   else reason=(!row && read_error==ERR_DATABASE_NO_MORE_DATA ?
                "Nenhum episodio local para este simbolo" :
                "Leitura do observador falhou");
   return(found);
  }

// Getter publico para Details; abre o banco somente leitura e nao cria dados.
bool JPWObserverReadCurrent(const string account_key,const string symbol,
                            JPWObserverSnapshot &snapshot,string &reason)
  {
   JPWObserverClear(snapshot); reason="";
   int db=INVALID_HANDLE;
   if(!JPWObserverOpen(account_key,false,db,reason)) return(false);
   const bool found=JPWObserverReadLatestInDb(db,account_key,symbol,
                                               snapshot,reason);
   DatabaseClose(db);
   return(found);
  }

#endif
