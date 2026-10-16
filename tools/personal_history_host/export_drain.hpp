// Host callers drain the real export job. No production timer drains.
bool host_export_drain(JPWPersonalExportJob &job){for(int n=0;n<1000000&&job.active;n++){auto r=JPWPersonalExportStep(job,GetTickCount64(),25,1024);if(r!=JPW_STORE_BUSY)return r==JPW_STORE_VALID;}return job.result==JPW_STORE_VALID;}
bool JPWPersonalBackupBuild(const string &key,string &json,string &reason){JPWPersonalExportJob job;bool ok=JPWPersonalExportBegin(key,true,job)==JPW_STORE_BUSY&&host_export_drain(job);reason=job.reason;json=ok?job.json:"";host_mono++;return ok;}
bool JPWPersonalExport(const string &key,bool backup,string &path,string &reason){JPWPersonalExportJob job;bool ok=JPWPersonalExportBegin(key,backup,job)==JPW_STORE_BUSY&&host_export_drain(job);path=job.path;reason=job.reason;return ok;}
