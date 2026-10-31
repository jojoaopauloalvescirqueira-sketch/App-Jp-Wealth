# Hedge didático — evolução de 31/10/2026

O motor financeiro de 27/10 é preservado byte a byte. Redesign altera apresentação e acrescenta acompanhamento independente confirmado; os contratos históricos abaixo continuam fontes matemáticas.

## Apresentação e catálogo

Modos uma fase, duas fases e Instant. Sliders e campos numéricos atualizam a mesma entrada em RAM, sem arredondar intermediários nem substituir o nó ativo. O campo aceita precisão superior ao passo sugerido do slider. Instantes não passam pelo motor de avaliação: mostram fluxo conta→regras→elegibilidade→Reward e ausência de hedge de aprovação, sem prometer ausência de risco.

Fluxo visual separa taxa, reserva dos hedges e orçamento total. Resultados de cenário são teóricos e condicionados ao recebimento; razões de exposição não são lotes executáveis. Custos continuam impactos separados, sem recalcular tamanho do hedge.

Catálogo factual consultado em 31/10/2026, sem preenchimento automático, homologação ou recomendação operacional. FTMO: https://ftmo.com/en/comparison-table/ e https://ftmo.com/en/trading-objectives/ . TTP: https://support.thetradingpit.com/en/articles/835084-cfd-prime-rules , https://support.thetradingpit.com/en/articles/835083-cfd-prime-how-it-works , https://support.thetradingpit.com/en/articles/835093-cfd-prime-rewards e https://support.thetradingpit.com/en/articles/835380-cfd-instant-rules . Valores variáveis por oferta/conta permanecem pendentes. Restrições a hedge coordenado ficam visíveis; não esconder a condição no “i”. Os limites fixos do laboratório não reproduzem regras diárias/trailing das mesas.

## Guia confirmado, separado dos fatos financeiros

`JPWHedgeGuide` é exportado antes da UI no mesmo script clássico `02-ui.js`, preservando a ordem dos 127 scripts. API: `KEY`, `validate(raw)` puro (retorna clone ou lança), `inspect(raw)`, `read()`, `write(document,{expectedRaw,replacePlan,signal})` assíncrono (Promise), `stages(mode)`.

Chave `jpwealth_hedge_guide_v1`, schema1, até 64 KiB e 500 marcos. Documento: `{schemaVersion,revision,plan:{mode,catalogId,catalogVersion,input},stage,confirmedAt,updatedAt,milestones:[{stage,confirmedAt}]}`. `mode` é one/two/instant; catálogo custom/ftmo/ttp por modo e versão2026-10-31. Snapshots do motor incluem valores finitos explícitos e custos `number|null`; null não vira zero. Instant guarda apenas nominalUSD/feeUSD, sem metas/exposição fictícias. Cada etapa é confirmação declarada pelo usuário, não verificação da mesa ou negociação.

Somente botões explícitos escrevem. Leitura inválida/futura não é substituída. Escrita compara o raw esperado e confere releitura: confirmado, recusado, conflito ou desconhecido. Desconhecido bloqueia retry até conferência. Histórico da mesma configuração é append-only; o snapshot inteiro de parâmetros/catálogo é imutável fora de substituição explicitamente confirmada. A escrita usa o mesmo Web Lock `jpwealth_state_writer_v1` de importação/finalização (`sessionAcquireWriteLock`), com expectedRaw e releitura dentro da seção serializada. Sem Web Locks seguro a gravação é recusada e a UI orienta usar o inicializador local; não existe fallback best-effort anunciado como atômico. UI aguarda o resultado, expõe busy, impede duplo envio e cancela requisição ainda enfileirada ao descartar/finalizar seu controlador. A coordenação é entre escritores cooperantes da mesma origem, não CAS universal de localStorage. Substituir plano/histórico exige confirmação própria e gravação verificada; trocar modo não substitui nada. Restabelecer campos de um plano salvo é gesto explícito; recarga apenas mostra o guia confirmado. Não cria fatos no ledger, ordens, LIFO, lotes, cadastro ou permissões.

Integração Backup Completo workspace3 reutiliza `validate(raw)` na frente N2 de backup. Ausência da família em backups antigos preserva destino. Até a integração combinada, o store existe separadamente e não autoriza dizer cobertura integral.

Testes permanentes `hedge_guide_store_test.js` e `hedge_redesign_browser_test.py`, encadeados pelas entradas de Hedge já existentes. FULL/revisão independente e aceite humano são etapas separadas. Contrato/autoridade: `BRIEF-HEDGE-REDESIGN-20261031.md`; controles em CHG próprio.

---

## Histórico preservado

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
