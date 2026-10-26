# Revisão A0 — sincronização do teste de foco mobile

24/10/2026. **Sem achado bloqueante P0–P3 na proposta.** Um requestAnimationFrame antes da leitura preserva o critério de foco e corresponde à conclusão já agendada pelo shell. Favorável à alteração delimitada do teste após reconciliação do CHG; sem mudança de runtime e sem aplicação por este revisor.

## Causa, preservação e contraprova

- Inspecionei shellNavigationApplied e shellFinishNavigation reais. A rota é aceita antes do RAF; o callback, sujeito aos guards/serial, fecha o menu e chama shellFocusCurrentScreen. O comentário explícito explica o frame: concluir depois da restauração de foco de diálogo. O contrato de navegação exige foco no conteúdo, sem garantia de sincronia no retorno do clique.
- O teste atual lê foco imediatamente depois de confirmar screen/primary. A proposta acrescenta somente um rendezvous de RAF antes de medir. Comparação AST própria: nenhuma função removida; só assert_keyboard_and_mobile muda; ao remover a nova expressão RAF, todo o AST anterior coincide. Geometria +2px, foco dentro Alladin, menu fechado, localização, alvos44px e ausência de erros permanecem iguais. Não há sleep, retry, foco manual ou maior tolerância.
- Conferi o ZIP protegido: 01-navigation.js e navigation_ia_test.py são byte-exatos à base anterior ao Dante. 11-operational-shell.js é byte-exato HEAD. O contraste diferente do teste com HEAD não o torna regressão Dante: o teste já era pendência da base.
- Li probe.py, PROPOSAL e receipt do construtor. Cinco contextos reais390×844: foco imediato falso em4/5, foco verdadeiro após o próximo RAF em5/5. Contraprova no sexto contexto: somente shellFocusCurrentScreen no-op; rota aceita, foco ainda fora Alladin após o mesmo frame, predicado rejeitado. Instrumentação conserva o RAF nativo, mas pode adicionar custo; 4/5 não é estimativa de frequência de usuários.
- Unidade própria com shellNavigationApplied/shellFinishNavigation extraídos: antes da fila, foco não concluído; no frame, foco concluído e menu fechado. Ao substituir só a função de foco por no-op, o mesmo frame conserva foco falso e o critério rejeita. Essa unidade verifica ordem/efeitos programáticos; não substitui a prova nativa lida.

## Verificações e limites

Hashes do recibo conferidos contra os cinco arquivos reais, source_unchanged=true. `git apply --check proposed.patch` exit0, sem aplicação. Não alterei fonte/testes ou iniciei browser.

Não rerodei browser próprio nem o teste permanente inteiro. Após aplicar o ajuste autorizado, executar navigation_ia_test.py pelo runner real, demais focais pertinentes e FULL no candidate final. O novo await deve continuar rejeitando ausência definitiva de foco; não autoriza mudar o runtime para foco síncrono ou criar um retry mais permissivo. FULL bruto96/102 e as outras falhas permanecem com seus recibos próprios. Não há aceite humano, headed, toque físico, publicação ou operação Git de mutação nesta revisão.

## Hashes

- Real `src/js/40-app/01-navigation.js`: `01101642d98fdd1ac18299153eaf6de5bcda4b5316aa1322a957967b3ede186e`
- Real `src/js/40-app/11-operational-shell.js`: `8e9cbd01549210458b7d8c1c1214d9907c3ee65aef6017a27c489c5c1018d5ee`
- Real `tools/navigation_ia_test.py`: `4aa1f271ba0c527b51a21e023f3656ade9e2555c91d7e6158325ebffeba7ace8`
- Real `build-id.js`: `b7ddb6a2a3ad74a508663b7b6181b51e88abfc1d4426bd951c9d4be7136c1e18`
- Real `index.html`: `a2f88529437a07211057d7e7531ae2810320cb9ed8abbca7fbeaf980aed1d748`
- Scratch `proposed.patch`: `c4d0708d6ce1c2c91a913c3f428b369e3c509c29720bbc4ae362fa4536606184`
- Scratch `probe.py`: `c04ceaf947a532e7f54c9922f3a6764b5aa1a732f43978892f1a8dd17bbd093b`
- Scratch `receipt.json`: `833df42851fde94b5bbd455103e1f15fceccb906c8a2ba5e8fc926f68a5449b3`

Única escrita: este relatório externo.
