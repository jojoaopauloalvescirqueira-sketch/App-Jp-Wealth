# Navigation mobile focus — diagnóstico A0

Parecer: a falha intermitente de foco é uma corrida observável entre o teste e a conclusão assíncrona já prevista no shell. Não foi demonstrada uma regressão de runtime Dante. O achado recomenda sincronizar o teste com o próximo frame de conclusão, mantendo os mesmos oráculos. Esta é proposta somente; nenhum arquivo do projeto foi editado e o FULL bruto anterior continua96/102.

## Cadeia causal observada
- tools/navigation_ia_test.py: assert_keyboard_and_mobile clica Alladin na viewport390×844, lê active_state e logo lê alladin.contains(document.activeElement), sem aguardar a conclusão do foco.
- src/js/40-app/11-operational-shell.js:728–743, shellNavigationApplied agenda requestAnimationFrame deliberadamente. O comentário explica que o próximo frame permite que a conclusão de navegação vença a restauração de foco de um diálogo.
- No callback, shellFinishNavigation (722–726) fecha o menu e chama shellFocusCurrentScreen; navFocusCurrentScreen (01-navigation.js:292–307) foca o título visível do destino.
- A rota já está aceita/renderizada antes desse callback. Por isso screen/primary podem estar corretos enquanto foco/menu ainda estão no estado anterior. Não existe uma garantia implementada de foco síncrono no retorno do clique.

## Execução própria
Comando: `DEBUG=pw:browser .superpowers/sdd/2026-10-21-planning-monthly-inline/runtime/bin/python3 /private/tmp/jpw-dante-20261024/navigation-focus-proposal/probe.py`.

PASS da sondagem diagnóstica, exit0 natural; source_unchanged=true para os5arquivos identificados no receipt. Cinco contextos descartáveis390×844, cliques reais pelo Playwright, sem force, sleep, supressão/atraso de RAF ou navegação simulada. Instrumentação registra capture/bubble/focusin e envolve somente callbacks RAF originados de shellNavigationApplied, conservando seu agendamento nativo. O wrapper pode adicionar custo de observação; a ordem observada e o código fonte são a evidência, não uma promessa de taxa de ocorrência.

| Repetição | Foco imediato dentroAlladin | Após próximo RAF dentroAlladin | Conclusão após click-bubble |
|---|---|---|---|
| 1 | True | True | 9.9 ms |
| 2 | False | True | 13.5 ms |
| 3 | False | True | 11.9 ms |
| 4 | False | True | 11.9 ms |
| 5 | False | True | 11.5 ms |

Em4/5a leitura imediata foi falsa; em5/5o frame seguinte terminou com H2 dentroAlladin e menu fechado. Todos os traces mostram click-bubble e RAF-before ainda no botão do menu; focusin do H2 ocorre dentro do callback e RAF-after já vê o destino correto. Todos os contextos positivos tiveram pageerror/console vazios.

## Contraprova
Sexto contexto isolado, mesma rota/clique/RAF, com somente shellFocusCurrentScreen substituída por no-op na memória daquele browser. A rota Alladin permaneceu aceita, mas alladin.contains(document.activeElement) continuoufalse após o mesmo rendezvous de1frame. O mesmo predicado rejeitou a violação. Nenhuma mutação dessa contraprova foi escrita no projeto, e não foi usado foco manual para obter verde.

## Comparação do baseline
O baseline-pending.zip inicial contém build1b695b809fe80c26. O runtime01-navigation.js e o próprio navigation_ia_test.py são byte a byte idênticos entre esse ZIP e a execução atual. 11-operational-shell.js é idêntico aHEAD a4bf278 e não aparece no arquivo de pendências inicial. Essa comparação sustenta a anterioridade do mecanismo/teste; não executamos o site inteiro baseline1b695b nesta sondagem.

Hashes comparativos completos e fontes build estão em receipt.json. O source_unchanged cobre navegação, shell, teste, build-id e index; não representa uma auditoria nova dos673arquivos globais.

## Proposta delimitada
proposed.patch contém somente um rendezvous nativo de requestAnimationFrame entre a aceitação da rota e a leitura geométrica/de foco. Mantém sem alteração: screen/primary, contenção horizontal+2px, contains(activeElement), fechamento do menu, shellLocation e ausência de erros. Não acrescenta sleep fixo, tolerância de foco, fallback, retry ou timeout mais amplo. Uma alternativa a discutir é aguardar diretamente o predicado de foco com a política existente, mas não foi implementada nem é necessária para explicar o resultado.

A contraprova missing-focus deve permanecer vinculada ao mesmo oráculo e ao mesmo rendezvous, para provar que esperar o frame não transforma ausência definitiva de foco em PASS. A mudança seria maturidade de sincronização do harness, sujeita à autorização própria de control plane e revisão; a solicitação atual é A0 e não a aplica. Se o objetivo futuro for foco síncrono, isso seria um novo contrato de runtime fora deste diagnóstico.

## Classificação e limites
Preservar PRODUCT_FAIL bruto do FULL, replay isolado PASS recebido do principal e sondagem própria como evidências separadas. A sondagem explica a falha; não converte retrospectivamente o FULL emPASS. Nenhuma conclusão sobre as outras5falhas ou aceite humano. Zero mudança de critério/latência/runtime/projeto nesta investigação.
