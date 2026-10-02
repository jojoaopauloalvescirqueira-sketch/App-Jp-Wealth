#property strict
#property version "1.140"
#property description "JPW Signal Copy: somente fixtures sintéticas, sem conta/ordens/arquivos reais."
#include <JPWealth/JPW_SignalCopy_Core.mqh>

int g_signal_pass=0,g_signal_fail=0;
void SignalAssert(const bool condition,const string name)
  {
   if(condition) g_signal_pass++;
   else { g_signal_fail++; Print("FAIL: ",name); }
  }
bool SignalNear(const double a,const double b)
  { return(MathIsValidNumber(a) && MathIsValidNumber(b) && MathAbs(a-b)<1e-10); }

void SignalRow(JPWSignalRow &row,const int kind,const ulong ticket,
                const string symbol,const int side,const double volume,
                const long opened)
  {
   row.kind=kind; row.ticket=ticket; row.identifier=(kind==JPW_SIGNAL_POSITION ? (long)ticket-1 : 0);
   row.symbol=symbol; row.side=side; row.volume=volume; row.initial_volume=volume;
   row.opened_msc=opened; row.updated_msc=opened; row.order_state=0; row.expiration=0;
   row.order_type=(kind==JPW_SIGNAL_POSITION ? -1 :
                   (side==POSITION_TYPE_BUY ? ORDER_TYPE_BUY_LIMIT : ORDER_TYPE_SELL_LIMIT));
   row.entry=100.0; row.sl=(side==POSITION_TYPE_BUY ? 98.0 : 102.0);
   row.tp=0.0; row.stop_limit=0.0; row.digits=2; row.volume_digits=2;
  }

void SignalFixture(JPWSignalCapture &capture,JPWSignalRow &rows[],
                    JPWSignalMember &members[],JPWSignalMetrics &metrics)
  {
   capture.account.login=991114; capture.account.server="SYNTHETIC.SERVER";
   capture.account.currency="USD"; capture.context="synthetic-opaque-context";
   capture.digest="synthetic-coherent-digest"; capture.margin_mode=ACCOUNT_MARGIN_MODE_RETAIL_HEDGING;
   capture.balance=10000.0; capture.equity=9800.0; capture.profit=-200.0; capture.credit=0.0;
   capture.observed_utc=(long)D'2026.10.01 12:00:01'; capture.accepted_ms=4000;
   capture.reference_closed=false; capture.reference_identifier=0;
   ArrayResize(rows,2);
   SignalRow(rows[0],JPW_SIGNAL_POSITION,9007199254740991,"SYNTH.EURUSD",POSITION_TYPE_BUY,1.0,
             ((long)D'2026.09.30 08:00:00')*1000);
   SignalRow(rows[1],JPW_SIGNAL_POSITION,999002,"SYNTH.EURUSD",POSITION_TYPE_BUY,0.5,
             ((long)D'2026.09.30 09:00:00')*1000);
   rows[0].tp=104.0;
   string reason="";
   JPWSignalSuggestMembers(rows,0,0,false,members,reason);
   for(int i=0;i<ArraySize(members);i++) members[i].origin=JPW_SIGNAL_CONFIRMED;
   JPWSignalClearMetrics(metrics);
   metrics.leverage_valid=true; metrics.scenario_valid=true; metrics.floating_valid=true;
   metrics.root_valid=true; metrics.stop_valid=true;
   metrics.leverage=2.75; metrics.scenario_leverage=3.20; metrics.floating_percent=-2.0;
   metrics.factor=1.5; metrics.n_1w=30; metrics.n_2w=60; metrics.atr=0.40;
   metrics.bid=99.0; metrics.ask=101.0; metrics.point=0.01; metrics.tick_size=0.01;
   metrics.quote_time_msc=((long)D'2026.10.01 12:00:00')*1000;
   metrics.atr_bar_time=(long)D'2026.10.01 04:00:00';
   metrics.leverage_quality=2; metrics.root_quality=1; metrics.quote_quality=2; metrics.floating_quality=2;
   metrics.leverage_reason=""; metrics.root_reason="Calendário semanal projetado";
   metrics.stop_reason=""; metrics.floating_reason="";
   double distance=0.0;
   JPWRaizNCalculate(100.0,metrics.atr,30,metrics.factor,distance,metrics.root_1w);
   JPWRaizNCalculate(100.0,metrics.atr,60,metrics.factor,distance,metrics.root_2w);
  }

void SignalVirtualTests()
  {
   JPWSignalCapture capture; JPWSignalRow rows[]; JPWSignalMember members[];
   JPWSignalMetrics metrics; JPWPosition positions[]; string reason="";
   SignalFixture(capture,rows,members,metrics);
   SignalAssert(JPWSignalVirtualPositions(rows,0,capture.margin_mode,positions,reason) &&
                 ArraySize(positions)==2 && SignalNear(positions[0].volume,1.0),
                 "posição selecionada não duplica exposição");
   ArrayResize(rows,5);
   SignalRow(rows[2],JPW_SIGNAL_PENDING,999003,"SYNTH.EURUSD",POSITION_TYPE_BUY,0.4,3000);
   rows[2].initial_volume=1.0;
   SignalRow(rows[3],JPW_SIGNAL_PENDING,999004,"SYNTH.EURUSD",POSITION_TYPE_BUY,8.0,4000);
   SignalRow(rows[4],JPW_SIGNAL_POSITION,999005,"SYNTH.USDJPY",POSITION_TYPE_SELL,0.2,5000);
   SignalAssert(JPWSignalVirtualPositions(rows,2,capture.margin_mode,positions,reason) &&
                 ArraySize(positions)==4 && SignalNear(positions[3].volume,0.4) &&
                 positions[2].symbol=="SYNTH.USDJPY",
                 "hedging só restante selecionado; demais posições da conta preservadas");
   SignalAssert(SignalNear(rows[2].volume,0.4) && SignalNear(rows[2].initial_volume,1.0) &&
                 SignalNear(rows[3].volume,8.0),"função pura preserva catálogo e outra pendente");
   rows[2].volume=1.1;
   SignalAssert(!JPWSignalVirtualPositions(rows,2,capture.margin_mode,positions,reason) &&
                 ArraySize(positions)==0,"volume corrente maior que inicial recusa cenário");
   rows[2].volume=0.4; rows[2].order_type=ORDER_TYPE_BUY_STOP_LIMIT;
   SignalAssert(!JPWSignalVirtualPositions(rows,2,capture.margin_mode,positions,reason),
                 "stop-limit não vira cenário padrão silencioso");
   SignalFixture(capture,rows,members,metrics);
   ArrayResize(rows,2);
   SignalRow(rows[1],JPW_SIGNAL_PENDING,999003,"SYNTH.EURUSD",POSITION_TYPE_SELL,0.4,3000);
   capture.margin_mode=ACCOUNT_MARGIN_MODE_RETAIL_NETTING;
   SignalAssert(JPWSignalVirtualPositions(rows,1,capture.margin_mode,positions,reason) &&
                 ArraySize(positions)==1 && positions[0].direction==POSITION_TYPE_BUY &&
                 SignalNear(positions[0].volume,0.6),"netting redução por pendente oposta");
   rows[1].volume=1.0; rows[1].initial_volume=1.0;
   SignalAssert(JPWSignalVirtualPositions(rows,1,capture.margin_mode,positions,reason) &&
                 ArraySize(positions)==0,"netting zeragem não cria zero artificial aberto");
   rows[1].volume=1.6; rows[1].initial_volume=1.6;
   SignalAssert(JPWSignalVirtualPositions(rows,1,capture.margin_mode,positions,reason) &&
                 ArraySize(positions)==1 && positions[0].direction==POSITION_TYPE_SELL &&
                 SignalNear(positions[0].volume,0.6),"netting reversão conserva volume líquido");
   rows[1].side=POSITION_TYPE_BUY; rows[1].order_type=ORDER_TYPE_BUY_LIMIT;
   SignalAssert(JPWSignalVirtualPositions(rows,1,capture.margin_mode,positions,reason) &&
                 SignalNear(positions[0].volume,2.6),"netting adição na mesma direção");
   capture.margin_mode=ACCOUNT_MARGIN_MODE_EXCHANGE;
   SignalAssert(!JPWSignalVirtualPositions(rows,1,capture.margin_mode,positions,reason),
                 "bolsa não suportada recusa cenário pendente");
   SignalAssert(!JPWSignalVirtualPositions(rows,-1,capture.margin_mode,positions,reason),
                 "seleção fora do catálogo recusada");
   capture.margin_mode=ACCOUNT_MARGIN_MODE_RETAIL_HEDGING;
   rows[1]=rows[0];
   SignalAssert(!JPWSignalVirtualPositions(rows,0,capture.margin_mode,positions,reason),
                 "ticket duplicado de posição recusa composição");
   rows[1].ticket++; // distinct ticket but same position identity
   SignalAssert(!JPWSignalVirtualPositions(rows,0,capture.margin_mode,positions,reason),
                 "identificador duplicado recusa composição");
  }

void SignalMembershipTests()
  {
   JPWSignalCapture capture; JPWSignalRow rows[]; JPWSignalMember members[];
   JPWSignalMetrics metrics; string reason="";
   SignalFixture(capture,rows,members,metrics);
   ArrayResize(rows,5);
   SignalRow(rows[2],JPW_SIGNAL_POSITION,999003,"SYNTH.EURUSD",POSITION_TYPE_SELL,0.3,3000);
   SignalRow(rows[3],JPW_SIGNAL_POSITION,999004,"SYNTH.EURUSD.m",POSITION_TYPE_BUY,0.3,4000);
   SignalRow(rows[4],JPW_SIGNAL_PENDING,999005,"SYNTH.EURUSD",POSITION_TYPE_BUY,0.2,5000);
   SignalAssert(JPWSignalSuggestMembers(rows,0,0,false,members,reason) && ArraySize(members)==3,
                 "grupo exige símbolo exato e direção");
   int genesis=0,pending_included=0;
   for(int i=0;i<ArraySize(members);i++)
     { if(members[i].role==1) genesis++; if(members[i].row==4 && members[i].included) pending_included++; }
   SignalAssert(genesis==1 && pending_included==0,"outras pendentes não entram na sugestão");
   SignalAssert(JPWSignalSuggestMembers(rows,4,rows[1].identifier,false,members,reason),
                 "referência explícita estável mesmo quando não é a mais antiga");
   for(int i=0;i<ArraySize(members);i++)
      if(members[i].role==1) SignalAssert(members[i].row==1 && members[i].origin==JPW_SIGNAL_REFERENCE,
                                          "referência preserva seu identificador");
   SignalAssert(JPWSignalSuggestMembers(rows,0,rows[0].identifier,true,members,reason),
                 "referência encerrada pode mostrar grupo sem promover sucessora");
   genesis=0; for(int i=0;i<ArraySize(members);i++) if(members[i].role>0) genesis++;
   SignalAssert(genesis==0 && StringFind(reason,"encerrada")>=0,"encerramento deixa papéis para conferência");
   rows[1].opened_msc=rows[0].opened_msc;
   JPWSignalSuggestMembers(rows,0,0,false,members,reason);
   genesis=0; for(int i=0;i<ArraySize(members);i++) if(members[i].role>0) genesis++;
   SignalAssert(genesis==0 && StringFind(reason,"empate")>=0,"empate não escolhe pelo ticket");
   rows[1].opened_msc=rows[0].opened_msc+1000;
   JPWSignalSuggestMembers(rows,0,-1,false,members,reason);
   genesis=0; for(int i=0;i<ArraySize(members);i++) if(members[i].role>0) genesis++;
   SignalAssert(genesis==0 && StringFind(reason,"indisponível")>=0,
                 "falha de leitura da referência não vira inferência silenciosa");
   rows[1].opened_msc=0;
   JPWSignalSuggestMembers(rows,0,0,false,members,reason);
   genesis=0; for(int i=0;i<ArraySize(members);i++) if(members[i].role>0) genesis++;
   SignalAssert(genesis==0,"horário ausente não certifica antiguidade");
   JPWSignalSuggestMembers(rows,0,888888,false,members,reason);
   SignalAssert(StringFind(reason,"não presente")>=0,"referência ausente não é substituída");
   ArrayResize(rows,1); SignalRow(rows[0],JPW_SIGNAL_PENDING,999099,"SYNTH.ONLY",POSITION_TYPE_BUY,0.2,1000);
   SignalAssert(JPWSignalSuggestMembers(rows,0,0,false,members,reason) && members[0].role==0,
                 "pendente isolada não vira Gênese executada");
  }

void SignalSharedTicketGrossTests()
  {
   JPWSignalRow rows[]; JPWPosition positions[]; string reason="";
   ArrayResize(rows,3);
   SignalRow(rows[0],JPW_SIGNAL_POSITION,1001,"SYNTH.NZDUSD",POSITION_TYPE_BUY,0.1,1000);
   SignalRow(rows[1],JPW_SIGNAL_POSITION,1002,"SYNTH.EURUSD",POSITION_TYPE_SELL,0.2,2000);
   SignalRow(rows[2],JPW_SIGNAL_PENDING,1001,"SYNTH.NZDUSD",POSITION_TYPE_BUY,0.05,3000);
   rows[2].initial_volume=0.15;
   SignalAssert(JPWSignalVirtualPositions(rows,2,ACCOUNT_MARGIN_MODE_RETAIL_HEDGING,positions,reason) &&
                 ArraySize(positions)==3 && positions[2].ticket>0 &&
                 positions[2].ticket!=positions[0].ticket && positions[2].ticket!=positions[1].ticket,
                 "parcial com ticket compartilhado recebe identidade sintética livre");
   SignalAssert(rows[0].ticket==1001 && rows[2].ticket==1001 &&
                 SignalNear(rows[2].volume,0.05) && SignalNear(rows[2].initial_volume,0.15),
                 "ticket real da posição e da pendente preservados no catálogo");
   JPWInstrument instruments[]; JPWQuote quotes[]; double scales[]; JPWRoute routes[];
   ArrayResize(instruments,3); ArrayResize(scales,3); ArrayResize(quotes,2);
   for(int i=0;i<3;i++)
     {
      instruments[i].symbol=positions[i].symbol; instruments[i].calc_mode=SYMBOL_CALC_MODE_FOREX;
      instruments[i].base=(positions[i].symbol=="SYNTH.NZDUSD" ? "NZD" : "EUR");
      instruments[i].profit="USD"; instruments[i].contract_size=100000.0;
      instruments[i].underlying_verified=false; scales[i]=1.0;
     }
   const long now=((long)D'2026.10.01 12:00:00')*1000;
   quotes[0].symbol="SYNTH.NZDUSD"; quotes[0].base="NZD"; quotes[0].profit="USD";
   quotes[0].bid=0.5999; quotes[0].ask=0.6001; quotes[0].time_msc=now; quotes[0].conversion_pair=true;
   quotes[1].symbol="SYNTH.EURUSD"; quotes[1].base="EUR"; quotes[1].profit="USD";
   quotes[1].bid=1.0999; quotes[1].ask=1.1001; quotes[1].time_msc=now; quotes[1].conversion_pair=true;
   double gross=0.0,leverage=0.0; bool estimated=false; long oldest=0;
   SignalAssert(JPWGrossReading(positions,instruments,quotes,"USD",now,30,true,true,
                                scales,routes,gross,estimated,oldest)==JPW_OK &&
                 SignalNear(gross,31000.0) &&
                 JPWLeverage(gross,900.0,leverage)==JPW_OK &&
                 SignalNear(leverage,31000.0/900.0),
                 "ticket parcial compartilhado chega ao núcleo nocional real e equity congelado");
   rows[0].ticket=1; rows[1].ticket=2;
   SignalAssert(JPWSignalVirtualPositions(rows,2,ACCOUNT_MARGIN_MODE_RETAIL_HEDGING,positions,reason) &&
                 positions[2].ticket==3,"busca sintética pula todas as identidades positivas ocupadas");
  }

void SignalGateAndMessageTests()
  {
   JPWSignalCapture capture; JPWSignalRow rows[]; JPWSignalMember members[];
   JPWSignalMetrics metrics; string reason="",message="";
   SignalFixture(capture,rows,members,metrics);
   SignalAssert(JPWSignalCanPrepare(capture,rows,0,members,metrics,reason),"amostra completa aceita Estimated explícito");
   SignalAssert(JPWSignalMessage(capture,rows,0,members,metrics,message,reason),"template produzido pelo núcleo real");
   const string golden=
      "New Order | JP Wealth Model\n"
      "Status: Posição aberta\n"
      "Ordem: Gênese · conferida pelo usuário\n"
      "Ticket da posição: 9007199254740991\n"
      "Ativo: SYNTH.EURUSD\n"
      "Tipo: Posição aberta · Buy\n"
      "Volume remanescente: 1.00 lote\n"
      "Entrada: 100.00\n"
      "Stop Loss: 98.00\n"
      "Take Profit: 104.00\n"
      "\n"
      "---\n"
      "Estrutura da operação — SYNTH.EURUSD · Buy\n"
      "🔹 Gênese: 1.00 lote · 9007199254740991 · Ativa\n"
      "🔹 Defesa 1: 0.50 lote · 999002 · Ativa\n"
      "\n"
      "Exposição aberta da operação: 1.50 lote\n"
      "Alavancagem atual da conta: 2.75x · Current\n"
      "\n"
      "---\n"
      "Risk Management\n"
      "Entrada → SL: 2.00% · SL à frente\n"
      "Mercado → SL: 1.01% · SL à frente · Current\n"
      "Raiz N 1W: 3.29% · F 1.5 · Estimated\n"
      "Raiz N 2W: 4.65% · F 1.5 · Estimated\n"
      "Flutuante da conta / saldo: -2.00% · Current\n"
      "\n"
      "Leitura: 2026.10.01 12:00:01 UTC (relógio do computador)\n"
      "Cotação: 2026.10.01 12:00:00 (servidor MT5; Bid para distância ao SL)\n"
      "Barra ATR(55,H4): 2026.10.01 04:00:00 (servidor MT5)\n"
      "Abertura do item: 2026.09.30 08:00:00 (servidor MT5)\n"
      "Identificador da posição: 9007199254740990\n"
      "N 1W/2W: 30 / 60\n"
      "Moeda da conta: USD (percentuais na mesma unidade; USC não escala preços)\n"
      "Estado Raiz N: Calendário semanal projetado\n"
      "Conferência transitória; não certifica tese, Gênese ou Defesas no Estatuto.\n"
      "Raiz N é diagnóstico do mercado atual; não é probabilidade remanescente do SL nem autorização de entrada.\n"
      "SL reached/passed indica nível geométrico, não execução. Não há envio ou negociação automática.";
   SignalAssert(message==golden,"golden Unicode, campos e quebras reais, ticket completo");
   rows[0].tp=0.0; JPWSignalMessage(capture,rows,0,members,metrics,message,reason);
   SignalAssert(StringFind(message,"Take Profit: Sem TP\n")>=0,"TP é opcional com ausência explícita");
   rows[0].sl=101.5;
   SignalAssert(JPWSignalMessage(capture,rows,0,members,metrics,message,reason) &&
                 StringFind(message,"1.50% · SL protege resultado")>=0 &&
                 StringFind(message,"SL passed")>=0,"SL protegido e ultrapassado preserva estados distintos");
   rows[0].sl=metrics.bid;
   JPWSignalMessage(capture,rows,0,members,metrics,message,reason);
   SignalAssert(StringFind(message,"0.00% · SL reached")>=0,"nível alcançado não afirma execução");
   rows[0].sl=0.0; message="old";
   SignalAssert(!JPWSignalMessage(capture,rows,0,members,metrics,message,reason) && message=="",
                 "SL ausente bloqueia e limpa mensagem anterior");
   SignalFixture(capture,rows,members,metrics);
   metrics.leverage_valid=false;
   SignalAssert(!JPWSignalCanPrepare(capture,rows,0,members,metrics,reason),"alavancagem obrigatória sem fallback");
   SignalFixture(capture,rows,members,metrics); metrics.root_quality=0;
   SignalAssert(!JPWSignalCanPrepare(capture,rows,0,members,metrics,reason),"Root N N/A bloqueia");
   SignalFixture(capture,rows,members,metrics); metrics.floating_valid=false;
   SignalAssert(!JPWSignalCanPrepare(capture,rows,0,members,metrics,reason),"flutuante obrigatório bloqueia");
   SignalFixture(capture,rows,members,metrics); metrics.stop_valid=false;
   SignalAssert(!JPWSignalCanPrepare(capture,rows,0,members,metrics,reason),"cotação incompleta bloqueia");
   SignalFixture(capture,rows,members,metrics); metrics.root_1w+=1.0;
   SignalAssert(!JPWSignalCanPrepare(capture,rows,0,members,metrics,reason),"Root desconexo da amostra recusado");
   SignalFixture(capture,rows,members,metrics); metrics.floating_percent=-4.0;
   SignalAssert(!JPWSignalCanPrepare(capture,rows,0,members,metrics,reason),"flutuante desconexo da conta recusado");
   SignalFixture(capture,rows,members,metrics); metrics.bid=102.0;
   SignalAssert(!JPWSignalCanPrepare(capture,rows,0,members,metrics,reason),"spread invertido recusado");
   SignalFixture(capture,rows,members,metrics); metrics.leverage=MathSqrt(-1.0);
   SignalAssert(!JPWSignalCanPrepare(capture,rows,0,members,metrics,reason),"NaN não passa flag valid");
   SignalFixture(capture,rows,members,metrics); members[0].origin=JPW_SIGNAL_INFERRED;
   SignalAssert(!JPWSignalCanPrepare(capture,rows,0,members,metrics,reason),"inferência exige conferência explícita");
   SignalFixture(capture,rows,members,metrics); members[1].role=1;
   SignalAssert(!JPWSignalCanPrepare(capture,rows,0,members,metrics,reason),"papéis duplicados recusados");
   SignalFixture(capture,rows,members,metrics); rows[1].symbol="SYNTH.EURUSD.m";
   SignalAssert(!JPWSignalCanPrepare(capture,rows,0,members,metrics,reason),"membro de outro instrumento recusado");
   SignalFixture(capture,rows,members,metrics); members[0].included=false;
   SignalAssert(!JPWSignalCanPrepare(capture,rows,0,members,metrics,reason),"selecionado excluído não prepara");
   SignalFixture(capture,rows,members,metrics); capture.account.currency="USC";
   capture.balance*=100.0; capture.equity*=100.0; capture.profit*=100.0;
   SignalAssert(JPWSignalMessage(capture,rows,0,members,metrics,message,reason) &&
                 StringFind(message,"Flutuante da conta / saldo: -2.00%")>=0 &&
                 StringFind(message,"Stop Loss: 98.00")>=0,
                 "USC cancela unidades financeiras e não altera preços");
   capture.reference_closed=true; members[0].role=2; members[1].role=3;
   SignalAssert(JPWSignalMessage(capture,rows,0,members,metrics,message,reason) &&
                 StringFind(message,"Gênese registrada encerrada; nenhuma sucessora")>=0,
                 "Defesas conferidas sobrevivem sem promoção da Gênese fechada");
   SignalFixture(capture,rows,members,metrics);
   capture.reference_identifier=555000; members[0].role=2; members[1].role=3;
   SignalAssert(JPWSignalMessage(capture,rows,0,members,metrics,message,reason) &&
                 StringFind(message,"fora dos itens incluídos")>=0,"Gênese fora do grupo permanece explícita");
   SignalFixture(capture,rows,members,metrics); ArrayResize(rows,1); ArrayResize(members,1);
   capture.margin_mode=ACCOUNT_MARGIN_MODE_RETAIL_NETTING; members[0].role=0;
   SignalAssert(JPWSignalMessage(capture,rows,0,members,metrics,message,reason) &&
                 StringFind(message,"Posição agregada — netting")>=0 &&
                 StringFind(message,"Ordem: Gênese")<0,"netting não fabrica Gênese/Defesas");
   SignalFixture(capture,rows,members,metrics);
   SignalRow(rows[1],JPW_SIGNAL_PENDING,999003,"SYNTH.EURUSD",POSITION_TYPE_BUY,0.4,
             ((long)D'2026.10.01 11:00:00')*1000);
   rows[1].initial_volume=1.0; rows[1].entry=97.0; rows[1].sl=95.0;
   JPWSignalSuggestMembers(rows,1,0,false,members,reason);
   for(int i=0;i<ArraySize(members);i++) members[i].origin=JPW_SIGNAL_CONFIRMED;
   SignalAssert(JPWSignalMessage(capture,rows,1,members,metrics,message,reason) &&
                 StringFind(message,"Volume remanescente: 0.40")>=0 &&
                 StringFind(message,"Alavancagem projetada após somente esta pendente: 3.20x")>=0 &&
                 StringFind(message,"preços e equity congelados")>=0,
                 "pendente parcial mostra condicional separado da exposição atual");
   const string golden_pending=
      "Pending Order | JP Wealth Model\n"
      "Status: Ordem pendente\n"
      "Ordem: Defesa 1 · conferida pelo usuário\n"
      "Ticket da ordem: 999003\n"
      "Ativo: SYNTH.EURUSD\n"
      "Tipo: BUY LIMIT\n"
      "Volume remanescente: 0.40 lote\n"
      "Entrada planejada: 97.00\n"
      "Stop Loss: 95.00\n"
      "Take Profit: Sem TP\n"
      "\n"
      "---\n"
      "Estrutura da operação — SYNTH.EURUSD · Buy\n"
      "🔹 Gênese: 1.00 lote · 9007199254740991 · Ativa\n"
      "\n"
      "Pendentes incluídas:\n"
      "🔹 Defesa 1: 0.40 lote · 999003 · Pendente planejada\n"
      "\n"
      "Exposição aberta da operação: 1.00 lote\n"
      "Alavancagem atual da conta: 2.75x · Current\n"
      "Exposição hipotética após somente esta pendente: 1.40 lote · Buy\n"
      "Alavancagem projetada após somente esta pendente: 3.20x · Current\n"
      "\n"
      "---\n"
      "Risk Management\n"
      "Entrada → SL: 2.06% · SL à frente\n"
      "Mercado → SL: 4.04% · SL à frente · Current\n"
      "Raiz N 1W: 3.29% · F 1.5 · Estimated\n"
      "Raiz N 2W: 4.65% · F 1.5 · Estimated\n"
      "Flutuante da conta / saldo: -2.00% · Current\n"
      "\n"
      "Leitura: 2026.10.01 12:00:01 UTC (relógio do computador)\n"
      "Cotação: 2026.10.01 12:00:00 (servidor MT5; Bid para distância ao SL)\n"
      "Barra ATR(55,H4): 2026.10.01 04:00:00 (servidor MT5)\n"
      "Abertura do item: 2026.10.01 11:00:00 (servidor MT5)\n"
      "N 1W/2W: 30 / 60\n"
      "Moeda da conta: USD (percentuais na mesma unidade; USC não escala preços)\n"
      "Cenário hipotético: apenas o volume remanescente selecionado; preços e equity congelados; a alavancagem usa a exposição bruta de toda a conta após somente esta pendente; lotes referem-se aos itens incluídos da operação.\n"
      "Estado Raiz N: Calendário semanal projetado\n"
      "Conferência transitória; não certifica tese, Gênese ou Defesas no Estatuto.\n"
      "Raiz N é diagnóstico do mercado atual; não é probabilidade remanescente do SL nem autorização de entrada.\n"
      "SL reached/passed indica nível geométrico, não execução. Não há envio ou negociação automática.";
   SignalAssert(message==golden_pending,"golden pendente literal, exposição aberta e hipótese separadas");
   metrics.scenario_valid=false;
   SignalAssert(!JPWSignalMessage(capture,rows,1,members,metrics,message,reason) && message=="",
                 "cenário pendente obrigatório recusa subtotal atual");
   SignalFixture(capture,rows,members,metrics); capture.reference_identifier=-1;
   SignalAssert(JPWSignalMessage(capture,rows,0,members,metrics,message,reason) &&
                 StringFind(message,"Referência registrada indisponível")>=0,
                 "conferência manual não alega recuperar referência indisponível");
   SignalFixture(capture,rows,members,metrics); capture.balance=0.0;
   SignalAssert(!JPWSignalCanPrepare(capture,rows,0,members,metrics,reason),"balance inválido bloqueia");
   SignalFixture(capture,rows,members,metrics); capture.equity=-1.0;
   SignalAssert(!JPWSignalCanPrepare(capture,rows,0,members,metrics,reason),"equity não positivo bloqueia alavancagem");
   SignalFixture(capture,rows,members,metrics); capture.digest="";
   SignalAssert(!JPWSignalCanPrepare(capture,rows,0,members,metrics,reason),"identidade da coleta ausente bloqueia");
   SignalFixture(capture,rows,members,metrics); rows[0].tp=MathSqrt(-1.0);
   SignalAssert(!JPWSignalCanPrepare(capture,rows,0,members,metrics,reason),"TP inválido não vira ausência opcional");
   SignalFixture(capture,rows,members,metrics); rows[0].entry=1e-300; rows[0].sl=1e300;
   SignalAssert(!JPWSignalCanPrepare(capture,rows,0,members,metrics,reason),"distância não representável não vira inf no texto");
   SignalFixture(capture,rows,members,metrics); metrics.factor=1.8;
   double distance=0.0;
   JPWRaizNCalculate(100.0,metrics.atr,30,metrics.factor,distance,metrics.root_1w);
   JPWRaizNCalculate(100.0,metrics.atr,60,metrics.factor,distance,metrics.root_2w);
   SignalAssert(JPWSignalMessage(capture,rows,0,members,metrics,message,reason) &&
                 StringFind(message,"F 1.8")>=0,"F alternativo usa a mesma fórmula validada");
   SignalFixture(capture,rows,members,metrics);
   rows[0].side=POSITION_TYPE_SELL; rows[1].side=POSITION_TYPE_SELL;
   rows[0].sl=102.0; rows[1].sl=102.0;
   SignalAssert(JPWSignalMessage(capture,rows,0,members,metrics,message,reason) &&
                 StringFind(message,"Mercado → SL: 0.99%")>=0 &&
                 StringFind(message,"Ask para distância ao SL")>=0,
                 "venda usa Ask, não Bid nem midpoint para SL");
   SignalFixture(capture,rows,members,metrics); metrics.leverage=0.0; metrics.floating_percent=0.0;
   capture.profit=0.0;
   SignalAssert(JPWSignalCanPrepare(capture,rows,0,members,metrics,reason),
                 "zero financeiro válido não é tratado como ausência por valor");
   SignalAssert(JPWSignalPercent(0.001,true)=="+<0.01%" &&
                 JPWSignalPercent(-0.001)=="−<0.01%" && JPWSignalPercent(0.0)=="0.00%",
                 "valores pequenos não viram falso zero");
   SignalAssert(JPWSignalQualityText(2)=="Current" && JPWSignalQualityText(1)=="Estimated" &&
                 JPWSignalQualityText(0)=="N/A","qualidade tipada não analisa mensagens");
  }

void OnStart()
  {
   SignalVirtualTests(); SignalMembershipTests(); SignalSharedTicketGrossTests(); SignalGateAndMessageTests();
   Print("JPW_SIGNAL_COPY: ",g_signal_pass," PASS / ",g_signal_fail," FAIL");
  }
