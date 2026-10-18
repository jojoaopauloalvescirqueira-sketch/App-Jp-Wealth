# Candidato local — submenu corrigido; botão principal em investigação —17/10/2026

Corrigida a exploração lateral que permanecia visível após congelar o módulo sem mudar de rota. ReparoN1/A2 apenas no shell; pin disponível e foco preservados nos casos cobertos. PF continua congelado por padrão; overrides explícitos permanecem válidos. Dados, backup, regras financeiras, três jogos e Bolsas Globais preservados.

Build `40045045ce5acd15`. AV-NAV-FROZEN RED/GREEN6casos; core26, UI30contextos, work, backup14/0 e sidebar16grupos source/portablePASS; contextual lifecyclePASS. Contextual completo BASELINE_FAIL na primeira recusa de Galton por checklist aberto, reproduzida na baseline integral, sem certificação dos grupos seguintes. IntegraçãoJP Engenharia20/2/17/13PASS após correção factual de metadado. FULL atual **81 PASS**, exit0,81IDs/ordem/comandos conferidos; rawSHA256`99cf8648cbe581e83c03f8746b93981d36566e1bb26e59d4379173250fa7b23c`; mapa testado1144/8SHA256`dad790a4457e3997ba3037b13f9d9ac6e13f6b4d6754d198dac86f7f236d59cb`. Prontidão acumuladaNOT_APPROVED: resultados anteriores/atuais não encerram incidentes históricos. Proprietário confirmou persistência do botão principal; reparo do submenu separado. EditorCongelado relatado pelo proprietário; versão e DOM do cliente ainda não observados. Não inferir cache/override. Aceite humano pendente. Relatório tools/.artifacts/pf-hidden-menu-20261017/REPORT.md; escopo e baseline em .superpowers/sdd/jpw-pf-hidden-menu-20261017/BRIEF.md. Mesma branch/base2b22175, sem Git/publicação.

## Fotografia anterior preservada

# Finanças Pessoais congelado por padrão

N2/A3 delimitado. Autorização: pedido humano de congelar o menu, seguido de “Por padrão no projeto”, nesta conversa de16/10/2026. [Decisão factual](../decisions/2026-10-16-personal-finance-congelado.md). Reutilizar o candidato completo corrente em /private/tmp/jpw-time-twins-20261015, branch codex/bolsas-globais-aisol-20261015, HEAD/base2b22175a4f3f47b1f289deca65366c4dc0445dca. Não criar branch/worktree nem executar operaçõesGit.

## Contrato delimitado

Alterar somente a entrada personal-finance dos defaults de JPWModuleAvailability de active para frozen. Nenhum schema, chave, algoritmo de inspect/setState, escritor financeiro ou regra de confirmação muda. PF ausente/sparse usa frozen; override explícito active continua ativo, sem gravação/migração automática. Backup antigo sem preferência conserva o destino; null conserva seu significado existente de remover override e usar defaults, agora com PF congelado. Valores incompatíveis permanecem preservados, não importáveis e sem escrita.

Preservar dados/S.personalFinance, histórico, rascunhos, backups, fórmulas, contas, nomes/aliases, ordem/nós de navegação, três minigames, acabamento de Bolsas Globais, instruções/skills/normas/gates/CI e todos os incidentes anteriores. Testes operacionais de PF usam ativação sintética explícita; não enfraquecer suas expectativas financeiras. Não mudar fixtures globais para ocultar o novo padrão.

Baseline1142arquivos/8links e90pendências, mapa e tar recuperável em .superpowers/sdd/jpw-pf-default-frozen-20261016/. Brief registra seis respostas, fontes, permitido e rollback: restaurar somente o delta desta tarefa, sem reset/stash e sem apagar preferências reais.

## Verificação e estado

Oráculos de default antes do runtime registraram RED causal; demais casos e override explícito preservados. Executar core/UI/work/backup, testes operacionais afetados, guia/navegação/Dashboard e distribuição oficial, seguidos do FULL congelado. Sem reutilizar PASS da tarefa anterior como validação deste delta. Resultado final, limites e identidade no relatório tools/.artifacts/pf-default-frozen-20261016/REPORT.md. Neste registro inicial: validação final NOT_RUN; aceite humano pendente.

Escopo de documentação: decisão factual acima, este CHG, descrição do default em MODULE-AVAILABILITY, CHANGELOG e cabeçalhos factuais de ACTIVE/CURRENT/HANDOFF. Não alterar regras, instruções, autoridade, juízes, CI, política ou memória global. Sem commit, merge, push ou publicação.

## Regressão revelada e correção delimitada

O primeiro testework falhou no retorno de foco de Alladin, antes do cenárioPF. Investigação isolada com o mesmo estímulo e somente o defaultPF como variável:4/4restaurações comactive e4/4perdas comfrozen;8/8preservam dados/rascunho. Não é dívida de baseline nem passa aPASS por repetição. Causa: refresh global de suspendPFjáfrozen chama noticeAlladin antes que suspendAlladin capture o campo; o botão de recuperação acaba memorizado e removido no retorno.

A correção funcional necessária fica em33-module-work.js: capturar o controle original imediatamente antes da inércia/deslocamento e impedir sobrescrita por um controle de recuperação. Sem alterarresume, APIs, guardas de comandos financeiros ou persistência. O casoAV-WORK-FOCUS mantém o oráculo original de foco e passa a declarar explicitamente PFcongelado. Revisão independente confirmou causa e recorte. Primeirobruto e8AB preservados em tools/.artifacts/pf-default-frozen-20261016/. Validação após correção aindaNOT_RUN neste registro.

Recuperação de ambiente: PlaywrightPython e o Chromiumtemporário antigo ficaram indisponíveis; causa externaUNKNOWN. Nova instalaçãoisolada da mesma versãoPlaywright1.60.0 em /private/tmp/jpw-pf-default-frozen-runtime-20261017 reaproveita a autorização temporária humana dada nesta conversa; usaChrome instalado em perfis descartáveis. Nenhuma dependência do projeto ou dado pessoal alterado. Erros de ambiente não sãoPASS.

## Resultado local —17/10/2026

Build `7b12beb62d30bb4d`. FULL atual NÃO APROVADO:80PASS/1PRODUCT_FAIL, exit1; rawSHA256`c080926790c255a8e48ab15001f00dc94a1f36f7d71d92b5faac1db511ed45e4`; freeze1144/8SHA256`07c56ce5b0378ed353bebe529f76823f6bdcc369177e6b7a4df703d926d86cd3`. Core26PASS, UI24contextos finais, workAV-WORK-FOCUSGREEN ebackup14/0;18comandos suplementares exit0. Falha atual do gate: download-assets-browser linha112 no cenário size, com modalOverlay/jpwWelcomeStart interceptando o downloadPine; cenários posteriores não executados, sem causalidade/reparo alegado. Primeira falhaP2de foco e8AB(4activePASS/4frozenFAIL) preservadas; reparo causal delimitado em33, sem fechar incidentes históricos. Dados/fórmulas/backup preservados. Prontidão acumuladaNOT_APPROVED e aceite humano pendente. Sem commit/merge/push/publicação. Relatório tools/.artifacts/pf-default-frozen-20261016/REPORT.md.

Pós-teste somente este resultado, três agregadores factuais e metadata da entrada16, com mapa de entrega próprio. Fontes/testes/CHANGELOG/derivados congelados. Quinze entradas anteriores preservadas.
# Continuação delimitada — menu congelado residual —17/10/2026

Pedido vigente do proprietário: “quando um menu é congelado ela deve sumir”. N1/A2 para apresentação, sobre a entrega anterior1144arquivos/8links SHA4487d012eb8a705945a6471defd431231b4a33ab084d55a6b8b37383603bf767. Mesma branch/base, preservação das126pendências conhecidas. Escopo próprio/baseline recuperável em `.superpowers/sdd/jpw-pf-hidden-menu-20261017/BRIEF.md`.

Reprodução em contextos sintéticos descartáveis:8PRODUCT_FAIL/1PASS/0falhas de harness. PF sobreDashboard/Tools em hover ou teclado esconde o botão principal, porém conserva cinco filhos visíveis/interativos. Repetição de tecladoPF3/3; Forex/Research reproduzem. Gate de acesso recusa a entrada eS permanece intacto. Não comprova a causa no cliente real, que não foi inspecionado.

Causa e menor reparo: `sidebarPaint` usava preview/pin sem reconsultar disponibilidade, enquanto a sincronização somente limpava exploração quando a rota mudava. O shell agora remove exploração indisponível, cancela timers relacionados e oculta imediatamente o submenu, conservando pin válido; foco do submenu removido vai ao Dashboard. UI32, defaults/overrides, persistência/escritores e lógica financeira não mudam.

AV-NAV-FROZEN permanente em `module_availability_test.py`:6casos GREEN com o mesmo teste final que falha sobre o shell recuperado da baseline. Cobre sidebar expandida/recolhida, hover/teclado, fallback de pin válido, inércia/foco, prazos de callbacks, ausência de replay após thaw, preservação de rota/S/storagealheio/nós. Durante autoria houve duas falhas do próprio teste (comparador de IDs em botões anônimos e fixture de rawnull para módulos já ativos); oráculos de visibilidade não foram relaxados. RED/GREEN finais SHAdo teste5bd155c1f4dc396b6f878fb1b8f50edbb2d09411c4de1f491f1b77af44223a48, shellbaseline3b69863e10be08e2a73ded3c89a644403264c90dfb4c04ed04d1b2c436fc6440→corrigidob357497957b11e446fe5329b021e1947dfd6836087bae9d9d608121b88b58854.

Geraçãooficial, focais integrados eFULL deste novo delta ainda em execução/NOT_RUN; resultados anteriores abaixo permanecem históricos. Revisão estática independente não encontrou novoP1/P2; apontou lacuna preexistente de focoN3 Research/Forex com rascunho remoto em navLocalSlot, fora do selector e deste reparo. Não alegar cobertura universal de foco; investigação adicional permanece pendente. Sem commit/merge/push/publicação nem encerramento automático de incidentes históricos. Evidências novas em `tools/.artifacts/pf-hidden-menu-20261017/`.

## Fotografia anterior preservada
