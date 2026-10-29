# Hedge Prop Firm — contrato educativo

Fonte: plano humano aprovado27/10/2026 e CHGs PRODUCT/CONTROLS HEDGE-PROP-20261027. Modelos inspirados nas capturas fornecidas da Cortex; não houve acesso ao código autenticado e não se afirma paridade universal.

## Responsabilidade e entradas
Tools→Mesas Proprietárias (`tools-prop-firms`, visão `prop-firms`) antes de MiniGames. Primeiro tópico Hedge Prop Firm. Engine puro em `src/js/40-app/32-prop-firms/01-engine.js`; apresentação separada, scripts clássicos registrados pelo builder existente. Não é novo módulo financeiro. Fica disponível independentemente de Forex.

`JPWHedgeProp.calculate({nominalUSD,feeUSD,payoutPercent,drawdownPercent,targetsPercent,refundUSD,costs})`: números estritos finitos, capital>0, taxa>=0, payout/drawdown em(0,100], 1/2metas>0, reembolso explícito0..taxa. USD sem conversões. Custos opcionais por etapa (passUSD/failUSD), vazios/ausentes pendentes, zero explícito completo. Propriedades do input não são alteradas. Entrada inválida não reapresenta números antigos como resultado atual.

## Fonte matemática aprovada
C é nominal, F taxa, p payout/100, D=C*drawdown/100, Ti=C*meta_i/100, Rreembolso.
L0=F. Por avaliação qi=Lprev/D; Hi=qi*Ti; Li=Lprev+Hi. Na financiada qf=Ln/D; G=(Ln-R)/(p-qf); perdahedge=qf*G; reserva=2*qf*G. Reservas totais=sumHi+reserva; orçamento-base=F+reservas; múltiplo=orçamento/F. Não arredondar intermediários.

Capital nominal reinicia em cada etapa. Lucro de avaliação não é recebimento. Drawdown fixo, sem limite diário/trailing, equivalência monetária hipotética exata. Razões são de resultado/exposição, não lotes executáveis. Reserva extra100% na financiada é convenção do modelo, não margem, solvência nem capital mínimo real. Taxa0⇒razões/metas/reservas0, múltiplo indisponível, sem custo inicial a recuperar. Com taxa>0 e p<=qf não há recuperação positiva finita. Overflow/não representável é indisponível explícito.

Ramos ideais: avaliaçãoi reprova=-Lprev+qiD; avaliaçãopassa=-Li; financiadafalha=-Ln+qfD; financiadasucesso=-Ln+(p-qf)G+R; atingirmeta sem receberpayout/reembolso=-Ln-qfG. O zero ideal é identidade construída sobpremissas, não garantia de aprovação/recebimento/breakevenreal.

## Custos somente como impacto
Custos incrementais reais emUSD por etapa/desfecho; excluir F, reservas, depósitos e despesas já refletidas. Não deslocar barreiras da prop nem ajustar q,G ou reservas. Resultado após custos=ideal−Σcustos do caminho. Ao reprovar, somar passUSD anteriores+failUSD atual; nafinanciada, passUSD avaliações+pass/failUSDfinanciada. Semrecebimento usa trajeto passUSD financiada atémesmoalvo. Somente caminhos comcampoausente/inválido ficampendentes/inválidos. Não somar desfechos alternativos em orçamento agregado.

## Interface e ciclo de vida
Campos vazios inicialmente, exemplo explícito por modo. Modo1C200000,F1200,p80,d7,t10,R1200;modo2d10,t10/5demaisiguais. Reembolsointegral é hipótese, não configuração contratual de FTMO. Rascunhos independentes emRAM, preservados ao navegar; Limpar afeta apenasmodoatual. Sem localStorage, backup, notificações, rede, S, contas, seleção operacional ou escritores. mount/activate/deactivate/disposeForSession descartam somenteRAM nafinalização. Observadores nuncaremontamapósdescarte; novaentradaaceita pode montar. Atualizarresultados não reconstrói campos ouremovefoco/cursor.

## Fontes e condições — consulta27/10/2026
- Referência visual fornecida: https://cortextradings.com/hedge-prop-firm/ . Método explicado com redação própria; nenhuma cópia de código/assets/marca.
- https://ftmo.com/en/forbidden-trading-practices/ : restrição a combinações manipulativas coordenadas/opostas entre contas eprovedores; não afirmar autorização destehedge.
- https://www.thetradingpit.com/general-terms-and-conditions : V5.08.26 §6.8.1 inclui hedgeexternocoordenado comcorretoras. Medidas/revisão/recursos conformecontrato, não pressupor perdaautomática por mera suspeita.
- https://ftmo.com/en/faq/is-the-entry-fee-refunded/ : 2-Step reembolso na primeira solicitação deReward;1-Step/Instantsemreembolso. Não generalizar produto/regra.

Condições podem mudar; fonte/dataficamvisíveis. Simulação não permite executar, contornar regras ou afirmar adequaçãoV11. Custos, gaps, slippage, trajetórias, limitesdiários/trailing, lotmínimo/margem, payout negado e divergências deexecução não são eliminados pelo cálculo.

## Oráculos, entrega e limites
1fase reservas2920.197044, orçamento4120.197044, meta2896.551724;2fases3793.548387/4993.548387/3870.967742. Não derivar expectativas deUIouengine. Contraprovas taxaomitida,refundpresumido,razõesarredondadas,custosduplicados,overflow/desalinhamento.
Testes automatizados, revisão independente e aceite humano são distintos. FULL histórico113 não aprova nova ferramenta. Build oficial, HTTP/offline/file/portátil e gate full com fontes congeladas. Sem novasdependências, dados reais, alterações normativas/financeiras persistidas ouGit/publicação.
