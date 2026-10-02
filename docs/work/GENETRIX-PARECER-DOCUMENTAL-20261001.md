# GENETRIX — Parecer documental de integração

Data: 2026-10-01. Escopo: pesquisa, manual do pacote, protocolo de demo/rollback e CHG do candidato isolado em `/private/tmp/jpw-genetrix-risk-ledger-20261001`.

Esta é uma revisão documental de coerência e autoridade, com confronto dirigido das passagens relevantes com fontes locais. Não constitui homologação V11, aprovação operacional, aprovação independente da UI de minha autoria, execução dos casos, compilação MQL nativa, inspeção visual MT5 ou autorização de negociação. Não foram alterados os documentos revisados nem o código de produção.

## Resultado documental

Os três achados materiais comunicados durante a revisão foram corrigidos nos documentos consultados. Não identifiquei outro conflito material aberto nas passagens examinadas. Esse resultado se limita à documentação e aos bytes registrados abaixo; não atribui PASS ao produto, à demo ou à conta real.

| Achado e localização inicial | Risco da redação | Delta confirmado |
|---|---|---|
| D01 — denominador descrito apenas como saldo atual; dossiê/manual/CHG | Tratar o percentual de uma publicação Historical como percentual da conta atual | Dossiê §Contabilidade, linha 126, e manual linha 14 vinculam saldo/data à mesma geração e preservam a observação Historical. CHG linha 34 passou a `saldo da mesma geração; atual somente quando a publicação é atual, Historical conserva data e saldo registrados`. |
| D02 — manual prometia componentes observados sem qualificar validade da origem | Mostrar parcelas monetárias como confiáveis com origem/histórico inválidos | Manual linha 18 agora permite subtotal conhecido somente com origem válida e custos parciais; origem ou montante inválido deixam também os componentes N/A. |
| D03 — CHG classificava proteção como informativa | Ocultar que o Supervisor separado pode enviar cancelamentos/fechamentos em demo armada | CHG linha 19 usa `adicional e derivada`. Dossiê linha 14 e manual linhas 7–10 distinguem indicador/Observer de leitura do Supervisor executor. |

O confronto do denominador usa `JPW_Genetrix_Ledger_Core.mqh:402–416`: `amount_valid` depende de Gênese inferida, cobertura histórica e valor finito; `percent_valid` exige saldo positivo; linha 409 usa `100*compensated/view.balance`. A apresentação, linhas 1332–1355, consulta a validade do montante para exibir componentes e explicita `saldo da amostra`, UTC e que o histórico não é flutuante atual nem saldo no encerramento. Conferir essas condições de interface não equivale a aprovar minha própria UI.

## Autoridade, contabilidade e limites preservados

- Dossiê linhas 31–35: 7x/Equity atual é uma proteção técnica adicional escolhida para este candidato. Não substitui os tetos por fase do art. 4.5 da V11, p. 36, calculados com `min(SI,Equity)`. O 7x localizado na p. 79 da V11 é distância em ATR. LIFO é a posição mais recente, não necessariamente a maior. A poda técnica não declara aderência completa à V11 nem infração formal anterior.
- CHG linha 6 separa risco de engenharia N2/N3 de níveis normativos N0–N3. CHG linhas 5 e 19 e dossiê linhas 12, 33, 175 e 183 mantêm autorização do candidato isolado, autoridade por documento/item e os estados PENDING, NOT_HOMOLOGATED e BLOCKED; pesquisa e número de versão não homologam parâmetros ou regra.
- Dossiê linhas 90–114 e manual linhas 16–18 qualificam a Gênese como INFERIDA. Não há promoção de uma defesa para nova Gênese, nem inferência de tese, flag operacional ou dupla confirmação. A Operação formal V11 permanece distinta do ciclo contábil; art. 8.4 §27, p. 73, não é reescrito pela inferência técnica.
- A cobertura do Accountant é DECLARADA, vinculada a referência e identidade da conta; não é automaticamente verificada. Sucesso de HistorySelect não comprova origem histórica completa. Os controles começam false/false/referência vazia, e inconsistências continuam reduzindo cobertura. Não encontrei afirmação de que membros/Gênese com histórico incompleto tenham origem comprovada.
- Dossiê linhas 116–143 e manual linhas 14–18 preservam sinal dos custos e separação realizado/flutuante. Subtotal com custos desconhecidos não se torna resultado líquido completo; ausência não vira zero. Resultado positivo não recompõe RC nem permite ampliar risco. USC permanece unidade monetária nativa e não justifica multiplicar contratos.
- Dossiê linhas 55, 63, 65, 71 e 88 declara limitações de hedge, captura/timer, preço projetado e exclusão entre terminais. O protocolo demo apura mudança direcional com inventário externo; o código não promete uma otimização ou medição automática desse efeito.
- Dossiê linhas 73–75 e manual linha 33 incorporam o delta RIS15: cancelamento com preenchimento exige vínculo ordem/deals/posição, volume reconciliado e testemunho persistido; histórico incompleto, mais de 2.048 deals por posição ou leitura sem suporte mantêm UNKNOWN. A redação corresponde ao limite e à seleção `HistorySelectByPosition` presentes no EA consultado; não foi executada a máquina de reconciliação nesta revisão documental.
- Manual linhas 24–41 e protocolo de demo/rollback distinguem observação, armamento explícito demo hedging, sessões novas, recebimentos/estados e rollback. Não prometem veto universal de entradas externas, compilação nativa já realizada, EX5 comprovado, demo validada, negociação real ou integração/publicação do site.

Precisão não impeditiva: dossiê linha 147 e protocolo demo linha 19 usam a palavra “membros” nos detalhes. A interface consultada exibe contagens de posições/pendentes e contexto do ciclo; uma listagem completa de identificadores individuais exige ledger/histórico. A palavra não deve ser interpretada como promessa de tabela de todos os tickets na UI. Não foi criado requisito novo de tela nesta revisão.

## Identidade dos documentos revisados

Hashes SHA-256 da última leitura. O CHG foi reexaminado após a correção final de sua linha 34; a mudança é registrada, não ocultada.

| Arquivo, relativo ao candidato | SHA-256 |
|---|---|
| `docs/work/GENETRIX-PESQUISA-7X-COMPENSADO-20261001.md` | `c9485d9ff3e006bc39665d3be8f4c44a9bed7db91eed19fedea1a3d8f51cd4b6` |
| `mt5/jpw-alavancagem-atual/GENETRIX_7X_LEDGER.md` | `a176444aedf70704b87f7c8c4924abc5746218eafd3c2f6a0c600176d465fba5` |
| `docs/work/GENETRIX-DEMO-E-ROLLBACK-20261001.md` | `22ad3a9959ef07e3afb9dcc4d4d3320000c5bd9b247423fde52c6fc09b464211` |
| `docs/work/CHG-GENETRIX-7X-LEDGER-20261001.md`, última leitura | `c2133ecebf6c74cf9764e35b6cfd94d657e4828ace8183f2d8e20417d95d61be` |
| mesmo CHG, leitura anterior ainda com denominador sem qualificação | `cd6ea679274227a2dc8db4a7ed7db644f004e1c9b83a2f7ec00b6c699d5b9c3b` |
| `docs/normative/Estatuto_JP_WEALTH_UNIFICADO.pdf` | `2dab6166bb8513cd9beb7fe39c574971af086ebae66683d99c0e6fac69eb6769` |
| `docs/normative/ANEXO_PARAMETRICO_CANONICO.md` | `6240b6330a35fd488f16d4191129eeb01aff8f7a4707158c043afb37d91cdc23` |
| `docs/normative/README.md` | `6f90e08400baca40183479dec2b728e3d2f888005886acdfcb156d44de0bac13` |

Os hashes normativos conferem com as referências do dossiê/CHG. Isso identifica o material local; não constitui auditoria integral de vigência, delegação e todas as pendências do corpus.

## Código de confronto e fronteira de evidência

Raiz dos headers: `mt5/jpw-alavancagem-atual/MQL5/Include/JPWealth/`. Raiz dos EAs: `mt5/jpw-alavancagem-atual/MQL5/Experts/JPWealth/`.

| Arquivo | SHA-256 observado |
|---|---|
| `JPW_Genetrix_Ledger_Core.mqh` | `89480ace885080fbdeb43250402596a373f7d18eaed77efed6671e2ec4ade8e7` |
| `JPW_Genetrix_Ledger_Store.mqh` | `47e2d6084dca31aa218b0f631e985b922e50559c1d1b699d501772e0183f7733` |
| `JPW_Genetrix_Ledger_Terminal.mqh` | `4efe9a62ab476f7add28ed7e3cf24eab85f4c2fa999ab64c3f03aaf61d75cbde` |
| `JPW_Genetrix_Ledger_Bridge.mqh` | `be1251ce39790edf1bec86ea99b33e434030a4dfacc3ccd04ae32785345d3a3a` |
| `JPW_Genetrix_Accountant.mq5` | `eff085079eca0cc7108ec18c01f120f06f4567d3daed650927681234e3e97e24` |
| `JPW_Genetrix_Risk_Core.mqh` | `8325dde4504ca17e72ce94604ef18ceac06a525edf325afaa12f4f127c00a380` |
| `JPW_Genetrix_Risk_Terminal.mqh` | `7a2de90a6b429a514653c1bba309272aab0944f42d6f18a057f2c400ce0cb68f` |
| `JPW_Genetrix_Risk_Store.mqh` | `fc5a858e2a28a67613734d12e266acb082b5b94100104e8246fb65375e20b442` |
| `JPW_Genetrix_Supervisor.mq5` | `fe803f551b7f7d5f35f3e5b1f89937bb12259ae97b1787e4cac3a99260f51d95` |
| `JPW_Alavancagem_Presentation.mqh` | `728f5e0a4c2571c461e636b7c6079e0fbf58771f7f31a411c4bd41f9e06da1c1` |
| `JPW_Genetrix_UI.mqh` | `8f850f5583016832bd0174de722b86565041e01e567e9c9224b8c54b9be76343` |

O parecer independente anterior sobre Risk avaliou EA `49f5500c…` e Core `8541070c…`. Os bytes finais acima incluem RIS15; este parecer documental não estende automaticamente aquela revisão nem confirma a execução dos 51 checks informados pelo autor/coordenador. O parecer anterior sobre Ledger identifica as versões finais dos cinco módulos do ledger acima e descreve seus limites host/native.

Não executei novos testes neste escopo. Compilação MQL/EX5, visual MT5 e demo permanecem NOT_RUN nesta revisão. A matriz final, manifestos, recibos externos e sua correspondência com o pacote consolidado ficam a cargo da integração: `docs/work/GENETRIX-VALIDACAO-20261001.md` ainda não estava presente na leitura registrada; `BASELINE-INPUTS.json`, `CANDIDATE-FROZEN.json` e `NATIVE-ENVIRONMENT.json` externos não foram verificados aqui. Não foi feita aceitação integral do pacote ou da publicação.

Mudança posterior de documento ou código exige releitura das conclusões afetadas. O original paralelo e as fontes normativas permaneceram fora da escrita deste trabalho.
