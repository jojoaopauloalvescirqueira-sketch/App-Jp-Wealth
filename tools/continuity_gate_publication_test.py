#!/usr/bin/env python3
"""Controlled fresh-process publication test of the actual host-only IPC helper."""
from pathlib import Path
import hashlib,json,re,subprocess,tempfile
ROOT=Path(__file__).resolve().parents[1]
HEADER=ROOT/'tools/personal_history_host/continuity_process.hpp'
PROGRAM=r'''
#include <filesystem>
#include <fstream>
#include <thread>
#include <chrono>
#include <string>
#include <stdexcept>
#include <iostream>
#include <unistd.h>
#include <sys/wait.h>
using string=std::string;
string host_root;
#define REQUIRE(c,m) do {if(!(c))throw std::runtime_error(m);}while(false)
void await_file(const string&p){for(int n=0;n<1000&&!std::filesystem::exists(p);n++)std::this_thread::sleep_for(std::chrono::milliseconds(5));REQUIRE(std::filesystem::exists(p),"probe barrier timeout");}
// Slow filesystem boundary: expose the interval after open, before payload write.
// Only the helper's stream constructor is replaced; all publication code is real.
struct ProbeStream:std::ofstream{explicit ProbeStream(const string&p):std::ofstream(p){std::ofstream(host_root+"/stage-ready")<<"1";await_file(host_root+"/allow-write");}};
HEADER_CONTENT
int main(int argc,char**argv){try{REQUIRE(argc==3,"arguments");host_root=argv[1];string wanted=argv[2];pid_t child=fork();REQUIRE(child>=0,"fork");if(child==0){continuity_gate("commit-status",wanted);std::_Exit(0);}await_file(host_root+"/stage-ready");bool early=std::filesystem::exists(host_root+"/commit-status");std::ofstream(host_root+"/allow-write")<<"1";int status=0;waitpid(child,&status,0);REQUIRE(WIFEXITED(status)&&WEXITSTATUS(status)==0,"publisher exit");std::ifstream input(host_root+"/commit-status");string actual;input>>actual;if(early){std::cerr<<"EARLY_VISIBLE_PAYLOAD\n";return 73;}REQUIRE(actual==wanted,"complete payload");std::cout<<"COMPLETE_FIRST_VISIBILITY "<<wanted<<"\n";return 0;}catch(const std::exception&e){std::cerr<<e.what()<<"\n";return 1;}}
'''
def main():
 raw=HEADER.read_text();assert raw.count('std::ofstream')==1
 # Same open-before-write publisher that caused the observed empty read.
 broken=re.sub(r'void continuity_gate\(.*?(?=void continuity_await_gate)',
 'void continuity_gate(const string &name,const string &value="1"){std::ofstream(host_root+"/"+name)<<value;}\n',raw,flags=re.S)
 results=[]
 with tempfile.TemporaryDirectory(prefix='jpw-gate-publication-') as directory:
  root=Path(directory)
  for name,header,expected in [('actual',raw,0),('open-before-write-counterproof',broken,73)]:
   source=root/(name+'.cpp');binary=root/name
   source.write_text(PROGRAM.replace('HEADER_CONTENT',header.replace('std::ofstream','ProbeStream')))
   compile=subprocess.run(['clang++','-std=c++17',str(source),'-o',str(binary)],capture_output=True,text=True)
   assert compile.returncode==0,compile.stderr
   for value in ['BUSY','PASS']:
    dest=root/(name+'-'+value);dest.mkdir()
    result=subprocess.run([str(binary),str(dest),value],capture_output=True,text=True,timeout=15)
    print(name,value,'exit',result.returncode,result.stdout.strip(),result.stderr.strip(),flush=True)
    assert result.returncode==expected,(name,value,result.stdout,result.stderr)
    if expected:assert 'EARLY_VISIBLE_PAYLOAD' in result.stderr
    results.append({'publisher':name,'payload':value,'exit':result.returncode})
 print(json.dumps({'result':'PASS','helperSha256':hashlib.sha256(HEADER.read_bytes()).hexdigest(),'cases':results}))
if __name__=='__main__':main()
