# CHG-JPW-ALAVANCAGEM-GENESE-SL-20260928 — MT5 1.3.0

```yaml
schema: jp-harness/chg/v1
change_id: CHG-JPW-ALAVANCAGEM-GENESE-SL-20260928
status: approved
objective: Exibir distância do mercado ao SL vigente da posição de referência Gênese, sem negociar nem alterar as métricas existentes.
risk_level: N3
authority_required: A4
target:
  root: /private/tmp/jpw-alavancagem-atual-20260926
  branch: codex/jpw-alavancagem-atual-20260926
  baseline_sha: f5145b25e86af6b4ccbfef847cba0d84d74e7c8a
  derived_from: jpw-alavancagem-atual-20260928-r6
  r6_build: 42613e9b9f1b8766
  r6_fingerprint: 637cfb1c57ac9a5e5a73a40a556f5b3bea69f2095de8b3dab85636b95daf0ae0
scope:
  allowed_files: [docs/work/CHG-JPW-ALAVANCAGEM-GENESE-SL-20260928.md, docs/work/ACTIVE-TASK.md, mt5/jpw-alavancagem-atual/MQL5/Include/JPWealth/JPW_Alavancagem_Core.mqh, mt5/jpw-alavancagem-atual/MQL5/Include/JPWealth/JPW_Alavancagem_Terminal.mqh, mt5/jpw-alavancagem-atual/MQL5/Include/JPWealth/JPW_Alavancagem_Genesis_Core.mqh, mt5/jpw-alavancagem-atual/MQL5/Include/JPWealth/JPW_Alavancagem_Genesis_Store.mqh, mt5/jpw-alavancagem-atual/MQL5/Indicators/JPWealth/JPW_Alavancagem_Atual.mq5, mt5/jpw-alavancagem-atual/MQL5/Scripts/JPWealth/JPW_Alavancagem_Genesis_Tests.mq5, mt5/jpw-alavancagem-atual/MQL5/Scripts/JPWealth/JPW_Alavancagem_Genesis_Store_Tests.mq5, mt5/jpw-alavancagem-atual/README.md, downloads/jpw-alavancagem-atual/manifest.json, downloads/jpw-alavancagem-atual/JPW_Alavancagem_Atual_Fontes_v1.3.0.zip, index.html, tools/build_leverage_package.py, tools/leverage_package_test.py, tools/leverage_page_test.py, tools/leverage_panel_test.py, tools/build_reproducibility_test.py, build-id.js, sw.js, dist/JP_Wealth_Risk_Terminal_V9.1_PORTABLE.html, external canonical specification]
  forbidden_files: [docs/normative/, docs/decisions/, skills/, tools/quality_gate.py, .github/, src/js/00-core/, src/js/10-domain/, mt5/jpw-alavancagem-atual/MQL5/Include/JPWealth/JPW_Alavancagem_MDD.mqh, mt5/jpw-alavancagem-atual/MQL5/Include/JPWealth/JPW_Alavancagem_Profile.mqh, mt5/jpw-alavancagem-atual/MQL5/Scripts/JPWealth/JPW_Alavancagem_Verificar_USC.mq5]
  allowed_actions: [bounded local implementation, synthetic tests, official generation, isolated native validation if available, independent audit, external candidate freeze]
  forbidden_actions: [real-account access by agent, operational MT5 installation, trading, commit, push, merge, deploy, publication, r6 snapshot rewrite]
data:
  test_policy: synthetic_only
  persistence: new account-and-selector-scoped MT5 Files record separate from MDD and USC profile
  browser_state_change: forbidden
acceptance_criteria:
  - Initial automatic selection is only the uniquely oldest open position in the sole exact-symbol/direction group and is visibly inferred.
  - A selected POSITION_IDENTIFIER survives ticket replacement and partial close; confirmed closure or netting reversal never silently promotes a successor.
  - An explicit current ticket selects a new reference; invalid/corrupt/incompatible records fail closed.
  - Buy uses Bid minus current POSITION_SL; sell uses current POSITION_SL minus Ask; positive distance is points and percent of Q, with optional exact-symbol pip convention.
  - Reached, passed, no SL, invalid, stale, estimated, and unsupported states never imply stop execution.
  - The fourth gray line is independent of leverage, floating, DD, and MDD persistence; the existing formulas and storage formats remain unchanged.
  - Site, README, manifest, sources and generated derivatives identify the same new version; no account data leaves MT5.
approved_tests: [synthetic math/selection/persistence and regression, focused panel/package/page/structure, full quality gate with raw classification, isolated native compile/run if available, independent adversarial audit]
rollback:
  source: Restore the externally frozen r6 candidate by its 39-file fingerprint; do not rewrite the r6 snapshot.
  data: Do not delete MDD or profile files; the new Genesis record is separate and not distributed.
  verification: Compare source hashes and confirm no account record or unverified EX5 entered a package.
approved_by: Proprietário, pedido expresso nesta conversa para implementar o plano N3/A4 localmente.
approved_at: 2026-09-28 America/Sao_Paulo
```

## Contrato e risco

O papel `GENESIS` do aplicativo web não tem vínculo verificável com `POSITION_IDENTIFIER` no MT5. A referência automática será declarada inferida entre as posições ainda abertas e não certificará tese ou conformidade estatutária. A referência persistida bloqueará promoção silenciosa após encerramento, reinício ou reanexação; erro de leitura ou desconexão não comprovará encerramento. A distância é informativa, em preço do instrumento, e não é risco agregado nem ordem para mover o stop.

O indicador atual, o núcleo e o adaptador são alterados apenas para esta métrica. Nocional bruto/equity, percentuais sobre saldo, perfil USC, registro MDD e seus formatos não mudam. A leitura de Bid/Ask para esta distância não altera o preço médio usado no nocional. Contratos de bolsa não receberão interpretação implícita de acionamento por Bid/Ask. A nova persistência local não armazenará SL, preços, saldos ou histórico de ordens; site e pacote não a lerão.

## Preflight da base

O candidate r6 preservado foi conferido contra seus 39 caminhos: 39/39 hashes e tamanhos iguais aos da worktree, fingerprint recalculado `637cfb1c57ac9a5e5a73a40a556f5b3bea69f2095de8b3dab85636b95daf0ae0`. Branch `codex/jpw-alavancagem-atual-20260926`, HEAD `f5145b25e86af6b4ccbfef847cba0d84d74e7c8a`, staging vazio e `git diff --check` limpo. O r6 registrou `AUDIT_FAIL`, full 52 PASS / 5 PRODUCT_FAIL e validação nativa 1.2.1 NOT_RUN; esses resultados não serão reclassificados nem atribuídos à nova versão. Nenhum EX5 atual será presumido válido.
