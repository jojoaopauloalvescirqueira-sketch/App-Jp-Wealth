// Native quote/specification/account primitives are synthetic seams. The actual
// TerminalRowMath and TerminalDetails bodies are compiled unchanged below.
#include <limits>
constexpr int POSITION_TYPE_BUY=0,POSITION_TYPE_SELL=1;
long TimeTradeServer(){return host_wall;}
bool g_quotes_pending=false;
JPWInstrument host_personal_spec;double host_personal_gross=0;
bool JPWReadSpecification(const string& symbol,JPWInstrument& value){value=host_personal_spec;value.symbol=symbol;return true;}
bool JPWRiskOneGross(JPWAccount&,JPWPosition&,int,std::vector<JPWQuote>&,std::vector<JPWProfileEntry>&,const string&,bool,long,ulong,bool,bool,double& gross,bool&){gross=host_personal_gross;return true;}
