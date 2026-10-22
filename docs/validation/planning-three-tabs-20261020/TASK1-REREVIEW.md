# Re-review independente — fix P3 R1

**PASS focal. P3 fechado na fonte examinada.** Não surgiram novos achados no delta e nas adjacências testadas. O relatório, screenshot e PRODUCT_FAIL originais permanecem preservados.

Li `task1-fix-r1.md`, o teste permanente novo, e os recibos RED, GREEN isolado e GREEN completo. Eles registram o mesmo teste/hash `1ab8d79f3b2dd2799931b4038aef57aa154c2dd7692a95f9ab6e8b5750d4bccd` falhando na fonte anterior e passando na corrigida. Esses resultados do construtor não foram herdados como execução independente.

Executei `critic-task1/rereview.py` em Chromium isolado com contas sintéticas, servidor local e fonte de UI explicitamente servida por rota em dois contextos distintos: contraprova anterior e candidato corrigido. **17 verificações próprias PASS**, registradas em `critic-task1/rereview-results.json` e `rereview.log`.

- Todas → Detalhes das contas: a contraprova exibe a promessa de comparação de esforço; o candidato a remove. Capturas reais `rereview-counterproof.png` e `rereview-fixed.png`, esta última inspecionada visualmente.
- A orientação sobre metas de renda/perfis e os dois links de contas permanecem. Clicar Beta seleciona Beta e mostra seu objetivo nativo.
- Preencher formulário da conta selecionada conserva Perfil Base; comparador abre os quatro perfis. Previsão adjacente mantém16 meses/jan2028 no cenário fixo. Abrir/navegar/fechar não altera o snapshot financeiro.
- Comparação literal independente com `task1-fix-r1-before-ui.js` demonstra que a única alteração de produção desta correção é “As metas de renda, os perfis e a comparação de esforço são individuais.” → “As metas de renda e os perfis são individuais.”
- CSS, engine e state mantêm os hashes da revisão anterior. Templates completos de formulário/perfis/parada são idênticos. Não foi reexecutada toda a matemática: a preservação dos demais cálculos/perfis se sustenta também na identidade desses bytes.

Identidade examinada: UI `4c35c87428863267e85142521c7e49a1ec6a85430ff4a5ddc7cf5c060c50396a`; teste permanente `1ab8d79f3b2dd2799931b4038aef57aa154c2dd7692a95f9ab6e8b5750d4bccd`. Hashes antes/depois de UI/CSS/engine/state/teste foram estáveis durante esta execução. **Essa afirmação é restrita a essas cinco fontes**; não atesta identidade do manifest, build_id, dist ou artefato gerado pelo rebuild concorrente do root.

Falha de preparo: o primeiro callback de rota do harness independente aceitou o segundo argumento como corpo por engano, quando Playwright passava Request. Corrigida apenas a assinatura do callback; recibos brutos preservados em `rereview-results.json.route-error` e `rereview.log.route-error`. Classificação: TEST_HARNESS_FAIL, não defeito do produto.

Esta revisão fecha o único P3 do relatório anterior no recorte autorizado. Não repete FULL, matriz completa, distribuição ou sessão autenticada Google; não concede aceite humano/publicação. Produtos identificáveis, sem alegação de cegamento. Nenhum arquivo do produto foi alterado pelo crítico.
