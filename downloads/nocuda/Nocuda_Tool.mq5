// Nocuda Tool 1.0 — manual geometry, no trading functions, network or DLL.
// Wire protocol: NOCUDA v1 / geom=bars1. See docs/architecture/NOCUDA-TRANSFER.md and MT5-LEIA-ME.md.
#property copyright "JP Wealth"
#property version "1.00"
#property strict
#property indicator_chart_window
#property indicator_plots 0

input group "Nocuda Tool | Controle"
input string InstanceId="main"; // ID unico por grafico (letras/numeros/_/-)
input string ImportarDesenho=""; // Cole codigo NOCUDA|v=1... completo
input bool AplicarImportacao=false; // Ative para aplicar codigo; desative para ajustar estilos
input bool ReiniciarPontos=false; // Reposicionar pelas entradas abaixo (descarta arraste anterior)
input string SimboloCanonico=""; // Identidade exata compartilhada (ex.: NZDUSD); vazio usa _Symbol
input string FeedIdentificador="UNKNOWN"; // Nome publico do feed; nunca numero de conta
input bool ProvedorDiferenteConfirmado=false; // Confirma ativo e escala de preco entre feeds diferentes
input bool MapeamentoSimboloConfirmado=false; // Confirma alias quando SimboloCanonico != _Symbol
input bool OffsetsHistoricosConfirmados=false; // Confirma os offsets para A, B e C nesta data
input int OffsetA_min=0; // Fuso do grafico/servidor em A; minutos em relacao a UTC
input int OffsetB_min=0; // Fuso do grafico/servidor em B
input int OffsetC_min=0; // Fuso do grafico/servidor em C
input datetime A_tempo=0; // A na linha17: abertura do candle no horario do grafico
input double A_preco=0; // A preco; zero gera proposta inicial a ajustar
input datetime B_tempo=0; // B na linha17
input double B_preco=0;
input datetime C_tempo=0; // C na linha9 (largura)
input double C_preco=0;
input group "Nocuda Tool | Malha"
input int ProjecoesAntes=8; // Linhas antes da linha1 (0..160)
input int ProjecoesDepois=24; // Linhas depois da linha17 (0..160);24 chega ao nivel4/MAX
input string Extensao="R"; // R=direita L=esquerda B=ambas N=segmento
input bool MostrarControles=true; // A/B17 e C9; independentes da visibilidade da malha
input group "Nocuda Tool | Linha 1"
input bool s1_visivel=true;
input color s1_cor=clrTomato;
input int s1_transparencia=0; // 0..100; aproximacao visual no fundo MT5
input int s1_espessura=2; // 1..5
input string s1_traco="S"; // S=continuo D=tracejado P=pontilhado
input group "Nocuda Tool | Linha 3"
input bool s3_visivel=true;
input color s3_cor=clrTomato;
input int s3_transparencia=0; // 0..100; aproximacao visual no fundo MT5
input int s3_espessura=1; // 1..5
input string s3_traco="S"; // S=continuo D=tracejado P=pontilhado
input group "Nocuda Tool | Linha 5"
input bool s5_visivel=true;
input color s5_cor=clrTomato;
input int s5_transparencia=0; // 0..100; aproximacao visual no fundo MT5
input int s5_espessura=1; // 1..5
input string s5_traco="S"; // S=continuo D=tracejado P=pontilhado
input group "Nocuda Tool | Linha 9"
input bool s9_visivel=true;
input color s9_cor=clrTomato;
input int s9_transparencia=0; // 0..100; aproximacao visual no fundo MT5
input int s9_espessura=2; // 1..5
input string s9_traco="S"; // S=continuo D=tracejado P=pontilhado
input group "Nocuda Tool | Linha 17"
input bool s17_visivel=true;
input color s17_cor=clrTomato;
input int s17_transparencia=0; // 0..100; aproximacao visual no fundo MT5
input int s17_espessura=2; // 1..5
input string s17_traco="S"; // S=continuo D=tracejado P=pontilhado
input group "Nocuda Tool | Intermediarias"
input bool si_visivel=true;
input color si_cor=clrTomato;
input int si_transparencia=35; // 0..100; aproximacao visual no fundo MT5
input int si_espessura=1; // 1..5
input string si_traco="P"; // S=continuo D=tracejado P=pontilhado
input group "Nocuda Tool | Projecoes externas"
input bool sx_visivel=true;
input color sx_cor=clrTomato;
input int sx_transparencia=55; // 0..100; aproximacao visual no fundo MT5
input int sx_espessura=1; // 1..5
input string sx_traco="P"; // S=continuo D=tracejado P=pontilhado
input group "Nocuda Tool | Rotulos"
input string Rotulos="M"; // M=marcos A=todos N=nenhum
input int RotuloTamanho=10; // 8..24
input color RotuloCor=clrTomato;
input int RotuloTransparencia=0;
input string RotuloPosicao="R"; // L=inicio C=centro R=fim T=ultimo candle
input string RotuloVertical="U"; // U=acima O=sobre D=abaixo
input double RotuloDistancia=1; // % da largura D (0..50)
input int RotuloDeslocamento=0; // candles (-100..100)
input bool MostrarNivel=false;
input bool MostrarPreco=false;
input bool MostrarMAX=true;
input bool CorDaLinha=true;

struct Style { bool on; int r,g,b,alpha,width; string dash; };
struct Labels { string mode; int size,r,g,b,alpha; string pos,vert; double gap; int offset; bool level,price,max,lineColor; };
struct Model {
 string id,src,symbol,feed,ext; long tf,utcA,utcB,utcC; int offA,offB,offC;
 double pa,pb,pc,d; string rawPa,rawPb,rawPc,rawD; int ab,ac,before,after; Style s[7]; Labels labels;
};
Model model;
string prefix,problem="";
bool ready=false,offsetsDirty=false,busy=false,nativeMode=true;
datetime ta=0,tb=0,tc=0;
int ia=0,ib=0,ic=0;
string keyList="v,geom,id,src,symbol,feed,tf,scale,a,b,c,d,ab,ac,step,before,after,ext,s1,s3,s5,s9,s17,si,sx,labels";

bool Fail(string message) { problem=message; return false; }
bool Member(string value,string choices) { return StringFind(","+choices+",",","+value+",")>=0; }
bool SafeId(string value,int maxlen=64) {
 int n=StringLen(value); if(n<1 || n>maxlen) return false;
 for(int i=0;i<n;i++){ ushort ch=StringGetCharacter(value,i);
  if(!((ch>=65&&ch<=90)||(ch>=97&&ch<=122)||(ch>=48&&ch<=57)||StringFind("._:/+-",ShortToString(ch))>=0)) return false;
 } return true;
}
bool InstanceValid(string value) {
 if(!SafeId(value,24)) return false;
 for(int i=0;i<StringLen(value);i++) if(StringFind(".:/+",StringSubstr(value,i,1))>=0)return false;
 return true;
}
bool Decimal(string value,double &number,bool integer=false) {
 int n=StringLen(value),i=0; if(n==0)return false;
 if(StringSubstr(value,0,1)=="-"){i++;if(i==n)return false;}
 int first=i; ushort ch=StringGetCharacter(value,i);
 if(ch<48||ch>57)return false;
 if(ch==48&&i+1<n&&StringSubstr(value,i+1,1)!=".")return false;
 for(;i<n&&StringGetCharacter(value,i)>=48&&StringGetCharacter(value,i)<=57;i++){}
 if(i<n){if(integer||StringSubstr(value,i,1)!=".")return false; i++;if(i==n)return false;
  for(;i<n;i++){ch=StringGetCharacter(value,i);if(ch<48||ch>57)return false;}}
 number=StringToDouble(value); return MathIsValidNumber(number)&&MathAbs(number)<=4102444800000.0;
}
bool Number(string text,double &out,double min,double max,bool integer=false) {
 return Decimal(text,out,integer)&&out>=min&&out<=max;
}
bool Integer(string text,int &out,int min,int max) {
 double n; if(!Number(text,n,min,max,true))return false; out=(int)n;return true;
}
bool Anchor(string text,long &utc,double &price,int &offset) {
 string p[];if(StringSplit(text,',',p)!=3)return false;
 double n;if(!Number(p[0],n,0,4102444800000.0,true))return false;utc=(long)n;
 return Number(p[1],price,-1e12,1e12)&&Integer(p[2],offset,-840,840);
}
bool ParseStyle(string text,Style &s) {
 string p[];if(StringSplit(text,',',p)!=7)return false;int on;
 if(!Integer(p[0],on,0,1)||!Integer(p[1],s.r,0,255)||!Integer(p[2],s.g,0,255)||!Integer(p[3],s.b,0,255)||!Integer(p[4],s.alpha,0,100)||!Integer(p[5],s.width,1,5)||!Member(p[6],"S,D,P"))return false;
 s.on=on==1;s.dash=p[6];return true;
}
bool ParseLabels(string text,Labels &l) {
 string p[];if(StringSplit(text,',',p)!=14)return false;int a,b,c,d;
 if(!Member(p[0],"M,A,N")||!Integer(p[1],l.size,8,24)||!Integer(p[2],l.r,0,255)||!Integer(p[3],l.g,0,255)||!Integer(p[4],l.b,0,255)||!Integer(p[5],l.alpha,0,100)||!Member(p[6],"L,C,R,T")||!Member(p[7],"U,O,D")||!Number(p[8],l.gap,0,50)||!Integer(p[9],l.offset,-100,100)||!Integer(p[10],a,0,1)||!Integer(p[11],b,0,1)||!Integer(p[12],c,0,1)||!Integer(p[13],d,0,1))return false;
 l.mode=p[0];l.pos=p[6];l.vert=p[7];l.level=a==1;l.price=b==1;l.max=c==1;l.lineColor=d==1;return true;
}
bool Parse(string wire,Model &m) {
 if(StringLen(wire)>16384)return Fail("Codigo excede 16 KiB.");
 string parts[],keys[];int count=StringSplit(wire,'|',parts);StringSplit(keyList,',',keys);
 if(count!=27||parts[0]!="NOCUDA")return Fail("Cabecalho/quantidade de campos invalida.");
 string v[26];bool seen[26];ArrayInitialize(seen,false);
 for(int i=1;i<count;i++) {
  int equal=StringFind(parts[i],"=");if(equal<1)return Fail("Campo sem valor.");
  string key=StringSubstr(parts[i],0,equal);int found=-1;
  for(int k=0;k<26;k++)if(keys[k]==key){found=k;break;}
  if(found<0||seen[found])return Fail("Campo desconhecido ou duplicado: "+key);
  seen[found]=true;v[found]=StringSubstr(parts[i],equal+1);
 }
 if(v[0]!="1"||v[1]!="bars1"||v[7]!="L"||v[14]!="0.125")return Fail("Versao/geometria/escala/passo incompativel.");
 if(!SafeId(v[2])||!Member(v[3],"TV,MT5,JPW")||!SafeId(v[4])||!SafeId(v[5]))return Fail("Identidade invalida.");
 m.id=v[2];m.src=v[3];m.symbol=v[4];m.feed=v[5];
 int tf;if(!Integer(v[6],tf,1,2592000))return Fail("Periodo invalido.");m.tf=tf;
 if(!Anchor(v[8],m.utcA,m.pa,m.offA)||!Anchor(v[9],m.utcB,m.pb,m.offB)||!Anchor(v[10],m.utcC,m.pc,m.offC))return Fail("Ancora invalida.");
 string raw[];StringSplit(v[8],',',raw);m.rawPa=raw[1];StringSplit(v[9],',',raw);m.rawPb=raw[1];StringSplit(v[10],',',raw);m.rawPc=raw[1];m.rawD=v[11];
 if(!Number(v[11],m.d,-1e12,1e12)||MathAbs(m.d)<=1e-12||!Integer(v[12],m.ab,-4999,4999)||m.ab==0||!Integer(v[13],m.ac,-4999,4999))return Fail("Distancia/contagem de candles invalida.");
 if(m.utcA==m.utcB||(m.utcB>m.utcA)!=(m.ab>0)||(m.utcC>m.utcA)!=(m.ac>0)||(m.utcC==m.utcA)!=(m.ac==0))return Fail("Ordem temporal e candles incoerentes.");
 if((m.utcC>m.utcB)!=(m.ac>m.ab)||(m.utcC==m.utcB)!=(m.ac==m.ab))return Fail("Ordem B-C incoerente.");
 double expected=m.pa+(m.pb-m.pa)*(double)m.ac/m.ab-m.pc;
 if(!MathIsValidNumber(expected)||MathAbs(expected-m.d)>MathMax(1e-10,MathAbs(m.d)*1e-8))return Fail("Largura diverge das ancoras e candles.");
 if(!Integer(v[15],m.before,0,160)||!Integer(v[16],m.after,0,160)||!Member(v[17],"R,L,B,N"))return Fail("Projecoes/extensao invalidas.");m.ext=v[17];
 for(int i=0;i<7;i++)if(!ParseStyle(v[18+i],m.s[i]))return Fail("Estilo invalido.");
 if(!ParseLabels(v[25],m.labels))return Fail("Rotulos invalidos.");
 return true;
}
string N(double x) {
 string s=DoubleToString(x,16);
 while(StringLen(s)>1&&StringSubstr(s,StringLen(s)-1)=="0")s=StringSubstr(s,0,StringLen(s)-1);
 if(StringSubstr(s,StringLen(s)-1)==".")s=StringSubstr(s,0,StringLen(s)-1);
 if(s=="-0")s="0";return s;
}
string Preserve(string raw,double value) {
 // Import tokens are transported unchanged until the numeric anchor is edited.
 return raw!=""&&StringToDouble(raw)==value?raw:N(value);
}
string I(long x){return IntegerToString(x);}
string Bit(bool x){return x?"1":"0";}
string StyleWire(Style &s){return Bit(s.on)+","+I(s.r)+","+I(s.g)+","+I(s.b)+","+I(s.alpha)+","+I(s.width)+","+s.dash;}
string Serialize(Model &m) {
 string out="NOCUDA|v=1|geom=bars1|id="+m.id+"|src="+m.src+"|symbol="+m.symbol+"|feed="+m.feed+"|tf="+I(m.tf)+"|scale=L";
 out+="|a="+I(m.utcA)+","+Preserve(m.rawPa,m.pa)+","+I(m.offA)+"|b="+I(m.utcB)+","+Preserve(m.rawPb,m.pb)+","+I(m.offB)+"|c="+I(m.utcC)+","+Preserve(m.rawPc,m.pc)+","+I(m.offC);
 out+="|d="+Preserve(m.rawD,m.d)+"|ab="+I(m.ab)+"|ac="+I(m.ac)+"|step=0.125|before="+I(m.before)+"|after="+I(m.after)+"|ext="+m.ext;
 string names[]={"s1","s3","s5","s9","s17","si","sx"};for(int j=0;j<7;j++)out+="|"+names[j]+"="+StyleWire(m.s[j]);
 Labels l=m.labels;
 out+="|labels="+l.mode+","+I(l.size)+","+I(l.r)+","+I(l.g)+","+I(l.b)+","+I(l.alpha)+","+l.pos+","+l.vert+","+N(l.gap)+","+I(l.offset)+","+Bit(l.level)+","+Bit(l.price)+","+Bit(l.max)+","+Bit(l.lineColor);
 return out;
}
void SetStyle(Style &s,bool on,color c,int alpha,int width,string dash) {
 s.on=on;s.r=(int)c&255;s.g=((int)c>>8)&255;s.b=((int)c>>16)&255;s.alpha=alpha;s.width=width;s.dash=dash;
}
void Appearance(Model &m) {
 m.before=ProjecoesAntes;m.after=ProjecoesDepois;m.ext=Extensao;
 SetStyle(m.s[0],s1_visivel,s1_cor,s1_transparencia,s1_espessura,s1_traco);
 SetStyle(m.s[1],s3_visivel,s3_cor,s3_transparencia,s3_espessura,s3_traco);
 SetStyle(m.s[2],s5_visivel,s5_cor,s5_transparencia,s5_espessura,s5_traco);
 SetStyle(m.s[3],s9_visivel,s9_cor,s9_transparencia,s9_espessura,s9_traco);
 SetStyle(m.s[4],s17_visivel,s17_cor,s17_transparencia,s17_espessura,s17_traco);
 SetStyle(m.s[5],si_visivel,si_cor,si_transparencia,si_espessura,si_traco);
 SetStyle(m.s[6],sx_visivel,sx_cor,sx_transparencia,sx_espessura,sx_traco);
 m.labels.mode=Rotulos;m.labels.size=RotuloTamanho;m.labels.r=(int)RotuloCor&255;m.labels.g=((int)RotuloCor>>8)&255;m.labels.b=((int)RotuloCor>>16)&255;m.labels.alpha=RotuloTransparencia;
 m.labels.pos=RotuloPosicao;m.labels.vert=RotuloVertical;m.labels.gap=RotuloDistancia;m.labels.offset=RotuloDeslocamento;m.labels.level=MostrarNivel;m.labels.price=MostrarPreco;m.labels.max=MostrarMAX;m.labels.lineColor=CorDaLinha;
}
string Canonical(){return SimboloCanonico==""?_Symbol:SimboloCanonico;}
bool OffsetsValid(){return OffsetA_min>=-840&&OffsetA_min<=840&&OffsetB_min>=-840&&OffsetB_min<=840&&OffsetC_min>=-840&&OffsetC_min<=840;}
bool SymbolValid(){return SafeId(Canonical())&&(Canonical()==_Symbol||MapeamentoSimboloConfirmado);}
bool LoadDestination(Model &m) {
 if(!OffsetsHistoricosConfirmados||!OffsetsValid())return Fail("Confirme os offsets historicos de DESTINO para A/B/C nas entradas.");
 if(!SymbolValid()||m.symbol!=Canonical())return Fail("Simbolo incompativel; confirme explicitamente o alias canonico.");
 if(_Period==PERIOD_MN1)return Fail("Periodo mensal nao e fixo; use outro periodo.");
 if((m.feed!=FeedIdentificador||m.feed=="UNKNOWN"||FeedIdentificador=="UNKNOWN")&&!ProvedorDiferenteConfirmado)return Fail("Provedor diferente. Confira ativo/precos e confirme nas entradas.");
 if(m.tf!=PeriodSeconds(_Period))return Fail("Periodo incompativel. Abra o periodo original.");
 if(m.utcA%1000!=0||m.utcB%1000!=0||m.utcC%1000!=0)return Fail("MT5 exige ancoras em segundos exatos.");
 ta=(datetime)(m.utcA/1000+OffsetA_min*60);tb=(datetime)(m.utcB/1000+OffsetB_min*60);tc=(datetime)(m.utcC/1000+OffsetC_min*60);
 ia=iBarShift(_Symbol,_Period,ta,true);ib=iBarShift(_Symbol,_Period,tb,true);ic=iBarShift(_Symbol,_Period,tc,true);
 if(ia<0||ib<0||ic<0||iTime(_Symbol,_Period,ia)!=ta||iTime(_Symbol,_Period,ib)!=tb||iTime(_Symbol,_Period,ic)!=tc)return Fail("Ancora sem candle de abertura exato; carregue historico ou confira fuso/feed.");
 if(ia-ib!=m.ab||ia-ic!=m.ac)return Fail("Historico/sessoes incompativeis: contagens A-B/A-C divergentes.");
 return true;
}
bool FromLocal(Model &m,datetime a,datetime b,datetime c,bool snap=false) {
 int sa=iBarShift(_Symbol,_Period,a,!snap),sb=iBarShift(_Symbol,_Period,b,!snap),sc=iBarShift(_Symbol,_Period,c,!snap);
 if(sa<0||sb<0||sc<0)return Fail("Candles indisponiveis para os pontos.");
 if(!snap&&(iTime(_Symbol,_Period,sa)!=a||iTime(_Symbol,_Period,sb)!=b||iTime(_Symbol,_Period,sc)!=c))return Fail("Use abertura exata do candle nas datas.");
 ta=iTime(_Symbol,_Period,sa);tb=iTime(_Symbol,_Period,sb);tc=iTime(_Symbol,_Period,sc);ia=sa;ib=sb;ic=sc;
 m.utcA=((long)ta-OffsetA_min*60)*1000;m.utcB=((long)tb-OffsetB_min*60)*1000;m.utcC=((long)tc-OffsetC_min*60)*1000;
 m.offA=OffsetA_min;m.offB=OffsetB_min;m.offC=OffsetC_min;m.ab=sa-sb;m.ac=sa-sc;
 if(m.ab==0)return Fail("A e B precisam de candles distintos.");
 m.d=m.pa+(m.pb-m.pa)*(double)m.ac/m.ab-m.pc;
 Model checked;if(!Parse(Serialize(m),checked))return false;
 return true;
}
color Blend(int r,int g,int b,int alpha) {
 color bg=(color)ChartGetInteger(0,CHART_COLOR_BACKGROUND);
 double a=(100-alpha)/100.0;
 int rr=(int)MathRound(r*a+((int)bg&255)*(1-a));
 int gg=(int)MathRound(g*a+(((int)bg>>8)&255)*(1-a));
 int bb=(int)MathRound(b*a+(((int)bg>>16)&255)*(1-a));
 return (color)(rr|(gg<<8)|(bb<<16));
}
int StyleIndex(int line) {if(line==1)return 0;if(line==3)return 1;if(line==5)return 2;if(line==9)return 3;if(line==17)return 4;return line<1||line>17?6:5;}
ENUM_LINE_STYLE Dash(string d){return d=="D"?STYLE_DASH:d=="P"?STYLE_DOT:STYLE_SOLID;}
void Status(string text,bool error=false) {
 string name=prefix+"status";
 if(ObjectFind(0,name)<0)ObjectCreate(0,name,OBJ_LABEL,0,0,0);
 ObjectSetInteger(0,name,OBJPROP_CORNER,CORNER_LEFT_UPPER);ObjectSetInteger(0,name,OBJPROP_XDISTANCE,12);ObjectSetInteger(0,name,OBJPROP_YDISTANCE,45);ObjectSetInteger(0,name,OBJPROP_FONTSIZE,9);
 ObjectSetInteger(0,name,OBJPROP_COLOR,error?clrOrangeRed:(color)ChartGetInteger(0,CHART_COLOR_FOREGROUND));
 ObjectSetString(0,name,OBJPROP_TEXT,"Nocuda Tool: "+text);ObjectSetString(0,name,OBJPROP_TOOLTIP,text);
}
void ConfirmOffsets() {
 if(!ready||!OffsetsHistoricosConfirmados){Status("Ative a confirmacao historica e informe os tres offsets nas entradas.",true);return;}
 Model next=model;
 if(!FromLocal(next,ta,tb,tc)){Status(problem,true);return;}
 next.d=model.d;model=next;offsetsDirty=false;SaveState();Status("Offsets historicos confirmados para os tres pontos atuais.");
}
void Button() {
 string n=prefix+"export";if(ObjectFind(0,n)<0)ObjectCreate(0,n,OBJ_BUTTON,0,0,0);
 ObjectSetInteger(0,n,OBJPROP_XDISTANCE,12);ObjectSetInteger(0,n,OBJPROP_YDISTANCE,18);ObjectSetInteger(0,n,OBJPROP_XSIZE,185);ObjectSetInteger(0,n,OBJPROP_YSIZE,23);
 ObjectSetInteger(0,n,OBJPROP_FONTSIZE,9);ObjectSetString(0,n,OBJPROP_TEXT,"Nocuda: exportar .txt");ObjectSetString(0,n,OBJPROP_TOOLTIP,"Salva codigo em MQL5/Files. Sem DLL/clipboard/rede.");
 string c=prefix+"confirm";if(ObjectFind(0,c)<0)ObjectCreate(0,c,OBJ_BUTTON,0,0,0);
 ObjectSetInteger(0,c,OBJPROP_XDISTANCE,205);ObjectSetInteger(0,c,OBJPROP_YDISTANCE,18);ObjectSetInteger(0,c,OBJPROP_XSIZE,155);ObjectSetInteger(0,c,OBJPROP_YSIZE,23);
 ObjectSetInteger(0,c,OBJPROP_FONTSIZE,9);ObjectSetString(0,c,OBJPROP_TEXT,"Confirmar fusos A/B/C");ObjectSetString(0,c,OBJPROP_TOOLTIP,"Confirma offsets das entradas para as datas atuais. Revise horario de verao historico antes de confirmar.");
}
bool Trend(string name,datetime t1,double p1,datetime t2,double p2,Style &s,bool selectable=false) {
 if(ObjectFind(0,name)<0&&!ObjectCreate(0,name,OBJ_TREND,0,t1,p1,t2,p2))return false;
 if(!ObjectMove(0,name,0,t1,p1)||!ObjectMove(0,name,1,t2,p2))return false;
 ObjectSetInteger(0,name,OBJPROP_COLOR,Blend(s.r,s.g,s.b,s.alpha));ObjectSetInteger(0,name,OBJPROP_STYLE,Dash(s.dash));ObjectSetInteger(0,name,OBJPROP_WIDTH,s.width);
 ObjectSetInteger(0,name,OBJPROP_RAY_LEFT,model.ext=="L"||model.ext=="B");ObjectSetInteger(0,name,OBJPROP_RAY_RIGHT,model.ext=="R"||model.ext=="B");ObjectSetInteger(0,name,OBJPROP_SELECTABLE,selectable);ObjectSetInteger(0,name,OBJPROP_HIDDEN,!selectable);
 ObjectSetString(0,name,OBJPROP_TOOLTIP,selectable?"Nocuda Tool A/B: linha17. Arraste as extremidades.":name);
 return true;
}
datetime AtShift(int shift) {
 if(shift>=0&&shift<Bars(_Symbol,_Period))return iTime(_Symbol,_Period,shift);
 if(shift<0)return (datetime)((long)iTime(_Symbol,_Period,0)-(long)shift*PeriodSeconds(_Period));
 return 0;
}
void Label(int line,Style &s) {
 string name=prefix+"label"+I(line);Labels l=model.labels;
 bool milestone=line==1||line==3||line==5||line==9||line==17;
 bool show=l.mode=="A"||(l.mode=="M"&&milestone)||(l.max&&line==41&&l.mode!="N");
 if(!show||!s.on){ObjectDelete(0,name);return;}
 int shift=l.pos=="L"?MathMax(ia,ib):l.pos=="C"?(ia+ib)/2:l.pos=="T"?0:MathMin(ia,ib);
 shift-=l.offset;datetime when=AtShift(shift);if(when==0){ObjectDelete(0,name);return;}
 double level=(line-9)/8.0;
 double price=model.pa+(model.pb-model.pa)*(double)(ia-shift)/model.ab+(level-1)*model.d;
 double gap=MathAbs(model.d)*l.gap/100;
 double y=price+(l.vert=="U"?gap:l.vert=="D"?-gap:0);
 if(ObjectFind(0,name)<0)ObjectCreate(0,name,OBJ_TEXT,0,when,y);else ObjectMove(0,name,0,when,y);
 string text=line==41&&l.max?"MAX":I(line);
 if(l.level)text+=" ["+N(level)+"]";
 if(l.price)text+=" "+DoubleToString(price,_Digits);
 ObjectSetString(0,name,OBJPROP_TEXT,text);ObjectSetString(0,name,OBJPROP_FONT,"Arial");
 ObjectSetInteger(0,name,OBJPROP_FONTSIZE,l.size);ObjectSetInteger(0,name,OBJPROP_COLOR,l.lineColor?Blend(s.r,s.g,s.b,l.alpha):Blend(l.r,l.g,l.b,l.alpha));
 ObjectSetInteger(0,name,OBJPROP_ANCHOR,l.vert=="U"?ANCHOR_LOWER:l.vert=="D"?ANCHOR_UPPER:ANCHOR_CENTER);ObjectSetInteger(0,name,OBJPROP_SELECTABLE,false);ObjectSetInteger(0,name,OBJPROP_HIDDEN,true);
}
void SaveState() {
 string name=prefix+"state";if(ObjectFind(0,name)<0)ObjectCreate(0,name,OBJ_LABEL,0,0,0);
 ObjectSetString(0,name,OBJPROP_TEXT,Serialize(model));ObjectSetInteger(0,name,OBJPROP_TIMEFRAMES,OBJ_NO_PERIODS);ObjectSetInteger(0,name,OBJPROP_HIDDEN,true);
 // Input fingerprint distinguishes an unchanged imported code from a new import.
 ObjectSetString(0,name,OBJPROP_TOOLTIP,ImportarDesenho);
 string local=prefix+"local";if(ObjectFind(0,local)<0)ObjectCreate(0,local,OBJ_LABEL,0,0,0);
 ObjectSetString(0,local,OBJPROP_TEXT,I((long)ta)+","+I((long)tb)+","+I((long)tc)+","+Bit(offsetsDirty)+","+Bit(nativeMode));ObjectSetInteger(0,local,OBJPROP_TIMEFRAMES,OBJ_NO_PERIODS);ObjectSetInteger(0,local,OBJPROP_HIDDEN,true);
}
bool Render() {
 if(!ready)return false;
 busy=true;
 for(int line=1-model.before;line<=17+model.after;line++) {
  Style s=model.s[StyleIndex(line)];string name=prefix+"line"+I(line);double offset=((line-9)/8.0-1)*model.d;
  if(s.on&&s.alpha<100) {
   if(!Trend(name,ta,model.pa+offset,tb,model.pb+offset,s)){busy=false;return Fail("Falha ao criar linha "+I(line));}
  }else ObjectDelete(0,name);
  Label(line,s);
 }
 string control=prefix+"AB17",c=prefix+"C9";
 if(MostrarControles) {
  Style s=model.s[4];s.on=true;s.alpha=0;s.width=1;s.dash="S";
  if(!Trend(control,ta,model.pa,tb,model.pb,s,true)){busy=false;return Fail("Falha controle A/B.");}
  // Reference is a bounded handle; the rendered grid owns extension/style.
  ObjectSetInteger(0,control,OBJPROP_RAY_LEFT,false);ObjectSetInteger(0,control,OBJPROP_RAY_RIGHT,false);
  if(ObjectFind(0,c)<0)ObjectCreate(0,c,OBJ_ARROW,0,tc,model.pc);else ObjectMove(0,c,0,tc,model.pc);
  ObjectSetInteger(0,c,OBJPROP_ARROWCODE,159);ObjectSetInteger(0,c,OBJPROP_ANCHOR,ANCHOR_TOP);ObjectSetInteger(0,c,OBJPROP_COLOR,Blend(model.s[3].r,model.s[3].g,model.s[3].b,0));ObjectSetInteger(0,c,OBJPROP_WIDTH,2);ObjectSetInteger(0,c,OBJPROP_SELECTABLE,true);ObjectSetInteger(0,c,OBJPROP_HIDDEN,false);
  ObjectSetString(0,c,OBJPROP_TOOLTIP,"Nocuda Tool C: linha9. Arraste para ajustar largura.");
 } else {ObjectDelete(0,control);ObjectDelete(0,c);}
 SaveState();Button();ChartRedraw();busy=false;return true;
}
void ClearGrid() {
 for(int j=ObjectsTotal(0)-1;j>=0;j--){string n=ObjectName(0,j);if(StringFind(n,prefix+"line")==0||StringFind(n,prefix+"label")==0||n==prefix+"AB17"||n==prefix+"C9")ObjectDelete(0,n);}
}
void Export() {
 if(!ready||!OffsetsHistoricosConfirmados||offsetsDirty){Status("Reconfirme offsets historicos A/B/C apos mudar datas, nas entradas.",true);return;}
 Model out=model;out.src="MT5";out.feed=FeedIdentificador;out.offA=OffsetA_min;out.offB=OffsetB_min;out.offC=OffsetC_min;
 Model check;string wire=Serialize(out);if(!Parse(wire,check)){Status(problem,true);return;}
 // A unique filename preserves previously exported drawings. No account identifiers.
 string filename="Nocuda_"+InstanceId+"_"+I((long)TimeLocal())+"_"+I((long)GetMicrosecondCount())+".txt";
 if(FileIsExist(filename)){Status("Nome de arquivo ja existe; tente exportar novamente.",true);return;}
 ResetLastError();int h=FileOpen(filename,FILE_WRITE|FILE_TXT|FILE_ANSI,0,CP_UTF8);
 if(h==INVALID_HANDLE){Status("Exportacao recusada: FileOpen erro "+I(GetLastError()),true);return;}
 uint written=FileWriteString(h,wire);FileFlush(h);FileClose(h);
 int read=FileOpen(filename,FILE_READ|FILE_TXT|FILE_ANSI,0,CP_UTF8);string confirm=read==INVALID_HANDLE?"":FileReadString(read);if(read!=INVALID_HANDLE)FileClose(read);
 if(written==0||confirm!=wire){Status("Arquivo nao confirmado. Nao foi anunciado sucesso.",true);return;}
 Status("Salvo em MQL5/Files/"+filename);Print("Nocuda Tool: exportacao confirmada em MQL5/Files/",filename);
}
int OnInit() {
 IndicatorSetString(INDICATOR_SHORTNAME,"Nocuda Tool | "+InstanceId);
 if(!InstanceValid(InstanceId)){Print("Nocuda Tool: InstanceId invalido.");return INIT_PARAMETERS_INCORRECT;}
 prefix="Nocuda#"+InstanceId+"#";problem="";
 if(_Period==PERIOD_MN1){ClearGrid();Status("Periodo mensal nao e fixo; use outro periodo.",true);return INIT_SUCCEEDED;}
 if(!OffsetsValid()||!SymbolValid()||!SafeId(FeedIdentificador)){ClearGrid();Status("Confira identidade, alias e offsets validos.",true);return INIT_SUCCEEDED;}
 string saved=ObjectGetString(0,prefix+"state",OBJPROP_TEXT),previousImport=ObjectGetString(0,prefix+"state",OBJPROP_TOOLTIP);
 Model candidate;offsetsDirty=false;
 if(AplicarImportacao&&ImportarDesenho!=""&&(ReiniciarPontos||ImportarDesenho!=previousImport||saved=="")) {
  if(!Parse(ImportarDesenho,candidate)||!LoadDestination(candidate)){Status("Importacao recusada: "+problem,true);return INIT_SUCCEEDED;}
  nativeMode=false;
 } else if(!ReiniciarPontos&&saved!="") {
  if(!Parse(saved,candidate)){Status("Estado preservado, invalido: "+problem,true);return INIT_SUCCEEDED;}
  string loc[];int fields=StringSplit(ObjectGetString(0,prefix+"local",OBJPROP_TEXT),',',loc);
  bool wasDirty=fields==5&&loc[3]=="1";nativeMode=fields==5&&loc[4]=="1";
  if(nativeMode&&candidate.symbol==Canonical()&&candidate.tf==PeriodSeconds(_Period)) {
   // A manual drag changed local dates. Editing historical offsets must update
   // UTC from these dates, rather than shift the trader's local anchor silently.
   double preservedWidth=candidate.d;
   if(!FromLocal(candidate,(datetime)StringToInteger(loc[0]),(datetime)StringToInteger(loc[1]),(datetime)StringToInteger(loc[2]))){Status(problem,true);ClearGrid();return INIT_SUCCEEDED;}
   candidate.d=preservedWidth;candidate.src="MT5";candidate.feed=FeedIdentificador;offsetsDirty=wasDirty;
  }else if(!LoadDestination(candidate)){Status("Desenho preservado, exibicao suspensa: "+problem,true);ClearGrid();return INIT_SUCCEEDED;}
  if(!AplicarImportacao)Appearance(candidate);
 } else {
  nativeMode=true;
  candidate.id=InstanceId;candidate.src="MT5";candidate.symbol=Canonical();candidate.feed=FeedIdentificador;candidate.tf=PeriodSeconds(_Period);Appearance(candidate);
  datetime a=A_tempo,b=B_tempo,c=C_tempo;candidate.pa=A_preco;candidate.pb=B_preco;candidate.pc=C_preco;
  bool empty=a==0&&b==0&&c==0&&candidate.pa==0&&candidate.pb==0&&candidate.pc==0;
  if(empty){
   int bars=Bars(_Symbol,_Period);if(bars<30){Status("Carregue ao menos 30 candles.",true);return INIT_FAILED;}
   int sa=MathMin(100,bars-1),sb=sa/5,sc=(sa+sb)/2;
   a=iTime(_Symbol,_Period,sa);b=iTime(_Symbol,_Period,sb);c=iTime(_Symbol,_Period,sc);
   double hi=ChartGetDouble(0,CHART_PRICE_MAX),lo=ChartGetDouble(0,CHART_PRICE_MIN);
   candidate.pa=lo+(hi-lo)*0.65;candidate.pb=lo+(hi-lo)*0.60;candidate.pc=lo+(hi-lo)*0.40;
  }else if(a==0||b==0||c==0){Status("Preencha todos os pontos ou deixe todos zerados.",true);return INIT_SUCCEEDED;}
  if(!FromLocal(candidate,a,b,c)){Status(problem,true);return INIT_SUCCEEDED;}
 }
 Model checked;if(!Parse(Serialize(candidate),checked)){Status(problem,true);return INIT_SUCCEEDED;}
 model=candidate;ready=true;ClearGrid();
 if(!Render()){Status(problem,true);return INIT_FAILED;}
 Status(offsetsDirty?"Datas alteradas. Revise entradas e clique Confirmar fusos A/B/C.":OffsetsHistoricosConfirmados?"Arraste A/B17 e C9. Exporte para transferir.":"Proposta inicial. Ajuste pontos e confirme offsets antes de exportar.",offsetsDirty);
 return INIT_SUCCEEDED;
}
void OnDeinit(const int reason) {
 ready=false;
 if(reason==REASON_REMOVE&&prefix!=""){ObjectsDeleteAll(0,prefix);ChartRedraw();}
 // On parameter changes, chart close, period change and compilation, preserve
 // exact wire state in hidden chart object. Explicit remove deletes only this ID.
}
int OnCalculate(const int rates_total,const int prev_calculated,const datetime &time[],const double &open[],const double &high[],const double &low[],const double &close[],const long &tick_volume[],const long &volume[],const int &spread[]) {
 if(ready&&rates_total!=prev_calculated) {
  int a=iBarShift(_Symbol,_Period,ta,true),b=iBarShift(_Symbol,_Period,tb,true),c=iBarShift(_Symbol,_Period,tc,true);
  if(a<0||b<0||c<0||a-b!=model.ab||a-c!=model.ac){ready=false;ClearGrid();Status("Historico mudou: exibicao suspensa. Recarregue e valide a origem.",true);}
  else {ia=a;ib=b;ic=c;if(!Render())Status(problem,true);}
 }
 return rates_total;
}
void OnChartEvent(const int event,const long &lparam,const double &dparam,const string &sparam) {
 if(busy||!ready)return;
 if(event==CHARTEVENT_OBJECT_CLICK&&sparam==prefix+"confirm"){ObjectSetInteger(0,sparam,OBJPROP_STATE,false);ConfirmOffsets();return;}
 if(event==CHARTEVENT_OBJECT_CLICK&&sparam==prefix+"export"){ObjectSetInteger(0,sparam,OBJPROP_STATE,false);Export();return;}
 if(event==CHARTEVENT_CHART_CHANGE){if(!Render())Status(problem,true);return;}
 if((event==CHARTEVENT_OBJECT_DRAG||event==CHARTEVENT_OBJECT_CHANGE)&&(sparam==prefix+"AB17"||sparam==prefix+"C9")) {
  Model next=model;datetime a=ta,b=tb,c=tc,oldA=ta,oldB=tb,oldC=tc;
  if(sparam==prefix+"AB17"){a=(datetime)ObjectGetInteger(0,sparam,OBJPROP_TIME,0);b=(datetime)ObjectGetInteger(0,sparam,OBJPROP_TIME,1);next.pa=ObjectGetDouble(0,sparam,OBJPROP_PRICE,0);next.pb=ObjectGetDouble(0,sparam,OBJPROP_PRICE,1);}
  else{c=(datetime)ObjectGetInteger(0,sparam,OBJPROP_TIME,0);next.pc=ObjectGetDouble(0,sparam,OBJPROP_PRICE,0);}
  if(!FromLocal(next,a,b,c,true)){FromLocal(model,oldA,oldB,oldC);Render();Status("Arraste recusado: "+problem,true);return;}
  model=next;nativeMode=true;model.src="MT5";model.feed=FeedIdentificador;
  if(ta!=oldA||tb!=oldB||tc!=oldC)offsetsDirty=true;
  Render();Status(offsetsDirty?"Datas alteradas: revise offsets e clique Confirmar fusos A/B/C.":"Malha atualizada; passo fixo 0.125.",offsetsDirty);
 }
}
