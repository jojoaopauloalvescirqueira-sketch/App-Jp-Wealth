# Revisão independente A0/A1 — Contabilidade / proposta Caixa Anual

Candidate confirmado: repositório CloudDocs `/SOFTWARES & EAS/JP Wealth OS`, branch `codex/mesas-proprietarias-hedge-20261027`, HEAD `3e24f60f8cfe87f79335f40e95a0927379a9f834`, 103 entradas pendentes antes e depois. Preflight audit PASS com avisos preservados. Preview `http://127.0.0.1:51757/index.html`, build `09cfa4f7b8a8dbed` consultado no navegador. Bytes servidos de index.html, build-id.js e 03-ui.js coincidiram com disco; hashes em concerns.json. Nenhuma edição no produto, dados reais, storage do operador, Git ou testes do repositório. Somente fixtures sintéticas e arquivos deste scratch.

A finalidade aprovada é comparar planejamento anual e fechamentos reais por conta/período/ano, conservando o writer canônico e a independência da seleção operacional Forex. Fonte humana: docs/superpowers/plans/2026-10-26-portfolio-management.md; contrato docs/architecture/MANAGEMENT-ANNUAL.md. Usadas jpw-critical-review, preflight, change-control em fase A0, browser-verification e test-triage. Nenhuma atualização de contexto foi feita.

## Conclusão

CONFIRMADO: a interface permite iniciar, rever e confirmar plano; cancelar sem gravar; registrar resultado monetário com prévia; corrigir com motivo; anular com confirmação; revisar e confirmar fechamento anual elegível. A identificação de conta/período/ano está visível. Resultados projetados e realizados aparecem em blocos distintos; dias decorridos, fechamentos e declarações têm contagens distintas, sem afirmar dias efetivamente trabalhados. Há duas incoerências materiais no resumo após alterações válidas das fontes financeiras, descritas abaixo. São apresentação e orientação; os cálculos e bloqueios pertinentes conservaram os estados corretos nos casos observados.

## Achado UX-01 — P2 — abertura real usada no retorno fica ausente do resumo

CONFIRMADO / PRODUCT_FAIL de apresentação; confiança alta. Fonte: `src/js/30-accounting/07-management/03-ui.js:91` usa `c.initialBalance` sob o rótulo genérico Saldo inicial, com nota Abertura conferida; `:93` mostra o retorno real e diz Saldo confirmado ÷ abertura − 1. Engine `01-engine.js:136-140` distingue `initialBalance` e `actualInitialBalance`; state `02-state.js:34-44` consulta a abertura real atual.

Esperado: preservar a abertura planejada já confirmada e expor qual abertura real sustenta o realizado quando ela muda. Observado: plano 2025-12-31 confirmado com abertura1000, último fechamento anterior corrigido via `JPWForex.state.recordAccountLedger` para1200, e fechamento derivado do dia recalculado para1212. Consulta real retornou initialBalance1000, actualInitialBalance1200, currentBalance1212, accumulatedResult12 e realCumulative1%. O resumo mostrou Saldo inicial1000 / Abertura conferida, Saldo confirmado1212 e retorno1%, sem apresentar1200. O denominador do retorno não pode ser reconstruído pelo resumo.

Evidência: `17-corrected-source-opening.png`, `concerns.json.corrected_source`, reprodução `concerns.py`. Contraprova: a abertura real correta1200 existe na tabela diária, e a abertura planejada1000 deve permanecer preservada; não é prova de cálculo errado nem motivo para sobrescrever plano automaticamente.

RECOMENDAÇÃO mínima: nomear e mostrar Abertura planejada e Abertura real consultada, com origem/data quando divergirem; sinalizar a mudança de fonte e manter a programação anterior até ato explícito. Validar com a mesma correção canônica e conferir resumo/tabela/retorno sem mudar os resultados.

## Achado UX-02 — P2 — selo Registros conferidos em saldo ainda não reconciliado

CONFIRMADO / PRODUCT_FAIL de apresentação; confiança alta. Fonte: `03-ui.js:91` decide a nota apenas por `pendingDays`; `:96` exibe alerta de mismatches separadamente. `:93` produz Aguardando pendências para toda ausência de `completeActual`. Engine `01-engine.js:110-125` distingue divergências, pendências e completude.

Esperado: quando há divergência de saldo, o resumo não afirmar conferência concluída; a causa da indisponibilidade das taxas deve ser discernível. Observado: no mesmo contexto sintético, writer confirmou saldo OBSERVED1300 com resultado12, após abertura real1200. Query: pendingDays0, mismatches1, completeActualfalse, recordedResult12, accumulatedResult100. Resumo: Resultado acumulado100 / Registros conferidos; Taxa diária realizada — / Aguardando pendências. Mais abaixo, alerta informa saldos observados diferentes da cadeia calculada.

Evidência: `18-mismatch-confirmed-label.png`, `19-mismatch-warning.png`, `concerns.json.mismatch`, reprodução `concerns.py`. Contraprova: o alerta específico existe, as observações são preservadas, taxas/extrapolações e termômetro ficam indisponíveis corretamente; não foi observado fechamento anual indevido nem alteração de fatos. A falha é o selo afirmativo contraditório no resumo.

RECOMENDAÇÃO mínima: derivar a nota do estado completo, mostrando Saldos a reconciliar para mismatch e a quantidade de dias somente para ausência; manter o alerta e os bloqueios. Validar pending0/mismatch1, pending>0/mismatch0 e caso completo.

## Jornadas e evidência positiva

- Empty desktop/mobile: orientação para cadastrar ou selecionar conta/período; nenhum plano ou resultado criado automaticamente. Screens01/02.
- Plano: Configurar planejamento anual → campos → Revisar programação → saldo/objetivo/checkbox → Confirmar programação. Cancelar restaurou foco em new-plan, agregado ausente e ledger vazio. Screens03/04, observations.json.plan_cancel.
- Resultado: Preencher no desktop ou data→detalhes→Registrar resultado no compacto → valor/nota/referência → Revisar → abertura/resultado/fechamento → checkbox → Confirmar fechamento. Digitação e revisão conservaram ledger vazio; confirmação criou um registro canônico10/1010. Screen06, observations.json.saved.
- Correção: resultado existente → valor12 + motivo → revisão → confirmação. Anulação: data→detalhes→Anular fechamento→motivo→revisão→checkbox→confirmação; ledger vigente voltou a vazio. Screens07/08; observations.json.voided.
- Ano atual: revisão informa indisponibilidade; ano histórico elegível2025 (um dia programado resolvido) mostrou conferência, confirmação e ✓Ano fechado. Histórico exibiu retrato diário. Screens09/14/15/16.
- Mobile390×844: tabela em3colunas, detalhes com valores completos e atos. Revisão do resultado permitiu cancelar sem escrever. Não houve overflow horizontal: document.scrollWidth390. Desktop1440×1000: scrollWidth1440; tabela ampla com blocos lado a lado. Screens10-13.
- A seleção operacional Forex antes/depois foi idêntica. Nenhum pageerror, requestfailed ou destino de rede inesperado na execução concluída. Rede externa conhecida foi respondida pelo fixture; acesso real somente localhost.

## Comparação estrutural com Todas

CONFIRMADO por leitura OOXML somente de rótulos/mesclas/estilos/colunas/painéis, sem registrar valores pessoais do XLSX Desktop `Planejamento_com_aporte copy.xlsx`. A primeira aba tem no topo Data Atual/Data Inicial/Data Final Projetada, Saldo Inicial/Target Anual/Saldo Final Desejado/Saldo atual; resultado real, calendário, metas e programação; tabela Projetado/Real em faixas separadas, Inicial/Resultado/Acumulado e subtotais. Painéis fonte congelados em G13 (xSplit6,ySplit12). O site conserva a hierarquia funcional desses grupos e as duas faixas, acrescenta confirmações e snapshot anual conforme plano. Em largura estreita, a tabela deliberadamente muda para3colunas e detalhes.

INFERÊNCIA UX, sem defeito demonstrado: no compacto, o resumo tem1107px de altura e a tabela começa em y2158 no estado testado; a entrada diária exige rolar e expandir a data. Os controles são alcançáveis e o ato foi concluído/cancelado, portanto isto é uma questão de eficiência a submeter ao uso do proprietário, não um bloqueio confirmado. Não há evidência de que a interface deva imitar pixel a pixel a grade Excel.

## Fluxo atual conectado

Usuário: Gerenciamento/Contabilidade → conta+período+ano → configurar ou revisar plano → revisão e confirmação → comparação diária → registro/correção/declaração/anulação → revisão anual/histórico.

Sistema: rota management-accounting → JPWManagement.activate/accounting → installContext/render → JPWManagementAnnual.queries.model → summaryHTML/tableHTML. Editor de plano → previewPlan → savePlan. Editor diário → previewResult/previewVoidResult → comando correspondente → JPWForex.state.recordAccountLedger → nova consulta/render. Fechamento anual → previewAnnualClose → closeAnnual → retrato/dependências; não encerra período nem ordens Forex. Fontes: 03-ui.js69-116,129-151,196-229,246-296; APIs declaradas no contrato anual.

## Cobertura e limites

PASS das jornadas delimitadas observadas; PRODUCT_FAIL dos dois textos de resumo acima. Duas tentativas exploratórias anteriores foram TEST_HARNESS_FAIL (dialog genérico encontrou Central de Notificações+dialog de gerenciamento; condição transitória do botão do menu durante resize). Só seletores/estado de captura do scratch foram corrigidos; sem force, aumento de timeout ou alteração do produto. A execução final do review.py terminou exit0,16capturas; concerns.py exit0,3capturas e contraprovas canônicas.

NÃO VERIFICADO: Excel nativo, equivalência visual integral da aba, toque físico, Safari, leitor de tela, pesquisa com usuários, tema escuro, zoom nativo, recuperação/reload e matriz FULL. Não foram executados nem solicitados nesta revisão independente delimitada. A revisão não implementou a renomeação Caixa Anual e não aprova publicação.
