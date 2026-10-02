# GENETRIX 1.17.0 — candidato da proteção em 7x e contabilidade

Estado: **CANDIDATE**. Fontes em cópia isolada; sem compilação, EX5, teste demo, integração/publicação ou conta real comprovados. O README histórico do observador continua aplicável ao observador. A instrução humana desta mudança autorizou separadamente o novo Supervisor; ele não transforma o indicador/Observer em executor.

| Componente | Uso | Limite |
|---|---|---|
| JPW_Genetrix_Accountant.mq5 | Gráfico próprio; publicar ledger de ciclos símbolo/direção de toda conta hedging | Não negocia. História/custos sem evidência ficam parciais |
| JPW_Alavancagem_Atual.mq5 | Cockpit/HUD com a sétima métrica e seletor de ciclo; atalho 7 | Só lê; não arma o Supervisor |
| JPW_Genetrix_Supervisor.mq5 | Gráfico próprio, inicialmente OBSERVE; planejar cancelar/fechar | Execução só demo hedging explicitamente armada; real/FIFO/netting bloqueados |
| JPW_Alavancagem_Observer.mq5 | Observação antiga ATR/stops/RaizN | Sem negociação; stores e função preservados |

## Leitura do compensado

Escolher um ciclo exato nos detalhes da sétima métrica; havendo apenas um ele pode ser selecionado automaticamente. `Compensado = Σ(profit+swap+commission+fee dos deals atribuídos) + Σ(profit+swap das posições remanescentes atribuídas)`. `% =100×compensado/saldo atual` na mesma geração de publicação. Dados Historical e ciclos encerrados conservam o saldo e a data da observação; esse percentual não é rotulado como atual. A moeda é a nativa da conta, incluindo USC; dinheiro e contratos não recebem escalas arbitrárias. Floating P/L global existente permanece separado.

Gênese é INFERIDA, pode fechar antes das defesas e não é promovida. O ciclo só fecha após zerar posições, pendentes e execuções conciliadas. Pendente anterior à primeira entrada é provisória e não inicia resultado financeiro. Correções/exclusões têm revisões; replay não duplica. Crédito/aporte/retirada sem vínculo fica fora do ciclo. Custos não atribuídos não viram resultado líquido completo. Resultado positivo não libera RC nem homologa V11.

A tela distingue Current/Partial/Historical/N/A e mostra componentes/cobertura, identificadores dos membros observados (incluindo fechados), geração e data. A lista é paginada e não infere tickets atuais. Publicações antigas sem essa lista mostram membros indisponíveis; cobertura parcial não afirma origem completa. Sem cobertura suficiente o cartão não apresenta um resultado completo. Quando a origem é válida e apenas os custos são parciais, os detalhes podem mostrar o subtotal observado e as lacunas. Origem ou montante inválido deixam também os componentes monetários indisponíveis; não são apresentados como zero. Consulte a referência de cobertura do Accountant e preserve o histórico exportado que a sustenta. Um checkbox ou input não verifica a corretora nem supre documentos ausentes.

## Proteção e armamento demo

`L=nocional bruto aberto/equity atual`; L > 7 sem arredondamento inicia LIFO integral por ms de abertura, ID decrescente em empate. Pendentes entram conjuntamente no cenário de preços planejados/conversões capturadas; orçamento=max(0,7E−N). Cada confirmação gera novo cálculo. Fechar um hedge pode aumentar risco direcional mesmo reduzindo bruto. 7x é proteção adicional, não substitui os tetos menores/V11 ou seu denominador.

Para eventual ensaio, depois de revisão e compilação comprovada:

1. Use conta demo hedging dedicada, permissões corretas e um único Supervisor autorizado; nunca conta operacional.
2. Inicialize com `InpArmDemo=false`; confira o plano e o desafio `Session challenge` mostrado na tela.
3. Nas propriedades da mesma instância, preencha `InpDemoLogin`, `InpDemoServer`, `InpDemoSession` com identidade exata e o desafio exibido; altere explicitamente `InpArmDemo=true`. Essa mudança reinicializa e consome o desafio anterior. `InpMaxDeviationPoints` é declarado; seu padrão0 não presume tolerância de preço.
4. Cada inicialização rotaciona o desafio. Inputs antigos não rearmam o terminal após reinício. Troca de conta desarma e exige reinicialização em observação. Intenção UNKNOWN recuperada é reconciliada antes de permitir outro envio; não apagá-la para rearmar.
5. Cancelamento recusado marca incompleto, não repete automaticamente e ainda pode podar posições em excesso; fechamento da posição mais recente recusado pausa sem pular LIFO. UNKNOWN não faz novo pedido por timeout; parcial completa o residual da mesma intenção.
6. Para parar, `InpArmDemo=false` e conferir pedidos/intenção antes de retirar o gráfico. O armazenamento não substitui o histórico da corretora.

Uma pendente executada durante cancelamento exige conciliação ordem → deals → identificador/volume da posição, com testemunho persistido. Histórico incompleto, mais de 2.048 deals por posição, orçamento de leitura excedido, correções ou reversões sem suporte mantêm UNKNOWN. A ausência do ticket na lista não comprova cancelamento.

Uma única ação permanece em andamento. Ticket/identificador/volume/composição/equity/permissões são conferidos novamente antes do envio. Retorno verdadeiro de OrderSend não é execução. Exclusão de instâncias é local; outros terminais/VPS da conta exigem coordenação externa. Veto prévio universal a celular/manuais/outros EAs não existe; prevenção cancela pendentes conhecidas e reação reduz exposição capturada.

## Validação e rollback

Testes do código efetivo em host são separados de MetaEditor/MT5. Os casos críticos exigem três sessões novas no terminal com fontes/EX5 ligados por hashes, logs/telas e revisão externa à autoria. Compilar apenas uma parte ou obter lucro não aprova o candidato. Guardar todas as tentativas; falha crítica bloqueia aprovação no escopo.

Os novos stores têm namespaces próprios e não migram/apagam os anteriores. Rollback: desarmar, reconciliar pedidos, retirar os novos componentes, preservar bancos/recibos e restaurar somente arquivos previamente comprovados no ambiente isolado. Não sobrescrever fontes/EX5 operacionais nem publicar este candidato.

Dossiê completo, fixtures, suítes locais, manifesto congelado, pareceres e recibos acompanham a entrega de pesquisa; fora do ZIP MT5 quando seu formato não é aceito pelo distribuidor. `PENDING`, `NOT_HOMOLOGATED`, `BLOCKED` e `NOT_RUN` continuam literais.
