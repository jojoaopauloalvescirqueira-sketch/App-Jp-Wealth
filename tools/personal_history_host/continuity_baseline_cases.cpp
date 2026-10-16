// Original valid-fixture RED reproducer; uses only base APIs.
void continuity_seed(PersonalFixture &f,long wanted){
 f.initial();int changed=0;REQUIRE(JPWPersonalPeakAccept(f.capture,"continuity-first-photo",f.current,f.estimated,changed),"seed peak");f.commit(changed);
 long first=scalar(f.context.db,"SELECT sequence FROM ph_meta");string payload="NO_SL_DETECTED|-",digest;JPWPersonalHash(payload,digest);
 REQUIRE(DatabaseTransactionBegin(f.context.db),"fixture bulk transaction");
 int q=DatabasePrepare(f.context.db,"INSERT INTO ph_rows VALUES(?1,'EVENT','bulk',1000,?2,?3)");REQUIRE(q!=-1,"fixture bulk prepare");
 for(long seq=first+1;seq<=wanted;seq++){sqlite3_reset(host_statements.at(q));sqlite3_clear_bindings(host_statements.at(q));REQUIRE(DatabaseBind(q,0,seq)&&DatabaseBind(q,1,payload)&&DatabaseBind(q,2,digest)&&JPWPersonalDone(q),"fixture bulk valid row");}
 DatabaseFinalize(q);REQUIRE(DatabaseExecute(f.context.db,"UPDATE ph_meta SET sequence="+IntegerToString(wanted)),"fixture sequence");REQUIRE(DatabaseTransactionCommit(f.context.db),"fixture commit");f.close();
}
void continuity_case(const string &id){
 PersonalFixture f;JPWPersonalHash("continuity-"+id,f.key);f.capture.account_key=f.key;
 if(id=="CONT-01"){continuity_seed(f,100001);JPWPersonalStoreContext reader{};bool opened=JPWPersonalOpen(f.key,false,"",0,0,reader);if(!opened)Print("DEBUG_CTX|",reader.result,"|",reader.reason);REQUIRE(opened,"CONT-01 valid 100001 rows must remain readable");JPWPersonalClose(reader,0,0);}
 else if(id=="CONT-02"){continuity_seed(f,3001);host_read_clock_ms=1;JPWPersonalStoreContext reader{};bool opened=JPWPersonalOpen(f.key,false,"",0,0,reader);host_read_clock_ms=0;if(!opened)Print("DEBUG_CTX|",reader.result,"|",reader.reason);REQUIRE(opened,"CONT-02 valid journal taking more than 2000 ms must remain readable");JPWPersonalClose(reader,0,0);}
 else if(id=="CONT-03"){continuity_seed(f,100001);int db=DatabaseOpen(JPWPersonalPath(f.key),DATABASE_OPEN_READWRITE);REQUIRE(DatabaseExecute(db,"UPDATE ph_rows SET digest='broken' WHERE sequence=100001"),"late corruption");DatabaseClose(db);JPWPersonalStoreContext reader{};REQUIRE(!JPWPersonalOpen(f.key,false,"",0,0,reader)&&reader.result==JPW_STORE_CORRUPT,"CONT-03 late corruption must be diagnosed after integral audit, not capacity");JPWPersonalClose(reader,0,0);}
 else if(id=="CONT-04"){f.initial();REQUIRE(DatabaseExecute(f.context.db,"UPDATE ph_rows SET wall=1000.75 WHERE category='EVENT'"),"real wall corrupt");f.close();host_getters_permissive=true;JPWPersonalStoreContext reader{};bool opened=JPWPersonalOpen(f.key,false,"",0,0,reader);host_getters_permissive=false;REQUIRE(!opened&&reader.result==JPW_STORE_CORRUPT,"CONT-04 SQL type validation cannot rely on strict shim getters");JPWPersonalClose(reader,0,0);}
 else if(id=="CONT-07"){f.initial();int b=DatabaseOpen(JPWPersonalPath(f.key),DATABASE_OPEN_READWRITE);REQUIRE(DatabaseExecute(b,"UPDATE ph_rows SET digest='broken' WHERE sequence=1"),"external commit same sequence");DatabaseClose(b);REQUIRE(!JPWPersonalKeepAlive(f.context,1001,1001000),"CONT-07 live writer must reject changed SQLite generation before heartbeat");f.close();}
 else throw std::runtime_error("unknown continuity case");
 Print("CONTINUITY_PASS|",id,"|",host_asserts);
}

