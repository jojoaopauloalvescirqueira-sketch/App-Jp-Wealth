// Test utilities only. Production timer callers must never drain in a loop.
bool host_personal_drain(JPWPersonalStoreContext &ctx,long wall=1000,ulong mono=1000000,int budget=25,int rows=1024){
 for(int steps=0;steps<1000000;steps++){
  auto r=JPWPersonalOpenStep(ctx,GetTickCount64(),budget,rows,wall,mono);
  if(r==JPW_STORE_VALID)return true;
  if(r!=JPW_STORE_BUSY||!JPWPersonalPreparing(ctx)||ctx.phase==JPW_PH_WAIT_OWNER||ctx.phase==JPW_PH_TRANSACTION||ctx.phase==JPW_PH_OWNER_COMMIT)return false;
 }
 throw std::runtime_error("test drain did not terminate");
}
bool JPWPersonalOpen(const string &key,bool writer,const string &token,long wall,ulong mono,JPWPersonalStoreContext &ctx){
 if(ctx.db!=-1)JPWPersonalOpenCancel(ctx);auto r=JPWPersonalOpenBegin(key,writer,token,wall,mono,ctx);if(r!=JPW_STORE_BUSY)return false;
 return host_personal_drain(ctx,wall,mono);
}
bool JPWPersonalReadSummary(const string &key,JPWPersonalSummary &out){JPWPersonalStoreContext ctx;bool ok=JPWPersonalOpen(key,false,"",0,0,ctx);if(ok)ok=JPWPersonalReadSummaryFrom(ctx,out);else{out.result=ctx.result;out.reason=ctx.reason;}if(ok)ok=JPWPersonalReadFinish(ctx,true);JPWPersonalOpenCancel(ctx);return ok;}
bool JPWPersonalReadPage(const string &key,const string &category,long before,int limit,std::vector<JPWPersonalRow>&rows,string &reason){JPWPersonalStoreContext ctx;bool ok=JPWPersonalOpen(key,false,"",0,0,ctx);if(ok)ok=JPWPersonalReadPageFrom(ctx,category,before,limit,rows,reason);else reason=ctx.reason;if(ok)ok=JPWPersonalReadFinish(ctx,true);JPWPersonalOpenCancel(ctx);return ok;}
bool JPWPersonalReadDetail(const string &key,long seq,JPWPersonalRow &row,string &reason){JPWPersonalStoreContext ctx;bool ok=JPWPersonalOpen(key,false,"",0,0,ctx);if(ok)ok=JPWPersonalReadDetailFrom(ctx,seq,row,reason);else reason=ctx.reason;if(ok)ok=JPWPersonalReadFinish(ctx,true);JPWPersonalOpenCancel(ctx);return ok;}
// Transitional host support for the old standalone restore path, removed with PH3.
bool JPWPersonalIntegrity(int db,string &reason){
 JPWPersonalStoreContext ctx;ctx.db=db;int q=DatabasePrepare(db,"SELECT account_key FROM ph_meta");bool ok=q!=-1&&DatabaseRead(q)&&DatabaseColumnText(q,0,ctx.account_key);if(q!=-1)DatabaseFinalize(q);
 bool own=sqlite3_get_autocommit(host_dbs.at(db));if(own)ok=ok&&DatabaseTransactionBegin(db);ctx.transaction_active=true;
 if(ok)ok=JPWPersonalAuditBegin(ctx);for(int i=0;ok&&i<100000;i++){auto r=JPWPersonalAuditStep(ctx,GetTickCount64(),25,1024);if(r==JPW_STORE_VALID)break;if(r!=JPW_STORE_BUSY){ok=false;break;}}
 reason=ctx.reason;if(own){if(ok)DatabaseTransactionCommit(db);else if(host_dbs.count(db))DatabaseTransactionRollback(db);}ctx.db=-1;return ok;
}
JPWStoreResult JPWPersonalAuditRows(int db,string &reason){return JPWPersonalIntegrity(db,reason)?JPW_STORE_VALID:JPW_STORE_CORRUPT;}
