# JP Wealth — primeiro acesso vazio — 24/10/2026

Candidato local **1b695b809fe80c26**, branch `codex/primeiro-acesso-vazio-20261024`, base `a4bf278` e 32 pendências de Calendário e Mercados preservadas. [Plano](../../superpowers/plans/2026-10-24-empty-first-use.md), [brief](../../work/BRIEF-EMPTY-FIRST-USE-20261024.md) e CHGs PRODUCT/TESTS dedicados. Sem commit, merge, push ou publicação.

## Estado atual

**FULL3: 102/102 PASS, exit 0, nenhuma falha ou caso não executado.** As 664 entradas congeladas permaneceram idênticas. [Resultado integral](full-confirmed.json) e [recibo de execução e integridade](full-confirmed-runner.json), concluídos às 16h28 de 24/10/2026. Focal adicional: 16/16 PASS, sete contraprovas rejeitadas e matriz 43/43 PASS no mesmo build. [Revisão de produto](independent-review.md) e [revisão das fixtures](independent-review-session-fixtures.md). Aceite visual humano pendente.

## O que mudou

| Antes | Depois |
|---|---|
| Quatro contas e desempenho demonstrativos no primeiro acesso | Nenhuma conta, período, operação ou histórico criado antes da ação explícita |
| Capital 10.000, saldo 10.240, início em 25/05/2026 e observações presumidos | Saldos e observações não informados como `null`; data, perfil e capital nominal vazios |
| Checklist respondido, com 23/30 e classificação válida | Sem seleção; pontuação “—” e quantidade respondida; classificação somente após resposta de todos os itens |
| Novo cadastro sem observação gravava saldos zero | Cadastro novo/recadastro usa `null`; valores anteriormente registrados, inclusive zero, preservados |
| No celular, quantidade respondida ficava atrás de reticências | Texto completo com quebra local; sem alterar demais indicadores |

Sugestões editáveis nos formulários continuam disponíveis antes da confirmação. Catálogos, bloqueios, política e fórmulas, referências públicas datadas e simuladores permanecem. Não há remoção de contas já salvas por nome/valor; a correção aplica o estado vazio a bases novas. Atualizar não limpa sua base pessoal.

O novo domínio admite `null` explícito; continua recusando `saldoIni` apagado e tipos incompatíveis. O Backup Completo mantém o envelope; o candidato lê backups anteriores e comprova ida e volta dos novos. Versões antigas podem recusar os novos nulos. JSON inválido continua preservado em recuperação com bloqueio de gravação. Finalizar sessão preserva fatos confirmados.

## Provas atuais

- [16 casos funcionais e 16 estados visuais](focal-final.json): primeiro acesso sem injetar estado pessoal, navegação, recarga/checkpoint, checklist parcial/completo/vazio, cadastro/cancelamento, legado/zero explícito, backup, corrupção e conflito. Rede pública bloqueada; não é auditoria de cotações ao vivo.
- [Sete contraprovas pela fonte real](tests-summary-visual-final.json): conta preexistente, respostas presumidas, ausência convertida em zero, classificação incompleta, `null` recusado, resposta do checklist sem chave `v` aceita e corte visual. Todas rejeitadas pela mesma entrada. A rejeição de `saldoIni` apagado é um caso distinto do focal. Seleção sem casos retorna TEST_HARNESS_FAIL e exit 1.
- [43 casos de distribuição](distribution-matrix/attempt3/matrix.json): 32 combinações HTTP (4 layouts × 2 temas × 4 larguras), arquivo modular, portátil isolado, PWA offline com cache e respostas do service worker, além de oito casos de zoom nativo de 200% em navegador sem janela (largura externa 1.440, interna 720 e CSS zoom 1). Nenhuma pré-injeção de estado pessoal, falha local, erro de página ou gravação financeira; 215 fontes estáveis.
- [Inspeção visual](distribution-matrix/attempt3-layout-inspection/report.json): larguras de 320, 390, 900 e 1.440 px, conteúdo integral e botão Fechar de 44 px com desvio interno de até 2 px. [Antes, 390 px](distribution-matrix/layout-inspection/checklist-390.png) · [Depois, 390 px](distribution-matrix/attempt3-layout-inspection/checklist-390.png). A [verificação visual da suíte final](full-confirmed-ui-visual-quality.json) aprovou seus 370 casos.
- Backup/importação: 35/35; senha de investidor nas distribuições modular/portátil e fundação Alladin aprovados. [Confiabilidade de backup: 26/26, com fontes estáveis](fixture-focals-final/backup-reliability.json). Estado Forex: 41/41 e cadastro: 35/35, em execução estável anterior à correção exclusiva do CSS; suas fontes e oráculos continuam preservados. A suíte integral atual passou no pacote final, incluindo backup, integridade, recuperação, finalização, guia, calendário, distribuições e minigames.
- [Dois focais integrais de preservação de sessão](session-fixtures-final/receipt.json), nos patches exatos: ambos PASS. [Contraprova de preservação](triage-finalize/exact-patch-counter-verified.json) e [contraprova de serialização](triage-serialization/exact-patch-counter.json) rejeitam perda de contas sem falhar na pré-condição.
- [Preservação de escopo](scope-audit-final.json): 153 arquivos preexistentes conferidos, nenhum arquivo perdido nem alteração inesperada. Os 96 registros anteriores, histórico de ACTIVE-TASK e fontes de Calendário/Mercados foram preservados. Cinco novas regressões permanentes adicionais ao FULL, sem afirmar inclusão automática no runner. Política, motor, AGENTS e runner intactos.

## Histórico de execução preservado

Falhas originais: [contas](tests-red-boot.json), [checklist](tests-red-checklist-v2.json), [cadastro](tests-red-registration.json) e [corte no celular](tests-red-visual-01.json). Tentativas com falha do verificador não foram usadas como prova de defeito do produto: boas-vindas tardias, âncora de mutante ambígua e classificação agregada incorreta foram corrigidas com evidências próprias.

A primeira rodada de estado Forex e confiabilidade de backup concluiu seus casos, mas detectou alteração de fontes durante reconstrução/implementação: não recebeu aprovação integral; novas execuções estáveis passaram. O primeiro cadastro retornou 32/35 ao exigir zeros agora deliberadamente substituídos; as três expectativas foram reconciliadas com `null` e o mesmo cenário passou 35/35, preservando as demais asserções. Chamadas com opções de comando ou PATH incorretos não executaram casos e permanecem registradas, distintas de falha de produto.

[FULL1 parcial](full-first-partial.json): 8 PASS e 94 NOT_RUN, interrompido intencionalmente após confirmar corte no celular. Não existe PASS integral dessa tentativa; [log](full-first.log) preservado. FULL2 usa as [664 entradas congeladas](full-final-inputs.json).

[FULL2 completo](full-second.json): 100 PASS e dois PRODUCT_FAIL brutos. Todos os 664 inputs permaneceram idênticos durante a execução. A [triagem de preservação](triage-finalize/TRIAGE.md) e a [triagem de serialização](triage-serialization/RESULT.md) demonstraram pré-condições ausentes: testes tratavam a coleção vazia como perda, sem instalar uma conta. Os patches preservam asserções anteriores e usam contas sintéticas explícitas; C8/C11/C14 também conferem igualdade integral. Variantes destrutivas continuam rejeitadas. Nenhum defeito do produto foi demonstrado nessas duas falhas; sua saída bruta não foi alterada.

FULL3 utiliza as [entradas congeladas após as duas correções de fixtures](full-confirmed-inputs.json). As outras 662 entradas, inclusive todo o produto, permanecem iguais às do FULL2. Os mesmos 102 identificadores do gate foram executados integralmente em 2.320 segundos: 102 PASS, zero PRODUCT_FAIL, TEST_HARNESS_FAIL, ENVIRONMENT_ERROR, BASELINE_FAIL ou NOT_RUN. Não houve exceção, dispensa ou alteração do runner. A passagem atual não apaga as falhas históricas das tentativas anteriores.

## Limites e próximo gate

O [parecer independente final](independent-final-audit.md) confirmou os recibos, os 102 identificadores do gate, a identidade das fontes e a preservação do escopo, sem impeditivo técnico aberto. [Estado Git e conferência final](final-git-state.json). A revisão não representa teste humano ou autorização de integração.

Nenhum perfil pessoal ou dado real foi editado; somente contextos sintéticos isolados. Safari, leitor de tela, toque físico e aceite/compreensão humana não são comprovados pelos testes em Chromium. Revisão independente, gate técnico e aceite do proprietário são provas distintas.

AGENTIC IMPACT CHECK: AGENTIC IMPACT DETECTED. BASIS: fonte inicial/contratos de ausência e fixtures consumidos por agentes mudaram; reconciliados somente STATE-SCHEMA, DATA-RECOVERY, plano/brief/CHGs/ACTIVE-TASK, registro factual e estes recibos dentro do contrato aprovado. Normas, instruções, routing, skill congelada e memória global intactos; histórias oficiais não foram promovidas a aprovação atual. INDEX NOT REQUIRED.

Prévia: http://127.0.0.1:51629/index.html?v=1b695b809fe80c26. Essa origem permite observar o primeiro acesso sem apagar a base salva na prévia anterior. O [recibo HTTP](preview-recheck.json) confirma página, build-id e CSS iguais aos arquivos testados.
