# Sessões Forex e B3 — brief autorizado em31/10/2026

Base `69b6cb677de2486be5c30681e4b2e02d4180d704`; branch `codex/sessoes-forex-b3-20261031`. Implementação do plano humano de quatro sessões Forex indicativas com B3 separada. O proprietário autorizou quatro worktrees, implantação delimitada, preferência de fuso persistida e uso dos contratos/controles versionados durante a indisponibilidade do Harness externo após a migração. Essa decisão não modifica gates nem autoriza Git/publicação.

A finalidade é orientar a leitura temporal, não executar operações, confirmar liquidez ou substituir horários de instrumento/corretora. O módulo mantém as APIs puras de calendário acionário e o catálogo de16identidades; o app passa a mostrar quatro centrosFX+SãoPaulo. B3 continua conforme o calendário original. Nenhum dado financeiro é importado ou alterado.

Antes:16bolsas na tabela, sem barras/fuso. Depois:4janelasFX, B3 separada, bandeiras, projeção de um dia civil, relógio consistente, globo preservado com cinco pontos, detalhes[i] e preferência estruturada para Backup Completo. Os estadosunknown e a cobertura limitada permanecem explícitos.

Fonte da convenção única: https://www.forex.com/en-uk/trading-guides/forex-market-hours/ , consultada31/10/2026; tabela local Sydney07–16,Tokyo09–18,London08–16,NewYork08–17. Segunda a sexta local; não adotar borda semanal/rollover de outra corretora. Não inferir calendáriosFX a partir de bolsas.

Risco: UI/comportamentoN1; preferênciaN2; extensões de build/testes/control planeN3 delimitadas em contrato próprio. Fontes do domínio: MARKET-HOURS, UI-VISUAL-QUALITY, COMPLETE-BACKUP, CHANGE-PROCESS e AGENTS vigentes. CatálogoFX usa o compilador local com TZif2026b e dados independentes; o catálogo acionário não é regenerado nem alterado.

Validação: focais puro/modelo/loader/UI e distribuiçõesHTTP,PWAoffline,file,portátil; FULL e revisão independente agendados pelo coordenador. Evidências ficam fora do repositório em work/implementation; não importar resultados antigos como novos. Rollback: reverter apenas o delta desta frente e reconstruir derivados pelo gerador; preservar a chave de preferência, que nunca contém estado financeiro. Nenhum reset ou localStorage.clear.

Fechamento da reauditoria: fronteiras de cobertura seguem o dia civil projetado também no Dispositivo; os controles da ajuda externa são medidos pelo mesmo mínimo44px; o recibo de distribuição verifica integridade novamente após todos os focais. São correções delimitadas do escopo aprovado, sem ampliação de cobertura temporal, horários, fusos persistidos ou poderes do runner.
