# CHG-JPW-ALAVANCAGEM-METRICAS-MDD-20260928 — MT5 1.2.0

```yaml
schema: jp-harness/chg/v1
change_id: CHG-JPW-ALAVANCAGEM-METRICAS-MDD-20260928
status: approved
objective: Acrescentar flutuante/saldo, DD/saldo e máximo observado persistido ao indicador MT5 informativo.
risk_level: N3
authority_required: A4
target:
  root: /private/tmp/jpw-alavancagem-atual-20260926
  branch: codex/jpw-alavancagem-atual-20260926
  baseline_sha: f5145b25e86af6b4ccbfef847cba0d84d74e7c8a
  derived_from: jpw-alavancagem-atual-20260928-r4
  r4_fingerprint: d8d1f98a45ce8051de4b36dab1426a46134696d76594d21a51ed3b6355d7d37a
scope:
  allowed_files: [docs/work/CHG-JPW-ALAVANCAGEM-METRICAS-MDD-20260928.md, docs/work/ACTIVE-TASK.md, mt5/jpw-alavancagem-atual/MQL5/Include/JPWealth/JPW_Alavancagem_Core.mqh, mt5/jpw-alavancagem-atual/MQL5/Include/JPWealth/JPW_Alavancagem_MDD.mqh, mt5/jpw-alavancagem-atual/MQL5/Indicators/JPWealth/JPW_Alavancagem_Atual.mq5, mt5/jpw-alavancagem-atual/MQL5/Scripts/JPWealth/JPW_Alavancagem_Tests.mq5, mt5/jpw-alavancagem-atual/MQL5/Scripts/JPWealth/JPW_Alavancagem_Metrics_Tests.mq5, mt5/jpw-alavancagem-atual/README.md, downloads/jpw-alavancagem-atual/manifest.json, downloads/jpw-alavancagem-atual/JPW_Alavancagem_Atual_Fontes_v1.2.0.zip, index.html, tools/leverage_panel_test.py, tools/leverage_page_test.py, tools/leverage_package_test.py, build-id.js, sw.js, dist/JP_Wealth_Risk_Terminal_V9.1_PORTABLE.html]
  forbidden_files: [docs/normative/, docs/decisions/, skills/, tools/quality_gate.py, .github/, src/js/00-core/, src/js/10-domain/, mt5/jpw-alavancagem-atual/MQL5/Include/JPWealth/JPW_Alavancagem_Profile.mqh, mt5/jpw-alavancagem-atual/MQL5/Include/JPWealth/JPW_Alavancagem_Terminal.mqh, mt5/jpw-alavancagem-atual/MQL5/Scripts/JPWealth/JPW_Alavancagem_Verificar_USC.mq5]
  allowed_actions: [bounded local implementation, synthetic tests, official generation, isolated native validation when available, independent audit, external candidate freeze]
  forbidden_actions: [real-account access by agent, operational MT5 installation, trading, commit, push, merge, deploy, publication, source r4 rewrite]
data:
  test_policy: synthetic_only
  persistence: MT5 local Files sandbox; account-scoped observed maximum only
  browser_state_change: forbidden
acceptance_criteria:
  - Leverage permanece gross_notional / ACCOUNT_EQUITY com cobertura USC e conversões idêntica.
  - Flutuante é 100*ACCOUNT_PROFIT/ACCOUNT_BALANCE; DD é 100*max(0,B-E)/B.
  - Validade de cada percentual é independente da conversão do nocional e das demais propriedades não necessárias.
  - MDD observado é monotônico, por conta, preservado em dois slots recuperáveis; estimativas não o atualizam.
  - Gráfico mostra três linhas compactas e nunca mostra o MDD; site não recebe dados da conta.
  - Pacote, manifesto, guia, portátil e evidências identificam a mesma versão derivada.
approved_tests: [MQL5 synthetic math and persistence, focused panel/package/page, structure, full gate, isolated native compile/run if available, independent review]
rollback:
  source: Restaurar o candidate r4 preservado externamente pelos 32 hashes aceitos.
  data: Nenhum dado real é criado nesta tarefa; registros futuros da v1.2.0 não são apagados em rollback.
  verification: Conferir os hashes r4 e a ausência de EX5 ou registro de conta nos pacotes.
approved_by: Proprietário, pedido expresso nesta conversa para implementação local N3/A4.
approved_at: 2026-09-28 America/Sao_Paulo
```

## Task brief e fontes

O JP Wealth organiza risco e decisão operacional sem transformar uma visualização em autorização de operação. O módulo MT5 é informativo e separado do motor financeiro do aplicativo web. A v1.1.2/r4 preservada externamente tem 32/32 hashes iguais à worktree; branch `codex/jpw-alavancagem-atual-20260926`, HEAD `f5145b25e86af6b4ccbfef847cba0d84d74e7c8a`, staging vazio e 25 entradas preexistentes de status Git que pertencem ao r4. O ZIP de fontes v1.1.2 tem SHA-256 `cc725f1ea413434a1cb1e08eb29f56dbc07ae8a50db1d4975bd9378677f7752b`; não há EX5 v1.1.2 com proveniência comprovada. Nenhuma captura real do operador entra no delta.

Fontes consultadas: `AGENTS.md`, `README.md`, `docs/governance/CONTEXT-MAP.md`, `PROJECT-CONTEXT.md` (SHA-256 `37637ca6...`), `CURRENT-STATE.md` (`4edd09e0...`), Estatuto V11 PDF (`2dab6166...`, pp. 32, 35–36), Anexo T03 (`6240b633...`, definições D-06/D-07), Harness externo (`b5680c22...`), indicador/core/manifesto r4 e documentação oficial MetaQuotes sobre AccountInfoDouble e arquivos. O preflight audit/edit passou com avisos de estado preexistente e frescor contextual; o r4 foi conferido byte a byte antes do novo escopo.

| Regra | Fonte normativa / pedido específico | Código antes | Prova exigida |
|---|---|---|---|
| DD operacional de fase | Estatuto V11 Art. 4.1: base Saldo Inicial do Ciclo, neutralização de fluxos | Fora deste indicador | Não apresentar DD/saldo ou máximo observado como DD normativo nem alimentar gates do produto |
| Alavancagem normativa | Estatuto V11 Art. 4.5: nocional bruto / min(Saldo Inicial do Ciclo, Equity) | Ferramenta MT5 r4 usa nocional bruto / Equity, conforme seu contrato informativo explícito | Não alterar a fórmula existente nem sugerir conformidade normativa da ferramenta |
| Flutuante/saldo e DD/saldo | Autorização A4 atual: `100*P/B` e `100*max(0,B-E)/B` | Ausentes | Núcleo comum produção/testes, USD/USC, bordas e independência por propriedade |
| Máximo observado/saldo | Autorização A4 atual: máximo apenas de amostras atuais válidas, a partir da primeira observação | Ausente | Persistência monotônica, concorrente, recuperável, sem inferir histórico não observado |

Invariantes: `ACCOUNT_PROFIT` não é substituído por E−B; crédito é contexto e não entra em fórmula; B, E e P permanecem na mesma unidade da conta; equity não é obrigado a ficar constante entre leituras. O timer atual continua solicitando atualização sem prometer intervalo fixo. O registro fica em `MQL5/Files/JPWealth/Alavancagem`, nunca em ZIP, site, PWA, backup ou telemetria. Falha de persistência não produz confirmação falsa. Falhas históricas do full são preservadas e uma nova falha não é reclassificada por conveniência.

AGENTIC IMPACT CHECK: AGENTIC IMPACT DETECTED. O contrato informativo da ferramenta, o guia público, o manifesto e o pacote consumidos por agentes mudam; reconciliar somente esses artefatos e `ACTIVE-TASK`. Estatuto, Harness, control plane e decisões permanecem sem alteração. Exposição do novo contrato não autoriza a camada agentic a tratá-lo como regra normativa.

## Recibo de implementação local

O derivado v1.2.0 conserva a base r4: dos 32 arquivos inventariados, 20 continuam idênticos e 12 mudaram no recorte permitido. Os três arquivos novos são este CHG, o include de máximo observado e o script sintético de persistência. O ZIP 1.2.0 foi regenerado pelo gerador oficial; não há EX5 distribuído.

Focais de painel, pacote, página e estrutura passaram. A página foi verificada por automação em HTTP, arquivo local, HTML portátil e PWA offline, nos quatro layouts e em 320/390/1440 px com os dois temas. O full único desta revisão, antes de uma correção exclusivamente editorial do guia e da regeneração correspondente, registrou **54 PASS / 3 PRODUCT_FAIL** no recibo `tools/.artifacts/quality-20260928T150438-full.json`: `pivot-studies` encontrou `jpwWorkspaceDraftProviders is not defined`, `session-finalization` encontrou `$ is not defined` em `closeModal`, e `async-generation` excedeu a espera por cotações. Esses três resultados permanecem PRODUCT_FAIL; a relação causal com o delta não foi demonstrada. Depois da correção editorial, os focais afetados e a estrutura passaram novamente. O full não foi repetido para buscar verde.

Compilação X64 Regular, execução dos scripts e inspeção nativa de duas instâncias da v1.2.0: **NOT_RUN**, pois não há ambiente MT5 isolado utilizável comprovado sem tocar na sessão operacional. O PASS manual de 117 assertivas e as compilações anteriores pertencem ao r1, não a esta versão. Até validação nativa e resolução dos riscos do gate, esta entrega é fonte e página revisáveis, não homologação operacional. O máximo recuperado de um slot truncado é a última geração válida; um pico existente apenas na geração perdida não pode ser reconstruído.
