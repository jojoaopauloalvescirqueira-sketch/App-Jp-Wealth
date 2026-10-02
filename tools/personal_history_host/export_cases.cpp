void export_case(const string& id){
if(id!="HIS-AC19"){Print("EXPORT_NOT_RUN|",id);return;}int start=host_asserts;PersonalFixture f;
f.subjects[0].id="9007199254740993";f.subjects[0].ticket="9007199254740995";f.subjects[0].symbol="=cmd,\"quoted\"\nÁrvore";f.initial();
int changed=0;string photo="synthetic photo\nIDs remain text:9007199254740993";
REQUIRE(JPWPersonalPeakAccept(f.capture,photo,f.current,f.estimated,changed),"peak with hostile-text original photo");f.commit(changed);
string json,key,why;long started=0,last=0;std::vector<JPWPersonalRow>rows;
REQUIRE(JPWPersonalBackupBuild(f.key,json,why),"actual production JSON build");
REQUIRE(JPWPersonalBackupParse(json,key,started,last,rows,why)&&key==f.key&&rows.size()==(size_t)scalar(f.context.db,"SELECT COUNT(*) FROM ph_rows"),"actual canonical checksum and sequence parser");
bool found=false;for(auto& row:rows)if(row.category=="EPISODE"){JPWPersonalEpisode episode;REQUIRE(JPWPersonalDecodeEpisode(row.payload,episode),"decode backed-up episode");REQUIRE(episode.subject.id=="9007199254740993"&&episode.subject.ticket=="9007199254740995"&&episode.subject.symbol==f.subjects[0].symbol,"wide IDs and hostile UTF8 text lossless");found=true;}REQUIRE(found,"episode included in integral backup");
string broken=json;auto digest=broken.rfind("sha256");REQUIRE(digest!=string::npos,"corruption fixture location");broken[digest+10]=broken[digest+10]=='a'?'b':'a';
REQUIRE(!JPWPersonalBackupParse(broken,key,started,last,rows,why)&&rows.empty(),"corrupt integral backup rejected");
string sandbox,path;JPWPersonalHash("synthetic-sandbox-1",sandbox);REQUIRE(JPWPersonalRestoreSandbox(json,sandbox,path,why),"actual sandbox SQLite reconstruction");
REQUIRE(path.find("PersonalHistorySandbox")!=string::npos&&path!=JPWPersonalPath(f.key),"restore cannot target operational history");
int restored=DatabaseOpen(path,DATABASE_OPEN_READONLY);REQUIRE(restored!=INVALID_HANDLE&&JPWPersonalIntegrity(restored,why),"restored SQLite integrity and immutable witnesses");
JPWPersonalStoreContext reader{};reader.db=restored;reader.account_key=f.key;reader.writer=false;std::vector<JPWPersonalEpisode>episodes;JPWPersonalPeak current{},estimated{};
REQUIRE(JPWPersonalLoad(reader,episodes,current,estimated)&&episodes.size()==1&&episodes[0].subject.id=="9007199254740993"&&current.leverage==7&&current.snapshot==photo,"actual reconstructed projection retains account/IDs/peak/photo");
REQUIRE(scalar(restored,"SELECT sequence FROM ph_meta")==scalar(f.context.db,"SELECT sequence FROM ph_meta"),"restored sequence exact");DatabaseClose(restored);
string refused;REQUIRE(!JPWPersonalRestoreSandbox(json,sandbox,refused,why)&&refused.empty()&&FileIsExist(path),"existing restored target never replaced or removed");
JPWPersonalHash("synthetic-corrupt-sandbox",sandbox);REQUIRE(!JPWPersonalRestoreSandbox(broken,sandbox,refused,why),"corrupt backup cannot reconstruct");
REQUIRE(JPWPersonalCSV("=1+1")=="\"'=1+1\""&&JPWPersonalCSV("@formula")=="\"'@formula\""&&JPWPersonalCSV("\tformula")=="\"'\tformula\"","CSV spreadsheet formula prefixes neutralized");
string csv_path,json_path;REQUIRE(JPWPersonalExport(f.key,false,csv_path,why),"actual CSV filesystem export");REQUIRE(JPWPersonalExport(f.key,true,json_path,why),"actual JSON filesystem export and parser readback");
Print("EXPORT_PATHS|",csv_path,"|",json_path);std::ifstream saved(host_path(json_path));string reread((std::istreambuf_iterator<char>(saved)),{});StringReplace(reread,"\r\n","\n");REQUIRE(reread==json,"exported JSON normalizes TXT CRLF to canonical validated payload");
string collision;REQUIRE(!JPWPersonalExport(f.key,true,collision,why)&&FileIsExist(json_path),"export collision preserves existing file");
f.close();Print("EXPORT_CASE_PASS|",id,"|",host_asserts-start);
}
