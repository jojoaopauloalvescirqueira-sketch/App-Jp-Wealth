# Planejamento — posições e proporções

As cinco falhas de apresentação foram corrigidas no candidato local, mantendo perguntas, opções, perfis, fórmulas, confirmações e dados. As três abas continuam **Comece aqui, Consolidado e Preenchimento mensal**; Planejamento permanece após Research e independente de Forex. [Plano aprovado](../../superpowers/plans/2026-10-21-planning-proportions.md) · [Contrato da mudança](../../work/CHG-JPW-PLANNING-PROPORTIONS-20261021.md).

## Antes e depois

| Defeito reproduzido | Correção e proteção | Evidência visual |
|---|---|---|
| Janelas no canto superior esquerdo | Centro dentro de2CSSpx; margens24px ou12px; formulário1120/720px, Perfis/Parada800px. | [Antes](before-dialog-center.png) · [Depois](after-dialog-center.png) |
| Custo abaixo da moeda | Rótulo e opcional juntos; bases dos controles alinhadas dentro de2px. | [Antes](before-money-bases.png) · [Depois](after-money-bases.png) |
| Fechar em segunda linha no celular | Cabeçalho local sem quebra do botão44×44; corpo com rolagem própria. | [Antes](before-mobile-header.png) · [Depois](after-mobile-header.png) |
| Previsão incompleta repetida e excessiva | Orientação única; tipografia grande reservada ao resultado calculado. | [Antes](before-pending-copy.png) · [Depois](after-pending-copy.png) |
| Amostras de legenda com largura zero | Amostras visíveis das duas séries; data utilizada no rodapé. | [Antes](before-stop-legend.png) · [Depois](after-stop-legend.png) |

[Formulário no desktop](form-desktop.png) · [Perfis no celular](profiles-mobile.png) · [Parada no celular](stop-mobile.png) · [Previsão no celular](forecast-mobile.png).

## Evidência focal

Os cinco casos falharam antes da mudança de produto ([RED original](FOCAL-RED-ORIGINAL.json)). O mesmo teste final rejeitou os bytes preservados09d53 ([contraprova](FOCAL-RED-COUNTERPROOF.json)); os oráculos geométricos foram preservados. No candidato corrigido, [94/94 casos focais passaram](FOCAL-GREEN.json): cinco defeitos,80combinações de viewport/layout/tema, uma jornada de gravação/marcos e oito verificações com zoom nativo200%. As capturas são anteriores à reconstrução oficial; os [hashes de UI/CSS e proveniência](FOCAL-PROVENANCE.json) identificam as fontes examinadas, sem atribuir o build-id antigo ao novo produto.

As jornadas verificam criação, edição, multiconta, erros, revisão, cancelamento, Perfis, Parada, foco e isolamento dos diálogos. Com início emoutubro/2026,US$1000,aporteUS$100,perfilBase e objetivosUS$50/100, os marcos continuam mar/2027 e jan/2028;US$2000 muda o segundo para jun/2027 antes de salvar. Leitura, previsão, revisão e cancelamento não gravam dados financeiros. Motor e state permanecem idênticos à base09d53.

A matriz das três abas também foi repetida em24casos, oito valores longos e360medições de palavras completas. As duas expectativas antigas da ordem do menu foram reconciliadas para Planejamento apósResearch;61/136asserções e os mesmos sete mappings de rota foram preservados. Isso não encerra incidentes históricos.

## Revisão independente e pacote final

A comparação A/B de organização e clareza dos dois marcos é registrada em [revisão independente](INDEPENDENT-REVIEW.md). A referência é o HTML original verificado com callbacks sintéticos, não uma sessão Google autenticada. Página e modal são reconhecíveis; não há cegamento completo nem teste humano.

O [candidato congelado](RELEASE-CANDIDATE.json) identifica327inputs oficiais ordenados,397recursos de execução,260testes e um runner. A execução completa tem95checks: todos os94anteriores preservados, com o novo teste de proporções. O resultado da execução, seu término e exit observado são registrados exclusivamente em [FULL-RESULT.json](FULL-RESULT.json) e [FULL-CHECKS.md](FULL-CHECKS.md); a ausência desses recibos ou qualquer resultado diferente dePASS mantém o gate pendente. Este texto não antecipa aprovação.

Os [resultados de proporções](PROPORTIONS-RESULT.json), [três abas](THREE-TABS-RESULT.json), [layout](LAYOUT-RESULT.json), [Notas globais](NOTES-GLOBAL-RESULT.json), [botão de Notas](NOTES-LAUNCHER-RESULT.json) e [escopo final](FINAL-SCOPE.json) devem corresponder ao mesmo candidato e à mesma execução. Distribuição cobre HTTP, PWAoffline, arquivo modular e portátil; a reprodutibilidade e atualização do serviceworker permanecem no gate.

## Preservação e limites

Baseea15afc, branchcodex/planejamento-patrimonial-20261020, candidato completo anterior09d53 preservado. O FULL anterior foi interrompido após90checks concluídos, sem recibo final nem exit observado; continua incompleto. As91verificações de versões anteriores não são aprovação deste pacote.

Dados sintéticos exclusivamente. Sem alterações de motores/state, formatos debackup, normas, instruções, dependências, dados reais, migração, operaçõesGit ou publicação. Preservados três minigames e BolsasGlobais. Somente o índice factual local de regressões foi reconciliado; memória global e wiki não foram alteradas. Google autenticado, Safari, leitor de tela, toque físico, compreensão e aceite visual humano permanecem não executados. Capturas e testes automáticos não demonstram compreensão humana.

Checagens adicionais: distribuição pós-reconstrução e integridade da integração JP Engenharia passaram. O verificador estrutural de instruções, fora do FULL95, continua recusando seu modo padrão histórico: contrato de outra pasta e duas Source revisions preservadas. Esses dois fatores já constavam da base09d53; [registro e limites](ADDITIONAL-CHECKS.json). Não se alterou o verificador, a autoridade histórica ou as instruções para obter aprovação.

A primeira execução completa deste candidato terminou93/95, com timeouts no guia e Gêmeos doTempo; os focais isolados passaram sem mudanças, mas a causa permanece inconclusiva. [Histórico integral e falhas preservadas](RUN-HISTORY.md). A nova execução completa tem recibo próprio; não substitui nem apaga a primeira.
