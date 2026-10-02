#ifndef JPW_NOCUDA_FIBO_CORE_MQH
#define JPW_NOCUDA_FIBO_CORE_MQH
// Imported native objects are not the manual AB0/C1 model. Geometry below is
// a named laboratory candidate, never a certified representation of MT5.
#define JPW_NCF_SCHEMA 1
#define JPW_NCF_RESOLVER 1
#define JPW_NCF_LEVELS 65
#define JPW_NCF_MAX_OPENS 200000
#define JPW_NCF_MAX_WIRE 6000000

enum JPWNCFStatus
  { JPW_NCF_VALID=0,JPW_NCF_ABSENT,JPW_NCF_BUSY,JPW_NCF_CORRUPT,
    JPW_NCF_INCOMPATIBLE,JPW_NCF_CONFLICT,JPW_NCF_IO_ERROR,
    JPW_NCF_UNVERIFIED_NATIVE,JPW_NCF_INVALID,JPW_NCF_CHANGED };
struct JPWNCFLevel
  { double value; string label; int line_color; int line_style; int line_width; };
struct JPWNCFSnapshot
  {
   int schema,resolver_version,reference_tf;
   string source_name,symbol,feed;
   long captured_utc,source_created;
   long anchor_time[3]; double anchor_price[3];
   JPWNCFLevel levels[JPW_NCF_LEVELS];
   int line_color,line_style,line_width;
   bool ray_left,ray_right,back,hidden,selectable;
   long timeframes,domain_from,domain_to;
   long opens[];
  };
void JPWNCFClear(JPWNCFSnapshot &s)
  {
   s.schema=JPW_NCF_SCHEMA; s.resolver_version=JPW_NCF_RESOLVER;
   s.reference_tf=0; s.source_name=""; s.symbol=""; s.feed=""; s.captured_utc=0; s.source_created=0;
   for(int i=0;i<3;i++) { s.anchor_time[i]=0; s.anchor_price[i]=0; }
   for(int i=0;i<JPW_NCF_LEVELS;i++)
     { s.levels[i].value=-4.0+i/8.0; s.levels[i].label="";
       s.levels[i].line_color=0; s.levels[i].line_style=0; s.levels[i].line_width=1; }
   s.line_color=0; s.line_style=0; s.line_width=1;
   s.ray_left=false; s.ray_right=false; s.back=false; s.hidden=false;
   s.selectable=true; s.timeframes=0; s.domain_from=0; s.domain_to=0;
   ArrayResize(s.opens,0);
  }
bool JPWNCFCopy(const JPWNCFSnapshot &a,JPWNCFSnapshot &b)
  {
   b.schema=a.schema; b.resolver_version=a.resolver_version;
   b.reference_tf=a.reference_tf; b.source_name=a.source_name;
   b.symbol=a.symbol; b.feed=a.feed; b.captured_utc=a.captured_utc; b.source_created=a.source_created;
   for(int i=0;i<3;i++) { b.anchor_time[i]=a.anchor_time[i]; b.anchor_price[i]=a.anchor_price[i]; }
   for(int i=0;i<JPW_NCF_LEVELS;i++)
     { b.levels[i].value=a.levels[i].value; b.levels[i].label=a.levels[i].label;
       b.levels[i].line_color=a.levels[i].line_color; b.levels[i].line_style=a.levels[i].line_style;
       b.levels[i].line_width=a.levels[i].line_width; }
   b.line_color=a.line_color; b.line_style=a.line_style; b.line_width=a.line_width;
   b.ray_left=a.ray_left; b.ray_right=a.ray_right; b.back=a.back;
   b.hidden=a.hidden; b.selectable=a.selectable; b.timeframes=a.timeframes;
   b.domain_from=a.domain_from; b.domain_to=a.domain_to;
   int count=ArraySize(a.opens);
   if(ArrayResize(b.opens,count)!=count) return(false);
   for(int i=0;i<count;i++) b.opens[i]=a.opens[i];
   return(true);
  }
bool JPWNCFFinitePositive(const double v) { return(MathIsValidNumber(v) && v>0.0); }
JPWNCFStatus JPWNCFValidate(const JPWNCFSnapshot &s,string &reason)
  {
   reason="";
   if(s.schema!=JPW_NCF_SCHEMA || s.resolver_version!=JPW_NCF_RESOLVER)
     { reason="Versao geometrica incompativel"; return(JPW_NCF_INCOMPATIBLE); }
   if(s.reference_tf<=0 || s.source_name=="" || StringLen(s.source_name)>256 ||
      s.symbol=="" || StringLen(s.symbol)>128 || s.feed=="" || StringLen(s.feed)>256 ||
      s.captured_utc<=0 || s.line_width<1 || s.line_width>5 ||
      s.line_style<0 || s.line_style>4 || s.timeframes<0)
     { reason="Metadados do canal invalidos"; return(JPW_NCF_INVALID); }
   const int count=ArraySize(s.opens);
   if(count<2 || count>JPW_NCF_MAX_OPENS || s.domain_from!=s.opens[0] ||
      s.domain_to!=s.opens[count-1] || s.domain_from<=0)
     { reason="Dominio temporal incompleto"; return(JPW_NCF_INVALID); }
   for(int i=1;i<count;i++) if(s.opens[i]<=s.opens[i-1])
     { reason="Sequencia temporal nao crescente"; return(JPW_NCF_INVALID); }
   for(int i=0;i<3;i++)
      if(s.anchor_time[i]<s.domain_from || s.anchor_time[i]>s.domain_to ||
         !JPWNCFFinitePositive(s.anchor_price[i]))
        { reason="Ancora fora do dominio carregado"; return(JPW_NCF_INVALID); }
   if(s.anchor_time[0]==s.anchor_time[1])
     { reason="A e B possuem o mesmo instante"; return(JPW_NCF_INVALID); }
   bool found[JPW_NCF_LEVELS];
   for(int i=0;i<JPW_NCF_LEVELS;i++) found[i]=false;
   for(int i=0;i<JPW_NCF_LEVELS;i++)
     {
      const double value=s.levels[i].value;
      if(!MathIsValidNumber(value) || value< -4.0 || value>4.0 ||
         StringLen(s.levels[i].label)>512 || s.levels[i].line_width<1 ||
         s.levels[i].line_width>5 || s.levels[i].line_style<0 || s.levels[i].line_style>4)
        { reason="Nivel invalido"; return(JPW_NCF_INVALID); }
      const int slot=(int)MathRound((value+4.0)*8.0);
      if(slot<0 || slot>=JPW_NCF_LEVELS || found[slot] ||
         MathAbs(value-(-4.0+slot/8.0))>1e-12)
        { reason="Esperados 65 niveis unicos de -4 a +4, passo 0,125"; return(JPW_NCF_INVALID); }
      found[slot]=true;
     }
   return(JPW_NCF_VALID);
  }
// Fractional ordinal uses the frozen observed opens, including intrabar anchors.
// Exact last open is available; nothing beyond it is silently extrapolated.
bool JPWNCFOrdinal(const JPWNCFSnapshot &s,const long when,double &ordinal)
  {
   ordinal=0; const int n=ArraySize(s.opens);
   if(n<2 || when<s.opens[0] || when>s.opens[n-1]) return(false);
   if(when==s.opens[n-1]) { ordinal=n-1; return(true); }
   int lo=0,hi=n-1;
   while(hi-lo>1) { int mid=lo+(hi-lo)/2; if(s.opens[mid]<=when) lo=mid; else hi=mid; }
   if(s.opens[hi]<=s.opens[lo]) return(false);
   ordinal=lo+(double)(when-s.opens[lo])/(double)(s.opens[hi]-s.opens[lo]);
   return(MathIsValidNumber(ordinal));
  }
// Candidate AB0_C1 / source-bar ordinal. NOT a demonstrated FiboChannel rule.
JPWNCFStatus JPWNCFCandidatePrice(const JPWNCFSnapshot &s,const double level,
                                 const long when,double &price,string &reason)
  {
   price=0; JPWNCFStatus status=JPWNCFValidate(s,reason);
   if(status!=JPW_NCF_VALID) return(status);
   double a=0,b=0,c=0,j=0;
   if(!MathIsValidNumber(level) || level< -4.0 || level>4.0 ||
      MathAbs((level+4.0)*8.0-MathRound((level+4.0)*8.0))>1e-10 ||
      !JPWNCFOrdinal(s,s.anchor_time[0],a) ||
      !JPWNCFOrdinal(s,s.anchor_time[1],b) || !JPWNCFOrdinal(s,s.anchor_time[2],c) ||
      !JPWNCFOrdinal(s,when,j) || a==b)
     { reason="Instante fora do dominio temporal"; return(JPW_NCF_INVALID); }
   const double slope=(s.anchor_price[1]-s.anchor_price[0])/(b-a);
   const double offset=s.anchor_price[2]-(s.anchor_price[0]+slope*(c-a));
   const double candidate=s.anchor_price[0]+slope*(j-a)+level*offset;
   if(!MathIsValidNumber(slope) || !MathIsValidNumber(offset) || offset==0 ||
      !JPWNCFFinitePositive(candidate))
     { reason="Geometria candidata degenerada"; return(JPW_NCF_INVALID); }
   price=candidate;
   reason="Candidato AB0_C1; paridade com Fibonacci nativo nao comprovada";
   return(JPW_NCF_UNVERIFIED_NATIVE);
  }
// There is deliberately no user preference or persisted boolean that unlocks
// native verification. A later audited resolver/receipt must change this gate.
JPWNCFStatus JPWNCFMeasure(const JPWNCFSnapshot &s,const double level,
                         const long when,double &price,string &reason)
  {
   double candidate=0;
   JPWNCFStatus status=JPWNCFCandidatePrice(s,level,when,candidate,reason);
   price=0; return(status);
  }
string JPWNCFFrame(const string v) { return(IntegerToString(StringLen(v))+":"+v); }
string JPWNCFNumber(const double v) { return(StringFormat("%.17g",v)); }
string JPWNCFSourceWire(const JPWNCFSnapshot &s)
  {
   string wire=JPWNCFFrame(s.symbol)+JPWNCFFrame(s.feed)+JPWNCFFrame(IntegerToString(s.reference_tf));
   for(int i=0;i<3;i++) wire+=JPWNCFFrame(IntegerToString(s.anchor_time[i]))+JPWNCFFrame(JPWNCFNumber(s.anchor_price[i]));
   wire+=JPWNCFFrame(IntegerToString(s.line_color))+JPWNCFFrame(IntegerToString(s.line_style))+
      JPWNCFFrame(IntegerToString(s.line_width))+JPWNCFFrame(IntegerToString((int)s.ray_left))+
      JPWNCFFrame(IntegerToString((int)s.ray_right))+JPWNCFFrame(IntegerToString((int)s.back))+
      JPWNCFFrame(IntegerToString((int)s.hidden))+JPWNCFFrame(IntegerToString((int)s.selectable))+
      JPWNCFFrame(IntegerToString(s.timeframes));
   for(int i=0;i<JPW_NCF_LEVELS;i++) wire+=JPWNCFFrame(JPWNCFNumber(s.levels[i].value))+
      JPWNCFFrame(s.levels[i].label)+JPWNCFFrame(IntegerToString(s.levels[i].line_color))+
      JPWNCFFrame(IntegerToString(s.levels[i].line_style))+JPWNCFFrame(IntegerToString(s.levels[i].line_width));
   return(wire);
  }
string JPWNCFPack(const JPWNCFSnapshot &s)
  {
   string reason=""; if(JPWNCFValidate(s,reason)!=JPW_NCF_VALID) return("");
   string wire=JPWNCFFrame(IntegerToString(s.schema))+JPWNCFFrame(IntegerToString(s.resolver_version))+
      JPWNCFFrame(s.source_name)+JPWNCFFrame(IntegerToString(s.captured_utc))+JPWNCFFrame(IntegerToString(s.source_created))+JPWNCFSourceWire(s)+
      JPWNCFFrame(IntegerToString(s.domain_from))+JPWNCFFrame(IntegerToString(s.domain_to))+
      JPWNCFFrame(IntegerToString(ArraySize(s.opens)));
   for(int i=0;i<ArraySize(s.opens);i++) wire+=JPWNCFFrame(IntegerToString(s.opens[i]));
   if(StringLen(wire)>JPW_NCF_MAX_WIRE) return("");
   return(wire);
  }
bool JPWNCFTake(const string wire,int &cursor,string &v)
  {
   v=""; const int end=StringFind(wire,":",cursor);
   if(end<cursor || end-cursor>8 || end==cursor) return(false);
   string size=StringSubstr(wire,cursor,end-cursor);
   const long count=StringToInteger(size);
   if(count<0 || IntegerToString(count)!=size || count>StringLen(wire)-end-1) return(false);
   v=StringSubstr(wire,end+1,(int)count); cursor=end+1+(int)count; return(true);
  }
bool JPWNCFTakeLong(const string wire,int &cursor,long &value)
  {
   string v=""; if(!JPWNCFTake(wire,cursor,v)) return(false);
   value=StringToInteger(v); return(IntegerToString(value)==v);
  }
bool JPWNCFTakeInt(const string wire,int &cursor,int &value)
  {
   long v=0; if(!JPWNCFTakeLong(wire,cursor,v) || v< -2147483648 || v>2147483647) return(false);
   value=(int)v; return(true);
  }
bool JPWNCFTakeBool(const string wire,int &cursor,bool &value)
  {
   int v=0; if(!JPWNCFTakeInt(wire,cursor,v) || (v!=0 && v!=1)) return(false);
   value=(v==1); return(true);
  }
bool JPWNCFTakeDouble(const string wire,int &cursor,double &value)
  {
   string v=""; if(!JPWNCFTake(wire,cursor,v)) return(false);
   value=StringToDouble(v); return(MathIsValidNumber(value) && JPWNCFNumber(value)==v);
  }
JPWNCFStatus JPWNCFUnpack(const string wire,JPWNCFSnapshot &s,string &reason)
  {
   JPWNCFClear(s); reason="Registro geometrico corrompido";
   if(StringLen(wire)>JPW_NCF_MAX_WIRE) return(JPW_NCF_CORRUPT);
   int p=0; JPWNCFSnapshot r; JPWNCFClear(r);
   bool ok=JPWNCFTakeInt(wire,p,r.schema) && JPWNCFTakeInt(wire,p,r.resolver_version) &&
      JPWNCFTake(wire,p,r.source_name) && JPWNCFTakeLong(wire,p,r.captured_utc) &&
      JPWNCFTakeLong(wire,p,r.source_created) && JPWNCFTake(wire,p,r.symbol) && JPWNCFTake(wire,p,r.feed) && JPWNCFTakeInt(wire,p,r.reference_tf);
   for(int i=0;i<3 && ok;i++) ok=JPWNCFTakeLong(wire,p,r.anchor_time[i]) && JPWNCFTakeDouble(wire,p,r.anchor_price[i]);
   ok=ok && JPWNCFTakeInt(wire,p,r.line_color) && JPWNCFTakeInt(wire,p,r.line_style) &&
      JPWNCFTakeInt(wire,p,r.line_width) && JPWNCFTakeBool(wire,p,r.ray_left) &&
      JPWNCFTakeBool(wire,p,r.ray_right) && JPWNCFTakeBool(wire,p,r.back) &&
      JPWNCFTakeBool(wire,p,r.hidden) && JPWNCFTakeBool(wire,p,r.selectable) && JPWNCFTakeLong(wire,p,r.timeframes);
   for(int i=0;i<JPW_NCF_LEVELS && ok;i++) ok=JPWNCFTakeDouble(wire,p,r.levels[i].value) &&
      JPWNCFTake(wire,p,r.levels[i].label) && JPWNCFTakeInt(wire,p,r.levels[i].line_color) &&
      JPWNCFTakeInt(wire,p,r.levels[i].line_style) && JPWNCFTakeInt(wire,p,r.levels[i].line_width);
   int n=0;
   ok=ok && JPWNCFTakeLong(wire,p,r.domain_from) && JPWNCFTakeLong(wire,p,r.domain_to) &&
      JPWNCFTakeInt(wire,p,n) && n>=2 && n<=JPW_NCF_MAX_OPENS;
   if(!ok || ArrayResize(r.opens,n)!=n) return(JPW_NCF_CORRUPT);
   for(int i=0;i<n && ok;i++) ok=JPWNCFTakeLong(wire,p,r.opens[i]);
   if(!ok || p!=StringLen(wire)) return(JPW_NCF_CORRUPT);
   JPWNCFStatus status=JPWNCFValidate(r,reason);
   if(status!=JPW_NCF_VALID) return(status==JPW_NCF_INCOMPATIBLE ? status : JPW_NCF_CORRUPT);
   if(!JPWNCFCopy(r,s)) { reason="Memoria insuficiente"; return(JPW_NCF_IO_ERROR); }
   reason=""; return(JPW_NCF_VALID);
  }
#endif
