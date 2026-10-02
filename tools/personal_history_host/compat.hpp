// MQL built-in compatibility only. No PersonalHistory domain formulas.

#include <algorithm>
#include <climits>
#include <cmath>
#include <cstdio>
#include <cstdlib>
#include <filesystem>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <map>
#include <sstream>
#include <stdexcept>
#include <string>
#include <vector>
#include <thread>
#include <chrono>
#include <sqlite3.h>
#ifdef __APPLE__
#include <CommonCrypto/CommonDigest.h>
#else
#include <openssl/sha.h>
#endif
using string=std::string; using uchar=unsigned char; using ushort=unsigned short;
constexpr int INVALID_HANDLE=-1, WHOLE_ARRAY=-1, CP_UTF8=65001;
constexpr int DATABASE_OPEN_READONLY=1, DATABASE_OPEN_READWRITE=2, DATABASE_OPEN_CREATE=4;
constexpr int ERR_DATABASE_NO_MORE_DATA=5126;
string host_root; int host_error=0,host_handle=1,host_asserts=0;bool host_forbid_io=false;
std::map<int,sqlite3*> host_dbs; std::map<int,sqlite3_stmt*> host_statements;
void ResetLastError(){host_error=0;} int GetLastError(){return host_error;}
template<class T> int ArraySize(const std::vector<T>& a){return (int)a.size();}
template<class T> int ArrayResize(std::vector<T>& a,int n){if(n<0)return -1;a.resize(n);return n;}
template<class T> bool ArraySort(std::vector<T>& a){std::sort(a.begin(),a.end());return true;}
double MathAbs(double v){return std::abs(v);} double MathMax(double a,double b){return std::max(a,b);}
bool MathIsValidNumber(double v){return std::isfinite(v);}
string IntegerToString(long v){return std::to_string(v);}
string DoubleToString(double v,int n){std::ostringstream s;s<<std::fixed<<std::setprecision(n)<<v;return s.str();}
int StringLen(const string& s){return (int)s.size();}
ushort StringGetCharacter(const string& s,int i){return (uchar)s.at(i);}
string StringSubstr(const string& s,int p,int n=-1){return s.substr(p,n<0 ? string::npos : (size_t)n);}
int StringFind(const string& s,const string& t,int p=0){auto n=s.find(t,p);return n==string::npos ? -1 : (int)n;}
int StringCompare(const string& a,const string& b){return a.compare(b);}
int StringSplit(const string& s,ushort sep,std::vector<string>& a){a.clear();size_t p=0,n;while((n=s.find((char)sep,p))!=string::npos){a.push_back(s.substr(p,n-p));p=n+1;}a.push_back(s.substr(p));return ArraySize(a);}
long StringToInteger(const string& s){try{return std::stol(s);}catch(...){return 0;}}
double StringToDouble(const string& s){try{return std::stod(s);}catch(...){return 0;}}
string StringFormat(const char* format,int n){char b[100];std::snprintf(b,sizeof(b),format,n);return b;}
int StringToCharArray(const string& s,std::vector<uchar>& b,int,int,int){b.assign(s.begin(),s.end());b.push_back(0);return ArraySize(b);}
string CharArrayToString(const std::vector<uchar>& b,int p,int n,int){return string(b.begin()+p,b.begin()+p+n);}
template<class... T> void Print(const T&... t){(std::cout<<...<<t)<<'\n';}
bool JPWRaizNIsHash(const string& s){return s.size()==64 && s.find_first_not_of("0123456789abcdef")==string::npos;}
bool JPWRaizNHash(const string& s,string& out){unsigned char b[32];
#ifdef __APPLE__
CC_SHA256(s.data(),(CC_LONG)s.size(),b);
#else
SHA256((const unsigned char*)s.data(),s.size(),b);
#endif
out="";for(int i=0;i<32;i++)out+=StringFormat("%02x",b[i]);return true;}
string host_path(string s){std::replace(s.begin(),s.end(),'\\','/');return host_root+"/"+s;}
bool FileIsExist(const string& s){if(host_forbid_io)throw std::runtime_error("forbidden filesystem IO in presentation/action");return std::filesystem::exists(host_path(s));}
bool FolderCreate(const string& s){if(host_forbid_io)throw std::runtime_error("forbidden filesystem IO in presentation/action");std::error_code e;std::filesystem::create_directories(host_path(s),e);return !e;}
int DatabaseOpen(const string& path,int flags){if(host_forbid_io)throw std::runtime_error("forbidden SQL IO in presentation/action");sqlite3* db=nullptr;int f=(flags&DATABASE_OPEN_READONLY)?SQLITE_OPEN_READONLY:SQLITE_OPEN_READWRITE;if(flags&DATABASE_OPEN_CREATE)f|=SQLITE_OPEN_CREATE;int rc=sqlite3_open_v2(host_path(path).c_str(),&db,f,nullptr);if(rc!=SQLITE_OK){if(db)sqlite3_close(db);host_error=rc;return -1;}int h=host_handle++;host_dbs[h]=db;return h;}
void DatabaseClose(int h){if(host_dbs.count(h)){sqlite3_close(host_dbs[h]);host_dbs.erase(h);}}
int DatabasePrepare(int h,const string& sql){if(host_forbid_io)throw std::runtime_error("forbidden SQL IO in presentation/action");sqlite3_stmt* q=nullptr;int rc=sqlite3_prepare_v2(host_dbs.at(h),sql.c_str(),-1,&q,nullptr);if(rc!=SQLITE_OK){host_error=rc;return -1;}int n=host_handle++;host_statements[n]=q;return n;}
bool DatabaseBind(int q,int i,long x){return sqlite3_bind_int64(host_statements.at(q),i+1,x)==SQLITE_OK;}
bool DatabaseBind(int q,int i,int x){return DatabaseBind(q,i,(long)x);}
bool DatabaseBind(int q,int i,double x){return sqlite3_bind_double(host_statements.at(q),i+1,x)==SQLITE_OK;}
bool DatabaseBind(int q,int i,const string& x){return sqlite3_bind_text(host_statements.at(q),i+1,x.c_str(),(int)x.size(),SQLITE_TRANSIENT)==SQLITE_OK;}
bool DatabaseRead(int q){int rc=sqlite3_step(host_statements.at(q));host_error=rc==SQLITE_DONE?ERR_DATABASE_NO_MORE_DATA:(rc==SQLITE_ROW?0:rc);return rc==SQLITE_ROW;}
void DatabaseFinalize(int q){if(host_statements.count(q)){sqlite3_finalize(host_statements[q]);host_statements.erase(q);}}
bool DatabaseColumnLong(int q,int i,long& n){if(sqlite3_column_type(host_statements.at(q),i)!=SQLITE_INTEGER)return false;n=(long)sqlite3_column_int64(host_statements.at(q),i);return true;}
bool DatabaseColumnInteger(int q,int i,int& n){long v=0;if(!DatabaseColumnLong(q,i,v))return false;n=(int)v;return true;}
bool DatabaseColumnText(int q,int i,string& s){if(sqlite3_column_type(host_statements.at(q),i)!=SQLITE_TEXT)return false;s=(const char*)sqlite3_column_text(host_statements.at(q),i);return true;}
bool DatabaseExecute(int h,const string& sql){int rc=sqlite3_exec(host_dbs.at(h),sql.c_str(),nullptr,nullptr,nullptr);host_error=rc==SQLITE_OK?0:rc;return rc==SQLITE_OK;}
bool DatabaseTransactionBegin(int h){return DatabaseExecute(h,"BEGIN");}
bool DatabaseTransactionCommit(int h){return DatabaseExecute(h,"COMMIT");}
bool DatabaseTransactionRollback(int h){return DatabaseExecute(h,"ROLLBACK");}
void REQUIRE(bool ok,const string& label){host_asserts++;if(!ok)throw std::runtime_error(label);}
long scalar(int db,const string& sql){int q=DatabasePrepare(db,sql);long n=-1;REQUIRE(q!=-1 && DatabaseRead(q) && DatabaseColumnLong(q,0,n),"scalar "+sql);DatabaseFinalize(q);return n;}

using ulong=unsigned long;
static_assert(sizeof(long)==8, "MQL long shim requires 64-bit long");
string StringFormat(const char* format,double n){char b[100];std::snprintf(b,sizeof(b),format,n);return b;}
constexpr int CRYPT_HASH_SHA256=1;
int CryptEncode(int algorithm,const std::vector<uchar>& input,const std::vector<uchar>& key,std::vector<uchar>& digest){
 if(algorithm!=CRYPT_HASH_SHA256)return 0;digest.resize(32);
#ifdef __APPLE__
 CC_SHA256(input.data(),(CC_LONG)input.size(),digest.data());
#else
 SHA256(input.data(),input.size(),digest.data());
#endif
 return 32;
}
std::map<long,std::vector<string>> host_find_files;std::map<long,size_t>host_find_indexes;long host_find_handle=100000;
long FileFindFirst(const string& pattern,string& found){auto path=std::filesystem::path(host_path(pattern));std::vector<string>files;std::error_code ec;
 for(const auto& entry:std::filesystem::directory_iterator(path.parent_path(),ec)){auto name=entry.path().filename().string();if(name.rfind("history_",0)==0&&entry.path().extension()==".sqlite")files.push_back(name);}
 if(files.empty())return INVALID_HANDLE;std::sort(files.begin(),files.end());long h=host_find_handle++;host_find_files[h]=files;host_find_indexes[h]=0;found=files[0];return h;}
bool FileFindNext(long h,string& found){auto& i=host_find_indexes.at(h);auto& files=host_find_files.at(h);if(++i>=files.size())return false;found=files[i];return true;}
void FileFindClose(long h){host_find_files.erase(h);host_find_indexes.erase(h);}
using uint=unsigned int;using datetime=long;
constexpr int FILE_WRITE=1,FILE_READ=2,FILE_TXT=4,FILE_ANSI=8,TIME_DATE=1,TIME_SECONDS=2;
long host_wall=2000;ulong host_mono=2000000;
long TimeGMT(){return host_wall;}ulong GetTickCount64(){return host_mono;}
string TimeToString(datetime value,int){return std::to_string(value);}
int StringReplace(string& value,const string& needle,const string& replacement){int count=0;size_t offset=0;while((offset=value.find(needle,offset))!=string::npos){value.replace(offset,needle.size(),replacement);offset+=replacement.size();count++;}return count;}
std::map<int,std::fstream*>host_files;int host_file_handle=200000;
int FileOpen(const string& name,int flags,int,int){if(host_forbid_io)throw std::runtime_error("forbidden filesystem IO in presentation/action");auto mode=std::ios::binary;if(flags&FILE_WRITE)mode|=std::ios::out|std::ios::trunc;if(flags&FILE_READ)mode|=std::ios::in;auto f=new std::fstream(host_path(name),mode);if(!*f){delete f;host_error=1;return INVALID_HANDLE;}int h=host_file_handle++;host_files[h]=f;return h;}
uint FileWriteString(int h,const string& value){auto f=host_files.at(h);f->write(value.data(),value.size());return *f?(uint)value.size():0;}
void FileFlush(int h){host_files.at(h)->flush();}
void FileClose(int h){if(host_files.count(h)){host_files[h]->close();delete host_files[h];host_files.erase(h);}}
bool FileIsEnding(int h){return host_files.at(h)->peek()==EOF;}
string FileReadString(int h){string line;std::getline(*host_files.at(h),line);if(!line.empty()&&line.back()=='\r')line.pop_back();return line;}
