// Fresh-process concurrency avoids a separately characterized Apple SQLite
// 3.54 unix-VFS same-process RO/RW IOERR_LOCK. No VFS/production changes.
#include <unistd.h>
#include <sys/wait.h>
string host_program;
void continuity_gate(const string &name,const string &value="1"){std::ofstream(host_root+"/"+name)<<value;}
void continuity_await_gate(const string &name){for(int n=0;n<1000&&!std::filesystem::exists(host_root+"/"+name);n++)std::this_thread::sleep_for(std::chrono::milliseconds(5));REQUIRE(std::filesystem::exists(host_root+"/"+name),"fresh process gate "+name);}
string continuity_gate_value(const string &name){continuity_await_gate(name);std::ifstream f(host_root+"/"+name);string value;f>>value;return value;}
pid_t continuity_spawn(const string &phase,const string &root=""){pid_t pid=fork();REQUIRE(pid>=0,"fresh subprocess created");if(pid==0){string directory=root.empty()?host_root:root;execl(host_program.c_str(),host_program.c_str(),directory.c_str(),"PROCESS",phase.c_str(),(char*)nullptr);std::_Exit(127);}return pid;}
void continuity_join(pid_t pid,int expected=0){int status=0;REQUIRE(waitpid(pid,&status,0)==pid&&WIFEXITED(status)&&WEXITSTATUS(status)==expected,"fresh subprocess expected result");}
